#!/usr/bin/env python3
"""Asset / CMDB / CAASM workbench — club teaching toy.

Dense configuration-item records with business services, scope tags,
verification confidence, config baselines, and AI-system inventory —
the kind of source-of-truth depth you'd want before an ISO or AI-gov
engagement. Not a real CMDB.
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
    "Business service",
    "Server / LPAR",
    "Mainframe",
    "Network",
    "Endpoint",
    "SaaS / IdP",
    "Application",
    "Database",
    "Jump / bastion",
    "AI system / model",
    "OT / IoT",
    "Cloud workload",
]
LIFECYCLES = ["New", "Active", "Inactive", "Decommissioned", "Ghost (seen / not in CMDB)"]
CRITICALITY = ["Crown jewel", "High", "Medium", "Low"]
MANAGED = ["Managed", "Unmanaged", "Partial"]
ENVS = ["Production", "DR", "Staging", "Dev", "Corp"]
VERIFY = ["Verified", "Stale", "Unverified", "Conflict"]

# Featured CIs rendered fully open
FEATURED = {"AST-2026-001", "AST-2026-002", "AST-2026-005", "AST-2026-017"}


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _blank_sot() -> dict:
    """Default source-of-truth fields every CI should carry."""
    return {
        "hostname": "",
        "fqdn": "",
        "serial": "",
        "cost_center": "",
        "steward": "",
        "tech_contact": "",
        "config_baseline": "",
        "os_or_runtime": "",
        "version": "",
        "patch_level": "",
        "change_window": "",
        "processing_purpose": "",
        "data_subjects": "",
        "personal_data_elements": "",
        "retention": "",
        "legal_basis": "",
        "scope_tags": "",
        "verification": "Unverified",
        "last_verified": pd.NaT,
        "confidence": 50,
        "record_quality": "",
        "applicable_controls": "",
        "related_services": "",
        "upstream_cis": "",
        "downstream_cis": "",
        "vendor_link": "",
        "ai_intended_use": "",
        "ai_training_sources": "",
        "ai_human_oversight": "",
        "ai_prohibited_use": "",
        "attribute_dict": [],
    }


def _sample(seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    today = _today()
    rng = np.random.default_rng(seed)

    def j(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    def ci(**kwargs):
        row = _blank_sot()
        row.update(kwargs)
        return row

    # ── Business services (logical SoT layer) ────────────────────────
    services = [
        {
            "service_id": "SVC-2026-001",
            "name": "Core ledger & settlement",
            "criticality": "Crown jewel",
            "owner": "Treasury · S. Okonkwo",
            "rto_h": 2,
            "rpo_h": 0.5,
            "users": "Treasury, Finance close, regulators (indirect)",
            "supporting_assets": "AST-2026-001, AST-2026-003, AST-2026-015",
            "scope_iso27001": True,
            "scope_soc2": True,
            "scope_ai_gov": False,
            "scope_pci": False,
            "description": "Daily settlement and general ledger path across IBM i + IBM Z.",
            "bia": "BIA-2026-001",
        },
        {
            "service_id": "SVC-2026-002",
            "name": "Order-to-cash",
            "criticality": "Crown jewel",
            "owner": "ERP Finance · M. Hassan",
            "rto_h": 4,
            "rpo_h": 1,
            "users": "Order mgmt, AR, warehouse, customers (portal)",
            "supporting_assets": "AST-2026-001, AST-2026-004, AST-2026-006, AST-2026-007",
            "scope_iso27001": True,
            "scope_soc2": True,
            "scope_ai_gov": False,
            "scope_pci": True,
            "description": "JDE World + SAP ECC order capture through cash application.",
            "bia": "BIA-2026-002",
        },
        {
            "service_id": "SVC-2026-003",
            "name": "Privileged remote access",
            "criticality": "High",
            "owner": "Infra · Jordan Blake",
            "rto_h": 4,
            "rpo_h": 1,
            "users": "Admins, vendors under PAM",
            "supporting_assets": "AST-2026-002, AST-2026-005, AST-2026-011",
            "scope_iso27001": True,
            "scope_soc2": True,
            "scope_ai_gov": False,
            "scope_pci": False,
            "description": "VPN + jump path for production administration.",
            "bia": "BIA-2026-005",
        },
        {
            "service_id": "SVC-2026-004",
            "name": "Employee payroll",
            "criticality": "Crown jewel",
            "owner": "Payroll Ops · T. Williams",
            "rto_h": 24,
            "rpo_h": 4,
            "users": "All employees; tax authorities",
            "supporting_assets": "AST-2026-012, AST-2026-008",
            "scope_iso27001": True,
            "scope_soc2": True,
            "scope_ai_gov": False,
            "scope_pci": False,
            "description": "PayrollCo SaaS processing — suspended under INC-2026-009.",
            "bia": "BIA-2026-004",
        },
        {
            "service_id": "SVC-2026-005",
            "name": "Customer digital identity",
            "criticality": "High",
            "owner": "IAM · L. Torres",
            "rto_h": 8,
            "rpo_h": 2,
            "users": "External customers (B2C)",
            "supporting_assets": "AST-2026-007, AST-2026-008, AST-2026-013",
            "scope_iso27001": True,
            "scope_soc2": True,
            "scope_ai_gov": False,
            "scope_pci": False,
            "description": "Portal auth via Azure AD B2C.",
            "bia": "BIA-2026-003",
        },
        {
            "service_id": "SVC-2026-006",
            "name": "Credit decision assist (AI)",
            "criticality": "High",
            "owner": "Credit Risk · AI product owner",
            "rto_h": 24,
            "rpo_h": 24,
            "users": "Credit analysts (human-in-the-loop); applicants (indirect)",
            "supporting_assets": "AST-2026-017, AST-2026-018, AST-2026-013",
            "scope_iso27001": True,
            "scope_soc2": False,
            "scope_ai_gov": True,
            "scope_pci": False,
            "description": "Model-assisted credit scoring — ISO/IEC 42001 inventory candidate.",
            "bia": "",
        },
    ]

    assets = [
        # ── Featured: IBM i ──────────────────────────────────────────
        ci(
            asset_id="AST-2026-001",
            name="IBM i PRODBOX (LPAR SN 065-1042)",
            asset_class="Server / LPAR",
            subtype="IBM i production LPAR",
            env="Production",
            criticality="Crown jewel",
            lifecycle="Active",
            managed="Managed",
            owner="IBM i Ops · D. Marshall",
            business_owner="Treasury / ERP Finance",
            bu="Finance",
            location="Primary DC · Power frame bay 12",
            cmdb_ci="ci_ibmi_prodbox",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=2),
            first_seen=today - timedelta(days=1400),
            sources="CMDB · QAUDJRN · PAM · HA monitor · ITSM · Discovery",
            ip_or_id="10.20.4.12",
            hostname="PRODBOX",
            fqdn="prodbox.finance.corp.local",
            serial="SN 065-1042 · LPAR 3",
            cost_center="CC-4100 Finance Ops",
            steward="IBM i Ops (primary) · Mainframe Security (secondary)",
            tech_contact="D. Marshall · on-call PagerDuty IBM-i",
            config_baseline="IBM i 7.5 · TR6 · security level 40",
            os_or_runtime="IBM i 7.5",
            version="7.5",
            patch_level="PTF group SF99750 level 6 (2026-Q2)",
            change_window="Sat 02:00–06:00 ET · CHG-* emergency path",
            data_class="Confidential",
            processing_purpose="System of record for customer master, O2C batch, settlement feeds to Z",
            data_subjects="Customers (B2B); employees (limited HR interfaces)",
            personal_data_elements="Name, address, phone, account IDs; no payment PAN on this LPAR",
            retention="Per FIN-RET-03 — transactional 7y; master until account close + 7y",
            legal_basis="Contract performance · legal obligation (SOX / tax)",
            scope_tags="ISO 27001 SoA · SOC 2 CC6/CC7 · SOX ITGC · BCM crown jewel",
            verification="Verified",
            last_verified=today - timedelta(days=12),
            confidence=92,
            record_quality="Golden — owners, BIA, controls, baseline populated; HA capacity gap noted",
            applicable_controls="A.5.9 · A.8.1 · A.8.8 · A.8.9 · A.8.15 · AC-02 · AC-06 · CP-09 · SI-04",
            related_services="SVC-2026-001, SVC-2026-002",
            upstream_cis="AST-2026-002 (admin path), Power frame, storage IASP",
            downstream_cis="AST-2026-006 (JDE), AST-2026-003 (settlement feed), HA mirror",
            vendor_link="Hardware OEM · Orbit AMS (VND-2026-003) for JDE ops",
            internet_facing=False,
            edr=False,
            vuln_scan=True,
            siem=True,
            backup=True,
            mfa_admin="Partial (PAM; *ALLOBJ exception EXC-2026-011)",
            linked_bia="BIA-2026-001, BIA-2026-002",
            linked_risk="INC-2026-003 · EXC-2026-011 · EXR-2026-003 · PLN-2026-001",
            crown_jewel_reason="Core ledger + O2C SoR. RTO 2h / achievable 6h (REM-BC-014).",
            summary="Authoritative CI for production IBM i. Record is engagement-ready for ISO/SOC scoping: purpose, data, controls, services, and verification confidence are explicit. Live risk is privileged break-glass and HA capacity — not inventory fog.",
            attribute_dict=[
                {"attr": "QSECURITY", "value": "40", "source": "DSPSYSVAL", "as_of": "2026-08-12"},
                {"attr": "QAUDCTL", "value": "*AUDLVL *NOQTEMP", "source": "DSPSYSVAL", "as_of": "2026-08-12"},
                {"attr": "HA mirror lag", "value": "< 5 min", "source": "HA monitor", "as_of": "live"},
                {"attr": "IASP", "value": "PRODASP01", "source": "CMDB", "as_of": "2026-07-01"},
                {"attr": "Break-glass profile", "value": "OPSBREAK01 (*ALLOBJ)", "source": "EXC-2026-011", "as_of": "active"},
                {"attr": "Last PTF apply", "value": "2026-06-14", "source": "PTF log", "as_of": "2026-06-14"},
                {"attr": "Discovery confidence", "value": "3 adapters agree", "source": "CAASM", "as_of": "today"},
            ],
        ),
        # ── Featured: VPN ────────────────────────────────────────────
        ci(
            asset_id="AST-2026-002",
            name="VPN Gateway (legacy concentrator)",
            asset_class="Network",
            subtype="SSL VPN concentrator",
            env="Production",
            criticality="High",
            lifecycle="Active",
            managed="Partial",
            owner="Infrastructure · Jordan Blake",
            business_owner="IT / SecOps",
            bu="IT",
            location="DMZ · primary edge rack A3",
            cmdb_ci="ci_vpn_gw_01",
            cmdb_status="Stale attributes",
            last_seen=today - timedelta(hours=1),
            first_seen=today - timedelta(days=2200),
            sources="CMDB · IDS · firewall · EXC register · Vuln scanner",
            ip_or_id="203.0.113.40",
            hostname="vpn-gw-01",
            fqdn="vpn.corp.example.com",
            serial="VPN-HW-88421",
            cost_center="CC-2200 Infrastructure",
            steward="Network Engineering",
            tech_contact="Jordan Blake · NetOps on-call",
            config_baseline="Vendor OS (unsupported) · geo-block ON · split-tunnel OFF",
            os_or_runtime="Concentrator OS 9.1 (EOL)",
            version="9.1.4",
            patch_level="No vendor patches — compensating controls only",
            change_window="Tue/Thu 22:00–00:00 ET",
            data_class="Internal",
            processing_purpose="Terminate remote admin and workforce VPN sessions; authenticate via IdP",
            data_subjects="Workforce; privileged vendors",
            personal_data_elements="Usernames, source IP, session metadata (no content)",
            retention="Session logs 1y in SIEM",
            legal_basis="Legitimate interest — security of processing",
            scope_tags="ISO 27001 SoA · SOC 2 CC6 · Exception EXC-2026-004",
            verification="Conflict",
            last_verified=today - timedelta(days=40),
            confidence=61,
            record_quality="CMDB OS field stale vs vuln scanner; exception packet attached",
            applicable_controls="A.8.8 · A.8.20 · A.8.21 · A.8.22 · SC-07 · SI-02",
            related_services="SVC-2026-003",
            upstream_cis="IdP · firewall · DNS",
            downstream_cis="AST-2026-005 jump fleet · production admin paths",
            vendor_link="Hardware OEM · refresh PO open",
            internet_facing=True,
            edr=False,
            vuln_scan=True,
            siem=True,
            backup=False,
            mfa_admin="Yes (admin plane) · user MFA via IdP",
            linked_bia="BIA-2026-005",
            linked_risk="EXC-2026-004 · INC-2026-010 · PLN-2026-005",
            crown_jewel_reason="",
            summary="Internet-facing privilege path. SoT record deliberately shows conflict: CMDB says supported OS, scanner says EOL. Compensating controls and exception are part of the record — not footnotes.",
            attribute_dict=[
                {"attr": "CMDB OS", "value": "Supported (stale)", "source": "ServiceNow", "as_of": "2026-07-01"},
                {"attr": "Scanner OS", "value": "EOL 9.1.4", "source": "Vuln scanner", "as_of": "2026-08-21"},
                {"attr": "Geo-block", "value": "Enabled — allowlist countries", "source": "Firewall", "as_of": "live"},
                {"attr": "Split tunnel", "value": "Disabled", "source": "VPN config", "as_of": "live"},
                {"attr": "Exception", "value": "EXC-2026-004 time-boxed", "source": "Exception register", "as_of": "active"},
                {"attr": "Refresh ETA", "value": "~6 weeks", "source": "PO", "as_of": "2026-08"},
            ],
        ),
        ci(
            asset_id="AST-2026-003",
            name="IBM Z sysplex — CICS / DB2",
            asset_class="Mainframe",
            subtype="z/OS sysplex",
            env="Production",
            criticality="Crown jewel",
            lifecycle="Active",
            managed="Managed",
            owner="Mainframe Security · Maya Chen",
            business_owner="Treasury",
            bu="Finance",
            location="Primary DC · raised floor (NorthStack colo)",
            cmdb_ci="ci_zos_sysplex_a",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=1),
            first_seen=today - timedelta(days=3000),
            sources="CMDB · SMF · RACF · GDPS · colo vendor",
            ip_or_id="sysplex-A",
            hostname="SYSPLEXA",
            fqdn="sysplexa.finance.corp.local",
            serial="CPC / LPAR set — see HMC inventory",
            cost_center="CC-4100 Finance Ops",
            steward="Mainframe Security",
            tech_contact="Maya Chen",
            config_baseline="z/OS 3.1 · GDPS Metro · RACF",
            os_or_runtime="z/OS 3.1",
            version="3.1",
            patch_level="RSU 2026-06",
            change_window="Sun 01:00–05:00 ET",
            data_class="Confidential",
            processing_purpose="CICS settlement and DB2 financial ledgers",
            data_subjects="Customers (account activity)",
            personal_data_elements="Account identifiers, balances, settlement instructions",
            retention="FIN-RET-03 7y",
            legal_basis="Contract · legal obligation",
            scope_tags="ISO 27001 · SOC 2 · SOX ITGC · Colo TPRM VND-2026-002",
            verification="Verified",
            last_verified=today - timedelta(days=20),
            confidence=90,
            record_quality="Platform-class coverage model documented (no EDR)",
            applicable_controls="A.5.9 · A.8.2 · A.8.15 · A.8.16 · AC-02 · AU-02",
            related_services="SVC-2026-001",
            upstream_cis="AST-2026-001 feeds · AST-2026-015 DR",
            downstream_cis="Regulatory reporting extracts",
            vendor_link="VND-2026-002 NorthStack Colo",
            internet_facing=False,
            edr=False,
            vuln_scan=False,
            siem=True,
            backup=True,
            mfa_admin="RACF + PAM for TSO; SPECIAL recert quarterly",
            linked_bia="BIA-2026-001",
            linked_risk="INC-2026-004 · VND-2026-002 · EXR-2026-003",
            crown_jewel_reason="Settlement path with GDPS secondary.",
            summary="Crown jewel mainframe CI. Coverage story is SMF/SIEM/RACF — agents are N/A and accepted in the record.",
        ),
        ci(
            asset_id="AST-2026-004",
            name="SAP ECC PRD",
            asset_class="Application",
            subtype="SAP ECC",
            env="Production",
            criticality="Crown jewel",
            lifecycle="Active",
            managed="Managed",
            owner="SAP Basis",
            business_owner="ERP Finance · M. Hassan",
            bu="Finance",
            location="Primary DC · app/DB cluster",
            cmdb_ci="ci_sap_ecc_prd",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=3),
            first_seen=today - timedelta(days=1800),
            sources="CMDB · Solution Manager · PAM · ST01",
            ip_or_id="sapprd.corp.local",
            hostname="SAPPRD",
            fqdn="sapprd.corp.local",
            serial="SID=PRD",
            cost_center="CC-4200 ERP",
            steward="SAP Basis",
            tech_contact="Basis on-call",
            config_baseline="ECC 6.0 EHP8 · kernel current · ST01 on for break-glass",
            os_or_runtime="Linux + HANA/Oracle (see child CI)",
            version="EHP8",
            patch_level="Support Pack stack 2026-Q1",
            change_window="Sat 20:00–02:00 ET",
            data_class="Confidential",
            processing_purpose="ERP financials and O2C with JDE",
            data_subjects="Customers, employees (HR mini-master)",
            personal_data_elements="Customer masters, vendor masters, limited HR",
            retention="FIN-RET-03",
            legal_basis="Contract · legal obligation",
            scope_tags="ISO 27001 · SOC 2 · SOX · PCI (payment-adjacent)",
            verification="Verified",
            last_verified=today - timedelta(days=25),
            confidence=88,
            record_quality="Strong — DR exercise pending EXR-2026-005",
            applicable_controls="A.8.1 · A.8.9 · A.8.32 · AC-02 · AU-03",
            related_services="SVC-2026-002",
            upstream_cis="AST-2026-006 interfaces",
            downstream_cis="Payment gateway · reporting",
            vendor_link="SAP · Basis AMS",
            internet_facing=False,
            edr=True,
            vuln_scan=True,
            siem=True,
            backup=True,
            mfa_admin="PAM for SAP_ALL break-glass",
            linked_bia="BIA-2026-002",
            linked_risk="INC-2026-006 · EXR-2026-005 · PLN-2026-002",
            crown_jewel_reason="Order-to-cash spine with JDE.",
            summary="ECC PRD CI with break-glass monitoring post INC-2026-006.",
        ),
        # ── Featured: jump ghost ─────────────────────────────────────
        ci(
            asset_id="AST-2026-005",
            name="DMZ jump host JUMP-DMZ-03",
            asset_class="Jump / bastion",
            subtype="Hardened jump",
            env="Production",
            criticality="High",
            lifecycle="Active",
            managed="Partial",
            owner="Infrastructure · Jordan Blake",
            business_owner="SecOps",
            bu="IT",
            location="DMZ VLAN 50",
            cmdb_ci="",
            cmdb_status="Missing from CMDB",
            last_seen=today - timedelta(hours=4),
            first_seen=today - timedelta(days=40),
            sources="AD · EDR · network discovery (not CMDB)",
            ip_or_id="10.50.9.33",
            hostname="JUMP-DMZ-03",
            fqdn="jump-dmz-03.dmz.corp.local",
            serial="VM-UUID a81e…c4",
            cost_center="CC-2200 Infrastructure",
            steward="(pending CI create)",
            tech_contact="Jordan Blake",
            config_baseline="Golden jump image v3 — NOT used (ad-hoc build)",
            os_or_runtime="RHEL 9.4",
            version="9.4",
            patch_level="Unknown — not in patch MGMT scope until CI exists",
            change_window="Unregistered",
            data_class="Internal",
            processing_purpose="Bastion for privileged sessions into production",
            data_subjects="Admin session metadata only",
            personal_data_elements="Usernames, session recordings (if enabled)",
            retention="Session logs — policy TBD until CI onboarded",
            legal_basis="Legitimate interest — security",
            scope_tags="Should be ISO/SOC in-scope privileged path — currently inventory gap",
            verification="Unverified",
            last_verified=pd.NaT,
            confidence=35,
            record_quality="Poor — discovery-only; blocks defensible scope statements",
            applicable_controls="A.8.1 · A.8.9 · A.8.15 · A.8.16 · AC-17 — applicability pending CI",
            related_services="SVC-2026-003",
            upstream_cis="AST-2026-002 VPN",
            downstream_cis="Production LPARs / clusters via PAM",
            vendor_link="",
            internet_facing=False,
            edr=True,
            vuln_scan=True,
            siem=False,
            backup=False,
            mfa_admin="Yes via PAM",
            linked_bia="BIA-2026-005",
            linked_risk="INC-2026-008 · PBC-2026-003",
            crown_jewel_reason="",
            summary="The anti-golden-record: live, privileged, and missing from CMDB. Shows why SoT quality is a scoping dependency — you cannot claim control coverage on CIs you cannot name.",
            attribute_dict=[
                {"attr": "AD object", "value": "Present", "source": "AD", "as_of": "live"},
                {"attr": "EDR", "value": "Healthy", "source": "CrowdStrike", "as_of": "live"},
                {"attr": "CMDB CI", "value": "Absent", "source": "ServiceNow", "as_of": "live"},
                {"attr": "SIEM", "value": "Not onboarded", "source": "SIEM", "as_of": "live"},
                {"attr": "Build pipeline", "value": "Bypassed", "source": "Infra", "as_of": "2026-07"},
                {"attr": "Confidence", "value": "35%", "source": "CAASM scoring", "as_of": "today"},
            ],
        ),
        ci(
            asset_id="AST-2026-006",
            name="JD Edwards World (on PRODBOX)",
            asset_class="Application",
            subtype="JDE World",
            env="Production",
            criticality="Crown jewel",
            lifecycle="Active",
            managed="Managed",
            owner="ERP / Orbit AMS",
            business_owner="ERP Finance",
            bu="Finance",
            location="Runs on AST-2026-001",
            cmdb_ci="ci_jde_world_prd",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=2),
            first_seen=today - timedelta(days=1400),
            sources="CMDB · IBM i · AMS tickets",
            ip_or_id="app:JDE-WORLD",
            hostname="(logical CI)",
            fqdn="",
            serial="JDE World A9.4",
            cost_center="CC-4200 ERP",
            steward="ERP Finance · Orbit AMS (VND-2026-003)",
            tech_contact="M. Hassan / Orbit L2",
            config_baseline="JDE World A9.4 · libraries PRODDATA",
            os_or_runtime="IBM i hosted",
            version="A9.4",
            patch_level="Cumulative 2026-Q1",
            change_window="Aligned to AST-2026-001",
            data_class="Confidential",
            processing_purpose="Order-to-cash application of record",
            data_subjects="Customers, vendors",
            personal_data_elements="Customer master, order history",
            retention="FIN-RET-03",
            legal_basis="Contract",
            scope_tags="ISO 27001 · SOC 2 · TPRM AMS",
            verification="Verified",
            last_verified=today - timedelta(days=18),
            confidence=84,
            record_quality="Good — IFS hygiene is the open control theme",
            applicable_controls="A.5.19 · A.8.1 · A.8.9 · A.8.12",
            related_services="SVC-2026-002",
            upstream_cis="AST-2026-001",
            downstream_cis="AST-2026-004 · WMS · portal",
            vendor_link="VND-2026-003 Orbit AMS",
            internet_facing=False,
            edr=False,
            vuln_scan=False,
            siem=True,
            backup=True,
            mfa_admin="Via IBM i / PAM",
            linked_bia="BIA-2026-002",
            linked_risk="INC-2026-005 · VND-2026-003 · EXR-2026-007",
            crown_jewel_reason="O2C application of record on IBM i.",
            summary="Logical app CI. Parent LPAR + AMS vendor + IFS incident are linked on the record.",
        ),
        ci(
            asset_id="AST-2026-007",
            name="Customer portal (portal.example.com)",
            asset_class="Application",
            subtype="Customer web + API",
            env="Production",
            criticality="High",
            lifecycle="Active",
            managed="Managed",
            owner="Platform Eng · R. Kim",
            business_owner="Digital",
            bu="Customer experience",
            location="Multi-AZ cloud",
            cmdb_ci="ci_portal_prd",
            cmdb_status="In sync",
            last_seen=today - timedelta(minutes=30),
            first_seen=today - timedelta(days=900),
            sources="CMDB · WAF · IdP · APM · GitHub deploy",
            ip_or_id="portal.example.com",
            hostname="portal-prd",
            fqdn="portal.example.com",
            serial="deploy SHA tracked in CD",
            cost_center="CC-5100 Digital",
            steward="Platform Engineering",
            tech_contact="R. Kim",
            config_baseline="K8s prod · WAF on · CAPTCHA+/api rate-limit post INC-2026-001",
            os_or_runtime="Containers on managed K8s",
            version="portal-api 4.12.3",
            patch_level="Image digest pinned · weekly rebuild",
            change_window="Continuous with canary",
            data_class="Confidential",
            processing_purpose="Customer self-service and authenticated API",
            data_subjects="External customers",
            personal_data_elements="Email, display name, account prefs",
            retention="Account life + 2y activity logs",
            legal_basis="Contract · consent (marketing prefs)",
            scope_tags="ISO 27001 · SOC 2 · GDPR Art. 30 candidate",
            verification="Verified",
            last_verified=today - timedelta(days=5),
            confidence=91,
            record_quality="Strong post-incident enrichment",
            applicable_controls="A.8.9 · A.8.20 · A.8.26 · A.5.34 · SC-07",
            related_services="SVC-2026-002, SVC-2026-005",
            upstream_cis="AST-2026-008 IdP · WAF · CDN",
            downstream_cis="AST-2026-013 marketing-DB · O2C",
            vendor_link="VND-2026-004 Azure AD B2C",
            internet_facing=True,
            edr=False,
            vuln_scan=True,
            siem=True,
            backup=True,
            mfa_admin="IdP; B2C MFA rollout in progress",
            linked_bia="BIA-2026-003",
            linked_risk="INC-2026-001 · VND-2026-004",
            crown_jewel_reason="",
            summary="Customer-facing CI with post-stuffing control changes captured on the record.",
        ),
        ci(
            asset_id="AST-2026-008",
            name="Azure AD B2C tenant",
            asset_class="SaaS / IdP",
            subtype="Customer identity",
            env="Production",
            criticality="High",
            lifecycle="Active",
            managed="Managed",
            owner="IAM · L. Torres",
            business_owner="Platform Eng",
            bu="IT",
            location="Microsoft cloud",
            cmdb_ci="ci_aadb2c",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=1),
            first_seen=today - timedelta(days=900),
            sources="CMDB · IdP admin · TPRM",
            ip_or_id="tenant:contoso-b2c",
            hostname="",
            fqdn="",
            serial="Tenant ID redacted in demo",
            cost_center="CC-2300 IAM",
            steward="IAM",
            tech_contact="L. Torres",
            config_baseline="Conditional access + PIM for admin; B2C MFA phased",
            os_or_runtime="SaaS",
            version="n/a",
            patch_level="Vendor-managed",
            change_window="IdP change board",
            data_class="Confidential",
            processing_purpose="Authenticate B2C customers for portal",
            data_subjects="External customers",
            personal_data_elements="Identity claims, email, auth events",
            retention="Sign-in logs per M365 retention",
            legal_basis="Contract",
            scope_tags="ISO 27001 · SOC 2 · TPRM hyperscaler",
            verification="Verified",
            last_verified=today - timedelta(days=30),
            confidence=93,
            record_quality="Inheritance model — trust docs + config review",
            applicable_controls="A.5.19 · A.8.5 · A.5.17",
            related_services="SVC-2026-005",
            upstream_cis="",
            downstream_cis="AST-2026-007",
            vendor_link="VND-2026-004",
            internet_facing=True,
            edr=False,
            vuln_scan=False,
            siem=True,
            backup=False,
            mfa_admin="Privileged Identity Management",
            linked_bia="BIA-2026-003",
            linked_risk="VND-2026-004 · INC-2026-001",
            crown_jewel_reason="",
            summary="Hyperscaler IdP CI — coverage is config + logging inheritance.",
        ),
        ci(
            asset_id="AST-2026-009",
            name="ENGWS-0042 (engineering workstation)",
            asset_class="Endpoint",
            subtype="Windows workstation",
            env="Corp",
            criticality="Medium",
            lifecycle="Active",
            managed="Managed",
            owner="Endpoint mgmt",
            business_owner="Engineering",
            bu="Engineering",
            location="HQ · dock",
            cmdb_ci="ci_engws_0042",
            cmdb_status="In sync",
            last_seen=today - timedelta(days=14),
            first_seen=today - timedelta(days=600),
            sources="CMDB · EDR · Intune · AD",
            ip_or_id="ENGWS-0042",
            hostname="ENGWS-0042",
            fqdn="engws-0042.corp.local",
            serial="SERVTAG-9X2K",
            cost_center="CC-6100 Engineering",
            steward="Endpoint mgmt",
            tech_contact="Service Desk",
            config_baseline="Win11 23H2 corp image · BitLocker · EDR",
            os_or_runtime="Windows 11 23H2",
            version="23H2",
            patch_level="Patch Tuesday current as of re-image",
            change_window="n/a endpoint",
            data_class="Internal",
            processing_purpose="Engineering workstation",
            data_subjects="Employee user",
            personal_data_elements="Local profile",
            retention="Device life",
            legal_basis="Employment",
            scope_tags="ISO 27001 endpoint population",
            verification="Verified",
            last_verified=today - timedelta(days=14),
            confidence=80,
            record_quality="Re-imaged post ransomware; watch inactive at 30d",
            applicable_controls="A.8.1 · A.8.7 · A.8.19",
            related_services="",
            upstream_cis="",
            downstream_cis="AST-2026-010 share access",
            vendor_link="",
            internet_facing=False,
            edr=True,
            vuln_scan=True,
            siem=True,
            backup=False,
            mfa_admin="N/A (user MFA)",
            linked_bia="",
            linked_risk="INC-2026-002",
            crown_jewel_reason="",
            summary="Ransomware host from INC-2026-002 — re-imaged.",
        ),
        ci(
            asset_id="AST-2026-010",
            name="\\\\ENG-NAS (engineering file share)",
            asset_class="Server / LPAR",
            subtype="NAS file share",
            env="Production",
            criticality="High",
            lifecycle="Active",
            managed="Managed",
            owner="Infrastructure",
            business_owner="Engineering",
            bu="Engineering",
            location="Primary DC",
            cmdb_ci="ci_eng_nas",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=6),
            first_seen=today - timedelta(days=1100),
            sources="CMDB · backup · AD ACL",
            ip_or_id="\\\\ENG-NAS",
            hostname="ENG-NAS",
            fqdn="eng-nas.corp.local",
            serial="NAS-ARRAY-22",
            cost_center="CC-2200",
            steward="Storage team",
            tech_contact="Infra on-call",
            config_baseline="Snapshots hourly · ACL tiering incomplete",
            os_or_runtime="NAS OS",
            version="",
            patch_level="",
            change_window="Sun 03:00–05:00",
            data_class="Internal",
            processing_purpose="Engineering IP and build artifacts",
            data_subjects="Employees",
            personal_data_elements="Incidental in docs",
            retention="Project + 3y",
            legal_basis="Employment · IP protection",
            scope_tags="ISO 27001 · SOC 2 availability",
            verification="Verified",
            last_verified=today - timedelta(days=45),
            confidence=78,
            record_quality="ACL tiering lesson from INC-2026-002 still open",
            applicable_controls="A.8.9 · A.8.10 · A.8.13 · CP-09",
            related_services="",
            upstream_cis="",
            downstream_cis="Build farm",
            vendor_link="",
            internet_facing=False,
            edr=False,
            vuln_scan=True,
            siem=True,
            backup=True,
            mfa_admin="N/A",
            linked_bia="",
            linked_risk="INC-2026-002",
            crown_jewel_reason="",
            summary="Share encryption attempted in ransomware incident; snapshots clean.",
        ),
        ci(
            asset_id="AST-2026-011",
            name="JUMP-DMZ-07 (retired tag, still checking in)",
            asset_class="Jump / bastion",
            subtype="Hardened jump",
            env="Production",
            criticality="Medium",
            lifecycle="Ghost (seen / not in CMDB)",
            managed="Unmanaged",
            owner="(unowned)",
            business_owner="(unowned)",
            bu="IT",
            location="DMZ",
            cmdb_ci="ci_jump_dmz_07 (Retired)",
            cmdb_status="Lifecycle conflict",
            last_seen=today - timedelta(days=2),
            first_seen=today - timedelta(days=800),
            sources="EDR · AD (CMDB says Retired)",
            ip_or_id="10.50.9.71",
            hostname="JUMP-DMZ-07",
            fqdn="jump-dmz-07.dmz.corp.local",
            serial="VM-UUID …",
            cost_center="CC-2200",
            steward="(conflict)",
            tech_contact="",
            config_baseline="Unknown — retired in CMDB",
            os_or_runtime="RHEL 8",
            version="",
            patch_level="",
            change_window="",
            data_class="Internal",
            processing_purpose="Should be decommissioned bastion — still live",
            data_subjects="",
            personal_data_elements="",
            retention="",
            legal_basis="",
            scope_tags="Must resolve before scope freeze — zombie CI",
            verification="Conflict",
            last_verified=today - timedelta(days=90),
            confidence=20,
            record_quality="Conflict — CMDB Retired vs EDR heartbeat",
            applicable_controls="A.8.1 · A.8.10 — lifecycle failure",
            related_services="SVC-2026-003",
            upstream_cis="AST-2026-002",
            downstream_cis="",
            vendor_link="",
            internet_facing=False,
            edr=True,
            vuln_scan=False,
            siem=False,
            backup=False,
            mfa_admin="Unknown",
            linked_bia="BIA-2026-005",
            linked_risk="",
            crown_jewel_reason="",
            summary="Lifecycle drift: retired in CMDB, alive on the wire.",
        ),
        ci(
            asset_id="AST-2026-012",
            name="PayrollCo SaaS (logical CI)",
            asset_class="SaaS / IdP",
            subtype="Payroll processor",
            env="Production",
            criticality="Crown jewel",
            lifecycle="Active",
            managed="Managed",
            owner="TPRM · A. Nguyen",
            business_owner="Payroll Ops",
            bu="HR",
            location="Vendor SaaS",
            cmdb_ci="ci_payrollco",
            cmdb_status="In sync",
            last_seen=today - timedelta(days=1),
            first_seen=today - timedelta(days=700),
            sources="CMDB · TPRM · SSO · API gateway",
            ip_or_id="saas:payrollco",
            hostname="",
            fqdn="api.payrollco.example.com",
            serial="DPA-2024-019",
            cost_center="CC-3100 HR",
            steward="TPRM + Payroll Ops",
            tech_contact="A. Nguyen",
            config_baseline="SSO federated · API token rotated · processing suspended",
            os_or_runtime="SaaS",
            version="n/a",
            patch_level="Vendor",
            change_window="Vendor + our IR freeze",
            data_class="Restricted",
            processing_purpose="Payroll calculation and tax filing (processor)",
            data_subjects="Employees (1,820)",
            personal_data_elements="SSN, bank, salary, tax withholding",
            retention="Per DPA + statutory retention",
            legal_basis="Legal obligation · contract",
            scope_tags="ISO 27001 · SOC 2 · GDPR Art. 28 processor · TPRM Tier 1",
            verification="Stale",
            last_verified=today - timedelta(days=120),
            confidence=55,
            record_quality="CI current; assurance/residual driven by INC-2026-009",
            applicable_controls="A.5.19 · A.5.20 · A.5.21 · A.5.34",
            related_services="SVC-2026-004",
            upstream_cis="AST-2026-008 SSO",
            downstream_cis="Bank ACH · tax e-file",
            vendor_link="VND-2026-001 PayrollCo",
            internet_facing=True,
            edr=False,
            vuln_scan=False,
            siem=True,
            backup=False,
            mfa_admin="Vendor + our SSO",
            linked_bia="BIA-2026-004",
            linked_risk="INC-2026-009 · VND-2026-001 · PLN-2026-004",
            crown_jewel_reason="Pay calendar dependency; PII processor.",
            summary="Logical SaaS CI — residual lived in TPRM/IR, not agent coverage.",
        ),
        ci(
            asset_id="AST-2026-013",
            name="marketing-DB read-replica",
            asset_class="Database",
            subtype="Postgres read replica",
            env="Production",
            criticality="Medium",
            lifecycle="Active",
            managed="Managed",
            owner="Data platform",
            business_owner="Marketing",
            bu="Marketing",
            location="Cloud AZ-b",
            cmdb_ci="ci_mkt_db_rr",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=5),
            first_seen=today - timedelta(days=400),
            sources="CMDB · cloud inventory · SIEM",
            ip_or_id="mkt-db-rr.internal",
            hostname="mkt-db-rr",
            fqdn="mkt-db-rr.internal",
            serial="RDS/equivalent ID",
            cost_center="CC-5100",
            steward="Data platform",
            tech_contact="Data on-call",
            config_baseline="Encrypted at rest · private subnet · rotated creds",
            os_or_runtime="PostgreSQL 15",
            version="15.6",
            patch_level="Managed minor",
            change_window="Tue 01:00",
            data_class="Confidential",
            processing_purpose="Portal profile reads / marketing analytics",
            data_subjects="Customers",
            personal_data_elements="Email, display name",
            retention="Aligned to portal account",
            legal_basis="Contract · legitimate interest (analytics)",
            scope_tags="ISO 27001 · GDPR",
            verification="Verified",
            last_verified=today - timedelta(days=8),
            confidence=85,
            record_quality="Creds rotated during INC-2026-001",
            applicable_controls="A.8.11 · A.8.24 · A.5.34",
            related_services="SVC-2026-005, SVC-2026-006",
            upstream_cis="AST-2026-007",
            downstream_cis="AST-2026-017 feature store reads (limited)",
            vendor_link="",
            internet_facing=False,
            edr=False,
            vuln_scan=True,
            siem=True,
            backup=True,
            mfa_admin="Cloud IAM",
            linked_bia="BIA-2026-003",
            linked_risk="INC-2026-001",
            crown_jewel_reason="",
            summary="Read replica — connection strings rotated in credential-stuffing IR.",
        ),
        ci(
            asset_id="AST-2026-014",
            name="Shadow NAS share (guest WLAN discovered)",
            asset_class="Server / LPAR",
            subtype="Unauthorized SMB share",
            env="Production",
            criticality="High",
            lifecycle="Ghost (seen / not in CMDB)",
            managed="Unmanaged",
            owner="(unowned)",
            business_owner="(unowned)",
            bu="Unknown",
            location="Plant network / guest adjacency",
            cmdb_ci="",
            cmdb_status="Missing from CMDB",
            last_seen=today - timedelta(days=7),
            first_seen=today - timedelta(days=7),
            sources="Network discovery · SOC alert only",
            ip_or_id="10.80.2.19",
            hostname="(unknown)",
            fqdn="",
            serial="",
            cost_center="",
            steward="",
            tech_contact="",
            config_baseline="",
            os_or_runtime="Unknown",
            version="",
            patch_level="",
            change_window="",
            data_class="Unknown",
            processing_purpose="Unknown — quarantined pending owner hunt",
            data_subjects="Unknown",
            personal_data_elements="Under review",
            retention="",
            legal_basis="",
            scope_tags="Out of declared scope until classified — discovery intake",
            verification="Unverified",
            last_verified=pd.NaT,
            confidence=10,
            record_quality="Discovery stub only",
            applicable_controls="A.8.1 — establish ownership",
            related_services="",
            upstream_cis="",
            downstream_cis="",
            vendor_link="",
            internet_facing=False,
            edr=False,
            vuln_scan=False,
            siem=False,
            backup=False,
            mfa_admin="None",
            linked_bia="",
            linked_risk="Related pattern to INC-2026-005",
            crown_jewel_reason="",
            summary="Unknown asset intake — cannot enter ISO scope until owned and classified.",
        ),
        ci(
            asset_id="AST-2026-015",
            name="GDPS secondary sysplex (DR)",
            asset_class="Mainframe",
            subtype="z/OS DR sysplex",
            env="DR",
            criticality="Crown jewel",
            lifecycle="Active",
            managed="Managed",
            owner="Mainframe · Maya Chen",
            business_owner="Treasury",
            bu="Finance",
            location="NorthStack colo · secondary",
            cmdb_ci="ci_zos_sysplex_b",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=8),
            first_seen=today - timedelta(days=2000),
            sources="CMDB · GDPS · colo",
            ip_or_id="sysplex-B",
            hostname="SYSPLEXB",
            fqdn="sysplexb.dr.corp.local",
            serial="DR CPC set",
            cost_center="CC-4100",
            steward="Mainframe",
            tech_contact="Maya Chen",
            config_baseline="GDPS Metro mirror of sysplex-A",
            os_or_runtime="z/OS 3.1",
            version="3.1",
            patch_level="Aligned to prod RSU",
            change_window="With GDPS exercises",
            data_class="Confidential",
            processing_purpose="DR target for settlement",
            data_subjects="Same as prod (mirror)",
            personal_data_elements="Mirrored",
            retention="Mirror of prod",
            legal_basis="Same as prod",
            scope_tags="ISO 27001 · SOC 2 · BCM",
            verification="Verified",
            last_verified=today - timedelta(days=55),
            confidence=87,
            record_quality="Tied to EXR-2026-003 / REM-BC-014",
            applicable_controls="A.8.13 · A.8.14 · CP-06 · CP-07",
            related_services="SVC-2026-001",
            upstream_cis="AST-2026-003",
            downstream_cis="",
            vendor_link="VND-2026-002",
            internet_facing=False,
            edr=False,
            vuln_scan=False,
            siem=True,
            backup=True,
            mfa_admin="RACF",
            linked_bia="BIA-2026-001",
            linked_risk="EXR-2026-003 · VND-2026-002 · REM-BC-014",
            crown_jewel_reason="DR target for settlement.",
            summary="DR CI — capacity coupled to colo and IBM i HA story.",
        ),
        ci(
            asset_id="AST-2026-016",
            name="WMS primary",
            asset_class="Application",
            subtype="Warehouse management",
            env="Production",
            criticality="High",
            lifecycle="Active",
            managed="Partial",
            owner="Ops IT",
            business_owner="Ops · D. Marshall",
            bu="Operations",
            location="DC + warehouse VLAN",
            cmdb_ci="ci_wms_prd",
            cmdb_status="Stale attributes",
            last_seen=today - timedelta(hours=12),
            first_seen=today - timedelta(days=1600),
            sources="CMDB · JDE interface",
            ip_or_id="wms.corp.local",
            hostname="WMS-PRD",
            fqdn="wms.corp.local",
            serial="",
            cost_center="CC-7100 Ops",
            steward="Ops IT",
            tech_contact="D. Marshall",
            config_baseline="Vendor WMS · RF integration",
            os_or_runtime="Windows Server",
            version="",
            patch_level="Unknown — vuln scan gap",
            change_window="Warehouse off-hours",
            data_class="Internal",
            processing_purpose="Pick/pack/ship execution",
            data_subjects="Employees (operators)",
            personal_data_elements="Operator IDs",
            retention="Ops + 3y",
            legal_basis="Employment · contract",
            scope_tags="ISO 27001 candidate · BIA overdue",
            verification="Stale",
            last_verified=today - timedelta(days=200),
            confidence=48,
            record_quality="Stale — BIA-2026-007 overdue; vuln gap",
            applicable_controls="A.8.1 · A.8.8 · A.5.29",
            related_services="",
            upstream_cis="AST-2026-006 JDE",
            downstream_cis="Carrier APIs",
            vendor_link="",
            internet_facing=False,
            edr=True,
            vuln_scan=False,
            siem=True,
            backup=True,
            mfa_admin="AD",
            linked_bia="BIA-2026-007",
            linked_risk="PLN-2026-007 (draft)",
            crown_jewel_reason="",
            summary="WMS — process BIA overdue; scanner coverage gap.",
        ),
        # ── Featured: AI system ──────────────────────────────────────
        ci(
            asset_id="AST-2026-017",
            name="CreditAssist v2 (scoring model)",
            asset_class="AI system / model",
            subtype="Supervised risk-scoring model",
            env="Production",
            criticality="High",
            lifecycle="Active",
            managed="Managed",
            owner="Credit Risk · AI product owner",
            business_owner="Chief Credit Officer",
            bu="Risk",
            location="Model serving VPC · inference API",
            cmdb_ci="ci_ai_creditassist_v2",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=3),
            first_seen=today - timedelta(days=220),
            sources="CMDB · MLflow · model registry · API gateway · AI inventory",
            ip_or_id="model:creditassist-v2",
            hostname="creditassist-infer",
            fqdn="creditassist.ml.corp.local",
            serial="Model card MC-CA-2026-02",
            cost_center="CC-4400 Credit Risk",
            steward="Model Risk Management + AI product owner",
            tech_contact="ML Eng on-call · Credit analytics",
            config_baseline="Registered model v2.3.1 · challenger v2.4.0 in staging",
            os_or_runtime="Python 3.11 · scikit/xgboost serving",
            version="2.3.1",
            patch_level="Feature store snapshot 2026-08-01",
            change_window="Model change board · monthly promote window",
            data_class="Confidential",
            processing_purpose="Assist credit analysts with recommended score band; human approves final decision",
            data_subjects="Credit applicants (consumers / SMEs)",
            personal_data_elements="Application attributes, bureau-derived features (licensed), outcome labels",
            retention="Scores 5y; training sets per MRM policy; features per FS-RET-01",
            legal_basis="Contract · legitimate interest (credit risk) · fair lending review",
            scope_tags="ISO/IEC 42001 inventory · ISO 27001 · Model risk · AI gov standup",
            verification="Verified",
            last_verified=today - timedelta(days=14),
            confidence=86,
            record_quality="AI SoT exemplar — intended use, oversight, prohibited use, training lineage on the CI",
            applicable_controls="ISO 42001 4–8 themes · A.5.9 · A.8.11 · A.5.34 · MRM-01 · MRM-04",
            related_services="SVC-2026-006",
            upstream_cis="AST-2026-018 feature store · bureau feeds · AST-2026-013 (limited)",
            downstream_cis="Credit workstation UI · decision archive",
            vendor_link="Bureau data licenses · cloud GPU (training)",
            ai_intended_use="Decision support for credit analysts; not autonomous decline/approve",
            ai_training_sources="Historical applications (licensed) · bureau features · internal performance labels — no scraped web PII",
            ai_human_oversight="Analyst must accept/override; overrides logged; monthly override QA sample",
            ai_prohibited_use="No fully automated denial; no use for employment/housing; no biometric inference",
            internet_facing=False,
            edr=False,
            vuln_scan=True,
            siem=True,
            backup=True,
            mfa_admin="Cloud IAM + break-glass for registry",
            linked_bia="",
            linked_risk="MRM findings register · AI gov backlog",
            crown_jewel_reason="",
            summary="AI system CI built as a true record: purpose, data, oversight, prohibitions, model version, and service link. This is what an AI-governance inventory row should look like when it lives in the same SoT as servers.",
            attribute_dict=[
                {"attr": "Model card", "value": "MC-CA-2026-02 approved", "source": "MRM", "as_of": "2026-08-10"},
                {"attr": "Fairness test", "value": "Pass w/ monitoring", "source": "MRM", "as_of": "2026-08-10"},
                {"attr": "Drift monitor", "value": "Enabled — PSI alert", "source": "MLOps", "as_of": "live"},
                {"attr": "Override rate", "value": "11% (30d)", "source": "Credit UI", "as_of": "2026-08"},
                {"attr": "Challenger", "value": "v2.4.0 staging", "source": "Registry", "as_of": "2026-08-18"},
                {"attr": "Training PII", "value": "Licensed bureau + apps only", "source": "Model card", "as_of": "2026-08-10"},
                {"attr": "Autonomous decision", "value": "Prohibited", "source": "AI policy", "as_of": "policy"},
            ],
        ),
        ci(
            asset_id="AST-2026-018",
            name="Credit feature store (prod)",
            asset_class="Database",
            subtype="Feature store / offline+online",
            env="Production",
            criticality="High",
            lifecycle="Active",
            managed="Managed",
            owner="ML Eng / Data platform",
            business_owner="Credit Risk",
            bu="Risk",
            location="Analytics VPC",
            cmdb_ci="ci_ai_featurestore_credit",
            cmdb_status="In sync",
            last_seen=today - timedelta(hours=2),
            first_seen=today - timedelta(days=300),
            sources="CMDB · Feast/equiv · data catalog",
            ip_or_id="fs-credit.ml.corp.local",
            hostname="fs-credit",
            fqdn="fs-credit.ml.corp.local",
            serial="",
            cost_center="CC-4400",
            steward="Data platform",
            tech_contact="ML Eng",
            config_baseline="Encrypted · row-level access · lineage tags required",
            os_or_runtime="Feature platform",
            version="2026.7",
            patch_level="",
            change_window="With model board",
            data_class="Confidential",
            processing_purpose="Store and serve features for CreditAssist",
            data_subjects="Applicants",
            personal_data_elements="Derived features; some directly identifying keys",
            retention="FS-RET-01",
            legal_basis="Same as CreditAssist",
            scope_tags="ISO 42001 · ISO 27001 · data catalog",
            verification="Verified",
            last_verified=today - timedelta(days=21),
            confidence=82,
            record_quality="Lineage to model CI required for AI gov",
            applicable_controls="A.8.11 · A.8.12 · A.5.34",
            related_services="SVC-2026-006",
            upstream_cis="Bureau ETL · application DB",
            downstream_cis="AST-2026-017",
            vendor_link="",
            internet_facing=False,
            edr=False,
            vuln_scan=True,
            siem=True,
            backup=True,
            mfa_admin="Cloud IAM",
            linked_bia="",
            linked_risk="",
            crown_jewel_reason="",
            summary="Feature store supporting AI system — lineage is the SoT point.",
        ),
    ]

    gaps = [
        {"gap_id": "GAP-2026-001", "asset_id": "AST-2026-005", "gap_type": "Missing SIEM", "severity": "High", "status": "Open", "opened": today - timedelta(days=28), "due": today + timedelta(days=3), "owner": "Jordan Blake", "detail": "Jump host not onboarded to SIEM — INC-2026-008 sibling. PBC-2026-003 evidence gap."},
        {"gap_id": "GAP-2026-002", "asset_id": "AST-2026-005", "gap_type": "Missing CMDB CI", "severity": "High", "status": "Open", "opened": today - timedelta(days=28), "due": today + timedelta(days=7), "owner": "Asset Mgmt", "detail": "Exists in AD + EDR; no cmdb_ci. Blocks ISO scope completeness."},
        {"gap_id": "GAP-2026-003", "asset_id": "AST-2026-002", "gap_type": "Stale CMDB attribute", "severity": "Medium", "status": "Open", "opened": today - timedelta(days=15), "due": today + timedelta(days=14), "owner": "Infra", "detail": "CMDB OS version disagrees with vuln scanner (EOL). Verification=Conflict."},
        {"gap_id": "GAP-2026-004", "asset_id": "AST-2026-002", "gap_type": "No EDR (expected for appliance)", "severity": "Low", "status": "Accepted", "opened": today - timedelta(days=100), "due": today + timedelta(days=200), "owner": "SecOps", "detail": "Appliance class — IDS/WAF/geo-block compensating."},
        {"gap_id": "GAP-2026-005", "asset_id": "AST-2026-011", "gap_type": "Lifecycle conflict", "severity": "High", "status": "Open", "opened": today - timedelta(days=2), "due": today + timedelta(days=5), "owner": "Asset Mgmt / Infra", "detail": "CMDB Retired but EDR last_seen 2d ago."},
        {"gap_id": "GAP-2026-006", "asset_id": "AST-2026-011", "gap_type": "Missing SIEM", "severity": "Medium", "status": "Open", "opened": today - timedelta(days=2), "due": today + timedelta(days=5), "owner": "SecOps", "detail": "If host stays live, SIEM required."},
        {"gap_id": "GAP-2026-007", "asset_id": "AST-2026-014", "gap_type": "Unknown / unmanaged asset", "severity": "Critical", "status": "Open", "opened": today - timedelta(days=7), "due": today + timedelta(days=2), "owner": "SOC / Asset Mgmt", "detail": "SMB share discovered. Quarantine + owner hunt before any scope claim."},
        {"gap_id": "GAP-2026-008", "asset_id": "AST-2026-014", "gap_type": "Missing CMDB CI", "severity": "Critical", "status": "Open", "opened": today - timedelta(days=7), "due": today + timedelta(days=2), "owner": "Asset Mgmt", "detail": "Create CI or confirm rogue and remove."},
        {"gap_id": "GAP-2026-009", "asset_id": "AST-2026-001", "gap_type": "Privileged control exception", "severity": "High", "status": "Accepted", "opened": today - timedelta(days=110), "due": today + timedelta(days=45), "owner": "IBM i Ops / GRC", "detail": "*ALLOBJ under EXC-2026-011 — INC-2026-003."},
        {"gap_id": "GAP-2026-010", "asset_id": "AST-2026-016", "gap_type": "Missing vuln scan", "severity": "Medium", "status": "Open", "opened": today - timedelta(days=40), "due": today + timedelta(days=10), "owner": "Ops IT", "detail": "WMS host not in vuln scanner scope."},
        {"gap_id": "GAP-2026-011", "asset_id": "AST-2026-003", "gap_type": "No EDR (platform class)", "severity": "Low", "status": "Accepted", "opened": today - timedelta(days=365), "due": today + timedelta(days=365), "owner": "Mainframe Security", "detail": "SMF + SIEM + RACF coverage model."},
        {"gap_id": "GAP-2026-012", "asset_id": "AST-2026-012", "gap_type": "Vendor residual elevated", "severity": "Critical", "status": "Open", "opened": today - timedelta(days=1), "due": today + timedelta(days=2), "owner": "TPRM", "detail": "INC-2026-009 — track in TPRM; CI stays Active."},
        {"gap_id": "GAP-2026-013", "asset_id": "AST-2026-005", "gap_type": "Record confidence below threshold", "severity": "High", "status": "Open", "opened": today - timedelta(days=28), "due": today + timedelta(days=7), "owner": "Asset Mgmt", "detail": "Confidence 35% — cannot use in scope attestation until CI + owner + SIEM closed."},
        {"gap_id": "GAP-2026-014", "asset_id": "AST-2026-017", "gap_type": "AI inventory — challenger not linked", "severity": "Low", "status": "Open", "opened": today - timedelta(days=6), "due": today + timedelta(days=30), "owner": "MRM", "detail": "Challenger v2.4.0 in staging needs its own CI or explicit link on model card."},
        {"gap_id": "GAP-2026-015", "asset_id": "AST-2026-016", "gap_type": "Verification stale (>90d)", "severity": "Medium", "status": "Open", "opened": today - timedelta(days=20), "due": today + timedelta(days=15), "owner": "Ops IT", "detail": "Last verified ~200d — refresh before SoA evidence pull."},
    ]

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
        {"obs_id": "OBS-013", "asset_id": "AST-2026-017", "adapter": "Model registry", "seen": today - timedelta(hours=3), "key_attr": "v2.3.1 prod stage", "in_cmdb": True},
        {"obs_id": "OBS-014", "asset_id": "AST-2026-017", "adapter": "Inference API gateway", "seen": today - timedelta(minutes=15), "key_attr": "p95 latency OK", "in_cmdb": True},
        {"obs_id": "OBS-015", "asset_id": "AST-2026-018", "adapter": "Data catalog", "seen": today - timedelta(days=1), "key_attr": "lineage to CreditAssist", "in_cmdb": True},
    ]

    deep = {
        "AST-2026-001": {
            "controls": [
                {"control": "A.8.1 Inventory", "status": "Covered", "note": "CI complete; confidence 92%"},
                {"control": "A.8.9 Config mgmt", "status": "Covered", "note": "Baseline + PTF level on record"},
                {"control": "A.8.15 Logging", "status": "Covered", "note": "QAUDJRN → SIEM"},
                {"control": "A.8.8 Vuln", "status": "Covered", "note": "PTF + network scan"},
                {"control": "Privileged access", "status": "Exception", "note": "EXC-2026-011 / INC-2026-003"},
                {"control": "A.8.13 Backup / HA", "status": "Partial", "note": "Mirror OK; Power capacity REM-BC-014"},
            ],
            "evidence": [
                {"ref": "EVD-A-001-A", "desc": "CMDB CI export", "source": "ServiceNow"},
                {"ref": "EVD-A-001-B", "desc": "DSPSYSVAL / PTF evidence pack", "source": "IBM i Ops"},
                {"ref": "EVD-A-001-C", "desc": "HA lag 90d", "source": "HA monitor"},
                {"ref": "EVD-A-001-D", "desc": "BIA-2026-001 linkage", "source": "BCM"},
                {"ref": "EVD-A-001-E", "desc": "Last verification checklist", "source": "Asset Mgmt 2026-08-12"},
            ],
            "open_actions": [
                {"action": "Close/tighten EXC-2026-011 after INC-2026-003", "owner": "GRC / IBM i Ops", "due": today + timedelta(days=5), "status": "Blocked on IR"},
                {"action": "REM-BC-014 secondary Power capacity", "owner": "Infra", "due": today + timedelta(days=45), "status": "In progress"},
                {"action": "Re-verify CI after IR close (confidence refresh)", "owner": "Asset Mgmt", "due": today + timedelta(days=14), "status": "Planned"},
            ],
            "relationships": [
                {"rel": "Supports service", "target": "SVC-2026-001 Core ledger"},
                {"rel": "Supports service", "target": "SVC-2026-002 Order-to-cash"},
                {"rel": "Runs", "target": "AST-2026-006 JDE World"},
                {"rel": "Feeds", "target": "AST-2026-003 IBM Z"},
                {"rel": "Admin path", "target": "AST-2026-002 / jumps"},
            ],
        },
        "AST-2026-002": {
            "controls": [
                {"control": "A.8.20 Network security", "status": "Compensating", "note": "Geo-block, no split-tunnel"},
                {"control": "A.8.8 Vuln / patch", "status": "Gap", "note": "EOL OS — EXC-2026-004"},
                {"control": "A.8.1 Inventory accuracy", "status": "Conflict", "note": "CMDB vs scanner OS"},
                {"control": "SIEM / IDS", "status": "Covered", "note": "INC-2026-010 path validated"},
                {"control": "EDR", "status": "N/A appliance", "note": "Accepted"},
            ],
            "evidence": [
                {"ref": "EVD-A-002-A", "desc": "EXC-2026-004 packet", "source": "Exception register"},
                {"ref": "EVD-A-002-B", "desc": "INC-2026-010 close-out", "source": "IR"},
                {"ref": "EVD-A-002-C", "desc": "Hardware refresh PO", "source": "Procurement"},
                {"ref": "EVD-A-002-D", "desc": "Attribute conflict report", "source": "CAASM"},
            ],
            "open_actions": [
                {"action": "Reconcile CMDB OS/EOL fields", "owner": "Infra", "due": today + timedelta(days=7), "status": "Open"},
                {"action": "Install replacement concentrator", "owner": "Infra", "due": today + timedelta(days=45), "status": "In progress"},
                {"action": "Re-verify → Verified after cutover", "owner": "Asset Mgmt", "due": today + timedelta(days=50), "status": "Planned"},
            ],
            "relationships": [
                {"rel": "Supports service", "target": "SVC-2026-003 Privileged remote access"},
                {"rel": "Fronts", "target": "Jump fleet"},
                {"rel": "Exception", "target": "EXC-2026-004"},
            ],
        },
        "AST-2026-005": {
            "controls": [
                {"control": "A.8.1 Inventory", "status": "Fail", "note": "No CI — confidence 35%"},
                {"control": "EDR", "status": "Covered", "note": "Agent healthy"},
                {"control": "Vuln scan", "status": "Covered", "note": "In scanner"},
                {"control": "SIEM", "status": "Gap", "note": "GAP-2026-001"},
                {"control": "Config baseline", "status": "Gap", "note": "Ad-hoc build"},
                {"control": "Scope readiness", "status": "Fail", "note": "Cannot attest until onboarded"},
            ],
            "evidence": [
                {"ref": "EVD-A-005-A", "desc": "AD computer object", "source": "AD"},
                {"ref": "EVD-A-005-B", "desc": "EDR device page", "source": "CrowdStrike"},
                {"ref": "EVD-A-005-C", "desc": "INC-2026-008 / PBC notes", "source": "IR / Audit"},
                {"ref": "EVD-A-005-D", "desc": "Confidence score card", "source": "CAASM"},
            ],
            "open_actions": [
                {"action": "Create CMDB CI + steward", "owner": "Asset Mgmt", "due": today + timedelta(days=7), "status": "Open"},
                {"action": "Deploy SIEM agent", "owner": "SecOps", "due": today + timedelta(days=3), "status": "In progress"},
                {"action": "Add host class to build template", "owner": "Platform Eng", "due": today + timedelta(days=21), "status": "Planned"},
                {"action": "First verification pass (target confidence ≥80)", "owner": "Asset Mgmt", "due": today + timedelta(days=14), "status": "Blocked on CI"},
            ],
            "relationships": [
                {"rel": "Should support", "target": "SVC-2026-003"},
                {"rel": "Accessed via", "target": "AST-2026-002 VPN"},
                {"rel": "Sibling gaps", "target": "INC-2026-008 cohort"},
            ],
        },
        "AST-2026-017": {
            "controls": [
                {"control": "ISO 42001 — inventory", "status": "Covered", "note": "CI + model card linked"},
                {"control": "Intended use documented", "status": "Covered", "note": "Decision support only"},
                {"control": "Human oversight", "status": "Covered", "note": "Override logged + QA sample"},
                {"control": "Training data lineage", "status": "Covered", "note": "Feature store + bureau licenses"},
                {"control": "Prohibited use", "status": "Covered", "note": "No autonomous denial"},
                {"control": "Drift / fairness monitoring", "status": "Covered", "note": "PSI + fairness watch"},
                {"control": "A.8.11 Data masking/minimization", "status": "Partial", "note": "Feature minimization review due"},
            ],
            "evidence": [
                {"ref": "EVD-A-017-A", "desc": "Model card MC-CA-2026-02", "source": "MRM"},
                {"ref": "EVD-A-017-B", "desc": "Fairness / monitoring pack", "source": "MRM"},
                {"ref": "EVD-A-017-C", "desc": "Registry stage proof v2.3.1", "source": "MLflow"},
                {"ref": "EVD-A-017-D", "desc": "Override QA sample (30d)", "source": "Credit Risk"},
                {"ref": "EVD-A-017-E", "desc": "AI policy excerpt — prohibited uses", "source": "AI governance"},
            ],
            "open_actions": [
                {"action": "Link or create challenger CI (v2.4.0)", "owner": "MRM", "due": today + timedelta(days=30), "status": "Open"},
                {"action": "Feature minimization review", "owner": "Data Protection + ML Eng", "due": today + timedelta(days=45), "status": "Planned"},
                {"action": "Include in next AI gov committee packet", "owner": "AI product owner", "due": today + timedelta(days=21), "status": "Planned"},
            ],
            "relationships": [
                {"rel": "Supports service", "target": "SVC-2026-006 Credit decision assist"},
                {"rel": "Reads", "target": "AST-2026-018 feature store"},
                {"rel": "Governed by", "target": "MRM + AI policy"},
                {"rel": "Human UI", "target": "Credit workstation"},
            ],
        },
    }

    df_a = pd.DataFrame(assets)
    for col in ("last_seen", "first_seen", "last_verified"):
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

    df_svc = pd.DataFrame(services)

    return df_a, df_g, df_s, df_svc


def _coverage_flags(row: pd.Series) -> list[str]:
    flags = []
    if not row.get("edr") and row["asset_class"] in {"Endpoint", "Jump / bastion"}:
        flags.append("No EDR")
    if not row.get("siem"):
        flags.append("No SIEM")
    if not row.get("vuln_scan") and row["asset_class"] not in {"Mainframe", "SaaS / IdP", "AI system / model", "Business service"}:
        flags.append("No vuln scan")
    if row.get("cmdb_status") in {"Missing from CMDB", "Lifecycle conflict", "Stale attributes"}:
        flags.append(row["cmdb_status"])
    if row.get("owner") in {"(unowned)", ""}:
        flags.append("Unowned")
    if row.get("internet_facing"):
        flags.append("Internet-facing")
    if row.get("verification") in {"Conflict", "Unverified", "Stale"}:
        flags.append(f"Verify:{row['verification']}")
    if row.get("confidence", 100) < 70:
        flags.append(f"Confidence {int(row['confidence'])}%")
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
    out["in_iso"] = out["scope_tags"].fillna("").str.contains("ISO 27001", na=False)
    out["in_ai"] = out["scope_tags"].fillna("").str.contains("42001|AI gov", case=False, na=False)
    out["scope_ready"] = (out["confidence"] >= 80) & out["verification"].eq("Verified") & ~out["is_ghost"]
    return out


def _sync(seed: int):
    if st.session_state.get("_ast_seed") != seed or "ast_assets" not in st.session_state:
        a, g, s, svc = _sample(seed)
        st.session_state.ast_assets = a
        st.session_state.ast_gaps = g
        st.session_state.ast_sources = s
        st.session_state.ast_services = svc
        st.session_state._ast_seed = seed
    if "ast_services" not in st.session_state:
        _, _, _, svc = _sample(seed)
        st.session_state.ast_services = svc
    return (
        st.session_state.ast_assets,
        st.session_state.ast_gaps,
        st.session_state.ast_sources,
        st.session_state.ast_services,
    )


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
        return p.strftime("%Y-%m-%d %H:%M") if (p.hour or p.minute) else p.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _metrics(assets, gaps, services):
    e = _enrich(assets)
    open_g = gaps[~gaps["status"].isin(["Closed", "Accepted"])]
    return {
        "total": len(e),
        "crown": int(e["is_crown"].sum()),
        "gaps": int(len(open_g)),
        "ghost": int(e["is_ghost"].sum()),
        "scope_ready": int(e["scope_ready"].sum()),
        "ai_cis": int(e["asset_class"].eq("AI system / model").sum()),
        "services": len(services),
        "low_conf": int((e["confidence"] < 70).sum()),
    }


def _asset_detail(row, gaps, sources, *, expanded=False):
    st.markdown(f"### {row['asset_id']} · {row['name']}")
    a, b, c, d, e = st.columns(5)
    a.metric("Criticality", row["criticality"])
    b.metric("Lifecycle", str(row["lifecycle"]).split("(")[0].strip())
    c.metric("CMDB", row["cmdb_status"])
    d.metric("Verification", row.get("verification", "—"))
    e.metric("Confidence", f"{int(row.get('confidence', 0))}%")

    c1, c2, c3 = st.columns(3)
    c1.write(f"**Class:** {row['asset_class']} · {row['subtype']}")
    c1.write(f"**Env:** {row['env']} · **BU:** {row['bu']}")
    c1.write(f"**Owner:** {row['owner']}")
    c1.write(f"**Business owner:** {row['business_owner']}")
    c1.write(f"**Steward:** {row.get('steward') or '—'}")
    c1.write(f"**Tech contact:** {row.get('tech_contact') or '—'}")
    c1.write(f"**Cost center:** {row.get('cost_center') or '—'}")
    c2.write(f"**Hostname / FQDN:** {row.get('hostname') or '—'} / {row.get('fqdn') or '—'}")
    c2.write(f"**IP / ID:** {row['ip_or_id']}")
    c2.write(f"**Serial:** {row.get('serial') or '—'}")
    c2.write(f"**Location:** {row['location']}")
    c2.write(f"**CI:** {row['cmdb_ci'] or '—'}")
    c2.write(f"**Sources:** {row['sources']}")
    c2.write(f"**Last / first seen:** {_fmt(row['last_seen'])} / {_fmt(row['first_seen'])}")
    c3.write(f"**OS / runtime:** {row.get('os_or_runtime') or '—'}")
    c3.write(f"**Version / patch:** {row.get('version') or '—'} / {row.get('patch_level') or '—'}")
    c3.write(f"**Config baseline:** {row.get('config_baseline') or '—'}")
    c3.write(f"**Change window:** {row.get('change_window') or '—'}")
    c3.write(f"**Last verified:** {_fmt(row.get('last_verified'))}")
    c3.write(f"**Record quality:** {row.get('record_quality') or '—'}")

    cov = {"EDR": row["edr"], "Vuln": row["vuln_scan"], "SIEM": row["siem"], "Backup": row["backup"]}
    cols = st.columns(len(cov))
    for i, (k, v) in enumerate(cov.items()):
        cols[i].metric(k, "Yes" if v else "No")

    st.write(row["summary"])
    if row.get("crown_jewel_reason"):
        st.info(f"Crown jewel: {row['crown_jewel_reason']}")
    if row.get("gap_flags"):
        st.warning("Flags: " + " · ".join(row["gap_flags"]))

    st.markdown("**Processing & data (SoT)**")
    d1, d2 = st.columns(2)
    d1.write(f"**Data class:** {row['data_class']}")
    d1.write(f"**Purpose:** {row.get('processing_purpose') or '—'}")
    d1.write(f"**Data subjects:** {row.get('data_subjects') or '—'}")
    d1.write(f"**Personal data elements:** {row.get('personal_data_elements') or '—'}")
    d2.write(f"**Retention:** {row.get('retention') or '—'}")
    d2.write(f"**Legal basis:** {row.get('legal_basis') or '—'}")
    d2.write(f"**Scope tags:** {row.get('scope_tags') or '—'}")
    d2.write(f"**Applicable controls:** {row.get('applicable_controls') or '—'}")

    if row["asset_class"] == "AI system / model" or row.get("ai_intended_use"):
        st.markdown("**AI system record**")
        st.write(f"**Intended use:** {row.get('ai_intended_use') or '—'}")
        st.write(f"**Training / data sources:** {row.get('ai_training_sources') or '—'}")
        st.write(f"**Human oversight:** {row.get('ai_human_oversight') or '—'}")
        st.write(f"**Prohibited use:** {row.get('ai_prohibited_use') or '—'}")

    st.markdown("**Dependencies**")
    x1, x2, x3 = st.columns(3)
    x1.write(f"**Services:** {row.get('related_services') or '—'}")
    x2.write(f"**Upstream CIs:** {row.get('upstream_cis') or '—'}")
    x3.write(f"**Downstream CIs:** {row.get('downstream_cis') or '—'}")
    if row.get("vendor_link"):
        st.caption(f"Vendor / contract: {row['vendor_link']}")
    if row.get("linked_bia"):
        st.caption(f"BIA: {row['linked_bia']}")
    if row.get("linked_risk"):
        st.caption(f"Risk / IR / TPRM: {row['linked_risk']}")
    st.caption(f"Admin MFA: {row['mfa_admin']} · Internet-facing: {'Yes' if row['internet_facing'] else 'No'}")

    raw = st.session_state.ast_assets
    rr = raw[raw["asset_id"] == row["asset_id"]]
    if not rr.empty:
        r0 = rr.iloc[0]
        attrs = r0.get("attribute_dict") or []
        controls = r0.get("controls") or []
        evid = r0.get("evidence") or []
        acts = r0.get("open_actions") or []
        rels = r0.get("relationships") or []
        if attrs:
            with st.expander(f"Configuration attributes ({len(attrs)})", expanded=expanded):
                st.dataframe(pd.DataFrame(attrs), use_container_width=True, hide_index=True)
        if controls:
            with st.expander(f"Control applicability ({len(controls)})", expanded=expanded):
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
    a1, a2, a3, a4 = st.columns(4)
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
                confidence=max(int(row.get("confidence", 0)), 70),
            )
            st.rerun()
    with a2:
        if not row["siem"] and st.button(
            "Mark SIEM onboarded", key=f"siem_{key}", use_container_width=True
        ):
            _patch_a(aid, siem=True)
            g = st.session_state.ast_gaps
            mask = (g["asset_id"] == aid) & (g["gap_type"] == "Missing SIEM") & (~g["status"].isin(["Closed"]))
            if mask.any():
                g = g.copy()
                g.loc[mask, "status"] = "Closed"
                _save_g(g)
            st.rerun()
    with a3:
        if row.get("verification") != "Verified" and st.button(
            "Mark verified", key=f"ver_{key}", use_container_width=True
        ):
            _patch_a(
                aid,
                verification="Verified",
                last_verified=_today(),
                confidence=max(int(row.get("confidence", 0)), 85),
            )
            st.rerun()
    with a4:
        if row["owner"] in {"(unowned)", ""} and st.button(
            "Assign to Infra", key=f"own_{key}", use_container_width=True
        ):
            _patch_a(aid, owner="Infrastructure · Jordan Blake", business_owner="IT", steward="Infrastructure")
            st.rerun()


def main() -> None:
    portfolio_skin.page_header(
        title="Asset Management System",
        lede="Configuration items as source of truth — services, scope, baselines, verification, AI systems. Club demo — not a system of record.",
        kicker="Cyber assets / CMDB",
    )

    seed = demo_kit.seed_controls()
    assets, gaps, sources, services = _sync(seed)
    ea = _enrich(assets)
    m = _metrics(assets, gaps, services)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    class_f = st.sidebar.multiselect("Class", CLASSES, default=CLASSES)
    crit_f = st.sidebar.multiselect("Criticality", CRITICALITY, default=CRITICALITY)
    life_f = st.sidebar.multiselect("Lifecycle", LIFECYCLES, default=LIFECYCLES)
    scope_only = st.sidebar.checkbox("Scope-ready only (Verified · ≥80% confidence)", value=False)
    filtered = ea[
        ea["asset_class"].isin(class_f)
        & ea["criticality"].isin(crit_f)
        & ea["lifecycle"].isin(life_f)
    ]
    if scope_only:
        filtered = filtered[filtered["scope_ready"]]

    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
    k1.metric("CIs", m["total"])
    k2.metric("Crown jewels", m["crown"])
    k3.metric("Services", m["services"])
    k4.metric("Scope-ready", m["scope_ready"])
    k5.metric("Open gaps", m["gaps"])
    k6.metric("Low confidence", m["low_conf"])
    k7.metric("AI system CIs", m["ai_cis"])

    work, inv, scope_tab, gaps_tab, recon, board, intake, export = st.tabs(
        [
            "Workbench",
            "Inventory",
            "Services & scope",
            "Coverage gaps",
            "Reconciliation",
            "Status board",
            "Intake",
            "Export",
        ]
    )

    with work:
        st.subheader("Asset workbench")
        if m["low_conf"]:
            st.warning(f"{m['low_conf']} CI(s) under 70% record confidence — weak for scope attestation.")
        if m["gaps"]:
            st.warning(f"{m['gaps']} open coverage / reconciliation finding(s).")

        featured = ea[ea["asset_id"].isin(FEATURED)].copy()
        # Keep a stable narrative order
        order = {i: n for n, i in enumerate(["AST-2026-001", "AST-2026-017", "AST-2026-002", "AST-2026-005"])}
        featured["_ord"] = featured["asset_id"].map(lambda x: order.get(x, 99))
        featured = featured.sort_values("_ord")

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
        st.subheader("CI inventory")
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
                "verification",
                "confidence",
                "scope_ready",
                "owner",
                "cmdb_status",
                "gap_count",
            ]
        ].copy()
        st.dataframe(show, use_container_width=True, hide_index=True)

    with scope_tab:
        st.subheader("Business services & engagement scope")
        st.caption(
            "Services are the unit of scope. CIs underpin services. "
            "A defensible ISO / AI-gov inventory starts here — not with a laptop list."
        )
        for _, svc in services.iterrows():
            tags = []
            if svc["scope_iso27001"]:
                tags.append("ISO 27001")
            if svc["scope_soc2"]:
                tags.append("SOC 2")
            if svc["scope_ai_gov"]:
                tags.append("AI gov / 42001")
            if svc["scope_pci"]:
                tags.append("PCI")
            with st.expander(
                f"{svc['service_id']} · {svc['name']} · {svc['criticality']} · {', '.join(tags)}"
            ):
                st.write(svc["description"])
                s1, s2 = st.columns(2)
                s1.write(f"**Owner:** {svc['owner']}")
                s1.write(f"**Users:** {svc['users']}")
                s1.write(f"**RTO / RPO:** {svc['rto_h']}h / {svc['rpo_h']}h")
                s1.write(f"**BIA:** {svc['bia'] or '—'}")
                s2.write(f"**Supporting assets:** {svc['supporting_assets']}")
                s2.write(f"**Scope tags:** {', '.join(tags)}")
                # Readiness of supporting CIs
                ids = [x.strip() for x in str(svc["supporting_assets"]).split(",") if x.strip()]
                kids = ea[ea["asset_id"].isin(ids)][
                    ["asset_id", "name", "verification", "confidence", "scope_ready", "cmdb_status"]
                ]
                st.dataframe(kids, use_container_width=True, hide_index=True)

        st.markdown("**Scope-ready CIs** (Verified · confidence ≥ 80 · not ghost)")
        ready = ea[ea["scope_ready"]][
            ["asset_id", "name", "asset_class", "criticality", "confidence", "scope_tags"]
        ]
        st.dataframe(ready, use_container_width=True, hide_index=True)

        st.markdown("**AI governance inventory slice**")
        ai = ea[ea["in_ai"] | ea["asset_class"].eq("AI system / model")][
            [
                "asset_id",
                "name",
                "version",
                "ai_intended_use",
                "ai_human_oversight",
                "confidence",
                "related_services",
            ]
        ]
        st.dataframe(ai, use_container_width=True, hide_index=True)

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
            "Adapters disagree on purpose: discovery vs CMDB vs registry. "
            "The SoT move is to surface mismatch and drive create/update — not average it away."
        )
        show = sources.copy()
        show["seen"] = show["seen"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

        miss = ea[ea["cmdb_status"].isin(["Missing from CMDB", "Lifecycle conflict", "Stale attributes"])]
        st.markdown(f"**CMDB mismatches ({len(miss)})**")
        st.dataframe(
            miss[["asset_id", "name", "cmdb_status", "verification", "confidence", "lifecycle"]].assign(
                last_seen=miss["last_seen"].apply(_fmt)
            ),
            use_container_width=True,
            hide_index=True,
        )

    with board:
        st.subheader("Status board")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.histogram(
                ea,
                x="confidence",
                color="verification",
                nbins=10,
                title="Record confidence by verification state",
            )
            st.plotly_chart(fig, use_container_width=True)
        with c2:
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

        melt = ea.melt(
            id_vars=["asset_id", "criticality"],
            value_vars=["edr", "vuln_scan", "siem", "backup"],
            var_name="control",
            value_name="covered",
        )
        melt["covered"] = melt["covered"].astype(int)
        fig = px.scatter(
            melt,
            x="control",
            y="asset_id",
            color="covered",
            title="Control coverage (1=yes)",
            color_continuous_scale=["#ff6b6b", "#38e881"],
        )
        st.plotly_chart(fig, use_container_width=True)

        ready_counts = (
            ea["scope_ready"]
            .value_counts()
            .rename({True: "Scope-ready", False: "Not ready"})
            .rename_axis("state")
            .reset_index(name="count")
        )
        fig = px.pie(ready_counts, names="state", values="count", title="Scope readiness")
        st.plotly_chart(fig, use_container_width=True)

    with intake:
        st.subheader("Register / discover CI")
        with st.form("intake"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Name")
                asset_class = st.selectbox("Class", [c for c in CLASSES if c != "Business service"])
                env = st.selectbox("Environment", ENVS)
                criticality = st.selectbox("Criticality", CRITICALITY, index=2)
                purpose = st.text_input("Processing purpose")
            with c2:
                owner = st.text_input("Owner", placeholder="team · person")
                in_cmdb = st.checkbox("Already in CMDB")
                internet = st.checkbox("Internet-facing")
                edr = st.checkbox("EDR present", value=asset_class == "Endpoint")
                scope_iso = st.checkbox("Tag ISO 27001 candidate")
                scope_ai = st.checkbox("Tag AI gov / 42001 candidate")
            sources_txt = st.text_input("Discovery sources", value="Manual intake")
            if st.form_submit_button("Create"):
                if not name.strip():
                    st.error("Name required.")
                else:
                    n = len(st.session_state.ast_assets) + 1
                    today = _today()
                    aid = f"AST-2026-{n:03d}"
                    tags = []
                    if scope_iso:
                        tags.append("ISO 27001 candidate")
                    if scope_ai:
                        tags.append("AI gov / 42001 candidate")
                    add = _blank_sot()
                    add.update(
                        {
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
                            "processing_purpose": purpose.strip() or "TBD",
                            "scope_tags": " · ".join(tags),
                            "verification": "Unverified",
                            "last_verified": pd.NaT,
                            "confidence": 40 if in_cmdb else 25,
                            "record_quality": "Intake stub — enrich before scope use",
                            "internet_facing": bool(internet),
                            "edr": bool(edr),
                            "vuln_scan": False,
                            "siem": False,
                            "backup": False,
                            "mfa_admin": "TBD",
                            "linked_bia": "",
                            "linked_risk": "",
                            "crown_jewel_reason": "",
                            "summary": "Intake / discovery record — enrich ownership, purpose, baseline, and verification.",
                            "controls": [],
                            "evidence": [],
                            "open_actions": [],
                            "relationships": [],
                            "attribute_dict": [],
                        }
                    )
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
        for col in ("last_seen", "first_seen", "last_verified"):
            if col in out.columns:
                out[col] = out[col].apply(_fmt)
        out["gap_flags"] = out["gap_flags"].apply(lambda x: "; ".join(x) if isinstance(x, list) else x)
        for col in ("controls", "evidence", "open_actions", "relationships", "attribute_dict"):
            if col in out.columns:
                out = out.drop(columns=[col])
        demo_kit.csv_download(out, "assets_cmdb.csv", label="Download CI inventory")
        demo_kit.csv_download(services, "business_services.csv", label="Download services", key="svc_csv")
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
