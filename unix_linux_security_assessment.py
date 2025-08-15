#!/usr/bin/env python3
"""
Unix/Linux Security Assessment Dashboard
======================================

A comprehensive Streamlit application for Unix/Linux security auditing and compliance.
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

# Import our Unix/Linux audit core classes
from unix_linux_audit_core import (
    UnixLinuxSecurityAuditor, SecurityLevel, ComplianceStatus, generate_mock_unix_linux_data
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
    page_title="Unix/Linux Security Assessment",
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
if 'unix_linux_auditor' not in st.session_state:
    st.session_state.unix_linux_auditor = UnixLinuxSecurityAuditor()
    st.session_state.audit_results = None
    st.session_state.audit_summary = None

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">Unix/Linux Security Assessment</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Unix/Linux Security Audit")
        st.markdown("---")
        
        # Audit controls
        if st.button("Run Full Security Audit", type="primary"):
            try:
                with st.spinner("Running comprehensive Unix/Linux Security Audit..."):
                    # Use mock data for demonstration
                    st.session_state.audit_results = generate_mock_unix_linux_data()
                    st.session_state.audit_summary = st.session_state.unix_linux_auditor.get_audit_summary(st.session_state.audit_results)
                st.success("Audit completed successfully!")
                log_security_event("AUDIT_COMPLETED", "Unix/Linux security audit completed")
            except Exception as e:
                st.error(f"Audit failed: {str(e)}")
                st.info("Please try again or check your configuration.")
                log_security_event("AUDIT_FAILED", f"Audit failed: {str(e)}")
        
        # Data persistence controls
        st.header("Data Management")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Data", type="secondary"):
                if st.session_state.unix_linux_auditor.data_manager.save_data_to_file():
                    st.success("Data saved!")
                    log_security_event("DATA_SAVED", "Audit data saved to file")
                else:
                    st.error("Failed to save data")
        with col2:
            if st.button("Load Data", type="secondary"):
                if st.session_state.unix_linux_auditor.data_manager.load_data_from_file():
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
                    file_name=f"unix_linux_security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # CSV Export
            if st.button("Export to CSV", key="csv_export", use_container_width=True):
                csv_data = []
                for analysis_name, df in st.session_state.audit_results.items():
                    if isinstance(df, list) and df:
                        df_copy = pd.DataFrame(df)
                        df_copy['analysis_type'] = analysis_name
                        csv_data.append(df_copy)
                
                if csv_data:
                    combined_df = pd.concat(csv_data, ignore_index=True)
                    csv_export = combined_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV Report",
                        data=csv_export,
                        file_name=f"unix_linux_security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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
            ["Dashboard", "Compliance Frameworks", "File System Analysis", "User Analysis", "Network Analysis", "STIG Compliance"]
        )
        
        st.markdown("---")
        
        # About section
        st.header("About")
        st.markdown("""
        **Unix/Linux Security Assessment**
        
        This tool provides comprehensive Unix/Linux security auditing capabilities.
        
        **Features:**
        - File system security analysis
        - User account security assessment
        - Network service analysis
        - STIG compliance checking
        - Multi-platform support (Linux, AIX, Solaris)
        - Interactive visualizations
        """)
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Compliance Frameworks":
        show_compliance_frameworks()
    elif page == "File System Analysis":
        show_file_system_analysis()
    elif page == "User Analysis":
        show_user_analysis()
    elif page == "Network Analysis":
        show_network_analysis()
    elif page == "STIG Compliance":
        show_stig_compliance()

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
    
    # System information
    if st.session_state.audit_results.get('system_info'):
        system_info = st.session_state.audit_results['system_info']
        st.subheader("System Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**OS Type:** {system_info.get('os_type', 'Unknown')}")
            st.markdown(f"**OS Version:** {system_info.get('os_version', 'Unknown')}")
            st.markdown(f"**Hostname:** {system_info.get('hostname', 'Unknown')}")
        
        with col2:
            st.markdown(f"**Architecture:** {system_info.get('architecture', 'Unknown')}")
            st.markdown(f"**Scan Timestamp:** {system_info.get('scan_timestamp', 'Unknown')}")
            st.markdown(f"**Scan Duration:** {system_info.get('scan_duration', 0):.1f} seconds")
    
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

def show_compliance_frameworks():
    """Display compliance framework analysis"""
    
    st.header("Compliance Framework Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Click 'Run Full Security Audit' in the sidebar to begin analysis.")
        return
    
    # Run compliance framework analysis
    try:
        compliance_results = st.session_state.unix_linux_auditor.analyze_compliance_frameworks()
    except Exception as e:
        st.error(f"Error analyzing compliance frameworks: {e}")
        return
    
    # Compliance Overview
    st.subheader("Compliance Framework Overview")
    
    # Create compliance score cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stig_score = compliance_results['STIG']['compliance_score']
        st.metric(
            label="STIG Compliance",
            value=f"{stig_score:.1f}%",
            delta=None,
            delta_color="inverse" if stig_score < 80 else "normal"
        )
    
    with col2:
        nist_score = compliance_results['NIST']['compliance_score']
        st.metric(
            label="NIST Compliance",
            value=f"{nist_score:.1f}%",
            delta=None,
            delta_color="inverse" if nist_score < 80 else "normal"
        )
    
    with col3:
        cis_score = compliance_results['CIS']['compliance_score']
        st.metric(
            label="CIS Compliance",
            value=f"{cis_score:.1f}%",
            delta=None,
            delta_color="inverse" if cis_score < 80 else "normal"
        )

def show_file_system_analysis():
    """Display file system security analysis"""
    
    st.header("File System Security Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view file system analysis.")
        return
    
    file_analysis = st.session_state.audit_results.get('file_analysis', [])
    
    if not file_analysis:
        st.success("No file system security issues found!")
        return
    
    # Convert to DataFrame
    df_files = pd.DataFrame(file_analysis)
    
    # Display results
    st.subheader(f"File System Security Issues ({len(df_files)} files)")
    
    # Risk level distribution for files
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = df_files['risk_level'].value_counts()
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map={
                'High': '#ff4444',
                'Medium': '#ffaa00',
                'Low': '#44ff44'
            },
            title="File Security Issues by Risk Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results table
    st.subheader("Detailed File System Results")
    
    # Format the dataframe for display
    display_columns = ['file_path', 'permissions', 'risk_level', 'security_issues']
    display_df = df_files[display_columns].copy()
    
    st.dataframe(display_df, use_container_width=True)

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
    
    # Security issues summary
    if security_issues:
        st.subheader("Security Issues Summary")
        
        issue_counts = {}
        for issue in security_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        df_issues = pd.DataFrame(list(issue_counts.items()), columns=['Issue', 'Count'])
        
        fig = px.bar(
            df_issues,
            x='Issue',
            y='Count',
            title="User Security Issues Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_network_analysis():
    """Display network analysis"""
    
    st.header("Network Security Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view network analysis.")
        return
    
    network_analysis = st.session_state.audit_results.get('network_analysis', {})
    
    if not network_analysis:
        st.success("No network security issues found!")
        return
    
    listening_ports = network_analysis.get('listening_ports', [])
    security_issues = network_analysis.get('security_issues', [])
    
    # Network statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Listening Ports", len(listening_ports))
    
    with col2:
        st.metric("Security Issues", len(security_issues))
    
    with col3:
        unique_services = len(set([port.get('program', 'Unknown') for port in listening_ports]))
        st.metric("Unique Services", unique_services)
    
    # Listening ports analysis
    if listening_ports:
        st.subheader("Listening Ports")
        
        df_ports = pd.DataFrame(listening_ports)
        
        # Service distribution
        service_counts = df_ports['program'].value_counts()
        fig = px.pie(
            values=service_counts.values,
            names=service_counts.index,
            title="Services by Count"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed ports table
        st.subheader("Detailed Port Information")
        st.dataframe(df_ports, use_container_width=True)
    
    # Security issues
    if security_issues:
        st.subheader("Network Security Issues")
        
        for issue in security_issues:
            st.warning(issue)

def show_stig_compliance():
    """Display STIG compliance analysis"""
    
    st.header("STIG Compliance Analysis")
    
    if st.session_state.audit_results is None:
        st.info("Run a security audit first to view STIG compliance.")
        return
    
    stig_analysis = st.session_state.audit_results.get('stig_analysis', {})
    
    if not stig_analysis:
        st.success("No STIG compliance data available!")
        return
    
    # STIG compliance overview
    col1, col2, col3 = st.columns(3)
    
    total_controls = len(stig_analysis)
    compliant_controls = len([r for r in stig_analysis.values() if r.get('status') == 'Compliant'])
    non_compliant_controls = total_controls - compliant_controls
    
    with col1:
        st.metric("Total Controls", total_controls)
    
    with col2:
        st.metric("Compliant", compliant_controls, delta_color="normal")
    
    with col3:
        st.metric("Non-Compliant", non_compliant_controls, delta_color="inverse")
    
    # Compliance visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Compliance status pie chart
        status_counts = {}
        for result in stig_analysis.values():
            status = result.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="STIG Compliance Status"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed STIG controls
    st.subheader("Detailed STIG Controls")
    
    stig_list = []
    for control_id, result in stig_analysis.items():
        stig_list.append({
            'Control ID': control_id,
            'Title': result.get('title', ''),
            'Status': result.get('status', ''),
            'Severity': result.get('severity', ''),
            'Evidence': result.get('evidence', '')
        })
    
    if stig_list:
        df_stig = pd.DataFrame(stig_list)
        st.dataframe(df_stig, use_container_width=True)

if __name__ == "__main__":
    main()
