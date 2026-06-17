import asyncio
import base64
import re
import tempfile
from pathlib import Path

import edge_tts
import speech_recognition as sr
import streamlit as st


def init_voice_state() -> None:
    if "voice_status" not in st.session_state:
        st.session_state.voice_status = "Ready"


def speech_to_text(timeout: int = 8, phrase_time_limit: int = 18) -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.7)
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    return recognizer.recognize_google(audio)


def text_to_speech_file(text: str, voice: str = "en-US-AriaNeural") -> Path:
    clean_text = _clean_for_speech(text)
    output_path = Path(tempfile.gettempdir()) / "aura_dev_assistant_response.mp3"
    asyncio.run(_edge_tts(clean_text, output_path, voice))
    return output_path


async def _edge_tts(text: str, output_path: Path, voice: str) -> None:
    communicate = edge_tts.Communicate(text=text[:4500], voice=voice)
    await communicate.save(str(output_path))


def autoplay_audio(audio_path: Path) -> None:
    data = audio_path.read_bytes()
    b64 = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True,
    )


def _clean_for_speech(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", " I found a code block. See the screen for details. ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"[*_>#~-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
