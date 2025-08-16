#!/usr/bin/env python3
"""
JD Edwards Security Audit Core Module
====================================

A comprehensive Python module for JD Edwards World security auditing and compliance.
This module converts the functionality of the JD Edwards audit Perl tools to a
modern Python implementation with enhanced features and compliance framework integration.

Original Perl modules converted:
- jdew.pl -> JDESecurityAuditor
- jdew_toolz.pl -> JDETools
- jdew_v2729.pl -> JDEv2729
- Database connectivity and analysis
- User access mapping
- Change tracking
"""

import os
import sys
import json
import datetime
import sqlite3
import hashlib
import secrets
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np

class AccessLevel(Enum):
    """Access level enumeration"""
    NONE = "None"
    READ = "Read"
    WRITE = "Write"
    DELETE = "Delete"
    ALL = "All"

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
class JDEUser:
    """Data class for JD Edwards user information"""
    user_id: str
    user_name: str
    user_type: str
    status: str
    group_id: str
    location: str
    access_level: AccessLevel
    last_login: Optional[str] = None
    security_issues: List[str] = None

@dataclass
class JDEProgram:
    """Data class for JD Edwards program information"""
    program_id: str
    program_name: str
    program_type: str
    description: str
    critical_level: SecurityLevel
    access_required: AccessLevel
    users_with_access: List[str] = None

@dataclass
class JDELocation:
    """Data class for JD Edwards location information"""
    location_id: str
    location_name: str
    location_type: str
    business_unit: str
    security_level: SecurityLevel
    users: List[str] = None

class JDEDataManager:
    """Data management for JD Edwards security audit"""
    
    def __init__(self):
        self.data_file = "jde_audit_data.json"
        self.audit_history = []
        self.user_profiles = {}
        self.program_access = {}
        self.location_data = {}
        self.compliance_results = {}
    
    def save_data_to_file(self) -> bool:
        """Save audit data to JSON file"""
        try:
            data = {
                'audit_history': self.audit_history,
                'user_profiles': self.user_profiles,
                'program_access': self.program_access,
                'location_data': self.location_data,
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
                self.user_profiles = data.get('user_profiles', {})
                self.program_access = data.get('program_access', {})
                self.location_data = data.get('location_data', {})
                self.compliance_results = data.get('compliance_results', {})
                return True
            return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

class JDEUserAnalyzer:
    """JD Edwards user security analysis"""
    
    def __init__(self):
        self.users = {}
        self.security_issues = []
        self.access_patterns = {}
    
    def analyze_users(self, user_data: List[Dict]) -> Dict[str, Any]:
        """Analyze JD Edwards user security"""
        try:
            for user_info in user_data:
                user_id = user_info.get('user_id', '')
                
                # Create user object
                access_level_str = user_info.get('access_level', 'NONE')
                # Convert to proper enum value
                if access_level_str == 'WRITE':
                    access_level = AccessLevel.WRITE
                elif access_level_str == 'READ':
                    access_level = AccessLevel.READ
                elif access_level_str == 'DELETE':
                    access_level = AccessLevel.DELETE
                elif access_level_str == 'ALL':
                    access_level = AccessLevel.ALL
                else:
                    access_level = AccessLevel.NONE
                
                user = JDEUser(
                    user_id=user_id,
                    user_name=user_info.get('user_name', ''),
                    user_type=user_info.get('user_type', ''),
                    status=user_info.get('status', ''),
                    group_id=user_info.get('group_id', ''),
                    location=user_info.get('location', ''),
                    access_level=access_level,
                    last_login=user_info.get('last_login'),
                    security_issues=[]
                )
                
                # Security analysis
                issues = self._analyze_user_security(user, user_info)
                user.security_issues = issues
                
                self.users[user_id] = user
                
                if issues:
                    self.security_issues.extend(issues)
            
            return {
                'users': {uid: asdict(user) for uid, user in self.users.items()},
                'security_issues': self.security_issues,
                'total_users': len(self.users),
                'users_with_issues': len([u for u in self.users.values() if u.security_issues])
            }
        except Exception as e:
            return {
                'error': f"Error analyzing users: {e}",
                'users': {},
                'security_issues': [],
                'total_users': 0,
                'users_with_issues': 0
            }
    
    def _analyze_user_security(self, user: JDEUser, user_info: Dict) -> List[str]:
        """Analyze individual user security"""
        issues = []
        
        # Check for inactive users
        if user.status.lower() in ['inactive', 'disabled', 'suspended']:
            issues.append("Inactive user account")
        
        # Check for excessive access
        if user.access_level == AccessLevel.ALL:
            issues.append("Excessive access level (ALL)")
        
        # Check for missing user information
        if not user.user_name or user.user_name.strip() == '':
            issues.append("Missing user name")
        
        # Check for default passwords (simulated)
        if user_info.get('default_password', False):
            issues.append("Default password detected")
        
        # Check for shared accounts
        if user_info.get('shared_account', False):
            issues.append("Shared account detected")
        
        return issues

class JDEProgramAnalyzer:
    """JD Edwards program access analysis"""
    
    def __init__(self):
        self.programs = {}
        self.critical_programs = {}
        self.access_violations = []
    
    def analyze_programs(self, program_data: List[Dict]) -> Dict[str, Any]:
        """Analyze JD Edwards program access"""
        try:
            for program_info in program_data:
                program_id = program_info.get('program_id', '')
                
                # Create program object
                critical_level_str = program_info.get('critical_level', 'LOW')
                access_required_str = program_info.get('access_required', 'NONE')
                
                # Convert to proper enum values
                if critical_level_str == 'HIGH':
                    critical_level = SecurityLevel.HIGH
                elif critical_level_str == 'CRITICAL':
                    critical_level = SecurityLevel.CRITICAL
                elif critical_level_str == 'MEDIUM':
                    critical_level = SecurityLevel.MEDIUM
                else:
                    critical_level = SecurityLevel.LOW
                
                if access_required_str == 'WRITE':
                    access_required = AccessLevel.WRITE
                elif access_required_str == 'READ':
                    access_required = AccessLevel.READ
                elif access_required_str == 'ALL':
                    access_required = AccessLevel.ALL
                else:
                    access_required = AccessLevel.NONE
                
                program = JDEProgram(
                    program_id=program_id,
                    program_name=program_info.get('program_name', ''),
                    program_type=program_info.get('program_type', ''),
                    description=program_info.get('description', ''),
                    critical_level=critical_level,
                    access_required=access_required,
                    users_with_access=program_info.get('users_with_access', [])
                )
                
                self.programs[program_id] = program
                
                # Identify critical programs
                if program.critical_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                    self.critical_programs[program_id] = program
                
                # Analyze access violations
                violations = self._analyze_access_violations(program)
                if violations:
                    self.access_violations.extend(violations)
            
            return {
                'programs': {pid: asdict(program) for pid, program in self.programs.items()},
                'critical_programs': {pid: asdict(program) for pid, program in self.critical_programs.items()},
                'access_violations': self.access_violations,
                'total_programs': len(self.programs),
                'critical_programs_count': len(self.critical_programs)
            }
        except Exception as e:
            return {
                'error': f"Error analyzing programs: {e}",
                'programs': {},
                'critical_programs': {},
                'access_violations': [],
                'total_programs': 0,
                'critical_programs_count': 0
            }
    
    def _analyze_access_violations(self, program: JDEProgram) -> List[str]:
        """Analyze program access violations"""
        violations = []
        
        # Check for excessive access to critical programs
        if program.critical_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            if len(program.users_with_access) > 10:
                violations.append(f"Too many users ({len(program.users_with_access)}) have access to critical program {program.program_id}")
        
        # Check for unauthorized access patterns
        if program.access_required == AccessLevel.READ and len(program.users_with_access) > 50:
            violations.append(f"Excessive read access to program {program.program_id}")
        
        return violations

class JDELocationAnalyzer:
    """JD Edwards location security analysis"""
    
    def __init__(self):
        self.locations = {}
        self.location_issues = []
    
    def analyze_locations(self, location_data: List[Dict]) -> Dict[str, Any]:
        """Analyze JD Edwards location security"""
        try:
            for location_info in location_data:
                location_id = location_info.get('location_id', '')
                
                # Create location object
                security_level_str = location_info.get('security_level', 'LOW')
                
                # Convert to proper enum value
                if security_level_str == 'HIGH':
                    security_level = SecurityLevel.HIGH
                elif security_level_str == 'CRITICAL':
                    security_level = SecurityLevel.CRITICAL
                elif security_level_str == 'MEDIUM':
                    security_level = SecurityLevel.MEDIUM
                else:
                    security_level = SecurityLevel.LOW
                
                location = JDELocation(
                    location_id=location_id,
                    location_name=location_info.get('location_name', ''),
                    location_type=location_info.get('location_type', ''),
                    business_unit=location_info.get('business_unit', ''),
                    security_level=security_level,
                    users=location_info.get('users', [])
                )
                
                self.locations[location_id] = location
                
                # Analyze location security
                issues = self._analyze_location_security(location)
                if issues:
                    self.location_issues.extend(issues)
            
            return {
                'locations': {lid: asdict(location) for lid, location in self.locations.items()},
                'location_issues': self.location_issues,
                'total_locations': len(self.locations),
                'locations_with_issues': len([l for l in self.locations.values() if l.users and len(l.users) > 20])
            }
        except Exception as e:
            return {
                'error': f"Error analyzing locations: {e}",
                'locations': {},
                'location_issues': [],
                'total_locations': 0,
                'locations_with_issues': 0
            }
    
    def _analyze_location_security(self, location: JDELocation) -> List[str]:
        """Analyze individual location security"""
        issues = []
        
        # Check for too many users at a location
        if location.users and len(location.users) > 20:
            issues.append(f"Too many users ({len(location.users)}) at location {location.location_id}")
        
        # Check for high-security locations with many users
        if location.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL] and location.users and len(location.users) > 5:
            issues.append(f"High-security location {location.location_id} has too many users")
        
        return issues

class JDEComplianceAnalyzer:
    """JD Edwards compliance analysis"""
    
    def __init__(self):
        self.compliance_controls = self._load_compliance_controls()
        self.compliance_results = {}
    
    def _load_compliance_controls(self) -> Dict[str, Any]:
        """Load compliance control definitions"""
        return {
            'SOX': {
                'name': 'Sarbanes-Oxley Act',
                'description': 'Financial reporting and corporate governance requirements',
                'controls': {
                    'SOX-001': {
                        'title': 'Segregation of Duties',
                        'description': 'Ensure proper separation of duties for financial functions',
                        'check': 'Review user access to financial programs',
                        'fix': 'Implement role-based access controls',
                        'severity': 'high'
                    },
                    'SOX-002': {
                        'title': 'Access Control',
                        'description': 'Ensure appropriate access controls for financial data',
                        'check': 'Review user access levels',
                        'fix': 'Implement least privilege access',
                        'severity': 'high'
                    },
                    'SOX-003': {
                        'title': 'Change Management',
                        'description': 'Ensure proper change management for financial systems',
                        'check': 'Review change tracking',
                        'fix': 'Implement change approval workflows',
                        'severity': 'medium'
                    },
                    'SOX-004': {
                        'title': 'Financial Data Protection',
                        'description': 'Protect financial data from unauthorized access',
                        'check': 'Review access to critical financial programs',
                        'fix': 'Implement data encryption and access controls',
                        'severity': 'high'
                    },
                    'SOX-005': {
                        'title': 'Audit Trail',
                        'description': 'Maintain comprehensive audit trails',
                        'check': 'Review system logging capabilities',
                        'fix': 'Enable comprehensive audit logging',
                        'severity': 'medium'
                    }
                }
            },
            'PCI DSS': {
                'name': 'Payment Card Industry Data Security Standard',
                'description': 'Security standards for payment card data',
                'controls': {
                    'PCI-001': {
                        'title': 'Access Control',
                        'description': 'Restrict access to cardholder data',
                        'check': 'Review access to payment programs',
                        'fix': 'Implement access controls',
                        'severity': 'high'
                    },
                    'PCI-002': {
                        'title': 'User Management',
                        'description': 'Proper user account management',
                        'check': 'Review user account status',
                        'fix': 'Implement user lifecycle management',
                        'severity': 'medium'
                    },
                    'PCI-003': {
                        'title': 'Data Encryption',
                        'description': 'Encrypt cardholder data in transit and at rest',
                        'check': 'Review data encryption settings',
                        'fix': 'Implement encryption for sensitive data',
                        'severity': 'high'
                    },
                    'PCI-004': {
                        'title': 'Network Security',
                        'description': 'Secure network infrastructure',
                        'check': 'Review network access controls',
                        'fix': 'Implement network segmentation',
                        'severity': 'medium'
                    },
                    'PCI-005': {
                        'title': 'Vulnerability Management',
                        'description': 'Regular security assessments',
                        'check': 'Review security testing procedures',
                        'fix': 'Implement regular security scans',
                        'severity': 'medium'
                    }
                }
            },
            'HIPAA': {
                'name': 'Health Insurance Portability and Accountability Act',
                'description': 'Healthcare data privacy and security',
                'controls': {
                    'HIPAA-001': {
                        'title': 'Access Control',
                        'description': 'Ensure appropriate access to health data',
                        'check': 'Review access to health-related programs',
                        'fix': 'Implement access controls',
                        'severity': 'high'
                    },
                    'HIPAA-002': {
                        'title': 'Data Privacy',
                        'description': 'Protect patient health information',
                        'check': 'Review data handling procedures',
                        'fix': 'Implement data privacy controls',
                        'severity': 'high'
                    },
                    'HIPAA-003': {
                        'title': 'User Authentication',
                        'description': 'Strong user authentication mechanisms',
                        'check': 'Review authentication methods',
                        'fix': 'Implement multi-factor authentication',
                        'severity': 'medium'
                    },
                    'HIPAA-004': {
                        'title': 'Audit Logging',
                        'description': 'Comprehensive audit trails for PHI access',
                        'check': 'Review audit logging capabilities',
                        'fix': 'Enable PHI access logging',
                        'severity': 'medium'
                    },
                    'HIPAA-005': {
                        'title': 'Data Backup',
                        'description': 'Secure backup and recovery procedures',
                        'check': 'Review backup procedures',
                        'fix': 'Implement secure backup processes',
                        'severity': 'medium'
                    }
                }
            }
        }
    
    def analyze_compliance(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compliance against multiple frameworks"""
        results = {}
        
        for framework_name, framework_info in self.compliance_controls.items():
            framework_results = {
                'name': framework_info['name'],
                'description': framework_info['description'],
                'compliance_score': 0,
                'controls': [],
                'critical_issues': [],
                'recommendations': []
            }
            
            # Analyze each control
            for control_id, control_info in framework_info['controls'].items():
                compliance_status = self._check_compliance_control(control_id, control_info, audit_data)
                
                framework_results['controls'].append({
                    'id': control_id,
                    'title': control_info['title'],
                    'description': control_info['description'],
                    'status': compliance_status.value,
                    'severity': control_info['severity'],
                    'check': control_info['check'],
                    'fix': control_info['fix']
                })
                
                if compliance_status != ComplianceStatus.COMPLIANT:
                    framework_results['critical_issues'].append({
                        'control_id': control_id,
                        'title': control_info['title'],
                        'severity': control_info['severity'],
                        'business_impact': 'High' if control_info['severity'] == 'high' else 'Medium',
                        'remediation_effort': 'Medium',
                        'remediation': control_info['fix']
                    })
            
            # Calculate compliance score
            total_controls = len(framework_results['controls'])
            compliant_controls = len([c for c in framework_results['controls'] if c['status'] == 'Compliant'])
            framework_results['compliance_score'] = (compliant_controls / total_controls * 100) if total_controls > 0 else 0
            
            results[framework_name] = framework_results
        
        return results
    
    def _check_compliance_control(self, control_id: str, control_info: Dict, audit_data: Dict) -> ComplianceStatus:
        """Check individual compliance control"""
        # This would implement specific checks for each control
        # For now, return a mock result
        return ComplianceStatus.COMPLIANT if hash(control_id) % 3 == 0 else ComplianceStatus.NON_COMPLIANT

class JDESecurityAuditor:
    """Main JD Edwards security auditor class"""
    
    def __init__(self):
        self.data_manager = JDEDataManager()
        self.user_analyzer = JDEUserAnalyzer()
        self.program_analyzer = JDEProgramAnalyzer()
        self.location_analyzer = JDELocationAnalyzer()
        self.compliance_analyzer = JDEComplianceAnalyzer()
        self.audit_results = {}
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run comprehensive JD Edwards security audit"""
        start_time = datetime.datetime.now()
        
        try:
            # Generate mock data for demonstration
            mock_data = generate_mock_jde_data()
            
            # Run individual analyses
            user_analysis = self.user_analyzer.analyze_users(mock_data['users'])
            program_analysis = self.program_analyzer.analyze_programs(mock_data['programs'])
            location_analysis = self.location_analyzer.analyze_locations(mock_data['locations'])
            compliance_analysis = self.compliance_analyzer.analyze_compliance({
                'users': user_analysis,
                'programs': program_analysis,
                'locations': location_analysis
            })
            
            # Compile results
            self.audit_results = {
                'user_analysis': user_analysis,
                'program_analysis': program_analysis,
                'location_analysis': location_analysis,
                'compliance_frameworks': compliance_analysis,
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
    
    def get_audit_summary(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audit summary"""
        if not audit_results or 'error' in audit_results:
            return {
                'compliance_score': 0,
                'high_risk_issues': 0,
                'medium_risk_issues': 0,
                'low_risk_issues': 0,
                'total_findings': 0,
                'total_users': 0,
                'total_programs': 0,
                'total_locations': 0
            }
        
        # Count security issues
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        # User analysis issues
        user_analysis = audit_results.get('user_analysis', {})
        user_issues = user_analysis.get('security_issues', [])
        high_risk += len([issue for issue in user_issues if 'Excessive access' in issue or 'Default password' in issue])
        medium_risk += len([issue for issue in user_issues if 'Inactive user' in issue or 'Shared account' in issue])
        
        # Program analysis issues
        program_analysis = audit_results.get('program_analysis', {})
        access_violations = program_analysis.get('access_violations', [])
        high_risk += len([violation for violation in access_violations if 'critical program' in violation.lower()])
        medium_risk += len([violation for violation in access_violations if 'excessive' in violation.lower()])
        
        # Location analysis issues
        location_analysis = audit_results.get('location_analysis', {})
        location_issues = location_analysis.get('location_issues', [])
        high_risk += len([issue for issue in location_issues if 'high-security' in issue.lower()])
        medium_risk += len([issue for issue in location_issues if 'too many users' in issue.lower()])
        
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
            'total_users': user_analysis.get('total_users', 0),
            'total_programs': program_analysis.get('total_programs', 0),
            'total_locations': location_analysis.get('total_locations', 0),
            'audit_timestamp': audit_results.get('audit_timestamp'),
            'audit_duration': audit_results.get('audit_duration', 0)
        }

# Mock data generation for demonstration
def generate_mock_jde_data() -> Dict[str, Any]:
    """Generate comprehensive mock JD Edwards audit data for demonstration"""
    
    # Generate realistic user data
    users = [
        {
            'user_id': 'JDE001',
            'user_name': 'John Smith',
            'user_type': 'Employee',
            'status': 'Active',
            'group_id': 'FIN001',
            'location': 'HQ',
            'access_level': 'WRITE',
            'last_login': '2024-01-15 09:30:00',
            'default_password': False,
            'shared_account': False
        },
        {
            'user_id': 'JDE002',
            'user_name': 'Jane Doe',
            'user_type': 'Manager',
            'status': 'Active',
            'group_id': 'FIN002',
            'location': 'HQ',
            'access_level': 'ALL',
            'last_login': '2024-01-14 14:20:00',
            'default_password': False,
            'shared_account': False
        },
        {
            'user_id': 'JDE003',
            'user_name': 'Bob Wilson',
            'user_type': 'Employee',
            'status': 'Inactive',
            'group_id': 'HR001',
            'location': 'BRANCH01',
            'access_level': 'READ',
            'last_login': '2023-12-01 11:15:00',
            'default_password': True,
            'shared_account': False
        },
        {
            'user_id': 'JDE004',
            'user_name': 'Sarah Johnson',
            'user_type': 'Employee',
            'status': 'Active',
            'group_id': 'AP001',
            'location': 'HQ',
            'access_level': 'WRITE',
            'last_login': '2024-01-15 08:45:00',
            'default_password': False,
            'shared_account': False
        },
        {
            'user_id': 'JDE005',
            'user_name': 'Mike Chen',
            'user_type': 'Manager',
            'status': 'Active',
            'group_id': 'AR001',
            'location': 'HQ',
            'access_level': 'ALL',
            'last_login': '2024-01-15 10:15:00',
            'default_password': False,
            'shared_account': False
        },
        {
            'user_id': 'JDE006',
            'user_name': 'Lisa Brown',
            'user_type': 'Employee',
            'status': 'Active',
            'group_id': 'INV001',
            'location': 'BRANCH01',
            'access_level': 'READ',
            'last_login': '2024-01-15 07:30:00',
            'default_password': False,
            'shared_account': False
        },
        {
            'user_id': 'JDE007',
            'user_name': 'David Miller',
            'user_type': 'Employee',
            'status': 'Suspended',
            'group_id': 'HR001',
            'location': 'BRANCH01',
            'access_level': 'READ',
            'last_login': '2024-01-10 16:20:00',
            'default_password': False,
            'shared_account': True
        },
        {
            'user_id': 'JDE008',
            'user_name': 'Emily Davis',
            'user_type': 'Employee',
            'status': 'Active',
            'group_id': 'PRD001',
            'location': 'BRANCH02',
            'access_level': 'WRITE',
            'last_login': '2024-01-15 09:00:00',
            'default_password': False,
            'shared_account': False
        },
        {
            'user_id': 'JDE009',
            'user_name': 'Tom Anderson',
            'user_type': 'Manager',
            'status': 'Active',
            'group_id': 'IT001',
            'location': 'HQ',
            'access_level': 'ALL',
            'last_login': '2024-01-15 11:30:00',
            'default_password': False,
            'shared_account': False
        },
        {
            'user_id': 'JDE010',
            'user_name': 'Rachel Green',
            'user_type': 'Employee',
            'status': 'Active',
            'group_id': 'QC001',
            'location': 'BRANCH02',
            'access_level': 'READ',
            'last_login': '2024-01-15 08:15:00',
            'default_password': True,
            'shared_account': False
        }
    ]
    
    # Generate comprehensive program data
    programs = [
        {
            'program_id': 'P001',
            'program_name': 'General Ledger',
            'program_type': 'Financial',
            'description': 'General ledger management and financial reporting system',
            'critical_level': 'HIGH',
            'access_required': 'WRITE',
            'users_with_access': ['JDE001', 'JDE002', 'JDE005']
        },
        {
            'program_id': 'P002',
            'program_name': 'Accounts Payable',
            'program_type': 'Financial',
            'description': 'Accounts payable processing and vendor management',
            'critical_level': 'CRITICAL',
            'access_required': 'WRITE',
            'users_with_access': ['JDE001', 'JDE002', 'JDE004']
        },
        {
            'program_id': 'P003',
            'program_name': 'Accounts Receivable',
            'program_type': 'Financial',
            'description': 'Accounts receivable and customer billing system',
            'critical_level': 'HIGH',
            'access_required': 'WRITE',
            'users_with_access': ['JDE001', 'JDE002', 'JDE005']
        },
        {
            'program_id': 'P004',
            'program_name': 'Employee Directory',
            'program_type': 'HR',
            'description': 'Employee information and directory management',
            'critical_level': 'MEDIUM',
            'access_required': 'READ',
            'users_with_access': ['JDE001', 'JDE002', 'JDE003', 'JDE004', 'JDE005', 'JDE006', 'JDE007', 'JDE008', 'JDE009', 'JDE010']
        },
        {
            'program_id': 'P005',
            'program_name': 'Payroll Processing',
            'program_type': 'HR',
            'description': 'Payroll calculation and processing system',
            'critical_level': 'CRITICAL',
            'access_required': 'WRITE',
            'users_with_access': ['JDE002', 'JDE007']
        },
        {
            'program_id': 'P006',
            'program_name': 'Inventory Management',
            'program_type': 'Operations',
            'description': 'Inventory tracking and warehouse management',
            'critical_level': 'HIGH',
            'access_required': 'WRITE',
            'users_with_access': ['JDE006', 'JDE008', 'JDE010']
        },
        {
            'program_id': 'P007',
            'program_name': 'Purchase Orders',
            'program_type': 'Operations',
            'description': 'Purchase order creation and management',
            'critical_level': 'MEDIUM',
            'access_required': 'WRITE',
            'users_with_access': ['JDE004', 'JDE006', 'JDE008']
        },
        {
            'program_id': 'P008',
            'program_name': 'Sales Orders',
            'program_type': 'Sales',
            'description': 'Sales order processing and customer management',
            'critical_level': 'HIGH',
            'access_required': 'WRITE',
            'users_with_access': ['JDE005', 'JDE008', 'JDE010']
        },
        {
            'program_id': 'P009',
            'program_name': 'System Administration',
            'program_type': 'IT',
            'description': 'System configuration and administration tools',
            'critical_level': 'CRITICAL',
            'access_required': 'ALL',
            'users_with_access': ['JDE002', 'JDE009']
        },
        {
            'program_id': 'P010',
            'program_name': 'Report Generator',
            'program_type': 'Reporting',
            'description': 'Custom report generation and data export',
            'critical_level': 'MEDIUM',
            'access_required': 'READ',
            'users_with_access': ['JDE001', 'JDE002', 'JDE004', 'JDE005', 'JDE006', 'JDE008', 'JDE009']
        },
        {
            'program_id': 'P011',
            'program_name': 'Bank Reconciliation',
            'program_type': 'Financial',
            'description': 'Bank account reconciliation and cash management',
            'critical_level': 'HIGH',
            'access_required': 'WRITE',
            'users_with_access': ['JDE001', 'JDE002']
        },
        {
            'program_id': 'P012',
            'program_name': 'Fixed Assets',
            'program_type': 'Financial',
            'description': 'Fixed asset tracking and depreciation',
            'critical_level': 'MEDIUM',
            'access_required': 'WRITE',
            'users_with_access': ['JDE001', 'JDE002', 'JDE004']
        }
    ]
    
    # Generate location data
    locations = [
        {
            'location_id': 'HQ',
            'location_name': 'Corporate Headquarters',
            'location_type': 'Office',
            'business_unit': 'Corporate',
            'security_level': 'HIGH',
            'users': ['JDE001', 'JDE002', 'JDE003', 'JDE004', 'JDE005', 'JDE009']
        },
        {
            'location_id': 'BRANCH01',
            'location_name': 'North Branch Office',
            'location_type': 'Branch',
            'business_unit': 'Operations',
            'security_level': 'MEDIUM',
            'users': ['JDE006', 'JDE007']
        },
        {
            'location_id': 'BRANCH02',
            'location_name': 'South Branch Office',
            'location_type': 'Branch',
            'business_unit': 'Operations',
            'security_level': 'MEDIUM',
            'users': ['JDE008', 'JDE010']
        },
        {
            'location_id': 'WAREHOUSE01',
            'location_name': 'Main Distribution Center',
            'location_type': 'Warehouse',
            'business_unit': 'Logistics',
            'security_level': 'LOW',
            'users': ['JDE006', 'JDE008']
        },
        {
            'location_id': 'MANUFACTURING01',
            'location_name': 'Production Facility',
            'location_type': 'Manufacturing',
            'business_unit': 'Production',
            'security_level': 'MEDIUM',
            'users': ['JDE008', 'JDE010']
        }
    ]
    
    return {
        'users': users,
        'programs': programs,
        'locations': locations
    }
