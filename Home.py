import streamlit as st
import portfolio_skin

st.set_page_config(
    page_title="GRC Streamlit Hub · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)
portfolio_skin.page_header(
    title="GRC Streamlit Hub",
    lede="Pick a tool from the sidebar. Club builds under #RUNGRCRaleigh.",
    kicker="Toolkit",
)
