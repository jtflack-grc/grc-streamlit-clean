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
_SYNC_KEY = "_csf_seed_v2"
INDUSTRY_BENCHMARK = {
    "Technology": {"Govern": 2.8, "Identify": 3.0, "Protect": 3.2, "Detect": 2.7, "Respond": 2.9, "Recover": 2.6},
    "Financial Services": {"Govern": 3.2, "Identify": 3.1, "Protect": 3.4, "Detect": 3.0, "Respond": 3.1, "Recover": 2.9},
    "Healthcare": {"Govern": 2.6, "Identify": 2.8, "Protect": 3.0, "Detect": 2.5, "Respond": 2.7, "Recover": 2.5},
    "Manufacturing": {"Govern": 2.4, "Identify": 2.6, "Protect": 2.8, "Detect": 2.3, "Respond": 2.5, "Recover": 2.4},
    "Government": {"Govern": 2.9, "Identify": 2.9, "Protect": 3.1, "Detect": 2.6, "Respond": 2.8, "Recover": 2.7},
    "Other": {"Govern": 2.7, "Identify": 2.8, "Protect": 3.0, "Detect": 2.6, "Respond": 2.7, "Recover": 2.6},
}


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
            {"test_id": "T-CSF-001", "subcat_id": "PR.AA-03", "name": "MFA coverage — workforce", "status": "Passing", "last_run": today - timedelta(days=1), "source": "IdP integration", "frequency": "Daily"},
            {"test_id": "T-CSF-002", "subcat_id": "PR.AA-05", "name": "Privileged access review ≤90d", "status": "Failing", "last_run": today - timedelta(days=2), "source": "IAM / GRC", "frequency": "Weekly"},
            {"test_id": "T-CSF-003", "subcat_id": "ID.AM-05", "name": "Crown-jewel CMDB match", "status": "Failing", "last_run": today - timedelta(days=3), "source": "CAASM", "frequency": "Daily"},
            {"test_id": "T-CSF-004", "subcat_id": "DE.CM-01", "name": "Network sensor coverage", "status": "Passing", "last_run": today - timedelta(days=1), "source": "SIEM", "frequency": "Continuous"},
            {"test_id": "T-CSF-005", "subcat_id": "DE.CM-03", "name": "UEBA — ops / colo users", "status": "Not monitored", "last_run": None, "source": "UEBA", "frequency": "—"},
            {"test_id": "T-CSF-006", "subcat_id": "RC.RP-03", "name": "Backup restore test evidence", "status": "Failing", "last_run": today - timedelta(days=7), "source": "BCP / vendor portal", "frequency": "Quarterly"},
            {"test_id": "T-CSF-007", "subcat_id": "GV.PO-01", "name": "Policy acknowledgment current", "status": "Passing", "last_run": today - timedelta(days=4), "source": "GRC", "frequency": "Monthly"},
            {"test_id": "T-CSF-008", "subcat_id": "RS.MA-02", "name": "IR triage SLA ≤1h Sev2", "status": "Failing", "last_run": today - timedelta(days=5), "source": "IR ticketing", "frequency": "Daily"},
            {"test_id": "T-CSF-009", "subcat_id": "GV.RR-02", "name": "RACI published for incident reporting", "status": "Failing", "last_run": today - timedelta(days=6), "source": "GRC / Confluence", "frequency": "Quarterly"},
            {"test_id": "T-CSF-010", "subcat_id": "PR.PS-01", "name": "Jump host config drift detection", "status": "Failing", "last_run": today - timedelta(days=2), "source": "Config mgmt", "frequency": "Daily"},
            {"test_id": "T-CSF-011", "subcat_id": "ID.RA-01", "name": "Critical vuln SLA compliance", "status": "Passing", "last_run": today - timedelta(days=1), "source": "Vuln platform", "frequency": "Daily"},
            {"test_id": "T-CSF-012", "subcat_id": "GV.SC-04", "name": "Tier-1 supplier inventory current", "status": "Manual only", "last_run": today - timedelta(days=20), "source": "TPRM", "frequency": "Monthly"},
        ]
    )

    crosswalk_map = {
        "GV.RR-02": ("A.5.2", "CC1.3", "12.1"),
        "GV.PO-01": ("A.5.1", "CC1.1", "12.1"),
        "GV.SC-04": ("A.5.19", "CC9.2", "12.8"),
        "ID.AM-05": ("A.5.9", "CC6.1", "2.4"),
        "ID.RA-01": ("A.8.8", "CC7.1", "6.2"),
        "ID.RA-07": ("A.5.29", "CC3.2", "—"),
        "PR.AA-03": ("A.5.17", "CC6.1", "8.3"),
        "PR.AA-05": ("A.5.15", "CC6.3", "7.1"),
        "PR.AT-01": ("A.6.3", "CC1.4", "12.6"),
        "PR.DS-01": ("A.8.24", "CC6.7", "3.4"),
        "PR.PS-01": ("A.8.9", "CC8.1", "2.2"),
        "DE.CM-01": ("A.8.16", "CC7.2", "10.6"),
        "DE.CM-03": ("A.8.16", "CC7.2", "10.2"),
        "RS.MA-02": ("A.5.24", "CC7.3", "12.10"),
        "RC.RP-03": ("A.8.13", "CC7.5", "12.10"),
    }
    crosswalk = []
    for row in subcats:
        sid = row["subcat_id"]
        iso, soc, pci = crosswalk_map.get(sid, ("—", "—", "—"))
        reuse = "High" if iso != "—" and soc != "—" else ("Medium" if iso != "—" or soc != "—" else "Low")
        crosswalk.append(
            {
                "subcat_id": sid,
                "function": row["function"],
                "title": row["title"][:60],
                "iso_27001": iso,
                "soc2_tsc": soc,
                "pci_dss": pci,
                "reuse_potential": reuse,
                "evidence_shared": int(rng.integers(0, 5)) if reuse != "Low" else 0,
            }
        )
    crosswalk_df = pd.DataFrame(crosswalk)

    evidence_register = []
    for i, row in enumerate(subcats):
        if row["evidence_count"] <= 0:
            continue
        for j in range(min(row["evidence_count"], 3)):
            evidence_register.append(
                {
                    "evidence_id": f"EVD-CSF-{i+1:03d}-{j+1}",
                    "subcat_id": row["subcat_id"],
                    "name": f"{row['subcat_id']} — artifact {j+1}",
                    "type": rng.choice(["Policy", "Screenshot", "Log export", "Attestation", "Ticket"]),
                    "status": row["evidence_status"] if j == 0 else rng.choice(EVIDENCE_STATUS),
                    "collected": today - timedelta(days=int(rng.integers(1, 120))),
                    "owner": row["owner"],
                }
            )
    evidence_df = pd.DataFrame(evidence_register)

    # Prior assessment period (Q3) for delta badges
    prior_scores = {}
    for row in subcats:
        sid = row["subcat_id"]
        prior_scores[sid] = max(0, min(5, row["current"] + int(rng.choice([-1, 0, 0, 1]))))

    prior_df = pd.DataFrame([{"subcat_id": k, "prior_current": v} for k, v in prior_scores.items()])

    return sub_df, gaps_df, hist_df, tier, narrative, evidence_tests, crosswalk_df, evidence_df, prior_df


def _enrich_subcats(df: pd.DataFrame, prior: pd.DataFrame | None = None) -> pd.DataFrame:
    out = df.copy()
    out["at_target"] = out["current"] >= out["target"]
    out["readiness_pct"] = (out["current"] / out["target"].clip(lower=1) * 100).clip(0, 100)
    out["failing_test"] = out["test_status"] == "Failing"
    out["evidence_risk"] = out["evidence_status"].isin(["Missing", "Stale"])
    if prior is not None and not prior.empty:
        out = out.merge(prior, on="subcat_id", how="left")
        out["prior_current"] = out["prior_current"].fillna(out["current"])
        out["delta_q"] = out["current"] - out["prior_current"]
    else:
        out["prior_current"] = out["current"]
        out["delta_q"] = 0
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
        s, g, h, t, n, e, cw, ev, pr = _sample(seed)
        st.session_state.csf_subcats = s
        st.session_state.csf_gaps = g
        st.session_state.csf_history = h
        st.session_state.csf_tier = t
        st.session_state.csf_narrative = n
        st.session_state.csf_tests = e
        st.session_state.csf_crosswalk = cw
        st.session_state.csf_evidence = ev
        st.session_state.csf_prior = pr
        st.session_state[_SYNC_KEY] = seed
    return (
        st.session_state.csf_subcats,
        st.session_state.csf_gaps,
        st.session_state.csf_history,
        st.session_state.csf_tier,
        st.session_state.csf_narrative,
        st.session_state.csf_tests,
        st.session_state.csf_crosswalk,
        st.session_state.csf_evidence,
        st.session_state.csf_prior,
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


def _sort_subcats(df: pd.DataFrame) -> pd.DataFrame:
    fn_ord = {f[0]: i for i, f in enumerate(FUNCTIONS)}
    out = df.copy()
    out["_fo"] = out["function"].map(fn_ord)
    return out.sort_values(["_fo", "category", "subcat_id"]).drop(columns="_fo")


def _heatmap_function_summary(subcats: pd.DataFrame, *, key: str):
    """Function × metric matrix — every cell populated (no cross-function category NaNs)."""
    fr = _function_readiness(subcats)
    fn_order = [f[0] for f in FUNCTIONS]
    fr = fr.set_index("function").reindex(fn_order)
    metrics = [
        ("Avg current", fr["avg_current"].tolist(), 0, 5),
        ("Avg target", fr["avg_target"].tolist(), 0, 5),
        ("Readiness %", fr["readiness_pct"].tolist(), 0, 100),
        ("Below target", fr["gaps"].tolist(), 0, max(1, fr["gaps"].max())),
    ]
    y_labels = [m[0] for m in metrics]
    z = np.array([m[1] for m in metrics], dtype=float)
    text = np.array(
        [
            [f"{v:.1f}" if row_i < 2 else (f"{v:.0f}%" if row_i == 2 else f"{int(v)}") for v in row]
            for row_i, row in enumerate(z)
        ]
    )
    # Normalize each row to 0-1 for shared colorscale display
    z_norm = np.zeros_like(z)
    for i, (_, _, lo, hi) in enumerate(metrics):
        span = max(hi - lo, 0.001)
        z_norm[i] = (z[i] - lo) / span

    fig = go.Figure(
        data=go.Heatmap(
            z=z_norm,
            x=fn_order,
            y=y_labels,
            text=text,
            texttemplate="%{text}",
            hovertemplate="%{y} · %{x}<br>Value: %{text}<extra></extra>",
            colorscale=[
                [0, "#7f1d1d"],
                [0.35, "#d97706"],
                [0.65, "#ca8a04"],
                [1, "#059669"],
            ],
            zmin=0,
            zmax=1,
            showscale=False,
        )
    )
    fig.update_layout(
        title="Function posture summary (all cells populated)",
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


def _heatmap_subcategory_grid(subcats: pd.DataFrame, *, key: str):
    """Subcategory × [Current, Target, Gap] — dense grid, no NaNs."""
    df = _sort_subcats(subcats)
    z = np.column_stack([df["current"].values, df["target"].values, df["gap_pts"].values])
    text = np.where(z == z, np.round(z, 0).astype(int).astype(str), "")
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=["Current", "Target", "Gap pts"],
            y=df["subcat_id"].tolist(),
            text=text,
            texttemplate="%{text}",
            hovertemplate="%{y}<br>%{x}: %{z}<extra></extra>",
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
        )
    )
    fig.update_layout(
        title="Subcategory maturity grid (every row = one CSF subcategory)",
        height=max(480, 14 * len(df)),
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(tickfont=dict(size=9)),
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


def _treemap_csf(subcats: pd.DataFrame, *, key: str, color_mode: str = "current"):
    df = subcats.copy()
    df["size"] = df["gap_pts"].clip(lower=1) + 1
    color_col = "readiness_pct" if color_mode == "readiness" else "current"
    fig = px.treemap(
        df,
        path=["function", "category", "subcat_id"],
        values="size",
        color=color_col,
        color_continuous_scale=[
            [0, "#7f1d1d"],
            [0.35, "#d97706"],
            [0.65, "#ca8a04"],
            [1, "#059669"],
        ],
        range_color=[0, 5] if color_col == "current" else [0, 100],
        title=f"CSF hierarchy treemap (color = {color_col})",
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True, key=key)


def _sunburst_csf(subcats: pd.DataFrame, *, key: str):
    df = subcats.copy()
    fig = px.sunburst(
        df,
        path=["function", "category", "subcat_id"],
        values="target",
        color="current",
        color_continuous_scale="RdYlGn",
        range_color=[0, 5],
        title="CSF sunburst — arc size = target maturity, color = current",
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True, key=key)


def _sankey_gaps(gaps: pd.DataFrame, subcats: pd.DataFrame, *, key: str):
    merged = gaps.merge(subcats[["subcat_id", "function"]], on="subcat_id", how="left")
    labels = list(dict.fromkeys(
        merged["function"].tolist() + merged["priority"].tolist() + merged["owner"].tolist()
    ))
    idx = {l: i for i, l in enumerate(labels)}
    sources, targets, values = [], [], []
    for _, row in merged.iterrows():
        sources.append(idx[row["function"]])
        targets.append(idx[row["priority"]])
        values.append(1)
        sources.append(idx[row["priority"]])
        targets.append(idx[row["owner"]])
        values.append(1)
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(label=labels, pad=12, thickness=14),
                link=dict(source=sources, target=targets, value=values),
            )
        ]
    )
    fig.update_layout(title="Gap flow: function → priority → owner", height=400, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True, key=key)


def _gap_timeline(gaps: pd.DataFrame, *, key: str):
    open_g = gaps[gaps["status"] != "Closed"].copy()
    if open_g.empty:
        st.info("No open gaps to plot.")
        return
    today = _today()
    open_g["days_to_due"] = (open_g["due"] - today).dt.days
    open_g = open_g.sort_values("days_to_due")
    colors = {"Critical": "#ef4444", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#6b7280"}
    fig = px.bar(
        open_g,
        x="days_to_due",
        y="gap_id",
        color="priority",
        color_discrete_map=colors,
        orientation="h",
        title="Remediation roadmap — days until due (negative = overdue)",
        hover_data=["title", "owner", "status"],
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#38e881", annotation_text="Today")
    fig.update_layout(height=max(300, 36 * len(open_g)), margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True, key=key)


def _function_pillars(fn_ready: pd.DataFrame):
    cols = st.columns(6)
    for col, (_, row) in zip(cols, fn_ready.iterrows()):
        with col:
            st.markdown(f"**{row['function']}**")
            st.progress(min(1.0, row["readiness_pct"] / 100))
            st.caption(f"{row['readiness_pct']:.0f}% ready · {int(row['gaps'])} gaps")
            st.caption(f"Avg {row['avg_current']:.1f} → {row['avg_target']:.1f}")


def _profile_radar(subcats: pd.DataFrame, *, key: str, industry: str = "Technology"):
    fr = _function_readiness(subcats)
    bench = INDUSTRY_BENCHMARK.get(industry, INDUSTRY_BENCHMARK["Technology"])
    bench_vals = [bench.get(fn, 2.7) for fn in fr["function"]]
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
    fig.add_trace(
        go.Scatterpolar(
            r=bench_vals,
            theta=fr["function"].tolist(),
            fill="toself",
            name=f"{industry} peer (demo)",
            line_color="#f59e0b",
            opacity=0.2,
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        title="Current vs target vs industry peer",
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
        lede="Framework posture workbench — subcategory maturity, implementation tier, evidence tests, cross-framework reuse, gap queue, and board narrative. Vanta/Drata-style readiness view; synthetic portfolio data.",
        kicker="NIST CSF 2.0",
    )

    seed = demo_kit.seed_controls()
    subcats, gaps, history, tier, narrative, tests, crosswalk, evidence, prior = _sync(seed)
    enriched = _enrich_subcats(subcats, prior)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Profile")
    profile_name = st.sidebar.text_input("Organization", "Acme Corp (sample)")
    assess_period = st.sidebar.selectbox("Assessment period", ["FY26 Q3", "FY26 Q4 (current)", "FY27 Q1 target"])
    industry = st.sidebar.selectbox(
        "Industry peer benchmark",
        list(INDUSTRY_BENCHMARK.keys()),
        index=0,
    )
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
    improved_q = int((enriched["delta_q"] > 0).sum())
    regressed_q = int((enriched["delta_q"] < 0).sum())

    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
    k1.metric("Overall readiness", f"{overall}%", delta=f"{at_target}/{in_scope} at target")
    k2.metric("Implementation tier", tier["overall_label"].replace("Tier ", "T"), delta=f"Target {tier['target_label'].split(' —')[0]}")
    k3.metric("Open gaps", open_gaps)
    k4.metric("Failing tests", failing_tests)
    k5.metric("Evidence risk", evidence_risk)
    k6.metric("QoQ improved", improved_q, delta=f"{regressed_q} regressed", delta_color="inverse")
    k7.metric("Subcategories", in_scope)

    if overall < 60:
        st.error("Readiness below 60% — board narrative should lead with gaps, not green averages.")
    elif open_gaps >= 6:
        st.warning(f"{open_gaps} open CSF gaps — prioritize GAP-CSF-001/006 before claiming Tier 3.")

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

    work, fmap, controls, workshop, gaps_tab, cross_tab, profile_tab, tests_tab, board_tab, export_tab = st.tabs(
        [
            "Workbench",
            "Framework map",
            "Subcategories",
            "Workshop",
            "Gap register",
            "Crosswalk",
            "Profiles & trends",
            "Evidence & tests",
            "Board brief",
            "Export",
        ]
    )

    with work:
        st.subheader("CSF posture workbench")
        _function_pillars(fn_ready)

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
            _profile_radar(enriched, key="plotly_radar_work", industry=industry)

        st.markdown("---")
        h1, h2 = st.columns(2)
        with h1:
            _heatmap_function_summary(enriched, key="plotly_heat_fn_summary")
        with h2:
            _sankey_gaps(gaps, enriched, key="plotly_sankey_gaps")

        st.markdown("---")
        _heatmap_subcategory_grid(enriched, key="plotly_heat_subcat_grid")

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

    with fmap:
        st.subheader("Interactive framework map")
        viz = st.segmented_control(
            "Visualization",
            ["Treemap", "Sunburst"],
            default="Treemap",
            key="csf_map_viz",
        )
        if viz == "Treemap":
            color_mode = st.radio("Color by", ["current", "readiness"], horizontal=True, key="treemap_color")
            _treemap_csf(enriched, key="plotly_treemap", color_mode=color_mode)
        else:
            _sunburst_csf(enriched, key="plotly_sunburst")

        st.markdown("**Function reference**")
        for name, code, desc, color in FUNCTIONS:
            with st.expander(f"{code} · {name}"):
                st.write(desc)
                cats = enriched[enriched["function"] == name]["category"].unique()
                st.write(f"Categories in scope: {', '.join(sorted(cats))}")

    with controls:
        st.subheader("Subcategory register")
        st.caption(
            "CMMI-style 0–5 maturity per NIST CSF 2.0 subcategory. "
            "Readiness = at or above target maturity (Drata control-ready analogue)."
        )

        search = st.text_input("Search subcategories", placeholder="e.g. AM-05, access, backup…", key="csf_search")
        display = view[
            [
                "subcat_id",
                "function",
                "category",
                "title",
                "current",
                "target",
                "gap_pts",
                "delta_q",
                "owner",
                "evidence_status",
                "test_status",
                "last_assessed",
            ]
        ].copy()
        if search.strip():
            q = search.strip().lower()
            mask = display.apply(lambda r: q in " ".join(str(v).lower() for v in r), axis=1)
            display = display[mask]
        display["last_assessed"] = display["last_assessed"].map(_fmt)
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "current": st.column_config.ProgressColumn("Current", min_value=0, max_value=5),
                "target": st.column_config.ProgressColumn("Target", min_value=0, max_value=5),
                "delta_q": st.column_config.NumberColumn("QoQ Δ", format="%+d"),
            },
        )

        pick = st.selectbox("Drill into subcategory", view["subcat_id"].tolist(), key="ctrl_pick")
        row = view[view["subcat_id"] == pick].iloc[0]
        _subcat_detail(row, widget_key="ctrl")

        ev_for = evidence[evidence["subcat_id"] == pick]
        if not ev_for.empty:
            st.markdown("**Evidence artifacts**")
            st.dataframe(ev_for.assign(collected=ev_for["collected"].map(_fmt)), use_container_width=True, hide_index=True)

    with workshop:
        st.subheader("Assessment workshop")
        st.caption("Bulk-edit maturity scores for the current session — like a facilitated CSF assessment workshop.")

        edit_view = view[
            ["subcat_id", "function", "title", "current", "target", "owner", "notes"]
        ].copy()
        edited = st.data_editor(
            edit_view,
            num_rows="fixed",
            use_container_width=True,
            hide_index=True,
            column_config={
                "current": st.column_config.SelectboxColumn("Current", options=list(range(6)), required=True),
                "target": st.column_config.SelectboxColumn("Target", options=list(range(1, 6)), required=True),
                "notes": st.column_config.TextColumn("Notes", width="large"),
            },
            key="csf_workshop_editor",
        )
        if st.button("Apply workshop changes", type="primary", key="csf_apply_workshop"):
            df = st.session_state.csf_subcats.copy()
            for _, row in edited.iterrows():
                loc = df.index[df["subcat_id"] == row["subcat_id"]]
                if len(loc) == 0:
                    continue
                df.at[loc[0], "current"] = int(row["current"])
                df.at[loc[0], "target"] = int(row["target"])
                df.at[loc[0], "notes"] = row["notes"]
                df.at[loc[0], "current_label"] = MATURITY_LABELS[int(row["current"])]
                df.at[loc[0], "target_label"] = MATURITY_LABELS[int(row["target"])]
                df.at[loc[0], "gap"] = int(row["current"]) < int(row["target"])
                df.at[loc[0], "gap_pts"] = max(0, int(row["target"]) - int(row["current"]))
            _save_subcats(df)
            st.toast("Workshop scores applied to session", icon="✅")
            st.rerun()

        with st.expander("Maturity rubric (CMMI 0–5)"):
            for lvl, label in MATURITY_LABELS.items():
                st.write(f"**{lvl} — {label}**")

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

        _gap_timeline(gaps, key="plotly_gap_timeline")

        st.dataframe(
            gaps.assign(due=gaps["due"].map(_fmt)),
            use_container_width=True,
            hide_index=True,
        )

    with cross_tab:
        st.subheader("Cross-framework crosswalk")
        st.caption("Reuse evidence across CSF, ISO 27001, SOC 2, and PCI — the Vanta/Drata efficiency play.")

        cw_view = crosswalk[crosswalk["subcat_id"].isin(view["subcat_id"])]
        c1, c2, c3 = st.columns(3)
        c1.metric("High reuse mappings", int((cw_view["reuse_potential"] == "High").sum()))
        c2.metric("Shared evidence (demo)", int(cw_view["evidence_shared"].sum()))
        c3.metric("Mapped subcategories", len(cw_view))

        fig = px.scatter(
            cw_view,
            x="iso_27001",
            y="soc2_tsc",
            size="evidence_shared",
            color="reuse_potential",
            hover_data=["subcat_id", "title"],
            title="ISO 27001 ↔ SOC 2 mapping density (bubble = shared evidence count)",
        )
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True, key="plotly_crosswalk_scatter")

        st.dataframe(cw_view, use_container_width=True, hide_index=True)

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
            _profile_radar(enriched, key="plotly_radar_profile", industry=industry)

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

        st.markdown("**QoQ subcategory deltas**")
        delta_chart = enriched[enriched["delta_q"] != 0].copy()
        if not delta_chart.empty:
            fig_d = px.bar(
                delta_chart.sort_values("delta_q"),
                x="delta_q",
                y="subcat_id",
                color="delta_q",
                color_continuous_scale="RdYlGn",
                orientation="h",
                title="Change vs prior quarter (current maturity)",
            )
            fig_d.update_layout(height=max(280, 14 * len(delta_chart)))
            st.plotly_chart(fig_d, use_container_width=True, key="plotly_delta_q")

        st.markdown("**Maturity level guide (CMMI-style)**")
        guide = pd.DataFrame([{"level": k, "label": v} for k, v in MATURITY_LABELS.items()])
        st.dataframe(guide, use_container_width=True, hide_index=True)

    with tests_tab:
        st.subheader("Evidence & automated tests")
        st.caption("Continuous monitoring analogue — passing/failing tests drive readiness, not self-attestation alone.")

        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Passing", int((tests["status"] == "Passing").sum()))
        t2.metric("Failing", failing_tests)
        t3.metric("Not monitored", int((tests["status"] == "Not monitored").sum()))
        t4.metric("Evidence artifacts", len(evidence))

        show = tests.copy()
        show["last_run"] = show["last_run"].map(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

        st.markdown("**Evidence register**")
        ev_show = evidence.copy()
        ev_show["collected"] = ev_show["collected"].map(_fmt)
        st.dataframe(ev_show, use_container_width=True, hide_index=True)

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
        st.markdown(f"**Organization:** {profile_name} · **Period:** {assess_period} · **Peer:** {industry}")

        st.markdown("#### Headline")
        st.write(
            f"NIST CSF 2.0 readiness is **{overall}%** ({at_target} of {in_scope} in-scope subcategories at target maturity). "
            f"Organizational implementation tier: **{tier['overall_label']}** (target {tier['target_label']}). "
            f"{open_gaps} remediation gaps open; {failing_tests} automated tests failing. "
            f"QoQ: **{improved_q}** subcategories improved, **{regressed_q}** regressed."
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

        with st.expander("Printable summary metrics"):
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Readiness", f"{overall}%")
            b2.metric("Tier gap", f"{tier['target_tier'] - tier['overall_tier']} levels")
            b3.metric("Critical/High gaps", int(gaps[gaps["priority"].isin(["Critical", "High"])].shape[0]))
            b4.metric("Crosswalk high-reuse", int((crosswalk["reuse_potential"] == "High").sum()))

    with export_tab:
        st.subheader("Export")
        pack = enriched.assign(last_assessed=enriched["last_assessed"].map(_fmt))
        demo_kit.csv_download(pack, "csf_subcategory_register.csv", label="Download subcategory register")
        demo_kit.csv_download(gaps.assign(due=gaps["due"].map(_fmt)), "csf_gap_register.csv", label="Download gap register")
        demo_kit.csv_download(tests.assign(last_run=tests["last_run"].map(_fmt)), "csf_evidence_tests.csv", label="Download evidence tests")
        demo_kit.csv_download(crosswalk, "csf_crosswalk.csv", label="Download cross-framework crosswalk")
        demo_kit.csv_download(evidence.assign(collected=evidence["collected"].map(_fmt)), "csf_evidence_register.csv", label="Download evidence register")

        summary = pd.DataFrame(
            [
                {"metric": "overall_readiness_pct", "value": overall},
                {"metric": "implementation_tier", "value": tier["overall_tier"]},
                {"metric": "target_tier", "value": tier["target_tier"]},
                {"metric": "subcategories_in_scope", "value": in_scope},
                {"metric": "at_target", "value": at_target},
                {"metric": "open_gaps", "value": open_gaps},
                {"metric": "qoq_improved", "value": improved_q},
                {"metric": "qoq_regressed", "value": regressed_q},
                {"metric": "organization", "value": profile_name},
                {"metric": "period", "value": assess_period},
                {"metric": "industry_peer", "value": industry},
            ]
        )
        demo_kit.csv_download(summary, "csf_executive_summary.csv", label="Download executive summary")


if __name__ == "__main__":
    main()
