import streamlit as st
from anthropic import Anthropic

from app.config import get_settings
from app.services.llm_service import build_system_prompt

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

    with st.chat_message("assistant"):
        with st.spinner("Estimando..."):
            response = client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                system=build_system_prompt(),
                messages=[{"role": "user", "content": transcription}],
            )
        texto = response.content[0].text
        st.markdown(texto)

    st.session_state.messages.append({"role": "assistant", "content": texto})