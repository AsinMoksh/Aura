import streamlit as st

from services.gemini_service import GeminiService, GeminiServiceError
from services.github_service import GitHubService
from services.speech_service import autoplay_audio, init_voice_state, text_to_speech_file
from utils.prompts import REPOSITORY_ANALYSIS_PROMPT
from utils.ui import load_css, render_header


st.set_page_config(page_title="GitHub Analyzer | Aura", page_icon="A", layout="wide")
load_css()
init_voice_state()

render_header("GitHub Repository Analyzer", "Clone, inspect, summarize, and improve repositories.")

with st.sidebar:
    st.markdown("### Analyzer Settings")
    max_files = st.slider("Max files to inspect", 10, 120, 45)
    max_chars = st.slider("Max characters per file", 500, 6000, 2200, step=250)
    speak = st.toggle("Speak analysis", value=True)

repo_url = st.text_input("GitHub repository URL", placeholder="https://github.com/owner/repository")

if st.button("Analyze Repository", type="primary"):
    if not repo_url.strip():
        st.warning("Enter a GitHub repository URL first.")
    else:
        try:
            with st.spinner("Fetching repository structure and files..."):
                repo_data = GitHubService().analyze_repository(
                    repo_url.strip(), max_files=max_files, max_chars=max_chars
                )

            st.markdown("### Repository Structure")
            st.code(repo_data["tree"], language="text")

            with st.spinner("Gemini is preparing architecture analysis..."):
                service = GeminiService()
                analysis = service.generate(
                    REPOSITORY_ANALYSIS_PROMPT.format(repository_context=repo_data["context"])
                )

            st.markdown("### Aura Analysis")
            st.markdown(analysis)

            if speak:
                audio_path = text_to_speech_file(analysis)
                autoplay_audio(audio_path)
        except GeminiServiceError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Repository analysis failed: {exc}")
