#!/usr/bin/env python3
"""Incident response workbench — club teaching toy."""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Incident Response Management · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

SEVERITIES = ["SEV-1", "SEV-2", "SEV-3", "SEV-4"]
PHASES = ["Detect", "Triage", "Contain", "Eradicate", "Recover", "Post-incident", "Closed"]
PHASE_COLOR = {
    "Detect": "#91aa9b",
    "Triage": "#f2b84b",
    "Contain": "#ffb347",
    "Eradicate": "#7fffb2",
    "Recover": "#38e881",
    "Post-incident": "#5c7a68",
    "Closed": "#3a5a44",
}
CATEGORIES = [
    "Malware / ransomware",
    "Unauthorized access",
    "Data exposure",
    "Phishing",
    "Denial of service",
    "Insider misuse",
    "Supply chain",
    "Physical",
    "Configuration drift",
]

# IDs of incidents that get rendered fully open on the workbench
FEATURED = {"INC-2026-001", "INC-2026-003", "INC-2026-009"}


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _now() -> pd.Timestamp:
    return pd.Timestamp.now()


def _sample(seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Named incidents with timeline entries, containment actions, and comms."""
    now = _now()
    today = _today()
    rng = np.random.default_rng(seed)

    def j(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    # ── INC-2026-001  Credential stuffing ────────────────────────────
    inc001_det = now - timedelta(hours=96 + j(-4, 5))
    inc001_tri = inc001_det + timedelta(minutes=22)
    inc001_con = inc001_tri + timedelta(hours=5, minutes=40)
    inc001_era = inc001_con + timedelta(hours=52)
    inc001_rec = inc001_era + timedelta(hours=30)

    # ── INC-2026-003  IBM i break-glass ──────────────────────────────
    inc003_det = now - timedelta(hours=38 + j(-2, 3))
    inc003_tri = inc003_det + timedelta(minutes=35)

    # ── INC-2026-009  Third-party SaaS breach ────────────────────────
    inc009_det = now - timedelta(hours=8 + j(-2, 3))

    incidents = [
        # ── 001 — Credential stuffing ────────────────────────────────
        {
            "incident_id": "INC-2026-001",
            "title": "Credential-stuffing spike on customer portal",
            "category": "Unauthorized access",
            "severity": "SEV-2",
            "phase": "Recover",
            "commander": "Alex Rivera · SecOps",
            "reporter": "SOC automated alert (WAF threshold)",
            "detected": inc001_det,
            "triaged": inc001_tri,
            "contained": inc001_con,
            "eradicated": inc001_era,
            "recovered": inc001_rec,
            "closed": pd.NaT,
            "affected_systems": "Customer portal (portal.example.com), Azure AD B2C IdP, marketing-DB (read-replica), CDN edge nodes",
            "affected_users": 340,
            "data_exposure": "Confirmed: 340 email + display-name pairs scraped via authenticated session after successful stuffing. No passwords, payment, or health data exposed. Scrape log SHA-256 preserved in evidence locker.",
            "pii": True,
            "regulatory": "GDPR Art. 33/34 · State breach-notification (CA, NY, TX thresholds met)",
            "root_cause": "Credential list (combo-list 'COMB-2026-Q3', ~2.4M pairs) reused against /api/login. Endpoint accepted unlimited attempts — WAF rule set excluded /api/* paths added during Q1 sprint. IdP conditional-access policy did not enforce MFA for B2C consumer tier.",
            "containment_summary": "1) Blocked 14 source-IP /24 ranges at WAF edge. 2) Forced password reset for 340 confirmed-compromised accounts + 1,200 accounts matching credential-list email domain. 3) Enabled CAPTCHA on /api/login. 4) Applied progressive rate-limit (5 failures → 60s lockout → escalating to 15m). 5) Revoked active sessions for scraping user-agent pattern. 6) Marketing-DB read-replica rotated; connection strings cycled.",
            "playbook": "PB-001 Unauthorized Access",
            "after_action": "Rate-limit + CAPTCHA should have been on the API endpoint at launch. WAF rule set missed /api/* paths added during the Q1 sprint — the pull request was approved without Security review because it was tagged 'frontend-only.' Conditional-access gap on the B2C consumer tier meant MFA was not enforced even though it was available.",
            "notify_required": True,
            "notified": True,
            "lessons": "1) WAF rule changes must go through Security review regardless of PR label. 2) Add /api/* to WAF scope and run quarterly WAF-coverage audit. 3) Threat-intel feed subscription for credential dumps — auto-block known combo-list user-agents. 4) B2C MFA rollout: phased enforcement starting with accounts that hold payment methods. 5) Tabletop this scenario annually.",
            "evidence": [
                {"ref": "EVD-001-A", "desc": "WAF alert export (14 source CIDRs, 87k requests/h)", "source": "WAF console"},
                {"ref": "EVD-001-B", "desc": "IdP sign-in risk report — 340 accounts with 'atRisk' flag", "source": "Azure AD B2C"},
                {"ref": "EVD-001-C", "desc": "Scrape-log extract (SHA-256: a4f3…c91e)", "source": "App server access logs"},
                {"ref": "EVD-001-D", "desc": "CAPTCHA + rate-limit deployment PR #4821 (merged)", "source": "GitHub"},
                {"ref": "EVD-001-E", "desc": "DPA Art. 33 notification receipt (ref DPA-2026-08-17-0042)", "source": "Legal — DPA portal"},
                {"ref": "EVD-001-F", "desc": "Password-reset campaign completion report — 1,540 resets", "source": "IdP admin console"},
                {"ref": "EVD-001-G", "desc": "Marketing-DB read-replica rotation change ticket CHG-9184", "source": "ITSM"},
            ],
            "open_actions": [
                {"action": "Close WAF-coverage gap for /api/* paths", "owner": "Platform Engineering", "due": today + timedelta(days=3), "status": "In progress"},
                {"action": "B2C consumer MFA phased rollout — phase 1 (payment accounts)", "owner": "IAM", "due": today + timedelta(days=14), "status": "Planned"},
                {"action": "Threat-intel feed integration (combo-list auto-block)", "owner": "SecOps", "due": today + timedelta(days=21), "status": "Planned"},
                {"action": "State breach-notification letters (CA, NY, TX)", "owner": "Legal", "due": today + timedelta(days=5), "status": "Drafting"},
                {"action": "After-action report finalization", "owner": "IR Commander", "due": today + timedelta(days=7), "status": "Draft"},
            ],
        },
        # ── 002 — Ransomware ─────────────────────────────────────────
        {
            "incident_id": "INC-2026-002",
            "title": "Ransomware execution on engineering workstation",
            "category": "Malware / ransomware",
            "severity": "SEV-1",
            "phase": "Post-incident",
            "commander": "Alex Rivera · SecOps",
            "reporter": "EDR (auto-quarantine)",
            "detected": now - timedelta(days=18, hours=j(2, 6)),
            "triaged": now - timedelta(days=18, hours=0),
            "contained": now - timedelta(days=17, hours=18),
            "eradicated": now - timedelta(days=16),
            "recovered": now - timedelta(days=14),
            "closed": pd.NaT,
            "affected_systems": "ENGWS-0042, file share \\\\ENG-NAS, build server",
            "affected_users": 12,
            "data_exposure": "None confirmed — EDR stopped lateral. Build artifacts restored from clean backup.",
            "pii": False,
            "regulatory": "None",
            "root_cause": "Phishing email with macro-enabled doc. User bypassed attachment warning. EDR caught execution but share encryption started.",
            "containment_summary": "Isolated host. Killed share sessions. Confirmed backup integrity for \\\\ENG-NAS. Re-imaged workstation.",
            "playbook": "PB-002 Ransomware",
            "after_action": "After-action complete. Tabletop results from 2026-07-09 matched the real response well. Comms templates worked.",
            "notify_required": False,
            "notified": False,
            "lessons": "Block macro-enabled Office docs at the mail gateway. Accelerate share-access tiering.",
            "evidence": [],
            "open_actions": [],
        },
        # ── 003 — IBM i *ALLOBJ break-glass ──────────────────────────
        {
            "incident_id": "INC-2026-003",
            "title": "IBM i *ALLOBJ break-glass used outside approved PAM window",
            "category": "Insider misuse",
            "severity": "SEV-2",
            "phase": "Contain",
            "commander": "Maya Chen · IT Security",
            "reporter": "QAUDJRN T-AF alert → SOC (IBM i Ops on-call)",
            "detected": inc003_det,
            "triaged": inc003_tri,
            "contained": pd.NaT,
            "eradicated": pd.NaT,
            "recovered": pd.NaT,
            "closed": pd.NaT,
            "affected_systems": "IBM i PRODBOX (LPAR SN 065-1042), PAM vault, QAUDJRN, production library PRODDATA/CUSTMAST",
            "affected_users": 1,
            "data_exposure": "Under active investigation. QAUDJRN journal entry type T-AF shows SAVRST (save/restore) activity against production library PRODDATA at 02:14. Object-level audit (T-ZC) shows *USE access to CUSTMAST file containing 48,200 customer records (name, address, phone). No confirmed exfiltration yet — IFS outbound transfer logs under review.",
            "pii": True,
            "regulatory": "SOX ITGC (privileged access) · Potential GDPR if exfiltration confirmed",
            "root_cause": "Ops profile OPSBREAK01 carries *ALLOBJ special authority under exception EXC-2026-011 (approved for batch restart only). Profile signed on interactively at 02:14 — PAM vault shows no checkout at that time. Last approved PAM checkout was 18:47 the prior day for CHG-8917 (batch restart). Either the PAM session was left open or the password was obtained outside the vault.",
            "containment_summary": "1) Profile OPSBREAK01 disabled (CHGUSRPRF STATUS(*DISABLED)) at triage +8 min. 2) PAM vault password rotated for OPSBREAK01. 3) Active jobs under OPSBREAK01 ended (*IMMED). 4) QAUDJRN entries from 02:00–03:30 exported to forensic hold (EVD-003-A). 5) IFS NetServer share audit enabled. 6) Network team confirmed no FTP/SFTP outbound from PRODBOX during the window. 7) SAVRST target SAVF identified — still on PRODBOX, not transferred.",
            "playbook": "PB-003 Unauthorized Access (IBM i)",
            "after_action": "",
            "notify_required": False,
            "notified": False,
            "lessons": "",
            "evidence": [
                {"ref": "EVD-003-A", "desc": "QAUDJRN export 02:00–03:30 (T-AF, T-ZC, T-CD entries) — 847 journal entries", "source": "DSPJRN QAUDJRN"},
                {"ref": "EVD-003-B", "desc": "PAM vault checkout log for OPSBREAK01 (last 7 days)", "source": "CyberArk"},
                {"ref": "EVD-003-C", "desc": "DSPUSRPRF OPSBREAK01 — shows *ALLOBJ, *SECADM, last sign-on 02:14", "source": "IBM i PRODBOX"},
                {"ref": "EVD-003-D", "desc": "SAVRST target SAVF object detail (PRODDATA/CUSTSAV, 214 MB)", "source": "DSPOBJD"},
                {"ref": "EVD-003-E", "desc": "Network flow logs — PRODBOX outbound 00:00–06:00 (no FTP/SFTP)", "source": "Firewall / NetFlow"},
                {"ref": "EVD-003-F", "desc": "Exception register entry EXC-2026-011 (*ALLOBJ waiver)", "source": "GRC exception register"},
                {"ref": "EVD-003-G", "desc": "Change ticket CHG-8917 (batch restart at 18:47, closed 19:22)", "source": "ITSM"},
                {"ref": "EVD-003-H", "desc": "WRKACTJOB snapshot at detection (OPSBREAK01 active jobs)", "source": "IBM i console"},
            ],
            "open_actions": [
                {"action": "Complete QAUDJRN forensic analysis (T-ZC object access scope)", "owner": "Maya Chen · IT Security", "due": today + timedelta(days=1), "status": "In progress"},
                {"action": "Interview on-call operator (shift log for overnight)", "owner": "HR / IT Security", "due": today + timedelta(days=1), "status": "Scheduled"},
                {"action": "Determine if SAVF was transferred off-box (IFS + FTP audit)", "owner": "Network Security", "due": today + timedelta(days=1), "status": "In progress"},
                {"action": "Review PAM session timeout policy (was checkout left open?)", "owner": "IAM", "due": today + timedelta(days=3), "status": "Planned"},
                {"action": "Tighten EXC-2026-011 conditions (interactive sign-on block)", "owner": "IBM i Ops / GRC", "due": today + timedelta(days=5), "status": "Planned"},
                {"action": "SOX ITGC notification to internal audit (if confirmed misuse)", "owner": "GRC Lead", "due": today + timedelta(days=2), "status": "Pending investigation"},
                {"action": "Delete SAVF PRODDATA/CUSTSAV after forensic copy", "owner": "IBM i Ops", "due": today + timedelta(days=3), "status": "Blocked on forensics"},
            ],
        },
        # ── 004 — RACF SPECIAL ───────────────────────────────────────
        {
            "incident_id": "INC-2026-004",
            "title": "RACF SPECIAL contractor ALTER attempt",
            "category": "Insider misuse",
            "severity": "SEV-1",
            "phase": "Closed",
            "commander": "Maya Chen · IT Security",
            "reporter": "Mainframe Security (SMF alert)",
            "detected": now - timedelta(days=42, hours=j(4, 8)),
            "triaged": now - timedelta(days=42, hours=2),
            "contained": now - timedelta(days=42),
            "eradicated": now - timedelta(days=41),
            "recovered": now - timedelta(days=40),
            "closed": now - timedelta(days=35),
            "affected_systems": "IBM Z sysplex — CICS region profiles",
            "affected_users": 1,
            "data_exposure": "None — ALTER was blocked by auditor-level monitoring.",
            "pii": False,
            "regulatory": "SOX",
            "root_cause": "Contractor TSO ID retained RACF SPECIAL after project end (EXC-2026-012 context). Attempted ALTER of CICS region profiles.",
            "containment_summary": "Revoked RACF SPECIAL immediately. Locked contractor ID. Confirmed no successful ALTER via SMF audit trail.",
            "playbook": "PB-004 Insider Threat (Mainframe)",
            "after_action": "Deprovision checklist did not include RACF attribute revoke. Added to JML process.",
            "notify_required": False,
            "notified": False,
            "lessons": "Quarterly RACF SPECIAL recert is necessary. JML must cover mainframe attributes.",
            "evidence": [],
            "open_actions": [],
        },
        # ── 005 — JDE IFS exposure ───────────────────────────────────
        {
            "incident_id": "INC-2026-005",
            "title": "JDE IFS anonymous share data exposure",
            "category": "Data exposure",
            "severity": "SEV-2",
            "phase": "Eradicate",
            "commander": "Jordan Blake · Infrastructure",
            "reporter": "SOC (SMB anomaly from guest WLAN)",
            "detected": now - timedelta(days=7, hours=j(2, 6)),
            "triaged": now - timedelta(days=7, hours=1),
            "contained": now - timedelta(days=7),
            "eradicated": pd.NaT,
            "recovered": pd.NaT,
            "closed": pd.NaT,
            "affected_systems": "JD Edwards IFS share (World data libraries)",
            "affected_users": 0,
            "data_exposure": "JDE World data libraries were readable without authentication from the guest WLAN segment.",
            "pii": True,
            "regulatory": "GDPR",
            "root_cause": "IFS share created with *PUBLIC authority during a migration years ago. No periodic review of IFS permissions.",
            "containment_summary": "Removed *PUBLIC from IFS path. Blocked SMB from guest WLAN to production VLAN. Scanning for data exfiltration markers.",
            "playbook": "PB-005 Data Exposure",
            "after_action": "",
            "notify_required": True,
            "notified": False,
            "lessons": "",
            "evidence": [],
            "open_actions": [],
        },
        # ── 006 — SAP ECC break-glass ────────────────────────────────
        {
            "incident_id": "INC-2026-006",
            "title": "SAP ECC break-glass use outside change window",
            "category": "Insider misuse",
            "severity": "SEV-3",
            "phase": "Eradicate",
            "commander": "Maya Chen · IT Security",
            "reporter": "SAP Basis (ST01 gap)",
            "detected": now - timedelta(days=11, hours=j(3, 7)),
            "triaged": now - timedelta(days=11),
            "contained": now - timedelta(days=10, hours=18),
            "eradicated": pd.NaT,
            "recovered": pd.NaT,
            "closed": pd.NaT,
            "affected_systems": "SAP ECC (SAP_ALL break-glass ID)",
            "affected_users": 1,
            "data_exposure": "ST01 trace incomplete for the session — cannot confirm or deny data access.",
            "pii": False,
            "regulatory": "SOX",
            "root_cause": "Emergency ID used for a P1 fix but outside the approved change ticket window. ST01 was not running for the first 40 minutes.",
            "containment_summary": "Password rotated in PAM. ST01 enabled permanently. Usage review against change log in progress.",
            "playbook": "PB-006 Insider Misuse (ERP)",
            "after_action": "",
            "notify_required": False,
            "notified": False,
            "lessons": "",
            "evidence": [],
            "open_actions": [],
        },
        # ── 007 — BEC phishing ───────────────────────────────────────
        {
            "incident_id": "INC-2026-007",
            "title": "Phishing campaign targeting finance (BEC attempt)",
            "category": "Phishing",
            "severity": "SEV-3",
            "phase": "Closed",
            "commander": "Alex Rivera · SecOps",
            "reporter": "User report + mail gateway",
            "detected": now - timedelta(days=22, hours=j(4, 8)),
            "triaged": now - timedelta(days=22, hours=2),
            "contained": now - timedelta(days=22, hours=1),
            "eradicated": now - timedelta(days=22),
            "recovered": now - timedelta(days=21),
            "closed": now - timedelta(days=19),
            "affected_systems": "Mail gateway, 3 user mailboxes",
            "affected_users": 3,
            "data_exposure": "None — no credentials entered. BEC wire transfer not initiated.",
            "pii": False,
            "regulatory": "None",
            "root_cause": "Targeted BEC using spoofed CFO domain. Mail gateway flagged but delivered to quarantine; one user pulled it out.",
            "containment_summary": "Purged messages. Blocked sender domain. Reset affected credentials. Confirmed no wire activity with Treasury.",
            "playbook": "PB-007 Phishing / BEC",
            "after_action": "User who released from quarantine gets targeted re-training. Quarantine release policy tightened.",
            "notify_required": False,
            "notified": False,
            "lessons": "Quarantine release should require Security approval for external-sender messages. Treasury wire SOP held.",
            "evidence": [],
            "open_actions": [],
        },
        # ── 008 — SIEM coverage gap ──────────────────────────────────
        {
            "incident_id": "INC-2026-008",
            "title": "DMZ jump host missing from SIEM (coverage gap incident)",
            "category": "Configuration drift",
            "severity": "SEV-3",
            "phase": "Recover",
            "commander": "Jordan Blake · Infrastructure",
            "reporter": "Control test CT-2026-006 (SecOps)",
            "detected": now - timedelta(days=28, hours=j(2, 6)),
            "triaged": now - timedelta(days=28),
            "contained": now - timedelta(days=27),
            "eradicated": now - timedelta(days=14),
            "recovered": pd.NaT,
            "closed": pd.NaT,
            "affected_systems": "6 DMZ jump hosts",
            "affected_users": 0,
            "data_exposure": "Unknown — auth logs were not collected for >14 days.",
            "pii": False,
            "regulatory": "SOC 2 CC7.2",
            "root_cause": "Jump hosts provisioned outside the standard build pipeline. SIEM onboarding checklist was not in the deployment template.",
            "containment_summary": "Hosts onboarded to SIEM. 14-day gap acknowledged in PBC-2026-003 (audit evidence).",
            "playbook": "PB-008 Config Drift",
            "after_action": "",
            "notify_required": False,
            "notified": False,
            "lessons": "SIEM onboarding must be in the infra build pipeline, not a follow-up ticket.",
            "evidence": [],
            "open_actions": [],
        },
        # ── 009 — Third-party SaaS breach ────────────────────────────
        {
            "incident_id": "INC-2026-009",
            "title": "Third-party SaaS breach notification (payroll provider)",
            "category": "Supply chain",
            "severity": "SEV-2",
            "phase": "Triage",
            "commander": "GRC Lead",
            "reporter": "Vendor notification email (security@payrollco.example.com)",
            "detected": inc009_det,
            "triaged": pd.NaT,
            "contained": pd.NaT,
            "eradicated": pd.NaT,
            "recovered": pd.NaT,
            "closed": pd.NaT,
            "affected_systems": "PayrollCo SaaS (data processor under DPA-2024-019), SSO federation, API integration (payroll sync), SFTP drop for tax filings",
            "affected_users": 0,
            "data_exposure": "Unknown scope. Vendor notification states 'a subset of customer tenants may have been affected by unauthorized access to a backup environment.' Our tenant processes payroll for 1,820 employees — records include SSN, bank routing/account, salary, tax withholding. No IOC list received yet. Vendor has engaged third-party forensics firm (report ETA: 48–72h from notification).",
            "pii": True,
            "regulatory": "GDPR Art. 33 (72h clock started at detection) · State breach-notification (all 50 states if SSN confirmed) · IRS Pub 4557 (tax data)",
            "root_cause": "Pending vendor forensic disclosure. Vendor's initial notification attributes the breach to 'compromised administrative credentials in a backup environment.' No further technical detail provided.",
            "containment_summary": "1) API bearer token rotated (revoked + reissued). 2) SSO federation session revoked; SAML assertion re-signed. 3) SFTP credentials rotated; IP allowlist tightened to our egress range only. 4) TPRM team activated — formal data-subject impact inquiry sent to vendor (DPA clause 8.3 response deadline: 24h). 5) Internal monitoring: alerting on any new PayrollCo API calls with prior credentials. 6) Payroll processing suspended pending vendor confirmation that production environment is unaffected.",
            "playbook": "PB-009 Supply Chain",
            "after_action": "",
            "notify_required": True,
            "notified": False,
            "lessons": "",
            "evidence": [
                {"ref": "EVD-009-A", "desc": "Vendor breach notification email (timestamped, full text preserved)", "source": "Email — security@payrollco.example.com"},
                {"ref": "EVD-009-B", "desc": "API token rotation confirmation + old token revocation log", "source": "API gateway"},
                {"ref": "EVD-009-C", "desc": "SSO federation session revocation log", "source": "IdP admin console"},
                {"ref": "EVD-009-D", "desc": "SFTP credential rotation + IP allowlist change ticket CHG-9201", "source": "ITSM"},
                {"ref": "EVD-009-E", "desc": "DPA clause 8.3 formal inquiry (sent, awaiting response)", "source": "Legal / TPRM"},
                {"ref": "EVD-009-F", "desc": "DPA-2024-019 — Data Processing Agreement with PayrollCo", "source": "Contract repository"},
                {"ref": "EVD-009-G", "desc": "PayrollCo SOC 2 Type II report (last received 2025-12-15)", "source": "TPRM evidence locker"},
                {"ref": "EVD-009-H", "desc": "Payroll processing suspension notice to Payroll Ops", "source": "Email — internal"},
            ],
            "open_actions": [
                {"action": "Obtain IOC list and impacted-tenant confirmation from vendor", "owner": "TPRM", "due": today + timedelta(days=1), "status": "Waiting on vendor"},
                {"action": "Determine if our tenant's backup data was accessed", "owner": "TPRM / Vendor forensics", "due": today + timedelta(days=3), "status": "Waiting on vendor"},
                {"action": "GDPR Art. 33 DPA notification (72h deadline)", "owner": "Legal / DPO", "due": today + timedelta(days=2), "status": "Drafting"},
                {"action": "Engage outside counsel for state breach-notification if SSN confirmed", "owner": "Legal", "due": today + timedelta(days=5), "status": "Contingent"},
                {"action": "Employee communication (if PII exposure confirmed)", "owner": "HR / Comms", "due": today + timedelta(days=5), "status": "Contingent"},
                {"action": "Evaluate PayrollCo contract termination / alternate provider", "owner": "Procurement / TPRM", "due": today + timedelta(days=14), "status": "Planned"},
                {"action": "Resume payroll processing (once vendor clears production env)", "owner": "Payroll Ops", "due": today + timedelta(days=3), "status": "Blocked on vendor"},
                {"action": "Request updated SOC 2 bridge letter from vendor", "owner": "TPRM", "due": today + timedelta(days=7), "status": "Planned"},
            ],
        },
        # ── 010 — VPN CVE attempt ────────────────────────────────────
        {
            "incident_id": "INC-2026-010",
            "title": "VPN concentrator CVE exploitation attempt",
            "category": "Unauthorized access",
            "severity": "SEV-3",
            "phase": "Closed",
            "commander": "Alex Rivera · SecOps",
            "reporter": "IDS alert",
            "detected": now - timedelta(days=30, hours=j(4, 8)),
            "triaged": now - timedelta(days=30, hours=2),
            "contained": now - timedelta(days=30, hours=1),
            "eradicated": now - timedelta(days=30),
            "recovered": now - timedelta(days=29),
            "closed": now - timedelta(days=27),
            "affected_systems": "VPN Gateway (EXC-2026-004 context — legacy OS)",
            "affected_users": 0,
            "data_exposure": "None — exploit attempt failed. Geo-block and jump-host requirement held.",
            "pii": False,
            "regulatory": "None",
            "root_cause": "Known CVE on unsupported concentrator OS. Compensating controls (geo-block, no split-tunnel) prevented exploitation.",
            "containment_summary": "Blocked source IP. Confirmed no successful auth. Accelerated hardware refresh PO.",
            "playbook": "PB-010 Vuln Exploitation",
            "after_action": "Compensating controls on the exception worked as designed. Hardware refresh PO approved — arrival in 6 weeks.",
            "notify_required": False,
            "notified": False,
            "lessons": "Time-boxed exception with compensating controls held. Still need to close EXC-2026-004 on schedule.",
            "evidence": [],
            "open_actions": [],
        },
    ]

    # ── Timeline entries ─────────────────────────────────────────────
    timeline_entries = []
    for inc in incidents:
        iid = inc["incident_id"]
        for phase_col, label in [
            ("detected", "Detected"),
            ("triaged", "Triaged"),
            ("contained", "Contained"),
            ("eradicated", "Eradicated"),
            ("recovered", "Recovered"),
            ("closed", "Closed"),
        ]:
            ts = inc.get(phase_col)
            if pd.notna(ts):
                timeline_entries.append(
                    {"incident_id": iid, "timestamp": ts, "phase": label, "entry": f"{label} by {inc['commander']}"}
                )

    # Deep timeline for featured incidents
    timeline_entries.extend([
        # ── INC-2026-001 deep timeline ───────────────────────────────
        {"incident_id": "INC-2026-001", "timestamp": inc001_det + timedelta(minutes=2), "phase": "Detect", "entry": "WAF alert: /api/login 87,412 requests/h from 14 CIDRs — threshold is 5,000/h."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_det + timedelta(minutes=8), "phase": "Detect", "entry": "SOC analyst confirms credential-stuffing pattern. Combo-list user-agent string identified."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_tri + timedelta(minutes=5), "phase": "Triage", "entry": "Commander assigned: Alex Rivera. Severity set SEV-2 (confirmed account compromise, no lateral movement)."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_tri + timedelta(minutes=15), "phase": "Triage", "entry": "IdP risk report pulled: 340 accounts flagged atRisk. Scrape-log pattern identified (profile-page GETs at 4/sec)."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_tri + timedelta(minutes=30), "phase": "Triage", "entry": "Data classification check: email + display name confirmed. No payment, health, or government ID in scrape scope."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con - timedelta(hours=4), "phase": "Contain", "entry": "WAF edge block applied: 14 source /24 ranges null-routed. Attack volume drops to 0."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con - timedelta(hours=3), "phase": "Contain", "entry": "Password reset campaign initiated: 340 confirmed + 1,200 domain-matched accounts (1,540 total)."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con - timedelta(hours=2), "phase": "Contain", "entry": "CAPTCHA enabled on /api/login. Progressive rate-limit deployed (5 fail → 60s → 15m escalation)."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con, "phase": "Contain", "entry": "Sessions revoked for scraping user-agent pattern. Marketing-DB read-replica connection strings rotated."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con + timedelta(hours=2), "phase": "Contain", "entry": "GDPR Art. 33 notification submitted to DPA (ref DPA-2026-08-17-0042). 72h clock satisfied."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_era - timedelta(hours=6), "phase": "Eradicate", "entry": "WAF rule audit: /api/* paths confirmed missing from rule set. PR #4821 merged to close gap."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_era, "phase": "Eradicate", "entry": "Scrape-log SHA-256 hash computed and stored in evidence locker. Source CIDRs added to permanent block list."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_rec - timedelta(hours=4), "phase": "Recover", "entry": "Password reset campaign: 1,494 of 1,540 accounts have completed reset (97%). Remaining 46 contacted individually."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_rec, "phase": "Recover", "entry": "Portal login volume returned to baseline. No residual stuffing attempts observed. Monitoring continues."},

        # ── INC-2026-003 deep timeline ───────────────────────────────
        {"incident_id": "INC-2026-003", "timestamp": inc003_det + timedelta(minutes=0), "phase": "Detect", "entry": "QAUDJRN T-AF entry: profile OPSBREAK01 signed on interactively at 02:14 from console DSP01."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_det + timedelta(minutes=3), "phase": "Detect", "entry": "Alert forwarded to SOC by IBM i Ops on-call. PAM vault checked — no active checkout for OPSBREAK01."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_det + timedelta(minutes=12), "phase": "Detect", "entry": "QAUDJRN T-ZC entries show *USE access to CUSTMAST file (PRODDATA library) starting 02:17."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_det + timedelta(minutes=18), "phase": "Detect", "entry": "SAVRST activity detected: SAVOBJ to SAVF PRODDATA/CUSTSAV (target: CUSTMAST). Size: 214 MB."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri, "phase": "Triage", "entry": "Commander assigned: Maya Chen. Severity set SEV-2 (*ALLOBJ misuse, PII file accessed, SOX scope)."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(minutes=5), "phase": "Triage", "entry": "EXC-2026-011 reviewed: *ALLOBJ approved for batch restart only, not interactive sign-on or SAVRST."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(minutes=8), "phase": "Triage", "entry": "Profile OPSBREAK01 disabled (CHGUSRPRF STATUS(*DISABLED)). Active jobs ended *IMMED."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(minutes=12), "phase": "Triage", "entry": "PAM vault password rotated for OPSBREAK01. Old password hash preserved for forensics."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(minutes=20), "phase": "Triage", "entry": "WRKACTJOB snapshot captured. OPSBREAK01 had 2 active jobs: QPADEV0004 (interactive) and QBATCH/CUSTSAV."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(minutes=40), "phase": "Triage", "entry": "Network team confirms: no FTP, SFTP, or SCP sessions from PRODBOX between 00:00–06:00. SAVF still on local disk."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(hours=1, minutes=30), "phase": "Contain", "entry": "IFS NetServer audit enabled. Monitoring for any attempt to copy CUSTSAV off-box via SMB."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(hours=2), "phase": "Contain", "entry": "QAUDJRN full export (02:00–03:30) completed: 847 entries. Preserved as EVD-003-A on forensic hold."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(hours=4), "phase": "Contain", "entry": "Shift log obtained from overnight operator. Claims CHG-8917 ran late and did not realize PAM session had expired."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(hours=6), "phase": "Contain", "entry": "HR and Legal notified for potential policy violation. Formal interview scheduled for tomorrow AM."},

        # ── INC-2026-009 deep timeline ───────────────────────────────
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(minutes=0), "phase": "Detect", "entry": "Vendor notification email received from security@payrollco.example.com. Subject: 'Security Incident Notification — Action Required.'"},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(minutes=12), "phase": "Detect", "entry": "GRC Lead reads notification. Key detail: 'unauthorized access to a backup environment affecting a subset of customer tenants.'"},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(minutes=20), "phase": "Detect", "entry": "DPA-2024-019 reviewed. PayrollCo is data processor for 1,820 employee payroll records (SSN, bank, salary, tax)."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(minutes=30), "phase": "Detect", "entry": "GDPR Art. 33 72h clock starts. DPO notified."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(minutes=45), "phase": "Detect", "entry": "API bearer token rotated — old token revoked. Confirmed no API calls with old token after revocation."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=1), "phase": "Detect", "entry": "SSO federation session revoked. SAML assertion re-signed. Users will re-auth on next access."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=1, minutes=15), "phase": "Detect", "entry": "SFTP credentials rotated. IP allowlist tightened to corporate egress only (2 CIDRs). CHG-9201 filed."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=1, minutes=30), "phase": "Detect", "entry": "TPRM activated. Formal DPA clause 8.3 inquiry sent to vendor. Response deadline: 24h."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=2), "phase": "Detect", "entry": "Payroll processing suspended. Payroll Ops notified. Next payroll run is in 5 business days."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=3), "phase": "Detect", "entry": "Legal engaged. Outside counsel on standby for state breach-notification if SSN exposure confirmed."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=4), "phase": "Triage", "entry": "Vendor call scheduled for tomorrow 09:00. TPRM preparing data-subject impact questionnaire."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=5), "phase": "Triage", "entry": "PayrollCo SOC 2 Type II (received 2025-12-15) reviewed. No critical findings but pen-test scope did not include backup infrastructure."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=6), "phase": "Triage", "entry": "Internal monitoring rule deployed: alert on any PayrollCo API call using old bearer token pattern."},
    ])

    # ── Comms log ────────────────────────────────────────────────────
    comms = [
        # INC-2026-001 comms (deep)
        {"incident_id": "INC-2026-001", "timestamp": inc001_det + timedelta(minutes=5), "channel": "Slack #soc", "author": "SOC Analyst (K. Patel)", "message": "WAF alert triggered: /api/login receiving 87k req/h from 14 CIDRs. Pattern matches credential stuffing. Pulling IdP logs."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_tri + timedelta(minutes=2), "channel": "Slack #incident-001", "author": "Alex Rivera", "message": "I'm commander on this one. Channel created. Bridge open for real-time. Severity SEV-2 for now — confirmed account compromise but no lateral movement."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_tri + timedelta(minutes=18), "channel": "Slack #incident-001", "author": "IAM (L. Torres)", "message": "IdP risk report: 340 accounts flagged atRisk. These had successful logins from stuffing IPs. Scrape activity on profile pages (4 GETs/sec per session). Data scope: email + display name only."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_tri + timedelta(minutes=35), "channel": "Bridge", "author": "Alex Rivera", "message": "Confirmed: data classification = email + display name. No payment, health, or gov ID in scrape scope. PII threshold met for GDPR Art. 33 — Legal loop in."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con - timedelta(hours=4, minutes=10), "channel": "Slack #incident-001", "author": "Platform Eng (R. Kim)", "message": "WAF block deployed for 14 source /24s. Attack volume → 0. Monitoring for rotation to new IPs."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con - timedelta(hours=2, minutes=30), "channel": "Slack #incident-001", "author": "Platform Eng (R. Kim)", "message": "CAPTCHA live on /api/login. Rate-limit rule active: 5 failures → 60s lockout → 15m escalation. PR #4821."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con + timedelta(minutes=15), "channel": "Slack #incident-001", "author": "Alex Rivera", "message": "Containment confirmed. Sessions revoked for scraping UA. Marketing-DB read-replica rotated. Moving to eradication."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con + timedelta(hours=2, minutes=5), "channel": "Email — Legal", "author": "GRC Lead", "message": "GDPR Art. 33 notification submitted to DPA. Reference: DPA-2026-08-17-0042. 72h clock satisfied with ~14h margin."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_con + timedelta(hours=4), "channel": "Email — exec", "author": "CISO", "message": "Exec brief: credential-stuffing incident on customer portal. 340 accounts affected. Contained. GDPR notified. No financial or health data. After-action in progress."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_era + timedelta(hours=2), "channel": "Slack #incident-001", "author": "SecOps (M. Hassan)", "message": "WAF rule audit complete. /api/* paths were excluded from WAF coverage during the Q1 sprint. PR approved without Security review (tagged 'frontend-only'). Root cause confirmed."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_rec - timedelta(hours=2), "channel": "Slack #incident-001", "author": "IAM (L. Torres)", "message": "Password reset: 1,494 / 1,540 complete (97%). Remaining 46 — dormant accounts, contacted individually. No new stuffing attempts."},
        {"incident_id": "INC-2026-001", "timestamp": inc001_rec, "channel": "Slack #incident-001", "author": "Alex Rivera", "message": "Portal at baseline. Recovery confirmed. After-action report draft due in 7 days. State notification letters in progress."},

        # INC-2026-002 comms
        {"incident_id": "INC-2026-002", "timestamp": incidents[1]["detected"] + timedelta(minutes=15), "channel": "EDR console", "author": "EDR", "message": "Auto-quarantine triggered on ENGWS-0042. Ransomware binary isolated."},
        {"incident_id": "INC-2026-002", "timestamp": incidents[1]["triaged"] + timedelta(hours=2), "channel": "Bridge", "author": "Alex Rivera", "message": "Share encryption caught early. \\\\ENG-NAS snapshots clean. Build server not affected."},
        {"incident_id": "INC-2026-002", "timestamp": incidents[1]["recovered"] + timedelta(hours=4), "channel": "Email — exec", "author": "CISO", "message": "All systems restored. No data exfiltration confirmed. After-action scheduled."},

        # INC-2026-003 comms (deep)
        {"incident_id": "INC-2026-003", "timestamp": inc003_det + timedelta(minutes=4), "channel": "Slack #ibm-i-ops", "author": "IBM i Ops (D. Marshall)", "message": "QAUDJRN T-AF alert: OPSBREAK01 signed on interactively at 02:14 from DSP01. No PAM checkout on record. This profile has *ALLOBJ under EXC-2026-011."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_det + timedelta(minutes=10), "channel": "Slack #ibm-i-ops", "author": "SOC Analyst (K. Patel)", "message": "Acknowledged. Pulling full QAUDJRN for 02:00–03:30. D. Marshall — can you check WRKACTJOB for any active jobs under OPSBREAK01?"},
        {"incident_id": "INC-2026-003", "timestamp": inc003_det + timedelta(minutes=14), "channel": "Slack #ibm-i-ops", "author": "IBM i Ops (D. Marshall)", "message": "WRKACTJOB shows 2 jobs: QPADEV0004 (interactive) and QBATCH/CUSTSAV. The CUSTSAV job looks like a SAVOBJ."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_det + timedelta(minutes=20), "channel": "Slack #ibm-i-ops", "author": "SOC Analyst (K. Patel)", "message": "SAVOBJ to SAVF PRODDATA/CUSTSAV. Target is CUSTMAST file — that's the customer master with 48K records. Escalating to Maya Chen."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(minutes=2), "channel": "Slack #incident-003", "author": "Maya Chen", "message": "I have command. SEV-2. First priority: disable the profile and rotate PAM. Second: confirm the SAVF has not left the box."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(minutes=10), "channel": "Slack #incident-003", "author": "IBM i Ops (D. Marshall)", "message": "Profile disabled. Jobs ended *IMMED. PAM password rotated. Old hash preserved for forensics."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(minutes=25), "channel": "Slack #incident-003", "author": "Maya Chen", "message": "Good. DSPOBJD on PRODDATA/CUSTSAV shows 214 MB, created 02:18 today. We need to confirm it hasn't been copied off-box. Network team — pull FTP/SFTP/SCP logs for PRODBOX 00:00–06:00."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(minutes=42), "channel": "Slack #incident-003", "author": "Network Security (J. Park)", "message": "NetFlow analysis complete: zero FTP/SFTP/SCP sessions from PRODBOX in the window. No unusual outbound on any port. SAVF appears to still be local."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(hours=1, minutes=15), "channel": "Bridge", "author": "Maya Chen", "message": "Good news: SAVF hasn't left the box. Bad news: someone with *ALLOBJ saved 48K customer records to a SAVF at 2 AM outside any approved window. We need to understand why. Interview the overnight operator."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(hours=4, minutes=30), "channel": "Slack #incident-003", "author": "Maya Chen", "message": "Shift log obtained. Operator claims CHG-8917 ran late and they didn't realize the PAM session had expired when they signed back on. That doesn't explain the SAVOBJ. HR and Legal notified — formal interview tomorrow AM."},
        {"incident_id": "INC-2026-003", "timestamp": inc003_tri + timedelta(hours=6, minutes=15), "channel": "Email — GRC", "author": "GRC Lead", "message": "SOX ITGC implication flagged. If this is confirmed misuse of a privileged profile, we need to notify internal audit per the ITGC exception protocol. Holding pending investigation outcome."},

        # INC-2026-005 comms
        {"incident_id": "INC-2026-005", "timestamp": incidents[4]["detected"] + timedelta(minutes=30), "channel": "Slack #soc", "author": "SOC", "message": "SMB traffic from guest WLAN to JDE IFS share. Anonymous read confirmed."},
        {"incident_id": "INC-2026-005", "timestamp": incidents[4]["contained"] + timedelta(hours=2), "channel": "Bridge", "author": "Jordan Blake", "message": "*PUBLIC removed from IFS path. Guest-to-prod SMB blocked at firewall."},

        # INC-2026-009 comms (deep)
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(minutes=5), "channel": "Email — GRC", "author": "GRC Lead", "message": "Forwarding PayrollCo breach notification to TPRM and Legal. This is a data processor under DPA-2024-019. They process SSN, bank routing, salary for 1,820 employees. Treat as SEV-2 until we know our tenant is in scope."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(minutes=25), "channel": "Slack #incident-009", "author": "GRC Lead", "message": "Incident channel created. I have command until we assign a technical lead. GDPR 72h clock started. Priority 1: rotate all integration credentials. Priority 2: determine if our tenant is affected."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(minutes=50), "channel": "Slack #incident-009", "author": "IAM (L. Torres)", "message": "API token rotated. Old token revoked. SSO federation session revoked — SAML re-signed. Users will re-auth next login."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=1, minutes=20), "channel": "Slack #incident-009", "author": "Infra (S. Okonkwo)", "message": "SFTP creds rotated. IP allowlist tightened to our 2 corporate egress CIDRs. CHG-9201 filed. No SFTP activity from non-allowlisted IPs in the last 30 days."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=1, minutes=35), "channel": "Slack #incident-009", "author": "TPRM (A. Nguyen)", "message": "Formal DPA clause 8.3 inquiry sent to PayrollCo. 24h response deadline. Asking: 1) Is our tenant in the affected subset? 2) What data was in the backup environment? 3) IOC list. 4) Forensic firm engagement details."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=2, minutes=10), "channel": "Slack #incident-009", "author": "Payroll Ops (T. Williams)", "message": "Payroll processing suspended per IR commander. Next payroll run is in 5 business days. If we can't resume by then, we activate the BCP manual payroll process."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=3, minutes=5), "channel": "Slack #incident-009", "author": "Legal (C. Hoffman)", "message": "Outside counsel on standby. If SSN exposure confirmed, we'll need state-by-state breach notification for all 50 states (employees are distributed nationally). IRS Pub 4557 also applies to tax withholding data."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=4, minutes=30), "channel": "Slack #incident-009", "author": "GRC Lead", "message": "Reviewed PayrollCo's last SOC 2 Type II (Dec 2025). No critical findings, but pen-test scope explicitly excluded backup infrastructure. That's a gap we should have flagged in our TPRM review. Adding to post-incident."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=5, minutes=15), "channel": "Slack #incident-009", "author": "TPRM (A. Nguyen)", "message": "Vendor call confirmed for tomorrow 09:00. Their CISO and outside forensics firm will be on the call. Preparing our data-subject impact questionnaire."},
        {"incident_id": "INC-2026-009", "timestamp": inc009_det + timedelta(hours=6, minutes=30), "channel": "Email — exec", "author": "CISO", "message": "Exec brief: PayrollCo (payroll processor) notified us of a breach in their backup environment. Unknown if our tenant is affected. All integration credentials rotated. Payroll processing suspended. GDPR clock running. Next update after vendor call tomorrow."},
    ]

    df_inc = pd.DataFrame(incidents)
    df_tl = pd.DataFrame(timeline_entries)
    df_comms = pd.DataFrame(comms)

    for col in ("detected", "triaged", "contained", "eradicated", "recovered", "closed"):
        df_inc[col] = pd.to_datetime(df_inc[col], errors="coerce")
    df_tl["timestamp"] = pd.to_datetime(df_tl["timestamp"], errors="coerce")
    df_comms["timestamp"] = pd.to_datetime(df_comms["timestamp"], errors="coerce")

    return df_inc, df_tl, df_comms


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    now = _now()
    out["open"] = ~out["phase"].isin(["Post-incident", "Closed"])
    out["age_hours"] = ((now - out["detected"]).dt.total_seconds() / 3600).round(1)
    out["detect_to_contain_h"] = (
        (out["contained"] - out["detected"]).dt.total_seconds() / 3600
    ).round(1)
    out["notify_gap"] = out["notify_required"] & ~out["notified"]
    return out


def _sync(seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if st.session_state.get("_ir_seed") != seed or "ir_incidents" not in st.session_state:
        inc, tl, comms = _sample(seed)
        st.session_state.ir_incidents = inc
        st.session_state.ir_timeline = tl
        st.session_state.ir_comms = comms
        st.session_state._ir_seed = seed
    return st.session_state.ir_incidents, st.session_state.ir_timeline, st.session_state.ir_comms


def _save_inc(df: pd.DataFrame) -> None:
    st.session_state.ir_incidents = df.reset_index(drop=True)


def _patch(incident_id: str, **fields) -> None:
    df = st.session_state.ir_incidents.copy()
    loc = df.index[df["incident_id"] == incident_id]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_inc(df)


def _add_comms(incident_id: str, channel: str, message: str) -> None:
    add = {
        "incident_id": incident_id,
        "timestamp": _now(),
        "channel": channel,
        "author": "Demo user",
        "message": message,
    }
    st.session_state.ir_comms = pd.concat(
        [st.session_state.ir_comms, pd.DataFrame([add])], ignore_index=True
    )


def _metrics(df: pd.DataFrame) -> dict:
    e = _enrich(df)
    return {
        "open": int(e["open"].sum()),
        "sev1": int((e["severity"] == "SEV-1").sum()),
        "sev12_open": int((e["open"] & e["severity"].isin(["SEV-1", "SEV-2"])).sum()),
        "notify_gap": int(e["notify_gap"].sum()),
        "median_ttc": float(e["detect_to_contain_h"].dropna().median()) if e["detect_to_contain_h"].notna().any() else 0,
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
        return parsed.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _render_evidence(inc_raw: pd.Series) -> None:
    """Render the evidence table for a single incident from the raw (non-enriched) data."""
    evidence = inc_raw.get("evidence", [])
    if not evidence:
        return
    st.markdown("**Evidence chain**")
    edf = pd.DataFrame(evidence)
    st.dataframe(edf, use_container_width=True, hide_index=True)


def _render_open_actions(inc_raw: pd.Series) -> None:
    """Render the open actions table for a single incident."""
    actions = inc_raw.get("open_actions", [])
    if not actions:
        return
    st.markdown("**Open actions**")
    adf = pd.DataFrame(actions)
    if "due" in adf.columns:
        adf["due"] = adf["due"].apply(_fmt)
    st.dataframe(adf, use_container_width=True, hide_index=True)


def _detail(row: pd.Series, tl: pd.DataFrame, comms: pd.DataFrame, *, expanded: bool = False) -> None:
    """Full incident detail view.  When expanded=True, timeline and comms are shown open."""
    st.markdown(f"### {row['incident_id']} · {row['title']}")
    sev, ph, cat, cmd = st.columns(4)
    sev.metric("Severity", row["severity"])
    ph.metric("Phase", row["phase"])
    cat.caption("Category")
    cat.write(row["category"])
    cmd.caption("Commander")
    cmd.write(row["commander"])

    c1, c2, c3 = st.columns(3)
    c1.write(f"**Affected systems:** {row['affected_systems']}")
    c1.write(f"**Affected users:** {int(row['affected_users'])}")
    c2.write(f"**PII:** {'Yes' if row['pii'] else 'No'}")
    c2.write(f"**Regulatory:** {row['regulatory']}")
    if row["notify_required"]:
        c2.write(f"**Notification:** {'Sent' if row['notified'] else 'REQUIRED — not yet sent'}")
    c3.write(f"**Reporter:** {row['reporter']}")
    c3.write(f"**Playbook:** {row['playbook']}")

    st.markdown("**Data exposure assessment**")
    st.write(row["data_exposure"])

    st.markdown("**Phase clock**")
    phases = ["detected", "triaged", "contained", "eradicated", "recovered", "closed"]
    cols = st.columns(len(phases))
    for i, ph_col in enumerate(phases):
        cols[i].caption(ph_col.capitalize())
        cols[i].write(_fmt(row.get(ph_col)))

    age = row.get("age_hours", 0)
    ttc = row.get("detect_to_contain_h")
    if pd.notna(ttc):
        st.caption(f"Age: {age:.0f}h · Detect → contain: {ttc:.1f}h")
    else:
        st.caption(f"Age: {age:.0f}h · Detect → contain: pending")

    st.markdown("**Root cause**")
    st.write(row["root_cause"])

    st.markdown("**Containment actions**")
    st.write(row["containment_summary"])

    # Evidence and actions (from raw data)
    raw = st.session_state.ir_incidents
    raw_row = raw[raw["incident_id"] == row["incident_id"]]
    if not raw_row.empty:
        _render_evidence(raw_row.iloc[0])
        _render_open_actions(raw_row.iloc[0])

    linked_tl = tl[tl["incident_id"] == row["incident_id"]].sort_values("timestamp")
    linked_comms = comms[comms["incident_id"] == row["incident_id"]].sort_values("timestamp")

    with st.expander(f"Timeline ({len(linked_tl)} entries)", expanded=expanded):
        if linked_tl.empty:
            st.info("No timeline entries.")
        else:
            show = linked_tl.copy()
            show["timestamp"] = show["timestamp"].apply(_fmt)
            st.dataframe(show[["timestamp", "phase", "entry"]], use_container_width=True, hide_index=True)

    with st.expander(f"Comms log ({len(linked_comms)} entries)", expanded=expanded):
        if linked_comms.empty:
            st.info("No comms recorded.")
        else:
            show = linked_comms.copy()
            show["timestamp"] = show["timestamp"].apply(_fmt)
            st.dataframe(show[["timestamp", "channel", "author", "message"]], use_container_width=True, hide_index=True)

    if row["after_action"]:
        with st.expander("After-action", expanded=expanded):
            st.write(row["after_action"])
            if row["lessons"]:
                st.write(f"**Lessons:** {row['lessons']}")


def _actions(row: pd.Series, *, key: str) -> None:
    iid = row["incident_id"]
    now = _now()
    phase_order = {p: i for i, p in enumerate(PHASES)}
    current = phase_order.get(row["phase"], 0)

    a1, a2, a3 = st.columns(3)
    with a1:
        next_phases = [p for p in PHASES if phase_order[p] == current + 1]
        if next_phases:
            label = f"Advance to {next_phases[0]}"
            if st.button(label, key=f"adv_{key}", use_container_width=True):
                next_p = next_phases[0]
                col_map = {
                    "Triage": "triaged",
                    "Contain": "contained",
                    "Eradicate": "eradicated",
                    "Recover": "recovered",
                    "Post-incident": "recovered",
                    "Closed": "closed",
                }
                fields = {"phase": next_p}
                ts_col = col_map.get(next_p)
                if ts_col and pd.isna(row.get(ts_col)):
                    fields[ts_col] = now
                _patch(iid, **fields)
                st.rerun()
    with a2:
        if row["phase"] not in {"Post-incident", "Closed"} and st.button(
            "Escalate to SEV-1", key=f"esc_{key}", use_container_width=True
        ):
            _patch(iid, severity="SEV-1")
            st.rerun()
    with a3:
        if row["notify_required"] and not row["notified"] and st.button(
            "Mark notified", key=f"ntf_{key}", use_container_width=True
        ):
            _patch(iid, notified=True)
            st.rerun()

    with st.expander("Add comms entry"):
        with st.form(f"comms_{key}"):
            channel = st.selectbox(
                "Channel",
                ["Slack #incident", "Bridge", "Email — Legal", "Email — exec", "Email — TPRM", "Other"],
                key=f"ch_{key}",
            )
            message = st.text_area("Message", key=f"msg_{key}")
            if st.form_submit_button("Log"):
                if message.strip():
                    _add_comms(iid, channel, message.strip())
                    st.rerun()


def _queue(title: str, subset: pd.DataFrame, tl: pd.DataFrame, comms: pd.DataFrame, empty: str, key_prefix: str) -> None:
    st.markdown(f"**{title} ({len(subset)})**")
    if subset.empty:
        st.info(empty)
        return
    for _, row in subset.iterrows():
        is_featured = row["incident_id"] in FEATURED
        age = f"{row['age_hours']:.0f}h" if pd.notna(row.get("age_hours")) else "—"
        label = f"{row['incident_id']} · {row['title']} · {row['severity']} · {row['phase']} · {age}"

        if is_featured:
            st.markdown("---")
            _detail(row, tl, comms, expanded=True)
            _actions(row, key=f"{key_prefix}_{row['incident_id']}")
            st.markdown("---")
        else:
            with st.expander(label):
                _detail(row, tl, comms)
                _actions(row, key=f"{key_prefix}_{row['incident_id']}")


def main() -> None:
    portfolio_skin.page_header(
        title="Incident Response Management",
        lede="Detect, contain, eradicate, recover, learn. Club demo — not a system of record.",
        kicker="Incident response",
    )

    seed = demo_kit.seed_controls()
    inc, tl, comms = _sync(seed)
    enriched = _enrich(inc)
    m = _metrics(inc)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    sev_f = st.sidebar.multiselect("Severity", SEVERITIES, default=SEVERITIES)
    phase_f = st.sidebar.multiselect("Phase", PHASES, default=PHASES)
    cat_f = st.sidebar.multiselect("Category", CATEGORIES, default=CATEGORIES)

    filtered = enriched[
        enriched["severity"].isin(sev_f)
        & enriched["phase"].isin(phase_f)
        & enriched["category"].isin(cat_f)
    ]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Open incidents", m["open"])
    k2.metric("SEV-1/2 open", m["sev12_open"])
    k3.metric("Notify required", m["notify_gap"], help="Notification required but not yet sent.")
    k4.metric("Median detect → contain", f"{m['median_ttc']:.1f}h")

    work, incident_tab, board, intake, export = st.tabs(
        ["Workbench", "Incident", "Status board", "Intake", "Export"]
    )

    with work:
        st.subheader("Active incidents")

        sev12 = enriched[enriched["open"] & enriched["severity"].isin(["SEV-1", "SEV-2"])].sort_values("detected")
        other_open = enriched[enriched["open"] & ~enriched["severity"].isin(["SEV-1", "SEV-2"])].sort_values("detected")
        post = enriched[enriched["phase"] == "Post-incident"].sort_values("detected")
        notify = enriched[enriched["notify_gap"]].sort_values("detected")

        if not notify.empty:
            st.warning(f"{len(notify)} incident(s) require notification and have not been sent.")

        _queue("SEV-1 / SEV-2 open", sev12, tl, comms, "No high-severity incidents open.", "s12")
        _queue("Other open", other_open, tl, comms, "No other open incidents.", "oth")
        _queue("Post-incident (after-action pending)", post, tl, comms, "Nothing in post-incident.", "pi")

    with incident_tab:
        st.subheader("Incident detail")
        ids = filtered["incident_id"].tolist()
        if not ids:
            st.info("Nothing in the current filter.")
        else:
            pick = st.selectbox("Incident", ids)
            row = enriched[enriched["incident_id"] == pick].iloc[0]
            _detail(row, tl, comms, expanded=True)
            _actions(row, key=f"det_{pick}")

    with board:
        st.subheader("Status board")
        show = filtered[
            [
                "incident_id",
                "title",
                "severity",
                "phase",
                "category",
                "commander",
                "age_hours",
                "detect_to_contain_h",
                "notify_gap",
            ]
        ].copy()
        st.dataframe(show, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            phase_counts = (
                filtered["phase"]
                .value_counts()
                .reindex(PHASES)
                .fillna(0)
                .rename_axis("phase")
                .reset_index(name="count")
            )
            fig = px.bar(
                phase_counts,
                x="phase",
                y="count",
                color="phase",
                color_discrete_map=PHASE_COLOR,
                title="By phase",
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            sev_counts = (
                filtered["severity"]
                .value_counts()
                .reindex(SEVERITIES)
                .fillna(0)
                .rename_axis("severity")
                .reset_index(name="count")
            )
            fig = px.bar(sev_counts, x="severity", y="count", title="By severity")
            st.plotly_chart(fig, use_container_width=True)

        closed = enriched[enriched["detect_to_contain_h"].notna()]
        if not closed.empty:
            fig = px.scatter(
                closed,
                x="detect_to_contain_h",
                y="severity",
                color="category",
                hover_name="incident_id",
                hover_data=["title", "commander"],
                category_orders={"severity": SEVERITIES},
                title="Detect → contain (hours)",
            )
            st.plotly_chart(fig, use_container_width=True)

    with intake:
        st.subheader("Report an incident")
        with st.form("intake"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Title", placeholder="e.g. Suspicious login from contractor VPN")
                category = st.selectbox("Category", CATEGORIES)
                severity = st.selectbox("Severity", SEVERITIES, index=2)
                commander = st.text_input("Commander", placeholder="e.g. Alex Rivera · SecOps")
            with c2:
                reporter = st.text_input("Reporter", placeholder="e.g. SOC (alert)")
                affected = st.text_input("Affected systems", placeholder="e.g. VPN gateway, AD")
                users = st.number_input("Affected users", 0, 100000, 0)
                notify_req = st.checkbox("Regulatory notification required")
            description = st.text_area("Initial description")
            if st.form_submit_button("Create incident"):
                if not title.strip() or not commander.strip():
                    st.error("Title and commander are required.")
                else:
                    n = len(st.session_state.ir_incidents) + 1
                    now = _now()
                    add = {
                        "incident_id": f"INC-2026-{n:03d}",
                        "title": title.strip(),
                        "category": category,
                        "severity": severity,
                        "phase": "Detect",
                        "commander": commander.strip(),
                        "reporter": reporter.strip() or "Manual",
                        "detected": now,
                        "triaged": pd.NaT,
                        "contained": pd.NaT,
                        "eradicated": pd.NaT,
                        "recovered": pd.NaT,
                        "closed": pd.NaT,
                        "affected_systems": affected.strip() or "TBD",
                        "affected_users": int(users),
                        "data_exposure": description.strip() or "Under investigation.",
                        "pii": False,
                        "regulatory": "TBD",
                        "root_cause": "Under investigation.",
                        "containment_summary": "",
                        "playbook": "TBD",
                        "after_action": "",
                        "notify_required": bool(notify_req),
                        "notified": False,
                        "lessons": "",
                        "evidence": [],
                        "open_actions": [],
                    }
                    _save_inc(
                        pd.concat(
                            [st.session_state.ir_incidents, pd.DataFrame([add])],
                            ignore_index=True,
                        )
                    )
                    st.success(f"INC-2026-{n:03d} created in Detect phase.")
                    st.rerun()

    with export:
        st.subheader("Export")
        out = filtered.copy()
        for col in ("detected", "triaged", "contained", "eradicated", "recovered", "closed"):
            out[col] = out[col].apply(_fmt)
        for col in ("evidence", "open_actions"):
            if col in out.columns:
                out = out.drop(columns=[col])
        demo_kit.csv_download(out, "incidents.csv", label="Download incidents")
        out_c = comms[comms["incident_id"].isin(filtered["incident_id"])].copy()
        out_c["timestamp"] = out_c["timestamp"].apply(_fmt)
        demo_kit.csv_download(out_c, "incident_comms.csv", label="Download comms log", key="comms_csv")
        st.caption("Resample rebuilds the demo set. Edits live in this browser session only.")


if __name__ == "__main__":
    main()
