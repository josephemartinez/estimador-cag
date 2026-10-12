import re
import time

import litellm
import structlog
from litellm import Router

from app.config import Settings, get_settings
from app.services.pricing import calculate_cost

log = structlog.get_logger()
litellm.suppress_debug_info = True


def _provider(model: str) -> str:
    return "anthropic" if model.startswith("claude") else "openai"


def _cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    cost = calculate_cost(model, input_tokens, output_tokens)
    if cost is None:  # probar sin el sufijo de fecha: claude-haiku-4-5-20251001
        cost = calculate_cost(re.sub(r"-\d{8}$", "", model), input_tokens, output_tokens)
    return cost


class LLMWrapper:
    def __init__(self, settings: Settings | None = None):
        s = settings or get_settings()
        self.primary_model = s.PRIMARY_MODEL
        self.max_tokens = s.LLM_MAX_TOKENS
        self.temperature = s.LLM_TEMPERATURE
        self.router = Router(
            model_list=[
                {
                    "model_name": "primary",
                    "litellm_params": {
                        "model": s.PRIMARY_MODEL,
                        "api_key": s.OPENAI_API_KEY,
                        "timeout": s.LLM_TIMEOUT,
                    },
                },
                {
                    "model_name": "fallback",
                    "litellm_params": {
                        "model": s.FALLBACK_MODEL,
                        "api_key": s.ANTHROPIC_API_KEY,
                        "timeout": s.LLM_TIMEOUT,
                    },
                },
            ],
            fallbacks=[{"primary": ["fallback"]}],
            num_retries=s.LLM_RETRIES,
        )

    def complete(self, *, system_prompt: str, user_message: str) -> dict:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        log.info("llm_call_started", primary=self.primary_model)
        t0 = time.perf_counter()
        try:
            response = self.router.completion(
                model="primary",
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        except Exception as exc:
            log.error(
                "llm_call_failed",
                error_type=type(exc).__name__,
                error=str(exc),
                latency_ms=int((time.perf_counter() - t0) * 1000),
            )
            raise

        latency_ms = int((time.perf_counter() - t0) * 1000)
        model = response.model.split("/", 1)[-1]
        input_tokens = response.usage.prompt_tokens or 0
        output_tokens = response.usage.completion_tokens or 0
        provider = _provider(model)
        cost = _cost(model, input_tokens, output_tokens)

        log.info(
            "llm_call_completed",
            model=model,
            provider=provider,
            fallback_used=provider != _provider(self.primary_model),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
        )
        return {
            "estimation": response.choices[0].message.content or "",
            "model": model,
            "provider": provider,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "latency_ms": latency_ms,
        }