"""Shared visual styling helpers for the Streamlit UI."""

from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    """Inject the app-wide visual system."""

    st.markdown(
        """
<style>
    :root {
        --cc-bg: #f3f1eb;
        --cc-surface: rgba(255, 255, 255, 0.86);
        --cc-surface-strong: rgba(255, 255, 255, 0.96);
        --cc-ink: #102330;
        --cc-muted: #5e7280;
        --cc-border: rgba(16, 35, 48, 0.10);
        --cc-shadow: 0 18px 45px rgba(16, 35, 48, 0.08);
        --cc-deep: #113b4a;
        --cc-teal: #1e6b73;
        --cc-blue: #7da9c4;
        --cc-sand: #d9cfbf;
        --cc-success: #1d6b48;
        --cc-success-bg: #e5f5ed;
        --cc-warning: #8b5a16;
        --cc-warning-bg: #fff3dd;
        --cc-danger: #9d3e39;
        --cc-danger-bg: #fde9e6;
        --cc-info: #305f84;
        --cc-info-bg: #eaf3fb;
        --cc-radius-lg: 22px;
        --cc-radius-md: 16px;
        --cc-radius-sm: 12px;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(125, 169, 196, 0.25), transparent 28%),
            linear-gradient(180deg, #fbfaf7 0%, var(--cc-bg) 100%);
        color: var(--cc-ink);
    }

    .main .block-container {
        padding-top: 1.3rem;
        padding-bottom: 2.5rem;
        max-width: 1460px;
    }

    h1, h2, h3, h4 {
        color: var(--cc-ink);
        letter-spacing: -0.03em;
    }

    p, li, [data-testid="stMarkdownContainer"] {
        color: var(--cc-ink);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #173844 0%, #102b36 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] * {
        color: #f7fbfc !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] .st-bb,
    [data-testid="stSidebar"] .st-b6 {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.16) !important;
    }

    [data-testid="stTextArea"] textarea {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid var(--cc-border);
        border-radius: 18px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.4);
        color: var(--cc-ink);
        font-size: 0.95rem;
        line-height: 1.65;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: rgba(30, 107, 115, 0.65);
        box-shadow: 0 0 0 1px rgba(30, 107, 115, 0.18);
    }

    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        border-radius: 999px;
        border: 1px solid var(--cc-border);
        background: rgba(255,255,255,0.78);
        color: var(--cc-ink);
        font-weight: 600;
        min-height: 2.7rem;
        box-shadow: none;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, var(--cc-deep) 0%, var(--cc-teal) 100%);
        color: white;
        border-color: transparent;
    }

    div[data-testid="stButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        border-color: rgba(17, 59, 74, 0.28);
        color: var(--cc-deep);
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        color: white;
        border-color: transparent;
        filter: brightness(1.03);
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.68);
        border: 1px solid var(--cc-border);
        border-radius: 18px;
        padding: 0.85rem 0.95rem;
    }

    .cc-hero {
        position: relative;
        overflow: hidden;
        border-radius: 30px;
        padding: 1.45rem 1.6rem 1.55rem 1.6rem;
        margin-bottom: 1rem;
        background:
            radial-gradient(circle at top right, rgba(255,255,255,0.18), transparent 32%),
            linear-gradient(135deg, #123847 0%, #195463 44%, #2a7380 100%);
        color: white;
        box-shadow: 0 22px 50px rgba(17, 59, 74, 0.22);
    }

    .cc-hero::after {
        content: "";
        position: absolute;
        inset: auto -30px -40px auto;
        width: 220px;
        height: 220px;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        filter: blur(2px);
    }

    .cc-overline {
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-size: 0.70rem;
        opacity: 0.78;
        font-weight: 700;
    }

    .cc-hero-title {
        font-size: clamp(2rem, 3vw, 2.8rem);
        line-height: 1.03;
        letter-spacing: -0.05em;
        font-weight: 700;
        margin: 0.2rem 0 0.45rem 0;
    }

    .cc-hero-copy {
        max-width: 58rem;
        font-size: 0.98rem;
        line-height: 1.65;
        opacity: 0.92;
        margin-bottom: 0.9rem;
    }

    .cc-chip-row {
        display: flex;
        gap: 0.55rem;
        flex-wrap: wrap;
    }

    .cc-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.44rem 0.82rem;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.16);
        background: rgba(255,255,255,0.12);
        color: white;
        font-size: 0.76rem;
        line-height: 1;
    }

    .cc-shell {
        background: var(--cc-surface);
        border: 1px solid var(--cc-border);
        border-radius: var(--cc-radius-lg);
        box-shadow: var(--cc-shadow);
        backdrop-filter: blur(14px);
        padding: 1.1rem 1.15rem 1.15rem 1.15rem;
        margin-bottom: 0.9rem;
    }

    .cc-shell.cc-shell-soft {
        background: rgba(255,255,255,0.68);
        box-shadow: none;
    }

    .cc-section-kicker {
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.68rem;
        color: var(--cc-teal);
        font-weight: 700;
        margin-bottom: 0.32rem;
    }

    .cc-section-title {
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        margin: 0;
        color: var(--cc-ink);
    }

    .cc-section-copy {
        font-size: 0.86rem;
        color: var(--cc-muted);
        line-height: 1.55;
        margin-top: 0.4rem;
    }

    .cc-meta-row {
        display: flex;
        gap: 0.45rem;
        flex-wrap: wrap;
        margin-top: 0.7rem;
    }

    .cc-meta-pill {
        border-radius: 999px;
        padding: 0.34rem 0.66rem;
        font-size: 0.74rem;
        background: rgba(17, 59, 74, 0.06);
        border: 1px solid rgba(17, 59, 74, 0.09);
        color: var(--cc-ink);
    }

    .cc-empty {
        text-align: left;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(255,255,255,0.84) 0%, rgba(247,248,244,0.88) 100%);
        border: 1px solid var(--cc-border);
        padding: 1.2rem 1.15rem;
    }

    .cc-empty-icon {
        font-size: 1.7rem;
        margin-bottom: 0.35rem;
    }

    .cc-empty-title {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        color: var(--cc-ink);
    }

    .cc-empty-copy {
        color: var(--cc-muted);
        font-size: 0.84rem;
        line-height: 1.55;
    }

    .cc-status {
        border-radius: 18px;
        padding: 0.95rem 1rem;
        border: 1px solid transparent;
        margin-bottom: 0.8rem;
        font-size: 0.88rem;
        line-height: 1.55;
    }

    .cc-status-info { background: var(--cc-info-bg); border-color: rgba(48,95,132,0.18); }
    .cc-status-success { background: var(--cc-success-bg); border-color: rgba(29,107,72,0.18); }
    .cc-status-warning { background: var(--cc-warning-bg); border-color: rgba(139,90,22,0.18); }
    .cc-status-danger { background: var(--cc-danger-bg); border-color: rgba(157,62,57,0.18); }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        background: rgba(17,59,74,0.05);
        border-radius: 999px;
        padding: 0.25rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        color: var(--cc-muted);
        font-weight: 600;
        padding: 0.45rem 0.9rem;
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: var(--cc-deep) !important;
        box-shadow: 0 5px 16px rgba(17,59,74,0.10);
    }

    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--cc-ink);
    }

    @media (max-width: 1100px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .cc-hero {
            border-radius: 24px;
            padding: 1.2rem;
        }
    }
</style>
        """,
        unsafe_allow_html=True,
    )


def hero_banner(title: str, copy: str, chips: list[str]) -> None:
    chip_html = "".join(f'<span class="cc-chip">{chip}</span>' for chip in chips)
    st.markdown(
        f"""
<section class="cc-hero">
    <div class="cc-overline">Clinical coding workspace</div>
    <div class="cc-hero-title">{title}</div>
    <div class="cc-hero-copy">{copy}</div>
    <div class="cc-chip-row">{chip_html}</div>
</section>
        """,
        unsafe_allow_html=True,
    )


def section_intro(kicker: str, title: str, copy: str, meta: list[str] | None = None) -> None:
    meta_html = ""
    if meta:
        meta_html = '<div class="cc-meta-row">' + "".join(
            f'<span class="cc-meta-pill">{item}</span>' for item in meta
        ) + "</div>"
    st.markdown(
        f"""
<div class="cc-shell cc-shell-soft">
    <div class="cc-section-kicker">{kicker}</div>
    <h3 class="cc-section-title">{title}</h3>
    <div class="cc-section-copy">{copy}</div>
    {meta_html}
</div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
<div class="cc-empty">
    <div class="cc-empty-icon">{icon}</div>
    <div class="cc-empty-title">{title}</div>
    <div class="cc-empty-copy">{copy}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def status_banner(message: str, tone: str = "info") -> None:
    st.markdown(
        f'<div class="cc-status cc-status-{tone}">{message}</div>',
        unsafe_allow_html=True,
    )
