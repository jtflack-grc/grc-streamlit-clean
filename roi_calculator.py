#!/usr/bin/env python3
"""Security & GRC investment business case workbench — club teaching toy.

Forrester TEI-style 3-year models (NPV, payback, benefit/cost streams) plus FAIR/ROSI
risk-reduction math for control investments. Synthetic portfolio scenarios — not live FP&A.
"""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="ROI Calculator · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

HORIZON = 3
DISCOUNT_DEFAULT = 0.10
FEATURED = {"INV-ROI-001", "INV-ROI-002", "INV-ROI-003", "INV-ROI-005"}
_SYNC_KEY = "_roi_seed_v2"

BENEFIT_CATS = [
    "Labor / productivity",
    "Audit & attestation efficiency",
    "Breach loss avoided (ALE reduction)",
    "Deal velocity & revenue enablement",
    "Insurance premium reduction",
    "Regulatory fine avoidance",
    "Vendor / incident cost avoidance",
]

COST_CATS = [
    "Implementation & integration",
    "Platform license / subscription",
    "Internal FTE (program)",
    "External consultants",
    "Audit & certification fees",
    "Ongoing operations",
]


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _npv(cashflows: list[float], rate: float) -> float:
    return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows))


def _irr(cashflows: list[float], guess: float = 0.15) -> float | None:
    """Simple IRR via numpy if sign change exists."""
    try:
        return float(np.irr(cashflows)) if hasattr(np, "irr") else None
    except Exception:
        pass
    # Newton-ish search
    low, high = -0.5, 1.0
    for _ in range(80):
        mid = (low + high) / 2
        v = _npv(cashflows, mid)
        if abs(v) < 1e-4:
            return mid
        if v > 0:
            low = mid
        else:
            high = mid
    return None


def _payback_months(net_by_year: list[float]) -> float | None:
    cumulative = 0.0
    for yr, net in enumerate(net_by_year):
        prior = cumulative
        cumulative += net
        if cumulative >= 0 and net != 0:
            fraction = (0 - prior) / net if net != 0 else 0
            return yr * 12 + fraction * 12
    return None


def _fair_ale(asset_value: float, exposure_pct: float, aro: float) -> tuple[float, float]:
    sle = asset_value * (exposure_pct / 100)
    ale = sle * aro
    return sle, ale


def _rosi(ale_before: float, ale_after: float, annual_cost: float) -> dict:
    avoided = ale_before - ale_after
    if annual_cost <= 0:
        roi_pct = float("inf") if avoided > 0 else 0.0
    else:
        roi_pct = ((avoided - annual_cost) / annual_cost) * 100
    return {
        "ale_before": ale_before,
        "ale_after": ale_after,
        "loss_avoided": avoided,
        "annual_cost": annual_cost,
        "rosi_pct": roi_pct,
        "payback_years": annual_cost / avoided if avoided > 0 else None,
    }


def _tei_from_streams(
    benefits: pd.DataFrame,
    costs: pd.DataFrame,
    *,
    discount_rate: float,
    horizon: int = HORIZON,
) -> dict:
    years = list(range(1, horizon + 1))
    ben_by_yr = [float(benefits[[f"y{y}" for y in years]].sum(axis=0).iloc[i - 1]) for i in years]
    cost_by_yr = [float(costs[[f"y{y}" for y in years]].sum(axis=0).iloc[i - 1]) for i in years]
    net_by_yr = [b - c for b, c in zip(ben_by_yr, cost_by_yr)]

    npv_ben = _npv(ben_by_yr, discount_rate)
    npv_cost = _npv(cost_by_yr, discount_rate)
    npv_net = npv_ben - npv_cost
    roi_pct = (npv_net / npv_cost * 100) if npv_cost > 0 else float("inf")
    bcr = (npv_ben / npv_cost) if npv_cost > 0 else float("inf")
    payback_mo = _payback_months(net_by_yr)

    cf_nets = [0.0] + list(np.cumsum([-c for c in cost_by_yr]))  # simplified for chart
    cumulative_net = list(np.cumsum(net_by_yr))

    return {
        "years": years,
        "benefits_by_year": ben_by_yr,
        "costs_by_year": cost_by_yr,
        "net_by_year": net_by_yr,
        "cumulative_net": cumulative_net,
        "npv_benefits": npv_ben,
        "npv_costs": npv_cost,
        "npv_net": npv_net,
        "roi_pct": roi_pct,
        "benefit_cost_ratio": bcr,
        "payback_months": payback_mo,
        "discount_rate": discount_rate,
    }


def _sample(seed: int):
    today = _today()
    rng = np.random.default_rng(seed)

    initiatives = [
        {
            "init_id": "INV-ROI-001",
            "name": "Integrated GRC platform (TEI composite)",
            "sponsor": "CISO · CFO co-sponsor",
            "owner": "GRC Director · L. Torres",
            "status": "Board review — Q4",
            "next_gate": "Board capital committee 2026-10-15",
            "budget_request_y1": 815_000,
            "capex_pct": 55,
            "horizon_years": 3,
            "discount_rate": 0.10,
            "summary": "Replace spreadsheet GRC + consultant-heavy audit prep with integrated controls, evidence, and workflow.",
            "linked": "CSF GAP-CSF-001 · Control Tracker · KRI-2026-012 · AST-2026-005",
            "so_what": "Audit prep still ~2,400 hours/year ($204K blended labor); three auditors flagged evidence gaps on IBM i and JD Edwards scopes last cycle.",
            "decision": "Fund Y1 implementation — CFO wants phased benefit recognition",
            "benefits": [
                {"category": "Labor / productivity", "y1": 180_000, "y2": 320_000, "y3": 380_000, "driver": "70% test automation; attestation workflow"},
                {"category": "Audit & attestation efficiency", "y1": 90_000, "y2": 140_000, "y3": 155_000, "driver": "Evidence reuse SOC2+ISO; −45% external audit prep"},
                {"category": "Breach loss avoided (ALE reduction)", "y1": 50_000, "y2": 120_000, "y3": 150_000, "driver": "Faster control gap detection"},
                {"category": "Deal velocity & revenue enablement", "y1": 0, "y2": 200_000, "y3": 350_000, "driver": "Security questionnaire deflection"},
            ],
            "costs": [
                {"category": "Implementation & integration", "y1": 420_000, "y2": 80_000, "y3": 40_000},
                {"category": "Platform license / subscription", "y1": 120_000, "y2": 140_000, "y3": 155_000},
                {"category": "Internal FTE (program)", "y1": 95_000, "y2": 110_000, "y3": 115_000},
                {"category": "External consultants", "y1": 180_000, "y2": 60_000, "y3": 25_000},
            ],
            "fair": {
                "asset_value": 4_200_000,
                "exposure_pct": 35,
                "aro_before": 0.45,
                "control_effectiveness_pct": 40,
                "annual_control_cost": 375_000,
                "scenario": "Enterprise GRC — operational risk register + evidence",
            },
            "risks": [
                "Adoption drag in IT and Engineering — benefits back-loaded",
                "Integration to IBM i / JD Edwards evidence feeds underestimated",
                "Audit firm may not accept all automated evidence first cycle",
            ],
        },
        {
            "init_id": "INV-ROI-002",
            "name": "Crown-jewel coverage & CAASM program",
            "sponsor": "CISO",
            "owner": "CAASM lead · D. Okonkwo",
            "status": "Approved — in flight",
            "next_gate": "Coverage attestation to board 2026-09-28",
            "budget_request_y1": 360_000,
            "capex_pct": 40,
            "horizon_years": 3,
            "discount_rate": 0.12,
            "summary": "Close GAP-2026-001 after portal stuffing — EDR+SIEM+backup on 100% crown jewels, not vanity agent counts.",
            "linked": "GAP-2026-001 · KRI-2026-001 · INC-2026-001 · AST-2026-005 · JUMP-DMZ-03",
            "so_what": "KRI-2026-001 at 86% vs 98% target; 14% crown jewels missing SIEM+backup combo — includes PayrollCo-adjacent payroll LPAR.",
            "decision": "Remediate now — no defer past Q4 board",
            "benefits": [
                {"category": "Breach loss avoided (ALE reduction)", "y1": 280_000, "y2": 420_000, "y3": 450_000, "driver": "ALE ↓ from $1.1M → $0.55M (modeled)"},
                {"category": "Labor / productivity", "y1": 40_000, "y2": 85_000, "y3": 95_000, "driver": "CAASM replaces manual CMDB reconciliations"},
                {"category": "Insurance premium reduction", "y1": 0, "y2": 45_000, "y3": 60_000, "driver": "Broker re-rate after verified coverage"},
            ],
            "costs": [
                {"category": "Platform license / subscription", "y1": 95_000, "y2": 110_000, "y3": 115_000},
                {"category": "Implementation & integration", "y1": 160_000, "y2": 45_000, "y3": 20_000},
                {"category": "Internal FTE (program)", "y1": 75_000, "y2": 80_000, "y3": 82_000},
                {"category": "Ongoing operations", "y1": 30_000, "y2": 35_000, "y3": 38_000},
            ],
            "fair": {
                "asset_value": 8_500_000,
                "exposure_pct": 28,
                "aro_before": 0.35,
                "control_effectiveness_pct": 55,
                "annual_control_cost": 280_000,
                "scenario": "Crown-jewel outage / exfiltration",
            },
            "risks": ["PayrollCo processor assets out of scope until IR lifts", "JUMP-DMZ-03 SIEM delay"],
        },
        {
            "init_id": "INV-ROI-003",
            "name": "TPRM uplift — PayrollCo & Tier-1 suppliers",
            "sponsor": "CISO + Procurement",
            "owner": "TPRM · S. Nguyen",
            "status": "CFO challenge — need ROSI",
            "next_gate": "CFO 1:1 review 2026-09-12",
            "budget_request_y1": 250_000,
            "capex_pct": 25,
            "horizon_years": 3,
            "discount_rate": 0.10,
            "summary": "Continuous monitoring + tiering after INC-2026-009 — ALE reduction narrative for CFO.",
            "linked": "INC-2026-009 · CMP-2026-004 · GAP-CSF-006 · DST-2026-001",
            "so_what": "Processor backup attestation expired mid-IR; Orbit AMS onboarded without tier refresh — Legal wants contract language before continuous monitoring.",
            "decision": "Approve if ROSI > 150% and Y1 benefits ≤ 40% of total",
            "benefits": [
                {"category": "Vendor / incident cost avoidance", "y1": 150_000, "y2": 320_000, "y3": 380_000, "driver": "Processor incident frequency ↓; faster attestations"},
                {"category": "Breach loss avoided (ALE reduction)", "y1": 200_000, "y2": 350_000, "y3": 400_000, "driver": "ALE €6.2M → €2.4M pattern (scaled)"},
                {"category": "Regulatory fine avoidance", "y1": 0, "y2": 100_000, "y3": 120_000, "driver": "DORA/NIS2 evidence trail"},
            ],
            "costs": [
                {"category": "Platform license / subscription", "y1": 85_000, "y2": 95_000, "y3": 100_000},
                {"category": "Implementation & integration", "y1": 70_000, "y2": 25_000, "y3": 15_000},
                {"category": "Internal FTE (program)", "y1": 55_000, "y2": 60_000, "y3": 62_000},
                {"category": "External consultants", "y1": 40_000, "y2": 20_000, "y3": 10_000},
            ],
            "fair": {
                "asset_value": 6_200_000,
                "exposure_pct": 40,
                "aro_before": 0.25,
                "control_effectiveness_pct": 61,
                "annual_control_cost": 180_000,
                "scenario": "Tier-1 supplier cyber failure",
            },
            "risks": ["Supplier assessment fatigue", "Legal pushback on continuous monitoring clauses"],
        },
        {
            "init_id": "INV-ROI-004",
            "name": "SOC 2 Type II acceleration",
            "sponsor": "CRO + CISO",
            "owner": "GRC · audit lead",
            "status": "Pipeline enablement",
            "next_gate": "RevOps pipeline review 2026-09-20",
            "budget_request_y1": 245_000,
            "capex_pct": 15,
            "horizon_years": 3,
            "discount_rate": 0.10,
            "summary": "Compress audit cycle; reduce questionnaire drag for enterprise deals.",
            "linked": "Control Testing · Privacy PB-2026-002",
            "so_what": "Deals AcmeCorp ($1.2M ARR) and NorthStack ($800K) stalled on security review — questionnaire backlog 23 days avg.",
            "decision": "Monitor",
            "benefits": [
                {"category": "Deal velocity & revenue enablement", "y1": 250_000, "y2": 400_000, "y3": 420_000},
                {"category": "Audit & attestation efficiency", "y1": 60_000, "y2": 90_000, "y3": 95_000},
                {"category": "Labor / productivity", "y1": 45_000, "y2": 70_000, "y3": 75_000},
            ],
            "costs": [
                {"category": "Audit & certification fees", "y1": 55_000, "y2": 58_000, "y3": 60_000},
                {"category": "External consultants", "y1": 90_000, "y2": 40_000, "y3": 25_000},
                {"category": "Internal FTE (program)", "y1": 65_000, "y2": 70_000, "y3": 72_000},
                {"category": "Platform license / subscription", "y1": 35_000, "y2": 40_000, "y3": 42_000},
            ],
            "fair": None,
            "risks": ["Scope creep on TSC criteria", "Engineering resistance to change freezes"],
        },
        {
            "init_id": "INV-ROI-005",
            "name": "Human-risk / phishing reporting program",
            "sponsor": "CISO",
            "owner": "Awareness · L. Torres",
            "status": "Funded via CMP-2026-001",
            "next_gate": "Board metrics close-out WAV-2026-019",
            "budget_request_y1": 95_000,
            "capex_pct": 5,
            "horizon_years": 3,
            "discount_rate": 0.10,
            "summary": "Incident-driven reporting reinforcement — reduce helpdesk misroutes and stuffing repeat.",
            "linked": "CMP-2026-001 · INC-2026-001 · PHISH-2026-003",
            "so_what": "340 users forwarded portal-stuffing mail to helpdesk; KRI-2026-002 MTTD 18.4h vs 8h target — helpdesk flood not in IR playbook.",
            "decision": "Continue sustain phase",
            "benefits": [
                {"category": "Breach loss avoided (ALE reduction)", "y1": 120_000, "y2": 180_000, "y3": 200_000},
                {"category": "Labor / productivity", "y1": 35_000, "y2": 55_000, "y3": 60_000, "driver": "Helpdesk triage hours ↓"},
            ],
            "costs": [
                {"category": "Ongoing operations", "y1": 45_000, "y2": 48_000, "y3": 50_000},
                {"category": "Platform license / subscription", "y1": 28_000, "y2": 30_000, "y3": 32_000},
                {"category": "Internal FTE (program)", "y1": 22_000, "y2": 24_000, "y3": 25_000},
            ],
            "fair": {
                "asset_value": 1_800_000,
                "exposure_pct": 55,
                "aro_before": 0.8,
                "control_effectiveness_pct": 35,
                "annual_control_cost": 95_000,
                "scenario": "Credential phishing → portal access",
            },
            "risks": ["Message collision with PayrollCo IR comms"],
        },
    ]

    init_df = pd.DataFrame(initiatives)

    benefit_rows, cost_rows = [], []
    for inv in initiatives:
        for b in inv["benefits"]:
            benefit_rows.append({"init_id": inv["init_id"], **b})
        for c in inv["costs"]:
            cost_rows.append({"init_id": inv["init_id"], **c})

    benefits_df = pd.DataFrame(benefit_rows)
    costs_df = pd.DataFrame(cost_rows)

    narrative = pd.DataFrame(
        [
            {
                "lane": "FY26 envelope",
                "text": "Security program cap $4.2M OPEX (+$600K board exception). Five initiatives below compete — CFO will not fund all Y1 asks ($1.77M combined).",
            },
            {
                "lane": "CFO framing",
                "text": "NPV alone is insufficient — show payback months, phased benefits, and ALE before/after. Revenue benefits need RevOps sign-off (INV-ROI-004).",
            },
            {
                "lane": "Portfolio context",
                "text": "Numbers trace to INC-2026-001/009, GAP-2026-001, KRI-2026-001/002 — crown-jewel and TPRM cases are incident-shaped, not template SOC 2 math.",
            },
            {
                "lane": "What wins funding",
                "text": "INV-ROI-002 approved (board mandate). INV-ROI-003 blocked on Legal + benefit timing. INV-ROI-001 waits on IBM i evidence connector quote.",
            },
            {
                "lane": "Sensitivity",
                "text": "Models break if Y1 realizes 100% of labor savings — GRC adoption historically 18-month curve here.",
            },
        ]
    )

    assumptions = pd.DataFrame(
        [
            {"assumption_id": "ASM-001", "init_id": "INV-ROI-001", "topic": "Audit labor baseline", "value": "2,400 hrs × $85 blended", "confidence": "High", "source": "GRC time study Aug 2026", "owner": "Internal Audit liaison"},
            {"assumption_id": "ASM-002", "init_id": "INV-ROI-001", "topic": "Test automation Y1", "value": "35% (not 70%)", "confidence": "Medium", "source": "Vendor SOW draft", "owner": "GRC Director"},
            {"assumption_id": "ASM-003", "init_id": "INV-ROI-001", "topic": "Revenue benefit", "value": "$0 Y1 — deferred Y2+", "confidence": "Medium", "source": "CFO edict", "owner": "CFO office"},
            {"assumption_id": "ASM-004", "init_id": "INV-ROI-002", "topic": "Crown-jewel count", "value": "42 assets (CMDB disputed)", "confidence": "Low", "source": "GAP-2026-001 workshop", "owner": "CAASM"},
            {"assumption_id": "ASM-005", "init_id": "INV-ROI-002", "topic": "ALE reduction", "value": "50% by Y3", "confidence": "Medium", "source": "FAIR workshop", "owner": "Risk"},
            {"assumption_id": "ASM-006", "init_id": "INV-ROI-003", "topic": "PayrollCo in scope", "value": "Phase 2 only (post-IR)", "confidence": "High", "source": "Legal / IR", "owner": "TPRM"},
            {"assumption_id": "ASM-007", "init_id": "INV-ROI-003", "topic": "ROSI hurdle", "value": ">150%", "confidence": "High", "source": "CFO email 2026-08-22", "owner": "CFO"},
            {"assumption_id": "ASM-008", "init_id": "INV-ROI-004", "topic": "Deal pull-forward", "value": "AcmeCorp + NorthStack only", "confidence": "Medium", "source": "RevOps", "owner": "CRO office"},
            {"assumption_id": "ASM-009", "init_id": "INV-ROI-005", "topic": "Helpdesk misroute reduction", "value": "40% by Y2", "confidence": "Medium", "source": "CMP-2026-001 KPI CKPI-002", "owner": "Awareness"},
            {"assumption_id": "ASM-010", "init_id": "INV-ROI-005", "topic": "ALE tie to phishing", "value": "Credential → portal path", "confidence": "Medium", "source": "INC-2026-001 lesson learned", "owner": "IR Lead"},
        ]
    )

    fte_models = pd.DataFrame(
        [
            {"init_id": "INV-ROI-001", "role": "GRC analysts", "hours_yr": 1200, "rate": 85, "automation_pct_y3": 70, "notes": "Control testing + evidence"},
            {"init_id": "INV-ROI-001", "role": "IT control owners", "hours_yr": 800, "rate": 95, "automation_pct_y3": 45, "notes": "Attestation chase"},
            {"init_id": "INV-ROI-001", "role": "External audit support", "hours_yr": 400, "rate": 220, "automation_pct_y3": 50, "notes": "PBC preparation"},
            {"init_id": "INV-ROI-002", "role": "CAASM / asset analysts", "hours_yr": 520, "rate": 90, "automation_pct_y3": 80, "notes": "Manual reconciliations today"},
            {"init_id": "INV-ROI-002", "role": "SOC enrichment", "hours_yr": 180, "rate": 105, "automation_pct_y3": 30, "notes": "Crown-jewel alert tuning"},
            {"init_id": "INV-ROI-003", "role": "TPRM analysts", "hours_yr": 960, "rate": 88, "automation_pct_y3": 55, "notes": "Questionnaires + tiering"},
            {"init_id": "INV-ROI-003", "role": "Procurement legal review", "hours_yr": 120, "rate": 175, "automation_pct_y3": 20, "notes": "Contract clause fights"},
            {"init_id": "INV-ROI-005", "role": "Helpdesk L1", "hours_yr": 640, "rate": 42, "automation_pct_y3": 35, "notes": "'Is this phishing?' tickets"},
            {"init_id": "INV-ROI-005", "role": "SOC triage", "hours_yr": 220, "rate": 105, "automation_pct_y3": 25, "notes": "Misrouted forwards"},
        ]
    )
    fte_models["labor_baseline"] = fte_models["hours_yr"] * fte_models["rate"]

    cfo_log = pd.DataFrame(
        [
            {"date": today - timedelta(days=18), "init_id": "INV-ROI-001", "question": "Why $420K implementation in Y1 when we already pay for a GRC license?", "response": "License is read-only archive — workflow + IBM i connector is net-new SOW", "status": "Open"},
            {"date": today - timedelta(days=14), "init_id": "INV-ROI-003", "question": "Show me ROSI, not NPV — processor risk is the board story", "response": "ALE $1.55M → $605K modeled; ROSI 187% at 61% effectiveness", "status": "In review"},
            {"date": today - timedelta(days=9), "init_id": "INV-ROI-004", "question": "RevOps won't sign $250K Y1 revenue benefit without closed-won proof", "response": "Scenario uses pipeline stage 4 only — sensitivity tab", "status": "Blocked"},
            {"date": today - timedelta(days=5), "init_id": "INV-ROI-002", "question": "Can we defer JUMP-DMZ-03 SIEM to Q1?", "response": "No — on KRI-2026-001 slide for Sept board", "status": "Closed"},
            {"date": today - timedelta(days=2), "init_id": "INV-ROI-005", "question": "Isn't this duplicate of campaign spend?", "response": "Campaign is comms; this line is SAT platform + helpdesk workflow", "status": "Closed"},
        ]
    )

    funding_gates = pd.DataFrame(
        [
            {"gate_id": "GATE-01", "init_id": "INV-ROI-001", "name": "IBM i evidence connector POC", "due": today + timedelta(days=21), "status": "In progress", "blocker": "JD Edwards CNC read-only API pending"},
            {"gate_id": "GATE-02", "init_id": "INV-ROI-001", "name": "Board capital committee", "due": today + timedelta(days=45), "status": "Scheduled", "blocker": "—"},
            {"gate_id": "GATE-03", "init_id": "INV-ROI-002", "name": "Crown-jewel CMDB reconcile", "due": today + timedelta(days=14), "status": "At risk", "blocker": "GAP-2026-001 owner dispute"},
            {"gate_id": "GATE-04", "init_id": "INV-ROI-002", "name": "SIEM on JUMP-DMZ-03", "due": today + timedelta(days=10), "status": "In progress", "blocker": "Change freeze exception filed"},
            {"gate_id": "GATE-05", "init_id": "INV-ROI-003", "name": "Legal — continuous monitoring clause", "due": today + timedelta(days=28), "status": "Blocked", "blocker": "PayrollCo IR"},
            {"gate_id": "GATE-06", "init_id": "INV-ROI-003", "name": "CFO ROSI sign-off", "due": today + timedelta(days=12), "status": "Scheduled", "blocker": "—"},
            {"gate_id": "GATE-07", "init_id": "INV-ROI-005", "name": "Board close-out metrics", "due": today + timedelta(days=12), "status": "Planned", "blocker": "WAV-2026-019 draft"},
        ]
    )

    actuals = []
    for inv in initiatives:
        iid = inv["init_id"]
        plan_y1_cost = sum(c["y1"] for c in inv["costs"])
        plan_y1_ben = sum(b["y1"] for b in inv["benefits"])
        for mo in range(1, 9):
            pct = mo / 12
            noise = float(rng.uniform(0.85, 1.15))
            actuals.append(
                {
                    "init_id": iid,
                    "month": today.replace(day=1) - timedelta(days=30 * (8 - mo)),
                    "plan_cost_mtd": plan_y1_cost / 12,
                    "actual_cost_mtd": (plan_y1_cost / 12) * pct * noise * (1.12 if iid == "INV-ROI-002" else 1.0),
                    "plan_benefit_mtd": plan_y1_ben / 12,
                    "actual_benefit_mtd": (plan_y1_ben / 12) * max(0, pct - 0.15) * noise,
                }
            )
    actuals_df = pd.DataFrame(actuals)

    deep = {
        "INV-ROI-001": {
            "memo": "Board asked for single GRC source of truth after INC cluster. Finance will not count revenue benefits until RevOps attributes a win — model already reflects $0 Y1.",
            "counterfactual": "Status quo: 2,400 audit hours, 3 parallel spreadsheet registers, $180K/yr consultants for SOC 2 + ISO evidence alone.",
            "milestones": [
                {"when": "2026-10", "what": "IBM i / JDE connector POC complete"},
                {"when": "2026-11", "what": "Control library migrated (wave 1 — ITGC)"},
                {"when": "2027-03", "what": "First audit cycle on automated evidence"},
            ],
            "deferred": "De-scoped: HR onboarding workflow — belongs in HRIS module, not this SOW.",
        },
        "INV-ROI-002": {
            "memo": "This is the board-mandated line item — not negotiable for Sept packet. PayrollCo assets stay out of phase 1 per Legal.",
            "counterfactual": "Without program: KRI-2026-001 stays red; cyber insurance renewal cites 'immature CAASM' — modeled $60K premium at risk.",
            "milestones": [
                {"when": "2026-09", "what": "JUMP-DMZ-03 SIEM + backup verify"},
                {"when": "2026-10", "what": "CMDB ↔ crown-jewel reconcile sign-off"},
                {"when": "2026-12", "what": "Broker re-rate submission"},
            ],
            "deferred": "Remote warehouse tape room — Facilities PO-4481 slip 3 weeks.",
        },
        "INV-ROI-003": {
            "memo": "CFO wants ROSI > 150%. Strong on paper (187% at base) but Y1 benefits are thin until PayrollCo assessments resume.",
            "counterfactual": "Orbit AMS onboarded with spreadsheet tiering — audit finding likely on supplier criticality.",
            "milestones": [
                {"when": "2026-09", "what": "CFO review with FAIR deck"},
                {"when": "2026-10", "what": "Tier-1 monitoring live (ex-PayrollCo)"},
                {"when": "2027-01", "what": "PayrollCo phase 2 if IR lifted"},
            ],
            "deferred": "Continuous monitoring clause — Legal redline with PayrollCo counsel.",
        },
        "INV-ROI-005": {
            "memo": "Funded through campaign CMP-2026-001 — separate ROI case proves helpdesk/SOC hour savings beyond comms spend.",
            "counterfactual": "340-forward incident repeats without workflow change — modeled $120K Y1 ALE component.",
            "milestones": [
                {"when": "2026-09", "what": "Helpdesk auto-reply → report hub"},
                {"when": "2026-10", "what": "IR playbook add mass-forward scenario"},
            ],
            "deferred": "None — sustain phase active.",
        },
    }

    budget_envelope = {
        "fy": "FY26",
        "opex_cap": 4_200_000,
        "exception": 600_000,
        "committed": 1_150_000,
        "requested_y1": sum(i.get("budget_request_y1", 0) for i in initiatives),
        "owner": "CFO · CISO joint",
    }

    # Benchmark TEI composites (public study ranges, demo labels only)
    benchmarks = pd.DataFrame(
        [
            {"study": "GRC platform (composite)", "roi_3yr_pct": 210, "npv_usd": 711_000, "payback_mo": 14},
            {"study": "Cloud security CNAPP (composite)", "roi_3yr_pct": 176, "npv_usd": 1_300_000, "payback_mo": 11},
            {"study": "Compliance automation (composite)", "roi_3yr_pct": 155, "npv_usd": 520_000, "payback_mo": 18},
        ]
    )

    return init_df, benefits_df, costs_df, narrative, benchmarks, assumptions, fte_models, cfo_log, funding_gates, actuals_df, deep, budget_envelope


def _initiative_detail(init: dict, benefits: pd.DataFrame, costs: pd.DataFrame) -> dict:
    b = benefits[benefits["init_id"] == init["init_id"]]
    c = costs[costs["init_id"] == init["init_id"]]
    tei = _tei_from_streams(b, c, discount_rate=init["discount_rate"], horizon=init["horizon_years"])
    fair_out = None
    if init.get("fair"):
        f = init["fair"]
        _, ale_b = _fair_ale(f["asset_value"], f["exposure_pct"], f["aro_before"])
        eff = f["control_effectiveness_pct"] / 100
        ale_a = ale_b * (1 - eff)
        fair_out = _rosi(ale_b, ale_a, f["annual_control_cost"])
        fair_out["sle"], _ = _fair_ale(f["asset_value"], f["exposure_pct"], 1.0)
        fair_out["scenario"] = f.get("scenario", "")
    return {"tei": tei, "fair": fair_out}


def _sync(seed: int):
    need = st.session_state.get(_SYNC_KEY) != seed or "roi_initiatives" not in st.session_state
    if need:
        i, b, c, n, bench, asm, fte, cfo, gates, act, deep, env = _sample(seed)
        st.session_state.roi_initiatives = i
        st.session_state.roi_benefits = b
        st.session_state.roi_costs = c
        st.session_state.roi_narrative = n
        st.session_state.roi_benchmarks = bench
        st.session_state.roi_assumptions = asm
        st.session_state.roi_fte = fte
        st.session_state.roi_cfo_log = cfo
        st.session_state.roi_gates = gates
        st.session_state.roi_actuals = act
        st.session_state.roi_deep = deep
        st.session_state.roi_envelope = env
        st.session_state.roi_active = "INV-ROI-001"
        st.session_state[_SYNC_KEY] = seed
    return (
        st.session_state.roi_initiatives,
        st.session_state.roi_benefits,
        st.session_state.roi_costs,
        st.session_state.roi_narrative,
        st.session_state.roi_benchmarks,
        st.session_state.roi_assumptions,
        st.session_state.roi_fte,
        st.session_state.roi_cfo_log,
        st.session_state.roi_gates,
        st.session_state.roi_actuals,
        st.session_state.roi_deep,
        st.session_state.roi_envelope,
    )


def _fmt_money(v: float) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    sign = "-" if v < 0 else ""
    av = abs(v)
    if av >= 1_000_000:
        return f"{sign}${av/1_000_000:.2f}M"
    if av >= 1_000:
        return f"{sign}${av/1_000:.0f}K"
    return f"{sign}${av:,.0f}"


def _waterfall_chart(tei: dict, *, key: str):
    years = tei["years"]
    labels = [f"Y{y} benefits" for y in years] + [f"Y{y} costs" for y in years] + ["NPV net"]
    measures = ["relative"] * (len(years) * 2) + ["total"]
    values = tei["benefits_by_year"] + [-c for c in tei["costs_by_year"]] + [tei["npv_net"]]
    fig = go.Figure(
        go.Waterfall(
            x=labels,
            y=values,
            measure=measures,
            connector={"line": {"color": "#38e881"}},
            increasing={"marker": {"color": "#22c55e"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#6366f1"}},
        )
    )
    fig.update_layout(title="3-year cash flow waterfall (undiscounted streams → NPV net)", height=400)
    st.plotly_chart(fig, use_container_width=True, key=key)


def _cashflow_chart(tei: dict, *, key: str):
    df = pd.DataFrame(
        {
            "Year": [f"Y{y}" for y in tei["years"]],
            "Benefits": tei["benefits_by_year"],
            "Costs": tei["costs_by_year"],
            "Net": tei["net_by_year"],
            "Cumulative": tei["cumulative_net"],
        }
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df["Year"], y=df["Benefits"], name="Benefits", marker_color="#22c55e"), secondary_y=False)
    fig.add_trace(go.Bar(x=df["Year"], y=df["Costs"], name="Costs", marker_color="#ef4444"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Year"], y=df["Cumulative"], name="Cumulative net", mode="lines+markers", line_color="#38e881"), secondary_y=True)
    fig.update_layout(title="Annual benefits vs costs + cumulative net", height=380, barmode="group")
    st.plotly_chart(fig, use_container_width=True, key=key)



def _fmt_date(ts) -> str:
    if ts is None:
        return "—"
    try:
        return pd.Timestamp(ts).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "—"


def _initiative_deep(init_id: str, deep: dict, assumptions: pd.DataFrame, fte: pd.DataFrame, gates: pd.DataFrame, actuals: pd.DataFrame, *, widget_key: str):
    if init_id not in deep:
        return
    pack = deep[init_id]
    st.markdown("**Program memo**")
    st.write(pack.get("memo", ""))
    st.write(f"**Without investment:** {pack.get('counterfactual', '')}")
    if pack.get("deferred"):
        st.caption(f"Deferred / descoped: {pack['deferred']}")

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**Milestones**")
        for m in pack.get("milestones", []):
            st.write(f"- **{m['when']}** — {m['what']}")
    with m2:
        g = gates[gates["init_id"] == init_id]
        if not g.empty:
            st.markdown("**Funding gates**")
            st.dataframe(g.assign(due=g["due"].map(_fmt_date)), use_container_width=True, hide_index=True)

    asm = assumptions[assumptions["init_id"] == init_id]
    if not asm.empty:
        st.markdown("**Assumption register**")
        st.dataframe(asm, use_container_width=True, hide_index=True)

    ft = fte[fte["init_id"] == init_id]
    if not ft.empty:
        st.markdown("**FTE / labor model (benefit justification)**")
        show = ft.copy()
        show["labor_baseline"] = show["labor_baseline"].map(lambda x: f"${x:,.0f}")
        st.dataframe(show, use_container_width=True, hide_index=True)

    act = actuals[actuals["init_id"] == init_id].copy()
    if not act.empty:
        act["month"] = pd.to_datetime(act["month"])
        act["cum_plan_cost"] = act["plan_cost_mtd"].cumsum()
        act["cum_actual_cost"] = act["actual_cost_mtd"].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=act["month"], y=act["cum_plan_cost"], name="Plan cost (YTD)", line=dict(dash="dash")))
        fig.add_trace(go.Scatter(x=act["month"], y=act["cum_actual_cost"], name="Actual cost (YTD)"))
        fig.update_layout(title="YTD spend vs plan (synthetic actuals)", height=280)
        st.plotly_chart(fig, use_container_width=True, key=f"plotly_actuals_{widget_key}")


def _initiative_panel(init: dict, benefits: pd.DataFrame, costs: pd.DataFrame, *, widget_key: str, deep: dict | None = None, assumptions: pd.DataFrame | None = None, fte: pd.DataFrame | None = None, gates: pd.DataFrame | None = None, actuals: pd.DataFrame | None = None):
    detail = _initiative_detail(init, benefits, costs)
    tei = detail["tei"]
    fair = detail["fair"]
    wk = widget_key

    st.markdown(f"### {init['init_id']} · {init['name']}")
    st.caption(f"{init['summary']}")

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("3yr NPV (net)", _fmt_money(tei["npv_net"]))
    m2.metric("ROI (NPV basis)", f"{tei['roi_pct']:.0f}%")
    m3.metric("Benefit-cost", f"{tei['benefit_cost_ratio']:.2f}:1")
    payback = f"{tei['payback_months']:.0f} mo" if tei["payback_months"] else "—"
    m4.metric("Payback", payback)
    m5.metric("NPV benefits", _fmt_money(tei["npv_benefits"]))
    m6.metric("NPV costs", _fmt_money(tei["npv_costs"]))

    if fair:
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("ALE (before)", _fmt_money(fair["ale_before"]))
        f2.metric("ALE (after)", _fmt_money(fair["ale_after"]))
        f3.metric("ROSI", f"{fair['rosi_pct']:.0f}%")
        f4.metric("Loss avoided / yr", _fmt_money(fair["loss_avoided"]))

    c1, c2 = st.columns(2)
    c1.write(f"**Sponsor:** {init['sponsor']} · **Owner:** {init.get('owner', '—')}")
    c1.write(f"**Status:** {init['status']} · **Next gate:** {init.get('next_gate', '—')}")
    c1.write(f"**Y1 ask:** {_fmt_money(init.get('budget_request_y1', 0))} · **CapEx mix:** {init.get('capex_pct', '—')}%")
    c1.write(f"**Linked:** {init['linked']}")
    c1.write(f"**So what:** {init['so_what']}")
    c2.write(f"**Decision:** {init['decision']}")
    if init.get("risks"):
        c2.write("**Risks:** " + "; ".join(init["risks"][:2]))

    _cashflow_chart(tei, key=f"cf_{wk}")
    _waterfall_chart(tei, key=f"wf_{wk}")

    with st.expander("Benefit & cost line items", expanded=False):
        b1, b2 = st.columns(2)
        with b1:
            st.markdown("**Benefits by year**")
            st.dataframe(benefits[benefits["init_id"] == init["init_id"]], use_container_width=True, hide_index=True)
        with b2:
            st.markdown("**Costs by year**")
            st.dataframe(costs[costs["init_id"] == init["init_id"]], use_container_width=True, hide_index=True)

    if fair:
        with st.expander("FAIR / ROSI assumptions", expanded=False):
            st.write(f"**Scenario:** {fair.get('scenario', '')}")
            st.write(
                "SLE = asset × exposure; ALE = SLE × ARO; control effectiveness reduces ALE; "
                "ROSI = (loss avoided − annual cost) / annual cost."
            )

    if deep and init["init_id"] in deep:
        with st.expander("Program detail — memo, gates, FTE model", expanded=init["init_id"] in FEATURED):
            _initiative_deep(
                init["init_id"],
                deep,
                assumptions if assumptions is not None else pd.DataFrame(),
                fte if fte is not None else pd.DataFrame(),
                gates if gates is not None else pd.DataFrame(),
                actuals if actuals is not None else pd.DataFrame(),
                widget_key=f"deep_{widget_key}",
            )


def _sensitivity_tornado(init: dict, benefits: pd.DataFrame, costs: pd.DataFrame, *, key: str):
    base = _initiative_detail(init, benefits, costs)["tei"]["roi_pct"]
    rows = []
    for label, ben_mult, cost_mult in [
        ("Benefits −20%", 0.8, 1.0),
        ("Benefits −10%", 0.9, 1.0),
        ("Benefits +10%", 1.1, 1.0),
        ("Costs +10%", 1.0, 1.1),
        ("Costs +20%", 1.0, 1.2),
        ("Adoption lag (Y1 −30%)", None, 1.0),
    ]:
        b = benefits[benefits["init_id"] == init["init_id"]].copy()
        c = costs[costs["init_id"] == init["init_id"]].copy()
        if ben_mult is not None:
            for col in ["y1", "y2", "y3"]:
                if col in b.columns:
                    b[col] = b[col] * ben_mult
        if label.startswith("Adoption"):
            if "y1" in b.columns:
                b["y1"] = b["y1"] * 0.7
        else:
            for col in ["y1", "y2", "y3"]:
                if col in c.columns:
                    c[col] = c[col] * cost_mult
        roi = _initiative_detail(init, b, c)["tei"]["roi_pct"]
        rows.append({"Driver": label, "ROI %": roi, "Delta": roi - base})
    df = pd.DataFrame(rows).sort_values("ROI %")
    fig = px.bar(df, x="ROI %", y="Driver", orientation="h", title=f"Sensitivity vs base ROI {base:.0f}%")
    fig.add_vline(x=base, line_dash="dash", line_color="#38e881")
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True, key=key)


def main() -> None:
    portfolio_skin.page_header(
        title="Security & GRC Investment Business Case",
        lede="TEI-style 3-year NPV models, payback, and FAIR/ROSI risk math for control investments — board/CFO-ready framing with synthetic portfolio scenarios.",
        kicker="Business case · ROSI",
    )

    seed = demo_kit.seed_controls()
    (
        initiatives,
        benefits,
        costs,
        narrative,
        benchmarks,
        assumptions,
        fte_models,
        cfo_log,
        funding_gates,
        actuals,
        deep,
        envelope,
    ) = _sync(seed)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Model settings")
    active_id = st.sidebar.selectbox(
        "Active initiative",
        initiatives["init_id"].tolist(),
        index=max(0, initiatives["init_id"].tolist().index(st.session_state.get("roi_active", "INV-ROI-001"))),
        format_func=lambda x: f"{x} — {initiatives[initiatives['init_id']==x]['name'].iloc[0]}",
        key="roi_active_select",
    )
    st.session_state.roi_active = active_id
    discount_override = st.sidebar.slider("Discount rate (TEI)", 0.05, 0.18, 0.10, 0.01)
    st.sidebar.caption("Session-only override for active initiative NPV.")

    active = initiatives[initiatives["init_id"] == active_id].iloc[0].to_dict()
    active = {**active, "discount_rate": discount_override}
    detail = _initiative_detail(active, benefits, costs)
    tei = detail["tei"]

    portfolio_rows = []
    for _, row in initiatives.iterrows():
        d = _initiative_detail(row.to_dict(), benefits, costs)
        portfolio_rows.append(
            {
                "init_id": row["init_id"],
                "name": row["name"],
                "npv_net": d["tei"]["npv_net"],
                "roi_pct": d["tei"]["roi_pct"],
                "payback_mo": d["tei"]["payback_months"],
                "status": row["status"],
            }
        )
    portfolio = pd.DataFrame(portfolio_rows)

    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
    k1.metric("Portfolio initiatives", len(initiatives))
    k2.metric("Active NPV (net)", _fmt_money(tei["npv_net"]))
    k3.metric("FY26 Y1 asks", _fmt_money(envelope["requested_y1"]), delta=f"cap {_fmt_money(envelope['opex_cap'])}")
    k4.metric("Open CFO questions", int((cfo_log["status"] != "Closed").sum()))
    k5.metric("Gates at risk", int(funding_gates["status"].isin(["At risk", "Blocked"]).sum()))
    k6.metric("Positive NPV", int((portfolio["npv_net"] > 0).sum()))
    k7.metric("Discount rate", f"{discount_override*100:.0f}%")

    over_cap = envelope["requested_y1"] > envelope["opex_cap"] * 0.35
    if over_cap:
        st.warning(
            f"Combined Y1 asks ({_fmt_money(envelope['requested_y1'])}) exceed ~35% of program cap — CFO will force rank."
        )

    work, model, rosi_tab, flows, assumptions_tab, compare, sens, board, export = st.tabs(
        [
            "Workbench",
            "TEI model",
            "ROSI / FAIR",
            "Cash flows",
            "Assumptions",
            "Compare",
            "Sensitivity",
            "Board brief",
            "Export",
        ]
    )

    with work:
        st.subheader("Investment workbench")

        e1, e2, e3, e4 = st.columns(4)
        e1.metric("FY26 OPEX cap", _fmt_money(envelope["opex_cap"]))
        e2.metric("Board exception", _fmt_money(envelope["exception"]))
        e3.metric("Already committed", _fmt_money(envelope["committed"]))
        e4.metric("Unallocated", _fmt_money(envelope["opex_cap"] - envelope["committed"]))

        st.markdown("**Executive narrative**")
        for _, n in narrative.iterrows():
            st.write(f"**{n['lane']}:** {n['text']}")

        st.markdown("---")
        st.markdown("**CFO challenge log**")
        for _, row in cfo_log.sort_values("date", ascending=False).iterrows():
            flag = "" if row["status"] == "Closed" else f" · **{row['status']}**"
            q_short = row["question"] if len(row["question"]) <= 60 else row["question"][:60] + "…"
            with st.expander(f"{_fmt_date(row['date'])} · {row['init_id']} · {q_short}{flag}"):
                st.write(f"**Question:** {row['question']}")
                st.write(f"**Response:** {row['response']}")

        st.markdown("---")
        st.markdown("**Funding gates (next 45 days)**")
        soon = funding_gates[funding_gates["due"] <= _today() + timedelta(days=45)].sort_values("due")
        st.dataframe(
            soon.assign(due=soon["due"].map(_fmt_date)),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        st.markdown(f"**Featured initiatives ({len(FEATURED)})**")
        pref = ["INV-ROI-001", "INV-ROI-002", "INV-ROI-003", "INV-ROI-005"]
        for iid in pref:
            if iid not in FEATURED:
                continue
            inv = initiatives[initiatives["init_id"] == iid].iloc[0].to_dict()
            st.markdown("---")
            _initiative_panel(
                inv,
                benefits,
                costs,
                widget_key=f"feat_{iid}",
                deep=deep,
                assumptions=assumptions,
                fte=fte_models,
                gates=funding_gates,
                actuals=actuals,
            )

        st.markdown("---")
        st.markdown("**Portfolio ranking (NPV net)**")
        rank = portfolio.sort_values("npv_net", ascending=False)
        fig = px.bar(rank, x="init_id", y="npv_net", color="npv_net", title="Initiative NPV comparison")
        fig.update_layout(showlegend=False, height=320)
        st.plotly_chart(fig, use_container_width=True, key="plotly_portfolio_npv")

    with model:
        st.subheader("TEI model — active initiative")
        st.caption("Benefits and costs by year. NPV uses sidebar discount rate.")

        inv = active
        b = benefits[benefits["init_id"] == active_id].copy()
        c = costs[costs["init_id"] == active_id].copy()

        st.markdown(f"**{inv['name']}** — {inv['summary']}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Benefit streams**")
            for i, row in b.iterrows():
                st.number_input(
                    f"{row['category']} Y1",
                    value=int(row["y1"]),
                    step=10_000,
                    key=f"ben_y1_{active_id}_{i}",
                    disabled=True,
                )
            st.caption("Enable workshop mode below to edit.")

        with col2:
            st.markdown("**Cost streams**")
            for i, row in c.iterrows():
                st.number_input(
                    f"{row['category']} Y1",
                    value=int(row["y1"]),
                    step=10_000,
                    key=f"cost_y1_{active_id}_{i}",
                    disabled=True,
                )

        workshop = st.checkbox("Workshop mode — edit Y1 benefit/cost totals (session)", key="roi_workshop")
        if workshop:
            ben_y1 = st.slider("Y1 total benefits", 0, 800_000, int(b["y1"].sum()), 10_000, key="roi_ben_y1")
            cost_y1 = st.slider("Y1 total costs", 0, 900_000, int(c["y1"].sum()), 10_000, key="roi_cost_y1")
            scale_b = ben_y1 / max(b["y1"].sum(), 1)
            scale_c = cost_y1 / max(c["y1"].sum(), 1)
            b_adj = b.copy()
            c_adj = c.copy()
            b_adj["y1"] = (b_adj["y1"] * scale_b).round(0)
            c_adj["y1"] = (c_adj["y1"] * scale_c).round(0)
            tei_adj = _tei_from_streams(b_adj, c_adj, discount_rate=discount_override)
            st.success(f"Adjusted Y1 → NPV net {_fmt_money(tei_adj['npv_net'])} · ROI {tei_adj['roi_pct']:.0f}%")

        st.markdown("**TEI element checklist**")
        tei_check = pd.DataFrame(
            [
                {"element": "Benefits", "modeled": "Yes", "notes": "Labor, audit, ALE, revenue, insurance, fines"},
                {"element": "Costs", "modeled": "Yes", "notes": "Implementation, license, FTE, consultants, audit"},
                {"element": "Flexibility", "modeled": "Partial", "notes": "Sensitivity tab — not real options pricing"},
                {"element": "Risks", "modeled": "Qualitative", "notes": "; ".join(inv.get("risks", [])[:3])},
            ]
        )
        st.dataframe(tei_check, use_container_width=True, hide_index=True)

    with rosi_tab:
        st.subheader("ROSI / FAIR — risk reduction lens")
        st.caption("ALE before vs after control investment. CFO compares loss avoided to program cost.")

        if not active.get("fair"):
            st.info("Active initiative has no FAIR scenario — select INV-ROI-001/002/003.")
        else:
            f = active["fair"]
            a1, a2, a3, a4 = st.columns(4)
            asset = a1.number_input("Asset value ($)", value=int(f["asset_value"]), step=100_000, key="fair_asset")
            exposure = a2.slider("Exposure factor (%)", 5, 90, int(f["exposure_pct"]), key="fair_exp")
            aro = a3.number_input("ARO (events/year)", value=float(f["aro_before"]), min_value=0.05, max_value=2.0, step=0.05, key="fair_aro")
            eff = a4.slider("Control effectiveness (%)", 10, 90, int(f["control_effectiveness_pct"]), key="fair_eff")
            annual_cost = st.number_input("Annual program cost ($)", value=int(f["annual_control_cost"]), step=10_000, key="fair_cost")

            sle, ale_b = _fair_ale(asset, exposure, aro)
            ale_a = ale_b * (1 - eff / 100)
            fair = _rosi(ale_b, ale_a, annual_cost)

            r1, r2, r3, r4, r5 = st.columns(5)
            r1.metric("SLE (single loss)", _fmt_money(sle))
            r2.metric("ALE before", _fmt_money(ale_b))
            r3.metric("ALE after", _fmt_money(ale_a))
            r4.metric("ROSI", f"{fair['rosi_pct']:.0f}%")
            r5.metric("Payback (yrs)", f"{fair['payback_years']:.1f}" if fair["payback_years"] else "—")

            st.markdown("**Cost of inaction vs invest**")
            inaction, invest = st.columns(2)
            inaction.error(f"Expected annual loss (status quo): **{_fmt_money(ale_b)}**")
            invest.success(f"After control: **{_fmt_money(ale_a)}** · Avoid **{_fmt_money(fair['loss_avoided'])}**/yr for **{_fmt_money(annual_cost)}** spend")

            loss_buckets = pd.DataFrame(
                [
                    {"bucket": "Productivity / downtime", "pct": 22},
                    {"bucket": "Response & forensics", "pct": 18},
                    {"bucket": "Regulatory fines", "pct": 15},
                    {"bucket": "Reputation / churn", "pct": 25},
                    {"bucket": "Replacement / recovery", "pct": 12},
                    {"bucket": "Competitive / IP loss", "pct": 8},
                ]
            )
            loss_buckets["estimated"] = loss_buckets["pct"] / 100 * sle
            fig = px.bar(loss_buckets, x="bucket", y="estimated", title="Illustrative SLE decomposition (FAIR buckets)")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True, key="plotly_fair_buckets")

    with flows:
        st.subheader("Cash flows — active initiative")
        _initiative_panel(
            active,
            benefits,
            costs,
            widget_key="flows_active",
            deep=deep,
            assumptions=assumptions,
            fte=fte_models,
            gates=funding_gates,
            actuals=actuals,
        )

    with assumptions_tab:
        st.subheader("Assumption register & labor models")
        st.caption("Every hard number should trace to an owner and confidence — CFO will challenge Low items first.")

        a_view = assumptions[assumptions["init_id"] == active_id] if active_id else assumptions
        st.markdown(f"**Active initiative ({active_id})**")
        st.dataframe(a_view, use_container_width=True, hide_index=True)

        st.markdown("**Full portfolio register**")
        st.dataframe(assumptions, use_container_width=True, hide_index=True)

        st.markdown("**FTE / labor baselines**")
        ft = fte_models.copy()
        ft["labor_baseline_fmt"] = ft["labor_baseline"].map(_fmt_money)
        st.dataframe(ft, use_container_width=True, hide_index=True)

        conf = assumptions.groupby("confidence").size().reset_index(name="count")
        fig = px.bar(conf, x="confidence", y="count", color="confidence", title="Assumptions by confidence")
        fig.update_layout(showlegend=False, height=280)
        st.plotly_chart(fig, use_container_width=True, key="plotly_asm_conf")

    with compare:
        st.subheader("Scenario comparison")
        cmp = portfolio.copy()
        cmp["npv_fmt"] = cmp["npv_net"].map(_fmt_money)
        cmp["payback_fmt"] = cmp["payback_mo"].apply(lambda x: f"{x:.0f} mo" if pd.notna(x) and x else "—")
        st.dataframe(
            cmp[["init_id", "name", "npv_fmt", "roi_pct", "payback_fmt", "status"]],
            use_container_width=True,
            hide_index=True,
        )

        fig = go.Figure()
        for _, row in initiatives.iterrows():
            d = _initiative_detail(row.to_dict(), benefits, costs)["tei"]
            fig.add_trace(
                go.Scatter(
                    x=[f"Y{y}" for y in d["years"]],
                    y=d["cumulative_net"],
                    mode="lines+markers",
                    name=row["init_id"],
                )
            )
        fig.update_layout(title="Cumulative net benefit by initiative", height=400)
        st.plotly_chart(fig, use_container_width=True, key="plotly_cumulative_compare")

        st.markdown("**Published composite benchmarks (demo reference ranges)**")
        st.dataframe(benchmarks, use_container_width=True, hide_index=True)

    with sens:
        st.subheader("Sensitivity — active initiative")
        _sensitivity_tornado(active, benefits, costs, key="plotly_tornado")

        st.markdown("**Discount rate sensitivity**")
        dr_rows = []
        for dr in [0.06, 0.08, 0.10, 0.12, 0.14, 0.16]:
            inv = {**active, "discount_rate": dr}
            t = _initiative_detail(inv, benefits, costs)["tei"]
            dr_rows.append({"discount_rate": f"{dr*100:.0f}%", "npv_net": t["npv_net"], "roi_pct": t["roi_pct"]})
        dr_df = pd.DataFrame(dr_rows)
        fig = px.line(dr_df, x="discount_rate", y="npv_net", markers=True, title="NPV vs discount rate")
        st.plotly_chart(fig, use_container_width=True, key="plotly_discount_sens")

    with board:
        st.subheader("Board / CFO brief — active initiative")
        st.markdown(f"**Initiative:** {active['name']} ({active_id})")
        payback_txt = (
            f"payback **{tei['payback_months']:.0f} months**"
            if tei["payback_months"]
            else "payback beyond model horizon"
        )
        st.markdown(
            f"Over {active['horizon_years']} years at **{discount_override*100:.0f}%** discount: "
            f"**NPV net {_fmt_money(tei['npv_net'])}**, **ROI {tei['roi_pct']:.0f}%**, {payback_txt}."
        )
        if detail["fair"]:
            fair = detail["fair"]
            st.markdown(
                f"**Risk lens:** ALE falls from {_fmt_money(fair['ale_before'])} to {_fmt_money(fair['ale_after'])} "
                f"(ROSI **{fair['rosi_pct']:.0f}%**)."
            )
        st.markdown(f"**So what:** {active['so_what']}")
        st.markdown(f"**Ask:** {active['decision']}")
        st.markdown("**Linked portfolio:** " + active["linked"])
        if active_id in deep:
            st.markdown(f"**Memo:** {deep[active_id].get('memo', '')}")
            st.markdown(f"**Counterfactual:** {deep[active_id].get('counterfactual', '')}")

        st.markdown("#### Open CFO questions")
        for _, row in cfo_log[cfo_log["init_id"] == active_id].iterrows():
            st.write(f"- ({_fmt_date(row['date'])}) {row['question']} → *{row['response']}* [{row['status']}]")

        st.markdown("#### Alternatives considered")
        alts = initiatives[initiatives["init_id"] != active_id].head(3)
        for _, a in alts.iterrows():
            d = _initiative_detail(a.to_dict(), benefits, costs)["tei"]
            st.write(f"- **{a['init_id']}** {a['name']}: NPV {_fmt_money(d['npv_net'])}")

    with export:
        st.subheader("Export")
        demo_kit.csv_download(portfolio, "roi_portfolio_summary.csv", label="Download portfolio summary")
        b_out = benefits.copy()
        c_out = costs.copy()
        demo_kit.csv_download(b_out, "roi_benefit_streams.csv", label="Download benefit streams")
        demo_kit.csv_download(c_out, "roi_cost_streams.csv", label="Download cost streams")
        demo_kit.csv_download(assumptions, "roi_assumptions.csv", label="Download assumption register")
        demo_kit.csv_download(cfo_log.assign(date=cfo_log["date"].map(_fmt_date)), "roi_cfo_log.csv", label="Download CFO challenge log")
        demo_kit.csv_download(funding_gates.assign(due=funding_gates["due"].map(_fmt_date)), "roi_funding_gates.csv", label="Download funding gates")

        active_export = pd.DataFrame(
            [
                {"metric": "init_id", "value": active_id},
                {"metric": "npv_net", "value": tei["npv_net"]},
                {"metric": "roi_pct", "value": tei["roi_pct"]},
                {"metric": "payback_months", "value": tei["payback_months"] or 0},
                {"metric": "discount_rate", "value": discount_override},
            ]
        )
        demo_kit.csv_download(active_export, "roi_active_summary.csv", label="Download active initiative summary")


if __name__ == "__main__":
    main()
