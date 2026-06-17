from pathlib import Path

import streamlit as st


def load_css() -> None:
    css_path = Path(__file__).resolve().parents[1] / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="aura-header">
            <div class="aura-orbit"></div>
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_cards(cards: list[tuple[str, str, str]]) -> None:
    cols = st.columns(len(cards))
    for col, (title, body, status) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="status-card">
                    <span>{status}</span>
                    <h3>{title}</h3>
                    <p>{body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_voice_indicator(status: str) -> None:
    st.markdown(
        f"""
        <div class="voice-indicator">
            <div class="voice-pulse"></div>
            <strong>Voice status:</strong> {status}
        </div>
        """,
        unsafe_allow_html=True,
    )
