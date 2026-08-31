#!/usr/bin/env python3
"""NIST CSF 2.0 maturity & readiness workbench — club teaching toy.

Vanta/Drata-style posture view: six CSF functions, subcategory maturity (CMMI 0–5),
implementation tier, evidence/tests, current vs target profile, gap queue, and
board narrative. Synthetic portfolio cross-links — not a live GRC integration.
"""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="CSF Maturity Assessment · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

FUNCTIONS = [
    ("Govern", "GV", "Cybersecurity risk management strategy, roles, policy, and oversight", "#6366f1"),
    ("Identify", "ID", "Understand organizational context and cyber risk to systems, people, assets, data", "#3b82f6"),
    ("Protect", "PR", "Safeguards to manage and limit impact of cybersecurity events", "#f59e0b"),
    ("Detect", "DE", "Timely discovery of cybersecurity events", "#22c55e"),
    ("Respond", "RS", "Actions regarding a detected cybersecurity incident", "#ef4444"),
    ("Recover", "RC", "Restore capabilities and services impaired by incidents", "#a855f7"),
]

MATURITY_LABELS = {
    0: "Not performed",
    1: "Ad hoc",
    2: "Repeatable",
    3: "Defined",
    4: "Managed",
    5: "Optimized",
}

TIER_LABELS = {
    1: "Tier 1 — Partial",
    2: "Tier 2 — Risk informed",
    3: "Tier 3 — Repeatable",
    4: "Tier 4 — Adaptive",
}

EVIDENCE_STATUS = ["Current", "Stale", "Missing", "Exception"]
TEST_STATUS = ["Passing", "Failing", "Not monitored", "Manual only"]
GAP_STATUS = ["Open", "In progress", "Blocked", "Closed"]
FEATURED = {
    "GV.RR-02",
    "ID.AM-05",
    "PR.AA-05",
    "DE.CM-03",
    "RS.MA-02",
    "RC.RP-03",
}
_SYNC_KEY = "_csf_seed_v1"


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _subcategory_catalog() -> list[dict]:
    """Representative NIST CSF 2.0 subcategories (demo subset, structurally faithful)."""
    rows = [
        # Govern
        ("GV.OC-01", "Govern", "GV.OC", "Organizational mission understood and informs cybersecurity risk management"),
        ("GV.OC-02", "Govern", "GV.OC", "Internal and external stakeholders identified and needs understood"),
        ("GV.RM-01", "Govern", "GV.RM", "Risk management objectives established and agreed by stakeholders"),
        ("GV.RM-04", "Govern", "GV.RM", "Strategic direction for cybersecurity risk management communicated"),
        ("GV.RR-01", "Govern", "GV.RR", "Leadership accountability for cybersecurity risk management established"),
        ("GV.RR-02", "Govern", "GV.RR", "Roles, responsibilities, and authorities for cybersecurity communicated"),
        ("GV.PO-01", "Govern", "GV.PO", "Policy for managing cybersecurity risks established and communicated"),
        ("GV.OV-01", "Govern", "GV.OV", "Cybersecurity risk management strategy outcomes reviewed"),
        ("GV.SC-01", "Govern", "GV.SC", "Cyber supply-chain risk management program established"),
        ("GV.SC-04", "Govern", "GV.SC", "Suppliers known and prioritized by criticality"),
        # Identify
        ("ID.AM-01", "Identify", "ID.AM", "Inventories of hardware managed and maintained"),
        ("ID.AM-02", "Identify", "ID.AM", "Inventories of software, services, and systems maintained"),
        ("ID.AM-05", "Identify", "ID.AM", "Assets prioritized based on classification, criticality, and business value"),
        ("ID.RA-01", "Identify", "ID.RA", "Vulnerabilities in assets identified, validated, and recorded"),
        ("ID.RA-05", "Identify", "ID.RA", "Threats, vulnerabilities, likelihoods, and impacts used to understand risk"),
        ("ID.RA-07", "Identify", "ID.RA", "Risk responses identified, prioritized, and implemented"),
        ("ID.IM-01", "Identify", "ID.IM", "Improvements from assessments and exercises incorporated"),
        ("ID.SC-02", "Identify", "ID.SC", "Suppliers and partners identified, prioritized, and monitored"),
        # Protect
        ("PR.AA-01", "Protect", "PR.AA", "Identities and credentials managed for authorized users and services"),
        ("PR.AA-03", "Protect", "PR.AA", "Users, services, and hardware authenticated"),
        ("PR.AA-05", "Protect", "PR.AA", "Access permissions, entitlements, and authorizations managed"),
        ("PR.AT-01", "Protect", "PR.AT", "Personnel provided awareness and training for general duties"),
        ("PR.AT-02", "Protect", "PR.AT", "Privileged users trained for specialized roles"),
        ("PR.DS-01", "Protect", "PR.DS", "Data-at-rest protected"),
        ("PR.DS-02", "Protect", "PR.DS", "Data-in-transit protected"),
        ("PR.DS-10", "Protect", "PR.DS", "Data destroyed per policy"),
        ("PR.PS-01", "Protect", "PR.PS", "Configuration management practices established and applied"),
        ("PR.PS-04", "Protect", "PR.PS", "Log records generated and made available for monitoring"),
        ("PR.IR-01", "Protect", "PR.IR", "Networks and environments protected from unauthorized logical access"),
        ("PR.PT-01", "Protect", "PR.PT", "Audit/log records determined, documented, and managed"),
        # Detect
        ("DE.AE-02", "Detect", "DE.AE", "Potentially adverse events analyzed to characterize and detect incidents"),
        ("DE.AE-06", "Detect", "DE.AE", "Information on adverse events provided to authorized staff and tools"),
        ("DE.CM-01", "Detect", "DE.CM", "Networks and network services monitored for potentially adverse events"),
        ("DE.CM-03", "Detect", "DE.CM", "Personnel activity and technology usage monitored for adverse events"),
        ("DE.CM-09", "Detect", "DE.CM", "Computing hardware, software, runtime, and data monitored"),
        ("DE.DP-02", "Detect", "DE.DP", "Detection processes tested for effectiveness and accuracy"),
        # Respond
        ("RS.MA-01", "Respond", "RS.MA", "Incident management plan executed in coordination with stakeholders"),
        ("RS.MA-02", "Respond", "RS.MA", "Incident reports triaged and validated"),
        ("RS.AN-03", "Respond", "RS.AN", "Analysis performed to establish what occurred and root cause"),
        ("RS.CO-02", "Respond", "RS.CO", "Internal and external stakeholders notified per plan"),
        ("RS.MI-01", "Respond", "RS.MI", "Incidents contained and eradicated"),
        ("RS.IM-01", "Respond", "RS.IM", "Incident response plan improved by incorporating lessons learned"),
        # Recover
        ("RC.RP-01", "Recover", "RC.RP", "Recovery portion of incident response plan executed"),
        ("RC.RP-03", "Recover", "RC.RP", "Backups verified, maintained, and stored per policy"),
        ("RC.RP-04", "Recover", "RC.RP", "Critical mission functions and services restored"),
        ("RC.CO-03", "Recover", "RC.CO", "Recovery activities communicated to stakeholders"),
        ("RC.IM-01", "Recover", "RC.IM", "Recovery plans improved by incorporating lessons learned"),
    ]
    return [
        {
            "subcat_id": sid,
            "function": fn,
            "category": cat,
            "title": title,
        }
        for sid, fn, cat, title in rows
    ]


def _sample(seed: int):
    today = _today()
    rng = np.random.default_rng(seed)
    catalog = _subcategory_catalog()

    # Curated current/target scores — incident-shaped story (portal stuffing, PayrollCo, IBM i gaps)
    profile = {
        "GV.OC-01": (3, 4), "GV.OC-02": (3, 4), "GV.RM-01": (3, 4), "GV.RM-04": (2, 4),
        "GV.RR-01": (4, 4), "GV.RR-02": (2, 4), "GV.PO-01": (3, 4), "GV.OV-01": (3, 4),
        "GV.SC-01": (2, 3), "GV.SC-04": (2, 3),
        "ID.AM-01": (3, 4), "ID.AM-02": (2, 4), "ID.AM-05": (2, 4), "ID.RA-01": (3, 4),
        "ID.RA-05": (3, 4), "ID.RA-07": (2, 4), "ID.IM-01": (2, 3), "ID.SC-02": (2, 3),
        "PR.AA-01": (3, 4), "PR.AA-03": (3, 4), "PR.AA-05": (2, 4), "PR.AT-01": (3, 4),
        "PR.AT-02": (3, 4), "PR.DS-01": (3, 4), "PR.DS-02": (3, 4), "PR.DS-10": (2, 3),
        "PR.PS-01": (2, 4), "PR.PS-04": (3, 4), "PR.IR-01": (3, 4), "PR.PT-01": (3, 4),
        "DE.AE-02": (3, 4), "DE.AE-06": (2, 4), "DE.CM-01": (3, 4), "DE.CM-03": (2, 4),
        "DE.CM-09": (2, 4), "DE.DP-02": (2, 3),
        "RS.MA-01": (3, 4), "RS.MA-02": (2, 4), "RS.AN-03": (3, 4), "RS.CO-02": (3, 4),
        "RS.MI-01": (3, 4), "RS.IM-01": (2, 4),
        "RC.RP-01": (3, 4), "RC.RP-03": (2, 4), "RC.RP-04": (3, 4), "RC.CO-03": (3, 4),
        "RC.IM-01": (2, 3),
    }

    owners = {
        "Govern": "CISO / GRC",
        "Identify": "Risk & Asset Mgmt",
        "Protect": "Security Engineering",
        "Detect": "SOC Lead",
        "Respond": "IR Lead",
        "Recover": "BCP / IT Ops",
    }

    subcats = []
    for row in catalog:
        sid = row["subcat_id"]
        cur, tgt = profile.get(sid, (2, 4))
        gap = cur < tgt
        ev_roll = float(rng.random())
        if cur >= 4:
            evidence = "Current"
            test = "Passing"
        elif cur <= 1:
            evidence = "Missing" if ev_roll < 0.5 else "Stale"
            test = "Failing" if ev_roll < 0.6 else "Not monitored"
        else:
            evidence = rng.choice(["Current", "Stale", "Missing"], p=[0.45, 0.35, 0.2])
            test = rng.choice(["Passing", "Failing", "Manual only", "Not monitored"], p=[0.4, 0.25, 0.2, 0.15])

        subcats.append(
            {
                **row,
                "current": cur,
                "target": tgt,
                "current_label": MATURITY_LABELS[cur],
                "target_label": MATURITY_LABELS[tgt],
                "gap": gap,
                "gap_pts": max(0, tgt - cur),
                "owner": owners[row["function"]],
                "evidence_status": evidence,
                "test_status": test,
                "in_scope": True,
                "last_assessed": today - timedelta(days=int(rng.integers(3, 45))),
                "evidence_count": int(rng.integers(0, 6)) if evidence != "Missing" else 0,
                "automated_tests": int(rng.integers(0, 4)),
                "linked": "",
                "notes": "",
            }
        )

    # Featured narrative overrides
    overrides = {
        "GV.RR-02": {
            "notes": "Board asked who owns reporting after INC-2026-001 — RACI still fuzzy between helpdesk and SOC.",
            "linked": "INC-2026-001 · CMP-2026-001",
            "evidence_status": "Stale",
            "test_status": "Manual only",
        },
        "ID.AM-05": {
            "notes": "Crown-jewel list disagrees with CMDB — GAP-2026-001 open; KRI-2026-001 off target.",
            "linked": "GAP-2026-001 · KRI-2026-001 · AST-2026-005",
            "current": 2,
            "target": 4,
            "gap": True,
            "gap_pts": 2,
            "evidence_status": "Stale",
            "test_status": "Failing",
        },
        "PR.AA-05": {
            "notes": "PayrollCo freeze blocked entitlement review — shared admin on JDE World still open.",
            "linked": "INC-2026-009 · PayrollCo",
            "current": 2,
            "test_status": "Failing",
        },
        "DE.CM-03": {
            "notes": "UEBA not covering IBM i / colo night crew — email read rate <40% in ops.",
            "linked": "CMP-2026-001 · IBM i Ops",
            "current": 2,
            "test_status": "Not monitored",
        },
        "RS.MA-02": {
            "notes": "Portal stuffing triage SLA missed on 340 forwarded mails — playbooks assume SOC intake, not helpdesk flood.",
            "linked": "INC-2026-001 · PHISH-2026-003",
            "current": 2,
            "evidence_status": "Stale",
        },
        "RC.RP-03": {
            "notes": "PayrollCo backup attestation expired during IR — RPO argument with processor unresolved.",
            "linked": "INC-2026-009 · DST-2026-001",
            "current": 2,
            "test_status": "Failing",
        },
    }
    for item in subcats:
        if item["subcat_id"] in overrides:
            item.update(overrides[item["subcat_id"]])
            item["current_label"] = MATURITY_LABELS[item["current"]]
            item["gap"] = item["current"] < item["target"]
            item["gap_pts"] = max(0, item["target"] - item["current"])

    sub_df = pd.DataFrame(subcats)

    gaps = [
        {
            "gap_id": "GAP-CSF-001",
            "subcat_id": "ID.AM-05",
            "title": "Crown-jewel asset prioritization not evidenced in CMDB",
            "priority": "Critical",
            "status": "In progress",
            "owner": "CAASM / GRC",
            "due": today + timedelta(days=14),
            "remediation": "Reconcile CAASM export with business crown-jewel register; close GAP-2026-001.",
            "linked": "GAP-2026-001 · KRI-2026-001",
        },
        {
            "gap_id": "GAP-CSF-002",
            "subcat_id": "GV.RR-02",
            "title": "Incident reporting RACI not communicated post-board review",
            "priority": "High",
            "status": "Open",
            "owner": "CISO office",
            "due": today + timedelta(days=21),
            "remediation": "Publish updated RACI; align helpdesk auto-reply with Phish Alert workflow (CMP-2026-001).",
            "linked": "INC-2026-001 · CMP-2026-001",
        },
        {
            "gap_id": "GAP-CSF-003",
            "subcat_id": "PR.AA-05",
            "title": "Privileged access review blocked for PayrollCo scope",
            "priority": "High",
            "status": "Blocked",
            "owner": "IAM Engineering",
            "due": today + timedelta(days=30),
            "remediation": "Resume entitlement review when processor lifts IR freeze; document compensating controls.",
            "linked": "INC-2026-009",
        },
        {
            "gap_id": "GAP-CSF-004",
            "subcat_id": "DE.CM-03",
            "title": "Operations / colo activity monitoring gap",
            "priority": "Medium",
            "status": "In progress",
            "owner": "SOC Lead",
            "due": today + timedelta(days=45),
            "remediation": "Extend UEBA to IBM i session exports; shift huddle comms per campaign WAV-2026-004.",
            "linked": "CMP-2026-001",
        },
        {
            "gap_id": "GAP-CSF-005",
            "subcat_id": "RS.MA-02",
            "title": "Helpdesk phishing flood not in IR triage playbook",
            "priority": "High",
            "status": "Open",
            "owner": "IR Lead",
            "due": today + timedelta(days=18),
            "remediation": "Add mass-forward scenario to IR plan; tabletop with helpdesk + SOC.",
            "linked": "INC-2026-001",
        },
        {
            "gap_id": "GAP-CSF-006",
            "subcat_id": "RC.RP-03",
            "title": "Third-party backup verification stale for payroll processor",
            "priority": "Critical",
            "status": "In progress",
            "owner": "BCP / Vendor Mgmt",
            "due": today + timedelta(days=10),
            "remediation": "Obtain PayrollCo restore test attestation; update BCP RPO table for board.",
            "linked": "INC-2026-009 · DST-2026-001",
        },
        {
            "gap_id": "GAP-CSF-007",
            "subcat_id": "GV.SC-04",
            "title": "Critical supplier tiering not refreshed after Orbit AMS onboarding",
            "priority": "Medium",
            "status": "Open",
            "owner": "TPRM",
            "due": today + timedelta(days=35),
            "remediation": "Complete Orbit AMS tiering workshop; map to CMP-2026-004 vendor pack.",
            "linked": "CMP-2026-004",
        },
        {
            "gap_id": "GAP-CSF-008",
            "subcat_id": "PR.PS-01",
            "title": "Configuration drift on jump hosts — change mgmt evidence thin",
            "priority": "Medium",
            "status": "In progress",
            "owner": "Platform Eng",
            "due": today + timedelta(days=28),
            "remediation": "Enforce IaC pipeline for JUMP-DMZ-03; tie to control testing AST-2026-005.",
            "linked": "AST-2026-005",
        },
    ]
    gaps_df = pd.DataFrame(gaps)

    # Quarterly assessment snapshots (function-level readiness %)
    quarters = pd.date_range(end=today, periods=8, freq="QE")
    hist = []
    base_readiness = {"Govern": 58, "Identify": 62, "Protect": 68, "Detect": 55, "Respond": 61, "Recover": 57}
    for i, q in enumerate(quarters):
        for fn, _, _, _ in FUNCTIONS:
            drift = i * 2.2 + (hash(fn) % 5)
            noise = float(rng.normal(0, 1.5))
            score = min(92, max(38, base_readiness[fn] + drift * 0.35 + noise))
            hist.append({"period": q, "period_label": f"Q{q.quarter} {q.year}", "function": fn, "readiness_pct": round(score, 1)})
    hist_df = pd.DataFrame(hist)

    # Implementation tier assessment (organizational)
    tier = {
        "overall_tier": 2,
        "overall_label": TIER_LABELS[2],
        "target_tier": 3,
        "target_label": TIER_LABELS[3],
        "as_of": today,
        "assessor": "GRC · external facilitator (sample)",
        "narrative": (
            "Risk-informed but uneven: board oversight is real after Q3 incidents, yet detection and "
            "recovery evidence trails protect/identify. Tier 3 requires repeatable evidence — not slide decks."
        ),
        "dimensions": [
            {"dimension": "Governance", "current": 3, "target": 3, "note": "Board cadence improved; RACI gaps remain"},
            {"dimension": "Risk management", "current": 2, "target": 3, "note": "Risk register fresh; crown-jewel prioritization weak"},
            {"dimension": "Supply chain", "current": 2, "target": 3, "note": "PayrollCo + Orbit AMS elevated scrutiny"},
            {"dimension": "Operations", "current": 2, "target": 3, "note": "SOC solid; IBM i / colo blind spots"},
            {"dimension": "Assurance", "current": 2, "target": 3, "note": "Tests exist; too many manual-only"},
        ],
    }

    narrative = pd.DataFrame(
        [
            {
                "lane": "Board ask",
                "text": "After INC-2026-001/005/009 the board wants CSF 2.0 readiness — not a maturity vanity score. "
                "Current profile: 67% subcategories at/above target; 11 critical/high gaps open.",
            },
            {
                "lane": "What improved",
                "text": "Govern function up 6 pts since Q1 — policy refresh, quarterly oversight, CISO town halls tied to CMP-2026-001.",
            },
            {
                "lane": "What regressed",
                "text": "Detect readiness flat — helpdesk flood and colo monitoring gaps. Recover dragged by PayrollCo backup attestation.",
            },
            {
                "lane": "Next 90 days",
                "text": "Close GAP-CSF-001/006 (crown jewels + PayrollCo backups), publish reporting RACI, extend monitoring to operations shifts.",
            },
        ]
    )

    evidence_tests = pd.DataFrame(
        [
            {"test_id": "T-CSF-001", "subcat_id": "PR.AA-03", "name": "MFA coverage — workforce", "status": "Passing", "last_run": today - timedelta(days=1), "source": "IdP integration"},
            {"test_id": "T-CSF-002", "subcat_id": "PR.AA-05", "name": "Privileged access review ≤90d", "status": "Failing", "last_run": today - timedelta(days=2), "source": "IAM / GRC"},
            {"test_id": "T-CSF-003", "subcat_id": "ID.AM-05", "name": "Crown-jewel CMDB match", "status": "Failing", "last_run": today - timedelta(days=3), "source": "CAASM"},
            {"test_id": "T-CSF-004", "subcat_id": "DE.CM-01", "name": "Network sensor coverage", "status": "Passing", "last_run": today - timedelta(days=1), "source": "SIEM"},
            {"test_id": "T-CSF-005", "subcat_id": "DE.CM-03", "name": "UEBA — ops / colo users", "status": "Not monitored", "last_run": None, "source": "UEBA"},
            {"test_id": "T-CSF-006", "subcat_id": "RC.RP-03", "name": "Backup restore test evidence", "status": "Failing", "last_run": today - timedelta(days=7), "source": "BCP / vendor portal"},
            {"test_id": "T-CSF-007", "subcat_id": "GV.PO-01", "name": "Policy acknowledgment current", "status": "Passing", "last_run": today - timedelta(days=4), "source": "GRC"},
            {"test_id": "T-CSF-008", "subcat_id": "RS.MA-02", "name": "IR triage SLA ≤1h Sev2", "status": "Failing", "last_run": today - timedelta(days=5), "source": "IR ticketing"},
        ]
    )

    return sub_df, gaps_df, hist_df, tier, narrative, evidence_tests


def _enrich_subcats(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["at_target"] = out["current"] >= out["target"]
    out["readiness_pct"] = (out["current"] / out["target"].clip(lower=1) * 100).clip(0, 100)
    out["failing_test"] = out["test_status"] == "Failing"
    out["evidence_risk"] = out["evidence_status"].isin(["Missing", "Stale"])
    return out


def _function_readiness(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fn, _, _, color in FUNCTIONS:
        sub = df[df["function"] == fn]
        if sub.empty:
            continue
        at_tgt = sub["at_target"].mean() * 100
        avg_cur = sub["current"].mean()
        avg_tgt = sub["target"].mean()
        gaps = int((~sub["at_target"]).sum())
        rows.append(
            {
                "function": fn,
                "color": color,
                "readiness_pct": round(at_tgt, 1),
                "avg_current": round(avg_cur, 2),
                "avg_target": round(avg_tgt, 2),
                "subcategories": len(sub),
                "gaps": gaps,
            }
        )
    return pd.DataFrame(rows)


def _overall_readiness(df: pd.DataFrame, *, weighted: bool = False) -> float:
    scoped = df[df["in_scope"]]
    if scoped.empty:
        return 0.0
    if not weighted:
        return round(scoped["at_target"].mean() * 100, 1)
    # Gap-weighted: partial credit by current/target ratio
    ratio = (scoped["current"] / scoped["target"].clip(lower=1)).clip(0, 1)
    return round(ratio.mean() * 100, 1)


def _sync(seed: int):
    need = st.session_state.get(_SYNC_KEY) != seed or "csf_subcats" not in st.session_state
    if need:
        s, g, h, t, n, e = _sample(seed)
        st.session_state.csf_subcats = s
        st.session_state.csf_gaps = g
        st.session_state.csf_history = h
        st.session_state.csf_tier = t
        st.session_state.csf_narrative = n
        st.session_state.csf_tests = e
        st.session_state[_SYNC_KEY] = seed
    return (
        st.session_state.csf_subcats,
        st.session_state.csf_gaps,
        st.session_state.csf_history,
        st.session_state.csf_tier,
        st.session_state.csf_narrative,
        st.session_state.csf_tests,
    )


def _save_subcats(df: pd.DataFrame):
    st.session_state.csf_subcats = df.reset_index(drop=True)


def _patch_subcat(sid: str, **fields):
    df = st.session_state.csf_subcats.copy()
    loc = df.index[df["subcat_id"] == sid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    if "current" in fields:
        df.at[loc[0], "current_label"] = MATURITY_LABELS[int(fields["current"])]
        df.at[loc[0], "gap"] = df.at[loc[0], "current"] < df.at[loc[0], "target"]
        df.at[loc[0], "gap_pts"] = max(0, int(df.at[loc[0], "target"]) - int(df.at[loc[0], "current"]))
    _save_subcats(df)


def _fmt(ts) -> str:
    if ts is None or (isinstance(ts, float) and np.isnan(ts)):
        return "—"
    try:
        if pd.isna(ts):
            return "—"
    except (TypeError, ValueError):
        pass
    try:
        return pd.Timestamp(ts).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _maturity_color(score: int) -> str:
    palette = {0: "#7f1d1d", 1: "#b91c1c", 2: "#d97706", 3: "#ca8a04", 4: "#16a34a", 5: "#059669"}
    return palette.get(int(score), "#6b7280")


def _heatmap(subcats: pd.DataFrame, *, key: str):
    pivot = subcats.pivot_table(index="category", columns="function", values="current", aggfunc="mean")
    fn_order = [f[0] for f in FUNCTIONS]
    pivot = pivot.reindex(columns=[c for c in fn_order if c in pivot.columns])
    z = pivot.values
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[
                [0, "#7f1d1d"],
                [0.2, "#b91c1c"],
                [0.4, "#d97706"],
                [0.6, "#ca8a04"],
                [0.8, "#16a34a"],
                [1, "#059669"],
            ],
            zmin=0,
            zmax=5,
            text=np.round(z, 1),
            texttemplate="%{text}",
            hovertemplate="Category %{y}<br>%{x}<br>Avg maturity: %{z:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Subcategory maturity heatmap (avg current 0–5)",
        height=max(320, 40 * len(pivot.index)),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


def _profile_radar(subcats: pd.DataFrame, *, key: str):
    fr = _function_readiness(subcats)
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=fr["avg_current"].tolist(),
            theta=fr["function"].tolist(),
            fill="toself",
            name="Current profile",
            line_color="#38e881",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=fr["avg_target"].tolist(),
            theta=fr["function"].tolist(),
            fill="toself",
            name="Target profile",
            line_color="#6366f1",
            opacity=0.35,
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        title="Current vs target profile (function average maturity)",
        height=420,
        margin=dict(l=40, r=40, t=50, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


def _subcat_detail(row, *, widget_key: str):
    sid = row["subcat_id"]
    wk = f"{widget_key}_{sid}"
    st.markdown(f"### {sid} · {row['title']}")
    a, b, c, d, e = st.columns(5)
    a.metric("Current", f"{row['current']}/5", delta=row["current_label"])
    b.metric("Target", f"{row['target']}/5", delta=row["target_label"])
    c.metric("Gap", f"{row['gap_pts']} pts" if row["gap"] else "At target")
    d.metric("Evidence", row["evidence_status"])
    e.metric("Test", row["test_status"])

    c1, c2 = st.columns(2)
    c1.write(f"**Function / category:** {row['function']} · {row['category']}")
    c1.write(f"**Owner:** {row['owner']} · **Last assessed:** {_fmt(row['last_assessed'])}")
    c1.write(f"**Evidence items:** {row['evidence_count']} · **Automated tests:** {row['automated_tests']}")
    if row.get("linked"):
        c1.write(f"**Linked:** {row['linked']}")
    if row.get("notes"):
        c2.write(f"**Notes:** {row['notes']}")

    with st.expander("Update assessment (session)", expanded=False):
        new_cur = st.select_slider(
            "Current maturity",
            options=list(range(6)),
            value=int(row["current"]),
            format_func=lambda x: f"{x} — {MATURITY_LABELS[x]}",
            key=f"cur_{wk}",
        )
        new_tgt = st.select_slider(
            "Target maturity",
            options=list(range(1, 6)),
            value=int(row["target"]),
            format_func=lambda x: f"{x} — {MATURITY_LABELS[x]}",
            key=f"tgt_{wk}",
        )
        note = st.text_input("Assessment note", value=row.get("notes") or "", key=f"note_{wk}")
        if st.button("Save subcategory", key=f"save_{wk}"):
            _patch_subcat(sid, current=new_cur, target=new_tgt, notes=note)
            st.rerun()


def main() -> None:
    portfolio_skin.page_header(
        title="NIST CSF 2.0 Maturity & Readiness",
        lede="Framework posture workbench — subcategory maturity, implementation tier, evidence tests, gap queue, and board narrative. Vanta/Drata-style readiness view; synthetic portfolio data.",
        kicker="NIST CSF 2.0",
    )

    seed = demo_kit.seed_controls()
    subcats, gaps, history, tier, narrative, tests = _sync(seed)
    enriched = _enrich_subcats(subcats)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Profile")
    profile_name = st.sidebar.text_input("Organization", "Acme Corp (sample)")
    assess_period = st.sidebar.selectbox("Assessment period", ["FY26 Q3", "FY26 Q4 (current)", "FY27 Q1 target"])
    view_mode = st.sidebar.radio(
        "Readiness lens",
        ["Subcategory at target", "Weighted by gap size"],
        help="Drata-style toggle: strict at-target vs gap-weighted readiness.",
    )
    weighted = view_mode == "Weighted by gap size"
    st.sidebar.caption("Sample / mock assessment — session edits are local.")

    fn_ready = _function_readiness(enriched)
    overall = _overall_readiness(enriched, weighted=weighted)
    in_scope = int(enriched["in_scope"].sum())
    at_target = int(enriched["at_target"].sum())
    open_gaps = int(gaps[gaps["status"].isin(["Open", "In progress", "Blocked"])].shape[0])
    failing_tests = int((tests["status"] == "Failing").sum())
    evidence_risk = int(enriched["evidence_risk"].sum())

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Overall readiness", f"{overall}%", delta=f"{at_target}/{in_scope} at target · {view_mode.split(' ')[0].lower()}")
    k2.metric("Implementation tier", tier["overall_label"].replace("Tier ", "T"), delta=f"Target {tier['target_label'].split(' —')[0]}")
    k3.metric("Open gaps", open_gaps)
    k4.metric("Failing tests", failing_tests)
    k5.metric("Evidence risk", evidence_risk, help="Stale or missing evidence on in-scope subcategories")
    k6.metric("Subcategories", in_scope)

    if overall < 60:
        st.error("Readiness below 60% — board narrative should lead with gaps, not green averages.")
    elif open_gaps >= 6:
        st.warning(f"{open_gaps} open CSF gaps — prioritize GAP-CSF-001/006 before claiming Tier 3.")

    work, controls, gaps_tab, profile_tab, tests_tab, board_tab, export_tab = st.tabs(
        [
            "Workbench",
            "Subcategories",
            "Gap register",
            "Profiles & trends",
            "Evidence & tests",
            "Board brief",
            "Export",
        ]
    )

    fn_filter = st.sidebar.multiselect(
        "Functions",
        [f[0] for f in FUNCTIONS],
        default=[f[0] for f in FUNCTIONS],
        key="csf_fn_filter",
    )
    gap_only = st.sidebar.checkbox("Below target only", value=False, key="csf_gap_only")

    view = enriched[enriched["function"].isin(fn_filter)]
    if gap_only:
        view = view[~view["at_target"]]

    with work:
        st.subheader("CSF posture workbench")

        st.markdown("**Executive narrative**")
        for _, n in narrative.iterrows():
            st.write(f"**{n['lane']}:** {n['text']}")

        st.markdown("---")
        c1, c2 = st.columns([1.1, 1])
        with c1:
            fig = px.bar(
                fn_ready,
                x="function",
                y="readiness_pct",
                color="function",
                color_discrete_map={f[0]: f[3] for f in FUNCTIONS},
                text="readiness_pct",
                title="Function readiness (% subcategories at target)",
            )
            fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
            fig.update_layout(showlegend=False, height=360, yaxis_range=[0, 105])
            st.plotly_chart(fig, use_container_width=True, key="plotly_fn_ready_work")
        with c2:
            _profile_radar(enriched, key="plotly_radar_work")

        st.markdown("---")
        _heatmap(enriched, key="plotly_heat_work")

        st.markdown(f"**Featured subcategories ({len(FEATURED)})** — incident-shaped gaps")
        pref = ["GV.RR-02", "ID.AM-05", "PR.AA-05", "DE.CM-03", "RS.MA-02", "RC.RP-03"]
        feat = view[view["subcat_id"].isin(FEATURED)].copy()
        feat["_o"] = feat["subcat_id"].map(lambda x: pref.index(x) if x in pref else 99)
        for _, row in feat.sort_values("_o").iterrows():
            st.markdown("---")
            _subcat_detail(row, widget_key="feat")

        st.markdown("---")
        st.markdown("**Gap queue (priority)**")
        hot = gaps[gaps["status"] != "Closed"].sort_values(
            by="priority",
            key=lambda s: s.map({"Critical": 0, "High": 1, "Medium": 2, "Low": 3}),
        )
        for _, g in hot.iterrows():
            flag = " · BLOCKED" if g["status"] == "Blocked" else ""
            with st.expander(f"{g['gap_id']} · {g['title']} · {g['priority']}{flag}"):
                st.write(f"**Subcategory:** {g['subcat_id']} · **Owner:** {g['owner']} · **Due:** {_fmt(g['due'])}")
                st.write(f"**Remediation:** {g['remediation']}")
                st.write(f"**Linked:** {g['linked']}")

    with controls:
        st.subheader("Subcategory register")
        st.caption(
            "CMMI-style 0–5 maturity per NIST CSF 2.0 subcategory. "
            "Readiness = at or above target maturity (Drata control-ready analogue)."
        )

        display = view[
            [
                "subcat_id",
                "function",
                "category",
                "title",
                "current",
                "target",
                "gap_pts",
                "owner",
                "evidence_status",
                "test_status",
                "last_assessed",
            ]
        ].copy()
        display["last_assessed"] = display["last_assessed"].map(_fmt)
        st.dataframe(display, use_container_width=True, hide_index=True)

        pick = st.selectbox("Drill into subcategory", view["subcat_id"].tolist(), key="ctrl_pick")
        row = view[view["subcat_id"] == pick].iloc[0]
        _subcat_detail(row, widget_key="ctrl")

    with gaps_tab:
        st.subheader("Gap register")
        g1, g2 = st.columns(2)
        with g1:
            by_pri = gaps.groupby("priority").size().reset_index(name="count")
            fig = px.bar(by_pri, x="priority", y="count", color="priority", title="Gaps by priority")
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True, key="plotly_gap_pri")
        with g2:
            by_fn = (
                enriched[~enriched["at_target"]]
                .groupby("function")
                .size()
                .reset_index(name="below_target")
            )
            fig2 = px.bar(by_fn, x="function", y="below_target", title="Subcategories below target")
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True, key="plotly_gap_fn")

        st.dataframe(
            gaps.assign(due=gaps["due"].map(_fmt)),
            use_container_width=True,
            hide_index=True,
        )

    with profile_tab:
        st.subheader("Profiles & trend")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Implementation tier (organizational)**")
            st.metric("Current tier", tier["overall_label"])
            st.metric("Target tier", tier["target_label"])
            st.write(tier["narrative"])
            st.caption(f"As of {_fmt(tier['as_of'])} · {tier['assessor']}")
            dim = pd.DataFrame(tier["dimensions"])
            st.dataframe(dim, use_container_width=True, hide_index=True)
        with c2:
            _profile_radar(enriched, key="plotly_radar_profile")

        st.markdown("**Quarterly readiness trend (function)**")
        fig = px.line(
            history,
            x="period",
            y="readiness_pct",
            color="function",
            markers=True,
            title="Function readiness % over time (simulated assessments)",
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="plotly_hist")

        st.markdown("**Maturity level guide (CMMI-style)**")
        guide = pd.DataFrame([{"level": k, "label": v} for k, v in MATURITY_LABELS.items()])
        st.dataframe(guide, use_container_width=True, hide_index=True)

    with tests_tab:
        st.subheader("Evidence & automated tests")
        st.caption("Continuous monitoring analogue — passing/failing tests drive readiness, not self-attestation alone.")

        t1, t2, t3 = st.columns(3)
        t1.metric("Passing", int((tests["status"] == "Passing").sum()))
        t2.metric("Failing", failing_tests)
        t3.metric("Not monitored", int((tests["status"] == "Not monitored").sum()))

        show = tests.copy()
        show["last_run"] = show["last_run"].map(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

        st.markdown("**Evidence status by function**")
        ev = (
            enriched.groupby(["function", "evidence_status"])
            .size()
            .reset_index(name="count")
        )
        fig = px.bar(ev, x="function", y="count", color="evidence_status", barmode="stack", title="Evidence freshness")
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True, key="plotly_evidence")

    with board_tab:
        st.subheader("Board / executive brief")
        st.markdown(f"**Organization:** {profile_name} · **Period:** {assess_period}")

        st.markdown("#### Headline")
        st.write(
            f"NIST CSF 2.0 readiness is **{overall}%** ({at_target} of {in_scope} in-scope subcategories at target maturity). "
            f"Organizational implementation tier: **{tier['overall_label']}** (target {tier['target_label']}). "
            f"{open_gaps} remediation gaps open; {failing_tests} automated tests failing."
        )

        st.markdown("#### Function summary")
        for _, r in fn_ready.iterrows():
            st.write(
                f"- **{r['function']}:** {r['readiness_pct']:.0f}% at target · "
                f"avg maturity {r['avg_current']:.1f} vs target {r['avg_target']:.1f} · {int(r['gaps'])} gaps"
            )

        st.markdown("#### Top risks (linked to portfolio)")
        for _, g in gaps[gaps["priority"].isin(["Critical", "High"])].head(5).iterrows():
            st.write(f"- **{g['gap_id']}** ({g['priority']}): {g['title']} — {g['linked']}")

        st.markdown("#### Ask")
        st.write(
            "Fund crown-jewel reconciliation and PayrollCo backup attestation (10 days), "
            "approve RACI update for phishing reporting, and extend monitoring to operations/colocation shifts."
        )

        with st.expander("Tier dimension detail"):
            st.dataframe(pd.DataFrame(tier["dimensions"]), use_container_width=True, hide_index=True)

    with export_tab:
        st.subheader("Export")
        pack = enriched.assign(last_assessed=enriched["last_assessed"].map(_fmt))
        demo_kit.csv_download(pack, "csf_subcategory_register.csv", label="Download subcategory register")
        demo_kit.csv_download(gaps.assign(due=gaps["due"].map(_fmt)), "csf_gap_register.csv", label="Download gap register")
        demo_kit.csv_download(tests.assign(last_run=tests["last_run"].map(_fmt)), "csf_evidence_tests.csv", label="Download evidence tests")

        summary = pd.DataFrame(
            [
                {"metric": "overall_readiness_pct", "value": overall},
                {"metric": "implementation_tier", "value": tier["overall_tier"]},
                {"metric": "target_tier", "value": tier["target_tier"]},
                {"metric": "subcategories_in_scope", "value": in_scope},
                {"metric": "at_target", "value": at_target},
                {"metric": "open_gaps", "value": open_gaps},
                {"metric": "organization", "value": profile_name},
                {"metric": "period", "value": assess_period},
            ]
        )
        demo_kit.csv_download(summary, "csf_executive_summary.csv", label="Download executive summary")


if __name__ == "__main__":
    main()
