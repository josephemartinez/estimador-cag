import json

import httpx
import streamlit as st

from app.config import get_settings
from app.context.examples import ESTIMATION_EXAMPLES
from app.services.llm_service import build_system_prompt, format_examples

settings = get_settings()
STREAM_URL = f"{settings.ESTIMATOR_API_BASE_URL.rstrip('/')}/api/v1/estimate/stream"


def stream_estimation(transcription: str, meta: dict):
    """Lee el flujo SSE de la API. Entrega el texto y deja las metricas en `meta`."""
    with httpx.stream(
        "POST",
        STREAM_URL,
        json={"transcription": transcription},
        timeout=httpx.Timeout(180.0, connect=10.0),
        headers={"Accept": "text/event-stream"},
    ) as response:
        response.raise_for_status()
        event, data = "token", []
        for line in response.iter_lines():
            if line == "":
                if data:
                    payload = "\n".join(data)
                    if event == "token":
                        yield payload
                    elif event == "meta":
                        meta.update(json.loads(payload))
                    elif event == "error":
                        raise RuntimeError(payload)
                    elif event == "done":
                        return
                event, data = "token", []
            elif line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                data.append(line[6:] if line.startswith("data: ") else line[5:])


st.set_page_config(page_title="Estimador CAG")
st.title("Estimador CAG")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if transcription := st.chat_input("Pegá la transcripción de la reunión"):
    st.session_state.messages.append({"role": "user", "content": transcription})
    with st.chat_message("user"):
        st.markdown(transcription)

    meta: dict = {}
    texto = None
    with st.chat_message("assistant"):
        try:
            texto = st.write_stream(stream_estimation(transcription, meta))
        except (httpx.HTTPError, RuntimeError) as exc:
            st.error(f"No se pudo obtener la estimación: {exc}")

    if texto:
        st.session_state.messages.append({"role": "assistant", "content": texto})
        st.session_state.last_metrics = meta

with st.sidebar:
    st.header("Contexto del modelo")
    with st.expander("System prompt activo"):
        st.text(build_system_prompt())
    with st.expander("Contexto estático (ejemplos CAG)"):
        st.caption(f"{len(ESTIMATION_EXAMPLES)} ejemplos inyectados en cada llamada")
        st.markdown(format_examples(ESTIMATION_EXAMPLES))
    st.subheader("Última llamada")
    m = st.session_state.get("last_metrics")
    if m:
        st.write(f"**Modelo:** {m.get('model')} ({m.get('provider')})")
        st.write(f"**Cache:** {'acierto' if m.get('cache_hit') else 'fallo'}")
        st.write(f"**Tokens de entrada:** {m.get('input_tokens')}")
        st.write(f"**Tokens de salida:** {m.get('output_tokens')}")
        st.write(f"**Tiempo:** {(m.get('latency_ms') or 0) / 1000:.1f} s")
        if m.get("cost_usd") is not None:
            st.write(f"**Costo:** US$ {m['cost_usd']}")
    else:
        st.caption("Todavía no hay llamadas.")