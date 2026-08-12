import streamlit as st
import demo_kit
import portfolio_skin
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Control Gap Analysis · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"]
STATUS_ORDER = ["Open", "In Progress", "Remediated"]
SEVERITY_WEIGHT = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}


@st.cache_data
def load_framework_data():
    """Load sample framework and control catalog."""
    frameworks = [
        {"id": "ISO27001", "name": "ISO 27001", "version": "2022", "type": "Information Security"},
        {"id": "SOC2", "name": "SOC 2", "version": "2017", "type": "Trust Services"},
        {"id": "NIST", "name": "NIST CSF", "version": "2.0", "type": "Cybersecurity"},
        {"id": "PCI", "name": "PCI DSS", "version": "4.0", "type": "Payment Security"},
        {"id": "HIPAA", "name": "HIPAA", "version": "1996", "type": "Healthcare"},
    ]

    controls = [
        {"id": "ISO-A.5.1", "name": "Information Security Policy", "framework": "ISO27001", "domain": "Policies", "category": "Governance"},
        {"id": "ISO-A.6.1", "name": "Information Security Roles", "framework": "ISO27001", "domain": "Organization", "category": "Governance"},
        {"id": "ISO-A.7.1", "name": "Screening", "framework": "ISO27001", "domain": "Human Resources", "category": "People"},
        {"id": "ISO-A.8.1", "name": "Inventory of Assets", "framework": "ISO27001", "domain": "Asset Management", "category": "Assets"},
        {"id": "ISO-A.9.1", "name": "Access Control Policy", "framework": "ISO27001", "domain": "Access Control", "category": "Access"},
        {"id": "ISO-A.10.1", "name": "Cryptographic Controls Policy", "framework": "ISO27001", "domain": "Cryptography", "category": "Protection"},
        {"id": "ISO-A.11.1", "name": "Physical Security Perimeters", "framework": "ISO27001", "domain": "Physical Security", "category": "Physical"},
        {"id": "ISO-A.12.1", "name": "Operational Procedures", "framework": "ISO27001", "domain": "Operations", "category": "Operations"},
        {"id": "ISO-A.13.1", "name": "Network Security Management", "framework": "ISO27001", "domain": "Communications", "category": "Network"},
        {"id": "ISO-A.14.1", "name": "Security Requirements", "framework": "ISO27001", "domain": "System Development", "category": "Development"},
        {"id": "SOC-CC1", "name": "Control Environment", "framework": "SOC2", "domain": "Control Environment", "category": "Governance"},
        {"id": "SOC-CC2", "name": "Communication and Information", "framework": "SOC2", "domain": "Communication", "category": "Governance"},
        {"id": "SOC-CC3", "name": "Risk Assessment", "framework": "SOC2", "domain": "Risk Assessment", "category": "Risk"},
        {"id": "SOC-CC4", "name": "Monitoring Activities", "framework": "SOC2", "domain": "Monitoring", "category": "Monitoring"},
        {"id": "SOC-CC5", "name": "Control Activities", "framework": "SOC2", "domain": "Control Activities", "category": "Controls"},
        {"id": "SOC-CC6", "name": "Logical and Physical Access", "framework": "SOC2", "domain": "Access Control", "category": "Access"},
        {"id": "SOC-CC7", "name": "System Operations", "framework": "SOC2", "domain": "Operations", "category": "Operations"},
        {"id": "SOC-CC8", "name": "Change Management", "framework": "SOC2", "domain": "Change Management", "category": "Change"},
        {"id": "SOC-CC9", "name": "Risk Mitigation", "framework": "SOC2", "domain": "Risk Mitigation", "category": "Risk"},
        {"id": "NIST-ID.AM-1", "name": "Asset Inventory", "framework": "NIST", "domain": "Identify", "category": "Asset Management"},
        {"id": "NIST-ID.AM-2", "name": "Software Platforms", "framework": "NIST", "domain": "Identify", "category": "Asset Management"},
        {"id": "NIST-ID.AM-3", "name": "Organizational Communication", "framework": "NIST", "domain": "Identify", "category": "Business Environment"},
        {"id": "NIST-PR.AC-1", "name": "Identity Management", "framework": "NIST", "domain": "Protect", "category": "Access Control"},
        {"id": "NIST-PR.AC-2", "name": "Physical Access Control", "framework": "NIST", "domain": "Protect", "category": "Access Control"},
        {"id": "NIST-PR.AC-3", "name": "Remote Access", "framework": "NIST", "domain": "Protect", "category": "Access Control"},
        {"id": "NIST-DE.AE-1", "name": "Baseline Network Operations", "framework": "NIST", "domain": "Detect", "category": "Anomalies"},
        {"id": "NIST-RS.RP-1", "name": "Response Plan Execution", "framework": "NIST", "domain": "Respond", "category": "Response Planning"},
        {"id": "NIST-RC.RP-1", "name": "Recovery Plan Execution", "framework": "NIST", "domain": "Recover", "category": "Recovery Planning"},
    ]

    return pd.DataFrame(frameworks), pd.DataFrame(controls)


def _base_gaps():
    """Canonical sample gap register (illustrative, refreshed Aug 2026)."""
    return [
        {
            "id": "GAP-001", "control_id": "ISO-A.8.1", "control_name": "Inventory of Assets", "framework": "ISO27001",
            "gap_type": "Missing", "severity": "Critical", "risk_score": 95, "status": "Open",
            "description": "No comprehensive asset inventory exists for IT infrastructure",
            "business_impact": "Unable to track and protect critical assets",
            "current_state": "Partial CMDB; cloud and midrange gaps",
            "target_state": "Automated asset discovery and tracking",
            "remediation_priority": "Immediate", "estimated_cost": 50000, "estimated_effort": "3 months",
            "owner": "IT Operations", "platform": "Mixed estate",
            "created_date": "2025-10-15", "target_date": "2026-09-30",
        },
        {
            "id": "GAP-002", "control_id": "SOC-CC6", "control_name": "Logical and Physical Access", "framework": "SOC2",
            "gap_type": "Incomplete", "severity": "Medium", "risk_score": 28, "status": "Remediated",
            "description": "MFA not implemented for all privileged accounts",
            "business_impact": "High risk of unauthorized access to critical systems",
            "current_state": "MFA on 100% of privileged cloud/AD accounts",
            "target_state": "MFA on 100% of privileged accounts",
            "remediation_priority": "Immediate", "estimated_cost": 25000, "estimated_effort": "2 months",
            "owner": "Security Team", "platform": "Cloud / AD",
            "created_date": "2025-10-20", "target_date": "2026-01-31",
        },
        {
            "id": "GAP-003", "control_id": "ISO-A.9.1", "control_name": "Access Control Policy", "framework": "ISO27001",
            "gap_type": "Ineffective", "severity": "High", "risk_score": 72, "status": "In Progress",
            "description": "Access control policy not consistently enforced across systems",
            "business_impact": "Inconsistent access controls increase security risk",
            "current_state": "Enforcement live for AD/SaaS; legacy platforms pending",
            "target_state": "Automated policy enforcement",
            "remediation_priority": "High", "estimated_cost": 35000, "estimated_effort": "4 months",
            "owner": "Security Team", "platform": "Mixed estate",
            "created_date": "2025-11-01", "target_date": "2026-08-31",
        },
        {
            "id": "GAP-004", "control_id": "NIST-PR.AC-1", "control_name": "Identity Management", "framework": "NIST",
            "gap_type": "Missing", "severity": "High", "risk_score": 80, "status": "Open",
            "description": "No centralized identity management system",
            "business_impact": "Manual user provisioning and deprovisioning",
            "current_state": "Manual processes for non-cloud platforms",
            "target_state": "Automated identity lifecycle management",
            "remediation_priority": "High", "estimated_cost": 75000, "estimated_effort": "6 months",
            "owner": "IT Operations", "platform": "Mixed estate",
            "created_date": "2025-11-10", "target_date": "2026-12-15",
        },
        {
            "id": "GAP-005", "control_id": "SOC-CC8", "control_name": "Change Management", "framework": "SOC2",
            "gap_type": "Incomplete", "severity": "Medium", "risk_score": 32, "status": "Remediated",
            "description": "Emergency changes bypass formal change management process",
            "business_impact": "Uncontrolled changes increase system instability",
            "current_state": "Emergency CAB path enforced with post-implementation review",
            "target_state": "Streamlined emergency change process",
            "remediation_priority": "High", "estimated_cost": 15000, "estimated_effort": "2 months",
            "owner": "Change Management", "platform": "Enterprise IT",
            "created_date": "2025-11-15", "target_date": "2026-02-28",
        },
        {
            "id": "GAP-006", "control_id": "ISO-A.12.1", "control_name": "Operational Procedures", "framework": "ISO27001",
            "gap_type": "Incomplete", "severity": "Medium", "risk_score": 52, "status": "In Progress",
            "description": "Documentation for critical operational procedures is outdated",
            "business_impact": "Inconsistent operational practices",
            "current_state": "Priority runbooks being rewritten in Q1",
            "target_state": "Current, accessible procedures",
            "remediation_priority": "Medium", "estimated_cost": 10000, "estimated_effort": "3 months",
            "owner": "IT Operations", "platform": "Enterprise IT",
            "created_date": "2025-11-20", "target_date": "2026-09-15",
        },
        {
            "id": "GAP-007", "control_id": "NIST-DE.AE-1", "control_name": "Baseline Network Operations", "framework": "NIST",
            "gap_type": "Missing", "severity": "Medium", "risk_score": 60, "status": "Open",
            "description": "No baseline established for network traffic patterns",
            "business_impact": "Unable to detect anomalous network activity",
            "current_state": "No baseline monitoring",
            "target_state": "Automated baseline monitoring",
            "remediation_priority": "Medium", "estimated_cost": 20000, "estimated_effort": "4 months",
            "owner": "Network Team", "platform": "Network",
            "created_date": "2025-12-01", "target_date": "2026-10-31",
        },
        {
            "id": "GAP-008", "control_id": "SOC-CC4", "control_name": "Monitoring Activities", "framework": "SOC2",
            "gap_type": "Ineffective", "severity": "Low", "risk_score": 22, "status": "Remediated",
            "description": "Security monitoring alerts not properly configured",
            "business_impact": "Delayed incident detection and response",
            "current_state": "Alert thresholds tuned; false positives reduced",
            "target_state": "Optimized alert configuration",
            "remediation_priority": "Medium", "estimated_cost": 12000, "estimated_effort": "2 months",
            "owner": "Security Team", "platform": "Security ops",
            "created_date": "2025-10-10", "target_date": "2025-12-15",
        },
        {
            "id": "GAP-009", "control_id": "ISO-A.5.1", "control_name": "Information Security Policy", "framework": "ISO27001",
            "gap_type": "Incomplete", "severity": "Low", "risk_score": 28, "status": "In Progress",
            "description": "Policy review schedule not documented",
            "business_impact": "Policies may become outdated",
            "current_state": "Annual review calendar drafted; owners assigned",
            "target_state": "Annual policy review process",
            "remediation_priority": "Low", "estimated_cost": 5000, "estimated_effort": "1 month",
            "owner": "Compliance Team", "platform": "Governance",
            "created_date": "2025-12-05", "target_date": "2026-08-15",
        },
        {
            "id": "GAP-010", "control_id": "NIST-RC.RP-1", "control_name": "Recovery Plan Execution", "framework": "NIST",
            "gap_type": "Missing", "severity": "Low", "risk_score": 25, "status": "Open",
            "description": "No disaster recovery testing schedule",
            "business_impact": "Recovery procedures not validated",
            "current_state": "No testing program",
            "target_state": "Quarterly DR testing",
            "remediation_priority": "Low", "estimated_cost": 8000, "estimated_effort": "2 months",
            "owner": "Business Continuity", "platform": "Enterprise IT",
            "created_date": "2025-12-10", "target_date": "2026-11-30",
        },
        {
            "id": "GAP-011", "control_id": "ISO-A.9.1", "control_name": "Access Control Policy", "framework": "ISO27001",
            "gap_type": "Incomplete", "severity": "Critical", "risk_score": 92, "status": "Open",
            "description": "IBM i *ALLOBJ and QSECURITY controls not covered by corporate access control policy enforcement",
            "business_impact": "Privileged midrange access outside IAM standards",
            "current_state": "Policy covers AD/cloud only",
            "target_state": "IBM i special authorities in scope of access policy",
            "remediation_priority": "Immediate", "estimated_cost": 40000, "estimated_effort": "4 months",
            "owner": "IBM i Ops", "platform": "IBM i",
            "created_date": "2026-01-15", "target_date": "2026-10-15",
        },
        {
            "id": "GAP-012", "control_id": "SOC-CC6", "control_name": "Logical and Physical Access", "framework": "SOC2",
            "gap_type": "Incomplete", "severity": "High", "risk_score": 82, "status": "In Progress",
            "description": "RACF SPECIAL and OPERATIONS attributes on IBM Z not included in quarterly access reviews",
            "business_impact": "Mainframe privileged access can persist after role change",
            "current_state": "Pilot RACF extract feeding Q1 access review",
            "target_state": "Unified privileged access review including RACF",
            "remediation_priority": "High", "estimated_cost": 55000, "estimated_effort": "5 months",
            "owner": "Mainframe Security", "platform": "IBM Z",
            "created_date": "2026-01-18", "target_date": "2026-09-30",
        },
        {
            "id": "GAP-013", "control_id": "NIST-PR.AC-1", "control_name": "Identity Management", "framework": "NIST",
            "gap_type": "Ineffective", "severity": "High", "risk_score": 78, "status": "Open",
            "description": "SAP ECC SAP_ALL / DDIC and JD Edwards IFS admin roles outside central identity lifecycle",
            "business_impact": "ERP emergency access not provisioned/deprovisioned with HR events",
            "current_state": "Manual SU01 / World security",
            "target_state": "ERP privileged IDs in IAM workflow",
            "remediation_priority": "High", "estimated_cost": 60000, "estimated_effort": "6 months",
            "owner": "ERP Security", "platform": "SAP / JD Edwards",
            "created_date": "2026-01-20", "target_date": "2026-12-31",
        },
    ]


def gaps_to_dataframe(rows):
    df = pd.DataFrame(rows)
    df["created_date"] = pd.to_datetime(df["created_date"])
    df["target_date"] = pd.to_datetime(df["target_date"])
    today = pd.Timestamp.today().normalize()
    active = df["status"].isin(["Open", "In Progress"])
    df["overdue"] = active & (df["target_date"] < today)
    df["days_to_target"] = (df["target_date"] - today).dt.days
    return df


def ensure_gap_session(seed: int) -> None:
    """Keep an editable gap register in session; reshuffle lightly on resample."""
    if st.session_state.get("_gap_seed") != seed or "gaps" not in st.session_state:
        rows = _base_gaps()
        rng = np.random.default_rng(seed)
        if seed != 42:
            # Light jitter for demo resampling without destroying the narrative
            for row in rows:
                if row["status"] != "Remediated":
                    jitter = int(rng.integers(-4, 5))
                    row["risk_score"] = int(np.clip(row["risk_score"] + jitter, 5, 99))
        st.session_state.gaps = rows
        st.session_state._gap_seed = seed


def calculate_gap_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_gaps": 0, "open_gaps": 0, "in_progress_gaps": 0, "remediated_gaps": 0,
            "critical_gaps": 0, "high_gaps": 0, "medium_gaps": 0, "low_gaps": 0,
            "avg_risk_score": 0.0, "total_cost": 0, "active_cost": 0,
            "remediation_rate": 0.0, "overdue_gaps": 0,
        }

    total_gaps = len(df)
    open_gaps = int((df["status"] == "Open").sum())
    in_progress_gaps = int((df["status"] == "In Progress").sum())
    remediated_gaps = int((df["status"] == "Remediated").sum())
    active = df[df["status"].isin(["Open", "In Progress"])]

    return {
        "total_gaps": total_gaps,
        "open_gaps": open_gaps,
        "in_progress_gaps": in_progress_gaps,
        "remediated_gaps": remediated_gaps,
        "critical_gaps": int((df["severity"] == "Critical").sum()),
        "high_gaps": int((df["severity"] == "High").sum()),
        "medium_gaps": int((df["severity"] == "Medium").sum()),
        "low_gaps": int((df["severity"] == "Low").sum()),
        "avg_risk_score": float(df["risk_score"].mean()),
        "total_cost": int(df["estimated_cost"].sum()),
        "active_cost": int(active["estimated_cost"].sum()) if not active.empty else 0,
        "remediation_rate": (remediated_gaps / total_gaps * 100) if total_gaps else 0.0,
        "overdue_gaps": int(df["overdue"].sum()) if "overdue" in df.columns else 0,
    }


def generate_remediation_plan(df: pd.DataFrame) -> pd.DataFrame:
    active = df[df["status"].isin(["Open", "In Progress"])].copy()
    if active.empty:
        return active
    active["priority_score"] = active["severity"].map(SEVERITY_WEIGHT) * active["risk_score"] / 25.0
    # Overdue gaps bubble up slightly
    active.loc[active["overdue"], "priority_score"] = active.loc[active["overdue"], "priority_score"] + 1.5
    return active.sort_values(["priority_score", "risk_score"], ascending=False)


def kpi_status(metric: str, value) -> str:
    checks = {
        "Total Gaps": value < 20,
        "Critical Gaps": value == 0,
        "High Gaps": value < 5,
        "Remediation Rate": value > 80,
        "Avg Risk Score": value < 50,
        "Active Backlog $": value < 200_000,
        "Overdue": value == 0,
    }
    ok = checks.get(metric)
    if ok is None:
        return "—"
    return "On track" if ok else "Off track"


def next_gap_id(rows) -> str:
    nums = []
    for row in rows:
        try:
            nums.append(int(str(row["id"]).split("-")[-1]))
        except (ValueError, IndexError):
            continue
    return f"GAP-{max(nums, default=0) + 1:03d}"


def update_gap_field(gap_id: str, **fields) -> None:
    for i, row in enumerate(st.session_state.gaps):
        if row["id"] == gap_id:
            st.session_state.gaps[i] = {**row, **fields}
            break


def main():
    portfolio_skin.page_header(
        title="Control Gap Analysis",
        lede="Prioritize control gaps across frameworks and legacy platforms — #RUNGRCRaleigh.",
        kicker="Controls",
    )
    st.caption("Sample gap register · refreshed Aug 2026 — illustrative data you can edit in-session.")

    frameworks_df, controls_df = load_framework_data()

    st.sidebar.header("Controls")
    seed = demo_kit.seed_controls()
    ensure_gap_session(seed)
    gaps_df = gaps_to_dataframe(st.session_state.gaps)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")

    framework_filter = st.sidebar.multiselect(
        "Framework", options=sorted(gaps_df["framework"].unique()), default=sorted(gaps_df["framework"].unique())
    )
    status_filter = st.sidebar.multiselect(
        "Status", options=STATUS_ORDER, default=STATUS_ORDER
    )
    severity_filter = st.sidebar.multiselect(
        "Severity", options=SEVERITY_ORDER, default=SEVERITY_ORDER
    )
    gap_type_filter = st.sidebar.multiselect(
        "Gap Type", options=sorted(gaps_df["gap_type"].unique()), default=sorted(gaps_df["gap_type"].unique())
    )
    platform_filter = st.sidebar.multiselect(
        "Platform", options=sorted(gaps_df["platform"].unique()), default=sorted(gaps_df["platform"].unique())
    )
    owner_filter = st.sidebar.multiselect(
        "Owner", options=sorted(gaps_df["owner"].unique()), default=sorted(gaps_df["owner"].unique())
    )
    show_overdue_only = st.sidebar.checkbox("Overdue only", value=False)

    filtered_df = gaps_df[
        gaps_df["framework"].isin(framework_filter)
        & gaps_df["status"].isin(status_filter)
        & gaps_df["severity"].isin(severity_filter)
        & gaps_df["gap_type"].isin(gap_type_filter)
        & gaps_df["platform"].isin(platform_filter)
        & gaps_df["owner"].isin(owner_filter)
    ].copy()
    if show_overdue_only:
        filtered_df = filtered_df[filtered_df["overdue"]]

    metrics = calculate_gap_metrics(filtered_df)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Gaps", metrics["total_gaps"])
        st.metric("Critical", metrics["critical_gaps"])
    with m2:
        st.metric("Open", metrics["open_gaps"])
        st.metric("In Progress", metrics["in_progress_gaps"])
    with m3:
        st.metric("Remediated", metrics["remediated_gaps"])
        st.metric("Remediation Rate", f"{metrics['remediation_rate']:.1f}%")
    with m4:
        st.metric("Overdue", metrics["overdue_gaps"])
        st.metric("Active Backlog", f"${metrics['active_cost']:,.0f}")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Gap Register", "Analytics", "Remediation Plan", "Framework Mapping", "Gap Management", "Export"]
    )

    with tab1:
        st.subheader("Gap Register")
        st.caption(f"Showing {len(filtered_df)} of {len(gaps_df)} gaps · sorted by risk.")

        if filtered_df.empty:
            st.info("No gaps match the current filters.")
        else:
            display = filtered_df.copy()
            display["severity"] = pd.Categorical(display["severity"], categories=SEVERITY_ORDER, ordered=True)
            display = display.sort_values(["severity", "risk_score"], ascending=[True, False])
            display["created"] = display["created_date"].dt.strftime("%Y-%m-%d")
            display["target"] = display["target_date"].dt.strftime("%Y-%m-%d")
            display["overdue_flag"] = display["overdue"].map({True: "Yes", False: ""})

            st.dataframe(
                display[
                    [
                        "id", "control_name", "framework", "platform", "gap_type", "severity",
                        "risk_score", "status", "owner", "target", "overdue_flag", "estimated_cost",
                    ]
                ].rename(columns={
                    "id": "ID",
                    "control_name": "Control",
                    "framework": "Framework",
                    "platform": "Platform",
                    "gap_type": "Gap Type",
                    "severity": "Severity",
                    "risk_score": "Risk",
                    "status": "Status",
                    "owner": "Owner",
                    "target": "Target Date",
                    "overdue_flag": "Overdue",
                    "estimated_cost": "Est. Cost",
                }),
                use_container_width=True,
                hide_index=True,
                height=420,
            )

            st.markdown("##### Gap detail / status update")
            selected_gap = st.selectbox(
                "Select gap",
                display["id"].tolist(),
                format_func=lambda gid: f"{gid} · {display.loc[display['id'] == gid, 'control_name'].iloc[0]}",
            )
            gap_data = display[display["id"] == selected_gap].iloc[0]

            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Control:** {gap_data['control_name']}")
                st.write(f"**Framework:** {gap_data['framework']}")
                st.write(f"**Platform:** {gap_data['platform']}")
                st.write(f"**Owner:** {gap_data['owner']}")
            with c2:
                st.write(f"**Severity:** {gap_data['severity']}")
                st.write(f"**Risk score:** {gap_data['risk_score']}/100")
                st.write(f"**Gap type:** {gap_data['gap_type']}")
                st.write(f"**Created:** {gap_data['created']}")
            with c3:
                st.write(f"**Target:** {gap_data['target']}")
                st.write(f"**Overdue:** {'Yes' if gap_data['overdue'] else 'No'}")
                st.write(f"**Est. cost:** ${gap_data['estimated_cost']:,.0f}")
                st.write(f"**Effort:** {gap_data['estimated_effort']}")

            st.write(f"**Description:** {gap_data['description']}")
            st.write(f"**Business impact:** {gap_data['business_impact']}")
            st.write(f"**Current state:** {gap_data['current_state']}")
            st.write(f"**Target state:** {gap_data['target_state']}")

            uc1, uc2, uc3 = st.columns([2, 2, 1])
            with uc1:
                new_status = st.selectbox(
                    "Update status",
                    STATUS_ORDER,
                    index=STATUS_ORDER.index(gap_data["status"]) if gap_data["status"] in STATUS_ORDER else 0,
                    key=f"status_{selected_gap}",
                )
            with uc2:
                new_owner = st.text_input("Owner", value=str(gap_data["owner"]), key=f"owner_{selected_gap}")
            with uc3:
                st.write("")
                st.write("")
                if st.button("Save", type="primary", use_container_width=True, key=f"save_{selected_gap}"):
                    update_gap_field(selected_gap, status=new_status, owner=new_owner.strip() or gap_data["owner"])
                    st.success(f"Updated {selected_gap}")
                    st.rerun()

    with tab2:
        st.subheader("Gap Analytics")
        if filtered_df.empty:
            st.info("No gaps to chart for the current filters.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                severity_counts = (
                    filtered_df["severity"]
                    .value_counts()
                    .reindex(SEVERITY_ORDER)
                    .dropna()
                )
                fig_severity = px.pie(
                    values=severity_counts.values,
                    names=severity_counts.index,
                    title="Gaps by Severity",
                )
                st.plotly_chart(fig_severity, use_container_width=True)

                framework_counts = filtered_df["framework"].value_counts()
                fig_framework = px.bar(
                    x=framework_counts.index,
                    y=framework_counts.values,
                    title="Gaps by Framework",
                    labels={"x": "Framework", "y": "Number of Gaps"},
                )
                st.plotly_chart(fig_framework, use_container_width=True)

            with col2:
                status_counts = (
                    filtered_df["status"].value_counts().reindex(STATUS_ORDER).dropna()
                )
                fig_status = px.bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    title="Gaps by Status",
                    labels={"x": "Status", "y": "Number of Gaps"},
                )
                st.plotly_chart(fig_status, use_container_width=True)

                fig_platform = px.bar(
                    filtered_df.groupby("platform", as_index=False).size(),
                    x="platform",
                    y="size",
                    title="Gaps by Platform",
                    labels={"platform": "Platform", "size": "Number of Gaps"},
                )
                fig_platform.update_xaxes(tickangle=30)
                st.plotly_chart(fig_platform, use_container_width=True)

            st.markdown("##### Illustrative 12-month trend")
            end = pd.Timestamp.today().normalize()
            start = end - pd.DateOffset(months=11)
            dates = pd.date_range(start=start, end=end, freq="ME")
            rng = np.random.default_rng(seed)
            trend_data = []
            for i, date in enumerate(dates):
                progress = i / max(len(dates) - 1, 1)
                gap_count = max(8, int(14 - progress * 2 + rng.normal(0, 0.8)))
                remediated_share = 0.12 + progress * 0.14
                open_share = max(0.35, 0.68 - progress * 0.22)
                trend_data.append({
                    "date": date,
                    "total_gaps": gap_count,
                    "open_gaps": int(gap_count * open_share),
                    "remediated_gaps": int(gap_count * remediated_share),
                    "avg_risk_score": 72 - progress * 10 + rng.normal(0, 2.5),
                })
            trend_df = pd.DataFrame(trend_data)

            t1, t2 = st.columns(2)
            with t1:
                st.plotly_chart(
                    px.line(
                        trend_df,
                        x="date",
                        y=["total_gaps", "open_gaps", "remediated_gaps"],
                        title="Gap Count Trends",
                        labels={"value": "Number of Gaps", "variable": "Series"},
                    ),
                    use_container_width=True,
                )
            with t2:
                st.plotly_chart(
                    px.line(
                        trend_df,
                        x="date",
                        y="avg_risk_score",
                        title="Average Risk Score Trend",
                        labels={"avg_risk_score": "Average Risk Score"},
                    ),
                    use_container_width=True,
                )

    with tab3:
        st.subheader("Remediation Plan")
        plan = generate_remediation_plan(filtered_df)
        if plan.empty:
            st.success("No open or in-progress gaps in the current filter.")
        else:
            st.caption(
                f"{len(plan)} active gaps · backlog ${plan['estimated_cost'].sum():,.0f} · "
                f"{int(plan['overdue'].sum())} overdue"
            )
            plan_view = plan.copy()
            plan_view["target"] = plan_view["target_date"].dt.strftime("%Y-%m-%d")
            plan_view["overdue_flag"] = plan_view["overdue"].map({True: "Yes", False: ""})
            st.dataframe(
                plan_view[
                    [
                        "id", "control_name", "framework", "platform", "severity", "risk_score",
                        "priority_score", "status", "owner", "target", "overdue_flag", "estimated_cost", "estimated_effort",
                    ]
                ].rename(columns={
                    "id": "ID",
                    "control_name": "Control",
                    "framework": "Framework",
                    "platform": "Platform",
                    "severity": "Severity",
                    "risk_score": "Risk",
                    "priority_score": "Priority",
                    "status": "Status",
                    "owner": "Owner",
                    "target": "Target",
                    "overdue_flag": "Overdue",
                    "estimated_cost": "Est. Cost",
                    "estimated_effort": "Effort",
                }),
                use_container_width=True,
                hide_index=True,
            )

            with st.expander("Top priority narratives", expanded=False):
                for _, gap in plan.head(5).iterrows():
                    st.markdown(
                        f"**{gap['id']}: {gap['control_name']}** "
                        f"(priority {gap['priority_score']:.1f} · {gap['platform']})"
                    )
                    st.write(gap["description"])
                    st.write(f"Impact: {gap['business_impact']}")
                    st.write(f"{gap['current_state']} → {gap['target_state']}")
                    st.divider()

            st.markdown("##### Cost analysis")
            c1, c2 = st.columns(2)
            with c1:
                cost_by_severity = (
                    plan.groupby("severity", observed=False)["estimated_cost"].sum().reindex(SEVERITY_ORDER).dropna().reset_index()
                )
                st.plotly_chart(
                    px.bar(
                        cost_by_severity,
                        x="severity",
                        y="estimated_cost",
                        title="Active Remediation Cost by Severity",
                        labels={"estimated_cost": "Estimated Cost ($)", "severity": "Severity"},
                    ),
                    use_container_width=True,
                )
            with c2:
                cost_by_platform = plan.groupby("platform", as_index=False)["estimated_cost"].sum()
                st.plotly_chart(
                    px.pie(
                        values=cost_by_platform["estimated_cost"],
                        names=cost_by_platform["platform"],
                        title="Active Cost by Platform",
                    ),
                    use_container_width=True,
                )

            st.markdown("##### Owner workload (active)")
            owner_workload = plan.groupby("owner").agg(
                gap_count=("id", "count"),
                total_cost=("estimated_cost", "sum"),
                avg_risk=("risk_score", "mean"),
                overdue=("overdue", "sum"),
            ).reset_index().sort_values("total_cost", ascending=False)
            owner_workload["avg_risk"] = owner_workload["avg_risk"].round(1)
            st.dataframe(
                owner_workload.rename(columns={
                    "owner": "Owner",
                    "gap_count": "Gaps",
                    "total_cost": "Backlog $",
                    "avg_risk": "Avg Risk",
                    "overdue": "Overdue",
                }),
                use_container_width=True,
                hide_index=True,
            )

    with tab4:
        st.subheader("Framework Mapping")
        if filtered_df.empty:
            st.info("No gaps to map for the current filters.")
        else:
            framework_coverage = filtered_df.groupby(["framework", "severity"]).size().unstack(fill_value=0)
            for sev in SEVERITY_ORDER:
                if sev not in framework_coverage.columns:
                    framework_coverage[sev] = 0
            framework_coverage = framework_coverage[SEVERITY_ORDER]
            st.plotly_chart(
                px.imshow(
                    framework_coverage,
                    title="Framework × Severity (gap counts)",
                    labels=dict(x="Severity", y="Framework", color="Gaps"),
                    aspect="auto",
                    text_auto=True,
                ),
                use_container_width=True,
            )

            # Control coverage: catalog vs gaps
            st.markdown("##### Control coverage against sample catalog")
            covered = set(filtered_df["control_id"].unique())
            catalog = controls_df.copy()
            catalog["has_gap"] = catalog["id"].isin(covered)
            cov_summary = catalog.groupby("framework").agg(
                controls=("id", "count"),
                with_gaps=("has_gap", "sum"),
            ).reset_index()
            cov_summary["gap_rate"] = (cov_summary["with_gaps"] / cov_summary["controls"] * 100).round(1)
            st.dataframe(
                cov_summary.rename(columns={
                    "framework": "Framework",
                    "controls": "Catalog Controls",
                    "with_gaps": "With Gaps",
                    "gap_rate": "Gap Rate %",
                }),
                use_container_width=True,
                hide_index=True,
            )

            c1, c2 = st.columns(2)
            with c1:
                st.write("**Framework catalog**")
                for _, framework in frameworks_df.iterrows():
                    st.write(f"- {framework['name']} ({framework['version']}) — {framework['type']}")
            with c2:
                gap_type_framework = filtered_df.groupby(["framework", "gap_type"]).size().unstack(fill_value=0)
                st.plotly_chart(
                    px.bar(
                        gap_type_framework,
                        title="Gap Types by Framework",
                        labels={"value": "Number of Gaps", "variable": "Gap Type"},
                        barmode="stack",
                    ),
                    use_container_width=True,
                )

    with tab5:
        st.subheader("Gap Management")
        left, right = st.columns(2)

        with left:
            st.markdown("##### Add gap")
            with st.form("new_gap_form", clear_on_submit=True):
                control_options = controls_df.apply(
                    lambda r: f"{r['id']} · {r['name']} ({r['framework']})", axis=1
                ).tolist()
                control_pick = st.selectbox("Control", control_options)
                gap_type = st.selectbox("Gap Type", ["Missing", "Incomplete", "Ineffective"])
                severity = st.selectbox("Severity", SEVERITY_ORDER)
                risk_score = st.slider("Risk Score", 1, 100, 65)
                platform = st.selectbox(
                    "Platform",
                    sorted(set(list(gaps_df["platform"].unique()) + demo_kit.legacy_platform_names() + ["Mixed estate", "Cloud / AD"])),
                )
                owner = st.text_input("Owner", value="Security Team")
                description = st.text_area("Description", placeholder="What is missing or ineffective?")
                business_impact = st.text_area("Business impact", placeholder="Why does this matter?")
                target_date = st.date_input("Target date", value=datetime.today().date() + timedelta(days=90))
                estimated_cost = st.number_input("Estimated cost ($)", min_value=0, value=15000, step=1000)
                submitted = st.form_submit_button("Add Gap", type="primary")
                if submitted:
                    if not description.strip():
                        st.error("Description is required.")
                    else:
                        control_id = control_pick.split(" · ")[0]
                        control_row = controls_df[controls_df["id"] == control_id].iloc[0]
                        new_row = {
                            "id": next_gap_id(st.session_state.gaps),
                            "control_id": control_id,
                            "control_name": control_row["name"],
                            "framework": control_row["framework"],
                            "gap_type": gap_type,
                            "severity": severity,
                            "risk_score": int(risk_score),
                            "status": "Open",
                            "description": description.strip(),
                            "business_impact": business_impact.strip() or "TBD",
                            "current_state": "Newly logged",
                            "target_state": "Control operating effectively",
                            "remediation_priority": "High" if severity in {"Critical", "High"} else severity,
                            "estimated_cost": int(estimated_cost),
                            "estimated_effort": "TBD",
                            "owner": owner.strip() or "Unassigned",
                            "platform": platform,
                            "created_date": datetime.today().strftime("%Y-%m-%d"),
                            "target_date": target_date.strftime("%Y-%m-%d"),
                        }
                        st.session_state.gaps.append(new_row)
                        st.success(f"Added {new_row['id']}")
                        st.rerun()

        with right:
            st.markdown("##### KPI snapshot (filtered view)")
            kpi_rows = [
                ("Total Gaps", metrics["total_gaps"], "<20"),
                ("Critical Gaps", metrics["critical_gaps"], "0"),
                ("High Gaps", metrics["high_gaps"], "<5"),
                ("Remediation Rate", round(metrics["remediation_rate"], 1), ">80%"),
                ("Avg Risk Score", round(metrics["avg_risk_score"], 1), "<50"),
                ("Active Backlog $", metrics["active_cost"], "<$200K"),
                ("Overdue", metrics["overdue_gaps"], "0"),
            ]
            kpi_df = pd.DataFrame([
                {
                    "Metric": name,
                    "Current": f"{val}%" if "Rate" in name else (f"${val:,.0f}" if "Backlog" in name or name.endswith("$") else val),
                    "Target": target,
                    "Status": kpi_status(name, val),
                }
                for name, val, target in kpi_rows
            ])
            st.dataframe(kpi_df, use_container_width=True, hide_index=True)

            st.markdown("##### Gaps by owner")
            if not filtered_df.empty:
                owner_counts = filtered_df["owner"].value_counts()
                fig_owner = px.bar(
                    x=owner_counts.index,
                    y=owner_counts.values,
                    title="Gaps by Owner",
                    labels={"x": "Owner", "y": "Number of Gaps"},
                )
                fig_owner.update_xaxes(tickangle=35)
                st.plotly_chart(fig_owner, use_container_width=True)

    with tab6:
        st.subheader("Export")
        export_df = filtered_df.copy()
        for col in ("created_date", "target_date"):
            if col in export_df.columns:
                export_df[col] = export_df[col].dt.strftime("%Y-%m-%d")
        if "overdue" in export_df.columns:
            export_df["overdue"] = export_df["overdue"].map({True: "Yes", False: "No"})
        st.caption(f"{len(export_df)} rows with current filters.")
        demo_kit.csv_download(export_df, "control_gaps_filtered.csv", label="Download filtered gaps")

        plan_export = generate_remediation_plan(filtered_df)
        if not plan_export.empty:
            pe = plan_export.copy()
            for col in ("created_date", "target_date"):
                pe[col] = pe[col].dt.strftime("%Y-%m-%d")
            pe["overdue"] = pe["overdue"].map({True: "Yes", False: "No"})
            demo_kit.csv_download(pe, "remediation_plan.csv", label="Download prioritized remediation plan", key="export_plan")


if __name__ == "__main__":
    main()
