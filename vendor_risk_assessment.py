#!/usr/bin/env python3
"""
Vendor Risk Assessment Tool
==========================

Interactive vendor risk evaluation and scoring sample.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Vendor Risk Assessment Tool · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

_CRITERIA = {
    "Financial Risk": ["Financial Stability", "Credit Rating", "Revenue", "Profitability"],
    "Operational Risk": ["Service Quality", "Business Continuity", "Capacity", "Geographic Risk"],
    "Security Risk": ["Security Controls", "Data Protection", "Incident Response", "Compliance"],
    "Strategic Risk": ["Strategic Alignment", "Innovation", "Market Position", "Dependency"],
}

_PRESETS = {
    "Blank / custom": {},
    "SaaS payroll": {
        "Financial Stability": 4,
        "Credit Rating": 4,
        "Revenue": 3,
        "Profitability": 3,
        "Service Quality": 4,
        "Business Continuity": 3,
        "Capacity": 4,
        "Geographic Risk": 2,
        "Security Controls": 3,
        "Data Protection": 3,
        "Incident Response": 2,
        "Compliance": 3,
        "Strategic Alignment": 4,
        "Innovation": 3,
        "Market Position": 3,
        "Dependency": 4,
    },
    "Niche MSP": {
        "Financial Stability": 2,
        "Credit Rating": 2,
        "Revenue": 2,
        "Profitability": 2,
        "Service Quality": 3,
        "Business Continuity": 2,
        "Capacity": 2,
        "Geographic Risk": 3,
        "Security Controls": 2,
        "Data Protection": 2,
        "Incident Response": 2,
        "Compliance": 2,
        "Strategic Alignment": 3,
        "Innovation": 2,
        "Market Position": 2,
        "Dependency": 5,
    },
}


def _tier(overall: float) -> str:
    if overall <= 2:
        return "Tier 1 — Strategic Partner"
    if overall <= 3:
        return "Tier 2 — Preferred Vendor"
    if overall <= 4:
        return "Tier 3 — Standard Vendor"
    return "Tier 4 — High Risk Vendor"


def _level(overall: float) -> str:
    if overall <= 2:
        return "Low"
    if overall <= 3.5:
        return "Medium"
    return "High"


def vendor_risk_assessment():
    portfolio_skin.page_header(
        title="Vendor Risk Assessment Tool",
        lede="Score a sample vendor across financial, operational, security, and strategic factors.",
        kicker="Third-party risk",
    )

    with st.sidebar:
        st.header("Vendor")
        vendor_name = st.text_input("Vendor name", value="Acme Cloud Billing")
        vendor_type = st.selectbox(
            "Vendor type",
            ["Technology", "Professional Services", "Financial", "Manufacturing", "Other"],
        )
        contract_value = st.number_input("Contract value ($)", 1000, 10_000_000, 250000, step=5000)
        contract_duration = st.number_input("Duration (months)", 1, 60, 24)
        preset = st.selectbox("Load score preset", list(_PRESETS.keys()))
        weight_security = st.slider(
            "Security weight",
            0.5,
            2.0,
            1.25,
            0.05,
            help="Emphasize security category in the overall average.",
        )

    defaults = {c: 3 for cats in _CRITERIA.values() for c in cats}
    defaults.update(_PRESETS.get(preset, {}))

    tab_score, tab_results, tab_export = st.tabs(["Score", "Results", "Export"])

    scores: dict[str, dict[str, int]] = {}
    with tab_score:
        for category, criteria in _CRITERIA.items():
            st.subheader(category)
            cols = st.columns(2)
            category_scores = {}
            for i, criterion in enumerate(criteria):
                with cols[i % 2]:
                    category_scores[criterion] = st.slider(
                        criterion,
                        1,
                        5,
                        int(defaults.get(criterion, 3)),
                        key=f"vr_{criterion}",
                    )
            scores[category] = category_scores

    category_averages = {
        cat: float(np.mean(list(vals.values()))) for cat, vals in scores.items()
    }
    weighted = []
    for cat, avg in category_averages.items():
        w = weight_security if cat == "Security Risk" else 1.0
        weighted.append(avg * w)
    # renormalize rough weight
    weight_sum = weight_security + 3.0
    overall = float(sum(weighted) / weight_sum)
    risk_level = _level(overall)
    tier = _tier(overall)

    with tab_results:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Overall score", f"{overall:.2f}/5")
        m2.metric("Risk level", risk_level)
        m3.metric("Contract value", f"${contract_value:,.0f}")
        m4.metric("Suggested tier", tier.split("—")[0].strip())

        cat_df = pd.DataFrame(
            {"Category": list(category_averages.keys()), "Average": list(category_averages.values())}
        )
        st.bar_chart(cat_df.set_index("Category"))
        st.info(f"Recommended tier: {tier}")

        if risk_level == "High":
            st.warning("High risk — tighten monitoring and exit options")
        elif risk_level == "Medium":
            st.info("Medium risk — periodic reassessment")
        else:
            st.success("Low risk — standard oversight")

    with tab_export:
        row = {
            "Vendor Name": vendor_name,
            "Vendor Type": vendor_type,
            "Contract Value": contract_value,
            "Contract Duration": contract_duration,
            "Overall Risk Score": round(overall, 3),
            "Risk Level": risk_level,
            "Vendor Tier": tier,
            "Security Weight": weight_security,
            "Assessment Date": pd.Timestamp.now().isoformat(),
        }
        for category, avg in category_averages.items():
            row[f"{category} Avg"] = round(avg, 3)
            for criterion, score in scores[category].items():
                row[criterion] = score
        demo_kit.csv_download(
            pd.DataFrame([row]),
            f"vendor_assessment_{vendor_name.replace(' ', '_') or 'vendor'}.csv",
            label="Download assessment CSV",
        )


if __name__ == "__main__":
    vendor_risk_assessment()
