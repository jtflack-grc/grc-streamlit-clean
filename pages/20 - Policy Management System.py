#!/usr/bin/env python3
"""Policy / standard register — club teaching toy."""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Policy Management System · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

STATUSES = ["Draft", "In Review", "Approved", "Published", "Retired"]
DOC_TYPES = ["Policy", "Standard", "Procedure"]
DOMAINS = ["Security", "Privacy", "Access", "Operations", "Third party", "IT"]
STATUS_COLOR = {
    "Draft": "#91aa9b",
    "In Review": "#f2b84b",
    "Approved": "#7fffb2",
    "Published": "#38e881",
    "Retired": "#5c7a68",
}
ACK_THRESHOLD = 90


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _sample_policies(seed: int) -> pd.DataFrame:
    """Named policy set a GRC team would actually keep, with clocks relative to today."""
    today = _today()
    rng = np.random.default_rng(seed)

    def j(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    def ack(base: int) -> int:
        return int(np.clip(base + j(-4, 5), 0, 99))

    rows = [
        {
            "policy_id": "POL-2026-001",
            "title": "Information Security Policy",
            "doc_type": "Policy",
            "domain": "Security",
            "version": "3.1",
            "status": "Published",
            "owner": "Security Governance",
            "approver": "CISO",
            "audience": "All workforce",
            "framework": "ISO 27001 A.5.1 · SOC 2 CC1.2",
            "purpose": "Management intent for protecting information; parent of the standards library.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": ack(96),
            "open_exceptions": 1,
            "issued": today - timedelta(days=400),
            "effective": today - timedelta(days=380),
            "last_review": today - timedelta(days=80),
            "next_review": today + timedelta(days=280 + j(-8, 9)),
        },
        {
            "policy_id": "POL-2026-002",
            "title": "Acceptable Use Policy",
            "doc_type": "Policy",
            "domain": "Security",
            "version": "2.4",
            "status": "Published",
            "owner": "Security Governance",
            "approver": "CHRO / CISO",
            "audience": "All workforce",
            "framework": "ISO 27001 A.5.10 · SOC 2 CC1.1",
            "purpose": "Permitted use of company systems, including personal devices and AI tools.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": ack(81),
            "open_exceptions": 0,
            "issued": today - timedelta(days=500),
            "effective": today - timedelta(days=490),
            "last_review": today - timedelta(days=400),
            "next_review": today - timedelta(days=22 + j(0, 8)),
        },
        {
            "policy_id": "POL-2026-003",
            "title": "Access Control Policy",
            "doc_type": "Policy",
            "domain": "Access",
            "version": "2.0",
            "status": "Published",
            "owner": "IAM",
            "approver": "CISO",
            "audience": "All workforce · IAM operators",
            "framework": "ISO 27001 A.5.15 · SOC 2 CC6.1 · NIST AC",
            "purpose": "Joiner/mover/leaver, least privilege, and recertification cadence.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": ack(93),
            "open_exceptions": 3,
            "issued": today - timedelta(days=360),
            "effective": today - timedelta(days=350),
            "last_review": today - timedelta(days=330),
            "next_review": today + timedelta(days=18 + j(-4, 5)),
        },
        {
            "policy_id": "POL-2026-004",
            "title": "Data Protection Policy",
            "doc_type": "Policy",
            "domain": "Privacy",
            "version": "1.3",
            "status": "In Review",
            "owner": "Privacy",
            "approver": "",
            "audience": "All workforce · processors",
            "framework": "GDPR Art. 24/32 · ISO 27001 A.8.10",
            "purpose": "Lawful processing, retention, and transfer of personal data. Legal redlines in flight.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": None,
            "open_exceptions": 0,
            "issued": today - timedelta(days=20),
            "effective": pd.NaT,
            "last_review": pd.NaT,
            "next_review": today + timedelta(days=14),
        },
        {
            "policy_id": "POL-2026-005",
            "title": "Incident Response Policy",
            "doc_type": "Policy",
            "domain": "Security",
            "version": "1.8",
            "status": "Published",
            "owner": "SecOps",
            "approver": "CISO",
            "audience": "IR leadership · on-call · Comms",
            "framework": "ISO 27001 A.5.24 · NIST RS · SOC 2 CC7.3",
            "purpose": "Severity model, notify/contain/eradicate, and evidence handling.",
            "review_cycle_months": 12,
            "ack_required": False,
            "ack_rate": None,
            "open_exceptions": 0,
            "issued": today - timedelta(days=210),
            "effective": today - timedelta(days=200),
            "last_review": today - timedelta(days=40),
            "next_review": today + timedelta(days=320 + j(-6, 7)),
        },
        {
            "policy_id": "STD-2026-006",
            "title": "Authenticator & Password Standard",
            "doc_type": "Standard",
            "domain": "Access",
            "version": "4.0",
            "status": "Published",
            "owner": "IAM",
            "approver": "CISO",
            "audience": "System owners · IAM",
            "framework": "NIST 800-63B · ISO 27001 A.5.17 · PCI 8",
            "purpose": "MFA, length, rotation exceptions, and service-account rules.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": ack(74),
            "open_exceptions": 2,
            "issued": today - timedelta(days=140),
            "effective": today - timedelta(days=130),
            "last_review": today - timedelta(days=130),
            "next_review": today + timedelta(days=230 + j(-8, 9)),
        },
        {
            "policy_id": "STD-2026-007",
            "title": "IBM i Security Standard (QSECURITY / special authorities)",
            "doc_type": "Standard",
            "domain": "IT",
            "version": "1.2",
            "status": "Published",
            "owner": "IBM i Ops",
            "approver": "CISO",
            "audience": "IBM i operators · Security",
            "framework": "IBM i Security Standard · ISO 27001 A.8.2",
            "purpose": "QSECURITY level, *ALLOBJ / QSECOFR day-use, QAUDJRN, and 5250 MFA exit.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": ack(71),
            "open_exceptions": 2,
            "issued": today - timedelta(days=125),
            "effective": today - timedelta(days=120),
            "last_review": today - timedelta(days=120),
            "next_review": today + timedelta(days=245 + j(-6, 7)),
        },
        {
            "policy_id": "STD-2026-008",
            "title": "Mainframe Security Standard (RACF / z/OS)",
            "doc_type": "Standard",
            "domain": "IT",
            "version": "2.0",
            "status": "Approved",
            "owner": "Mainframe Security",
            "approver": "CISO",
            "audience": "z/OS security · contractors",
            "framework": "RACF standard · ISO 27001 A.8.2",
            "purpose": "SPECIAL / OPERATIONS use, contractor TSO duration, SMF review. Approved, not yet posted.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": None,
            "open_exceptions": 1,
            "issued": today - timedelta(days=18),
            "effective": pd.NaT,
            "last_review": pd.NaT,
            "next_review": today + timedelta(days=30),
        },
        {
            "policy_id": "POL-2026-009",
            "title": "Third-Party Risk Policy",
            "doc_type": "Policy",
            "domain": "Third party",
            "version": "1.1",
            "status": "Published",
            "owner": "TPRM",
            "approver": "CISO / Procurement",
            "audience": "Procurement · vendor owners",
            "framework": "SOC 2 CC9.2 · ISO 27001 A.5.19",
            "purpose": "Due diligence tiers, contract clauses, and ongoing monitoring.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": ack(88),
            "open_exceptions": 1,
            "issued": today - timedelta(days=430),
            "effective": today - timedelta(days=420),
            "last_review": today - timedelta(days=400),
            "next_review": today - timedelta(days=8 + j(0, 6)),
        },
        {
            "policy_id": "STD-2026-010",
            "title": "Encryption Standard",
            "doc_type": "Standard",
            "domain": "Security",
            "version": "2.2",
            "status": "Published",
            "owner": "Security Engineering",
            "approver": "CISO",
            "audience": "Engineering · infrastructure",
            "framework": "ISO 27001 A.8.24 · PCI 3.4 · NIST SC-28",
            "purpose": "TLS, at-rest keys, and approved algorithms. CMK preferred.",
            "review_cycle_months": 24,
            "ack_required": False,
            "ack_rate": None,
            "open_exceptions": 1,
            "issued": today - timedelta(days=200),
            "effective": today - timedelta(days=190),
            "last_review": today - timedelta(days=40),
            "next_review": today + timedelta(days=500 + j(-10, 11)),
        },
        {
            "policy_id": "POL-2026-011",
            "title": "Backup & Recovery Policy",
            "doc_type": "Policy",
            "domain": "Operations",
            "version": "1.4",
            "status": "In Review",
            "owner": "Infrastructure",
            "approver": "",
            "audience": "IT Ops · app owners",
            "framework": "ISO 27001 A.8.13 · SOC 2 CC6.1",
            "purpose": "RPO/RTO classes and restore-test cadence. Waiting on Legal hold language.",
            "review_cycle_months": 12,
            "ack_required": False,
            "ack_rate": None,
            "open_exceptions": 0,
            "issued": today - timedelta(days=12),
            "effective": pd.NaT,
            "last_review": pd.NaT,
            "next_review": today + timedelta(days=21),
        },
        {
            "policy_id": "STD-2026-012",
            "title": "Logging & Monitoring Standard",
            "doc_type": "Standard",
            "domain": "Security",
            "version": "1.6",
            "status": "Published",
            "owner": "SecOps",
            "approver": "CISO",
            "audience": "Platform owners",
            "framework": "ISO 27001 A.8.15 · SOC 2 CC7.2 · NIST DE.CM",
            "purpose": "What must land in SIEM, retention, and privileged-session recording.",
            "review_cycle_months": 12,
            "ack_required": False,
            "ack_rate": None,
            "open_exceptions": 1,
            "issued": today - timedelta(days=175),
            "effective": today - timedelta(days=170),
            "last_review": today - timedelta(days=30),
            "next_review": today + timedelta(days=335 + j(-8, 9)),
        },
        {
            "policy_id": "POL-2026-013",
            "title": "Physical Security Policy",
            "doc_type": "Policy",
            "domain": "Operations",
            "version": "1.0",
            "status": "Retired",
            "owner": "Facilities",
            "approver": "COO",
            "audience": "Facilities · all sites",
            "framework": "ISO 27001 A.7",
            "purpose": "Superseded by POL-2026-001 §physical + site playbooks. Kept for audit trail.",
            "review_cycle_months": 24,
            "ack_required": False,
            "ack_rate": None,
            "open_exceptions": 0,
            "issued": today - timedelta(days=900),
            "effective": today - timedelta(days=880),
            "last_review": today - timedelta(days=60),
            "next_review": pd.NaT,
        },
        {
            "policy_id": "POL-2026-014",
            "title": "Acceptable Use of Generative AI",
            "doc_type": "Policy",
            "domain": "Security",
            "version": "0.9",
            "status": "Draft",
            "owner": "Security Governance",
            "approver": "",
            "audience": "All workforce",
            "framework": "ISO 27001 A.5.10 · internal AI board",
            "purpose": "What may be pasted into public models; approved tools; data-class rules.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": None,
            "open_exceptions": 0,
            "issued": today - timedelta(days=75),
            "effective": pd.NaT,
            "last_review": pd.NaT,
            "next_review": today + timedelta(days=30),
        },
        {
            "policy_id": "STD-2026-015",
            "title": "SAP Access Standard (SU01 / Firefighter)",
            "doc_type": "Standard",
            "domain": "Access",
            "version": "1.0",
            "status": "Published",
            "owner": "ERP Security",
            "approver": "CISO",
            "audience": "SAP Basis · finance ops",
            "framework": "SAP security standard · SOX ITGC",
            "purpose": "SAP_ALL prohibition, Firefighter, and dual-control for SU01.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": ack(67),
            "open_exceptions": 1,
            "issued": today - timedelta(days=95),
            "effective": today - timedelta(days=90),
            "last_review": today - timedelta(days=90),
            "next_review": today + timedelta(days=270 + j(-6, 7)),
        },
        {
            "policy_id": "POL-2026-016",
            "title": "Change Management Policy",
            "doc_type": "Policy",
            "domain": "Operations",
            "version": "2.1",
            "status": "Published",
            "owner": "IT Operations",
            "approver": "CIO",
            "audience": "All change requesters",
            "framework": "ISO 27001 A.8.32 · SOC 2 CC8.1",
            "purpose": "CAB, emergency change, and production freeze windows.",
            "review_cycle_months": 12,
            "ack_required": False,
            "ack_rate": None,
            "open_exceptions": 0,
            "issued": today - timedelta(days=260),
            "effective": today - timedelta(days=250),
            "last_review": today - timedelta(days=20),
            "next_review": today + timedelta(days=340 + j(-6, 7)),
        },
        {
            "policy_id": "STD-2026-017",
            "title": "Records Retention Standard",
            "doc_type": "Standard",
            "domain": "Privacy",
            "version": "1.2",
            "status": "Published",
            "owner": "Privacy / Legal",
            "approver": "General Counsel",
            "audience": "Data owners · Legal",
            "framework": "GDPR Art. 5(1)(e) · ISO 27001 A.8.10",
            "purpose": "Retention classes and legal-hold overlay. Review slipped during hold cleanup.",
            "review_cycle_months": 12,
            "ack_required": True,
            "ack_rate": ack(62),
            "open_exceptions": 1,
            "issued": today - timedelta(days=410),
            "effective": today - timedelta(days=400),
            "last_review": today - timedelta(days=390),
            "next_review": today - timedelta(days=35 + j(0, 10)),
        },
        {
            "policy_id": "PRC-2026-018",
            "title": "Privileged Access Checkout Procedure",
            "doc_type": "Procedure",
            "domain": "Access",
            "version": "1.0",
            "status": "Draft",
            "owner": "IAM",
            "approver": "",
            "audience": "PAM operators",
            "framework": "ISO 27001 A.8.2 · PCI 8.1",
            "purpose": "How to check out break-glass via PAM, including IBM i and SAP IDs.",
            "review_cycle_months": 12,
            "ack_required": False,
            "ack_rate": None,
            "open_exceptions": 0,
            "issued": today - timedelta(days=50),
            "effective": pd.NaT,
            "last_review": pd.NaT,
            "next_review": today + timedelta(days=40),
        },
    ]
    df = pd.DataFrame(rows)
    for col in ("issued", "effective", "last_review", "next_review"):
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["ack_rate"] = pd.to_numeric(df["ack_rate"], errors="coerce")
    return df


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["days_to_review"] = (out["next_review"] - today).dt.days
    in_force = out["status"].eq("Published")
    out["review_overdue"] = in_force & out["next_review"].notna() & (out["next_review"] < today)
    out["review_due_90"] = in_force & out["days_to_review"].between(0, 90)
    out["low_ack"] = (
        in_force
        & out["ack_required"].eq(True)
        & out["ack_rate"].notna()
        & (out["ack_rate"] < ACK_THRESHOLD)
    )
    out["aging_draft"] = out["status"].eq("Draft") & ((today - out["issued"]).dt.days >= 45)
    out["awaiting"] = out["status"].isin(["Draft", "In Review", "Approved"])
    return out


def _sync(seed: int) -> pd.DataFrame:
    if st.session_state.get("_policy_seed") != seed or "policies" not in st.session_state:
        st.session_state.policies = _sample_policies(seed)
        st.session_state._policy_seed = seed
    return st.session_state.policies


def _save(df: pd.DataFrame) -> None:
    st.session_state.policies = df.reset_index(drop=True)


def _patch(policy_id: str, **fields) -> None:
    df = st.session_state.policies.copy()
    loc = df.index[df["policy_id"] == policy_id]
    if len(loc) == 0:
        return
    i = loc[0]
    for k, v in fields.items():
        df.at[i, k] = v
    _save(df)


def _bump_version(version: str) -> str:
    try:
        major, minor = str(version).split(".")[:2]
        return f"{int(major)}.{int(minor) + 1}"
    except (ValueError, TypeError):
        return f"{version}.1"


def _metrics(df: pd.DataFrame) -> dict:
    e = _enrich(df)
    published = e[e["status"] == "Published"]
    return {
        "in_force": int(len(published)),
        "awaiting": int(e["status"].isin(["Draft", "In Review", "Approved"]).sum()),
        "overdue": int(e["review_overdue"].sum()),
        "due_90": int(e["review_due_90"].sum()),
        "low_ack": int(e["low_ack"].sum()),
        "exceptions": int(pd.to_numeric(e["open_exceptions"], errors="coerce").fillna(0).sum()),
    }


def _fmt(ts) -> str:
    if pd.isna(ts):
        return "—"
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def _detail(row: pd.Series) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Type / domain:** {row['doc_type']} · {row['domain']}")
        st.write(f"**Version:** {row['version']} · **{row['status']}**")
        st.write(f"**Owner / approver:** {row['owner']} / {row['approver'] or '— (pending)'}")
        st.write(f"**Audience:** {row['audience']}")
        st.write(f"**Maps to:** {row['framework']}")
        st.write(f"**Open exceptions:** {int(row['open_exceptions'])}")
    with c2:
        st.write(f"**Issued:** {_fmt(row['issued'])}")
        st.write(f"**Effective:** {_fmt(row['effective'])}")
        st.write(f"**Last review:** {_fmt(row['last_review'])}")
        days = row["days_to_review"]
        clock = "—" if pd.isna(days) else f"{int(days)}d"
        st.write(f"**Next review:** {_fmt(row['next_review'])} ({clock})")
        st.write(f"**Review cycle:** {int(row['review_cycle_months'])} months")
        if row["ack_required"]:
            ack = "—" if pd.isna(row["ack_rate"]) else f"{int(row['ack_rate'])}%"
            st.write(f"**Acknowledgement:** {ack} (required)")
        else:
            st.write("**Acknowledgement:** not required (role-based / technical)")
    st.write(f"**Purpose:** {row['purpose']}")


def _actions(row: pd.Series, *, key: str) -> None:
    pid = row["policy_id"]
    today = _today()
    cycle = int(row["review_cycle_months"] or 12)
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if row["status"] == "Draft" and st.button(
            "Submit for review", key=f"rev_{key}", use_container_width=True
        ):
            _patch(pid, status="In Review")
            st.rerun()
        if row["status"] == "In Review" and st.button(
            "Approve", key=f"appr_{key}", use_container_width=True
        ):
            _patch(pid, status="Approved", approver=row["approver"] or "CISO (demo)")
            st.rerun()
    with a2:
        if row["status"] == "In Review" and st.button(
            "Return to draft", key=f"back_{key}", use_container_width=True
        ):
            _patch(pid, status="Draft")
            st.rerun()
        if row["status"] == "Approved" and st.button(
            "Publish", key=f"pub_{key}", use_container_width=True
        ):
            fields = {
                "status": "Published",
                "effective": today,
                "last_review": today,
                "next_review": today + timedelta(days=cycle * 30),
            }
            if row["ack_required"]:
                fields["ack_rate"] = 0
            _patch(pid, **fields)
            st.rerun()
    with a3:
        if row["status"] == "Published" and st.button(
            "Complete review", key=f"done_{key}", use_container_width=True
        ):
            _patch(
                pid,
                version=_bump_version(str(row["version"])),
                last_review=today,
                next_review=today + timedelta(days=cycle * 30),
            )
            st.rerun()
    with a4:
        if row["status"] not in {"Retired"} and st.button(
            "Retire", key=f"ret_{key}", use_container_width=True
        ):
            _patch(pid, status="Retired", next_review=pd.NaT)
            st.rerun()
    if row["status"] == "Published" and row["ack_required"] and (
        pd.isna(row["ack_rate"]) or int(row["ack_rate"]) < ACK_THRESHOLD
    ):
        if st.button("Record ack campaign (95%)", key=f"ack_{key}"):
            _patch(pid, ack_rate=95)
            st.rerun()


def main() -> None:
    portfolio_skin.page_header(
        title="Policy Management System",
        lede="Policies, standards, and procedures: draft, approve, publish, review on a clock. Club demo — not a system of record.",
        kicker="Governance",
    )

    seed = demo_kit.seed_controls()
    df = _sync(seed)
    enriched = _enrich(df)
    m = _metrics(df)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Library filters")
    status_f = st.sidebar.multiselect("Status", STATUSES, default=STATUSES)
    type_f = st.sidebar.multiselect("Document type", DOC_TYPES, default=DOC_TYPES)
    domain_f = st.sidebar.multiselect("Domain", DOMAINS, default=DOMAINS)

    filtered = enriched[
        enriched["status"].isin(status_f)
        & enriched["doc_type"].isin(type_f)
        & enriched["domain"].isin(domain_f)
    ]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("In force", m["in_force"], help="Published — this is what people are held to.")
    k2.metric("In pipeline", m["awaiting"], help="Draft, in review, or approved but not posted.")
    k3.metric("Review overdue", m["overdue"], help="Still published, past next-review date.")
    k4.metric(f"Ack below {ACK_THRESHOLD}%", m["low_ack"])
    st.caption(
        f"Reviews due in 90 days: {m['due_90']} · "
        f"Open exceptions pointing at this library: {m['exceptions']}"
    )

    work, library, intake, aging, export = st.tabs(
        ["Workbench", "Library", "Intake", "Aging", "Export"]
    )

    with work:
        st.subheader("Needs a policy owner")
        st.caption(
            "Published documents stay in force until retired. Overdue review is not the same as draft. "
            "Approved-but-unpublished is a shelf document — auditors will ask why."
        )

        overdue = enriched[enriched["review_overdue"]].sort_values("next_review")
        due = enriched[enriched["review_due_90"]].sort_values("days_to_review")
        pipeline = enriched[enriched["status"].isin(["In Review", "Approved"])].sort_values("issued")
        drafts = enriched[enriched["aging_draft"]].sort_values("issued")
        low = enriched[enriched["low_ack"]].sort_values("ack_rate")

        st.markdown(f"**Periodic review overdue ({len(overdue)})**")
        if overdue.empty:
            st.success("No published documents past their review date.")
        else:
            for _, row in overdue.iterrows():
                with st.expander(
                    f"{row['policy_id']} · {row['title']} · due {_fmt(row['next_review'])}"
                ):
                    _detail(row)
                    _actions(row, key=f"od_{row['policy_id']}")

        st.markdown(f"**Review due in 90 days ({len(due)})**")
        if due.empty:
            st.info("Nothing in the 90-day review window.")
        else:
            for _, row in due.iterrows():
                with st.expander(
                    f"{row['policy_id']} · {row['title']} · {int(row['days_to_review'])}d"
                ):
                    _detail(row)
                    _actions(row, key=f"d90_{row['policy_id']}")

        st.markdown(f"**Awaiting approval or publish ({len(pipeline)})**")
        if pipeline.empty:
            st.info("No documents sitting in review or on the approval shelf.")
        else:
            for _, row in pipeline.iterrows():
                with st.expander(f"{row['policy_id']} · {row['title']} · {row['status']}"):
                    _detail(row)
                    _actions(row, key=f"pipe_{row['policy_id']}")

        st.markdown(f"**Acknowledgement lag ({len(low)})**")
        if low.empty:
            st.info(f"Published documents that require ack are at or above {ACK_THRESHOLD}%.")
        else:
            st.warning("Workforce attestation is part of 'policy communicated' evidence.")
            for _, row in low.iterrows():
                with st.expander(
                    f"{row['policy_id']} · {row['title']} · {int(row['ack_rate'])}% ack"
                ):
                    _detail(row)
                    _actions(row, key=f"ackq_{row['policy_id']}")

        st.markdown(f"**Aging drafts (≥45 days) ({len(drafts)})**")
        if drafts.empty:
            st.info("No stale drafts.")
        else:
            for _, row in drafts.iterrows():
                with st.expander(f"{row['policy_id']} · {row['title']}"):
                    _detail(row)
                    _actions(row, key=f"dr_{row['policy_id']}")

    with library:
        st.subheader("Policy library")
        show = filtered[
            [
                "policy_id",
                "title",
                "doc_type",
                "domain",
                "version",
                "status",
                "owner",
                "next_review",
                "days_to_review",
                "ack_rate",
                "open_exceptions",
            ]
        ].copy()
        show["next_review"] = show["next_review"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)
        ids = filtered["policy_id"].tolist()
        if ids:
            pick = st.selectbox("Open a record", ids)
            row = enriched[enriched["policy_id"] == pick].iloc[0]
            _detail(row)
            _actions(row, key=f"lib_{pick}")

    with intake:
        st.subheader("New document")
        st.caption("A real intake names the owner, the audience, and whether people must attest.")
        with st.form("intake"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Title", placeholder="e.g. Remote Access Policy")
                doc_type = st.selectbox("Document type", DOC_TYPES)
                domain = st.selectbox("Domain", DOMAINS)
                owner = st.text_input("Owner", placeholder="e.g. IAM")
                audience = st.text_input("Audience", placeholder="e.g. All workforce")
            with c2:
                framework = st.text_input("Framework map", placeholder="ISO 27001 A.5.15 · SOC 2 CC6")
                cycle = st.selectbox("Review cycle (months)", [12, 24], index=0)
                ack_required = st.checkbox("Acknowledgement required", value=True)
                purpose = st.text_area("Purpose (one or two sentences)")
            submitted = st.form_submit_button("Create as draft")
        if submitted:
            if not title.strip() or not owner.strip() or not purpose.strip():
                st.error("Title, owner, and purpose are required.")
            else:
                n = len(st.session_state.policies) + 1
                prefix = {"Policy": "POL", "Standard": "STD", "Procedure": "PRC"}[doc_type]
                new_id = f"{prefix}-2026-{n:03d}"
                today = _today()
                add = {
                    "policy_id": new_id,
                    "title": title.strip(),
                    "doc_type": doc_type,
                    "domain": domain,
                    "version": "0.1",
                    "status": "Draft",
                    "owner": owner.strip(),
                    "approver": "",
                    "audience": audience.strip() or "TBD",
                    "framework": framework.strip() or "TBD",
                    "purpose": purpose.strip(),
                    "review_cycle_months": int(cycle),
                    "ack_required": bool(ack_required),
                    "ack_rate": np.nan,
                    "open_exceptions": 0,
                    "issued": today,
                    "effective": pd.NaT,
                    "last_review": pd.NaT,
                    "next_review": today + timedelta(days=45),
                }
                _save(pd.concat([st.session_state.policies, pd.DataFrame([add])], ignore_index=True))
                st.success(f"{new_id} is a draft on the Workbench.")
                st.rerun()

    with aging:
        st.subheader("Review clock")
        plot_df = filtered[filtered["status"] != "Retired"].copy()
        if plot_df.empty:
            st.info("No rows in the current filter.")
        else:
            fig = px.scatter(
                plot_df,
                x="days_to_review",
                y="doc_type",
                color="status",
                hover_name="policy_id",
                hover_data=["title", "owner", "ack_rate"],
                color_discrete_map=STATUS_COLOR,
                category_orders={"status": STATUSES, "doc_type": DOC_TYPES},
                title="Days to next review (negative = overdue)",
            )
            fig.add_vline(x=0, line_dash="dash", line_color="#ff6b6b")
            fig.add_vline(x=90, line_dash="dot", line_color="#f2b84b")
            st.plotly_chart(fig, use_container_width=True)

            c1, c2 = st.columns(2)
            with c1:
                status_counts = (
                    plot_df["status"]
                    .value_counts()
                    .reindex(STATUSES)
                    .fillna(0)
                    .rename_axis("status")
                    .reset_index(name="count")
                )
                fig_s = px.bar(
                    status_counts,
                    x="status",
                    y="count",
                    color="status",
                    color_discrete_map=STATUS_COLOR,
                    title="By status",
                )
                fig_s.update_layout(showlegend=False)
                st.plotly_chart(fig_s, use_container_width=True)
            with c2:
                ack_view = plot_df[plot_df["ack_required"] & plot_df["ack_rate"].notna()]
                if ack_view.empty:
                    st.info("No acknowledgement rates in this filter.")
                else:
                    fig_a = px.bar(
                        ack_view.sort_values("ack_rate"),
                        x="ack_rate",
                        y="policy_id",
                        orientation="h",
                        title=f"Ack rate (threshold {ACK_THRESHOLD}%)",
                        labels={"ack_rate": "Acknowledgement %"},
                    )
                    fig_a.add_vline(x=ACK_THRESHOLD, line_dash="dot", line_color="#f2b84b")
                    st.plotly_chart(fig_a, use_container_width=True)

    with export:
        st.subheader("Filtered library")
        out = filtered.copy()
        for col in ("issued", "effective", "last_review", "next_review"):
            out[col] = out[col].apply(_fmt)
        demo_kit.csv_download(out, "policy_library.csv")
        st.caption("Resample rebuilds the demo set. Edits live in this browser session only.")


if __name__ == "__main__":
    main()
