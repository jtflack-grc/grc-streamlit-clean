#!/usr/bin/env python3
"""Third-party risk workbench — club teaching toy."""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Third-Party Risk Management · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

TIERS = ["Tier 1 — Critical", "Tier 2 — High", "Tier 3 — Medium", "Tier 4 — Low"]
LIFECYCLE = ["Intake", "Diligence", "Active", "Remediation", "Offboarding", "Terminated"]
ASSURANCE = ["HITRUST r2", "HITRUST i1", "SOC 2 Type II", "ISO 27001", "SIG Lite", "Questionnaire only", "None on file"]
ISSUE_STATUS = ["Open", "With vendor", "Accepted risk", "Closed"]

FEATURED = {"VND-2026-001", "VND-2026-002", "VND-2026-003"}
QUESTIONNAIRE_VENDOR = "VND-2026-003"  # Orbit AMS — dense SIG-Lite demo


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _orbit_sig_lite() -> dict:
    """Faux modern SIG-Lite / CAIQ-energy questionnaire for Orbit AMS."""
    return {
        "instrument": "SIG Lite (customized) · AMS / privileged ops addendum",
        "vendor_id": QUESTIONNAIRE_VENDOR,
        "vendor_name": "Orbit AMS (JD Edwards)",
        "assessment_id": "ASM-2026-003",
        "submitted": "2026-06-12",
        "analyst": "A. Nguyen",
        "review_status": "Partial — insufficient on privileged access & IFS",
        "score_pct": 61,
        "domains_pass": 4,
        "domains_partial": 3,
        "domains_fail": 3,
        "items": [
            {
                "q_id": "AC-01",
                "domain": "Access control",
                "question": "Is access to customer systems granted only via named accounts under MFA, with no shared privileged IDs?",
                "answer": "Yes — all AMS engineers use named IDs. MFA via our IdP for VPN; customer PAM for IBM i sign-on.",
                "evidence": "PAM checkout log sample (redacted); IdP MFA policy screenshot",
                "rating": "Partial",
                "analyst_note": "PAM covers interactive sign-on. Batch / IFS service profiles not evidenced. See ISS-2026-006.",
                "linked_issue": "ISS-2026-006",
            },
            {
                "q_id": "AC-02",
                "domain": "Access control",
                "question": "Are privileged / *ALLOBJ-equivalent authorities time-boxed and logged?",
                "answer": "Privileged work is performed only during approved change windows. Logs retained 90 days.",
                "evidence": "Change calendar excerpt; 'we follow customer PAM'",
                "rating": "Insufficient",
                "analyst_note": "No evidence of *ALLOBJ / special-authority inventory or 90-day log export. Tier-2 AMS requires this.",
                "linked_issue": "ISS-2026-005",
            },
            {
                "q_id": "AC-03",
                "domain": "Access control",
                "question": "Is joiner/mover/leaver for customer-facing staff completed within 24 hours of role change?",
                "answer": "Yes. HR ticket drives AD disable same day; customer access request closed within 24h.",
                "evidence": "JML SOP v1.4; sample ticket",
                "rating": "Adequate",
                "analyst_note": "",
                "linked_issue": "",
            },
            {
                "q_id": "CR-01",
                "domain": "Cryptography",
                "question": "Is data in transit to/from customer environments encrypted (TLS 1.2+)?",
                "answer": "Yes — TLS 1.2 minimum on VPN and SFTP. TLS 1.3 preferred.",
                "evidence": "VPN config export",
                "rating": "Adequate",
                "analyst_note": "",
                "linked_issue": "",
            },
            {
                "q_id": "CR-02",
                "domain": "Cryptography",
                "question": "Are credentials / secrets stored in a vault (not shared spreadsheets or chat)?",
                "answer": "Customer PAM for IBM i. Internal secrets in 1Password Business.",
                "evidence": "1Password org screenshot",
                "rating": "Adequate",
                "analyst_note": "",
                "linked_issue": "",
            },
            {
                "q_id": "IR-01",
                "domain": "Incident response",
                "question": "Will you notify the customer within 24 hours of a suspected security incident affecting their environment?",
                "answer": "Yes — per MSA security addendum, notify security contact within 24 hours.",
                "evidence": "MSA §8.2",
                "rating": "Adequate",
                "analyst_note": "",
                "linked_issue": "",
            },
            {
                "q_id": "IR-02",
                "domain": "Incident response",
                "question": "Do you maintain an IR plan tested at least annually?",
                "answer": "Tabletop annually. Last: 2025-11. Full technical test not applicable (AMS, not SaaS host).",
                "evidence": "Tabletop attendance sheet",
                "rating": "Partial",
                "analyst_note": "Acceptable for AMS model, but customer-impact runbook (who to call, evidence hold) not attached.",
                "linked_issue": "",
            },
            {
                "q_id": "BC-01",
                "domain": "Business continuity",
                "question": "Can AMS services continue if your primary delivery site is unavailable (RTO ≤ 24h)?",
                "answer": "Yes — dual-site staff; remote-first. Offshore L2 can cover.",
                "evidence": "BC one-pager",
                "rating": "Partial",
                "analyst_note": "Relies on offshore L2 — sub-processor notice just received (SIG-008). Concentration risk.",
                "linked_issue": "",
            },
            {
                "q_id": "OP-01",
                "domain": "Operations / change",
                "question": "Are IFS / file-share permission changes peer-reviewed and logged before promotion?",
                "answer": "Changes follow customer CAB. Permission reviews are customer's responsibility.",
                "evidence": "None attached",
                "rating": "Insufficient",
                "analyst_note": "Fails post INC-2026-005. AMS touches IFS; 'customer owns permissions' is not acceptable without dual control. → ISS-2026-006.",
                "linked_issue": "ISS-2026-006",
            },
            {
                "q_id": "OP-02",
                "domain": "Operations / change",
                "question": "Is production change activity prohibited outside approved windows without emergency ticket?",
                "answer": "Yes — emergency path documented.",
                "evidence": "Emergency change SOP",
                "rating": "Adequate",
                "analyst_note": "",
                "linked_issue": "",
            },
            {
                "q_id": "VM-01",
                "domain": "Vulnerability mgmt",
                "question": "Are laptops / jump endpoints used for customer access patched within 14 days for critical CVEs?",
                "answer": "Monthly patch cycle. Critical within 30 days.",
                "evidence": "Intune compliance % screenshot (87%)",
                "rating": "Partial",
                "analyst_note": "30-day critical SLA weaker than our Tier-2 standard (14d). Accept with compensating VPN posture check.",
                "linked_issue": "",
            },
            {
                "q_id": "SP-01",
                "domain": "Subprocessors",
                "question": "List all subprocessors with access to customer systems or data; notify 30 days before add.",
                "answer": "Offshore L2 desk (India). Ticketing SaaS. Will notify on material changes.",
                "evidence": "Subprocessor list v2",
                "rating": "Partial",
                "analyst_note": "New sub-processor notice arrived after this answer (SIG-008). List stale — chase update.",
                "linked_issue": "",
            },
            {
                "q_id": "LG-01",
                "domain": "Logging / monitoring",
                "question": "Are privileged session logs for customer systems retained ≥ 1 year and available to customer on request?",
                "answer": "We retain our side 90 days. Customer PAM is system of record.",
                "evidence": "None",
                "rating": "Insufficient",
                "analyst_note": "For AMS with privileged IBM i access, 90 days on vendor side is thin if PAM gaps exist. Open a dedicated logging retention issue.",
                "linked_issue": "",
            },
            {
                "q_id": "EX-01",
                "domain": "Exit / data return",
                "question": "On contract end, will you certify destruction / return of customer data and revoke all access within 10 business days?",
                "answer": "We will cooperate on access revoke. Data return process not in current MSA.",
                "evidence": "MSA (no exit schedule)",
                "rating": "Insufficient",
                "analyst_note": "Matches ISS-2026-007 — exit clause amendment required.",
                "linked_issue": "ISS-2026-007",
            },
            {
                "q_id": "AS-01",
                "domain": "Assurance",
                "question": "Provide current SOC 2 Type II, ISO 27001, or HITRUST i1/r2 covering services in scope.",
                "answer": "SIG Lite completed. SOC 2 Type II kickoff planned for next FY.",
                "evidence": "Kickoff email (soft date)",
                "rating": "Insufficient",
                "analyst_note": "Core Tier-2 failure. ISS-2026-005.",
                "linked_issue": "ISS-2026-005",
            },
        ],
    }


def _sample(seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    today = _today()
    rng = np.random.default_rng(seed)

    def j(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    vendors = [
        {
            "vendor_id": "VND-2026-001",
            "name": "PayrollCo",
            "service": "Payroll SaaS / tax filing (data processor)",
            "category": "HR / Payroll SaaS",
            "owner": "TPRM · A. Nguyen",
            "business_owner": "Payroll Ops · T. Williams",
            "lifecycle": "Remediation",
            "tier": "Tier 1 — Critical",
            "inherent": "Critical",
            "residual": "High",
            "data_access": "SSN, bank routing/account, salary, tax withholding — 1,820 employees",
            "system_access": "SSO federation · API payroll sync · SFTP tax drop",
            "criticality_note": "Mission-critical on pay calendar (BIA-2026-004). No easy swap mid-cycle.",
            "outside_in": 62,
            "outside_in_trend": "↓ 18 pts (7d)",
            "assurance": "SOC 2 Type II",
            "assurance_period": "2025-01-01 → 2025-12-31",
            "assurance_gap": "Pen-test / scope excluded backup infrastructure — material to INC-2026-009.",
            "dpa": True,
            "security_addendum": True,
            "right_to_audit": True,
            "exit_clause": True,
            "contract_end": today + timedelta(days=210),
            "last_assessment": today - timedelta(days=120),
            "next_assessment": today + timedelta(days=5),
            "fourth_parties": "AWS (backup region) · tax e-file gateway · SMS OTP provider",
            "monitoring_alert": "Vendor breach notification — backup environment; tenant impact unknown",
            "risk_refs": "INC-2026-009 · BIA-2026-004 · DPA-2024-019 · PLN-2026-004",
            "summary": "Active IR: processing suspended, credentials rotated, waiting on IOC/tenant confirmation. Residual elevated until forensics clears our tenant and backup-scope gap is remediated in next SOC 2.",
        },
        {
            "vendor_id": "VND-2026-002",
            "name": "NorthStack Colo (IBM Z)",
            "service": "Managed IBM Z / z/OS colocation, HMC access, LPAR hosting",
            "category": "Colocation / Mainframe",
            "owner": "TPRM · A. Nguyen",
            "business_owner": "Mainframe Security · Maya Chen",
            "lifecycle": "Active",
            "tier": "Tier 1 — Critical",
            "inherent": "Critical",
            "residual": "Medium",
            "data_access": "Production CICS / DB2 workloads; physical + logical access to raised floor",
            "system_access": "HMC · sysplex ops · escorted DC access · break-glass under PAM",
            "criticality_note": "Underpins BIA-2026-001 core ledger. GDPS secondary also hosted here.",
            "outside_in": 78,
            "outside_in_trend": "→ flat",
            "assurance": "SOC 2 Type II",
            "assurance_period": "2025-04-01 → 2026-03-31",
            "assurance_gap": "Two open findings from last diligence: visitor-log retention; HMC MFA exception for console ops.",
            "dpa": False,
            "security_addendum": True,
            "right_to_audit": True,
            "exit_clause": True,
            "contract_end": today + timedelta(days=330),
            "last_assessment": today - timedelta(days=75),
            "next_assessment": today + timedelta(days=290),
            "fourth_parties": "Power utility · cross-connect carrier · tape vault vendor",
            "monitoring_alert": "",
            "risk_refs": "BIA-2026-001 · PLN-2026-001 · EXR-2026-003",
            "summary": "Tier-1 colo. Residual Medium after compensating controls on HMC. Re-test of GDPS path depends on their floor capacity — tied to REM-BC-014 narrative.",
        },
        {
            "vendor_id": "VND-2026-003",
            "name": "Orbit AMS (JD Edwards)",
            "service": "JD Edwards World AMS + IFS operations",
            "category": "Application management",
            "owner": "TPRM · A. Nguyen",
            "business_owner": "ERP Finance · M. Hassan",
            "lifecycle": "Remediation",
            "tier": "Tier 2 — High",
            "inherent": "High",
            "residual": "High",
            "data_access": "JDE World data libraries; IFS paths incl. customer master extracts",
            "system_access": "Privileged IBM i profiles via PAM · IFS NetServer · change windows",
            "criticality_note": "Supports BIA-2026-002 order-to-cash. Privileged ops on PRODBOX.",
            "outside_in": 71,
            "outside_in_trend": "↓ 4 pts (30d)",
            "assurance": "SIG Lite",
            "assurance_period": "2025-06-01 → 2026-05-31",
            "assurance_gap": "No SOC 2. SIG Lite only — insufficient for Tier-2 data processor with *ALLOBJ-adjacent access patterns.",
            "dpa": True,
            "security_addendum": True,
            "right_to_audit": True,
            "exit_clause": False,
            "contract_end": today + timedelta(days=510),
            "last_assessment": today - timedelta(days=50),
            "next_assessment": today + timedelta(days=40),
            "fourth_parties": "Offshore L2 desk (India) · ticketing SaaS",
            "monitoring_alert": "IFS *PUBLIC exposure context (INC-2026-005) — AMS change windows under review",
            "risk_refs": "INC-2026-005 · BIA-2026-002 · EXC IFS *PUBLIC",
            "summary": "High residual until SOC 2 delivered and IFS permission ops proven in DR checklist. Exit clause missing — legal tracking.",
        },
        {
            "vendor_id": "VND-2026-004",
            "name": "Azure AD B2C (Microsoft)",
            "service": "Customer identity (B2C)",
            "category": "Cloud / IdP",
            "owner": "IAM · L. Torres",
            "business_owner": "Platform Eng · R. Kim",
            "lifecycle": "Active",
            "tier": "Tier 1 — Critical",
            "inherent": "Critical",
            "residual": "Low",
            "data_access": "Customer auth identities; email",
            "system_access": "IdP admin · conditional access",
            "criticality_note": "Portal auth path (BIA-2026-003). Post INC-2026-001 MFA rollout in flight.",
            "outside_in": 92,
            "outside_in_trend": "→ flat",
            "assurance": "SOC 2 Type II",
            "assurance_period": "Vendor public trust docs (rolling)",
            "assurance_gap": "",
            "dpa": True,
            "security_addendum": True,
            "right_to_audit": False,
            "exit_clause": True,
            "contract_end": today + timedelta(days=400),
            "last_assessment": today - timedelta(days=200),
            "next_assessment": today + timedelta(days=165),
            "fourth_parties": "—",
            "monitoring_alert": "",
            "risk_refs": "INC-2026-001 · BIA-2026-003",
            "summary": "Hyperscaler — residual Low. Diligence is inheritance + config review, not questionnaire theater.",
        },
        {
            "vendor_id": "VND-2026-005",
            "name": "MailGuard Edge",
            "service": "Secure email gateway",
            "category": "Security tooling",
            "owner": "SecOps · K. Patel",
            "business_owner": "IT Service Desk",
            "lifecycle": "Active",
            "tier": "Tier 2 — High",
            "inherent": "High",
            "residual": "Medium",
            "data_access": "Mail metadata + quarantine content",
            "system_access": "Gateway admin · API",
            "criticality_note": "BEC controls (INC-2026-007). Quarantine release policy dependency.",
            "outside_in": 84,
            "outside_in_trend": "↑ 3 pts",
            "assurance": "ISO 27001",
            "assurance_period": "2025-09-01 → 2026-08-31",
            "assurance_gap": "",
            "dpa": True,
            "security_addendum": True,
            "right_to_audit": True,
            "exit_clause": True,
            "contract_end": today + timedelta(days=280),
            "last_assessment": today - timedelta(days=90),
            "next_assessment": today + timedelta(days=275),
            "fourth_parties": "Threat-intel feed vendor",
            "monitoring_alert": "",
            "risk_refs": "INC-2026-007",
            "summary": "Stable. Next diligence light-touch unless score drops.",
        },
        {
            "vendor_id": "VND-2026-006",
            "name": "PixelForge CMS",
            "service": "Marketing website CMS",
            "category": "Marketing SaaS",
            "owner": "Marketing Ops",
            "business_owner": "Marketing",
            "lifecycle": "Active",
            "tier": "Tier 4 — Low",
            "inherent": "Low",
            "residual": "Low",
            "data_access": "Public web content; form leads (business email)",
            "system_access": "CMS admin",
            "criticality_note": "BIA-2026-008 — Medium process criticality, low data sensitivity.",
            "outside_in": 80,
            "outside_in_trend": "→ flat",
            "assurance": "Questionnaire only",
            "assurance_period": "2026-01 intake",
            "assurance_gap": "",
            "dpa": False,
            "security_addendum": False,
            "right_to_audit": False,
            "exit_clause": True,
            "contract_end": today + timedelta(days=100),
            "last_assessment": today - timedelta(days=200),
            "next_assessment": today + timedelta(days=165),
            "fourth_parties": "CDN",
            "monitoring_alert": "",
            "risk_refs": "BIA-2026-008",
            "summary": "Tier-4 — annual light review. Contract renews soon; no security blockers.",
        },
        {
            "vendor_id": "VND-2026-007",
            "name": "FleetDesk IT Support",
            "service": "Outsourced L1/L2 desk",
            "category": "IT services",
            "owner": "IT Service Desk · A. Nguyen",
            "business_owner": "IT",
            "lifecycle": "Offboarding",
            "tier": "Tier 3 — Medium",
            "inherent": "Medium",
            "residual": "Medium",
            "data_access": "Ticket content; limited AD helpdesk group",
            "system_access": "ITSM · AD helpdesk (removing)",
            "criticality_note": "Contract non-renewal — bringing L1 in-house.",
            "outside_in": 76,
            "outside_in_trend": "→ flat",
            "assurance": "SOC 2 Type II",
            "assurance_period": "2024-07-01 → 2025-06-30 (expired)",
            "assurance_gap": "SOC 2 lapsed during offboarding — acceptable if access fully revoked.",
            "dpa": True,
            "security_addendum": True,
            "right_to_audit": True,
            "exit_clause": True,
            "contract_end": today - timedelta(days=5),
            "last_assessment": today - timedelta(days=400),
            "next_assessment": today - timedelta(days=35),
            "fourth_parties": "Offshore overflow partner",
            "monitoring_alert": "Offboarding checklist incomplete — AD group still has 3 accounts",
            "risk_refs": "",
            "summary": "Offboarding in progress. Blocker: AD helpdesk accounts not revoked. Data return certificate pending.",
        },
        {
            "vendor_id": "VND-2026-008",
            "name": "LedgerLink Payments",
            "service": "Payment gateway",
            "category": "Payments",
            "owner": "Finance · M. Hassan",
            "business_owner": "Treasury",
            "lifecycle": "Diligence",
            "tier": "Tier 1 — Critical",
            "inherent": "Critical",
            "residual": "High",
            "data_access": "PAN (tokenized) · transaction metadata",
            "system_access": "API · webhook to portal / O2C",
            "criticality_note": "Replacement evaluation for aging gateway. PCI scope.",
            "outside_in": 88,
            "outside_in_trend": "→ flat",
            "assurance": "HITRUST i1",
            "assurance_period": "Pending — shared draft report",
            "assurance_gap": "HITRUST i1 in validation; SOC 2 also on file from prior year.",
            "dpa": True,
            "security_addendum": True,
            "right_to_audit": True,
            "exit_clause": True,
            "contract_end": today + timedelta(days=45),
            "last_assessment": pd.NaT,
            "next_assessment": today + timedelta(days=14),
            "fourth_parties": "Card network · tokenization vault",
            "monitoring_alert": "",
            "risk_refs": "BIA-2026-002",
            "summary": "Pre-contract diligence. Tier-1 because of card data + O2C dependency. Waiting on final HITRUST letter.",
        },
    ]

    # Diligence assessments
    assessments = [
        {
            "assessment_id": "ASM-2026-001",
            "vendor_id": "VND-2026-001",
            "title": "Annual diligence + IR-triggered reassess (PayrollCo)",
            "scope": "SOC 2 review · DPA · backup-scope gap · IR evidence pack",
            "status": "In progress",
            "due": today + timedelta(days=5),
            "started": today - timedelta(days=8),
            "assessor": "A. Nguyen",
            "tier_driven": "Full — Tier 1",
            "notes": "Accelerated by INC-2026-009. Cannot close until tenant impact known.",
        },
        {
            "assessment_id": "ASM-2026-002",
            "vendor_id": "VND-2026-002",
            "title": "Periodic Tier-1 colo review",
            "scope": "SOC 2 · physical security · HMC MFA exception · right-to-audit walkthrough",
            "status": "Complete",
            "due": today - timedelta(days=70),
            "started": today - timedelta(days=90),
            "assessor": "A. Nguyen",
            "tier_driven": "Full — Tier 1",
            "notes": "Two findings opened (ISS-2026-003, ISS-2026-004).",
        },
        {
            "assessment_id": "ASM-2026-003",
            "vendor_id": "VND-2026-003",
            "title": "Tier-2 AMS diligence — escalate assurance",
            "scope": "SIG Lite → demand SOC 2 · privileged access · IFS ops · offshore L2",
            "status": "With vendor",
            "due": today + timedelta(days=40),
            "started": today - timedelta(days=50),
            "assessor": "A. Nguyen",
            "tier_driven": "Standard — Tier 2",
            "notes": "Vendor committed to SOC 2 kickoff; timeline soft.",
        },
        {
            "assessment_id": "ASM-2026-004",
            "vendor_id": "VND-2026-008",
            "title": "Pre-contract diligence — LedgerLink",
            "scope": "HITRUST i1 · PCI · DPA · tokenization architecture",
            "status": "In progress",
            "due": today + timedelta(days=14),
            "started": today - timedelta(days=20),
            "assessor": "A. Nguyen",
            "tier_driven": "Full — Tier 1",
            "notes": "Blocked on final HITRUST validated report.",
        },
        {
            "assessment_id": "ASM-2026-005",
            "vendor_id": "VND-2026-007",
            "title": "Offboarding assurance close-out",
            "scope": "Access revoke · data return · cert of destruction",
            "status": "Overdue",
            "due": today - timedelta(days=10),
            "started": today - timedelta(days=30),
            "assessor": "IT / TPRM",
            "tier_driven": "Offboarding",
            "notes": "AD accounts still active.",
        },
        {
            "assessment_id": "ASM-2026-006",
            "vendor_id": "VND-2026-005",
            "title": "Annual light review — MailGuard",
            "scope": "ISO cert check · scorecard · questionnaire delta",
            "status": "Scheduled",
            "due": today + timedelta(days=275),
            "started": pd.NaT,
            "assessor": "SecOps",
            "tier_driven": "Light — Tier 2",
            "notes": "",
        },
    ]

    issues = [
        {
            "issue_id": "ISS-2026-001",
            "vendor_id": "VND-2026-001",
            "title": "Backup-environment breach — tenant impact unknown",
            "severity": "Critical",
            "status": "With vendor",
            "opened": today - timedelta(days=1),
            "due": today + timedelta(days=2),
            "owner": "TPRM / Vendor forensics",
            "source": "INC-2026-009 / monitoring",
            "detail": "Vendor notified unauthorized access to backup env. Need IOC list + confirmation whether our tenant backups were accessed.",
        },
        {
            "issue_id": "ISS-2026-002",
            "vendor_id": "VND-2026-001",
            "title": "SOC 2 scope excludes backup infrastructure",
            "severity": "High",
            "status": "Open",
            "opened": today - timedelta(days=8),
            "due": today + timedelta(days=60),
            "owner": "PayrollCo / TPRM",
            "source": "Assurance review",
            "detail": "Prior SOC 2 pen-test explicitly excluded backup infrastructure. Require scope expansion or compensating evidence.",
        },
        {
            "issue_id": "ISS-2026-003",
            "vendor_id": "VND-2026-002",
            "title": "Visitor-log retention below policy (90d vs 365d)",
            "severity": "Medium",
            "status": "With vendor",
            "opened": today - timedelta(days=70),
            "due": today + timedelta(days=20),
            "owner": "NorthStack",
            "source": "ASM-2026-002",
            "detail": "Physical security finding. Vendor proposed policy change; evidence pending.",
        },
        {
            "issue_id": "ISS-2026-004",
            "vendor_id": "VND-2026-002",
            "title": "HMC console MFA exception",
            "severity": "High",
            "status": "Accepted risk",
            "opened": today - timedelta(days=70),
            "due": today + timedelta(days=180),
            "owner": "Maya Chen / NorthStack",
            "source": "ASM-2026-002",
            "detail": "Time-boxed acceptance with escort + PAM logging. Revisit at next Tier-1 review.",
        },
        {
            "issue_id": "ISS-2026-005",
            "vendor_id": "VND-2026-003",
            "title": "Assurance below tier — SIG Lite only",
            "severity": "High",
            "status": "With vendor",
            "opened": today - timedelta(days=45),
            "due": today + timedelta(days=90),
            "owner": "Orbit AMS",
            "source": "ASM-2026-003",
            "detail": "Tier-2 with privileged IBM i access requires SOC 2 Type II (or HITRUST i1) within 90 days.",
        },
        {
            "issue_id": "ISS-2026-006",
            "vendor_id": "VND-2026-003",
            "title": "IFS permission ops not evidenced in change process",
            "severity": "High",
            "status": "Open",
            "opened": today - timedelta(days=7),
            "due": today + timedelta(days=21),
            "owner": "Orbit AMS / IBM i Ops",
            "source": "INC-2026-005",
            "detail": "Anonymous IFS share context. AMS must show permission review in every change touching IFS.",
        },
        {
            "issue_id": "ISS-2026-007",
            "vendor_id": "VND-2026-003",
            "title": "MSA missing exit / data-return clause",
            "severity": "Medium",
            "status": "Open",
            "opened": today - timedelta(days=40),
            "due": today + timedelta(days=45),
            "owner": "Legal / Procurement",
            "source": "Contract review",
            "detail": "Amendment in flight.",
        },
        {
            "issue_id": "ISS-2026-008",
            "vendor_id": "VND-2026-007",
            "title": "Offboarding — AD helpdesk accounts still active",
            "severity": "High",
            "status": "Open",
            "opened": today - timedelta(days=12),
            "due": today - timedelta(days=2),
            "owner": "IAM",
            "source": "Offboarding checklist",
            "detail": "3 accounts in AD helpdesk group. Contract ended. Overdue revoke.",
        },
        {
            "issue_id": "ISS-2026-009",
            "vendor_id": "VND-2026-007",
            "title": "Certificate of data destruction pending",
            "severity": "Medium",
            "status": "With vendor",
            "opened": today - timedelta(days=5),
            "due": today + timedelta(days=10),
            "owner": "FleetDesk",
            "source": "Offboarding",
            "detail": "Vendor drafting CoD for ticket archives containing employee PII fragments.",
        },
    ]

    signals = [
        {"signal_id": "SIG-001", "vendor_id": "VND-2026-001", "detected": today - timedelta(hours=10), "severity": "Critical", "signal": "Breach notification email — backup environment", "status": "Open", "action": "Linked to INC-2026-009 / ISS-2026-001"},
        {"signal_id": "SIG-002", "vendor_id": "VND-2026-001", "detected": today - timedelta(days=2), "severity": "High", "signal": "Outside-in score drop 80 → 62", "status": "Open", "action": "Triggered reassessment ASM-2026-001"},
        {"signal_id": "SIG-003", "vendor_id": "VND-2026-003", "detected": today - timedelta(days=7), "severity": "High", "signal": "Related IR: IFS anonymous share (INC-2026-005)", "status": "Open", "action": "ISS-2026-006 opened"},
        {"signal_id": "SIG-004", "vendor_id": "VND-2026-007", "detected": today - timedelta(days=5), "severity": "Medium", "signal": "Contract end date passed — offboarding SLA clock", "status": "Open", "action": "Checklist incomplete"},
        {"signal_id": "SIG-005", "vendor_id": "VND-2026-002", "detected": today - timedelta(days=15), "severity": "Low", "signal": "SOC 2 period ends in ~220 days — schedule bridge letter", "status": "Watch", "action": "Calendar reminder"},
        {"signal_id": "SIG-006", "vendor_id": "VND-2026-008", "detected": today - timedelta(days=3), "severity": "Medium", "signal": "HITRUST i1 validation still pending past vendor ETA", "status": "Open", "action": "Chase in ASM-2026-004"},
        {"signal_id": "SIG-007", "vendor_id": "VND-2026-005", "detected": today - timedelta(days=20), "severity": "Low", "signal": "Outside-in +3 pts", "status": "Closed", "action": "No action"},
        {"signal_id": "SIG-008", "vendor_id": "VND-2026-003", "detected": today - timedelta(days=1), "severity": "Medium", "signal": "Fourth-party: offshore L2 desk — new sub-processor notice", "status": "Open", "action": "Review DPA sub-processor list"},
    ]

    df_v = pd.DataFrame(vendors)
    df_a = pd.DataFrame(assessments)
    df_i = pd.DataFrame(issues)
    df_s = pd.DataFrame(signals)

    for col in ("contract_end", "last_assessment", "next_assessment"):
        df_v[col] = pd.to_datetime(df_v[col], errors="coerce")
    for col in ("due", "started"):
        df_a[col] = pd.to_datetime(df_a[col], errors="coerce")
    for col in ("opened", "due"):
        df_i[col] = pd.to_datetime(df_i[col], errors="coerce")
    df_s["detected"] = pd.to_datetime(df_s["detected"], errors="coerce")

    # Featured deep packs
    for v in vendors:
        v.setdefault("diligence_steps", [])
        v.setdefault("evidence", [])
        v.setdefault("open_actions", [])

    # Attach via session rebuild — store as columns on dataframe by merging from lists
    deep = {
        "VND-2026-001": {
            "diligence_steps": [
                {"seq": 1, "step": "Confirm DPA + breach-notification clause (Art. 33 path)", "status": "Done"},
                {"seq": 2, "step": "Rotate API / SSO / SFTP (IR containment)", "status": "Done"},
                {"seq": 3, "step": "Obtain IOC list + tenant-impact letter", "status": "Waiting"},
                {"seq": 4, "step": "Review SOC 2; document backup-scope gap", "status": "Done"},
                {"seq": 5, "step": "Residual decision: continue / exit / accept with conditions", "status": "Blocked"},
                {"seq": 6, "step": "Update BIA-2026-004 / PLN-2026-004 with TPRM outcome", "status": "Pending"},
            ],
            "evidence": [
                {"ref": "EVD-T-001-A", "desc": "Vendor breach notification", "source": "Email"},
                {"ref": "EVD-T-001-B", "desc": "DPA-2024-019", "source": "Contracts"},
                {"ref": "EVD-T-001-C", "desc": "SOC 2 Type II (Dec 2025)", "source": "TPRM locker"},
                {"ref": "EVD-T-001-D", "desc": "Credential rotation logs", "source": "IR / IAM"},
                {"ref": "EVD-T-001-E", "desc": "DPA 8.3 inquiry", "source": "Legal"},
            ],
            "open_actions": [
                {"action": "Tenant impact + IOC from vendor", "owner": "TPRM", "due": today + timedelta(days=1), "status": "Waiting"},
                {"action": "SOC 2 scope expansion commitment", "owner": "PayrollCo", "due": today + timedelta(days=60), "status": "Open"},
                {"action": "Alternate processor evaluation", "owner": "Procurement", "due": today + timedelta(days=14), "status": "Planned"},
            ],
        },
        "VND-2026-002": {
            "diligence_steps": [
                {"seq": 1, "step": "SOC 2 Type II review", "status": "Done"},
                {"seq": 2, "step": "Physical / visitor controls sample", "status": "Done"},
                {"seq": 3, "step": "HMC access + MFA exception review", "status": "Done"},
                {"seq": 4, "step": "Right-to-audit clause confirmation", "status": "Done"},
                {"seq": 5, "step": "Close or accept open findings", "status": "In progress"},
            ],
            "evidence": [
                {"ref": "EVD-T-002-A", "desc": "SOC 2 Type II", "source": "TPRM locker"},
                {"ref": "EVD-T-002-B", "desc": "Colo physical security addendum", "source": "Contracts"},
                {"ref": "EVD-T-002-C", "desc": "HMC MFA exception memo", "source": "Mainframe Security"},
            ],
            "open_actions": [
                {"action": "Visitor-log retention evidence", "owner": "NorthStack", "due": today + timedelta(days=20), "status": "With vendor"},
                {"action": "Revisit HMC MFA acceptance", "owner": "Maya Chen", "due": today + timedelta(days=180), "status": "Accepted risk"},
            ],
        },
        "VND-2026-003": {
            "diligence_steps": [
                {"seq": 1, "step": "SIG Lite intake", "status": "Done"},
                {"seq": 2, "step": "Demand SOC 2 / HITRUST for Tier-2 privileged AMS", "status": "In progress"},
                {"seq": 3, "step": "Offshore L2 / sub-processor review", "status": "In progress"},
                {"seq": 4, "step": "IFS change-control evidence post INC-2026-005", "status": "Open"},
                {"seq": 5, "step": "MSA exit clause amendment", "status": "Open"},
            ],
            "evidence": [
                {"ref": "EVD-T-003-A", "desc": "SIG Lite responses", "source": "TPRM"},
                {"ref": "EVD-T-003-B", "desc": "Privileged access listing (PAM)", "source": "IAM"},
                {"ref": "EVD-T-003-C", "desc": "INC-2026-005 IR summary", "source": "IR"},
            ],
            "open_actions": [
                {"action": "SOC 2 kickoff letter from vendor", "owner": "Orbit AMS", "due": today + timedelta(days=30), "status": "With vendor"},
                {"action": "IFS permission review in AMS SOP", "owner": "Orbit / IBM i Ops", "due": today + timedelta(days=21), "status": "Open"},
                {"action": "Exit clause amendment", "owner": "Legal", "due": today + timedelta(days=45), "status": "Open"},
            ],
        },
    }

    df_v["diligence_steps"] = df_v["vendor_id"].map(lambda i: deep.get(i, {}).get("diligence_steps", []))
    df_v["evidence"] = df_v["vendor_id"].map(lambda i: deep.get(i, {}).get("evidence", []))
    df_v["open_actions"] = df_v["vendor_id"].map(lambda i: deep.get(i, {}).get("open_actions", []))

    return df_v, df_a, df_i, df_s


def _enrich_v(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["assess_overdue"] = out["next_assessment"].notna() & (out["next_assessment"] < today)
    out["has_alert"] = out["monitoring_alert"].fillna("").astype(str).str.len() > 0
    out["tier1"] = out["tier"].str.startswith("Tier 1")
    return out


def _sync(seed: int):
    if st.session_state.get("_tprm_seed") != seed or "tprm_vendors" not in st.session_state:
        v, a, i, s = _sample(seed)
        st.session_state.tprm_vendors = v
        st.session_state.tprm_asm = a
        st.session_state.tprm_issues = i
        st.session_state.tprm_signals = s
        st.session_state.tprm_questionnaire = _orbit_sig_lite()
        st.session_state._tprm_seed = seed
    if "tprm_questionnaire" not in st.session_state:
        st.session_state.tprm_questionnaire = _orbit_sig_lite()
    return (
        st.session_state.tprm_vendors,
        st.session_state.tprm_asm,
        st.session_state.tprm_issues,
        st.session_state.tprm_signals,
    )


def _save_v(df):
    st.session_state.tprm_vendors = df.reset_index(drop=True)


def _save_a(df):
    st.session_state.tprm_asm = df.reset_index(drop=True)


def _save_i(df):
    st.session_state.tprm_issues = df.reset_index(drop=True)


def _patch_v(vid, **fields):
    df = st.session_state.tprm_vendors.copy()
    loc = df.index[df["vendor_id"] == vid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_v(df)


def _patch_a(aid, **fields):
    df = st.session_state.tprm_asm.copy()
    loc = df.index[df["assessment_id"] == aid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_a(df)


def _patch_i(iid, **fields):
    df = st.session_state.tprm_issues.copy()
    loc = df.index[df["issue_id"] == iid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_i(df)


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
        p = pd.Timestamp(ts)
        if pd.isna(p):
            return "—"
        return p.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _metrics(v, a, i, s):
    ev = _enrich_v(v)
    open_issues = i[~i["status"].isin(["Closed", "Accepted risk"])]
    return {
        "tier1": int(ev["tier1"].sum()),
        "alerts": int(ev["has_alert"].sum()),
        "asm_hot": int(a["status"].isin(["Overdue", "In progress", "With vendor"]).sum()),
        "issues_open": int(len(open_issues)),
        "offboard": int(ev["lifecycle"].eq("Offboarding").sum()),
    }


def _render_questionnaire(*, expanded: bool = False, key_prefix: str = "q") -> None:
    q = st.session_state.get("tprm_questionnaire") or _orbit_sig_lite()
    items = q["items"]
    n_fail = sum(1 for x in items if x["rating"] == "Insufficient")
    n_part = sum(1 for x in items if x["rating"] == "Partial")
    n_ok = sum(1 for x in items if x["rating"] == "Adequate")

    with st.expander(
        f"Questionnaire · {q['instrument']} · {q['score_pct']}% · "
        f"{n_fail} insufficient / {n_part} partial / {n_ok} adequate",
        expanded=expanded,
    ):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Score", f"{q['score_pct']}%")
        m2.metric("Insufficient", n_fail)
        m3.metric("Partial", n_part)
        m4.metric("Review", q["review_status"].split("—")[0].strip())
        st.caption(
            f"Submitted {q['submitted']} · Assessor {q['analyst']} · "
            f"Linked assessment {q['assessment_id']}"
        )
        st.write(f"**Status:** {q['review_status']}")

        # Domain rollup
        dom = {}
        for it in items:
            d = it["domain"]
            dom.setdefault(d, {"Adequate": 0, "Partial": 0, "Insufficient": 0})
            dom[d][it["rating"]] = dom[d].get(it["rating"], 0) + 1
        roll = pd.DataFrame(
            [{"domain": k, **v} for k, v in dom.items()]
        )
        st.dataframe(roll, use_container_width=True, hide_index=True)

        show_f = st.checkbox(
            "Show insufficient / partial only",
            value=True,
            key=f"{key_prefix}_filter_fail",
        )
        view = [
            x
            for x in items
            if (not show_f) or x["rating"] in {"Insufficient", "Partial"}
        ]

        for it in view:
            badge = it["rating"]
            title = f"{it['q_id']} · {it['domain']} · {badge}"
            with st.container():
                st.markdown(f"**{title}**")
                st.write(it["question"])
                st.write(f"**Vendor:** {it['answer']}")
                st.caption(f"Evidence cited: {it['evidence']}")
                if it["analyst_note"]:
                    if badge == "Insufficient":
                        st.error(f"Analyst: {it['analyst_note']}")
                    else:
                        st.warning(f"Analyst: {it['analyst_note']}")
                if it["linked_issue"]:
                    st.caption(f"→ {it['linked_issue']}")
                st.markdown("---")

        orphans = [x for x in items if x["rating"] == "Insufficient" and not x["linked_issue"]]
        if orphans:
            st.markdown("**Open issue from questionnaire**")
            pick = st.selectbox(
                "Insufficient item",
                [f"{x['q_id']} — {x['question'][:60]}…" for x in orphans],
                key=f"{key_prefix}_orphan_pick",
            )
            if st.button("Create issue from selection", key=f"{key_prefix}_mk_issue"):
                qid = pick.split(" — ")[0]
                src = next(x for x in orphans if x["q_id"] == qid)
                n = len(st.session_state.tprm_issues) + 1
                iid = f"ISS-2026-{n:03d}"
                add = {
                    "issue_id": iid,
                    "vendor_id": QUESTIONNAIRE_VENDOR,
                    "title": f"Questionnaire {qid}: {src['domain']} insufficient",
                    "severity": "High",
                    "status": "Open",
                    "opened": _today(),
                    "due": _today() + timedelta(days=30),
                    "owner": "Orbit AMS / TPRM",
                    "source": f"SIG Lite · {qid}",
                    "detail": f"Q: {src['question']}\nA: {src['answer']}\nAnalyst: {src['analyst_note']}",
                }
                _save_i(
                    pd.concat(
                        [st.session_state.tprm_issues, pd.DataFrame([add])],
                        ignore_index=True,
                    )
                )
                for x in st.session_state.tprm_questionnaire["items"]:
                    if x["q_id"] == qid:
                        x["linked_issue"] = iid
                st.success(f"{iid} opened from {qid}.")
                st.rerun()


def _vendor_detail(row, asm, issues, signals, *, expanded=False):
    st.markdown(f"### {row['vendor_id']} · {row['name']}")
    a, b, c, d = st.columns(4)
    a.metric("Tier", row["tier"].split("—")[0].strip())
    b.metric("Inherent → Residual", f"{row['inherent']} → {row['residual']}")
    c.metric("Outside-in", f"{int(row['outside_in'])}  {row['outside_in_trend']}")
    d.metric("Lifecycle", row["lifecycle"])

    c1, c2, c3 = st.columns(3)
    c1.write(f"**Service:** {row['service']}")
    c1.write(f"**Category:** {row['category']}")
    c1.write(f"**TPRM owner:** {row['owner']}")
    c1.write(f"**Business owner:** {row['business_owner']}")
    c2.write(f"**Data access:** {row['data_access']}")
    c2.write(f"**System access:** {row['system_access']}")
    c2.write(f"**Criticality:** {row['criticality_note']}")
    c3.write(f"**Assurance:** {row['assurance']}")
    c3.write(f"**Period:** {row['assurance_period']}")
    c3.write(f"**Next assessment:** {_fmt(row['next_assessment'])}")
    c3.write(f"**Contract end:** {_fmt(row['contract_end'])}")

    flags = []
    if row["dpa"]:
        flags.append("DPA")
    if row["security_addendum"]:
        flags.append("Security addendum")
    if row["right_to_audit"]:
        flags.append("Right to audit")
    if row["exit_clause"]:
        flags.append("Exit clause")
    st.caption("Contract flags: " + (", ".join(flags) if flags else "none"))

    st.write(row["summary"])
    if row["assurance_gap"]:
        st.warning(f"Assurance gap: {row['assurance_gap']}")
    if row["monitoring_alert"]:
        st.error(f"Monitoring: {row['monitoring_alert']}")
    if row["fourth_parties"] and row["fourth_parties"] != "—":
        st.write(f"**Fourth parties / concentration:** {row['fourth_parties']}")
    if row["risk_refs"]:
        st.caption(f"Linked: {row['risk_refs']}")

    if row["vendor_id"] == QUESTIONNAIRE_VENDOR:
        _render_questionnaire(expanded=expanded, key_prefix=f"vq_{row['vendor_id']}")

    raw = st.session_state.tprm_vendors
    rr = raw[raw["vendor_id"] == row["vendor_id"]]
    if not rr.empty:
        r0 = rr.iloc[0]
        steps = r0.get("diligence_steps") or []
        evid = r0.get("evidence") or []
        acts = r0.get("open_actions") or []
        if steps:
            with st.expander(f"Diligence checklist ({len(steps)})", expanded=expanded):
                st.dataframe(pd.DataFrame(steps), use_container_width=True, hide_index=True)
        if evid:
            with st.expander(f"Evidence ({len(evid)})", expanded=expanded):
                st.dataframe(pd.DataFrame(evid), use_container_width=True, hide_index=True)
        if acts:
            with st.expander(f"Open actions ({len(acts)})", expanded=expanded):
                adf = pd.DataFrame(acts)
                if "due" in adf.columns:
                    adf["due"] = adf["due"].apply(_fmt)
                st.dataframe(adf, use_container_width=True, hide_index=True)

    va = asm[asm["vendor_id"] == row["vendor_id"]]
    vi = issues[issues["vendor_id"] == row["vendor_id"]]
    vs = signals[signals["vendor_id"] == row["vendor_id"]]

    with st.expander(f"Assessments ({len(va)})", expanded=False):
        if va.empty:
            st.info("None.")
        else:
            show = va.copy()
            show["due"] = show["due"].apply(_fmt)
            show["started"] = show["started"].apply(_fmt)
            st.dataframe(
                show[["assessment_id", "title", "status", "tier_driven", "due", "assessor"]],
                use_container_width=True,
                hide_index=True,
            )

    with st.expander(f"Issues ({len(vi)})", expanded=expanded):
        if vi.empty:
            st.info("None.")
        else:
            show = vi.copy()
            show["opened"] = show["opened"].apply(_fmt)
            show["due"] = show["due"].apply(_fmt)
            st.dataframe(
                show[["issue_id", "title", "severity", "status", "due", "owner"]],
                use_container_width=True,
                hide_index=True,
            )

    with st.expander(f"Monitoring signals ({len(vs)})", expanded=False):
        if vs.empty:
            st.info("None.")
        else:
            show = vs.copy()
            show["detected"] = show["detected"].apply(_fmt)
            st.dataframe(
                show[["signal_id", "detected", "severity", "signal", "status", "action"]],
                use_container_width=True,
                hide_index=True,
            )


def _vendor_actions(row, *, key: str):
    vid = row["vendor_id"]
    a1, a2, a3 = st.columns(3)
    with a1:
        if row["lifecycle"] not in {"Terminated"} and st.button(
            "Mark residual Medium", key=f"res_{key}", use_container_width=True
        ):
            _patch_v(vid, residual="Medium", monitoring_alert="")
            st.rerun()
    with a2:
        if row["lifecycle"] == "Diligence" and st.button(
            "Approve → Active", key=f"act_{key}", use_container_width=True
        ):
            _patch_v(vid, lifecycle="Active", residual="Medium")
            st.rerun()
    with a3:
        if row["lifecycle"] not in {"Offboarding", "Terminated"} and st.button(
            "Start offboarding", key=f"off_{key}", use_container_width=True
        ):
            _patch_v(vid, lifecycle="Offboarding")
            st.rerun()


def main() -> None:
    portfolio_skin.page_header(
        title="Third-Party Risk Management",
        lede="Tier, diligence, assurance, monitoring, remediate, exit. Club demo — not a system of record.",
        kicker="Third-party risk",
    )

    seed = demo_kit.seed_controls()
    vendors, asm, issues, signals = _sync(seed)
    ev = _enrich_v(vendors)
    m = _metrics(vendors, asm, issues, signals)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    tier_f = st.sidebar.multiselect("Tier", TIERS, default=TIERS)
    life_f = st.sidebar.multiselect("Lifecycle", LIFECYCLE, default=LIFECYCLE)
    filtered = ev[ev["tier"].isin(tier_f) & ev["lifecycle"].isin(life_f)]

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Tier 1", m["tier1"])
    k2.metric("Monitoring alerts", m["alerts"])
    k3.metric("Hot diligence", m["asm_hot"])
    k4.metric("Open issues", m["issues_open"])
    k5.metric("Offboarding", m["offboard"])

    work, vend_tab, dil_tab, mon_tab, iss_tab, intake, export = st.tabs(
        ["Workbench", "Vendor", "Diligence", "Monitoring", "Issues", "Intake", "Export"]
    )

    with work:
        st.subheader("TPRM workbench")
        if m["alerts"]:
            st.warning(f"{m['alerts']} vendor(s) have open monitoring alerts.")

        featured = ev[ev["vendor_id"].isin(FEATURED)].sort_values("tier")
        st.markdown(f"**Featured — statement of record ({len(featured)})**")
        for _, row in featured.iterrows():
            st.markdown("---")
            _vendor_detail(row, asm, issues, signals, expanded=True)
            _vendor_actions(row, key=f"feat_{row['vendor_id']}")
            st.markdown("---")

        hot_asm = asm[asm["status"].isin(["Overdue", "In progress", "With vendor"])].sort_values("due")
        st.markdown(f"**Diligence needing attention ({len(hot_asm)})**")
        if hot_asm.empty:
            st.info("Clear.")
        else:
            for _, r in hot_asm.iterrows():
                with st.expander(f"{r['assessment_id']} · {r['title']} · {r['status']} · due {_fmt(r['due'])}"):
                    st.write(f"**Vendor:** {r['vendor_id']} · **Scope:** {r['scope']}")
                    st.write(f"**Tier-driven:** {r['tier_driven']} · **Assessor:** {r['assessor']}")
                    if r["notes"]:
                        st.write(r["notes"])
                    if r["status"] != "Complete" and st.button("Mark complete", key=f"ac_{r['assessment_id']}"):
                        _patch_a(r["assessment_id"], status="Complete")
                        st.rerun()

        open_iss = issues[~issues["status"].isin(["Closed"])].sort_values("due")
        st.markdown(f"**Open / accepted issues ({len(open_iss)})**")
        show = open_iss.copy()
        show["due"] = show["due"].apply(_fmt)
        st.dataframe(
            show[["issue_id", "vendor_id", "title", "severity", "status", "due", "owner"]],
            use_container_width=True,
            hide_index=True,
        )

        off = ev[ev["lifecycle"].eq("Offboarding")]
        if not off.empty:
            st.markdown("**Offboarding**")
            for _, row in off.iterrows():
                with st.expander(f"{row['vendor_id']} · {row['name']}"):
                    _vendor_detail(row, asm, issues, signals)
                    if st.button("Mark terminated", key=f"term_{row['vendor_id']}"):
                        _patch_v(row["vendor_id"], lifecycle="Terminated", monitoring_alert="")
                        st.rerun()

    with vend_tab:
        st.subheader("Vendor register")
        ids = filtered["vendor_id"].tolist()
        if not ids:
            st.info("Nothing in filter.")
        else:
            pick = st.selectbox("Vendor", ids)
            row = ev[ev["vendor_id"] == pick].iloc[0]
            _vendor_detail(row, asm, issues, signals, expanded=True)
            _vendor_actions(row, key=f"v_{pick}")
        show = filtered[
            [
                "vendor_id",
                "name",
                "tier",
                "inherent",
                "residual",
                "lifecycle",
                "outside_in",
                "assurance",
                "next_assessment",
            ]
        ].copy()
        show["next_assessment"] = show["next_assessment"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

    with dil_tab:
        st.subheader("Diligence / assessments")
        show = asm.copy()
        show["due"] = show["due"].apply(_fmt)
        show["started"] = show["started"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

        st.caption(
            "Tier drives depth: Tier 1 = full assurance + on-site/rights as needed; "
            "Tier 2 = SOC 2 / HITRUST i1 or equivalent; Tier 3–4 = light questionnaire / cert check."
        )
        st.markdown("**Featured questionnaire (Orbit AMS)**")
        _render_questionnaire(expanded=True, key_prefix="dil_q")

    with mon_tab:
        st.subheader("Continuous monitoring (synthetic signals)")
        show = signals.copy()
        show["detected"] = show["detected"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

        fig = px.bar(
            ev.sort_values("outside_in"),
            x="name",
            y="outside_in",
            color="tier",
            title="Outside-in score by vendor (demo)",
            category_orders={"tier": TIERS},
        )
        st.plotly_chart(fig, use_container_width=True)

    with iss_tab:
        st.subheader("Issues & remediation")
        for _, r in issues.sort_values("due").iterrows():
            with st.expander(f"{r['issue_id']} · {r['title']} · {r['severity']} · {r['status']}"):
                st.write(f"**Vendor:** {r['vendor_id']} · **Due:** {_fmt(r['due'])} · **Owner:** {r['owner']}")
                st.write(f"**Source:** {r['source']}")
                st.write(r["detail"])
                b1, b2, b3 = st.columns(3)
                with b1:
                    if r["status"] != "Closed" and st.button("Close", key=f"icl_{r['issue_id']}"):
                        _patch_i(r["issue_id"], status="Closed")
                        st.rerun()
                with b2:
                    if r["status"] == "Open" and st.button("Send to vendor", key=f"iv_{r['issue_id']}"):
                        _patch_i(r["issue_id"], status="With vendor")
                        st.rerun()
                with b3:
                    if r["status"] not in {"Closed", "Accepted risk"} and st.button(
                        "Accept risk", key=f"ia_{r['issue_id']}"
                    ):
                        _patch_i(r["issue_id"], status="Accepted risk")
                        st.rerun()

    with intake:
        st.subheader("Intake new third party")
        with st.form("intake"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Vendor name")
                service = st.text_input("Service")
                data_access = st.text_input("Data access", placeholder="e.g. customer PII")
                system_access = st.text_input("System access", placeholder="e.g. SSO, API")
            with c2:
                # Simple inherent → tier (ProcessUnity-style lite)
                has_pii = st.checkbox("Processes personal / regulated data")
                prod_access = st.checkbox("Production / privileged system access")
                mission = st.checkbox("Mission-critical process dependency")
                owner = st.text_input("TPRM owner", value="TPRM")
            if st.form_submit_button("Create vendor"):
                if not name.strip():
                    st.error("Name required.")
                else:
                    score = int(has_pii) + int(prod_access) + int(mission)
                    if score >= 3 or (has_pii and prod_access):
                        tier, inherent = "Tier 1 — Critical", "Critical"
                    elif score == 2:
                        tier, inherent = "Tier 2 — High", "High"
                    elif score == 1:
                        tier, inherent = "Tier 3 — Medium", "Medium"
                    else:
                        tier, inherent = "Tier 4 — Low", "Low"
                    n = len(st.session_state.tprm_vendors) + 1
                    today = _today()
                    add = {
                        "vendor_id": f"VND-2026-{n:03d}",
                        "name": name.strip(),
                        "service": service.strip() or "TBD",
                        "category": "Intake",
                        "owner": owner.strip() or "TPRM",
                        "business_owner": "TBD",
                        "lifecycle": "Intake",
                        "tier": tier,
                        "inherent": inherent,
                        "residual": inherent,
                        "data_access": data_access.strip() or "TBD",
                        "system_access": system_access.strip() or "TBD",
                        "criticality_note": "Intake — inherent from checklist.",
                        "outside_in": 70,
                        "outside_in_trend": "—",
                        "assurance": "None on file",
                        "assurance_period": "—",
                        "assurance_gap": "",
                        "dpa": False,
                        "security_addendum": False,
                        "right_to_audit": False,
                        "exit_clause": False,
                        "contract_end": today + timedelta(days=365),
                        "last_assessment": pd.NaT,
                        "next_assessment": today + timedelta(days=30),
                        "fourth_parties": "",
                        "monitoring_alert": "",
                        "risk_refs": "",
                        "summary": f"Intake complete. Tier {tier} from inherent checklist. Diligence not started.",
                        "diligence_steps": [],
                        "evidence": [],
                        "open_actions": [],
                    }
                    _save_v(pd.concat([st.session_state.tprm_vendors, pd.DataFrame([add])], ignore_index=True))
                    st.success(f"{add['vendor_id']} created as {tier}.")
                    st.rerun()

    with export:
        st.subheader("Export")
        out = filtered.copy()
        for col in ("contract_end", "last_assessment", "next_assessment"):
            out[col] = out[col].apply(_fmt)
        for col in ("diligence_steps", "evidence", "open_actions"):
            if col in out.columns:
                out = out.drop(columns=[col])
        demo_kit.csv_download(out, "vendors.csv", label="Download vendors")
        oa = asm.copy()
        oa["due"] = oa["due"].apply(_fmt)
        oa["started"] = oa["started"].apply(_fmt)
        demo_kit.csv_download(oa, "assessments.csv", label="Download assessments", key="a_csv")
        oi = issues.copy()
        oi["opened"] = oi["opened"].apply(_fmt)
        oi["due"] = oi["due"].apply(_fmt)
        demo_kit.csv_download(oi, "issues.csv", label="Download issues", key="i_csv")
        q = st.session_state.get("tprm_questionnaire") or _orbit_sig_lite()
        demo_kit.csv_download(
            pd.DataFrame(q["items"]),
            "orbit_sig_lite.csv",
            label="Download Orbit SIG Lite questionnaire",
            key="q_csv",
        )
        st.caption("Resample rebuilds the demo set. Edits live in this browser session only.")


if __name__ == "__main__":
    main()
