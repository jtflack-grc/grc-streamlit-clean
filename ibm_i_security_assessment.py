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
    "FND-IBMI-006",
    "FND-IBMI-007",
    "FND-IBMI-011",
    "FND-IBMI-013",
    "FND-IBMI-014",
}
_SYNC_KEY = "_ibmi_assess_v2"

REDBOOKS = [
    {"id": "SG24-8150", "title": "IBM i Security Guide", "use": "System values, QSECURITY, passwords"},
    {"id": "SC41-5302", "title": "IBM i Security Reference", "use": "QAUDJRN entry types, system values"},
    {"id": "SG24-7806", "title": "IBM i PowerHA / HA security notes", "use": "Replication exposure"},
    {"id": "REDP-5460", "title": "IBM i and PCI DSS considerations", "use": "Cardholder data on midrange"},
    {"id": "SG24-6326", "title": "IBM i and network security", "use": "Exit points, TCP servers"},
    {"id": "WHITE-FORTRA", "title": "IBM i security assessment practices (industry)", "use": "Domain RAG scoring pattern"},
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
                "site": "NorthStack colo A · cage 12",
                "os": "IBM i 7.5 TR5",
                "role": "Production ERP / JDE World",
                "qsecurity": 40,
                "serial": "78A3XYZ",
                "partition": "1",
                "cpu_pct": 62,
                "storage_pct": 71,
                "profiles": 1842,
                "allobj_count": 14,
                "default_pwd": 47,
                "exit_coverage_pct": 10,
                "crown_jewel": True,
                "owner": "IBM i Ops · M. Reyes",
                "linked": "AST-2026-005 · KRI-2026-001 · INC-2026-001",
            },
            {
                "lpar_id": "LPAR-DEVBOX",
                "name": "DEVBOX",
                "host": "NSK-IBMI-02",
                "site": "NorthStack colo A · cage 12",
                "os": "IBM i 7.4 TR11",
                "role": "Dev / QA · weekly prod refresh",
                "qsecurity": 30,
                "serial": "78A3XYZ",
                "partition": "2",
                "cpu_pct": 28,
                "storage_pct": 44,
                "profiles": 410,
                "allobj_count": 22,
                "default_pwd": 31,
                "exit_coverage_pct": 0,
                "crown_jewel": False,
                "owner": "DevOps · J. Park",
                "linked": "Change freeze · PB-2026-002",
            },
            {
                "lpar_id": "LPAR-HA",
                "name": "HAREPL",
                "host": "NSK-IBMI-03",
                "site": "NorthStack colo B (DR) · cage 3",
                "os": "IBM i 7.5 TR5",
                "role": "HA target / PowerHA",
                "qsecurity": 40,
                "serial": "78B9QRS",
                "partition": "1",
                "cpu_pct": 18,
                "storage_pct": 68,
                "profiles": 1801,
                "allobj_count": 11,
                "default_pwd": 40,
                "exit_coverage_pct": 10,
                "crown_jewel": True,
                "owner": "BCP · IBM i Ops",
                "linked": "DST-2026-001 · BCP RPO · RC.RP-03",
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
                "lane": "SST / service tools",
                "text": "DST password last rotated 2025-04 after Orbit AMS remote. Dual-control CHGDSTPWD still not enforced — FND-IBMI-013 due in 3 days.",
            },
            {
                "lane": "Prior scan delta",
                "text": "vs SCAN-IBMI-2026-078 (60 days ago): overall −4 pts. Exit-point coverage unchanged; *ALLOBJ count rose 11→14 after PAYBATCH grant.",
            },
            {
                "lane": "90-day ask",
                "text": "Exit-point log-only → enforce; fix PAYMAST; *ALLOBJ reduction; QAUDLVL + 90-day receivers; QPWDLVL impact on JDE.",
            },
        ]
    )

    # Object authority samples (DSPOBJAUT style)
    objects = pd.DataFrame(
        [
            {"library": "PAYLIB", "object": "PAYMAST", "type": "*FILE", "owner": "PAYOWNER", "public": "*CHANGE", "autl": "*NONE", "objaud": "*NONE", "risk": "Critical", "finding_id": "FND-IBMI-006", "notes": "Payroll master — any interactive user"},
            {"library": "PAYLIB", "object": "PAYHIST", "type": "*FILE", "owner": "PAYOWNER", "public": "*USE", "autl": "*NONE", "objaud": "*CHANGE", "risk": "High", "finding_id": "FND-IBMI-006", "notes": "History readable"},
            {"library": "JDFLIB", "object": "F0005", "type": "*FILE", "owner": "JDEOWNER", "public": "*USE", "autl": "JDE_AL", "objaud": "*CHANGE", "risk": "Medium", "finding_id": "", "notes": "JDE World UDC"},
            {"library": "QGPL", "object": "PAYFIX", "type": "*PGM", "owner": "QPGMR", "public": "*USE", "autl": "*NONE", "objaud": "*NONE", "risk": "High", "finding_id": "FND-IBMI-014", "notes": "Orphan CL in QGPL"},
            {"library": "QGPL", "object": "TMPPAY", "type": "*FILE", "owner": "QPGMR", "public": "*ALL", "autl": "*NONE", "objaud": "*NONE", "risk": "Critical", "finding_id": "FND-IBMI-014", "notes": "Temp file left public"},
            {"library": "APPLIB", "object": "CUSTMAST", "type": "*FILE", "owner": "APPOWNER", "public": "*EXCLUDE", "autl": "APP_AL", "objaud": "*CHANGE", "risk": "Low", "finding_id": "", "notes": "OK pattern"},
            {"library": "QSYS", "object": "QCMD", "type": "*CMD", "owner": "QSYS", "public": "*USE", "autl": "*NONE", "objaud": "*NONE", "risk": "Info", "finding_id": "", "notes": "Expected"},
            {"library": "HRLIB", "object": "EMPSSN", "type": "*FILE", "owner": "HROWNER", "public": "*USE", "autl": "*NONE", "objaud": "*NONE", "risk": "High", "finding_id": "", "notes": "SSN data — tighten"},
            {"library": "BKULIB", "object": "SAVFPROD", "type": "*FILE", "owner": "BACKUPOP", "public": "*USE", "autl": "*NONE", "objaud": "*NONE", "risk": "Medium", "finding_id": "", "notes": "Save file readable"},
            {"library": "PAYLIB", "object": "PAYBAT", "type": "*PGM", "owner": "PAYOWNER", "public": "*USE", "autl": "PAYROLL_AL", "objaud": "*ALL", "risk": "Medium", "finding_id": "", "notes": "Adopted owner USRPRF"},
        ]
    )

    # IFS / NetServer shares
    ifs_shares = pd.DataFrame(
        [
            {"path": "/payroll", "share_name": "PAYROLL", "public": "RW", "guest": False, "mapped_users": 18, "risk": "Critical", "finding_id": "FND-IBMI-007", "notes": "Night crew SMB map"},
            {"path": "/home", "share_name": "HOME", "public": "R", "guest": False, "mapped_users": 120, "risk": "Medium", "finding_id": "FND-IBMI-015", "notes": "7 world-writable dirs under"},
            {"path": "/jde/export", "share_name": "JDEEXP", "public": "RW", "guest": False, "mapped_users": 9, "risk": "High", "finding_id": "", "notes": "Finance extracts"},
            {"path": "/tmp/orbit", "share_name": "ORBIT", "public": "RW", "guest": True, "mapped_users": 2, "risk": "Critical", "finding_id": "", "notes": "Vendor Orbit AMS leftover"},
            {"path": "/backup/nightly", "share_name": "BKUNITE", "public": "R", "guest": False, "mapped_users": 3, "risk": "Medium", "finding_id": "", "notes": "Tape room staging"},
        ]
    )

    # Network listeners
    listeners = pd.DataFrame(
        [
            {"port": 23, "service": "Telnet", "state": "*ACTIVE", "tls": False, "source_restrict": "JUMP-DMZ-03 only (claimed)", "risk": "High", "finding_id": "FND-IBMI-010"},
            {"port": 21, "service": "FTP", "state": "*ACTIVE", "tls": False, "source_restrict": "None", "risk": "Critical", "finding_id": "FND-IBMI-002"},
            {"port": 446, "service": "DDM / DRDA", "state": "*ACTIVE", "tls": True, "source_restrict": "HA peer", "risk": "Medium", "finding_id": ""},
            {"port": 8471, "service": "as-database (ODBC)", "state": "*ACTIVE", "tls": False, "source_restrict": "None", "risk": "Critical", "finding_id": "FND-IBMI-002"},
            {"port": 8476, "service": "as-signon", "state": "*ACTIVE", "tls": False, "source_restrict": "Corporate VPN", "risk": "Medium", "finding_id": ""},
            {"port": 992, "service": "Telnet TLS", "state": "*INACTIVE", "tls": True, "source_restrict": "—", "risk": "High", "finding_id": "FND-IBMI-010"},
            {"port": 445, "service": "NetServer SMB", "state": "*ACTIVE", "tls": False, "source_restrict": "Colo VLAN", "risk": "Critical", "finding_id": "FND-IBMI-007"},
        ]
    )

    # Command evidence packs
    evidence_cmds = pd.DataFrame(
        [
            {"evidence_id": "EVD-IBMI-001", "finding_id": "FND-IBMI-001", "command": "DSPUSRPRF USRPRF(*ALL) TYPE(*BASIC)", "captured": today - timedelta(days=1), "result_summary": "14 profiles with *ALLOBJ; OPSNIGHT last used yesterday", "operator": "M. Reyes"},
            {"evidence_id": "EVD-IBMI-002", "finding_id": "FND-IBMI-002", "command": "WRKREGINF EXITPNT(*ALL)", "captured": today - timedelta(days=1), "result_summary": "FTP/ODBC/Telnet/NetServer/RMTCMD unregistered", "operator": "SecEng"},
            {"evidence_id": "EVD-IBMI-003", "finding_id": "FND-IBMI-003", "command": "ANZDFTPWD OUTPUT(*OUTFILE)", "captured": today - timedelta(days=2), "result_summary": "47 default/known passwords; QUSER/QTCP included", "operator": "IAM"},
            {"evidence_id": "EVD-IBMI-004", "finding_id": "FND-IBMI-005", "command": "DSPSYSVAL SYSVAL(QAUDLVL)", "captured": today - timedelta(days=1), "result_summary": "*SECURITY *AUTFAIL only — no *NETCMN *PGMADP", "operator": "SOC"},
            {"evidence_id": "EVD-IBMI-005", "finding_id": "FND-IBMI-006", "command": "DSPOBJAUT OBJ(PAYLIB/PAYMAST) OBJTYPE(*FILE)", "captured": today, "result_summary": "*PUBLIC *CHANGE; no AUTL", "operator": "AppSec"},
            {"evidence_id": "EVD-IBMI-006", "finding_id": "FND-IBMI-007", "command": "GO NETS → Work with shares", "captured": today - timedelta(days=1), "result_summary": "/payroll share Public RW; 18 mapped sessions", "operator": "IBM i Ops"},
            {"evidence_id": "EVD-IBMI-007", "finding_id": "FND-IBMI-011", "command": "WRKJRNA JRN(QAUDJRN)", "captured": today - timedelta(days=2), "result_summary": "Receivers deleted after 14 days; MNGRCV(*SYSTEM)", "operator": "SOC"},
            {"evidence_id": "EVD-IBMI-008", "finding_id": "FND-IBMI-013", "command": "CHGDSTPWD (attempt log)", "captured": today - timedelta(days=5), "result_summary": "Last successful DST change 2025-04-18; no dual control", "operator": "IBM i Ops"},
            {"evidence_id": "EVD-IBMI-009", "finding_id": "FND-IBMI-010", "command": "NETSTAT *CNN", "captured": today - timedelta(days=1), "result_summary": "Port 23 active from JUMP-DMZ-03; 992 inactive", "operator": "Network"},
            {"evidence_id": "EVD-IBMI-010", "finding_id": "FND-IBMI-014", "command": "DSPOBJD OBJ(QGPL/*ALL) OBJTYPE(*ALL)", "captured": today - timedelta(days=3), "result_summary": "PAYFIX *PGM + TMPPAY *FILE public in QGPL", "operator": "App owners"},
        ]
    )

    # SST / DST dual-control log
    sst_log = pd.DataFrame(
        [
            {"event_id": "SST-2025-0418", "when": today - timedelta(days=503), "action": "CHGDSTPWD", "requester": "Orbit AMS tech", "approver": "— (none)", "dual_control": False, "notes": "Vendor remote — FND-IBMI-013 root cause"},
            {"event_id": "SST-2026-0112", "when": today - timedelta(days=234), "action": "DST sign-on", "requester": "M. Reyes", "approver": "N/A", "dual_control": False, "notes": "Disk cleanup"},
            {"event_id": "SST-2026-0620", "when": today - timedelta(days=75), "action": "DST sign-on", "requester": "Vendor HW", "approver": "— (none)", "dual_control": False, "notes": "HMC assist"},
            {"event_id": "SST-2026-0828", "when": today - timedelta(days=6), "action": "DST sign-on attempt", "requester": "Unknown", "approver": "Blocked?", "dual_control": False, "notes": "Failed PW — investigate"},
            {"event_id": "SST-POLICY", "when": today, "action": "Policy draft", "requester": "GRC", "approver": "CISO", "dual_control": True, "notes": "Dual-control CHGDSTPWD — not yet live"},
        ]
    )

    # Remediation tickets
    tickets = pd.DataFrame(
        [
            {"ticket_id": "CHG-IBMI-4412", "finding_id": "FND-IBMI-002", "title": "Register exit programs log-only (FTP/ODBC/Telnet)", "status": "In change CAB", "owner": "SecEng", "due": today + timedelta(days=14), "effort": "L"},
            {"ticket_id": "CHG-IBMI-4418", "finding_id": "FND-IBMI-006", "title": "PAYMAST *PUBLIC *EXCLUDE + PAYROLL_AL", "status": "Ready", "owner": "AppSec", "due": today + timedelta(days=5), "effort": "M"},
            {"ticket_id": "CHG-IBMI-4420", "finding_id": "FND-IBMI-007", "title": "Remove /payroll public share; named ACL", "status": "Blocked — night crew", "owner": "Facilities", "due": today + timedelta(days=7), "effort": "M"},
            {"ticket_id": "CHG-IBMI-4421", "finding_id": "FND-IBMI-005", "title": "QAUDLVL add *NETCMN *PGMADP", "status": "Scheduled IPL window", "owner": "IBM i Ops", "due": today + timedelta(days=7), "effort": "S"},
            {"ticket_id": "CHG-IBMI-4425", "finding_id": "FND-IBMI-001", "title": "Retire OPSNIGHT; named night profiles", "status": "HR + Ops workshop", "owner": "IAM", "due": today + timedelta(days=14), "effort": "L"},
            {"ticket_id": "CHG-IBMI-4430", "finding_id": "FND-IBMI-013", "title": "Rotate DST + dual-control procedure", "status": "Open", "owner": "IBM i Ops", "due": today + timedelta(days=3), "effort": "S"},
            {"ticket_id": "CHG-IBMI-4433", "finding_id": "FND-IBMI-011", "title": "QAUDJRN 90-day receiver archive", "status": "Storage quote", "owner": "SOC", "due": today + timedelta(days=25), "effort": "M"},
            {"ticket_id": "CHG-IBMI-4440", "finding_id": "FND-IBMI-003", "title": "ANZDFTPWD remediation wave 1", "status": "In progress", "owner": "IAM", "due": today + timedelta(days=10), "effort": "M"},
        ]
    )

    # Prior scan history
    hist = pd.DataFrame(
        [
            {"scan_id": "SCAN-IBMI-2026-040", "as_of": today - timedelta(days=180), "overall": 48, "critical": 5, "exit_gap": 9},
            {"scan_id": "SCAN-IBMI-2026-061", "as_of": today - timedelta(days=120), "overall": 51, "critical": 4, "exit_gap": 9},
            {"scan_id": "SCAN-IBMI-2026-078", "as_of": today - timedelta(days=60), "overall": 56, "critical": 3, "exit_gap": 9},
            {"scan_id": "SCAN-IBMI-2026-091", "as_of": today, "overall": int(domains["score"].mean()), "critical": 3, "exit_gap": 9},
        ]
    )

    deep = {
        "FND-IBMI-001": {
            "memo": "OPSNIGHT exists because colo night crew shares a single 5250 session binder. CMP-2026-001 huddles cannot attribute actions.",
            "counterfactual": "If portal stuffing had used OPSNIGHT, QAUDJRN PW entries would not identify a person.",
            "commands": ["DSPUSRPRF OPSNIGHT", "DSPOBJAUT OBJ(OPSNIGHT) OBJTYPE(*USRPRF)"],
        },
        "FND-IBMI-002": {
            "memo": "Exit-point SOW drafted; Legal reviewing 'log-only 30 days' vs enforce. JUMP-DMZ-03 ODBC from Finance still unmanaged.",
            "counterfactual": "SafeNet-style registration would have blocked anonymous FTP pulls of PAYMAST during INC-2026-009 window.",
            "commands": ["WRKREGINF", "DSPEXITPGM EXITPNT(QIBM_QTMF_SERVER_REQ)"],
        },
        "FND-IBMI-007": {
            "memo": "Facilities says night crew needs RW for shift checklists. Alternative: named share + MFA ACS — blocked on schedule.",
            "counterfactual": "Ransomware via NetServer would encrypt /payroll with no pattern alert today.",
            "commands": ["GO NETS", "WRKLNK OBJ('/payroll')"],
        },
    }

    scan_meta = {
        "scan_id": "SCAN-IBMI-2026-091",
        "as_of": today,
        "primary_lpar": "PRODBOX",
        "prior_scan": "SCAN-IBMI-2026-078",
        "delta_pts": int(domains["score"].mean()) - 56,
        "tool_pattern": "Security Scan–style domain assessment (synthetic)",
        "assessor": "GRC · IBM i security (sample)",
        "overall_score": int(domains["score"].mean()),
        "overall_rag": _rag(float(domains["score"].mean())),
        "references": "SG24-8150 · SC41-5302 · CIS IBM i V7R5 · COBIT DSS05 · SG24-6326",
        "duration_min": 12,
        "method": "Non-intrusive config collect (demo) — no live WRKREGINF",
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
        objects,
        ifs_shares,
        listeners,
        evidence_cmds,
        sst_log,
        tickets,
        hist,
        deep,
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
        "ibmi_objects",
        "ibmi_ifs",
        "ibmi_listeners",
        "ibmi_evidence",
        "ibmi_sst",
        "ibmi_tickets",
        "ibmi_hist",
        "ibmi_deep",
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


def _finding_card(row, *, widget_key: str, deep: dict | None = None, evidence: pd.DataFrame | None = None, tickets: pd.DataFrame | None = None):
    st.markdown(f"### {row['finding_id']} · {row['title']}")
    a, b, c, d = st.columns(4)
    a.metric("Severity", row["severity"])
    b.metric("Domain", row["domain_id"])
    c.metric("Status", row["status"])
    d.metric("Due", _fmt(row["due"]))
    st.write(row["detail"])
    c1, c2 = st.columns(2)
    c1.write(f"**Evidence cmd:** {row['evidence']}")
    c1.write(f"**Owner:** {row['owner']} · **LPAR:** {row['lpar_id']}")
    c1.write(f"**Linked:** {row['linked']}")
    c2.write(f"**Remediation:** {row['remediation']}")
    c2.write(f"**CIS:** {row['cis']} · **Redbook:** {row['redbook']}")
    c2.write(f"**ISO 27001:** {row['iso27001']} · **SOC 2:** {row['soc2']} · **PCI:** {row['pci']}")

    fid = row["finding_id"]
    if deep and fid in deep:
        with st.expander("Program memo / counterfactual", expanded=False):
            st.write(f"**Memo:** {deep[fid].get('memo', '')}")
            st.write(f"**Without fix:** {deep[fid].get('counterfactual', '')}")
            if deep[fid].get("commands"):
                st.write("**Reproduce:** " + " · ".join(f"`{c}`" for c in deep[fid]["commands"]))
    if evidence is not None and not evidence.empty:
        ev = evidence[evidence["finding_id"] == fid]
        if not ev.empty:
            with st.expander("Captured command evidence", expanded=False):
                st.dataframe(
                    ev.assign(captured=ev["captured"].map(_fmt)),
                    use_container_width=True,
                    hide_index=True,
                )
    if tickets is not None and not tickets.empty:
        tk = tickets[tickets["finding_id"] == fid]
        if not tk.empty:
            with st.expander("Remediation tickets", expanded=False):
                st.dataframe(tk.assign(due=tk["due"].map(_fmt)), use_container_width=True, hide_index=True)


def main() -> None:
    portfolio_skin.page_header(
        title="IBM i Security Assessment",
        lede="LPAR posture workbench — Security Scan–style domains, QAUDJRN, exit points, object authorities, IFS shares, SST dual-control, CIS/Redbook baselines, and ISO/SOC 2/PCI crosswalks. Synthetic PRODBOX / NorthStack data.",
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
        objects,
        ifs_shares,
        listeners,
        evidence,
        sst_log,
        tickets,
        hist,
        deep,
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
    open_tk = int(tickets["status"].apply(lambda s: s not in {"Closed", "Done"}).sum())
    pub_crit = int((objects["risk"] == "Critical").sum())

    k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)
    k1.metric("Overall score", f"{overall}%", delta=f"{scan_meta.get('delta_pts', 0):+d} vs prior")
    k2.metric("Critical", crit)
    k3.metric("High", high)
    k4.metric("Exit gaps", exit_gap)
    k5.metric("Baseline drift", drift)
    k6.metric("Open tickets", open_tk)
    k7.metric("Critical objects", pub_crit)
    k8.metric("CIS ready", f"{cis_ready:.0f}%")

    if overall < 55:
        st.error(
            f"Scan {scan_meta['scan_id']} — {scan_meta['primary_lpar']} is Red overall "
            f"({scan_meta.get('delta_pts', 0):+d} vs {scan_meta.get('prior_scan', 'prior')}). "
            "Network/exit points and IFS public shares dominate residual risk."
        )
    elif crit:
        st.warning(f"{crit} critical findings open — treat *ALLOBJ, exit points, and PAYMAST before board packet.")

    (
        work,
        domains_tab,
        findings_tab,
        sys_tab,
        obj_tab,
        exit_tab,
        aud_tab,
        sst_tab,
        cross_tab,
        base_tab,
        board_tab,
        export_tab,
    ) = st.tabs(
        [
            "Workbench",
            "Scan domains",
            "Findings",
            "System values",
            "Objects / IFS",
            "Exit points",
            "QAUDJRN",
            "SST / service tools",
            "Crosswalk",
            "Baseline / CIS",
            "Board brief",
            "Export",
        ]
    )

    with work:
        st.subheader("IBM i posture workbench")
        st.caption(
            f"**{scan_meta['scan_id']}** · {_fmt(scan_meta['as_of'])} · ~{scan_meta.get('duration_min', 10)} min · "
            f"{scan_meta['tool_pattern']} · Refs: {scan_meta['references']}"
        )
        _domain_pillars(domains)

        st.markdown("**Executive narrative**")
        for _, n in narrative.iterrows():
            st.write(f"**{n['lane']}:** {n['text']}")

        st.markdown("---")
        st.markdown("**Remediation queue**")
        for _, t in tickets.sort_values("due").iterrows():
            flag = " · BLOCKED" if "Blocked" in str(t["status"]) else ""
            with st.expander(f"{t['ticket_id']} · {t['title']} · {_fmt(t['due'])}{flag}"):
                st.write(f"**Finding:** {t['finding_id']} · **Owner:** {t['owner']} · **Status:** {t['status']} · **Effort:** {t['effort']}")

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
            fig = px.line(hist, x="as_of", y="overall", markers=True, title="Overall score trend (prior scans)")
            fig.update_layout(height=360)
            st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_hist")

        st.markdown("**LPARs**")
        st.dataframe(lpars, use_container_width=True, hide_index=True)

        st.markdown(f"**Featured findings ({len(FEATURED_FINDINGS)})**")
        pref = [
            "FND-IBMI-001",
            "FND-IBMI-002",
            "FND-IBMI-003",
            "FND-IBMI-006",
            "FND-IBMI-007",
            "FND-IBMI-011",
            "FND-IBMI-013",
            "FND-IBMI-014",
        ]
        feat = findings[findings["finding_id"].isin(FEATURED_FINDINGS)].copy()
        feat["_o"] = feat["finding_id"].map(lambda x: pref.index(x) if x in pref else 99)
        for _, row in feat.sort_values("_o").iterrows():
            st.markdown("---")
            _finding_card(row, widget_key=f"feat_{row['finding_id']}", deep=deep, evidence=evidence, tickets=tickets)

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
        search = st.text_input("Search findings", placeholder="PAYMAST, exit, *ALLOBJ…", key="ibmi_fnd_search")
        show = view_f
        if search.strip():
            q = search.strip().lower()
            show = show[show.apply(lambda r: q in " ".join(str(v).lower() for v in r), axis=1)]
        st.dataframe(
            show[
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
            ].assign(due=show["due"].map(_fmt)),
            use_container_width=True,
            hide_index=True,
        )
        if not show.empty:
            pick = st.selectbox("Drill into finding", show["finding_id"].tolist(), key="fnd_pick")
            row = show[show["finding_id"] == pick].iloc[0]
            _finding_card(row, widget_key="drill", deep=deep, evidence=evidence, tickets=tickets)

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

    with obj_tab:
        st.subheader("Object authorities & IFS / NetServer")
        st.caption("DSPOBJAUT-style crown-jewel sample + NetServer shares — public authority is the midrange classic miss.")
        st.markdown("**Libraries / objects**")
        st.dataframe(objects, use_container_width=True, hide_index=True)
        hot = objects[objects["risk"].isin(["Critical", "High"])]
        st.warning(f"{len(hot)} objects Critical/High — PAYMAST and QGPL orphans lead.")

        st.markdown("**IFS / NetServer shares**")
        st.dataframe(ifs_shares, use_container_width=True, hide_index=True)
        fig = px.bar(ifs_shares, x="share_name", y="mapped_users", color="risk", title="Mapped sessions by share")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ibmi_ifs")

        st.markdown("**Command evidence register**")
        st.dataframe(
            evidence.assign(captured=evidence["captured"].map(_fmt)),
            use_container_width=True,
            hide_index=True,
        )

    with exit_tab:
        st.subheader("Network exit points & listeners")
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

        st.markdown("**TCP listeners (NETSTAT-style)**")
        st.dataframe(listeners, use_container_width=True, hide_index=True)

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

    with sst_tab:
        st.subheader("SST / DST service tools")
        st.caption("Dual-control for CHGDSTPWD is policy-draft only — last real rotation was vendor Orbit AMS in 2025-04.")
        st.dataframe(
            sst_log.assign(when=sst_log["when"].map(_fmt)),
            use_container_width=True,
            hide_index=True,
        )
        bad = sst_log[~sst_log["dual_control"]]
        st.error(f"{len(bad)} of {len(sst_log)} SST events lack dual control — including the password change that still stands.")
        with st.expander("Recommended dual-control procedure (sample)"):
            st.write(
                "1. Ticket + CAB for CHGDSTPWD · 2. Two operators present (Ops + Security) · "
                "3. Log event_id in GRC · 4. Rotate after any vendor remote · 5. Test DST sign-on under change window."
            )

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

        st.markdown("**Prior scan history**")
        st.dataframe(hist.assign(as_of=hist["as_of"].map(_fmt)), use_container_width=True, hide_index=True)

    with board_tab:
        st.subheader("Board / CISO brief — IBM i")
        st.markdown(
            f"**Scan:** {scan_meta['scan_id']} on **{scan_meta['primary_lpar']}** "
            f"({_fmt(scan_meta['as_of'])}) · Overall **{overall}% ({scan_meta['overall_rag']})** · "
            f"Δ {scan_meta.get('delta_pts', 0):+d} vs {scan_meta.get('prior_scan', 'prior')}"
        )
        st.markdown("#### Headline")
        st.write(
            f"IBM i production LPAR **PRODBOX** (JDE World / NorthStack) scores **{overall}%**. "
            f"**{crit} critical** and **{high} high** findings. "
            f"**{exit_gap}** network exit points unregistered — FTP/ODBC/Telnet/NetServer effectively open "
            f"to any authenticated profile. Payroll file **PAYMAST** is *PUBLIC *CHANGE; "
            f"IFS **/payroll** share is world-writable. DST password unchanged since Orbit AMS remote (2025-04)."
        )
        st.markdown("#### Domain RAG")
        for _, r in domains.iterrows():
            st.write(f"- **{r['domain']}:** {r['rag']} {r['score']}% ({int(r['fails'])} fails) — {r['benchmark']}")
        st.markdown("#### Top asks (30 days)")
        for fid in ["FND-IBMI-001", "FND-IBMI-002", "FND-IBMI-006", "FND-IBMI-007", "FND-IBMI-005", "FND-IBMI-013"]:
            row = findings[findings["finding_id"] == fid].iloc[0]
            st.write(f"- **{fid}** ({row['severity']}): {row['title']}")
        st.markdown("#### Change tickets in flight")
        for _, t in tickets.head(6).iterrows():
            st.write(f"- **{t['ticket_id']}** [{t['status']}]: {t['title']}")
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
            "CMP-2026-001 · DST-2026-001 · AST-2026-005 · Orbit AMS · PayrollCo"
        )

    with export_tab:
        st.subheader("Export")
        demo_kit.csv_download(findings.assign(due=findings["due"].map(_fmt)), "ibmi_findings.csv", label="Download findings")
        demo_kit.csv_download(domains, "ibmi_domain_scores.csv", label="Download domain scores")
        demo_kit.csv_download(sysvals, "ibmi_system_values.csv", label="Download system values")
        demo_kit.csv_download(exits, "ibmi_exit_points.csv", label="Download exit points")
        demo_kit.csv_download(objects, "ibmi_object_authorities.csv", label="Download object authorities")
        demo_kit.csv_download(ifs_shares, "ibmi_ifs_shares.csv", label="Download IFS shares")
        demo_kit.csv_download(evidence.assign(captured=evidence["captured"].map(_fmt)), "ibmi_command_evidence.csv", label="Download command evidence")
        demo_kit.csv_download(tickets.assign(due=tickets["due"].map(_fmt)), "ibmi_remediation_tickets.csv", label="Download remediation tickets")
        demo_kit.csv_download(sst_log.assign(when=sst_log["when"].map(_fmt)), "ibmi_sst_log.csv", label="Download SST log")
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
                {"metric": "delta_vs_prior", "value": scan_meta.get("delta_pts", 0)},
                {"metric": "critical", "value": crit},
                {"metric": "high", "value": high},
                {"metric": "exit_gaps", "value": exit_gap},
                {"metric": "baseline_drift", "value": drift},
                {"metric": "open_tickets", "value": open_tk},
            ]
        )
        demo_kit.csv_download(summary, "ibmi_executive_summary.csv", label="Download executive summary")


if __name__ == "__main__":
    main()
