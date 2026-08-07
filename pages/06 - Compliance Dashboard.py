#!/usr/bin/env python3
"""
GRC Compliance Dashboard
=======================

Sample compliance monitoring and reporting dashboard
built with Streamlit and Plotly for interactive visualization.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="GRC Compliance Dashboard · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)


def _sample_frameworks(seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    base = pd.DataFrame(
        {
            "Framework": ["ISO 27001", "SOC 2", "NIST CSF", "GDPR", "PCI DSS"],
            "Compliance Score": [85, 92, 78, 88, 95],
            "Last Assessment": [
                datetime.now() - timedelta(days=30),
                datetime.now() - timedelta(days=15),
                datetime.now() - timedelta(days=45),
                datetime.now() - timedelta(days=20),
                datetime.now() - timedelta(days=10),
            ],
            "Owner": ["Security", "Compliance", "Security", "Privacy", "Security"],
        }
    )
    jitter = rng.integers(-4, 5, size=len(base))
    base["Compliance Score"] = (base["Compliance Score"] + jitter).clip(55, 99)
    return base


def _sample_controls() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Control Category": [
                "Access Control",
                "Data Protection",
                "Incident Response",
                "Business Continuity",
                "Vendor Management",
            ],
            "Effectiveness": [88, 92, 75, 82, 90],
            "Frameworks": [
                "ISO 27001, SOC 2, NIST CSF",
                "ISO 27001, GDPR, PCI DSS",
                "NIST CSF, SOC 2",
                "ISO 27001, NIST CSF",
                "SOC 2, GDPR",
            ],
        }
    )


def _sample_findings(seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 7)
    frames = ["ISO 27001", "NIST CSF", "SOC 2", "SOC 2", "PCI DSS", "GDPR"]
    findings = [
        "Weak password policy",
        "Missing backup testing",
        "Incomplete vendor assessment",
        "Access review backlog",
        "Encryption gap on secondary storage",
        "Retention schedule not enforced",
    ]
    severities = ["Medium", "High", "Low", "Medium", "High", "Medium"]
    statuses = ["Open", "In Progress", "Closed", "Open", "In Progress", "Open"]
    # shuffle status lightly with seed
    order = rng.permutation(len(findings))
    rows = []
    for i in order:
        rows.append(
            {
                "Finding": findings[i],
                "Framework": frames[i],
                "Severity": severities[i],
                "Status": statuses[i],
                "Due Date": (datetime.now() + timedelta(days=int(rng.integers(7, 60)))).strftime(
                    "%Y-%m-%d"
                ),
            }
        )
    return pd.DataFrame(rows)


def _sample_actions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Action": [
                "Implement multi-factor authentication for all critical systems",
                "Establish quarterly backup testing procedures",
                "Complete vendor risk assessment for new suppliers",
                "Update incident response playbook",
                "Conduct security awareness training",
                "Align retention controls with published schedule",
            ],
            "Related Finding": [
                "Weak password policy",
                "Missing backup testing",
                "Incomplete vendor assessment",
                "Access review backlog",
                "Encryption gap on secondary storage",
                "Retention schedule not enforced",
            ],
            "Priority": ["High", "High", "Medium", "Medium", "Low", "Medium"],
        }
    )


def compliance_dashboard():
    portfolio_skin.page_header(
        title="GRC Compliance Dashboard",
        lede="Interactive sample view for framework scores, control effectiveness, "
        "and audit findings — workshop toy, not a system of record.",
        kicker="Compliance",
    )

    with st.sidebar:
        st.header("Controls")
        seed = demo_kit.seed_controls()
        st.markdown("---")
        st.subheader("Filters")
        frameworks_all = ["ISO 27001", "SOC 2", "NIST CSF", "GDPR", "PCI DSS"]
        selected_frameworks = st.multiselect(
            "Frameworks",
            options=frameworks_all,
            default=frameworks_all,
        )
        threshold = st.slider(
            "Compliance threshold (%)",
            min_value=50,
            max_value=100,
            value=80,
            step=5,
        )
        score_adjust = st.slider(
            "What-if score adjust",
            min_value=-15,
            max_value=15,
            value=0,
            step=1,
            help="Shift all framework / control scores to explore threshold impact.",
        )
        severity_opts = st.multiselect(
            "Finding severity",
            options=["High", "Medium", "Low"],
            default=["High", "Medium", "Low"],
        )
        status_opts = st.multiselect(
            "Finding status",
            options=["Open", "In Progress", "Closed"],
            default=["Open", "In Progress"],
        )
        st.markdown("---")
        st.caption("Sample / mock data only.")

    frameworks_df = _sample_frameworks(seed)
    controls_df = _sample_controls()
    findings_df = _sample_findings(seed)
    actions_df = _sample_actions()

    if not selected_frameworks:
        st.warning("Select at least one framework in the sidebar.")
        return

    view_fw = frameworks_df[frameworks_df["Framework"].isin(selected_frameworks)].copy()
    view_fw["Compliance Score"] = (view_fw["Compliance Score"] + score_adjust).clip(0, 100)

    view_findings = findings_df[
        findings_df["Framework"].isin(selected_frameworks)
        & findings_df["Severity"].isin(severity_opts)
        & findings_df["Status"].isin(status_opts)
    ].copy()

    fw_mask = controls_df["Frameworks"].apply(
        lambda cell: any(fw in cell for fw in selected_frameworks)
    )
    view_controls = controls_df[fw_mask].copy()
    if not view_controls.empty:
        view_controls["Effectiveness"] = (
            view_controls["Effectiveness"] + score_adjust
        ).clip(0, 100)

    related_findings = set(view_findings["Finding"])
    view_actions = actions_df[actions_df["Related Finding"].isin(related_findings)].copy()

    overall_score = float(view_fw["Compliance Score"].mean()) if not view_fw.empty else 0.0
    compliant_count = int((view_fw["Compliance Score"] >= threshold).sum())
    openish = view_findings[view_findings["Status"].isin(["Open", "In Progress"])]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Score", f"{overall_score:.1f}%")
    with col2:
        st.metric("Compliant Frameworks", f"{compliant_count}/{len(view_fw)}")
    with col3:
        next_assessment = view_fw["Last Assessment"].min() + timedelta(days=90)
        st.metric("Oldest cycle + 90d", next_assessment.strftime("%Y-%m-%d"))
    with col4:
        st.metric("Open findings", len(openish))

    tab_overview, tab_findings, tab_actions, tab_export = st.tabs(
        ["Overview", "Findings", "Actions", "Export"]
    )

    with tab_overview:
        st.subheader("Framework Compliance Scores")
        fig = px.bar(
            view_fw,
            x="Framework",
            y="Compliance Score",
            color="Compliance Score",
            color_continuous_scale="RdYlGn",
            title="Compliance Scores by Framework",
            hover_data=["Owner", "Last Assessment"],
        )
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Threshold {threshold}%",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Control Effectiveness")
        if view_controls.empty:
            st.info("No control categories map to the selected frameworks.")
        else:
            fig2 = px.bar(
                view_controls,
                x="Control Category",
                y="Effectiveness",
                color="Effectiveness",
                color_continuous_scale="Blues",
                title="Control effectiveness for selected frameworks",
            )
            fig2.add_hline(y=threshold, line_dash="dash", line_color="orange")
            st.plotly_chart(fig2, use_container_width=True)

    with tab_findings:
        if view_findings.empty:
            st.info("No findings match the current severity / status filters.")
        else:
            st.dataframe(
                view_findings[["Finding", "Framework", "Severity", "Status", "Due Date"]],
                use_container_width=True,
                hide_index=True,
            )
            sev = view_findings["Severity"].value_counts().rename_axis("Severity").reset_index(name="Count")
            st.plotly_chart(
                px.bar(sev, x="Severity", y="Count", title="Findings by severity"),
                use_container_width=True,
            )

    with tab_actions:
        if view_actions.empty:
            st.caption("No related actions for the filtered findings.")
        else:
            for i, (_, row) in enumerate(view_actions.iterrows(), 1):
                st.write(f"{i}. **{row['Priority']}** — {row['Action']}")
                st.caption(f"Related: {row['Related Finding']}")

    with tab_export:
        st.caption("Export the currently filtered sample views.")
        c1, c2, c3 = st.columns(3)
        with c1:
            demo_kit.csv_download(
                view_fw,
                "compliance_frameworks.csv",
                label="Frameworks CSV",
                key="exp_fw",
            )
        with c2:
            demo_kit.csv_download(
                view_findings,
                "compliance_findings.csv",
                label="Findings CSV",
                key="exp_find",
            )
        with c3:
            demo_kit.csv_download(
                view_actions,
                "compliance_actions.csv",
                label="Actions CSV",
                key="exp_act",
            )


if __name__ == "__main__":
    compliance_dashboard()
