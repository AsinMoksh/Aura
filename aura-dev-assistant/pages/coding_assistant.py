import streamlit as st

from services.gemini_service import GeminiService, GeminiServiceError
from services.speech_service import (
    autoplay_audio,
    init_voice_state,
    speech_to_text,
    text_to_speech_file,
)
from utils.prompts import CODING_SYSTEM_PROMPT
from utils.ui import load_css, render_header, render_voice_indicator


st.set_page_config(page_title="Coding Assistant | Aura", page_icon="A", layout="wide")
load_css()
init_voice_state()

render_header("Coding Assistant", "Speak or type. Aura responds with code-aware reasoning and voice.")

if "coding_messages" not in st.session_state:
    st.session_state.coding_messages = [
        {
            "role": "assistant",
            "content": "Aura online. Send code, an error trace, or a build request.",
        }
    ]

with st.sidebar:
    st.markdown("### Voice Controls")
    auto_speak = st.toggle("Auto speak responses", value=True)
    voice_name = st.selectbox(
        "Edge TTS voice",
        [
            "en-US-AriaNeural",
            "en-US-JennyNeural",
            "en-US-GuyNeural",
            "en-GB-SoniaNeural",
            "en-IN-NeerjaNeural",
        ],
        index=0,
    )
    st.caption("Microphone capture uses SpeechRecognition and your system microphone.")

for message in st.session_state.coding_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_col, text_col = st.columns([0.25, 0.75], vertical_alignment="center")
with voice_col:
    listen = st.button("Start Voice Input", use_container_width=True)
with text_col:
    render_voice_indicator(st.session_state.voice_status)

if listen:
    try:
        st.session_state.voice_status = "Listening"
        with st.spinner("Listening through microphone..."):
            spoken_text = speech_to_text()
        st.session_state.voice_status = "Ready"
        if spoken_text:
            st.session_state.coding_messages.append({"role": "user", "content": spoken_text})
            st.rerun()
    except Exception as exc:
        st.session_state.voice_status = "Error"
        st.error(f"Speech recognition failed: {exc}")

typed_prompt = st.chat_input("Ask Aura to explain, debug, improve, generate, or summarize code...")

if typed_prompt:
    st.session_state.coding_messages.append({"role": "user", "content": typed_prompt})
    st.rerun()

if st.session_state.coding_messages[-1]["role"] == "user":
    user_prompt = st.session_state.coding_messages[-1]["content"]
    with st.chat_message("assistant"):
        with st.spinner("Gemini is reasoning through the code..."):
            try:
                service = GeminiService()
                response = service.chat(
                    user_prompt,
                    system_prompt=CODING_SYSTEM_PROMPT,
                    history=st.session_state.coding_messages[:-1],
                )
                st.markdown(response)
                st.session_state.coding_messages.append({"role": "assistant", "content": response})
                if auto_speak:
                    audio_path = text_to_speech_file(response, voice=voice_name)
                    autoplay_audio(audio_path)
            except GeminiServiceError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Assistant failed: {exc}")
