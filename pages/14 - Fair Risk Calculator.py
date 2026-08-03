#!/usr/bin/env python3
"""
FAIR Risk Assessment Calculator
==============================

Interactive Factor Analysis of Information Risk (FAIR) calculator
built with Streamlit for real-time risk assessment and visualization.
"""

import streamlit as st
import pandas as pd

import portfolio_skin

st.set_page_config(
    page_title="FAIR Risk Assessment Calculator · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

portfolio_skin.apply(hide_sidebar=True)


def fair_risk_calculator():
    portfolio_skin.page_header(
        title="FAIR Risk Assessment Calculator",
        lede="Factor Analysis of Information Risk — translate threat frequency, "
        "control strength, and loss magnitude into annualized exposure.",
        kicker="Quantitative risk",
    )

    st.header("Risk Parameters")

    col1, col2 = st.columns(2)

    with col1:
        threat_event_frequency = st.slider(
            "Threat Event Frequency (per year)", 0.1, 100.0, 10.0
        )
        vulnerability = st.slider("Vulnerability (%)", 1, 100, 50)
        threat_capability = st.slider("Threat Capability (1-10)", 1, 10, 5)
        control_strength = st.slider("Control Strength (1-10)", 1, 10, 7)

    with col2:
        primary_loss_magnitude = st.number_input(
            "Primary Loss Magnitude ($)", 1000, 1000000, 50000
        )
        secondary_loss_magnitude = st.number_input(
            "Secondary Loss Magnitude ($)", 1000, 1000000, 10000
        )
        secondary_loss_frequency = st.slider(
            "Secondary Loss Frequency (%)", 1, 100, 20
        )

    loss_event_frequency = (
        threat_event_frequency
        * (vulnerability / 100)
        * (threat_capability / control_strength)
    )
    primary_loss_exposure = loss_event_frequency * primary_loss_magnitude
    secondary_loss_exposure = (
        loss_event_frequency
        * (secondary_loss_frequency / 100)
        * secondary_loss_magnitude
    )
    total_risk_exposure = primary_loss_exposure + secondary_loss_exposure

    st.header("Risk Assessment Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Loss Event Frequency", f"{loss_event_frequency:.2f}/year")
        st.metric("Primary Loss Exposure", f"${primary_loss_exposure:,.0f}/year")

    with col2:
        st.metric(
            "Secondary Loss Exposure", f"${secondary_loss_exposure:,.0f}/year"
        )
        st.metric("Total Risk Exposure", f"${total_risk_exposure:,.0f}/year")

    with col3:
        risk_level = (
            "High"
            if total_risk_exposure > 100000
            else "Medium"
            if total_risk_exposure > 10000
            else "Low"
        )
        st.metric("Risk Level", risk_level)

    st.header("Risk Visualization")

    risk_data = pd.DataFrame(
        {
            "Component": ["Primary Loss", "Secondary Loss"],
            "Exposure": [primary_loss_exposure, secondary_loss_exposure],
        }
    )

    st.bar_chart(risk_data.set_index("Component"))

    st.header("Risk Treatment Recommendations")

    if total_risk_exposure > 100000:
        st.warning("High Risk — Immediate action required")
        st.write("- Implement additional controls")
        st.write("- Consider risk transfer options")
        st.write("- Increase monitoring frequency")
    elif total_risk_exposure > 10000:
        st.info("Medium Risk — Monitor and review")
        st.write("- Review control effectiveness")
        st.write("- Consider incremental improvements")
        st.write("- Regular risk reassessment")
    else:
        st.success("Low Risk — Acceptable level")
        st.write("- Continue current controls")
        st.write("- Periodic review")
        st.write("- Monitor for changes")


if __name__ == "__main__":
    fair_risk_calculator()
