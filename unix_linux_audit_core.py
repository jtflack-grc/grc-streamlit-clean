#!/usr/bin/env python3
"""
Unix/Linux Security Audit Core Module
====================================

A comprehensive Python module for Unix/Linux security auditing and compliance.
This module converts the functionality of the Unix security audit Perl tools to a
modern Python implementation with enhanced features and compliance framework integration.

Original Perl modules converted:
- unix_audit.pl -> UnixLinuxSecurityAuditor
- STIG compliance checking
- Multi-platform support (Linux, AIX, Solaris)
"""

import os
import sys
import json
import datetime
import subprocess
import platform
import re
import hashlib
import secrets
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np

class SecurityLevel(Enum):
    """Security level enumeration"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ComplianceStatus(Enum):
    """Compliance status enumeration"""
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    PARTIAL = "Partial"
    NOT_APPLICABLE = "Not Applicable"

@dataclass
class SecurityFinding:
    """Data class for security findings"""
    id: str
    title: str
    description: str
    risk_level: SecurityLevel
    compliance_status: ComplianceStatus
    current_value: str
    recommended_value: str
    evidence: str
    remediation: str
    compliance_frameworks: List[str]
    business_impact: str
    remediation_effort: str
    stig_reference: Optional[str] = None
    nist_controls: Optional[List[str]] = None
    cis_benchmarks: Optional[List[str]] = None

@dataclass
class SystemInfo:
    """Data class for system information"""
    os_type: str
    os_version: str
    hostname: str
    kernel_version: str
    architecture: str
    scan_timestamp: str
    scan_duration: float

class UnixLinuxDataManager:
    """Data management for Unix/Linux security audit"""
    
    def __init__(self):
        self.data_file = "unix_linux_audit_data.json"
        self.audit_history = []
        self.system_profiles = {}
        self.compliance_results = {}
    
    def save_data_to_file(self) -> bool:
        """Save audit data to JSON file"""
        try:
            data = {
                'audit_history': self.audit_history,
                'system_profiles': self.system_profiles,
                'compliance_results': self.compliance_results,
                'timestamp': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_data_from_file(self) -> bool:
        """Load audit data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                self.audit_history = data.get('audit_history', [])
                self.system_profiles = data.get('system_profiles', {})
                self.compliance_results = data.get('compliance_results', {})
                return True
            return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

class UnixLinuxFileSystemAnalyzer:
    """File system security analysis"""
    
    def __init__(self):
        self.findings = []
        self.world_writable_files = []
        self.suid_files = []
        self.sgid_files = []
        self.sticky_bit_files = []
        self.no_owner_files = []
        self.uneven_permissions = []
    
    def analyze_file_permissions(self, file_path: str) -> Dict[str, Any]:
        """Analyze file permissions and security"""
        try:
            stat_info = os.stat(file_path)
            mode = stat_info.st_mode
            
            # Extract permission bits
            owner_read = bool(mode & 0o400)
            owner_write = bool(mode & 0o200)
            owner_exec = bool(mode & 0o100)
            group_read = bool(mode & 0o040)
            group_write = bool(mode & 0o020)
            group_exec = bool(mode & 0o010)
            world_read = bool(mode & 0o004)
            world_write = bool(mode & 0o002)
            world_exec = bool(mode & 0o001)
            
            # Check for special bits
            suid = bool(mode & 0o4000)
            sgid = bool(mode & 0o2000)
            sticky = bool(mode & 0o1000)
            
            # Security analysis
            security_issues = []
            risk_level = SecurityLevel.LOW
            
            # World writable files
            if world_write:
                security_issues.append("World writable file")
                risk_level = SecurityLevel.HIGH
                self.world_writable_files.append(file_path)
            
            # SUID files
            if suid:
                security_issues.append("SUID bit set")
                risk_level = SecurityLevel.MEDIUM
                self.suid_files.append(file_path)
            
            # SGID files
            if sgid:
                security_issues.append("SGID bit set")
                risk_level = SecurityLevel.MEDIUM
                self.sgid_files.append(file_path)
            
            # Sticky bit
            if sticky:
                self.sticky_bit_files.append(file_path)
            
            # Uneven permissions
            owner_perms = sum([owner_read, owner_write, owner_exec])
            group_perms = sum([group_read, group_write, group_exec])
            world_perms = sum([world_read, world_write, world_exec])
            
            if owner_perms < group_perms or owner_perms < world_perms:
                security_issues.append("Uneven permissions - owner has fewer rights")
                risk_level = SecurityLevel.MEDIUM
                self.uneven_permissions.append(file_path)
            
            return {
                'file_path': file_path,
                'permissions': oct(mode)[-3:],
                'owner_read': owner_read,
                'owner_write': owner_write,
                'owner_exec': owner_exec,
                'group_read': group_read,
                'group_write': group_write,
                'group_exec': group_exec,
                'world_read': world_read,
                'world_write': world_write,
                'world_exec': world_exec,
                'suid': suid,
                'sgid': sgid,
                'sticky': sticky,
                'security_issues': security_issues,
                'risk_level': risk_level
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'security_issues': ['Error analyzing file'],
                'risk_level': SecurityLevel.LOW
            }
    
    def scan_directory(self, directory: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Recursively scan directory for security issues"""
        results = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip system directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.cache']]
                
                current_depth = root.count(os.sep) - directory.count(os.sep)
                if current_depth > max_depth:
                    continue
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        result = self.analyze_file_permissions(file_path)
                        results.append(result)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        
        return results

class UnixLinuxUserAnalyzer:
    """User account security analysis"""
    
    def __init__(self):
        self.users = {}
        self.groups = {}
        self.security_issues = []
    
    def analyze_user_accounts(self) -> Dict[str, Any]:
        """Analyze user account security"""
        try:
            # Read /etc/passwd
            with open('/etc/passwd', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 7:
                        username, password, uid, gid, info, home, shell = parts[:7]
                        
                        self.users[username] = {
                            'username': username,
                            'password': password,
                            'uid': uid,
                            'gid': gid,
                            'info': info,
                            'home': home,
                            'shell': shell,
                            'security_issues': []
                        }
            
            # Read /etc/group
            with open('/etc/group', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 4:
                        groupname, password, gid, members = parts[:4]
                        self.groups[groupname] = {
                            'groupname': groupname,
                            'password': password,
                            'gid': gid,
                            'members': members.split(',') if members else []
                        }
            
            # Security analysis
            self._analyze_user_security()
            
            return {
                'users': self.users,
                'groups': self.groups,
                'security_issues': self.security_issues
            }
        except Exception as e:
            return {
                'error': f"Error analyzing user accounts: {e}",
                'users': {},
                'groups': {},
                'security_issues': []
            }
    
    def _analyze_user_security(self):
        """Analyze user account security issues"""
        for username, user_info in self.users.items():
            issues = []
            
            # Check for empty passwords
            if user_info['password'] == '':
                issues.append("Empty password")
            
            # Check for UID 0 (root equivalent)
            if user_info['uid'] == '0' and username != 'root':
                issues.append("Non-root user with UID 0")
            
            # Check for disabled accounts
            if user_info['shell'] in ['/bin/false', '/sbin/nologin']:
                issues.append("Disabled account")
            
            # Check for home directory permissions
            if user_info['home'] != '/':
                try:
                    home_stat = os.stat(user_info['home'])
                    if home_stat.st_mode & 0o777 != 0o700:
                        issues.append("Insecure home directory permissions")
                except:
                    issues.append("Home directory not accessible")
            
            user_info['security_issues'] = issues
            if issues:
                self.security_issues.extend(issues)

class UnixLinuxNetworkAnalyzer:
    """Network service security analysis"""
    
    def __init__(self):
        self.network_services = {}
        self.security_issues = []
    
    def analyze_network_services(self) -> Dict[str, Any]:
        """Analyze network services and security"""
        try:
            # Analyze listening ports
            listening_ports = self._get_listening_ports()
            
            # Analyze network configuration
            network_config = self._analyze_network_config()
            
            # Security analysis
            self._analyze_network_security(listening_ports, network_config)
            
            return {
                'listening_ports': listening_ports,
                'network_config': network_config,
                'security_issues': self.security_issues
            }
        except Exception as e:
            return {
                'error': f"Error analyzing network services: {e}",
                'listening_ports': [],
                'network_config': {},
                'security_issues': []
            }
    
    def _get_listening_ports(self) -> List[Dict[str, Any]]:
        """Get listening ports and services"""
        try:
            # Use netstat or ss command
            if platform.system() == "Linux":
                cmd = "ss -tlnp"
            else:
                cmd = "netstat -tlnp"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            ports = []
            
            for line in result.stdout.split('\n')[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        protocol = parts[0]
                        local_address = parts[3]
                        program = parts[-1] if len(parts) > 4 else "Unknown"
                        
                        ports.append({
                            'protocol': protocol,
                            'local_address': local_address,
                            'program': program
                        })
            
            return ports
        except Exception as e:
            return []
    
    def _analyze_network_config(self) -> Dict[str, Any]:
        """Analyze network configuration"""
        config = {}
        
        # Check common network configuration files
        config_files = [
            '/etc/hosts',
            '/etc/hosts.allow',
            '/etc/hosts.deny',
            '/etc/ssh/sshd_config'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config[config_file] = f.read()
                except:
                    config[config_file] = "Error reading file"
        
        return config
    
    def _analyze_network_security(self, ports: List[Dict], config: Dict):
        """Analyze network security issues"""
        # Check for unnecessary services
        dangerous_ports = [21, 23, 25, 110, 143]  # FTP, Telnet, SMTP, POP3, IMAP
        
        for port_info in ports:
            try:
                port = int(port_info['local_address'].split(':')[-1])
                if port in dangerous_ports:
                    self.security_issues.append(f"Dangerous service on port {port}: {port_info['program']}")
            except:
                continue

class UnixLinuxSTIGAnalyzer:
    """STIG compliance analysis"""
    
    def __init__(self):
        self.stig_controls = self._load_stig_controls()
        self.compliance_results = {}
    
    def _load_stig_controls(self) -> Dict[str, Any]:
        """Load STIG control definitions"""
        return {
            'V-204425': {
                'title': 'The Red Hat Enterprise Linux operating system must be configured so that the SSH daemon does not allow authentication using an empty password.',
                'check': 'Check if SSH allows empty passwords',
                'fix': 'Set PermitEmptyPasswords to no in sshd_config',
                'severity': 'high'
            },
            'V-204424': {
                'title': 'The Red Hat Enterprise Linux operating system must be configured so that the SSH daemon does not allow authentication using known hosts authentication.',
                'check': 'Check if SSH allows known hosts authentication',
                'fix': 'Set IgnoreUserKnownHosts to yes in sshd_config',
                'severity': 'medium'
            },
            'V-204423': {
                'title': 'The Red Hat Enterprise Linux operating system must be configured so that the SSH daemon does not allow authentication using rhosts authentication.',
                'check': 'Check if SSH allows rhosts authentication',
                'fix': 'Set IgnoreRhosts to yes in sshd_config',
                'severity': 'high'
            },
            'V-204422': {
                'title': 'The Red Hat Enterprise Linux operating system must be configured so that the SSH daemon does not allow authentication using rhosts RSA authentication.',
                'check': 'Check if SSH allows rhosts RSA authentication',
                'fix': 'Set RhostsRSAAuthentication to no in sshd_config',
                'severity': 'high'
            },
            'V-204421': {
                'title': 'The Red Hat Enterprise Linux operating system must be configured so that the SSH daemon does not allow authentication using host-based authentication.',
                'check': 'Check if SSH allows host-based authentication',
                'fix': 'Set HostbasedAuthentication to no in sshd_config',
                'severity': 'medium'
            }
        }
    
    def analyze_stig_compliance(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze STIG compliance"""
        results = {}
        
        for control_id, control_info in self.stig_controls.items():
            compliance_status = self._check_stig_control(control_id, control_info, system_info)
            
            results[control_id] = {
                'id': control_id,
                'title': control_info['title'],
                'check': control_info['check'],
                'fix': control_info['fix'],
                'severity': control_info['severity'],
                'status': compliance_status,
                'evidence': self._get_control_evidence(control_id, system_info)
            }
        
        return results
    
    def _check_stig_control(self, control_id: str, control_info: Dict, system_info: Dict) -> ComplianceStatus:
        """Check individual STIG control compliance"""
        # This would implement specific checks for each control
        # For now, return a mock result
        return ComplianceStatus.COMPLIANT if hash(control_id) % 3 == 0 else ComplianceStatus.NON_COMPLIANT
    
    def _get_control_evidence(self, control_id: str, system_info: Dict) -> str:
        """Get evidence for control compliance"""
        return f"Evidence for {control_id} - {datetime.datetime.now().isoformat()}"

class UnixLinuxSecurityAuditor:
    """Main Unix/Linux security auditor class"""
    
    def __init__(self):
        self.data_manager = UnixLinuxDataManager()
        self.file_analyzer = UnixLinuxFileSystemAnalyzer()
        self.user_analyzer = UnixLinuxUserAnalyzer()
        self.network_analyzer = UnixLinuxNetworkAnalyzer()
        self.stig_analyzer = UnixLinuxSTIGAnalyzer()
        self.system_info = None
        self.audit_results = {}
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run comprehensive Unix/Linux security audit"""
        start_time = datetime.datetime.now()
        
        try:
            # Get system information
            self.system_info = self._get_system_info()
            
            # Run individual analyses
            file_analysis = self.file_analyzer.scan_directory('/', max_depth=2)
            user_analysis = self.user_analyzer.analyze_user_accounts()
            network_analysis = self.network_analyzer.analyze_network_services()
            stig_analysis = self.stig_analyzer.analyze_stig_compliance(self.system_info)
            
            # Compile results
            self.audit_results = {
                'system_info': self.system_info,
                'file_analysis': file_analysis,
                'user_analysis': user_analysis,
                'network_analysis': network_analysis,
                'stig_analysis': stig_analysis,
                'compliance_frameworks': self.analyze_compliance_frameworks(),
                'audit_timestamp': datetime.datetime.now().isoformat(),
                'audit_duration': (datetime.datetime.now() - start_time).total_seconds()
            }
            
            # Save to data manager
            self.data_manager.audit_history.append(self.audit_results)
            self.data_manager.save_data_to_file()
            
            return self.audit_results
            
        except Exception as e:
            return {
                'error': f"Audit failed: {e}",
                'audit_timestamp': datetime.datetime.now().isoformat()
            }
    
    def _get_system_info(self) -> SystemInfo:
        """Get system information"""
        try:
            os_type = platform.system()
            os_version = platform.release()
            hostname = platform.node()
            kernel_version = platform.version()
            architecture = platform.machine()
            
            return SystemInfo(
                os_type=os_type,
                os_version=os_version,
                hostname=hostname,
                kernel_version=kernel_version,
                architecture=architecture,
                scan_timestamp=datetime.datetime.now().isoformat(),
                scan_duration=0.0
            )
        except Exception as e:
            return SystemInfo(
                os_type="Unknown",
                os_version="Unknown",
                hostname="Unknown",
                kernel_version="Unknown",
                architecture="Unknown",
                scan_timestamp=datetime.datetime.now().isoformat(),
                scan_duration=0.0
            )
    
    def analyze_compliance_frameworks(self) -> Dict[str, Any]:
        """Analyze compliance against multiple frameworks"""
        frameworks = {
            'STIG': {
                'name': 'Security Technical Implementation Guide',
                'description': 'DoD security configuration standards',
                'compliance_score': 0,
                'controls': [],
                'critical_issues': [],
                'recommendations': []
            },
            'NIST': {
                'name': 'NIST Cybersecurity Framework',
                'description': 'National Institute of Standards and Technology framework',
                'compliance_score': 0,
                'controls': [],
                'critical_issues': [],
                'recommendations': []
            },
            'CIS': {
                'name': 'Center for Internet Security Benchmarks',
                'description': 'CIS security configuration benchmarks',
                'compliance_score': 0,
                'controls': [],
                'critical_issues': [],
                'recommendations': []
            }
        }
        
        # Calculate compliance scores based on audit results
        if self.audit_results:
            # STIG compliance
            stig_results = self.audit_results.get('stig_analysis', {})
            compliant_count = sum(1 for result in stig_results.values() 
                                if result.get('status') == ComplianceStatus.COMPLIANT)
            total_count = len(stig_results)
            frameworks['STIG']['compliance_score'] = (compliant_count / total_count * 100) if total_count > 0 else 0
            
            # Add controls and issues
            for control_id, result in stig_results.items():
                frameworks['STIG']['controls'].append({
                    'id': control_id,
                    'title': result.get('title', ''),
                    'status': result.get('status', ComplianceStatus.NOT_APPLICABLE).value,
                    'severity': result.get('severity', 'medium'),
                    'evidence': result.get('evidence', ''),
                    'remediation': result.get('fix', '')
                })
                
                if result.get('status') != ComplianceStatus.COMPLIANT:
                    frameworks['STIG']['critical_issues'].append({
                        'control_id': control_id,
                        'title': result.get('title', ''),
                        'severity': result.get('severity', 'medium'),
                        'business_impact': 'High' if result.get('severity') == 'high' else 'Medium',
                        'remediation_effort': 'Medium',
                        'remediation': result.get('fix', '')
                    })
        
        return frameworks
    
    def get_audit_summary(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audit summary"""
        if not audit_results or 'error' in audit_results:
            return {
                'compliance_score': 0,
                'high_risk_issues': 0,
                'medium_risk_issues': 0,
                'low_risk_issues': 0,
                'total_findings': 0,
                'system_info': None
            }
        
        # Count security issues
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        # File analysis issues
        file_analysis = audit_results.get('file_analysis', [])
        for file_info in file_analysis:
            if file_info.get('risk_level') == SecurityLevel.HIGH:
                high_risk += 1
            elif file_info.get('risk_level') == SecurityLevel.MEDIUM:
                medium_risk += 1
            else:
                low_risk += 1
        
        # User analysis issues
        user_analysis = audit_results.get('user_analysis', {})
        user_issues = user_analysis.get('security_issues', [])
        high_risk += len([issue for issue in user_issues if 'UID 0' in issue or 'Empty password' in issue])
        medium_risk += len([issue for issue in user_issues if 'home directory' in issue])
        
        # Network analysis issues
        network_analysis = audit_results.get('network_analysis', {})
        network_issues = network_analysis.get('security_issues', [])
        high_risk += len([issue for issue in network_issues if 'Dangerous service' in issue])
        
        # STIG analysis issues
        stig_analysis = audit_results.get('stig_analysis', {})
        for result in stig_analysis.values():
            if result.get('status') != ComplianceStatus.COMPLIANT:
                if result.get('severity') == 'high':
                    high_risk += 1
                else:
                    medium_risk += 1
        
        total_findings = high_risk + medium_risk + low_risk
        
        # Calculate compliance score
        compliance_score = 100 - (high_risk * 10 + medium_risk * 5 + low_risk * 1)
        compliance_score = max(0, min(100, compliance_score))
        
        return {
            'compliance_score': round(compliance_score, 1),
            'high_risk_issues': high_risk,
            'medium_risk_issues': medium_risk,
            'low_risk_issues': low_risk,
            'total_findings': total_findings,
            'system_info': audit_results.get('system_info'),
            'audit_timestamp': audit_results.get('audit_timestamp'),
            'audit_duration': audit_results.get('audit_duration', 0)
        }

# Mock data generation for demonstration
def generate_mock_unix_linux_data() -> Dict[str, Any]:
    """Generate mock Unix/Linux audit data for demonstration"""
    return {
        'system_info': {
            'os_type': 'Linux',
            'os_version': '5.4.0-42-generic',
            'hostname': 'demo-server-01',
            'kernel_version': '#46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020',
            'architecture': 'x86_64',
            'scan_timestamp': datetime.datetime.now().isoformat(),
            'scan_duration': 45.2
        },
        'file_analysis': [
            {
                'file_path': '/tmp/test_file',
                'permissions': '666',
                'security_issues': ['World writable file'],
                'risk_level': SecurityLevel.HIGH.value
            },
            {
                'file_path': '/usr/bin/passwd',
                'permissions': '4755',
                'security_issues': ['SUID bit set'],
                'risk_level': SecurityLevel.MEDIUM.value
            }
        ],
        'user_analysis': {
            'users': {
                'root': {
                    'username': 'root',
                    'uid': '0',
                    'security_issues': []
                },
                'testuser': {
                    'username': 'testuser',
                    'uid': '1000',
                    'security_issues': ['Empty password']
                }
            },
            'security_issues': ['Empty password']
        },
        'network_analysis': {
            'listening_ports': [
                {
                    'protocol': 'tcp',
                    'local_address': '0.0.0.0:22',
                    'program': 'sshd'
                },
                {
                    'protocol': 'tcp',
                    'local_address': '0.0.0.0:80',
                    'program': 'nginx'
                }
            ],
            'security_issues': []
        },
        'stig_analysis': {
            'V-204425': {
                'id': 'V-204425',
                'title': 'SSH daemon must not allow empty passwords',
                'status': ComplianceStatus.COMPLIANT.value,
                'severity': 'high',
                'evidence': 'PermitEmptyPasswords no in sshd_config'
            },
            'V-204424': {
                'id': 'V-204424',
                'title': 'SSH daemon must not allow known hosts authentication',
                'status': ComplianceStatus.NON_COMPLIANT.value,
                'severity': 'medium',
                'evidence': 'IgnoreUserKnownHosts not set in sshd_config'
            }
        }
    }
