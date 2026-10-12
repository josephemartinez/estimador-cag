import json

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import iterate_in_threadpool, run_in_threadpool
from sse_starlette.sse import EventSourceResponse

from app.dependencies import get_llm_wrapper
from app.schemas.estimation import EstimationRequest, EstimationResponse
from app.services.llm_service import build_system_prompt, generate_estimation
from app.services.llm_wrapper import LLMWrapper

log = structlog.get_logger()

router = APIRouter(prefix="/api/v1", tags=["estimations"])


@router.post("/estimate", response_model=EstimationResponse)
async def estimate(request: EstimationRequest, wrapper: LLMWrapper = Depends(get_llm_wrapper)):
    try:
        return await run_in_threadpool(generate_estimation, wrapper, request.transcription)
    except Exception as exc:
        log.error("estimate_failed", error_type=type(exc).__name__, error=str(exc))
        raise HTTPException(
            status_code=502, detail="No se pudo generar la estimacion: fallaron todos los proveedores"
        )


@router.post("/estimate/stream")
async def estimate_stream(
    request: EstimationRequest, wrapper: LLMWrapper = Depends(get_llm_wrapper)
):
    async def events():
        try:
            stream = wrapper.complete_stream(
                system_prompt=build_system_prompt(), user_message=request.transcription
            )
            async for ev in iterate_in_threadpool(stream):
                if ev["type"] == "token":
                    yield {"event": "token", "data": ev["text"]}
                else:
                    meta = {k: v for k, v in ev.items() if k != "type"}
                    yield {"event": "meta", "data": json.dumps(meta)}
            yield {"event": "done", "data": "[DONE]"}
        except Exception as exc:
            log.error("estimate_stream_failed", error_type=type(exc).__name__, error=str(exc))
            yield {"event": "error", "data": "No se pudo generar la estimacion"}

    return EventSourceResponse(events())