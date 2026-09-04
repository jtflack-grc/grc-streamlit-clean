#!/usr/bin/env python3
"""Unix/Linux security assessment workbench — club teaching toy.

CIS Benchmark / STIG / PowerSC-style domain scoring across RHEL, AIX, and
Solaris — Qualys SCA and Tenable CIS assessment patterns, IBM PowerSC for AIX,
Oracle Solaris compliance / BSM, Lynis-class control domains. Synthetic
NorthStack estate (JUMP-DMZ-03 and friends) — not a live host connection.
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
    page_title="Unix/Linux Security Assessment · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)

SCAN_DOMAINS = [
    ("AUTH", "Authentication / PAM / passwords", "#6366f1"),
    ("PRIV", "Privileged access / sudo / root", "#f59e0b"),
    ("SSH", "SSH / remote access", "#3b82f6"),
    ("NET", "Network services / firewall", "#ef4444"),
    ("FS", "Filesystem / NFS / shares", "#22c55e"),
    ("KERN", "Kernel / sysctl / OS hardening", "#a855f7"),
    ("AUD", "Audit logging (auditd / AIX / BSM)", "#ec4899"),
    ("PATCH", "Patch & package currency", "#14b8a6"),
]

SEVERITY = ["Critical", "High", "Medium", "Low", "Info"]
FEATURED_FINDINGS = {
    "FND-UX-001",
    "FND-UX-002",
    "FND-UX-003",
    "FND-UX-005",
    "FND-UX-007",
    "FND-UX-009",
    "FND-UX-011",
    "FND-UX-014",
}
_SYNC_KEY = "_ux_assess_v1"

REFERENCES = [
    {"id": "CIS-RHEL9", "title": "CIS Red Hat Enterprise Linux 9 Benchmark", "use": "SSH, PAM, sudo, sysctl"},
    {"id": "CIS-AIX73", "title": "CIS IBM AIX 7.3 Benchmark", "use": "PowerSC profiles, TCB, NFS"},
    {"id": "CIS-SOL11", "title": "CIS Oracle Solaris 11 Benchmark", "use": "SMF, BSM, RBAC"},
    {"id": "STIG-RHEL8", "title": "DISA STIG RHEL 8 / 9", "use": "DoD hardening checklist"},
    {"id": "POWERSC", "title": "IBM PowerSC Security & Compliance Automation", "use": "AIX CIS/STIG/PCI profiles"},
    {"id": "LYNIS", "title": "Lynis audit categories (industry pattern)", "use": "Domain RAG scoring pattern"},
    {"id": "NIST-800-53", "title": "NIST SP 800-53 Rev. 5", "use": "AC / AU / CM / IA / SC families"},
    {"id": "QUALYS-SCA", "title": "Qualys SCA / Tenable CIS assessment pattern", "use": "Continuous config scoring"},
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

    hosts = pd.DataFrame(
        [
            {
                "host_id": "HOST-JUMP",
                "hostname": "JUMP-DMZ-03",
                "fqdn": "jump-dmz-03.northstack.internal",
                "os_family": "Linux",
                "os": "RHEL 9.4",
                "kernel": "5.14.0-427.37.1.el9_4",
                "role": "Privileged jump / bastion (colo DMZ)",
                "site": "NorthStack colo A · cage 12 · DMZ VLAN 40",
                "cpu_pct": 18,
                "mem_pct": 41,
                "disk_pct": 52,
                "users": 38,
                "sudoers": 14,
                "suid_bins": 62,
                "listeners": 9,
                "open_cves_crit": 2,
                "days_since_patch": 47,
                "agent": "Qualys Cloud Agent · CrowdStrike Falcon",
                "crown_jewel": True,
                "owner": "Platform Sec · J. Okonkwo",
                "linked": "AST-2026-005 · INC-2026-001 · KRI-2026-001",
            },
            {
                "host_id": "HOST-APP",
                "hostname": "nsk-rhel-app01",
                "fqdn": "nsk-rhel-app01.northstack.internal",
                "os_family": "Linux",
                "os": "RHEL 8.10",
                "kernel": "4.18.0-553.22.1.el8_10",
                "role": "JDE World middleware / SFTP drop to PayrollCo",
                "site": "NorthStack colo A · cage 12 · App VLAN 20",
                "cpu_pct": 64,
                "mem_pct": 71,
                "disk_pct": 68,
                "users": 112,
                "sudoers": 27,
                "suid_bins": 88,
                "listeners": 14,
                "open_cves_crit": 5,
                "days_since_patch": 63,
                "agent": "Qualys Cloud Agent · Wazuh",
                "crown_jewel": True,
                "owner": "AppOps · M. Chen",
                "linked": "PayrollCo · INC-2026-009 · AST-2026-012",
            },
            {
                "host_id": "HOST-AIX",
                "hostname": "nsk-aix-db01",
                "fqdn": "nsk-aix-db01.northstack.internal",
                "os_family": "AIX",
                "os": "AIX 7.3 TL3 SP2",
                "kernel": "7300-03-02-2446",
                "role": "DB2 LUW · payroll extract / PRODBOX feed",
                "site": "NorthStack colo A · Power10 frame · LPAR 4",
                "cpu_pct": 55,
                "mem_pct": 78,
                "disk_pct": 61,
                "users": 46,
                "sudoers": 9,
                "suid_bins": 41,
                "listeners": 7,
                "open_cves_crit": 3,
                "days_since_patch": 91,
                "agent": "IBM PowerSC GUI agent · Qualys",
                "crown_jewel": True,
                "owner": "AIX Ops · R. Nair",
                "linked": "PRODBOX · KRI-2026-002 · CMP-2026-001",
            },
            {
                "host_id": "HOST-SOL",
                "hostname": "nsk-sol-ora01",
                "fqdn": "nsk-sol-ora01.northstack.internal",
                "os_family": "Solaris",
                "os": "Oracle Solaris 11.4 SRU72",
                "kernel": "11.4.72.0.1.185.1",
                "role": "Legacy Oracle EBS DB (read-mostly)",
                "site": "NorthStack colo B (DR) · cage 3 · SPARC T8",
                "cpu_pct": 22,
                "mem_pct": 48,
                "disk_pct": 74,
                "users": 29,
                "sudoers": 6,
                "suid_bins": 35,
                "listeners": 11,
                "open_cves_crit": 4,
                "days_since_patch": 118,
                "agent": "Qualys scanner (agentless) · no EDR",
                "crown_jewel": False,
                "owner": "Oracle Ops · Legacy · S. Berg",
                "linked": "DST-2026-001 · GAP-2026-001 · decommission backlog",
            },
            {
                "host_id": "HOST-WEB",
                "hostname": "nsk-rhel-web01",
                "fqdn": "nsk-rhel-web01.northstack.internal",
                "os_family": "Linux",
                "os": "RHEL 9.3",
                "kernel": "5.14.0-362.24.1.el9_3",
                "role": "External portal edge (read-only CMS)",
                "site": "NorthStack colo A · DMZ VLAN 40",
                "cpu_pct": 31,
                "mem_pct": 44,
                "disk_pct": 39,
                "users": 18,
                "sudoers": 5,
                "suid_bins": 54,
                "listeners": 6,
                "open_cves_crit": 1,
                "days_since_patch": 28,
                "agent": "Qualys · CrowdStrike Falcon",
                "crown_jewel": False,
                "owner": "WebOps · L. Duarte",
                "linked": "INC-2026-001 portal stuffing narrative",
            },
        ]
    )

    domains = pd.DataFrame(
        [
            {"domain_id": "AUTH", "domain": "Authentication / PAM / passwords", "score": 54, "checks": 24, "fails": 11, "benchmark": "CIS RHEL/AIX/SOL · PAM / logindefs"},
            {"domain_id": "PRIV", "domain": "Privileged access / sudo / root", "score": 38, "checks": 18, "fails": 12, "benchmark": "CIS sudo · least privilege · PowerSC"},
            {"domain_id": "SSH", "domain": "SSH / remote access", "score": 41, "checks": 20, "fails": 13, "benchmark": "CIS SSH · STIG RHEL · sshd_config"},
            {"domain_id": "NET", "domain": "Network services / firewall", "score": 47, "checks": 16, "fails": 9, "benchmark": "firewalld / ipfilter / AIX IPSec"},
            {"domain_id": "FS", "domain": "Filesystem / NFS / shares", "score": 36, "checks": 22, "fails": 14, "benchmark": "World-writable · NFS · exports"},
            {"domain_id": "KERN", "domain": "Kernel / sysctl / OS hardening", "score": 61, "checks": 28, "fails": 10, "benchmark": "sysctl · AIX SEC · Solaris SMF"},
            {"domain_id": "AUD", "domain": "Audit logging (auditd / AIX / BSM)", "score": 49, "checks": 15, "fails": 8, "benchmark": "auditd · AIX audit · Solaris BSM"},
            {"domain_id": "PATCH", "domain": "Patch & package currency", "score": 44, "checks": 12, "fails": 7, "benchmark": "dnf / yum · AIX TL · Solaris SRU"},
        ]
    )
    domains["rag"] = domains["score"].map(_rag)

    findings = [
        {
            "finding_id": "FND-UX-001",
            "host_id": "HOST-JUMP",
            "domain_id": "SSH",
            "severity": "Critical",
            "title": "JUMP-DMZ-03 allows root SSH with password auth",
            "detail": "sshd_config: PermitRootLogin yes · PasswordAuthentication yes · PubkeyAuthentication yes. Shared ops account opsnight still authenticates with password after INC-2026-001 portal stuffing — jump is the blast-radius gate to PRODBOX and nsk-aix-db01.",
            "evidence": "sshd -T | grep -E 'permitrootlogin|passwordauthentication'",
            "cis": "CIS RHEL 9 5.2.x SSH server",
            "stig": "RHEL-09-255040 / 255055",
            "iso27001": "A.5.15 · A.8.5",
            "soc2": "CC6.1 · CC6.6",
            "pci": "2.2 · 8.3 · 8.4",
            "ref": "CIS-RHEL9 · STIG-RHEL8",
            "remediation": "PermitRootLogin prohibit-password; PasswordAuthentication no; force named keys + PAM MFA; retire opsnight.",
            "owner": "Platform Sec · J. Okonkwo",
            "status": "Open",
            "due": today + timedelta(days=7),
            "linked": "AST-2026-005 · INC-2026-001 · KRI-2026-001",
        },
        {
            "finding_id": "FND-UX-002",
            "host_id": "HOST-APP",
            "domain_id": "PRIV",
            "severity": "Critical",
            "title": "sudo NOPASSWD:ALL for deploy and payrollsvc groups",
            "detail": "/etc/sudoers.d/90-deploy: %deploy ALL=(ALL) NOPASSWD:ALL · %payrollsvc ALL=(ALL) NOPASSWD:/usr/bin/*,/opt/jde/*. PayrollCo SFTP drop runs as payrollsvc — any member can escalate to root without ticket.",
            "evidence": "visudo -c; grep -R NOPASSWD /etc/sudoers*",
            "cis": "CIS RHEL 8 5.3.x sudo",
            "stig": "RHEL-08-010380",
            "iso27001": "A.8.2 · A.8.3",
            "soc2": "CC6.1 · CC6.3",
            "pci": "7.1 · 7.2",
            "ref": "CIS-RHEL9 · QUALYS-SCA",
            "remediation": "Replace with command allow-lists; require ticket ID in sudo lecture; break-glass only for root.",
            "owner": "AppOps · IAM",
            "status": "In progress",
            "due": today + timedelta(days=14),
            "linked": "INC-2026-009 · PayrollCo · CMP-2026-001",
        },
        {
            "finding_id": "FND-UX-003",
            "host_id": "HOST-AIX",
            "domain_id": "FS",
            "severity": "Critical",
            "title": "NFS export /payroll with root= and no root squash",
            "detail": "/etc/exports: /payroll -sec=sys,rw,root=nsk-rhel-app01:JUMP-DMZ-03. Anyone root on those clients maps to AIX uid 0 on the payroll extract volume feeding PRODBOX.",
            "evidence": "exportfs -v; cat /etc/exports",
            "cis": "CIS AIX 7.3 5.x NFS",
            "stig": "AIX STIG V-917xx NFS",
            "iso27001": "A.8.12 · A.8.20",
            "soc2": "CC6.6 · CC6.7",
            "pci": "1.2 · 7.1",
            "ref": "CIS-AIX73 · POWERSC",
            "remediation": "Enable root squash; restrict to named Kerberos/NFSv4; move extract to SFTP with key auth.",
            "owner": "AIX Ops · R. Nair",
            "status": "Open",
            "due": today + timedelta(days=10),
            "linked": "PRODBOX · KRI-2026-002 · PAYMAST narrative",
        },
        {
            "finding_id": "FND-UX-004",
            "host_id": "HOST-SOL",
            "domain_id": "NET",
            "severity": "High",
            "title": "Telnet and rlogin SMF services still online",
            "detail": "svc:/network/telnet:default and rlogin online on nsk-sol-ora01. Legacy Oracle DBA habit — cleartext credentials across colo B DR network.",
            "evidence": "svcs -a | grep -E 'telnet|rlogin|rsh'",
            "cis": "CIS Solaris 11 3.x network services",
            "stig": "SOL11 STIG network legacy",
            "iso27001": "A.8.20 · A.8.22",
            "soc2": "CC6.6",
            "pci": "2.2 · 4.1",
            "ref": "CIS-SOL11",
            "remediation": "svcadm disable telnet rlogin rsh; enforce SSH-only; document exception if any vendor requires it.",
            "owner": "Oracle Ops · S. Berg",
            "status": "Open",
            "due": today + timedelta(days=21),
            "linked": "GAP-2026-001 · DST-2026-001",
        },
        {
            "finding_id": "FND-UX-005",
            "host_id": "HOST-AIX",
            "domain_id": "KERN",
            "severity": "Critical",
            "title": "PowerSC CIS/STIG profile never applied on nsk-aix-db01",
            "detail": "pscxpert / PowerSC GUI shows endpoint enrolled but last profile apply = never. AIX still at install defaults for many SEC_* attributes. Real Time Compliance FIM not watching /payroll or DB2 configs.",
            "evidence": "lssrc -s pscxpert; PowerSC GUI endpoint detail",
            "cis": "CIS AIX 7.3 profile apply",
            "stig": "AIX DoD STIG baseline",
            "iso27001": "A.8.9 · A.8.32",
            "soc2": "CC7.1 · CC8.1",
            "pci": "2.2 · 6.2",
            "ref": "POWERSC · CIS-AIX73",
            "remediation": "Apply PowerSC CIS Level 1 in change window; enable RTC on critical paths; weekly drift report to GRC.",
            "owner": "AIX Ops · Security",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "CMP-2026-001 · KRI-2026-002",
        },
        {
            "finding_id": "FND-UX-006",
            "host_id": "HOST-JUMP",
            "domain_id": "AUTH",
            "severity": "High",
            "title": "PAM MFA not enforced on jump; password quality weak",
            "detail": "authselect shows password-auth only — no pam_sss / Duo / okta pam. /etc/security/pwquality.conf: minlen=8, minclass=1. Shared colo night crew passwords rotated irregularly.",
            "evidence": "authselect current; grep -v '^#' /etc/security/pwquality.conf",
            "cis": "CIS RHEL 9 5.3 / 5.4 PAM",
            "stig": "RHEL-09-611010",
            "iso27001": "A.5.17 · A.8.5",
            "soc2": "CC6.1",
            "pci": "8.3 · 8.4",
            "ref": "CIS-RHEL9 · STIG-RHEL8",
            "remediation": "Enforce MFA PAM stack; minlen 15 minclass 4; block shared IDs.",
            "owner": "IAM · Platform Sec",
            "status": "In progress",
            "due": today + timedelta(days=14),
            "linked": "INC-2026-001 · AST-2026-005",
        },
        {
            "finding_id": "FND-UX-007",
            "host_id": "HOST-APP",
            "domain_id": "FS",
            "severity": "Critical",
            "title": "World-writable /opt/jde/drop and sticky-bit missing",
            "detail": "drwxrwxrwx root root /opt/jde/drop — PayrollCo inbound files land here before AIX NFS push. Any local user can plant or wipe extracts. No sticky bit; no ACL.",
            "evidence": "ls -ld /opt/jde/drop; getfacl /opt/jde/drop",
            "cis": "CIS RHEL 8 6.1.x file permissions",
            "stig": "RHEL-08-010700",
            "iso27001": "A.8.12",
            "soc2": "CC6.1 · CC6.7",
            "pci": "7.1 · 10.2",
            "ref": "CIS-RHEL9 · LYNIS",
            "remediation": "chmod 1770; group jde-drop only; enable audit watch; consider dedicated SFTP chroot.",
            "owner": "AppOps · M. Chen",
            "status": "Open",
            "due": today + timedelta(days=7),
            "linked": "PayrollCo · INC-2026-009 · FND-UX-003",
        },
        {
            "finding_id": "FND-UX-008",
            "host_id": "HOST-WEB",
            "domain_id": "NET",
            "severity": "High",
            "title": "firewalld inactive; nginx listens 0.0.0.0:80 without redirect",
            "detail": "systemctl is-active firewalld = inactive. nginx still serves HTTP on :80 with no HSTS/redirect to TLS — portal stuffing narrative used cleartext probing from DMZ.",
            "evidence": "systemctl status firewalld; ss -lntp | grep nginx",
            "cis": "CIS RHEL 9 3.4 firewall · 5.x web",
            "stig": "RHEL-09-251015",
            "iso27001": "A.8.20 · A.8.22",
            "soc2": "CC6.6",
            "pci": "1.2 · 4.1",
            "ref": "CIS-RHEL9 · QUALYS-SCA",
            "remediation": "Enable firewalld with minimal allow; force HTTPS redirect; terminate TLS at edge.",
            "owner": "WebOps · L. Duarte",
            "status": "Open",
            "due": today + timedelta(days=14),
            "linked": "INC-2026-001",
        },
        {
            "finding_id": "FND-UX-009",
            "host_id": "HOST-SOL",
            "domain_id": "AUD",
            "severity": "High",
            "title": "Solaris BSM / auditd equivalent disabled",
            "detail": "auditconfig -getcond shows auditing disabled. No trail for oracle user DDL or root SMF changes since 2025-11. Board IR reconstruct for DST-2026-001 cannot use this host.",
            "evidence": "auditconfig -getcond; svcs auditd",
            "cis": "CIS Solaris 11 4.x auditing",
            "stig": "SOL11 audit enable",
            "iso27001": "A.8.15 · A.8.16",
            "soc2": "CC7.2 · CC7.3",
            "pci": "10.2 · 10.3",
            "ref": "CIS-SOL11",
            "remediation": "Enable BSM with class lo,ad,ex,fw; ship to SIEM; 90-day retention.",
            "owner": "Oracle Ops · SecOps",
            "status": "Open",
            "due": today + timedelta(days=21),
            "linked": "DST-2026-001 · GAP-2026-001",
        },
        {
            "finding_id": "FND-UX-010",
            "host_id": "HOST-APP",
            "domain_id": "AUD",
            "severity": "Medium",
            "title": "auditd retention 7 days; space_left action ignore",
            "detail": "max_log_file_action = ignore · num_logs = 3 · approx 7 days of local trail. SIEM forwarder intermittently drops — same gap pattern as IBM i QAUDJRN 14-day receivers.",
            "evidence": "grep -E 'max_log|num_logs|space_left' /etc/audit/auditd.conf",
            "cis": "CIS RHEL 8 4.1.x auditd",
            "stig": "RHEL-08-030060",
            "iso27001": "A.8.15",
            "soc2": "CC7.2",
            "pci": "10.5 · 10.7",
            "ref": "CIS-RHEL9 · STIG-RHEL8",
            "remediation": "num_logs ≥ 20; space_left_action email+syslog; verify SIEM ACK.",
            "owner": "SecOps · AppOps",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "FND-IBMI-011 pattern · KRI-2026-001",
        },
        {
            "finding_id": "FND-UX-011",
            "host_id": "HOST-APP",
            "domain_id": "PATCH",
            "severity": "Critical",
            "title": "5 critical CVEs open >60 days including kernel and OpenSSH",
            "detail": "Qualys VMDR: CVE-2024-6387 (OpenSSH), kernel privilege CVEs, and openssl still Open on nsk-rhel-app01. Last full patch window cancelled during PayrollCo IR freeze.",
            "evidence": "Qualys host detection · dnf updateinfo list security",
            "cis": "CIS continuous patching · Qualys VMDR",
            "stig": "RHEL patch currency",
            "iso27001": "A.8.8",
            "soc2": "CC7.1 · CC8.1",
            "pci": "6.2 · 6.3",
            "ref": "QUALYS-SCA · CIS-RHEL9",
            "remediation": "Emergency patch CAB; reboot window; reopen freeze exception for security-only.",
            "owner": "AppOps · Patch Mgmt",
            "status": "Blocked",
            "due": today + timedelta(days=5),
            "linked": "INC-2026-009 · PayrollCo freeze",
        },
        {
            "finding_id": "FND-UX-012",
            "host_id": "HOST-JUMP",
            "domain_id": "PRIV",
            "severity": "High",
            "title": "SUID custom binary /usr/local/bin/jumpwrap owned by root",
            "detail": "Custom colo wrapper setuid root — wraps ssh to PRODBOX. Source not in git; last mtime 2024-06. Lynis and CIS both flag unknown SUID.",
            "evidence": "find /usr/local -perm -4000 -ls; rpm -qf /usr/local/bin/jumpwrap",
            "cis": "CIS RHEL 9 6.1.13 SUID",
            "stig": "RHEL-09-232020",
            "iso27001": "A.8.19",
            "soc2": "CC6.1 · CC8.1",
            "pci": "6.3 · 7.1",
            "ref": "LYNIS · CIS-RHEL9",
            "remediation": "Remove SUID; rewrite as sudoers allow-list; inventory all local SUID.",
            "owner": "Platform Sec",
            "status": "Open",
            "due": today + timedelta(days=14),
            "linked": "AST-2026-005 · JUMP-DMZ-03",
        },
        {
            "finding_id": "FND-UX-013",
            "host_id": "HOST-AIX",
            "domain_id": "AUTH",
            "severity": "High",
            "title": "AIX root remotely reachable; rhosts remnants",
            "detail": "/etc/security/user default rlogin=true for root · .rhosts files found under /home/oracle and /home/db2inst1 referencing retired jump host JUMP-DMZ-01.",
            "evidence": "lsuser -a rlogin root; find /home -name .rhosts",
            "cis": "CIS AIX 7.3 authentication",
            "stig": "AIX root remote",
            "iso27001": "A.5.15 · A.8.5",
            "soc2": "CC6.1",
            "pci": "2.2 · 8.2",
            "ref": "CIS-AIX73 · POWERSC",
            "remediation": "rlogin=false for root; delete .rhosts; SSH keys + PowerSC MFA profile.",
            "owner": "AIX Ops",
            "status": "Open",
            "due": today + timedelta(days=14),
            "linked": "FND-UX-001 · JUMP path",
        },
        {
            "finding_id": "FND-UX-014",
            "host_id": "HOST-SOL",
            "domain_id": "PRIV",
            "severity": "Critical",
            "title": "No RBAC — six admins share root password",
            "detail": "Oracle Ops team of 6 uses a shared root password in a sealed envelope + LastPass folder 'sol-ora-root'. pfexec / RBAC roles unused. Orbit AMS remote in 2025 used this path.",
            "evidence": "profiles -l; userattr ...; last root",
            "cis": "CIS Solaris 11 RBAC / privileges",
            "stig": "SOL11 privileged access",
            "iso27001": "A.5.15 · A.8.2",
            "soc2": "CC6.1 · CC6.2",
            "pci": "7.1 · 8.2",
            "ref": "CIS-SOL11",
            "remediation": "Named RBAC roles; break-glass root in PAM vault; rotate after any vendor remote.",
            "owner": "Oracle Ops · IAM",
            "status": "Open",
            "due": today + timedelta(days=21),
            "linked": "Orbit AMS · DST-2026-001 · CMP-2026-004",
        },
        {
            "finding_id": "FND-UX-015",
            "host_id": "HOST-JUMP",
            "domain_id": "KERN",
            "severity": "Medium",
            "title": "sysctl ip_forward=1 and rp_filter=0 on jump",
            "detail": "Jump host unexpectedly routing; reverse-path filter disabled. Increases pivot risk after credential theft.",
            "evidence": "sysctl net.ipv4.ip_forward net.ipv4.conf.all.rp_filter",
            "cis": "CIS RHEL 9 3.3.x network parameters",
            "stig": "RHEL-09-253010",
            "iso27001": "A.8.20",
            "soc2": "CC6.6",
            "pci": "1.2",
            "ref": "CIS-RHEL9",
            "remediation": "ip_forward=0; rp_filter=1; document if any NAT exception is intentional.",
            "owner": "Network · Platform Sec",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "AST-2026-005",
        },
        {
            "finding_id": "FND-UX-016",
            "host_id": "HOST-AIX",
            "domain_id": "PATCH",
            "severity": "High",
            "title": "AIX TL/SP 91 days stale; APARs for SSH and NFS open",
            "detail": "oslevel -s shows 7300-03-02 while 7300-03-04 available. Service pack delayed for DB2 regression fear after PowerHA test slip.",
            "evidence": "oslevel -s; instfix -i | grep -i openssh",
            "cis": "CIS AIX patch currency · PowerSC patch mgmt",
            "stig": "AIX patch",
            "iso27001": "A.8.8",
            "soc2": "CC8.1",
            "pci": "6.2",
            "ref": "POWERSC · CIS-AIX73",
            "remediation": "Schedule TL apply on HA secondary first; document DB2 regression tests.",
            "owner": "AIX Ops",
            "status": "In progress",
            "due": today + timedelta(days=45),
            "linked": "PRODBOX HA · KRI-2026-002",
        },
        {
            "finding_id": "FND-UX-017",
            "host_id": "HOST-WEB",
            "domain_id": "SSH",
            "severity": "Medium",
            "title": "Weak SSH ciphers and no MaxAuthTries limit",
            "detail": "Ciphers include 3des-cbc · MaxAuthTries unset (default 6 still high for portal-adjacent host).",
            "evidence": "sshd -T | grep -E 'ciphers|maxauthtries'",
            "cis": "CIS RHEL 9 5.2.13 / 5.2.5",
            "stig": "RHEL-09-255060",
            "iso27001": "A.8.24",
            "soc2": "CC6.6",
            "pci": "4.1 · 8.3",
            "ref": "CIS-RHEL9 · STIG-RHEL8",
            "remediation": "Modern cipher suite only; MaxAuthTries 3; fail2ban or firewall rate limit.",
            "owner": "WebOps",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "INC-2026-001",
        },
        {
            "finding_id": "FND-UX-018",
            "host_id": "HOST-SOL",
            "domain_id": "PATCH",
            "severity": "High",
            "title": "Solaris SRU 118 days behind; no IPS publisher mirror SLA",
            "detail": "pkg update dry-run shows 140+ packages including openssl and ntp. Host is DR-only but still holds readable EBS schemas.",
            "evidence": "pkg list -u | wc -l; pkg publisher",
            "cis": "CIS Solaris 11 patching",
            "stig": "SOL11 patch",
            "iso27001": "A.8.8",
            "soc2": "CC8.1",
            "pci": "6.2",
            "ref": "CIS-SOL11",
            "remediation": "Quarterly SRU cadence; or accelerate decommission and cut data exposure.",
            "owner": "Oracle Ops · Patch Mgmt",
            "status": "Open",
            "due": today + timedelta(days=60),
            "linked": "GAP-2026-001 decommission",
        },
    ]
    findings_df = pd.DataFrame(findings)

    # Hardening controls (sysctl / AIX SEC / Solaris) — baseline drift view
    baseline = pd.DataFrame(
        [
            {"host_id": "HOST-JUMP", "control": "PermitRootLogin", "desired": "prohibit-password", "current": "yes", "drift": True, "source": "sshd_config", "last_change": today - timedelta(days=400)},
            {"host_id": "HOST-JUMP", "control": "PasswordAuthentication", "desired": "no", "current": "yes", "drift": True, "source": "sshd_config", "last_change": today - timedelta(days=400)},
            {"host_id": "HOST-JUMP", "control": "net.ipv4.ip_forward", "desired": "0", "current": "1", "drift": True, "source": "sysctl", "last_change": today - timedelta(days=120)},
            {"host_id": "HOST-JUMP", "control": "net.ipv4.conf.all.rp_filter", "desired": "1", "current": "0", "drift": True, "source": "sysctl", "last_change": today - timedelta(days=120)},
            {"host_id": "HOST-APP", "control": "sudo NOPASSWD", "desired": "none / allow-list", "current": "deploy,payrollsvc ALL", "drift": True, "source": "sudoers.d", "last_change": today - timedelta(days=55)},
            {"host_id": "HOST-APP", "control": "/opt/jde/drop mode", "desired": "1770", "current": "0777", "drift": True, "source": "filesystem", "last_change": today - timedelta(days=12)},
            {"host_id": "HOST-APP", "control": "auditd num_logs", "desired": "≥20", "current": "3", "drift": True, "source": "auditd.conf", "last_change": today - timedelta(days=200)},
            {"host_id": "HOST-AIX", "control": "PowerSC CIS profile", "desired": "applied + RTC", "current": "enrolled / never applied", "drift": True, "source": "PowerSC", "last_change": today - timedelta(days=0)},
            {"host_id": "HOST-AIX", "control": "NFS root=", "desired": "none (root squash)", "current": "root=app01,JUMP", "drift": True, "source": "/etc/exports", "last_change": today - timedelta(days=33)},
            {"host_id": "HOST-AIX", "control": "root rlogin", "desired": "false", "current": "true", "drift": True, "source": "/etc/security/user", "last_change": today - timedelta(days=500)},
            {"host_id": "HOST-SOL", "control": "telnet SMF", "desired": "disabled", "current": "online", "drift": True, "source": "svcs", "last_change": today - timedelta(days=900)},
            {"host_id": "HOST-SOL", "control": "BSM audit", "desired": "enabled", "current": "disabled", "drift": True, "source": "auditconfig", "last_change": today - timedelta(days=180)},
            {"host_id": "HOST-SOL", "control": "RBAC roles", "desired": "named roles", "current": "shared root", "drift": True, "source": "profiles", "last_change": today - timedelta(days=600)},
            {"host_id": "HOST-WEB", "control": "firewalld", "desired": "active", "current": "inactive", "drift": True, "source": "systemd", "last_change": today - timedelta(days=40)},
            {"host_id": "HOST-WEB", "control": "SSH Ciphers", "desired": "modern only", "current": "includes 3des-cbc", "drift": True, "source": "sshd_config", "last_change": today - timedelta(days=220)},
            {"host_id": "HOST-JUMP", "control": "PAM MFA", "desired": "required", "current": "password only", "drift": True, "source": "authselect", "last_change": today - timedelta(days=90)},
            {"host_id": "HOST-APP", "control": "kernel patch age", "desired": "≤30 days", "current": "63 days", "drift": True, "source": "Qualys VMDR", "last_change": today - timedelta(days=63)},
            {"host_id": "HOST-AIX", "control": "oslevel TL", "desired": "current SP", "current": "91 days behind", "drift": True, "source": "oslevel", "last_change": today - timedelta(days=91)},
        ]
    )

    listeners = pd.DataFrame(
        [
            {"host_id": "HOST-JUMP", "proto": "tcp", "port": 22, "process": "sshd", "bind": "0.0.0.0", "risk": "High", "notes": "Password auth still on"},
            {"host_id": "HOST-JUMP", "proto": "tcp", "port": 2222, "process": "sshd (alt)", "bind": "0.0.0.0", "risk": "Medium", "notes": "Undocumented alt SSH"},
            {"host_id": "HOST-APP", "proto": "tcp", "port": 22, "process": "sshd", "bind": "10.20.20.0/24", "risk": "Medium", "notes": "App VLAN only — OK"},
            {"host_id": "HOST-APP", "proto": "tcp", "port": 21, "process": "vsftpd", "bind": "0.0.0.0", "risk": "Critical", "notes": "Cleartext FTP for legacy vendor"},
            {"host_id": "HOST-APP", "proto": "tcp", "port": 2049, "process": "nfsd", "bind": "0.0.0.0", "risk": "Critical", "notes": "NFS to AIX payroll"},
            {"host_id": "HOST-APP", "proto": "tcp", "port": 445, "process": "smbd", "bind": "0.0.0.0", "risk": "High", "notes": "Samba share for Windows finance"},
            {"host_id": "HOST-AIX", "proto": "tcp", "port": 22, "process": "sshd", "bind": "0.0.0.0", "risk": "Medium", "notes": "Should be jump-only"},
            {"host_id": "HOST-AIX", "proto": "tcp", "port": 50000, "process": "db2sysc", "bind": "10.20.30.14", "risk": "High", "notes": "DB2 · crown jewel"},
            {"host_id": "HOST-AIX", "proto": "tcp", "port": 2049, "process": "nfsd", "bind": "0.0.0.0", "risk": "Critical", "notes": "/payroll export"},
            {"host_id": "HOST-SOL", "proto": "tcp", "port": 23, "process": "in.telnetd", "bind": "0.0.0.0", "risk": "Critical", "notes": "Telnet online"},
            {"host_id": "HOST-SOL", "proto": "tcp", "port": 513, "process": "in.rlogind", "bind": "0.0.0.0", "risk": "Critical", "notes": "rlogin online"},
            {"host_id": "HOST-SOL", "proto": "tcp", "port": 1521, "process": "tnslsnr", "bind": "0.0.0.0", "risk": "High", "notes": "Oracle listener wide open"},
            {"host_id": "HOST-WEB", "proto": "tcp", "port": 80, "process": "nginx", "bind": "0.0.0.0", "risk": "High", "notes": "No HTTPS redirect"},
            {"host_id": "HOST-WEB", "proto": "tcp", "port": 443, "process": "nginx", "bind": "0.0.0.0", "risk": "Low", "notes": "TLS OK"},
            {"host_id": "HOST-WEB", "proto": "tcp", "port": 22, "process": "sshd", "bind": "10.40.40.0/24", "risk": "Low", "notes": "DMZ mgmt only"},
        ]
    )

    # World-writable / sensitive paths
    filesys = pd.DataFrame(
        [
            {"host_id": "HOST-APP", "path": "/opt/jde/drop", "mode": "0777", "owner": "root:root", "risk": "Critical", "issue": "World-writable drop for PayrollCo"},
            {"host_id": "HOST-APP", "path": "/opt/jde/bin/runbatch", "mode": "4755", "owner": "root:jde", "risk": "High", "issue": "Unexpected SUID"},
            {"host_id": "HOST-APP", "path": "/var/tmp/payroll_*.csv", "mode": "0666", "owner": "payrollsvc", "risk": "Critical", "issue": "Cleartext payroll extracts in tmp"},
            {"host_id": "HOST-AIX", "path": "/payroll", "mode": "0775", "owner": "bin:bin", "risk": "Critical", "issue": "NFS export root="},
            {"host_id": "HOST-AIX", "path": "/home/db2inst1/.rhosts", "mode": "0644", "owner": "db2inst1", "risk": "High", "issue": "Trusts retired JUMP-DMZ-01"},
            {"host_id": "HOST-JUMP", "path": "/usr/local/bin/jumpwrap", "mode": "4755", "owner": "root:root", "risk": "High", "issue": "Custom SUID not packaged"},
            {"host_id": "HOST-JUMP", "path": "/home/opsnight/.ssh/authorized_keys", "mode": "0644", "owner": "opsnight", "risk": "High", "issue": "Shared account + world-readable keys file"},
            {"host_id": "HOST-SOL", "path": "/export/home/oracle/.rhosts", "mode": "0600", "owner": "oracle", "risk": "High", "issue": "rhosts trust"},
            {"host_id": "HOST-SOL", "path": "/var/opt/oracle/backup", "mode": "0777", "owner": "oracle:dba", "risk": "Critical", "issue": "World-writable DB backups"},
            {"host_id": "HOST-WEB", "path": "/var/www/html/.env.bak", "mode": "0644", "owner": "nginx", "risk": "High", "issue": "Creds in web root backup"},
        ]
    )

    nfs_shares = pd.DataFrame(
        [
            {"host_id": "HOST-AIX", "export": "/payroll", "clients": "nsk-rhel-app01, JUMP-DMZ-03", "options": "rw,root=,sec=sys", "risk": "Critical", "notes": "No root squash"},
            {"host_id": "HOST-APP", "export": "/opt/jde/drop", "clients": "* (Samba)", "options": "guest ok = yes (Samba)", "risk": "Critical", "notes": "Finance Windows mapped drive"},
            {"host_id": "HOST-SOL", "export": "/export/home", "clients": "10.50.0.0/16", "options": "rw,anon=0", "risk": "High", "notes": "anon=0 is root map"},
        ]
    )

    # Privileged identities
    priv = pd.DataFrame(
        [
            {"host_id": "HOST-JUMP", "account": "root", "type": "uid0", "last_login": today - timedelta(days=1), "mfa": False, "notes": "Password SSH enabled"},
            {"host_id": "HOST-JUMP", "account": "opsnight", "type": "shared", "last_login": today - timedelta(days=3), "mfa": False, "notes": "Colo night crew shared ID"},
            {"host_id": "HOST-JUMP", "account": "jokonkwo", "type": "named sudo", "last_login": today - timedelta(days=0), "mfa": True, "notes": "Owner — OK"},
            {"host_id": "HOST-APP", "account": "payrollsvc", "type": "service sudo", "last_login": today - timedelta(days=0), "mfa": False, "notes": "NOPASSWD:ALL"},
            {"host_id": "HOST-APP", "account": "deploy", "type": "group sudo", "last_login": today - timedelta(days=1), "mfa": False, "notes": "12 members · NOPASSWD"},
            {"host_id": "HOST-AIX", "account": "root", "type": "uid0", "last_login": today - timedelta(days=5), "mfa": False, "notes": "rlogin=true"},
            {"host_id": "HOST-AIX", "account": "db2inst1", "type": "DB2 instance", "last_login": today - timedelta(days=0), "mfa": False, "notes": ".rhosts present"},
            {"host_id": "HOST-SOL", "account": "root", "type": "shared uid0", "last_login": today - timedelta(days=2), "mfa": False, "notes": "6 admins · envelope + LastPass"},
            {"host_id": "HOST-SOL", "account": "oracle", "type": "DBA", "last_login": today - timedelta(days=4), "mfa": False, "notes": "No RBAC role"},
        ]
    )

    # Synthetic audit volume
    days = pd.date_range(today - timedelta(days=29), today, freq="D")
    audit_rows = []
    for h, base in [("HOST-JUMP", 800), ("HOST-APP", 2200), ("HOST-AIX", 1400), ("HOST-SOL", 40), ("HOST-WEB", 900)]:
        for d in days:
            spike = 1.0
            if h == "HOST-JUMP" and (today - d).days == 16:
                spike = 3.4  # aligns with INC-2026-001
            if h == "HOST-APP" and (today - d).days in {9, 10}:
                spike = 2.1  # PayrollCo noise
            if h == "HOST-SOL":
                spike = 0.15  # BSM mostly off
            for etype, w in [("USER_AUTH", 0.35), ("USER_CMD", 0.25), ("SYSCALL", 0.2), ("CRED_ACQ", 0.1), ("CONFIG_CHANGE", 0.1)]:
                audit_rows.append(
                    {
                        "day": d,
                        "host_id": h,
                        "entry_type": etype,
                        "count": int(rng.poisson(base * w * spike) + 1),
                    }
                )
    audit_df = pd.DataFrame(audit_rows)

    # SSH config matrix
    ssh_matrix = pd.DataFrame(
        [
            {"host_id": "HOST-JUMP", "setting": "PermitRootLogin", "value": "yes", "cis": "prohibit-password", "status": "Fail"},
            {"host_id": "HOST-JUMP", "setting": "PasswordAuthentication", "value": "yes", "cis": "no", "status": "Fail"},
            {"host_id": "HOST-JUMP", "setting": "PubkeyAuthentication", "value": "yes", "cis": "yes", "status": "Pass"},
            {"host_id": "HOST-JUMP", "setting": "MaxAuthTries", "value": "6", "cis": "≤4", "status": "Fail"},
            {"host_id": "HOST-JUMP", "setting": "AllowUsers", "value": "(unset)", "cis": "explicit list", "status": "Fail"},
            {"host_id": "HOST-APP", "setting": "PermitRootLogin", "value": "no", "cis": "no", "status": "Pass"},
            {"host_id": "HOST-APP", "setting": "PasswordAuthentication", "value": "no", "cis": "no", "status": "Pass"},
            {"host_id": "HOST-APP", "setting": "Ciphers", "value": "modern", "cis": "modern", "status": "Pass"},
            {"host_id": "HOST-WEB", "setting": "PermitRootLogin", "value": "no", "cis": "no", "status": "Pass"},
            {"host_id": "HOST-WEB", "setting": "Ciphers", "value": "includes 3des-cbc", "cis": "modern only", "status": "Fail"},
            {"host_id": "HOST-WEB", "setting": "MaxAuthTries", "value": "6", "cis": "≤4", "status": "Fail"},
            {"host_id": "HOST-AIX", "setting": "PermitRootLogin", "value": "yes", "cis": "no", "status": "Fail"},
            {"host_id": "HOST-AIX", "setting": "PasswordAuthentication", "value": "yes", "cis": "no", "status": "Fail"},
            {"host_id": "HOST-SOL", "setting": "PermitRootLogin", "value": "yes", "cis": "no", "status": "Fail"},
            {"host_id": "HOST-SOL", "setting": "Protocol", "value": "2", "cis": "2", "status": "Pass"},
        ]
    )

    evidence_cmds = pd.DataFrame(
        [
            {"finding_id": "FND-UX-001", "host_id": "HOST-JUMP", "command": "sshd -T | grep -E 'permitrootlogin|passwordauthentication'", "output_excerpt": "permitrootlogin yes\\npasswordauthentication yes", "captured": today - timedelta(days=1), "tool": "sshd -T"},
            {"finding_id": "FND-UX-002", "host_id": "HOST-APP", "command": "grep -R NOPASSWD /etc/sudoers /etc/sudoers.d", "output_excerpt": "%deploy ALL=(ALL) NOPASSWD:ALL\\n%payrollsvc ALL=(ALL) NOPASSWD:ALL", "captured": today - timedelta(days=2), "tool": "visudo"},
            {"finding_id": "FND-UX-003", "host_id": "HOST-AIX", "command": "exportfs -v", "output_excerpt": "/payroll  nsk-rhel-app01(rw,root=...) JUMP-DMZ-03(rw,root=...)", "captured": today - timedelta(days=1), "tool": "exportfs"},
            {"finding_id": "FND-UX-004", "host_id": "HOST-SOL", "command": "svcs -a | grep -E 'telnet|rlogin'", "output_excerpt": "online  ... svc:/network/telnet:default\\nonline ... rlogin", "captured": today - timedelta(days=3), "tool": "svcs"},
            {"finding_id": "FND-UX-005", "host_id": "HOST-AIX", "command": "PowerSC GUI · profile history", "output_excerpt": "Endpoint enrolled · Last apply: never · RTC: off", "captured": today - timedelta(days=0), "tool": "PowerSC"},
            {"finding_id": "FND-UX-007", "host_id": "HOST-APP", "command": "ls -ld /opt/jde/drop", "output_excerpt": "drwxrwxrwx. 2 root root 4096 ... /opt/jde/drop", "captured": today - timedelta(days=1), "tool": "ls"},
            {"finding_id": "FND-UX-009", "host_id": "HOST-SOL", "command": "auditconfig -getcond", "output_excerpt": "audit condition = noaudit", "captured": today - timedelta(days=2), "tool": "auditconfig"},
            {"finding_id": "FND-UX-011", "host_id": "HOST-APP", "command": "Qualys VMDR critical detections", "output_excerpt": "5 Critical · oldest 63d · CVE-2024-6387 Open", "captured": today - timedelta(days=0), "tool": "Qualys"},
            {"finding_id": "FND-UX-012", "host_id": "HOST-JUMP", "command": "find /usr/local -perm -4000 -ls", "output_excerpt": "... /usr/local/bin/jumpwrap", "captured": today - timedelta(days=4), "tool": "find"},
            {"finding_id": "FND-UX-014", "host_id": "HOST-SOL", "command": "last root | head", "output_excerpt": "root pts/3 ... shared ops sessions · 6 distinct source IPs", "captured": today - timedelta(days=1), "tool": "last"},
        ]
    )

    tickets = pd.DataFrame(
        [
            {"ticket_id": "CHG-UX-1041", "finding_id": "FND-UX-001", "title": "Harden JUMP-DMZ-03 sshd (keys + no root pw)", "owner": "Platform Sec", "status": "CAB approved", "due": today + timedelta(days=7), "effort": "M"},
            {"ticket_id": "CHG-UX-1042", "finding_id": "FND-UX-002", "title": "Rewrite sudoers allow-lists on app01", "owner": "AppOps · IAM", "status": "In progress", "due": today + timedelta(days=14), "effort": "L"},
            {"ticket_id": "CHG-UX-1043", "finding_id": "FND-UX-003", "title": "NFS root squash + Kerberos on /payroll", "owner": "AIX Ops", "status": "Open", "due": today + timedelta(days=10), "effort": "L"},
            {"ticket_id": "CHG-UX-1044", "finding_id": "FND-UX-005", "title": "Apply PowerSC CIS L1 on nsk-aix-db01", "owner": "AIX Ops · Sec", "status": "Open", "due": today + timedelta(days=30), "effort": "XL"},
            {"ticket_id": "CHG-UX-1045", "finding_id": "FND-UX-007", "title": "Lock down /opt/jde/drop permissions", "owner": "AppOps", "status": "Open", "due": today + timedelta(days=7), "effort": "S"},
            {"ticket_id": "CHG-UX-1046", "finding_id": "FND-UX-011", "title": "Emergency patch app01 (OpenSSH/kernel)", "owner": "Patch Mgmt", "status": "Blocked", "due": today + timedelta(days=5), "effort": "M"},
            {"ticket_id": "CHG-UX-1047", "finding_id": "FND-UX-004", "title": "Disable Telnet/rlogin on sol-ora01", "owner": "Oracle Ops", "status": "Open", "due": today + timedelta(days=21), "effort": "S"},
            {"ticket_id": "CHG-UX-1048", "finding_id": "FND-UX-014", "title": "Solaris RBAC + vault root", "owner": "IAM · Oracle Ops", "status": "Open", "due": today + timedelta(days=21), "effort": "L"},
            {"ticket_id": "CHG-UX-1049", "finding_id": "FND-UX-008", "title": "firewalld + HTTPS redirect web01", "owner": "WebOps", "status": "In progress", "due": today + timedelta(days=14), "effort": "M"},
            {"ticket_id": "CHG-UX-1050", "finding_id": "FND-UX-009", "title": "Enable Solaris BSM → SIEM", "owner": "SecOps", "status": "Open", "due": today + timedelta(days=21), "effort": "M"},
        ]
    )

    hist = pd.DataFrame(
        [
            {"scan_id": "UX-SCAN-2025-Q4", "as_of": today - timedelta(days=120), "overall": 51, "critical": 9, "hosts": 5, "notes": "First multi-OS baseline"},
            {"scan_id": "UX-SCAN-2026-Q1", "as_of": today - timedelta(days=60), "overall": 48, "critical": 11, "hosts": 5, "notes": "PayrollCo freeze stalled patches"},
            {"scan_id": "UX-SCAN-2026-08", "as_of": today - timedelta(days=28), "overall": 46, "critical": 10, "hosts": 5, "notes": "Jump SSH still open post INC-2026-001"},
            {"scan_id": "UX-SCAN-2026-09", "as_of": today, "overall": 46, "critical": 8, "hosts": 5, "notes": "This assessment"},
        ]
    )

    frameworks = pd.DataFrame(
        [
            {"framework": "CIS Benchmarks (multi-OS)", "passing": 62, "failing": 48, "partial": 19, "readiness_pct": 48.0},
            {"framework": "DISA STIG (RHEL/AIX)", "passing": 41, "failing": 55, "partial": 22, "readiness_pct": 39.0},
            {"framework": "ISO 27001:2022", "passing": 28, "failing": 14, "partial": 11, "readiness_pct": 53.0},
            {"framework": "SOC 2 (CC6/CC7/CC8)", "passing": 22, "failing": 16, "partial": 9, "readiness_pct": 47.0},
            {"framework": "PCI DSS 4.0 (in-scope hosts)", "passing": 18, "failing": 21, "partial": 8, "readiness_pct": 38.0},
            {"framework": "IBM PowerSC profiles (AIX)", "passing": 0, "failing": 1, "partial": 0, "readiness_pct": 12.0},
        ]
    )

    crosswalk = findings_df[
        ["finding_id", "title", "severity", "cis", "stig", "iso27001", "soc2", "pci", "ref"]
    ].copy()

    narrative = pd.DataFrame(
        [
            {
                "lane": "Blast radius",
                "text": "JUMP-DMZ-03 is still a password-root SSH beachhead into AIX DB2 and PRODBOX-adjacent paths — same story as AST-2026-005 / INC-2026-001.",
            },
            {
                "lane": "Payroll path",
                "text": "World-writable JDE drop → NFS root= on AIX /payroll → PRODBOX PAYMAST narrative. PayrollCo freeze is blocking the patch ticket that would close critical CVEs on app01.",
            },
            {
                "lane": "Unix differentiators",
                "text": "AIX PowerSC profile never applied; Solaris still runs Telnet/rlogin with shared root and BSM off — legacy DR host that audit cannot reconstruct.",
            },
            {
                "lane": "Prior scan",
                "text": "Overall score flat at 46% for two cycles (−2 pts since Q4). Critical count down slightly, but privileged and filesystem domains remain Red.",
            },
        ]
    )

    deep = {
        "FND-UX-001": {
            "memo": "Jump hardening was promised in the INC-2026-001 post-incident plan. Colo night crew refused key-only until a break-glass runbook exists — draft is in GRC but unsigned.",
            "counterfactual": "With password root SSH open, a single phished opsnight session pivots to AIX DB2 and IBM i via existing trusts.",
            "commands": ["sshd -T", "grep opsnight /etc/passwd", "last opsnight"],
        },
        "FND-UX-002": {
            "memo": "deploy NOPASSWD landed during a 2025 go-live fire drill and was never wound back. payrollsvc inherited the same pattern for 'automation'.",
            "counterfactual": "Any CI runner or compromised SFTP credential becomes instant root on the PayrollCo landing host.",
            "commands": ["visudo -c", "getent group deploy"],
        },
        "FND-UX-003": {
            "memo": "NFS root= was added so app01 could chown extracts 'for DB2'. Security exception expired 2025-12; still in production.",
            "counterfactual": "Root on JUMP or app01 = uid 0 on the payroll volume — classic Unix lateral.",
            "commands": ["exportfs -v", "showmount -e nsk-aix-db01"],
        },
        "FND-UX-005": {
            "memo": "PowerSC licenses purchased after the IBM i assessment push; AIX endpoint enrolled for a PoC that never got a change window.",
            "counterfactual": "Without CIS/STIG apply + RTC, drift on SEC_* and /payroll is invisible until the next manual scan.",
            "commands": ["lssrc -s pscxpert", "PowerSC GUI drift report"],
        },
        "FND-UX-007": {
            "memo": "Mode 777 was a 'temporary' fix when Finance Windows mapping broke ACLs. Ticket closed as done without verification.",
            "counterfactual": "Local unprivileged user plants malware in the payroll drop — lands on AIX and toward PRODBOX.",
            "commands": ["ls -ld /opt/jde/drop", "auditctl -w /opt/jde/drop -p wa"],
        },
        "FND-UX-009": {
            "memo": "BSM disabled years ago for 'performance on SPARC'. No compensating FIM.",
            "counterfactual": "DST-2026-001-style vendor remote leaves no local forensic trail.",
            "commands": ["auditconfig -getcond", "svcs auditd"],
        },
        "FND-UX-011": {
            "memo": "Patch CAB blocked by PayrollCo IR freeze language that Security Legal interpreted as all change — need explicit security-only carve-out.",
            "counterfactual": "OpenSSH regreSSHion-class exposure on the SFTP host facing a third party.",
            "commands": ["dnf updateinfo list security", "Qualys VMDR host view"],
        },
        "FND-UX-014": {
            "memo": "Same shared-root culture called out on IBM i SST/DST. Orbit AMS used the envelope password in 2025-04.",
            "counterfactual": "No attribution if EBS schemas are copied off DR — six people and a vendor all look the same in logs (when logs exist).",
            "commands": ["profiles -l", "last root"],
        },
    }

    scan_meta = {
        "scan_id": "UX-SCAN-2026-09",
        "as_of": today,
        "primary_host": "JUMP-DMZ-03",
        "overall_score": 46,
        "overall_rag": _rag(46),
        "delta_pts": 0,
        "prior_scan": "UX-SCAN-2026-08",
        "duration_min": 38,
        "tool_pattern": "CIS/STIG · Qualys SCA · PowerSC · Lynis-class domains",
        "references": "CIS RHEL/AIX/Solaris · DISA STIG · IBM PowerSC · NIST 800-53",
        "hosts_in_scope": 5,
    }

    return (
        hosts,
        domains,
        findings_df,
        baseline,
        listeners,
        filesys,
        nfs_shares,
        priv,
        audit_df,
        ssh_matrix,
        evidence_cmds,
        tickets,
        hist,
        frameworks,
        crosswalk,
        narrative,
        scan_meta,
        pd.DataFrame(REFERENCES),
        deep,
    )


def _sync(seed: int):
    keys = [
        "ux_hosts",
        "ux_domains",
        "ux_findings",
        "ux_baseline",
        "ux_listeners",
        "ux_filesys",
        "ux_nfs",
        "ux_priv",
        "ux_audit",
        "ux_ssh",
        "ux_evidence",
        "ux_tickets",
        "ux_hist",
        "ux_frameworks",
        "ux_crosswalk",
        "ux_narrative",
        "ux_scan_meta",
        "ux_refs",
        "ux_deep",
    ]
    need = st.session_state.get(_SYNC_KEY) != seed or "ux_findings" not in st.session_state
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


def _finding_card(
    row,
    *,
    widget_key: str,
    deep: dict | None = None,
    evidence: pd.DataFrame | None = None,
    tickets: pd.DataFrame | None = None,
):
    st.markdown(f"### {row['finding_id']} · {row['title']}")
    a, b, c, d = st.columns(4)
    a.metric("Severity", row["severity"])
    b.metric("Domain", row["domain_id"])
    c.metric("Status", row["status"])
    d.metric("Due", _fmt(row["due"]))
    st.write(row["detail"])
    c1, c2 = st.columns(2)
    c1.write(f"**Evidence cmd:** `{row['evidence']}`")
    c1.write(f"**Owner:** {row['owner']} · **Host:** {row['host_id']}")
    c1.write(f"**Linked:** {row['linked']}")
    c2.write(f"**Remediation:** {row['remediation']}")
    c2.write(f"**CIS:** {row['cis']} · **STIG:** {row['stig']}")
    c2.write(f"**ISO 27001:** {row['iso27001']} · **SOC 2:** {row['soc2']} · **PCI:** {row['pci']}")
    c2.write(f"**Refs:** {row['ref']}")

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
        title="Unix/Linux Security Assessment",
        lede="Multi-OS posture workbench — CIS/STIG domain scoring across RHEL, AIX, and Solaris. Qualys SCA / Tenable CIS patterns, IBM PowerSC for AIX, Oracle Solaris BSM/RBAC, Lynis-class controls. Synthetic NorthStack estate (JUMP-DMZ-03 and friends).",
        kicker="Linux · AIX · Solaris",
    )

    seed = demo_kit.seed_controls()
    (
        hosts,
        domains,
        findings,
        baseline,
        listeners,
        filesys,
        nfs_shares,
        priv,
        audit_df,
        ssh_matrix,
        evidence,
        tickets,
        hist,
        frameworks,
        crosswalk,
        narrative,
        scan_meta,
        refs,
        deep,
    ) = _sync(seed)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Scan scope")
    host_opts = ["All hosts"] + hosts["hostname"].tolist()
    host_pick = st.sidebar.selectbox("Host", host_opts, index=1)
    family_opts = ["All OS"] + sorted(hosts["os_family"].unique().tolist())
    family_pick = st.sidebar.selectbox("OS family", family_opts, index=0)
    sev_f = st.sidebar.multiselect("Severities", SEVERITY, default=["Critical", "High", "Medium"])
    open_only = st.sidebar.checkbox("Open / in progress / blocked only", value=True)
    st.sidebar.caption("Sample assessment — not connected to live hosts.")

    view_f = findings.copy()
    if host_pick != "All hosts":
        hid = hosts[hosts["hostname"] == host_pick]["host_id"].iloc[0]
        view_f = view_f[view_f["host_id"] == hid]
    if family_pick != "All OS":
        fam_hosts = hosts[hosts["os_family"] == family_pick]["host_id"]
        view_f = view_f[view_f["host_id"].isin(fam_hosts)]
    view_f = view_f[view_f["severity"].isin(sev_f)]
    if open_only:
        view_f = view_f[view_f["status"].isin(["Open", "In progress", "Blocked"])]

    overall = scan_meta["overall_score"]
    crit = int((findings["severity"] == "Critical").sum())
    high = int((findings["severity"] == "High").sum())
    drift = int(baseline["drift"].sum())
    open_tk = int(tickets["status"].apply(lambda s: s not in {"Closed", "Done"}).sum())
    crit_fs = int((filesys["risk"] == "Critical").sum())
    crit_listen = int((listeners["risk"] == "Critical").sum())
    cis_ready = float(frameworks[frameworks["framework"].str.contains("CIS")]["readiness_pct"].iloc[0])
    patch_lag = int(hosts["days_since_patch"].max())

    k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)
    k1.metric("Overall score", f"{overall}%", delta=f"{scan_meta.get('delta_pts', 0):+d} vs prior")
    k2.metric("Critical", crit)
    k3.metric("High", high)
    k4.metric("Baseline drift", drift)
    k5.metric("Open tickets", open_tk)
    k6.metric("Crit FS paths", crit_fs)
    k7.metric("Crit listeners", crit_listen)
    k8.metric("CIS ready", f"{cis_ready:.0f}%")

    if overall < 55:
        st.error(
            f"Scan {scan_meta['scan_id']} — estate is Red overall "
            f"({scan_meta.get('delta_pts', 0):+d} vs {scan_meta.get('prior_scan', 'prior')}). "
            "Jump SSH, sudo NOPASSWD, NFS root=, and PowerSC/Solaris gaps dominate residual risk."
        )
    elif crit:
        st.warning(f"{crit} critical findings open — treat JUMP SSH, payroll FS path, and AIX PowerSC before board packet.")

    (
        work,
        domains_tab,
        findings_tab,
        hosts_tab,
        ssh_tab,
        fs_tab,
        net_tab,
        aud_tab,
        aix_sol_tab,
        cross_tab,
        base_tab,
        board_tab,
        export_tab,
    ) = st.tabs(
        [
            "Workbench",
            "Scan domains",
            "Findings",
            "Hosts",
            "SSH / auth",
            "Filesystem / NFS",
            "Listeners",
            "Audit trails",
            "AIX / Solaris",
            "Crosswalk",
            "Baseline / CIS",
            "Board brief",
            "Export",
        ]
    )

    with work:
        st.subheader("Unix/Linux posture workbench")
        st.caption(
            f"**{scan_meta['scan_id']}** · {_fmt(scan_meta['as_of'])} · ~{scan_meta.get('duration_min', 30)} min · "
            f"{scan_meta['hosts_in_scope']} hosts · {scan_meta['tool_pattern']} · Refs: {scan_meta['references']}"
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
                st.write(
                    f"**Finding:** {t['finding_id']} · **Owner:** {t['owner']} · "
                    f"**Status:** {t['status']} · **Effort:** {t['effort']}"
                )

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
                title="Domain scores (CIS / Lynis-class)",
            )
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(yaxis_range=[0, 105], height=360)
            st.plotly_chart(fig, use_container_width=True, key="plotly_ux_domains")
        with c2:
            fig = px.line(hist, x="as_of", y="overall", markers=True, title="Overall score trend (prior scans)")
            fig.update_layout(height=360)
            st.plotly_chart(fig, use_container_width=True, key="plotly_ux_hist")

        st.markdown("**Hosts in scope**")
        st.dataframe(
            hosts[
                [
                    "hostname",
                    "os_family",
                    "os",
                    "role",
                    "days_since_patch",
                    "open_cves_crit",
                    "crown_jewel",
                    "owner",
                    "linked",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(f"**Featured findings ({len(FEATURED_FINDINGS)})**")
        pref = [
            "FND-UX-001",
            "FND-UX-002",
            "FND-UX-003",
            "FND-UX-005",
            "FND-UX-007",
            "FND-UX-009",
            "FND-UX-011",
            "FND-UX-014",
        ]
        feat = findings[findings["finding_id"].isin(FEATURED_FINDINGS)].copy()
        feat["_o"] = feat["finding_id"].map(lambda x: pref.index(x) if x in pref else 99)
        for _, row in feat.sort_values("_o").iterrows():
            st.markdown("---")
            _finding_card(row, widget_key=f"feat_{row['finding_id']}", deep=deep, evidence=evidence, tickets=tickets)

    with domains_tab:
        st.subheader("Scan domains")
        st.caption("Eight assessment areas aligned to CIS Benchmark / Lynis / Qualys SCA report sections.")
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
        search = st.text_input("Search findings", placeholder="JUMP, NFS, PowerSC, sudo…", key="ux_fnd_search")
        show = view_f
        if search.strip():
            q = search.strip().lower()
            show = show[show.apply(lambda r: q in " ".join(str(v).lower() for v in r), axis=1)]
        st.dataframe(
            show[
                [
                    "finding_id",
                    "host_id",
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
            pick = st.selectbox("Drill into finding", show["finding_id"].tolist(), key="ux_fnd_pick")
            row = show[show["finding_id"] == pick].iloc[0]
            _finding_card(row, widget_key="drill", deep=deep, evidence=evidence, tickets=tickets)

        by_sev = findings.groupby("severity").size().reset_index(name="count")
        fig = px.bar(by_sev, x="severity", y="count", color="severity", title="Findings by severity")
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_sev")

    with hosts_tab:
        st.subheader("Host inventory")
        st.caption("RHEL jump/app/web · AIX DB2 · Solaris Oracle — crown jewels tagged.")
        st.dataframe(hosts, use_container_width=True, hide_index=True)
        fig = px.bar(
            hosts,
            x="hostname",
            y="days_since_patch",
            color="os_family",
            title=f"Days since last patch (max lag {patch_lag}d)",
            text="open_cves_crit",
        )
        fig.update_traces(texttemplate="CVE crit %{text}", textposition="outside")
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_patch_lag")
        st.markdown("**Privileged identities**")
        st.dataframe(priv.assign(last_login=priv["last_login"].map(_fmt)), use_container_width=True, hide_index=True)

    with ssh_tab:
        st.subheader("SSH / authentication posture")
        st.caption("sshd_config vs CIS — jump and AIX still fail PermitRootLogin / PasswordAuthentication.")
        st.dataframe(ssh_matrix, use_container_width=True, hide_index=True)
        fail_n = int((ssh_matrix["status"] == "Fail").sum())
        st.error(f"{fail_n} of {len(ssh_matrix)} SSH controls failing CIS desired state.")
        fig = px.histogram(ssh_matrix, x="status", color="host_id", barmode="group", title="SSH control pass/fail by host")
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_ssh")

    with fs_tab:
        st.subheader("Filesystem, SUID & NFS / shares")
        st.caption("World-writable drops and NFS root= are the Unix classic — same payroll path as IBM i PAYMAST.")
        st.markdown("**Sensitive paths**")
        st.dataframe(filesys, use_container_width=True, hide_index=True)
        hot = filesys[filesys["risk"].isin(["Critical", "High"])]
        st.warning(f"{len(hot)} paths Critical/High — /opt/jde/drop and /payroll lead.")
        st.markdown("**NFS / Samba exports**")
        st.dataframe(nfs_shares, use_container_width=True, hide_index=True)
        st.markdown("**Command evidence register**")
        st.dataframe(
            evidence.assign(captured=evidence["captured"].map(_fmt)),
            use_container_width=True,
            hide_index=True,
        )

    with net_tab:
        st.subheader("Network listeners")
        st.caption("ss / netstat-style sample — Telnet, FTP, NFS, and wide Oracle listener.")
        st.dataframe(listeners, use_container_width=True, hide_index=True)
        fig = px.bar(
            listeners,
            x="port",
            y="host_id",
            color="risk",
            orientation="h",
            title="Listener risk by host/port",
            hover_data=["process", "bind", "notes"],
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_listen")

    with aud_tab:
        st.subheader("Audit trail volume (synthetic)")
        st.caption("Spike on JUMP ~day −16 aligns with portal stuffing (INC-2026-001). Solaris near-flat — BSM off.")
        daily = audit_df.groupby(["day", "host_id"], as_index=False)["count"].sum()
        fig = px.area(daily, x="day", y="count", color="host_id", title="Audit events by host")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_aud")
        by_type = audit_df.groupby("entry_type", as_index=False)["count"].sum()
        fig2 = px.bar(by_type, x="entry_type", y="count", title="Events by type (30d)")
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True, key="plotly_ux_aud_type")
        st.warning("app01 auditd retention ~7 days (FND-UX-010); Solaris BSM disabled (FND-UX-009).")

    with aix_sol_tab:
        st.subheader("AIX & Solaris differentiators")
        st.caption("IBM PowerSC + CIS AIX · Oracle Solaris CIS / BSM / RBAC — why this isn't a Linux-only scanner.")
        aix_h = hosts[hosts["os_family"] == "AIX"]
        sol_h = hosts[hosts["os_family"] == "Solaris"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**AIX (PowerSC)**")
            st.dataframe(aix_h, use_container_width=True, hide_index=True)
            aix_f = findings[findings["host_id"].isin(aix_h["host_id"])]
            st.dataframe(
                aix_f[["finding_id", "severity", "title", "status"]].sort_values("severity"),
                use_container_width=True,
                hide_index=True,
            )
            st.info("PowerSC endpoint enrolled but CIS/STIG profile never applied — RTC FIM off on /payroll.")
        with c2:
            st.markdown("**Solaris**")
            st.dataframe(sol_h, use_container_width=True, hide_index=True)
            sol_f = findings[findings["host_id"].isin(sol_h["host_id"])]
            st.dataframe(
                sol_f[["finding_id", "severity", "title", "status"]].sort_values("severity"),
                use_container_width=True,
                hide_index=True,
            )
            st.error("Telnet/rlogin online · BSM off · shared root — DR host still holds readable EBS schemas.")
        with st.expander("Recommended PowerSC apply sequence (sample)"):
            st.write(
                "1. CAB for CIS Level 1 on nsk-aix-db01 (HA secondary first) · "
                "2. Enable Real Time Compliance watches on /payroll and DB2 configs · "
                "3. Weekly drift → GRC · 4. Retire NFS root= in same window as FND-UX-003."
            )

    with cross_tab:
        st.subheader("Compliance crosswalk")
        st.caption("Each finding mapped to CIS, STIG, ISO 27001, SOC 2, and PCI — reuse evidence across audits.")
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
        fig.update_layout(height=360, xaxis_tickangle=-25)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_cross_stack")
        st.markdown("**Authoritative references**")
        st.dataframe(refs, use_container_width=True, hide_index=True)

    with base_tab:
        st.subheader("Hardening baseline vs current")
        st.caption("Desired CIS/STIG/PowerSC state vs live — drift drives the Red domains.")
        show_b = baseline.copy()
        show_b["last_change"] = show_b["last_change"].map(_fmt)
        st.dataframe(show_b, use_container_width=True, hide_index=True)
        drifted = baseline[baseline["drift"]]
        st.error(f"{len(drifted)} of {len(baseline)} controls drifted — SSH, sudo, NFS, PowerSC, BSM.")
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
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_baseline_gauge")
        st.markdown("**Prior scan history**")
        st.dataframe(hist.assign(as_of=hist["as_of"].map(_fmt)), use_container_width=True, hide_index=True)

    with board_tab:
        st.subheader("Board / CISO brief — Unix/Linux")
        st.markdown(
            f"**Scan:** {scan_meta['scan_id']} · primary **{scan_meta['primary_host']}** "
            f"({_fmt(scan_meta['as_of'])}) · Overall **{overall}% ({scan_meta['overall_rag']})** · "
            f"Δ {scan_meta.get('delta_pts', 0):+d} vs {scan_meta.get('prior_scan', 'prior')}"
        )
        st.markdown("#### Headline")
        st.write(
            f"NorthStack Unix/Linux estate scores **{overall}%** across **5** hosts (RHEL, AIX, Solaris). "
            f"**{crit} critical** and **{high} high** findings. "
            f"**JUMP-DMZ-03** still allows root password SSH; **nsk-rhel-app01** has sudo NOPASSWD and a world-writable "
            f"PayrollCo drop; **nsk-aix-db01** exports /payroll with root= and has never applied PowerSC CIS; "
            f"**nsk-sol-ora01** runs Telnet with shared root and BSM off. Patch ticket on app01 is **Blocked** by PayrollCo freeze."
        )
        st.markdown("#### Domain RAG")
        for _, r in domains.iterrows():
            st.write(f"- **{r['domain']}:** {r['rag']} {r['score']}% ({int(r['fails'])} fails) — {r['benchmark']}")
        st.markdown("#### Top asks (30 days)")
        for fid in ["FND-UX-001", "FND-UX-002", "FND-UX-003", "FND-UX-007", "FND-UX-005", "FND-UX-011", "FND-UX-014"]:
            row = findings[findings["finding_id"] == fid].iloc[0]
            st.write(f"- **{fid}** ({row['severity']}): {row['title']}")
        st.markdown("#### Change tickets in flight")
        for _, t in tickets.head(7).iterrows():
            st.write(f"- **{t['ticket_id']}** [{t['status']}]: {t['title']}")
        st.markdown("#### Framework impact")
        st.write(
            f"CIS **{frameworks.iloc[0]['readiness_pct']:.0f}%** · "
            f"STIG **{frameworks.iloc[1]['readiness_pct']:.0f}%** · "
            f"ISO **{frameworks.iloc[2]['readiness_pct']:.0f}%** · "
            f"SOC 2 **{frameworks.iloc[3]['readiness_pct']:.0f}%** · "
            f"PCI **{frameworks.iloc[4]['readiness_pct']:.0f}%** · "
            f"PowerSC **{frameworks.iloc[5]['readiness_pct']:.0f}%**."
        )
        st.markdown("#### Linked portfolio")
        st.write(
            "INC-2026-001 · INC-2026-009 · AST-2026-005 · JUMP-DMZ-03 · PRODBOX · "
            "KRI-2026-001/002 · CMP-2026-001 · GAP-2026-001 · DST-2026-001 · "
            "PayrollCo · Orbit AMS · IBM i assessment narrative"
        )

    with export_tab:
        st.subheader("Export")
        demo_kit.csv_download(findings.assign(due=findings["due"].map(_fmt)), "ux_findings.csv", label="Download findings")
        demo_kit.csv_download(domains, "ux_domain_scores.csv", label="Download domain scores")
        demo_kit.csv_download(hosts, "ux_hosts.csv", label="Download hosts")
        demo_kit.csv_download(ssh_matrix, "ux_ssh_matrix.csv", label="Download SSH matrix")
        demo_kit.csv_download(filesys, "ux_filesystem.csv", label="Download filesystem findings")
        demo_kit.csv_download(nfs_shares, "ux_nfs_shares.csv", label="Download NFS/Samba shares")
        demo_kit.csv_download(listeners, "ux_listeners.csv", label="Download listeners")
        demo_kit.csv_download(priv.assign(last_login=priv["last_login"].map(_fmt)), "ux_privileged.csv", label="Download privileged IDs")
        demo_kit.csv_download(evidence.assign(captured=evidence["captured"].map(_fmt)), "ux_command_evidence.csv", label="Download command evidence")
        demo_kit.csv_download(tickets.assign(due=tickets["due"].map(_fmt)), "ux_remediation_tickets.csv", label="Download remediation tickets")
        demo_kit.csv_download(crosswalk, "ux_crosswalk.csv", label="Download compliance crosswalk")
        demo_kit.csv_download(
            baseline.assign(last_change=baseline["last_change"].map(_fmt)),
            "ux_baseline.csv",
            label="Download baseline drift",
        )
        demo_kit.csv_download(frameworks, "ux_framework_readiness.csv", label="Download framework readiness")
        summary = pd.DataFrame(
            [
                {"metric": "scan_id", "value": scan_meta["scan_id"]},
                {"metric": "overall_score", "value": overall},
                {"metric": "overall_rag", "value": scan_meta["overall_rag"]},
                {"metric": "delta_vs_prior", "value": scan_meta.get("delta_pts", 0)},
                {"metric": "critical", "value": crit},
                {"metric": "high", "value": high},
                {"metric": "baseline_drift", "value": drift},
                {"metric": "open_tickets", "value": open_tk},
                {"metric": "hosts_in_scope", "value": scan_meta["hosts_in_scope"]},
            ]
        )
        demo_kit.csv_download(summary, "ux_executive_summary.csv", label="Download executive summary")


if __name__ == "__main__":
    main()
