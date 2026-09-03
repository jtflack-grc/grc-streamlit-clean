#!/usr/bin/env python3
"""IBM i security assessment workbench — club teaching toy.

Fortra Security Scan–style domain scoring plus Kisco-style exit-point / IFS /
policy-baseline views. Synthetic LPAR posture (PRODBOX / NorthStack) with
QAUDJRN, CIS Benchmark, Redbook, ISO 27001, and SOC 2 crosswalks — not a live
system connection.
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
    page_title="IBM i Security Assessment · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

SCAN_DOMAINS = [
    ("SYS", "Server / system security", "#6366f1"),
    ("USR", "User & password security", "#3b82f6"),
    ("ADM", "Administrative privileges", "#f59e0b"),
    ("NET", "Network access & exit points", "#ef4444"),
    ("PUB", "Public object authority", "#22c55e"),
    ("AUD", "System auditing (QAUDJRN)", "#a855f7"),
    ("IFS", "IFS / malware exposure", "#ec4899"),
]

SEVERITY = ["Critical", "High", "Medium", "Low", "Info"]
FEATURED_FINDINGS = {
    "FND-IBMI-001",
    "FND-IBMI-002",
    "FND-IBMI-003",
    "FND-IBMI-007",
    "FND-IBMI-011",
    "FND-IBMI-014",
}
_SYNC_KEY = "_ibmi_assess_v1"

REDBOOKS = [
    {"id": "SG24-8150", "title": "IBM i Security Guide", "use": "System values, QSECURITY, passwords"},
    {"id": "SC41-5302", "title": "IBM i Security Reference", "use": "QAUDJRN entry types, system values"},
    {"id": "SG24-7806", "title": "IBM i PowerHA / HA security notes", "use": "Replication exposure"},
    {"id": "REDP-5460", "title": "IBM i and PCI DSS considerations", "use": "Cardholder data on midrange"},
]


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _fmt(ts) -> str:
    if ts is None:
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


def _rag(score: float) -> str:
    if score >= 80:
        return "Green"
    if score >= 55:
        return "Yellow"
    return "Red"


def _sample(seed: int):
    today = _today()
    rng = np.random.default_rng(seed)

    lpars = pd.DataFrame(
        [
            {
                "lpar_id": "LPAR-PRODBOX",
                "name": "PRODBOX",
                "host": "NSK-IBMI-01",
                "site": "NorthStack colo A",
                "os": "IBM i 7.5 TR5",
                "role": "Production ERP / JDE World",
                "qsecurity": 40,
                "serial": "78A3XYZ",
                "partition": "1",
                "crown_jewel": True,
                "linked": "AST-2026-005 · KRI-2026-001 · INC-2026-001",
            },
            {
                "lpar_id": "LPAR-DEVBOX",
                "name": "DEVBOX",
                "host": "NSK-IBMI-02",
                "site": "NorthStack colo A",
                "os": "IBM i 7.4 TR11",
                "role": "Dev / QA",
                "qsecurity": 30,
                "serial": "78A3XYZ",
                "partition": "2",
                "crown_jewel": False,
                "linked": "Change freeze exceptions",
            },
            {
                "lpar_id": "LPAR-HA",
                "name": "HAREPL",
                "host": "NSK-IBMI-03",
                "site": "NorthStack colo B (DR)",
                "os": "IBM i 7.5 TR5",
                "role": "HA target",
                "qsecurity": 40,
                "serial": "78B9QRS",
                "partition": "1",
                "crown_jewel": True,
                "linked": "DST-2026-001 · BCP RPO",
            },
        ]
    )

    domains = pd.DataFrame(
        [
            {"domain_id": "SYS", "domain": "Server / system security", "score": 72, "checks": 18, "fails": 5, "benchmark": "CIS IBM i 7.5 · SG24-8150"},
            {"domain_id": "USR", "domain": "User & password security", "score": 58, "checks": 22, "fails": 9, "benchmark": "CIS · QPWDLVL 3"},
            {"domain_id": "ADM", "domain": "Administrative privileges", "score": 41, "checks": 14, "fails": 8, "benchmark": "Least privilege · *ALLOBJ"},
            {"domain_id": "NET", "domain": "Network access & exit points", "score": 34, "checks": 16, "fails": 11, "benchmark": "Exit point / SafeNet pattern"},
            {"domain_id": "PUB", "domain": "Public object authority", "score": 49, "checks": 12, "fails": 6, "benchmark": "*PUBLIC *EXCLUDE"},
            {"domain_id": "AUD", "domain": "System auditing (QAUDJRN)", "score": 63, "checks": 15, "fails": 5, "benchmark": "QAUDCTL *AUDLVL · SC41-5302"},
            {"domain_id": "IFS", "domain": "IFS / malware exposure", "score": 38, "checks": 10, "fails": 6, "benchmark": "IFS ransomware / NetServer"},
        ]
    )
    domains["rag"] = domains["score"].map(_rag)

    findings = [
        {
            "finding_id": "FND-IBMI-001",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "ADM",
            "severity": "Critical",
            "title": "*ALLOBJ on 14 profiles including night-ops shared ID",
            "detail": "QSECOFR + 13 named/service profiles hold *ALLOBJ. OPSNIGHT shared ID used by colo night crew — last sign-on 2026-08-29.",
            "evidence": "DSPUSRPRF *ALL · SPCAUT filter",
            "cis": "1.4.x Privileged access",
            "iso27001": "A.5.15 · A.8.2",
            "soc2": "CC6.1 · CC6.3",
            "pci": "7.1 · 8.2",
            "redbook": "SG24-8150 Ch. special authorities",
            "remediation": "Break glass for QSECOFR; replace OPSNIGHT with named *JOBCTL + adopted authority; weekly *ALLOBJ attestation.",
            "owner": "IBM i Ops · Security",
            "status": "Open",
            "due": today + timedelta(days=14),
            "linked": "CMP-2026-001 · DE.CM-03 · KRI-2026-001",
        },
        {
            "finding_id": "FND-IBMI-002",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "NET",
            "severity": "Critical",
            "title": "No exit programs on FTP / ODBC / Remote Command",
            "detail": "QIBM_QTMF_SERVER_REQ, QIBM_QZDA_SQL1/SQL2, and QIBM_QTG_DEVINIT unregistered. Any authenticated profile can FTP/ODBC without secondary control.",
            "evidence": "WRKREGINF · DSPEXITPGM",
            "cis": "3.x Network services",
            "iso27001": "A.8.20 · A.8.21",
            "soc2": "CC6.6 · CC6.7",
            "pci": "1.3 · 8.3",
            "redbook": "SG24-8150 exit point security",
            "remediation": "Deploy exit-point firewall in log-only 30 days then enforce; SIEM feed for rejected requests.",
            "owner": "Security Engineering",
            "status": "In progress",
            "due": today + timedelta(days=21),
            "linked": "INC-2026-001 · JUMP-DMZ-03",
        },
        {
            "finding_id": "FND-IBMI-003",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "USR",
            "severity": "High",
            "title": "47 profiles with default passwords (*NONE / known IBM defaults)",
            "detail": "Includes QUSER, QTCP, and vendor install IDs. ANZDFTPWD not reviewed since 2025-11.",
            "evidence": "ANZDFTPWD · DSPUSRPRF",
            "cis": "1.2 Password policy",
            "iso27001": "A.5.17",
            "soc2": "CC6.1",
            "pci": "8.3.6",
            "redbook": "SG24-8150 password defaults",
            "remediation": "Disable unused IBM defaults; set *NONE where interactive not required; force change on first use.",
            "owner": "IAM / IBM i Ops",
            "status": "Open",
            "due": today + timedelta(days=10),
            "linked": "PR.AA-01 · PR.AA-05",
        },
        {
            "finding_id": "FND-IBMI-004",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "SYS",
            "severity": "High",
            "title": "QPWDLVL = 2 (recommend 3 for long passwords)",
            "detail": "Password level 2 limits length/complexity. CIS IBM i 7.5 prefers level 3 where applications allow.",
            "evidence": "DSPSYSVAL QPWDLVL",
            "cis": "1.2.1",
            "iso27001": "A.5.17",
            "soc2": "CC6.1",
            "pci": "8.3.6",
            "redbook": "SG24-8150 QPWDLVL",
            "remediation": "Impact analysis on JDE World 5250 clients; stage QPWDLVL 3 on DEVBOX then PRODBOX.",
            "owner": "IBM i Ops",
            "status": "Open",
            "due": today + timedelta(days=45),
            "linked": "JDE World CNC",
        },
        {
            "finding_id": "FND-IBMI-005",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "AUD",
            "severity": "High",
            "title": "QAUDLVL missing *NETCMN and *PGMADP",
            "detail": "QAUDCTL=*AUDLVL active but QAUDLVL lacks network command and program adoption events — portal stuffing forensics thin.",
            "evidence": "DSPSYSVAL QAUDCTL · QAUDLVL · QAUDLVL2",
            "cis": "5.1 Auditing",
            "iso27001": "A.8.15 · A.8.16",
            "soc2": "CC7.2",
            "pci": "10.2",
            "redbook": "SC41-5302 audit journal",
            "remediation": "Add *NETCMN *PGMADP *AUTFAIL *SECURITY; extend receiver retention to 90 days.",
            "owner": "SOC · IBM i Ops",
            "status": "In progress",
            "due": today + timedelta(days=7),
            "linked": "INC-2026-001 · RS.MA-02 · KRI-2026-002",
        },
        {
            "finding_id": "FND-IBMI-006",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "PUB",
            "severity": "High",
            "title": "*PUBLIC *CHANGE on PAYLIB/PAYMAST",
            "detail": "Payroll master file public change authority — PayrollCo IR adjacent; any interactive user can update.",
            "evidence": "DSPOBJAUT PAYLIB/PAYMAST *FILE",
            "cis": "2.1 Object authority",
            "iso27001": "A.8.3 · A.5.15",
            "soc2": "CC6.1",
            "pci": "7.2",
            "redbook": "SG24-8150 resource security",
            "remediation": "Set *PUBLIC *EXCLUDE; grant via authorization list PAYROLL_AL; journal file.",
            "owner": "AppSec · Payroll",
            "status": "Open",
            "due": today + timedelta(days=5),
            "linked": "INC-2026-009 · PayrollCo",
        },
        {
            "finding_id": "FND-IBMI-007",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "IFS",
            "severity": "Critical",
            "title": "NetServer share /payroll with *PUBLIC RW — no ransomware pattern monitor",
            "detail": "IFS path /payroll exported; night crew maps via SMB. No pattern matching for mass rename/encrypt.",
            "evidence": "GO NETS · WRKLNK '/payroll'",
            "cis": "4.x IFS",
            "iso27001": "A.8.9 · A.8.10",
            "soc2": "CC6.6",
            "pci": "1.2",
            "redbook": "SG24-8150 IFS",
            "remediation": "Remove public share; named ACL; enable IFS activity pattern alerts.",
            "owner": "Facilities · IBM i Ops",
            "status": "Open",
            "due": today + timedelta(days=7),
            "linked": "CMP-2026-001 · WAV-2026-004",
        },
        {
            "finding_id": "FND-IBMI-008",
            "lpar_id": "LPAR-DEVBOX",
            "domain_id": "SYS",
            "severity": "High",
            "title": "QSECURITY=30 on DEVBOX with prod-like data refresh",
            "detail": "Weekly refresh from PRODBOX includes PAYMAST subset; integrity protection off at level 30.",
            "evidence": "DSPSYSVAL QSECURITY",
            "cis": "1.1.1",
            "iso27001": "A.8.1 · A.8.11",
            "soc2": "CC6.1",
            "pci": "6.4",
            "redbook": "SG24-8150 QSECURITY",
            "remediation": "Mask PII on refresh; raise DEVBOX to 40 after regression; or scrubbed library only.",
            "owner": "DevOps · Privacy",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "PB-2026-002",
        },
        {
            "finding_id": "FND-IBMI-009",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "USR",
            "severity": "Medium",
            "title": "112 inactive profiles (>90 days) still enabled",
            "detail": "Includes contractors and terminated warehouse leads. LASTUSED beyond 90 days.",
            "evidence": "DSPUSRPRF · ANZPRFACT",
            "cis": "1.3 Account lifecycle",
            "iso27001": "A.5.18",
            "soc2": "CC6.2",
            "pci": "8.2.6",
            "redbook": "SG24-8150 inactive users",
            "remediation": "*DISABLED + review; integrate HR JML feed.",
            "owner": "IAM",
            "status": "In progress",
            "due": today + timedelta(days=20),
            "linked": "PR.AA-05",
        },
        {
            "finding_id": "FND-IBMI-010",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "NET",
            "severity": "High",
            "title": "TELNET open from JUMP-DMZ-03 without TLS enforcement",
            "detail": "5250 via ACS from jump host; QRMTSIGN=*VERIFY; session encryption not forced.",
            "evidence": "NETSTAT *CNN · ACS config",
            "cis": "3.2 Remote access",
            "iso27001": "A.8.20",
            "soc2": "CC6.6",
            "pci": "4.2",
            "redbook": "SG24-8150 remote sign-on",
            "remediation": "Require TLS on ACS; restrict source IP to JUMP-DMZ-03; SIEM on QAUDJRN PW.",
            "owner": "Network · IBM i Ops",
            "status": "Open",
            "due": today + timedelta(days=18),
            "linked": "AST-2026-005 · GAP-2026-001",
        },
        {
            "finding_id": "FND-IBMI-011",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "AUD",
            "severity": "Medium",
            "title": "Audit journal receivers deleted at 14 days — board wants 90",
            "detail": "CHGJRN QAUDJRN MNGRCV(*SYSTEM) with short retention. IR cannot reconstruct portal stuffing beyond 2 weeks.",
            "evidence": "WRKJRNA QAUDJRN",
            "cis": "5.2 Retention",
            "iso27001": "A.8.15",
            "soc2": "CC7.2",
            "pci": "10.5",
            "redbook": "SC41-5302 receiver management",
            "remediation": "Detach to archive ASP / SIEM; 90-day online + 1-year cold.",
            "owner": "SOC · Storage",
            "status": "Open",
            "due": today + timedelta(days=25),
            "linked": "KRI-2026-002",
        },
        {
            "finding_id": "FND-IBMI-012",
            "lpar_id": "LPAR-HA",
            "domain_id": "SYS",
            "severity": "Medium",
            "title": "HAREPL QAUDCTL=*NONE during replication window",
            "detail": "Ops disables auditing on HA target to save CPU during sync — forensic gap if failover.",
            "evidence": "DSPSYSVAL QAUDCTL on HAREPL",
            "cis": "5.1",
            "iso27001": "A.8.15",
            "soc2": "CC7.2",
            "pci": "10.2",
            "redbook": "SC41-5302",
            "remediation": "Keep *AUDLVL on HA; size receivers; document exception if temporary.",
            "owner": "IBM i Ops · BCP",
            "status": "Open",
            "due": today + timedelta(days=14),
            "linked": "DST-2026-001 · RC.RP-03",
        },
        {
            "finding_id": "FND-IBMI-013",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "ADM",
            "severity": "Medium",
            "title": "Service tools (SST/DST) password not rotated post-contractor",
            "detail": "QSECOFR service tools password last changed 2025-04. Vendor remote support left without rotation.",
            "evidence": "SST password change log",
            "cis": "1.5 Service tools",
            "iso27001": "A.5.17 · A.8.2",
            "soc2": "CC6.1",
            "pci": "8.2",
            "redbook": "SG24-8150 SST/DST",
            "remediation": "Rotate SST; dual control; log CHGDSTPWD.",
            "owner": "IBM i Ops",
            "status": "Open",
            "due": today + timedelta(days=3),
            "linked": "—",
        },
        {
            "finding_id": "FND-IBMI-014",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "PUB",
            "severity": "High",
            "title": "Library QGPL *PUBLIC *USE with custom production objects",
            "detail": "Custom CL and PF objects left in QGPL after migrations — world-readable.",
            "evidence": "DSPOBJD QGPL/*ALL",
            "cis": "2.2",
            "iso27001": "A.8.3",
            "soc2": "CC6.1",
            "pci": "7.2",
            "redbook": "SG24-8150 libraries",
            "remediation": "Move to APP_PROD; *PUBLIC *EXCLUDE; delete orphans.",
            "owner": "App owners",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "PR.PS-01",
        },
        {
            "finding_id": "FND-IBMI-015",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "IFS",
            "severity": "Medium",
            "title": "IFS /home world-writable directories (7)",
            "detail": "User home directories with *PUBLIC W — ransomware staging risk.",
            "evidence": "WRKLNK audit",
            "cis": "4.2",
            "iso27001": "A.8.9",
            "soc2": "CC6.6",
            "pci": "2.2",
            "redbook": "SG24-8150 IFS authorities",
            "remediation": "Fix authorities; monitor mass change patterns.",
            "owner": "IBM i Ops",
            "status": "Open",
            "due": today + timedelta(days=21),
            "linked": "—",
        },
        {
            "finding_id": "FND-IBMI-016",
            "lpar_id": "LPAR-PRODBOX",
            "domain_id": "NET",
            "severity": "Medium",
            "title": "ODBC DSN from Finance laptops using QUSER",
            "detail": "Shared QUSER for Excel/ODBC extracts from PAYLIB — no row-level controls.",
            "evidence": "Exit-point gap · job logs",
            "cis": "3.3",
            "iso27001": "A.8.3 · A.5.15",
            "soc2": "CC6.1",
            "pci": "7.1",
            "redbook": "SG24-8150 database server",
            "remediation": "Named service profiles; exit program allow-list; retire QUSER interactive.",
            "owner": "Finance IT · Security",
            "status": "Open",
            "due": today + timedelta(days=35),
            "linked": "PayrollCo · FND-IBMI-006",
        },
    ]
    findings_df = pd.DataFrame(findings)

    sysvals = pd.DataFrame(
        [
            {"name": "QSECURITY", "current": "40", "recommended": "40 or 50", "status": "Pass", "domain_id": "SYS", "cis": "1.1.1", "redbook": "SG24-8150"},
            {"name": "QPWDLVL", "current": "2", "recommended": "3", "status": "Fail", "domain_id": "USR", "cis": "1.2.1", "redbook": "SG24-8150"},
            {"name": "QPWDMINLEN", "current": "8", "recommended": "≥8", "status": "Pass", "domain_id": "USR", "cis": "1.2.2", "redbook": "SG24-8150"},
            {"name": "QPWDEXPITV", "current": "90", "recommended": "≤90", "status": "Pass", "domain_id": "USR", "cis": "1.2.3", "redbook": "SG24-8150"},
            {"name": "QMAXSIGN", "current": "5", "recommended": "≤5", "status": "Pass", "domain_id": "USR", "cis": "1.2.4", "redbook": "SG24-8150"},
            {"name": "QINACTITV", "current": "60", "recommended": "≤30", "status": "Fail", "domain_id": "USR", "cis": "1.2.5", "redbook": "SG24-8150"},
            {"name": "QAUDCTL", "current": "*AUDLVL", "recommended": "*AUDLVL *OBJAUD", "status": "Partial", "domain_id": "AUD", "cis": "5.1.1", "redbook": "SC41-5302"},
            {"name": "QAUDLVL", "current": "*SECURITY *AUTFAIL", "recommended": "+ *NETCMN *PGMADP", "status": "Fail", "domain_id": "AUD", "cis": "5.1.2", "redbook": "SC41-5302"},
            {"name": "QALWOBJRST", "current": "*ALL", "recommended": "*ALWPGMADP *ALWPTF", "status": "Fail", "domain_id": "SYS", "cis": "1.1.3", "redbook": "SG24-8150"},
            {"name": "QFRCCVNRST", "current": "0", "recommended": "≥1", "status": "Fail", "domain_id": "SYS", "cis": "1.1.4", "redbook": "SG24-8150"},
            {"name": "QLMTSECOFR", "current": "0", "recommended": "1", "status": "Fail", "domain_id": "ADM", "cis": "1.4.2", "redbook": "SG24-8150"},
            {"name": "QRMTSIGN", "current": "*VERIFY", "recommended": "*VERIFY / reject", "status": "Partial", "domain_id": "NET", "cis": "3.2.1", "redbook": "SG24-8150"},
            {"name": "QVFYOBJRST", "current": "3", "recommended": "3", "status": "Pass", "domain_id": "SYS", "cis": "1.1.5", "redbook": "SG24-8150"},
            {"name": "QDSPSGNINF", "current": "0", "recommended": "1", "status": "Fail", "domain_id": "USR", "cis": "1.2.6", "redbook": "SG24-8150"},
        ]
    )

    exit_points = pd.DataFrame(
        [
            {"exit_point": "QIBM_QTMF_SERVER_REQ", "server": "FTP Server", "registered": False, "mode": "None", "risk": "Critical", "notes": "FTP unrestricted"},
            {"exit_point": "QIBM_QTMF_CLIENT_REQ", "server": "FTP Client", "registered": False, "mode": "None", "risk": "High", "notes": "Outbound FTP"},
            {"exit_point": "QIBM_QZDA_SQL1", "server": "Database server", "registered": False, "mode": "None", "risk": "Critical", "notes": "ODBC/JDBC"},
            {"exit_point": "QIBM_QZDA_SQL2", "server": "Database server init", "registered": False, "mode": "None", "risk": "Critical", "notes": "ODBC init"},
            {"exit_point": "QIBM_QTG_DEVINIT", "server": "Telnet device init", "registered": False, "mode": "None", "risk": "High", "notes": "5250"},
            {"exit_point": "QIBM_QSO_ACCEPT", "server": "Sockets accept", "registered": False, "mode": "None", "risk": "Medium", "notes": "Raw sockets"},
            {"exit_point": "QIBM_QFILESVR_SERVER", "server": "File Server / NetServer", "registered": False, "mode": "None", "risk": "Critical", "notes": "SMB / IFS"},
            {"exit_point": "QIBM_QCN_INET_RMTCMD", "server": "Remote Command", "registered": False, "mode": "None", "risk": "Critical", "notes": "REXEC-style"},
            {"exit_point": "QIBM_QTMX_SERVER_REQ", "server": "DDM / DRDA", "registered": True, "mode": "Log only", "risk": "Medium", "notes": "Vendor installed stub"},
            {"exit_point": "QIBM_QNPS_ENTRY", "server": "Network print", "registered": False, "mode": "None", "risk": "Low", "notes": "Print servers"},
        ]
    )

    priv_profiles = pd.DataFrame(
        [
            {"profile": "QSECOFR", "spcaut": "*ALLOBJ *SECADM *SAVSYS *IOSYSCFG *SERVICE *AUDIT *JOBCTL *SPLCTL", "status": "*ENABLED", "last_used": today - timedelta(days=2), "issue": "Break-glass not dual-control"},
            {"profile": "OPSNIGHT", "spcaut": "*ALLOBJ *JOBCTL", "status": "*ENABLED", "last_used": today - timedelta(days=1), "issue": "Shared night-crew ID"},
            {"profile": "QSYSOPR", "spcaut": "*JOBCTL *SAVSYS", "status": "*ENABLED", "last_used": today, "issue": "OK — monitor"},
            {"profile": "PAYBATCH", "spcaut": "*ALLOBJ", "status": "*ENABLED", "last_used": today - timedelta(days=3), "issue": "Batch needs adopted authority instead"},
            {"profile": "VNDORBIT", "spcaut": "*ALLOBJ *IOSYSCFG", "status": "*ENABLED", "last_used": today - timedelta(days=40), "issue": "Vendor Orbit AMS — revoke"},
            {"profile": "QUSER", "spcaut": "*NONE", "status": "*ENABLED", "last_used": today, "issue": "ODBC shared use"},
            {"profile": "BACKUPOP", "spcaut": "*SAVSYS *JOBCTL", "status": "*ENABLED", "last_used": today - timedelta(days=1), "issue": "OK"},
            {"profile": "QPGMR", "spcaut": "*JOBCTL", "status": "*ENABLED", "last_used": today - timedelta(days=12), "issue": "Dev use on prod?"},
        ]
    )

    aud_days = pd.date_range(end=today, periods=30, freq="D")
    aud_types = ["AF", "PW", "SV", "JS", "CO", "DO", "OM", "ZC", "CA"]
    audit_volume = []
    for d in aud_days:
        for t in aud_types:
            base = {"AF": 40, "PW": 25, "SV": 8, "JS": 120, "CO": 15, "DO": 10, "OM": 6, "ZC": 30, "CA": 12}[t]
            audit_volume.append({"day": d, "entry_type": t, "count": int(max(0, rng.normal(base, base * 0.25)))})
    for t in ["PW", "AF"]:
        audit_volume.append({"day": today - timedelta(days=16), "entry_type": t, "count": 890 if t == "PW" else 340})
    audit_df = pd.DataFrame(audit_volume)

    crosswalk_df = pd.DataFrame(
        [
            {
                "finding_id": f["finding_id"],
                "title": f["title"][:50],
                "iso27001": f["iso27001"],
                "soc2": f["soc2"],
                "pci": f["pci"],
                "cis": f["cis"],
                "severity": f["severity"],
            }
            for f in findings
        ]
    )

    frameworks = pd.DataFrame(
        [
            {"framework": "CIS IBM i 7.5", "in_scope": 96, "passing": 54, "failing": 28, "partial": 14},
            {"framework": "ISO 27001:2022", "in_scope": 42, "passing": 22, "failing": 12, "partial": 8},
            {"framework": "SOC 2 TSC", "in_scope": 28, "passing": 15, "failing": 8, "partial": 5},
            {"framework": "PCI DSS 4.0", "in_scope": 31, "passing": 14, "failing": 11, "partial": 6},
            {"framework": "NIST CSF 2.0", "in_scope": 24, "passing": 11, "failing": 9, "partial": 4},
            {"framework": "COBIT 2019", "in_scope": 18, "passing": 10, "failing": 5, "partial": 3},
        ]
    )
    frameworks["readiness_pct"] = (frameworks["passing"] / frameworks["in_scope"] * 100).round(1)

    baseline = pd.DataFrame(
        [
            {"control": "QSECURITY", "baseline": "40", "current": "40", "drift": False, "last_change": today - timedelta(days=120)},
            {"control": "QPWDLVL", "baseline": "3", "current": "2", "drift": True, "last_change": today - timedelta(days=400)},
            {"control": "QAUDLVL", "baseline": "*SECURITY *AUTFAIL *NETCMN *PGMADP", "current": "*SECURITY *AUTFAIL", "drift": True, "last_change": today - timedelta(days=16)},
            {"control": "Exit: FTP", "baseline": "Enforce", "current": "None", "drift": True, "last_change": None},
            {"control": "Exit: ODBC", "baseline": "Log+Enforce", "current": "None", "drift": True, "last_change": None},
            {"control": "*ALLOBJ count", "baseline": "≤5", "current": "14", "drift": True, "last_change": today - timedelta(days=3)},
            {"control": "Default passwords", "baseline": "0", "current": "47", "drift": True, "last_change": today - timedelta(days=200)},
            {"control": "IFS /payroll share", "baseline": "No public", "current": "Public RW", "drift": True, "last_change": today - timedelta(days=60)},
            {"control": "QAUDJRN retention", "baseline": "90 days", "current": "14 days", "drift": True, "last_change": today - timedelta(days=14)},
            {"control": "QLMTSECOFR", "baseline": "1", "current": "0", "drift": True, "last_change": today - timedelta(days=500)},
        ]
    )

    narrative = pd.DataFrame(
        [
            {
                "lane": "Scan verdict",
                "text": "PRODBOX overall 52% — Red on network/exit points, IFS, and admin privileges. QSECURITY 40 alone is not a secure server.",
            },
            {
                "lane": "Incident truth",
                "text": "INC-2026-001 portal stuffing exposed missing *NETCMN auditing; IBM i night crew never saw email (CMP-2026-001 huddles).",
            },
            {
                "lane": "Crown jewel",
                "text": "PAYLIB/PAYMAST *PUBLIC *CHANGE + NetServer /payroll share — PayrollCo-adjacent blast radius. KRI-2026-001 still off target.",
            },
            {
                "lane": "90-day ask",
                "text": "Exit-point log-only → enforce; fix PAYMAST; *ALLOBJ reduction; QAUDLVL + 90-day receivers; QPWDLVL impact on JDE.",
            },
        ]
    )

    scan_meta = {
        "scan_id": "SCAN-IBMI-2026-091",
        "as_of": today,
        "primary_lpar": "PRODBOX",
        "tool_pattern": "Security Scan–style domain assessment (synthetic)",
        "assessor": "GRC · IBM i security (sample)",
        "overall_score": int(domains["score"].mean()),
        "overall_rag": _rag(float(domains["score"].mean())),
        "references": "SG24-8150 · SC41-5302 · CIS IBM i V7R5 · COBIT DSS05",
    }

    return (
        lpars,
        domains,
        findings_df,
        sysvals,
        exit_points,
        priv_profiles,
        audit_df,
        crosswalk_df,
        frameworks,
        baseline,
        narrative,
        scan_meta,
        pd.DataFrame(REDBOOKS),
    )


def _sync(seed: int):
    keys = [
        "ibmi_lpars",
        "ibmi_domains",
        "ibmi_findings",
        "ibmi_sysvals",
        "ibmi_exits",
        "ibmi_priv",
        "ibmi_audit",
        "ibmi_crosswalk",
        "ibmi_frameworks",
        "ibmi_baseline",
        "ibmi_narrative",
        "ibmi_scan_meta",
        "ibmi_redbooks",
    ]
    need = st.session_state.get(_SYNC_KEY) != seed or "ibmi_findings" not in st.session_state
    if need:
        for k, v in zip(keys, _sample(seed)):
            st.session_state[k] = v
        st.session_state[_SYNC_KEY] = seed
    return tuple(st.session_state[k] for k in keys)


def _domain_pillars(domains: pd.DataFrame):
    cols = st.columns(len(domains))
    for col, (_, row) in zip(cols, domains.iterrows()):
        with col:
            st.markdown(f"**{row['domain_id']}**")
            st.progress(min(1.0, row["score"] / 100))
            st.caption(f"{row['rag']} {row['score']}% · {int(row['fails'])} fails")


def _finding_card(row, *, widget_key: str):
    st.markdown(f"### {row['finding_id']} · {row['title']}")
    a, b, c, d = st.columns(4)
    a.metric("Severity", row["severity"])
    b.metric("Domain", row["domain_id"])
    c.metric("Status", row["status"])
    d.metric("Due", _fmt(row["due"]))
    st.write(row["detail"])
    c1, c2 = st.columns(2)
    c1.write(f"**Evidence:** {row['evidence']}")
    c1.write(f"**Owner:** {row['owner']} · **LPAR:** {row['lpar_id']}")
    c1.write(f"**Linked:** {row['linked']}")
    c2.write(f"**Remediation:** {row['remediation']}")
    c2.write(f"**CIS:** {row['cis']} · **Redbook:** {row['redbook']}")
    c2.write(f"**ISO 27001:** {row['iso27001']} · **SOC 2:** {row['soc2']} · **PCI:** {row['pci']}")


def main() -> None:
    portfolio_skin.page_header(
        title="IBM i Security Assessment",
        lede="LPAR posture workbench — Security Scan–style domains, QAUDJRN, exit points, privileged profiles, CIS/Redbook baselines, and ISO/SOC 2/PCI crosswalks. Synthetic PRODBOX / NorthStack data.",
        kicker="IBM i · Midrange",
    )

    seed = demo_kit.seed_controls()
    (
        lpars,
        domains,
        findings,
        sysvals,
        exits,
        priv,
        audit_df,
        crosswalk,
        frameworks,
        baseline,
        narrative,
        scan_meta,
        redbooks,
    ) = _sync(seed)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Scan scope")
    lpar_opts = ["All LPARs"] + lpars["name"].tolist()
    lpar_pick = st.sidebar.selectbox("LPAR", lpar_opts, index=1)
    sev_f = st.sidebar.multiselect("Severities", SEVERITY, default=["Critical", "High", "Medium"])
    open_only = st.sidebar.checkbox("Open / in progress only", value=True)
    st.sidebar.caption("Sample assessment — not connected to a live IBM i.")

    view_f = findings.copy()
    if lpar_pick != "All LPARs":
        lid = lpars[lpars["name"] == lpar_pick]["lpar_id"].iloc[0]
        view_f = view_f[view_f["lpar_id"] == lid]
    view_f = view_f[view_f["severity"].isin(sev_f)]
    if open_only:
        view_f = view_f[view_f["status"].isin(["Open", "In progress"])]

    overall = scan_meta["overall_score"]
    crit = int((findings["severity"] == "Critical").sum())
    high = int((findings["severity"] == "High").sum())
    exit_gap = int((~exits["registered"]).sum())
    drift = int(baseline["drift"].sum())
    cis_ready = float(frameworks[frameworks["framework"].str.contains("CIS")]["readiness_pct"].iloc[0])

    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
    k1.metric("Overall score", f"{overall}%", delta=scan_meta["overall_rag"])
    k2.metric("Critical findings", crit)
    k3.metric("High findings", high)
    k4.metric("Exit points open", exit_gap)
    k5.metric("Baseline drift", drift)
    k6.metric("LPARs in scope", len(lpars))
    k7.metric("CIS readiness", f"{cis_ready:.0f}%")

    if overall < 55:
        st.error(
            f"Scan {scan_meta['scan_id']} — {scan_meta['primary_lpar']} is Red overall. "
            "Network/exit points and IFS public shares dominate residual risk."
        )
    elif crit:
        st.warning(f"{crit} critical findings open — treat *ALLOBJ, exit points, and PAYMAST before board packet.")

    work, domains_tab, findings_tab, sys_tab, exit_tab, aud_tab, cross_tab, base_tab, board_tab, export_tab = st.tabs(
        [
            "Workbench",
            "Scan domains",
            "Findings",
            "System values",
            "Exit points",
            "QAUDJRN",
            "Crosswalk",
            "Baseline / CIS",
            "Board brief",
            "Export",
        ]
    )

    with work:
        st.subheader("IBM i posture workbench")
        st.caption(
            f"**{scan_meta['scan_id']}** · {_fmt(scan_meta['as_of'])} · {scan_meta['tool_pattern']} · "
            f"Refs: {scan_meta['references']}"
        )
        _domain_pillars(domains)

        st.markdown("**Executive narrative**")
        for _, n in narrative.iterrows():
            st.write(f"**{n['lane']}:** {n['text']}")

        st.markdown("---")
        c1, c2 = st.columns([1.1, 1])
        with c1:
            fig = px.bar(
                domains,
                x="domain_id",
                y="score",
                color="rag",
                color_discrete_map={"Green": "#22c55e", "Yellow": "#f59e0b", "Red": "#ef4444"},
                text="score",
                title="Domain scores (Security Scan–style)",
            )
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(yaxis_range=[0, 105], height=360)
            st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_domains")
        with c2:
            fig = px.bar(
                frameworks,
                x="framework",
                y="readiness_pct",
                color="readiness_pct",
                title="Framework readiness (% passing)",
            )
            fig.update_layout(height=360, xaxis_tickangle=-25)
            st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_fw")

        st.markdown("**LPARs**")
        st.dataframe(lpars, use_container_width=True, hide_index=True)

        st.markdown(f"**Featured findings ({len(FEATURED_FINDINGS)})**")
        pref = ["FND-IBMI-001", "FND-IBMI-002", "FND-IBMI-003", "FND-IBMI-007", "FND-IBMI-011", "FND-IBMI-014"]
        feat = findings[findings["finding_id"].isin(FEATURED_FINDINGS)].copy()
        feat["_o"] = feat["finding_id"].map(lambda x: pref.index(x) if x in pref else 99)
        for _, row in feat.sort_values("_o").iterrows():
            st.markdown("---")
            _finding_card(row, widget_key=f"feat_{row['finding_id']}")

    with domains_tab:
        st.subheader("Scan domains")
        st.caption("Seven assessment areas aligned to common IBM i Security Scan report sections.")
        st.dataframe(domains, use_container_width=True, hide_index=True)
        for _, row in domains.iterrows():
            with st.expander(f"{row['domain_id']} · {row['domain']} · {row['rag']} {row['score']}%"):
                st.write(f"**Checks:** {int(row['checks'])} · **Fails:** {int(row['fails'])}")
                st.write(f"**Benchmark:** {row['benchmark']}")
                sub = findings[findings["domain_id"] == row["domain_id"]]
                st.dataframe(
                    sub[["finding_id", "severity", "title", "status", "due"]].assign(due=sub["due"].map(_fmt)),
                    use_container_width=True,
                    hide_index=True,
                )

    with findings_tab:
        st.subheader("Finding register")
        st.dataframe(
            view_f[
                [
                    "finding_id",
                    "lpar_id",
                    "domain_id",
                    "severity",
                    "title",
                    "status",
                    "owner",
                    "due",
                    "iso27001",
                    "soc2",
                ]
            ].assign(due=view_f["due"].map(_fmt)),
            use_container_width=True,
            hide_index=True,
        )
        if not view_f.empty:
            pick = st.selectbox("Drill into finding", view_f["finding_id"].tolist(), key="fnd_pick")
            row = view_f[view_f["finding_id"] == pick].iloc[0]
            _finding_card(row, widget_key="drill")

        by_sev = findings.groupby("severity").size().reset_index(name="count")
        fig = px.bar(by_sev, x="severity", y="count", color="severity", title="Findings by severity")
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_sev")

    with sys_tab:
        st.subheader("System values vs recommended")
        st.caption("QSECURITY, password, audit, and restore-related values — Redbook SG24-8150 / SC41-5302.")
        st.dataframe(sysvals, use_container_width=True, hide_index=True)
        fig = px.pie(sysvals, names="status", title="System value status mix", hole=0.4)
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_sysval")
        st.markdown("**Privileged profiles (*ALLOBJ and friends)**")
        st.dataframe(priv.assign(last_used=priv["last_used"].map(_fmt)), use_container_width=True, hide_index=True)

    with exit_tab:
        st.subheader("Network exit points")
        st.caption(
            "Exit-point firewall view (SafeNet-style): visibility and control over FTP, ODBC, Telnet, "
            "NetServer, Remote Command — without changing QSECURITY."
        )
        st.dataframe(exits, use_container_width=True, hide_index=True)
        open_e = exits[~exits["registered"]]
        st.error(f"{len(open_e)} of {len(exits)} network servers have no exit program registered.")
        fig = px.bar(
            exits,
            x="server",
            color="risk",
            color_discrete_map={"Critical": "#ef4444", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#6b7280"},
            title="Exit point risk by server",
            hover_data=["exit_point", "mode", "notes", "registered"],
        )
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_exit")

    with aud_tab:
        st.subheader("QAUDJRN activity (synthetic)")
        st.caption("Spike on PW/AF ~day −16 aligns with portal stuffing narrative (INC-2026-001).")
        daily = audit_df.groupby(["day", "entry_type"], as_index=False)["count"].sum()
        fig = px.area(daily, x="day", y="count", color="entry_type", title="Audit journal entries by type")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_aud")
        legend = pd.DataFrame(
            [
                {"type": "AF", "meaning": "Authority failure"},
                {"type": "PW", "meaning": "Password / sign-on"},
                {"type": "SV", "meaning": "System value change"},
                {"type": "JS", "meaning": "Job start"},
                {"type": "CO", "meaning": "Create object"},
                {"type": "DO", "meaning": "Delete object"},
                {"type": "OM", "meaning": "Object management"},
                {"type": "ZC", "meaning": "Object change (audited)"},
                {"type": "CA", "meaning": "Authority change"},
            ]
        )
        st.dataframe(legend, use_container_width=True, hide_index=True)
        st.warning("Receiver retention currently 14 days (FND-IBMI-011) — insufficient for board IR reconstruct.")

    with cross_tab:
        st.subheader("Compliance crosswalk")
        st.caption("Each finding mapped to CIS, ISO 27001, SOC 2, and PCI — reuse evidence across audits.")
        st.dataframe(crosswalk, use_container_width=True, hide_index=True)
        st.markdown("**Framework readiness**")
        st.dataframe(frameworks, use_container_width=True, hide_index=True)
        melt = frameworks.melt(
            id_vars=["framework"],
            value_vars=["passing", "failing", "partial"],
            var_name="state",
            value_name="count",
        )
        fig = px.bar(melt, x="framework", y="count", color="state", barmode="stack", title="Control states by framework")
        fig.update_layout(height=360, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_cross_stack")
        st.markdown("**Authoritative references (Redbooks / manuals)**")
        st.dataframe(redbooks, use_container_width=True, hide_index=True)

    with base_tab:
        st.subheader("Security policy baseline")
        st.caption("Desired hardened baseline vs current — drift drives alerts (iSecMap-style).")
        show_b = baseline.copy()
        show_b["last_change"] = show_b["last_change"].map(_fmt)
        st.dataframe(show_b, use_container_width=True, hide_index=True)
        drifted = baseline[baseline["drift"]]
        st.error(f"{len(drifted)} controls drifted from baseline — including exit points and *ALLOBJ count.")
        adhere = 100 - (drift / max(len(baseline), 1) * 100)
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=adhere,
                title={"text": "Baseline adherence %"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#38e881"},
                    "steps": [
                        {"range": [0, 55], "color": "#7f1d1d"},
                        {"range": [55, 80], "color": "#92400e"},
                        {"range": [80, 100], "color": "#14532d"},
                    ],
                },
            )
        )
        fig.update_layout(height=280)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_baseline_gauge")

    with board_tab:
        st.subheader("Board / CISO brief — IBM i")
        st.markdown(
            f"**Scan:** {scan_meta['scan_id']} on **{scan_meta['primary_lpar']}** "
            f"({_fmt(scan_meta['as_of'])}) · Overall **{overall}% ({scan_meta['overall_rag']})**"
        )
        st.markdown("#### Headline")
        st.write(
            f"IBM i production LPAR **PRODBOX** (JDE World / NorthStack) scores **{overall}%**. "
            f"**{crit} critical** and **{high} high** findings. "
            f"**{exit_gap}** network exit points unregistered — FTP/ODBC/Telnet/NetServer effectively open "
            f"to any authenticated profile. Payroll file **PAYMAST** is *PUBLIC *CHANGE; "
            f"IFS **/payroll** share is world-writable."
        )
        st.markdown("#### Domain RAG")
        for _, r in domains.iterrows():
            st.write(f"- **{r['domain']}:** {r['rag']} {r['score']}% ({int(r['fails'])} fails) — {r['benchmark']}")
        st.markdown("#### Top asks (30 days)")
        for fid in ["FND-IBMI-001", "FND-IBMI-002", "FND-IBMI-006", "FND-IBMI-007", "FND-IBMI-005"]:
            row = findings[findings["finding_id"] == fid].iloc[0]
            st.write(f"- **{fid}** ({row['severity']}): {row['title']}")
        st.markdown("#### Framework impact")
        st.write(
            f"CIS readiness **{frameworks.iloc[0]['readiness_pct']:.0f}%** · "
            f"ISO **{frameworks.iloc[1]['readiness_pct']:.0f}%** · "
            f"SOC 2 **{frameworks.iloc[2]['readiness_pct']:.0f}%** · "
            f"PCI **{frameworks.iloc[3]['readiness_pct']:.0f}%**."
        )
        st.markdown("#### Linked portfolio")
        st.write(
            "INC-2026-001 · INC-2026-009 · GAP-2026-001 · KRI-2026-001/002 · "
            "CMP-2026-001 · DST-2026-001 · AST-2026-005"
        )

    with export_tab:
        st.subheader("Export")
        demo_kit.csv_download(findings.assign(due=findings["due"].map(_fmt)), "ibmi_findings.csv", label="Download findings")
        demo_kit.csv_download(domains, "ibmi_domain_scores.csv", label="Download domain scores")
        demo_kit.csv_download(sysvals, "ibmi_system_values.csv", label="Download system values")
        demo_kit.csv_download(exits, "ibmi_exit_points.csv", label="Download exit points")
        demo_kit.csv_download(crosswalk, "ibmi_crosswalk.csv", label="Download compliance crosswalk")
        demo_kit.csv_download(
            baseline.assign(last_change=baseline["last_change"].map(_fmt)),
            "ibmi_baseline.csv",
            label="Download baseline drift",
        )
        demo_kit.csv_download(frameworks, "ibmi_framework_readiness.csv", label="Download framework readiness")
        summary = pd.DataFrame(
            [
                {"metric": "scan_id", "value": scan_meta["scan_id"]},
                {"metric": "overall_score", "value": overall},
                {"metric": "overall_rag", "value": scan_meta["overall_rag"]},
                {"metric": "critical", "value": crit},
                {"metric": "high", "value": high},
                {"metric": "exit_gaps", "value": exit_gap},
                {"metric": "baseline_drift", "value": drift},
            ]
        )
        demo_kit.csv_download(summary, "ibmi_executive_summary.csv", label="Download executive summary")


if __name__ == "__main__":
    main()
