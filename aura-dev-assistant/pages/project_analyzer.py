import streamlit as st

from services.gemini_service import GeminiService, GeminiServiceError
from services.project_service import ProjectService
from services.speech_service import autoplay_audio, init_voice_state, text_to_speech_file
from utils.prompts import LOCAL_PROJECT_ANALYSIS_PROMPT
from utils.ui import load_css, render_header


st.set_page_config(page_title="Project Analyzer | Aura", page_icon="A", layout="wide")
load_css()
init_voice_state()

render_header("Local Project Analyzer", "Upload a ZIP project and receive a structured engineering summary.")

with st.sidebar:
    st.markdown("### ZIP Analysis")
    max_files = st.slider("Max files to inspect", 10, 160, 60)
    max_chars = st.slider("Max characters per file", 500, 5000, 1800, step=250)
    speak = st.toggle("Speak summary", value=True)

uploaded = st.file_uploader("Upload project ZIP", type=["zip"])

if uploaded and st.button("Analyze Project", type="primary"):
    try:
        with st.spinner("Extracting and parsing project files..."):
            project_data = ProjectService().analyze_zip(
                uploaded, max_files=max_files, max_chars=max_chars
            )

        st.markdown("### Project Structure")
        st.code(project_data["tree"], language="text")

        with st.expander("File-level notes", expanded=False):
            for item in project_data["file_summaries"]:
                st.markdown(f"**{item['path']}**")
                st.caption(item["summary"])

        with st.spinner("Gemini is synthesizing the project overview..."):
            analysis = GeminiService().generate(
                LOCAL_PROJECT_ANALYSIS_PROMPT.format(project_context=project_data["context"])
            )

        st.markdown("### Aura Analysis")
        st.markdown(analysis)

        if speak:
            audio_path = text_to_speech_file(analysis)
            autoplay_audio(audio_path)
    except GeminiServiceError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Project analysis failed: {exc}")
elif not uploaded:
    st.info("Upload a ZIP archive to begin.")
