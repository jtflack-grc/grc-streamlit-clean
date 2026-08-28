#!/usr/bin/env python3
"""Security awareness *campaign* manager — club teaching toy.

Campaign ops realm (not SAT/people-risk): briefs, multi-channel waves,
content calendar, asset library, approvals, delivery & engagement KPIs —
the way program teams run Cybersecurity Awareness Month, themed pushes,
and manager toolkits. Distinct from the Training Tracker. Synthetic only.
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
    page_title="Security Awareness Campaign Manager · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

CAMPAIGN_TYPES = [
    "Themed month (e.g. Cybersecurity Awareness)",
    "Incident-driven reactive",
    "Role / department push",
    "New-hire onboarding comms",
    "Executive / board narrative",
    "Vendor / third-party outreach",
    "Product launch (internal tool)",
    "Compliance deadline comms",
]
CHANNELS = [
    "Email newsletter",
    "Intranet / SharePoint",
    "Teams / Slack",
    "Digital signage",
    "Poster / print",
    "Manager toolkit",
    "Town hall / live event",
    "Table topic / huddle",
    "Screensaver / lock screen",
    "Payroll insert / HR comms",
]
PHASES = ["Brief", "Build", "Approve", "Teaser", "Launch", "Sustain", "Close", "Retro"]
WAVE_STATUS = ["Planned", "Scheduled", "Live", "Delivered", "Skipped", "Blocked"]
ASSET_TYPES = ["Email template", "Poster", "Intranet page", "Slide deck", "Manager script", "Video short", "FAQ", "Quiz embed"]
APPROVAL = ["Draft", "In review", "Approved", "Changes requested", "Retired"]
FEATURED = {"CMP-2026-001", "CMP-2026-003", "CMP-2026-005"}
_SYNC_KEY = "_camp_seed_v2"


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _sample(seed: int):
    today = _today()
    rng = np.random.default_rng(seed)

    # ── Campaigns (program containers) ───────────────────────────────
    campaigns = [
        {
            "campaign_id": "CMP-2026-001",
            "name": "Q4 report-first reinforcement — post-INC board commit",
            "type": "Themed month (e.g. Cybersecurity Awareness)",
            "theme": "Stop forwarding suspicious mail to helpdesk — use PAB / security@ before you click",
            "objective": "Board commit after INC-2026-001/005/009 cluster: PAB reports +22% vs 12-wk SOC baseline; helpdesk 'is this phishing?' misroutes −40%; manager attestation 100% in Finance/IT/Ops; zero IR interviews citing 'didn't know how to report'",
            "audience_segment": "All workforce (~1,820) — overweight IBM i/colo shifts, Marketing, Customer Support (lagging reporters per SOC)",
            "owner": "Awareness · L. Torres + SOC liaison",
            "sponsor": "CISO (board deck 2026-09-12)",
            "budget_usd": 8400,
            "phase": "Sustain",
            "status": "Live — week 3 of 4",
            "start": today - timedelta(days=18),
            "end": today + timedelta(days=12),
            "success_metrics": "PAB reports/wk +22% vs baseline · helpdesk misroute tickets −40% · manager attestation ≥95% (currently 78%) · colo/NOC poster install 8/8 · NOT vanity completion %",
            "risks": "Message collision with CMP-2026-002 PayrollCo IR comms — Legal owns single HR/payroll wording. IBM i ops low email read-rate — need shift huddles not another blast. Marketing wants mascot October content — explicitly descoped.",
            "linked_program": "INC-2026-001 (portal stuffing) · INC-2026-005 (IFS) · INC-2026-009 · PHISH-2026-003 runs parallel in Training Tracker · KRI-2026-010",
            "summary": "Not a generic Cybersecurity Awareness Month poster program. This campaign exists because the board asked what we changed after three Sev1/2 incidents — and IR found users forwarding phish to helpdesk instead of reporting. Comms waves are incident-shaped: portal lesson week, colo shift huddles, redacted real samples, manager accountability by dept.",
        },
        {
            "campaign_id": "CMP-2026-002",
            "name": "Payroll / benefits scam alert (IR-adjacent)",
            "type": "Incident-driven reactive",
            "theme": "HR and payroll themes are bait right now",
            "objective": "48h reach to 100% on email+Teams; intranet FAQ live; no duplicate conflicting HR messages",
            "audience_segment": "All workforce — boost Finance & HR",
            "owner": "Awareness + HR Comms",
            "sponsor": "CISO + CHRO",
            "budget_usd": 0,
            "phase": "Launch",
            "status": "Live — expedited",
            "start": today - timedelta(days=3),
            "end": today + timedelta(days=11),
            "success_metrics": "Email open ≥70% · FAQ page views ≥40% · helpdesk ticket deflection on 'is this email real'",
            "risks": "Message drift vs actual PayrollCo INC-2026-009 facts — Legal review gate",
            "linked_program": "INC-2026-009 · Privacy PB-2026-002",
            "summary": "Reactive campaign playbook. Speed + single source of truth beats another generic phishing poster.",
        },
        {
            "campaign_id": "CMP-2026-003",
            "name": "Finance & payment authority — wire fraud prevention",
            "type": "Role / department push",
            "theme": "Dual-channel verification — no exceptions",
            "objective": "Every payment authority completes manager toolkit; poster in AP pods; exec assistant script distributed",
            "audience_segment": "Finance / payment authority (~86)",
            "owner": "Finance control + Awareness",
            "sponsor": "CFO",
            "budget_usd": 3500,
            "phase": "Launch",
            "status": "Live",
            "start": today - timedelta(days=10),
            "end": today + timedelta(days=50),
            "success_metrics": "Toolkit delivery confirmed 100% · tabletop attendance ≥90% · campaign recall survey ≥75%",
            "risks": "Overlaps BEC sim in Training Tracker — align dates so comms precede sim 48h",
            "linked_program": "CMP cohort finance · PHISH-2026-002 (tracker)",
            "summary": "Role campaign with manager enablement. Featured because campaign ops = toolkits + waves, not LMS rows.",
        },
        {
            "campaign_id": "CMP-2026-004",
            "name": "Privileged / vendor admin — no shared IDs",
            "type": "Vendor / third-party outreach",
            "theme": "Named accounts, PAM, and reporting suspicious admin email",
            "objective": "Orbit AMS named-ID attestation campaign; jump-host poster at colo; TPRM sends vendor pack",
            "audience_segment": "Privileged internal + Orbit AMS admins (~64)",
            "owner": "TPRM + SecOps comms",
            "sponsor": "CISO",
            "budget_usd": 1800,
            "phase": "Build",
            "status": "Scheduled",
            "start": today + timedelta(days=7),
            "end": today + timedelta(days=45),
            "success_metrics": "Vendor pack delivered · poster install checklist 100% · attestations returned ≥95%",
            "risks": "Vendor fatigue — single coordinated wave, not three teams emailing",
            "linked_program": "VND-2026-003 · AST-2026-005",
            "summary": "Third-party campaign channel is distinct from workforce SAT.",
        },
        {
            "campaign_id": "CMP-2026-005",
            "name": "New hire security culture — first 30 days",
            "type": "New-hire onboarding comms",
            "theme": "Security is day 1, not day 90",
            "objective": "Automated 4-touch drip: welcome → report button → clean desk → manager check-in",
            "audience_segment": "New hires <90d (rolling)",
            "owner": "HR + Awareness",
            "sponsor": "CHRO",
            "budget_usd": 500,
            "phase": "Sustain",
            "status": "Live (always-on)",
            "start": today - timedelta(days=120),
            "end": today + timedelta(days=245),
            "success_metrics": "Drip completion ≥85% · day-7 report button awareness survey · manager check-in logged",
            "risks": "Mailbox enabled before drip touch 1 — HRIS timing bug",
            "linked_program": "PHISH-2026-006 (tracker sim after touch 2)",
            "summary": "Always-on drip campaign. Calendar-driven waves, not a one-shot blast.",
        },
        {
            "campaign_id": "CMP-2026-006",
            "name": "Q2 deepfake / vishing executive briefing",
            "type": "Executive / board narrative",
            "theme": "Voice + email combo attacks on wire requests",
            "objective": "EA + CFO staff briefing; board slide one-pager; no full workforce blast",
            "audience_segment": "Executive · EAs · Finance leadership (~42)",
            "owner": "Awareness + CFO office",
            "sponsor": "CEO",
            "budget_usd": 0,
            "phase": "Close",
            "status": "Completed",
            "start": today - timedelta(days=75),
            "end": today - timedelta(days=60),
            "success_metrics": "Briefing held · callback-verify procedure adopted · board slide filed",
            "risks": "—",
            "linked_program": "PHISH-2026-005 retro input",
            "summary": "Closed exec campaign — feeds retro library for reuse.",
        },
        {
            "campaign_id": "CMP-2026-007",
            "name": "Privacy awareness — workforce notice refresh",
            "type": "Compliance deadline comms",
            "theme": "RoPA / rights / report privacy questions to DPO",
            "objective": "Intranet publish + Teams post + poster; link privacy portal; not a duplicate of SAT privacy module",
            "audience_segment": "All with HRIS profile",
            "owner": "DPO office + Awareness",
            "sponsor": "GC",
            "budget_usd": 2200,
            "phase": "Approve",
            "status": "Awaiting Legal",
            "start": today + timedelta(days=14),
            "end": today + timedelta(days=44),
            "success_metrics": "Publish by deadline · acknowledgment tracking via intranet · DPO inbox categorization",
            "risks": "ISO 27701 wording review — don't ship before Legal",
            "linked_program": "Privacy app RoPA comms",
            "summary": "Compliance comms campaign — content approval is the gating artifact.",
        },
    ]

    # ── Audience segments (targeting definitions — not people-risk) ─
    segments = [
        {
            "segment_id": "SEG-2026-001",
            "name": "All workforce",
            "definition": "Active HRIS · corporate email",
            "est_size": 1820,
            "channels_ok": "Email · Intranet · Teams · Signage",
            "owner": "Awareness",
        },
        {
            "segment_id": "SEG-2026-002",
            "name": "People managers",
            "definition": "Manager flag in HRIS · responsible for ≥1 FTE",
            "est_size": 210,
            "channels_ok": "Manager toolkit · Email · Huddle guides",
            "owner": "HR + Awareness",
        },
        {
            "segment_id": "SEG-2026-003",
            "name": "Finance / payment authority",
            "definition": "Payment system role · AP/AR approvers",
            "est_size": 86,
            "channels_ok": "Email · Poster · Live tabletop",
            "owner": "Finance control",
        },
        {
            "segment_id": "SEG-2026-004",
            "name": "Privileged + vendor admins",
            "definition": "PAM users · Orbit AMS named IDs",
            "est_size": 64,
            "channels_ok": "Email · Vendor pack · Colo poster",
            "owner": "TPRM",
        },
        {
            "segment_id": "SEG-2026-005",
            "name": "New hires <90d",
            "definition": "Hire date rolling window",
            "est_size": 38,
            "channels_ok": "Drip email · HRIS task · Manager script",
            "owner": "HR",
        },
        {
            "segment_id": "SEG-2026-006",
            "name": "Executive / EA",
            "definition": "C-suite · direct EAs",
            "est_size": 42,
            "channels_ok": "Briefing · Slide · Secure email",
            "owner": "CFO/CEO office",
        },
    ]

    # ── Content assets (creative library) ────────────────────────────
    assets = [
        {"asset_id": "AST-C-001", "campaign_id": "CMP-2026-001", "type": "Email template", "title": "After INC-001 — report in Outlook, don't forward to helpdesk", "version": "v4", "approval": "Approved", "owner": "Awareness + Legal", "locale": "EN", "notes": "Subject A/B: '340 of you forwarded this' vs 'Report button — 10 seconds'. Legal cleared redacted screenshot."},
        {"asset_id": "AST-C-002", "campaign_id": "CMP-2026-001", "type": "Poster", "title": "NOC/colo — PAB on mail + mobile (NorthStack)", "version": "v2", "approval": "Approved", "owner": "Facilities + IBM i Ops", "locale": "EN", "notes": "PRODBOX/NOC break areas — not generic break-room art. PO-4481."},
        {"asset_id": "AST-C-003", "campaign_id": "CMP-2026-001", "type": "Manager script", "title": "Dept attestation — who still forwards instead of reports", "version": "v2", "approval": "Approved", "owner": "HR + SOC", "locale": "EN", "notes": "Names lagging units: Marketing 62%, Support 58%, Warehouse 71% attested. Finance/IT template."},
        {"asset_id": "AST-C-004", "campaign_id": "CMP-2026-001", "type": "Intranet page", "title": "Report hub — PAB, security@, mobile, what happens next", "version": "v5", "approval": "Approved", "owner": "Comms + SOC", "locale": "EN", "notes": "Replaced generic CSAM hub. FAQ from real helpdesk tickets (redacted)."},
        {"asset_id": "AST-C-014", "campaign_id": "CMP-2026-001", "type": "FAQ", "title": "Helpdesk vs security@ — when to use which", "version": "v2", "approval": "Approved", "owner": "SOC", "locale": "EN", "notes": "Deflect password resets; route phish to PAB."},
        {"asset_id": "AST-C-015", "campaign_id": "CMP-2026-001", "type": "Slide deck", "title": "CISO town hall — INC cluster timeline (board commit)", "version": "v1", "approval": "Approved", "owner": "CISO office", "locale": "EN", "notes": "Used day −16. Sets why October is reporting, not mascots."},
        {"asset_id": "AST-C-016", "campaign_id": "CMP-2026-001", "type": "Video short", "title": "90s PAB demo — mobile + desktop", "version": "v1", "approval": "Approved", "owner": "Awareness", "locale": "EN", "notes": "For warehouse/colo staff without daily Outlook habits."},
        {"asset_id": "AST-C-017", "campaign_id": "CMP-2026-001", "type": "Manager script", "title": "IBM i / colo shift huddle (5 min)", "version": "v1", "approval": "Approved", "owner": "IBM i Ops", "locale": "EN", "notes": "Read-rate on email <40% in ops — mandatory shift start."},
        {"asset_id": "AST-C-005", "campaign_id": "CMP-2026-002", "type": "Email template", "title": "Payroll scam alert — single source", "version": "v2", "approval": "Approved", "owner": "HR Comms", "locale": "EN", "notes": "Legal footnote INC-2026-009"},
        {"asset_id": "AST-C-006", "campaign_id": "CMP-2026-002", "type": "FAQ", "title": "Is this HR email real?", "version": "v1", "approval": "Approved", "owner": "Awareness", "locale": "EN", "notes": "Intranet only"},
        {"asset_id": "AST-C-007", "campaign_id": "CMP-2026-003", "type": "Manager script", "title": "Dual-channel wire verify", "version": "v2", "approval": "Approved", "owner": "Finance control", "locale": "EN", "notes": "CFO intro video linked"},
        {"asset_id": "AST-C-008", "campaign_id": "CMP-2026-003", "type": "Poster", "title": "Stop · Call · Verify", "version": "v1", "approval": "Approved", "owner": "Finance", "locale": "EN", "notes": "AP pod install"},
        {"asset_id": "AST-C-009", "campaign_id": "CMP-2026-003", "type": "Slide deck", "title": "BEC tabletop facilitator", "version": "v1", "approval": "In review", "owner": "Awareness", "locale": "EN", "notes": "Waiting CFO EA comment"},
        {"asset_id": "AST-C-010", "campaign_id": "CMP-2026-004", "type": "Email template", "title": "Vendor admin — named ID policy", "version": "v1", "approval": "Draft", "owner": "TPRM", "locale": "EN", "notes": "Orbit AMS co-brand"},
        {"asset_id": "AST-C-011", "campaign_id": "CMP-2026-005", "type": "Email template", "title": "Day 1 — Welcome security", "version": "v3", "approval": "Approved", "owner": "HR", "locale": "EN", "notes": "Drip step 1"},
        {"asset_id": "AST-C-012", "campaign_id": "CMP-2026-005", "type": "Email template", "title": "Day 7 — Report button", "version": "v2", "approval": "Approved", "owner": "Awareness", "locale": "EN", "notes": "Drip step 2"},
        {"asset_id": "AST-C-013", "campaign_id": "CMP-2026-007", "type": "Intranet page", "title": "Privacy at Acme — 2026 notice", "version": "v1", "approval": "In review", "owner": "DPO", "locale": "EN", "notes": "Legal redlines open"},
    ]

    # ── Waves / touchpoints (delivery schedule) ──────────────────────
    waves = [
        {"wave_id": "WAV-2026-001", "campaign_id": "CMP-2026-001", "name": "CISO town hall — why reporting failed in INC-001", "channel": "Town hall / live event", "segment": "SEG-2026-001", "phase": "Teaser", "scheduled": today - timedelta(days=16), "status": "Delivered", "owner": "CISO office", "reach_pct": 68.0, "engage_pct": 54.0, "notes": "Recording on intranet · board commit read verbatim"},
        {"wave_id": "WAV-2026-002", "campaign_id": "CMP-2026-001", "name": "Launch email — '340 forwarded to helpdesk' + PAB how-to", "channel": "Email newsletter", "segment": "SEG-2026-001", "phase": "Launch", "scheduled": today - timedelta(days=14), "status": "Delivered", "owner": "Awareness", "reach_pct": 96.0, "engage_pct": 58.0, "notes": "Open 58% · hub click 31% · subject B won (+4% open)"},
        {"wave_id": "WAV-2026-003", "campaign_id": "CMP-2026-001", "name": "Manager attestation — lagging dept call-out", "channel": "Manager toolkit", "segment": "SEG-2026-002", "phase": "Sustain", "scheduled": today - timedelta(days=7), "status": "Live", "owner": "HR + SOC", "reach_pct": 78.0, "engage_pct": 72.0, "notes": "Marketing/Support/Warehouse below 65% — exec ping sent"},
        {"wave_id": "WAV-2026-004", "campaign_id": "CMP-2026-001", "name": "IBM i / colo shift huddles (NorthStack)", "channel": "Table topic / huddle", "segment": "SEG-2026-001", "phase": "Sustain", "scheduled": today - timedelta(days=5), "status": "Live", "owner": "IBM i Ops", "reach_pct": 62.0, "engage_pct": 88.0, "notes": "6/8 colo shifts done · PRODBOX night crew Thu"},
        {"wave_id": "WAV-2026-005", "campaign_id": "CMP-2026-001", "name": "Teams — redacted real phish from INC-001", "channel": "Teams / Slack", "segment": "SEG-2026-001", "phase": "Sustain", "scheduled": today + timedelta(days=2), "status": "Scheduled", "owner": "SOC", "reach_pct": None, "engage_pct": None, "notes": "Show actual stuffing lure · quiz poll 'report or delete?'"},
        {"wave_id": "WAV-2026-006", "campaign_id": "CMP-2026-001", "name": "Intranet — report vs forward decision tree", "channel": "Intranet / SharePoint", "segment": "SEG-2026-001", "phase": "Sustain", "scheduled": today - timedelta(days=10), "status": "Delivered", "owner": "Comms", "reach_pct": 44.0, "engage_pct": 36.0, "notes": "Linked from helpdesk auto-reply template"},
        {"wave_id": "WAV-2026-017", "campaign_id": "CMP-2026-001", "name": "NOC/colo posters (8 sites)", "channel": "Poster / print", "segment": "SEG-2026-001", "phase": "Sustain", "scheduled": today - timedelta(days=4), "status": "Delivered", "owner": "Facilities", "reach_pct": 75.0, "engage_pct": None, "notes": "6/8 installed — remote warehouse + DR tape room pending"},
        {"wave_id": "WAV-2026-018", "campaign_id": "CMP-2026-001", "name": "SOC office hours — bring suspicious email", "channel": "Town hall / live event", "segment": "SEG-2026-001", "phase": "Sustain", "scheduled": today + timedelta(days=5), "status": "Scheduled", "owner": "SOC", "reach_pct": None, "engage_pct": None, "notes": "3×30min slots · target Support/Marketing"},
        {"wave_id": "WAV-2026-019", "campaign_id": "CMP-2026-001", "name": "Close — board metrics email (PAB delta)", "channel": "Email newsletter", "segment": "SEG-2026-001", "phase": "Close", "scheduled": today + timedelta(days=12), "status": "Planned", "owner": "CISO + Awareness", "reach_pct": None, "engage_pct": None, "notes": "Include SOC baseline chart · what we still owe for IFS lesson"},
        {"wave_id": "WAV-2026-020", "campaign_id": "CMP-2026-001", "name": "DESCOPED — generic October mascot / puzzle poster", "channel": "Poster / print", "segment": "SEG-2026-001", "phase": "Build", "scheduled": today - timedelta(days=25), "status": "Skipped", "owner": "Marketing", "reach_pct": None, "engage_pct": None, "notes": "Killed — CISO: 'We're not doing CSAM clipart after three incidents.'"},
        {"wave_id": "WAV-2026-007", "campaign_id": "CMP-2026-002", "name": "Emergency all-hands email", "channel": "Email newsletter", "segment": "SEG-2026-001", "phase": "Launch", "scheduled": today - timedelta(days=3), "status": "Delivered", "owner": "HR Comms", "reach_pct": 99.0, "engage_pct": 74.0, "notes": "Legal approved v2"},
        {"wave_id": "WAV-2026-008", "campaign_id": "CMP-2026-002", "name": "Teams urgent post", "channel": "Teams / Slack", "segment": "SEG-2026-001", "phase": "Launch", "scheduled": today - timedelta(days=3), "status": "Delivered", "owner": "Awareness", "reach_pct": 91.0, "engage_pct": 35.0, "notes": "Pin 72h"},
        {"wave_id": "WAV-2026-009", "campaign_id": "CMP-2026-002", "name": "FAQ intranet publish", "channel": "Intranet / SharePoint", "segment": "SEG-2026-001", "phase": "Sustain", "scheduled": today - timedelta(days=2), "status": "Delivered", "owner": "Awareness", "reach_pct": 38.0, "engage_pct": 31.0, "notes": "Growing — promote in wave 10"},
        {"wave_id": "WAV-2026-010", "campaign_id": "CMP-2026-002", "name": "Payroll insert reminder", "channel": "Payroll insert / HR comms", "segment": "SEG-2026-001", "phase": "Sustain", "scheduled": today + timedelta(days=4), "status": "Blocked", "owner": "HR", "reach_pct": None, "engage_pct": None, "notes": "Blocked — PayrollCo IR freeze; use email only"},
        {"wave_id": "WAV-2026-011", "campaign_id": "CMP-2026-003", "name": "CFO video + toolkit email", "channel": "Email newsletter", "segment": "SEG-2026-003", "phase": "Launch", "scheduled": today - timedelta(days=8), "status": "Delivered", "owner": "Finance", "reach_pct": 100.0, "engage_pct": 82.0, "notes": "Toolkit PDF attached"},
        {"wave_id": "WAV-2026-012", "campaign_id": "CMP-2026-003", "name": "AP pod posters", "channel": "Poster / print", "segment": "SEG-2026-003", "phase": "Sustain", "scheduled": today - timedelta(days=3), "status": "Delivered", "owner": "Finance", "reach_pct": 95.0, "engage_pct": None, "notes": "6/6 pods"},
        {"wave_id": "WAV-2026-013", "campaign_id": "CMP-2026-003", "name": "BEC tabletop sessions", "channel": "Town hall / live event", "segment": "SEG-2026-003", "phase": "Sustain", "scheduled": today + timedelta(days=7), "status": "Scheduled", "owner": "Finance control", "reach_pct": None, "engage_pct": None, "notes": "3 sessions scheduled"},
        {"wave_id": "WAV-2026-014", "campaign_id": "CMP-2026-005", "name": "Drip 1 — welcome", "channel": "Email newsletter", "segment": "SEG-2026-005", "phase": "Launch", "scheduled": today - timedelta(days=1), "status": "Delivered", "owner": "HR", "reach_pct": 100.0, "engage_pct": 88.0, "notes": "Auto on hire"},
        {"wave_id": "WAV-2026-015", "campaign_id": "CMP-2026-005", "name": "Drip 2 — report button", "channel": "Email newsletter", "segment": "SEG-2026-005", "phase": "Sustain", "scheduled": today + timedelta(days=6), "status": "Scheduled", "owner": "Awareness", "reach_pct": None, "engage_pct": None, "notes": "Day 7 trigger"},
        {"wave_id": "WAV-2026-016", "campaign_id": "CMP-2026-004", "name": "Vendor pack send", "channel": "Email newsletter", "segment": "SEG-2026-004", "phase": "Launch", "scheduled": today + timedelta(days=10), "status": "Planned", "owner": "TPRM", "reach_pct": None, "engage_pct": None, "notes": "Await AST-C-010 approval"},
    ]

    # ── Approvals queue ──────────────────────────────────────────────
    approvals = [
        {"appr_id": "APR-2026-001", "asset_id": "AST-C-009", "campaign_id": "CMP-2026-003", "title": "BEC tabletop deck", "reviewer": "CFO EA", "due": today + timedelta(days=2), "status": "In review"},
        {"appr_id": "APR-2026-002", "asset_id": "AST-C-010", "campaign_id": "CMP-2026-004", "title": "Vendor named-ID email", "reviewer": "TPRM + Legal", "due": today + timedelta(days=5), "status": "Draft"},
        {"appr_id": "APR-2026-003", "asset_id": "AST-C-013", "campaign_id": "CMP-2026-007", "title": "Privacy notice intranet", "reviewer": "GC / DPO", "due": today + timedelta(days=3), "status": "In review"},
        {"appr_id": "APR-2026-004", "asset_id": "AST-C-005", "campaign_id": "CMP-2026-002", "title": "Payroll scam email v2", "reviewer": "Legal", "due": today - timedelta(days=4), "status": "Approved"},
    ]

    # ── Campaign-level KPIs (engagement, not people-risk) ───────────
    kpis = [
        {"kpi_id": "CKPI-001", "campaign_id": "CMP-2026-001", "name": "PAB reports / week vs 12-wk baseline", "value": 18.0, "target": 22.0, "unit": "% uplift", "as_of": today},
        {"kpi_id": "CKPI-002", "campaign_id": "CMP-2026-001", "name": "Helpdesk phish misroutes (wkly avg)", "value": 41.0, "target": 40.0, "unit": "% reduction", "as_of": today},
        {"kpi_id": "CKPI-003", "campaign_id": "CMP-2026-001", "name": "Manager attestation (all depts)", "value": 78.0, "target": 95.0, "unit": "%", "as_of": today},
        {"kpi_id": "CKPI-007", "campaign_id": "CMP-2026-001", "name": "Colo/NOC poster sites installed", "value": 6.0, "target": 8.0, "unit": "sites", "as_of": today},
        {"kpi_id": "CKPI-008", "campaign_id": "CMP-2026-001", "name": "Ops shift huddle completion", "value": 75.0, "target": 100.0, "unit": "% shifts", "as_of": today},
        {"kpi_id": "CKPI-004", "campaign_id": "CMP-2026-002", "name": "Emergency email open", "value": 74.0, "target": 70.0, "unit": "%", "as_of": today},
        {"kpi_id": "CKPI-005", "campaign_id": "CMP-2026-003", "name": "Toolkit delivered", "value": 100.0, "target": 100.0, "unit": "%", "as_of": today},
        {"kpi_id": "CKPI-006", "campaign_id": "CMP-2026-003", "name": "Tabletop scheduled", "value": 3.0, "target": 3.0, "unit": "sessions", "as_of": today},
    ]

    # Deep packs for featured campaigns
    deep = {
        "CMP-2026-001": {
            "brief": {
                "trigger": "Board ask (2026-09-12): 'What changed after INC-001, 005, 009?' IR interviews: users forwarded phish to helpdesk, didn't know PAB, ops shifts never got email.",
                "problem": "SOC baseline: 41 PAB reports/wk vs 127 helpdesk 'is this real?' tickets/wk. Portal stuffing (INC-001) — 340 users forwarded alerts internally instead of reporting.",
                "board_commit": "Measurable reporting behavior change by end of Q4 — not another awareness month poster.",
                "key_messages": [
                    "Report with PAB or security@ — never forward to helpdesk",
                    "Helpdesk resets passwords; SOC triages threats — different jobs",
                    "Managers attest their team knows the difference (named lagging depts)",
                    "Colo/IBM i: shift huddle + poster — email alone fails here",
                ],
                "baseline": "12-wk pre-campaign: PAB 41/wk · misroute tickets 127/wk · Marketing attestation 0%",
                "lagging_units": "Marketing (62% attested) · Customer Support (58%) · Warehouse (71%) · IBM i night crew (pending)",
                "cta": "Report suspicious mail now · managers complete attestation · ops shifts attend huddle",
                "non_goals": "No mascot/puzzle CSAM content (WAV-2026-020 killed). Not SAT modules or phishing sim scores — see Training Tracker.",
            },
            "checklist": [
                {"item": "Legal sign-off on redacted INC-001 screenshot in email", "done": True},
                {"item": "CISO town hall delivered + recording posted", "done": True},
                {"item": "Helpdesk auto-reply links to report hub (AST-C-004)", "done": True},
                {"item": "Manager attestation form live with dept leaderboard", "done": True},
                {"item": "IBM i / colo shift huddles 6/8 complete", "done": False},
                {"item": "NOC posters 6/8 sites (warehouse + DR room outstanding)", "done": False},
                {"item": "Coordinate wording with CMP-2026-002 PayrollCo IR comms", "done": True},
                {"item": "Board close-out metrics draft for WAV-2026-019", "done": False},
                {"item": "Kill generic October mascot creative (WAV-2026-020)", "done": True},
            ],
            "retro": None,
        },
        "CMP-2026-003": {
            "brief": {
                "problem": "Finance cohort click rate on BEC sims unacceptable; need behavior message before next sim.",
                "key_messages": ["Dual-channel verify", "No wire changes on email alone", "CFO backs procedure"],
                "cta": "Complete toolkit · attend tabletop",
                "non_goals": "Not individual risk scoring — see Training Tracker for that",
            },
            "checklist": [
                {"item": "CFO video recorded", "done": True},
                {"item": "AP posters installed", "done": True},
                {"item": "Tabletop deck approved", "done": False},
                {"item": "Align sim date +48h after launch email", "done": True},
            ],
            "retro": None,
        },
        "CMP-2026-005": {
            "brief": {
                "problem": "New hires get mailbox before security culture message; 21% click on onboarding phish.",
                "key_messages": ["Security day 1", "Report button before first week ends", "Manager check-in day 14"],
                "cta": "Complete HRIS security tasks",
                "non_goals": "Not a one-time blast — drip automation",
            },
            "checklist": [
                {"item": "HRIS trigger wired", "done": True},
                {"item": "Drip 1/4 live", "done": True},
                {"item": "Manager script in onboarding kit", "done": True},
                {"item": "Fix mailbox-before-drip race", "done": False},
            ],
            "retro": None,
        },
    }

    narrative = [
        {"lane": "Live now", "text": "Q4 report-first campaign (post-INC board commit) week 3 · Payroll IR comms · Finance wire push · new-hire drip."},
        {"lane": "Blocked", "text": "Payroll insert wave blocked by PayrollCo IR — reroute to email/Teams only."},
        {"lane": "Pipeline", "text": "Vendor admin campaign builds next week; privacy notice awaits Legal."},
        {"lane": "Not this app", "text": "Phishing sim clicks and people-risk scores live in Training Tracker — this is comms orchestration."},
    ]

    df_c = pd.DataFrame(campaigns)
    for col in ("start", "end"):
        df_c[col] = pd.to_datetime(df_c[col], errors="coerce")
    df_c["brief_pack"] = df_c["campaign_id"].map(lambda i: deep.get(i, {}).get("brief"))
    df_c["checklist"] = df_c["campaign_id"].map(lambda i: deep.get(i, {}).get("checklist", []))

    df_s = pd.DataFrame(segments)
    df_a = pd.DataFrame(assets)
    df_w = pd.DataFrame(waves)
    df_w["scheduled"] = pd.to_datetime(df_w["scheduled"], errors="coerce")
    df_ap = pd.DataFrame(approvals)
    df_ap["due"] = pd.to_datetime(df_ap["due"], errors="coerce")
    df_k = pd.DataFrame(kpis)
    df_k["as_of"] = pd.to_datetime(df_k["as_of"], errors="coerce")
    df_n = pd.DataFrame(narrative)

    return df_c, df_s, df_a, df_w, df_ap, df_k, df_n


def _enrich_campaign(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["days_left"] = (out["end"] - today).dt.days
    out["pct_elapsed"] = ((today - out["start"]) / (out["end"] - out["start"]).clip(lower=pd.Timedelta(days=1)) * 100).round(0)
    out["live"] = out["status"].astype(str).str.contains("Live", case=False)
    return out


def _enrich_wave(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["overdue"] = out["status"].isin(["Planned", "Scheduled"]) & (out["scheduled"] < today)
    out["this_week"] = (out["scheduled"] >= today - timedelta(days=today.weekday())) & (
        out["scheduled"] <= today + timedelta(days=6 - today.weekday())
    )
    return out


def _sync(seed: int):
    need = st.session_state.get(_SYNC_KEY) != seed or "camp_campaigns" not in st.session_state
    if need:
        c, s, a, w, ap, k, n = _sample(seed)
        st.session_state.camp_campaigns = c
        st.session_state.camp_segments = s
        st.session_state.camp_assets = a
        st.session_state.camp_waves = w
        st.session_state.camp_approvals = ap
        st.session_state.camp_kpis = k
        st.session_state.camp_narrative = n
        st.session_state[_SYNC_KEY] = seed
    return (
        st.session_state.camp_campaigns,
        st.session_state.camp_segments,
        st.session_state.camp_assets,
        st.session_state.camp_waves,
        st.session_state.camp_approvals,
        st.session_state.camp_kpis,
        st.session_state.camp_narrative,
    )


def _save_campaigns(df):
    st.session_state.camp_campaigns = df.reset_index(drop=True)


def _save_waves(df):
    st.session_state.camp_waves = df.reset_index(drop=True)


def _save_assets(df):
    st.session_state.camp_assets = df.reset_index(drop=True)


def _save_approvals(df):
    st.session_state.camp_approvals = df.reset_index(drop=True)


def _patch_campaign(cid, **fields):
    df = st.session_state.camp_campaigns.copy()
    loc = df.index[df["campaign_id"] == cid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_campaigns(df)


def _patch_wave(wid, **fields):
    df = st.session_state.camp_waves.copy()
    loc = df.index[df["wave_id"] == wid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_waves(df)


def _patch_approval(aid, **fields):
    df = st.session_state.camp_approvals.copy()
    loc = df.index[df["appr_id"] == aid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_approvals(df)


def _patch_asset(asid, **fields):
    df = st.session_state.camp_assets.copy()
    loc = df.index[df["asset_id"] == asid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_assets(df)


def _fmt(ts) -> str:
    try:
        if ts is None or pd.isna(ts):
            return "—"
        return pd.Timestamp(ts).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _campaign_detail(row, waves, assets, kpis, *, widget_key: str):
    cid = row["campaign_id"]
    wk = widget_key
    st.markdown(f"### {cid} · {row['name']}")
    a, b, c, d = st.columns(4)
    a.metric("Phase", row["phase"])
    b.metric("Status", row["status"].split("—")[0].strip()[:20])
    c.metric("Days left", int(row["days_left"]) if row["days_left"] >= 0 else 0)
    d.metric("Budget", f"${int(row['budget_usd']):,}")

    c1, c2 = st.columns(2)
    c1.write(f"**Type:** {row['type']}")
    c1.write(f"**Theme:** {row['theme']}")
    c1.write(f"**Audience:** {row['audience_segment']}")
    c1.write(f"**Owner / sponsor:** {row['owner']} · {row['sponsor']}")
    c1.write(f"**Window:** {_fmt(row['start'])} → {_fmt(row['end'])} ({int(row['pct_elapsed'])}% elapsed)")
    c2.write(f"**Objective:** {row['objective']}")
    c2.write(f"**Success metrics:** {row['success_metrics']}")
    c2.write(f"**Risks:** {row['risks']}")
    c2.write(f"**Linked:** {row['linked_program']}")
    st.write(row["summary"])

    brief = row.get("brief_pack")
    if brief:
        with st.expander("Campaign brief", expanded=True):
            if brief.get("trigger"):
                st.write(f"**Trigger:** {brief['trigger']}")
            if brief.get("board_commit"):
                st.write(f"**Board commit:** {brief['board_commit']}")
            st.write(f"**Problem:** {brief.get('problem', '')}")
            if brief.get("baseline"):
                st.write(f"**SOC baseline:** {brief['baseline']}")
            msgs = brief.get("key_messages", "")
            if isinstance(msgs, list):
                for m in msgs:
                    st.write(f"- {m}")
            else:
                st.write(f"**Key messages:** {msgs}")
            if brief.get("lagging_units"):
                st.write(f"**Lagging units:** {brief['lagging_units']}")
            st.write(f"**CTA:** {brief.get('cta', '')}")
            st.write(f"**Non-goals:** {brief.get('non_goals', '')}")

    checklist = row.get("checklist") or []
    if checklist:
        with st.expander(f"Runbook checklist ({len(checklist)})", expanded=True):
            st.dataframe(pd.DataFrame(checklist), use_container_width=True, hide_index=True)

    cw = waves[waves["campaign_id"] == cid].sort_values("scheduled")
    if not cw.empty:
        with st.expander(f"Waves / touchpoints ({len(cw)})", expanded=True):
            show = cw.copy()
            show["scheduled"] = show["scheduled"].apply(_fmt)
            st.dataframe(
                show[
                    [
                        "wave_id",
                        "name",
                        "channel",
                        "phase",
                        "scheduled",
                        "status",
                        "reach_pct",
                        "engage_pct",
                        "notes",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

    ca = assets[assets["campaign_id"] == cid]
    if not ca.empty:
        with st.expander(f"Assets ({len(ca)})", expanded=False):
            st.dataframe(ca, use_container_width=True, hide_index=True)

    ck = kpis[kpis["campaign_id"] == cid]
    if not ck.empty:
        with st.expander(f"Campaign KPIs ({len(ck)})", expanded=False):
            st.dataframe(ck, use_container_width=True, hide_index=True)

    # Mini Gantt for waves
    if not cw.empty and cw["scheduled"].notna().any():
        g = cw.copy()
        g["scheduled"] = pd.to_datetime(g["scheduled"], errors="coerce")
        g = g.dropna(subset=["scheduled"])
        if not g.empty:
            fig = px.scatter(
                g,
                x="scheduled",
                y="channel",
                color="status",
                symbol="phase",
                hover_name="name",
                title="Touchpoint calendar",
            )
            fig.update_layout(height=max(260, len(g["channel"].unique()) * 40), margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True, key=f"plotly_gantt_{wk}_{cid}")


def main() -> None:
    portfolio_skin.page_header(
        title="Security Awareness Campaign Manager",
        lede="Comms campaign orchestration — briefs, segments, multi-channel waves, assets, approvals, reach/engagement KPIs. Not the Training Tracker (sims/people-risk). Club demo — synthetic.",
        kicker="Awareness · Campaigns",
    )

    seed = demo_kit.seed_controls()
    campaigns, segments, assets, waves, approvals, kpis, narrative = _sync(seed)
    ec = _enrich_campaign(campaigns)
    ew = _enrich_wave(waves)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    live_only = st.sidebar.checkbox("Live campaigns only", value=False)
    type_f = st.sidebar.multiselect("Campaign types", CAMPAIGN_TYPES, default=CAMPAIGN_TYPES)

    view_c = ec[ec["type"].isin(type_f)]
    if live_only:
        view_c = view_c[view_c["live"]]

    live_n = int(ec["live"].sum())
    blocked_w = int(ew["status"].eq("Blocked").sum())
    od_w = int(ew["overdue"].sum())
    pend_ap = int(approvals["status"].isin(["Draft", "In review"]).sum())
    week_w = int(ew["this_week"].sum())

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Campaigns", len(ec))
    k2.metric("Live", live_n)
    k3.metric("Waves this week", week_w)
    k4.metric("Blocked waves", blocked_w)
    k5.metric("Overdue scheduled", od_w)
    k6.metric("Assets in review", pend_ap)

    if blocked_w:
        st.warning(f"{blocked_w} wave(s) blocked — check IR/legal dependencies before forcing send.")

    work, cal_tab, assets_tab, segments_tab, approvals_tab, intake, export = st.tabs(
        [
            "Workbench",
            "Calendar / waves",
            "Asset library",
            "Segments",
            "Approvals",
            "Intake",
            "Export",
        ]
    )

    with work:
        st.subheader("Campaign workbench")
        for _, n in narrative.iterrows():
            st.write(f"**{n['lane']}:** {n['text']}")

        feat = view_c[view_c["campaign_id"].isin(FEATURED)].copy()
        order = {i: n for n, i in enumerate(["CMP-2026-001", "CMP-2026-003", "CMP-2026-005"])}
        feat["_o"] = feat["campaign_id"].map(lambda x: order.get(x, 99))
        st.markdown(f"**Featured campaigns — statement of record ({len(feat)})**")
        for _, row in feat.sort_values("_o").iterrows():
            st.markdown("---")
            _campaign_detail(row, ew, assets, kpis, widget_key=f"feat_{row['campaign_id']}")
            st.markdown("---")

        hot_w = ew[(ew["overdue"] | ew["status"].eq("Blocked")) & ew["campaign_id"].isin(view_c["campaign_id"])]
        st.markdown(f"**Attention waves ({len(hot_w)})**")
        if hot_w.empty:
            st.info("No blocked/overdue waves in filter.")
        else:
            for _, w in hot_w.sort_values("scheduled").iterrows():
                with st.expander(f"{w['wave_id']} · {w['name']} · {w['status']}"):
                    st.write(f"**Campaign:** {w['campaign_id']} · **Channel:** {w['channel']}")
                    st.write(f"**Scheduled:** {_fmt(w['scheduled'])} · **Owner:** {w['owner']}")
                    st.write(w["notes"])
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if w["status"] == "Blocked" and st.button("Mark delivered (override)", key=f"wb_{w['wave_id']}"):
                            _patch_wave(w["wave_id"], status="Delivered", notes=(w["notes"] or "") + " [Override send.]")
                            st.rerun()
                    with c2:
                        if w["status"] in {"Planned", "Scheduled", "Blocked"} and st.button(
                            "Skip wave", key=f"ws_{w['wave_id']}"
                        ):
                            _patch_wave(w["wave_id"], status="Skipped")
                            st.rerun()
                    with c3:
                        if w["overdue"] and st.button("Mark live", key=f"wl_{w['wave_id']}"):
                            _patch_wave(w["wave_id"], status="Live")
                            st.rerun()

        st.markdown("**All campaigns**")
        show = view_c[
            ["campaign_id", "name", "type", "phase", "status", "start", "end", "owner", "budget_usd"]
        ].copy()
        show["start"] = show["start"].apply(_fmt)
        show["end"] = show["end"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

    with cal_tab:
        st.subheader("Content calendar / waves")
        st.caption("Multi-channel touchpoints — email, intranet, posters, manager toolkits, events. Campaign delivery ops.")
        cal_view = ew.merge(
            campaigns[["campaign_id", "name"]].rename(columns={"name": "campaign_name"}),
            on="campaign_id",
            how="left",
        )
        cal_view = cal_view[cal_view["campaign_id"].isin(view_c["campaign_id"])]
        show = cal_view.sort_values("scheduled").copy()
        show["scheduled"] = show["scheduled"].apply(_fmt)
        st.dataframe(
            show[
                [
                    "wave_id",
                    "campaign_id",
                    "campaign_name",
                    "name",
                    "channel",
                    "phase",
                    "scheduled",
                    "status",
                    "reach_pct",
                    "engage_pct",
                    "owner",
                ]
            ].rename(columns={"name": "wave", "campaign_name": "campaign"}),
            use_container_width=True,
            hide_index=True,
        )

        fig = px.timeline(
            cal_view.assign(
                Start=cal_view["scheduled"],
                Finish=cal_view["scheduled"] + pd.Timedelta(days=1),
            ),
            x_start="Start",
            x_end="Finish",
            y="name",
            color="channel",
            hover_name="wave_id",
            title="Wave timeline (by touchpoint)",
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=500, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True, key="plotly_cal_timeline")

        # Channel mix for live campaigns
        live_ids = view_c[view_c["live"]]["campaign_id"]
        mix = ew[ew["campaign_id"].isin(live_ids)].groupby("channel").size().reset_index(name="waves")
        if not mix.empty:
            fig2 = px.pie(mix, names="channel", values="waves", title="Live campaign — channel mix (# waves)")
            fig2.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig2, use_container_width=True, key="plotly_channel_mix")

    with assets_tab:
        st.subheader("Creative / asset library")
        st.dataframe(assets, use_container_width=True, hide_index=True)
        pick = st.selectbox("Asset", assets["asset_id"].tolist(), key="asset_pick")
        ar = assets[assets["asset_id"] == pick].iloc[0]
        st.markdown(f"#### {ar['asset_id']} · {ar['title']}")
        st.write(f"**Campaign:** {ar['campaign_id']} · **Type:** {ar['type']} · **v{ar['version']}")
        st.write(f"**Approval:** {ar['approval']} · **Owner:** {ar['owner']}")
        st.write(ar["notes"])
        if ar["approval"] != "Approved" and st.button("Submit for approval", key=f"aa_{pick}"):
            _patch_asset(pick, approval="In review")
            st.rerun()

    with segments_tab:
        st.subheader("Audience segments (targeting)")
        st.caption("Who the campaign reaches — not individual risk scores (see Training Tracker).")
        st.dataframe(segments, use_container_width=True, hide_index=True)

        # Reach rollup from delivered waves
        deliv = ew[ew["status"].eq("Delivered") & ew["reach_pct"].notna()]
        if not deliv.empty:
            fig = px.bar(
                deliv.groupby("campaign_id")["reach_pct"].max().reset_index(),
                x="campaign_id",
                y="reach_pct",
                title="Best reach % among delivered waves (by campaign)",
            )
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True, key="plotly_reach_bar")

    with approvals_tab:
        st.subheader("Content approvals")
        for _, ap in approvals.sort_values("due").iterrows():
            flag = " · DUE" if ap["due"] < _today() and ap["status"] in {"Draft", "In review"} else ""
            with st.expander(f"{ap['appr_id']} · {ap['title']} · {ap['status']}{flag}"):
                st.write(f"**Campaign:** {ap['campaign_id']} · **Asset:** {ap['asset_id']}")
                st.write(f"**Reviewer:** {ap['reviewer']} · **Due:** {_fmt(ap['due'])}")
                if ap["status"] in {"Draft", "In review"} and st.button("Approve", key=f"ap_{ap['appr_id']}"):
                    _patch_approval(ap["appr_id"], status="Approved")
                    _patch_asset(ap["asset_id"], approval="Approved")
                    st.rerun()

        # Campaign KPIs board
        st.markdown("**Campaign KPIs (engagement)**")
        kshow = kpis.merge(campaigns[["campaign_id", "name"]], on="campaign_id")
        kshow["as_of"] = kshow["as_of"].apply(_fmt)
        st.dataframe(kshow, use_container_width=True, hide_index=True)

    with intake:
        st.subheader("New campaign brief")
        with st.form("intake_camp"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Campaign name")
                ctype = st.selectbox("Type", CAMPAIGN_TYPES)
                theme = st.text_input("Theme")
                owner = st.text_input("Owner")
            with c2:
                audience = st.text_input("Audience segment")
                budget = st.number_input("Budget USD", 0, 100000, 0)
                days = st.number_input("Duration (days)", 7, 365, 30)
            objective = st.text_area("Objective")
            if st.form_submit_button("Create campaign"):
                if not name.strip():
                    st.error("Name required.")
                else:
                    n = len(st.session_state.camp_campaigns) + 1
                    today = _today()
                    add = {
                        "campaign_id": f"CMP-2026-{n:03d}",
                        "name": name.strip(),
                        "type": ctype,
                        "theme": theme.strip() or "TBD",
                        "objective": objective.strip() or "TBD",
                        "audience_segment": audience.strip() or "TBD",
                        "owner": owner.strip() or "Awareness",
                        "sponsor": "CISO",
                        "budget_usd": int(budget),
                        "phase": "Brief",
                        "status": "Planning",
                        "start": today,
                        "end": today + timedelta(days=int(days)),
                        "success_metrics": "TBD",
                        "risks": "",
                        "linked_program": "",
                        "summary": "Intake stub — build waves and assets before launch.",
                        "brief_pack": None,
                        "checklist": [],
                    }
                    _save_campaigns(
                        pd.concat([st.session_state.camp_campaigns, pd.DataFrame([add])], ignore_index=True)
                    )
                    st.success(f"CMP-2026-{n:03d} created.")
                    st.rerun()

        st.subheader("Schedule wave")
        with st.form("intake_wave"):
            camp = st.selectbox("Campaign", campaigns["campaign_id"].tolist())
            wname = st.text_input("Wave name")
            channel = st.selectbox("Channel", CHANNELS)
            phase = st.selectbox("Phase", PHASES)
            seg = st.selectbox("Segment", segments["segment_id"].tolist())
            sched = st.number_input("Days from today", -30, 90, 7)
            if st.form_submit_button("Add wave"):
                if not wname.strip():
                    st.error("Wave name required.")
                else:
                    n = len(st.session_state.camp_waves) + 1
                    add = {
                        "wave_id": f"WAV-2026-{n:03d}",
                        "campaign_id": camp,
                        "name": wname.strip(),
                        "channel": channel,
                        "segment": seg,
                        "phase": phase,
                        "scheduled": _today() + timedelta(days=int(sched)),
                        "status": "Planned",
                        "owner": "Awareness",
                        "reach_pct": None,
                        "engage_pct": None,
                        "notes": "",
                    }
                    _save_waves(pd.concat([st.session_state.camp_waves, pd.DataFrame([add])], ignore_index=True))
                    st.success(f"WAV-2026-{n:03d} scheduled.")
                    st.rerun()

    with export:
        st.subheader("Export")
        out_c = ec.copy()
        out_c["start"] = out_c["start"].apply(_fmt)
        out_c["end"] = out_c["end"].apply(_fmt)
        for col in ("brief_pack", "checklist"):
            if col in out_c.columns:
                out_c = out_c.drop(columns=[col])
        demo_kit.csv_download(out_c, "campaigns.csv", label="Download campaigns")
        out_w = ew.copy()
        out_w["scheduled"] = out_w["scheduled"].apply(_fmt)
        demo_kit.csv_download(out_w, "campaign_waves.csv", label="Download waves", key="w_csv")
        demo_kit.csv_download(assets, "campaign_assets.csv", label="Download assets", key="a_csv")
        demo_kit.csv_download(segments, "audience_segments.csv", label="Download segments", key="s_csv")
        demo_kit.csv_download(kpis, "campaign_kpis.csv", label="Download KPIs", key="k_csv")
        st.caption("Campaign comms only. Phishing sims & people-risk → Training Tracker app.")


if __name__ == "__main__":
    main()
