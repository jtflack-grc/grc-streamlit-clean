#!/usr/bin/env python3
"""Asset / CAASM workbench — club teaching toy.

Modeled loosely on modern CMDB + cyber asset practices (business context,
lifecycle, coverage gaps, source reconciliation) — not a real CMDB.
"""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Asset Management System · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

CLASSES = [
    "Server / LPAR",
    "Mainframe",
    "Network",
    "Endpoint",
    "SaaS / IdP",
    "Application",
    "Database",
    "Jump / bastion",
    "OT / IoT",
    "Cloud workload",
]
LIFECYCLES = ["New", "Active", "Inactive", "Decommissioned", "Ghost (seen / not in CMDB)"]
CRITICALITY = ["Crown jewel", "High", "Medium", "Low"]
MANAGED = ["Managed", "Unmanaged", "Partial"]
ENVS = ["Production", "DR", "Staging", "Dev", "Corp"]

FEATURED = {"AST-2026-001", "AST-2026-002", "AST-2026-005"}


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _sample(seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    today = _today()
    rng = np.random.default_rng(seed)

    def j(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    assets = [
        # ── Featured ─────────────────────────────────────────────────
        {
            "asset_id": "AST-2026-001",
            "name": "IBM i PRODBOX (LPAR SN 065-1042)",
            "asset_class": "Server / LPAR",
            "subtype": "IBM i production LPAR",
            "env": "Production",
            "criticality": "Crown jewel",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "IBM i Ops · D. Marshall",
            "business_owner": "Treasury / ERP Finance",
            "bu": "Finance",
            "location": "Primary DC · Power frame",
            "cmdb_ci": "ci_ibmi_prodbox",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(hours=2),
            "first_seen": today - timedelta(days=1400),
            "sources": "CMDB · QAUDJRN · PAM · HA monitor · ITSM",
            "ip_or_id": "10.20.4.12 / SN 065-1042",
            "data_class": "Confidential — CUSTMAST, settlement",
            "internet_facing": False,
            "edr": True,
            "vuln_scan": True,
            "siem": True,
            "backup": True,
            "mfa_admin": "Partial (PAM; *ALLOBJ exception EXC-2026-011)",
            "linked_bia": "BIA-2026-001, BIA-2026-002",
            "linked_risk": "INC-2026-003 · EXC-2026-011 · EXR-2026-003 · PLN-2026-001",
            "crown_jewel_reason": "Core ledger + O2C system of record. RTO 2h / achievable 6h gap.",
            "summary": "Golden record for production IBM i. Controls mostly covered; privileged break-glass and HA capacity are the live risk themes. CMDB attributes enriched from ops telemetry.",
        },
        {
            "asset_id": "AST-2026-002",
            "name": "VPN Gateway (legacy concentrator)",
            "asset_class": "Network",
            "subtype": "SSL VPN concentrator",
            "env": "Production",
            "criticality": "High",
            "lifecycle": "Active",
            "managed": "Partial",
            "owner": "Infrastructure · Jordan Blake",
            "business_owner": "IT / SecOps",
            "bu": "IT",
            "location": "DMZ · primary edge",
            "cmdb_ci": "ci_vpn_gw_01",
            "cmdb_status": "Stale attributes",
            "last_seen": today - timedelta(hours=1),
            "first_seen": today - timedelta(days=2200),
            "sources": "CMDB · IDS · firewall · EXC register",
            "ip_or_id": "203.0.113.40",
            "data_class": "Internal — auth sessions",
            "internet_facing": True,
            "edr": False,
            "vuln_scan": True,
            "siem": True,
            "backup": False,
            "mfa_admin": "Yes (admin plane) · user MFA via IdP",
            "linked_bia": "BIA-2026-005",
            "linked_risk": "EXC-2026-004 · INC-2026-010 · PLN-2026-005",
            "crown_jewel_reason": "",
            "summary": "Internet-facing privilege path. OS unsupported — time-boxed exception with geo-block / no split-tunnel. Hardware refresh PO in flight (~6 weeks). CMDB OS version field stale.",
        },
        {
            "asset_id": "AST-2026-003",
            "name": "IBM Z sysplex — CICS / DB2",
            "asset_class": "Mainframe",
            "subtype": "z/OS sysplex",
            "env": "Production",
            "criticality": "Crown jewel",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "Mainframe Security · Maya Chen",
            "business_owner": "Treasury",
            "bu": "Finance",
            "location": "Primary DC · raised floor (NorthStack colo)",
            "cmdb_ci": "ci_zos_sysplex_a",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(hours=1),
            "first_seen": today - timedelta(days=3000),
            "sources": "CMDB · SMF · RACF · GDPS · colo vendor",
            "ip_or_id": "sysplex-A",
            "data_class": "Confidential — settlement / CICS",
            "internet_facing": False,
            "edr": False,
            "vuln_scan": False,
            "siem": True,
            "backup": True,
            "mfa_admin": "RACF + PAM for TSO; SPECIAL recert quarterly",
            "linked_bia": "BIA-2026-001",
            "linked_risk": "INC-2026-004 · VND-2026-002 · EXR-2026-003",
            "crown_jewel_reason": "Settlement path with GDPS secondary. No EDR (platform class) — SMF/SIEM is the control story.",
            "summary": "Crown jewel mainframe. Coverage model differs from distributed (no EDR/vuln agent). Colo + RACF SPECIAL lifecycle are the TPRM/IR touchpoints.",
        },
        {
            "asset_id": "AST-2026-004",
            "name": "SAP ECC PRD",
            "asset_class": "Application",
            "subtype": "SAP ECC",
            "env": "Production",
            "criticality": "Crown jewel",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "SAP Basis",
            "business_owner": "ERP Finance · M. Hassan",
            "bu": "Finance",
            "location": "Primary DC · app/DB cluster",
            "cmdb_ci": "ci_sap_ecc_prd",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(hours=3),
            "first_seen": today - timedelta(days=1800),
            "sources": "CMDB · SAP Solution Manager · PAM · ST01",
            "ip_or_id": "sapprd.corp.local",
            "data_class": "Confidential — financials",
            "internet_facing": False,
            "edr": True,
            "vuln_scan": True,
            "siem": True,
            "backup": True,
            "mfa_admin": "PAM for SAP_ALL break-glass",
            "linked_bia": "BIA-2026-002",
            "linked_risk": "INC-2026-006 · EXR-2026-005 · PLN-2026-002",
            "crown_jewel_reason": "Order-to-cash spine with JDE.",
            "summary": "DR landscape exercise scheduled (EXR-2026-005). Break-glass monitoring tightened after INC-2026-006.",
        },
        {
            "asset_id": "AST-2026-005",
            "name": "DMZ jump host JUMP-DMZ-03",
            "asset_class": "Jump / bastion",
            "subtype": "Hardened jump",
            "env": "Production",
            "criticality": "High",
            "lifecycle": "Active",
            "managed": "Partial",
            "owner": "Infrastructure · Jordan Blake",
            "business_owner": "SecOps",
            "bu": "IT",
            "location": "DMZ",
            "cmdb_ci": "",
            "cmdb_status": "Missing from CMDB",
            "last_seen": today - timedelta(hours=4),
            "first_seen": today - timedelta(days=40),
            "sources": "AD · EDR · network discovery (not CMDB)",
            "ip_or_id": "10.50.9.33",
            "data_class": "Internal — admin sessions",
            "internet_facing": False,
            "edr": True,
            "vuln_scan": True,
            "siem": False,
            "backup": False,
            "mfa_admin": "Yes via PAM",
            "linked_bia": "BIA-2026-005",
            "linked_risk": "INC-2026-008 · PBC-2026-003",
            "crown_jewel_reason": "",
            "summary": "Provisioned outside standard build pipeline. SIEM gap closed on siblings; this host still missing SIEM agent and CMDB CI. Classic CAASM coverage + reconciliation finding.",
        },
        {
            "asset_id": "AST-2026-006",
            "name": "JD Edwards World (on PRODBOX)",
            "asset_class": "Application",
            "subtype": "JDE World",
            "env": "Production",
            "criticality": "Crown jewel",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "ERP / Orbit AMS",
            "business_owner": "ERP Finance",
            "bu": "Finance",
            "location": "Runs on AST-2026-001",
            "cmdb_ci": "ci_jde_world_prd",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(hours=2),
            "first_seen": today - timedelta(days=1400),
            "sources": "CMDB · IBM i · AMS tickets",
            "ip_or_id": "app:JDE-WORLD",
            "data_class": "Confidential — O2C",
            "internet_facing": False,
            "edr": False,
            "vuln_scan": False,
            "siem": True,
            "backup": True,
            "mfa_admin": "Via IBM i / PAM",
            "linked_bia": "BIA-2026-002",
            "linked_risk": "INC-2026-005 · VND-2026-003 · EXR-2026-007",
            "crown_jewel_reason": "O2C application of record on IBM i.",
            "summary": "Logical app CI on PRODBOX. IFS permission hygiene is the live control story (INC-2026-005 / Orbit AMS).",
        },
        {
            "asset_id": "AST-2026-007",
            "name": "Customer portal (portal.example.com)",
            "asset_class": "Application",
            "subtype": "Customer web + API",
            "env": "Production",
            "criticality": "High",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "Platform Eng · R. Kim",
            "business_owner": "Digital",
            "bu": "Customer experience",
            "location": "Multi-AZ cloud",
            "cmdb_ci": "ci_portal_prd",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(minutes=30),
            "first_seen": today - timedelta(days=900),
            "sources": "CMDB · WAF · IdP · APM · GitHub deploy",
            "ip_or_id": "portal.example.com",
            "data_class": "Confidential — customer PII (limited)",
            "internet_facing": True,
            "edr": False,
            "vuln_scan": True,
            "siem": True,
            "backup": True,
            "mfa_admin": "IdP; B2C MFA rollout in progress",
            "linked_bia": "BIA-2026-003",
            "linked_risk": "INC-2026-001 · VND-2026-004",
            "crown_jewel_reason": "",
            "summary": "Post credential-stuffing: CAPTCHA + rate-limit on /api/login; WAF /api/* coverage remediating.",
        },
        {
            "asset_id": "AST-2026-008",
            "name": "Azure AD B2C tenant",
            "asset_class": "SaaS / IdP",
            "subtype": "Customer identity",
            "env": "Production",
            "criticality": "High",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "IAM · L. Torres",
            "business_owner": "Platform Eng",
            "bu": "IT",
            "location": "Microsoft cloud",
            "cmdb_ci": "ci_aadb2c",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(hours=1),
            "first_seen": today - timedelta(days=900),
            "sources": "CMDB · IdP admin · TPRM",
            "ip_or_id": "tenant:contoso-b2c",
            "data_class": "Confidential — identities",
            "internet_facing": True,
            "edr": False,
            "vuln_scan": False,
            "siem": True,
            "backup": False,
            "mfa_admin": "Privileged Identity Management",
            "linked_bia": "BIA-2026-003",
            "linked_risk": "VND-2026-004 · INC-2026-001",
            "crown_jewel_reason": "",
            "summary": "Hyperscaler IdP — coverage is config + logging inheritance, not agents.",
        },
        {
            "asset_id": "AST-2026-009",
            "name": "ENGWS-0042 (engineering workstation)",
            "asset_class": "Endpoint",
            "subtype": "Windows workstation",
            "env": "Corp",
            "criticality": "Medium",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "Endpoint mgmt",
            "business_owner": "Engineering",
            "bu": "Engineering",
            "location": "HQ · dock",
            "cmdb_ci": "ci_engws_0042",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(days=14),
            "first_seen": today - timedelta(days=600),
            "sources": "CMDB · EDR · Intune · AD",
            "ip_or_id": "ENGWS-0042",
            "data_class": "Internal — source / build artifacts",
            "internet_facing": False,
            "edr": True,
            "vuln_scan": True,
            "siem": True,
            "backup": False,
            "mfa_admin": "N/A (user MFA)",
            "linked_bia": "",
            "linked_risk": "INC-2026-002",
            "crown_jewel_reason": "",
            "summary": "Ransomware host from INC-2026-002 — re-imaged. Last_seen 14d (user OOO). Watch inactive rule at 30d.",
        },
        {
            "asset_id": "AST-2026-010",
            "name": "\\\\ENG-NAS (engineering file share)",
            "asset_class": "Server / LPAR",
            "subtype": "NAS file share",
            "env": "Production",
            "criticality": "High",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "Infrastructure",
            "business_owner": "Engineering",
            "bu": "Engineering",
            "location": "Primary DC",
            "cmdb_ci": "ci_eng_nas",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(hours=6),
            "first_seen": today - timedelta(days=1100),
            "sources": "CMDB · backup · AD ACL",
            "ip_or_id": "\\\\ENG-NAS",
            "data_class": "Internal — IP / builds",
            "internet_facing": False,
            "edr": False,
            "vuln_scan": True,
            "siem": True,
            "backup": True,
            "mfa_admin": "N/A",
            "linked_bia": "",
            "linked_risk": "INC-2026-002",
            "crown_jewel_reason": "",
            "summary": "Share encryption attempted in ransomware incident; snapshots clean. Tiering of share ACLs still open lesson.",
        },
        {
            "asset_id": "AST-2026-011",
            "name": "JUMP-DMZ-07 (retired tag, still checking in)",
            "asset_class": "Jump / bastion",
            "subtype": "Hardened jump",
            "env": "Production",
            "criticality": "Medium",
            "lifecycle": "Ghost (seen / not in CMDB)",
            "managed": "Unmanaged",
            "owner": "(unowned)",
            "business_owner": "(unowned)",
            "bu": "IT",
            "location": "DMZ",
            "cmdb_ci": "ci_jump_dmz_07 (Retired)",
            "cmdb_status": "Lifecycle conflict",
            "last_seen": today - timedelta(days=2),
            "first_seen": today - timedelta(days=800),
            "sources": "EDR · AD (CMDB says Retired)",
            "ip_or_id": "10.50.9.71",
            "data_class": "Internal",
            "internet_facing": False,
            "edr": True,
            "vuln_scan": False,
            "siem": False,
            "backup": False,
            "mfa_admin": "Unknown",
            "linked_bia": "BIA-2026-005",
            "linked_risk": "",
            "crown_jewel_reason": "",
            "summary": "CMDB Retired / Decommissioned but EDR still sees heartbeats. Classic lifecycle drift — power, license, and attack surface still live.",
        },
        {
            "asset_id": "AST-2026-012",
            "name": "PayrollCo SaaS (logical CI)",
            "asset_class": "SaaS / IdP",
            "subtype": "Payroll processor",
            "env": "Production",
            "criticality": "Crown jewel",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "TPRM · A. Nguyen",
            "business_owner": "Payroll Ops",
            "bu": "HR",
            "location": "Vendor SaaS",
            "cmdb_ci": "ci_payrollco",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(days=1),
            "first_seen": today - timedelta(days=700),
            "sources": "CMDB · TPRM · SSO · API gateway",
            "ip_or_id": "saas:payrollco",
            "data_class": "Restricted — SSN / bank / tax",
            "internet_facing": True,
            "edr": False,
            "vuln_scan": False,
            "siem": True,
            "backup": False,
            "mfa_admin": "Vendor + our SSO",
            "linked_bia": "BIA-2026-004",
            "linked_risk": "INC-2026-009 · VND-2026-001 · PLN-2026-004",
            "crown_jewel_reason": "Pay calendar dependency; PII processor.",
            "summary": "Logical SaaS CI. Processing suspended under IR. Outside-in / TPRM owns residual — not agent coverage.",
        },
        {
            "asset_id": "AST-2026-013",
            "name": "marketing-DB read-replica",
            "asset_class": "Database",
            "subtype": "Postgres read replica",
            "env": "Production",
            "criticality": "Medium",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "Data platform",
            "business_owner": "Marketing",
            "bu": "Marketing",
            "location": "Cloud AZ-b",
            "cmdb_ci": "ci_mkt_db_rr",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(hours=5),
            "first_seen": today - timedelta(days=400),
            "sources": "CMDB · cloud inventory · SIEM",
            "ip_or_id": "mkt-db-rr.internal",
            "data_class": "Confidential — email / display name",
            "internet_facing": False,
            "edr": False,
            "vuln_scan": True,
            "siem": True,
            "backup": True,
            "mfa_admin": "Cloud IAM",
            "linked_bia": "BIA-2026-003",
            "linked_risk": "INC-2026-001",
            "crown_jewel_reason": "",
            "summary": "Connection strings rotated during credential-stuffing incident.",
        },
        {
            "asset_id": "AST-2026-014",
            "name": "Shadow NAS share (guest WLAN discovered)",
            "asset_class": "Server / LPAR",
            "subtype": "Unauthorized SMB share",
            "env": "Production",
            "criticality": "High",
            "lifecycle": "Ghost (seen / not in CMDB)",
            "managed": "Unmanaged",
            "owner": "(unowned)",
            "business_owner": "(unowned)",
            "bu": "Unknown",
            "location": "Plant network / guest adjacency",
            "cmdb_ci": "",
            "cmdb_status": "Missing from CMDB",
            "last_seen": today - timedelta(days=7),
            "first_seen": today - timedelta(days=7),
            "sources": "Network discovery · SOC alert only",
            "ip_or_id": "10.80.2.19",
            "data_class": "Unknown — under review",
            "internet_facing": False,
            "edr": False,
            "vuln_scan": False,
            "siem": False,
            "backup": False,
            "mfa_admin": "None",
            "linked_bia": "",
            "linked_risk": "Related pattern to INC-2026-005",
            "crown_jewel_reason": "",
            "summary": "Discovered SMB share not in CMDB. Quarantined pending owner identification. Example of CAASM 'unknown asset' intake.",
        },
        {
            "asset_id": "AST-2026-015",
            "name": "GDPS secondary sysplex (DR)",
            "asset_class": "Mainframe",
            "subtype": "z/OS DR sysplex",
            "env": "DR",
            "criticality": "Crown jewel",
            "lifecycle": "Active",
            "managed": "Managed",
            "owner": "Mainframe · Maya Chen",
            "business_owner": "Treasury",
            "bu": "Finance",
            "location": "NorthStack colo · secondary",
            "cmdb_ci": "ci_zos_sysplex_b",
            "cmdb_status": "In sync",
            "last_seen": today - timedelta(hours=8),
            "first_seen": today - timedelta(days=2000),
            "sources": "CMDB · GDPS · colo",
            "ip_or_id": "sysplex-B",
            "data_class": "Confidential — DR mirror",
            "internet_facing": False,
            "edr": False,
            "vuln_scan": False,
            "siem": True,
            "backup": True,
            "mfa_admin": "RACF",
            "linked_bia": "BIA-2026-001",
            "linked_risk": "EXR-2026-003 · VND-2026-002 · REM-BC-014",
            "crown_jewel_reason": "DR target for settlement.",
            "summary": "DR capacity coupled to colo and Power secondary story for IBM i HA.",
        },
        {
            "asset_id": "AST-2026-016",
            "name": "WMS primary",
            "asset_class": "Application",
            "subtype": "Warehouse management",
            "env": "Production",
            "criticality": "High",
            "lifecycle": "Active",
            "managed": "Partial",
            "owner": "Ops IT",
            "business_owner": "Ops · D. Marshall",
            "bu": "Operations",
            "location": "DC + warehouse VLAN",
            "cmdb_ci": "ci_wms_prd",
            "cmdb_status": "Stale attributes",
            "last_seen": today - timedelta(hours=12),
            "first_seen": today - timedelta(days=1600),
            "sources": "CMDB · JDE interface",
            "ip_or_id": "wms.corp.local",
            "data_class": "Internal — inventory",
            "internet_facing": False,
            "edr": True,
            "vuln_scan": False,
            "siem": True,
            "backup": True,
            "mfa_admin": "AD",
            "linked_bia": "BIA-2026-007",
            "linked_risk": "PLN-2026-007 (draft)",
            "crown_jewel_reason": "",
            "summary": "BIA overdue on warehouse process. Vuln scan coverage gap on WMS host.",
        },
    ]

    # Coverage / reconciliation findings
    gaps = [
        {"gap_id": "GAP-2026-001", "asset_id": "AST-2026-005", "gap_type": "Missing SIEM", "severity": "High", "status": "Open", "opened": today - timedelta(days=28), "due": today + timedelta(days=3), "owner": "Jordan Blake", "detail": "Jump host not onboarded to SIEM — INC-2026-008 sibling. Evidence gap called out in PBC-2026-003."},
        {"gap_id": "GAP-2026-002", "asset_id": "AST-2026-005", "gap_type": "Missing CMDB CI", "severity": "High", "status": "Open", "opened": today - timedelta(days=28), "due": today + timedelta(days=7), "owner": "Asset Mgmt", "detail": "Exists in AD + EDR; no cmdb_ci. Outside build pipeline."},
        {"gap_id": "GAP-2026-003", "asset_id": "AST-2026-002", "gap_type": "Stale CMDB attribute", "severity": "Medium", "status": "Open", "opened": today - timedelta(days=15), "due": today + timedelta(days=14), "owner": "Infra", "detail": "CMDB OS version still shows supported release; device is on unsupported OS under EXC-2026-004."},
        {"gap_id": "GAP-2026-004", "asset_id": "AST-2026-002", "gap_type": "No EDR (expected for appliance)", "severity": "Low", "status": "Accepted", "opened": today - timedelta(days=100), "due": today + timedelta(days=200), "owner": "SecOps", "detail": "Appliance class — IDS/WAF/geo-block are compensating. Documented."},
        {"gap_id": "GAP-2026-005", "asset_id": "AST-2026-011", "gap_type": "Lifecycle conflict", "severity": "High", "status": "Open", "opened": today - timedelta(days=2), "due": today + timedelta(days=5), "owner": "Asset Mgmt / Infra", "detail": "CMDB Retired but EDR last_seen 2d ago. Reclaim or resurrect CI."},
        {"gap_id": "GAP-2026-006", "asset_id": "AST-2026-011", "gap_type": "Missing SIEM", "severity": "Medium", "status": "Open", "opened": today - timedelta(days=2), "due": today + timedelta(days=5), "owner": "SecOps", "detail": "If host stays live, SIEM required; if truly retired, kill EDR enrollment."},
        {"gap_id": "GAP-2026-007", "asset_id": "AST-2026-014", "gap_type": "Unknown / unmanaged asset", "severity": "Critical", "status": "Open", "opened": today - timedelta(days=7), "due": today + timedelta(days=2), "owner": "SOC / Asset Mgmt", "detail": "SMB share discovered from guest adjacency. Quarantine + owner hunt."},
        {"gap_id": "GAP-2026-008", "asset_id": "AST-2026-014", "gap_type": "Missing CMDB CI", "severity": "Critical", "status": "Open", "opened": today - timedelta(days=7), "due": today + timedelta(days=2), "owner": "Asset Mgmt", "detail": "Create CI or confirm rogue and remove."},
        {"gap_id": "GAP-2026-009", "asset_id": "AST-2026-001", "gap_type": "Privileged control exception", "severity": "High", "status": "Accepted", "opened": today - timedelta(days=110), "due": today + timedelta(days=45), "owner": "IBM i Ops / GRC", "detail": "*ALLOBJ under EXC-2026-011 — linked to INC-2026-003 investigation."},
        {"gap_id": "GAP-2026-010", "asset_id": "AST-2026-016", "gap_type": "Missing vuln scan", "severity": "Medium", "status": "Open", "opened": today - timedelta(days=40), "due": today + timedelta(days=10), "owner": "Ops IT", "detail": "WMS host not in vuln scanner scope."},
        {"gap_id": "GAP-2026-011", "asset_id": "AST-2026-003", "gap_type": "No EDR (platform class)", "severity": "Low", "status": "Accepted", "opened": today - timedelta(days=365), "due": today + timedelta(days=365), "owner": "Mainframe Security", "detail": "SMF + SIEM + RACF is the coverage model."},
        {"gap_id": "GAP-2026-012", "asset_id": "AST-2026-012", "gap_type": "Vendor residual elevated", "severity": "Critical", "status": "Open", "opened": today - timedelta(days=1), "due": today + timedelta(days=2), "owner": "TPRM", "detail": "INC-2026-009 — SaaS CI remains Active but processing suspended; track in TPRM not agent gaps."},
    ]

    # Source observations (reconciliation rows)
    sources = [
        {"obs_id": "OBS-001", "asset_id": "AST-2026-005", "adapter": "Active Directory", "seen": today - timedelta(hours=4), "key_attr": "host JUMP-DMZ-03", "in_cmdb": False},
        {"obs_id": "OBS-002", "asset_id": "AST-2026-005", "adapter": "CrowdStrike EDR", "seen": today - timedelta(hours=4), "key_attr": "agent healthy", "in_cmdb": False},
        {"obs_id": "OBS-003", "asset_id": "AST-2026-005", "adapter": "ServiceNow CMDB", "seen": pd.NaT, "key_attr": "(no CI)", "in_cmdb": False},
        {"obs_id": "OBS-004", "asset_id": "AST-2026-011", "adapter": "CrowdStrike EDR", "seen": today - timedelta(days=2), "key_attr": "heartbeat", "in_cmdb": True},
        {"obs_id": "OBS-005", "asset_id": "AST-2026-011", "adapter": "ServiceNow CMDB", "seen": today - timedelta(days=90), "key_attr": "Install Status=Retired", "in_cmdb": True},
        {"obs_id": "OBS-006", "asset_id": "AST-2026-002", "adapter": "ServiceNow CMDB", "seen": today - timedelta(days=40), "key_attr": "OS=supported (stale)", "in_cmdb": True},
        {"obs_id": "OBS-007", "asset_id": "AST-2026-002", "adapter": "Vuln scanner", "seen": today - timedelta(days=3), "key_attr": "unsupported OS + CVE family", "in_cmdb": True},
        {"obs_id": "OBS-008", "asset_id": "AST-2026-014", "adapter": "Network discovery", "seen": today - timedelta(days=7), "key_attr": "SMB :445 open", "in_cmdb": False},
        {"obs_id": "OBS-009", "asset_id": "AST-2026-001", "adapter": "HA monitor", "seen": today - timedelta(hours=2), "key_attr": "mirror lag OK", "in_cmdb": True},
        {"obs_id": "OBS-010", "asset_id": "AST-2026-001", "adapter": "PAM", "seen": today - timedelta(hours=38), "key_attr": "OPSBREAK01 events", "in_cmdb": True},
        {"obs_id": "OBS-011", "asset_id": "AST-2026-012", "adapter": "SSO / API gateway", "seen": today - timedelta(days=1), "key_attr": "tokens rotated", "in_cmdb": True},
        {"obs_id": "OBS-012", "asset_id": "AST-2026-007", "adapter": "WAF", "seen": today - timedelta(minutes=30), "key_attr": "rate-limit rules live", "in_cmdb": True},
    ]

    # Deep packs for featured
    deep = {
        "AST-2026-001": {
            "controls": [
                {"control": "EDR / endpoint", "status": "N/A → platform agents", "note": "IBM i — use QAUDJRN + SIEM"},
                {"control": "SIEM", "status": "Covered", "note": "QAUDJRN forwarders"},
                {"control": "Vuln scan", "status": "Covered", "note": "Network + PTFs tracked"},
                {"control": "Backup / HA", "status": "Partial", "note": "HA mirror OK; secondary Power capacity gap REM-BC-014"},
                {"control": "Privileged access", "status": "Exception", "note": "EXC-2026-011 *ALLOBJ — INC-2026-003 open"},
                {"control": "CMDB completeness", "status": "Covered", "note": "Owner, criticality, BIA links populated"},
            ],
            "evidence": [
                {"ref": "EVD-A-001-A", "desc": "CMDB CI export ci_ibmi_prodbox", "source": "ServiceNow"},
                {"ref": "EVD-A-001-B", "desc": "HA lag dashboard 90d", "source": "IBM i Ops"},
                {"ref": "EVD-A-001-C", "desc": "PAM + QAUDJRN correlation (INC-2026-003)", "source": "IR"},
                {"ref": "EVD-A-001-D", "desc": "BIA-2026-001 link", "source": "BCM"},
            ],
            "open_actions": [
                {"action": "Close or tighten EXC-2026-011 after INC-2026-003", "owner": "GRC / IBM i Ops", "due": today + timedelta(days=5), "status": "Blocked on IR"},
                {"action": "REM-BC-014 secondary Power capacity", "owner": "Infra", "due": today + timedelta(days=45), "status": "In progress"},
                {"action": "Re-test HA failover post capacity", "owner": "Mainframe Recovery", "due": today + timedelta(days=90), "status": "Blocked"},
            ],
            "relationships": [
                {"rel": "Runs", "target": "AST-2026-006 JD Edwards World"},
                {"rel": "Feeds", "target": "AST-2026-003 IBM Z settlement"},
                {"rel": "Protected by", "target": "AST-2026-002 VPN path (admin)"},
                {"rel": "BIA", "target": "BIA-2026-001 / BIA-2026-002"},
            ],
        },
        "AST-2026-002": {
            "controls": [
                {"control": "Internet exposure", "status": "Accepted w/ compensations", "note": "Geo-block, no split-tunnel, jump required"},
                {"control": "Patch / OS support", "status": "Gap", "note": "Unsupported OS — EXC-2026-004"},
                {"control": "Vuln scan", "status": "Covered", "note": "Flags CVE family (INC-2026-010 attempt failed)"},
                {"control": "SIEM / IDS", "status": "Covered", "note": "IDS alert path validated"},
                {"control": "CMDB hygiene", "status": "Stale", "note": "OS field wrong"},
                {"control": "EDR", "status": "N/A appliance", "note": "Accepted GAP-2026-004"},
            ],
            "evidence": [
                {"ref": "EVD-A-002-A", "desc": "EXC-2026-004 waiver packet", "source": "Exception register"},
                {"ref": "EVD-A-002-B", "desc": "INC-2026-010 close-out", "source": "IR"},
                {"ref": "EVD-A-002-C", "desc": "Hardware refresh PO", "source": "Procurement"},
                {"ref": "EVD-A-002-D", "desc": "Geo-block rule set", "source": "Firewall"},
            ],
            "open_actions": [
                {"action": "Update CMDB OS / EOL fields", "owner": "Infra", "due": today + timedelta(days=7), "status": "Open"},
                {"action": "Install replacement concentrator", "owner": "Infra", "due": today + timedelta(days=45), "status": "In progress"},
                {"action": "Close EXC-2026-004 on cutover", "owner": "GRC", "due": today + timedelta(days=50), "status": "Planned"},
            ],
            "relationships": [
                {"rel": "Fronts", "target": "AST-2026-005 / jump fleet"},
                {"rel": "BIA", "target": "BIA-2026-005"},
                {"rel": "Exception", "target": "EXC-2026-004"},
            ],
        },
        "AST-2026-005": {
            "controls": [
                {"control": "EDR", "status": "Covered", "note": "Agent healthy"},
                {"control": "Vuln scan", "status": "Covered", "note": "In scanner"},
                {"control": "SIEM", "status": "Gap", "note": "GAP-2026-001"},
                {"control": "CMDB", "status": "Gap", "note": "GAP-2026-002 — ghost until CI created"},
                {"control": "Build pipeline", "status": "Gap", "note": "Provisioned outside template"},
                {"control": "PAM / MFA", "status": "Covered", "note": "Admin via PAM"},
            ],
            "evidence": [
                {"ref": "EVD-A-005-A", "desc": "AD computer object", "source": "AD"},
                {"ref": "EVD-A-005-B", "desc": "EDR device page", "source": "CrowdStrike"},
                {"ref": "EVD-A-005-C", "desc": "INC-2026-008 / PBC-2026-003 notes", "source": "IR / Audit"},
                {"ref": "EVD-A-005-D", "desc": "Network discovery hit", "source": "Nmap job"},
            ],
            "open_actions": [
                {"action": "Create CMDB CI + owner", "owner": "Asset Mgmt", "due": today + timedelta(days=7), "status": "Open"},
                {"action": "Deploy SIEM agent", "owner": "SecOps", "due": today + timedelta(days=3), "status": "In progress"},
                {"action": "Add host class to infra build template", "owner": "Platform Eng", "due": today + timedelta(days=21), "status": "Planned"},
            ],
            "relationships": [
                {"rel": "Accessed via", "target": "AST-2026-002 VPN"},
                {"rel": "Sibling gaps", "target": "INC-2026-008 jump cohort"},
                {"rel": "BIA", "target": "BIA-2026-005"},
            ],
        },
    }

    df_a = pd.DataFrame(assets)
    for col in ("last_seen", "first_seen"):
        df_a[col] = pd.to_datetime(df_a[col], errors="coerce")

    df_a["controls"] = df_a["asset_id"].map(lambda i: deep.get(i, {}).get("controls", []))
    df_a["evidence"] = df_a["asset_id"].map(lambda i: deep.get(i, {}).get("evidence", []))
    df_a["open_actions"] = df_a["asset_id"].map(lambda i: deep.get(i, {}).get("open_actions", []))
    df_a["relationships"] = df_a["asset_id"].map(lambda i: deep.get(i, {}).get("relationships", []))

    df_g = pd.DataFrame(gaps)
    for col in ("opened", "due"):
        df_g[col] = pd.to_datetime(df_g[col], errors="coerce")

    df_s = pd.DataFrame(sources)
    df_s["seen"] = pd.to_datetime(df_s["seen"], errors="coerce")

    return df_a, df_g, df_s


def _coverage_flags(row: pd.Series) -> list[str]:
    flags = []
    if not row.get("edr") and row["asset_class"] in {"Endpoint", "Jump / bastion", "Server / LPAR"}:
        if row["asset_class"] != "Server / LPAR" or "IBM i" not in str(row.get("name", "")):
            flags.append("No EDR")
    if not row.get("siem"):
        flags.append("No SIEM")
    if not row.get("vuln_scan") and row["asset_class"] not in {"Mainframe", "SaaS / IdP"}:
        flags.append("No vuln scan")
    if row.get("cmdb_status") in {"Missing from CMDB", "Lifecycle conflict", "Stale attributes"}:
        flags.append(row["cmdb_status"])
    if row.get("owner") in {"(unowned)", ""}:
        flags.append("Unowned")
    if row.get("internet_facing"):
        flags.append("Internet-facing")
    return flags


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["days_since_seen"] = (today - out["last_seen"]).dt.days
    out["is_crown"] = out["criticality"].eq("Crown jewel")
    out["is_ghost"] = out["lifecycle"].str.contains("Ghost", na=False) | out["cmdb_status"].eq("Missing from CMDB")
    out["is_stale"] = out["days_since_seen"].fillna(999) > 30
    out["gap_flags"] = out.apply(_coverage_flags, axis=1)
    out["gap_count"] = out["gap_flags"].apply(len)
    out["has_gaps"] = out["gap_count"] > 0
    return out


def _sync(seed: int):
    if st.session_state.get("_ast_seed") != seed or "ast_assets" not in st.session_state:
        a, g, s = _sample(seed)
        st.session_state.ast_assets = a
        st.session_state.ast_gaps = g
        st.session_state.ast_sources = s
        st.session_state._ast_seed = seed
    return st.session_state.ast_assets, st.session_state.ast_gaps, st.session_state.ast_sources


def _save_a(df):
    st.session_state.ast_assets = df.reset_index(drop=True)


def _save_g(df):
    st.session_state.ast_gaps = df.reset_index(drop=True)


def _patch_a(aid, **fields):
    df = st.session_state.ast_assets.copy()
    loc = df.index[df["asset_id"] == aid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_a(df)


def _patch_g(gid, **fields):
    df = st.session_state.ast_gaps.copy()
    loc = df.index[df["gap_id"] == gid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_g(df)


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
        return p.strftime("%Y-%m-%d %H:%M") if p.hour or p.minute else p.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _metrics(assets, gaps):
    e = _enrich(assets)
    open_g = gaps[~gaps["status"].isin(["Closed", "Accepted"])]
    return {
        "total": len(e),
        "crown": int(e["is_crown"].sum()),
        "gaps": int(len(open_g)),
        "ghost": int(e["is_ghost"].sum()),
        "unowned": int(e["owner"].isin(["(unowned)", ""]).sum()),
        "iface": int(e["internet_facing"].sum()),
    }


def _asset_detail(row, gaps, sources, *, expanded=False):
    st.markdown(f"### {row['asset_id']} · {row['name']}")
    a, b, c, d = st.columns(4)
    a.metric("Criticality", row["criticality"])
    b.metric("Lifecycle", row["lifecycle"].split("(")[0].strip())
    c.metric("Managed", row["managed"])
    d.metric("CMDB", row["cmdb_status"])

    c1, c2, c3 = st.columns(3)
    c1.write(f"**Class:** {row['asset_class']} · {row['subtype']}")
    c1.write(f"**Env:** {row['env']} · **BU:** {row['bu']}")
    c1.write(f"**Owner:** {row['owner']}")
    c1.write(f"**Business owner:** {row['business_owner']}")
    c2.write(f"**Location:** {row['location']}")
    c2.write(f"**ID:** {row['ip_or_id']}")
    c2.write(f"**Data class:** {row['data_class']}")
    c2.write(f"**Internet-facing:** {'Yes' if row['internet_facing'] else 'No'}")
    c3.write(f"**CI:** {row['cmdb_ci'] or '—'}")
    c3.write(f"**Sources:** {row['sources']}")
    c3.write(f"**Last / first seen:** {_fmt(row['last_seen'])} / {_fmt(row['first_seen'])}")
    c3.write(f"**Admin MFA:** {row['mfa_admin']}")

    # Coverage chips
    cov = {
        "EDR": row["edr"],
        "Vuln": row["vuln_scan"],
        "SIEM": row["siem"],
        "Backup": row["backup"],
    }
    cols = st.columns(len(cov))
    for i, (k, v) in enumerate(cov.items()):
        cols[i].metric(k, "Yes" if v else "No")

    st.write(row["summary"])
    if row["crown_jewel_reason"]:
        st.info(f"Crown jewel: {row['crown_jewel_reason']}")
    if row.get("gap_flags"):
        st.warning("Flags: " + " · ".join(row["gap_flags"]))
    if row["linked_bia"]:
        st.caption(f"BIA: {row['linked_bia']}")
    if row["linked_risk"]:
        st.caption(f"Risk / IR / TPRM: {row['linked_risk']}")

    raw = st.session_state.ast_assets
    rr = raw[raw["asset_id"] == row["asset_id"]]
    if not rr.empty:
        r0 = rr.iloc[0]
        controls = r0.get("controls") or []
        evid = r0.get("evidence") or []
        acts = r0.get("open_actions") or []
        rels = r0.get("relationships") or []
        if controls:
            with st.expander(f"Control coverage ({len(controls)})", expanded=expanded):
                st.dataframe(pd.DataFrame(controls), use_container_width=True, hide_index=True)
        if rels:
            with st.expander(f"Relationships ({len(rels)})", expanded=expanded):
                st.dataframe(pd.DataFrame(rels), use_container_width=True, hide_index=True)
        if evid:
            with st.expander(f"Evidence ({len(evid)})", expanded=expanded):
                st.dataframe(pd.DataFrame(evid), use_container_width=True, hide_index=True)
        if acts:
            with st.expander(f"Open actions ({len(acts)})", expanded=expanded):
                adf = pd.DataFrame(acts)
                if "due" in adf.columns:
                    adf["due"] = adf["due"].apply(_fmt)
                st.dataframe(adf, use_container_width=True, hide_index=True)

    ag = gaps[gaps["asset_id"] == row["asset_id"]]
    with st.expander(f"Gaps / findings ({len(ag)})", expanded=expanded):
        if ag.empty:
            st.info("None.")
        else:
            show = ag.copy()
            show["opened"] = show["opened"].apply(_fmt)
            show["due"] = show["due"].apply(_fmt)
            st.dataframe(
                show[["gap_id", "gap_type", "severity", "status", "due", "owner", "detail"]],
                use_container_width=True,
                hide_index=True,
            )

    so = sources[sources["asset_id"] == row["asset_id"]]
    with st.expander(f"Source adapters ({len(so)})", expanded=False):
        if so.empty:
            st.info("None.")
        else:
            show = so.copy()
            show["seen"] = show["seen"].apply(_fmt)
            st.dataframe(
                show[["obs_id", "adapter", "seen", "key_attr", "in_cmdb"]],
                use_container_width=True,
                hide_index=True,
            )


def _asset_actions(row, *, key: str):
    aid = row["asset_id"]
    a1, a2, a3 = st.columns(3)
    with a1:
        if row["cmdb_status"] == "Missing from CMDB" and st.button(
            "Create CMDB CI", key=f"ci_{key}", use_container_width=True
        ):
            _patch_a(
                aid,
                cmdb_ci=f"ci_{aid.lower().replace('-', '_')}",
                cmdb_status="In sync",
                lifecycle="Active",
                managed="Managed",
            )
            st.rerun()
    with a2:
        if not row["siem"] and st.button(
            "Mark SIEM onboarded", key=f"siem_{key}", use_container_width=True
        ):
            _patch_a(aid, siem=True)
            # close matching gaps
            g = st.session_state.ast_gaps
            mask = (g["asset_id"] == aid) & (g["gap_type"] == "Missing SIEM") & (~g["status"].isin(["Closed"]))
            if mask.any():
                g = g.copy()
                g.loc[mask, "status"] = "Closed"
                _save_g(g)
            st.rerun()
    with a3:
        if row["owner"] in {"(unowned)", ""} and st.button(
            "Assign to Infra", key=f"own_{key}", use_container_width=True
        ):
            _patch_a(aid, owner="Infrastructure · Jordan Blake", business_owner="IT")
            st.rerun()


def main() -> None:
    portfolio_skin.page_header(
        title="Asset Management System",
        lede="Inventory with business context, coverage gaps, and CMDB reconciliation. Club demo — not a system of record.",
        kicker="Cyber assets",
    )

    seed = demo_kit.seed_controls()
    assets, gaps, sources = _sync(seed)
    ea = _enrich(assets)
    m = _metrics(assets, gaps)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    class_f = st.sidebar.multiselect("Class", CLASSES, default=CLASSES)
    crit_f = st.sidebar.multiselect("Criticality", CRITICALITY, default=CRITICALITY)
    life_f = st.sidebar.multiselect("Lifecycle", LIFECYCLES, default=LIFECYCLES)
    filtered = ea[
        ea["asset_class"].isin(class_f)
        & ea["criticality"].isin(crit_f)
        & ea["lifecycle"].isin(life_f)
    ]

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Assets", m["total"])
    k2.metric("Crown jewels", m["crown"])
    k3.metric("Open gaps", m["gaps"])
    k4.metric("Ghost / missing CI", m["ghost"])
    k5.metric("Unowned", m["unowned"])
    k6.metric("Internet-facing", m["iface"])

    work, inv, gaps_tab, recon, board, intake, export = st.tabs(
        ["Workbench", "Inventory", "Coverage gaps", "Reconciliation", "Status board", "Intake", "Export"]
    )

    with work:
        st.subheader("Asset workbench")
        if m["gaps"]:
            st.warning(f"{m['gaps']} open coverage / reconciliation finding(s).")

        featured = ea[ea["asset_id"].isin(FEATURED)].sort_values("criticality")
        st.markdown(f"**Featured — statement of record ({len(featured)})**")
        for _, row in featured.iterrows():
            st.markdown("---")
            _asset_detail(row, gaps, sources, expanded=True)
            _asset_actions(row, key=f"feat_{row['asset_id']}")
            st.markdown("---")

        ghosts = ea[ea["is_ghost"] & ~ea["asset_id"].isin(FEATURED)]
        st.markdown(f"**Other ghosts / CMDB misses ({len(ghosts)})**")
        if ghosts.empty:
            st.info("Clear.")
        else:
            for _, row in ghosts.iterrows():
                with st.expander(f"{row['asset_id']} · {row['name']} · {row['cmdb_status']}"):
                    _asset_detail(row, gaps, sources)
                    _asset_actions(row, key=f"gh_{row['asset_id']}")

        open_g = gaps[~gaps["status"].isin(["Closed", "Accepted"])].sort_values("due")
        st.markdown(f"**Open gaps queue ({len(open_g)})**")
        show = open_g.copy()
        show["due"] = show["due"].apply(_fmt)
        st.dataframe(
            show[["gap_id", "asset_id", "gap_type", "severity", "status", "due", "owner"]],
            use_container_width=True,
            hide_index=True,
        )

    with inv:
        st.subheader("Inventory")
        ids = filtered["asset_id"].tolist()
        if not ids:
            st.info("Nothing in filter.")
        else:
            pick = st.selectbox("Asset", ids)
            row = ea[ea["asset_id"] == pick].iloc[0]
            _asset_detail(row, gaps, sources, expanded=True)
            _asset_actions(row, key=f"inv_{pick}")

        show = filtered[
            [
                "asset_id",
                "name",
                "asset_class",
                "criticality",
                "lifecycle",
                "managed",
                "owner",
                "cmdb_status",
                "internet_facing",
                "gap_count",
            ]
        ].copy()
        st.dataframe(show, use_container_width=True, hide_index=True)

    with gaps_tab:
        st.subheader("Coverage & hygiene gaps")
        for _, g in gaps.sort_values("due").iterrows():
            with st.expander(
                f"{g['gap_id']} · {g['asset_id']} · {g['gap_type']} · {g['severity']} · {g['status']}"
            ):
                st.write(f"**Owner:** {g['owner']} · **Due:** {_fmt(g['due'])}")
                st.write(g["detail"])
                b1, b2, b3 = st.columns(3)
                with b1:
                    if g["status"] not in {"Closed"} and st.button("Close", key=f"gc_{g['gap_id']}"):
                        _patch_g(g["gap_id"], status="Closed")
                        st.rerun()
                with b2:
                    if g["status"] == "Open" and st.button("Accept risk", key=f"ga_{g['gap_id']}"):
                        _patch_g(g["gap_id"], status="Accepted")
                        st.rerun()
                with b3:
                    if g["status"] == "Open" and st.button("With owner", key=f"go_{g['gap_id']}"):
                        _patch_g(g["gap_id"], status="With owner")
                        st.rerun()

    with recon:
        st.subheader("Source reconciliation")
        st.caption(
            "Adapters disagree: EDR/AD/network say an asset exists; CMDB says retired or missing — "
            "the CAASM move is to surface the mismatch and drive a CI create/update."
        )
        show = sources.copy()
        show["seen"] = show["seen"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

        # Mismatch summary
        miss = ea[ea["cmdb_status"].isin(["Missing from CMDB", "Lifecycle conflict", "Stale attributes"])]
        st.markdown(f"**CMDB mismatches ({len(miss)})**")
        st.dataframe(
            miss[["asset_id", "name", "cmdb_status", "lifecycle", "sources", "last_seen"]].assign(
                last_seen=lambda d: d["last_seen"].apply(_fmt)
            ),
            use_container_width=True,
            hide_index=True,
        )

    with board:
        st.subheader("Status board")
        c1, c2 = st.columns(2)
        with c1:
            crit = (
                ea["criticality"]
                .value_counts()
                .reindex(CRITICALITY)
                .fillna(0)
                .rename_axis("criticality")
                .reset_index(name="count")
            )
            fig = px.bar(crit, x="criticality", y="count", title="By criticality")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            cls = ea["asset_class"].value_counts().rename_axis("class").reset_index(name="count")
            fig = px.bar(cls, x="class", y="count", title="By class")
            fig.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(fig, use_container_width=True)

        # Coverage heatmap-ish
        cov_df = pd.DataFrame(
            {
                "asset_id": ea["asset_id"],
                "name": ea["name"],
                "EDR": ea["edr"].astype(int),
                "Vuln": ea["vuln_scan"].astype(int),
                "SIEM": ea["siem"].astype(int),
                "Backup": ea["backup"].astype(int),
                "criticality": ea["criticality"],
            }
        )
        melt = cov_df.melt(
            id_vars=["asset_id", "name", "criticality"],
            value_vars=["EDR", "Vuln", "SIEM", "Backup"],
            var_name="control",
            value_name="covered",
        )
        fig = px.scatter(
            melt,
            x="control",
            y="asset_id",
            color="covered",
            symbol="criticality",
            title="Control coverage (1=yes, 0=no)",
            color_continuous_scale=["#ff6b6b", "#38e881"],
        )
        st.plotly_chart(fig, use_container_width=True)

        life = ea["lifecycle"].value_counts().rename_axis("lifecycle").reset_index(name="count")
        fig = px.bar(life, x="lifecycle", y="count", title="Lifecycle")
        st.plotly_chart(fig, use_container_width=True)

    with intake:
        st.subheader("Register / discover asset")
        with st.form("intake"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Name")
                asset_class = st.selectbox("Class", CLASSES)
                env = st.selectbox("Environment", ENVS)
                criticality = st.selectbox("Criticality", CRITICALITY, index=2)
            with c2:
                owner = st.text_input("Owner", placeholder="team · person")
                in_cmdb = st.checkbox("Already in CMDB")
                internet = st.checkbox("Internet-facing")
                edr = st.checkbox("EDR present", value=True)
            sources_txt = st.text_input("Discovery sources", value="Manual intake")
            if st.form_submit_button("Create"):
                if not name.strip():
                    st.error("Name required.")
                else:
                    n = len(st.session_state.ast_assets) + 1
                    today = _today()
                    aid = f"AST-2026-{n:03d}"
                    add = {
                        "asset_id": aid,
                        "name": name.strip(),
                        "asset_class": asset_class,
                        "subtype": "Intake",
                        "env": env,
                        "criticality": criticality,
                        "lifecycle": "New" if in_cmdb else "Ghost (seen / not in CMDB)",
                        "managed": "Managed" if in_cmdb else "Unmanaged",
                        "owner": owner.strip() or "(unowned)",
                        "business_owner": "TBD",
                        "bu": "TBD",
                        "location": "TBD",
                        "cmdb_ci": f"ci_{aid.lower()}" if in_cmdb else "",
                        "cmdb_status": "In sync" if in_cmdb else "Missing from CMDB",
                        "last_seen": today,
                        "first_seen": today,
                        "sources": sources_txt.strip() or "Manual",
                        "ip_or_id": "TBD",
                        "data_class": "TBD",
                        "internet_facing": bool(internet),
                        "edr": bool(edr),
                        "vuln_scan": False,
                        "siem": False,
                        "backup": False,
                        "mfa_admin": "TBD",
                        "linked_bia": "",
                        "linked_risk": "",
                        "crown_jewel_reason": "",
                        "summary": "Intake / discovery record — enrich ownership and coverage.",
                        "controls": [],
                        "evidence": [],
                        "open_actions": [],
                        "relationships": [],
                    }
                    _save_a(
                        pd.concat([st.session_state.ast_assets, pd.DataFrame([add])], ignore_index=True)
                    )
                    if not in_cmdb:
                        gid = f"GAP-2026-{len(st.session_state.ast_gaps)+1:03d}"
                        gadd = {
                            "gap_id": gid,
                            "asset_id": aid,
                            "gap_type": "Missing CMDB CI",
                            "severity": "High",
                            "status": "Open",
                            "opened": today,
                            "due": today + timedelta(days=14),
                            "owner": "Asset Mgmt",
                            "detail": "Created from intake without CMDB CI.",
                        }
                        _save_g(
                            pd.concat(
                                [st.session_state.ast_gaps, pd.DataFrame([gadd])],
                                ignore_index=True,
                            )
                        )
                    st.success(f"{aid} created.")
                    st.rerun()

    with export:
        st.subheader("Export")
        out = filtered.copy()
        for col in ("last_seen", "first_seen"):
            out[col] = out[col].apply(_fmt)
        out["gap_flags"] = out["gap_flags"].apply(lambda x: "; ".join(x) if isinstance(x, list) else x)
        for col in ("controls", "evidence", "open_actions", "relationships"):
            if col in out.columns:
                out = out.drop(columns=[col])
        demo_kit.csv_download(out, "assets.csv", label="Download inventory")
        og = gaps.copy()
        og["opened"] = og["opened"].apply(_fmt)
        og["due"] = og["due"].apply(_fmt)
        demo_kit.csv_download(og, "asset_gaps.csv", label="Download gaps", key="g_csv")
        os_ = sources.copy()
        os_["seen"] = os_["seen"].apply(_fmt)
        demo_kit.csv_download(os_, "asset_sources.csv", label="Download source observations", key="s_csv")
        st.caption("Resample rebuilds the demo set. Edits live in this browser session only.")


if __name__ == "__main__":
    main()
