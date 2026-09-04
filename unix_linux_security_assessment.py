#!/usr/bin/env python3
"""Unix/Linux security assessment workbench â€” club teaching toy.

Best-in-breed Unix/Linux posture patterns in one board:
  Â· Qualys VMDR + Policy Compliance / Tenable CIS host audit
  Â· OpenSCAP / SCAP Security Guide rule evidence (XCCDF)
  Â· Lynis hardening index (pulse check, not auditor evidence)
  Â· Tripwire / AIDE / Wazuh FIM + IBM PowerSC Real Time Compliance
  Â· SELinux / AppArmor / AIX TCB mandatory access
  Â· IBM PowerSC (pscxpert, Trusted Logging/Boot/Firewall, MFA)
  Â· Oracle Solaris ``compliance`` assessor (benchmark + PCI)

Synthetic NorthStack estate (JUMP-DMZ-03 and friends) â€” not a live scan.
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
    page_title="Unix/Linux Security Assessment Â· i on GRC",
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
    ("KERN", "Kernel / sysctl / MAC", "#a855f7"),
    ("AUD", "Audit / FIM / logging", "#ec4899"),
    ("PATCH", "Patch & package currency", "#14b8a6"),
]

SEVERITY = ["Critical", "High", "Medium", "Low", "Info"]
FEATURED_FINDINGS = {
    "FND-UX-001",
    "FND-UX-002",
    "FND-UX-003",
    "FND-UX-005",
    "FND-UX-007",
    "FND-UX-011",
    "FND-UX-019",
    "FND-UX-020",
    "FND-UX-021",
    "FND-UX-014",
}
_SYNC_KEY = "_ux_assess_v2"

REFERENCES = [
    {"id": "CIS-RHEL9", "title": "CIS Red Hat Enterprise Linux 9 Benchmark", "use": "SSH, PAM, sudo, sysctl, SELinux"},
    {"id": "CIS-AIX73", "title": "CIS IBM AIX 7.3 Benchmark", "use": "PowerSC profiles, TCB, NFS"},
    {"id": "CIS-SOL11", "title": "CIS Oracle Solaris 11 Benchmark", "use": "SMF, BSM, RBAC"},
    {"id": "STIG-RHEL8", "title": "DISA STIG RHEL 8 / 9", "use": "DoD hardening Â· OpenSCAP SSG"},
    {"id": "OPENSCAP", "title": "OpenSCAP / SCAP Security Guide", "use": "XCCDF rule pass/fail Â· auditor HTML"},
    {"id": "POWERSC", "title": "IBM PowerSC (pscxpert / RTC / Trusted*)", "use": "AIX CIS/STIG Â· FIM Â· Trusted Logging"},
    {"id": "SOL-COMPLY", "title": "Oracle Solaris compliance(8) assessor", "use": "Solaris Benchmark Â· PCI-DSS SCAP"},
    {"id": "LYNIS", "title": "Lynis / CISOfy hardening index", "use": "Fast pulse score Â· warnings trend"},
    {"id": "QUALYS-VMDR", "title": "Qualys VMDR + Policy Compliance", "use": "CVE queue + CIS continuous config"},
    {"id": "TENABLE", "title": "Tenable CIS / DISA host audit", "use": "Authenticated policy compliance"},
    {"id": "TRIPWIRE", "title": "Tripwire / AIDE / Wazuh FIM", "use": "Integrity baselines Â· change detect"},
    {"id": "NIST-800-53", "title": "NIST SP 800-53 Rev. 5", "use": "AC / AU / CM / IA / SC / SI families"},
]


def _today() -> pd.Timestamp:
    return pd.Timestamp.now().normalize()


def _fmt(ts) -> str:
    if ts is None:
        return "â€”"
    try:
        if pd.isna(ts):
            return "â€”"
    except (TypeError, ValueError):
        pass
    try:
        return pd.Timestamp(ts).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return "â€”"


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
                "site": "NorthStack colo A Â· cage 12 Â· DMZ VLAN 40",
                "cpu_pct": 18,
                "mem_pct": 41,
                "disk_pct": 52,
                "users": 38,
                "sudoers": 14,
                "suid_bins": 62,
                "listeners": 9,
                "open_cves_crit": 2,
                "days_since_patch": 47,
                "lynis_index": 58,
                "openscap_pass_pct": 41,
                "mac_mode": "SELinux enforcing",
                "fim_tool": "None (AIDE not initialized)",
                "agent": "Qualys Cloud Agent Â· CrowdStrike Falcon",
                "crown_jewel": True,
                "owner": "Platform Sec Â· J. Okonkwo",
                "linked": "AST-2026-005 Â· INC-2026-001 Â· KRI-2026-001",
            },
            {
                "host_id": "HOST-APP",
                "hostname": "nsk-rhel-app01",
                "fqdn": "nsk-rhel-app01.northstack.internal",
                "os_family": "Linux",
                "os": "RHEL 8.10",
                "kernel": "4.18.0-553.22.1.el8_10",
                "role": "JDE World middleware / SFTP drop to PayrollCo",
                "site": "NorthStack colo A Â· cage 12 Â· App VLAN 20",
                "cpu_pct": 64,
                "mem_pct": 71,
                "disk_pct": 68,
                "users": 112,
                "sudoers": 27,
                "suid_bins": 88,
                "listeners": 14,
                "open_cves_crit": 5,
                "days_since_patch": 63,
                "lynis_index": 49,
                "openscap_pass_pct": 36,
                "mac_mode": "SELinux permissive",
                "fim_tool": "Wazuh FIM (partial Â· drop path excluded)",
                "agent": "Qualys Cloud Agent Â· Wazuh",
                "crown_jewel": True,
                "owner": "AppOps Â· M. Chen",
                "linked": "PayrollCo Â· INC-2026-009 Â· AST-2026-012",
            },
            {
                "host_id": "HOST-AIX",
                "hostname": "nsk-aix-db01",
                "fqdn": "nsk-aix-db01.northstack.internal",
                "os_family": "AIX",
                "os": "AIX 7.3 TL3 SP2",
                "kernel": "7300-03-02-2446",
                "role": "DB2 LUW Â· payroll extract / PRODBOX feed",
                "site": "NorthStack colo A Â· Power10 frame Â· LPAR 4",
                "cpu_pct": 55,
                "mem_pct": 78,
                "disk_pct": 61,
                "users": 46,
                "sudoers": 9,
                "suid_bins": 41,
                "listeners": 7,
                "open_cves_crit": 3,
                "days_since_patch": 91,
                "lynis_index": 44,
                "openscap_pass_pct": 12,
                "mac_mode": "TCB not enabled",
                "fim_tool": "PowerSC RTC off (enrolled only)",
                "agent": "IBM PowerSC GUI agent Â· Qualys",
                "crown_jewel": True,
                "owner": "AIX Ops Â· R. Nair",
                "linked": "PRODBOX Â· KRI-2026-002 Â· CMP-2026-001",
            },
            {
                "host_id": "HOST-SOL",
                "hostname": "nsk-sol-ora01",
                "fqdn": "nsk-sol-ora01.northstack.internal",
                "os_family": "Solaris",
                "os": "Oracle Solaris 11.4 SRU72",
                "kernel": "11.4.72.0.1.185.1",
                "role": "Legacy Oracle EBS DB (read-mostly)",
                "site": "NorthStack colo B (DR) Â· cage 3 Â· SPARC T8",
                "cpu_pct": 22,
                "mem_pct": 48,
                "disk_pct": 74,
                "users": 29,
                "sudoers": 6,
                "suid_bins": 35,
                "listeners": 11,
                "open_cves_crit": 4,
                "days_since_patch": 118,
                "lynis_index": 38,
                "openscap_pass_pct": 22,
                "mac_mode": "No MAC (RBAC unused)",
                "fim_tool": "None Â· BSM off",
                "agent": "Qualys scanner (agentless) Â· no EDR",
                "crown_jewel": False,
                "owner": "Oracle Ops Â· Legacy Â· S. Berg",
                "linked": "DST-2026-001 Â· GAP-2026-001 Â· decommission backlog",
            },
            {
                "host_id": "HOST-WEB",
                "hostname": "nsk-rhel-web01",
                "fqdn": "nsk-rhel-web01.northstack.internal",
                "os_family": "Linux",
                "os": "RHEL 9.3",
                "kernel": "5.14.0-362.24.1.el9_3",
                "role": "External portal edge (read-only CMS)",
                "site": "NorthStack colo A Â· DMZ VLAN 40",
                "cpu_pct": 31,
                "mem_pct": 44,
                "disk_pct": 39,
                "users": 18,
                "sudoers": 5,
                "suid_bins": 54,
                "listeners": 6,
                "open_cves_crit": 1,
                "days_since_patch": 28,
                "lynis_index": 67,
                "openscap_pass_pct": 58,
                "mac_mode": "SELinux enforcing",
                "fim_tool": "AIDE daily Â· CrowdStrike",
                "agent": "Qualys Â· CrowdStrike Falcon",
                "crown_jewel": False,
                "owner": "WebOps Â· L. Duarte",
                "linked": "INC-2026-001 portal stuffing narrative",
            },
        ]
    )

    domains = pd.DataFrame(
        [
            {"domain_id": "AUTH", "domain": "Authentication / PAM / passwords", "score": 54, "checks": 24, "fails": 11, "benchmark": "CIS RHEL/AIX/SOL Â· PAM / logindefs"},
            {"domain_id": "PRIV", "domain": "Privileged access / sudo / root", "score": 38, "checks": 18, "fails": 12, "benchmark": "CIS sudo Â· least privilege Â· PowerSC"},
            {"domain_id": "SSH", "domain": "SSH / remote access", "score": 41, "checks": 20, "fails": 13, "benchmark": "CIS SSH Â· STIG RHEL Â· sshd_config"},
            {"domain_id": "NET", "domain": "Network services / firewall", "score": 47, "checks": 16, "fails": 9, "benchmark": "firewalld / ipfilter / AIX IPSec"},
            {"domain_id": "FS", "domain": "Filesystem / NFS / shares", "score": 36, "checks": 22, "fails": 14, "benchmark": "World-writable Â· NFS Â· exports"},
            {"domain_id": "KERN", "domain": "Kernel / sysctl / MAC", "score": 52, "checks": 28, "fails": 14, "benchmark": "sysctl Â· SELinux/AppArmor Â· AIX TCB"},
            {"domain_id": "AUD", "domain": "Audit / FIM / logging", "score": 42, "checks": 18, "fails": 11, "benchmark": "auditd Â· AIDE/Tripwire Â· PowerSC RTC Â· BSM"},
            {"domain_id": "PATCH", "domain": "Patch & package currency", "score": 44, "checks": 12, "fails": 7, "benchmark": "Qualys VMDR Â· dnf Â· AIX TL Â· Solaris SRU"},
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
            "detail": "sshd_config: PermitRootLogin yes Â· PasswordAuthentication yes Â· PubkeyAuthentication yes. Shared ops account opsnight still authenticates with password after INC-2026-001 portal stuffing â€” jump is the blast-radius gate to PRODBOX and nsk-aix-db01.",
            "evidence": "sshd -T | grep -E 'permitrootlogin|passwordauthentication'",
            "cis": "CIS RHEL 9 5.2.x SSH server",
            "stig": "RHEL-09-255040 / 255055",
            "iso27001": "A.5.15 Â· A.8.5",
            "soc2": "CC6.1 Â· CC6.6",
            "pci": "2.2 Â· 8.3 Â· 8.4",
            "ref": "CIS-RHEL9 Â· STIG-RHEL8",
            "remediation": "PermitRootLogin prohibit-password; PasswordAuthentication no; force named keys + PAM MFA; retire opsnight.",
            "owner": "Platform Sec Â· J. Okonkwo",
            "status": "Open",
            "due": today + timedelta(days=7),
            "linked": "AST-2026-005 Â· INC-2026-001 Â· KRI-2026-001",
        },
        {
            "finding_id": "FND-UX-002",
            "host_id": "HOST-APP",
            "domain_id": "PRIV",
            "severity": "Critical",
            "title": "sudo NOPASSWD:ALL for deploy and payrollsvc groups",
            "detail": "/etc/sudoers.d/90-deploy: %deploy ALL=(ALL) NOPASSWD:ALL Â· %payrollsvc ALL=(ALL) NOPASSWD:/usr/bin/*,/opt/jde/*. PayrollCo SFTP drop runs as payrollsvc â€” any member can escalate to root without ticket.",
            "evidence": "visudo -c; grep -R NOPASSWD /etc/sudoers*",
            "cis": "CIS RHEL 8 5.3.x sudo",
            "stig": "RHEL-08-010380",
            "iso27001": "A.8.2 Â· A.8.3",
            "soc2": "CC6.1 Â· CC6.3",
            "pci": "7.1 Â· 7.2",
            "ref": "CIS-RHEL9 Â· QUALYS-SCA",
            "remediation": "Replace with command allow-lists; require ticket ID in sudo lecture; break-glass only for root.",
            "owner": "AppOps Â· IAM",
            "status": "In progress",
            "due": today + timedelta(days=14),
            "linked": "INC-2026-009 Â· PayrollCo Â· CMP-2026-001",
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
            "iso27001": "A.8.12 Â· A.8.20",
            "soc2": "CC6.6 Â· CC6.7",
            "pci": "1.2 Â· 7.1",
            "ref": "CIS-AIX73 Â· POWERSC",
            "remediation": "Enable root squash; restrict to named Kerberos/NFSv4; move extract to SFTP with key auth.",
            "owner": "AIX Ops Â· R. Nair",
            "status": "Open",
            "due": today + timedelta(days=10),
            "linked": "PRODBOX Â· KRI-2026-002 Â· PAYMAST narrative",
        },
        {
            "finding_id": "FND-UX-004",
            "host_id": "HOST-SOL",
            "domain_id": "NET",
            "severity": "High",
            "title": "Telnet and rlogin SMF services still online",
            "detail": "svc:/network/telnet:default and rlogin online on nsk-sol-ora01. Legacy Oracle DBA habit â€” cleartext credentials across colo B DR network.",
            "evidence": "svcs -a | grep -E 'telnet|rlogin|rsh'",
            "cis": "CIS Solaris 11 3.x network services",
            "stig": "SOL11 STIG network legacy",
            "iso27001": "A.8.20 Â· A.8.22",
            "soc2": "CC6.6",
            "pci": "2.2 Â· 4.1",
            "ref": "CIS-SOL11",
            "remediation": "svcadm disable telnet rlogin rsh; enforce SSH-only; document exception if any vendor requires it.",
            "owner": "Oracle Ops Â· S. Berg",
            "status": "Open",
            "due": today + timedelta(days=21),
            "linked": "GAP-2026-001 Â· DST-2026-001",
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
            "iso27001": "A.8.9 Â· A.8.32",
            "soc2": "CC7.1 Â· CC8.1",
            "pci": "2.2 Â· 6.2",
            "ref": "POWERSC Â· CIS-AIX73",
            "remediation": "Apply PowerSC CIS Level 1 in change window; enable RTC on critical paths; weekly drift report to GRC.",
            "owner": "AIX Ops Â· Security",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "CMP-2026-001 Â· KRI-2026-002",
        },
        {
            "finding_id": "FND-UX-006",
            "host_id": "HOST-JUMP",
            "domain_id": "AUTH",
            "severity": "High",
            "title": "PAM MFA not enforced on jump; password quality weak",
            "detail": "authselect shows password-auth only â€” no pam_sss / Duo / okta pam. /etc/security/pwquality.conf: minlen=8, minclass=1. Shared colo night crew passwords rotated irregularly.",
            "evidence": "authselect current; grep -v '^#' /etc/security/pwquality.conf",
            "cis": "CIS RHEL 9 5.3 / 5.4 PAM",
            "stig": "RHEL-09-611010",
            "iso27001": "A.5.17 Â· A.8.5",
            "soc2": "CC6.1",
            "pci": "8.3 Â· 8.4",
            "ref": "CIS-RHEL9 Â· STIG-RHEL8",
            "remediation": "Enforce MFA PAM stack; minlen 15 minclass 4; block shared IDs.",
            "owner": "IAM Â· Platform Sec",
            "status": "In progress",
            "due": today + timedelta(days=14),
            "linked": "INC-2026-001 Â· AST-2026-005",
        },
        {
            "finding_id": "FND-UX-007",
            "host_id": "HOST-APP",
            "domain_id": "FS",
            "severity": "Critical",
            "title": "World-writable /opt/jde/drop and sticky-bit missing",
            "detail": "drwxrwxrwx root root /opt/jde/drop â€” PayrollCo inbound files land here before AIX NFS push. Any local user can plant or wipe extracts. No sticky bit; no ACL.",
            "evidence": "ls -ld /opt/jde/drop; getfacl /opt/jde/drop",
            "cis": "CIS RHEL 8 6.1.x file permissions",
            "stig": "RHEL-08-010700",
            "iso27001": "A.8.12",
            "soc2": "CC6.1 Â· CC6.7",
            "pci": "7.1 Â· 10.2",
            "ref": "CIS-RHEL9 Â· LYNIS",
            "remediation": "chmod 1770; group jde-drop only; enable audit watch; consider dedicated SFTP chroot.",
            "owner": "AppOps Â· M. Chen",
            "status": "Open",
            "due": today + timedelta(days=7),
            "linked": "PayrollCo Â· INC-2026-009 Â· FND-UX-003",
        },
        {
            "finding_id": "FND-UX-008",
            "host_id": "HOST-WEB",
            "domain_id": "NET",
            "severity": "High",
            "title": "firewalld inactive; nginx listens 0.0.0.0:80 without redirect",
            "detail": "systemctl is-active firewalld = inactive. nginx still serves HTTP on :80 with no HSTS/redirect to TLS â€” portal stuffing narrative used cleartext probing from DMZ.",
            "evidence": "systemctl status firewalld; ss -lntp | grep nginx",
            "cis": "CIS RHEL 9 3.4 firewall Â· 5.x web",
            "stig": "RHEL-09-251015",
            "iso27001": "A.8.20 Â· A.8.22",
            "soc2": "CC6.6",
            "pci": "1.2 Â· 4.1",
            "ref": "CIS-RHEL9 Â· QUALYS-SCA",
            "remediation": "Enable firewalld with minimal allow; force HTTPS redirect; terminate TLS at edge.",
            "owner": "WebOps Â· L. Duarte",
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
            "iso27001": "A.8.15 Â· A.8.16",
            "soc2": "CC7.2 Â· CC7.3",
            "pci": "10.2 Â· 10.3",
            "ref": "CIS-SOL11",
            "remediation": "Enable BSM with class lo,ad,ex,fw; ship to SIEM; 90-day retention.",
            "owner": "Oracle Ops Â· SecOps",
            "status": "Open",
            "due": today + timedelta(days=21),
            "linked": "DST-2026-001 Â· GAP-2026-001",
        },
        {
            "finding_id": "FND-UX-010",
            "host_id": "HOST-APP",
            "domain_id": "AUD",
            "severity": "Medium",
            "title": "auditd retention 7 days; space_left action ignore",
            "detail": "max_log_file_action = ignore Â· num_logs = 3 Â· approx 7 days of local trail. SIEM forwarder intermittently drops â€” same gap pattern as IBM i QAUDJRN 14-day receivers.",
            "evidence": "grep -E 'max_log|num_logs|space_left' /etc/audit/auditd.conf",
            "cis": "CIS RHEL 8 4.1.x auditd",
            "stig": "RHEL-08-030060",
            "iso27001": "A.8.15",
            "soc2": "CC7.2",
            "pci": "10.5 Â· 10.7",
            "ref": "CIS-RHEL9 Â· STIG-RHEL8",
            "remediation": "num_logs â‰¥ 20; space_left_action email+syslog; verify SIEM ACK.",
            "owner": "SecOps Â· AppOps",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "FND-IBMI-011 pattern Â· KRI-2026-001",
        },
        {
            "finding_id": "FND-UX-011",
            "host_id": "HOST-APP",
            "domain_id": "PATCH",
            "severity": "Critical",
            "title": "5 critical CVEs open >60 days including kernel and OpenSSH",
            "detail": "Qualys VMDR: CVE-2024-6387 (OpenSSH), kernel privilege CVEs, and openssl still Open on nsk-rhel-app01. Last full patch window cancelled during PayrollCo IR freeze.",
            "evidence": "Qualys host detection Â· dnf updateinfo list security",
            "cis": "CIS continuous patching Â· Qualys VMDR",
            "stig": "RHEL patch currency",
            "iso27001": "A.8.8",
            "soc2": "CC7.1 Â· CC8.1",
            "pci": "6.2 Â· 6.3",
            "ref": "QUALYS-SCA Â· CIS-RHEL9",
            "remediation": "Emergency patch CAB; reboot window; reopen freeze exception for security-only.",
            "owner": "AppOps Â· Patch Mgmt",
            "status": "Blocked",
            "due": today + timedelta(days=5),
            "linked": "INC-2026-009 Â· PayrollCo freeze",
        },
        {
            "finding_id": "FND-UX-012",
            "host_id": "HOST-JUMP",
            "domain_id": "PRIV",
            "severity": "High",
            "title": "SUID custom binary /usr/local/bin/jumpwrap owned by root",
            "detail": "Custom colo wrapper setuid root â€” wraps ssh to PRODBOX. Source not in git; last mtime 2024-06. Lynis and CIS both flag unknown SUID.",
            "evidence": "find /usr/local -perm -4000 -ls; rpm -qf /usr/local/bin/jumpwrap",
            "cis": "CIS RHEL 9 6.1.13 SUID",
            "stig": "RHEL-09-232020",
            "iso27001": "A.8.19",
            "soc2": "CC6.1 Â· CC8.1",
            "pci": "6.3 Â· 7.1",
            "ref": "LYNIS Â· CIS-RHEL9",
            "remediation": "Remove SUID; rewrite as sudoers allow-list; inventory all local SUID.",
            "owner": "Platform Sec",
            "status": "Open",
            "due": today + timedelta(days=14),
            "linked": "AST-2026-005 Â· JUMP-DMZ-03",
        },
        {
            "finding_id": "FND-UX-013",
            "host_id": "HOST-AIX",
            "domain_id": "AUTH",
            "severity": "High",
            "title": "AIX root remotely reachable; rhosts remnants",
            "detail": "/etc/security/user default rlogin=true for root Â· .rhosts files found under /home/oracle and /home/db2inst1 referencing retired jump host JUMP-DMZ-01.",
            "evidence": "lsuser -a rlogin root; find /home -name .rhosts",
            "cis": "CIS AIX 7.3 authentication",
            "stig": "AIX root remote",
            "iso27001": "A.5.15 Â· A.8.5",
            "soc2": "CC6.1",
            "pci": "2.2 Â· 8.2",
            "ref": "CIS-AIX73 Â· POWERSC",
            "remediation": "rlogin=false for root; delete .rhosts; SSH keys + PowerSC MFA profile.",
            "owner": "AIX Ops",
            "status": "Open",
            "due": today + timedelta(days=14),
            "linked": "FND-UX-001 Â· JUMP path",
        },
        {
            "finding_id": "FND-UX-014",
            "host_id": "HOST-SOL",
            "domain_id": "PRIV",
            "severity": "Critical",
            "title": "No RBAC â€” six admins share root password",
            "detail": "Oracle Ops team of 6 uses a shared root password in a sealed envelope + LastPass folder 'sol-ora-root'. pfexec / RBAC roles unused. Orbit AMS remote in 2025 used this path.",
            "evidence": "profiles -l; userattr ...; last root",
            "cis": "CIS Solaris 11 RBAC / privileges",
            "stig": "SOL11 privileged access",
            "iso27001": "A.5.15 Â· A.8.2",
            "soc2": "CC6.1 Â· CC6.2",
            "pci": "7.1 Â· 8.2",
            "ref": "CIS-SOL11",
            "remediation": "Named RBAC roles; break-glass root in PAM vault; rotate after any vendor remote.",
            "owner": "Oracle Ops Â· IAM",
            "status": "Open",
            "due": today + timedelta(days=21),
            "linked": "Orbit AMS Â· DST-2026-001 Â· CMP-2026-004",
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
            "owner": "Network Â· Platform Sec",
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
            "cis": "CIS AIX patch currency Â· PowerSC patch mgmt",
            "stig": "AIX patch",
            "iso27001": "A.8.8",
            "soc2": "CC8.1",
            "pci": "6.2",
            "ref": "POWERSC Â· CIS-AIX73",
            "remediation": "Schedule TL apply on HA secondary first; document DB2 regression tests.",
            "owner": "AIX Ops",
            "status": "In progress",
            "due": today + timedelta(days=45),
            "linked": "PRODBOX HA Â· KRI-2026-002",
        },
        {
            "finding_id": "FND-UX-017",
            "host_id": "HOST-WEB",
            "domain_id": "SSH",
            "severity": "Medium",
            "title": "Weak SSH ciphers and no MaxAuthTries limit",
            "detail": "Ciphers include 3des-cbc Â· MaxAuthTries unset (default 6 still high for portal-adjacent host).",
            "evidence": "sshd -T | grep -E 'ciphers|maxauthtries'",
            "cis": "CIS RHEL 9 5.2.13 / 5.2.5",
            "stig": "RHEL-09-255060",
            "iso27001": "A.8.24",
            "soc2": "CC6.6",
            "pci": "4.1 Â· 8.3",
            "ref": "CIS-RHEL9 Â· STIG-RHEL8",
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
            "owner": "Oracle Ops Â· Patch Mgmt",
            "status": "Open",
            "due": today + timedelta(days=60),
            "linked": "GAP-2026-001 decommission",
        },
        {
            "finding_id": "FND-UX-019",
            "host_id": "HOST-APP",
            "domain_id": "KERN",
            "severity": "Critical",
            "title": "SELinux permissive on payroll landing host",
            "detail": "getenforce = Permissive on nsk-rhel-app01. Set during 2025 JDE go-live 'to stop denials' and never returned to Enforcing. OpenSCAP CIS 1.6.x fails; Wazuh SCA flags the same.",
            "evidence": "getenforce; sestatus; ausearch -m AVC -ts recent | head",
            "cis": "CIS RHEL 8 1.6.1.x SELinux",
            "stig": "RHEL-08-010170",
            "iso27001": "A.8.7 Â· A.8.32",
            "soc2": "CC6.6 Â· CC7.1",
            "pci": "2.2 Â· 5.3",
            "ref": "CIS-RHEL9 Â· OPENSCAP Â· QUALYS-VMDR",
            "remediation": "Fix denials in permissive with audit2allow review; set Enforcing; bake into golden image.",
            "owner": "AppOps Â· Platform Sec",
            "status": "Open",
            "due": today + timedelta(days=14),
            "linked": "PayrollCo Â· FND-UX-007 Â· INC-2026-009",
        },
        {
            "finding_id": "FND-UX-020",
            "host_id": "HOST-JUMP",
            "domain_id": "AUD",
            "severity": "High",
            "title": "No FIM baseline on JUMP-DMZ-03 (AIDE/Tripwire absent)",
            "detail": "aide --check fails (no database). Tripwire Enterprise not licensed for DMZ. CrowdStrike covers malware but not config integrity on /etc/ssh, sudoers, jumpwrap. Lynis warns 'no file integrity tool'.",
            "evidence": "rpm -q aide; ls /var/lib/aide; lynis audit system | grep -i integrity",
            "cis": "CIS RHEL 9 6.3.x FIM",
            "stig": "RHEL-09-651010",
            "iso27001": "A.8.16 Â· A.8.19",
            "soc2": "CC7.1 Â· CC7.2",
            "pci": "11.5 Â· 10.3",
            "ref": "TRIPWIRE Â· LYNIS Â· CIS-RHEL9",
            "remediation": "Initialize AIDE (or Tripwire) on jump critical paths; alert on sshd_config/sudoers/jumpwrap changes.",
            "owner": "Platform Sec Â· SecOps",
            "status": "Open",
            "due": today + timedelta(days=14),
            "linked": "AST-2026-005 Â· INC-2026-001",
        },
        {
            "finding_id": "FND-UX-021",
            "host_id": "HOST-AIX",
            "domain_id": "AUD",
            "severity": "Critical",
            "title": "PowerSC Trusted Logging and RTC not enabled",
            "detail": "Endpoint has PowerSC GUI agent but Trusted Logging (VIOS-central tamper-proof logs), Real Time Compliance FIM, Trusted Boot, and MFA profiles are all Off. Local root can still wipe AIX audit without VIOS copy.",
            "evidence": "PowerSC GUI feature matrix Â· lssrc -a | grep -i powersc",
            "cis": "CIS AIX Â· PowerSC RTC/Trusted Logging",
            "stig": "AIX audit integrity",
            "iso27001": "A.8.15 Â· A.8.16",
            "soc2": "CC7.2 Â· CC7.3",
            "pci": "10.3 Â· 10.5",
            "ref": "POWERSC",
            "remediation": "Enable Trusted Logging to VIOS; turn on RTC for /payroll and DB2 configs; plan Trusted Boot attestation.",
            "owner": "AIX Ops Â· Security",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "FND-UX-005 Â· KRI-2026-002 Â· PRODBOX",
        },
        {
            "finding_id": "FND-UX-022",
            "host_id": "HOST-APP",
            "domain_id": "AUTH",
            "severity": "High",
            "title": "Duplicate UID 0 account toor left from break-glass drill",
            "detail": "getent passwd | awk -F: '$3==0' shows root and toor. toor password last changed 2025-11; not in PAM vault. Classic Lynis/CIS fail.",
            "evidence": "awk -F: '($3 == 0) {print}' /etc/passwd",
            "cis": "CIS RHEL 8 5.4.2 unique UID 0",
            "stig": "RHEL-08-010160",
            "iso27001": "A.5.15 Â· A.8.2",
            "soc2": "CC6.1",
            "pci": "7.1 Â· 8.2",
            "ref": "CIS-RHEL9 Â· LYNIS Â· OPENSCAP",
            "remediation": "Lock/remove toor; document single break-glass in PAM; alert on new UID 0.",
            "owner": "IAM Â· AppOps",
            "status": "Open",
            "due": today + timedelta(days=7),
            "linked": "FND-UX-002",
        },
        {
            "finding_id": "FND-UX-023",
            "host_id": "HOST-SOL",
            "domain_id": "KERN",
            "severity": "High",
            "title": "Solaris compliance assessor never scheduled",
            "detail": "compliance list / compliance assess against solaris and pci-dss benchmarks not in cron. Last manual run was 2024-08 (pre-Orbit AMS remote). No SCAP HTML in GRC evidence locker.",
            "evidence": "compliance list; ls /var/share/compliance; crontab -l | grep compliance",
            "cis": "CIS Solaris 11 Â· Oracle compliance(8)",
            "stig": "SOL11 SCAP",
            "iso27001": "A.8.9 Â· A.5.36",
            "soc2": "CC7.1 Â· CC8.1",
            "pci": "2.2 Â· 11.3",
            "ref": "SOL-COMPLY Â· CIS-SOL11 Â· OPENSCAP",
            "remediation": "Weekly compliance assess --benchmark solaris; archive HTML to GRC; fail build if score drops.",
            "owner": "Oracle Ops Â· GRC",
            "status": "Open",
            "due": today + timedelta(days=21),
            "linked": "GAP-2026-001 Â· DST-2026-001",
        },
        {
            "finding_id": "FND-UX-024",
            "host_id": "HOST-JUMP",
            "domain_id": "KERN",
            "severity": "Medium",
            "title": "OpenSCAP CIS Level 1 pass rate 41% on jump",
            "detail": "oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis against SSG for RHEL 9: 41% pass. Failures cluster on SSH, PAM, and audit rules â€” matches Qualys Policy Compliance host audit.",
            "evidence": "oscap xccdf eval --profile cis --results jump-cis.xml ...",
            "cis": "CIS RHEL 9 Level 1 (aggregate)",
            "stig": "SSG stig profile alternate",
            "iso27001": "A.8.9",
            "soc2": "CC7.1",
            "pci": "2.2",
            "ref": "OPENSCAP Â· TENABLE Â· QUALYS-VMDR",
            "remediation": "Treat OpenSCAP HTML as control evidence; close FND-UX-001/006/015 first â€” index should jump ~15 pts.",
            "owner": "Platform Sec",
            "status": "Open",
            "due": today + timedelta(days=30),
            "linked": "AST-2026-005 Â· UX-SCAN-2026-09",
        },
    ]
    findings_df = pd.DataFrame(findings)

    # Hardening controls (sysctl / AIX SEC / Solaris) â€” baseline drift view
    baseline = pd.DataFrame(
        [
            {"host_id": "HOST-JUMP", "control": "PermitRootLogin", "desired": "prohibit-password", "current": "yes", "drift": True, "source": "sshd_config", "last_change": today - timedelta(days=400)},
            {"host_id": "HOST-JUMP", "control": "PasswordAuthentication", "desired": "no", "current": "yes", "drift": True, "source": "sshd_config", "last_change": today - timedelta(days=400)},
            {"host_id": "HOST-JUMP", "control": "net.ipv4.ip_forward", "desired": "0", "current": "1", "drift": True, "source": "sysctl", "last_change": today - timedelta(days=120)},
            {"host_id": "HOST-JUMP", "control": "net.ipv4.conf.all.rp_filter", "desired": "1", "current": "0", "drift": True, "source": "sysctl", "last_change": today - timedelta(days=120)},
            {"host_id": "HOST-APP", "control": "sudo NOPASSWD", "desired": "none / allow-list", "current": "deploy,payrollsvc ALL", "drift": True, "source": "sudoers.d", "last_change": today - timedelta(days=55)},
            {"host_id": "HOST-APP", "control": "/opt/jde/drop mode", "desired": "1770", "current": "0777", "drift": True, "source": "filesystem", "last_change": today - timedelta(days=12)},
            {"host_id": "HOST-APP", "control": "auditd num_logs", "desired": "â‰¥20", "current": "3", "drift": True, "source": "auditd.conf", "last_change": today - timedelta(days=200)},
            {"host_id": "HOST-AIX", "control": "PowerSC CIS profile", "desired": "applied + RTC", "current": "enrolled / never applied", "drift": True, "source": "PowerSC", "last_change": today - timedelta(days=0)},
            {"host_id": "HOST-AIX", "control": "NFS root=", "desired": "none (root squash)", "current": "root=app01,JUMP", "drift": True, "source": "/etc/exports", "last_change": today - timedelta(days=33)},
            {"host_id": "HOST-AIX", "control": "root rlogin", "desired": "false", "current": "true", "drift": True, "source": "/etc/security/user", "last_change": today - timedelta(days=500)},
            {"host_id": "HOST-SOL", "control": "telnet SMF", "desired": "disabled", "current": "online", "drift": True, "source": "svcs", "last_change": today - timedelta(days=900)},
            {"host_id": "HOST-SOL", "control": "BSM audit", "desired": "enabled", "current": "disabled", "drift": True, "source": "auditconfig", "last_change": today - timedelta(days=180)},
            {"host_id": "HOST-SOL", "control": "RBAC roles", "desired": "named roles", "current": "shared root", "drift": True, "source": "profiles", "last_change": today - timedelta(days=600)},
            {"host_id": "HOST-WEB", "control": "firewalld", "desired": "active", "current": "inactive", "drift": True, "source": "systemd", "last_change": today - timedelta(days=40)},
            {"host_id": "HOST-WEB", "control": "SSH Ciphers", "desired": "modern only", "current": "includes 3des-cbc", "drift": True, "source": "sshd_config", "last_change": today - timedelta(days=220)},
            {"host_id": "HOST-JUMP", "control": "PAM MFA", "desired": "required", "current": "password only", "drift": True, "source": "authselect", "last_change": today - timedelta(days=90)},
            {"host_id": "HOST-APP", "control": "kernel patch age", "desired": "â‰¤30 days", "current": "63 days", "drift": True, "source": "Qualys VMDR", "last_change": today - timedelta(days=63)},
            {"host_id": "HOST-AIX", "control": "oslevel TL", "desired": "current SP", "current": "91 days behind", "drift": True, "source": "oslevel", "last_change": today - timedelta(days=91)},
            {"host_id": "HOST-APP", "control": "SELinux mode", "desired": "Enforcing", "current": "Permissive", "drift": True, "source": "getenforce", "last_change": today - timedelta(days=280)},
            {"host_id": "HOST-JUMP", "control": "AIDE database", "desired": "initialized + daily", "current": "absent", "drift": True, "source": "aide", "last_change": today - timedelta(days=0)},
            {"host_id": "HOST-AIX", "control": "PowerSC Trusted Logging", "desired": "On â†’ VIOS", "current": "Off", "drift": True, "source": "PowerSC", "last_change": today - timedelta(days=0)},
            {"host_id": "HOST-AIX", "control": "PowerSC RTC FIM", "desired": "On (/payroll, DB2)", "current": "Off", "drift": True, "source": "PowerSC", "last_change": today - timedelta(days=0)},
            {"host_id": "HOST-APP", "control": "UID 0 uniqueness", "desired": "root only", "current": "root + toor", "drift": True, "source": "/etc/passwd", "last_change": today - timedelta(days=310)},
            {"host_id": "HOST-SOL", "control": "compliance assess cron", "desired": "weekly", "current": "never (last 2024-08)", "drift": True, "source": "compliance(8)", "last_change": today - timedelta(days=390)},
        ]
    )

    listeners = pd.DataFrame(
        [
            {"host_id": "HOST-JUMP", "proto": "tcp", "port": 22, "process": "sshd", "bind": "0.0.0.0", "risk": "High", "notes": "Password auth still on"},
            {"host_id": "HOST-JUMP", "proto": "tcp", "port": 2222, "process": "sshd (alt)", "bind": "0.0.0.0", "risk": "Medium", "notes": "Undocumented alt SSH"},
            {"host_id": "HOST-APP", "proto": "tcp", "port": 22, "process": "sshd", "bind": "10.20.20.0/24", "risk": "Medium", "notes": "App VLAN only â€” OK"},
            {"host_id": "HOST-APP", "proto": "tcp", "port": 21, "process": "vsftpd", "bind": "0.0.0.0", "risk": "Critical", "notes": "Cleartext FTP for legacy vendor"},
            {"host_id": "HOST-APP", "proto": "tcp", "port": 2049, "process": "nfsd", "bind": "0.0.0.0", "risk": "Critical", "notes": "NFS to AIX payroll"},
            {"host_id": "HOST-APP", "proto": "tcp", "port": 445, "process": "smbd", "bind": "0.0.0.0", "risk": "High", "notes": "Samba share for Windows finance"},
            {"host_id": "HOST-AIX", "proto": "tcp", "port": 22, "process": "sshd", "bind": "0.0.0.0", "risk": "Medium", "notes": "Should be jump-only"},
            {"host_id": "HOST-AIX", "proto": "tcp", "port": 50000, "process": "db2sysc", "bind": "10.20.30.14", "risk": "High", "notes": "DB2 Â· crown jewel"},
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
            {"host_id": "HOST-JUMP", "account": "jokonkwo", "type": "named sudo", "last_login": today - timedelta(days=0), "mfa": True, "notes": "Owner â€” OK"},
            {"host_id": "HOST-APP", "account": "payrollsvc", "type": "service sudo", "last_login": today - timedelta(days=0), "mfa": False, "notes": "NOPASSWD:ALL"},
            {"host_id": "HOST-APP", "account": "deploy", "type": "group sudo", "last_login": today - timedelta(days=1), "mfa": False, "notes": "12 members Â· NOPASSWD"},
            {"host_id": "HOST-AIX", "account": "root", "type": "uid0", "last_login": today - timedelta(days=5), "mfa": False, "notes": "rlogin=true"},
            {"host_id": "HOST-AIX", "account": "db2inst1", "type": "DB2 instance", "last_login": today - timedelta(days=0), "mfa": False, "notes": ".rhosts present"},
            {"host_id": "HOST-SOL", "account": "root", "type": "shared uid0", "last_login": today - timedelta(days=2), "mfa": False, "notes": "6 admins Â· envelope + LastPass"},
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
            {"host_id": "HOST-JUMP", "setting": "MaxAuthTries", "value": "6", "cis": "â‰¤4", "status": "Fail"},
            {"host_id": "HOST-JUMP", "setting": "AllowUsers", "value": "(unset)", "cis": "explicit list", "status": "Fail"},
            {"host_id": "HOST-APP", "setting": "PermitRootLogin", "value": "no", "cis": "no", "status": "Pass"},
            {"host_id": "HOST-APP", "setting": "PasswordAuthentication", "value": "no", "cis": "no", "status": "Pass"},
            {"host_id": "HOST-APP", "setting": "Ciphers", "value": "modern", "cis": "modern", "status": "Pass"},
            {"host_id": "HOST-WEB", "setting": "PermitRootLogin", "value": "no", "cis": "no", "status": "Pass"},
            {"host_id": "HOST-WEB", "setting": "Ciphers", "value": "includes 3des-cbc", "cis": "modern only", "status": "Fail"},
            {"host_id": "HOST-WEB", "setting": "MaxAuthTries", "value": "6", "cis": "â‰¤4", "status": "Fail"},
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
            {"finding_id": "FND-UX-005", "host_id": "HOST-AIX", "command": "PowerSC GUI Â· profile history", "output_excerpt": "Endpoint enrolled Â· Last apply: never Â· RTC: off", "captured": today - timedelta(days=0), "tool": "PowerSC"},
            {"finding_id": "FND-UX-007", "host_id": "HOST-APP", "command": "ls -ld /opt/jde/drop", "output_excerpt": "drwxrwxrwx. 2 root root 4096 ... /opt/jde/drop", "captured": today - timedelta(days=1), "tool": "ls"},
            {"finding_id": "FND-UX-009", "host_id": "HOST-SOL", "command": "auditconfig -getcond", "output_excerpt": "audit condition = noaudit", "captured": today - timedelta(days=2), "tool": "auditconfig"},
            {"finding_id": "FND-UX-011", "host_id": "HOST-APP", "command": "Qualys VMDR critical detections", "output_excerpt": "5 Critical Â· oldest 63d Â· CVE-2024-6387 Open", "captured": today - timedelta(days=0), "tool": "Qualys"},
            {"finding_id": "FND-UX-012", "host_id": "HOST-JUMP", "command": "find /usr/local -perm -4000 -ls", "output_excerpt": "... /usr/local/bin/jumpwrap", "captured": today - timedelta(days=4), "tool": "find"},
            {"finding_id": "FND-UX-014", "host_id": "HOST-SOL", "command": "last root | head", "output_excerpt": "root pts/3 ... shared ops sessions Â· 6 distinct source IPs", "captured": today - timedelta(days=1), "tool": "last"},
            {"finding_id": "FND-UX-019", "host_id": "HOST-APP", "command": "getenforce; sestatus", "output_excerpt": "Permissive\\nSELinux status: enabled Â· Current mode: permissive", "captured": today - timedelta(days=1), "tool": "sestatus"},
            {"finding_id": "FND-UX-020", "host_id": "HOST-JUMP", "command": "rpm -q aide; aide --check", "output_excerpt": "package aide is not installed", "captured": today - timedelta(days=2), "tool": "aide"},
            {"finding_id": "FND-UX-021", "host_id": "HOST-AIX", "command": "PowerSC feature matrix", "output_excerpt": "RTC=Off Â· Trusted Logging=Off Â· Trusted Boot=Off Â· MFA=Off", "captured": today - timedelta(days=0), "tool": "PowerSC"},
            {"finding_id": "FND-UX-022", "host_id": "HOST-APP", "command": "awk -F: '($3==0){print}' /etc/passwd", "output_excerpt": "root:x:0:0:...\\ntoor:x:0:0:breakglass:/root:/bin/bash", "captured": today - timedelta(days=1), "tool": "passwd"},
        ]
    )

    tickets = pd.DataFrame(
        [
            {"ticket_id": "CHG-UX-1041", "finding_id": "FND-UX-001", "title": "Harden JUMP-DMZ-03 sshd (keys + no root pw)", "owner": "Platform Sec", "status": "CAB approved", "due": today + timedelta(days=7), "effort": "M"},
            {"ticket_id": "CHG-UX-1042", "finding_id": "FND-UX-002", "title": "Rewrite sudoers allow-lists on app01", "owner": "AppOps Â· IAM", "status": "In progress", "due": today + timedelta(days=14), "effort": "L"},
            {"ticket_id": "CHG-UX-1043", "finding_id": "FND-UX-003", "title": "NFS root squash + Kerberos on /payroll", "owner": "AIX Ops", "status": "Open", "due": today + timedelta(days=10), "effort": "L"},
            {"ticket_id": "CHG-UX-1044", "finding_id": "FND-UX-005", "title": "Apply PowerSC CIS L1 on nsk-aix-db01", "owner": "AIX Ops Â· Sec", "status": "Open", "due": today + timedelta(days=30), "effort": "XL"},
            {"ticket_id": "CHG-UX-1045", "finding_id": "FND-UX-007", "title": "Lock down /opt/jde/drop permissions", "owner": "AppOps", "status": "Open", "due": today + timedelta(days=7), "effort": "S"},
            {"ticket_id": "CHG-UX-1046", "finding_id": "FND-UX-011", "title": "Emergency patch app01 (OpenSSH/kernel)", "owner": "Patch Mgmt", "status": "Blocked", "due": today + timedelta(days=5), "effort": "M"},
            {"ticket_id": "CHG-UX-1047", "finding_id": "FND-UX-004", "title": "Disable Telnet/rlogin on sol-ora01", "owner": "Oracle Ops", "status": "Open", "due": today + timedelta(days=21), "effort": "S"},
            {"ticket_id": "CHG-UX-1048", "finding_id": "FND-UX-014", "title": "Solaris RBAC + vault root", "owner": "IAM Â· Oracle Ops", "status": "Open", "due": today + timedelta(days=21), "effort": "L"},
            {"ticket_id": "CHG-UX-1049", "finding_id": "FND-UX-008", "title": "firewalld + HTTPS redirect web01", "owner": "WebOps", "status": "In progress", "due": today + timedelta(days=14), "effort": "M"},
            {"ticket_id": "CHG-UX-1050", "finding_id": "FND-UX-009", "title": "Enable Solaris BSM â†’ SIEM", "owner": "SecOps", "status": "Open", "due": today + timedelta(days=21), "effort": "M"},
            {"ticket_id": "CHG-UX-1051", "finding_id": "FND-UX-019", "title": "Return app01 SELinux to Enforcing", "owner": "AppOps Â· Sec", "status": "Open", "due": today + timedelta(days=14), "effort": "M"},
            {"ticket_id": "CHG-UX-1052", "finding_id": "FND-UX-020", "title": "Stand up AIDE on JUMP-DMZ-03", "owner": "Platform Sec", "status": "Open", "due": today + timedelta(days=14), "effort": "S"},
            {"ticket_id": "CHG-UX-1053", "finding_id": "FND-UX-021", "title": "PowerSC Trusted Logging + RTC on", "owner": "AIX Ops", "status": "Open", "due": today + timedelta(days=30), "effort": "L"},
            {"ticket_id": "CHG-UX-1054", "finding_id": "FND-UX-022", "title": "Remove duplicate UID 0 toor", "owner": "IAM", "status": "Open", "due": today + timedelta(days=7), "effort": "S"},
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
            {"framework": "CIS Benchmarks (multi-OS)", "passing": 62, "failing": 54, "partial": 19, "readiness_pct": 46.0},
            {"framework": "DISA STIG (RHEL/AIX)", "passing": 41, "failing": 58, "partial": 22, "readiness_pct": 37.0},
            {"framework": "OpenSCAP SSG (Linux)", "passing": 88, "failing": 112, "partial": 14, "readiness_pct": 41.0},
            {"framework": "ISO 27001:2022", "passing": 28, "failing": 16, "partial": 11, "readiness_pct": 51.0},
            {"framework": "SOC 2 (CC6/CC7/CC8)", "passing": 22, "failing": 18, "partial": 9, "readiness_pct": 45.0},
            {"framework": "PCI DSS 4.0 (in-scope hosts)", "passing": 18, "failing": 23, "partial": 8, "readiness_pct": 36.0},
            {"framework": "IBM PowerSC profiles (AIX)", "passing": 0, "failing": 1, "partial": 0, "readiness_pct": 12.0},
            {"framework": "Solaris compliance(8)", "passing": 0, "failing": 1, "partial": 0, "readiness_pct": 18.0},
        ]
    )

    crosswalk = findings_df[
        ["finding_id", "title", "severity", "cis", "stig", "iso27001", "soc2", "pci", "ref"]
    ].copy()

    # Lynis hardening index history (pulse â€” not auditor evidence)
    lynis = pd.DataFrame(
        [
            {"host_id": "HOST-JUMP", "as_of": today - timedelta(days=90), "index": 61, "warnings": 42, "suggestions": 88},
            {"host_id": "HOST-JUMP", "as_of": today - timedelta(days=30), "index": 59, "warnings": 45, "suggestions": 90},
            {"host_id": "HOST-JUMP", "as_of": today, "index": 58, "warnings": 47, "suggestions": 91},
            {"host_id": "HOST-APP", "as_of": today - timedelta(days=90), "index": 55, "warnings": 51, "suggestions": 102},
            {"host_id": "HOST-APP", "as_of": today - timedelta(days=30), "index": 52, "warnings": 58, "suggestions": 110},
            {"host_id": "HOST-APP", "as_of": today, "index": 49, "warnings": 63, "suggestions": 118},
            {"host_id": "HOST-AIX", "as_of": today - timedelta(days=90), "index": 48, "warnings": 40, "suggestions": 70},
            {"host_id": "HOST-AIX", "as_of": today - timedelta(days=30), "index": 46, "warnings": 44, "suggestions": 74},
            {"host_id": "HOST-AIX", "as_of": today, "index": 44, "warnings": 48, "suggestions": 79},
            {"host_id": "HOST-SOL", "as_of": today - timedelta(days=90), "index": 40, "warnings": 55, "suggestions": 95},
            {"host_id": "HOST-SOL", "as_of": today - timedelta(days=30), "index": 39, "warnings": 56, "suggestions": 96},
            {"host_id": "HOST-SOL", "as_of": today, "index": 38, "warnings": 58, "suggestions": 98},
            {"host_id": "HOST-WEB", "as_of": today - timedelta(days=90), "index": 64, "warnings": 28, "suggestions": 60},
            {"host_id": "HOST-WEB", "as_of": today - timedelta(days=30), "index": 66, "warnings": 26, "suggestions": 58},
            {"host_id": "HOST-WEB", "as_of": today, "index": 67, "warnings": 24, "suggestions": 55},
        ]
    )

    # OpenSCAP / Qualys PC / Tenable-style rule results (sample)
    openscap = pd.DataFrame(
        [
            {"host_id": "HOST-JUMP", "rule_id": "xccdf_org.ssgproject.content_rule_sshd_disable_root_login", "title": "Disable SSH root login", "profile": "CIS L1", "result": "fail", "severity": "High", "tool": "OpenSCAP SSG"},
            {"host_id": "HOST-JUMP", "rule_id": "xccdf_org.ssgproject.content_rule_sshd_disable_password_auth", "title": "Disable SSH password auth", "profile": "CIS L1", "result": "fail", "severity": "High", "tool": "OpenSCAP SSG"},
            {"host_id": "HOST-JUMP", "rule_id": "xccdf_org.ssgproject.content_rule_package_aide_installed", "title": "Ensure AIDE is installed", "profile": "CIS L1", "result": "fail", "severity": "Medium", "tool": "OpenSCAP SSG"},
            {"host_id": "HOST-JUMP", "rule_id": "xccdf_org.ssgproject.content_rule_audit_rules_loginuid", "title": "Audit loginuid immutable", "profile": "CIS L1", "result": "fail", "severity": "Medium", "tool": "OpenSCAP SSG"},
            {"host_id": "HOST-APP", "rule_id": "xccdf_org.ssgproject.content_rule_selinux_state", "title": "SELinux Enforcing", "profile": "CIS L1", "result": "fail", "severity": "High", "tool": "OpenSCAP SSG"},
            {"host_id": "HOST-APP", "rule_id": "xccdf_org.ssgproject.content_rule_sudo_require_reauthentication", "title": "sudo reauth / no NOPASSWD", "profile": "CIS L1", "result": "fail", "severity": "High", "tool": "Qualys PC"},
            {"host_id": "HOST-APP", "rule_id": "xccdf_org.ssgproject.content_rule_no_files_unowned", "title": "No unowned files", "profile": "CIS L1", "result": "fail", "severity": "Medium", "tool": "OpenSCAP SSG"},
            {"host_id": "HOST-APP", "rule_id": "xccdf_org.ssgproject.content_rule_accounts_no_uid_except_zero", "title": "Only one UID 0", "profile": "CIS L1", "result": "fail", "severity": "High", "tool": "OpenSCAP SSG"},
            {"host_id": "HOST-WEB", "rule_id": "xccdf_org.ssgproject.content_rule_firewalld_enabled", "title": "firewalld enabled", "profile": "CIS L1", "result": "fail", "severity": "High", "tool": "Tenable CIS"},
            {"host_id": "HOST-WEB", "rule_id": "xccdf_org.ssgproject.content_rule_sshd_use_strong_ciphers", "title": "SSH strong ciphers", "profile": "CIS L1", "result": "fail", "severity": "Medium", "tool": "OpenSCAP SSG"},
            {"host_id": "HOST-WEB", "rule_id": "xccdf_org.ssgproject.content_rule_package_aide_installed", "title": "Ensure AIDE is installed", "profile": "CIS L1", "result": "pass", "severity": "Medium", "tool": "OpenSCAP SSG"},
            {"host_id": "HOST-AIX", "rule_id": "powersc_cis_aix73_profile", "title": "PowerSC CIS AIX 7.3 profile applied", "profile": "PowerSC CIS", "result": "fail", "severity": "Critical", "tool": "PowerSC pscxpert"},
            {"host_id": "HOST-AIX", "rule_id": "powersc_rtc_enabled", "title": "Real Time Compliance enabled", "profile": "PowerSC RTC", "result": "fail", "severity": "High", "tool": "PowerSC"},
            {"host_id": "HOST-SOL", "rule_id": "solaris_benchmark_telnet_disabled", "title": "Telnet service disabled", "profile": "Solaris Benchmark", "result": "fail", "severity": "Critical", "tool": "compliance(8)"},
            {"host_id": "HOST-SOL", "rule_id": "solaris_benchmark_bsm_enabled", "title": "BSM auditing enabled", "profile": "Solaris Benchmark", "result": "fail", "severity": "High", "tool": "compliance(8)"},
            {"host_id": "HOST-SOL", "rule_id": "pci_dss_unique_user_ids", "title": "Unique user IDs (no shared root)", "profile": "PCI-DSS", "result": "fail", "severity": "Critical", "tool": "compliance(8)"},
        ]
    )

    # Qualys VMDR / Tenable vuln queue (separate from config findings)
    vulns = pd.DataFrame(
        [
            {"qid": "QID-38299", "cve": "CVE-2024-6387", "title": "OpenSSH regreSSHion RCE", "severity": "Critical", "host_id": "HOST-APP", "age_days": 63, "status": "Active", "tool": "Qualys VMDR", "linked": "FND-UX-011 Â· PayrollCo freeze"},
            {"qid": "QID-91345", "cve": "CVE-2024-36971", "title": "Kernel netfilter privilege", "severity": "Critical", "host_id": "HOST-APP", "age_days": 55, "status": "Active", "tool": "Qualys VMDR", "linked": "FND-UX-011"},
            {"qid": "QID-73045", "cve": "CVE-2023-38408", "title": "OpenSSH agent forwarding", "severity": "High", "host_id": "HOST-JUMP", "age_days": 120, "status": "Active", "tool": "Qualys VMDR", "linked": "FND-UX-001"},
            {"qid": "QID-50419", "cve": "CVE-2024-1086", "title": "nf_tables use-after-free", "severity": "Critical", "host_id": "HOST-WEB", "age_days": 40, "status": "Fixed pending reboot", "tool": "Qualys VMDR", "linked": "â€”"},
            {"qid": "QID-AIX-2210", "cve": "CVE-2023-45853", "title": "AIX OpenSSH / zlib APAR", "severity": "High", "host_id": "HOST-AIX", "age_days": 91, "status": "Active", "tool": "Qualys Â· IBM APAR", "linked": "FND-UX-016"},
            {"qid": "QID-AIX-2198", "cve": "CVE-2024-23296", "title": "AIX NFS client APAR", "severity": "High", "host_id": "HOST-AIX", "age_days": 70, "status": "Active", "tool": "IBM APAR", "linked": "FND-UX-003"},
            {"qid": "QID-SOL-4412", "cve": "CVE-2023-4911", "title": "Solaris openssl / liblo_ong", "severity": "Critical", "host_id": "HOST-SOL", "age_days": 100, "status": "Active", "tool": "Qualys agentless", "linked": "FND-UX-018"},
            {"qid": "QID-SOL-4388", "cve": "CVE-2024-6387", "title": "OpenSSH on Solaris SRU lag", "severity": "Critical", "host_id": "HOST-SOL", "age_days": 63, "status": "Active", "tool": "Qualys agentless", "linked": "FND-UX-018"},
            {"qid": "QID-91201", "cve": "CVE-2024-3094", "title": "xz / liblzma supply chain (check)", "severity": "Info", "host_id": "HOST-APP", "age_days": 150, "status": "Not applicable (RHEL8)", "tool": "CrowdStrike", "linked": "â€”"},
            {"qid": "QID-88012", "cve": "CVE-2024-21626", "title": "runc container escape", "severity": "High", "host_id": "HOST-APP", "age_days": 80, "status": "Active", "tool": "Qualys VMDR", "linked": "Docker on app01 (dev leftover)"},
        ]
    )

    # FIM / RTC / AIDE events
    fim_events = pd.DataFrame(
        [
            {"when": today - timedelta(days=2), "host_id": "HOST-APP", "path": "/opt/jde/drop/pay_20260901.csv", "change": "created", "tool": "Wazuh FIM", "severity": "High", "notes": "World-writable drop â€” any local user"},
            {"when": today - timedelta(days=5), "host_id": "HOST-APP", "path": "/etc/sudoers.d/90-deploy", "change": "modified", "tool": "Wazuh FIM", "severity": "Critical", "notes": "NOPASSWD still present after 'cleanup'"},
            {"when": today - timedelta(days=1), "host_id": "HOST-JUMP", "path": "/etc/ssh/sshd_config", "change": "unknown", "tool": "None", "severity": "Critical", "notes": "No AIDE â€” blind to config change"},
            {"when": today - timedelta(days=3), "host_id": "HOST-JUMP", "path": "/usr/local/bin/jumpwrap", "change": "unknown", "tool": "None", "severity": "High", "notes": "SUID binary unsupervised"},
            {"when": today - timedelta(days=8), "host_id": "HOST-AIX", "path": "/payroll/.extract_lock", "change": "modified", "tool": "None (RTC off)", "severity": "Critical", "notes": "Would have been PowerSC RTC"},
            {"when": today - timedelta(days=12), "host_id": "HOST-AIX", "path": "/etc/exports", "change": "modified", "tool": "None (RTC off)", "severity": "Critical", "notes": "root= added â€” no alert"},
            {"when": today - timedelta(days=4), "host_id": "HOST-WEB", "path": "/etc/nginx/nginx.conf", "change": "modified", "tool": "AIDE", "severity": "Medium", "notes": "Expected change window â€” OK"},
            {"when": today - timedelta(days=6), "host_id": "HOST-SOL", "path": "/etc/ssh/sshd_config", "change": "unknown", "tool": "None Â· BSM off", "severity": "High", "notes": "No integrity trail"},
            {"when": today - timedelta(days=16), "host_id": "HOST-JUMP", "path": "/home/opsnight/.ssh/authorized_keys", "change": "unknown", "tool": "None", "severity": "Critical", "notes": "Aligns with INC-2026-001 window"},
        ]
    )

    mac_posture = pd.DataFrame(
        [
            {"host_id": "HOST-JUMP", "mechanism": "SELinux", "mode": "Enforcing", "policy": "targeted", "status": "Pass", "notes": "OK â€” jump"},
            {"host_id": "HOST-APP", "mechanism": "SELinux", "mode": "Permissive", "policy": "targeted", "status": "Fail", "notes": "FND-UX-019"},
            {"host_id": "HOST-WEB", "mechanism": "SELinux", "mode": "Enforcing", "policy": "targeted", "status": "Pass", "notes": "OK"},
            {"host_id": "HOST-AIX", "mechanism": "TCB / Trusted Computing Base", "mode": "Not enabled", "policy": "â€”", "status": "Fail", "notes": "PowerSC CIS would set"},
            {"host_id": "HOST-SOL", "mechanism": "RBAC + privileges", "mode": "Unused", "policy": "basic", "status": "Fail", "notes": "Shared root instead"},
        ]
    )

    powersc = pd.DataFrame(
        [
            {"feature": "Security & Compliance Automation (pscxpert)", "status": "Enrolled Â· never applied", "desired": "CIS L1 applied", "risk": "Critical", "notes": "FND-UX-005"},
            {"feature": "Real Time Compliance (RTC / FIM)", "status": "Off", "desired": "On Â· /payroll Â· DB2", "risk": "Critical", "notes": "FND-UX-021"},
            {"feature": "Trusted Logging (VIOS)", "status": "Off", "desired": "On", "risk": "Critical", "notes": "Root can wipe local audit"},
            {"feature": "Trusted Boot", "status": "Off", "desired": "On Â· attest", "risk": "High", "notes": "No vTPM attestation"},
            {"feature": "Trusted Firewall", "status": "Off", "desired": "Evaluate", "risk": "Medium", "notes": "Same-frame VLAN shortcut"},
            {"feature": "MFA (PowerSC)", "status": "Off", "desired": "On for root/SSH", "risk": "High", "notes": "Complements jump MFA"},
            {"feature": "Patch Management / TNC", "status": "Not configured", "desired": "SUMA-aware", "risk": "High", "notes": "91d TL lag"},
            {"feature": "EDR / Allow-list", "status": "Not configured", "desired": "Evaluate", "risk": "Medium", "notes": "Qualys agent present"},
        ]
    )

    solaris_comply = pd.DataFrame(
        [
            {"benchmark": "Solaris Security Benchmark", "last_run": today - timedelta(days=390), "score_pct": 34, "result": "fail", "schedule": "None", "notes": "FND-UX-023"},
            {"benchmark": "PCI-DSS (Solaris)", "last_run": today - timedelta(days=390), "score_pct": 28, "result": "fail", "schedule": "None", "notes": "Shared root fails uniqueness"},
            {"benchmark": "Baseline (site custom)", "last_run": None, "score_pct": None, "result": "never", "schedule": "None", "notes": "Not created"},
        ]
    )

    narrative = pd.DataFrame(
        [
            {
                "lane": "Blast radius",
                "text": "JUMP-DMZ-03 is still a password-root SSH beachhead with no AIDE/Tripwire FIM â€” blind during the INC-2026-001 window when opsnight keys may have changed.",
            },
            {
                "lane": "Config vs vuln",
                "text": "Qualys VMDR shows critical OpenSSH/kernel CVEs on app01 blocked by PayrollCo freeze; OpenSCAP/Qualys PC separately fail SELinux, sudo, and UID 0 â€” two queues, one host.",
            },
            {
                "lane": "Integrity gap",
                "text": "PowerSC RTC and Trusted Logging off on AIX; Wazuh FIM excludes the world-writable drop; Solaris has neither BSM nor compliance(8) cadence.",
            },
            {
                "lane": "Unix differentiators",
                "text": "AIX PowerSC feature matrix is almost entirely Off; Solaris compliance assessor last run 2024-08. This is not a Linux-only CIS clone.",
            },
            {
                "lane": "Lynis pulse",
                "text": "Hardening indices drifting down on jump/app/AIX (58â†’49â†’44). web01 is the only host trending up â€” use Lynis for ops pulse, OpenSCAP HTML for auditors.",
            },
        ]
    )

    deep = {
        "FND-UX-001": {
            "memo": "Jump hardening was promised in the INC-2026-001 post-incident plan. Colo night crew refused key-only until a break-glass runbook exists â€” draft is in GRC but unsigned.",
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
            "counterfactual": "Root on JUMP or app01 = uid 0 on the payroll volume â€” classic Unix lateral.",
            "commands": ["exportfs -v", "showmount -e nsk-aix-db01"],
        },
        "FND-UX-005": {
            "memo": "PowerSC licenses purchased after the IBM i assessment push; AIX endpoint enrolled for a PoC that never got a change window.",
            "counterfactual": "Without CIS/STIG apply + RTC, drift on SEC_* and /payroll is invisible until the next manual scan.",
            "commands": ["lssrc -s pscxpert", "PowerSC GUI drift report"],
        },
        "FND-UX-007": {
            "memo": "Mode 777 was a 'temporary' fix when Finance Windows mapping broke ACLs. Ticket closed as done without verification.",
            "counterfactual": "Local unprivileged user plants malware in the payroll drop â€” lands on AIX and toward PRODBOX.",
            "commands": ["ls -ld /opt/jde/drop", "auditctl -w /opt/jde/drop -p wa"],
        },
        "FND-UX-011": {
            "memo": "Patch CAB blocked by PayrollCo IR freeze language that Security Legal interpreted as all change â€” need explicit security-only carve-out.",
            "counterfactual": "OpenSSH regreSSHion-class exposure on the SFTP host facing a third party.",
            "commands": ["dnf updateinfo list security", "Qualys VMDR host view"],
        },
        "FND-UX-014": {
            "memo": "Same shared-root culture called out on IBM i SST/DST. Orbit AMS used the envelope password in 2025-04.",
            "counterfactual": "No attribution if EBS schemas are copied off DR â€” six people and a vendor all look the same in logs (when logs exist).",
            "commands": ["profiles -l", "last root"],
        },
        "FND-UX-019": {
            "memo": "SELinux permissive was the 'make JDE install finish' shortcut. AVC denials were never triaged.",
            "counterfactual": "Even with better file modes, a compromised process can ignore MAC policy while still looking 'SELinux enabled' to casual checks.",
            "commands": ["getenforce", "ausearch -m AVC -ts recent"],
        },
        "FND-UX-020": {
            "memo": "AIDE package was scoped out of the jump golden image to 'reduce attack surface' â€” irony noted in Lynis report.",
            "counterfactual": "sshd_config or jumpwrap changes during an incident leave no integrity evidence for IR.",
            "commands": ["rpm -q aide", "lynis show details FILE-INT"],
        },
        "FND-UX-021": {
            "memo": "Trusted Logging was demo'd on a lab LPAR; prod VIOS change never scheduled. RTC file list still empty.",
            "counterfactual": "Insider or malware with root erases AIX audit â€” no VIOS copy to reconstruct payroll NFS abuse.",
            "commands": ["PowerSC GUI Â· Trusted Logging", "RTC watch list"],
        },
    }

    scan_meta = {
        "scan_id": "UX-SCAN-2026-09",
        "as_of": today,
        "primary_host": "JUMP-DMZ-03",
        "overall_score": 44,
        "overall_rag": _rag(44),
        "delta_pts": -2,
        "prior_scan": "UX-SCAN-2026-08",
        "duration_min": 42,
        "tool_pattern": "Qualys VMDR+PC Â· OpenSCAP Â· Lynis Â· PowerSC Â· Solaris compliance Â· FIM",
        "references": "CIS Â· STIG/SSG Â· PowerSC Â· Tripwire/AIDE Â· NIST 800-53",
        "hosts_in_scope": 5,
        "lynis_fleet_avg": 51,
        "openscap_fleet_avg": 34,
        "vmdr_crit_open": 7,
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
        lynis,
        openscap,
        vulns,
        fim_events,
        mac_posture,
        powersc,
        solaris_comply,
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
        "ux_lynis",
        "ux_openscap",
        "ux_vulns",
        "ux_fim",
        "ux_mac",
        "ux_powersc",
        "ux_sol_comply",
    ]
    need = st.session_state.get(_SYNC_KEY) != seed or "ux_findings" not in st.session_state or "ux_lynis" not in st.session_state
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
            st.caption(f"{row['rag']} {row['score']}% Â· {int(row['fails'])} fails")


def _finding_card(
    row,
    *,
    widget_key: str,
    deep: dict | None = None,
    evidence: pd.DataFrame | None = None,
    tickets: pd.DataFrame | None = None,
):
    st.markdown(f"### {row['finding_id']} Â· {row['title']}")
    a, b, c, d = st.columns(4)
    a.metric("Severity", row["severity"])
    b.metric("Domain", row["domain_id"])
    c.metric("Status", row["status"])
    d.metric("Due", _fmt(row["due"]))
    st.write(row["detail"])
    c1, c2 = st.columns(2)
    c1.write(f"**Evidence cmd:** `{row['evidence']}`")
    c1.write(f"**Owner:** {row['owner']} Â· **Host:** {row['host_id']}")
    c1.write(f"**Linked:** {row['linked']}")
    c2.write(f"**Remediation:** {row['remediation']}")
    c2.write(f"**CIS:** {row['cis']} Â· **STIG:** {row['stig']}")
    c2.write(f"**ISO 27001:** {row['iso27001']} Â· **SOC 2:** {row['soc2']} Â· **PCI:** {row['pci']}")
    c2.write(f"**Refs:** {row['ref']}")

    fid = row["finding_id"]
    if deep and fid in deep:
        with st.expander("Program memo / counterfactual", expanded=False):
            st.write(f"**Memo:** {deep[fid].get('memo', '')}")
            st.write(f"**Without fix:** {deep[fid].get('counterfactual', '')}")
            if deep[fid].get("commands"):
                st.write("**Reproduce:** " + " Â· ".join(f"`{c}`" for c in deep[fid]["commands"]))
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
        lede="Best-in-breed Unix/Linux posture â€” Qualys VMDR + Policy Compliance, OpenSCAP/SSG rule evidence, Lynis hardening index, Tripwire/AIDE/Wazuh FIM, SELinux/MAC, IBM PowerSC (RTC Â· Trusted Logging), and Oracle Solaris compliance(8). Synthetic NorthStack estate (JUMP-DMZ-03 and friends).",
        kicker="Linux Â· AIX Â· Solaris",
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
        lynis,
        openscap,
        vulns,
        fim_events,
        mac_posture,
        powersc,
        solaris_comply,
    ) = _sync(seed)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Scan scope")
    host_opts = ["All hosts"] + hosts["hostname"].tolist()
    host_pick = st.sidebar.selectbox("Host", host_opts, index=1)
    family_opts = ["All OS"] + sorted(hosts["os_family"].unique().tolist())
    family_pick = st.sidebar.selectbox("OS family", family_opts, index=0)
    sev_f = st.sidebar.multiselect("Severities", SEVERITY, default=["Critical", "High", "Medium"])
    open_only = st.sidebar.checkbox("Open / in progress / blocked only", value=True)
    st.sidebar.caption("Sample assessment â€” not connected to live hosts.")

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
    vmdr_crit = int(
        ((vulns["severity"] == "Critical") & (vulns["status"].astype(str).str.contains("Active"))).sum()
    )
    lynis_avg = float(scan_meta.get("lynis_fleet_avg", hosts["lynis_index"].mean()))
    oscap_avg = float(scan_meta.get("openscap_fleet_avg", hosts["openscap_pass_pct"].mean()))
    fim_blind = int(fim_events["tool"].astype(str).str.contains("None", na=False).sum())

    k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)
    k1.metric("Overall score", f"{overall}%", delta=f"{scan_meta.get('delta_pts', 0):+d} vs prior")
    k2.metric("Critical findings", crit)
    k3.metric("VMDR crit open", vmdr_crit)
    k4.metric("Lynis fleet avg", f"{lynis_avg:.0f}")
    k5.metric("OpenSCAP avg", f"{oscap_avg:.0f}%")
    k6.metric("Baseline drift", drift)
    k7.metric("FIM blind events", fim_blind)
    k8.metric("Open tickets", open_tk)

    if overall < 55:
        st.error(
            f"Scan {scan_meta['scan_id']} â€” estate is Red overall "
            f"({scan_meta.get('delta_pts', 0):+d} vs {scan_meta.get('prior_scan', 'prior')}). "
            "Config fails (OpenSCAP/PC) and vuln debt (VMDR) both Red â€” plus FIM/PowerSC integrity gaps."
        )
    elif crit:
        st.warning(f"{crit} critical findings open â€” treat JUMP SSH, SELinux, PowerSC RTC, and payroll FS before board packet.")

    (
        work,
        domains_tab,
        findings_tab,
        hosts_tab,
        scap_tab,
        vuln_tab,
        fim_tab,
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
            "Hosts / Lynis",
            "CIS Â· OpenSCAP",
            "Vulns Â· VMDR",
            "FIM Â· RTC",
            "SSH / auth",
            "Filesystem / NFS",
            "Listeners",
            "Audit trails",
            "PowerSC Â· Solaris",
            "Crosswalk",
            "Baseline",
            "Board brief",
            "Export",
        ]
    )

    with work:
        st.subheader("Unix/Linux posture workbench")
        st.caption(
            f"**{scan_meta['scan_id']}** Â· {_fmt(scan_meta['as_of'])} Â· ~{scan_meta.get('duration_min', 30)} min Â· "
            f"{scan_meta['hosts_in_scope']} hosts Â· {scan_meta['tool_pattern']}"
        )
        _domain_pillars(domains)

        st.markdown("**Executive narrative**")
        for _, n in narrative.iterrows():
            st.write(f"**{n['lane']}:** {n['text']}")

        st.markdown("---")
        st.markdown("**Remediation queue**")
        for _, t in tickets.sort_values("due").iterrows():
            flag = " Â· BLOCKED" if "Blocked" in str(t["status"]) else ""
            with st.expander(f"{t['ticket_id']} Â· {t['title']} Â· {_fmt(t['due'])}{flag}"):
                st.write(
                    f"**Finding:** {t['finding_id']} Â· **Owner:** {t['owner']} Â· "
                    f"**Status:** {t['status']} Â· **Effort:** {t['effort']}"
                )

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
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
            fig.update_layout(yaxis_range=[0, 105], height=340)
            st.plotly_chart(fig, use_container_width=True, key="plotly_ux_domains")
        with c2:
            latest_lynis = lynis.sort_values("as_of").groupby("host_id").tail(1)
            latest_lynis = latest_lynis.merge(hosts[["host_id", "hostname"]], on="host_id")
            fig = px.bar(latest_lynis, x="hostname", y="index", color="index", title="Lynis hardening index (pulse)")
            fig.update_layout(height=340, yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True, key="plotly_ux_lynis_bar")
        with c3:
            fig = px.line(hist, x="as_of", y="overall", markers=True, title="Overall score trend")
            fig.update_layout(height=340)
            st.plotly_chart(fig, use_container_width=True, key="plotly_ux_hist")

        st.markdown("**Hosts in scope**")
        st.dataframe(
            hosts[
                [
                    "hostname",
                    "os_family",
                    "os",
                    "lynis_index",
                    "openscap_pass_pct",
                    "mac_mode",
                    "fim_tool",
                    "open_cves_crit",
                    "days_since_patch",
                    "crown_jewel",
                    "owner",
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
            "FND-UX-011",
            "FND-UX-019",
            "FND-UX-020",
            "FND-UX-021",
            "FND-UX-014",
        ]
        feat = findings[findings["finding_id"].isin(FEATURED_FINDINGS)].copy()
        feat["_o"] = feat["finding_id"].map(lambda x: pref.index(x) if x in pref else 99)
        for _, row in feat.sort_values("_o").iterrows():
            st.markdown("---")
            _finding_card(row, widget_key=f"feat_{row['finding_id']}", deep=deep, evidence=evidence, tickets=tickets)

    with domains_tab:
        st.subheader("Scan domains")
        st.caption("Eight areas â€” Auth, Priv, SSH, Net, FS, Kernel/MAC, Audit/FIM, Patch/VMDR.")
        st.dataframe(domains, use_container_width=True, hide_index=True)
        for _, row in domains.iterrows():
            with st.expander(f"{row['domain_id']} Â· {row['domain']} Â· {row['rag']} {row['score']}%"):
                st.write(f"**Checks:** {int(row['checks'])} Â· **Fails:** {int(row['fails'])}")
                st.write(f"**Benchmark:** {row['benchmark']}")
                sub = findings[findings["domain_id"] == row["domain_id"]]
                st.dataframe(
                    sub[["finding_id", "severity", "title", "status", "due"]].assign(due=sub["due"].map(_fmt)),
                    use_container_width=True,
                    hide_index=True,
                )

    with findings_tab:
        st.subheader("Finding register")
        search = st.text_input("Search findings", placeholder="SELinux, PowerSC, AIDE, NFSâ€¦", key="ux_fnd_search")
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
        st.subheader("Hosts + Lynis hardening index")
        st.caption("Lynis = ops pulse (0â€“100). Pair with OpenSCAP HTML for auditors â€” they answer different questions.")
        st.dataframe(hosts, use_container_width=True, hide_index=True)
        c1, c2 = st.columns(2)
        with c1:
            fig = px.line(lynis.merge(hosts[["host_id", "hostname"]], on="host_id"), x="as_of", y="index", color="hostname", markers=True, title="Lynis index trend")
            fig.update_layout(height=360, yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True, key="plotly_ux_lynis_trend")
        with c2:
            fig = px.scatter(
                hosts,
                x="lynis_index",
                y="openscap_pass_pct",
                color="os_family",
                size="open_cves_crit",
                hover_name="hostname",
                title="Lynis vs OpenSCAP (size = crit CVEs)",
            )
            fig.update_layout(height=360, xaxis_range=[0, 100], yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True, key="plotly_ux_lynis_oscap")
        st.markdown("**MAC posture**")
        st.dataframe(mac_posture, use_container_width=True, hide_index=True)
        st.markdown("**Privileged identities**")
        st.dataframe(priv.assign(last_login=priv["last_login"].map(_fmt)), use_container_width=True, hide_index=True)

    with scap_tab:
        st.subheader("CIS / OpenSCAP / Policy Compliance rules")
        st.caption("XCCDF-style rule results â€” OpenSCAP SSG, Qualys PC, Tenable CIS host audit, PowerSC pscxpert, Solaris compliance(8).")
        st.dataframe(openscap, use_container_width=True, hide_index=True)
        fail_n = int((openscap["result"] == "fail").sum())
        st.error(f"{fail_n} of {len(openscap)} sampled rules failing.")
        by_host = openscap.groupby(["host_id", "result"]).size().reset_index(name="count")
        fig = px.bar(by_host, x="host_id", y="count", color="result", barmode="stack", title="Rule results by host")
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_oscap")
        st.markdown("**SSH matrix (sshd_config vs CIS)**")
        st.dataframe(ssh_matrix, use_container_width=True, hide_index=True)

    with vuln_tab:
        st.subheader("Vulnerability queue (VMDR)")
        st.caption("Separate from config findings â€” Qualys VMDR / IBM APAR / CrowdStrike. Patch ticket on app01 is Blocked by PayrollCo freeze.")
        st.dataframe(vulns, use_container_width=True, hide_index=True)
        active = vulns[vulns["status"].astype(str).str.contains("Active")]
        st.warning(f"{len(active)} active detections Â· {int((active['severity']=='Critical').sum())} critical.")
        fig = px.bar(vulns, x="host_id", y="age_days", color="severity", hover_data=["cve", "title", "status"], title="CVE age by host")
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_vmdr")

    with fim_tab:
        st.subheader("File integrity / Real Time Compliance")
        st.caption("Tripwire Â· AIDE Â· Wazuh FIM Â· PowerSC RTC â€” change detection on crown-jewel paths. Blind spots are the story.")
        st.dataframe(fim_events.assign(when=fim_events["when"].map(_fmt)), use_container_width=True, hide_index=True)
        blind = fim_events[fim_events["tool"].astype(str).str.contains("None")]
        st.error(f"{len(blind)} events with no FIM sensor â€” including JUMP during INC-2026-001 window and AIX /etc/exports.")
        st.markdown("**Host FIM coverage**")
        st.dataframe(hosts[["hostname", "os_family", "fim_tool", "mac_mode"]], use_container_width=True, hide_index=True)

    with ssh_tab:
        st.subheader("SSH / authentication posture")
        st.caption("sshd_config vs CIS â€” jump and AIX still fail PermitRootLogin / PasswordAuthentication.")
        st.dataframe(ssh_matrix, use_container_width=True, hide_index=True)
        fail_n = int((ssh_matrix["status"] == "Fail").sum())
        st.error(f"{fail_n} of {len(ssh_matrix)} SSH controls failing CIS desired state.")
        fig = px.histogram(ssh_matrix, x="status", color="host_id", barmode="group", title="SSH control pass/fail by host")
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_ssh")

    with fs_tab:
        st.subheader("Filesystem, SUID & NFS / shares")
        st.caption("World-writable drops and NFS root= â€” classic Unix lateral into the payroll path.")
        st.markdown("**Sensitive paths**")
        st.dataframe(filesys, use_container_width=True, hide_index=True)
        hot = filesys[filesys["risk"].isin(["Critical", "High"])]
        st.warning(f"{len(hot)} paths Critical/High â€” /opt/jde/drop and /payroll lead.")
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
        st.caption("ss / netstat-style sample â€” Telnet, FTP, NFS, and wide Oracle listener.")
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
        st.caption("Spike on JUMP ~day âˆ’16 aligns with portal stuffing (INC-2026-001). Solaris near-flat â€” BSM off.")
        daily = audit_df.groupby(["day", "host_id"], as_index=False)["count"].sum()
        fig = px.area(daily, x="day", y="count", color="host_id", title="Audit events by host")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="plotly_ux_aud")
        by_type = audit_df.groupby("entry_type", as_index=False)["count"].sum()
        fig2 = px.bar(by_type, x="entry_type", y="count", title="Events by type (30d)")
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True, key="plotly_ux_aud_type")
        st.warning("app01 auditd retention ~7 days (FND-UX-010); Solaris BSM disabled (FND-UX-009); AIX Trusted Logging off (FND-UX-021).")

    with aix_sol_tab:
        st.subheader("IBM PowerSC Â· Oracle Solaris compliance")
        st.caption("Why this isn't a Linux-only CIS clone â€” PowerSC feature matrix and Solaris compliance(8) assessor.")
        st.markdown("**PowerSC feature matrix (nsk-aix-db01)**")
        st.dataframe(powersc, use_container_width=True, hide_index=True)
        off_n = int(powersc["status"].astype(str).str.contains("Off|never|Not", case=False).sum())
        st.error(f"{off_n} of {len(powersc)} PowerSC capabilities Off / never applied.")

        st.markdown("**Solaris compliance(8) benchmarks**")
        show_sc = solaris_comply.copy()
        show_sc["last_run"] = show_sc["last_run"].map(_fmt)
        st.dataframe(show_sc, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**AIX findings**")
            aix_f = findings[findings["host_id"] == "HOST-AIX"]
            st.dataframe(aix_f[["finding_id", "severity", "title", "status"]], use_container_width=True, hide_index=True)
        with c2:
            st.markdown("**Solaris findings**")
            sol_f = findings[findings["host_id"] == "HOST-SOL"]
            st.dataframe(sol_f[["finding_id", "severity", "title", "status"]], use_container_width=True, hide_index=True)

        with st.expander("Recommended PowerSC apply sequence (sample)"):
            st.write(
                "1. CAB for CIS Level 1 via pscxpert on HA secondary first Â· "
                "2. Enable Real Time Compliance watches on /payroll and DB2 configs Â· "
                "3. Turn on Trusted Logging to VIOS Â· "
                "4. Weekly drift â†’ GRC Â· 5. Retire NFS root= with FND-UX-003."
            )
        with st.expander("Solaris compliance cadence (sample)"):
            st.write(
                "`compliance assess -b solaris` weekly Â· archive HTML to GRC evidence locker Â· "
                "add pci-dss benchmark for EBS schemas Â· fail change if score regresses >5 pts."
            )

    with cross_tab:
        st.subheader("Compliance crosswalk")
        st.caption("Each finding mapped to CIS, STIG, ISO 27001, SOC 2, and PCI â€” reuse evidence across audits.")
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
        st.markdown("**Authoritative references / product patterns**")
        st.dataframe(refs, use_container_width=True, hide_index=True)

    with base_tab:
        st.subheader("Hardening baseline vs current")
        st.caption("Desired CIS/STIG/PowerSC/FIM state vs live â€” drift drives the Red domains.")
        show_b = baseline.copy()
        show_b["last_change"] = show_b["last_change"].map(_fmt)
        st.dataframe(show_b, use_container_width=True, hide_index=True)
        drifted = baseline[baseline["drift"]]
        st.error(f"{len(drifted)} of {len(baseline)} controls drifted â€” SSH, sudo, SELinux, FIM, PowerSC, BSM.")
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
        st.subheader("Board / CISO brief â€” Unix/Linux")
        st.markdown(
            f"**Scan:** {scan_meta['scan_id']} Â· primary **{scan_meta['primary_host']}** "
            f"({_fmt(scan_meta['as_of'])}) Â· Overall **{overall}% ({scan_meta['overall_rag']})** Â· "
            f"Î” {scan_meta.get('delta_pts', 0):+d} vs {scan_meta.get('prior_scan', 'prior')}"
        )
        st.markdown("#### Headline")
        st.write(
            f"NorthStack Unix/Linux estate scores **{overall}%** across **5** hosts (RHEL, AIX, Solaris). "
            f"**{crit} critical** config findings plus **{vmdr_crit}** active critical CVEs (VMDR). "
            f"Lynis fleet avg **{lynis_avg:.0f}** / OpenSCAP avg **{oscap_avg:.0f}%**. "
            f"**JUMP** has no FIM; **app01** is SELinux permissive with sudo NOPASSWD and world-writable PayrollCo drop; "
            f"**AIX** PowerSC RTC/Trusted Logging Off with NFS root=; **Solaris** compliance(8) last run 2024-08, Telnet still up."
        )
        st.markdown("#### Domain RAG")
        for _, r in domains.iterrows():
            st.write(f"- **{r['domain']}:** {r['rag']} {r['score']}% ({int(r['fails'])} fails) â€” {r['benchmark']}")
        st.markdown("#### Top asks (30 days)")
        for fid in ["FND-UX-001", "FND-UX-019", "FND-UX-003", "FND-UX-007", "FND-UX-021", "FND-UX-011", "FND-UX-020", "FND-UX-014"]:
            row = findings[findings["finding_id"] == fid].iloc[0]
            st.write(f"- **{fid}** ({row['severity']}): {row['title']}")
        st.markdown("#### Change tickets in flight")
        for _, t in tickets.head(8).iterrows():
            st.write(f"- **{t['ticket_id']}** [{t['status']}]: {t['title']}")
        st.markdown("#### Framework impact")
        bits = [f"{r['framework'].split('(')[0].strip()} **{r['readiness_pct']:.0f}%**" for _, r in frameworks.iterrows()]
        st.write(" Â· ".join(bits) + ".")
        st.markdown("#### Linked portfolio")
        st.write(
            "INC-2026-001 Â· INC-2026-009 Â· AST-2026-005 Â· JUMP-DMZ-03 Â· PRODBOX Â· "
            "KRI-2026-001/002 Â· CMP-2026-001 Â· GAP-2026-001 Â· DST-2026-001 Â· "
            "PayrollCo Â· Orbit AMS Â· IBM i assessment narrative"
        )

    with export_tab:
        st.subheader("Export")
        demo_kit.csv_download(findings.assign(due=findings["due"].map(_fmt)), "ux_findings.csv", label="Download findings")
        demo_kit.csv_download(domains, "ux_domain_scores.csv", label="Download domain scores")
        demo_kit.csv_download(hosts, "ux_hosts.csv", label="Download hosts")
        demo_kit.csv_download(lynis.assign(as_of=lynis["as_of"].map(_fmt)), "ux_lynis_index.csv", label="Download Lynis index")
        demo_kit.csv_download(openscap, "ux_openscap_rules.csv", label="Download OpenSCAP/PC rules")
        demo_kit.csv_download(vulns, "ux_vmdr_vulns.csv", label="Download VMDR vulns")
        demo_kit.csv_download(fim_events.assign(when=fim_events["when"].map(_fmt)), "ux_fim_events.csv", label="Download FIM events")
        demo_kit.csv_download(mac_posture, "ux_mac_posture.csv", label="Download MAC posture")
        demo_kit.csv_download(powersc, "ux_powersc_matrix.csv", label="Download PowerSC matrix")
        demo_kit.csv_download(
            solaris_comply.assign(last_run=solaris_comply["last_run"].map(_fmt)),
            "ux_solaris_compliance.csv",
            label="Download Solaris compliance",
        )
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
                {"metric": "vmdr_crit_open", "value": vmdr_crit},
                {"metric": "lynis_fleet_avg", "value": lynis_avg},
                {"metric": "openscap_fleet_avg", "value": oscap_avg},
                {"metric": "baseline_drift", "value": drift},
                {"metric": "open_tickets", "value": open_tk},
                {"metric": "hosts_in_scope", "value": scan_meta["hosts_in_scope"]},
            ]
        )
        demo_kit.csv_download(summary, "ux_executive_summary.csv", label="Download executive summary")


if __name__ == "__main__":
    main()
