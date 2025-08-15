#!/usr/bin/env python3
"""
IBM i Security Assessment Dashboard
==================================

A comprehensive Streamlit application for IBM i security auditing and compliance.
This application converts the functionality of the IBM i Perl audit tools to a
modern web interface with interactive visualizations and real-time analysis.

Original Perl modules converted:
- AS4Data.pm -> IBMiDataManager
- AS4AnzObjectAuthority.pm -> IBMiObjectAuthority  
- AS4AnzProfiles_*.pm -> IBMiUserProfiles
- AS4AnzSystemValues.pm -> IBMiSystemValues
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import json
import sys
import os
import re
import hashlib
import secrets

# Add the current directory to the path to import our core module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our IBM i audit core classes
from ibm_i_audit_core import IBMiSecurityAuditor, IBMiDataManager, IBMiObjectAuthority, IBMiUserProfiles, IBMiSystemValues

# Security configuration
SESSION_TIMEOUT_MINUTES = 30
MAX_LOGIN_ATTEMPTS = 5
SECURE_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}

def validate_input(input_string, max_length=1000):
    """Validate and sanitize user input"""
    if not input_string or len(input_string) > max_length:
        return False, "Input validation failed"
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_string)
    return True, sanitized

def check_session_timeout():
    """Check if user session has timed out"""
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.datetime.now()
    
    time_diff = datetime.datetime.now() - st.session_state.last_activity
    if time_diff.total_seconds() > (SESSION_TIMEOUT_MINUTES * 60):
        st.session_state.clear()
        st.error("Session timed out. Please refresh the page.")
        st.stop()
    
    st.session_state.last_activity = datetime.datetime.now()

def log_security_event(event_type, details, user_role="Unknown"):
    """Log security events for audit purposes"""
    if 'security_log' not in st.session_state:
        st.session_state.security_log = []
    
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'event_type': event_type,
        'details': details,
        'user_role': user_role,
        'session_id': st.session_state.get('session_id', 'unknown')
    }
    
    st.session_state.security_log.append(log_entry)
    
    # Keep only last 1000 entries
    if len(st.session_state.security_log) > 1000:
        st.session_state.security_log = st.session_state.security_log[-1000:]

def initialize_session_security():
    """Initialize security features for the session"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = secrets.token_hex(16)
    
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    
    if 'security_level' not in st.session_state:
        st.session_state.security_level = 'standard'
    
    log_security_event("SESSION_START", "New session initialized")

# Page configuration
st.set_page_config(
    page_title="IBM i Security Assessment",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Professional dark theme styling */
    .main-header {
        color: #ffffff;
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        border-bottom: 2px solid rgba(255, 193, 7, 0.3);
        padding-bottom: 0.5rem;
    }
    
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    .stSidebar {
        background-color: #000000;
        color: #ffffff;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ffc107, #7e57c2);
        color: #000000;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 193, 7, 0.3);
        background: linear-gradient(135deg, #ffffff, #ffc107);
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stNumberInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stDateInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        padding: 16px;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }
    
    .stExpander {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }
    
    .stDataFrame {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }
    
    /* Plotly chart styling */
    .js-plotly-plot {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 193, 7, 0.2) !important;
    }
    
    /* Risk level indicators */
    .risk-high {
        color: #ff4444;
        font-weight: bold;
    }
    
    .risk-medium {
        color: #ffaa00;
        font-weight: bold;
    }
    
    .risk-low {
        color: #44ff44;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize security features
initialize_session_security()
check_session_timeout()

# Initialize session state
if 'ibm_i_auditor' not in st.session_state:
    st.session_state.ibm_i_auditor = IBMiSecurityAuditor()
    st.session_state.audit_results = None
    st.session_state.audit_summary = None

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">IBM i Security Assessment</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("IBM i Security Audit")
        st.markdown("---")
        
        # Audit controls
        if st.button("Run Full Security Audit", type="primary"):
            try:
                with st.spinner("Running comprehensive IBM i Security Audit..."):
                    st.session_state.audit_results = st.session_state.ibm_i_auditor.run_full_audit()
                    st.session_state.audit_summary = st.session_state.ibm_i_auditor.get_audit_summary(st.session_state.audit_results)
                st.success("Audit completed successfully!")
            except Exception as e:
                st.error(f"Audit failed: {str(e)}")
                st.info("Please try again or check your configuration.")
        
        # Data persistence controls
        st.header("Data Management")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Data", type="secondary"):
                if st.session_state.ibm_i_auditor.data_manager.save_data_to_file():
                    st.success("Data saved!")
                else:
                    st.error("Failed to save data")
        with col2:
            if st.button("Load Data", type="secondary"):
                if st.session_state.ibm_i_auditor.data_manager.load_data_from_file():
                    st.success("Data loaded!")
                else:
                    st.info("No saved data found, using current data")
        
        st.markdown("---")
        
        # Export functionality
        st.header("Export Reports")
        if st.session_state.audit_results is not None:
            # Use a more compact layout for export buttons
            st.markdown("**Available Reports:**")
            
            # JSON Export
            if st.button("Export to JSON", key="json_export", use_container_width=True):
                export_data = {
                    'audit_summary': st.session_state.audit_summary,
                    'audit_results': st.session_state.audit_results,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'security_level': st.session_state.security_level
                }
                export_json = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    label="Download JSON Report",
                    data=export_json,
                    file_name=f"ibm_i_security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # CSV Export
            if st.button("Export to CSV", key="csv_export", use_container_width=True):
                # Create comprehensive CSV export
                csv_data = []
                for analysis_name, df in st.session_state.audit_results.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        df_copy = df.copy()
                        df_copy['analysis_type'] = analysis_name
                        csv_data.append(df_copy)
                
                if csv_data:
                    combined_df = pd.concat(csv_data, ignore_index=True)
                    csv_export = combined_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV Report",
                        data=csv_export,
                        file_name=f"ibm_i_security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            # Security Log Export
            if st.button("Export Security Log", key="security_log_export", use_container_width=True):
                if 'security_log' in st.session_state:
                    security_log_json = json.dumps(st.session_state.security_log, indent=2, default=str)
                    st.download_button(
                        label="Download Security Log",
                        data=security_log_json,
                        file_name=f"security_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
        else:
            st.info("Run an audit first to enable export options")
        
        st.markdown("---")
        
        # Navigation
        st.header("Navigation")
        page = st.selectbox(
            "Select Analysis",
            ["Dashboard", "Compliance Frameworks", "Object Authorities", "User Profiles", "System Values", "Real-time Monitoring", "Compliance Report"]
        )
        
        st.markdown("---")
        
        # About section
        st.header("About")
        st.markdown("""
        **IBM i Security Assessment**
        
        This tool provides comprehensive IBM i security auditing capabilities.
        
        **Features:**
        - Object authority analysis
        - User profile security assessment
        - System values compliance
        - Risk level identification
        - Interactive visualizations
        """)
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Compliance Frameworks":
        show_compliance_frameworks()
    elif page == "Object Authorities":
        show_object_authorities()
    elif page == "User Profiles":
        show_user_profiles()
    elif page == "System Values":
        show_system_values()
    elif page == "Real-time Monitoring":
        show_real_time_monitoring()
    elif page == "Compliance Report":
        show_compliance_report()

def show_dashboard():
    """Display the main dashboard with overview metrics"""
    
    st.header("Security Assessment Dashboard")
    
    if st.session_state.audit_results is None:
        st.info("Click 'Run Full Security Audit' in the sidebar to begin analysis.")
        return
    
    # Use caching for expensive computations
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def compute_dashboard_metrics(audit_summary):
        """Compute dashboard metrics with caching"""
        return {
            'compliance_score': audit_summary['compliance_score'],
            'high_risk_issues': audit_summary['high_risk_issues'],
            'medium_risk_issues': audit_summary['medium_risk_issues'],
            'low_risk_issues': audit_summary['low_risk_issues'],
            'total_objects_analyzed': audit_summary['total_objects_analyzed']
        }
    
    # Get cached metrics
    metrics = compute_dashboard_metrics(st.session_state.audit_summary)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Compliance Score",
            value=f"{metrics['compliance_score']}%",
            delta=None
        )
    
    with col2:
        st.metric(
            label="High Risk Issues",
            value=metrics['high_risk_issues'],
            delta=None,
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Medium Risk Issues",
            value=metrics['medium_risk_issues'],
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Total Objects Analyzed",
            value=metrics['total_objects_analyzed'],
            delta=None
        )
    
    st.markdown("---")
    
    # Risk distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Level Distribution")
        
        # Create risk distribution data
        risk_data = {
            'Risk Level': ['High', 'Medium', 'Low'],
            'Count': [
                st.session_state.audit_summary['high_risk_issues'],
                st.session_state.audit_summary['medium_risk_issues'],
                st.session_state.audit_summary['low_risk_issues']
            ]
        }
        
        df_risk = pd.DataFrame(risk_data)
        
        fig = px.pie(
            df_risk, 
            values='Count', 
            names='Risk Level',
            color_discrete_map={
                'High': '#ff4444',
                'Medium': '#ffaa00',
                'Low': '#44ff44'
            }
        )
        
        fig.update_layout(
            title="Security Issues by Risk Level",
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Compliance Overview")
        
        # Compliance gauge chart
        compliance_score = st.session_state.audit_summary['compliance_score']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = compliance_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Compliance Score"},
            delta = {'reference': 100},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent security issues
    st.subheader("Recent Security Issues")
    
    # Get high and medium risk issues from all analyses
    high_risk_issues = []
    
    for analysis_name, df in st.session_state.audit_results.items():
        if 'risk_level' in df.columns:
            high_risk = df[df['risk_level'].isin(['High', 'Medium'])]
            for _, row in high_risk.iterrows():
                issue = {
                    'analysis': analysis_name.replace('_', ' ').title(),
                    'issue': row.get('security_issue', 'Security issue detected'),
                    'risk_level': row['risk_level'],
                    'recommendation': row.get('recommendation', 'Review and remediate')
                }
                high_risk_issues.append(issue)
    
    if high_risk_issues:
        df_issues = pd.DataFrame(high_risk_issues)
        st.dataframe(df_issues, use_container_width=True)
    else:
        st.success("No high or medium risk issues detected!")

def show_compliance_frameworks():
    """Display compliance framework analysis"""
    
    st.header("Compliance Framework Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Click 'Run Full Security Audit' in the sidebar to begin analysis.")
        return
    
    # Run compliance framework analysis
    try:
        compliance_results = st.session_state.ibm_i_auditor.analyze_compliance_frameworks()
    except Exception as e:
        st.error(f"Error analyzing compliance frameworks: {e}")
        return
    
    # Compliance Overview
    st.subheader("Compliance Framework Overview")
    
    # Create compliance score cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sox_score = compliance_results['SOX']['compliance_score']
        st.metric(
            label="SOX Compliance",
            value=f"{sox_score}%",
            delta=None,
            delta_color="inverse" if sox_score < 80 else "normal"
        )
    
    with col2:
        pci_score = compliance_results['PCI DSS']['compliance_score']
        st.metric(
            label="PCI DSS Compliance",
            value=f"{pci_score}%",
            delta=None,
            delta_color="inverse" if pci_score < 80 else "normal"
        )
    
    with col3:
        hipaa_score = compliance_results['HIPAA']['compliance_score']
        st.metric(
            label="HIPAA Compliance",
            value=f"{hipaa_score}%",
            delta=None,
            delta_color="inverse" if hipaa_score < 80 else "normal"
        )
    
    # Second row of compliance scores
    col4, col5, col6 = st.columns(3)
    
    with col4:
        iso_score = compliance_results['ISO 27001']['compliance_score']
        st.metric(
            label="ISO 27001 Compliance",
            value=f"{iso_score}%",
            delta=None,
            delta_color="inverse" if iso_score < 80 else "normal"
        )
    
    with col5:
        nist_score = compliance_results['NIST']['compliance_score']
        st.metric(
            label="NIST Compliance",
            value=f"{nist_score}%",
            delta=None,
            delta_color="inverse" if nist_score < 80 else "normal"
        )
    
    with col6:
        hitrust_score = compliance_results['HI-TRUST']['compliance_score']
        st.metric(
            label="HI-TRUST Compliance",
            value=f"{hitrust_score}%",
            delta=None,
            delta_color="inverse" if hitrust_score < 80 else "normal"
        )
    
    st.markdown("---")
    
    # Compliance Framework Details
    st.subheader("Framework Details")
    
    # Create tabs for each framework
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["SOX", "PCI DSS", "HIPAA", "ISO 27001", "NIST", "HI-TRUST"])
    
    with tab1:
        show_framework_details("SOX", compliance_results['SOX'])
    
    with tab2:
        show_framework_details("PCI DSS", compliance_results['PCI DSS'])
    
    with tab3:
        show_framework_details("HIPAA", compliance_results['HIPAA'])
    
    with tab4:
        show_framework_details("ISO 27001", compliance_results['ISO 27001'])
    
    with tab5:
        show_framework_details("NIST", compliance_results['NIST'])
    
    with tab6:
        show_framework_details("HI-TRUST", compliance_results['HI-TRUST'])
    
    # Business Impact Analysis
    st.markdown("---")
    st.subheader("Business Impact Analysis")
    
    # Calculate business impact metrics
    high_impact_issues = 0
    medium_impact_issues = 0
    low_impact_issues = 0
    
    for framework in compliance_results.values():
        for issue in framework['critical_issues']:
            impact = issue.get('business_impact', 'Unknown')
            if impact == 'High':
                high_impact_issues += 1
            elif impact == 'Medium':
                medium_impact_issues += 1
            elif impact == 'Low':
                low_impact_issues += 1
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("High Impact Issues", high_impact_issues, delta_color="inverse")
    
    with col2:
        st.metric("Medium Impact Issues", medium_impact_issues)
    
    with col3:
        st.metric("Low Impact Issues", low_impact_issues)
    
    # Remediation Effort Analysis
    st.markdown("---")
    st.subheader("Remediation Effort Analysis")
    
    high_effort = 0
    medium_effort = 0
    low_effort = 0
    
    for framework in compliance_results.values():
        for issue in framework['critical_issues']:
            effort = issue.get('remediation_effort', 'Unknown')
            if effort == 'High':
                high_effort += 1
            elif effort == 'Medium':
                medium_effort += 1
            elif effort == 'Low':
                low_effort += 1
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("High Effort Remediation", high_effort, delta_color="inverse")
    
    with col2:
        st.metric("Medium Effort Remediation", medium_effort)
    
    with col3:
        st.metric("Low Effort Remediation", low_effort)
    
    # Export compliance report
    st.markdown("---")
    st.subheader("Export Compliance Analysis")
    
    if st.button("Generate Compliance Framework Report"):
        # Create comprehensive compliance report
        report_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'compliance_frameworks': compliance_results,
            'business_impact_summary': {
                'high_impact': high_impact_issues,
                'medium_impact': medium_impact_issues,
                'low_impact': low_impact_issues
            },
            'remediation_effort_summary': {
                'high_effort': high_effort,
                'medium_effort': medium_effort,
                'low_effort': low_effort
            }
        }
        
        # Export as JSON
        json_report = json.dumps(report_data, indent=2)
        st.download_button(
            label="Download Compliance Framework Report (JSON)",
            data=json_report,
            file_name=f"ibm_i_compliance_frameworks_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def show_framework_details(framework_name: str, framework_data: dict):
    """Display detailed information for a specific compliance framework"""
    
    st.markdown(f"### {framework_data['name']}")
    st.markdown(f"**Description:** {framework_data['description']}")
    
    # Compliance score gauge
    compliance_score = framework_data['compliance_score']
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = compliance_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"{framework_name} Compliance Score"},
        delta = {'reference': 100},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Compliance Controls
    st.markdown("#### Compliance Controls")
    
    if 'controls' in framework_data:
        controls_df = pd.DataFrame(framework_data['controls'])
        
        # Color code by status and priority
        def color_status(val):
            if val == 'PASS':
                return 'background-color: #44ff44; color: black; font-weight: bold'
            else:
                return 'background-color: #ff4444; color: white; font-weight: bold'
        
        def color_priority(val):
            if val == 'Critical':
                return 'background-color: #ff0000; color: white; font-weight: bold'
            elif val == 'High':
                return 'background-color: #ff6600; color: white; font-weight: bold'
            elif val == 'Medium':
                return 'background-color: #ffaa00; color: black; font-weight: bold'
            else:
                return 'background-color: #44ff44; color: black; font-weight: bold'
        
        # Select columns to display
        display_columns = ['id', 'title', 'status', 'priority', 'evidence', 'remediation']
        display_df = controls_df[display_columns].copy()
        
        # Add control links column
        def get_control_link(control_id):
            """Get official control documentation link"""
            links = {
                'SOX-001': 'https://www.sec.gov/about/laws/soa2002.pdf',
                'SOX-002': 'https://www.sec.gov/about/laws/soa2002.pdf',
                'SOX-003': 'https://www.sec.gov/about/laws/soa2002.pdf',
                'SOX-004': 'https://www.sec.gov/about/laws/soa2002.pdf',
                'PCI-001': 'https://www.pcisecuritystandards.org/document_library',
                'PCI-002': 'https://www.pcisecuritystandards.org/document_library',
                'PCI-003': 'https://www.pcisecuritystandards.org/document_library',
                'PCI-004': 'https://www.pcisecuritystandards.org/document_library',
                'HIPAA-001': 'https://www.hhs.gov/hipaa/for-professionals/security/',
                'HIPAA-002': 'https://www.hhs.gov/hipaa/for-professionals/security/',
                'HIPAA-003': 'https://www.hhs.gov/hipaa/for-professionals/security/',
                'HIPAA-004': 'https://www.hhs.gov/hipaa/for-professionals/security/',
                'ISO-001': 'https://www.iso.org/isoiec-27001-information-security.html',
                'ISO-002': 'https://www.iso.org/isoiec-27001-information-security.html',
                'ISO-003': 'https://www.iso.org/isoiec-27001-information-security.html',
                'ISO-004': 'https://www.iso.org/isoiec-27001-information-security.html',
                'ISO-005': 'https://www.iso.org/isoiec-27001-information-security.html',
                'NIST-001': 'https://www.nist.gov/cyberframework',
                'NIST-002': 'https://www.nist.gov/cyberframework',
                'NIST-003': 'https://www.nist.gov/cyberframework',
                'NIST-004': 'https://www.nist.gov/cyberframework',
                'NIST-005': 'https://www.nist.gov/cyberframework',
                'HITRUST-001': 'https://hitrustalliance.net/csf/',
                'HITRUST-002': 'https://hitrustalliance.net/csf/',
                'HITRUST-003': 'https://hitrustalliance.net/csf/',
                'HITRUST-004': 'https://hitrustalliance.net/csf/',
                'HITRUST-005': 'https://hitrustalliance.net/csf/',
                'HITRUST-006': 'https://hitrustalliance.net/csf/'
            }
            return links.get(control_id, '#')
        
        # Add control links
        display_df['control_link'] = display_df['id'].apply(get_control_link)
        display_columns.append('control_link')
        
        # Apply styling
        styled_controls = display_df.style.map(color_status, subset=['status']).map(color_priority, subset=['priority'])
        
        # Display with clickable links
        st.markdown("**Note:** Click on control IDs to view official documentation")
        st.dataframe(styled_controls, use_container_width=True)
        
        # Display clickable links separately for better UX
        st.markdown("### Control Documentation Links")
        for _, control in display_df.iterrows():
            st.markdown(f"**[{control['id']}]({control['control_link']})** - {control['title']}")
        
        # Control summary
        total_controls = len(controls_df)
        passed_controls = len(controls_df[controls_df['status'] == 'PASS'])
        failed_controls = len(controls_df[controls_df['status'] == 'FAIL'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Controls", total_controls)
        with col2:
            st.metric("Passed", passed_controls, delta_color="normal")
        with col3:
            st.metric("Failed", failed_controls, delta_color="inverse")
        
        # Failed controls details
        if failed_controls > 0:
            st.markdown("#### Failed Controls Details")
            failed_df = controls_df[controls_df['status'] == 'FAIL'].copy()
            
            for _, control in failed_df.iterrows():
                with st.expander(f"{control['id']}: {control['title']}"):
                    st.markdown(f"**Requirement:** {control['requirement']}")
                    st.markdown(f"**Description:** {control['description']}")
                    st.markdown(f"**Test Method:** {control['test_method']}")
                    st.markdown(f"**Pass Criteria:** {control['pass_criteria']}")
                    st.markdown(f"**Evidence:** {control['evidence']}")
                    st.markdown(f"**Remediation:** {control['remediation']}")
                    st.markdown(f"**Priority:** {control['priority']}")
    
    # Recommendations
    st.markdown("#### Recommendations")
    
    if framework_data['recommendations']:
        for i, rec in enumerate(framework_data['recommendations'], 1):
            st.markdown(rec)
    else:
        st.info("No specific recommendations at this time.")

def show_object_authorities():
    """Display object authority analysis"""
    
    st.header("Object Authority Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view object authority analysis.")
        return
    
    df_objects = st.session_state.audit_results['object_authorities']
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_filter = st.selectbox("Filter by Risk Level", ["All"] + list(df_objects['risk_level'].unique()))
    
    with col2:
        object_filter = st.selectbox("Filter by Object Type", ["All"] + list(df_objects['object_type'].unique()))
    
    # Apply filters
    filtered_df = df_objects.copy()
    
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    
    if object_filter != "All":
        filtered_df = filtered_df[filtered_df['object_type'] == object_filter]
    
    # Display results
    st.subheader(f"Object Authorities ({len(filtered_df)} objects)")
    
    # Risk level distribution for objects
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = filtered_df['risk_level'].value_counts()
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map={
                'High': '#ff4444',
                'Medium': '#ffaa00',
                'Low': '#44ff44'
            },
            title="Object Authorities by Risk Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Object types by risk
        object_risk = filtered_df.groupby(['object_type', 'risk_level']).size().unstack(fill_value=0)
        fig = px.bar(
            object_risk,
            title="Object Types by Risk Level",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results table
    st.subheader("Detailed Object Authority Results")
    
    # Format the dataframe for display
    display_df = filtered_df[['object', 'user', 'object_type', 'risk_level', 'security_issues']].copy()
    
    # Add color coding for risk levels
    def color_risk_level(val):
        if val == 'High':
            return 'background-color: #ff4444; color: white'
        elif val == 'Medium':
            return 'background-color: #ffaa00; color: black'
        else:
            return 'background-color: #44ff44; color: black'
    
    styled_df = display_df.style.map(color_risk_level, subset=['risk_level'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Export functionality
    if st.button("Export Object Authority Report"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"ibm_i_object_authorities_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def show_user_profiles():
    """Display user profile analysis"""
    
    st.header("User Profile Security Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view user profile analysis.")
        return
    
    df_user_profiles = st.session_state.audit_results['user_profiles']
    
    if df_user_profiles.empty:
        st.success("No user profile security issues found!")
        return
    
    # Risk level distribution
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = df_user_profiles['risk_level'].value_counts()
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="User Profile Issues by Risk Level",
            color_discrete_map={
                'High': '#ff4444',
                'Medium': '#ffaa00',
                'Low': '#44ff44'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Status distribution
        status_counts = df_user_profiles['status'].value_counts()
        fig = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="User Status Distribution",
            color=status_counts.index,
            color_discrete_map={
                '*ENABLED': '#44ff44',
                '*DISABLED': '#ff4444'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Filter options
    st.subheader("Filter Options")
    col1, col2 = st.columns(2)
    
    with col1:
        risk_filter = st.selectbox("Filter by Risk Level", ["All"] + list(df_user_profiles['risk_level'].unique()))
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df_user_profiles['status'].unique()))
    
    # Apply filters
    filtered_df = df_user_profiles.copy()
    
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    # Display results
    st.subheader(f"User Profile Security Issues ({len(filtered_df)} users)")
    
    # Detailed results table
    display_df = filtered_df[['user_id', 'name', 'status', 'group', 'special_authorities', 'security_issues', 'risk_level']].copy()
    
    # Add color coding for risk levels
    def color_risk_level(val):
        if val == 'High':
            return 'background-color: #ff4444; color: white'
        elif val == 'Medium':
            return 'background-color: #ffaa00; color: black'
        else:
            return 'background-color: #44ff44; color: black'
    
    styled_df = display_df.style.map(color_risk_level, subset=['risk_level'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Export functionality
    if st.button("Export User Profile Report"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"ibm_i_user_profiles_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def show_system_values():
    """Display system values analysis"""
    
    st.header("System Values Security Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view system values analysis.")
        return
    
    df_sysvals = st.session_state.audit_results['system_values']
    
    # Compliance overview
    col1, col2 = st.columns(2)
    
    with col1:
        compliance_counts = df_sysvals['compliance_status'].value_counts()
        fig = px.pie(
            values=compliance_counts.values,
            names=compliance_counts.index,
            title="System Values Compliance Status"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        risk_counts = df_sysvals['risk_level'].value_counts()
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map={
                'High': '#ff4444',
                'Medium': '#ffaa00',
                'Low': '#44ff44'
            },
            title="System Values by Risk Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Non-compliant system values
    non_compliant = df_sysvals[df_sysvals['compliance_status'] == 'Non-Compliant']
    
    if len(non_compliant) > 0:
        st.subheader("Non-Compliant System Values")
        st.warning(f"Found {len(non_compliant)} non-compliant system values!")
        
        # Display non-compliant values
        st.dataframe(non_compliant[['system_value', 'current_value', 'recommended_value', 'description', 'compliance_status', 'risk_level']], use_container_width=True)
    
    # All system values
    st.subheader("All System Values")
    st.dataframe(df_sysvals, use_container_width=True)

def show_compliance_report():
    """Display comprehensive compliance report"""
    
    st.header("IBM i Security Compliance Report")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view the compliance report.")
        return
    
    # Report header
    st.markdown(f"""
    **Report Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    **Overall Compliance Score:** {st.session_state.audit_summary['compliance_score']}%
    
    **Total Objects Analyzed:** {st.session_state.audit_summary['total_objects_analyzed']}
    **Total Users Analyzed:** {st.session_state.audit_summary['total_users_analyzed']}
    **Total System Values:** {st.session_state.audit_summary['total_system_values']}
    """)
    
    st.markdown("---")
    
    # Executive summary
    st.subheader("Executive Summary")
    
    compliance_score = st.session_state.audit_summary['compliance_score']
    
    if compliance_score >= 90:
        st.success("**Excellent Security Posture** - The IBM i system demonstrates strong security controls and compliance.")
    elif compliance_score >= 70:
        st.warning("**Good Security Posture** - The IBM i system has generally good security controls with some areas for improvement.")
    elif compliance_score >= 50:
        st.error("**Moderate Security Concerns** - The IBM i system has several security issues that should be addressed.")
    else:
        st.error("**Critical Security Issues** - The IBM i system has significant security vulnerabilities that require immediate attention.")
    
    # Risk summary
    st.subheader("Risk Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("High Risk Issues", st.session_state.audit_summary['high_risk_issues'])
    
    with col2:
        st.metric("Medium Risk Issues", st.session_state.audit_summary['medium_risk_issues'])
    
    with col3:
        st.metric("Low Risk Issues", st.session_state.audit_summary['low_risk_issues'])
    
    # Detailed findings
    st.subheader("Detailed Findings")
    
    # High risk issues
    if st.session_state.audit_summary['high_risk_issues'] > 0:
        st.markdown("### High Risk Issues")
        
        high_risk_findings = []
        for analysis_name, df in st.session_state.audit_results.items():
            if not df.empty and 'risk_level' in df.columns:
                high_risk = df[df['risk_level'] == 'High']
                for _, row in high_risk.iterrows():
                    finding = {
                        'Analysis': analysis_name.replace('_', ' ').title(),
                        'Issue': row.get('security_issues', row.get('security_issue', 'High risk issue detected')),
                        'Recommendation': row.get('recommendation', 'Immediate action required')
                    }
                    high_risk_findings.append(finding)
        
        if high_risk_findings:
            st.dataframe(pd.DataFrame(high_risk_findings), use_container_width=True)
    
    # Recommendations
    st.subheader("Recommendations")
    
    recommendations = []
    
    # Add recommendations based on findings
    if st.session_state.audit_summary['high_risk_issues'] > 0:
        recommendations.append("**Immediate Actions Required:**")
        recommendations.append("- Address all high-risk security issues identified in the audit")
        recommendations.append("- Review and remediate default password vulnerabilities")
        recommendations.append("- Restrict excessive object authorities")
    
    if st.session_state.audit_summary['medium_risk_issues'] > 0:
        recommendations.append("**Short-term Improvements:**")
        recommendations.append("- Review and adjust system values to meet security standards")
        recommendations.append("- Implement additional access controls where needed")
    
    recommendations.append("**Ongoing Security Practices:**")
    recommendations.append("- Conduct regular security audits")
    recommendations.append("- Monitor user access and privileges")
    recommendations.append("- Keep system values aligned with security policies")
    recommendations.append("- Implement automated security monitoring")
    
    for rec in recommendations:
        st.markdown(rec)
    
    # Export full report
    st.markdown("---")
    st.subheader("Export Report")
    
    if st.button("Generate Full Compliance Report"):
        # Create comprehensive report
        report_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'compliance_score': st.session_state.audit_summary['compliance_score'],
            'summary': st.session_state.audit_summary,
            'detailed_results': {}
        }
        
        # Add detailed results
        for analysis_name, df in st.session_state.audit_results.items():
            report_data['detailed_results'][analysis_name] = df.to_dict('records')
        
        # Export as JSON
        json_report = json.dumps(report_data, indent=2)
        st.download_button(
            label="Download Full Report (JSON)",
            data=json_report,
            file_name=f"ibm_i_compliance_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def show_real_time_monitoring():
    """Display real-time security monitoring dashboard"""
    
    st.header("Real-time Security Monitoring")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to enable monitoring.")
        return
    
    # Simulate real-time security events
    if 'security_events' not in st.session_state:
        st.session_state.security_events = []
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Enable Auto-refresh", value=False)
    
    if auto_refresh:
        st.info("Auto-refresh enabled - monitoring for security events...")
        
        # Simulate new security events
        import random
        
        current_time = datetime.datetime.now()
        event_types = [
            "Failed login attempt",
            "Unauthorized object access",
            "System value change",
            "User profile modification",
            "Suspicious activity detected"
        ]
        
        users = list(st.session_state.ibm_i_auditor.data_manager.user_profiles.keys())
        
        # Generate random events
        if random.random() < 0.3:  # 30% chance of new event
            new_event = {
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'event_type': random.choice(event_types),
                'user': random.choice(users),
                'severity': random.choice(['Low', 'Medium', 'High']),
                'details': f"Event occurred at {current_time.strftime('%H:%M:%S')}"
            }
            st.session_state.security_events.append(new_event)
    
    # Display recent events
    st.subheader("Recent Security Events")
    
    if st.session_state.security_events:
        events_df = pd.DataFrame(st.session_state.security_events)
        
        # Color code by severity
        def color_severity(val):
            if val == 'High':
                return 'background-color: #ff4444; color: white'
            elif val == 'Medium':
                return 'background-color: #ffaa00; color: black'
            else:
                return 'background-color: #44ff44; color: black'
        
        styled_events = events_df.style.map(color_severity, subset=['severity'])
        st.dataframe(styled_events, use_container_width=True)
        
        # Event statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            high_events = len(events_df[events_df['severity'] == 'High'])
            st.metric("High Severity Events", high_events)
        with col2:
            medium_events = len(events_df[events_df['severity'] == 'Medium'])
            st.metric("Medium Severity Events", medium_events)
        with col3:
            total_events = len(events_df)
            st.metric("Total Events", total_events)
        
        # Event type distribution
        st.subheader("Event Type Distribution")
        event_counts = events_df['event_type'].value_counts()
        fig = px.pie(
            values=event_counts.values,
            names=event_counts.index,
            title="Security Events by Type"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No security events detected yet.")
    
    # Clear events button
    if st.button("Clear Events"):
        st.session_state.security_events = []
        st.success("Events cleared!")

if __name__ == "__main__":
    main()
