#!/usr/bin/env python3
"""
FAIR Risk Assessment Calculator
==============================

Interactive Factor Analysis of Information Risk (FAIR) calculator
built with Streamlit for real-time risk assessment and visualization.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="FAIR Risk Assessment Calculator · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

_PRESETS = {
    "Custom": None,
    "Phishing mailbox": {
        "tef": 40.0,
        "vuln": 55,
        "threat_cap": 6,
        "control": 5,
        "primary": 25000,
        "secondary": 80000,
        "sec_freq": 35,
    },
    "Ransomware edge": {
        "tef": 8.0,
        "vuln": 40,
        "threat_cap": 8,
        "control": 6,
        "primary": 150000,
        "secondary": 400000,
        "sec_freq": 45,
    },
    "Insider low / slow": {
        "tef": 3.0,
        "vuln": 25,
        "threat_cap": 4,
        "control": 8,
        "primary": 40000,
        "secondary": 20000,
        "sec_freq": 10,
    },
}


def _calc(
    tef: float,
    vuln: int,
    threat_cap: int,
    control: int,
    primary: int,
    secondary: int,
    sec_freq: int,
) -> dict:
    control = max(control, 1)
    lef = tef * (vuln / 100.0) * (threat_cap / control)
    primary_exp = lef * primary
    secondary_exp = lef * (sec_freq / 100.0) * secondary
    total = primary_exp + secondary_exp
    return {
        "lef": lef,
        "primary_exp": primary_exp,
        "secondary_exp": secondary_exp,
        "total": total,
    }


def fair_risk_calculator():
    portfolio_skin.page_header(
        title="FAIR Risk Assessment Calculator",
        lede="Factor Analysis of Information Risk — translate threat frequency, "
        "control strength, and loss magnitude into annualized exposure.",
        kicker="Quantitative risk",
    )

    with st.sidebar:
        st.header("Scenario")
        preset = st.selectbox("Load preset", list(_PRESETS.keys()))
        high_bar = st.number_input("High-risk bar ($/yr)", 10000, 5_000_000, 100000, step=5000)
        med_bar = st.number_input("Medium-risk bar ($/yr)", 1000, high_bar, 10000, step=1000)
        st.caption("Results update live as you move the sliders.")

    p = _PRESETS.get(preset) or {}
    defaults = {
        "tef": 10.0,
        "vuln": 50,
        "threat_cap": 5,
        "control": 7,
        "primary": 50000,
        "secondary": 10000,
        "sec_freq": 20,
    }
    defaults.update({k: v for k, v in p.items() if v is not None})

    tab_params, tab_results, tab_treat, tab_export = st.tabs(
        ["Parameters", "Results", "Treatment", "Export"]
    )

    with tab_params:
        st.subheader("Risk parameters")
        c1, c2 = st.columns(2)
        with c1:
            tef = st.slider("Threat Event Frequency (per year)", 0.1, 100.0, float(defaults["tef"]))
            vuln = st.slider("Vulnerability (%)", 1, 100, int(defaults["vuln"]))
            threat_cap = st.slider("Threat Capability (1-10)", 1, 10, int(defaults["threat_cap"]))
            control = st.slider("Control Strength (1-10)", 1, 10, int(defaults["control"]))
        with c2:
            primary = st.number_input(
                "Primary Loss Magnitude ($)", 1000, 2_000_000, int(defaults["primary"]), step=1000
            )
            secondary = st.number_input(
                "Secondary Loss Magnitude ($)",
                1000,
                2_000_000,
                int(defaults["secondary"]),
                step=1000,
            )
            sec_freq = st.slider(
                "Secondary Loss Frequency (%)", 1, 100, int(defaults["sec_freq"])
            )

    out = _calc(tef, vuln, threat_cap, control, primary, secondary, sec_freq)
    if out["total"] > high_bar:
        risk_level = "High"
    elif out["total"] > med_bar:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    with tab_results:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Loss Event Frequency", f"{out['lef']:.2f}/year")
        m2.metric("Primary Exposure", f"${out['primary_exp']:,.0f}/yr")
        m3.metric("Secondary Exposure", f"${out['secondary_exp']:,.0f}/yr")
        m4.metric("Total / Risk level", f"${out['total']:,.0f}", risk_level)

        chart_df = pd.DataFrame(
            {
                "Component": ["Primary Loss", "Secondary Loss"],
                "Exposure": [out["primary_exp"], out["secondary_exp"]],
            }
        )
        st.bar_chart(chart_df.set_index("Component"))

        # Simple sensitivity: bump control strength ±1
        st.subheader("Control strength sensitivity")
        sens_rows = []
        for c in range(max(1, control - 2), min(10, control + 2) + 1):
            s = _calc(tef, vuln, threat_cap, c, primary, secondary, sec_freq)
            sens_rows.append({"Control Strength": c, "Total Exposure": s["total"]})
        st.line_chart(pd.DataFrame(sens_rows).set_index("Control Strength"))

    with tab_treat:
        if risk_level == "High":
            st.warning("Above high-risk bar — prioritize treatment")
            st.write("- Add or harden controls that cut LEF")
            st.write("- Consider transfer (insurance / contract)")
            st.write("- Increase monitoring on the loss pathway")
        elif risk_level == "Medium":
            st.info("Between medium and high bars — monitor and improve")
            st.write("- Review control effectiveness")
            st.write("- Track residual after incremental improvements")
        else:
            st.success("Below medium bar — accept and revisit on change")
            st.write("- Keep current controls")
            st.write("- Re-run when TEF or magnitudes shift")

    with tab_export:
        export_df = pd.DataFrame(
            [
                {
                    "preset": preset,
                    "threat_event_frequency": tef,
                    "vulnerability_pct": vuln,
                    "threat_capability": threat_cap,
                    "control_strength": control,
                    "primary_loss_magnitude": primary,
                    "secondary_loss_magnitude": secondary,
                    "secondary_loss_frequency_pct": sec_freq,
                    "loss_event_frequency": round(out["lef"], 4),
                    "primary_exposure": round(out["primary_exp"], 2),
                    "secondary_exposure": round(out["secondary_exp"], 2),
                    "total_exposure": round(out["total"], 2),
                    "risk_level": risk_level,
                    "high_bar": high_bar,
                    "medium_bar": med_bar,
                }
            ]
        )
        demo_kit.csv_download(export_df, "fair_risk_scenario.csv", label="Download scenario CSV")


if __name__ == "__main__":
    fair_risk_calculator()
