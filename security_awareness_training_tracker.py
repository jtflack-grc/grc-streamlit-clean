#!/usr/bin/env python3
"""Security awareness / human-risk workbench — club teaching toy.

KnowBe4 / Proofpoint-flavored SAT: people risk scores, phishing sims,
smart cohorts, remedial queues, program KPIs — not a completion checklist
for Mike Chen finished a video. Synthetic / educational only.
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
    page_title="Security Awareness Training Tracker · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

DEPTS = [
    "Finance",
    "HR",
    "IT / SecOps",
    "ERP / Ops",
    "Marketing",
    "Legal / Privacy",
    "Executive",
    "Vendor / AMS",
    "Credit Risk",
    "Customer Support",
]
PRIVILEGE = ["Standard", "Elevated", "Privileged", "Executive / VIP"]
RISK_BANDS = ["Critical", "High", "Medium", "Low"]
MODULE_CATS = [
    "Phishing / social engineering",
    "BEC / payment fraud",
    "Data privacy / handling",
    "Privileged access hygiene",
    "Incident reporting",
    "AI / deepfake awareness",
    "Physical / hybrid",
    "Role-specific (finance / admin)",
]
ASSIGN_STATUS = ["Assigned", "In progress", "Completed", "Overdue", "Remedial", "Waived"]
PHISH_OUTCOME = ["Reported", "Ignored", "Clicked", "Entered creds", "Opened attachment"]
COHORT_TYPES = [
    "Repeat clickers",
    "Privileged / admin",
    "Finance / payment authority",
    "New hire <90d",
    "VIP / exec",
    "Vendor admins",
    "High people-risk",
    "Compliant baseline",
]
FEATURED_PEOPLE = {"USR-2026-014", "USR-2026-003", "USR-2026-021", "USR-2026-008"}
FEATURED_PHISH = {"PHISH-2026-003", "PHISH-2026-005"}
_SYNC_KEY = "_sat_seed_v1"


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _sample(seed: int):
    today = _today()
    rng = np.random.default_rng(seed)

    # ── Catalog (modules) ────────────────────────────────────────────
    modules = [
        {
            "module_id": "MOD-2026-001",
            "title": "Phishing fundamentals + report button",
            "category": "Phishing / social engineering",
            "minutes": 18,
            "mandatory": True,
            "audience": "All workforce",
            "frameworks": "SOC 2 · ISO 27001 A.6.3 · NIST awareness",
            "status": "Active",
            "summary": "Baseline annual. Fail a sim → auto-enroll remedial variant.",
        },
        {
            "module_id": "MOD-2026-002",
            "title": "BEC & invoice fraud (finance track)",
            "category": "BEC / payment fraud",
            "minutes": 25,
            "mandatory": True,
            "audience": "Finance · AP · exec assistants",
            "frameworks": "SOC 2 · fraud controls",
            "status": "Active",
            "summary": "Role-based. Tied to payment authority cohort.",
        },
        {
            "module_id": "MOD-2026-003",
            "title": "Privacy & data handling (workforce)",
            "category": "Data privacy / handling",
            "minutes": 22,
            "mandatory": True,
            "audience": "All with PII access",
            "frameworks": "GDPR Art. 39 awareness · ISO 27701 6.3",
            "status": "Active",
            "summary": "Links to privacy program — not a checkbox for Art. 30.",
        },
        {
            "module_id": "MOD-2026-004",
            "title": "Privileged access & social engineering of admins",
            "category": "Privileged access hygiene",
            "minutes": 20,
            "mandatory": True,
            "audience": "Privileged · vendor admins",
            "frameworks": "NIS2 awareness · ISO 27001",
            "status": "Active",
            "summary": "Required for PAM / jump / IBM i / AMS named admins.",
        },
        {
            "module_id": "MOD-2026-005",
            "title": "How to report an incident (IR awareness)",
            "category": "Incident reporting",
            "minutes": 12,
            "mandatory": True,
            "audience": "All",
            "frameworks": "SOC 2 CC7 · IR plan",
            "status": "Active",
            "summary": "Pairs with INC-2026-003 lessons learned.",
        },
        {
            "module_id": "MOD-2026-006",
            "title": "Deepfake / vishing / AI social engineering",
            "category": "AI / deepfake awareness",
            "minutes": 15,
            "mandatory": False,
            "audience": "Finance · exec · HR",
            "frameworks": "Emerging threat",
            "status": "Active",
            "summary": "Campaign push after industry vishing spikes.",
        },
        {
            "module_id": "MOD-2026-007",
            "title": "Remedial: you clicked — now what",
            "category": "Phishing / social engineering",
            "minutes": 10,
            "mandatory": False,
            "audience": "Auto after click / creds",
            "frameworks": "Remedial SAT",
            "status": "Active",
            "summary": "Smart-group remedial. Completion required before next advanced sim.",
        },
        {
            "module_id": "MOD-2026-008",
            "title": "Vendor / AMS security expectations",
            "category": "Role-specific (finance / admin)",
            "minutes": 20,
            "mandatory": True,
            "audience": "Orbit AMS named IDs · TPRM liaisons",
            "frameworks": "TPRM · Art. 28 awareness",
            "status": "Active",
            "summary": "VND-2026-003 cohort — shared-ID culture is the risk.",
        },
    ]

    # ── People (workforce sample — dense enough to score) ────────────
    people_raw = [
        ("USR-2026-001", "A. Rivera", "IT / SecOps", "SecOps Lead", "Privileged", False),
        ("USR-2026-002", "R. Kim", "IT / SecOps", "Platform Eng", "Elevated", False),
        ("USR-2026-003", "T. Okonkwo", "Finance", "AP Manager", "Elevated", True),
        ("USR-2026-004", "M. Hassan", "ERP / Ops", "ERP Finance Owner", "Elevated", False),
        ("USR-2026-005", "J. Park", "HR", "HRIS Steward", "Elevated", False),
        ("USR-2026-006", "C. Hoffman", "Legal / Privacy", "DPO", "Elevated", False),
        ("USR-2026-007", "L. Torres", "Legal / Privacy", "Privacy Ops", "Standard", False),
        ("USR-2026-008", "S. Varga", "Vendor / AMS", "Orbit AMS L2", "Privileged", True),
        ("USR-2026-009", "K. Singh", "Credit Risk", "MRM Steward", "Elevated", False),
        ("USR-2026-010", "N. Brooks", "Executive", "COO EA", "Executive / VIP", False),
        ("USR-2026-011", "P. Nguyen", "Finance", "Treasury Analyst", "Elevated", False),
        ("USR-2026-012", "D. Alvarez", "Customer Support", "CX Lead", "Standard", False),
        ("USR-2026-013", "E. Cho", "Marketing", "Martech", "Standard", False),
        ("USR-2026-014", "B. Whitaker", "Finance", "Controller", "Elevated", True),
        ("USR-2026-015", "H. Patel", "IT / SecOps", "IBM i Ops", "Privileged", False),
        ("USR-2026-016", "Y. Morita", "IT / SecOps", "IAM Eng", "Privileged", False),
        ("USR-2026-017", "F. Gilles", "HR", "Recruiter (new hire)", "Standard", False),
        ("USR-2026-018", "I. Costa", "ERP / Ops", "Warehouse Lead", "Standard", False),
        ("USR-2026-019", "G. Berg", "Executive", "CFO", "Executive / VIP", False),
        ("USR-2026-020", "W. Zhao", "Credit Risk", "Credit Analyst", "Standard", False),
        ("USR-2026-021", "A. Nguyen", "Vendor / AMS", "TPRM Lead", "Elevated", False),
        ("USR-2026-022", "M. Ruiz", "Finance", "AP Clerk", "Standard", True),
        ("USR-2026-023", "J. Keller", "IT / SecOps", "SOC L1", "Elevated", False),
        ("USR-2026-024", "C. Dane", "Customer Support", "Agent", "Standard", False),
    ]

    people = []
    for uid, name, dept, role, priv, payment in people_raw:
        # Synthetic behavioral signals
        clicks_90 = int(rng.integers(0, 4))
        reports_90 = int(rng.integers(0, 8))
        creds_90 = 0
        if uid in {"USR-2026-014", "USR-2026-003", "USR-2026-022"}:
            clicks_90 = 3 if uid == "USR-2026-014" else 2
            creds_90 = 1 if uid == "USR-2026-014" else 0
            reports_90 = 0 if uid == "USR-2026-014" else 1
        if uid == "USR-2026-008":
            clicks_90 = 2
            reports_90 = 0
        if uid in {"USR-2026-001", "USR-2026-006", "USR-2026-016"}:
            clicks_90 = 0
            reports_90 = int(rng.integers(4, 9))
        if uid == "USR-2026-017":
            clicks_90 = 1
            reports_90 = 0

        overdue_mods = 0
        if uid in {"USR-2026-014", "USR-2026-008", "USR-2026-017", "USR-2026-022"}:
            overdue_mods = 2 if uid != "USR-2026-017" else 3
        elif uid in {"USR-2026-003", "USR-2026-013"}:
            overdue_mods = 1

        real_inc = uid in {"USR-2026-014"}  # INC-2026-003 mailbox rule path
        # People risk score 0–100 (higher = worse) — KnowBe4/Proofpoint-ish composite
        score = (
            clicks_90 * 12
            + creds_90 * 25
            + overdue_mods * 8
            + (15 if real_inc else 0)
            + {"Standard": 0, "Elevated": 5, "Privileged": 12, "Executive / VIP": 10}[priv]
            + (8 if payment else 0)
            - min(reports_90 * 3, 18)
        )
        score = int(max(5, min(98, score + int(rng.integers(-3, 4)))))
        if score >= 75:
            band = "Critical"
        elif score >= 55:
            band = "High"
        elif score >= 35:
            band = "Medium"
        else:
            band = "Low"

        people.append(
            {
                "user_id": uid,
                "name": name,
                "dept": dept,
                "role": role,
                "privilege": priv,
                "payment_authority": payment,
                "manager": {
                    "Finance": "G. Berg",
                    "IT / SecOps": "A. Rivera",
                    "Vendor / AMS": "A. Nguyen",
                    "Executive": "Board",
                    "HR": "J. Park",
                    "Legal / Privacy": "C. Hoffman",
                    "ERP / Ops": "M. Hassan",
                    "Marketing": "E. Cho",
                    "Credit Risk": "K. Singh",
                    "Customer Support": "D. Alvarez",
                }.get(dept, "TBD"),
                "hire_date": today - timedelta(days=int(rng.integers(30, 2200)) if uid != "USR-2026-017" else 40),
                "clicks_90d": clicks_90,
                "creds_90d": creds_90,
                "reports_90d": reports_90,
                "overdue_modules": overdue_mods,
                "real_incident_flag": real_inc,
                "people_risk": score,
                "risk_band": band,
                "last_training": today - timedelta(days=int(rng.integers(5, 200))),
                "phish_prone_pct": round(min(95, clicks_90 / max(1, clicks_90 + reports_90 + 2) * 100 + overdue_mods * 5), 1),
                "cohort_tags": "",
                "notes": "",
                "recommended_action": "",
            }
        )

    # Tag cohorts + actions
    for p in people:
        tags = []
        if p["people_risk"] >= 55:
            tags.append("High people-risk")
        if p["clicks_90d"] >= 2:
            tags.append("Repeat clickers")
        if p["privilege"] in {"Privileged", "Executive / VIP"}:
            tags.append("Privileged / admin" if p["privilege"] == "Privileged" else "VIP / exec")
        if p["payment_authority"]:
            tags.append("Finance / payment authority")
        if (today - pd.Timestamp(p["hire_date"])).days < 90:
            tags.append("New hire <90d")
        if p["dept"] == "Vendor / AMS":
            tags.append("Vendor admins")
        if p["risk_band"] == "Low" and p["overdue_modules"] == 0:
            tags.append("Compliant baseline")
        p["cohort_tags"] = " · ".join(tags) if tags else "—"

        if p["risk_band"] == "Critical":
            p["recommended_action"] = "Remedial MOD-2026-007 + manager coaching + next sim easy-mode"
        elif p["overdue_modules"] > 0:
            p["recommended_action"] = "Clear overdue mandatory · escalate manager if >14d"
        elif p["clicks_90d"] >= 2:
            p["recommended_action"] = "Enroll remedial · increase sim frequency"
        elif p["privilege"] == "Privileged" and p["reports_90d"] < 2:
            p["recommended_action"] = "Privileged track MOD-2026-004 refresh"
        else:
            p["recommended_action"] = "Maintain cadence · monitor"

        if p["user_id"] == "USR-2026-014":
            p["notes"] = "Repeat clicker + entered creds on BEC lure. Linked INC-2026-003 mailbox rule. Payment authority — crown human risk."
            p["summary"] = (
                "Controller with payment authority who fails phishing and under-reports. "
                "This is the Proofpoint/KnowBe4 'people risk' poster child — not someone who finished a video."
            )
        elif p["user_id"] == "USR-2026-003":
            p["notes"] = "AP Manager — two clicks in 90d; BEC module overdue. High blast radius for invoice fraud."
            p["summary"] = "Role + behavior mismatch. Smart-group: finance payment authority + repeat clicker."
        elif p["user_id"] == "USR-2026-021":
            p["notes"] = "TPRM Lead — solid reporter; owns Orbit AMS awareness for VND-2026-003."
            p["summary"] = "Positive control owner. Featured as contrast: elevated privilege, low people-risk when reporting is strong."
        elif p["user_id"] == "USR-2026-008":
            p["notes"] = "Orbit AMS L2 — privileged path into PRODBOX; clicks, no reports, MOD-2026-004/008 overdue."
            p["summary"] = "Vendor admin is workforce risk too. Shared-ID culture + sim fails → PAM/awareness dual fix."
        else:
            p["summary"] = f"{p['risk_band']} people-risk · {p['role']} · privilege {p['privilege']}."

    # ── Assignments ──────────────────────────────────────────────────
    assignments = []
    aid = 1
    mandatory = ["MOD-2026-001", "MOD-2026-003", "MOD-2026-005"]
    for p in people:
        due_base = today + timedelta(days=int(rng.integers(-20, 40)))
        for mid in mandatory:
            status = "Completed"
            completed = today - timedelta(days=int(rng.integers(10, 120)))
            due = due_base
            if p["overdue_modules"] and mid in {"MOD-2026-001", "MOD-2026-003"} and p["user_id"] in {
                "USR-2026-014",
                "USR-2026-008",
                "USR-2026-017",
                "USR-2026-022",
                "USR-2026-003",
                "USR-2026-013",
            }:
                # Mark some overdue
                if aid % 2 == 0 or p["user_id"] in {"USR-2026-014", "USR-2026-017", "USR-2026-008"}:
                    status = "Overdue"
                    completed = pd.NaT
                    due = today - timedelta(days=int(rng.integers(5, 25)))
            assignments.append(
                {
                    "assign_id": f"ASN-2026-{aid:03d}",
                    "user_id": p["user_id"],
                    "module_id": mid,
                    "status": status,
                    "due": due,
                    "completed": completed,
                    "score_pct": None if status != "Completed" else int(rng.integers(70, 100)),
                    "source": "Annual mandatory",
                }
            )
            aid += 1
        if p["payment_authority"]:
            st_ = "Overdue" if p["user_id"] in {"USR-2026-014", "USR-2026-003"} else "Completed"
            assignments.append(
                {
                    "assign_id": f"ASN-2026-{aid:03d}",
                    "user_id": p["user_id"],
                    "module_id": "MOD-2026-002",
                    "status": st_,
                    "due": today - timedelta(days=8) if st_ == "Overdue" else today + timedelta(days=20),
                    "completed": pd.NaT if st_ == "Overdue" else today - timedelta(days=40),
                    "score_pct": None if st_ == "Overdue" else 88,
                    "source": "Role — finance track",
                }
            )
            aid += 1
        if p["privilege"] == "Privileged" or p["dept"] == "Vendor / AMS":
            st_ = "Overdue" if p["user_id"] == "USR-2026-008" else ("Completed" if rng.random() > 0.25 else "In progress")
            assignments.append(
                {
                    "assign_id": f"ASN-2026-{aid:03d}",
                    "user_id": p["user_id"],
                    "module_id": "MOD-2026-004",
                    "status": st_,
                    "due": today - timedelta(days=12) if st_ == "Overdue" else today + timedelta(days=15),
                    "completed": pd.NaT if st_ != "Completed" else today - timedelta(days=30),
                    "score_pct": 91 if st_ == "Completed" else None,
                    "source": "Privileged track",
                }
            )
            aid += 1
        if p["dept"] == "Vendor / AMS":
            st_ = "Overdue" if p["user_id"] == "USR-2026-008" else "In progress"
            assignments.append(
                {
                    "assign_id": f"ASN-2026-{aid:03d}",
                    "user_id": p["user_id"],
                    "module_id": "MOD-2026-008",
                    "status": st_,
                    "due": today - timedelta(days=6) if st_ == "Overdue" else today + timedelta(days=10),
                    "completed": pd.NaT,
                    "score_pct": None,
                    "source": "Vendor admin track",
                }
            )
            aid += 1
        if p["clicks_90d"] >= 2 or p["creds_90d"]:
            assignments.append(
                {
                    "assign_id": f"ASN-2026-{aid:03d}",
                    "user_id": p["user_id"],
                    "module_id": "MOD-2026-007",
                    "status": "Remedial" if p["user_id"] != "USR-2026-014" else "Overdue",
                    "due": today + timedelta(days=3) if p["user_id"] != "USR-2026-014" else today - timedelta(days=4),
                    "completed": pd.NaT,
                    "score_pct": None,
                    "source": "Auto — failed phishing sim",
                }
            )
            aid += 1

    # ── Phishing simulations ─────────────────────────────────────────
    phish = [
        {
            "phish_id": "PHISH-2026-001",
            "name": "Q1 baseline — IT helpdesk password reset",
            "template": "Internal IT · MFA reset",
            "difficulty": "Easy",
            "launched": today - timedelta(days=110),
            "closed": today - timedelta(days=100),
            "audience": "All workforce (n≈1,820)",
            "sent": 1820,
            "clicked": 98,
            "creds": 12,
            "reported": 410,
            "ignored": 1300,
            "status": "Closed",
            "owner": "Awareness · L. Torres",
            "so_what": "Baseline phish-prone ~5.4%. Report rate healthy.",
            "decision": "Graduate org to medium difficulty",
            "summary": "Closed baseline. Used for trend — not a celebration of 'training done'.",
        },
        {
            "phish_id": "PHISH-2026-002",
            "name": "Finance spear — vendor bank change",
            "template": "BEC · payment change PDF",
            "difficulty": "Hard",
            "launched": today - timedelta(days=70),
            "closed": today - timedelta(days=60),
            "audience": "Finance / payment authority cohort",
            "sent": 86,
            "clicked": 11,
            "creds": 3,
            "reported": 28,
            "ignored": 44,
            "status": "Closed",
            "owner": "Awareness + Finance control owner",
            "so_what": "12.8% click on payment cohort — unacceptable for AP. Whitaker + Okonkwo in failure set.",
            "decision": "Mandatory MOD-2026-002 + remedial; manager coaching",
            "summary": "Role-targeted sim. This is how SAT becomes a control, not a video library.",
        },
        {
            "phish_id": "PHISH-2026-003",
            "name": "PayrollCo / HR benefits lure (active IR context)",
            "template": "HR · benefits enrollment SSO",
            "difficulty": "Medium",
            "launched": today - timedelta(days=8),
            "closed": pd.NaT,
            "audience": "All + boost to Finance/HR",
            "sent": 1820,
            "clicked": 64,
            "creds": 7,
            "reported": 290,
            "ignored": 1459,
            "status": "Active — results streaming",
            "owner": "Awareness · SecOps",
            "so_what": "Running during PayrollCo INC-2026-009 — users primed for HR/payroll themes. Watch false trust.",
            "decision": "Extend + coach clickers within 48h; do not pause sim",
            "summary": "Featured active campaign. Context-aware lures beat generic 'Spot the Dog' phish kits.",
        },
        {
            "phish_id": "PHISH-2026-004",
            "name": "Privileged — VPN cert / jump maintenance",
            "template": "IT · jump host maintenance",
            "difficulty": "Hard",
            "launched": today - timedelta(days=35),
            "closed": today - timedelta(days=28),
            "audience": "Privileged + vendor admins",
            "sent": 64,
            "clicked": 9,
            "creds": 2,
            "reported": 22,
            "ignored": 31,
            "status": "Closed",
            "owner": "SecOps / Awareness",
            "so_what": "14% click on privileged cohort incl. Orbit AMS L2. Maps to KRI-2026-008 / privileged coverage story.",
            "decision": "MOD-2026-004 overdue enforcement; named-ID push for AMS",
            "summary": "Admin-targeted. Failures here are NIS2/awareness evidence problems.",
        },
        {
            "phish_id": "PHISH-2026-005",
            "name": "Deepfake CFO voice-mail follow-up email",
            "template": "Vishing callback + wire urgency",
            "difficulty": "Hard",
            "launched": today - timedelta(days=18),
            "closed": today - timedelta(days=12),
            "audience": "Finance · exec assistants · VIP",
            "sent": 42,
            "clicked": 6,
            "creds": 1,
            "reported": 19,
            "ignored": 16,
            "status": "Closed — lessons to board brief",
            "owner": "Awareness + CFO EA",
            "so_what": "14% click on VIP/finance. One cred harvest. Board narrative for KRI-2026-010.",
            "decision": "Roll MOD-2026-006; dual-channel verify procedure drill",
            "summary": "Featured. Modern SAT includes deepfake/vishing — not just 'hover the link'.",
        },
        {
            "phish_id": "PHISH-2026-006",
            "name": "New-hire onboarding phish (welcome portal)",
            "template": "HRIS · complete your profile",
            "difficulty": "Easy",
            "launched": today - timedelta(days=25),
            "closed": today - timedelta(days=20),
            "audience": "New hire <90d",
            "sent": 38,
            "clicked": 8,
            "creds": 2,
            "reported": 6,
            "ignored": 22,
            "status": "Closed",
            "owner": "HR + Awareness",
            "so_what": "21% click — new hires are a smart-group for a reason.",
            "decision": "Day-1 training before mailbox; shorter sims weekly ×4",
            "summary": "Onboarding control gap. Gilles in failure set.",
        },
    ]

    # Individual phish events (sample for featured users)
    events = []
    eid = 1
    # Whitaker fails hard on BEC + deepfake
    for ph, outcome in [
        ("PHISH-2026-002", "Entered creds"),
        ("PHISH-2026-003", "Clicked"),
        ("PHISH-2026-005", "Clicked"),
        ("PHISH-2026-001", "Ignored"),
    ]:
        events.append(
            {
                "event_id": f"PE-2026-{eid:03d}",
                "phish_id": ph,
                "user_id": "USR-2026-014",
                "outcome": outcome,
                "ts": today - timedelta(days=int(rng.integers(5, 70))),
                "remedial_assigned": True,
            }
        )
        eid += 1
    for ph, outcome in [
        ("PHISH-2026-002", "Clicked"),
        ("PHISH-2026-003", "Ignored"),
        ("PHISH-2026-005", "Reported"),
    ]:
        events.append(
            {
                "event_id": f"PE-2026-{eid:03d}",
                "phish_id": ph,
                "user_id": "USR-2026-003",
                "outcome": outcome,
                "ts": today - timedelta(days=int(rng.integers(5, 70))),
                "remedial_assigned": outcome in {"Clicked", "Entered creds"},
            }
        )
        eid += 1
    for ph, outcome in [
        ("PHISH-2026-004", "Clicked"),
        ("PHISH-2026-003", "Clicked"),
        ("PHISH-2026-001", "Ignored"),
    ]:
        events.append(
            {
                "event_id": f"PE-2026-{eid:03d}",
                "phish_id": ph,
                "user_id": "USR-2026-008",
                "outcome": outcome,
                "ts": today - timedelta(days=int(rng.integers(5, 70))),
                "remedial_assigned": True,
            }
        )
        eid += 1
    for ph, outcome in [
        ("PHISH-2026-003", "Reported"),
        ("PHISH-2026-004", "Reported"),
        ("PHISH-2026-001", "Reported"),
        ("PHISH-2026-005", "Reported"),
    ]:
        events.append(
            {
                "event_id": f"PE-2026-{eid:03d}",
                "phish_id": ph,
                "user_id": "USR-2026-021",
                "outcome": outcome,
                "ts": today - timedelta(days=int(rng.integers(5, 70))),
                "remedial_assigned": False,
            }
        )
        eid += 1
    events.append(
        {
            "event_id": f"PE-2026-{eid:03d}",
            "phish_id": "PHISH-2026-006",
            "user_id": "USR-2026-017",
            "outcome": "Entered creds",
            "ts": today - timedelta(days=22),
            "remedial_assigned": True,
        }
    )

    # ── Cohorts (smart groups) ───────────────────────────────────────
    cohorts = [
        {
            "cohort_id": "COH-2026-001",
            "name": "Repeat clickers (90d ≥2)",
            "cohort_type": "Repeat clickers",
            "rule": "clicks_90d ≥ 2 OR creds_90d ≥ 1",
            "members": "USR-2026-014 · USR-2026-003 · USR-2026-008 · USR-2026-022",
            "size": 4,
            "avg_risk": 78,
            "playbook": "Remedial MOD-2026-007 · easy sims until 2 consecutive passes · manager notify",
            "owner": "Awareness",
            "status": "Active",
        },
        {
            "cohort_id": "COH-2026-002",
            "name": "Finance / payment authority",
            "cohort_type": "Finance / payment authority",
            "rule": "payment_authority = true",
            "members": "USR-2026-003 · USR-2026-014 · USR-2026-022 · …",
            "size": 3,
            "avg_risk": 72,
            "playbook": "MOD-2026-002 mandatory · hard BEC sims quarterly · dual-channel wire verify drill",
            "owner": "Finance + Awareness",
            "status": "Active",
        },
        {
            "cohort_id": "COH-2026-003",
            "name": "Privileged & vendor admins",
            "cohort_type": "Privileged / admin",
            "rule": "privilege=Privileged OR dept=Vendor/AMS",
            "members": "USR-2026-001 · 008 · 015 · 016 · …",
            "size": 5,
            "avg_risk": 48,
            "playbook": "MOD-2026-004/008 · admin-targeted sims · no shared IDs",
            "owner": "SecOps + TPRM",
            "status": "Active",
        },
        {
            "cohort_id": "COH-2026-004",
            "name": "New hire <90d",
            "cohort_type": "New hire <90d",
            "rule": "hire_date within 90d",
            "members": "USR-2026-017 · …",
            "size": 1,
            "avg_risk": 58,
            "playbook": "Day-1 before mailbox · weekly easy phish ×4 · buddy report coaching",
            "owner": "HR + Awareness",
            "status": "Active",
        },
        {
            "cohort_id": "COH-2026-005",
            "name": "VIP / executive assistants",
            "cohort_type": "VIP / exec",
            "rule": "privilege = Executive / VIP",
            "members": "USR-2026-010 · USR-2026-019",
            "size": 2,
            "avg_risk": 36,
            "playbook": "Deepfake/vishing module · callback verify · EA-specific sims",
            "owner": "Awareness + EA office",
            "status": "Active",
        },
        {
            "cohort_id": "COH-2026-006",
            "name": "Critical people-risk (≥75)",
            "cohort_type": "High people-risk",
            "rule": "people_risk ≥ 75",
            "members": "USR-2026-014 · …",
            "size": 1,
            "avg_risk": 88,
            "playbook": "CISO/HR coaching · access review if payment · weekly check-in 30d",
            "owner": "CISO + Awareness",
            "status": "Active — escalate",
        },
    ]

    # ── Remediation queue ────────────────────────────────────────────
    remediations = [
        {
            "rem_id": "REM-2026-001",
            "user_id": "USR-2026-014",
            "trigger": "Entered creds PHISH-2026-002 · INC-2026-003",
            "action": "Overdue remedial + manager coaching + temporary payment dual-control",
            "owner": "Awareness + Finance",
            "due": today - timedelta(days=2),
            "status": "Overdue",
            "priority": "P1",
        },
        {
            "rem_id": "REM-2026-002",
            "user_id": "USR-2026-008",
            "trigger": "Click PHISH-2026-004 · MOD-2026-004/008 overdue",
            "action": "Complete privileged + vendor modules · named-ID attestation",
            "owner": "TPRM + SecOps",
            "due": today + timedelta(days=3),
            "status": "Open",
            "priority": "P1",
        },
        {
            "rem_id": "REM-2026-003",
            "user_id": "USR-2026-003",
            "trigger": "Click PHISH-2026-002 · BEC module overdue",
            "action": "Finish MOD-2026-002 · coaching with AP lead",
            "owner": "Finance",
            "due": today + timedelta(days=5),
            "status": "Open",
            "priority": "P2",
        },
        {
            "rem_id": "REM-2026-004",
            "user_id": "USR-2026-017",
            "trigger": "New-hire creds on PHISH-2026-006",
            "action": "Remedial + restart onboarding SAT path",
            "owner": "HR",
            "due": today + timedelta(days=2),
            "status": "In progress",
            "priority": "P2",
        },
        {
            "rem_id": "REM-2026-005",
            "user_id": "USR-2026-022",
            "trigger": "Repeat clicker AP clerk",
            "action": "Easy-mode sims · remove solo payment steps until 2 passes",
            "owner": "Finance",
            "due": today + timedelta(days=7),
            "status": "Open",
            "priority": "P2",
        },
        {
            "rem_id": "REM-2026-006",
            "user_id": "COH-2026-002",
            "trigger": "Cohort — finance payment authority click rate",
            "action": "Schedule dual-channel wire verify tabletop",
            "owner": "Finance control + Awareness",
            "due": today + timedelta(days=14),
            "status": "Open",
            "priority": "P3",
        },
    ]

    # Program KPI trend (weekly)
    weeks = pd.date_range(today - timedelta(days=84), periods=13, freq="W-MON")
    kpi_trends = []
    # phish-prone declining slowly, report rate up, completion flat-ish, org risk down slightly
    for i, w in enumerate(weeks):
        t = i / max(len(weeks) - 1, 1)
        kpi_trends.append({"week": w, "metric": "Org phish-prone %", "value": round(8.2 - 2.4 * t + float(rng.normal(0, 0.25)), 2)})
        kpi_trends.append({"week": w, "metric": "Report rate %", "value": round(18 + 6 * t + float(rng.normal(0, 0.4)), 2)})
        kpi_trends.append({"week": w, "metric": "Mandatory completion %", "value": round(84 + 3 * t + float(rng.normal(0, 0.5)), 2)})
        kpi_trends.append({"week": w, "metric": "Avg people-risk", "value": round(42 - 4 * t + float(rng.normal(0, 0.6)), 2)})

    narrative = [
        {"lane": "Human risk up", "text": "Critical people-risk on payment-authority controller (Whitaker); vendor admin clickers on privileged sims."},
        {"lane": "Human risk down", "text": "Org phish-prone trending 8%→~6%; report rate rising; TPRM lead is a positive reporter model."},
        {"lane": "Program gap", "text": "Completion % looks OK while remedial for P1 clickers is overdue — vanity completion ≠ behavior change."},
        {"lane": "Ask", "text": "Clear REM-2026-001 today; enforce privileged modules on Orbit AMS; finance dual-control until two clean sims."},
    ]

    df_m = pd.DataFrame(modules)
    df_p = pd.DataFrame(people)
    df_p["hire_date"] = pd.to_datetime(df_p["hire_date"], errors="coerce")
    df_p["last_training"] = pd.to_datetime(df_p["last_training"], errors="coerce")
    df_a = pd.DataFrame(assignments)
    for col in ("due", "completed"):
        df_a[col] = pd.to_datetime(df_a[col], errors="coerce")
    df_ph = pd.DataFrame(phish)
    for col in ("launched", "closed"):
        df_ph[col] = pd.to_datetime(df_ph[col], errors="coerce")
    df_e = pd.DataFrame(events)
    df_e["ts"] = pd.to_datetime(df_e["ts"], errors="coerce")
    df_c = pd.DataFrame(cohorts)
    df_r = pd.DataFrame(remediations)
    df_r["due"] = pd.to_datetime(df_r["due"], errors="coerce")
    df_k = pd.DataFrame(kpi_trends)
    df_k["week"] = pd.to_datetime(df_k["week"], errors="coerce")
    df_n = pd.DataFrame(narrative)

    return df_m, df_p, df_a, df_ph, df_e, df_c, df_r, df_k, df_n


def _enrich_people(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["resilience"] = np.where(
        out["clicks_90d"] + out["reports_90d"] == 0,
        np.nan,
        out["reports_90d"] / (out["clicks_90d"] + 0.01),
    )
    out["needs_remediation"] = (out["risk_band"].isin(["Critical", "High"])) | (out["overdue_modules"] > 0)
    return out


def _enrich_assign(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["is_overdue"] = out["status"].eq("Overdue") | (
        out["status"].isin(["Assigned", "In progress", "Remedial"]) & (out["due"] < today)
    )
    return out


def _enrich_phish(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["click_pct"] = (out["clicked"] / out["sent"] * 100).round(1)
    out["report_pct"] = (out["reported"] / out["sent"] * 100).round(1)
    out["cred_pct"] = (out["creds"] / out["sent"] * 100).round(2)
    out["resilience_ratio"] = (out["reported"] / out["clicked"].clip(lower=1)).round(2)
    return out


def _enrich_rem(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["open"] = ~out["status"].isin(["Closed", "Waived"])
    out["overdue"] = out["open"] & (out["due"] < today)
    return out


def _sync(seed: int):
    need = st.session_state.get(_SYNC_KEY) != seed or "sat_people" not in st.session_state
    if need:
        m, p, a, ph, e, c, r, k, n = _sample(seed)
        st.session_state.sat_modules = m
        st.session_state.sat_people = p
        st.session_state.sat_assign = a
        st.session_state.sat_phish = ph
        st.session_state.sat_events = e
        st.session_state.sat_cohorts = c
        st.session_state.sat_rem = r
        st.session_state.sat_kpi = k
        st.session_state.sat_narrative = n
        st.session_state[_SYNC_KEY] = seed
    return (
        st.session_state.sat_modules,
        st.session_state.sat_people,
        st.session_state.sat_assign,
        st.session_state.sat_phish,
        st.session_state.sat_events,
        st.session_state.sat_cohorts,
        st.session_state.sat_rem,
        st.session_state.sat_kpi,
        st.session_state.sat_narrative,
    )


def _save_people(df):
    st.session_state.sat_people = df.reset_index(drop=True)


def _save_assign(df):
    st.session_state.sat_assign = df.reset_index(drop=True)


def _save_rem(df):
    st.session_state.sat_rem = df.reset_index(drop=True)


def _patch_person(uid, **fields):
    df = st.session_state.sat_people.copy()
    loc = df.index[df["user_id"] == uid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_people(df)


def _patch_assign(aid, **fields):
    df = st.session_state.sat_assign.copy()
    loc = df.index[df["assign_id"] == aid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_assign(df)


def _patch_rem(rid, **fields):
    df = st.session_state.sat_rem.copy()
    loc = df.index[df["rem_id"] == rid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_rem(df)


def _fmt(ts) -> str:
    try:
        if ts is None or pd.isna(ts):
            return "—"
    except (TypeError, ValueError):
        return "—"
    try:
        return pd.Timestamp(ts).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _person_detail(row, assigns, events, modules, *, widget_key: str):
    uid = row["user_id"]
    wk = f"{widget_key}_{uid}"
    st.markdown(f"### {uid} · {row['name']}")
    a, b, c, d = st.columns(4)
    a.metric("People risk", f"{int(row['people_risk'])}", delta=row["risk_band"])
    b.metric("Clicks / creds (90d)", f"{int(row['clicks_90d'])} / {int(row['creds_90d'])}")
    c.metric("Reports (90d)", int(row["reports_90d"]))
    d.metric("Overdue modules", int(row["overdue_modules"]))

    c1, c2 = st.columns(2)
    c1.write(f"**Role / dept:** {row['role']} · {row['dept']}")
    c1.write(f"**Privilege:** {row['privilege']} · **Payment authority:** {'Yes' if row['payment_authority'] else 'No'}")
    c1.write(f"**Manager:** {row['manager']}")
    c1.write(f"**Cohorts:** {row['cohort_tags']}")
    c1.write(f"**Hire / last training:** {_fmt(row['hire_date'])} / {_fmt(row['last_training'])}")
    c2.write(f"**Phish-prone (proxy):** {row['phish_prone_pct']}%")
    c2.write(f"**Recommended action:** {row['recommended_action']}")
    if row["notes"]:
        c2.warning(row["notes"])
    st.write(row.get("summary") or "")

    my_a = assigns[assigns["user_id"] == uid].copy()
    if not my_a.empty:
        my_a = my_a.merge(modules[["module_id", "title"]], on="module_id", how="left")
        my_a["due"] = my_a["due"].apply(_fmt)
        my_a["completed"] = my_a["completed"].apply(_fmt)
        with st.expander(f"Assignments ({len(my_a)})", expanded=True):
            st.dataframe(
                my_a[["assign_id", "module_id", "title", "status", "due", "completed", "source"]],
                use_container_width=True,
                hide_index=True,
            )

    my_e = events[events["user_id"] == uid].copy()
    if not my_e.empty:
        my_e["ts"] = my_e["ts"].apply(_fmt)
        with st.expander(f"Phish outcomes ({len(my_e)})", expanded=True):
            st.dataframe(my_e, use_container_width=True, hide_index=True)

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Assign remedial MOD-2026-007", key=f"rem_{wk}"):
            n = len(st.session_state.sat_assign) + 1
            add = {
                "assign_id": f"ASN-2026-{n:03d}",
                "user_id": uid,
                "module_id": "MOD-2026-007",
                "status": "Remedial",
                "due": _today() + timedelta(days=5),
                "completed": pd.NaT,
                "score_pct": None,
                "source": "Manual — awareness ops",
            }
            _save_assign(pd.concat([st.session_state.sat_assign, pd.DataFrame([add])], ignore_index=True))
            st.rerun()
    with b2:
        if st.button("Notify manager", key=f"mgr_{wk}"):
            note = (row.get("notes") or "") + f" [Manager {row['manager']} notified {_fmt(_today())}.]"
            _patch_person(uid, notes=note.strip())
            st.rerun()
    with b3:
        if row["risk_band"] in {"Critical", "High"} and st.button("Acknowledge risk (demo)", key=f"ack_{wk}"):
            _patch_person(uid, recommended_action="Acknowledged — coaching scheduled")
            st.rerun()


def _phish_detail(row, *, widget_key: str):
    pid = row["phish_id"]
    st.markdown(f"### {pid} · {row['name']}")
    a, b, c, d = st.columns(4)
    a.metric("Click %", f"{row['click_pct']}%")
    b.metric("Report %", f"{row['report_pct']}%")
    c.metric("Cred harvest %", f"{row['cred_pct']}%")
    d.metric("Resilience (report/click)", f"{row['resilience_ratio']}")

    st.write(f"**Template / difficulty:** {row['template']} · {row['difficulty']}")
    st.write(f"**Audience:** {row['audience']} · **Sent:** {int(row['sent'])}")
    st.write(f"**Status:** {row['status']} · **Owner:** {row['owner']}")
    st.write(f"**Launched / closed:** {_fmt(row['launched'])} / {_fmt(row['closed'])}")
    st.write(f"**So what:** {row['so_what']}")
    st.write(f"**Decision:** {row['decision']}")
    st.write(row["summary"])

    fig = go.Figure(
        data=[
            go.Bar(
                name="Outcomes",
                x=["Reported", "Ignored", "Clicked", "Creds"],
                y=[row["reported"], row["ignored"], row["clicked"], row["creds"]],
            )
        ]
    )
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10), title="Outcome counts")
    st.plotly_chart(fig, use_container_width=True, key=f"plotly_phish_{widget_key}_{pid}")


def main() -> None:
    portfolio_skin.page_header(
        title="Security Awareness Training Tracker",
        lede="Human-risk SAT workbench — people scores, phishing outcomes, smart cohorts, remedial queues. Not a video completion list. Club demo — synthetic.",
        kicker="Awareness · Human risk",
    )

    seed = demo_kit.seed_controls()
    modules, people, assigns, phish, events, cohorts, rems, kpi, narrative = _sync(seed)
    ep = _enrich_people(people)
    ea = _enrich_assign(assigns)
    eph = _enrich_phish(phish)
    er = _enrich_rem(rems)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    band_f = st.sidebar.multiselect("Risk bands", RISK_BANDS, default=RISK_BANDS)
    dept_f = st.sidebar.multiselect("Departments", DEPTS, default=DEPTS)
    needs_only = st.sidebar.checkbox("Needs remediation only", value=False)

    view_p = ep[ep["risk_band"].isin(band_f) & ep["dept"].isin(dept_f)]
    if needs_only:
        view_p = view_p[view_p["needs_remediation"]]

    crit = int((ep["risk_band"] == "Critical").sum())
    high = int((ep["risk_band"] == "High").sum())
    overdue_a = int(ea["is_overdue"].sum())
    rem_od = int(er["overdue"].sum())
    active_phish = int(eph["status"].astype(str).str.contains("Active").sum())
    avg_risk = round(float(ep["people_risk"].mean()), 1)

    # Latest closed-ish org phish-prone from trends
    latest_pp = kpi[kpi["metric"] == "Org phish-prone %"].sort_values("week").iloc[-1]["value"]

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Avg people-risk", avg_risk)
    k2.metric("Critical / High humans", f"{crit} / {high}")
    k3.metric("Overdue assignments", overdue_a)
    k4.metric("Remediation overdue", rem_od)
    k5.metric("Active phish campaigns", active_phish)
    k6.metric("Org phish-prone (trend)", f"{latest_pp}%")

    if rem_od:
        st.error(f"{rem_od} remediation item(s) past due — behavior change stalled.")
    elif crit:
        st.warning(f"{crit} critical people-risk user(s). Completion dashboards will lie to you here.")

    work, people_tab, phish_tab, train_tab, cohort_tab, program_tab, intake, export = st.tabs(
        [
            "Workbench",
            "People risk",
            "Phishing sims",
            "Training",
            "Cohorts",
            "Program KPIs",
            "Intake",
            "Export",
        ]
    )

    with work:
        st.subheader("Awareness / human-risk workbench")
        for _, n in narrative.iterrows():
            st.write(f"**{n['lane']}:** {n['text']}")

        st.markdown("---")
        st.markdown("**Featured people — statement of record**")
        feat = ep[ep["user_id"].isin(FEATURED_PEOPLE)].copy()
        order = {i: n for n, i in enumerate(["USR-2026-014", "USR-2026-003", "USR-2026-008", "USR-2026-021"])}
        feat["_o"] = feat["user_id"].map(lambda x: order.get(x, 99))
        for _, row in feat.sort_values("_o").iterrows():
            st.markdown("---")
            _person_detail(row, ea, events, modules, widget_key="feat")
            st.markdown("---")

        st.markdown("**Featured phishing campaigns**")
        for _, row in eph[eph["phish_id"].isin(FEATURED_PHISH)].iterrows():
            with st.expander(f"{row['phish_id']} · {row['name']} · click {row['click_pct']}%", expanded=True):
                _phish_detail(row, widget_key="feat")

        hot_r = er[er["open"]].sort_values(["priority", "due"])
        st.markdown(f"**Remediation queue ({len(hot_r)})**")
        for _, r in hot_r.iterrows():
            flag = " · OVERDUE" if r["overdue"] else ""
            with st.expander(f"{r['rem_id']} · {r['priority']} · {r['user_id']} · {_fmt(r['due'])}{flag}"):
                st.write(f"**Trigger:** {r['trigger']}")
                st.write(f"**Action:** {r['action']}")
                st.write(f"**Owner:** {r['owner']} · **Status:** {r['status']}")
                c1, c2 = st.columns(2)
                with c1:
                    if r["status"] != "Closed" and st.button("Mark closed", key=f"rc_{r['rem_id']}"):
                        _patch_rem(r["rem_id"], status="Closed")
                        st.rerun()
                with c2:
                    if r["status"] == "Open" and st.button("In progress", key=f"rp_{r['rem_id']}"):
                        _patch_rem(r["rem_id"], status="In progress")
                        st.rerun()

    with people_tab:
        st.subheader("People risk register")
        st.caption(
            "Composite score from sim failures, credential harvest, overdue training, privilege, "
            "payment authority, real incidents, minus reporting — KnowBe4/Proofpoint-style, synthetic."
        )
        show = view_p.sort_values("people_risk", ascending=False)[
            [
                "user_id",
                "name",
                "dept",
                "role",
                "privilege",
                "payment_authority",
                "people_risk",
                "risk_band",
                "clicks_90d",
                "creds_90d",
                "reports_90d",
                "overdue_modules",
                "cohort_tags",
                "recommended_action",
            ]
        ]
        st.dataframe(show, use_container_width=True, hide_index=True)

        fig = px.histogram(
            view_p,
            x="people_risk",
            color="risk_band",
            nbins=20,
            title="People-risk distribution",
            category_orders={"risk_band": RISK_BANDS},
        )
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True, key="plotly_risk_hist")

        pick = st.selectbox("Person detail", view_p.sort_values("people_risk", ascending=False)["user_id"].tolist(), key="people_pick")
        row = ep[ep["user_id"] == pick].iloc[0]
        _person_detail(row, ea, events, modules, widget_key="tab")

    with phish_tab:
        st.subheader("Phishing simulations")
        st.caption("Outcomes that matter: click %, report %, cred harvest, resilience ratio — not 'campaign sent'.")
        show = eph[
            [
                "phish_id",
                "name",
                "difficulty",
                "status",
                "sent",
                "click_pct",
                "report_pct",
                "cred_pct",
                "resilience_ratio",
                "audience",
            ]
        ].copy()
        st.dataframe(show, use_container_width=True, hide_index=True)

        fig = px.bar(
            eph,
            x="phish_id",
            y=["click_pct", "report_pct"],
            barmode="group",
            title="Click vs report % by campaign",
        )
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True, key="plotly_phish_cmp")

        pick = st.selectbox("Campaign detail", eph["phish_id"].tolist(), key="phish_pick")
        _phish_detail(eph[eph["phish_id"] == pick].iloc[0], widget_key="tab")

    with train_tab:
        st.subheader("Training catalog & assignments")
        st.dataframe(modules, use_container_width=True, hide_index=True)

        od = ea[ea["is_overdue"]].copy()
        od = od.merge(people[["user_id", "name", "dept"]], on="user_id", how="left")
        od = od.merge(modules[["module_id", "title"]], on="module_id", how="left")
        st.markdown(f"**Overdue assignments ({len(od)})**")
        if od.empty:
            st.info("Clear.")
        else:
            oshow = od.copy()
            oshow["due"] = oshow["due"].apply(_fmt)
            st.dataframe(
                oshow[["assign_id", "user_id", "name", "dept", "module_id", "title", "status", "due", "source"]],
                use_container_width=True,
                hide_index=True,
            )
            aid = st.selectbox("Mark complete", od["assign_id"].tolist(), key="asn_pick")
            if st.button("Complete assignment", key="asn_done"):
                _patch_assign(aid, status="Completed", completed=_today(), score_pct=85)
                # reduce overdue count on person if possible
                uid = od[od["assign_id"] == aid].iloc[0]["user_id"]
                prow = ep[ep["user_id"] == uid].iloc[0]
                _patch_person(uid, overdue_modules=max(0, int(prow["overdue_modules"]) - 1), last_training=_today())
                st.rerun()

        # Completion by dept (mandatory)
        mand = ea[ea["module_id"].isin(["MOD-2026-001", "MOD-2026-003", "MOD-2026-005"])].merge(
            people[["user_id", "dept"]], on="user_id"
        )
        mand["done"] = mand["status"].eq("Completed")
        by = mand.groupby("dept")["done"].mean().mul(100).round(1).reset_index(name="completion_pct")
        fig = px.bar(by, x="dept", y="completion_pct", title="Mandatory module completion % by dept")
        fig.add_hline(y=90, line_dash="dash", annotation_text="90% target")
        fig.update_layout(height=320, xaxis_tickangle=-25, margin=dict(l=10, r=10, t=40, b=80))
        st.plotly_chart(fig, use_container_width=True, key="plotly_dept_comp")
        st.caption("Completion is necessary but not sufficient — pair with people-risk and sim outcomes.")

    with cohort_tab:
        st.subheader("Smart cohorts / groups")
        st.caption("Auto-segmentation like KnowBe4 Smart Groups / Proofpoint priority populations.")
        for _, c in cohorts.iterrows():
            with st.expander(f"{c['cohort_id']} · {c['name']} · n={int(c['size'])} · avg risk {c['avg_risk']}"):
                st.write(f"**Type:** {c['cohort_type']}")
                st.write(f"**Rule:** {c['rule']}")
                st.write(f"**Members (sample):** {c['members']}")
                st.write(f"**Playbook:** {c['playbook']}")
                st.write(f"**Owner / status:** {c['owner']} · {c['status']}")

    with program_tab:
        st.subheader("Program KPIs (board-friendly)")
        st.caption("Trends over vanity snapshots. Aligns to security metrics KRI-2026-010 phishing resilience.")
        fig = px.line(kpi, x="week", y="value", color="metric", markers=True, title="13-week program trends")
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True, key="plotly_prog_kpi")

        # Dept risk rollup
        roll = (
            ep.groupby("dept")
            .agg(avg_risk=("people_risk", "mean"), n=("user_id", "count"), critical=("risk_band", lambda s: (s == "Critical").sum()))
            .reset_index()
        )
        roll["avg_risk"] = roll["avg_risk"].round(1)
        st.dataframe(roll.sort_values("avg_risk", ascending=False), use_container_width=True, hide_index=True)

        st.info(
            "Talking point: 87% 'completed phishing video' while a payment controller harvests credentials "
            "is how awareness programs get laughed out of the boardroom. Lead with people-risk and remediation SLAs."
        )

    with intake:
        st.subheader("Add person (demo)")
        with st.form("intake_user"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Name")
                dept = st.selectbox("Department", DEPTS)
                role = st.text_input("Role")
            with c2:
                priv = st.selectbox("Privilege", PRIVILEGE)
                pay = st.checkbox("Payment authority")
                risk = st.slider("Initial people-risk", 5, 95, 40)
            if st.form_submit_button("Create"):
                if not name.strip():
                    st.error("Name required.")
                else:
                    n = len(st.session_state.sat_people) + 1
                    band = "Critical" if risk >= 75 else "High" if risk >= 55 else "Medium" if risk >= 35 else "Low"
                    add = {
                        "user_id": f"USR-2026-{n:03d}",
                        "name": name.strip(),
                        "dept": dept,
                        "role": role.strip() or "TBD",
                        "privilege": priv,
                        "payment_authority": bool(pay),
                        "manager": "TBD",
                        "hire_date": _today(),
                        "clicks_90d": 0,
                        "creds_90d": 0,
                        "reports_90d": 0,
                        "overdue_modules": 0,
                        "real_incident_flag": False,
                        "people_risk": int(risk),
                        "risk_band": band,
                        "last_training": _today(),
                        "phish_prone_pct": 0.0,
                        "cohort_tags": "New hire <90d",
                        "notes": "Intake stub",
                        "recommended_action": "Assign mandatory modules",
                        "summary": "Intake stub.",
                    }
                    _save_people(pd.concat([st.session_state.sat_people, pd.DataFrame([add])], ignore_index=True))
                    st.success(f"USR-2026-{n:03d} created.")
                    st.rerun()

        st.subheader("Log remediation")
        with st.form("intake_rem"):
            uid = st.selectbox("User", people["user_id"].tolist())
            trigger = st.text_input("Trigger")
            action = st.text_area("Action")
            due_d = st.number_input("Due in days", 1, 60, 7)
            if st.form_submit_button("Create remediation"):
                n = len(st.session_state.sat_rem) + 1
                add = {
                    "rem_id": f"REM-2026-{n:03d}",
                    "user_id": uid,
                    "trigger": trigger.strip() or "Manual",
                    "action": action.strip() or "TBD",
                    "owner": "Awareness",
                    "due": _today() + timedelta(days=int(due_d)),
                    "status": "Open",
                    "priority": "P2",
                }
                _save_rem(pd.concat([st.session_state.sat_rem, pd.DataFrame([add])], ignore_index=True))
                st.success(f"REM-2026-{n:03d} logged.")
                st.rerun()

    with export:
        st.subheader("Export")
        out_p = ep.copy()
        out_p["hire_date"] = out_p["hire_date"].apply(_fmt)
        out_p["last_training"] = out_p["last_training"].apply(_fmt)
        demo_kit.csv_download(out_p, "people_risk.csv", label="Download people risk")
        out_a = ea.copy()
        out_a["due"] = out_a["due"].apply(_fmt)
        out_a["completed"] = out_a["completed"].apply(_fmt)
        demo_kit.csv_download(out_a, "training_assignments.csv", label="Download assignments", key="a_csv")
        out_ph = eph.copy()
        out_ph["launched"] = out_ph["launched"].apply(_fmt)
        out_ph["closed"] = out_ph["closed"].apply(_fmt)
        demo_kit.csv_download(out_ph, "phishing_sims.csv", label="Download phishing sims", key="ph_csv")
        out_r = er.copy()
        out_r["due"] = out_r["due"].apply(_fmt)
        demo_kit.csv_download(out_r, "remediation_queue.csv", label="Download remediations", key="r_csv")
        demo_kit.csv_download(cohorts, "cohorts.csv", label="Download cohorts", key="c_csv")
        demo_kit.csv_download(modules, "modules.csv", label="Download modules", key="m_csv")
        st.caption("Resample rebuilds demo data. Session-local edits only. Not a live SAT platform.")


if __name__ == "__main__":
    main()
