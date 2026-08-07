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
    rows = [
        {
            "Finding": "Password minimum length below ISO 27001 A.5.17 guidance",
            "Framework": "ISO 27001",
            "Control Ref": "A.5.17",
            "Severity": "Medium",
            "Status": "Open",
            "Owner": "IAM",
            "Due Date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "Quarterly backup restore test not evidenced (NIST PR.DS)",
            "Framework": "NIST CSF",
            "Control Ref": "PR.DS-04",
            "Severity": "High",
            "Status": "In Progress",
            "Owner": "IT Ops",
            "Due Date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "SOC 2 vendor due-diligence incomplete for Tier-1 SaaS",
            "Framework": "SOC 2",
            "Control Ref": "CC9.2",
            "Severity": "Low",
            "Status": "Closed",
            "Owner": "Procurement",
            "Due Date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "User access review backlog exceeds SOC 2 CC6 cadence",
            "Framework": "SOC 2",
            "Control Ref": "CC6.2",
            "Severity": "Medium",
            "Status": "Open",
            "Owner": "IAM",
            "Due Date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "Cardholder secondary storage missing disk encryption (PCI 3.4)",
            "Framework": "PCI DSS",
            "Control Ref": "3.4",
            "Severity": "High",
            "Status": "In Progress",
            "Owner": "Security",
            "Due Date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "GDPR Article 30 RoPA retention schedule not enforced in DLP",
            "Framework": "GDPR",
            "Control Ref": "Art. 30",
            "Severity": "Medium",
            "Status": "Open",
            "Owner": "Privacy",
            "Due Date": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "Incident tabletop exercise older than 12 months (NIST RS.IM)",
            "Framework": "NIST CSF",
            "Control Ref": "RS.IM-01",
            "Severity": "Medium",
            "Status": "Open",
            "Owner": "SIRT",
            "Due Date": (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "Privileged break-glass accounts lack dual control evidence",
            "Framework": "ISO 27001",
            "Control Ref": "A.8.2",
            "Severity": "High",
            "Status": "Open",
            "Owner": "Security",
            "Due Date": (datetime.now() + timedelta(days=18)).strftime("%Y-%m-%d"),
        },
        # Brownfield / legacy platform additions
        {
            "Finding": "IBM i: QPWDVLDPGM unset — weak password validation on production LPAR",
            "Framework": "ISO 27001",
            "Control Ref": "A.5.17",
            "Severity": "High",
            "Status": "Open",
            "Owner": "IBM i Ops",
            "Due Date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "IBM Z: RACF special attributes over-assigned on CICS region IDs",
            "Framework": "SOC 2",
            "Control Ref": "CC6.1",
            "Severity": "High",
            "Status": "In Progress",
            "Owner": "Mainframe Security",
            "Due Date": (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "JD Edwards: IFS share allows anonymous read of World data libraries",
            "Framework": "PCI DSS",
            "Control Ref": "7.1",
            "Severity": "High",
            "Status": "Open",
            "Owner": "ERP Team",
            "Due Date": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "SAP ECC: sap* / DDIC emergency users not covered by access review cycle",
            "Framework": "SOC 2",
            "Control Ref": "CC6.2",
            "Severity": "Medium",
            "Status": "Open",
            "Owner": "SAP Basis",
            "Due Date": (datetime.now() + timedelta(days=40)).strftime("%Y-%m-%d"),
        },
        {
            "Finding": "AIX LPAR: adopted authority used by batch jobs with no audit journal",
            "Framework": "NIST CSF",
            "Control Ref": "PR.AC-04",
            "Severity": "Medium",
            "Status": "In Progress",
            "Owner": "Unix Team",
            "Due Date": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
        },
    ]
    # Stable shuffle for Resample feel without wiping content quality
    order = rng.permutation(len(rows))
    return pd.DataFrame([rows[i] for i in order])


def _sample_actions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Action": [
                "Raise password minimum length and enforce MFA on admin paths",
                "Schedule and document the next backup restore test",
                "Complete Tier-1 SaaS vendor risk questionnaire package",
                "Close access-review backlog for finance systems",
                "Enable encryption on PCI secondary storage volumes",
                "Wire retention tags into DLP policy for RoPA systems",
                "Run an incident tabletop and file attendance/evidence",
                "Add dual approval workflow for break-glass activation",
                "Configure QPWDVLDPGM and document IBM i password policy evidence",
                "Recertify RACF special attributes on CICS region IDs",
                "Lock down JD Edwards IFS shares and remove anonymous access",
                "Bring SAP ECC emergency users into the quarterly access review",
                "Replace AIX adopted-authority patterns with audited service profiles",
            ],
            "Related Finding": [
                "Password minimum length below ISO 27001 A.5.17 guidance",
                "Quarterly backup restore test not evidenced (NIST PR.DS)",
                "SOC 2 vendor due-diligence incomplete for Tier-1 SaaS",
                "User access review backlog exceeds SOC 2 CC6 cadence",
                "Cardholder secondary storage missing disk encryption (PCI 3.4)",
                "GDPR Article 30 RoPA retention schedule not enforced in DLP",
                "Incident tabletop exercise older than 12 months (NIST RS.IM)",
                "Privileged break-glass accounts lack dual control evidence",
                "IBM i: QPWDVLDPGM unset — weak password validation on production LPAR",
                "IBM Z: RACF special attributes over-assigned on CICS region IDs",
                "JD Edwards: IFS share allows anonymous read of World data libraries",
                "SAP ECC: sap* / DDIC emergency users not covered by access review cycle",
                "AIX LPAR: adopted authority used by batch jobs with no audit journal",
            ],
            "Priority": [
                "High",
                "High",
                "Medium",
                "Medium",
                "High",
                "Medium",
                "Medium",
                "High",
                "High",
                "High",
                "High",
                "Medium",
                "Medium",
            ],
        }
    )


def _build_issue_register(
    view_fw: pd.DataFrame,
    view_controls: pd.DataFrame,
    view_findings: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    """Synthetic issue register: score gaps + weak controls + audit findings."""
    rows: list[dict] = []
    for _, row in view_fw.iterrows():
        score = float(row["Compliance Score"])
        if score < threshold:
            rows.append(
                {
                    "Issue Type": "Framework gap",
                    "Issue": f"{row['Framework']} below threshold ({score:.0f}% < {threshold:.0f}%)",
                    "Framework": row["Framework"],
                    "Ref": "—",
                    "Severity": "High" if score < threshold - 10 else "Medium",
                    "Status": "Open",
                    "Owner": row.get("Owner", ""),
                    "Due Date": "",
                }
            )
    for _, row in view_controls.iterrows():
        eff = float(row["Effectiveness"])
        if eff < threshold:
            rows.append(
                {
                    "Issue Type": "Control effectiveness",
                    "Issue": f"{row['Control Category']} effectiveness {eff:.0f}%",
                    "Framework": row["Frameworks"],
                    "Ref": row["Control Category"],
                    "Severity": "High" if eff < threshold - 10 else "Medium",
                    "Status": "Open",
                    "Owner": "Control owner",
                    "Due Date": "",
                }
            )
    for _, row in view_findings.iterrows():
        rows.append(
            {
                "Issue Type": "Audit finding",
                "Issue": row["Finding"],
                "Framework": row["Framework"],
                "Ref": row.get("Control Ref", ""),
                "Severity": row["Severity"],
                "Status": row["Status"],
                "Owner": row.get("Owner", ""),
                "Due Date": row.get("Due Date", ""),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "Issue Type",
                "Issue",
                "Framework",
                "Ref",
                "Severity",
                "Status",
                "Owner",
                "Due Date",
            ]
        )
    return pd.DataFrame(rows)


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
            default=["Open", "In Progress", "Closed"],
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
    issue_register = _build_issue_register(view_fw, view_controls, view_findings, threshold)

    overall_score = float(view_fw["Compliance Score"].mean()) if not view_fw.empty else 0.0
    compliant_count = int((view_fw["Compliance Score"] >= threshold).sum())
    openish = view_findings[view_findings["Status"].isin(["Open", "In Progress"])]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Score", f"{overall_score:.1f}%")
    with col2:
        st.metric("Compliant Frameworks", f"{compliant_count}/{len(view_fw)}")
    with col3:
        st.metric("Issues in register", len(issue_register))
    with col4:
        st.metric("Open findings", len(openish))

    tab_overview, tab_findings, tab_actions, tab_export = st.tabs(
        ["Overview", "Findings", "Actions", "Export"]
    )

    with tab_overview:
        st.subheader("Compliance issue register")
        if issue_register.empty:
            st.success("No issues for the current filters / threshold.")
        else:
            st.dataframe(issue_register, use_container_width=True, hide_index=True)

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
                view_findings[
                    ["Finding", "Framework", "Control Ref", "Severity", "Status", "Owner", "Due Date"]
                ],
                use_container_width=True,
                hide_index=True,
            )
            sev = (
                view_findings["Severity"]
                .value_counts()
                .rename_axis("Severity")
                .reset_index(name="Count")
            )
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
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            demo_kit.csv_download(
                view_fw, "compliance_frameworks.csv", label="Frameworks CSV", key="exp_fw"
            )
        with c2:
            demo_kit.csv_download(
                view_findings, "compliance_findings.csv", label="Findings CSV", key="exp_find"
            )
        with c3:
            demo_kit.csv_download(
                issue_register, "compliance_issues.csv", label="Issue register CSV", key="exp_iss"
            )
        with c4:
            demo_kit.csv_download(
                view_actions, "compliance_actions.csv", label="Actions CSV", key="exp_act"
            )


if __name__ == "__main__":
    compliance_dashboard()
