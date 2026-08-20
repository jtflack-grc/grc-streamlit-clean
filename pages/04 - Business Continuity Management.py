#!/usr/bin/env python3
"""Business continuity workbench — club teaching toy."""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Business Continuity Management · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

CRITICALITY = ["Mission-critical", "High", "Medium", "Low"]
BIA_STATUS = ["Current", "Due for refresh", "Overdue", "Draft"]
PLAN_STATUS = ["Approved", "In review", "Draft", "Retired"]
EXERCISE_TYPES = ["Tabletop", "Walkthrough", "Technical failover", "Full simulation"]
EXERCISE_RESULTS = ["Pass", "Pass with findings", "Fail", "Scheduled", "In progress"]
PLAN_TYPES = ["BC plan", "IT DR plan", "Crisis / crisis-comms", "Workplace", "Supplier continuity"]

# Featured processes rendered fully open on the workbench
FEATURED = {"BIA-2026-001", "BIA-2026-002", "BIA-2026-004"}


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _now() -> pd.Timestamp:
    return pd.Timestamp.now()


def _sample(seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """BIA register, BC/DR plans, and exercise records with current relative dates."""
    today = _today()
    rng = np.random.default_rng(seed)

    def j(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    # ── BIA / critical processes ─────────────────────────────────────
    processes = [
        {
            "process_id": "BIA-2026-001",
            "title": "Core ledger & settlement (IBM i + IBM Z)",
            "function": "Finance / Treasury",
            "owner": "Treasury Ops · Lead: S. Okonkwo",
            "criticality": "Mission-critical",
            "rto_h": 2,
            "rpo_h": 0.5,
            "mtpd_h": 4,
            "achievable_rto_h": 6,
            "bia_status": "Current",
            "last_bia": today - timedelta(days=45),
            "next_bia": today + timedelta(days=140),
            "systems": "IBM i PRODBOX (LPAR), IBM Z CICS / DB2, GDPS secondary sysplex, IBM i HA mirror",
            "dependencies": "Power frame · raised-floor DC · network to secondary · GDPS · overnight batch feed from JDE/SAP",
            "recovery_strategy": "GDPS role-swap for Z; IBM i HA IASP failover to secondary Power host. Manual settlement worksheet only for <4h window.",
            "upstream": "Order-to-cash (BIA-2026-002), Payment rails",
            "downstream": "Regulatory reporting, customer statements, SOX close",
            "personnel": "Mainframe Recovery Team (4) · IBM i Ops (3) · Treasury (2)",
            "workarounds": "Manual settlement worksheet for high-value wires only. Batch replay from tape if HA mirror lag exceeds RPO.",
            "gap_notes": "Achievable RTO is 6h against a 2h objective. Last technical failover (EXR-2026-003) hit 5.8h. Gap owned under remediation REM-BC-014 — secondary Power host procurement delayed.",
            "linked_plan": "PLN-2026-001",
            "linked_exercise": "EXR-2026-003",
            "risk_refs": "EXC-2026-011 (*ALLOBJ break-glass) · INC-2026-003 (active IR)",
            "notes": "Mission-critical for SOX ITGC and daily settlement. Any outage past MTPD (4h) triggers crisis protocol.",
        },
        {
            "process_id": "BIA-2026-002",
            "title": "Order-to-cash (JD Edwards World / SAP ECC)",
            "function": "Finance / Order management",
            "owner": "ERP Finance · Lead: M. Hassan",
            "criticality": "Mission-critical",
            "rto_h": 4,
            "rpo_h": 1,
            "mtpd_h": 12,
            "achievable_rto_h": 8,
            "bia_status": "Due for refresh",
            "last_bia": today - timedelta(days=280),
            "next_bia": today - timedelta(days=10),
            "systems": "JD Edwards World on IBM i · SAP ECC PRD · IBM i customer master (CUSTMAST) · payment gateway",
            "dependencies": "IBM i PRODBOX · SAP app/DB cluster · payment gateway · warehouse WMS feed",
            "recovery_strategy": "Warm LPAR failover for JDE; SAP DR landscape (QAS/PRD mirror). Batch replay from nightly save if LPAR fail. Manual order entry for top-20 customers as workaround.",
            "upstream": "Warehouse / fulfillment, customer portal",
            "downstream": "Core ledger (BIA-2026-001), AR collections, revenue recognition",
            "personnel": "ERP Recovery Team (5) · SAP Basis (2) · IBM i Ops (2)",
            "workarounds": "Manual order sheet for top-20 accounts. Hold non-critical shipments past 8h.",
            "gap_notes": "BIA refresh overdue by 10 days. Achievable RTO 8h vs 4h objective — SAP DR landscape last tested 11 months ago (walkthrough only). JDE HA LPAR failover last passed at 3.2h.",
            "linked_plan": "PLN-2026-002",
            "linked_exercise": "EXR-2026-005",
            "risk_refs": "INC-2026-005 (JDE IFS exposure) · EXC-2026-related IFS *PUBLIC",
            "notes": "Customer-facing revenue path. Portal credential-stuffing (INC-2026-001) did not take O2C offline but raised dependency awareness.",
        },
        {
            "process_id": "BIA-2026-003",
            "title": "Customer portal & identity (B2C)",
            "function": "Digital / Customer experience",
            "owner": "Platform Engineering · Lead: R. Kim",
            "criticality": "High",
            "rto_h": 8,
            "rpo_h": 2,
            "mtpd_h": 24,
            "achievable_rto_h": 4,
            "bia_status": "Current",
            "last_bia": today - timedelta(days=90),
            "next_bia": today + timedelta(days=275),
            "systems": "Customer portal · Azure AD B2C · CDN · marketing-DB read-replica · WAF",
            "dependencies": "IdP · WAF · CDN · payment gateway (read) · marketing-DB",
            "recovery_strategy": "Multi-AZ failover + CDN static degrade. IdP region failover. Static status page if auth unavailable.",
            "upstream": "CDN / ISP, IdP",
            "downstream": "Order capture (light), support tickets",
            "personnel": "Platform Eng (3) · IAM (1) · SecOps (1)",
            "workarounds": "Static status page + phone order line for priority accounts.",
            "gap_notes": "RTO currently achievable. Post INC-2026-001: CAPTCHA + rate-limit on /api/login; WAF /api/* coverage remediating.",
            "linked_plan": "PLN-2026-003",
            "linked_exercise": "EXR-2026-001",
            "risk_refs": "INC-2026-001 (credential stuffing — Recover)",
            "notes": "",
        },
        {
            "process_id": "BIA-2026-004",
            "title": "Employee payroll processing",
            "function": "HR / Payroll",
            "owner": "Payroll Ops · Lead: T. Williams",
            "criticality": "Mission-critical",
            "rto_h": 24,
            "rpo_h": 4,
            "mtpd_h": 72,
            "achievable_rto_h": 48,
            "bia_status": "Current",
            "last_bia": today - timedelta(days=60),
            "next_bia": today + timedelta(days=305),
            "systems": "PayrollCo SaaS (DPA-2024-019) · SSO federation · SFTP tax drop · HRIS",
            "dependencies": "PayrollCo SaaS · IdP SSO · banking ACH · SFTP · HRIS employee master",
            "recovery_strategy": "Primary: restore PayrollCo integration after vendor clears production. Fallback: BCP manual payroll (spreadsheet + ACH file) for one cycle. Alternate processor evaluation in TPRM.",
            "upstream": "HRIS, timekeeping",
            "downstream": "Employee pay, tax filings, benefits withholdings",
            "personnel": "Payroll Ops (3) · TPRM (1) · Treasury (1) · HR (2)",
            "workarounds": "Manual payroll workbook + ACH NACHA file. Freeze discretionary deductions if needed. Next run in 5 business days from last IR brief.",
            "gap_notes": "INC-2026-009: PayrollCo backup-env breach notification — processing suspended pending vendor IOC/tenant confirmation. Achievable RTO under suspension is manual path (~48h) vs 24h objective. Vendor SOC 2 pen-test excluded backup infrastructure.",
            "linked_plan": "PLN-2026-004",
            "linked_exercise": "EXR-2026-006",
            "risk_refs": "INC-2026-009 (SEV-2 Triage) · DPA-2024-019",
            "notes": "Mission-critical on pay calendar. Manual BCP was tabletop-tested but never run live.",
        },
        {
            "process_id": "BIA-2026-005",
            "title": "Privileged remote access (VPN / jump hosts)",
            "function": "IT / Security",
            "owner": "Infrastructure · Lead: Jordan Blake",
            "criticality": "High",
            "rto_h": 4,
            "rpo_h": 1,
            "mtpd_h": 12,
            "achievable_rto_h": 2,
            "bia_status": "Current",
            "last_bia": today - timedelta(days=120),
            "next_bia": today + timedelta(days=245),
            "systems": "VPN concentrator · 6 DMZ jump hosts · PAM vault",
            "dependencies": "IdP · PAM · SIEM · firewall · geo-block rules",
            "recovery_strategy": "Standby concentrator + jump-host rebuild from golden image. Compensating: geo-block, no split-tunnel (EXC-2026-004).",
            "upstream": "ISP, IdP",
            "downstream": "All admin recovery paths (IBM i, SAP, Z)",
            "personnel": "Infra (2) · SecOps (1)",
            "workarounds": "Break-glass console access at DC (physical) under PAM exception.",
            "gap_notes": "Hardware refresh PO approved after INC-2026-010. SIEM coverage gap on jump hosts closed under INC-2026-008 / PBC-2026-003.",
            "linked_plan": "PLN-2026-005",
            "linked_exercise": "EXR-2026-002",
            "risk_refs": "EXC-2026-004 · INC-2026-010 · INC-2026-008",
            "notes": "",
        },
        {
            "process_id": "BIA-2026-006",
            "title": "Email & collaboration",
            "function": "IT / Corporate",
            "owner": "IT Service Desk · Lead: A. Nguyen",
            "criticality": "High",
            "rto_h": 8,
            "rpo_h": 2,
            "mtpd_h": 24,
            "achievable_rto_h": 4,
            "bia_status": "Current",
            "last_bia": today - timedelta(days=150),
            "next_bia": today + timedelta(days=215),
            "systems": "M365 Exchange Online · Teams · mail gateway",
            "dependencies": "M365 tenant · DNS · mail gateway · IdP",
            "recovery_strategy": "M365 native HA. Gateway failover. Crisis channel on Slack/Teams bridge as alternate.",
            "upstream": "IdP, DNS",
            "downstream": "Crisis comms, IR bridges, customer email",
            "personnel": "IT Service Desk (4) · SecOps (mail) (1)",
            "workarounds": "SMS tree for crisis team; Slack #incident as primary during mail outage.",
            "gap_notes": "None material. BEC playbook (INC-2026-007) validated quarantine SOP.",
            "linked_plan": "PLN-2026-006",
            "linked_exercise": "EXR-2026-004",
            "risk_refs": "INC-2026-007",
            "notes": "",
        },
        {
            "process_id": "BIA-2026-007",
            "title": "Warehouse management & shipping",
            "function": "Operations / Logistics",
            "owner": "Ops · Lead: D. Marshall",
            "criticality": "High",
            "rto_h": 12,
            "rpo_h": 4,
            "mtpd_h": 36,
            "achievable_rto_h": 16,
            "bia_status": "Overdue",
            "last_bia": today - timedelta(days=400),
            "next_bia": today - timedelta(days=35),
            "systems": "WMS · carrier APIs · handheld RF · JDE inventory interface",
            "dependencies": "JDE · network · RF scanners · carrier portals",
            "recovery_strategy": "Paper pick tickets for priority SKUs. Carrier portal manual booking. Restore WMS from nightly backup.",
            "upstream": "Order-to-cash, inventory",
            "downstream": "Customer delivery, 3PL",
            "personnel": "Warehouse supervisors (6) · Ops IT (2)",
            "workarounds": "Paper pick + manual ASN. Cap daily volume at 40% of normal.",
            "gap_notes": "BIA 35 days overdue. Achievable RTO 16h vs 12h — RF scanner spare pool below target. No exercise in 18 months.",
            "linked_plan": "PLN-2026-007",
            "linked_exercise": "",
            "risk_refs": "",
            "notes": "Refresh scheduled; blocked on ops capacity.",
        },
        {
            "process_id": "BIA-2026-008",
            "title": "Corporate website & marketing CMS",
            "function": "Marketing",
            "owner": "Marketing Ops",
            "criticality": "Medium",
            "rto_h": 48,
            "rpo_h": 24,
            "mtpd_h": 120,
            "achievable_rto_h": 12,
            "bia_status": "Current",
            "last_bia": today - timedelta(days=200),
            "next_bia": today + timedelta(days=165),
            "systems": "CMS · CDN · static failover",
            "dependencies": "CDN, DNS, CMS host",
            "recovery_strategy": "CDN static snapshot. Status page.",
            "upstream": "DNS",
            "downstream": "Lead gen (non-critical)",
            "personnel": "Marketing Ops (2)",
            "workarounds": "Static site only.",
            "gap_notes": "None.",
            "linked_plan": "PLN-2026-003",
            "linked_exercise": "",
            "risk_refs": "",
            "notes": "",
        },
    ]

    # ── BC / DR plans ────────────────────────────────────────────────
    plans = [
        {
            "plan_id": "PLN-2026-001",
            "title": "IT DR — Mainframe & IBM i core finance",
            "plan_type": "IT DR plan",
            "status": "Approved",
            "version": "3.2",
            "owner": "Mainframe Recovery Team · Maya Chen (sponsor)",
            "linked_processes": "BIA-2026-001",
            "last_reviewed": today - timedelta(days=40),
            "next_review": today + timedelta(days=50),
            "last_exercised": today - timedelta(days=55),
            "coverage": "GDPS role-swap · IBM i HA IASP · settlement workaround · crisis escalation to Treasury",
            "invoke_trigger": "PRODBOX or Z CICS unavailable >30 min; or RPO breach on HA mirror",
            "gaps": "Secondary Power host capacity short of full production load — documented in REM-BC-014. Achievable RTO 6h vs 2h BIA objective.",
        },
        {
            "plan_id": "PLN-2026-002",
            "title": "BC — Order-to-cash (ERP)",
            "plan_type": "BC plan",
            "status": "In review",
            "version": "2.0-rc",
            "owner": "ERP Finance · M. Hassan",
            "linked_processes": "BIA-2026-002",
            "last_reviewed": today - timedelta(days=200),
            "next_review": today - timedelta(days=20),
            "last_exercised": today - timedelta(days=330),
            "coverage": "JDE warm LPAR · SAP DR landscape · top-20 manual order path · AR hold rules",
            "invoke_trigger": "JDE or SAP PRD unavailable >1h; or CUSTMAST integrity incident",
            "gaps": "Review overdue. SAP DR not technically exercised in 11 months. Align with BIA refresh.",
        },
        {
            "plan_id": "PLN-2026-003",
            "title": "IT DR — Digital / customer portal",
            "plan_type": "IT DR plan",
            "status": "Approved",
            "version": "1.4",
            "owner": "Platform Engineering · R. Kim",
            "linked_processes": "BIA-2026-003, BIA-2026-008",
            "last_reviewed": today - timedelta(days=70),
            "next_review": today + timedelta(days=110),
            "last_exercised": today - timedelta(days=95),
            "coverage": "Multi-AZ · CDN degrade · IdP failover · WAF · status page",
            "invoke_trigger": "Portal error rate >5% for 15 min; IdP regional outage",
            "gaps": "WAF /api/* coverage remediating post INC-2026-001.",
        },
        {
            "plan_id": "PLN-2026-004",
            "title": "Supplier continuity — PayrollCo",
            "plan_type": "Supplier continuity",
            "status": "Approved",
            "version": "1.1",
            "owner": "Payroll Ops / TPRM · T. Williams",
            "linked_processes": "BIA-2026-004",
            "last_reviewed": today - timedelta(days=30),
            "next_review": today + timedelta(days=150),
            "last_exercised": today - timedelta(days=180),
            "coverage": "Credential rotation · SSO revoke · manual payroll BCP · alternate processor evaluation · employee comms templates",
            "invoke_trigger": "Vendor breach notification; SaaS unavailable on pay calendar; DPA Art. 33 path",
            "gaps": "Manual payroll never run live — tabletop only (EXR-2026-006 Pass with findings). INC-2026-009 active.",
        },
        {
            "plan_id": "PLN-2026-005",
            "title": "IT DR — Privileged access path",
            "plan_type": "IT DR plan",
            "status": "Approved",
            "version": "2.0",
            "owner": "Infrastructure · Jordan Blake",
            "linked_processes": "BIA-2026-005",
            "last_reviewed": today - timedelta(days=25),
            "next_review": today + timedelta(days=160),
            "last_exercised": today - timedelta(days=100),
            "coverage": "Standby VPN · jump rebuild · PAM · geo-block compensating controls",
            "invoke_trigger": "VPN concentrator unavailable; mass jump-host failure",
            "gaps": "Legacy concentrator under EXC-2026-004 until hardware refresh arrives (~6 weeks).",
        },
        {
            "plan_id": "PLN-2026-006",
            "title": "Crisis communications",
            "plan_type": "Crisis / crisis-comms",
            "status": "Approved",
            "version": "4.0",
            "owner": "CISO / Comms · GRC Lead",
            "linked_processes": "BIA-2026-006, all mission-critical",
            "last_reviewed": today - timedelta(days=15),
            "next_review": today + timedelta(days=170),
            "last_exercised": today - timedelta(days=80),
            "coverage": "Exec brief templates · employee SMS · regulator / DPA · customer notice · Slack #incident / bridge",
            "invoke_trigger": "Any SEV-1; any mission-critical process past RTO; regulatory notification path",
            "gaps": "None material. Validated during ransomware and BEC incidents.",
        },
        {
            "plan_id": "PLN-2026-007",
            "title": "BC — Warehouse & shipping",
            "plan_type": "BC plan",
            "status": "Draft",
            "version": "0.9",
            "owner": "Ops · D. Marshall",
            "linked_processes": "BIA-2026-007",
            "last_reviewed": today - timedelta(days=390),
            "next_review": today - timedelta(days=30),
            "last_exercised": today - timedelta(days=540),
            "coverage": "Paper pick · carrier manual · volume cap · restore WMS",
            "invoke_trigger": "WMS unavailable >2h; site access loss",
            "gaps": "Draft only. No exercise in 18 months. BIA overdue — plan cannot finalize until BIA refresh.",
        },
    ]

    # ── Exercises ────────────────────────────────────────────────────
    exercises = [
        {
            "exercise_id": "EXR-2026-001",
            "title": "Portal multi-AZ failover (technical)",
            "exercise_type": "Technical failover",
            "plan_id": "PLN-2026-003",
            "process_ids": "BIA-2026-003",
            "owner": "Platform Engineering",
            "scheduled": today - timedelta(days=95),
            "completed": today - timedelta(days=95),
            "result": "Pass",
            "duration_h": 3.5,
            "participants": 8,
            "objective": "Fail portal + IdP to secondary AZ within RTO 8h; validate status page.",
            "outcome": "Failover complete in 42 minutes. Status page live. No data loss.",
            "findings": "CDN cache purge delayed 12 minutes — runbook step missing.",
            "remediation": "Runbook updated. Re-test not required.",
            "next_due": today + timedelta(days=270),
        },
        {
            "exercise_id": "EXR-2026-002",
            "title": "VPN standby concentrator cutover",
            "exercise_type": "Technical failover",
            "plan_id": "PLN-2026-005",
            "process_ids": "BIA-2026-005",
            "owner": "Infrastructure",
            "scheduled": today - timedelta(days=100),
            "completed": today - timedelta(days=100),
            "result": "Pass with findings",
            "duration_h": 2.0,
            "participants": 5,
            "objective": "Cut over to standby VPN; re-auth admin cohort via PAM.",
            "outcome": "Cutover in 55 minutes. Geo-block held. Compensating controls validated (INC-2026-010 context).",
            "findings": "Two jump hosts missing SIEM agents (later INC-2026-008).",
            "remediation": "SIEM onboarding closed. Hardware refresh still open under EXC-2026-004.",
            "next_due": today + timedelta(days=265),
        },
        {
            "exercise_id": "EXR-2026-003",
            "title": "IBM i HA + GDPS settlement failover",
            "exercise_type": "Technical failover",
            "plan_id": "PLN-2026-001",
            "process_ids": "BIA-2026-001",
            "owner": "Mainframe Recovery Team",
            "scheduled": today - timedelta(days=55),
            "completed": today - timedelta(days=55),
            "result": "Fail",
            "duration_h": 5.8,
            "participants": 12,
            "objective": "Role-swap Z via GDPS and fail IBM i to HA mirror within RTO 2h.",
            "outcome": "Z GDPS swap succeeded at 1.4h. IBM i HA failover delayed — secondary Power host CPU saturated under settlement batch. Total 5.8h. RTO missed.",
            "findings": "Secondary Power capacity insufficient for peak settlement. Manual worksheet used for high-value wires after hour 4.",
            "remediation": "REM-BC-014: procure additional Power capacity. Target re-test within 90 days of hardware arrival.",
            "next_due": today + timedelta(days=35 + j(-5, 6)),
        },
        {
            "exercise_id": "EXR-2026-004",
            "title": "Crisis comms tabletop — ransomware",
            "exercise_type": "Tabletop",
            "plan_id": "PLN-2026-006",
            "process_ids": "BIA-2026-006",
            "owner": "CISO / GRC",
            "scheduled": today - timedelta(days=80),
            "completed": today - timedelta(days=80),
            "result": "Pass",
            "duration_h": 2.5,
            "participants": 14,
            "objective": "Walk exec brief, employee notice, and regulator decision tree under ransomware scenario.",
            "outcome": "Templates used successfully; matched real INC-2026-002 response.",
            "findings": "Minor: SMS tree contact list had 2 stale numbers.",
            "remediation": "Contact list refreshed quarterly.",
            "next_due": today + timedelta(days=285),
        },
        {
            "exercise_id": "EXR-2026-005",
            "title": "SAP DR landscape failover (scheduled)",
            "exercise_type": "Technical failover",
            "plan_id": "PLN-2026-002",
            "process_ids": "BIA-2026-002",
            "owner": "SAP Basis / ERP",
            "scheduled": today + timedelta(days=18 + j(-3, 4)),
            "completed": pd.NaT,
            "result": "Scheduled",
            "duration_h": 0,
            "participants": 10,
            "objective": "Fail SAP ECC PRD to DR landscape; validate O2C order path for top-20 accounts.",
            "outcome": "",
            "findings": "",
            "remediation": "",
            "next_due": today + timedelta(days=18),
        },
        {
            "exercise_id": "EXR-2026-006",
            "title": "Manual payroll BCP tabletop",
            "exercise_type": "Tabletop",
            "plan_id": "PLN-2026-004",
            "process_ids": "BIA-2026-004",
            "owner": "Payroll Ops / TPRM",
            "scheduled": today - timedelta(days=180),
            "completed": today - timedelta(days=180),
            "result": "Pass with findings",
            "duration_h": 3.0,
            "participants": 7,
            "objective": "Produce NACHA ACH file from HRIS extract without PayrollCo within one pay cycle.",
            "outcome": "Workbook produced test ACH in 6 hours simulated. Banking partner accepted format.",
            "findings": "Tax withholding edge cases incomplete. No live run ever performed. Vendor backup-env gap not in TPRM checklist.",
            "remediation": "Tax edge-case appendix added to plan. Live dry-run deferred — now accelerated under INC-2026-009.",
            "next_due": today + timedelta(days=5),
        },
        {
            "exercise_id": "EXR-2026-007",
            "title": "JDE warm LPAR failover",
            "exercise_type": "Technical failover",
            "plan_id": "PLN-2026-002",
            "process_ids": "BIA-2026-002",
            "owner": "IBM i Ops",
            "scheduled": today - timedelta(days=200),
            "completed": today - timedelta(days=200),
            "result": "Pass",
            "duration_h": 3.2,
            "participants": 6,
            "objective": "Fail JDE World to warm LPAR within RTO contribution.",
            "outcome": "3.2h — within overall O2C RTO if SAP also ready. CUSTMAST integrity checks passed.",
            "findings": "IFS share permissions not reviewed during DR (later relevant to INC-2026-005).",
            "remediation": "IFS permission check added to DR checklist.",
            "next_due": today + timedelta(days=165),
        },
        {
            "exercise_id": "EXR-2026-008",
            "title": "Warehouse paper-pick walkthrough",
            "exercise_type": "Walkthrough",
            "plan_id": "PLN-2026-007",
            "process_ids": "BIA-2026-007",
            "owner": "Ops",
            "scheduled": today + timedelta(days=40),
            "completed": pd.NaT,
            "result": "Scheduled",
            "duration_h": 0,
            "participants": 8,
            "objective": "Validate paper pick tickets and volume-cap procedures after BIA refresh.",
            "outcome": "",
            "findings": "",
            "remediation": "",
            "next_due": today + timedelta(days=40),
        },
    ]

    # Featured deep detail blobs (rendered as structured sections)
    # Stored as list-of-dicts columns for evidence / steps / actions
    for p in processes:
        p.setdefault("recovery_steps", [])
        p.setdefault("evidence", [])
        p.setdefault("open_actions", [])

    processes[0]["recovery_steps"] = [
        {"seq": 1, "step": "Declare DR for core finance; open bridge; notify Treasury & CISO", "role": "Commander", "eta_min": 15},
        {"seq": 2, "step": "Confirm HA mirror lag ≤ RPO (0.5h); abort if lag exceeded — go tape path", "role": "IBM i Ops", "eta_min": 20},
        {"seq": 3, "step": "GDPS role-swap for Z CICS / DB2 to secondary sysplex", "role": "Mainframe", "eta_min": 90},
        {"seq": 4, "step": "IBM i HA IASP failover to secondary Power host; validate PRODBOX roles", "role": "IBM i Ops", "eta_min": 120},
        {"seq": 5, "step": "Settlement smoke test: 5 high-value wires + batch sample", "role": "Treasury", "eta_min": 45},
        {"seq": 6, "step": "If past 4h MTPD: activate manual settlement worksheet for critical wires only", "role": "Treasury", "eta_min": 30},
        {"seq": 7, "step": "Exec / SOX ITGC notification if outage > RTO", "role": "GRC", "eta_min": 30},
    ]
    processes[0]["evidence"] = [
        {"ref": "EVD-BC-001-A", "desc": "EXR-2026-003 after-action (Fail — 5.8h)", "source": "BC evidence locker"},
        {"ref": "EVD-BC-001-B", "desc": "GDPS runbook v3.2 signed", "source": "PLN-2026-001"},
        {"ref": "EVD-BC-001-C", "desc": "REM-BC-014 Power capacity PO status", "source": "ITSM / Procurement"},
        {"ref": "EVD-BC-001-D", "desc": "HA mirror lag dashboard export (last 90 days)", "source": "IBM i Ops"},
        {"ref": "EVD-BC-001-E", "desc": "Manual settlement worksheet template", "source": "Treasury"},
        {"ref": "EVD-BC-001-F", "desc": "BIA sign-off (45 days ago)", "source": "BCM register"},
    ]
    processes[0]["open_actions"] = [
        {"action": "REM-BC-014 — secondary Power capacity for settlement peak", "owner": "Infra / Procurement", "due": today + timedelta(days=45), "status": "In progress"},
        {"action": "Re-test IBM i HA after capacity arrival (target ≤2h)", "owner": "Mainframe Recovery", "due": today + timedelta(days=90), "status": "Blocked on hardware"},
        {"action": "Keep INC-2026-003 containment from blocking HA mirror integrity", "owner": "Maya Chen / IR", "due": today + timedelta(days=2), "status": "In progress"},
        {"action": "Update PLN-2026-001 with EXR-2026-003 lessons", "owner": "Plan owner", "due": today + timedelta(days=14), "status": "Draft"},
    ]

    processes[1]["recovery_steps"] = [
        {"seq": 1, "step": "Declare O2C disruption; freeze non-critical order intake if >1h", "role": "ERP Lead", "eta_min": 20},
        {"seq": 2, "step": "Assess JDE LPAR vs SAP PRD — which path is down", "role": "ERP Recovery", "eta_min": 15},
        {"seq": 3, "step": "JDE: warm LPAR failover; validate CUSTMAST + inventory interface", "role": "IBM i Ops", "eta_min": 180},
        {"seq": 4, "step": "SAP: DR landscape activate; Basis validates RFC / IDoc paths", "role": "SAP Basis", "eta_min": 240},
        {"seq": 5, "step": "Top-20 customer manual order path if either stack >4h", "role": "Order Mgmt", "eta_min": 60},
        {"seq": 6, "step": "Payment gateway health check; hold AR posts if ledger lag", "role": "Finance", "eta_min": 30},
    ]
    processes[1]["evidence"] = [
        {"ref": "EVD-BC-002-A", "desc": "EXR-2026-007 JDE LPAR result (Pass 3.2h)", "source": "BC evidence locker"},
        {"ref": "EVD-BC-002-B", "desc": "SAP DR landscape topology diagram", "source": "SAP Basis"},
        {"ref": "EVD-BC-002-C", "desc": "Top-20 manual order workbook", "source": "Order Mgmt"},
        {"ref": "EVD-BC-002-D", "desc": "BIA packet (280 days old — refresh required)", "source": "BCM register"},
        {"ref": "EVD-BC-002-E", "desc": "EXR-2026-005 schedule confirmation", "source": "Change calendar"},
    ]
    processes[1]["open_actions"] = [
        {"action": "Complete BIA refresh (overdue)", "owner": "M. Hassan / BCM", "due": today + timedelta(days=7), "status": "Overdue"},
        {"action": "Execute EXR-2026-005 SAP DR technical failover", "owner": "SAP Basis", "due": today + timedelta(days=18), "status": "Scheduled"},
        {"action": "Finalize PLN-2026-002 v2.0 approval after BIA + exercise", "owner": "ERP Finance", "due": today + timedelta(days=30), "status": "Blocked"},
        {"action": "IFS DR checklist item from INC-2026-005", "owner": "IBM i Ops", "due": today + timedelta(days=10), "status": "In progress"},
    ]

    processes[3]["recovery_steps"] = [
        {"seq": 1, "step": "Activate supplier continuity plan; open #incident-009 / TPRM bridge", "role": "GRC / Payroll", "eta_min": 15},
        {"seq": 2, "step": "Rotate API / SSO / SFTP credentials (already done under INC-2026-009)", "role": "IAM / Infra", "eta_min": 60},
        {"seq": 3, "step": "Confirm vendor tenant impact + IOC list", "role": "TPRM", "eta_min": 1440},
        {"seq": 4, "step": "If vendor uncleared before pay calendar: run manual payroll workbook", "role": "Payroll Ops", "eta_min": 480},
        {"seq": 5, "step": "Submit ACH NACHA to bank; freeze discretionary deductions if needed", "role": "Treasury", "eta_min": 120},
        {"seq": 6, "step": "Employee / regulator comms per PLN-2026-006 if SSN exposure confirmed", "role": "Legal / HR", "eta_min": 240},
    ]
    processes[3]["evidence"] = [
        {"ref": "EVD-BC-004-A", "desc": "PLN-2026-004 supplier continuity plan v1.1", "source": "BCM"},
        {"ref": "EVD-BC-004-B", "desc": "EXR-2026-006 tabletop after-action", "source": "BC evidence locker"},
        {"ref": "EVD-BC-004-C", "desc": "Manual payroll workbook + NACHA template", "source": "Payroll Ops"},
        {"ref": "EVD-BC-004-D", "desc": "DPA-2024-019 + PayrollCo SOC 2 Type II", "source": "TPRM locker"},
        {"ref": "EVD-BC-004-E", "desc": "INC-2026-009 evidence pack (EVD-009-*)", "source": "IR register"},
        {"ref": "EVD-BC-004-F", "desc": "Payroll suspension notice", "source": "Email — internal"},
    ]
    processes[3]["open_actions"] = [
        {"action": "Vendor IOC + tenant confirmation (INC-2026-009)", "owner": "TPRM", "due": today + timedelta(days=1), "status": "Waiting on vendor"},
        {"action": "Live dry-run of manual payroll before next pay date", "owner": "Payroll Ops", "due": today + timedelta(days=5), "status": "Accelerated"},
        {"action": "GDPR Art. 33 path if exposure confirmed", "owner": "Legal / DPO", "due": today + timedelta(days=2), "status": "Drafting"},
        {"action": "Evaluate alternate payroll processor", "owner": "Procurement / TPRM", "due": today + timedelta(days=14), "status": "Planned"},
        {"action": "Resume SaaS payroll only after vendor clears production", "owner": "Payroll Ops", "due": today + timedelta(days=3), "status": "Blocked on vendor"},
    ]

    df_p = pd.DataFrame(processes)
    df_pl = pd.DataFrame(plans)
    df_e = pd.DataFrame(exercises)

    for col in ("last_bia", "next_bia"):
        df_p[col] = pd.to_datetime(df_p[col], errors="coerce")
    for col in ("last_reviewed", "next_review", "last_exercised"):
        df_pl[col] = pd.to_datetime(df_pl[col], errors="coerce")
    for col in ("scheduled", "completed", "next_due"):
        df_e[col] = pd.to_datetime(df_e[col], errors="coerce")

    return df_p, df_pl, df_e


def _enrich_proc(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["rto_gap_h"] = (out["achievable_rto_h"] - out["rto_h"]).round(1)
    out["has_rto_gap"] = out["rto_gap_h"] > 0
    out["bia_overdue"] = out["next_bia"] < today
    out["days_to_bia"] = (out["next_bia"] - today).dt.days
    return out


def _enrich_plans(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["review_overdue"] = out["next_review"] < today
    out["days_to_review"] = (out["next_review"] - today).dt.days
    out["exercise_age_d"] = (today - out["last_exercised"]).dt.days
    return out


def _enrich_ex(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["is_open"] = out["result"].isin(["Scheduled", "In progress", "Fail"])
    out["is_fail"] = out["result"].eq("Fail")
    out["upcoming"] = out["result"].eq("Scheduled") & (out["scheduled"] <= today + timedelta(days=30))
    return out


def _sync(seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if st.session_state.get("_bcm_seed") != seed or "bcm_proc" not in st.session_state:
        p, pl, e = _sample(seed)
        st.session_state.bcm_proc = p
        st.session_state.bcm_plans = pl
        st.session_state.bcm_ex = e
        st.session_state._bcm_seed = seed
    return st.session_state.bcm_proc, st.session_state.bcm_plans, st.session_state.bcm_ex


def _save_proc(df: pd.DataFrame) -> None:
    st.session_state.bcm_proc = df.reset_index(drop=True)


def _save_plans(df: pd.DataFrame) -> None:
    st.session_state.bcm_plans = df.reset_index(drop=True)


def _save_ex(df: pd.DataFrame) -> None:
    st.session_state.bcm_ex = df.reset_index(drop=True)


def _patch_proc(process_id: str, **fields) -> None:
    df = st.session_state.bcm_proc.copy()
    loc = df.index[df["process_id"] == process_id]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_proc(df)


def _patch_plan(plan_id: str, **fields) -> None:
    df = st.session_state.bcm_plans.copy()
    loc = df.index[df["plan_id"] == plan_id]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_plans(df)


def _patch_ex(exercise_id: str, **fields) -> None:
    df = st.session_state.bcm_ex.copy()
    loc = df.index[df["exercise_id"] == exercise_id]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_ex(df)


def _metrics(proc: pd.DataFrame, plans: pd.DataFrame, ex: pd.DataFrame) -> dict:
    p = _enrich_proc(proc)
    pl = _enrich_plans(plans)
    e = _enrich_ex(ex)
    return {
        "mission": int(p["criticality"].eq("Mission-critical").sum()),
        "rto_gaps": int(p["has_rto_gap"].sum()),
        "bia_overdue": int(p["bia_overdue"].sum()),
        "plan_review_od": int(pl["review_overdue"].sum()),
        "ex_fail": int(e["is_fail"].sum()),
        "ex_upcoming": int(e["upcoming"].sum()),
    }


def _fmt(ts) -> str:
    if ts is None:
        return "—"
    if isinstance(ts, str) and ts.strip() in {"", "—", "NaT", "None"}:
        return "—"
    try:
        if pd.isna(ts):
            return "—"
    except (TypeError, ValueError):
        pass
    try:
        parsed = pd.Timestamp(ts)
        if pd.isna(parsed):
            return "—"
        return parsed.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _process_detail(row: pd.Series, plans: pd.DataFrame, ex: pd.DataFrame, *, expanded: bool = False) -> None:
    st.markdown(f"### {row['process_id']} · {row['title']}")
    a, b, c, d = st.columns(4)
    a.metric("Criticality", row["criticality"])
    b.metric("RTO / Achievable", f"{row['rto_h']:.0f}h / {row['achievable_rto_h']:.0f}h")
    c.metric("RPO / MTPD", f"{row['rpo_h']}h / {row['mtpd_h']:.0f}h")
    gap = row.get("rto_gap_h", row["achievable_rto_h"] - row["rto_h"])
    d.metric("RTO gap", f"{gap:+.1f}h" if gap else "0h")

    c1, c2, c3 = st.columns(3)
    c1.write(f"**Function:** {row['function']}")
    c1.write(f"**Owner:** {row['owner']}")
    c1.write(f"**BIA status:** {row['bia_status']}")
    c1.write(f"**Last / next BIA:** {_fmt(row['last_bia'])} → {_fmt(row['next_bia'])}")
    c2.write(f"**Systems:** {row['systems']}")
    c2.write(f"**Dependencies:** {row['dependencies']}")
    c2.write(f"**Personnel:** {row['personnel']}")
    c3.write(f"**Linked plan:** {row['linked_plan'] or '—'}")
    c3.write(f"**Linked exercise:** {row['linked_exercise'] or '—'}")
    c3.write(f"**Risk / IR refs:** {row['risk_refs'] or '—'}")

    st.markdown("**Recovery strategy**")
    st.write(row["recovery_strategy"])
    st.markdown("**Workarounds**")
    st.write(row["workarounds"])
    if row["gap_notes"]:
        st.markdown("**Gaps**")
        st.warning(row["gap_notes"])

    u1, u2 = st.columns(2)
    u1.write(f"**Upstream:** {row['upstream']}")
    u2.write(f"**Downstream:** {row['downstream']}")

    raw = st.session_state.bcm_proc
    raw_row = raw[raw["process_id"] == row["process_id"]]
    if not raw_row.empty:
        rr = raw_row.iloc[0]
        steps = rr.get("recovery_steps") or []
        evidence = rr.get("evidence") or []
        actions = rr.get("open_actions") or []

        if steps:
            with st.expander(f"Recovery runbook ({len(steps)} steps)", expanded=expanded):
                sdf = pd.DataFrame(steps)
                st.dataframe(sdf, use_container_width=True, hide_index=True)
        if evidence:
            with st.expander(f"Evidence ({len(evidence)})", expanded=expanded):
                st.dataframe(pd.DataFrame(evidence), use_container_width=True, hide_index=True)
        if actions:
            with st.expander(f"Open actions ({len(actions)})", expanded=expanded):
                adf = pd.DataFrame(actions)
                if "due" in adf.columns:
                    adf["due"] = adf["due"].apply(_fmt)
                st.dataframe(adf, use_container_width=True, hide_index=True)

    # Linked plan + exercise summary
    if row["linked_plan"]:
        pl = plans[plans["plan_id"] == row["linked_plan"]]
        if not pl.empty:
            pr = pl.iloc[0]
            with st.expander(f"Plan {pr['plan_id']} · {pr['title']}", expanded=False):
                st.write(f"**Status:** {pr['status']} · v{pr['version']} · Owner: {pr['owner']}")
                st.write(f"**Reviewed:** {_fmt(pr['last_reviewed'])} → next {_fmt(pr['next_review'])}")
                st.write(f"**Last exercised:** {_fmt(pr['last_exercised'])}")
                st.write(f"**Coverage:** {pr['coverage']}")
                st.write(f"**Invoke when:** {pr['invoke_trigger']}")
                if pr["gaps"]:
                    st.write(f"**Plan gaps:** {pr['gaps']}")

    if row["linked_exercise"]:
        er = ex[ex["exercise_id"] == row["linked_exercise"]]
        if not er.empty:
            e = er.iloc[0]
            with st.expander(f"Exercise {e['exercise_id']} · {e['title']} · {e['result']}", expanded=expanded):
                st.write(f"**Type:** {e['exercise_type']} · **Owner:** {e['owner']}")
                st.write(f"**Scheduled / completed:** {_fmt(e['scheduled'])} / {_fmt(e['completed'])}")
                st.write(f"**Objective:** {e['objective']}")
                if e["outcome"]:
                    st.write(f"**Outcome:** {e['outcome']}")
                if e["findings"]:
                    st.write(f"**Findings:** {e['findings']}")
                if e["remediation"]:
                    st.write(f"**Remediation:** {e['remediation']}")


def _proc_actions(row: pd.Series, *, key: str) -> None:
    pid = row["process_id"]
    today = _today()
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("Mark BIA refreshed", key=f"bia_{key}", use_container_width=True):
            _patch_proc(
                pid,
                last_bia=today,
                next_bia=today + timedelta(days=365),
                bia_status="Current",
            )
            st.rerun()
    with a2:
        if row.get("has_rto_gap") and st.button(
            "Accept RTO gap (document)", key=f"gap_{key}", use_container_width=True
        ):
            note = (row.get("gap_notes") or "") + " [Gap accepted pending REM.]"
            _patch_proc(pid, gap_notes=note.strip())
            st.rerun()
    with a3:
        if st.button("Bump criticality ↑", key=f"crit_{key}", use_container_width=True):
            order = CRITICALITY
            idx = order.index(row["criticality"]) if row["criticality"] in order else 1
            if idx > 0:
                _patch_proc(pid, criticality=order[idx - 1])
                st.rerun()


def _queue_proc(
    title: str,
    subset: pd.DataFrame,
    plans: pd.DataFrame,
    ex: pd.DataFrame,
    empty: str,
    key_prefix: str,
) -> None:
    st.markdown(f"**{title} ({len(subset)})**")
    if subset.empty:
        st.info(empty)
        return
    for _, row in subset.iterrows():
        is_featured = row["process_id"] in FEATURED
        gap = f"gap {row['rto_gap_h']:+.0f}h" if row.get("has_rto_gap") else "RTO met"
        label = (
            f"{row['process_id']} · {row['title']} · {row['criticality']} · "
            f"RTO {row['rto_h']:.0f}h · {gap}"
        )
        if is_featured:
            st.markdown("---")
            _process_detail(row, plans, ex, expanded=True)
            _proc_actions(row, key=f"{key_prefix}_{row['process_id']}")
            st.markdown("---")
        else:
            with st.expander(label):
                _process_detail(row, plans, ex)
                _proc_actions(row, key=f"{key_prefix}_{row['process_id']}")


def main() -> None:
    portfolio_skin.page_header(
        title="Business Continuity Management",
        lede="BIA, plans, exercises, and the gaps between objective and achievable. Club demo — not a system of record.",
        kicker="Resilience",
    )

    seed = demo_kit.seed_controls()
    proc, plans, ex = _sync(seed)
    ep = _enrich_proc(proc)
    epl = _enrich_plans(plans)
    eex = _enrich_ex(ex)
    m = _metrics(proc, plans, ex)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    crit_f = st.sidebar.multiselect("Criticality", CRITICALITY, default=CRITICALITY)
    bia_f = st.sidebar.multiselect("BIA status", BIA_STATUS, default=BIA_STATUS)

    filtered = ep[ep["criticality"].isin(crit_f) & ep["bia_status"].isin(bia_f)]

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Mission-critical", m["mission"])
    k2.metric("RTO gaps", m["rto_gaps"])
    k3.metric("BIA overdue", m["bia_overdue"])
    k4.metric("Plans past review", m["plan_review_od"])
    k5.metric("Failed / upcoming ex.", f"{m['ex_fail']} / {m['ex_upcoming']}")

    work, bia_tab, plans_tab, ex_tab, board, intake, export = st.tabs(
        ["Workbench", "BIA register", "Plans", "Exercises", "Status board", "Intake", "Export"]
    )

    with work:
        st.subheader("Continuity workbench")

        gaps = ep[ep["has_rto_gap"]].sort_values("rto_gap_h", ascending=False)
        overdue_bia = ep[ep["bia_overdue"]].sort_values("next_bia")
        fail_ex = eex[eex["is_fail"] | eex["upcoming"]].sort_values("scheduled")
        plan_od = epl[epl["review_overdue"]].sort_values("next_review")

        if m["rto_gaps"]:
            st.warning(f"{m['rto_gaps']} process(es) cannot meet published RTO with current recovery capability.")
        if m["bia_overdue"]:
            st.warning(f"{m['bia_overdue']} BIA(s) past refresh date.")

        # Featured mission-critical first (open)
        featured = ep[ep["process_id"].isin(FEATURED)].sort_values("criticality")
        _queue_proc(
            "Featured — statement of record",
            featured,
            plans,
            ex,
            "No featured processes.",
            "feat",
        )

        other_gaps = gaps[~gaps["process_id"].isin(FEATURED)]
        _queue_proc("Other RTO gaps", other_gaps, plans, ex, "No other RTO gaps.", "gap")
        other_od = overdue_bia[~overdue_bia["process_id"].isin(FEATURED)]
        _queue_proc("Other overdue BIAs", other_od, plans, ex, "No other overdue BIAs.", "obia")

        st.markdown("**Exercises needing attention**")
        if fail_ex.empty:
            st.info("No failed or upcoming exercises in the next 30 days.")
        else:
            for _, row in fail_ex.iterrows():
                with st.expander(
                    f"{row['exercise_id']} · {row['title']} · {row['result']} · {_fmt(row['scheduled'])}"
                ):
                    st.write(f"**Plan:** {row['plan_id']} · **Processes:** {row['process_ids']}")
                    st.write(f"**Objective:** {row['objective']}")
                    if row["outcome"]:
                        st.write(f"**Outcome:** {row['outcome']}")
                    if row["findings"]:
                        st.write(f"**Findings:** {row['findings']}")
                    if row["remediation"]:
                        st.write(f"**Remediation:** {row['remediation']}")
                    b1, b2 = st.columns(2)
                    with b1:
                        if row["result"] == "Scheduled" and st.button(
                            "Mark in progress", key=f"exip_{row['exercise_id']}"
                        ):
                            _patch_ex(row["exercise_id"], result="In progress")
                            st.rerun()
                    with b2:
                        if row["result"] in {"Scheduled", "In progress", "Fail"} and st.button(
                            "Record pass w/ findings", key=f"exp_{row['exercise_id']}"
                        ):
                            _patch_ex(
                                row["exercise_id"],
                                result="Pass with findings",
                                completed=_today(),
                            )
                            st.rerun()

        if not plan_od.empty:
            st.markdown("**Plans past review date**")
            show = plan_od[
                ["plan_id", "title", "status", "owner", "next_review", "gaps"]
            ].copy()
            show["next_review"] = show["next_review"].apply(_fmt)
            st.dataframe(show, use_container_width=True, hide_index=True)

    with bia_tab:
        st.subheader("BIA register")
        pick = st.selectbox("Process", filtered["process_id"].tolist() if len(filtered) else [])
        if pick:
            row = ep[ep["process_id"] == pick].iloc[0]
            _process_detail(row, plans, ex, expanded=True)
            _proc_actions(row, key=f"bia_{pick}")
        st.markdown("**Register**")
        show = filtered[
            [
                "process_id",
                "title",
                "criticality",
                "rto_h",
                "achievable_rto_h",
                "rpo_h",
                "mtpd_h",
                "bia_status",
                "next_bia",
                "owner",
            ]
        ].copy()
        show["next_bia"] = show["next_bia"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

    with plans_tab:
        st.subheader("BC / DR plans")
        for _, pr in epl.iterrows():
            flag = " · REVIEW OVERDUE" if pr["review_overdue"] else ""
            with st.expander(f"{pr['plan_id']} · {pr['title']} · {pr['status']}{flag}"):
                c1, c2 = st.columns(2)
                c1.write(f"**Type:** {pr['plan_type']} · **Version:** {pr['version']}")
                c1.write(f"**Owner:** {pr['owner']}")
                c1.write(f"**Processes:** {pr['linked_processes']}")
                c2.write(f"**Reviewed:** {_fmt(pr['last_reviewed'])} → {_fmt(pr['next_review'])}")
                c2.write(f"**Last exercised:** {_fmt(pr['last_exercised'])} ({pr['exercise_age_d']}d ago)")
                st.write(f"**Coverage:** {pr['coverage']}")
                st.write(f"**Invoke when:** {pr['invoke_trigger']}")
                if pr["gaps"]:
                    st.warning(pr["gaps"])
                if pr["review_overdue"] and st.button(
                    "Complete review", key=f"prv_{pr['plan_id']}"
                ):
                    _patch_plan(
                        pr["plan_id"],
                        last_reviewed=_today(),
                        next_review=_today() + timedelta(days=180),
                        status="Approved",
                    )
                    st.rerun()

    with ex_tab:
        st.subheader("Exercises & tests")
        show = eex.copy()
        for col in ("scheduled", "completed", "next_due"):
            show[col] = show[col].apply(_fmt)
        st.dataframe(
            show[
                [
                    "exercise_id",
                    "title",
                    "exercise_type",
                    "plan_id",
                    "process_ids",
                    "result",
                    "scheduled",
                    "completed",
                    "duration_h",
                    "owner",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
        eid = st.selectbox("Exercise detail", eex["exercise_id"].tolist())
        e = eex[eex["exercise_id"] == eid].iloc[0]
        st.markdown(f"#### {e['exercise_id']} · {e['title']}")
        st.write(f"**Result:** {e['result']} · **Type:** {e['exercise_type']}")
        st.write(f"**Objective:** {e['objective']}")
        if e["outcome"]:
            st.write(f"**Outcome:** {e['outcome']}")
        if e["findings"]:
            st.write(f"**Findings:** {e['findings']}")
        if e["remediation"]:
            st.write(f"**Remediation:** {e['remediation']}")

    with board:
        st.subheader("Status board")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.scatter(
                ep,
                x="rto_h",
                y="achievable_rto_h",
                color="criticality",
                size="mtpd_h",
                hover_name="process_id",
                hover_data=["title", "owner"],
                title="Objective RTO vs achievable",
                category_orders={"criticality": CRITICALITY},
            )
            fig.add_shape(
                type="line",
                x0=0,
                y0=0,
                x1=float(ep["rto_h"].max()) + 2,
                y1=float(ep["rto_h"].max()) + 2,
                line=dict(dash="dash", color="#91aa9b"),
            )
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            crit_counts = (
                ep["criticality"]
                .value_counts()
                .reindex(CRITICALITY)
                .fillna(0)
                .rename_axis("criticality")
                .reset_index(name="count")
            )
            fig = px.bar(crit_counts, x="criticality", y="count", title="Processes by criticality")
            st.plotly_chart(fig, use_container_width=True)

        fig = px.bar(
            ep.sort_values("rto_gap_h", ascending=False),
            x="process_id",
            y="rto_gap_h",
            color="criticality",
            hover_data=["title"],
            title="RTO gap (achievable − objective, hours)",
            category_orders={"criticality": CRITICALITY},
        )
        st.plotly_chart(fig, use_container_width=True)

        res_counts = eex["result"].value_counts().rename_axis("result").reset_index(name="count")
        fig = px.bar(res_counts, x="result", y="count", title="Exercise results")
        st.plotly_chart(fig, use_container_width=True)

    with intake:
        st.subheader("Add BIA / process")
        with st.form("intake_bia"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Process title")
                function = st.text_input("Business function", placeholder="e.g. Finance / Treasury")
                owner = st.text_input("Owner")
                criticality = st.selectbox("Criticality", CRITICALITY, index=1)
            with c2:
                rto_h = st.number_input("RTO (hours)", 0.5, 168.0, 8.0)
                rpo_h = st.number_input("RPO (hours)", 0.1, 168.0, 1.0)
                mtpd_h = st.number_input("MTPD (hours)", 1.0, 720.0, 24.0)
                achievable = st.number_input("Achievable RTO (hours)", 0.5, 168.0, 8.0)
            systems = st.text_input("Systems")
            strategy = st.text_area("Recovery strategy")
            if st.form_submit_button("Create BIA entry"):
                if not title.strip() or not owner.strip():
                    st.error("Title and owner are required.")
                else:
                    n = len(st.session_state.bcm_proc) + 1
                    today = _today()
                    add = {
                        "process_id": f"BIA-2026-{n:03d}",
                        "title": title.strip(),
                        "function": function.strip() or "TBD",
                        "owner": owner.strip(),
                        "criticality": criticality,
                        "rto_h": float(rto_h),
                        "rpo_h": float(rpo_h),
                        "mtpd_h": float(mtpd_h),
                        "achievable_rto_h": float(achievable),
                        "bia_status": "Draft",
                        "last_bia": today,
                        "next_bia": today + timedelta(days=365),
                        "systems": systems.strip() or "TBD",
                        "dependencies": "TBD",
                        "recovery_strategy": strategy.strip() or "TBD",
                        "upstream": "",
                        "downstream": "",
                        "personnel": "",
                        "workarounds": "",
                        "gap_notes": "",
                        "linked_plan": "",
                        "linked_exercise": "",
                        "risk_refs": "",
                        "notes": "",
                        "recovery_steps": [],
                        "evidence": [],
                        "open_actions": [],
                    }
                    _save_proc(
                        pd.concat([st.session_state.bcm_proc, pd.DataFrame([add])], ignore_index=True)
                    )
                    st.success(f"BIA-2026-{n:03d} created.")
                    st.rerun()

        st.subheader("Schedule exercise")
        with st.form("intake_ex"):
            title = st.text_input("Exercise title", key="ex_title")
            etype = st.selectbox("Type", EXERCISE_TYPES)
            plan_id = st.selectbox("Plan", plans["plan_id"].tolist())
            process_ids = st.text_input("Process IDs", placeholder="BIA-2026-001")
            when = st.date_input("Scheduled date", value=_today().date() + timedelta(days=30))
            if st.form_submit_button("Schedule"):
                if not title.strip():
                    st.error("Title required.")
                else:
                    n = len(st.session_state.bcm_ex) + 1
                    add = {
                        "exercise_id": f"EXR-2026-{n:03d}",
                        "title": title.strip(),
                        "exercise_type": etype,
                        "plan_id": plan_id,
                        "process_ids": process_ids.strip() or "",
                        "owner": "Demo user",
                        "scheduled": pd.Timestamp(when),
                        "completed": pd.NaT,
                        "result": "Scheduled",
                        "duration_h": 0,
                        "participants": 0,
                        "objective": "",
                        "outcome": "",
                        "findings": "",
                        "remediation": "",
                        "next_due": pd.Timestamp(when),
                    }
                    _save_ex(
                        pd.concat([st.session_state.bcm_ex, pd.DataFrame([add])], ignore_index=True)
                    )
                    st.success(f"EXR-2026-{n:03d} scheduled.")
                    st.rerun()

    with export:
        st.subheader("Export")
        out_p = filtered.copy()
        for col in ("last_bia", "next_bia"):
            out_p[col] = out_p[col].apply(_fmt)
        for col in ("recovery_steps", "evidence", "open_actions"):
            if col in out_p.columns:
                out_p = out_p.drop(columns=[col])
        demo_kit.csv_download(out_p, "bia_register.csv", label="Download BIA register")

        out_pl = epl.copy()
        for col in ("last_reviewed", "next_review", "last_exercised"):
            out_pl[col] = out_pl[col].apply(_fmt)
        demo_kit.csv_download(out_pl, "bc_plans.csv", label="Download plans", key="plans_csv")

        out_e = eex.copy()
        for col in ("scheduled", "completed", "next_due"):
            out_e[col] = out_e[col].apply(_fmt)
        demo_kit.csv_download(out_e, "bc_exercises.csv", label="Download exercises", key="ex_csv")
        st.caption("Resample rebuilds the demo set. Edits live in this browser session only.")


if __name__ == "__main__":
    main()
