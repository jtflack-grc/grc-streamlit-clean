"""Shared portfolio skin for Streamlit GRC tools.

Tokens mirror https://jtflack-grc.github.io/portfolio/ (ink / green / IBM Plex).
Import and call apply() once after st.set_page_config().
"""

from __future__ import annotations

import streamlit as st

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
  --ink: #050a08;
  --panel: #09110d;
  --panel2: #0c1711;
  --green: #7fffb2;
  --green2: #38e881;
  --muted: #91aa9b;
  --line: rgba(105, 255, 164, 0.16);
  --amber: #f2b84b;
  --white: #e8f4ec;
  --font-sans: "IBM Plex Sans", -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

html, body, .stApp,
.stApp p, .stApp label, .stApp li, .stApp a,
.stApp div, .stApp button, .stApp input, .stApp textarea,
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"],
[data-testid="stText"],
[data-baseweb],
.stSlider, .stNumberInput, .stSelectbox, .stTextInput {
  font-family: var(--font-sans) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Preserve Material icon font (global span override was showing icon names as text) */
[data-testid="stIconMaterial"] {
  font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
  font-style: normal !important;
  font-weight: 400 !important;
  letter-spacing: normal !important;
  text-transform: none !important;
  -webkit-font-smoothing: antialiased;
}

.stApp {
  background: var(--ink);
  color: var(--white);
  font-weight: 400;
  line-height: 1.55;
  letter-spacing: 0;
}

.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(rgba(127, 255, 178, 0.018) 1px, transparent 1px);
  background-size: 100% 4px;
  z-index: 0;
}

[data-testid="stAppViewContainer"] > .main,
[data-testid="stHeader"] {
  background: transparent;
}

[data-testid="stHeader"] {
  background: rgba(5, 10, 8, 0.86) !important;
  backdrop-filter: blur(12px);
}

section[data-testid="stSidebar"] {
  background: var(--panel) !important;
  border-right: 1px solid var(--line);
}

.block-container {
  padding-top: 3.5rem !important;
  padding-bottom: 3rem;
  max-width: 1100px;
}

/* Brand lockup — matches portfolio wordmark */
.portfolio-top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1.25rem;
  margin: 0 0 1.35rem 0;
  padding: 0.35rem 0 1rem 0;
  border-bottom: 1px solid var(--line);
  overflow: visible;
}

.portfolio-brand {
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  overflow: visible;
  padding-bottom: 0.2rem;
}

.brand-wordmark {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.28em;
  padding: 0.1rem 0.05rem 0.45rem;
  font-family: var(--font-mono) !important;
  font-weight: 600;
  font-size: 1.15rem;
  letter-spacing: 0.035em;
  color: var(--green);
  text-shadow:
    0 0 7px rgba(127, 255, 178, 0.42),
    0 0 18px rgba(56, 232, 129, 0.18);
  white-space: nowrap;
  overflow: visible;
}

.brand-wordmark strong {
  position: relative;
  font: inherit;
  color: inherit;
}

.brand-wordmark strong::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: -0.34rem;
  height: 2px;
  background: var(--amber);
  box-shadow: 0 0 8px rgba(242, 184, 75, 0.55);
}

.portfolio-context {
  margin: 0;
  font-family: var(--font-mono) !important;
  font-weight: 500;
  font-size: 0.78rem;
  line-height: 1;
  letter-spacing: 0.06em;
  color: var(--green2);
}

.portfolio-kicker {
  font-family: var(--font-mono) !important;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--green2);
  margin: 0.35rem 0 0.55rem 0;
}

.portfolio-title {
  font-family: var(--font-sans) !important;
  font-size: clamp(1.85rem, 3.2vw, 2.55rem);
  font-weight: 300 !important;
  line-height: 1.08;
  letter-spacing: -0.048em;
  color: var(--white);
  margin: 0 0 0.65rem 0;
}

.portfolio-lede {
  font-family: var(--font-sans) !important;
  font-weight: 400;
  color: var(--muted);
  font-size: 1.05rem;
  line-height: 1.65;
  max-width: 42rem;
  margin: 0 0 1.5rem 0;
}

h1, h2, h3, h4 {
  font-family: var(--font-sans) !important;
  color: var(--white) !important;
}

h1 {
  font-weight: 300 !important;
  letter-spacing: -0.048em !important;
  line-height: 1.08 !important;
}

h2 {
  font-size: 1.15rem !important;
  font-weight: 500 !important;
  letter-spacing: -0.01em !important;
  border-left: 2px solid var(--green2);
  padding-left: 0.65rem;
  margin-top: 1.6rem !important;
}

p, label, .stMarkdown, .stCaption {
  color: var(--white);
  font-family: var(--font-sans) !important;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
  font-family: var(--font-sans) !important;
  font-weight: 500 !important;
  font-size: 0.92rem !important;
  letter-spacing: 0.01em;
  color: var(--white) !important;
}

[data-testid="stMetric"] {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 0.85rem 1rem;
}

[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.72rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

[data-testid="stMetricValue"] {
  color: var(--white) !important;
  font-family: var(--font-sans) !important;
  font-weight: 300 !important;
  letter-spacing: -0.02em;
}

div[data-baseweb="input"] > div,
div[data-baseweb="base-input"],
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] {
  background-color: var(--panel2) !important;
  border-color: var(--line) !important;
  border-radius: 4px !important;
  font-family: var(--font-sans) !important;
}

.stSlider [data-baseweb="slider"] div[role="slider"] {
  background-color: var(--green2) !important;
}

.stButton > button {
  background: var(--green2) !important;
  color: #021008 !important;
  border: 1px solid transparent !important;
  border-radius: 4px !important;
  font-family: var(--font-sans) !important;
  font-weight: 600 !important;
  font-size: 0.76rem !important;
  letter-spacing: 0.055em !important;
  padding: 0.55rem 1.1rem !important;
  box-shadow: none !important;
}

.stButton > button:hover {
  background: var(--green) !important;
  border-color: var(--green) !important;
  transform: none !important;
  box-shadow: none !important;
}

div[data-testid="stAlert"] {
  border-radius: 4px;
  border: 1px solid var(--line);
  background: var(--panel);
  font-family: var(--font-sans) !important;
}

[data-testid="stExpander"] {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 4px;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
  border: 1px solid var(--line);
  border-radius: 4px;
}

div[data-testid="stDecoration"] {
  background: linear-gradient(90deg, var(--green2), transparent) !important;
}

footer { visibility: hidden; }
"""


_HIDE_SIDEBAR_CSS = """
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"],
button[kind="headerNoPadding"] {
  display: none !important;
  visibility: hidden !important;
  pointer-events: none !important;
}

section[data-testid="stSidebar"] {
  display: none !important;
}
"""


def apply(*, hide_sidebar: bool = False) -> None:
    """Inject portfolio CSS. Call once after st.set_page_config.

    hide_sidebar=True for single-pane tools with no sidebar controls (e.g. FAIR).
    """
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap"
          rel="stylesheet"
        />
        """,
        unsafe_allow_html=True,
    )
    css = _CSS + (_HIDE_SIDEBAR_CSS if hide_sidebar else "")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_header(
    title: str,
    lede: str,
    kicker: str = "Quantitative risk",
    club_tag: str = "#RUNGRCRaleigh",
) -> None:
    """Brand wordmark + hashtag bar, then title."""
    st.markdown(
        f"""
        <div class="portfolio-top">
          <div class="portfolio-brand">
            <span class="brand-wordmark"><strong>i</strong> on GRC</span>
          </div>
          <p class="portfolio-context">{club_tag}</p>
        </div>
        <div class="portfolio-kicker">{kicker}</div>
        <h1 class="portfolio-title">{title}</h1>
        <p class="portfolio-lede">{lede}</p>
        """,
        unsafe_allow_html=True,
    )
