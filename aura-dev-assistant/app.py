import streamlit as st

from services.speech_service import init_voice_state
from utils.ui import load_css, render_header, render_status_cards


st.set_page_config(
    page_title="Aura Dev Assistant",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
init_voice_state()

with st.sidebar:
    st.markdown("## Aura Dev Assistant")
    st.caption("Voice controlled AI coding workspace")
    st.divider()
    st.page_link("app.py", label="Command Center")
    st.page_link("pages/coding_assistant.py", label="Coding Assistant")
    st.page_link("pages/github_analyzer.py", label="GitHub Analyzer")
    st.page_link("pages/project_analyzer.py", label="Project Analyzer")
    st.page_link("pages/vision_assistant.py", label="Vision Assistant")
    st.divider()
    st.caption("Set GEMINI_API_KEY in your environment or .env file.")

render_header(
    title="Aura Dev Assistant",
    subtitle="A Jarvis-inspired developer companion for voice, code, repos, projects, and screenshots.",
)

render_status_cards(
    [
        ("Voice", "Speech input + Edge neural TTS", "Ready"),
        ("Gemini", "Text and vision intelligence", "API key required"),
        ("Analyzers", "GitHub repositories and ZIP projects", "Modular"),
    ]
)

st.markdown("### Mission Console")
st.markdown(
    """
    Use the sidebar to move between the assistant modules. The coding assistant supports
    microphone input, chat, code explanation, debugging, improvement suggestions, concept
    explanations, and code generation. Repository, project, and screenshot analyzers
    produce structured summaries and can speak the result automatically.
    """
)

left, right = st.columns([1.2, 0.8])
with left:
    st.markdown("#### Capabilities")
    st.markdown(
        """
        - Voice-controlled coding chat with automatic neural speech output.
        - Gemini-powered code review, debugging, refactoring, and generation.
        - GitHub repository cloning, README extraction, file scanning, and architecture analysis.
        - ZIP project extraction with AST-based Python file summaries.
        - Screenshot analysis for UI, terminal, diagram, and code-error detection.
        """
    )

with right:
    st.markdown("#### Quick Start")
    st.code(
        "python -m venv .venv\n"
        ".venv\\Scripts\\activate\n"
        "pip install -r requirements.txt\n"
        "copy .env.example .env\n"
        "streamlit run app.py",
        language="powershell",
    )
