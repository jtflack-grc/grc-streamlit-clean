#!/usr/bin/env python3
"""
FAIR Risk Assessment Calculator
==============================

Interactive Factor Analysis of Information Risk (FAIR) calculator
built with Streamlit for real-time risk assessment and visualization.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="FAIR Risk Assessment Calculator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Professional dark theme styling */
    .main-header {
        color: #ffffff;
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        border-bottom: 2px solid rgba(255, 193, 7, 0.3);
        padding-bottom: 0.5rem;
    }

    .stApp {
        background-color: #000000;
        color: #ffffff;
    }

    .stSidebar {
        background-color: #000000;
        color: #ffffff;
    }

    .stButton > button {
        background: linear-gradient(135deg, #ffc107, #7e57c2);
        color: #000000;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 193, 7, 0.3);
        background: linear-gradient(135deg, #ffffff, #ffc107);
    }

    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }

    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }

    .stNumberInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }

    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }

    .stDateInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }

    .stMetric {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        padding: 16px;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }

    .stExpander {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }

    .stDataFrame {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }

    /* Plotly chart styling */
    .js-plotly-plot {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 193, 7, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

def fair_risk_calculator():
    st.markdown('<h1 class="main-header">FAIR Risk Assessment Calculator</h1>', unsafe_allow_html=True)
    st.write("Factor Analysis of Information Risk (FAIR) implementation")
    
    # Input parameters
    st.header("Risk Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        threat_event_frequency = st.slider("Threat Event Frequency (per year)", 0.1, 100.0, 10.0)
        vulnerability = st.slider("Vulnerability (%)", 1, 100, 50)
        threat_capability = st.slider("Threat Capability (1-10)", 1, 10, 5)
        control_strength = st.slider("Control Strength (1-10)", 1, 10, 7)
    
    with col2:
        primary_loss_magnitude = st.number_input("Primary Loss Magnitude ($)", 1000, 1000000, 50000)
        secondary_loss_magnitude = st.number_input("Secondary Loss Magnitude ($)", 1000, 1000000, 10000)
        secondary_loss_frequency = st.slider("Secondary Loss Frequency (%)", 1, 100, 20)
    
    # FAIR calculation
    loss_event_frequency = threat_event_frequency * (vulnerability / 100) * (threat_capability / control_strength)
    primary_loss_exposure = loss_event_frequency * primary_loss_magnitude
    secondary_loss_exposure = loss_event_frequency * (secondary_loss_frequency / 100) * secondary_loss_magnitude
    total_risk_exposure = primary_loss_exposure + secondary_loss_exposure
    
    # Results
    st.header("Risk Assessment Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Loss Event Frequency", f"{loss_event_frequency:.2f}/year")
        st.metric("Primary Loss Exposure", f"${primary_loss_exposure:,.0f}/year")
    
    with col2:
        st.metric("Secondary Loss Exposure", f"${secondary_loss_exposure:,.0f}/year")
        st.metric("Total Risk Exposure", f"${total_risk_exposure:,.0f}/year")
    
    with col3:
        risk_level = "High" if total_risk_exposure > 100000 else "Medium" if total_risk_exposure > 10000 else "Low"
        st.metric("Risk Level", risk_level)
    
    # Risk visualization
    st.header("Risk Visualization")
    
    risk_data = pd.DataFrame({
        'Component': ['Primary Loss', 'Secondary Loss'],
        'Exposure': [primary_loss_exposure, secondary_loss_exposure]
    })
    
    st.bar_chart(risk_data.set_index('Component'))
    
    # Recommendations
    st.header("Risk Treatment Recommendations")
    
    if total_risk_exposure > 100000:
        st.warning("High Risk - Immediate action required")
        st.write("- Implement additional controls")
        st.write("- Consider risk transfer options")
        st.write("- Increase monitoring frequency")
    elif total_risk_exposure > 10000:
        st.info("Medium Risk - Monitor and review")
        st.write("- Review control effectiveness")
        st.write("- Consider incremental improvements")
        st.write("- Regular risk reassessment")
    else:
        st.success("Low Risk - Acceptable level")
        st.write("- Continue current controls")
        st.write("- Periodic review")
        st.write("- Monitor for changes")

if __name__ == "__main__":
    fair_risk_calculator()
