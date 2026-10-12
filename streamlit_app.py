import time

import streamlit as st
from anthropic import Anthropic

from app.config import get_settings
from app.context.examples import ESTIMATION_EXAMPLES
from app.services.llm_service import build_system_prompt, format_examples
from app.services.pricing import calculate_cost

settings = get_settings()
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

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

    inicio = time.perf_counter()
    with st.chat_message("assistant"):
        with client.messages.stream(
            model=settings.LLM_MODEL,
            max_tokens=settings.LLM_MAX_TOKENS,
            system=build_system_prompt(),
            messages=[{"role": "user", "content": transcription}],
        ) as stream:
            texto = st.write_stream(stream.text_stream)
            final = stream.get_final_message()

    st.session_state.messages.append({"role": "assistant", "content": texto})
    st.session_state.last_metrics = {
        "model": settings.LLM_MODEL,
        "input_tokens": final.usage.input_tokens,
        "output_tokens": final.usage.output_tokens,
        "seconds": time.perf_counter() - inicio,
        "cost_usd": calculate_cost(
            settings.LLM_MODEL,
            final.usage.input_tokens,
            final.usage.output_tokens,
        ),
    }

# Panel lateral (va al final para que muestre las métricas de la llamada recién hecha)
with st.sidebar:
    st.header("Contexto del modelo")

    with st.expander("System prompt activo"):
        st.text(build_system_prompt())

    with st.expander("Contexto estático (ejemplos CAG)"):
        st.caption(f"{len(ESTIMATION_EXAMPLES)} ejemplos inyectados en cada llamada")
        st.markdown(format_examples(ESTIMATION_EXAMPLES))

    st.subheader("Última llamada")
    metricas = st.session_state.get("last_metrics")
    if metricas:
        st.write(f"**Modelo:** {metricas['model']}")
        st.write(f"**Tokens de entrada:** {metricas['input_tokens']}")
        st.write(f"**Tokens de salida:** {metricas['output_tokens']}")
        st.write(f"**Tiempo:** {metricas['seconds']:.1f} s")
        if metricas["cost_usd"] is not None:
            st.write(f"**Costo:** US$ {metricas['cost_usd']}")
    else:
        st.caption("Todavía no hay llamadas.")