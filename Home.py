from pathlib import Path

import streamlit as st

import portfolio_skin

st.set_page_config(
    page_title="GRC Streamlit Hub · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

portfolio_skin.apply(hide_sidebar=True)
portfolio_skin.page_header(
    title="GRC Streamlit Hub",
    lede="Local multipage index for #RUNGRCRaleigh club builds. "
    "Each Cloud URL stays a standalone app — no cross-links in those sidebars.",
    kicker="Toolkit",
)

pages_dir = Path(__file__).resolve().parent / "pages"
page_files = sorted(pages_dir.glob("*.py"))

st.header("Tools")
if not page_files:
    st.info("No pages found under /pages.")
else:
    cols = st.columns(2)
    for i, page in enumerate(page_files):
        label = page.stem.split(" - ", 1)[-1]
        with cols[i % 2]:
            st.page_link(str(page), label=label, icon=":material/arrow_forward:")
