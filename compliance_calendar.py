#!/usr/bin/env python3
"""Compliance obligation calendar — club teaching toy."""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Compliance Calendar · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

STATUSES = ["Not started", "In progress", "Evidence due", "Complete"]
TYPES = [
    "Recertification",
    "Control test",
    "Evidence pack",
    "External audit",
    "Regulatory filing",
    "Policy review",
    "Training",
    "Exercise",
    "Committee pack",
]
PROGRAMS = ["SOC 2", "ISO 27001", "PCI DSS", "SOX", "GDPR", "NIST CSF", "Internal"]
STATUS_COLOR = {
    "Not started": "#91aa9b",
    "In progress": "#f2b84b",
    "Evidence due": "#ffb347",
    "Complete": "#38e881",
    "Overdue": "#ff6b6b",
}


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _sample_obligations(seed: int) -> pd.DataFrame:
    """Named GRC obligations with clocks relative to today — not a wall calendar."""
    today = _today()
    rng = np.random.default_rng(seed)

    def j(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    rows = [
        {
            "obligation_id": "OBL-2026-001",
            "title": "Q3 privileged access recertification",
            "obligation_type": "Recertification",
            "program": "SOC 2",
            "cadence": "Quarterly",
            "owner": "IAM",
            "work_product": "Manager attestations + exception list for standing privileged IDs",
            "status": "Evidence due",
            "ticket_ref": "GRC-REC-331",
            "notes": "Citrix VDI cohort still outstanding — same gap as EXC-2026-002.",
            "due": today + timedelta(days=4 + j(-2, 3)),
            "window_start": today - timedelta(days=20),
            "window_end": today + timedelta(days=10),
            "last_done": today - timedelta(days=92),
            "slip_count": 1,
        },
        {
            "obligation_id": "OBL-2026-002",
            "title": "SOC 2 Type II fieldwork (FY26)",
            "obligation_type": "External audit",
            "program": "SOC 2",
            "cadence": "Annual",
            "owner": "GRC",
            "work_product": "PBC list complete; walkthroughs; Type II sample evidence in GRC",
            "status": "In progress",
            "ticket_ref": "SOC2-FY26",
            "notes": "Deloitte on-site window. CUECs for payroll SaaS still thin.",
            "due": today + timedelta(days=24 + j(-3, 4)),
            "window_start": today - timedelta(days=5),
            "window_end": today + timedelta(days=24),
            "last_done": today - timedelta(days=370),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-003",
            "title": "PCI DSS ROC / AOC package",
            "obligation_type": "Regulatory filing",
            "program": "PCI DSS",
            "cadence": "Annual",
            "owner": "PCI Lead",
            "work_product": "Signed ROC + AOC to acquirer; ASV scans current",
            "status": "In progress",
            "ticket_ref": "PCI-2026-ROC",
            "notes": "Jump-host MFA waiver (EXC-2026-018) must be closed or disclosed.",
            "due": today + timedelta(days=48 + j(-4, 5)),
            "window_start": today + timedelta(days=20),
            "window_end": today + timedelta(days=48),
            "last_done": today - timedelta(days=340),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-004",
            "title": "ISO 27001 surveillance audit",
            "obligation_type": "External audit",
            "program": "ISO 27001",
            "cadence": "Annual",
            "owner": "ISMS owner",
            "work_product": "Statement of Applicability refresh + internal audit close-out",
            "status": "Not started",
            "ticket_ref": "ISO-SURV-26",
            "notes": "Internal audit finding on logging coverage still open.",
            "due": today + timedelta(days=95 + j(-6, 7)),
            "window_start": today + timedelta(days=80),
            "window_end": today + timedelta(days=95),
            "last_done": today - timedelta(days=280),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-005",
            "title": "Acceptable Use Policy annual review",
            "obligation_type": "Policy review",
            "program": "Internal",
            "cadence": "Annual",
            "owner": "Security Governance",
            "work_product": "Reviewed AUP posted; ack campaign ≥90%",
            "status": "Not started",
            "ticket_ref": "POL-2026-002",
            "notes": "Already past next-review on the policy library. Ack sitting ~81%.",
            "due": today - timedelta(days=22 + j(0, 6)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=400),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-006",
            "title": "IBM i QSECURITY / special-authority review",
            "obligation_type": "Recertification",
            "program": "SOX",
            "cadence": "Quarterly",
            "owner": "IBM i Ops",
            "work_product": "DSPUSRPRF extract + *ALLOBJ exceptions tied to EXC-2026-011",
            "status": "In progress",
            "ticket_ref": "IBMi-Q3-REV",
            "notes": "QAUDJRN sample ready; *ALLOBJ on ops profiles still waived.",
            "due": today + timedelta(days=11 + j(-2, 3)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=88),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-007",
            "title": "RACF SPECIAL / OPERATIONS recert",
            "obligation_type": "Recertification",
            "program": "SOX",
            "cadence": "Quarterly",
            "owner": "Mainframe Security",
            "work_product": "SIGNED recert of SPECIAL attributes; contractor IDs revoked or re-justified",
            "status": "Evidence due",
            "ticket_ref": "MF-REC-Q3",
            "notes": "Contractor SPECIAL (EXC-2026-012) lapsed — do not recertify as-is.",
            "due": today - timedelta(days=3 + j(0, 4)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=94),
            "slip_count": 1,
        },
        {
            "obligation_id": "OBL-2026-008",
            "title": "ERP backup restore drill",
            "obligation_type": "Exercise",
            "program": "SOC 2",
            "cadence": "Semi-annual",
            "owner": "Infrastructure",
            "work_product": "Restore timings vs RTO; checksum sign-off",
            "status": "Complete",
            "ticket_ref": "BC-DRILL-Q2",
            "notes": "Completed 3h 40m against 4h RTO. Next drill Q4.",
            "due": today - timedelta(days=40),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=40),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-009",
            "title": "Annual security awareness campaign close",
            "obligation_type": "Training",
            "program": "SOC 2",
            "cadence": "Annual",
            "owner": "People Ops",
            "work_product": "LMS completion ≥95%; phish-sim click-rate vs target",
            "status": "In progress",
            "ticket_ref": "AWR-2026",
            "notes": "Two contractor cohorts late. Completion ~88%.",
            "due": today + timedelta(days=16 + j(-3, 4)),
            "window_start": today - timedelta(days=45),
            "window_end": today + timedelta(days=16),
            "last_done": today - timedelta(days=360),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-010",
            "title": "GDPR Article 30 RoPA refresh",
            "obligation_type": "Regulatory filing",
            "program": "GDPR",
            "cadence": "Quarterly",
            "owner": "Privacy",
            "work_product": "Updated processing register + DPA log",
            "status": "Not started",
            "ticket_ref": "PRIV-ROPA-Q3",
            "notes": "New HRIS processor not on the register yet.",
            "due": today + timedelta(days=28 + j(-4, 5)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=80),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-011",
            "title": "Q3 risk committee pack",
            "obligation_type": "Committee pack",
            "program": "Internal",
            "cadence": "Quarterly",
            "owner": "GRC",
            "work_product": "KRI dashboard, top risks, exception aging, overdue obligations",
            "status": "Not started",
            "ticket_ref": "BRD-Q3-26",
            "notes": "Needs lapsed-exception count and this calendar's overdue list.",
            "due": today + timedelta(days=21 + j(-2, 3)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=85),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-012",
            "title": "Tier-1 vendor recertifications",
            "obligation_type": "Recertification",
            "program": "SOC 2",
            "cadence": "Annual",
            "owner": "TPRM",
            "work_product": "SOC reports on file + residual-risk memos for 8 Tier-1 vendors",
            "status": "Evidence due",
            "ticket_ref": "TPRM-T1-26",
            "notes": "Payroll SaaS SOC 2 bridge letter expired last month.",
            "due": today + timedelta(days=9 + j(-2, 3)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=355),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-013",
            "title": "MFA enforcement control test",
            "obligation_type": "Control test",
            "program": "SOC 2",
            "cadence": "Quarterly",
            "owner": "IT Security",
            "work_product": "Sample of remote-access and admin consoles vs AC-07",
            "status": "In progress",
            "ticket_ref": "CT-2026-009",
            "notes": "IBM i 5250 still excepted. Cloud admin consoles in sample.",
            "due": today + timedelta(days=7 + j(-2, 3)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=86),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-014",
            "title": "Ransomware tabletop",
            "obligation_type": "Exercise",
            "program": "NIST CSF",
            "cadence": "Annual",
            "owner": "SecOps",
            "work_product": "After-action + playbook updates",
            "status": "Complete",
            "ticket_ref": "IR-TTX-26",
            "notes": "Ran 2026-07-09. Comms templates still to refresh.",
            "due": today - timedelta(days=38),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=38),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-015",
            "title": "SOX 404 management certification",
            "obligation_type": "Regulatory filing",
            "program": "SOX",
            "cadence": "Annual",
            "owner": "CFO / ITGC lead",
            "work_product": "ITGC testing complete; deficiency log; management assertion",
            "status": "Not started",
            "ticket_ref": "SOX-404-FY26",
            "notes": "Year-end. Depends on access recerts and change-control samples.",
            "due": today + timedelta(days=130 + j(-8, 9)),
            "window_start": today + timedelta(days=90),
            "window_end": today + timedelta(days=130),
            "last_done": today - timedelta(days=250),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-016",
            "title": "Exception register aging review",
            "obligation_type": "Evidence pack",
            "program": "Internal",
            "cadence": "Monthly",
            "owner": "GRC",
            "work_product": "Lapsed-in-prod list + repeat-extension memo to CISO",
            "status": "Not started",
            "ticket_ref": "EXC-AGE-AUG",
            "notes": "Pull from the waiver workbench. RACF and Citrix recert are the story.",
            "due": today + timedelta(days=5 + j(-1, 2)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=28),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-017",
            "title": "SAP Firefighter / SAP_ALL recert",
            "obligation_type": "Recertification",
            "program": "SOX",
            "cadence": "Quarterly",
            "owner": "ERP Security",
            "work_product": "Firefighter logs + SU01 dual-control sample",
            "status": "Not started",
            "ticket_ref": "SAP-FF-Q3",
            "notes": "Firefighter workflow still In Review as a waiver.",
            "due": today + timedelta(days=19 + j(-3, 4)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=89),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-018",
            "title": "Central logging coverage evidence",
            "obligation_type": "Control test",
            "program": "SOC 2",
            "cadence": "Quarterly",
            "owner": "SecOps",
            "work_product": "Asset inventory vs SIEM sources; DMZ gap close-out",
            "status": "Evidence due",
            "ticket_ref": "CT-2026-006",
            "notes": "Failed last test — 6 DMZ jump hosts. Corrective due this window.",
            "due": today - timedelta(days=8 + j(0, 4)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=25),
            "slip_count": 1,
        },
        {
            "obligation_id": "OBL-2026-019",
            "title": "BCP / crisis comms tabletop",
            "obligation_type": "Exercise",
            "program": "ISO 27001",
            "cadence": "Annual",
            "owner": "Business Continuity",
            "work_product": "Scenario write-up + action log",
            "status": "Not started",
            "ticket_ref": "BCP-TTX-26",
            "notes": "Schedule after SOC 2 fieldwork so GRC is not double-booked.",
            "due": today + timedelta(days=70 + j(-5, 6)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=310),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-020",
            "title": "DPIA — new HRIS processor",
            "obligation_type": "Evidence pack",
            "program": "GDPR",
            "cadence": "Ad hoc",
            "owner": "Privacy",
            "work_product": "DPIA signed before go-live; DPA executed",
            "status": "In progress",
            "ticket_ref": "DPIA-HRIS-26",
            "notes": "Legal has the DPA. Go-live targeted next month.",
            "due": today + timedelta(days=33 + j(-4, 5)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": pd.NaT,
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-021",
            "title": "Q2 access recertification close-out",
            "obligation_type": "Recertification",
            "program": "SOC 2",
            "cadence": "Quarterly",
            "owner": "IAM",
            "work_product": "Completed campaign pack in GRC",
            "status": "Complete",
            "ticket_ref": "GRC-REC-318",
            "notes": "Closed on time. Citrix follow-ups rolled into Q3.",
            "due": today - timedelta(days=55),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=52),
            "slip_count": 0,
        },
        {
            "obligation_id": "OBL-2026-022",
            "title": "Records retention legal-hold cleanup",
            "obligation_type": "Policy review",
            "program": "GDPR",
            "cadence": "Annual",
            "owner": "Privacy / Legal",
            "work_product": "Hold register vs repositories; disposal evidence",
            "status": "Not started",
            "ticket_ref": "STD-2026-017",
            "notes": "Retention standard is past review on the policy library.",
            "due": today - timedelta(days=14 + j(0, 5)),
            "window_start": pd.NaT,
            "window_end": pd.NaT,
            "last_done": today - timedelta(days=390),
            "slip_count": 0,
        },
    ]
    df = pd.DataFrame(rows)
    for col in ("due", "window_start", "window_end", "last_done"):
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["days_to_due"] = (out["due"] - today).dt.days
    open_row = ~out["status"].eq("Complete")
    out["is_overdue"] = open_row & (out["days_to_due"] < 0)
    out["due_7"] = open_row & out["days_to_due"].between(0, 7)
    out["due_30"] = open_row & out["days_to_due"].between(0, 30)
    out["display_status"] = np.where(out["is_overdue"], "Overdue", out["status"])
    out["in_window"] = (
        out["window_start"].notna()
        & (out["window_start"] <= today)
        & out["window_end"].notna()
        & (out["window_end"] >= today)
        & open_row
    )
    return out


def _sync(seed: int) -> pd.DataFrame:
    if st.session_state.get("_cal_seed") != seed or "obligations" not in st.session_state:
        st.session_state.obligations = _sample_obligations(seed)
        st.session_state._cal_seed = seed
    return st.session_state.obligations


def _save(df: pd.DataFrame) -> None:
    st.session_state.obligations = df.reset_index(drop=True)


def _patch(oid: str, **fields) -> None:
    df = st.session_state.obligations.copy()
    loc = df.index[df["obligation_id"] == oid]
    if len(loc) == 0:
        return
    i = loc[0]
    for k, v in fields.items():
        df.at[i, k] = v
    _save(df)


def _metrics(df: pd.DataFrame) -> dict:
    e = _enrich(df)
    return {
        "overdue": int(e["is_overdue"].sum()),
        "due_7": int(e["due_7"].sum()),
        "due_30": int(e["due_30"].sum()),
        "in_flight": int((e["status"] == "In progress").sum()),
        "in_window": int(e["in_window"].sum()),
        "done_q": int(
            (
                e["status"].eq("Complete")
                & e["last_done"].notna()
                & (e["last_done"] >= _today() - timedelta(days=90))
            ).sum()
        ),
    }


def _fmt(ts) -> str:
    if pd.isna(ts):
        return "—"
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def _detail(row: pd.Series) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Type / program:** {row['obligation_type']} · {row['program']}")
        st.write(f"**Cadence:** {row['cadence']}")
        st.write(f"**Status:** {row['display_status']}")
        st.write(f"**Owner:** {row['owner']}")
        st.write(f"**Ticket:** {row['ticket_ref'] or '—'}")
        st.write(f"**Slips:** {int(row['slip_count'])}")
    with c2:
        st.write(f"**Due:** {_fmt(row['due'])} ({int(row['days_to_due'])}d)")
        st.write(f"**Window:** {_fmt(row['window_start'])} → {_fmt(row['window_end'])}")
        st.write(f"**Last completed:** {_fmt(row['last_done'])}")
        st.write(f"**Work product:** {row['work_product']}")
    st.write(f"**Notes:** {row['notes']}")


def _actions(row: pd.Series, *, key: str) -> None:
    oid = row["obligation_id"]
    today = _today()
    a1, a2, a3 = st.columns(3)
    with a1:
        if row["status"] in {"Not started", "Evidence due"} and st.button(
            "Start / in progress", key=f"ip_{key}", use_container_width=True
        ):
            _patch(oid, status="In progress")
            st.rerun()
    with a2:
        if row["status"] != "Complete" and st.button(
            "Mark complete", key=f"done_{key}", use_container_width=True
        ):
            _patch(oid, status="Complete", last_done=today)
            st.rerun()
    with a3:
        if row["status"] != "Complete" and st.button(
            "Slip 14 days", key=f"slip_{key}", use_container_width=True
        ):
            new_due = pd.Timestamp(row["due"]) + timedelta(days=14)
            fields = {"due": new_due, "slip_count": int(row["slip_count"]) + 1}
            if pd.notna(row["window_end"]):
                fields["window_end"] = pd.Timestamp(row["window_end"]) + timedelta(days=14)
            _patch(oid, **fields)
            st.rerun()


def _queue(title: str, subset: pd.DataFrame, empty: str, key_prefix: str) -> None:
    st.markdown(f"**{title} ({len(subset)})**")
    if subset.empty:
        st.info(empty)
        return
    for _, row in subset.iterrows():
        due_txt = f"{int(row['days_to_due'])}d" if row["days_to_due"] >= 0 else f"{abs(int(row['days_to_due']))}d overdue"
        with st.expander(
            f"{row['obligation_id']} · {row['title']} · {row['display_status']} · {due_txt}"
        ):
            _detail(row)
            _actions(row, key=f"{key_prefix}_{row['obligation_id']}")


def main() -> None:
    portfolio_skin.page_header(
        title="Compliance Calendar",
        lede="Obligation look-ahead: what's due, who owns it, what 'done' looks like. Club demo — not a system of record.",
        kicker="Compliance",
    )

    seed = demo_kit.seed_controls()
    df = _sync(seed)
    enriched = _enrich(df)
    m = _metrics(df)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    status_f = st.sidebar.multiselect(
        "Status",
        ["Overdue"] + STATUSES,
        default=["Overdue"] + STATUSES,
    )
    type_f = st.sidebar.multiselect("Type", TYPES, default=TYPES)
    program_f = st.sidebar.multiselect("Program", PROGRAMS, default=PROGRAMS)
    horizon = st.sidebar.slider("Look-ahead (days)", 14, 180, 60, 7)

    filtered = enriched[
        enriched["display_status"].isin(status_f)
        & enriched["obligation_type"].isin(type_f)
        & enriched["program"].isin(program_f)
    ]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Overdue", m["overdue"], help="Past due and not complete — this is the Monday list.")
    k2.metric("Due in 7 days", m["due_7"])
    k3.metric("Due in 30 days", m["due_30"])
    k4.metric("In-flight windows", m["in_window"], help="External audit / campaign currently in its fieldwork window.")
    st.caption(f"In progress: {m['in_flight']} · Completed in last 90 days: {m['done_q']}")

    work, register, ahead, intake, export = st.tabs(
        ["Workbench", "Register", "Look-ahead", "Intake", "Export"]
    )

    with work:
        st.subheader("This week's GRC list")
        st.caption(
            "A compliance calendar is an obligation register with dates — not a month grid. "
            "Overdue first, then this week, then evidence sitting with owners."
        )
        overdue = enriched[enriched["is_overdue"]].sort_values("days_to_due")
        week = enriched[enriched["due_7"]].sort_values("days_to_due")
        evidence = enriched[enriched["status"].eq("Evidence due") & ~enriched["is_overdue"]].sort_values(
            "days_to_due"
        )
        windows = enriched[enriched["in_window"]].sort_values("due")

        _queue("Overdue", overdue, "Nothing past due. Rare, enjoy it.", "od")
        _queue("Due in 7 days", week, "Clear week.", "wk")
        _queue(
            "Evidence sitting with owners",
            evidence,
            "No open evidence requests outside the overdue/week lists.",
            "ev",
        )
        _queue("In a live window (audit / campaign)", windows, "No fieldwork windows open today.", "win")

    with register:
        st.subheader("Obligation register")
        show = filtered[
            [
                "obligation_id",
                "title",
                "obligation_type",
                "program",
                "cadence",
                "display_status",
                "owner",
                "due",
                "days_to_due",
                "ticket_ref",
                "slip_count",
            ]
        ].copy()
        show["due"] = show["due"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)
        ids = filtered["obligation_id"].tolist()
        if ids:
            pick = st.selectbox("Open a record", ids)
            row = enriched[enriched["obligation_id"] == pick].iloc[0]
            _detail(row)
            _actions(row, key=f"reg_{pick}")

    with ahead:
        st.subheader(f"Next {horizon} days")
        st.caption("Point-in-time dues plus any multi-day audit/campaign windows.")
        cutoff = _today() + timedelta(days=horizon)
        floor = _today() - timedelta(days=14)
        horizon_df = filtered[
            (filtered["due"] <= cutoff) & (filtered["due"] >= floor) & ~filtered["status"].eq("Complete")
        ].sort_values("due")

        if horizon_df.empty:
            st.info("Nothing open in this look-ahead. Widen the slider or clear filters.")
        else:
            by_day = horizon_df.copy()
            by_day["due_day"] = by_day["due"].dt.strftime("%Y-%m-%d (%a)")
            for day, grp in by_day.groupby("due_day", sort=True):
                st.markdown(f"**{day}**")
                st.dataframe(
                    grp[["obligation_id", "title", "owner", "display_status", "program"]],
                    use_container_width=True,
                    hide_index=True,
                )

            plot_df = filtered[~filtered["status"].eq("Complete")].copy()
            fig = px.scatter(
                plot_df,
                x="days_to_due",
                y="obligation_type",
                color="display_status",
                hover_name="obligation_id",
                hover_data=["title", "owner", "program"],
                color_discrete_map=STATUS_COLOR,
                category_orders={"obligation_type": TYPES, "display_status": ["Overdue"] + STATUSES},
                title="Days to due (negative = overdue)",
            )
            fig.add_vline(x=0, line_dash="dash", line_color="#ff6b6b")
            fig.add_vline(x=7, line_dash="dot", line_color="#f2b84b")
            fig.add_vline(x=30, line_dash="dot", line_color="#91aa9b")
            st.plotly_chart(fig, use_container_width=True)

            windows = filtered[filtered["window_start"].notna() & ~filtered["status"].eq("Complete")]
            if not windows.empty:
                gantt = windows.copy()
                gantt["start"] = gantt["window_start"]
                gantt["finish"] = gantt["window_end"].fillna(gantt["due"])
                fig_g = px.timeline(
                    gantt,
                    x_start="start",
                    x_end="finish",
                    y="title",
                    color="display_status",
                    color_discrete_map=STATUS_COLOR,
                    hover_data=["obligation_id", "owner"],
                    title="Fieldwork / campaign windows",
                )
                fig_g.add_vline(x=_today(), line_dash="dash", line_color="#e8f4ec")
                st.plotly_chart(fig_g, use_container_width=True)

    with intake:
        st.subheader("Add an obligation")
        st.caption("Name the work product. A date without 'what done looks like' is a meeting, not an obligation.")
        with st.form("intake"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Title", placeholder="e.g. Q4 privileged access recert")
                obligation_type = st.selectbox("Type", TYPES)
                program = st.selectbox("Program", PROGRAMS)
                cadence = st.selectbox(
                    "Cadence",
                    ["Ad hoc", "Monthly", "Quarterly", "Semi-annual", "Annual"],
                    index=2,
                )
            with c2:
                owner = st.text_input("Owner", placeholder="e.g. IAM")
                due = st.date_input("Due date", value=(_today() + timedelta(days=30)).date())
                ticket_ref = st.text_input("Ticket / ref", placeholder="GRC-…")
                work_product = st.text_area("Work product (definition of done)")
            notes = st.text_input("Notes", placeholder="Optional context")
            submitted = st.form_submit_button("Add to register")
        if submitted:
            if not title.strip() or not owner.strip() or not work_product.strip():
                st.error("Title, owner, and work product are required.")
            else:
                n = len(st.session_state.obligations) + 1
                new_id = f"OBL-2026-{n:03d}"
                add = {
                    "obligation_id": new_id,
                    "title": title.strip(),
                    "obligation_type": obligation_type,
                    "program": program,
                    "cadence": cadence,
                    "owner": owner.strip(),
                    "work_product": work_product.strip(),
                    "status": "Not started",
                    "ticket_ref": ticket_ref.strip(),
                    "notes": notes.strip(),
                    "due": pd.Timestamp(due),
                    "window_start": pd.NaT,
                    "window_end": pd.NaT,
                    "last_done": pd.NaT,
                    "slip_count": 0,
                }
                _save(pd.concat([st.session_state.obligations, pd.DataFrame([add])], ignore_index=True))
                st.success(f"{new_id} is on the register.")
                st.rerun()

    with export:
        st.subheader("Filtered obligations")
        out = filtered.copy()
        for col in ("due", "window_start", "window_end", "last_done"):
            out[col] = out[col].apply(_fmt)
        demo_kit.csv_download(out, "compliance_obligations.csv")
        st.caption("Resample rebuilds the demo set. Edits live in this browser session only.")


if __name__ == "__main__":
    main()
