#!/usr/bin/env python3
"""Audit PBC / evidence-trail workbench — club teaching toy.

The unit of work is not 'an audit.' It is a request that must stay tied to
a control, an owner, the evidence submitted, the auditor's response, and next.
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
    page_title="Audit Management System · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

ENGAGEMENT = {
    "id": "ENG-SOC2-FY26",
    "name": "SOC 2 Type II FY26",
    "auditor": "Deloitte · fieldwork in progress",
    "period": "2025-08-01 → 2026-07-31",
}

STATUSES = [
    "Not started",
    "With owner",
    "Submitted",
    "Auditor questions",
    "Accepted",
    "Deficiency",
]
STATUS_COLOR = {
    "Not started": "#91aa9b",
    "With owner": "#f2b84b",
    "Submitted": "#7fffb2",
    "Auditor questions": "#ffb347",
    "Accepted": "#38e881",
    "Deficiency": "#ff6b6b",
}
READINESS = ["Existing trail", "Scramble"]


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _sample(seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    today = _today()
    rng = np.random.default_rng(seed)

    def j(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    requests = [
        {
            "request_id": "PBC-2026-001",
            "control": "CC6.2 / AC-02 Privileged access review",
            "title": "Privileged access operated during the review period",
            "auditor_ask": "Please provide evidence that privileged access was reviewed during the review period, including population completeness.",
            "owner": "IAM",
            "system_of_record": "GRC register + AD / Citrix",
            "period_from": pd.Timestamp("2026-02-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Auditor questions",
            "readiness": "Scramble",
            "due": today + timedelta(days=3 + j(-1, 2)),
            "issued": today - timedelta(days=18),
            "auditor_response": "v1 covered Q2 only and omitted the Citrix VDI cohort. Population is incomplete.",
            "next_action": "Attach Citrix campaign pack or EXC-2026-002 close-out; resubmit full-period extract.",
        },
        {
            "request_id": "PBC-2026-002",
            "control": "CC6.1 / AC-07 MFA",
            "title": "MFA enforced on remote and admin access",
            "auditor_ask": "Provide evidence MFA operated for remote access and privileged consoles during the period.",
            "owner": "IAM / SecOps",
            "system_of_record": "IdP + exception register",
            "period_from": pd.Timestamp("2025-08-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Accepted",
            "readiness": "Existing trail",
            "due": today - timedelta(days=6),
            "issued": today - timedelta(days=22),
            "auditor_response": "Accepted. IBM i 5250 gap is covered by approved waiver EXC-2026-001 with compensating QAUDJRN monitoring.",
            "next_action": "None — trail already existed (control test CT-2026-009 + waiver).",
        },
        {
            "request_id": "PBC-2026-003",
            "control": "CC7.2 / MON-02 Logging",
            "title": "Security logging coverage for in-scope systems",
            "auditor_ask": "Provide evidence in-scope hosts forwarded auth and privileged activity logs to the SIEM during the period.",
            "owner": "SecOps",
            "system_of_record": "SIEM source list vs asset inventory",
            "period_from": pd.Timestamp("2026-05-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Deficiency",
            "readiness": "Scramble",
            "due": today - timedelta(days=2 + j(0, 3)),
            "issued": today - timedelta(days=16),
            "auditor_response": "Control test CT-2026-006 failed: 6 DMZ jump hosts not forwarding. Evidence does not support operating effectiveness.",
            "next_action": "Corrective onboarding + re-test. Finding will land unless coverage is evidenced before exit.",
        },
        {
            "request_id": "PBC-2026-004",
            "control": "CC6.1 / BC-05 Backup restore",
            "title": "Restore test within the review period",
            "auditor_ask": "Provide evidence a production-relevant restore was tested and met RTO during the period.",
            "owner": "Infrastructure",
            "system_of_record": "GRC evidence library / BC-05",
            "period_from": pd.Timestamp("2025-08-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Accepted",
            "readiness": "Existing trail",
            "due": today - timedelta(days=10),
            "issued": today - timedelta(days=20),
            "auditor_response": "Accepted. Drill pack from 2026-06-04 already in GRC — retrieved, not created.",
            "next_action": "None.",
        },
        {
            "request_id": "PBC-2026-005",
            "control": "CC6.2 / RACF standard",
            "title": "RACF SPECIAL / OPERATIONS recertification",
            "auditor_ask": "Provide the period recertification of RACF SPECIAL and OPERATIONS, including contractor TSO IDs.",
            "owner": "Mainframe Security",
            "system_of_record": "RACF / SMF extracts — owner knows the library",
            "period_from": pd.Timestamp("2026-05-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Not started",
            "readiness": "Scramble",
            "due": today - timedelta(days=4 + j(0, 3)),
            "issued": today - timedelta(days=14),
            "auditor_response": "",
            "next_action": "Start the extract. EXC-2026-012 (contractor SPECIAL) lapsed — do not recertify as-is.",
        },
        {
            "request_id": "PBC-2026-006",
            "control": "CC6.1 / SAP access standard",
            "title": "SAP Firefighter / SAP_ALL usage in the period",
            "auditor_ask": "Provide Firefighter (or equivalent) logs and dual-control evidence for emergency SU01 / SAP_ALL use.",
            "owner": "ERP Security",
            "system_of_record": "SAP ST01 / GRC Firefighter",
            "period_from": pd.Timestamp("2026-02-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Submitted",
            "readiness": "Existing trail",
            "due": today + timedelta(days=5 + j(-1, 2)),
            "issued": today - timedelta(days=12),
            "auditor_response": "",
            "next_action": "Awaiting auditor. Waiver EXC-2026-013 still In Review — disclose if asked.",
        },
        {
            "request_id": "PBC-2026-007",
            "control": "CC8.1 / CM-03 Change control",
            "title": "Production change sample with CAB evidence",
            "auditor_ask": "For a sample of production changes in the period, provide approval, backout, and post-implementation notes.",
            "owner": "IT Operations",
            "system_of_record": "ServiceNow CHG",
            "period_from": pd.Timestamp("2026-05-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Accepted",
            "readiness": "Existing trail",
            "due": today - timedelta(days=8),
            "issued": today - timedelta(days=19),
            "auditor_response": "Accepted. 40-change sample already tested in CT-2026-003.",
            "next_action": "None.",
        },
        {
            "request_id": "PBC-2026-008",
            "control": "CC9.2 / TPRM",
            "title": "Tier-1 vendor SOC reports on file",
            "auditor_ask": "Provide current SOC reports (or bridge letters) for Tier-1 vendors in the CUEC population.",
            "owner": "TPRM",
            "system_of_record": "TPRM repository",
            "period_from": pd.Timestamp("2025-08-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Auditor questions",
            "readiness": "Scramble",
            "due": today + timedelta(days=2 + j(-1, 2)),
            "issued": today - timedelta(days=11),
            "auditor_response": "Payroll SaaS bridge letter expired last month. Report does not cover the full period.",
            "next_action": "Obtain updated SOC / bridge or document as CUEC gap.",
        },
        {
            "request_id": "PBC-2026-009",
            "control": "CC1.4 / AT-01 Awareness",
            "title": "Security awareness completion for the period",
            "auditor_ask": "Provide completion evidence for the annual campaign and contractor coverage.",
            "owner": "People Ops",
            "system_of_record": "LMS",
            "period_from": pd.Timestamp("2026-01-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Submitted",
            "readiness": "Existing trail",
            "due": today + timedelta(days=8 + j(-2, 3)),
            "issued": today - timedelta(days=9),
            "auditor_response": "",
            "next_action": "Campaign still closing (~88%). Expect a follow-up on contractor cohorts.",
        },
        {
            "request_id": "PBC-2026-010",
            "control": "CC6.1 / IBM i Security Standard",
            "title": "*ALLOBJ and QSECOFR day-use in the period",
            "auditor_ask": "Provide DSPUSRPRF (or equivalent) of special authorities on production LPARs for the period.",
            "owner": "IBM i Ops",
            "system_of_record": "IBM i PRODBOX / QAUDJRN",
            "period_from": pd.Timestamp("2026-05-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Submitted",
            "readiness": "Existing trail",
            "due": today + timedelta(days=6 + j(-1, 2)),
            "issued": today - timedelta(days=10),
            "auditor_response": "",
            "next_action": "Extract is in. Waiver EXC-2026-011 must travel with it or this becomes a finding.",
        },
        {
            "request_id": "PBC-2026-011",
            "control": "CC7.3 / IR-01 Incident response",
            "title": "IR plan tested during the period",
            "auditor_ask": "Provide evidence the incident response plan was exercised in the review period.",
            "owner": "SecOps",
            "system_of_record": "GRC / IR-01 evidence folder",
            "period_from": pd.Timestamp("2025-08-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Accepted",
            "readiness": "Existing trail",
            "due": today - timedelta(days=12),
            "issued": today - timedelta(days=21),
            "auditor_response": "Accepted. Tabletop 2026-07-09 pack was already filed.",
            "next_action": "None.",
        },
        {
            "request_id": "PBC-2026-012",
            "control": "CC6.1 / CR-01 Encryption",
            "title": "Encryption at rest for confidential stores",
            "auditor_ask": "Provide evidence confidential / restricted storage is encrypted at rest for the period.",
            "owner": "Security Engineering",
            "system_of_record": "CSPM",
            "period_from": pd.Timestamp("2026-05-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "Auditor questions",
            "readiness": "Scramble",
            "due": today + timedelta(days=4 + j(-1, 2)),
            "issued": today - timedelta(days=8),
            "auditor_response": "Screenshot of one bucket is not a population. Does not show the control operated across in-scope stores.",
            "next_action": "CSPM query for the period + exception list. One screenshot is not the control.",
        },
        {
            "request_id": "PBC-2026-013",
            "control": "CC6.1 / IA-05 Authenticators",
            "title": "Authenticator standard operating in the period",
            "auditor_ask": "Provide evidence the authenticator / password standard was in force (not merely published).",
            "owner": "IAM",
            "system_of_record": "IdP policy export + AD",
            "period_from": pd.Timestamp("2026-02-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "With owner",
            "readiness": "Scramble",
            "due": today + timedelta(days=7 + j(-2, 3)),
            "issued": today - timedelta(days=7),
            "auditor_response": "v1 was last year's standard PDF. A policy is not operating evidence.",
            "next_action": "Export live IdP / AD password policy as of period dates. Do not resubmit the PDF.",
        },
        {
            "request_id": "PBC-2026-014",
            "control": "PCI 8.3.1 / AC-07",
            "title": "MFA on PCI CDE jump hosts",
            "auditor_ask": "Provide evidence MFA operated on CDE administrative access during the period.",
            "owner": "PCI Lead",
            "system_of_record": "PAM + exception register",
            "period_from": pd.Timestamp("2026-05-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "status": "With owner",
            "readiness": "Existing trail",
            "due": today + timedelta(days=9 + j(-2, 3)),
            "issued": today - timedelta(days=5),
            "auditor_response": "",
            "next_action": "Disclose EXC-2026-018 (break-glass without MFA) with PAM checkout logs. Do not imply 100% coverage.",
        },
    ]

    artifacts = [
        {
            "artifact_id": "EVD-2026-001",
            "request_id": "PBC-2026-001",
            "version": 1,
            "name": "Q2 privileged recert export",
            "source": "GRC-REC-318",
            "period_from": pd.Timestamp("2026-04-01"),
            "period_to": pd.Timestamp("2026-06-30"),
            "submitted": today - timedelta(days=9),
            "submitted_by": "IAM",
            "disposition": "Wrong period",
            "note": "Q2 only. Citrix VDI not in population.",
        },
        {
            "artifact_id": "EVD-2026-002",
            "request_id": "PBC-2026-001",
            "version": 2,
            "name": "Feb–Jul extract (still missing Citrix)",
            "source": "GRC-REC-331",
            "period_from": pd.Timestamp("2026-02-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "submitted": today - timedelta(days=2),
            "submitted_by": "IAM",
            "disposition": "Insufficient",
            "note": "Period fixed. Population still incomplete.",
        },
        {
            "artifact_id": "EVD-2026-003",
            "request_id": "PBC-2026-002",
            "version": 1,
            "name": "IdP MFA enforcement report + EXC-2026-001",
            "source": "CT-2026-009 / exception register",
            "period_from": pd.Timestamp("2025-08-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "submitted": today - timedelta(days=21),
            "submitted_by": "IAM",
            "disposition": "Sufficient",
            "note": "Already in GRC from the quarterly test. Waiver attached.",
        },
        {
            "artifact_id": "EVD-2026-004",
            "request_id": "PBC-2026-003",
            "version": 1,
            "name": "SIEM source list (current)",
            "source": "SIEM admin",
            "period_from": pd.Timestamp("2026-07-22"),
            "period_to": pd.Timestamp("2026-07-22"),
            "submitted": today - timedelta(days=8),
            "submitted_by": "SecOps",
            "disposition": "Insufficient",
            "note": "Point-in-time list, not period coverage. Failed test already on file.",
        },
        {
            "artifact_id": "EVD-2026-005",
            "request_id": "PBC-2026-004",
            "version": 1,
            "name": "ERP restore drill pack",
            "source": "GRC/Evidence/BC-05/2026-Q2",
            "period_from": pd.Timestamp("2026-06-04"),
            "period_to": pd.Timestamp("2026-06-04"),
            "submitted": today - timedelta(days=19),
            "submitted_by": "Infrastructure",
            "disposition": "Sufficient",
            "note": "Filed when the drill ran. Retrieved for the PBC.",
        },
        {
            "artifact_id": "EVD-2026-006",
            "request_id": "PBC-2026-006",
            "version": 1,
            "name": "Firefighter / ST01 extract Feb–Jul",
            "source": "SAP GRC",
            "period_from": pd.Timestamp("2026-02-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "submitted": today - timedelta(days=3),
            "submitted_by": "ERP Security",
            "disposition": "Pending",
            "note": "Includes dual-control tickets. SAP_ALL waiver still open.",
        },
        {
            "artifact_id": "EVD-2026-007",
            "request_id": "PBC-2026-007",
            "version": 1,
            "name": "40-change CAB sample",
            "source": "CT-2026-003 / ServiceNow",
            "period_from": pd.Timestamp("2026-05-01"),
            "period_to": pd.Timestamp("2026-06-30"),
            "submitted": today - timedelta(days=18),
            "submitted_by": "IT Operations",
            "disposition": "Sufficient",
            "note": "Same pack used for the control test.",
        },
        {
            "artifact_id": "EVD-2026-008",
            "request_id": "PBC-2026-008",
            "version": 1,
            "name": "Tier-1 SOC zip (incl. expired payroll bridge)",
            "source": "TPRM-T1-26",
            "period_from": pd.Timestamp("2025-08-01"),
            "period_to": pd.Timestamp("2026-06-15"),
            "submitted": today - timedelta(days=6),
            "submitted_by": "TPRM",
            "disposition": "Wrong period",
            "note": "Payroll SaaS coverage ended before period end.",
        },
        {
            "artifact_id": "EVD-2026-009",
            "request_id": "PBC-2026-009",
            "version": 1,
            "name": "LMS completion export",
            "source": "AWR-2026",
            "period_from": pd.Timestamp("2026-01-01"),
            "period_to": pd.Timestamp("2026-08-01"),
            "submitted": today - timedelta(days=4),
            "submitted_by": "People Ops",
            "disposition": "Pending",
            "note": "88% complete; contractors flagged.",
        },
        {
            "artifact_id": "EVD-2026-010",
            "request_id": "PBC-2026-010",
            "version": 1,
            "name": "DSPUSRPRF special authorities + EXC-2026-011",
            "source": "IBMi-Q3-REV",
            "period_from": pd.Timestamp("2026-05-01"),
            "period_to": pd.Timestamp("2026-07-31"),
            "submitted": today - timedelta(days=1),
            "submitted_by": "IBM i Ops",
            "disposition": "Pending",
            "note": "Waiver must stay attached.",
        },
        {
            "artifact_id": "EVD-2026-011",
            "request_id": "PBC-2026-011",
            "version": 1,
            "name": "Ransomware tabletop after-action",
            "source": "GRC/Evidence/IR-01/2026-Q3",
            "period_from": pd.Timestamp("2026-07-09"),
            "period_to": pd.Timestamp("2026-07-09"),
            "submitted": today - timedelta(days=20),
            "submitted_by": "SecOps",
            "disposition": "Sufficient",
            "note": "Already on the evidence shelf.",
        },
        {
            "artifact_id": "EVD-2026-012",
            "request_id": "PBC-2026-012",
            "version": 1,
            "name": "Screenshot — one confidential bucket",
            "source": "Console screenshot",
            "period_from": pd.Timestamp("2026-08-12"),
            "period_to": pd.Timestamp("2026-08-12"),
            "submitted": today - timedelta(days=5),
            "submitted_by": "Security Engineering",
            "disposition": "Insufficient",
            "note": "Does not support the control. Not a population, not the period.",
        },
        {
            "artifact_id": "EVD-2026-013",
            "request_id": "PBC-2026-013",
            "version": 1,
            "name": "Authenticator Standard v4.0 PDF",
            "source": "Policy library STD-2026-006",
            "period_from": pd.Timestamp("2026-04-01"),
            "period_to": pd.Timestamp("2026-04-01"),
            "submitted": today - timedelta(days=6),
            "submitted_by": "IAM",
            "disposition": "Duplicate",
            "note": "Publishing a standard is not evidence it operated. Auditor sent it back.",
        },
        {
            "artifact_id": "EVD-2026-014",
            "request_id": "PBC-2026-014",
            "version": 1,
            "name": "PAM checkout log + EXC-2026-018",
            "source": "PAM / exception register",
            "period_from": pd.Timestamp("2026-07-01"),
            "period_to": pd.Timestamp("2026-08-17"),
            "submitted": pd.NaT,
            "submitted_by": "PCI Lead",
            "disposition": "Pending",
            "note": "Staged, not yet sent. Period starts late vs request.",
        },
    ]

    req = pd.DataFrame(requests)
    art = pd.DataFrame(artifacts)
    for col in ("period_from", "period_to", "due", "issued"):
        req[col] = pd.to_datetime(req[col], errors="coerce")
    for col in ("period_from", "period_to", "submitted"):
        art[col] = pd.to_datetime(art[col], errors="coerce")
    return req, art


def _enrich(req: pd.DataFrame, art: pd.DataFrame) -> pd.DataFrame:
    out = req.copy()
    today = _today()
    out["days_to_due"] = (out["due"] - today).dt.days
    open_row = ~out["status"].isin(["Accepted", "Deficiency"])
    out["is_overdue"] = open_row & (out["days_to_due"] < 0)
    counts = art.groupby("request_id").size().rename("artifact_count")
    versions = art.groupby("request_id")["version"].max().rename("latest_version")
    out = out.merge(counts, left_on="request_id", right_index=True, how="left")
    out = out.merge(versions, left_on="request_id", right_index=True, how="left")
    out["artifact_count"] = out["artifact_count"].fillna(0).astype(int)
    out["latest_version"] = out["latest_version"].fillna(0).astype(int)
    return out


def _sync(seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    if st.session_state.get("_audit_seed") != seed or "pbc" not in st.session_state:
        req, art = _sample(seed)
        st.session_state.pbc = req
        st.session_state.artifacts = art
        st.session_state._audit_seed = seed
    return st.session_state.pbc, st.session_state.artifacts


def _save_req(df: pd.DataFrame) -> None:
    st.session_state.pbc = df.reset_index(drop=True)


def _save_art(df: pd.DataFrame) -> None:
    st.session_state.artifacts = df.reset_index(drop=True)


def _patch_req(request_id: str, **fields) -> None:
    df = st.session_state.pbc.copy()
    loc = df.index[df["request_id"] == request_id]
    if len(loc) == 0:
        return
    i = loc[0]
    for k, v in fields.items():
        df.at[i, k] = v
    _save_req(df)


def _metrics(req: pd.DataFrame, art: pd.DataFrame) -> dict:
    e = _enrich(req, art)
    open_n = int((~e["status"].isin(["Accepted", "Deficiency"])).sum())
    existing = int((e["readiness"] == "Existing trail").sum())
    scramble = int((e["readiness"] == "Scramble").sum())
    return {
        "open": open_n,
        "overdue": int(e["is_overdue"].sum()),
        "questions": int((e["status"] == "Auditor questions").sum()),
        "accepted": int((e["status"] == "Accepted").sum()),
        "existing": existing,
        "scramble": scramble,
        "resubmits": int((e["latest_version"] >= 2).sum()),
    }


def _fmt(ts) -> str:
    if pd.isna(ts):
        return "—"
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def _trail(row: pd.Series, art: pd.DataFrame) -> None:
    st.markdown(f"### {row['request_id']} · {row['title']}")
    st.caption(f"{ENGAGEMENT['name']} · review period {ENGAGEMENT['period']}")
    st.write(f"**Auditor asked:** {row['auditor_ask']}")

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Control:** {row['control']}")
        st.write(f"**Owner:** {row['owner']}")
        st.write(f"**System of record:** {row['system_of_record']}")
        st.write(f"**Readiness:** {row['readiness']}")
    with c2:
        st.write(f"**Period requested:** {_fmt(row['period_from'])} → {_fmt(row['period_to'])}")
        st.write(f"**Status:** {row['status']}")
        st.write(f"**Due:** {_fmt(row['due'])} ({int(row['days_to_due'])}d)")
        st.write(f"**Issued:** {_fmt(row['issued'])} · artifacts: {int(row['artifact_count'])} · v{int(row['latest_version'])}")

    linked = art[art["request_id"] == row["request_id"]].sort_values("version")
    st.markdown("**Evidence submitted**")
    if linked.empty:
        st.warning("Nothing on the trail yet. That is the archaeological expedition.")
    else:
        show = linked.copy()
        show["period"] = show["period_from"].apply(_fmt) + " → " + show["period_to"].apply(_fmt)
        show["submitted"] = show["submitted"].apply(_fmt)
        st.dataframe(
            show[
                [
                    "artifact_id",
                    "version",
                    "name",
                    "source",
                    "period",
                    "submitted",
                    "submitted_by",
                    "disposition",
                    "note",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
        bad = linked[linked["disposition"].isin(["Insufficient", "Wrong period", "Duplicate"])]
        if not bad.empty:
            st.caption(
                "Insufficient / wrong period / duplicate means the artifact did not support the control "
                "for the period asked — not that a file failed to attach."
            )

    st.markdown("**Auditor response**")
    st.write(row["auditor_response"] or "— (none yet)")
    st.markdown("**Next**")
    st.write(row["next_action"] or "—")


def _actions(row: pd.Series, *, key: str) -> None:
    rid = row["request_id"]
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if row["status"] == "Not started" and st.button(
            "Send to owner", key=f"own_{key}", use_container_width=True
        ):
            _patch_req(rid, status="With owner")
            st.rerun()
    with a2:
        if row["status"] in {"Not started", "With owner", "Auditor questions"} and st.button(
            "Submit to auditor", key=f"sub_{key}", use_container_width=True
        ):
            _patch_req(rid, status="Submitted")
            st.rerun()
    with a3:
        if row["status"] in {"Submitted", "Auditor questions"} and st.button(
            "Mark accepted", key=f"ok_{key}", use_container_width=True
        ):
            _patch_req(
                rid,
                status="Accepted",
                auditor_response=row["auditor_response"] or "Accepted (demo).",
                next_action="None.",
            )
            st.rerun()
    with a4:
        if row["status"] not in {"Accepted", "Deficiency"} and st.button(
            "Flag questions", key=f"q_{key}", use_container_width=True
        ):
            _patch_req(
                rid,
                status="Auditor questions",
                auditor_response=row["auditor_response"]
                or "Follow-up: period, population, or support for the control is unclear.",
            )
            st.rerun()


def _queue(title: str, subset: pd.DataFrame, art: pd.DataFrame, empty: str, key_prefix: str) -> None:
    st.markdown(f"**{title} ({len(subset)})**")
    if subset.empty:
        st.info(empty)
        return
    for _, row in subset.iterrows():
        due = f"{int(row['days_to_due'])}d" if row["days_to_due"] >= 0 else f"{abs(int(row['days_to_due']))}d overdue"
        with st.expander(
            f"{row['request_id']} · {row['title']} · {row['status']} · {due} · {row['readiness']}"
        ):
            _trail(row, art)
            _actions(row, key=f"{key_prefix}_{row['request_id']}")


def main() -> None:
    portfolio_skin.page_header(
        title="Audit Management System",
        lede="A request is a sentence. The work is the trail: control, owner, evidence, period, auditor response, next. Club demo — not a system of record.",
        kicker="Audit readiness",
    )

    seed = demo_kit.seed_controls()
    req, art = _sync(seed)
    enriched = _enrich(req, art)
    m = _metrics(req, art)

    st.sidebar.markdown("---")
    st.sidebar.caption(f"{ENGAGEMENT['name']}")
    st.sidebar.caption(ENGAGEMENT["auditor"])
    st.sidebar.caption(f"Period {ENGAGEMENT['period']}")
    st.sidebar.subheader("Filters")
    status_f = st.sidebar.multiselect("Status", STATUSES, default=STATUSES)
    ready_f = st.sidebar.multiselect("Readiness", READINESS, default=READINESS)
    owners = sorted(req["owner"].astype(str).unique())
    owner_f = st.sidebar.multiselect("Owner", owners, default=owners)

    filtered = enriched[
        enriched["status"].isin(status_f)
        & enriched["readiness"].isin(ready_f)
        & enriched["owner"].isin(owner_f)
    ]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Open requests", m["open"])
    k2.metric("Overdue", m["overdue"])
    k3.metric("Auditor questions", m["questions"])
    k4.metric("Accepted", m["accepted"])
    st.caption(
        f"Existing trail: {m['existing']} · Scramble after the request: {m['scramble']} · "
        f"Resubmits (v2+): {m['resubmits']}"
    )

    work, trail, register, intake, export = st.tabs(
        ["Workbench", "Request trail", "Register", "Intake", "Export"]
    )

    with work:
        st.subheader("What still needs a human")
        st.caption(
            "Audit readiness is whether the trail already existed. "
            "Overdue and 'auditor questions' are where scramble shows."
        )
        overdue = enriched[enriched["is_overdue"]].sort_values("days_to_due")
        questions = enriched[enriched["status"].eq("Auditor questions")].sort_values("due")
        with_owner = enriched[enriched["status"].isin(["Not started", "With owner"])].sort_values("due")
        sitting = enriched[enriched["status"].eq("Submitted")].sort_values("due")

        _queue("Overdue", overdue, art, "Nothing past due.", "od")
        _queue(
            "Auditor questions — evidence did not support the ask",
            questions,
            art,
            "No open follow-ups.",
            "q",
        )
        _queue("Not submitted (not started / with owner)", with_owner, art, "Owners have sent their packs.", "own")
        _queue("Submitted — waiting on the auditor", sitting, art, "Nothing in the auditor's inbox.", "sit")

    with trail:
        st.subheader("Reconstruct one request")
        st.caption(
            "If another person cannot follow this without the employee who remembers where the file lives, "
            "you do not have a trail — you have folklore."
        )
        ids = filtered["request_id"].tolist()
        if not ids:
            st.info("Nothing in the current filter.")
        else:
            pick = st.selectbox("Request", ids)
            row = enriched[enriched["request_id"] == pick].iloc[0]
            _trail(row, art)
            _actions(row, key=f"trail_{pick}")

            with st.expander("Attach another artifact version"):
                with st.form(f"art_{pick}"):
                    name = st.text_input("Artifact name", placeholder="e.g. Citrix recert extract v3")
                    source = st.text_input("Source system / ticket")
                    c1, c2 = st.columns(2)
                    with c1:
                        p_from = st.date_input("Period from", value=row["period_from"].date())
                    with c2:
                        p_to = st.date_input("Period to", value=row["period_to"].date())
                    note = st.text_input("Note")
                    if st.form_submit_button("Add to trail"):
                        if not name.strip():
                            st.error("Name is required.")
                        else:
                            n = len(st.session_state.artifacts) + 1
                            ver = int(row["latest_version"]) + 1
                            add = {
                                "artifact_id": f"EVD-2026-{n:03d}",
                                "request_id": pick,
                                "version": ver,
                                "name": name.strip(),
                                "source": source.strip() or "—",
                                "period_from": pd.Timestamp(p_from),
                                "period_to": pd.Timestamp(p_to),
                                "submitted": _today(),
                                "submitted_by": "Demo user",
                                "disposition": "Pending",
                                "note": note.strip(),
                            }
                            _save_art(
                                pd.concat(
                                    [st.session_state.artifacts, pd.DataFrame([add])],
                                    ignore_index=True,
                                )
                            )
                            _patch_req(pick, status="Submitted")
                            st.rerun()

    with register:
        st.subheader("PBC register")
        show = filtered[
            [
                "request_id",
                "title",
                "control",
                "owner",
                "status",
                "readiness",
                "due",
                "days_to_due",
                "artifact_count",
                "latest_version",
            ]
        ].copy()
        show["due"] = show["due"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

        fig = px.scatter(
            filtered,
            x="days_to_due",
            y="readiness",
            color="status",
            hover_name="request_id",
            hover_data=["title", "owner", "control"],
            color_discrete_map=STATUS_COLOR,
            category_orders={"status": STATUSES, "readiness": READINESS},
            title="Days to due vs whether the trail already existed",
        )
        fig.add_vline(x=0, line_dash="dash", line_color="#ff6b6b")
        st.plotly_chart(fig, use_container_width=True)

    with intake:
        st.subheader("Log a request")
        st.caption("Capture the sentence, the control, the owner, and the period — before anyone hunts for a file.")
        with st.form("intake"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Short title", placeholder="e.g. Quarterly access recert evidence")
                control = st.text_input("Control", placeholder="e.g. CC6.2 / AC-02")
                owner = st.text_input("Owner", placeholder="e.g. IAM")
                system_of_record = st.text_input("System of record", placeholder="e.g. GRC + AD")
            with c2:
                due = st.date_input("Due", value=(_today() + timedelta(days=14)).date())
                p_from = st.date_input("Period from", value=pd.Timestamp("2026-02-01").date())
                p_to = st.date_input("Period to", value=pd.Timestamp("2026-07-31").date())
                readiness = st.selectbox("Readiness (honest)", READINESS, index=1)
            auditor_ask = st.text_area(
                "Auditor request",
                placeholder="Please provide evidence that this control operated during the review period.",
            )
            if st.form_submit_button("Add request"):
                if not title.strip() or not control.strip() or not owner.strip() or not auditor_ask.strip():
                    st.error("Title, control, owner, and the auditor's sentence are required.")
                else:
                    n = len(st.session_state.pbc) + 1
                    add = {
                        "request_id": f"PBC-2026-{n:03d}",
                        "control": control.strip(),
                        "title": title.strip(),
                        "auditor_ask": auditor_ask.strip(),
                        "owner": owner.strip(),
                        "system_of_record": system_of_record.strip() or "TBD",
                        "period_from": pd.Timestamp(p_from),
                        "period_to": pd.Timestamp(p_to),
                        "status": "Not started",
                        "readiness": readiness,
                        "due": pd.Timestamp(due),
                        "issued": _today(),
                        "auditor_response": "",
                        "next_action": "Identify the system of record and whether a pack already exists.",
                    }
                    _save_req(pd.concat([st.session_state.pbc, pd.DataFrame([add])], ignore_index=True))
                    st.success(f"PBC-2026-{n:03d} is on the workbench.")
                    st.rerun()

    with export:
        st.subheader("Requests and artifacts")
        out_r = filtered.copy()
        for col in ("period_from", "period_to", "due", "issued"):
            out_r[col] = out_r[col].apply(_fmt)
        demo_kit.csv_download(out_r, "pbc_requests.csv", label="Download requests")
        out_a = art[art["request_id"].isin(filtered["request_id"])].copy()
        for col in ("period_from", "period_to", "submitted"):
            out_a[col] = out_a[col].apply(_fmt)
        demo_kit.csv_download(out_a, "pbc_artifacts.csv", label="Download artifacts", key="art_csv")
        st.caption("Resample rebuilds the demo set. Edits live in this browser session only.")


if __name__ == "__main__":
    main()
