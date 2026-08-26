#!/usr/bin/env python3
"""Security metrics / CISO decision dashboard — club teaching toy.

Outcome-oriented KRIs (not vanity green arrows): posture, detection &
response, exposure/vuln aging, control coverage, incident & exception
load — structured like board/SOC dashboards from SIEM / CNAPP / vuln
leaders, with synthetic portfolio cross-links. Not a live telemetry feed.
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
    page_title="Security Metrics Dashboard · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

DOMAINS = [
    "Posture / risk",
    "Detection & response",
    "Exposure / vulnerability",
    "Coverage / controls",
    "Identity & access",
    "Awareness / human",
    "Compliance / audit",
    "Third-party / supply",
]
DIRECTIONS = ["Improving", "Stable", "Worsening", "Unknown"]
DECISION_TYPES = [
    "Fund / resource",
    "Accept risk",
    "Remediate now",
    "Escalate to board",
    "Monitor",
    "Change SLA / policy",
]
FEATURED_KRIS = {"KRI-2026-001", "KRI-2026-002", "KRI-2026-005", "KRI-2026-008", "KRI-2026-012"}
_SYNC_KEY = "_secmet_seed_v1"


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _now() -> pd.Timestamp:
    return pd.Timestamp.now()


def _sample(seed: int):
    today = _today()
    now = _now()
    rng = np.random.default_rng(seed)

    # ── Outcome KRIs (decision objects, not vanity counters) ─────────
    kris = [
        {
            "kri_id": "KRI-2026-001",
            "name": "Crown-jewel visibility & coverage",
            "domain": "Coverage / controls",
            "value": 86.0,
            "unit": "%",
            "target": 98.0,
            "direction": "Worsening",
            "prior": 91.0,
            "owner": "CISO / CAASM",
            "audience": "Board · CISO",
            "formula": "Verified crown-jewel CIs with EDR+vuln+SIEM+backup / total crown jewels",
            "so_what": "14% of crown jewels have a coverage gap — JUMP-DMZ-03 and PayrollCo freeze cut the score.",
            "decision": "Remediate now",
            "decision_detail": "Fund SIEM onjump + re-attest PayrollCo backup scope before board packet locks.",
            "linked": "AST-2026-005 · DST-2026-001 · GAP-2026-001",
            "status": "Breach of target",
            "as_of": today,
            "summary": "Best-in-breed posture dashboards lead with critical-asset coverage, not 'EDR installed %'. This KRI fails when inventory or telemetry lies.",
        },
        {
            "kri_id": "KRI-2026-002",
            "name": "Mean time to detect (MTTD)",
            "domain": "Detection & response",
            "value": 18.4,
            "unit": "hours",
            "target": 8.0,
            "direction": "Worsening",
            "prior": 11.2,
            "owner": "SOC Lead",
            "audience": "CISO · Board",
            "formula": "Avg (detect_ts − first_hostile_activity) for Sev1–2 last 90d",
            "so_what": "PayrollCo backup issue sat ~10h before IR open; portal stuffing was faster. Aggregate pulled by supplier blind spots.",
            "decision": "Fund / resource",
            "decision_detail": "Vendor telemetry SLA + SOC surge for processor incidents; don't celebrate internal MTTD alone.",
            "linked": "INC-2026-009 · INC-2026-001",
            "status": "Breach of target",
            "as_of": today,
            "summary": "Outcome metric. Vanity cousin is 'SIEM events processed' — we don't show that.",
        },
        {
            "kri_id": "KRI-2026-003",
            "name": "Mean time to contain (MTTC)",
            "domain": "Detection & response",
            "value": 5.1,
            "unit": "hours",
            "target": 4.0,
            "direction": "Stable",
            "prior": 4.8,
            "owner": "IR Lead",
            "audience": "CISO",
            "formula": "Avg (contain_ts − detect_ts) Sev1–2 last 90d",
            "so_what": "Containment OK when we own the plane; processor incidents stall at 'assessing'.",
            "decision": "Change SLA / policy",
            "decision_detail": "Define processor-contain playbooks with TPRM kill-switch criteria.",
            "linked": "INC-2026-009 · PLN IR",
            "status": "Near miss",
            "as_of": today,
            "summary": "Separating contain from full remediate avoids MTTR mush that boards can't act on.",
        },
        {
            "kri_id": "KRI-2026-004",
            "name": "Mean time to remediate (full close)",
            "domain": "Detection & response",
            "value": 9.6,
            "unit": "days",
            "target": 7.0,
            "direction": "Worsening",
            "prior": 7.2,
            "owner": "IR Lead / GRC",
            "audience": "CISO",
            "formula": "Avg (close_ts − detect_ts) for closed Sev1–2; open excl.",
            "so_what": "IFS exposure and payroll processor still open — remediate clock is the business story.",
            "decision": "Escalate to board",
            "decision_detail": "Board brief: two open Sev1 with privacy/NIS2 dual-report adjacency.",
            "linked": "INC-2026-005 · INC-2026-009 · PB-2026-*",
            "status": "Breach of target",
            "as_of": today,
            "summary": "Full close includes root cause and control fix — not just ticket status.",
        },
        {
            "kri_id": "KRI-2026-005",
            "name": "Critical vuln SLA compliance (≤7d)",
            "domain": "Exposure / vulnerability",
            "value": 71.0,
            "unit": "%",
            "target": 95.0,
            "direction": "Worsening",
            "prior": 84.0,
            "owner": "Vuln Mgmt · Platform",
            "audience": "CISO · Board",
            "formula": "Crit CVEs closed ≤7d / crit opened in window (excl. accepted risk w/ EXC)",
            "so_what": "Change freeze + IBM i / JDE patch windows + JUMP exposure drove miss. Accepted risks must be EXC-linked.",
            "decision": "Remediate now",
            "decision_detail": "Prioritize crown-jewel crits; force EXC-2026-* for anything past SLA.",
            "linked": "VUL-2026-001 · VUL-2026-004 · EXC-2026-004",
            "status": "Breach of target",
            "as_of": today,
            "summary": "Patch count is vanity. SLA on criticals against crown jewels is the decision metric.",
        },
        {
            "kri_id": "KRI-2026-006",
            "name": "Open critical / high findings (aged)",
            "domain": "Exposure / vulnerability",
            "value": 38.0,
            "unit": "findings",
            "target": 15.0,
            "direction": "Worsening",
            "prior": 24.0,
            "owner": "Vuln Mgmt",
            "audience": "CISO",
            "formula": "Open Crit+High older than SLA (7d crit / 30d high)",
            "so_what": "Backlog is risk concentration, not 'work left'. 11 on crown-jewel services.",
            "decision": "Fund / resource",
            "decision_detail": "Surge week on PRODBOX / portal / jump; defer low on marketing-DB.",
            "linked": "AST-2026-001 · AST-2026-007 · AST-2026-005",
            "status": "Breach of target",
            "as_of": today,
            "summary": "Aging + asset criticality beats raw open counts.",
        },
        {
            "kri_id": "KRI-2026-007",
            "name": "Alert → true-positive incident rate",
            "domain": "Detection & response",
            "value": 4.2,
            "unit": "%",
            "target": 8.0,
            "direction": "Stable",
            "prior": 4.0,
            "owner": "SOC Lead",
            "audience": "CISO",
            "formula": "Confirmed incidents / actionable alerts (excl. info)",
            "so_what": "Low conversion = analyst burnout and missed signal. Tuning debt after portal stuffing rules.",
            "decision": "Fund / resource",
            "decision_detail": "Detection engineering sprint: suppress known-good, promote high-fidelity.",
            "linked": "SOC queue · INC-2026-001 detections",
            "status": "Near miss",
            "as_of": today,
            "summary": "Opposite of vanity 'alerts closed'. Quality of signal.",
        },
        {
            "kri_id": "KRI-2026-008",
            "name": "Privileged path monitoring coverage",
            "domain": "Identity & access",
            "value": 78.0,
            "unit": "%",
            "target": 100.0,
            "direction": "Worsening",
            "prior": 92.0,
            "owner": "SecOps · Alex Rivera",
            "audience": "CISO · Audit",
            "formula": "Privileged jump/PAM sessions with SIEM+session log / all privileged paths",
            "so_what": "JUMP-DMZ-03 not in SIEM — false assurance on ROPA-2026-006 / NIS2 monitoring.",
            "decision": "Remediate now",
            "decision_detail": "Ship jump logs this week; block new privileged paths without telemetry.",
            "linked": "AST-2026-005 · ROPA-2026-006 · NIS2",
            "status": "Breach of target",
            "as_of": today,
            "summary": "Identity/control coverage the board can understand: are admin paths watched?",
        },
        {
            "kri_id": "KRI-2026-009",
            "name": "MFA coverage (workforce + break-glass exceptions)",
            "domain": "Identity & access",
            "value": 94.0,
            "unit": "%",
            "target": 99.0,
            "direction": "Improving",
            "prior": 91.0,
            "owner": "IAM",
            "audience": "CISO",
            "formula": "Users with phishing-resistant or MFA / in-scope identities (svc accts separate)",
            "so_what": "Gap is mostly service accounts + 3 break-glass with EXC. Portal B2C MFA phased.",
            "decision": "Monitor",
            "decision_detail": "Finish B2C MFA phase; keep EXC aged <90d.",
            "linked": "EXC-2026-011 · AST-2026-008",
            "status": "Near miss",
            "as_of": today,
            "summary": "Coverage with exception hygiene — not 'MFA project complete'.",
        },
        {
            "kri_id": "KRI-2026-010",
            "name": "Phishing resilience (report − click)",
            "domain": "Awareness / human",
            "value": 2.1,
            "unit": "ratio",
            "target": 3.0,
            "direction": "Improving",
            "prior": 1.4,
            "owner": "Awareness · HR",
            "audience": "CISO",
            "formula": "Report rate / click rate on last campaign (higher better)",
            "so_what": "Click 3.8% · report 8.0%. Better than last quarter; still below target ratio.",
            "decision": "Monitor",
            "decision_detail": "Target finance + AMS vendor admins next sim.",
            "linked": "Campaign Q3",
            "status": "Near miss",
            "as_of": today,
            "summary": "Resilience ratio beats completion % vanity.",
        },
        {
            "kri_id": "KRI-2026-011",
            "name": "Active risk exceptions (past review)",
            "domain": "Compliance / audit",
            "value": 7.0,
            "unit": "exceptions",
            "target": 3.0,
            "direction": "Worsening",
            "prior": 4.0,
            "owner": "GRC",
            "audience": "CISO · Audit committee",
            "formula": "Open EXC past next_review or compensating control unverified",
            "so_what": "Stale waivers are silent risk acceptance. Includes patch SLA and IFS-related.",
            "decision": "Escalate to board",
            "decision_detail": "Force re-cert or close; no silent renewals this cycle.",
            "linked": "EXC-2026-004 · EXC-2026-011",
            "status": "Breach of target",
            "as_of": today,
            "summary": "Exception aging is a first-class KRI in mature GRC platforms.",
        },
        {
            "kri_id": "KRI-2026-012",
            "name": "Material third-party cyber incidents (open)",
            "domain": "Third-party / supply",
            "value": 2.0,
            "unit": "incidents",
            "target": 0.0,
            "direction": "Worsening",
            "prior": 0.0,
            "owner": "TPRM / CISO",
            "audience": "Board · CISO",
            "formula": "Open Sev1–2 where primary blast is processor/vendor",
            "so_what": "PayrollCo + Orbit AMS adjacency. Residual risk not on internal EDR charts.",
            "decision": "Escalate to board",
            "decision_detail": "Board: processing freeze, Art.33/NIS2 clocks, exit options.",
            "linked": "INC-2026-009 · VND-2026-001 · VND-2026-003",
            "status": "Breach of target",
            "as_of": today,
            "summary": "Supply-chain cyber is a board metric — CNAPP/SIEM leaders now surface vendor blast radius.",
        },
        {
            "kri_id": "KRI-2026-013",
            "name": "Backup restore test success (tier-0)",
            "domain": "Coverage / controls",
            "value": 67.0,
            "unit": "%",
            "target": 100.0,
            "direction": "Stable",
            "prior": 67.0,
            "owner": "Infra / BCM",
            "audience": "CISO · Board",
            "formula": "Tier-0 services with successful restore test ≤90d / tier-0 count",
            "so_what": "PRODBOX / Z tested; portal OK; payroll processor restore unverified under IR.",
            "decision": "Accept risk",
            "decision_detail": "Documented accept until PayrollCo IR closes — time-box 14d.",
            "linked": "BIA / PLN-2026-* · VND-2026-001",
            "status": "Breach of target",
            "as_of": today,
            "summary": "Backup configured ≠ restore proven. Outcome over activity.",
        },
        {
            "kri_id": "KRI-2026-014",
            "name": "External attack-surface critical exposures",
            "domain": "Exposure / vulnerability",
            "value": 9.0,
            "unit": "exposures",
            "target": 3.0,
            "direction": "Improving",
            "prior": 14.0,
            "owner": "ASM / SecOps",
            "audience": "CISO",
            "formula": "Internet-facing critical findings (auth bypass, RCE, open admin)",
            "so_what": "Down from 14 after portal hardening; 9 remain incl. staging bleed and jump management plane.",
            "decision": "Remediate now",
            "decision_detail": "Kill staging bleed; restrict jump mgmt to VPN+PAM only.",
            "linked": "AST-2026-007 · AST-2026-005",
            "status": "Breach of target",
            "as_of": today,
            "summary": "ASM-style exposure count with trend — what Wiz/Tenable-style boards show.",
        },
        {
            "kri_id": "KRI-2026-015",
            "name": "Control effectiveness (sampled)",
            "domain": "Compliance / audit",
            "value": 81.0,
            "unit": "%",
            "target": 90.0,
            "direction": "Stable",
            "prior": 80.0,
            "owner": "GRC / Internal Audit",
            "audience": "Audit committee",
            "formula": "Controls tested operating effectively / controls tested (rolling 90d)",
            "so_what": "Failures cluster: privileged logging, vendor sub-processor notice, IFS ACL.",
            "decision": "Remediate now",
            "decision_detail": "Tie failed controls to open INC/EXC; no green SoA without evidence.",
            "linked": "ISO 27701 SoA · PBC-2026-003",
            "status": "Near miss",
            "as_of": today,
            "summary": "Design existence ≠ operating effectiveness — GRC platforms lead with this distinction.",
        },
    ]

    # Trend series (90d weekly) for featured / charted KRIs
    weeks = pd.date_range(today - timedelta(days=84), periods=13, freq="W-MON")
    trends = []
    bases = {
        "KRI-2026-001": (91, 86, True),
        "KRI-2026-002": (9, 18.4, True),
        "KRI-2026-005": (88, 71, True),
        "KRI-2026-008": (95, 78, True),
        "KRI-2026-012": (0, 2, True),
        "KRI-2026-014": (14, 9, False),
    }
    for kid, (start, end, higher_worse) in bases.items():
        for i, w in enumerate(weeks):
            t = i / max(len(weeks) - 1, 1)
            noise = float(rng.normal(0, abs(end - start) * 0.04))
            val = start + (end - start) * t + noise
            trends.append(
                {
                    "kri_id": kid,
                    "week": w,
                    "value": round(max(val, 0), 2),
                    "higher_worse": higher_worse,
                }
            )

    # Alert funnel (SOC)
    funnel = pd.DataFrame(
        [
            {"stage": "Raw signals (7d)", "count": 1_240_000, "order": 1},
            {"stage": "Correlated alerts", "count": 18_400, "order": 2},
            {"stage": "Actionable / queued", "count": 1_120, "order": 3},
            {"stage": "Investigated", "count": 640, "order": 4},
            {"stage": "True positive / incident", "count": 27, "order": 5},
            {"stage": "Sev1–2 declared", "count": 4, "order": 6},
        ]
    )

    # Coverage by control domain × criticality
    coverage = [
        {"control": "EDR", "crown_jewel": 96, "high": 91, "medium": 84, "gap_note": "OT / a few jump hosts"},
        {"control": "Vuln scan", "crown_jewel": 88, "high": 85, "medium": 70, "gap_note": "IBM i / Z auth scan limits"},
        {"control": "SIEM ingest", "crown_jewel": 82, "high": 78, "medium": 65, "gap_note": "JUMP-DMZ-03 · some SaaS"},
        {"control": "Backup + restore test", "crown_jewel": 67, "high": 72, "medium": 80, "gap_note": "PayrollCo unverified"},
        {"control": "MFA / phishing-resistant", "crown_jewel": 94, "high": 92, "medium": 88, "gap_note": "svc accts · B2C phase"},
        {"control": "PAM / privileged session", "crown_jewel": 78, "high": 70, "medium": 55, "gap_note": "AMS + jump gap"},
        {"control": "DLP / egress", "crown_jewel": 60, "high": 55, "medium": 40, "gap_note": "Legacy midrange weak"},
        {"control": "CSPM / cloud posture", "crown_jewel": 85, "high": 80, "medium": 75, "gap_note": "Portal OK · training GPU tenant"},
    ]

    # Vuln aging buckets
    vulns = [
        {
            "vuln_id": "VUL-2026-001",
            "title": "Critical RCE on portal API dependency",
            "severity": "Critical",
            "cvss": 9.8,
            "asset": "AST-2026-007 portal",
            "crown_jewel": True,
            "age_d": 11,
            "sla_d": 7,
            "status": "Open — past SLA",
            "owner": "Platform Eng",
            "decision": "Emergency change window — EXC if slip another 48h",
            "linked_exc": "",
        },
        {
            "vuln_id": "VUL-2026-002",
            "title": "Outdated TLS on internal JDE web",
            "severity": "High",
            "cvss": 7.5,
            "asset": "AST-2026-006 JDE",
            "crown_jewel": True,
            "age_d": 34,
            "sla_d": 30,
            "status": "Open — past SLA",
            "owner": "ERP / Orbit AMS",
            "decision": "Tie to AMS change; EXC-2026-004 if freeze holds",
            "linked_exc": "EXC-2026-004",
        },
        {
            "vuln_id": "VUL-2026-003",
            "title": "Jump host missing EDR sensor",
            "severity": "High",
            "cvss": 7.1,
            "asset": "AST-2026-005 JUMP-DMZ-03",
            "crown_jewel": True,
            "age_d": 21,
            "sla_d": 14,
            "status": "In progress",
            "owner": "SecOps",
            "decision": "Same sprint as SIEM — coverage KRI depends on it",
            "linked_exc": "",
        },
        {
            "vuln_id": "VUL-2026-004",
            "title": "Privilege escalation in PAM connector",
            "severity": "Critical",
            "cvss": 9.1,
            "asset": "PAM · IdP",
            "crown_jewel": True,
            "age_d": 5,
            "sla_d": 7,
            "status": "In progress",
            "owner": "IAM",
            "decision": "Still inside SLA — watch daily",
            "linked_exc": "",
        },
        {
            "vuln_id": "VUL-2026-005",
            "title": "Public S3 listing on non-prod marketing",
            "severity": "High",
            "cvss": 7.2,
            "asset": "marketing-DB staging",
            "crown_jewel": False,
            "age_d": 8,
            "sla_d": 30,
            "status": "Open",
            "owner": "Martech",
            "decision": "Close this week — ASM exposure count",
            "linked_exc": "",
        },
        {
            "vuln_id": "VUL-2026-006",
            "title": "IBM i user profile with stale *ALLOBJ",
            "severity": "Critical",
            "cvss": 8.8,
            "asset": "AST-2026-001 PRODBOX",
            "crown_jewel": True,
            "age_d": 16,
            "sla_d": 7,
            "status": "Open — past SLA",
            "owner": "IBM i Ops / Security",
            "decision": "Remove or EXC with compensating QAUDJRN — board-visible",
            "linked_exc": "",
        },
        {
            "vuln_id": "VUL-2026-007",
            "title": "Medium XSS in support widget",
            "severity": "Medium",
            "cvss": 5.4,
            "asset": "AST-2026-007",
            "crown_jewel": False,
            "age_d": 40,
            "sla_d": 90,
            "status": "Open",
            "owner": "Platform",
            "decision": "Backlog — do not distract from crits",
            "linked_exc": "",
        },
        {
            "vuln_id": "VUL-2026-008",
            "title": "Vendor admin shared ID (Orbit)",
            "severity": "High",
            "cvss": 7.0,
            "asset": "VND-2026-003",
            "crown_jewel": True,
            "age_d": 45,
            "sla_d": 30,
            "status": "Accepted — EXC",
            "owner": "TPRM",
            "decision": "Re-challenge EXC; named IDs required",
            "linked_exc": "EXC-2026-011",
        },
    ]

    # Decision queue (what leadership must do)
    decisions = [
        {
            "decision_id": "DEC-2026-001",
            "title": "Approve emergency change for portal critical RCE",
            "kri_id": "KRI-2026-005",
            "owner": "CISO + Platform",
            "due": today + timedelta(days=1),
            "status": "Open",
            "impact": "Crown-jewel internet exposure; SLA already breached",
            "options": "Patch now · WAF virtual patch + EXC 72h · Accept (not recommended)",
        },
        {
            "decision_id": "DEC-2026-002",
            "title": "Board brief — open processor Sev1 (PayrollCo)",
            "kri_id": "KRI-2026-012",
            "owner": "CISO + GC + TPRM",
            "due": today + timedelta(days=2),
            "status": "Open",
            "impact": "Art.33 / NIS2 / payroll continuity",
            "options": "Escalate pack · continue freeze · begin exit assessment",
        },
        {
            "decision_id": "DEC-2026-003",
            "title": "Fund detection-engineering sprint (alert quality)",
            "kri_id": "KRI-2026-007",
            "owner": "CISO + SOC",
            "due": today + timedelta(days=7),
            "status": "Open",
            "impact": "Analyst capacity · MTTD secondary benefit",
            "options": "2 FTE weeks · MSSP surge · defer (risk)",
        },
        {
            "decision_id": "DEC-2026-004",
            "title": "Close or re-certify stale exceptions (≥7)",
            "kri_id": "KRI-2026-011",
            "owner": "GRC",
            "due": today + timedelta(days=5),
            "status": "Open",
            "impact": "Audit committee narrative · silent risk accept",
            "options": "Force close · re-cert with new expiry · escalate owners",
        },
        {
            "decision_id": "DEC-2026-005",
            "title": "SIEM + EDR on JUMP-DMZ-03 this week",
            "kri_id": "KRI-2026-008",
            "owner": "SecOps",
            "due": today + timedelta(days=3),
            "status": "In progress",
            "impact": "Privileged coverage KRI · NIS2 evidence",
            "options": "Complete · compensating temporary block of jump use",
        },
        {
            "decision_id": "DEC-2026-006",
            "title": "Time-box backup restore accept for PayrollCo",
            "kri_id": "KRI-2026-013",
            "owner": "BCM + TPRM",
            "due": today + timedelta(days=14),
            "status": "Open",
            "impact": "Tier-0 restore claim false until proven",
            "options": "14d accept · require vendor restore evidence · exit",
        },
    ]

    # Incident scorecard (portfolio-linked)
    incidents = [
        {
            "inc_id": "INC-2026-001",
            "title": "Portal credential stuffing",
            "sev": "Sev2",
            "mttd_h": 3.2,
            "mttc_h": 4.5,
            "status": "Contained — notify path",
            "driver_kri": "KRI-2026-002 · KRI-2026-014",
        },
        {
            "inc_id": "INC-2026-005",
            "title": "JDE IFS anonymous share",
            "sev": "Sev1",
            "mttd_h": 72.0,
            "mttc_h": 8.0,
            "status": "Open — forensics",
            "driver_kri": "KRI-2026-004 · KRI-2026-001",
        },
        {
            "inc_id": "INC-2026-009",
            "title": "PayrollCo backup-environment",
            "sev": "Sev1",
            "mttd_h": 10.0,
            "mttc_h": None,
            "status": "Assessing — processor",
            "driver_kri": "KRI-2026-002 · KRI-2026-012",
        },
        {
            "inc_id": "INC-2026-003",
            "title": "Phishing → mailbox rule",
            "sev": "Sev3",
            "mttd_h": 6.0,
            "mttc_h": 2.0,
            "status": "Closed",
            "driver_kri": "KRI-2026-010",
        },
        {
            "inc_id": "INC-2026-008",
            "title": "Suspicious VPN geo",
            "sev": "Sev3",
            "mttd_h": 1.5,
            "mttc_h": 1.0,
            "status": "Closed",
            "driver_kri": "KRI-2026-008",
        },
    ]

    # Executive narrative bullets
    narrative = [
        {
            "lane": "Risk up",
            "text": "Crown-jewel coverage and critical SLA breached; two open vendor/processor Sev1s.",
        },
        {
            "lane": "Risk down",
            "text": "External critical exposures 14→9; phishing resilience improving; MFA trending up.",
        },
        {
            "lane": "Blind spot",
            "text": "Privileged jump without SIEM + payroll restore unproven = false assurance on monitoring/BCM.",
        },
        {
            "lane": "Ask of leadership",
            "text": "Six open decisions this week — patch, board brief, exceptions, jump telemetry, backup accept, detection eng.",
        },
    ]

    df_k = pd.DataFrame(kris)
    df_k["as_of"] = pd.to_datetime(df_k["as_of"], errors="coerce")
    df_tr = pd.DataFrame(trends)
    df_tr["week"] = pd.to_datetime(df_tr["week"], errors="coerce")
    df_cov = pd.DataFrame(coverage)
    df_v = pd.DataFrame(vulns)
    df_d = pd.DataFrame(decisions)
    df_d["due"] = pd.to_datetime(df_d["due"], errors="coerce")
    df_i = pd.DataFrame(incidents)
    df_n = pd.DataFrame(narrative)

    return df_k, df_tr, funnel, df_cov, df_v, df_d, df_i, df_n


def _enrich_kri(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # For % and counts where higher can be good or bad — use domain heuristics
    higher_worse = {
        "KRI-2026-002",
        "KRI-2026-003",
        "KRI-2026-004",
        "KRI-2026-006",
        "KRI-2026-011",
        "KRI-2026-012",
        "KRI-2026-014",
    }
    out["higher_worse"] = out["kri_id"].isin(higher_worse)
    # Breach if wrong side of target
    out["off_target"] = np.where(
        out["higher_worse"],
        out["value"] > out["target"],
        out["value"] < out["target"],
    )
    out["delta"] = out["value"] - out["prior"]
    return out


def _enrich_decisions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["open"] = out["status"].isin(["Open", "In progress"])
    out["overdue"] = out["open"] & (out["due"] < today)
    out["due_soon"] = out["open"] & (out["due"] <= today + timedelta(days=3))
    return out


def _enrich_vulns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["past_sla"] = out["age_d"] > out["sla_d"]
    out["needs_action"] = out["status"].astype(str).str.contains("past SLA|In progress|Open", regex=True) & ~out[
        "status"
    ].astype(str).str.contains("Accepted")
    return out


def _sync(seed: int):
    need = st.session_state.get(_SYNC_KEY) != seed or "sec_kris" not in st.session_state
    if need:
        k, tr, fun, cov, v, d, i, n = _sample(seed)
        st.session_state.sec_kris = k
        st.session_state.sec_trends = tr
        st.session_state.sec_funnel = fun
        st.session_state.sec_cov = cov
        st.session_state.sec_vulns = v
        st.session_state.sec_decisions = d
        st.session_state.sec_incs = i
        st.session_state.sec_narrative = n
        st.session_state[_SYNC_KEY] = seed
    return (
        st.session_state.sec_kris,
        st.session_state.sec_trends,
        st.session_state.sec_funnel,
        st.session_state.sec_cov,
        st.session_state.sec_vulns,
        st.session_state.sec_decisions,
        st.session_state.sec_incs,
        st.session_state.sec_narrative,
    )


def _save_kris(df):
    st.session_state.sec_kris = df.reset_index(drop=True)


def _save_decisions(df):
    st.session_state.sec_decisions = df.reset_index(drop=True)


def _save_vulns(df):
    st.session_state.sec_vulns = df.reset_index(drop=True)


def _patch_kri(kid, **fields):
    df = st.session_state.sec_kris.copy()
    loc = df.index[df["kri_id"] == kid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_kris(df)


def _patch_decision(did, **fields):
    df = st.session_state.sec_decisions.copy()
    loc = df.index[df["decision_id"] == did]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_decisions(df)


def _patch_vuln(vid, **fields):
    df = st.session_state.sec_vulns.copy()
    loc = df.index[df["vuln_id"] == vid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_vulns(df)


def _fmt(ts) -> str:
    if ts is None:
        return "—"
    try:
        if pd.isna(ts):
            return "—"
    except (TypeError, ValueError):
        pass
    try:
        p = pd.Timestamp(ts)
        if pd.isna(p):
            return "—"
        return p.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _fmt_val(row) -> str:
    v = row["value"]
    u = row["unit"]
    if u == "%":
        return f"{v:.0f}%"
    if u in {"hours", "days", "findings", "incidents", "exceptions", "exposures", "ratio"}:
        if float(v) == int(v):
            return f"{int(v)} {u}"
        return f"{v:.1f} {u}"
    return f"{v} {u}"


def _kri_detail(row, trends, *, widget_key: str, expanded=False):
    """Render one KRI. widget_key must be unique across the full page (all tabs)."""
    kid = row["kri_id"]
    wk = f"{widget_key}_{kid}"

    st.markdown(f"### {kid} · {row['name']}")
    a, b, c, d = st.columns(4)
    a.metric("Current", _fmt_val(row), delta=f"{row['delta']:+.1f} vs prior")
    b.metric("Target", f"{row['target']:g} {row['unit']}")
    c.metric("Direction", row["direction"])
    d.metric("Status", row["status"])

    c1, c2 = st.columns(2)
    c1.write(f"**Domain:** {row['domain']}")
    c1.write(f"**Owner:** {row['owner']} · **Audience:** {row['audience']}")
    c1.write(f"**Formula:** {row['formula']}")
    c1.write(f"**Linked:** {row['linked']}")
    c2.write(f"**So what:** {row['so_what']}")
    c2.write(f"**Decision:** {row['decision']} — {row['decision_detail']}")
    st.write(row["summary"])

    t = trends[trends["kri_id"] == kid]
    if not t.empty:
        fig = px.line(t, x="week", y="value", markers=True, title="13-week trend")
        fig.add_hline(y=row["target"], line_dash="dash", annotation_text="target")
        fig.update_layout(height=280, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True, key=f"plotly_kri_{wk}")

    with st.expander("Record decision outcome", expanded=False):
        new_dec = st.selectbox(
            "Decision type",
            DECISION_TYPES,
            index=DECISION_TYPES.index(row["decision"]) if row["decision"] in DECISION_TYPES else 0,
            key=f"dec_sel_{wk}",
        )
        note = st.text_input("Decision note", key=f"dec_note_{wk}")
        if st.button("Save decision", key=f"dec_save_{wk}"):
            detail = row["decision_detail"]
            if note.strip():
                detail = f"{detail} | {note.strip()}"
            _patch_kri(kid, decision=new_dec, decision_detail=detail)
            st.rerun()


def main() -> None:
    portfolio_skin.page_header(
        title="Security Metrics Dashboard",
        lede="CISO decision dashboard — outcome KRIs, coverage, exposure aging, SOC funnel, open decisions. Not vanity green arrows. Club demo — synthetic.",
        kicker="Metrics · Posture",
    )

    seed = demo_kit.seed_controls()
    kris, trends, funnel, cov, vulns, decisions, incs, narrative = _sync(seed)
    ek = _enrich_kri(kris)
    ed = _enrich_decisions(decisions)
    ev = _enrich_vulns(vulns)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    domain_f = st.sidebar.multiselect("Domains", DOMAINS, default=DOMAINS)
    off_only = st.sidebar.checkbox("Off-target KRIs only", value=False)
    cj_vuln = st.sidebar.checkbox("Crown-jewel vulns only", value=False)

    off = int(ek["off_target"].sum())
    open_dec = int(ed["open"].sum())
    past_sla = int(ev["past_sla"].sum())
    worsening = int((ek["direction"] == "Worsening").sum())

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("KRIs tracked", len(ek))
    k2.metric("Off target", off)
    k3.metric("Worsening", worsening)
    k4.metric("Open decisions", open_dec)
    k5.metric("Vulns past SLA", past_sla)
    k6.metric("Open Sev1–2 (demo)", int((incs["sev"].isin(["Sev1", "Sev2"]) & ~incs["status"].str.contains("Closed")).sum()))

    if off >= 8:
        st.error(f"{off} KRIs off target — posture is not 'mostly green'. See decision queue.")
    elif off:
        st.warning(f"{off} KRIs off target. Direction matters more than any single green cell.")

    work, kri_tab, soc_tab, exp_tab, cov_tab, board_tab, intake, export = st.tabs(
        [
            "Workbench",
            "KRIs / outcomes",
            "Detect & respond",
            "Exposure",
            "Coverage",
            "Board brief",
            "Intake",
            "Export",
        ]
    )

    view_k = ek[ek["domain"].isin(domain_f)]
    if off_only:
        view_k = view_k[view_k["off_target"]]

    with work:
        st.subheader("CISO workbench")

        st.markdown("**Executive narrative**")
        for _, n in narrative.iterrows():
            st.write(f"**{n['lane']}:** {n['text']}")

        st.markdown("---")
        st.markdown(f"**Featured KRIs — statement of record ({len(FEATURED_KRIS)})**")
        feat = view_k[view_k["kri_id"].isin(FEATURED_KRIS)].copy()
        order = {i: n for n, i in enumerate(sorted(FEATURED_KRIS))}
        # Prefer narrative order
        pref = ["KRI-2026-001", "KRI-2026-002", "KRI-2026-005", "KRI-2026-008", "KRI-2026-012"]
        order = {i: n for n, i in enumerate(pref)}
        feat["_o"] = feat["kri_id"].map(lambda x: order.get(x, 99))
        feat = feat.sort_values("_o")
        for _, row in feat.iterrows():
            st.markdown("---")
            _kri_detail(row, trends, widget_key="feat", expanded=True)
            st.markdown("---")

        hot_d = ed[ed["open"]].sort_values("due")
        st.markdown(f"**Decision queue ({len(hot_d)})** — what leadership must choose")
        for _, d in hot_d.iterrows():
            flag = " · OVERDUE" if d["overdue"] else (" · due ≤3d" if d["due_soon"] else "")
            with st.expander(f"{d['decision_id']} · {d['title']} · {_fmt(d['due'])}{flag}"):
                st.write(f"**KRI:** {d['kri_id']} · **Owner:** {d['owner']} · **Status:** {d['status']}")
                st.write(f"**Impact:** {d['impact']}")
                st.write(f"**Options:** {d['options']}")
                c1, c2 = st.columns(2)
                with c1:
                    if d["status"] != "Closed" and st.button("Mark decided / closed", key=f"dc_{d['decision_id']}"):
                        _patch_decision(d["decision_id"], status="Closed")
                        st.rerun()
                with c2:
                    if d["status"] == "Open" and st.button("Mark in progress", key=f"dp_{d['decision_id']}"):
                        _patch_decision(d["decision_id"], status="In progress")
                        st.rerun()

        past = ev[ev["past_sla"]].sort_values("age_d", ascending=False)
        st.markdown(f"**Vulns past SLA ({len(past)})**")
        if not past.empty:
            st.dataframe(
                past[["vuln_id", "title", "severity", "asset", "age_d", "sla_d", "owner", "decision"]],
                use_container_width=True,
                hide_index=True,
            )

    with kri_tab:
        st.subheader("Outcome KRIs")
        st.caption("Each row: value · target · direction · so-what · decision. Vanity activity metrics intentionally omitted.")
        show = view_k[
            [
                "kri_id",
                "name",
                "domain",
                "value",
                "unit",
                "target",
                "direction",
                "status",
                "owner",
                "decision",
            ]
        ].copy()
        st.dataframe(show, use_container_width=True, hide_index=True)

        pick = st.selectbox("KRI detail", view_k["kri_id"].tolist(), key="kri_tab_pick")
        row = view_k[view_k["kri_id"] == pick].iloc[0]
        _kri_detail(row, trends, widget_key="tab", expanded=True)

        # Heat: domain vs status
        heat = (
            view_k.assign(flag=view_k["off_target"].map({True: "Off target", False: "On / near"}))
            .groupby(["domain", "flag"])
            .size()
            .reset_index(name="n")
        )
        if not heat.empty:
            fig = px.bar(heat, x="domain", y="n", color="flag", title="KRIs by domain · on vs off target", barmode="stack")
            fig.update_layout(height=320, xaxis_tickangle=-25, margin=dict(l=10, r=10, t=40, b=80))
            st.plotly_chart(fig, use_container_width=True, key="plotly_kri_domain_heat")

    with soc_tab:
        st.subheader("Detect & respond")
        st.caption("SIEM/XDR-style funnel + response times. Volume alone is not a win.")

        fig = go.Figure(
            go.Funnel(
                y=funnel.sort_values("order")["stage"],
                x=funnel.sort_values("order")["count"],
                textinfo="value+percent initial",
            )
        )
        fig.update_layout(height=420, title="7-day detection funnel (synthetic)")
        st.plotly_chart(fig, use_container_width=True, key="plotly_soc_funnel")

        dr = ek[ek["domain"] == "Detection & response"]
        c1, c2, c3, c4 = st.columns(4)
        for col, (_, r) in zip([c1, c2, c3, c4], dr.iterrows()):
            col.metric(r["name"].split("(")[0].strip()[:28], _fmt_val(r), delta=r["direction"])

        st.markdown("**Incident scorecard (portfolio-linked)**")
        ishow = incs.copy()
        ishow["mttc_h"] = ishow["mttc_h"].apply(lambda x: "—" if pd.isna(x) else x)
        st.dataframe(ishow, use_container_width=True, hide_index=True)
        st.caption("MTTD spike on IFS and PayrollCo dominates the 90d average — don't hide that in a blended green.")

    with exp_tab:
        st.subheader("Exposure & vulnerability aging")
        view_v = ev[ev["crown_jewel"]] if cj_vuln else ev
        st.dataframe(
            view_v[
                [
                    "vuln_id",
                    "title",
                    "severity",
                    "cvss",
                    "asset",
                    "crown_jewel",
                    "age_d",
                    "sla_d",
                    "status",
                    "owner",
                    "decision",
                    "linked_exc",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        # Aging chart
        ages = view_v.copy()
        ages["bucket"] = pd.cut(
            ages["age_d"],
            bins=[-1, 7, 14, 30, 90, 10_000],
            labels=["0–7d", "8–14d", "15–30d", "31–90d", "90d+"],
        )
        fig = px.histogram(
            ages,
            x="bucket",
            color="severity",
            title="Open findings by age bucket",
            category_orders={"bucket": ["0–7d", "8–14d", "15–30d", "31–90d", "90d+"]},
        )
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True, key="plotly_vuln_age")

        pick = st.selectbox("Vuln actions", view_v["vuln_id"].tolist(), key="vuln_pick")
        vr = view_v[view_v["vuln_id"] == pick].iloc[0]
        st.write(f"**Decision cue:** {vr['decision']}")
        b1, b2 = st.columns(2)
        with b1:
            if "Accepted" not in str(vr["status"]) and st.button("Mark remediated", key=f"vr_{pick}"):
                _patch_vuln(pick, status="Closed", age_d=0)
                st.rerun()
        with b2:
            if "Accepted" not in str(vr["status"]) and st.button("Accept with EXC", key=f"va_{pick}"):
                _patch_vuln(pick, status="Accepted — EXC", linked_exc=vr["linked_exc"] or "EXC-PENDING")
                st.rerun()

        exp_kri = ek[ek["kri_id"].isin(["KRI-2026-005", "KRI-2026-006", "KRI-2026-014"])]
        for _, row in exp_kri.iterrows():
            with st.expander(f"{row['kri_id']} · {row['name']} · {_fmt_val(row)}"):
                st.write(row["so_what"])
                st.write(f"**Decision:** {row['decision']} — {row['decision_detail']}")

    with cov_tab:
        st.subheader("Control coverage (crown jewel → medium)")
        st.caption("CNAPP / CAASM energy: coverage by control family × criticality — gaps are the story.")
        show = cov.copy()
        st.dataframe(show, use_container_width=True, hide_index=True)

        melt = cov.melt(id_vars=["control", "gap_note"], value_vars=["crown_jewel", "high", "medium"], var_name="tier", value_name="pct")
        fig = px.bar(
            melt,
            x="control",
            y="pct",
            color="tier",
            barmode="group",
            title="Coverage % by control · asset tier",
        )
        fig.add_hline(y=95, line_dash="dash", annotation_text="95% aspirational")
        fig.update_layout(height=380, xaxis_tickangle=-30, margin=dict(l=10, r=10, t=40, b=100))
        st.plotly_chart(fig, use_container_width=True, key="plotly_cov_bars")

        for _, r in cov.iterrows():
            if r["crown_jewel"] < 90:
                st.warning(f"**{r['control']}** crown-jewel {r['crown_jewel']}% — {r['gap_note']}")

    with board_tab:
        st.subheader("Board / exec brief (one page)")
        st.caption("Limit to direction, magnitude, and asks — not 40 charts.")

        for _, n in narrative.iterrows():
            st.markdown(f"- **{n['lane']}:** {n['text']}")

        board_kris = ek[ek["audience"].str.contains("Board", regex=False)].copy()
        st.markdown("**Board-facing KRIs**")
        bshow = board_kris[
            ["kri_id", "name", "value", "unit", "target", "direction", "status", "so_what", "decision"]
        ].copy()
        st.dataframe(bshow, use_container_width=True, hide_index=True)

        # Multi-trend small multiples for board set
        board_ids = board_kris["kri_id"].tolist()
        bt = trends[trends["kri_id"].isin(board_ids)]
        if not bt.empty:
            fig = px.line(
                bt,
                x="week",
                y="value",
                facet_col="kri_id",
                facet_col_wrap=3,
                markers=True,
                title="Board KRI trends (13 weeks)",
            )
            fig.update_yaxes(matches=None, showticklabels=True)
            fig.update_layout(height=480, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, use_container_width=True, key="plotly_board_trends")

        st.markdown("**Asks this cycle**")
        asks = ed[ed["open"]].sort_values("due")
        for _, d in asks.iterrows():
            st.write(f"- `{d['decision_id']}` due {_fmt(d['due'])}: {d['title']} ({d['owner']})")

        st.info(
            "Talking point: green MFA and training completion do not offset open processor Sev1, "
            "jump SIEM gap, or critical SLA at 71%. Lead with outcomes and decisions."
        )

    with intake:
        st.subheader("Register a KRI")
        with st.form("intake_kri"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("KRI name")
                domain = st.selectbox("Domain", DOMAINS)
                value = st.number_input("Current value", value=0.0)
                target = st.number_input("Target", value=0.0)
            with c2:
                unit = st.text_input("Unit", value="%")
                direction = st.selectbox("Direction", DIRECTIONS)
                owner = st.text_input("Owner")
                decision = st.selectbox("Decision", DECISION_TYPES)
            so_what = st.text_area("So what (business implication)")
            if st.form_submit_button("Create KRI"):
                if not name.strip():
                    st.error("Name required.")
                else:
                    n = len(st.session_state.sec_kris) + 1
                    add = {
                        "kri_id": f"KRI-2026-{n:03d}",
                        "name": name.strip(),
                        "domain": domain,
                        "value": float(value),
                        "unit": unit.strip() or "%",
                        "target": float(target),
                        "direction": direction,
                        "prior": float(value),
                        "owner": owner.strip() or "TBD",
                        "audience": "CISO",
                        "formula": "TBD",
                        "so_what": so_what.strip() or "TBD",
                        "decision": decision,
                        "decision_detail": "Intake stub",
                        "linked": "",
                        "status": "Draft",
                        "as_of": _today(),
                        "summary": "Intake stub — define formula and decision owner before board use.",
                    }
                    _save_kris(pd.concat([st.session_state.sec_kris, pd.DataFrame([add])], ignore_index=True))
                    st.success(f"KRI-2026-{n:03d} created.")
                    st.rerun()

        st.subheader("Add decision")
        with st.form("intake_dec"):
            title = st.text_input("Decision title")
            kri_link = st.text_input("Linked KRI ID")
            owner = st.text_input("Owner", key="dec_own")
            due_d = st.number_input("Due in days", 1, 90, 7)
            impact = st.text_area("Impact")
            if st.form_submit_button("Create decision"):
                if not title.strip():
                    st.error("Title required.")
                else:
                    n = len(st.session_state.sec_decisions) + 1
                    add = {
                        "decision_id": f"DEC-2026-{n:03d}",
                        "title": title.strip(),
                        "kri_id": kri_link.strip() or "TBD",
                        "owner": owner.strip() or "CISO",
                        "due": _today() + timedelta(days=int(due_d)),
                        "status": "Open",
                        "impact": impact.strip() or "TBD",
                        "options": "TBD",
                    }
                    _save_decisions(
                        pd.concat([st.session_state.sec_decisions, pd.DataFrame([add])], ignore_index=True)
                    )
                    st.success(f"DEC-2026-{n:03d} logged.")
                    st.rerun()

    with export:
        st.subheader("Export")
        out_k = ek.copy()
        out_k["as_of"] = out_k["as_of"].apply(_fmt)
        demo_kit.csv_download(out_k, "security_kris.csv", label="Download KRIs")
        out_d = ed.copy()
        out_d["due"] = out_d["due"].apply(_fmt)
        demo_kit.csv_download(out_d, "security_decisions.csv", label="Download decisions", key="d_csv")
        demo_kit.csv_download(ev, "vuln_aging.csv", label="Download vuln aging", key="v_csv")
        demo_kit.csv_download(cov, "control_coverage.csv", label="Download coverage", key="c_csv")
        demo_kit.csv_download(incs, "incident_scorecard.csv", label="Download incident scorecard", key="i_csv")
        st.caption("Resample rebuilds demo data. Session-local edits only. Not a live SIEM/CNAPP.")


if __name__ == "__main__":
    main()
