"""Control Tracker — lightweight remediation coordination register.

Tracks where control remediation work lives across owners, doing teams, and tools.
Sample data is illustrative; session edits are local to the browser session.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import demo_kit
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

# Practical coordination labels (fork-friendly)
COORD_STATES = [
    "Aligned",
    "Pending transfer",
    "Status drift",
    "Split ownership",
    "Undocumented",
]

COORD_COLORS = {
    "Aligned": "#2e7d32",
    "Pending transfer": "#1976d2",
    "Status drift": "#f57c00",
    "Split ownership": "#7b1fa2",
    "Undocumented": "#c62828",
}

FRAMEWORKS = ["NIST CSF", "ISO 27001", "SOC 2", "PCI DSS", "HIPAA", "Other"]
WORK_SYSTEMS = [
    "GRC platform",
    "Jira",
    "ServiceNow",
    "Change ticket",
    "Email",
    "Meeting notes",
    "Chat",
    "Spreadsheet",
    "Other",
]
CONTROL_STATUSES = [
    "Not Implemented",
    "In Progress",
    "Implemented",
    "Tested",
    "Compliant",
]
TEST_RESULTS = ["Not Started", "In Progress", "Passed", "Failed"]

EXPORT_COLS = [
    "control_id",
    "control_name",
    "framework",
    "issue",
    "control_status",
    "coord_state",
    "owner",
    "doing_team",
    "informed",
    "source_of_truth",
    "ticket_ref",
    "notes",
    "risk_score",
    "last_update",
    "due_date",
    "evidence_count",
    "test_results",
]


def _sample_rows(today: date | None = None) -> list[dict[str, Any]]:
    """Illustrative remediation register (Aug 2026)."""
    today = today or date(2026, 8, 12)
    return [
        {
            "control_id": "AC-01",
            "control_name": "Access Control Policy",
            "framework": "NIST CSF",
            "issue": "Annual policy refresh; evidence attached in GRC",
            "control_status": "Compliant",
            "coord_state": "Aligned",
            "owner": "IT Security Team",
            "doing_team": "IT Security Team",
            "informed": "GRC; Internal Audit",
            "source_of_truth": "GRC platform",
            "ticket_ref": "GRC-CTRL-1042",
            "notes": "GRC record matches completed policy update.",
            "risk_score": 25,
            "last_update": (today - timedelta(days=5)).isoformat(),
            "due_date": (today + timedelta(days=95)).isoformat(),
            "evidence_count": 5,
            "test_results": "Passed",
        },
        {
            "control_id": "AC-02",
            "control_name": "Account Management",
            "framework": "NIST CSF",
            "issue": "JML exceptions for shared service accounts",
            "control_status": "Tested",
            "coord_state": "Pending transfer",
            "owner": "IAM Engineering",
            "doing_team": "IAM Engineering",
            "informed": "IT Security; GRC",
            "source_of_truth": "Jira",
            "ticket_ref": "SEC-2841",
            "notes": "Active work in Jira; GRC narrative not yet refreshed.",
            "risk_score": 35,
            "last_update": (today - timedelta(days=1)).isoformat(),
            "due_date": (today + timedelta(days=40)).isoformat(),
            "evidence_count": 3,
            "test_results": "Passed",
        },
        {
            "control_id": "A.5.1",
            "control_name": "Information Security Policies",
            "framework": "ISO 27001",
            "issue": "Editorial updates after management review",
            "control_status": "Compliant",
            "coord_state": "Aligned",
            "owner": "Security Governance",
            "doing_team": "Security Governance",
            "informed": "Legal; GRC",
            "source_of_truth": "GRC platform",
            "ticket_ref": "GRC-POL-220",
            "notes": "Policy set and control record are consistent.",
            "risk_score": 20,
            "last_update": (today - timedelta(days=8)).isoformat(),
            "due_date": (today + timedelta(days=110)).isoformat(),
            "evidence_count": 4,
            "test_results": "Passed",
        },
        {
            "control_id": "CC6.1",
            "control_name": "Logical Access Security Software",
            "framework": "SOC 2",
            "issue": "MFA gaps on a subset of SaaS admin consoles",
            "control_status": "Implemented",
            "coord_state": "Status drift",
            "owner": "IT Operations",
            "doing_team": "Cloud Ops",
            "informed": "IT Security; GRC; SOC 2 readiness",
            "source_of_truth": "ServiceNow",
            "ticket_ref": "INC/RITM-77821",
            "notes": "ServiceNow still In Progress; GRC already marked Implemented.",
            "risk_score": 45,
            "last_update": (today - timedelta(days=2)).isoformat(),
            "due_date": (today + timedelta(days=55)).isoformat(),
            "evidence_count": 2,
            "test_results": "In Progress",
        },
        {
            "control_id": "CC7.1",
            "control_name": "System Operation Monitoring",
            "framework": "SOC 2",
            "issue": "Alert tuning for dormant accounts on brownfield hosts",
            "control_status": "In Progress",
            "coord_state": "Split ownership",
            "owner": "GRC",
            "doing_team": "Security Operations",
            "informed": "IT Operations; Audit",
            "source_of_truth": "Spreadsheet",
            "ticket_ref": "TRACKER-sheet-tab3",
            "notes": "Finding owned in GRC; SIEM work owned by SecOps; shared sheet is interim.",
            "risk_score": 60,
            "last_update": (today - timedelta(days=4)).isoformat(),
            "due_date": (today + timedelta(days=18)).isoformat(),
            "evidence_count": 1,
            "test_results": "Not Started",
        },
        {
            "control_id": "3.1",
            "control_name": "Network Security Controls",
            "framework": "PCI DSS",
            "issue": "Segment rule review after payment-zone change",
            "control_status": "Tested",
            "coord_state": "Aligned",
            "owner": "Network Security",
            "doing_team": "Network Security",
            "informed": "PCI liaison; GRC",
            "source_of_truth": "Change ticket",
            "ticket_ref": "CHG004912",
            "notes": "Change record is live SoT until CAB close, then evidence to GRC.",
            "risk_score": 40,
            "last_update": (today - timedelta(days=7)).isoformat(),
            "due_date": (today + timedelta(days=70)).isoformat(),
            "evidence_count": 3,
            "test_results": "Passed",
        },
        {
            "control_id": "164.308",
            "control_name": "Administrative Safeguards",
            "framework": "HIPAA",
            "issue": "Workforce sanction procedure missing from ops runbooks",
            "control_status": "Not Implemented",
            "coord_state": "Undocumented",
            "owner": "Compliance Team",
            "doing_team": "HR Ops",
            "informed": "Legal; Privacy; GRC",
            "source_of_truth": "Email",
            "ticket_ref": "",
            "notes": "Decision trail is email-only; no durable ticket yet.",
            "risk_score": 80,
            "last_update": (today - timedelta(days=19)).isoformat(),
            "due_date": (today - timedelta(days=4)).isoformat(),
            "evidence_count": 0,
            "test_results": "Not Started",
        },
        {
            "control_id": "ID.AM-1",
            "control_name": "Asset Inventory",
            "framework": "NIST CSF",
            "issue": "Reconcile CMDB vs discovered LPARs and appliances",
            "control_status": "Implemented",
            "coord_state": "Status drift",
            "owner": "Asset Management",
            "doing_team": "Platform Engineering",
            "informed": "IT Security; GRC",
            "source_of_truth": "ServiceNow",
            "ticket_ref": "CMDB-941",
            "notes": "Discovery feed updated; CMDB ownership still under review.",
            "risk_score": 30,
            "last_update": today.isoformat(),
            "due_date": (today + timedelta(days=60)).isoformat(),
            "evidence_count": 2,
            "test_results": "Passed",
        },
        {
            "control_id": "PR.AC-1",
            "control_name": "Identity Management",
            "framework": "NIST CSF",
            "issue": "Privileged identity recert for break-glass accounts",
            "control_status": "Compliant",
            "coord_state": "Aligned",
            "owner": "IT Security Team",
            "doing_team": "IT Security Team",
            "informed": "IAM; GRC",
            "source_of_truth": "GRC platform",
            "ticket_ref": "GRC-RECERT-88",
            "notes": "Recert closed with attestations attached.",
            "risk_score": 25,
            "last_update": (today - timedelta(days=10)).isoformat(),
            "due_date": (today + timedelta(days=100)).isoformat(),
            "evidence_count": 4,
            "test_results": "Passed",
        },
        {
            "control_id": "DE.CM-1",
            "control_name": "Security Monitoring",
            "framework": "NIST CSF",
            "issue": "Legacy middleware logging coverage gap",
            "control_status": "In Progress",
            "coord_state": "Undocumented",
            "owner": "Security Operations",
            "doing_team": "Middleware Ops",
            "informed": "GRC; Audit",
            "source_of_truth": "Meeting notes",
            "ticket_ref": "",
            "notes": "Verbal agreement in standup; ticket not opened yet.",
            "risk_score": 55,
            "last_update": (today - timedelta(days=1)).isoformat(),
            "due_date": (today + timedelta(days=25)).isoformat(),
            "evidence_count": 1,
            "test_results": "In Progress",
        },
        {
            "control_id": "IBMI-QSEC",
            "control_name": "IBM i QSECURITY & *ALLOBJ Governance",
            "framework": "NIST CSF",
            "issue": "Reduce standing *ALLOBJ; monitor QSECURITY drift on prod LPARs",
            "control_status": "In Progress",
            "coord_state": "Undocumented",
            "owner": "IBM i Ops",
            "doing_team": "IBM i Ops",
            "informed": "GRC; Mainframe Security; Audit",
            "source_of_truth": "Email",
            "ticket_ref": "",
            "notes": "Work underway; status updates live in email, not GRC.",
            "risk_score": 78,
            "last_update": (today - timedelta(days=2)).isoformat(),
            "due_date": (today + timedelta(days=14)).isoformat(),
            "evidence_count": 2,
            "test_results": "In Progress",
        },
        {
            "control_id": "ZOS-RACF",
            "control_name": "z/OS RACF Privileged Attribute Recertification",
            "framework": "SOC 2",
            "issue": "Recert SPECIAL/OPERATIONS; align CICS region ID ownership",
            "control_status": "Implemented",
            "coord_state": "Status drift",
            "owner": "Mainframe Security",
            "doing_team": "Mainframe Security",
            "informed": "GRC; Internal Audit",
            "source_of_truth": "Change ticket",
            "ticket_ref": "CHG004880",
            "notes": "Change closed on Z; GRC control status still lagging.",
            "risk_score": 72,
            "last_update": (today - timedelta(days=3)).isoformat(),
            "due_date": (today + timedelta(days=45)).isoformat(),
            "evidence_count": 3,
            "test_results": "Passed",
        },
        {
            "control_id": "ERP-SAPALL",
            "control_name": "SAP ECC / JD Edwards Privileged Access",
            "framework": "ISO 27001",
            "issue": "Break-glass for SAP_ALL / DDIC and JDE IFS admin roles",
            "control_status": "Not Implemented",
            "coord_state": "Split ownership",
            "owner": "ERP Security",
            "doing_team": "SAP Basis / JDE CNC",
            "informed": "GRC; Internal Audit; App owners",
            "source_of_truth": "Jira",
            "ticket_ref": "ERP-551; RITM-66210",
            "notes": "Sprint work in Jira; related RITM in ServiceNow; finding in GRC.",
            "risk_score": 82,
            "last_update": (today - timedelta(days=1)).isoformat(),
            "due_date": (today - timedelta(days=2)).isoformat(),
            "evidence_count": 0,
            "test_results": "Not Started",
        },
    ]


def ensure_register(seed: int) -> None:
    if st.session_state.get("_ctrl_seed") != seed or "controls" not in st.session_state:
        st.session_state.controls = [dict(r) for r in _sample_rows()]
        st.session_state._ctrl_seed = seed


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=EXPORT_COLS)
    return pd.DataFrame(rows)


def metrics(df: pd.DataFrame) -> dict[str, Any]:
    now = datetime.now()
    if df.empty:
        return {
            "total": 0,
            "aligned": 0,
            "attention": 0,
            "overdue": 0,
            "owner_mismatch": 0,
            "systems": 0,
            "high_risk": 0,
            "avg_risk": 0.0,
        }
    attention_states = {"Pending transfer", "Status drift", "Split ownership", "Undocumented"}
    return {
        "total": len(df),
        "aligned": int((df["coord_state"] == "Aligned").sum()),
        "attention": int(df["coord_state"].isin(attention_states).sum()),
        "overdue": int((pd.to_datetime(df["due_date"]) < now).sum()),
        "owner_mismatch": int((df["owner"] != df["doing_team"]).sum()),
        "systems": int(df["source_of_truth"].nunique()),
        "high_risk": int((df["risk_score"] >= 70).sum()),
        "avg_risk": float(df["risk_score"].mean()),
    }


def upsert_row(fields: dict[str, Any]) -> str:
    cid = fields["control_id"].strip()
    for i, row in enumerate(st.session_state.controls):
        if row["control_id"] == cid:
            st.session_state.controls[i] = {**row, **fields}
            return "updated"
    st.session_state.controls.append(fields)
    return "added"


def main():
    portfolio_skin.page_header(
        title="Control Tracker",
        lede="Session register for control remediation ownership, handoffs, and source of truth.",
        kicker="Controls",
    )

    seed = demo_kit.ensure_seed()
    ensure_register(seed)

    st.sidebar.header("Controls")
    demo_kit.seed_controls()
    st.sidebar.caption("Resample reloads sample rows (session edits cleared).")

    with st.sidebar.expander("Add / update item", expanded=False):
        with st.form("upsert_control"):
            control_id = st.text_input("Control ID", placeholder="e.g. AC-02")
            control_name = st.text_input("Control name")
            framework = st.selectbox("Framework", FRAMEWORKS)
            issue = st.text_area("Remediation issue", height=80)
            c1, c2 = st.columns(2)
            with c1:
                control_status = st.selectbox("Control status", CONTROL_STATUSES)
                owner = st.text_input("Owner (accountable)")
                source_of_truth = st.selectbox("Source of truth", WORK_SYSTEMS)
                risk_score = st.slider("Risk score", 1, 100, 50)
            with c2:
                coord_state = st.selectbox("Coordination state", COORD_STATES)
                doing_team = st.text_input("Doing team")
                ticket_ref = st.text_input("Ticket / ref", placeholder="Jira / CHG / RITM…")
                evidence_count = st.number_input("Evidence count", 0, 50, 0)
            informed = st.text_input("Informed", placeholder="GRC; Audit; …")
            notes = st.text_area("Notes", height=60)
            test_results = st.selectbox("Test results", TEST_RESULTS)
            due_date = st.date_input("Due date", value=date(2026, 9, 30))
            submitted = st.form_submit_button("Save item", type="primary")
            if submitted:
                if not control_id.strip() or not control_name.strip():
                    st.error("Control ID and name are required.")
                else:
                    fields = {
                        "control_id": control_id.strip(),
                        "control_name": control_name.strip(),
                        "framework": framework,
                        "issue": issue.strip() or "—",
                        "control_status": control_status,
                        "coord_state": coord_state,
                        "owner": owner.strip() or "Unassigned",
                        "doing_team": doing_team.strip() or owner.strip() or "Unassigned",
                        "informed": informed.strip(),
                        "source_of_truth": source_of_truth,
                        "ticket_ref": ticket_ref.strip(),
                        "notes": notes.strip(),
                        "risk_score": int(risk_score),
                        "last_update": date.today().isoformat(),
                        "due_date": due_date.isoformat(),
                        "evidence_count": int(evidence_count),
                        "test_results": test_results,
                    }
                    action = upsert_row(fields)
                    st.success(f"{'Updated' if action == 'updated' else 'Added'} {fields['control_id']}")
                    st.rerun()

    df = to_dataframe(st.session_state.controls)

    st.sidebar.subheader("Filters")
    fw_filter = st.sidebar.multiselect(
        "Framework",
        sorted(df["framework"].unique()) if not df.empty else FRAMEWORKS,
        default=sorted(df["framework"].unique()) if not df.empty else [],
    )
    coord_filter = st.sidebar.multiselect(
        "Coordination state",
        COORD_STATES,
        default=COORD_STATES,
    )
    sot_filter = st.sidebar.multiselect(
        "Source of truth",
        sorted(df["source_of_truth"].unique()) if not df.empty else WORK_SYSTEMS,
        default=sorted(df["source_of_truth"].unique()) if not df.empty else [],
    )
    risk_lo, risk_hi = st.sidebar.slider("Risk score", 0, 100, (0, 100))

    filtered = df
    if not df.empty:
        filtered = df[
            df["framework"].isin(fw_filter)
            & df["coord_state"].isin(coord_filter)
            & df["source_of_truth"].isin(sot_filter)
            & (df["risk_score"] >= risk_lo)
            & (df["risk_score"] <= risk_hi)
        ]

    m = metrics(filtered)
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Register", "Attention", "Export"])

    with tab1:
        st.header("Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Items", m["total"], delta=f"{m['aligned']} aligned")
        c2.metric("Needs attention", m["attention"], delta=f"{m['owner_mismatch']} owner≠doer")
        c3.metric("Past due", m["overdue"])
        c4.metric("Avg risk", f"{m['avg_risk']:.0f}", delta=f"{m['high_risk']} ≥70")

        if filtered.empty:
            st.info("No rows match the current filters.")
        else:
            left, right = st.columns(2)
            with left:
                counts = (
                    filtered["coord_state"]
                    .value_counts()
                    .reindex(COORD_STATES)
                    .fillna(0)
                )
                fig = px.pie(
                    names=counts.index,
                    values=counts.values,
                    title="Coordination state",
                    color=counts.index,
                    color_discrete_map=COORD_COLORS,
                )
                st.plotly_chart(fig, use_container_width=True)
            with right:
                sot = filtered["source_of_truth"].value_counts()
                fig2 = px.bar(
                    x=sot.index,
                    y=sot.values,
                    title="Source of truth",
                    labels={"x": "System", "y": "Items"},
                )
                st.plotly_chart(fig2, use_container_width=True)

            by_fw = (
                filtered.groupby(["framework", "coord_state"])
                .size()
                .reset_index(name="count")
            )
            fig3 = px.bar(
                by_fw,
                x="framework",
                y="count",
                color="coord_state",
                color_discrete_map=COORD_COLORS,
                title="Coordination by framework",
                barmode="stack",
            )
            st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.header("Register")
        search = st.text_input("Search", placeholder="ID, name, owner, ticket, issue…")
        sort_by = st.selectbox(
            "Sort by",
            ["Risk score", "Due date", "Coordination state", "Control ID", "Last update"],
        )

        view = filtered.copy()
        if search and not view.empty:
            q = search.lower()
            mask = False
            for col in (
                "control_id",
                "control_name",
                "issue",
                "owner",
                "doing_team",
                "source_of_truth",
                "ticket_ref",
                "notes",
            ):
                mask = mask | view[col].astype(str).str.lower().str.contains(q, na=False)
            view = view[mask]

        sort_map = {
            "Risk score": ("risk_score", False),
            "Due date": ("due_date", True),
            "Coordination state": ("coord_state", True),
            "Control ID": ("control_id", True),
            "Last update": ("last_update", False),
        }
        col, asc = sort_map[sort_by]
        if not view.empty:
            view = view.sort_values(col, ascending=asc)

        st.dataframe(
            view[EXPORT_COLS] if not view.empty else view,
            use_container_width=True,
            hide_index=True,
            height=420,
        )

        for _, row in view.iterrows():
            title = (
                f"{row['control_id']} — {row['control_name']} · "
                f"{row['coord_state']} · {row['source_of_truth']}"
            )
            with st.expander(title):
                a, b = st.columns([2, 1])
                with a:
                    st.write(f"**Issue:** {row['issue']}")
                    st.write(f"**Owner:** {row['owner']}")
                    st.write(f"**Doing team:** {row['doing_team']}")
                    st.write(f"**Informed:** {row['informed'] or '—'}")
                    st.write(f"**Source of truth:** {row['source_of_truth']}")
                    st.write(f"**Ticket / ref:** {row['ticket_ref'] or '—'}")
                    st.write(f"**Notes:** {row['notes'] or '—'}")
                with b:
                    st.metric("Risk", int(row["risk_score"]))
                    st.write(f"**Control status:** {row['control_status']}")
                    st.write(f"**Test:** {row['test_results']}")
                    st.write(f"**Evidence:** {row['evidence_count']}")
                    st.write(f"**Updated:** {row['last_update']}")
                    st.write(f"**Due:** {row['due_date']}")
                    if row["owner"] != row["doing_team"]:
                        st.warning("Owner and doing team differ.")
                    if row["coord_state"] in ("Undocumented", "Split ownership", "Status drift"):
                        st.error("Coordination gap — confirm durable source of truth.")
                    elif row["coord_state"] == "Aligned":
                        st.success("Ownership and source of truth look consistent.")

    with tab3:
        st.header("Attention queue")
        if filtered.empty:
            st.info("No rows to review.")
        else:
            needs = filtered[
                filtered["coord_state"].isin(
                    ["Undocumented", "Split ownership", "Status drift", "Pending transfer"]
                )
            ].sort_values("risk_score", ascending=False)

            overdue = filtered[pd.to_datetime(filtered["due_date"]) < datetime.now()]
            high = filtered[filtered["risk_score"] >= 70]

            if len(needs):
                st.warning(f"{len(needs)} items with coordination friction")
                st.dataframe(
                    needs[
                        [
                            "control_id",
                            "control_name",
                            "coord_state",
                            "source_of_truth",
                            "owner",
                            "doing_team",
                            "ticket_ref",
                            "risk_score",
                            "due_date",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.success("No coordination friction in the current filter set.")

            if len(overdue):
                st.error(f"{len(overdue)} past due")
                for _, row in overdue.iterrows():
                    days = (datetime.now() - pd.to_datetime(row["due_date"])).days
                    st.write(
                        f"• {row['control_id']} — {row['control_name']} "
                        f"({days}d) · {row['source_of_truth']} · {row['ticket_ref'] or 'no ticket'}"
                    )
            else:
                st.success("No past-due items in the filtered set.")

            if len(high):
                st.subheader("High risk (≥ 70)")
                st.dataframe(
                    high[
                        [
                            "control_id",
                            "control_name",
                            "coord_state",
                            "source_of_truth",
                            "owner",
                            "doing_team",
                            "risk_score",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

    with tab4:
        st.header("Export")
        st.caption(
            "Fork-friendly CSV of the filtered register. Session edits are not persisted server-side."
        )
        demo_kit.csv_download(
            filtered[EXPORT_COLS].copy() if not filtered.empty else filtered,
            "control_remediation_register.csv",
            label="Download filtered CSV",
        )
        summary = pd.DataFrame(
            {
                "Metric": [
                    "Items",
                    "Aligned",
                    "Needs attention",
                    "Owner ≠ doing team",
                    "Distinct sources of truth",
                    "High risk (≥70)",
                    "Past due",
                    "Average risk",
                ],
                "Value": [
                    m["total"],
                    m["aligned"],
                    m["attention"],
                    m["owner_mismatch"],
                    m["systems"],
                    m["high_risk"],
                    m["overdue"],
                    f"{m['avg_risk']:.1f}",
                ],
            }
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
