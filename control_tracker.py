"""Control Tracker — Day Eight: remediation coordination (not lifecycle status).

GRC Lego block: isolates the idea that control remediation is often a distributed
workflow / handoff problem before it is a compliance problem.
"""

from __future__ import annotations

import datetime
from datetime import timedelta

import demo_kit
import numpy as np
import pandas as pd
import plotly.express as px
import portfolio_skin
import streamlit as st

st.set_page_config(
    page_title="Control Tracker · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

# Coordination states — not Open → In Progress → Closed
COORD_STATES = [
    "Synced",
    "In Between",
    "Handoff",
    "Split Ownership",
    "Telephone Risk",
]

COORD_COLORS = {
    "Synced": "#2e7d32",
    "In Between": "#f57c00",
    "Handoff": "#1976d2",
    "Split Ownership": "#7b1fa2",
    "Telephone Risk": "#c62828",
}

SYSTEMS = [
    "GRC platform",
    "Jira",
    "ServiceNow",
    "Change ticket",
    "Email thread",
    "Meeting notes",
    "Slack / Teams",
    "Spreadsheet",
]


@st.cache_data
def load_control_data():
    """Sample remediation work — current enough to feel live (Aug 2026)."""
    # Anchor "today" for educational demos so Cloud deploys stay coherent.
    today = datetime.date(2026, 8, 12)
    controls = [
        {
            "control_id": "AC-01",
            "control_name": "Access Control Policy",
            "framework": "NIST CSF",
            "category": "Identity Management and Access Control",
            "description": "Establish and maintain access control policies and procedures",
            "remediation_issue": "Annual policy refresh signed; evidence linked in GRC",
            "status": "Compliant",
            "coordination_state": "Synced",
            "current_owner": "IT Security Team",
            "doing_team": "IT Security Team",
            "informed": "GRC, Internal Audit",
            "authoritative_system": "GRC platform",
            "handoff_note": "Single SoT — GRC matches what Security actually updated.",
            "risk_score": 25,
            "last_handoff": (today - timedelta(days=12)).isoformat(),
            "last_update": (today - timedelta(days=5)).isoformat(),
            "next_review": (today + timedelta(days=95)).isoformat(),
            "evidence_count": 5,
            "test_results": "Passed",
        },
        {
            "control_id": "AC-02",
            "control_name": "Account Management",
            "framework": "NIST CSF",
            "category": "Identity Management and Access Control",
            "description": "Manage information system accounts",
            "remediation_issue": "Joiner/mover/leaver exceptions for shared service accounts",
            "status": "Tested",
            "coordination_state": "Handoff",
            "current_owner": "IAM Engineering",
            "doing_team": "IAM Engineering",
            "informed": "IT Security, GRC",
            "authoritative_system": "Jira",
            "handoff_note": "Work lives in Jira; GRC still shows last quarter's narrative.",
            "risk_score": 35,
            "last_handoff": (today - timedelta(days=3)).isoformat(),
            "last_update": (today - timedelta(days=1)).isoformat(),
            "next_review": (today + timedelta(days=40)).isoformat(),
            "evidence_count": 3,
            "test_results": "Passed",
        },
        {
            "control_id": "A.5.1",
            "control_name": "Information Security Policies",
            "framework": "ISO 27001",
            "category": "Information Security Policies",
            "description": "Define information security policy framework",
            "remediation_issue": "Minor editorial updates after management review",
            "status": "Compliant",
            "coordination_state": "Synced",
            "current_owner": "Security Governance",
            "doing_team": "Security Governance",
            "informed": "Legal, GRC",
            "authoritative_system": "GRC platform",
            "handoff_note": "Policy set and GRC control record stay in lockstep.",
            "risk_score": 20,
            "last_handoff": (today - timedelta(days=20)).isoformat(),
            "last_update": (today - timedelta(days=8)).isoformat(),
            "next_review": (today + timedelta(days=110)).isoformat(),
            "evidence_count": 4,
            "test_results": "Passed",
        },
        {
            "control_id": "CC6.1",
            "control_name": "Logical Access Security Software",
            "framework": "SOC 2",
            "category": "Security",
            "description": "Implement logical access security software",
            "remediation_issue": "MFA coverage gap on a subset of SaaS admin consoles",
            "status": "Implemented",
            "coordination_state": "In Between",
            "current_owner": "IT Operations",
            "doing_team": "Cloud Ops",
            "informed": "IT Security, GRC, SOC 2 readiness",
            "authoritative_system": "ServiceNow",
            "handoff_note": "Ticket says 'In Progress'; GRC says 'Implemented' — classic In-Between.",
            "risk_score": 45,
            "last_handoff": (today - timedelta(days=6)).isoformat(),
            "last_update": (today - timedelta(days=2)).isoformat(),
            "next_review": (today + timedelta(days=55)).isoformat(),
            "evidence_count": 2,
            "test_results": "In Progress",
        },
        {
            "control_id": "CC7.1",
            "control_name": "System Operation Monitoring",
            "framework": "SOC 2",
            "category": "Security",
            "description": "Monitor system operations for security events",
            "remediation_issue": "Alert tuning for dormant service accounts on brownfield hosts",
            "status": "In Progress",
            "coordination_state": "Split Ownership",
            "current_owner": "GRC",
            "doing_team": "Security Operations",
            "informed": "IT Operations, Audit",
            "authoritative_system": "Spreadsheet",
            "handoff_note": "GRC owns the finding; SecOps owns the SIEM work; tracker is a shared sheet.",
            "risk_score": 60,
            "last_handoff": (today - timedelta(days=9)).isoformat(),
            "last_update": (today - timedelta(days=4)).isoformat(),
            "next_review": (today + timedelta(days=18)).isoformat(),
            "evidence_count": 1,
            "test_results": "Not Started",
        },
        {
            "control_id": "3.1",
            "control_name": "Network Security Controls",
            "framework": "PCI DSS",
            "category": "Network Security",
            "description": "Implement network security controls",
            "remediation_issue": "Segment rule review after payment-zone change",
            "status": "Tested",
            "coordination_state": "Synced",
            "current_owner": "Network Security",
            "doing_team": "Network Security",
            "informed": "PCI QSA liaison, GRC",
            "authoritative_system": "Change ticket",
            "handoff_note": "Change ticket is authoritative until CAB close; then evidence lands in GRC.",
            "risk_score": 40,
            "last_handoff": (today - timedelta(days=15)).isoformat(),
            "last_update": (today - timedelta(days=7)).isoformat(),
            "next_review": (today + timedelta(days=70)).isoformat(),
            "evidence_count": 3,
            "test_results": "Passed",
        },
        {
            "control_id": "164.308",
            "control_name": "Administrative Safeguards",
            "framework": "HIPAA",
            "category": "Administrative Safeguards",
            "description": "Implement administrative safeguards",
            "remediation_issue": "Workforce sanction procedure not reflected in ops runbooks",
            "status": "Not Implemented",
            "coordination_state": "Telephone Risk",
            "current_owner": "Compliance Team",
            "doing_team": "HR Ops",
            "informed": "Legal, Privacy, GRC",
            "authoritative_system": "Email thread",
            "handoff_note": "Last 'decision' lives in an email nobody can find. Progress = Telephone.",
            "risk_score": 80,
            "last_handoff": (today - timedelta(days=22)).isoformat(),
            "last_update": (today - timedelta(days=19)).isoformat(),
            "next_review": (today - timedelta(days=4)).isoformat(),
            "evidence_count": 0,
            "test_results": "Not Started",
        },
        {
            "control_id": "ID.AM-1",
            "control_name": "Asset Inventory",
            "framework": "NIST CSF",
            "category": "Asset Management",
            "description": "Maintain asset inventory",
            "remediation_issue": "Reconcile CMDB vs. discovered LPARs and appliances",
            "status": "Implemented",
            "coordination_state": "In Between",
            "current_owner": "Asset Management",
            "doing_team": "Platform Engineering",
            "informed": "IT Security, GRC",
            "authoritative_system": "ServiceNow",
            "handoff_note": "Discovery feed updated; CMDB owners still debating authoritative records.",
            "risk_score": 30,
            "last_handoff": (today - timedelta(days=2)).isoformat(),
            "last_update": today.isoformat(),
            "next_review": (today + timedelta(days=60)).isoformat(),
            "evidence_count": 2,
            "test_results": "Passed",
        },
        {
            "control_id": "PR.AC-1",
            "control_name": "Identity Management",
            "framework": "NIST CSF",
            "category": "Identity Management and Access Control",
            "description": "Manage identities and credentials",
            "remediation_issue": "Privileged identity recert for break-glass accounts",
            "status": "Compliant",
            "coordination_state": "Synced",
            "current_owner": "IT Security Team",
            "doing_team": "IT Security Team",
            "informed": "IAM, GRC",
            "authoritative_system": "GRC platform",
            "handoff_note": "Recert campaign closed in GRC with attestation evidence attached.",
            "risk_score": 25,
            "last_handoff": (today - timedelta(days=18)).isoformat(),
            "last_update": (today - timedelta(days=10)).isoformat(),
            "next_review": (today + timedelta(days=100)).isoformat(),
            "evidence_count": 4,
            "test_results": "Passed",
        },
        {
            "control_id": "DE.CM-1",
            "control_name": "Security Monitoring",
            "framework": "NIST CSF",
            "category": "Security Continuous Monitoring",
            "description": "Monitor security events",
            "remediation_issue": "Coverage gap for legacy middleware logging",
            "status": "In Progress",
            "coordination_state": "Telephone Risk",
            "current_owner": "Security Operations",
            "doing_team": "Middleware Ops",
            "informed": "GRC, Audit",
            "authoritative_system": "Meeting notes",
            "handoff_note": "Agreed in standup; no durable ticket yet. Upside-Down territory.",
            "risk_score": 55,
            "last_handoff": (today - timedelta(days=1)).isoformat(),
            "last_update": (today - timedelta(days=1)).isoformat(),
            "next_review": (today + timedelta(days=25)).isoformat(),
            "evidence_count": 1,
            "test_results": "In Progress",
        },
        {
            "control_id": "IBMI-QSEC",
            "control_name": "IBM i QSECURITY & *ALLOBJ Governance",
            "framework": "NIST CSF",
            "category": "Identity Management and Access Control",
            "description": "Govern IBM i system values and special authorities including *ALLOBJ on production LPARs",
            "remediation_issue": "Reduce standing *ALLOBJ; monitor QSECURITY level drift on prod LPARs",
            "status": "In Progress",
            "coordination_state": "Telephone Risk",
            "current_owner": "IBM i Ops",
            "doing_team": "IBM i Ops",
            "informed": "GRC, Mainframe Security, Audit",
            "authoritative_system": "Email thread",
            "handoff_note": "Doing team is clear; SoT is an email chain. GRC is informed, not authoritative.",
            "risk_score": 78,
            "last_handoff": (today - timedelta(days=5)).isoformat(),
            "last_update": (today - timedelta(days=2)).isoformat(),
            "next_review": (today + timedelta(days=14)).isoformat(),
            "evidence_count": 2,
            "test_results": "In Progress",
        },
        {
            "control_id": "ZOS-RACF",
            "control_name": "z/OS RACF Privileged Attribute Recertification",
            "framework": "SOC 2",
            "category": "Security",
            "description": "Recertify RACF SPECIAL / OPERATIONS attributes and CICS region IDs on IBM Z",
            "remediation_issue": "Recert SPECIAL/OPERATIONS; align CICS region ID ownership",
            "status": "Implemented",
            "coordination_state": "In Between",
            "current_owner": "Mainframe Security",
            "doing_team": "Mainframe Security",
            "informed": "GRC, Internal Audit",
            "authoritative_system": "Change ticket",
            "handoff_note": "Change closed on Z; GRC control status still lagging the change record.",
            "risk_score": 72,
            "last_handoff": (today - timedelta(days=8)).isoformat(),
            "last_update": (today - timedelta(days=3)).isoformat(),
            "next_review": (today + timedelta(days=45)).isoformat(),
            "evidence_count": 3,
            "test_results": "Passed",
        },
        {
            "control_id": "ERP-SAPALL",
            "control_name": "SAP ECC / JD Edwards Privileged Access",
            "framework": "ISO 27001",
            "category": "Access Control",
            "description": "Control SAP_ALL, DDIC, and JD Edwards IFS admin roles with monitoring",
            "remediation_issue": "Break-glass for SAP_ALL / DDIC and JDE IFS admin roles",
            "status": "Not Implemented",
            "coordination_state": "Split Ownership",
            "current_owner": "ERP Security",
            "doing_team": "SAP Basis / JDE CNC",
            "informed": "GRC, Internal Audit, Application owners",
            "authoritative_system": "Jira",
            "handoff_note": "ServiceNow has a related RITM; Jira has the sprint work; GRC has the finding.",
            "risk_score": 82,
            "last_handoff": (today - timedelta(days=4)).isoformat(),
            "last_update": (today - timedelta(days=1)).isoformat(),
            "next_review": (today - timedelta(days=2)).isoformat(),
            "evidence_count": 0,
            "test_results": "Not Started",
        },
    ]
    return pd.DataFrame(controls)


def calculate_coordination_metrics(df: pd.DataFrame) -> dict:
    now = datetime.datetime.now()
    return {
        "total": len(df),
        "in_between": len(df[df["coordination_state"] == "In Between"]),
        "telephone": len(df[df["coordination_state"] == "Telephone Risk"]),
        "split": len(df[df["coordination_state"] == "Split Ownership"]),
        "handoff": len(df[df["coordination_state"] == "Handoff"]),
        "synced": len(df[df["coordination_state"] == "Synced"]),
        "systems_in_play": df["authoritative_system"].nunique() if len(df) else 0,
        "avg_risk": float(df["risk_score"].mean()) if len(df) else 0.0,
        "high_risk": len(df[df["risk_score"] >= 70]),
        "overdue_reviews": len(df[pd.to_datetime(df["next_review"]) < now]) if len(df) else 0,
        "doing_vs_owner_mismatch": len(df[df["current_owner"] != df["doing_team"]]) if len(df) else 0,
    }


def main():
    portfolio_skin.page_header(
        title="Control Tracker",
        lede=(
            "Day Eight: remediation coordination — who owns it right now, "
            "and which system is authoritative in the In-Between."
        ),
        kicker="Controls · Coordination",
        club_tag="#RUNGRCRaleigh · Sep 1 @ 6:00pm",
    )

    st.info(
        "**GRC Lego block** — intentionally simple. Not a replacement for ticketing, "
        "GRC platforms, or delivery tools. Isolates one idea: control remediation can be a "
        "**distributed workflow problem** before it is a compliance problem."
    )

    df = load_control_data()

    st.sidebar.header("Controls")
    seed = demo_kit.seed_controls()
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")

    framework_filter = st.sidebar.multiselect(
        "Framework",
        sorted(df["framework"].unique()),
        default=sorted(df["framework"].unique()),
    )
    coord_filter = st.sidebar.multiselect(
        "Coordination state",
        COORD_STATES,
        default=COORD_STATES,
    )
    system_filter = st.sidebar.multiselect(
        "Authoritative system",
        sorted(df["authoritative_system"].unique()),
        default=sorted(df["authoritative_system"].unique()),
    )
    risk_filter = st.sidebar.slider("Risk score range", 0, 100, (0, 100))

    filtered = df[
        df["framework"].isin(framework_filter)
        & df["coordination_state"].isin(coord_filter)
        & df["authoritative_system"].isin(system_filter)
        & (df["risk_score"] >= risk_filter[0])
        & (df["risk_score"] <= risk_filter[1])
    ]

    metrics = calculate_coordination_metrics(filtered)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Dashboard", "Work in Motion", "Analytics", "Coordination Watch", "Export"]
    )

    with tab1:
        st.header("Coordination Dashboard")
        st.caption(
            "Less Open → In Progress → Complete. More: who is doing the work, "
            "who is only informed, and which system is authoritative *right now*."
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active items", metrics["total"], delta=f"{metrics['synced']} Synced")
        c2.metric(
            "In-Between / Handoff",
            metrics["in_between"] + metrics["handoff"],
            delta=f"{metrics['in_between']} In Between",
        )
        c3.metric(
            "Telephone / Split",
            metrics["telephone"] + metrics["split"],
            delta=f"{metrics['telephone']} Telephone Risk",
            delta_color="inverse",
        )
        c4.metric(
            "Systems of record in play",
            metrics["systems_in_play"],
            delta=f"{metrics['doing_vs_owner_mismatch']} owner≠doer",
        )

        col1, col2 = st.columns(2)
        with col1:
            counts = filtered["coordination_state"].value_counts().reindex(COORD_STATES).fillna(0)
            fig = px.pie(
                names=counts.index,
                values=counts.values,
                title="Coordination state (not lifecycle)",
                color=counts.index,
                color_discrete_map=COORD_COLORS,
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            sys_counts = filtered["authoritative_system"].value_counts()
            fig2 = px.bar(
                x=sys_counts.index,
                y=sys_counts.values,
                title="Where authoritative state lives *now*",
                labels={"x": "System", "y": "Items"},
            )
            st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.histogram(
            filtered,
            x="risk_score",
            nbins=10,
            title="Risk score distribution",
            labels={"risk_score": "Risk score", "count": "Items"},
        )
        fig3.add_vline(x=70, line_dash="dash", line_color="red", annotation_text="High risk")
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.header("Work in Motion")
        st.caption(
            "Ask on every row: Who owns it right now? What is the source of truth? "
            "Who is doing vs. informed? How do we stop progress from becoming Telephone?"
        )

        search = st.text_input(
            "Search",
            placeholder="ID, name, team, system, or issue…",
        )
        sort_by = st.selectbox(
            "Sort by",
            [
                "Coordination state",
                "Risk score",
                "Last update",
                "Control ID",
                "Authoritative system",
            ],
        )

        display = filtered
        if search:
            q = search.lower()
            mask = (
                display["control_id"].str.lower().str.contains(q, na=False)
                | display["control_name"].str.lower().str.contains(q, na=False)
                | display["remediation_issue"].str.lower().str.contains(q, na=False)
                | display["current_owner"].str.lower().str.contains(q, na=False)
                | display["doing_team"].str.lower().str.contains(q, na=False)
                | display["authoritative_system"].str.lower().str.contains(q, na=False)
            )
            display = display[mask]

        sort_map = {
            "Coordination state": ("coordination_state", True),
            "Risk score": ("risk_score", False),
            "Last update": ("last_update", False),
            "Control ID": ("control_id", True),
            "Authoritative system": ("authoritative_system", True),
        }
        col, asc = sort_map[sort_by]
        display = display.sort_values(col, ascending=asc)

        for _, row in display.iterrows():
            label = (
                f"{row['control_id']} — {row['control_name']} · "
                f"{row['coordination_state']} · SoT: {row['authoritative_system']}"
            )
            with st.expander(label):
                left, right = st.columns([2, 1])
                with left:
                    st.write(f"**Framework:** {row['framework']} · **Category:** {row['category']}")
                    st.write(f"**Remediation issue:** {row['remediation_issue']}")
                    st.write(f"**Current owner (now):** {row['current_owner']}")
                    st.write(f"**Doing the work:** {row['doing_team']}")
                    st.write(f"**Informed:** {row['informed']}")
                    st.write(f"**Authoritative system (this moment):** {row['authoritative_system']}")
                    st.write(f"**Handoff note:** {row['handoff_note']}")
                with right:
                    risk_color = (
                        "red"
                        if row["risk_score"] >= 70
                        else "orange"
                        if row["risk_score"] >= 50
                        else "green"
                    )
                    st.metric("Risk score", row["risk_score"], delta=f"{risk_color} band")
                    st.write(f"**Lifecycle label (legacy):** {row['status']}")
                    st.write(f"**Test results:** {row['test_results']}")
                    st.write(f"**Last handoff:** {row['last_handoff']}")
                    st.write(f"**Last update:** {row['last_update']}")
                    st.write(f"**Next review:** {row['next_review']}")
                    st.write(f"**Evidence count:** {row['evidence_count']}")

                    mismatch = row["current_owner"] != row["doing_team"]
                    if mismatch:
                        st.warning("Owner ≠ doing team — seam risk.")
                    if row["coordination_state"] in ("Telephone Risk", "Split Ownership"):
                        st.error("Coordination friction — durable SoT unclear or fragmented.")
                    elif row["coordination_state"] == "Synced":
                        st.success("Authoritative state and ownership line up.")

    with tab3:
        st.header("Analytics")
        col1, col2 = st.columns(2)
        with col1:
            by_fw = (
                filtered.groupby("framework")["coordination_state"]
                .apply(lambda s: (s != "Synced").sum())
                .reset_index(name="Not Synced")
            )
            fig = px.bar(
                by_fw,
                x="framework",
                y="Not Synced",
                title="Items not Synced by framework",
                labels={"framework": "Framework"},
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.box(
                filtered,
                x="authoritative_system",
                y="risk_score",
                title="Risk by authoritative system",
                labels={"authoritative_system": "System", "risk_score": "Risk score"},
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Handoff activity (simulated weekly pulse)")
        rng = np.random.default_rng(seed)
        weeks = pd.date_range(end=datetime.date(2026, 8, 12), periods=16, freq="W")
        pulse = []
        for i, w in enumerate(weeks):
            base = 4 + (i % 5)
            pulse.append(
                {
                    "Week": w,
                    "Handoffs recorded": max(0, int(base + rng.normal(0, 1.2))),
                    "Telephone-risk flags": max(0, int(1 + rng.integers(0, 3))),
                }
            )
        pulse_df = pd.DataFrame(pulse)
        fig = px.line(
            pulse_df,
            x="Week",
            y=["Handoffs recorded", "Telephone-risk flags"],
            title="Coordination pulse (demo)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("Coordination Watch")
        st.caption(
            "Governance breakdowns rarely happen only in Open or Closed — "
            "they show up in the nebulous In-Between."
        )

        friction = filtered[
            filtered["coordination_state"].isin(
                ["Telephone Risk", "Split Ownership", "In Between", "Handoff"]
            )
        ].sort_values("risk_score", ascending=False)

        if len(friction):
            st.warning(f"{len(friction)} items with active coordination friction")
            for _, row in friction.iterrows():
                with st.expander(
                    f"{row['control_id']} — {row['control_name']} "
                    f"({row['coordination_state']}, risk {row['risk_score']})"
                ):
                    st.write(f"**Issue:** {row['remediation_issue']}")
                    st.write(f"**Owner now:** {row['current_owner']} · **Doing:** {row['doing_team']}")
                    st.write(f"**Informed:** {row['informed']}")
                    st.write(f"**Authoritative system:** {row['authoritative_system']}")
                    st.write(f"**Why it matters:** {row['handoff_note']}")
                    st.markdown(
                        "- Who owns it **right now**?\n"
                        "- What system is the **source of truth** for current state?\n"
                        "- Who is **doing** vs. merely **informed**?\n"
                        "- How do we keep progress from becoming a game of **Telephone**?"
                    )
        else:
            st.success("No coordination friction in the current filter set.")

        overdue = filtered[pd.to_datetime(filtered["next_review"]) < datetime.datetime.now()]
        if len(overdue):
            st.error(f"{len(overdue)} items past next-review date")
            for _, row in overdue.iterrows():
                days = (datetime.datetime.now() - pd.to_datetime(row["next_review"])).days
                st.write(
                    f"• {row['control_id']} — {row['control_name']} "
                    f"({days} days past review) · SoT: {row['authoritative_system']}"
                )
        else:
            st.success("Next-review dates are current for the filtered set.")

        high = filtered[filtered["risk_score"] >= 70]
        if len(high):
            st.subheader("High-risk items (score ≥ 70)")
            st.dataframe(
                high[
                    [
                        "control_id",
                        "control_name",
                        "coordination_state",
                        "authoritative_system",
                        "current_owner",
                        "doing_team",
                        "risk_score",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

    with tab5:
        st.header("Export & notes")
        st.markdown(
            """
**If you try something like this in your own org, ask:**

When a control issue is actively being worked, can you tell where the
**authoritative state** actually lives — and who is responsible for updating it as it moves?

Most governance breakdowns don’t happen in an “Open” or “Closed” state.
They happen in the **In-Between**.
            """
        )
        demo_kit.csv_download(
            filtered.copy(),
            "control_coordination_filtered.csv",
            label="Download filtered view",
        )
        if st.button("Refresh"):
            st.rerun()

        summary = pd.DataFrame(
            {
                "Metric": [
                    "Active items",
                    "Synced",
                    "In Between",
                    "Handoff",
                    "Split Ownership",
                    "Telephone Risk",
                    "Owner ≠ doing team",
                    "Systems of record in play",
                    "High risk (≥70)",
                    "Past next review",
                ],
                "Value": [
                    metrics["total"],
                    metrics["synced"],
                    metrics["in_between"],
                    metrics["handoff"],
                    metrics["split"],
                    metrics["telephone"],
                    metrics["doing_vs_owner_mismatch"],
                    metrics["systems_in_play"],
                    metrics["high_risk"],
                    metrics["overdue_reviews"],
                ],
            }
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
