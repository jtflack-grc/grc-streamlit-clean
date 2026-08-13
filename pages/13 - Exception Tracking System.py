#!/usr/bin/env python3
"""Control-exception / policy-waiver register — club teaching toy."""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Exception Tracking System · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

STATUSES = ["Submitted", "In Review", "Approved", "Denied", "Expired", "Closed"]
RISK_ORDER = ["Critical", "High", "Medium", "Low"]
STATUS_COLOR = {
    "Submitted": "#91aa9b",
    "In Review": "#f2b84b",
    "Approved": "#38e881",
    "Denied": "#e8f4ec",
    "Expired": "#ff6b6b",
    "Closed": "#5c7a68",
}


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _sample_exceptions(seed: int) -> pd.DataFrame:
    """Time-boxed waivers a GRC team would actually keep in a register."""
    today = _today()
    rng = np.random.default_rng(seed)

    def jitter(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    rows = [
        {
            "exception_id": "EXC-2026-001",
            "title": "MFA not enforced on IBM i 5250 sessions",
            "control": "AC-07 MFA / ISO A.8.5",
            "system_asset": "IBM i (PRODBOX)",
            "category": "Access",
            "exception_type": "Time-boxed waiver",
            "status": "Approved",
            "residual_risk": "High",
            "requestor": "IBM i Ops",
            "owner": "IAM",
            "approver": "CISO",
            "business_justification": "TN5250 clients used by plant supervisors do not support MFA; replacement client is in FY27 roadmap.",
            "compensating_control": "VPN + source-IP restrict; QAUDJRN on *SIGNON; weekly DSPUSRPRF of interactive profiles",
            "conditions": "No new interactive profiles without Security sign-off. Exit by 5250 client cutover.",
            "linked_finding": "AUD-2026-014",
            "extension_count": 1,
            "requested": today - timedelta(days=120),
            "effective": today - timedelta(days=110),
            "expiration": today + timedelta(days=45 + jitter(-4, 5)),
            "next_review": today + timedelta(days=12),
        },
        {
            "exception_id": "EXC-2026-002",
            "title": "Quarterly access recertification slipped — Citrix VDI",
            "control": "AC-02 Access review / SOC 2 CC6.2",
            "system_asset": "Citrix VDI",
            "category": "Access",
            "exception_type": "Time-boxed waiver",
            "status": "Expired",
            "residual_risk": "Medium",
            "requestor": "IT Operations",
            "owner": "IAM",
            "approver": "IT Manager",
            "business_justification": "Staffing gap during Q2; recert campaign not launched.",
            "compensating_control": "None in place — joiner/mover/leaver still via ticket only",
            "conditions": "Complete recert within 30 days of approval. No further extension without CISO.",
            "linked_finding": "AUD-2026-022",
            "extension_count": 2,
            "requested": today - timedelta(days=200),
            "effective": today - timedelta(days=190),
            "expiration": today - timedelta(days=18 + jitter(0, 6)),
            "next_review": today - timedelta(days=18),
        },
        {
            "exception_id": "EXC-2026-003",
            "title": "Audit logging disabled on Oracle DB for perf test",
            "control": "AU-02 Audit logging / ISO A.8.15",
            "system_asset": "Oracle DB (FINPROD)",
            "category": "Logging",
            "exception_type": "Time-boxed waiver",
            "status": "In Review",
            "residual_risk": "High",
            "requestor": "Database Team",
            "owner": "Security Engineering",
            "approver": "",
            "business_justification": "Month-end close job overruns SLA with unified auditing on; DBA wants a 14-day window.",
            "compensating_control": "Host OS audit + network IDS on DB subnet; change freeze except this job",
            "conditions": "Production only. Re-enable unified auditing at window end. CISO approval required.",
            "linked_finding": "",
            "extension_count": 0,
            "requested": today - timedelta(days=3),
            "effective": pd.NaT,
            "expiration": today + timedelta(days=14),
            "next_review": today + timedelta(days=7),
        },
        {
            "exception_id": "EXC-2026-004",
            "title": "Legacy VPN concentrator OS unsupported by EDR",
            "control": "SI-02 Malware protection / ISO A.8.7",
            "system_asset": "VPN Gateway",
            "category": "Endpoint",
            "exception_type": "Time-boxed waiver",
            "status": "Approved",
            "residual_risk": "Medium",
            "requestor": "Network Team",
            "owner": "Infrastructure",
            "approver": "IT Director",
            "business_justification": "Hardware refresh PO approved; lead time 10 weeks. Current image has no EDR agent.",
            "compensating_control": "Management plane on jump host; weekly config diff; no split-tunnel; geo-block",
            "conditions": "No feature changes on the box. Cutover by refresh date. Do not extend past hardware arrival + 14 days.",
            "linked_finding": "VM-2026-088",
            "extension_count": 0,
            "requested": today - timedelta(days=40),
            "effective": today - timedelta(days=35),
            "expiration": today + timedelta(days=16 + jitter(-3, 4)),
            "next_review": today + timedelta(days=5),
        },
        {
            "exception_id": "EXC-2026-005",
            "title": "Standing admin on time-tracking app",
            "control": "AC-06 Least privilege / ISO A.8.2",
            "system_asset": "Time Tracking System",
            "category": "Privileged access",
            "exception_type": "Risk acceptance",
            "status": "Denied",
            "residual_risk": "High",
            "requestor": "HR IT",
            "owner": "IAM",
            "approver": "CISO",
            "business_justification": "Vendor console has no JIT / PAM integration; payroll ops want 24/7 admin.",
            "compensating_control": "Proposed: named accounts + monthly log review (not implemented)",
            "conditions": "Standing privileged access is out of policy. Use break-glass with 8-hour expiry.",
            "linked_finding": "",
            "extension_count": 0,
            "requested": today - timedelta(days=28),
            "effective": pd.NaT,
            "expiration": today - timedelta(days=5),
            "next_review": pd.NaT,
        },
        {
            "exception_id": "EXC-2026-006",
            "title": "Vendor-controlled IPs permitted through edge firewall",
            "control": "SC-07 Boundary protection / PCI 1.3",
            "system_asset": "Cloud IAM / edge FW",
            "category": "Network",
            "exception_type": "Time-boxed waiver",
            "status": "Approved",
            "residual_risk": "Medium",
            "requestor": "Cloud Team",
            "owner": "Network Security",
            "approver": "IT Director",
            "business_justification": "Payroll SaaS file-drop still uses vendor NAT pool; they will publish FQDN allow-list in Q4.",
            "compensating_control": "Allow-list to SFTP DMZ only; TLS 1.2+; vendor IPs reviewed monthly; no inbound shell",
            "conditions": "Replace with FQDN/egress proxy by expiration. Any new vendor IP requires a change ticket.",
            "linked_finding": "",
            "extension_count": 0,
            "requested": today - timedelta(days=55),
            "effective": today - timedelta(days=50),
            "expiration": today + timedelta(days=70 + jitter(-5, 6)),
            "next_review": today + timedelta(days=20),
        },
        {
            "exception_id": "EXC-2026-007",
            "title": "Critical patch deferred — backup appliance vendor hold",
            "control": "SI-02 Patch SLA / ISO A.8.8",
            "system_asset": "Backup Appliance",
            "category": "Patching",
            "exception_type": "Time-boxed waiver",
            "status": "Approved",
            "residual_risk": "Critical",
            "requestor": "Infrastructure",
            "owner": "Vulnerability Mgmt",
            "approver": "CISO",
            "business_justification": "Vendor PSIRT: patch bricks replication on our code-level. Hotfix promised.",
            "compensating_control": "Appliance isolated to backup VLAN; admin via PAM; IDS on replication ports; daily vendor PSIRT check",
            "conditions": "Apply hotfix within 7 days of vendor release. No internet admin. Max one extension.",
            "linked_finding": "VM-2026-104",
            "extension_count": 0,
            "requested": today - timedelta(days=21),
            "effective": today - timedelta(days=20),
            "expiration": today + timedelta(days=6 + jitter(-2, 3)),
            "next_review": today + timedelta(days=2),
        },
        {
            "exception_id": "EXC-2026-008",
            "title": "Web farm excluded from central monitoring (license cap)",
            "control": "SI-04 Monitoring / SOC 2 CC7.2",
            "system_asset": "Linux Web Server farm",
            "category": "Logging",
            "exception_type": "Time-boxed waiver",
            "status": "Closed",
            "residual_risk": "Low",
            "requestor": "Web Team",
            "owner": "SecOps",
            "approver": "IT Manager",
            "business_justification": "License shortfall during FY26 true-up.",
            "compensating_control": "Was: host syslog to local disk. Now: SIEM onboarded after license add.",
            "conditions": "Closed — control operating as designed.",
            "linked_finding": "",
            "extension_count": 1,
            "requested": today - timedelta(days=160),
            "effective": today - timedelta(days=150),
            "expiration": today - timedelta(days=20),
            "next_review": pd.NaT,
        },
        {
            "exception_id": "EXC-2026-009",
            "title": "SMBv1 required by legacy CRM file share",
            "control": "SC-08 Transmission / CIS 4.8",
            "system_asset": "Legacy CRM",
            "category": "Network",
            "exception_type": "Time-boxed waiver",
            "status": "Approved",
            "residual_risk": "High",
            "requestor": "Business Systems",
            "owner": "Infrastructure",
            "approver": "CISO",
            "business_justification": "Vendor sunset is 2027; plant floor PCs cannot speak SMBv2 without a line-stop.",
            "compensating_control": "Share VLAN isolated; SMB signing where possible; no internet path; weekly vuln scan",
            "conditions": "No additional SMBv1 hosts. Migration milestone review each quarter. Third extension requires Risk Committee.",
            "linked_finding": "AUD-2025-061",
            "extension_count": 2,
            "requested": today - timedelta(days=400),
            "effective": today - timedelta(days=390),
            "expiration": today + timedelta(days=85 + jitter(-6, 7)),
            "next_review": today + timedelta(days=25),
        },
        {
            "exception_id": "EXC-2026-010",
            "title": "Backup job encryption paused after failed script",
            "control": "SC-28 Encryption at rest / ISO A.8.24",
            "system_asset": "Wireless Controllers / backup",
            "category": "Encryption",
            "exception_type": "Time-boxed waiver",
            "status": "Submitted",
            "residual_risk": "High",
            "requestor": "Network Team",
            "owner": "Infrastructure",
            "approver": "",
            "business_justification": "Nightly config backup job failing after key-rotation; ops paused encryption to restore recoverability.",
            "compensating_control": "Backups land on encrypted volume; access limited to backup operators; restore test this week",
            "conditions": "Pending Security review. Encryption must resume within 14 days of approval.",
            "linked_finding": "",
            "extension_count": 0,
            "requested": today - timedelta(days=1),
            "effective": pd.NaT,
            "expiration": today + timedelta(days=14),
            "next_review": today + timedelta(days=7),
        },
        {
            "exception_id": "EXC-2026-011",
            "title": "*ALLOBJ retained on production ops profiles",
            "control": "AC-06 Least privilege / IBM i Security Standard",
            "system_asset": "IBM i (PRODBOX)",
            "category": "Privileged access",
            "exception_type": "Time-boxed waiver",
            "status": "Approved",
            "residual_risk": "Critical",
            "requestor": "IBM i Ops",
            "owner": "IBM i Security",
            "approver": "CISO",
            "business_justification": "Nightly save / restore and vendor PTF apply still coded to *ALLOBJ. Split-owner project in flight.",
            "compensating_control": "QAUDJRN *AUTFAIL *SAVRST; weekly DSPUSRPRF; profiles signoff via PAM checkout 4h max",
            "conditions": "Named profiles only (no QSECOFR day-use). Remove *ALLOBJ from batch by expiration.",
            "linked_finding": "IBMi-2026-007",
            "extension_count": 1,
            "requested": today - timedelta(days=95),
            "effective": today - timedelta(days=90),
            "expiration": today + timedelta(days=19 + jitter(-3, 4)),
            "next_review": today - timedelta(days=2),
            "review_note": "Weekly review is overdue.",
        },
        {
            "exception_id": "EXC-2026-012",
            "title": "RACF SPECIAL on contractor TSO IDs past project end",
            "control": "AC-02 Account management / RACF standard",
            "system_asset": "IBM Z (z/OS)",
            "category": "Privileged access",
            "exception_type": "Time-boxed waiver",
            "status": "Expired",
            "residual_risk": "Critical",
            "requestor": "Mainframe Security",
            "owner": "Mainframe Security",
            "approver": "CISO",
            "business_justification": "Migration project overrun; contractor SPECIAL not revoked at original end date.",
            "compensating_control": "Daily SMF / RACF auditor extract of SPECIAL use — still running, IDs still active",
            "conditions": "Revoke at project close. Expired — treat as unauthorized standing access until closed or re-approved.",
            "linked_finding": "MF-2026-003",
            "extension_count": 1,
            "requested": today - timedelta(days=150),
            "effective": today - timedelta(days=140),
            "expiration": today - timedelta(days=12 + jitter(0, 5)),
            "next_review": today - timedelta(days=12),
        },
        {
            "exception_id": "EXC-2026-013",
            "title": "SAP_ALL on dual-control break-glass until Firefighter live",
            "control": "AC-06 Least privilege / SAP security standard",
            "system_asset": "SAP ECC",
            "category": "Privileged access",
            "exception_type": "Time-boxed waiver",
            "status": "In Review",
            "residual_risk": "High",
            "requestor": "SAP Basis",
            "owner": "ERP Security",
            "approver": "",
            "business_justification": "GRC Firefighter workflow delayed; month-end still needs emergency SU01 path.",
            "compensating_control": "ST01 session logging; dual approval ticket; password in PAM; 4-hour checkout",
            "conditions": "Two named IDs only. Firefighter go-live is the exit. Risk Committee if >90 days.",
            "linked_finding": "SAP-2026-011",
            "extension_count": 0,
            "requested": today - timedelta(days=8),
            "effective": pd.NaT,
            "expiration": today + timedelta(days=60),
            "next_review": today + timedelta(days=14),
        },
        {
            "exception_id": "EXC-2026-014",
            "title": "AD service account password-never-expires",
            "control": "IA-05 Authenticator management / CIS 5.2",
            "system_asset": "Windows AD (on-prem)",
            "category": "Access",
            "exception_type": "Time-boxed waiver",
            "status": "Approved",
            "residual_risk": "Medium",
            "requestor": "Windows Engineering",
            "owner": "IAM",
            "approver": "IT Director",
            "business_justification": "Print-spooler and backup agents fail when the password rotates; gMSA conversion scheduled.",
            "compensating_control": "LAPS/gMSA for new accounts; these 6 accounts in PAM vault; Kerberos AES; no interactive logon",
            "conditions": "Convert to gMSA by expiration. No additional never-expire flags.",
            "linked_finding": "",
            "extension_count": 0,
            "requested": today - timedelta(days=33),
            "effective": today - timedelta(days=30),
            "expiration": today + timedelta(days=28 + jitter(-4, 5)),
            "next_review": today + timedelta(days=14),
        },
        {
            "exception_id": "EXC-2026-015",
            "title": "Oracle EBS APPS schema used by batch jobs",
            "control": "AC-06 Least privilege / Oracle EBS standard",
            "system_asset": "Oracle E-Business Suite",
            "category": "Privileged access",
            "exception_type": "Time-boxed waiver",
            "status": "Approved",
            "residual_risk": "High",
            "requestor": "ERP Ops",
            "owner": "Database Team",
            "approver": "CISO",
            "business_justification": "Concurrent Manager customizations still connect as APPS; proxy-user rewrite in sprint 3.",
            "compensating_control": "APPS login from app tier only; Unified Audit on APPS; no ad-hoc SQL*Plus for humans",
            "conditions": "Human APPS use remains prohibited. Proxy-user cutover is the exit.",
            "linked_finding": "EBS-2026-004",
            "extension_count": 0,
            "requested": today - timedelta(days=48),
            "effective": today - timedelta(days=44),
            "expiration": today + timedelta(days=52 + jitter(-5, 6)),
            "next_review": today + timedelta(days=16),
        },
        {
            "exception_id": "EXC-2026-016",
            "title": "AIX adopted authority on shared run user",
            "control": "AC-06 Least privilege / AIX security standard",
            "system_asset": "AIX LPAR (nfin01)",
            "category": "Privileged access",
            "exception_type": "Time-boxed waiver",
            "status": "Closed",
            "residual_risk": "Low",
            "requestor": "UNIX Team",
            "owner": "UNIX Team",
            "approver": "IT Director",
            "business_justification": "Was required for a vendor agent; agent now runs with dedicated UID.",
            "compensating_control": "N/A — remediated. Adopted authority removed; vendor UID confined.",
            "conditions": "Closed after config review 2026-07-22.",
            "linked_finding": "",
            "extension_count": 0,
            "requested": today - timedelta(days=110),
            "effective": today - timedelta(days=100),
            "expiration": today - timedelta(days=40),
            "next_review": pd.NaT,
        },
        {
            "exception_id": "EXC-2026-017",
            "title": "JDE World menu security bypass for plant clerks",
            "control": "AC-03 Access enforcement / JDE security standard",
            "system_asset": "JD Edwards World",
            "category": "Access",
            "exception_type": "Time-boxed waiver",
            "status": "Submitted",
            "residual_risk": "Medium",
            "requestor": "Plant IT",
            "owner": "ERP Security",
            "approver": "",
            "business_justification": "World program *PUBLIC on inventory inquiry during peak season; role redesign not done.",
            "compensating_control": "Inquiry-only library list; no update programs; nightly user extract to IAM",
            "conditions": "Peak-season only. Role redesign before next season.",
            "linked_finding": "",
            "extension_count": 0,
            "requested": today - timedelta(days=2),
            "effective": pd.NaT,
            "expiration": today + timedelta(days=90),
            "next_review": today + timedelta(days=30),
        },
        {
            "exception_id": "EXC-2026-018",
            "title": "Break-glass on PCI CDE jump host without MFA",
            "control": "PCI DSS 8.3.1 / AC-07 MFA",
            "system_asset": "PCI CDE jump host",
            "category": "Access",
            "exception_type": "Time-boxed waiver",
            "status": "Approved",
            "residual_risk": "High",
            "requestor": "Card Ops",
            "owner": "PCI Compliance",
            "approver": "CISO",
            "business_justification": "Hardware token shipment delayed; one emergency ID for QSA evidence window.",
            "compensating_control": "Password in PAM; 2-person checkout; session recording; ID disabled when unused 24h",
            "conditions": "Single named ID. MFA live before QSA fieldwork. No extension without PCI Lead + CISO.",
            "linked_finding": "PCI-2026-009",
            "extension_count": 0,
            "requested": today - timedelta(days=12),
            "effective": today - timedelta(days=11),
            "expiration": today + timedelta(days=9 + jitter(-2, 3)),
            "next_review": today + timedelta(days=3),
        },
    ]

    df = pd.DataFrame(rows)
    for col in ("requested", "effective", "expiration", "next_review"):
        df[col] = pd.to_datetime(df[col], errors="coerce")
    if "review_note" not in df.columns:
        df["review_note"] = ""
    df["review_note"] = df["review_note"].fillna("")
    return df


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["days_to_expire"] = (out["expiration"] - today).dt.days
    out["review_overdue"] = (
        out["status"].eq("Approved")
        & out["next_review"].notna()
        & (out["next_review"] < today)
    )
    out["lapsed_in_prod"] = out["status"].eq("Expired") | (
        out["status"].eq("Approved") & (out["days_to_expire"] < 0)
    )
    out["expiring_30"] = out["status"].eq("Approved") & out["days_to_expire"].between(0, 30)
    return out


def _sync(seed: int) -> pd.DataFrame:
    if st.session_state.get("_exc_seed") != seed or "exceptions" not in st.session_state:
        st.session_state.exceptions = _sample_exceptions(seed)
        st.session_state._exc_seed = seed
    return st.session_state.exceptions


def _save(df: pd.DataFrame) -> None:
    st.session_state.exceptions = df.reset_index(drop=True)


def _patch(exception_id: str, **fields) -> None:
    df = st.session_state.exceptions.copy()
    loc = df.index[df["exception_id"] == exception_id]
    if len(loc) == 0:
        return
    i = loc[0]
    for k, v in fields.items():
        df.at[i, k] = v
    _save(df)


def _metrics(df: pd.DataFrame) -> dict:
    e = _enrich(df)
    active = e[e["status"] == "Approved"]
    pending = e[e["status"].isin(["Submitted", "In Review"])]
    return {
        "active": int(len(active)),
        "pending": int(len(pending)),
        "expiring": int(e["expiring_30"].sum()),
        "lapsed": int(e["lapsed_in_prod"].sum()),
        "overdue_review": int(e["review_overdue"].sum()),
        "repeat_ext": int((e["extension_count"] >= 2).sum()),
        "critical_active": int(len(active[active["residual_risk"] == "Critical"])),
    }


def _fmt(ts) -> str:
    if pd.isna(ts):
        return "—"
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def _detail(row: pd.Series) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Control waived:** {row['control']}")
        st.write(f"**Type:** {row['exception_type']}")
        st.write(f"**Status:** {row['status']} · residual **{row['residual_risk']}**")
        st.write(f"**Requestor / owner:** {row['requestor']} / {row['owner']}")
        st.write(f"**Approver:** {row['approver'] or '— (pending)'}")
        st.write(f"**Linked finding:** {row['linked_finding'] or '—'}")
    with c2:
        st.write(f"**Requested:** {_fmt(row['requested'])}")
        st.write(f"**Effective:** {_fmt(row['effective'])}")
        st.write(f"**Expires:** {_fmt(row['expiration'])} ({row['days_to_expire']}d)")
        st.write(f"**Next review:** {_fmt(row['next_review'])}")
        st.write(f"**Extensions:** {int(row['extension_count'])}")
    st.write(f"**Justification:** {row['business_justification']}")
    st.write(f"**Compensating control:** {row['compensating_control']}")
    st.write(f"**Conditions of approval:** {row['conditions']}")


def _actions(row: pd.Series, *, key: str) -> None:
    eid = row["exception_id"]
    today = _today()
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if row["status"] in {"Submitted", "In Review"} and st.button(
            "Approve 90d", key=f"appr_{key}", use_container_width=True
        ):
            _patch(
                eid,
                status="Approved",
                approver="CISO (demo)",
                effective=today,
                expiration=today + timedelta(days=90),
                next_review=today + timedelta(days=30),
            )
            st.rerun()
    with a2:
        if row["status"] in {"Submitted", "In Review"} and st.button(
            "Deny", key=f"deny_{key}", use_container_width=True
        ):
            _patch(eid, status="Denied", approver="CISO (demo)", effective=pd.NaT)
            st.rerun()
    with a3:
        if row["status"] in {"Approved", "Expired"} and st.button(
            "Extend 90d", key=f"ext_{key}", use_container_width=True
        ):
            new_exp = pd.Timestamp(row["expiration"])
            if pd.isna(new_exp) or new_exp < today:
                new_exp = today
            _patch(
                eid,
                status="Approved",
                expiration=new_exp + timedelta(days=90),
                next_review=today + timedelta(days=30),
                extension_count=int(row["extension_count"]) + 1,
                approver=row["approver"] or "CISO (demo)",
                effective=row["effective"] if pd.notna(row["effective"]) else today,
            )
            st.rerun()
    with a4:
        if row["status"] not in {"Closed", "Denied"} and st.button(
            "Close — remediated", key=f"cls_{key}", use_container_width=True
        ):
            _patch(eid, status="Closed", next_review=pd.NaT)
            st.rerun()


def main() -> None:
    portfolio_skin.page_header(
        title="Exception Tracking System",
        lede="Time-boxed control waivers: request, compensate, approve, expire. Club demo — not a system of record.",
        kicker="Control exceptions",
    )

    seed = demo_kit.seed_controls()
    df = _sync(seed)
    enriched = _enrich(df)
    m = _metrics(df)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Register filters")
    status_f = st.sidebar.multiselect("Status", STATUSES, default=STATUSES)
    risk_f = st.sidebar.multiselect("Residual risk", RISK_ORDER, default=RISK_ORDER)
    systems = sorted(df["system_asset"].astype(str).unique())
    system_f = st.sidebar.multiselect("System / asset", systems, default=systems)

    filtered = enriched[
        enriched["status"].isin(status_f)
        & enriched["residual_risk"].isin(risk_f)
        & enriched["system_asset"].isin(system_f)
    ]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Active waivers", m["active"], help="Status = Approved (clock is running).")
    k2.metric("Awaiting decision", m["pending"])
    k3.metric("Expire in 30 days", m["expiring"])
    k4.metric(
        "Lapsed still in prod",
        m["lapsed"],
        help="Expired (or past date) and not closed — this is what auditors sample.",
    )
    st.caption(
        f"Overdue periodic reviews: {m['overdue_review']} · "
        f"Repeat extensions (≥2): {m['repeat_ext']} · "
        f"Critical among active: {m['critical_active']}"
    )

    work, register, intake, aging, export = st.tabs(
        ["Workbench", "Register", "Intake", "Aging", "Export"]
    )

    with work:
        st.subheader("Needs action")
        st.caption(
            "Submitted / In Review → approve or deny. Approved → watch the clock. "
            "Expired still in production is an open risk, not a filing status."
        )

        pending = enriched[enriched["status"].isin(["Submitted", "In Review"])].sort_values(
            "requested"
        )
        expiring = enriched[enriched["expiring_30"]].sort_values("days_to_expire")
        lapsed = enriched[enriched["lapsed_in_prod"]].sort_values("days_to_expire")
        overdue = enriched[enriched["review_overdue"]].sort_values("next_review")

        st.markdown(f"**Awaiting decision ({len(pending)})**")
        if pending.empty:
            st.success("Nothing in the approval queue.")
        else:
            for _, row in pending.iterrows():
                with st.expander(
                    f"{row['exception_id']} · {row['title']} · {row['status']} · {row['residual_risk']}"
                ):
                    _detail(row)
                    _actions(row, key=f"pend_{row['exception_id']}")

        st.markdown(f"**Expiring within 30 days ({len(expiring)})**")
        if expiring.empty:
            st.info("No active waivers inside the 30-day window.")
        else:
            for _, row in expiring.iterrows():
                with st.expander(
                    f"{row['exception_id']} · {row['title']} · {int(row['days_to_expire'])}d left"
                ):
                    _detail(row)
                    _actions(row, key=f"exp_{row['exception_id']}")

        st.markdown(f"**Lapsed — still in production ({len(lapsed)})**")
        if lapsed.empty:
            st.success("No lapsed waivers hanging open.")
        else:
            st.warning("These expired without close-out. Extend (renewal) or close as remediated.")
            for _, row in lapsed.iterrows():
                with st.expander(
                    f"{row['exception_id']} · {row['title']} · expired {abs(int(row['days_to_expire']))}d ago"
                ):
                    _detail(row)
                    _actions(row, key=f"lapse_{row['exception_id']}")

        st.markdown(f"**Periodic review overdue ({len(overdue)})**")
        if overdue.empty:
            st.info("Active waivers are inside their review cadence.")
        else:
            for _, row in overdue.iterrows():
                with st.expander(
                    f"{row['exception_id']} · {row['title']} · review was {_fmt(row['next_review'])}"
                ):
                    _detail(row)
                    _actions(row, key=f"rev_{row['exception_id']}")

    with register:
        st.subheader("Exception register")
        show = filtered[
            [
                "exception_id",
                "title",
                "system_asset",
                "control",
                "status",
                "residual_risk",
                "owner",
                "approver",
                "expiration",
                "days_to_expire",
                "extension_count",
                "linked_finding",
            ]
        ].copy()
        show["expiration"] = show["expiration"].dt.strftime("%Y-%m-%d")
        st.dataframe(show, use_container_width=True, hide_index=True)

        ids = filtered["exception_id"].tolist()
        if ids:
            pick = st.selectbox("Open a record", ids)
            row = enriched[enriched["exception_id"] == pick].iloc[0]
            _detail(row)
            _actions(row, key=f"reg_{pick}")

    with intake:
        st.subheader("Request a waiver")
        st.caption("A real intake asks what control you are breaking, for how long, and what sits in front of the hole.")
        with st.form("intake"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Short title", placeholder="e.g. MFA not on plant-floor 5250")
                system_asset = st.text_input("System / asset", placeholder="e.g. IBM i (PRODBOX)")
                control = st.text_input("Control / policy waived", placeholder="e.g. AC-07 MFA / ISO A.8.5")
                category = st.selectbox(
                    "Category",
                    ["Access", "Privileged access", "Logging", "Patching", "Encryption", "Network", "Endpoint"],
                )
                exception_type = st.selectbox(
                    "Type",
                    ["Time-boxed waiver", "Risk acceptance", "Scope exclusion"],
                )
                residual_risk = st.selectbox("Residual risk", RISK_ORDER, index=1)
            with c2:
                requestor = st.text_input("Requestor (business)", placeholder="e.g. Plant IT")
                owner = st.text_input("Control owner", placeholder="e.g. IAM")
                linked_finding = st.text_input("Linked finding (optional)", placeholder="AUD-2026-014")
                expiration = st.date_input(
                    "Requested expiration",
                    value=(_today() + timedelta(days=90)).date(),
                )
                justification = st.text_area("Business justification")
                compensating = st.text_area("Compensating control")
            conditions = st.text_input(
                "Proposed conditions",
                placeholder="Named accounts only; no further extension without CISO",
            )
            submitted = st.form_submit_button("Submit to register")

        if submitted:
            if not title.strip() or not control.strip() or not compensating.strip():
                st.error("Title, control, and compensating control are required.")
            else:
                n = len(st.session_state.exceptions) + 1
                new_id = f"EXC-2026-{n:03d}"
                today = _today()
                add = {
                    "exception_id": new_id,
                    "title": title.strip(),
                    "control": control.strip(),
                    "system_asset": system_asset.strip() or "Unspecified",
                    "category": category,
                    "exception_type": exception_type,
                    "status": "Submitted",
                    "residual_risk": residual_risk,
                    "requestor": requestor.strip() or "Requestor",
                    "owner": owner.strip() or "Control owner",
                    "approver": "",
                    "business_justification": justification.strip() or "—",
                    "compensating_control": compensating.strip(),
                    "conditions": conditions.strip() or "Time-boxed. Exit criteria required before renewal.",
                    "linked_finding": linked_finding.strip(),
                    "extension_count": 0,
                    "requested": today,
                    "effective": pd.NaT,
                    "expiration": pd.Timestamp(expiration),
                    "next_review": today + timedelta(days=14),
                    "review_note": "",
                }
                _save(pd.concat([st.session_state.exceptions, pd.DataFrame([add])], ignore_index=True))
                st.success(f"{new_id} submitted. It is on the Workbench approval queue.")
                st.rerun()

    with aging:
        st.subheader("Clock and concentration")
        plot_df = filtered.copy()
        if plot_df.empty:
            st.info("No rows in the current filter.")
        else:
            plot_df["renewals"] = plot_df["extension_count"].astype(int) + 1
            fig = px.scatter(
                plot_df,
                x="days_to_expire",
                y="residual_risk",
                color="status",
                size="renewals",
                size_max=24,
                hover_name="exception_id",
                hover_data=["title", "system_asset", "owner", "extension_count"],
                color_discrete_map=STATUS_COLOR,
                category_orders={"residual_risk": RISK_ORDER, "status": STATUSES},
                title="Days to expiration vs residual risk (bubble = 1 + renewal count)",
                labels={"days_to_expire": "Days to expiration (negative = already lapsed)"},
            )
            fig.add_vline(x=0, line_dash="dash", line_color="#ff6b6b")
            fig.add_vline(x=30, line_dash="dot", line_color="#f2b84b")
            st.plotly_chart(fig, use_container_width=True)

            c1, c2 = st.columns(2)
            with c1:
                status_counts = (
                    plot_df["status"]
                    .value_counts()
                    .reindex(STATUSES)
                    .fillna(0)
                    .rename_axis("status")
                    .reset_index(name="count")
                )
                fig_s = px.bar(
                    status_counts,
                    x="status",
                    y="count",
                    color="status",
                    color_discrete_map=STATUS_COLOR,
                    title="By status",
                )
                fig_s.update_layout(showlegend=False)
                st.plotly_chart(fig_s, use_container_width=True)
            with c2:
                cat_counts = (
                    plot_df["category"].value_counts().rename_axis("category").reset_index(name="count")
                )
                fig_c = px.bar(cat_counts, x="category", y="count", title="By category")
                st.plotly_chart(fig_c, use_container_width=True)

            repeats = plot_df[plot_df["extension_count"] >= 2]
            if not repeats.empty:
                st.caption("Repeat extensions are a finding in most audit programs — they mean the exit never happened.")
                st.dataframe(
                    repeats[["exception_id", "title", "extension_count", "status", "expiration"]],
                    use_container_width=True,
                    hide_index=True,
                )

    with export:
        st.subheader("Filtered register")
        out = filtered.copy()
        for col in ("requested", "effective", "expiration", "next_review"):
            out[col] = out[col].apply(_fmt)
        demo_kit.csv_download(out.drop(columns=["review_note"], errors="ignore"), "exception_register.csv")
        st.caption("Resample in the sidebar rebuilds the demo set. Adds and approvals live in this browser session only.")


if __name__ == "__main__":
    main()
