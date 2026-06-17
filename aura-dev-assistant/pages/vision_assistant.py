from PIL import Image
import streamlit as st

from services.speech_service import autoplay_audio, init_voice_state, text_to_speech_file
from services.vision_service import VisionService
from utils.ui import load_css, render_header


st.set_page_config(page_title="Vision Assistant | Aura", page_icon="A", layout="wide")
load_css()
init_voice_state()

render_header("Vision Assistant", "Analyze screenshots, code errors, terminal output, UI designs, and diagrams.")

with st.sidebar:
    st.markdown("### Vision Settings")
    speak = st.toggle("Speak findings", value=True)
    focus = st.selectbox(
        "Analysis focus",
        ["Auto detect", "Code errors", "UI design", "Terminal error", "Diagram explanation"],
    )

uploaded = st.file_uploader("Upload screenshot", type=["png", "jpg", "jpeg", "webp"])

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded screenshot", use_container_width=True)

    if st.button("Analyze Screenshot", type="primary"):
        try:
            with st.spinner("Gemini Vision is inspecting the image..."):
                result = VisionService().analyze_image(image, focus=focus)
            st.markdown("### Aura Findings")
            st.markdown(result)
            if speak:
                audio_path = text_to_speech_file(result)
                autoplay_audio(audio_path)
        except Exception as exc:
            st.error(f"Vision analysis failed: {exc}")
else:
    st.info("Upload a screenshot to inspect UI, code, diagrams, or terminal output.")
