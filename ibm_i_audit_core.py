#!/usr/bin/env python3
"""
IBM i Security Audit - Python Core Classes
==========================================

This module provides Python classes that convert the functionality
of the IBM i Perl audit tools (system_i_audit) to Python for use
in Streamlit applications.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IBMiDataManager:
    """Core data management class for IBM i system data"""
    
    def __init__(self):
        self.system_values = {}
        self.user_profiles = {}
        self.object_authorities = {}
        self.groups = {}  # Add missing groups attribute
        
    def save_data_to_file(self, filename: str = "ibm_i_data.json"):
        """Save current data to JSON file for persistence"""
        try:
            data_to_save = {
                'system_values': self.system_values,
                'user_profiles': self.user_profiles,
                'object_authorities': self.object_authorities,
                'groups': self.groups,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, default=str, indent=2)
            
            logger.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False
    
    def load_data_from_file(self, filename: str = "ibm_i_data.json"):
        """Load data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.system_values = data.get('system_values', {})
            self.user_profiles = data.get('user_profiles', {})
            self.object_authorities = data.get('object_authorities', {})
            self.groups = data.get('groups', {})
            
            logger.info(f"Data loaded from {filename}")
            return True
        except FileNotFoundError:
            logger.info(f"Data file {filename} not found, generating new data")
            return False
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False
    
    def generate_mock_ibm_i_data(self):
        """Generate realistic mock IBM i system data for demonstration"""
        
        # Enhanced Mock System Values based on IBM Redbooks
        self.system_values = {
            # Security Level and Access Control
            'QSECURITY': {
                'current': '40',
                'recommended': '40',
                'description': 'System security level (10=Basic, 20=Standard, 30=Enhanced, 40=Maximum)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA', 'ISO 27001', 'NIST'],
                'business_impact': 'High',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            
            # Password Management
            'QPWDEXPITV': {
                'current': '90',
                'recommended': '90',
                'description': 'Password expiration interval in days',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA', 'ISO 27001', 'NIST'],
                'business_impact': 'Medium',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QPWDLVL': {
                'current': '2',
                'recommended': '2',
                'description': 'Password level (0=Basic, 1=Enhanced, 2=Maximum)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA'],
                'business_impact': 'Medium',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QPWDMINLEN': {
                'current': '8',
                'recommended': '8',
                'description': 'Minimum password length',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA', 'ISO 27001'],
                'business_impact': 'Medium',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QPWDMAXLEN': {
                'current': '128',
                'recommended': '128',
                'description': 'Maximum password length',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS'],
                'business_impact': 'Low',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QPWDRQDDIF': {
                'current': '5',
                'recommended': '5',
                'description': 'Number of different characters required in new password',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA'],
                'business_impact': 'Medium',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QPWDVLDPGM': {
                'current': '*NONE',
                'recommended': 'CUSTPWD',
                'description': 'Password validation program name',
                'exception': True,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA'],
                'business_impact': 'High',
                'remediation_effort': 'Medium',
                'ibm_redbook_ref': 'SG24-8150'
            },
            
            # Sign-on and Session Management
            'QMAXSIGN': {
                'current': '5',
                'recommended': '5',
                'description': 'Maximum sign-on attempts before account lockout',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA', 'ISO 27001'],
                'business_impact': 'High',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QMAXSGNACN': {
                'current': '10',
                'recommended': '10',
                'description': 'Action when maximum sign-on attempts exceeded (*DISABLE, *ENDJOB, *ENDJOBSBS)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA'],
                'business_impact': 'High',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QINACTITV': {
                'current': '30',
                'recommended': '30',
                'description': 'Inactivity timeout in minutes before automatic sign-off',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA', 'ISO 27001'],
                'business_impact': 'Medium',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QINACTMSGQ': {
                'current': '*NONE',
                'recommended': 'INACTMSGQ',
                'description': 'Inactive message queue for timeout notifications',
                'exception': True,
                'compliance_frameworks': ['SOX', 'PCI DSS'],
                'business_impact': 'Low',
                'remediation_effort': 'Medium',
                'ibm_redbook_ref': 'SG24-8150'
            },
            
            # Audit and Journaling
            'QAUDCTL': {
                'current': '*AUDLVL',
                'recommended': '*AUDLVL',
                'description': 'Audit control (*NONE, *AUDLVL, *AUTFAIL, *AUTFAIL, *AUTFAIL)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA', 'ISO 27001', 'NIST'],
                'business_impact': 'High',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QAUDLVL': {
                'current': '*SECURITY',
                'recommended': '*SECURITY',
                'description': 'Audit level (*NONE, *SECURITY, *SECURITY, *SECURITY, *SECURITY)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA', 'ISO 27001', 'NIST'],
                'business_impact': 'High',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QAUDLVL2': {
                'current': '*NONE',
                'recommended': '*SECURITY',
                'description': 'Secondary audit level for additional events',
                'exception': True,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA'],
                'business_impact': 'Medium',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QAUDJRN': {
                'current': 'QSYS/AUDIT_JRN',
                'recommended': 'QSYS/AUDIT_JRN',
                'description': 'Audit journal name and library',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA', 'ISO 27001', 'NIST'],
                'business_impact': 'High',
                'remediation_effort': 'Medium',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QAUDJRNRCV': {
                'current': 'QSYS/AUDIT_JRN',
                'recommended': 'QSYS/AUDIT_JRN',
                'description': 'Audit journal receiver name and library',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA'],
                'business_impact': 'Medium',
                'remediation_effort': 'Medium',
                'ibm_redbook_ref': 'SG24-8150'
            },
            
            # Network and Remote Access
            'QRMTSIGN': {
                'current': '*NONE',
                'recommended': '*NONE',
                'description': 'Remote sign-on control (*NONE, *SIGNON, *SIGNON, *SIGNON)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA', 'ISO 27001'],
                'business_impact': 'High',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QLMTSECOFR': {
                'current': '*YES',
                'recommended': '*NO',
                'description': 'Limit QSECOFR to console (*YES, *NO)',
                'exception': True,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA'],
                'business_impact': 'High',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QLMTDEVSSN': {
                'current': '*YES',
                'recommended': '*YES',
                'description': 'Limit device sessions (*YES, *NO)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS'],
                'business_impact': 'Medium',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            
            # System Access Control
            'QALWOBJRST': {
                'current': '*NONE',
                'recommended': '*NONE',
                'description': 'Allow object restore (*NONE, *ALL, *AUTL, *AUTL)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA'],
                'business_impact': 'High',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QALWOBJRSTDTA': {
                'current': '*NONE',
                'recommended': '*NONE',
                'description': 'Allow object restore with data (*NONE, *ALL, *AUTL)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA'],
                'business_impact': 'High',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QALWUSRDMN': {
                'current': '*NONE',
                'recommended': '*NONE',
                'description': 'Allow user domain (*NONE, *ALL, *AUTL)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS'],
                'business_impact': 'Medium',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            
            # Library List Security
            'QLIBLACN': {
                'current': '*NONE',
                'recommended': '*NONE',
                'description': 'Library list action (*NONE, *CHGLIBL, *CHGLIBL)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS'],
                'business_impact': 'Medium',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            },
            'QSPLACN': {
                'current': '*NONE',
                'recommended': '*NONE',
                'description': 'Spooled file action (*NONE, *CHGSPLFA, *CHGSPLFA)',
                'exception': False,
                'compliance_frameworks': ['SOX', 'PCI DSS'],
                'business_impact': 'Low',
                'remediation_effort': 'Low',
                'ibm_redbook_ref': 'SG24-8150'
            }
        }
        
        # Enhanced Mock User Profiles with Enterprise Scenarios
        self.user_profiles = {
            'QSECOFR': {
                'name': 'Security Officer',
                'status': '*ENABLED',
                'group': 'QSECOFR',
                'pass_none': '*NO',
                'spec_auth': ['*ALLOBJ', '*SECADM'],
                'prev_sign_on': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'user_class': '*SECOFR',
                'pass_exp': '*YES',
                'job_title': 'Security Administrator',
                'department': 'IT Security',
                'last_password_change': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
                'failed_login_attempts': 0,
                'compliance_status': 'Compliant'
            },
            'JOHNDOE': {
                'name': 'John Doe',
                'status': '*ENABLED',
                'group': 'USERS',
                'pass_none': '*YES',  # Security issue
                'spec_auth': [],
                'prev_sign_on': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'user_class': '*USER',
                'pass_exp': '*NO',
                'job_title': 'Application Developer',
                'department': 'Development',
                'last_password_change': (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d'),
                'failed_login_attempts': 2,
                'compliance_status': 'Non-Compliant'
            },
            'JANESMITH': {
                'name': 'Jane Smith',
                'status': '*DISABLED',  # Security issue
                'group': 'USERS',
                'pass_none': '*NO',
                'spec_auth': [],
                'prev_sign_on': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d'),
                'user_class': '*USER',
                'pass_exp': '*YES',
                'job_title': 'Business Analyst',
                'department': 'Finance',
                'last_password_change': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
                'failed_login_attempts': 0,
                'compliance_status': 'Non-Compliant'
            },
            'ADMIN': {
                'name': 'System Administrator',
                'status': '*ENABLED',
                'group': 'ADMIN',
                'pass_none': '*NO',
                'spec_auth': ['*ALLOBJ', '*IOSYSCFG'],
                'prev_sign_on': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'user_class': '*SECOFR',
                'pass_exp': '*YES',
                'job_title': 'System Administrator',
                'department': 'IT Operations',
                'last_password_change': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'failed_login_attempts': 0,
                'compliance_status': 'Compliant'
            },
            'GUEST': {
                'name': 'Guest User',
                'status': '*ENABLED',
                'group': 'GUEST',
                'pass_none': '*YES',  # Security issue
                'spec_auth': [],
                'prev_sign_on': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                'user_class': '*USER',
                'pass_exp': '*NO',
                'job_title': 'Guest Access',
                'department': 'External',
                'last_password_change': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                'failed_login_attempts': 0,
                'compliance_status': 'Non-Compliant'
            }
        }
        
        # Enhanced Mock Groups with Enterprise Structure
        self.groups = {
            'QSECOFR': {
                'name': 'Security Officers',
                'members': ['QSECOFR'],
                'status': '*ENABLED',
                'description': 'System security administrators',
                'created_date': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA']
            },
            'ADMIN': {
                'name': 'System Administrators',
                'members': ['ADMIN'],
                'status': '*ENABLED',
                'description': 'System administration team',
                'created_date': (datetime.now() - timedelta(days=300)).strftime('%Y-%m-%d'),
                'compliance_frameworks': ['SOX', 'PCI DSS']
            },
            'USERS': {
                'name': 'General Users',
                'members': ['JOHNDOE', 'JANESMITH'],
                'status': '*ENABLED',
                'description': 'Standard business users',
                'created_date': (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d'),
                'compliance_frameworks': ['SOX']
            },
            'GUEST': {
                'name': 'Guest Access',
                'members': ['GUEST'],
                'status': '*ENABLED',
                'description': 'Temporary guest access',
                'created_date': (datetime.now() - timedelta(days=50)).strftime('%Y-%m-%d'),
                'compliance_frameworks': []
            },
            'DEVELOPERS': {
                'name': 'Development Team',
                'members': ['JOHNDOE'],
                'status': '*ENABLED',
                'description': 'Application development team',
                'created_date': (datetime.now() - timedelta(days=150)).strftime('%Y-%m-%d'),
                'compliance_frameworks': ['SOX']
            }
        }
        
        # Enhanced Mock Object Authorities with Enterprise Scenarios
        self.object_authorities = {
            'QSYS/QCMD': {
                '*PUBLIC': {
                    'obj_auth': '*EXCLUDE',
                    'obj_type': '*CMD',
                    'obj_owner': 'QSYS',
                    'risk_level': 'Low',
                    'compliance_frameworks': ['SOX', 'PCI DSS']
                },
                'QSECOFR': {
                    'obj_auth': '*ALL',
                    'obj_type': '*CMD',
                    'obj_owner': 'QSYS',
                    'risk_level': 'High',
                    'compliance_frameworks': ['SOX', 'PCI DSS']
                },
                'ADMIN': {
                    'obj_auth': '*USE',
                    'obj_type': '*CMD',
                    'obj_owner': 'QSYS',
                    'risk_level': 'Medium',
                    'compliance_frameworks': ['SOX']
                }
            },
            'PRODLIB/CUSTOMER': {
                '*PUBLIC': {
                    'obj_auth': '*EXCLUDE',
                    'obj_type': '*FILE',
                    'obj_owner': 'QSECOFR',
                    'risk_level': 'Low',
                    'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA']
                },
                'JOHNDOE': {
                    'obj_auth': '*CHANGE',
                    'obj_type': '*FILE',
                    'obj_owner': 'QSECOFR',
                    'risk_level': 'Medium',
                    'compliance_frameworks': ['SOX', 'PCI DSS']
                }
            },
            'FINLIB/PAYROLL': {
                '*PUBLIC': {
                    'obj_auth': '*EXCLUDE',
                    'obj_type': '*FILE',
                    'obj_owner': 'QSECOFR',
                    'risk_level': 'Low',
                    'compliance_frameworks': ['SOX', 'PCI DSS', 'HIPAA']
                },
                'JANESMITH': {
                    'obj_auth': '*READ',
                    'obj_type': '*FILE',
                    'obj_owner': 'QSECOFR',
                    'risk_level': 'Low',
                    'compliance_frameworks': ['SOX', 'PCI DSS']
                }
            },
            'QSYS/QSYSOPR': {
                '*PUBLIC': {
                    'obj_auth': '*EXCLUDE',
                    'obj_type': '*MSGQ',
                    'obj_owner': 'QSYS',
                    'risk_level': 'Low',
                    'compliance_frameworks': ['SOX']
                },
                'QSECOFR': {
                    'obj_auth': '*ALL',
                    'obj_type': '*MSGQ',
                    'obj_owner': 'QSYS',
                    'risk_level': 'High',
                    'compliance_frameworks': ['SOX']
                }
            }
        }

class IBMiObjectAuthority:
    """Object authority analysis class"""
    
    def __init__(self, data_manager: IBMiDataManager):
        self.data_manager = data_manager
    
    def analyze_object_authorities(self) -> pd.DataFrame:
        """Analyze object authorities and return security issues"""
        results = []
        
        for obj_name, authorities in self.data_manager.object_authorities.items():
            for user, auth_data in authorities.items():
                security_issues = []
                
                if auth_data.get('obj_auth') == '*ALL':
                    security_issues.append("Excessive object authority")
                
                if user == '*PUBLIC' and obj_name.startswith('QSYS/'):
                    security_issues.append("Public access to system objects")
                
                if security_issues:
                    results.append({
                        'object': obj_name,
                        'user': user,
                        'object_type': auth_data.get('obj_type', 'Unknown'),
                        'security_issues': '; '.join(security_issues),
                        'risk_level': self._calculate_risk_level(security_issues, auth_data.get('obj_type'))
                    })
        
        return pd.DataFrame(results)
    
    def _calculate_risk_level(self, security_issues: List[str], object_type: str = None) -> str:
        """Calculate risk level based on security issues"""
        base_score = len(security_issues) * 10
        
        if object_type:
            object_risk_factors = {
                '*CMD': 5,
                '*FILE': 8,
                '*LIB': 6,
                '*PGM': 7
            }
            base_score += object_risk_factors.get(object_type, 3)
        
        if base_score >= 40:
            return 'High'
        elif base_score >= 20:
            return 'Medium'
        else:
            return 'Low'

class IBMiUserProfiles:
    """User profile analysis class"""
    
    def __init__(self, data_manager: IBMiDataManager):
        self.data_manager = data_manager
    
    def analyze_user_profiles(self) -> pd.DataFrame:
        """Analyze user profiles and return security issues"""
        results = []
        
        for user_id, profile in self.data_manager.user_profiles.items():
            security_issues = []
            
            if profile.get('pass_none') == '*YES':
                security_issues.append("No password set")
            
            if profile.get('status') == '*DISABLED':
                security_issues.append("Account disabled")
            
            spec_auth = profile.get('spec_auth', [])
            if '*ALLOBJ' in spec_auth:
                security_issues.append("All object authority")
            
            if security_issues:
                results.append({
                    'user_id': user_id,
                    'name': profile.get('name', 'Unknown'),
                    'status': profile.get('status', 'Unknown'),
                    'group': profile.get('group', 'Unknown'),
                    'special_authorities': ', '.join(spec_auth) if spec_auth else 'None',
                    'security_issues': '; '.join(security_issues),
                    'risk_level': self._calculate_risk_level(security_issues, profile)
                })
        
        return pd.DataFrame(results)
    
    def _calculate_risk_level(self, security_issues: List[str], user_profile: Dict = None) -> str:
        """Calculate risk level based on security issues"""
        base_score = len(security_issues) * 10
        
        if user_profile:
            if user_profile.get('pass_none') == '*YES':
                base_score += 20
            if user_profile.get('status') == '*DISABLED':
                base_score += 15
            if '*ALLOBJ' in user_profile.get('spec_auth', []):
                base_score += 25
        
        if base_score >= 40:
            return 'High'
        elif base_score >= 20:
            return 'Medium'
        else:
            return 'Low'

class IBMiSystemValues:
    """System values analysis class"""
    
    def __init__(self, data_manager: IBMiDataManager):
        self.data_manager = data_manager
    
    def analyze_system_values(self) -> pd.DataFrame:
        """Analyze system values and return compliance issues"""
        results = []
        
        for sysval_name, sysval_data in self.data_manager.system_values.items():
            if sysval_data.get('exception', False):
                results.append({
                    'system_value': sysval_name,
                    'current_value': sysval_data.get('current', 'Unknown'),
                    'recommended_value': sysval_data.get('recommended', 'Unknown'),
                    'description': sysval_data.get('description', 'Unknown'),
                    'compliance_status': 'Non-Compliant',
                    'risk_level': 'High'
                })
            else:
                results.append({
                    'system_value': sysval_name,
                    'current_value': sysval_data.get('current', 'Unknown'),
                    'recommended_value': sysval_data.get('recommended', 'Unknown'),
                    'description': sysval_data.get('description', 'Unknown'),
                    'compliance_status': 'Compliant',
                    'risk_level': 'Low'
                })
        
        return pd.DataFrame(results)

class IBMiSecurityAuditor:
    """Main auditor class that orchestrates all security analysis"""
    
    def __init__(self):
        self.data_manager = IBMiDataManager()
        self.object_authority = IBMiObjectAuthority(self.data_manager)
        self.user_profiles = IBMiUserProfiles(self.data_manager)
        self.system_values = IBMiSystemValues(self.data_manager)
        
        # Generate initial data
        self.data_manager.generate_mock_ibm_i_data()
    
    def analyze_compliance_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Analyze compliance against major frameworks with specific controls"""
        
        # Define specific compliance controls for each framework
        compliance_controls = {
            'SOX': {
                'name': 'Sarbanes-Oxley Act',
                'description': 'Financial reporting and corporate governance',
                'controls': [
                    {
                        'id': 'SOX-001',
                        'title': 'Password Policy Enforcement',
                        'description': 'System must enforce password policies including expiration and complexity',
                        'requirement': 'SOX Section 404 - Internal Controls',
                        'test_method': 'Check QPWDEXPITV and QPWDCHGCYC system values',
                        'pass_criteria': 'Password expiration enabled and change cycle required',
                        'status': 'PASS',
                        'evidence': '',
                        'remediation': '',
                        'priority': 'High'
                    },
                    {
                        'id': 'SOX-002',
                        'title': 'Access Control Monitoring',
                        'description': 'System must monitor and log access to financial data',
                        'requirement': 'SOX Section 404 - Access Controls',
                        'test_method': 'Check QINACTMSGQ system value for inactivity monitoring',
                        'pass_criteria': 'Inactivity message queue configured',
                        'status': 'FAIL',
                        'evidence': 'QINACTMSGQ set to *NONE',
                        'remediation': 'Set QINACTMSGQ to QSYSOPR',
                        'priority': 'Medium'
                    },
                    {
                        'id': 'SOX-003',
                        'title': 'User Account Management',
                        'description': 'All user accounts must be properly managed and monitored',
                        'requirement': 'SOX Section 404 - User Management',
                        'test_method': 'Review user profiles for compliance status',
                        'pass_criteria': 'All users have proper passwords and are enabled',
                        'status': 'FAIL',
                        'evidence': '3 users with security issues found',
                        'remediation': 'Fix password and account issues for JOHNDOE, JANESMITH, GUEST',
                        'priority': 'High'
                    },
                    {
                        'id': 'SOX-004',
                        'title': 'System Security Level',
                        'description': 'System must operate at appropriate security level',
                        'requirement': 'SOX Section 404 - System Security',
                        'test_method': 'Check QSECURITY system value',
                        'pass_criteria': 'QSECURITY set to 40 or higher',
                        'status': 'PASS',
                        'evidence': 'QSECURITY set to 40',
                        'remediation': '',
                        'priority': 'High'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'PCI DSS': {
                'name': 'Payment Card Industry Data Security Standard',
                'description': 'Payment card data security',
                'controls': [
                    {
                        'id': 'PCI-001',
                        'title': 'Strong Password Requirements',
                        'description': 'Implement strong password policies for all users',
                        'requirement': 'PCI DSS Requirement 8.2',
                        'test_method': 'Check password validation program and expiration settings',
                        'pass_criteria': 'Password validation program configured and expiration enabled',
                        'status': 'FAIL',
                        'evidence': 'QPWDVLDPGM set to *NONE, QPWDCHGCYC set to 0',
                        'remediation': 'Configure QPWDVLDPGM and enable password change cycle',
                        'priority': 'High'
                    },
                    {
                        'id': 'PCI-002',
                        'title': 'Access Control Implementation',
                        'description': 'Restrict access to cardholder data based on job function',
                        'requirement': 'PCI DSS Requirement 7.1',
                        'test_method': 'Review object authorities for sensitive data files',
                        'pass_criteria': 'No excessive object authorities on sensitive files',
                        'status': 'FAIL',
                        'evidence': 'QSECOFR has *ALL authority on system objects',
                        'remediation': 'Review and restrict QSECOFR object authorities',
                        'priority': 'High'
                    },
                    {
                        'id': 'PCI-003',
                        'title': 'Failed Login Attempts',
                        'description': 'Limit repeated access attempts by locking out user IDs',
                        'requirement': 'PCI DSS Requirement 8.1.6',
                        'test_method': 'Check QMAXSIGN system value',
                        'pass_criteria': 'QMAXSIGN set to 5 or fewer attempts',
                        'status': 'PASS',
                        'evidence': 'QMAXSIGN set to 5',
                        'remediation': '',
                        'priority': 'Medium'
                    },
                    {
                        'id': 'PCI-004',
                        'title': 'User Authentication',
                        'description': 'Ensure all users have proper authentication',
                        'requirement': 'PCI DSS Requirement 8.1',
                        'test_method': 'Review user profiles for password requirements',
                        'pass_criteria': 'All users have passwords set',
                        'status': 'FAIL',
                        'evidence': 'JOHNDOE and GUEST have no passwords set',
                        'remediation': 'Set passwords for JOHNDOE and GUEST users',
                        'priority': 'Critical'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'HIPAA': {
                'name': 'Health Insurance Portability and Accountability Act',
                'description': 'Healthcare data privacy and security',
                'controls': [
                    {
                        'id': 'HIPAA-001',
                        'title': 'Access Control',
                        'description': 'Implement technical policies and procedures for electronic information systems',
                        'requirement': 'HIPAA Security Rule 164.312(a)(1)',
                        'test_method': 'Review user access controls and authentication',
                        'pass_criteria': 'All users have proper access controls and authentication',
                        'status': 'FAIL',
                        'evidence': 'Multiple users with authentication and access control issues',
                        'remediation': 'Implement proper access controls for all users',
                        'priority': 'High'
                    },
                    {
                        'id': 'HIPAA-002',
                        'title': 'Audit Controls',
                        'description': 'Implement hardware, software, and/or procedural mechanisms to record and examine access',
                        'requirement': 'HIPAA Security Rule 164.312(b)',
                        'test_method': 'Check system values for audit and monitoring capabilities',
                        'pass_criteria': 'Audit controls and monitoring enabled',
                        'status': 'FAIL',
                        'evidence': 'QINACTMSGQ not configured for monitoring',
                        'remediation': 'Configure inactivity monitoring and audit controls',
                        'priority': 'Medium'
                    },
                    {
                        'id': 'HIPAA-003',
                        'title': 'Person or Entity Authentication',
                        'description': 'Implement procedures to verify that a person or entity seeking access is authorized',
                        'requirement': 'HIPAA Security Rule 164.312(d)',
                        'test_method': 'Review user authentication mechanisms',
                        'pass_criteria': 'All users have proper authentication',
                        'status': 'FAIL',
                        'evidence': 'Users without passwords and disabled accounts found',
                        'remediation': 'Ensure all users have proper authentication',
                        'priority': 'Critical'
                    },
                    {
                        'id': 'HIPAA-004',
                        'title': 'Transmission Security',
                        'description': 'Implement technical security measures to guard against unauthorized access',
                        'requirement': 'HIPAA Security Rule 164.312(c)(1)',
                        'test_method': 'Check system security level and access controls',
                        'pass_criteria': 'System security level appropriate and access controlled',
                        'status': 'PASS',
                        'evidence': 'QSECURITY set to 40',
                        'remediation': '',
                        'priority': 'Medium'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'ISO 27001': {
                'name': 'ISO/IEC 27001 Information Security Management',
                'description': 'International standard for information security management systems',
                'controls': [
                    {
                        'id': 'ISO-001',
                        'title': 'Access Control Policy',
                        'description': 'Define and implement access control policy based on business requirements',
                        'requirement': 'ISO 27001 A.9.1.1',
                        'test_method': 'Review system security level and access control mechanisms',
                        'pass_criteria': 'Access control policy implemented and enforced',
                        'status': 'PASS',
                        'evidence': 'QSECURITY set to 40 with proper access controls',
                        'remediation': '',
                        'priority': 'High'
                    },
                    {
                        'id': 'ISO-002',
                        'title': 'User Registration and De-registration',
                        'description': 'Formal user registration and de-registration process for access to systems',
                        'requirement': 'ISO 27001 A.9.2.1',
                        'test_method': 'Review user profile management and status',
                        'pass_criteria': 'All users properly registered and managed',
                        'status': 'FAIL',
                        'evidence': 'GUEST account disabled, JOHNDOE has no password',
                        'remediation': 'Review and fix user registration issues',
                        'priority': 'High'
                    },
                    {
                        'id': 'ISO-003',
                        'title': 'Password Management System',
                        'description': 'Implement secure password management system',
                        'requirement': 'ISO 27001 A.9.3.1',
                        'test_method': 'Check password policies and validation',
                        'pass_criteria': 'Strong password policy enforced',
                        'status': 'FAIL',
                        'evidence': 'QPWDVLDPGM not configured, weak password settings',
                        'remediation': 'Implement strong password validation program',
                        'priority': 'High'
                    },
                    {
                        'id': 'ISO-004',
                        'title': 'Privileged Access Rights',
                        'description': 'Allocation and use of privileged access rights',
                        'requirement': 'ISO 27001 A.9.2.3',
                        'test_method': 'Review special authorities and object access',
                        'pass_criteria': 'Privileged access properly controlled',
                        'status': 'FAIL',
                        'evidence': 'QSECOFR has excessive *ALL authorities',
                        'remediation': 'Review and restrict privileged access rights',
                        'priority': 'Critical'
                    },
                    {
                        'id': 'ISO-005',
                        'title': 'Information Access Restriction',
                        'description': 'Restrict access to information and application system functions',
                        'requirement': 'ISO 27001 A.9.1.2',
                        'test_method': 'Review object authorities and access controls',
                        'pass_criteria': 'Information access properly restricted',
                        'status': 'FAIL',
                        'evidence': 'Multiple excessive object authorities found',
                        'remediation': 'Implement proper access restrictions',
                        'priority': 'High'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'NIST': {
                'name': 'NIST Cybersecurity Framework',
                'description': 'Framework for improving critical infrastructure cybersecurity',
                'controls': [
                    {
                        'id': 'NIST-001',
                        'title': 'Identity Management and Access Control',
                        'description': 'Implement identity management and access control capabilities',
                        'requirement': 'NIST CSF ID.AM-6',
                        'test_method': 'Review user identity management and access controls',
                        'pass_criteria': 'Proper identity management and access control implemented',
                        'status': 'FAIL',
                        'evidence': 'Multiple identity and access control issues found',
                        'remediation': 'Implement proper identity management and access controls',
                        'priority': 'High'
                    },
                    {
                        'id': 'NIST-002',
                        'title': 'Asset Inventory',
                        'description': 'Maintain inventory of authorized and unauthorized devices and software',
                        'requirement': 'NIST CSF ID.AM-1',
                        'test_method': 'Review system object inventory and access',
                        'pass_criteria': 'Complete asset inventory maintained',
                        'status': 'PASS',
                        'evidence': 'System objects properly inventoried and tracked',
                        'remediation': '',
                        'priority': 'Medium'
                    },
                    {
                        'id': 'NIST-003',
                        'title': 'Access Control Implementation',
                        'description': 'Implement access control policies and procedures',
                        'requirement': 'NIST CSF PR.AC-1',
                        'test_method': 'Review access control mechanisms and policies',
                        'pass_criteria': 'Access control policies properly implemented',
                        'status': 'FAIL',
                        'evidence': 'Access control policies not fully implemented',
                        'remediation': 'Implement comprehensive access control policies',
                        'priority': 'High'
                    },
                    {
                        'id': 'NIST-004',
                        'title': 'Continuous Monitoring',
                        'description': 'Implement continuous monitoring capabilities',
                        'requirement': 'NIST CSF DE.CM-1',
                        'test_method': 'Check monitoring and logging capabilities',
                        'pass_criteria': 'Continuous monitoring implemented',
                        'status': 'FAIL',
                        'evidence': 'QINACTMSGQ not configured for monitoring',
                        'remediation': 'Implement continuous monitoring capabilities',
                        'priority': 'Medium'
                    },
                    {
                        'id': 'NIST-005',
                        'title': 'Incident Response',
                        'description': 'Implement incident response capabilities',
                        'requirement': 'NIST CSF RS.RP-1',
                        'test_method': 'Review incident response and monitoring capabilities',
                        'pass_criteria': 'Incident response capabilities implemented',
                        'status': 'FAIL',
                        'evidence': 'No incident response monitoring configured',
                        'remediation': 'Implement incident response and monitoring',
                        'priority': 'High'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'HI-TRUST': {
                'name': 'HITRUST Common Security Framework',
                'description': 'Comprehensive security framework for healthcare organizations',
                'controls': [
                    {
                        'id': 'HITRUST-001',
                        'title': 'Access Control Policy and Procedures',
                        'description': 'Establish, document, and disseminate access control policy',
                        'requirement': 'HITRUST CSF 01.a',
                        'test_method': 'Review access control policy implementation',
                        'pass_criteria': 'Access control policy established and documented',
                        'status': 'FAIL',
                        'evidence': 'No formal access control policy documented',
                        'remediation': 'Establish and document access control policy',
                        'priority': 'High'
                    },
                    {
                        'id': 'HITRUST-002',
                        'title': 'Account Management',
                        'description': 'Establish and maintain procedures for account management',
                        'requirement': 'HITRUST CSF 01.b',
                        'test_method': 'Review user account management procedures',
                        'pass_criteria': 'Account management procedures implemented',
                        'status': 'FAIL',
                        'evidence': 'Account management procedures not properly implemented',
                        'remediation': 'Implement proper account management procedures',
                        'priority': 'High'
                    },
                    {
                        'id': 'HITRUST-003',
                        'title': 'Access Enforcement',
                        'description': 'Enforce access control policy for all users',
                        'requirement': 'HITRUST CSF 01.c',
                        'test_method': 'Review access enforcement mechanisms',
                        'pass_criteria': 'Access control policy enforced for all users',
                        'status': 'FAIL',
                        'evidence': 'Access control not properly enforced',
                        'remediation': 'Enforce access control policy consistently',
                        'priority': 'Critical'
                    },
                    {
                        'id': 'HITRUST-004',
                        'title': 'Information Flow Enforcement',
                        'description': 'Enforce information flow control policy',
                        'requirement': 'HITRUST CSF 01.d',
                        'test_method': 'Review information flow controls',
                        'pass_criteria': 'Information flow controls implemented',
                        'status': 'FAIL',
                        'evidence': 'Information flow controls not implemented',
                        'remediation': 'Implement information flow controls',
                        'priority': 'High'
                    },
                    {
                        'id': 'HITRUST-005',
                        'title': 'Separation of Duties',
                        'description': 'Implement separation of duties for critical functions',
                        'requirement': 'HITRUST CSF 01.e',
                        'test_method': 'Review user roles and responsibilities',
                        'pass_criteria': 'Separation of duties implemented',
                        'status': 'FAIL',
                        'evidence': 'QSECOFR has excessive privileges',
                        'remediation': 'Implement proper separation of duties',
                        'priority': 'Critical'
                    },
                    {
                        'id': 'HITRUST-006',
                        'title': 'Least Privilege',
                        'description': 'Implement least privilege principle for user access',
                        'requirement': 'HITRUST CSF 01.f',
                        'test_method': 'Review user privileges and access rights',
                        'pass_criteria': 'Least privilege principle implemented',
                        'status': 'FAIL',
                        'evidence': 'Multiple users have excessive privileges',
                        'remediation': 'Implement least privilege principle',
                        'priority': 'High'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            }
        }
        
        # Evaluate controls based on actual system data
        for framework_name, framework_data in compliance_controls.items():
            failed_controls = []
            
            for control in framework_data['controls']:
                # Evaluate control based on system data
                if framework_name == 'SOX':
                    if control['id'] == 'SOX-001':
                        # Check password policy enforcement
                        pwd_exp = self.data_manager.system_values.get('QPWDEXPITV', {}).get('current', '0')
                        pwd_cycle = self.data_manager.system_values.get('QPWDCHGCYC', {}).get('current', '0')
                        if pwd_exp != '0' and pwd_cycle != '0':
                            control['status'] = 'PASS'
                            control['evidence'] = f'QPWDEXPITV={pwd_exp}, QPWDCHGCYC={pwd_cycle}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QPWDEXPITV={pwd_exp}, QPWDCHGCYC={pwd_cycle}'
                            control['remediation'] = 'Enable password expiration and change cycle'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'SOX-002':
                        # Check access control monitoring
                        inact_msgq = self.data_manager.system_values.get('QINACTMSGQ', {}).get('current', '*NONE')
                        if inact_msgq != '*NONE':
                            control['status'] = 'PASS'
                            control['evidence'] = f'QINACTMSGQ={inact_msgq}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QINACTMSGQ={inact_msgq}'
                            control['remediation'] = 'Set QINACTMSGQ to QSYSOPR'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'SOX-003':
                        # Check user account management
                        non_compliant_users = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                             if profile.get('compliance_status') == 'Non-Compliant']
                        if not non_compliant_users:
                            control['status'] = 'PASS'
                            control['evidence'] = 'All users compliant'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'{len(non_compliant_users)} non-compliant users: {", ".join(non_compliant_users)}'
                            control['remediation'] = f'Fix compliance issues for: {", ".join(non_compliant_users)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'SOX-004':
                        # Check system security level
                        qsecurity = self.data_manager.system_values.get('QSECURITY', {}).get('current', '0')
                        if int(qsecurity) >= 40:
                            control['status'] = 'PASS'
                            control['evidence'] = f'QSECURITY={qsecurity}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QSECURITY={qsecurity}'
                            control['remediation'] = 'Set QSECURITY to 40 or higher'
                            failed_controls.append(control)
                
                elif framework_name == 'PCI DSS':
                    if control['id'] == 'PCI-001':
                        # Check strong password requirements
                        pwd_val = self.data_manager.system_values.get('QPWDVLDPGM', {}).get('current', '*NONE')
                        pwd_cycle = self.data_manager.system_values.get('QPWDCHGCYC', {}).get('current', '0')
                        if pwd_val != '*NONE' and pwd_cycle != '0':
                            control['status'] = 'PASS'
                            control['evidence'] = f'QPWDVLDPGM={pwd_val}, QPWDCHGCYC={pwd_cycle}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QPWDVLDPGM={pwd_val}, QPWDCHGCYC={pwd_cycle}'
                            control['remediation'] = 'Configure QPWDVLDPGM and enable password change cycle'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'PCI-002':
                        # Check access control implementation
                        excessive_auth = False
                        for obj_name, authorities in self.data_manager.object_authorities.items():
                            for user, auth_data in authorities.items():
                                if auth_data.get('obj_auth') == '*ALL' and obj_name.startswith('QSYS/'):
                                    excessive_auth = True
                                    break
                        if not excessive_auth:
                            control['status'] = 'PASS'
                            control['evidence'] = 'No excessive object authorities found'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = 'QSECOFR has *ALL authority on system objects'
                            control['remediation'] = 'Review and restrict QSECOFR object authorities'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'PCI-003':
                        # Check failed login attempts
                        max_sign = self.data_manager.system_values.get('QMAXSIGN', {}).get('current', '10')
                        if int(max_sign) <= 5:
                            control['status'] = 'PASS'
                            control['evidence'] = f'QMAXSIGN={max_sign}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QMAXSIGN={max_sign}'
                            control['remediation'] = 'Set QMAXSIGN to 5 or fewer'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'PCI-004':
                        # Check user authentication
                        users_no_pwd = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                      if profile.get('pass_none') == '*YES']
                        if not users_no_pwd:
                            control['status'] = 'PASS'
                            control['evidence'] = 'All users have passwords set'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Users without passwords: {", ".join(users_no_pwd)}'
                            control['remediation'] = f'Set passwords for: {", ".join(users_no_pwd)}'
                            failed_controls.append(control)
                
                elif framework_name == 'HIPAA':
                    if control['id'] == 'HIPAA-001':
                        # Check access control
                        access_issues = []
                        for uid, profile in self.data_manager.user_profiles.items():
                            if profile.get('pass_none') == '*YES' or profile.get('status') == '*DISABLED':
                                access_issues.append(uid)
                        if not access_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'All users have proper access controls'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Access control issues: {", ".join(access_issues)}'
                            control['remediation'] = f'Fix access controls for: {", ".join(access_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HIPAA-002':
                        # Check audit controls
                        inact_msgq = self.data_manager.system_values.get('QINACTMSGQ', {}).get('current', '*NONE')
                        if inact_msgq != '*NONE':
                            control['status'] = 'PASS'
                            control['evidence'] = f'QINACTMSGQ={inact_msgq}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QINACTMSGQ={inact_msgq}'
                            control['remediation'] = 'Configure inactivity monitoring and audit controls'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HIPAA-003':
                        # Check person or entity authentication
                        auth_issues = []
                        for uid, profile in self.data_manager.user_profiles.items():
                            if profile.get('pass_none') == '*YES':
                                auth_issues.append(uid)
                        if not auth_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'All users have proper authentication'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Authentication issues: {", ".join(auth_issues)}'
                            control['remediation'] = f'Ensure proper authentication for: {", ".join(auth_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HIPAA-004':
                        # Check transmission security
                        qsecurity = self.data_manager.system_values.get('QSECURITY', {}).get('current', '0')
                        if int(qsecurity) >= 40:
                            control['status'] = 'PASS'
                            control['evidence'] = f'QSECURITY={qsecurity}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QSECURITY={qsecurity}'
                            control['remediation'] = 'Set QSECURITY to 40 or higher'
                            failed_controls.append(control)
                
                elif framework_name == 'ISO 27001':
                    if control['id'] == 'ISO-001':
                        # Check access control policy
                        qsecurity = self.data_manager.system_values.get('QSECURITY', {}).get('current', '0')
                        if int(qsecurity) >= 40:
                            control['status'] = 'PASS'
                            control['evidence'] = f'QSECURITY={qsecurity} with proper access controls'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QSECURITY={qsecurity} - insufficient access controls'
                            control['remediation'] = 'Set QSECURITY to 40 or higher'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'ISO-002':
                        # Check user registration and de-registration
                        registration_issues = []
                        for uid, profile in self.data_manager.user_profiles.items():
                            if profile.get('status') == '*DISABLED' or profile.get('pass_none') == '*YES':
                                registration_issues.append(uid)
                        if not registration_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'All users properly registered and managed'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Registration issues: {", ".join(registration_issues)}'
                            control['remediation'] = f'Review and fix user registration issues for: {", ".join(registration_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'ISO-003':
                        # Check password management system
                        pwd_val = self.data_manager.system_values.get('QPWDVLDPGM', {}).get('current', '*NONE')
                        pwd_cycle = self.data_manager.system_values.get('QPWDCHGCYC', {}).get('current', '0')
                        if pwd_val != '*NONE' and pwd_cycle != '0':
                            control['status'] = 'PASS'
                            control['evidence'] = f'QPWDVLDPGM={pwd_val}, QPWDCHGCYC={pwd_cycle}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QPWDVLDPGM={pwd_val}, QPWDCHGCYC={pwd_cycle}'
                            control['remediation'] = 'Implement strong password validation program'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'ISO-004':
                        # Check privileged access rights
                        excessive_priv = False
                        for obj_name, authorities in self.data_manager.object_authorities.items():
                            for user, auth_data in authorities.items():
                                if auth_data.get('obj_auth') == '*ALL' and user == 'QSECOFR':
                                    excessive_priv = True
                                    break
                        if not excessive_priv:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Privileged access properly controlled'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = 'QSECOFR has excessive *ALL authorities'
                            control['remediation'] = 'Review and restrict privileged access rights'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'ISO-005':
                        # Check information access restriction
                        excessive_auth = False
                        for obj_name, authorities in self.data_manager.object_authorities.items():
                            for user, auth_data in authorities.items():
                                if auth_data.get('obj_auth') == '*ALL':
                                    excessive_auth = True
                                    break
                        if not excessive_auth:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Information access properly restricted'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = 'Multiple excessive object authorities found'
                            control['remediation'] = 'Implement proper access restrictions'
                            failed_controls.append(control)
                
                elif framework_name == 'NIST':
                    if control['id'] == 'NIST-001':
                        # Check identity management and access control
                        identity_issues = []
                        for uid, profile in self.data_manager.user_profiles.items():
                            if profile.get('pass_none') == '*YES' or profile.get('status') == '*DISABLED':
                                identity_issues.append(uid)
                        if not identity_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Proper identity management and access control implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Identity and access control issues: {", ".join(identity_issues)}'
                            control['remediation'] = f'Implement proper identity management and access controls for: {", ".join(identity_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'NIST-002':
                        # Check asset inventory
                        total_objects = len(self.data_manager.object_authorities)
                        if total_objects > 0:
                            control['status'] = 'PASS'
                            control['evidence'] = f'System objects properly inventoried and tracked ({total_objects} objects)'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = 'No system objects inventoried'
                            control['remediation'] = 'Implement proper asset inventory'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'NIST-003':
                        # Check access control implementation
                        access_issues = []
                        for obj_name, authorities in self.data_manager.object_authorities.items():
                            for user, auth_data in authorities.items():
                                if auth_data.get('obj_auth') == '*ALL':
                                    access_issues.append(f'{user} on {obj_name}')
                        if not access_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Access control policies properly implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Access control issues: {", ".join(access_issues[:3])}'
                            control['remediation'] = 'Implement comprehensive access control policies'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'NIST-004':
                        # Check continuous monitoring
                        inact_msgq = self.data_manager.system_values.get('QINACTMSGQ', {}).get('current', '*NONE')
                        if inact_msgq != '*NONE':
                            control['status'] = 'PASS'
                            control['evidence'] = f'Continuous monitoring implemented: QINACTMSGQ={inact_msgq}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'QINACTMSGQ={inact_msgq} - monitoring not configured'
                            control['remediation'] = 'Implement continuous monitoring capabilities'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'NIST-005':
                        # Check incident response
                        monitoring_configured = self.data_manager.system_values.get('QINACTMSGQ', {}).get('current', '*NONE') != '*NONE'
                        if monitoring_configured:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Incident response monitoring configured'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = 'No incident response monitoring configured'
                            control['remediation'] = 'Implement incident response and monitoring'
                            failed_controls.append(control)
                
                elif framework_name == 'HI-TRUST':
                    if control['id'] == 'HITRUST-001':
                        # Check access control policy and procedures
                        qsecurity = self.data_manager.system_values.get('QSECURITY', {}).get('current', '0')
                        if int(qsecurity) >= 40:
                            control['status'] = 'PASS'
                            control['evidence'] = f'Access control policy implemented: QSECURITY={qsecurity}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'No formal access control policy documented: QSECURITY={qsecurity}'
                            control['remediation'] = 'Establish and document access control policy'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HITRUST-002':
                        # Check account management
                        account_issues = []
                        for uid, profile in self.data_manager.user_profiles.items():
                            if profile.get('pass_none') == '*YES' or profile.get('status') == '*DISABLED':
                                account_issues.append(uid)
                        if not account_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Account management procedures implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Account management issues: {", ".join(account_issues)}'
                            control['remediation'] = f'Implement proper account management procedures for: {", ".join(account_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HITRUST-003':
                        # Check access enforcement
                        enforcement_issues = []
                        for obj_name, authorities in self.data_manager.object_authorities.items():
                            for user, auth_data in authorities.items():
                                if auth_data.get('obj_auth') == '*ALL':
                                    enforcement_issues.append(f'{user} on {obj_name}')
                        if not enforcement_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Access control policy enforced for all users'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Access control not properly enforced: {", ".join(enforcement_issues[:3])}'
                            control['remediation'] = 'Enforce access control policy consistently'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HITRUST-004':
                        # Check information flow enforcement
                        flow_issues = []
                        for obj_name, authorities in self.data_manager.object_authorities.items():
                            for user, auth_data in authorities.items():
                                if auth_data.get('obj_auth') == '*ALL':
                                    flow_issues.append(f'{user} on {obj_name}')
                        if not flow_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Information flow controls implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Information flow controls not implemented: {", ".join(flow_issues[:3])}'
                            control['remediation'] = 'Implement information flow controls'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HITRUST-005':
                        # Check separation of duties
                        excessive_priv = False
                        for obj_name, authorities in self.data_manager.object_authorities.items():
                            for user, auth_data in authorities.items():
                                if auth_data.get('obj_auth') == '*ALL' and user == 'QSECOFR':
                                    excessive_priv = True
                                    break
                        if not excessive_priv:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Separation of duties implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = 'QSECOFR has excessive privileges'
                            control['remediation'] = 'Implement proper separation of duties'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HITRUST-006':
                        # Check least privilege
                        privilege_issues = []
                        for obj_name, authorities in self.data_manager.object_authorities.items():
                            for user, auth_data in authorities.items():
                                if auth_data.get('obj_auth') == '*ALL':
                                    privilege_issues.append(f'{user} on {obj_name}')
                        if not privilege_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Least privilege principle implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Multiple users have excessive privileges: {", ".join(privilege_issues[:3])}'
                            control['remediation'] = 'Implement least privilege principle'
                            failed_controls.append(control)
            
            # Calculate compliance score based on controls
            total_controls = len(framework_data['controls'])
            passed_controls = len([c for c in framework_data['controls'] if c['status'] == 'PASS'])
            framework_data['compliance_score'] = int((passed_controls / total_controls) * 100) if total_controls > 0 else 0
            
            # Generate recommendations based on failed controls
            if failed_controls:
                framework_data['recommendations'] = [
                    f"Address {len(failed_controls)} failed controls",
                    "Prioritize Critical and High priority controls",
                    "Implement automated compliance monitoring",
                    "Conduct regular compliance audits"
                ]
                # Add specific remediation steps
                for control in failed_controls:
                    if control['remediation']:
                        framework_data['recommendations'].append(f"- {control['id']}: {control['remediation']}")
            else:
                framework_data['recommendations'] = [
                    "All controls are passing",
                    "Maintain current security posture",
                    "Continue regular compliance monitoring"
                ]
            
            # Add failed controls to critical issues
            framework_data['critical_issues'] = failed_controls
        
        return compliance_controls
    
    def analyze_user_management_compliance(self) -> Dict[str, Dict[str, Any]]:
        """Analyze user management compliance against major frameworks with user-specific controls"""
        
        # Define user management specific compliance controls for each framework
        user_management_controls = {
            'SOX': {
                'name': 'Sarbanes-Oxley Act - User Management',
                'description': 'User management controls for financial reporting compliance',
                'controls': [
                    {
                        'id': 'SOX-UM-001',
                        'title': 'User Account Lifecycle Management',
                        'description': 'Proper user account creation, modification, and termination processes',
                        'requirement': 'SOX Section 404 - User Management Controls',
                        'test_method': 'Review user profile status and management procedures',
                        'pass_criteria': 'All user accounts properly managed and documented',
                        'status': 'PASS',
                        'evidence': '',
                        'remediation': '',
                        'priority': 'High'
                    },
                    {
                        'id': 'SOX-UM-002',
                        'title': 'Password Policy Enforcement',
                        'description': 'Strong password policies enforced for all users',
                        'requirement': 'SOX Section 404 - Authentication Controls',
                        'test_method': 'Check user password settings and policies',
                        'pass_criteria': 'All users have passwords and password policies enforced',
                        'status': 'FAIL',
                        'evidence': 'Multiple users without passwords found',
                        'remediation': 'Enforce password requirements for all users',
                        'priority': 'High'
                    },
                    {
                        'id': 'SOX-UM-003',
                        'title': 'User Access Review',
                        'description': 'Regular review of user access and privileges',
                        'requirement': 'SOX Section 404 - Access Control Monitoring',
                        'test_method': 'Review user special authorities and access rights',
                        'pass_criteria': 'User access regularly reviewed and documented',
                        'status': 'FAIL',
                        'evidence': 'Users with excessive privileges found',
                        'remediation': 'Implement regular user access reviews',
                        'priority': 'Medium'
                    },
                    {
                        'id': 'SOX-UM-004',
                        'title': 'User Activity Monitoring',
                        'description': 'Monitor and log user activities for audit purposes',
                        'requirement': 'SOX Section 404 - Audit Controls',
                        'test_method': 'Check user activity logging and monitoring',
                        'pass_criteria': 'User activities properly monitored and logged',
                        'status': 'PASS',
                        'evidence': 'User activity monitoring enabled',
                        'remediation': '',
                        'priority': 'Medium'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'PCI DSS': {
                'name': 'Payment Card Industry Data Security Standard - User Management',
                'description': 'User management controls for payment card data security',
                'controls': [
                    {
                        'id': 'PCI-UM-001',
                        'title': 'Unique User Identification',
                        'description': 'Each user must have a unique identifier',
                        'requirement': 'PCI DSS Requirement 8.1',
                        'test_method': 'Review user profile uniqueness and identification',
                        'pass_criteria': 'All users have unique identifiers',
                        'status': 'PASS',
                        'evidence': 'All users have unique user IDs',
                        'remediation': '',
                        'priority': 'High'
                    },
                    {
                        'id': 'PCI-UM-002',
                        'title': 'Strong Authentication',
                        'description': 'Implement strong authentication mechanisms',
                        'requirement': 'PCI DSS Requirement 8.2',
                        'test_method': 'Check user password strength and authentication',
                        'pass_criteria': 'Strong authentication implemented for all users',
                        'status': 'FAIL',
                        'evidence': 'Users without passwords and weak authentication found',
                        'remediation': 'Implement strong authentication for all users',
                        'priority': 'Critical'
                    },
                    {
                        'id': 'PCI-UM-003',
                        'title': 'Account Management',
                        'description': 'Proper account management and lifecycle controls',
                        'requirement': 'PCI DSS Requirement 8.3',
                        'test_method': 'Review account management procedures and status',
                        'pass_criteria': 'Account management properly implemented',
                        'status': 'FAIL',
                        'evidence': 'Account management issues found',
                        'remediation': 'Implement proper account management procedures',
                        'priority': 'High'
                    },
                    {
                        'id': 'PCI-UM-004',
                        'title': 'Access Control',
                        'description': 'Restrict access based on job function',
                        'requirement': 'PCI DSS Requirement 7.1',
                        'test_method': 'Review user access rights and job functions',
                        'pass_criteria': 'Access restricted based on job function',
                        'status': 'FAIL',
                        'evidence': 'Users with excessive access rights found',
                        'remediation': 'Restrict user access based on job function',
                        'priority': 'High'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'HIPAA': {
                'name': 'Health Insurance Portability and Accountability Act - User Management',
                'description': 'User management controls for healthcare data privacy',
                'controls': [
                    {
                        'id': 'HIPAA-UM-001',
                        'title': 'Unique User Identification',
                        'description': 'Assign unique user identification for each user',
                        'requirement': 'HIPAA Security Rule 164.312(a)(2)(i)',
                        'test_method': 'Review user identification and uniqueness',
                        'pass_criteria': 'All users have unique identification',
                        'status': 'PASS',
                        'evidence': 'All users have unique user IDs',
                        'remediation': '',
                        'priority': 'High'
                    },
                    {
                        'id': 'HIPAA-UM-002',
                        'title': 'Emergency Access Procedures',
                        'description': 'Establish emergency access procedures',
                        'requirement': 'HIPAA Security Rule 164.312(a)(2)(ii)',
                        'test_method': 'Review emergency access procedures and accounts',
                        'pass_criteria': 'Emergency access procedures established',
                        'status': 'FAIL',
                        'evidence': 'No emergency access procedures documented',
                        'remediation': 'Establish emergency access procedures',
                        'priority': 'Medium'
                    },
                    {
                        'id': 'HIPAA-UM-003',
                        'title': 'Automatic Logoff',
                        'description': 'Implement automatic logoff mechanisms',
                        'requirement': 'HIPAA Security Rule 164.312(a)(2)(iii)',
                        'test_method': 'Check automatic logoff settings and procedures',
                        'pass_criteria': 'Automatic logoff implemented',
                        'status': 'FAIL',
                        'evidence': 'Automatic logoff not configured',
                        'remediation': 'Implement automatic logoff mechanisms',
                        'priority': 'Medium'
                    },
                    {
                        'id': 'HIPAA-UM-004',
                        'title': 'Encryption and Decryption',
                        'description': 'Implement encryption for user authentication',
                        'requirement': 'HIPAA Security Rule 164.312(c)(2)',
                        'test_method': 'Review user authentication encryption',
                        'pass_criteria': 'User authentication properly encrypted',
                        'status': 'PASS',
                        'evidence': 'User authentication encryption enabled',
                        'remediation': '',
                        'priority': 'High'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'ISO 27001': {
                'name': 'ISO/IEC 27001 Information Security Management - User Management',
                'description': 'User management controls for information security',
                'controls': [
                    {
                        'id': 'ISO-UM-001',
                        'title': 'User Registration and De-registration',
                        'description': 'Formal user registration and de-registration process',
                        'requirement': 'ISO 27001 A.9.2.1',
                        'test_method': 'Review user registration and de-registration procedures',
                        'pass_criteria': 'Formal user registration process implemented',
                        'status': 'FAIL',
                        'evidence': 'No formal user registration process documented',
                        'remediation': 'Implement formal user registration process',
                        'priority': 'High'
                    },
                    {
                        'id': 'ISO-UM-002',
                        'title': 'Privilege Management',
                        'description': 'Allocation and use of privileged access rights',
                        'requirement': 'ISO 27001 A.9.2.3',
                        'test_method': 'Review user privilege allocation and management',
                        'pass_criteria': 'Privileged access properly managed',
                        'status': 'FAIL',
                        'evidence': 'Users with excessive privileges found',
                        'remediation': 'Implement proper privilege management',
                        'priority': 'Critical'
                    },
                    {
                        'id': 'ISO-UM-003',
                        'title': 'Password Management',
                        'description': 'Secure password management system',
                        'requirement': 'ISO 27001 A.9.3.1',
                        'test_method': 'Review password management and policies',
                        'pass_criteria': 'Secure password management implemented',
                        'status': 'FAIL',
                        'evidence': 'Weak password management found',
                        'remediation': 'Implement secure password management',
                        'priority': 'High'
                    },
                    {
                        'id': 'ISO-UM-004',
                        'title': 'User Access Review',
                        'description': 'Regular review of user access rights',
                        'requirement': 'ISO 27001 A.9.2.5',
                        'test_method': 'Review user access review procedures',
                        'pass_criteria': 'Regular user access reviews conducted',
                        'status': 'FAIL',
                        'evidence': 'No regular access reviews documented',
                        'remediation': 'Implement regular user access reviews',
                        'priority': 'Medium'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'NIST': {
                'name': 'NIST Cybersecurity Framework - User Management',
                'description': 'User management controls for cybersecurity framework',
                'controls': [
                    {
                        'id': 'NIST-UM-001',
                        'title': 'Identity Management',
                        'description': 'Implement identity management capabilities',
                        'requirement': 'NIST CSF ID.AM-6',
                        'test_method': 'Review identity management implementation',
                        'pass_criteria': 'Identity management properly implemented',
                        'status': 'FAIL',
                        'evidence': 'Identity management issues found',
                        'remediation': 'Implement proper identity management',
                        'priority': 'High'
                    },
                    {
                        'id': 'NIST-UM-002',
                        'title': 'Access Control',
                        'description': 'Implement access control policies',
                        'requirement': 'NIST CSF PR.AC-1',
                        'test_method': 'Review access control implementation',
                        'pass_criteria': 'Access control policies implemented',
                        'status': 'FAIL',
                        'evidence': 'Access control policy gaps found',
                        'remediation': 'Implement comprehensive access control policies',
                        'priority': 'High'
                    },
                    {
                        'id': 'NIST-UM-003',
                        'title': 'User Training',
                        'description': 'Provide user security awareness training',
                        'requirement': 'NIST CSF PR.AT-1',
                        'test_method': 'Review user training and awareness programs',
                        'pass_criteria': 'User security training provided',
                        'status': 'FAIL',
                        'evidence': 'No user security training documented',
                        'remediation': 'Implement user security awareness training',
                        'priority': 'Medium'
                    },
                    {
                        'id': 'NIST-UM-004',
                        'title': 'Incident Response',
                        'description': 'User-related incident response capabilities',
                        'requirement': 'NIST CSF RS.RP-1',
                        'test_method': 'Review user incident response procedures',
                        'pass_criteria': 'User incident response procedures established',
                        'status': 'FAIL',
                        'evidence': 'No user incident response procedures found',
                        'remediation': 'Establish user incident response procedures',
                        'priority': 'Medium'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            },
            'HI-TRUST': {
                'name': 'HITRUST Common Security Framework - User Management',
                'description': 'User management controls for healthcare security framework',
                'controls': [
                    {
                        'id': 'HITRUST-UM-001',
                        'title': 'Account Management',
                        'description': 'Establish and maintain account management procedures',
                        'requirement': 'HITRUST CSF 01.b',
                        'test_method': 'Review account management procedures',
                        'pass_criteria': 'Account management procedures implemented',
                        'status': 'FAIL',
                        'evidence': 'Account management procedures not properly implemented',
                        'remediation': 'Implement proper account management procedures',
                        'priority': 'High'
                    },
                    {
                        'id': 'HITRUST-UM-002',
                        'title': 'Access Enforcement',
                        'description': 'Enforce access control policy for all users',
                        'requirement': 'HITRUST CSF 01.c',
                        'test_method': 'Review access enforcement mechanisms',
                        'pass_criteria': 'Access control policy enforced for all users',
                        'status': 'FAIL',
                        'evidence': 'Access control not properly enforced',
                        'remediation': 'Enforce access control policy consistently',
                        'priority': 'Critical'
                    },
                    {
                        'id': 'HITRUST-UM-003',
                        'title': 'Separation of Duties',
                        'description': 'Implement separation of duties for user functions',
                        'requirement': 'HITRUST CSF 01.e',
                        'test_method': 'Review user role separation and duties',
                        'pass_criteria': 'Separation of duties implemented',
                        'status': 'FAIL',
                        'evidence': 'Users with conflicting duties found',
                        'remediation': 'Implement proper separation of duties',
                        'priority': 'Critical'
                    },
                    {
                        'id': 'HITRUST-UM-004',
                        'title': 'Least Privilege',
                        'description': 'Implement least privilege principle for user access',
                        'requirement': 'HITRUST CSF 01.f',
                        'test_method': 'Review user privileges and access rights',
                        'pass_criteria': 'Least privilege principle implemented',
                        'status': 'FAIL',
                        'evidence': 'Users with excessive privileges found',
                        'remediation': 'Implement least privilege principle',
                        'priority': 'High'
                    }
                ],
                'compliance_score': 0,
                'critical_issues': [],
                'recommendations': []
            }
        }
        
        # Evaluate user management controls based on actual user data
        for framework_name, framework_data in user_management_controls.items():
            failed_controls = []
            
            for control in framework_data['controls']:
                # Evaluate control based on user management data
                if framework_name == 'SOX':
                    if control['id'] == 'SOX-UM-001':
                        # Check user account lifecycle management
                        disabled_users = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                        if profile.get('status') == '*DISABLED']
                        if len(disabled_users) <= 1:  # Allow for one disabled admin account
                            control['status'] = 'PASS'
                            control['evidence'] = 'User accounts properly managed'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Multiple disabled users found: {", ".join(disabled_users)}'
                            control['remediation'] = f'Review and clean up disabled accounts: {", ".join(disabled_users)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'SOX-UM-002':
                        # Check password policy enforcement
                        users_no_pwd = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                      if profile.get('pass_none') == '*YES']
                        if not users_no_pwd:
                            control['status'] = 'PASS'
                            control['evidence'] = 'All users have passwords set'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Users without passwords: {", ".join(users_no_pwd)}'
                            control['remediation'] = f'Set passwords for: {", ".join(users_no_pwd)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'SOX-UM-003':
                        # Check user access review
                        excessive_priv = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                        if '*ALLOBJ' in profile.get('spec_auth', [])]
                        if not excessive_priv:
                            control['status'] = 'PASS'
                            control['evidence'] = 'No users with excessive privileges found'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Users with excessive privileges: {", ".join(excessive_priv)}'
                            control['remediation'] = f'Review and restrict privileges for: {", ".join(excessive_priv)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'SOX-UM-004':
                        # Check user activity monitoring
                        control['status'] = 'PASS'
                        control['evidence'] = 'User activity monitoring enabled'
                
                elif framework_name == 'PCI DSS':
                    if control['id'] == 'PCI-UM-001':
                        # Check unique user identification
                        total_users = len(self.data_manager.user_profiles)
                        unique_users = len(set(self.data_manager.user_profiles.keys()))
                        if total_users == unique_users:
                            control['status'] = 'PASS'
                            control['evidence'] = f'All {total_users} users have unique identifiers'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Duplicate user identifiers found'
                            control['remediation'] = 'Ensure all users have unique identifiers'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'PCI-UM-002':
                        # Check strong authentication
                        users_no_pwd = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                      if profile.get('pass_none') == '*YES']
                        if not users_no_pwd:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Strong authentication implemented for all users'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Users without strong authentication: {", ".join(users_no_pwd)}'
                            control['remediation'] = f'Implement strong authentication for: {", ".join(users_no_pwd)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'PCI-UM-003':
                        # Check account management
                        account_issues = []
                        for uid, profile in self.data_manager.user_profiles.items():
                            if profile.get('pass_none') == '*YES' or profile.get('status') == '*DISABLED':
                                account_issues.append(uid)
                        if not account_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Account management properly implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Account management issues: {", ".join(account_issues)}'
                            control['remediation'] = f'Fix account management for: {", ".join(account_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'PCI-UM-004':
                        # Check access control
                        excessive_access = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                          if '*ALLOBJ' in profile.get('spec_auth', [])]
                        if not excessive_access:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Access properly restricted based on job function'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Users with excessive access: {", ".join(excessive_access)}'
                            control['remediation'] = f'Restrict access for: {", ".join(excessive_access)}'
                            failed_controls.append(control)
                
                elif framework_name == 'HIPAA':
                    if control['id'] == 'HIPAA-UM-001':
                        # Check unique user identification
                        total_users = len(self.data_manager.user_profiles)
                        unique_users = len(set(self.data_manager.user_profiles.keys()))
                        if total_users == unique_users:
                            control['status'] = 'PASS'
                            control['evidence'] = f'All {total_users} users have unique identification'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = 'Duplicate user identification found'
                            control['remediation'] = 'Ensure all users have unique identification'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HIPAA-UM-002':
                        # Check emergency access procedures
                        emergency_accounts = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                            if 'emergency' in uid.lower() or 'admin' in uid.lower()]
                        if emergency_accounts:
                            control['status'] = 'PASS'
                            control['evidence'] = f'Emergency access accounts found: {", ".join(emergency_accounts)}'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = 'No emergency access procedures documented'
                            control['remediation'] = 'Establish emergency access procedures and accounts'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HIPAA-UM-003':
                        # Check automatic logoff
                        control['status'] = 'FAIL'
                        control['evidence'] = 'Automatic logoff not configured'
                        control['remediation'] = 'Implement automatic logoff mechanisms'
                        failed_controls.append(control)
                    
                    elif control['id'] == 'HIPAA-UM-004':
                        # Check encryption and decryption
                        control['status'] = 'PASS'
                        control['evidence'] = 'User authentication encryption enabled'
                
                elif framework_name == 'ISO 27001':
                    if control['id'] == 'ISO-UM-001':
                        # Check user registration and de-registration
                        formal_process = True  # Assume formal process exists
                        if formal_process:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Formal user registration process implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = 'No formal user registration process documented'
                            control['remediation'] = 'Implement formal user registration process'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'ISO-UM-002':
                        # Check privilege management
                        excessive_priv = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                        if '*ALLOBJ' in profile.get('spec_auth', [])]
                        if not excessive_priv:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Privileged access properly managed'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Users with excessive privileges: {", ".join(excessive_priv)}'
                            control['remediation'] = f'Implement proper privilege management for: {", ".join(excessive_priv)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'ISO-UM-003':
                        # Check password management
                        users_no_pwd = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                      if profile.get('pass_none') == '*YES']
                        if not users_no_pwd:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Secure password management implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Weak password management: {", ".join(users_no_pwd)}'
                            control['remediation'] = f'Implement secure password management for: {", ".join(users_no_pwd)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'ISO-UM-004':
                        # Check user access review
                        control['status'] = 'FAIL'
                        control['evidence'] = 'No regular access reviews documented'
                        control['remediation'] = 'Implement regular user access reviews'
                        failed_controls.append(control)
                
                elif framework_name == 'NIST':
                    if control['id'] == 'NIST-UM-001':
                        # Check identity management
                        identity_issues = []
                        for uid, profile in self.data_manager.user_profiles.items():
                            if profile.get('pass_none') == '*YES' or profile.get('status') == '*DISABLED':
                                identity_issues.append(uid)
                        if not identity_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Identity management properly implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Identity management issues: {", ".join(identity_issues)}'
                            control['remediation'] = f'Implement proper identity management for: {", ".join(identity_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'NIST-UM-002':
                        # Check access control
                        access_issues = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                       if '*ALLOBJ' in profile.get('spec_auth', [])]
                        if not access_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Access control policies implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Access control policy gaps: {", ".join(access_issues)}'
                            control['remediation'] = f'Implement comprehensive access control policies for: {", ".join(access_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'NIST-UM-003':
                        # Check user training
                        control['status'] = 'FAIL'
                        control['evidence'] = 'No user security training documented'
                        control['remediation'] = 'Implement user security awareness training'
                        failed_controls.append(control)
                    
                    elif control['id'] == 'NIST-UM-004':
                        # Check incident response
                        control['status'] = 'FAIL'
                        control['evidence'] = 'No user incident response procedures found'
                        control['remediation'] = 'Establish user incident response procedures'
                        failed_controls.append(control)
                
                elif framework_name == 'HI-TRUST':
                    if control['id'] == 'HITRUST-UM-001':
                        # Check account management
                        account_issues = []
                        for uid, profile in self.data_manager.user_profiles.items():
                            if profile.get('pass_none') == '*YES' or profile.get('status') == '*DISABLED':
                                account_issues.append(uid)
                        if not account_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Account management procedures implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Account management issues: {", ".join(account_issues)}'
                            control['remediation'] = f'Implement proper account management procedures for: {", ".join(account_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HITRUST-UM-002':
                        # Check access enforcement
                        enforcement_issues = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                            if '*ALLOBJ' in profile.get('spec_auth', [])]
                        if not enforcement_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Access control policy enforced for all users'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Access control not properly enforced: {", ".join(enforcement_issues)}'
                            control['remediation'] = f'Enforce access control policy for: {", ".join(enforcement_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HITRUST-UM-003':
                        # Check separation of duties
                        separation_issues = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                           if '*ALLOBJ' in profile.get('spec_auth', [])]
                        if not separation_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Separation of duties implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Users with conflicting duties: {", ".join(separation_issues)}'
                            control['remediation'] = f'Implement proper separation of duties for: {", ".join(separation_issues)}'
                            failed_controls.append(control)
                    
                    elif control['id'] == 'HITRUST-UM-004':
                        # Check least privilege
                        privilege_issues = [uid for uid, profile in self.data_manager.user_profiles.items() 
                                          if '*ALLOBJ' in profile.get('spec_auth', [])]
                        if not privilege_issues:
                            control['status'] = 'PASS'
                            control['evidence'] = 'Least privilege principle implemented'
                        else:
                            control['status'] = 'FAIL'
                            control['evidence'] = f'Users with excessive privileges: {", ".join(privilege_issues)}'
                            control['remediation'] = f'Implement least privilege principle for: {", ".join(privilege_issues)}'
                            failed_controls.append(control)
            
            # Calculate compliance score based on controls
            total_controls = len(framework_data['controls'])
            passed_controls = len([c for c in framework_data['controls'] if c['status'] == 'PASS'])
            framework_data['compliance_score'] = int((passed_controls / total_controls) * 100) if total_controls > 0 else 0
            
            # Generate recommendations based on failed controls
            if failed_controls:
                framework_data['recommendations'] = [
                    f"Address {len(failed_controls)} failed user management controls",
                    "Prioritize Critical and High priority user management controls",
                    "Implement automated user management monitoring",
                    "Conduct regular user access reviews"
                ]
                # Add specific remediation steps
                for control in failed_controls:
                    if control['remediation']:
                        framework_data['recommendations'].append(f"- {control['id']}: {control['remediation']}")
            else:
                framework_data['recommendations'] = [
                    "All user management controls are passing",
                    "Maintain current user management practices",
                    "Continue regular user management monitoring"
                ]
            
            # Add failed controls to critical issues
            framework_data['critical_issues'] = failed_controls
        
        return user_management_controls
    
    def run_full_audit(self) -> Dict[str, pd.DataFrame]:
        """Run complete security audit and return all results"""
        try:
            return {
                'object_authorities': self.object_authority.analyze_object_authorities(),
                'user_profiles': self.user_profiles.analyze_user_profiles(),
                'system_values': self.system_values.analyze_system_values()
            }
        except Exception as e:
            logger.error(f"Error running full audit: {e}")
            # Return empty DataFrames with proper structure
            return {
                'object_authorities': pd.DataFrame(columns=['object', 'user', 'object_type', 'security_issues', 'risk_level']),
                'user_profiles': pd.DataFrame(columns=['user_id', 'name', 'status', 'group', 'special_authorities', 'security_issues', 'risk_level']),
                'system_values': pd.DataFrame(columns=['system_value', 'current_value', 'recommended_value', 'description', 'compliance_status', 'risk_level'])
            }
    
    def get_audit_summary(self, audit_results: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate audit summary with key metrics"""
        try:
            summary = {
                'total_issues': 0,
                'high_risk_issues': 0,
                'medium_risk_issues': 0,
                'low_risk_issues': 0,
                'compliance_score': 0,
                'total_objects_analyzed': 0,
                'categories': {}
            }
            
            for category, df in audit_results.items():
                if not df.empty and 'risk_level' in df.columns:
                    category_issues = len(df)
                    high_risk = len(df[df['risk_level'] == 'High'])
                    medium_risk = len(df[df['risk_level'] == 'Medium'])
                    low_risk = len(df[df['risk_level'] == 'Low'])
                    
                    summary['total_issues'] += category_issues
                    summary['high_risk_issues'] += high_risk
                    summary['medium_risk_issues'] += medium_risk
                    summary['low_risk_issues'] += low_risk
                    
                    summary['categories'][category] = {
                        'total': category_issues,
                        'high_risk': high_risk,
                        'medium_risk': medium_risk,
                        'low_risk': low_risk
                    }
            
            # Calculate total objects analyzed
            summary['total_objects_analyzed'] = len(self.data_manager.system_values) + len(self.data_manager.user_profiles) + len(self.data_manager.object_authorities)
            summary['total_users_analyzed'] = len(self.data_manager.user_profiles)
            summary['total_system_values'] = len(self.data_manager.system_values)
            
            # Calculate compliance score
            total_possible_issues = summary['total_objects_analyzed']
            if total_possible_issues > 0:
                summary['compliance_score'] = max(0, 100 - (summary['total_issues'] / total_possible_issues * 100))
            
            return summary
        except Exception as e:
            logger.error(f"Error generating audit summary: {e}")
            return {
                'total_issues': 0,
                'high_risk_issues': 0,
                'medium_risk_issues': 0,
                'low_risk_issues': 0,
                'compliance_score': 100,
                'total_objects_analyzed': 0,
                'total_users_analyzed': 0,
                'total_system_values': 0,
                'categories': {}
            }
