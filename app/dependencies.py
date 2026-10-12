from functools import lru_cache

from app.services.llm_wrapper import LLMWrapper


@lru_cache
def get_llm_wrapper() -> LLMWrapper:
    return LLMWrapper()