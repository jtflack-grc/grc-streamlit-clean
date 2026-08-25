#!/usr/bin/env python3
"""Data privacy program workbench — club teaching toy.

RoPA / Art. 30, DPIAs, rights requests, breach clocks, US state law,
GDPR, and NIS2-flavored obligations — educational / synthetic only.
"""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Data Privacy Management · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

LEGAL_BASES = [
    "Consent (Art. 6(1)(a))",
    "Contract (Art. 6(1)(b))",
    "Legal obligation (Art. 6(1)(c))",
    "Vital interests (Art. 6(1)(d))",
    "Public task (Art. 6(1)(e))",
    "Legitimate interests (Art. 6(1)(f))",
    "US — employment / contract",
    "US — legal obligation",
    "US — legitimate interest / business purpose (CPRA)",
]
ROLES = ["Controller", "Joint controller", "Processor", "Sub-processor"]
DSAR_TYPES = [
    "Access (Art. 15 / CPRA know)",
    "Rectification (Art. 16)",
    "Erasure (Art. 17 / delete)",
    "Restriction (Art. 18)",
    "Portability (Art. 20)",
    "Objection (Art. 21)",
    "Opt-out sale/share (CPRA)",
    "Limit sensitive use (CPRA)",
]
FEATURED_ROPA = {"ROPA-2026-001", "ROPA-2026-004", "ROPA-2026-006"}


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _now() -> pd.Timestamp:
    return pd.Timestamp.now()


def _sample(seed: int):
    today = _today()
    now = _now()
    rng = np.random.default_rng(seed)

    def j(lo: int, hi: int) -> int:
        return int(rng.integers(lo, hi))

    # ── RoPA / Art. 30 ───────────────────────────────────────────────
    ropa = [
        {
            "ropa_id": "ROPA-2026-001",
            "name": "Employee payroll & tax filing",
            "purpose": "Calculate and pay wages; withhold and file taxes; benefits deductions",
            "controller": "Acme Corp (US parent) — HR/Payroll",
            "joint_controller": "",
            "processor": "PayrollCo (VND-2026-001) under DPA-2024-019",
            "role_of_org": "Controller",
            "owner": "Payroll Ops · T. Williams",
            "dpo_contact": "dpo@acme.example · C. Hoffman (Legal)",
            "legal_basis": "Legal obligation (Art. 6(1)(c)) · US — legal obligation",
            "li_assessment": "",
            "categories_subjects": "Employees (1,820) · former employees in retention window",
            "categories_data": "Identity, SSN/national ID, bank routing/account, salary, tax, benefits",
            "special_category": "No (payroll) — health only if benefits vendor separate",
            "recipients": "PayrollCo · tax authorities · bank ACH · benefits carriers",
            "transfers": "DPF (US) · processor US; EU staff subset via SCCs addendum",
            "transfer_tool": "SCCs + DPF",
            "retention": "7 years post employment (tax) · bank details while employed + 90d",
            "security_measures": "SSO · API token rotation · DPA Art. 28 · encryption in transit",
            "systems": "AST-2026-012 PayrollCo · AST-2026-008 IdP · SFTP tax drop",
            "jurisdictions": "GDPR · UK GDPR · CCPA/CPRA workforce limited · NIS2 (HR essential-service adjacency)",
            "nis2_flag": True,
            "dpia_id": "DPIA-2026-002",
            "status": "Active — IR freeze",
            "last_review": today - timedelta(days=40),
            "next_review": today + timedelta(days=50),
            "risk_notes": "INC-2026-009: processor backup breach — processing suspended; Art. 33 clock on org if tenant confirmed.",
            "summary": "Crown-jewel processing. Art. 30 row must stay accurate through the PayrollCo incident — purpose, processor, transfers, and retention are the audit face of the activity.",
        },
        {
            "ropa_id": "ROPA-2026-002",
            "name": "Customer portal accounts & support",
            "purpose": "Provide authenticated customer self-service; support tickets; account prefs",
            "controller": "Acme Corp — Digital / CX",
            "joint_controller": "",
            "processor": "Azure AD B2C (VND-2026-004) · cloud host",
            "role_of_org": "Controller",
            "owner": "Platform Eng · R. Kim",
            "dpo_contact": "dpo@acme.example",
            "legal_basis": "Contract (Art. 6(1)(b))",
            "li_assessment": "",
            "categories_subjects": "B2C customers · trial users",
            "categories_data": "Email, display name, auth events, prefs, support content",
            "special_category": "No",
            "recipients": "Support tooling · IdP · marketing-DB (limited prefs)",
            "transfers": "DPF (US) for M365/Azure",
            "transfer_tool": "DPF (US)",
            "retention": "Account life + 2y activity logs",
            "security_measures": "WAF · MFA rollout · CAPTCHA/rate-limit post INC-2026-001",
            "systems": "AST-2026-007 portal · AST-2026-008 B2C · AST-2026-013 marketing-DB",
            "jurisdictions": "GDPR · CCPA/CPRA · state privacy",
            "nis2_flag": False,
            "dpia_id": "DPIA-2026-001",
            "status": "Active",
            "last_review": today - timedelta(days=20),
            "next_review": today + timedelta(days=160),
            "risk_notes": "Credential-stuffing INC-2026-001 — 340 emails exposed in scrape; Art. 33 done; state letters in flight.",
            "summary": "Core customer processing. RoPA updated after stuffing incident with security measures actually in force.",
        },
        {
            "ropa_id": "ROPA-2026-003",
            "name": "Order-to-cash / customer master (IBM i + JDE)",
            "purpose": "Process orders, invoices, customer master for B2B commerce",
            "controller": "Acme Corp — ERP Finance",
            "joint_controller": "",
            "processor": "Orbit AMS (VND-2026-003) — privileged ops under AMS MSA",
            "role_of_org": "Controller",
            "owner": "ERP Finance · M. Hassan",
            "dpo_contact": "dpo@acme.example",
            "legal_basis": "Contract (Art. 6(1)(b))",
            "li_assessment": "",
            "categories_subjects": "B2B customer contacts · shipping contacts",
            "categories_data": "Name, address, phone, account IDs, order history",
            "special_category": "No",
            "recipients": "Warehouse · carriers · SAP ECC · payment gateway",
            "transfers": "None for EU customers held in-region mirror; US primary",
            "transfer_tool": "None (EEA/UK only) for EU shard · else DPF",
            "retention": "FIN-RET-03 — 7y transactional; master until close + 7y",
            "security_measures": "PAM · QAUDJRN · AMS change control (IFS gap open)",
            "systems": "AST-2026-001 PRODBOX · AST-2026-006 JDE · AST-2026-004 SAP",
            "jurisdictions": "GDPR · SOX (financial) · state breach if personal",
            "nis2_flag": True,
            "dpia_id": "",
            "status": "Active",
            "last_review": today - timedelta(days=95),
            "next_review": today - timedelta(days=5),
            "risk_notes": "RoPA review overdue 5d. INC-2026-005 IFS exposure — verify categories still accurate.",
            "summary": "Legacy SoR processing. Art. 30 review clock slipped — classic RoPA hygiene failure under ops load.",
        },
        {
            "ropa_id": "ROPA-2026-004",
            "name": "CreditAssist AI scoring (decision support)",
            "purpose": "Assist analysts with credit score-band recommendation; human approves",
            "controller": "Acme Corp — Credit Risk",
            "joint_controller": "",
            "processor": "Cloud GPU training vendor (training only) · bureau licenses",
            "role_of_org": "Controller",
            "owner": "Credit Risk · AI product owner",
            "dpo_contact": "dpo@acme.example · MRM liaison",
            "legal_basis": "Contract (Art. 6(1)(b)) · Legitimate interests (Art. 6(1)(f)) for model improvement",
            "li_assessment": "LIA-2026-CA-01 — balancing test filed; opt-out not applicable to credit underwriting core",
            "categories_subjects": "Credit applicants (consumers / SMEs)",
            "categories_data": "Application attributes, bureau-derived features, outcomes, overrides",
            "special_category": "No — but high-risk profiling under DPIA / AI Act adjacency",
            "recipients": "Credit analysts · model registry · MRM · (no automated denial recipients)",
            "transfers": "Bureau US · model training region US",
            "transfer_tool": "SCCs + contractual bureau terms",
            "retention": "Scores 5y · training sets per MRM · features FS-RET-01",
            "security_measures": "Model card · drift/fairness monitors · access-controlled feature store",
            "systems": "AST-2026-017 CreditAssist · AST-2026-018 feature store",
            "jurisdictions": "GDPR Art. 22 adjacency · ISO 42001 · FCRA/ECOA (US) · CPRA automated decision notice",
            "nis2_flag": False,
            "dpia_id": "DPIA-2026-003",
            "status": "Active",
            "last_review": today - timedelta(days=14),
            "next_review": today + timedelta(days=170),
            "risk_notes": "DPIA complete — proceed with human oversight mandatory. No Art. 22 solely automated decision.",
            "summary": "AI processing on the RoPA. Intended use and prohibitions must match AST-2026-017 model CI — SoT consistency across privacy and asset inventory.",
        },
        {
            "ropa_id": "ROPA-2026-005",
            "name": "Marketing email & analytics",
            "purpose": "Send product updates and measure campaign engagement",
            "controller": "Acme Corp — Marketing",
            "joint_controller": "",
            "processor": "ESP vendor · analytics SDK",
            "role_of_org": "Controller",
            "owner": "Marketing Ops",
            "dpo_contact": "dpo@acme.example",
            "legal_basis": "Consent (Art. 6(1)(a)) · CPRA business purpose for limited analytics",
            "li_assessment": "",
            "categories_subjects": "Prospects · customers who opted in",
            "categories_data": "Email, engagement events, segment tags",
            "special_category": "No",
            "recipients": "ESP · analytics",
            "transfers": "DPF (US)",
            "transfer_tool": "DPF (US)",
            "retention": "2y from last engagement or until withdraw",
            "security_measures": "Consent log · suppression list · DSR delete cascade",
            "systems": "ESP · AST-2026-013 marketing-DB",
            "jurisdictions": "GDPR · ePrivacy · CCPA/CPRA · CAN-SPAM",
            "nis2_flag": False,
            "dpia_id": "",
            "status": "Active",
            "last_review": today - timedelta(days=60),
            "next_review": today + timedelta(days=120),
            "risk_notes": "Consent rate health OK; watch CPRA share/sale classification of ad pixels.",
            "summary": "Consent-based marketing — RoPA ties to suppression and DSAR delete path.",
        },
        {
            "ropa_id": "ROPA-2026-006",
            "name": "Privileged access & security monitoring",
            "purpose": "Authenticate admins; log privileged sessions; detect misuse; SIEM correlation",
            "controller": "Acme Corp — IT Security",
            "joint_controller": "",
            "processor": "EDR · SIEM · PAM vendors",
            "role_of_org": "Controller",
            "owner": "SecOps · Alex Rivera",
            "dpo_contact": "dpo@acme.example",
            "legal_basis": "Legitimate interests (Art. 6(1)(f)) · US — legitimate interest / security",
            "li_assessment": "LIA-2026-SEC-01 — security of processing; workforce notice in handbook",
            "categories_subjects": "Employees · contractors · vendor admins",
            "categories_data": "Usernames, source IP, session metadata, device IDs, alert context",
            "special_category": "No",
            "recipients": "IR team · forensic hold counsel · (lawful authority if compelled)",
            "transfers": "US SIEM region · EDR cloud",
            "transfer_tool": "SCCs / DPF as applicable per vendor",
            "retention": "Auth logs 1y · privileged session 1y · IR evidence per hold",
            "security_measures": "PAM · MFA · geo-block · jump hosts · need-to-know SIEM RBAC",
            "systems": "AST-2026-002 VPN · jumps · PAM · SIEM · EDR",
            "jurisdictions": "GDPR · NIS2 Art. logging/monitoring expectations · state privacy",
            "nis2_flag": True,
            "dpia_id": "DPIA-2026-004",
            "status": "Active",
            "last_review": today - timedelta(days=30),
            "next_review": today + timedelta(days=150),
            "risk_notes": "NIS2-relevant: essential-entity cybersecurity measures include monitoring — RoPA must reflect reality of jump/SIEM gaps (AST-2026-005).",
            "summary": "Security processing under LI. Featured because NIS2 and GDPR both care that monitoring is documented, proportionate, and actually covering privileged paths.",
        },
        {
            "ropa_id": "ROPA-2026-007",
            "name": "Settlement & ledger (IBM Z / CICS)",
            "purpose": "Execute and record financial settlement instructions",
            "controller": "Acme Corp — Treasury",
            "joint_controller": "",
            "processor": "NorthStack Colo (VND-2026-002) — hosting only",
            "role_of_org": "Controller",
            "owner": "Treasury · S. Okonkwo",
            "dpo_contact": "dpo@acme.example",
            "legal_basis": "Contract (Art. 6(1)(b)) · Legal obligation (Art. 6(1)(c))",
            "li_assessment": "",
            "categories_subjects": "Customers (account activity)",
            "categories_data": "Account IDs, balances, settlement instructions",
            "special_category": "No",
            "recipients": "Clearing partners · regulators (as required)",
            "transfers": "Limited — partner jurisdictions per settlement network",
            "transfer_tool": "Contractual + SCCs where personal",
            "retention": "FIN-RET-03 7y",
            "security_measures": "RACF · SMF · GDPS · colo physical",
            "systems": "AST-2026-003 · AST-2026-015",
            "jurisdictions": "GDPR · SOX · NIS2 (financial entity class candidate)",
            "nis2_flag": True,
            "dpia_id": "",
            "status": "Active",
            "last_review": today - timedelta(days=70),
            "next_review": today + timedelta(days=110),
            "risk_notes": "",
            "summary": "High-integrity financial processing — personal data limited but NIS2/cyber resilience still in frame.",
        },
        {
            "ropa_id": "ROPA-2026-008",
            "name": "Vendor / AMS privileged operations",
            "purpose": "Allow Orbit AMS to operate JDE/IFS under documented change control",
            "controller": "Acme Corp",
            "joint_controller": "",
            "processor": "Orbit AMS (VND-2026-003)",
            "role_of_org": "Controller",
            "owner": "TPRM · A. Nguyen",
            "dpo_contact": "dpo@acme.example",
            "legal_basis": "Legitimate interests (Art. 6(1)(f)) / Contract with customers (downstream)",
            "li_assessment": "Covered under ops LI + customer contracts",
            "categories_subjects": "Customer contacts residing in JDE (incidental access)",
            "categories_data": "As in ROPA-2026-003 — AMS has privileged path",
            "special_category": "No",
            "recipients": "Orbit AMS engineers · offshore L2 (sub-processor)",
            "transfers": "India L2 — SCCs required",
            "transfer_tool": "SCCs",
            "retention": "Ticket content per AMS MSA · access logs 1y",
            "security_measures": "PAM · named IDs · (SIG Lite insufficient — ISS TPRM open)",
            "systems": "AST-2026-001 · AST-2026-006",
            "jurisdictions": "GDPR Ch. V transfers · TPRM",
            "nis2_flag": True,
            "dpia_id": "",
            "status": "Active — remediation",
            "last_review": today - timedelta(days=50),
            "next_review": today + timedelta(days=40),
            "risk_notes": "Sub-processor notice stale; exit clause missing; IFS permission ops insufficient on questionnaire.",
            "summary": "Processor RoPA lens — Art. 28 + Ch. V transfers + sub-processors must be explicit.",
        },
    ]

    # ── DPIAs ────────────────────────────────────────────────────────
    dpias = [
        {
            "dpia_id": "DPIA-2026-001",
            "title": "Customer portal auth & profile (post-stuffing refresh)",
            "ropa_id": "ROPA-2026-002",
            "status": "Complete — proceed",
            "owner": "DPO / Platform",
            "started": today - timedelta(days=100),
            "completed": today - timedelta(days=25),
            "next_review": today + timedelta(days=340),
            "criteria": "Large-scale auth · account data · internet-facing",
            "risks": "Credential stuffing · scrape of email/display name · session takeover",
            "measures": "CAPTCHA · rate-limit · forced resets · WAF /api/* · MFA phased",
            "residual": "Medium",
            "consult_dpa": False,
            "notes": "Refreshed after INC-2026-001. Residual accepted with monitoring.",
        },
        {
            "dpia_id": "DPIA-2026-002",
            "title": "Payroll processor (PayrollCo) — Art. 28 + breach scenario",
            "ropa_id": "ROPA-2026-001",
            "status": "Overdue",
            "owner": "DPO / TPRM",
            "started": today - timedelta(days=200),
            "completed": pd.NaT,
            "next_review": today - timedelta(days=20),
            "criteria": "Special-adjacent financial ID · processor · large workforce",
            "risks": "Processor breach · backup-env gap · cross-border · pay disruption",
            "measures": "DPA · token rotation · suspend processing · manual BCP",
            "residual": "High (pending INC-2026-009)",
            "consult_dpa": False,
            "notes": "Annual DPIA refresh overdue — accelerate under active IR. May need Art. 33/34 path.",
        },
        {
            "dpia_id": "DPIA-2026-003",
            "title": "CreditAssist AI decision support",
            "ropa_id": "ROPA-2026-004",
            "status": "Complete — proceed",
            "owner": "DPO / MRM",
            "started": today - timedelta(days=120),
            "completed": today - timedelta(days=40),
            "next_review": today + timedelta(days=325),
            "criteria": "Profiling · credit · AI · systematic evaluation",
            "risks": "Bias · over-automation · feature leakage · opaque scoring",
            "measures": "Human-in-loop · prohibited autonomous denial · fairness/drift monitors · model card",
            "residual": "Medium",
            "consult_dpa": False,
            "notes": "Aligned to AST-2026-017. Art. 22 solely automated decision not used.",
        },
        {
            "dpia_id": "DPIA-2026-004",
            "title": "Privileged session monitoring & SIEM",
            "ropa_id": "ROPA-2026-006",
            "status": "Complete — proceed",
            "owner": "DPO / SecOps",
            "started": today - timedelta(days=80),
            "completed": today - timedelta(days=35),
            "next_review": today + timedelta(days=330),
            "criteria": "Systematic monitoring of employees · LI",
            "risks": "Over-collection · function creep · coverage gaps creating false assurance",
            "measures": "RBAC · retention limits · workforce notice · LIA on file",
            "residual": "Low–Medium",
            "consult_dpa": False,
            "notes": "Call out jump hosts missing SIEM as control failure, not DPIA failure.",
        },
        {
            "dpia_id": "DPIA-2026-005",
            "title": "New LedgerLink payments gateway (pre-contract)",
            "ropa_id": "",
            "status": "In progress",
            "owner": "DPO / Finance",
            "started": today - timedelta(days=15),
            "completed": pd.NaT,
            "next_review": today + timedelta(days=14),
            "criteria": "Payment data · new processor · PCI + privacy",
            "risks": "PAN handling · processor breach · transfer tools",
            "measures": "Tokenization · HITRUST i1 pending · DPA draft",
            "residual": "TBD",
            "consult_dpa": False,
            "notes": "Gate on VND-2026-008 diligence — do not go live without DPIA complete.",
        },
    ]

    # ── Rights / DSAR ────────────────────────────────────────────────
    dsars = [
        {
            "request_id": "DSAR-2026-001",
            "type": "Access (Art. 15 / CPRA know)",
            "regime": "GDPR",
            "subject_ref": "Customer · portal ID C-10422",
            "channel": "Privacy portal",
            "status": "In progress",
            "received": today - timedelta(days=12),
            "due": today + timedelta(days=18),
            "extended": False,
            "owner": "Privacy ops · L. Torres",
            "systems_in_scope": "Portal · B2C · marketing-DB · support",
            "notes": "Identity verified. Pull exports from portal + ESP suppression check.",
        },
        {
            "request_id": "DSAR-2026-002",
            "type": "Erasure (Art. 17 / delete)",
            "regime": "GDPR",
            "subject_ref": "Ex-customer · email on file",
            "channel": "Email to DPO",
            "status": "Legal hold",
            "received": today - timedelta(days=8),
            "due": today + timedelta(days=22),
            "extended": False,
            "owner": "Privacy ops / Legal",
            "systems_in_scope": "Portal · marketing · support",
            "notes": "Open billing dispute — erasure deferred under Art. 17(3)(b)/(e); inform subject.",
        },
        {
            "request_id": "DSAR-2026-003",
            "type": "Opt-out sale/share (CPRA)",
            "regime": "CPRA",
            "subject_ref": "CA resident · GPC signal",
            "channel": "GPC / website",
            "status": "Complete",
            "received": today - timedelta(days=20),
            "due": today - timedelta(days=5),
            "extended": False,
            "owner": "Marketing Ops",
            "systems_in_scope": "ESP · ad pixels",
            "notes": "GPC honored within 15 business days. Suppression written.",
        },
        {
            "request_id": "DSAR-2026-004",
            "type": "Access (Art. 15 / CPRA know)",
            "regime": "GDPR",
            "subject_ref": "Employee · HR ticket",
            "channel": "HRIS privacy form",
            "status": "Intake",
            "received": today - timedelta(days=2),
            "due": today + timedelta(days=28),
            "extended": False,
            "owner": "HR / Privacy ops",
            "systems_in_scope": "HRIS · PayrollCo · badge · email",
            "notes": "Identity pending manager attestation. PayrollCo freeze may delay payroll slice.",
        },
        {
            "request_id": "DSAR-2026-005",
            "type": "Portability (Art. 20)",
            "regime": "GDPR",
            "subject_ref": "Customer · SME admin",
            "channel": "Privacy portal",
            "status": "Identity verified",
            "received": today - timedelta(days=5),
            "due": today + timedelta(days=25),
            "extended": False,
            "owner": "Privacy ops",
            "systems_in_scope": "Portal · O2C contact fields",
            "notes": "Machine-readable JSON export path exists for portal; JDE contacts manual.",
        },
        {
            "request_id": "DSAR-2026-006",
            "type": "Objection (Art. 21)",
            "regime": "GDPR",
            "subject_ref": "Prospect · marketing LI historically mis-tagged",
            "channel": "Unsubscribe + DPO",
            "status": "Complete",
            "received": today - timedelta(days=40),
            "due": today - timedelta(days=10),
            "extended": False,
            "owner": "Marketing Ops",
            "systems_in_scope": "ESP",
            "notes": "Reclassified to consent-only; objection closed.",
        },
        {
            "request_id": "DSAR-2026-007",
            "type": "Limit sensitive use (CPRA)",
            "regime": "CPRA",
            "subject_ref": "CA employee",
            "channel": "HR",
            "status": "In progress",
            "received": today - timedelta(days=9),
            "due": today + timedelta(days=6),
            "extended": False,
            "owner": "HR / Privacy",
            "systems_in_scope": "HRIS",
            "notes": "Sensitive workforce data limit — confirm no secondary analytics use.",
        },
        {
            "request_id": "DSAR-2026-008",
            "type": "Access (Art. 15 / CPRA know)",
            "regime": "GDPR",
            "subject_ref": "Applicant · CreditAssist",
            "channel": "Credit privacy form",
            "status": "In progress",
            "received": today - timedelta(days=18),
            "due": today + timedelta(days=12),
            "extended": True,
            "owner": "Credit Risk / Privacy",
            "systems_in_scope": "CreditAssist · feature store · bureau (disclose source)",
            "notes": "Complex — model input/output explanation + bureau source. 60-day extension letter sent (complexity).",
        },
    ]

    # ── Breaches / security incidents with privacy notify path ───────
    breaches = [
        {
            "breach_id": "PB-2026-001",
            "title": "Portal credential-stuffing — email/display-name scrape",
            "related_ir": "INC-2026-001",
            "ropa_id": "ROPA-2026-002",
            "status": "Notify subjects",
            "detected": now - timedelta(hours=96),
            "assessed": now - timedelta(hours=88),
            "dpa_notified": now - timedelta(hours=70),
            "subjects_notified": pd.NaT,
            "affected_count": 340,
            "data_types": "Email · display name",
            "risk_to_rights": "Possible phishing targeting — not high for Art. 34 alone but state letters required",
            "regimes": "GDPR Art. 33 (done) · CA/NY/TX state letters",
            "owner": "DPO / GRC",
            "nis2_relevant": False,
            "notes": "Art. 33 within 72h. State notification letters drafting. Subjects: decide on notice vs FAQs.",
        },
        {
            "breach_id": "PB-2026-002",
            "title": "PayrollCo backup-environment — tenant impact unknown",
            "related_ir": "INC-2026-009",
            "ropa_id": "ROPA-2026-001",
            "status": "Assessing",
            "detected": now - timedelta(hours=10),
            "assessed": pd.NaT,
            "dpa_notified": pd.NaT,
            "subjects_notified": pd.NaT,
            "affected_count": 0,
            "data_types": "Possibly SSN · bank · tax (if tenant in scope)",
            "risk_to_rights": "High if confirmed — Art. 34 + multi-state + IRS considerations",
            "regimes": "GDPR Art. 33 clock running · US state · NIS2 early-warning if essential entity criteria met",
            "owner": "DPO / TPRM / Legal",
            "nis2_relevant": True,
            "notes": "Do not miss 72h. Draft Art. 33 holding notice. NIS2: assess if cyber notification to CSIRT/authority required in parallel to DPA.",
        },
        {
            "breach_id": "PB-2026-003",
            "title": "JDE IFS anonymous share — personal data readability",
            "related_ir": "INC-2026-005",
            "ropa_id": "ROPA-2026-003",
            "status": "Assessing",
            "detected": now - timedelta(days=7),
            "assessed": now - timedelta(days=6),
            "dpa_notified": pd.NaT,
            "subjects_notified": pd.NaT,
            "affected_count": 0,
            "data_types": "Customer contact fields in World libraries (scope TBD)",
            "risk_to_rights": "Depends on exfil — containment done; forensics ongoing",
            "regimes": "GDPR risk assessment · possible Art. 33",
            "owner": "DPO / Infra",
            "nis2_relevant": True,
            "notes": "Significant cyber incident candidate under NIS2 if essential — coordinate with CISO on dual-reporting.",
        },
        {
            "breach_id": "PB-2026-004",
            "title": "Misdirected employee email (single)",
            "related_ir": "",
            "ropa_id": "ROPA-2026-006",
            "status": "Closed — no notify",
            "detected": now - timedelta(days=45),
            "assessed": now - timedelta(days=45),
            "dpa_notified": pd.NaT,
            "subjects_notified": pd.NaT,
            "affected_count": 1,
            "data_types": "Name · work email · performance snippet",
            "risk_to_rights": "Low — recalled; recipient confirmed delete",
            "regimes": "Internal register only",
            "owner": "Privacy ops",
            "nis2_relevant": False,
            "notes": "Logged per policy. No DPA notify.",
        },
    ]

    # ── Transfer / vendor privacy inventory (light) ───────────────────
    transfers = [
        {
            "transfer_id": "XFR-2026-001",
            "ropa_id": "ROPA-2026-001",
            "importer": "PayrollCo (US)",
            "mechanism": "DPF (US) · SCCs backup",
            "tia_status": "Complete 2025-11 — refresh triggered by INC-2026-009",
            "owner": "DPO / TPRM",
            "next_review": today + timedelta(days=30),
        },
        {
            "transfer_id": "XFR-2026-002",
            "ropa_id": "ROPA-2026-008",
            "importer": "Orbit AMS offshore L2 (India)",
            "mechanism": "SCCs",
            "tia_status": "Stale — sub-processor notice pending update",
            "owner": "TPRM / DPO",
            "next_review": today + timedelta(days=14),
        },
        {
            "transfer_id": "XFR-2026-003",
            "ropa_id": "ROPA-2026-004",
            "importer": "Credit bureau (US)",
            "mechanism": "Contractual + SCCs where personal leaves EEA",
            "tia_status": "Complete",
            "owner": "Credit Risk / DPO",
            "next_review": today + timedelta(days=200),
        },
        {
            "transfer_id": "XFR-2026-004",
            "ropa_id": "ROPA-2026-002",
            "importer": "Microsoft Azure / B2C",
            "mechanism": "DPF (US)",
            "tia_status": "Rely on vendor docs + config review",
            "owner": "IAM / DPO",
            "next_review": today + timedelta(days=180),
        },
    ]

    # Deep packs for featured RoPA
    deep = {
        "ROPA-2026-001": {
            "tom": [
                {"measure": "Art. 28 DPA", "status": "In force — DPA-2024-019", "evidence": "Contract repo"},
                {"measure": "Encryption in transit", "status": "TLS", "evidence": "API gateway"},
                {"measure": "Access control / SSO", "status": "Federated — sessions revoked in IR", "evidence": "IdP logs"},
                {"measure": "Breach notice clause", "status": "Invoked", "evidence": "INC-2026-009"},
                {"measure": "Sub-processors listed", "status": "AWS backup region — scope issue", "evidence": "SOC 2 gap"},
                {"measure": "Return/delete on exit", "status": "In DPA — not tested live", "evidence": "PLN-2026-004"},
            ],
            "evidence": [
                {"ref": "EVD-P-001-A", "desc": "Art. 30 entry approved", "source": "RoPA register"},
                {"ref": "EVD-P-001-B", "desc": "DPA-2024-019", "source": "Legal"},
                {"ref": "EVD-P-001-C", "desc": "INC-2026-009 pack", "source": "IR"},
                {"ref": "EVD-P-001-D", "desc": "Workforce privacy notice", "source": "HR"},
            ],
            "open_actions": [
                {"action": "Complete DPIA-2026-002 refresh", "owner": "DPO", "due": today + timedelta(days=7), "status": "Overdue"},
                {"action": "Art. 33 draft if tenant confirmed", "owner": "DPO / Legal", "due": today + timedelta(days=2), "status": "Drafting"},
                {"action": "TIA refresh post-incident", "owner": "DPO / TPRM", "due": today + timedelta(days=30), "status": "Planned"},
                {"action": "NIS2 dual-report assessment with CISO", "owner": "CISO / DPO", "due": today + timedelta(days=3), "status": "Open"},
            ],
        },
        "ROPA-2026-004": {
            "tom": [
                {"measure": "Human oversight", "status": "Mandatory override", "evidence": "AST-2026-017 / model card"},
                {"measure": "DPIA", "status": "Complete — proceed", "evidence": "DPIA-2026-003"},
                {"measure": "Fairness / drift monitoring", "status": "Enabled", "evidence": "MLOps"},
                {"measure": "Prohibited autonomous denial", "status": "Policy enforced in UI", "evidence": "Credit UI"},
                {"measure": "Training data licenses", "status": "Bureau contracts", "evidence": "Procurement"},
                {"measure": "CPRA automated decision notice", "status": "In applicant notices", "evidence": "Legal"},
            ],
            "evidence": [
                {"ref": "EVD-P-004-A", "desc": "DPIA-2026-003", "source": "DPO"},
                {"ref": "EVD-P-004-B", "desc": "LIA-2026-CA-01", "source": "DPO"},
                {"ref": "EVD-P-004-C", "desc": "Model card MC-CA-2026-02", "source": "MRM"},
                {"ref": "EVD-P-004-D", "desc": "Applicant privacy notice excerpt", "source": "Legal"},
            ],
            "open_actions": [
                {"action": "Align RoPA wording with any model v2.4 promote", "owner": "AI product / DPO", "due": today + timedelta(days=45), "status": "Planned"},
                {"action": "DSAR-2026-008 complex access — complete pack", "owner": "Privacy ops", "due": today + timedelta(days=12), "status": "In progress"},
            ],
        },
        "ROPA-2026-006": {
            "tom": [
                {"measure": "LIA", "status": "On file", "evidence": "LIA-2026-SEC-01"},
                {"measure": "Workforce notice", "status": "Handbook §12", "evidence": "HR"},
                {"measure": "SIEM RBAC", "status": "Need-to-know", "evidence": "SecOps"},
                {"measure": "Retention", "status": "1y auth / session", "evidence": "SIEM policy"},
                {"measure": "Coverage completeness", "status": "Gap — JUMP-DMZ-03", "evidence": "AST-2026-005"},
                {"measure": "NIS2 monitoring expectation", "status": "Partial until jump SIEM closed", "evidence": "CISO"},
            ],
            "evidence": [
                {"ref": "EVD-P-006-A", "desc": "DPIA-2026-004", "source": "DPO"},
                {"ref": "EVD-P-006-B", "desc": "LIA-2026-SEC-01", "source": "DPO"},
                {"ref": "EVD-P-006-C", "desc": "Asset gap GAP-2026-001", "source": "CMDB / CAASM"},
            ],
            "open_actions": [
                {"action": "Close SIEM gap on JUMP-DMZ-03 before NIS2 evidence pull", "owner": "SecOps", "due": today + timedelta(days=3), "status": "In progress"},
                {"action": "Annual LIA re-attest", "owner": "DPO", "due": today + timedelta(days=150), "status": "Planned"},
            ],
        },
    }

    df_r = pd.DataFrame(ropa)
    for col in ("last_review", "next_review"):
        df_r[col] = pd.to_datetime(df_r[col], errors="coerce")
    df_r["tom"] = df_r["ropa_id"].map(lambda i: deep.get(i, {}).get("tom", []))
    df_r["evidence"] = df_r["ropa_id"].map(lambda i: deep.get(i, {}).get("evidence", []))
    df_r["open_actions"] = df_r["ropa_id"].map(lambda i: deep.get(i, {}).get("open_actions", []))

    df_d = pd.DataFrame(dpias)
    for col in ("started", "completed", "next_review"):
        df_d[col] = pd.to_datetime(df_d[col], errors="coerce")

    df_q = pd.DataFrame(dsars)
    for col in ("received", "due"):
        df_q[col] = pd.to_datetime(df_q[col], errors="coerce")

    df_b = pd.DataFrame(breaches)
    for col in ("detected", "assessed", "dpa_notified", "subjects_notified"):
        df_b[col] = pd.to_datetime(df_b[col], errors="coerce")

    df_t = pd.DataFrame(transfers)
    df_t["next_review"] = pd.to_datetime(df_t["next_review"], errors="coerce")

    return df_r, df_d, df_q, df_b, df_t


def _enrich_ropa(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["review_overdue"] = out["next_review"] < today
    out["days_to_review"] = (out["next_review"] - today).dt.days
    return out


def _enrich_dsar(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    today = _today()
    out["open"] = ~out["status"].isin(["Complete", "Rejected"])
    out["overdue"] = out["open"] & (out["due"] < today)
    out["due_soon"] = out["open"] & (out["due"] <= today + timedelta(days=7)) & ~out["overdue"]
    out["age_d"] = (today - out["received"]).dt.days
    return out


def _enrich_breach(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    now = _now()
    out["hours_since_detect"] = ((now - out["detected"]).dt.total_seconds() / 3600).round(1)
    out["art33_due"] = out["detected"] + timedelta(hours=72)
    out["art33_remaining_h"] = ((out["art33_due"] - now).dt.total_seconds() / 3600).round(1)
    out["needs_art33"] = out["status"].isin(["Detected", "Assessing", "Notify DPA"]) & out["dpa_notified"].isna()
    out["art33_breach_risk"] = out["needs_art33"] & (out["art33_remaining_h"] < 24)
    return out


def _sync(seed: int):
    if st.session_state.get("_priv_seed") != seed or "priv_ropa" not in st.session_state:
        r, d, q, b, t = _sample(seed)
        st.session_state.priv_ropa = r
        st.session_state.priv_dpia = d
        st.session_state.priv_dsar = q
        st.session_state.priv_breach = b
        st.session_state.priv_xfer = t
        st.session_state._priv_seed = seed
    return (
        st.session_state.priv_ropa,
        st.session_state.priv_dpia,
        st.session_state.priv_dsar,
        st.session_state.priv_breach,
        st.session_state.priv_xfer,
    )


def _save_ropa(df):
    st.session_state.priv_ropa = df.reset_index(drop=True)


def _save_dsar(df):
    st.session_state.priv_dsar = df.reset_index(drop=True)


def _save_breach(df):
    st.session_state.priv_breach = df.reset_index(drop=True)


def _save_dpia(df):
    st.session_state.priv_dpia = df.reset_index(drop=True)


def _patch_ropa(rid, **fields):
    df = st.session_state.priv_ropa.copy()
    loc = df.index[df["ropa_id"] == rid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_ropa(df)


def _patch_dsar(qid, **fields):
    df = st.session_state.priv_dsar.copy()
    loc = df.index[df["request_id"] == qid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_dsar(df)


def _patch_breach(bid, **fields):
    df = st.session_state.priv_breach.copy()
    loc = df.index[df["breach_id"] == bid]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_breach(df)


def _patch_dpia(did, **fields):
    df = st.session_state.priv_dpia.copy()
    loc = df.index[df["dpia_id"] == did]
    if len(loc) == 0:
        return
    for k, v in fields.items():
        df.at[loc[0], k] = v
    _save_dpia(df)


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
        if p.hour or p.minute:
            return p.strftime("%Y-%m-%d %H:%M")
        return p.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "—"


def _metrics(ropa, dpias, dsars, breaches):
    er = _enrich_ropa(ropa)
    eq = _enrich_dsar(dsars)
    eb = _enrich_breach(breaches)
    return {
        "ropa": len(er),
        "ropa_od": int(er["review_overdue"].sum()),
        "dsar_open": int(eq["open"].sum()),
        "dsar_od": int(eq["overdue"].sum()),
        "art33": int(eb["needs_art33"].sum()),
        "art33_hot": int(eb["art33_breach_risk"].sum()),
        "dpia_hot": int(dpias["status"].isin(["Overdue", "In progress", "Screening"]).sum()),
        "nis2": int(er["nis2_flag"].sum()),
    }


def _ropa_detail(row, dpias, *, expanded=False):
    st.markdown(f"### {row['ropa_id']} · {row['name']}")
    a, b, c, d = st.columns(4)
    a.metric("Org role", row["role_of_org"])
    b.metric("Status", row["status"].split("—")[0].strip())
    c.metric("NIS2-relevant", "Yes" if row["nis2_flag"] else "No")
    d.metric("Next review", _fmt(row["next_review"]))

    c1, c2, c3 = st.columns(3)
    c1.write(f"**Purpose:** {row['purpose']}")
    c1.write(f"**Owner:** {row['owner']}")
    c1.write(f"**DPO:** {row['dpo_contact']}")
    c1.write(f"**Controller:** {row['controller']}")
    if row["processor"]:
        c1.write(f"**Processor:** {row['processor']}")
    c2.write(f"**Legal basis:** {row['legal_basis']}")
    if row["li_assessment"]:
        c2.write(f"**LI assessment:** {row['li_assessment']}")
    c2.write(f"**Subjects:** {row['categories_subjects']}")
    c2.write(f"**Data categories:** {row['categories_data']}")
    c2.write(f"**Special category:** {row['special_category']}")
    c3.write(f"**Recipients:** {row['recipients']}")
    c3.write(f"**Transfers:** {row['transfers']}")
    c3.write(f"**Transfer tool:** {row['transfer_tool']}")
    c3.write(f"**Retention:** {row['retention']}")
    c3.write(f"**Security measures:** {row['security_measures']}")

    st.write(row["summary"])
    if row["risk_notes"]:
        st.warning(row["risk_notes"])
    st.caption(f"Systems: {row['systems']}")
    st.caption(f"Jurisdictions: {row['jurisdictions']}")
    if row["dpia_id"]:
        st.caption(f"DPIA: {row['dpia_id']}")
    st.caption(f"Last review: {_fmt(row['last_review'])}")

    raw = st.session_state.priv_ropa
    rr = raw[raw["ropa_id"] == row["ropa_id"]]
    if not rr.empty:
        r0 = rr.iloc[0]
        tom = r0.get("tom") or []
        evid = r0.get("evidence") or []
        acts = r0.get("open_actions") or []
        if tom:
            with st.expander(f"Technical & organisational measures ({len(tom)})", expanded=expanded):
                st.dataframe(pd.DataFrame(tom), use_container_width=True, hide_index=True)
        if evid:
            with st.expander(f"Evidence ({len(evid)})", expanded=expanded):
                st.dataframe(pd.DataFrame(evid), use_container_width=True, hide_index=True)
        if acts:
            with st.expander(f"Open actions ({len(acts)})", expanded=expanded):
                adf = pd.DataFrame(acts)
                if "due" in adf.columns:
                    adf["due"] = adf["due"].apply(_fmt)
                st.dataframe(adf, use_container_width=True, hide_index=True)

    if row["dpia_id"]:
        d = dpias[dpias["dpia_id"] == row["dpia_id"]]
        if not d.empty:
            dr = d.iloc[0]
            with st.expander(f"Linked DPIA · {dr['dpia_id']} · {dr['status']}", expanded=False):
                st.write(f"**Risks:** {dr['risks']}")
                st.write(f"**Measures:** {dr['measures']}")
                st.write(f"**Residual:** {dr['residual']}")
                st.write(dr["notes"])


def _ropa_actions(row, *, key: str):
    rid = row["ropa_id"]
    a1, a2 = st.columns(2)
    with a1:
        if st.button("Mark Art. 30 reviewed", key=f"rr_{key}", use_container_width=True):
            _patch_ropa(
                rid,
                last_review=_today(),
                next_review=_today() + timedelta(days=180),
            )
            st.rerun()
    with a2:
        if row.get("review_overdue") and st.button(
            "Flag owner — review overdue", key=f"ro_{key}", use_container_width=True
        ):
            note = (row.get("risk_notes") or "") + " [Owner notified: Art. 30 review overdue.]"
            _patch_ropa(rid, risk_notes=note.strip())
            st.rerun()


def main() -> None:
    portfolio_skin.page_header(
        title="Data Privacy Management",
        lede="Art. 30 RoPA, DPIAs, rights clocks, breach / NIS2 paths, US state privacy. Club demo — not a system of record.",
        kicker="Privacy",
    )

    seed = demo_kit.seed_controls()
    ropa, dpias, dsars, breaches, xfers = _sync(seed)
    er = _enrich_ropa(ropa)
    eq = _enrich_dsar(dsars)
    eb = _enrich_breach(breaches)
    m = _metrics(ropa, dpias, dsars, breaches)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    nis2_only = st.sidebar.checkbox("NIS2-relevant RoPA only", value=False)
    open_dsar_only = st.sidebar.checkbox("Open DSARs only", value=False)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("RoPA entries", m["ropa"])
    k2.metric("RoPA review overdue", m["ropa_od"])
    k3.metric("Open rights requests", m["dsar_open"])
    k4.metric("DSAR overdue", m["dsar_od"])
    k5.metric("Art. 33 clocks live", m["art33"], help="Incidents still needing DPA notification assessment")
    k6.metric("NIS2-tagged activities", m["nis2"])

    if m["art33_hot"]:
        st.error(f"{m['art33_hot']} privacy incident(s) inside final 24h of GDPR Art. 33 72-hour window.")
    elif m["art33"]:
        st.warning(f"{m['art33']} privacy incident(s) with Art. 33 notification still open.")

    work, ropa_tab, rights, breach_tab, dpia_tab, xfer_tab, intake, export = st.tabs(
        [
            "Workbench",
            "RoPA (Art. 30)",
            "Rights / DSAR",
            "Breach & notify",
            "DPIA",
            "Transfers",
            "Intake",
            "Export",
        ]
    )

    with work:
        st.subheader("Privacy workbench")

        featured = er[er["ropa_id"].isin(FEATURED_ROPA)].copy()
        order = {i: n for n, i in enumerate(["ROPA-2026-001", "ROPA-2026-004", "ROPA-2026-006"])}
        featured["_o"] = featured["ropa_id"].map(lambda x: order.get(x, 99))
        featured = featured.sort_values("_o")

        st.markdown(f"**Featured RoPA — statement of record ({len(featured)})**")
        for _, row in featured.iterrows():
            st.markdown("---")
            _ropa_detail(row, dpias, expanded=True)
            _ropa_actions(row, key=f"feat_{row['ropa_id']}")
            st.markdown("---")

        # Art 33 queue
        hot_b = eb[eb["needs_art33"]].sort_values("art33_remaining_h")
        st.markdown(f"**Breach / Art. 33 queue ({len(hot_b)})**")
        if hot_b.empty:
            st.info("No open Art. 33 clocks.")
        else:
            for _, b in hot_b.iterrows():
                with st.expander(
                    f"{b['breach_id']} · {b['title']} · {b['status']} · "
                    f"{b['art33_remaining_h']:.0f}h left to 72h"
                ):
                    st.write(f"**Detected:** {_fmt(b['detected'])} · **IR:** {b['related_ir'] or '—'}")
                    st.write(f"**Regimes:** {b['regimes']}")
                    st.write(f"**Risk to rights:** {b['risk_to_rights']}")
                    st.write(b["notes"])
                    if b["nis2_relevant"]:
                        st.warning("NIS2-relevant — coordinate cyber authority / CSIRT path with CISO.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Mark DPA notified (Art. 33)", key=f"a33_{b['breach_id']}"):
                            _patch_breach(
                                b["breach_id"],
                                dpa_notified=_now(),
                                status="Notify subjects",
                                assessed=_now() if pd.isna(b["assessed"]) else b["assessed"],
                            )
                            st.rerun()
                    with c2:
                        if st.button("Close — no notify", key=f"bn_{b['breach_id']}"):
                            _patch_breach(b["breach_id"], status="Closed — no notify", assessed=_now())
                            st.rerun()

        # DSAR due soon / overdue
        hot_q = eq[eq["overdue"] | eq["due_soon"]].sort_values("due")
        st.markdown(f"**Rights requests due ≤7d or overdue ({len(hot_q)})**")
        if hot_q.empty:
            st.info("Clear.")
        else:
            show = hot_q.copy()
            show["due"] = show["due"].apply(_fmt)
            show["received"] = show["received"].apply(_fmt)
            st.dataframe(
                show[["request_id", "type", "regime", "status", "due", "owner", "notes"]],
                use_container_width=True,
                hide_index=True,
            )

        od_ropa = er[er["review_overdue"]]
        if not od_ropa.empty:
            st.markdown("**Art. 30 reviews overdue**")
            st.dataframe(
                od_ropa[["ropa_id", "name", "owner", "next_review", "risk_notes"]].assign(
                    next_review=lambda d: d["next_review"].apply(_fmt)
                ),
                use_container_width=True,
                hide_index=True,
            )

    with ropa_tab:
        st.subheader("Records of processing (GDPR Art. 30)")
        view = er[er["nis2_flag"]] if nis2_only else er
        pick = st.selectbox("Activity", view["ropa_id"].tolist())
        row = er[er["ropa_id"] == pick].iloc[0]
        _ropa_detail(row, dpias, expanded=True)
        _ropa_actions(row, key=f"ropa_{pick}")

        show = view[
            [
                "ropa_id",
                "name",
                "role_of_org",
                "legal_basis",
                "owner",
                "transfer_tool",
                "nis2_flag",
                "next_review",
                "status",
            ]
        ].copy()
        show["next_review"] = show["next_review"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)

    with rights:
        st.subheader("Data subject / consumer rights")
        view = eq[eq["open"]] if open_dsar_only else eq
        show = view.copy()
        show["received"] = show["received"].apply(_fmt)
        show["due"] = show["due"].apply(_fmt)
        st.dataframe(
            show[
                [
                    "request_id",
                    "type",
                    "regime",
                    "subject_ref",
                    "status",
                    "received",
                    "due",
                    "extended",
                    "owner",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        rid = st.selectbox("Request detail", view["request_id"].tolist())
        r = eq[eq["request_id"] == rid].iloc[0]
        st.markdown(f"#### {r['request_id']} · {r['type']}")
        st.write(f"**Regime:** {r['regime']} · **Status:** {r['status']} · **Due:** {_fmt(r['due'])}")
        st.write(f"**Subject:** {r['subject_ref']}")
        st.write(f"**Systems:** {r['systems_in_scope']}")
        st.write(r["notes"])
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if r["status"] == "Intake" and st.button("Verify identity", key=f"dv_{rid}"):
                _patch_dsar(rid, status="Identity verified")
                st.rerun()
        with b2:
            if r["status"] in {"Identity verified", "Intake"} and st.button(
                "Start work", key=f"ds_{rid}"
            ):
                _patch_dsar(rid, status="In progress")
                st.rerun()
        with b3:
            if r["open"] and not r["extended"] and st.button("Extend +30d", key=f"de_{rid}"):
                _patch_dsar(rid, extended=True, due=pd.Timestamp(r["due"]) + timedelta(days=30))
                st.rerun()
        with b4:
            if r["open"] and st.button("Complete", key=f"dc_{rid}"):
                _patch_dsar(rid, status="Complete")
                st.rerun()

        st.caption(
            "Clocks: GDPR typically 1 month (extendable); CPRA often 45 days (extendable). "
            "Demo uses due dates already set per request — not a lawyer."
        )

    with breach_tab:
        st.subheader("Personal data breaches & notification")
        for _, b in eb.sort_values("detected", ascending=False).iterrows():
            clock = ""
            if b["needs_art33"]:
                clock = f" · Art.33 {b['art33_remaining_h']:.0f}h left"
            with st.expander(f"{b['breach_id']} · {b['title']} · {b['status']}{clock}"):
                st.write(f"**Detected:** {_fmt(b['detected'])} · **Hours since:** {b['hours_since_detect']}")
                st.write(f"**IR / RoPA:** {b['related_ir'] or '—'} / {b['ropa_id']}")
                st.write(f"**Affected (est.):** {int(b['affected_count'])} · **Data:** {b['data_types']}")
                st.write(f"**Risk to rights:** {b['risk_to_rights']}")
                st.write(f"**Regimes:** {b['regimes']}")
                st.write(f"**DPA notified:** {_fmt(b['dpa_notified'])} · **Subjects:** {_fmt(b['subjects_notified'])}")
                if b["nis2_relevant"]:
                    st.warning("NIS2-relevant cyber notification may run in parallel to privacy notify.")
                st.write(b["notes"])
                c1, c2, c3 = st.columns(3)
                with c1:
                    if b["needs_art33"] and st.button("Art. 33 notified", key=f"b33_{b['breach_id']}"):
                        _patch_breach(b["breach_id"], dpa_notified=_now(), status="Notify subjects")
                        st.rerun()
                with c2:
                    if b["status"] == "Notify subjects" and st.button(
                        "Subjects notified", key=f"bs_{b['breach_id']}"
                    ):
                        _patch_breach(
                            b["breach_id"],
                            subjects_notified=_now(),
                            status="Closed",
                        )
                        st.rerun()
                with c3:
                    if b["status"] not in {"Closed", "Closed — no notify"} and st.button(
                        "Close — no notify", key=f"bc_{b['breach_id']}"
                    ):
                        _patch_breach(b["breach_id"], status="Closed — no notify")
                        st.rerun()

    with dpia_tab:
        st.subheader("DPIAs / PIAs")
        for _, d in dpias.sort_values("next_review").iterrows():
            flag = " · OVERDUE" if d["status"] == "Overdue" else ""
            with st.expander(f"{d['dpia_id']} · {d['title']} · {d['status']}{flag}"):
                st.write(f"**RoPA:** {d['ropa_id'] or '—'} · **Owner:** {d['owner']}")
                st.write(f"**Criteria:** {d['criteria']}")
                st.write(f"**Risks:** {d['risks']}")
                st.write(f"**Measures:** {d['measures']}")
                st.write(f"**Residual:** {d['residual']}")
                st.write(f"**Started / completed / next:** {_fmt(d['started'])} / {_fmt(d['completed'])} / {_fmt(d['next_review'])}")
                st.write(d["notes"])
                if d["status"] in {"Overdue", "In progress", "Screening"} and st.button(
                    "Mark complete — proceed", key=f"dp_{d['dpia_id']}"
                ):
                    _patch_dpia(
                        d["dpia_id"],
                        status="Complete — proceed",
                        completed=_today(),
                        next_review=_today() + timedelta(days=365),
                    )
                    st.rerun()

    with xfer_tab:
        st.subheader("International transfers")
        show = xfers.copy()
        show["next_review"] = show["next_review"].apply(_fmt)
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.caption("TIA = transfer impact assessment. Demo mechanisms: SCCs, DPF, adequacy — not legal advice.")

    with intake:
        st.subheader("Add RoPA entry")
        with st.form("intake_ropa"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Activity name")
                purpose = st.text_area("Purpose")
                owner = st.text_input("Business owner")
                legal = st.selectbox("Legal basis", LEGAL_BASES)
            with c2:
                role = st.selectbox("Our role", ROLES)
                processor = st.text_input("Processor (if any)")
                subjects = st.text_input("Categories of data subjects")
                data_cats = st.text_input("Categories of personal data")
                nis2 = st.checkbox("NIS2-relevant")
            if st.form_submit_button("Create Art. 30 entry"):
                if not name.strip() or not purpose.strip():
                    st.error("Name and purpose required.")
                else:
                    n = len(st.session_state.priv_ropa) + 1
                    today = _today()
                    add = {
                        "ropa_id": f"ROPA-2026-{n:03d}",
                        "name": name.strip(),
                        "purpose": purpose.strip(),
                        "controller": "Acme Corp",
                        "joint_controller": "",
                        "processor": processor.strip(),
                        "role_of_org": role,
                        "owner": owner.strip() or "TBD",
                        "dpo_contact": "dpo@acme.example",
                        "legal_basis": legal,
                        "li_assessment": "",
                        "categories_subjects": subjects.strip() or "TBD",
                        "categories_data": data_cats.strip() or "TBD",
                        "special_category": "TBD",
                        "recipients": "TBD",
                        "transfers": "Not assessed",
                        "transfer_tool": "Not assessed",
                        "retention": "TBD",
                        "security_measures": "TBD",
                        "systems": "TBD",
                        "jurisdictions": "TBD",
                        "nis2_flag": bool(nis2),
                        "dpia_id": "",
                        "status": "Draft",
                        "last_review": today,
                        "next_review": today + timedelta(days=90),
                        "risk_notes": "",
                        "summary": "Intake stub — complete Art. 30 fields before relying on this entry.",
                        "tom": [],
                        "evidence": [],
                        "open_actions": [],
                    }
                    _save_ropa(
                        pd.concat([st.session_state.priv_ropa, pd.DataFrame([add])], ignore_index=True)
                    )
                    st.success(f"ROPA-2026-{n:03d} created.")
                    st.rerun()

        st.subheader("Log rights request")
        with st.form("intake_dsar"):
            c1, c2 = st.columns(2)
            with c1:
                dtype = st.selectbox("Type", DSAR_TYPES)
                regime = st.selectbox("Regime", ["GDPR", "CPRA", "Other US state", "UK GDPR"])
                subject = st.text_input("Subject reference")
            with c2:
                channel = st.text_input("Channel", value="Privacy portal")
                due_days = st.number_input("Due in days", 1, 90, 30)
            notes = st.text_area("Notes")
            if st.form_submit_button("Create request"):
                n = len(st.session_state.priv_dsar) + 1
                today = _today()
                add = {
                    "request_id": f"DSAR-2026-{n:03d}",
                    "type": dtype,
                    "regime": regime,
                    "subject_ref": subject.strip() or "TBD",
                    "channel": channel.strip() or "Manual",
                    "status": "Intake",
                    "received": today,
                    "due": today + timedelta(days=int(due_days)),
                    "extended": False,
                    "owner": "Privacy ops",
                    "systems_in_scope": "TBD",
                    "notes": notes.strip(),
                }
                _save_dsar(
                    pd.concat([st.session_state.priv_dsar, pd.DataFrame([add])], ignore_index=True)
                )
                st.success(f"DSAR-2026-{n:03d} logged.")
                st.rerun()

    with export:
        st.subheader("Export")
        out_r = er.copy()
        for col in ("last_review", "next_review"):
            out_r[col] = out_r[col].apply(_fmt)
        for col in ("tom", "evidence", "open_actions"):
            if col in out_r.columns:
                out_r = out_r.drop(columns=[col])
        demo_kit.csv_download(out_r, "ropa_art30.csv", label="Download RoPA")
        out_q = eq.copy()
        out_q["received"] = out_q["received"].apply(_fmt)
        out_q["due"] = out_q["due"].apply(_fmt)
        demo_kit.csv_download(out_q, "dsar_rights.csv", label="Download rights requests", key="q_csv")
        out_b = eb.copy()
        for col in ("detected", "assessed", "dpa_notified", "subjects_notified", "art33_due"):
            if col in out_b.columns:
                out_b[col] = out_b[col].apply(_fmt)
        demo_kit.csv_download(out_b, "privacy_breaches.csv", label="Download breach register", key="b_csv")
        out_d = dpias.copy()
        for col in ("started", "completed", "next_review"):
            out_d[col] = out_d[col].apply(_fmt)
        demo_kit.csv_download(out_d, "dpias.csv", label="Download DPIAs", key="d_csv")
        st.caption("Resample rebuilds the demo set. Edits live in this browser session only. Not legal advice.")


if __name__ == "__main__":
    main()
