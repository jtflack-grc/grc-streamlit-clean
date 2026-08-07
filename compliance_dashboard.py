#!/usr/bin/env python3
"""
GRC Compliance Dashboard
=======================

Sample compliance monitoring and reporting dashboard
built with Streamlit and Plotly for interactive visualization.
"""

import streamlit as st
import portfolio_skin
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="GRC Compliance Dashboard · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)


def _sample_frameworks() -> pd.DataFrame:
    return pd.DataFrame(
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
            "Owner": [
                "Security",
                "Compliance",
                "Security",
                "Privacy",
                "Security",
            ],
        }
    )


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


def _sample_findings() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Finding": [
                "Weak password policy",
                "Missing backup testing",
                "Incomplete vendor assessment",
                "Access review backlog",
                "Encryption gap on secondary storage",
            ],
            "Framework": [
                "ISO 27001",
                "NIST CSF",
                "SOC 2",
                "SOC 2",
                "PCI DSS",
            ],
            "Severity": ["Medium", "High", "Low", "Medium", "High"],
            "Status": ["Open", "In Progress", "Closed", "Open", "In Progress"],
            "Due Date": [
                "2024-02-15",
                "2024-01-30",
                "2024-01-15",
                "2024-03-01",
                "2024-02-28",
            ],
        }
    )


def _sample_actions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Action": [
                "Implement multi-factor authentication for all critical systems",
                "Establish quarterly backup testing procedures",
                "Complete vendor risk assessment for new suppliers",
                "Update incident response playbook",
                "Conduct security awareness training",
            ],
            "Related Finding": [
                "Weak password policy",
                "Missing backup testing",
                "Incomplete vendor assessment",
                "Access review backlog",
                "Encryption gap on secondary storage",
            ],
            "Priority": ["High", "High", "Medium", "Medium", "Low"],
        }
    )


def compliance_dashboard():
    portfolio_skin.page_header(
        title="GRC Compliance Dashboard",
        lede="Interactive sample view for framework scores, control effectiveness, "
        "and audit findings — workshop toy, not a system of record.",
        kicker="Compliance",
    )

    frameworks_df = _sample_frameworks()
    controls_df = _sample_controls()
    findings_df = _sample_findings()
    actions_df = _sample_actions()

    with st.sidebar:
        st.header("Filters")
        st.caption("Drive the main view with these controls.")

        selected_frameworks = st.multiselect(
            "Frameworks",
            options=frameworks_df["Framework"].tolist(),
            default=frameworks_df["Framework"].tolist(),
        )
        threshold = st.slider(
            "Compliance threshold (%)",
            min_value=50,
            max_value=100,
            value=80,
            step=5,
            help="Scores at or above this count as compliant.",
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

    if not selected_frameworks:
        st.warning("Select at least one framework in the sidebar.")
        return

    view_fw = frameworks_df[frameworks_df["Framework"].isin(selected_frameworks)].copy()
    view_findings = findings_df[
        findings_df["Framework"].isin(selected_frameworks)
        & findings_df["Severity"].isin(severity_opts)
        & findings_df["Status"].isin(status_opts)
    ].copy()

    # Controls tagged with any selected framework
    fw_mask = controls_df["Frameworks"].apply(
        lambda cell: any(fw in cell for fw in selected_frameworks)
    )
    view_controls = controls_df[fw_mask].copy()

    related_findings = set(view_findings["Finding"])
    view_actions = actions_df[actions_df["Related Finding"].isin(related_findings)].copy()
    if view_actions.empty and not view_findings.empty:
        view_actions = actions_df.head(0)
    elif view_findings.empty:
        view_actions = actions_df.head(0)

    overall_score = float(view_fw["Compliance Score"].mean()) if not view_fw.empty else 0.0
    compliant_count = int((view_fw["Compliance Score"] >= threshold).sum())
    openish = view_findings[view_findings["Status"].isin(["Open", "In Progress"])]

    st.header("Overall Compliance Status")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Score", f"{overall_score:.1f}%")
    with col2:
        st.metric(
            "Compliant Frameworks",
            f"{compliant_count}/{len(view_fw)}",
            help=f"At or above {threshold}% threshold",
        )
    with col3:
        next_assessment = view_fw["Last Assessment"].min() + timedelta(days=90)
        st.metric("Oldest cycle + 90d", next_assessment.strftime("%Y-%m-%d"))
    with col4:
        st.metric("Open findings (filtered)", len(openish))

    st.header("Framework Compliance Scores")
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

    st.header("Control Effectiveness")
    if view_controls.empty:
        st.info("No control categories map to the selected frameworks.")
    else:
        fig2 = px.bar(
            view_controls,
            x="Control Category",
            y="Effectiveness",
            color="Effectiveness",
            color_continuous_scale="Blues",
            title="Control Effectiveness (categories tagged to selected frameworks)",
        )
        fig2.add_hline(y=threshold, line_dash="dash", line_color="orange")
        st.plotly_chart(fig2, use_container_width=True)

    st.header("Recent Audit Findings")
    if view_findings.empty:
        st.info("No findings match the current severity / status filters.")
    else:
        st.dataframe(
            view_findings[
                ["Finding", "Framework", "Severity", "Status", "Due Date"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.header("Action Items")
    if view_actions.empty:
        st.caption("No related actions for the filtered findings.")
    else:
        for i, (_, row) in enumerate(view_actions.iterrows(), 1):
            st.write(f"{i}. **{row['Priority']}** — {row['Action']}")
            st.caption(f"Related: {row['Related Finding']}")


if __name__ == "__main__":
    compliance_dashboard()
