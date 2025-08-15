#!/usr/bin/env python3
"""
JD Edwards Security Assessment Dashboard
======================================

A comprehensive Streamlit application for JD Edwards World security auditing and compliance.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import json
import sys
import os
import re
import hashlib
import secrets

# Import our JD Edwards audit core classes
from jde_audit_core import (
    JDESecurityAuditor, AccessLevel, SecurityLevel, ComplianceStatus, generate_mock_jde_data
)

# Security configuration
SESSION_TIMEOUT_MINUTES = 30
MAX_LOGIN_ATTEMPTS = 5

def validate_input(input_string, max_length=1000):
    """Validate and sanitize user input"""
    if not input_string or len(input_string) > max_length:
        return False, "Input validation failed"
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
    page_title="JD Edwards Security Assessment",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
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
    
    .stMetric {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        padding: 16px;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }
    
    .js-plotly-plot {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 193, 7, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize security features
initialize_session_security()
check_session_timeout()

# Initialize session state
if 'jde_auditor' not in st.session_state:
    st.session_state.jde_auditor = JDESecurityAuditor()
    st.session_state.audit_results = None
    st.session_state.audit_summary = None

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">JD Edwards Security Assessment</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("JD Edwards Security Audit")
        st.markdown("---")
        
        # Audit controls
        if st.button("Run Full Security Audit", type="primary"):
            try:
                with st.spinner("Running comprehensive JD Edwards Security Audit..."):
                    # Run the full audit through the auditor
                    st.session_state.audit_results = st.session_state.jde_auditor.run_full_audit()
                    st.session_state.audit_summary = st.session_state.jde_auditor.get_audit_summary(st.session_state.audit_results)
                    
                st.success("Audit completed successfully!")
                log_security_event("AUDIT_COMPLETED", "JD Edwards security audit completed")
            except Exception as e:
                st.error(f"Audit failed: {str(e)}")
                st.info("Please try again or check your configuration.")
                log_security_event("AUDIT_FAILED", f"Audit failed: {str(e)}")
        
        # Data persistence controls
        st.header("Data Management")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Data", type="secondary"):
                if st.session_state.jde_auditor.data_manager.save_data_to_file():
                    st.success("Data saved!")
                    log_security_event("DATA_SAVED", "Audit data saved to file")
                else:
                    st.error("Failed to save data")
        with col2:
            if st.button("Load Data", type="secondary"):
                if st.session_state.jde_auditor.data_manager.load_data_from_file():
                    st.success("Data loaded!")
                    log_security_event("DATA_LOADED", "Audit data loaded from file")
                else:
                    st.info("No saved data found, using current data")
        
        st.markdown("---")
        
        # Export functionality
        st.header("Export Reports")
        if st.session_state.audit_results is not None:
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
                    file_name=f"jde_security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # CSV Export
            if st.button("Export to CSV", key="csv_export", use_container_width=True):
                csv_data = []
                for analysis_name, df in st.session_state.audit_results.items():
                    if isinstance(df, dict) and 'users' in df:
                        # Handle user data
                        users_df = pd.DataFrame.from_dict(df['users'], orient='index')
                        users_df['analysis_type'] = analysis_name
                        csv_data.append(users_df)
                    elif isinstance(df, dict) and 'programs' in df:
                        # Handle program data
                        programs_df = pd.DataFrame.from_dict(df['programs'], orient='index')
                        programs_df['analysis_type'] = analysis_name
                        csv_data.append(programs_df)
                
                if csv_data:
                    combined_df = pd.concat(csv_data, ignore_index=True)
                    csv_export = combined_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV Report",
                        data=csv_export,
                        file_name=f"jde_security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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
            ["Dashboard", "User Analysis", "Program Analysis", "Location Analysis", "Compliance Frameworks", "Access Control"]
        )
        
        st.markdown("---")
        
        # About section
        st.header("About")
        st.markdown("""
        **JD Edwards Security Assessment**
        
        This tool provides comprehensive JD Edwards World security auditing capabilities.
        
        **Features:**
        - User account security analysis
        - Program access control assessment
        - Location-based security analysis
        - SOX, PCI DSS, HIPAA compliance
        - Database connectivity analysis
        - Change tracking and monitoring
        """)
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "User Analysis":
        show_user_analysis()
    elif page == "Program Analysis":
        show_program_analysis()
    elif page == "Location Analysis":
        show_location_analysis()
    elif page == "Compliance Frameworks":
        show_compliance_frameworks()
    elif page == "Access Control":
        show_access_control()

def show_dashboard():
    """Display the main dashboard with overview metrics"""
    
    st.header("Security Assessment Dashboard")
    
    if st.session_state.audit_results is None:
        st.info("Click 'Run Full Security Audit' in the sidebar to begin analysis.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Compliance Score",
            value=f"{st.session_state.audit_summary['compliance_score']}%",
            delta=None
        )
    
    with col2:
        st.metric(
            label="High Risk Issues",
            value=st.session_state.audit_summary['high_risk_issues'],
            delta=None,
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Medium Risk Issues",
            value=st.session_state.audit_summary['medium_risk_issues'],
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Total Findings",
            value=st.session_state.audit_summary['total_findings'],
            delta=None
        )
    
    st.markdown("---")
    
    # System overview
    st.subheader("System Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Users",
            value=st.session_state.audit_summary['total_users'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Programs",
            value=st.session_state.audit_summary['total_programs'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Locations",
            value=st.session_state.audit_summary['total_locations'],
            delta=None
        )
    
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

def show_user_analysis():
    """Display user account analysis"""
    
    st.header("User Account Security Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view user analysis.")
        return
    
    user_analysis = st.session_state.audit_results.get('user_analysis', {})
    
    if not user_analysis or 'users' not in user_analysis:
        st.success("No user account security issues found!")
        return
    
    users = user_analysis.get('users', {})
    security_issues = user_analysis.get('security_issues', [])
    
    # User statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", len(users))
    
    with col2:
        users_with_issues = len([u for u in users.values() if u.get('security_issues')])
        st.metric("Users with Issues", users_with_issues)
    
    with col3:
        st.metric("Security Issues", len(security_issues))
    
    # User access level distribution
    st.subheader("User Access Level Distribution")
    
    access_levels = {}
    for user in users.values():
        access_level = user.get('access_level', 'Unknown')
        # Convert enum to string if it's an enum
        if hasattr(access_level, 'value'):
            access_level = access_level.value
        access_levels[access_level] = access_levels.get(access_level, 0) + 1
    
    if access_levels:
        fig = px.pie(
            values=list(access_levels.values()),
            names=list(access_levels.keys()),
            title="Users by Access Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # User status distribution
    st.subheader("User Status Distribution")
    
    user_status = {}
    for user in users.values():
        status = user.get('status', 'Unknown')
        user_status[status] = user_status.get(status, 0) + 1
    
    if user_status:
        fig = px.bar(
            x=list(user_status.keys()),
            y=list(user_status.values()),
            title="Users by Status"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed user table
    st.subheader("Detailed User Information")
    
    if users:
        users_list = []
        for user_id, user_info in users.items():
            access_level = user_info.get('access_level', '')
            # Convert enum to string if it's an enum
            if hasattr(access_level, 'value'):
                access_level = access_level.value
            
            users_list.append({
                'User ID': user_id,
                'User Name': user_info.get('user_name', ''),
                'User Type': user_info.get('user_type', ''),
                'Status': user_info.get('status', ''),
                'Access Level': access_level,
                'Group ID': user_info.get('group_id', ''),
                'Location': user_info.get('location', ''),
                'Last Login': user_info.get('last_login', ''),
                'Security Issues': ', '.join(user_info.get('security_issues', []))
            })
        
        df_users = pd.DataFrame(users_list)
        st.dataframe(df_users, use_container_width=True)

def show_program_analysis():
    """Display program access analysis"""
    
    st.header("Program Access Security Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view program analysis.")
        return
    
    program_analysis = st.session_state.audit_results.get('program_analysis', {})
    
    if not program_analysis:
        st.success("No program access security issues found!")
        return
    
    programs = program_analysis.get('programs', {})
    critical_programs = program_analysis.get('critical_programs', {})
    access_violations = program_analysis.get('access_violations', [])
    
    # Program statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Programs", len(programs))
    
    with col2:
        st.metric("Critical Programs", len(critical_programs))
    
    with col3:
        st.metric("Access Violations", len(access_violations))
    
    # Critical programs analysis
    st.subheader("Critical Programs Analysis")
    
    if critical_programs:
        critical_list = []
        for program_id, program_info in critical_programs.items():
            critical_level = program_info.get('critical_level', '')
            access_required = program_info.get('access_required', '')
            
            # Convert enums to strings if they're enums
            if hasattr(critical_level, 'value'):
                critical_level = critical_level.value
            if hasattr(access_required, 'value'):
                access_required = access_required.value
            
            critical_list.append({
                'Program ID': program_id,
                'Program Name': program_info.get('program_name', ''),
                'Program Type': program_info.get('program_type', ''),
                'Critical Level': critical_level,
                'Access Required': access_required,
                'Users with Access': len(program_info.get('users_with_access', [])),
                'Description': program_info.get('description', '')
            })
        
        df_critical = pd.DataFrame(critical_list)
        st.dataframe(df_critical, use_container_width=True)
    
    # Program type distribution
    st.subheader("Program Type Distribution")
    
    program_types = {}
    for program in programs.values():
        program_type = program.get('program_type', 'Unknown')
        program_types[program_type] = program_types.get(program_type, 0) + 1
    
    if program_types:
        fig = px.pie(
            values=list(program_types.values()),
            names=list(program_types.keys()),
            title="Programs by Type"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Access violations
    if access_violations:
        st.subheader("Access Violations")
        
        for violation in access_violations:
            st.warning(violation)

def show_location_analysis():
    """Display location security analysis"""
    
    st.header("Location Security Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view location analysis.")
        return
    
    location_analysis = st.session_state.audit_results.get('location_analysis', {})
    
    if not location_analysis:
        st.success("No location security issues found!")
        return
    
    locations = location_analysis.get('locations', {})
    location_issues = location_analysis.get('location_issues', [])
    
    # Location statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Locations", len(locations))
    
    with col2:
        locations_with_issues = len([l for l in locations.values() if l.get('users') and len(l.get('users', [])) > 20])
        st.metric("Locations with Issues", locations_with_issues)
    
    with col3:
        st.metric("Security Issues", len(location_issues))
    
    # Location security level distribution
    st.subheader("Location Security Level Distribution")
    
    security_levels = {}
    for location in locations.values():
        security_level = location.get('security_level', 'Unknown')
        # Convert enum to string if it's an enum
        if hasattr(security_level, 'value'):
            security_level = security_level.value
        security_levels[security_level] = security_levels.get(security_level, 0) + 1
    
    if security_levels:
        fig = px.pie(
            values=list(security_levels.values()),
            names=list(security_levels.keys()),
            title="Locations by Security Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Business unit distribution
    st.subheader("Business Unit Distribution")
    
    business_units = {}
    for location in locations.values():
        business_unit = location.get('business_unit', 'Unknown')
        business_units[business_unit] = business_units.get(business_unit, 0) + 1
    
    if business_units:
        fig = px.bar(
            x=list(business_units.keys()),
            y=list(business_units.values()),
            title="Locations by Business Unit"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed location table
    st.subheader("Detailed Location Information")
    
    if locations:
        location_list = []
        for location_id, location_info in locations.items():
            security_level = location_info.get('security_level', '')
            # Convert enum to string if it's an enum
            if hasattr(security_level, 'value'):
                security_level = security_level.value
            
            location_list.append({
                'Location ID': location_id,
                'Location Name': location_info.get('location_name', ''),
                'Location Type': location_info.get('location_type', ''),
                'Business Unit': location_info.get('business_unit', ''),
                'Security Level': security_level,
                'Users': len(location_info.get('users', []))
            })
        
        df_locations = pd.DataFrame(location_list)
        st.dataframe(df_locations, use_container_width=True)
    
    # Location issues
    if location_issues:
        st.subheader("Location Security Issues")
        
        for issue in location_issues:
            st.warning(issue)

def show_compliance_frameworks():
    """Display compliance framework analysis"""
    
    st.header("Compliance Framework Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Click 'Run Full Security Audit' in the sidebar to begin analysis.")
        return
    
    # Run compliance framework analysis
    try:
        compliance_results = st.session_state.jde_auditor.compliance_analyzer.analyze_compliance(st.session_state.audit_results)
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
            value=f"{sox_score:.1f}%",
            delta=None,
            delta_color="inverse" if sox_score < 80 else "normal"
        )
    
    with col2:
        pci_score = compliance_results['PCI DSS']['compliance_score']
        st.metric(
            label="PCI DSS Compliance",
            value=f"{pci_score:.1f}%",
            delta=None,
            delta_color="inverse" if pci_score < 80 else "normal"
        )
    
    with col3:
        hipaa_score = compliance_results['HIPAA']['compliance_score']
        st.metric(
            label="HIPAA Compliance",
            value=f"{hipaa_score:.1f}%",
            delta=None,
            delta_color="inverse" if hipaa_score < 80 else "normal"
        )
    
    # Framework details
    st.subheader("Framework Details")
    
    # Create tabs for each framework
    tab1, tab2, tab3 = st.tabs(["SOX", "PCI DSS", "HIPAA"])
    
    with tab1:
        show_framework_details("SOX", compliance_results['SOX'])
    
    with tab2:
        show_framework_details("PCI DSS", compliance_results['PCI DSS'])
    
    with tab3:
        show_framework_details("HIPAA", compliance_results['HIPAA'])

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
    
    if framework_data['controls']:
        controls_df = pd.DataFrame(framework_data['controls'])
        
        # Select columns to display
        display_columns = ['id', 'title', 'status', 'severity', 'check', 'fix']
        display_df = controls_df[display_columns].copy()
        
        st.dataframe(display_df, use_container_width=True)
        
        # Control summary
        total_controls = len(controls_df)
        compliant_controls = len(controls_df[controls_df['status'] == 'Compliant'])
        non_compliant_controls = len(controls_df[controls_df['status'] != 'Compliant'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Controls", total_controls)
        with col2:
            st.metric("Compliant", compliant_controls, delta_color="normal")
        with col3:
            st.metric("Non-Compliant", non_compliant_controls, delta_color="inverse")

def show_access_control():
    """Display access control analysis"""
    
    st.header("Access Control Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view access control analysis.")
        return
    
    # Access control overview
    st.subheader("Access Control Overview")
    
    # Get data from all analyses
    user_analysis = st.session_state.audit_results.get('user_analysis', {})
    program_analysis = st.session_state.audit_results.get('program_analysis', {})
    location_analysis = st.session_state.audit_results.get('location_analysis', {})
    
    # Access level distribution
    st.subheader("Access Level Distribution")
    
    access_levels = {}
    if user_analysis.get('users'):
        for user in user_analysis['users'].values():
            access_level = user.get('access_level', 'Unknown')
            # Convert enum to string if it's an enum
            if hasattr(access_level, 'value'):
                access_level = access_level.value
            access_levels[access_level] = access_levels.get(access_level, 0) + 1
    
    if access_levels:
        fig = px.pie(
            values=list(access_levels.values()),
            names=list(access_levels.keys()),
            title="Users by Access Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Critical access analysis
    st.subheader("Critical Access Analysis")
    
    critical_access_issues = []
    
    # Check for users with ALL access
    if user_analysis.get('users'):
        for user_id, user_info in user_analysis['users'].items():
            access_level = user_info.get('access_level')
            # Convert enum to string if it's an enum
            if hasattr(access_level, 'value'):
                access_level = access_level.value
            if access_level == 'All':
                critical_access_issues.append(f"User {user_id} has ALL access level")
    
    # Check for excessive access to critical programs
    if program_analysis.get('access_violations'):
        critical_access_issues.extend(program_analysis['access_violations'])
    
    if critical_access_issues:
        st.warning("**Critical Access Issues Detected:**")
        for issue in critical_access_issues:
            st.markdown(f"- {issue}")
    else:
        st.success("No critical access issues detected!")
    
    # Access recommendations
    st.subheader("Access Control Recommendations")
    
    recommendations = [
        "Implement role-based access control (RBAC)",
        "Review and reduce excessive access levels",
        "Implement least privilege principle",
        "Regular access reviews and recertification",
        "Monitor access to critical programs",
        "Implement segregation of duties controls"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")

if __name__ == "__main__":
    main()
