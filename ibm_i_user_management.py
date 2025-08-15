#!/usr/bin/env python3
"""
IBM i User Management Dashboard
===============================

A comprehensive Streamlit application for IBM i user management and administration.
This application provides tools for managing user profiles, groups, authorities,
and access controls in IBM i environments.

Features:
- User profile management and analysis
- Group membership administration
- Special authority assignment and review
- Access control analysis
- User activity monitoring
- Security policy enforcement
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

def validate_user_id(user_id):
    """Validate IBM i user ID format"""
    if not user_id or len(user_id) > 10:
        return False, "User ID must be 1-10 characters"
    
    # IBM i user ID rules: alphanumeric, no spaces, no special chars except @#$_
    if not re.match(r'^[A-Z@#$_\d]{1,10}$', user_id.upper()):
        return False, "User ID contains invalid characters"
    
    return True, user_id.upper()

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
    page_title="IBM i User Management",
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
    
    /* Status indicators */
    .status-enabled {
        color: #44ff44;
        font-weight: bold;
    }
    
    .status-disabled {
        color: #ff4444;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffaa00;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ibm_i_data' not in st.session_state:
    st.session_state.ibm_i_data = IBMiDataManager()
    st.session_state.ibm_i_data.generate_mock_ibm_i_data()

if 'ibm_i_auditor' not in st.session_state:
    st.session_state.ibm_i_auditor = IBMiSecurityAuditor()
    # Set the data manager to use our existing one
    st.session_state.ibm_i_auditor.data_manager = st.session_state.ibm_i_data

# Initialize role-based access control
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'Admin'  # Default role

# Initialize audit trail
if 'audit_trail' not in st.session_state:
    st.session_state.audit_trail = []

# Initialize loading states
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

def add_audit_entry(action: str, details: str, user_id: str = None, status: str = "Success"):
    """Add an entry to the audit trail"""
    import datetime
    audit_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'action': action,
        'details': details,
        'user_id': user_id,
        'status': status,
        'role': st.session_state.user_role
    }
    st.session_state.audit_trail.append(audit_entry)
    
    # Keep only last 100 entries to prevent memory issues
    if len(st.session_state.audit_trail) > 100:
        st.session_state.audit_trail = st.session_state.audit_trail[-100:]

def check_permission(required_role: str) -> bool:
    """Check if current user has required role"""
    role_hierarchy = {
        'Viewer': 1,
        'Analyst': 2,
        'Admin': 3
    }
    current_level = role_hierarchy.get(st.session_state.user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    return current_level >= required_level

def show_loading_spinner(message: str = "Processing..."):
    """Show loading spinner with custom message"""
    st.session_state.is_loading = True
    return st.spinner(message)

def hide_loading_spinner():
    """Hide loading spinner"""
    st.session_state.is_loading = False

def show_audit_trail():
    """Display the audit trail"""
    st.header("Audit Trail")
    
    if not st.session_state.audit_trail:
        st.info("No audit entries found.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        action_filter = st.selectbox(
            "Filter by Action",
            ["All"] + list(set([entry['action'] for entry in st.session_state.audit_trail]))
        )
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All"] + list(set([entry['status'] for entry in st.session_state.audit_trail]))
        )
    with col3:
        role_filter = st.selectbox(
            "Filter by Role",
            ["All"] + list(set([entry['role'] for entry in st.session_state.audit_trail]))
        )
    
    # Apply filters
    filtered_entries = st.session_state.audit_trail.copy()
    
    if action_filter != "All":
        filtered_entries = [entry for entry in filtered_entries if entry['action'] == action_filter]
    
    if status_filter != "All":
        filtered_entries = [entry for entry in filtered_entries if entry['status'] == status_filter]
    
    if role_filter != "All":
        filtered_entries = [entry for entry in filtered_entries if entry['role'] == role_filter]
    
    # Display audit trail
    if filtered_entries:
        # Convert to DataFrame for better display
        audit_df = pd.DataFrame(filtered_entries)
        audit_df['timestamp'] = pd.to_datetime(audit_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Color code by status
        def color_status(val):
            if val == 'Success':
                return 'background-color: #44ff44; color: black; font-weight: bold'
            elif val == 'Failed':
                return 'background-color: #ff4444; color: white; font-weight: bold'
            else:
                return 'background-color: #ffaa00; color: black; font-weight: bold'
        
        styled_df = audit_df.style.map(color_status, subset=['status'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Export audit trail
        if st.button("Export Audit Trail"):
            audit_json = json.dumps(filtered_entries, indent=2, default=str)
            st.download_button(
                label="Download Audit Trail (JSON)",
                data=audit_json,
                file_name=f"audit_trail_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    else:
        st.info("No audit entries match the selected filters.")

def main():
    """Main application function"""
    
    # Initialize security features
    initialize_session_security()
    check_session_timeout()
    
    # Header with status indicator
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<h1 class="main-header">IBM i User Management</h1>', unsafe_allow_html=True)
    
    with col2:
        # Status indicator
        if st.session_state.is_loading:
            st.markdown("**Processing...**")
        else:
            st.markdown("**Ready**")
        
        # Role indicator
        st.markdown(f"**{st.session_state.user_role}**")
    
    # Sidebar
    with st.sidebar:
        st.header("User Management")
        st.markdown("---")
        
        # Role-based access control
        st.subheader("Access Control")
        current_role = st.selectbox(
            "Current Role",
            ["Admin", "Analyst", "Viewer"],
            index=["Admin", "Analyst", "Viewer"].index(st.session_state.user_role)
        )
        
        if current_role != st.session_state.user_role:
            st.session_state.user_role = current_role
            add_audit_entry("Role Change", f"User role changed to {current_role}")
            st.success(f"Role updated to {current_role}")
        
        # Show role permissions
        with st.expander("Role Permissions"):
            if st.session_state.user_role == "Admin":
                st.markdown("**Admin Permissions:**")
                st.markdown("- Full user management")
                st.markdown("- Group administration")
                st.markdown("- Security policy changes")
                st.markdown("- Compliance reporting")
            elif st.session_state.user_role == "Analyst":
                st.markdown("**Analyst Permissions:**")
                st.markdown("- View user profiles")
                st.markdown("- Run compliance reports")
                st.markdown("- View audit trails")
            else:
                st.markdown("**Viewer Permissions:**")
                st.markdown("- Read-only access")
                st.markdown("- View dashboards")
        
        st.markdown("---")
        
        # Data persistence controls (Admin only)
        if check_permission("Admin"):
            st.subheader("Data Management")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Data", type="secondary"):
                    with show_loading_spinner("Saving data..."):
                        if st.session_state.ibm_i_data.save_data_to_file():
                            add_audit_entry("Data Save", "User data saved successfully")
                            st.success("Data saved successfully!")
                        else:
                            add_audit_entry("Data Save", "Failed to save data", status="Failed")
                            st.error("Failed to save data")
            with col2:
                if st.button("Load Data", type="secondary"):
                    with show_loading_spinner("Loading data..."):
                        if st.session_state.ibm_i_data.load_data_from_file():
                            add_audit_entry("Data Load", "User data loaded successfully")
                            st.success("Data loaded successfully!")
                        else:
                            add_audit_entry("Data Load", "No saved data found", status="Info")
                            st.info("No saved data found, using current data")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        
        # Filter navigation based on role
        available_pages = ["Dashboard"]
        
        if check_permission("Analyst"):
            available_pages.extend(["User Profiles", "User Activity", "Security Policies", "Compliance Reports"])
        
        if check_permission("Admin"):
            available_pages.extend(["Group Management", "Access Control"])
        
        page = st.selectbox(
            "Select Module",
            available_pages
        )
        
        # Quick stats
        if not st.session_state.is_loading:
            st.markdown("---")
            st.subheader("Quick Stats")
            total_users = len(st.session_state.ibm_i_data.user_profiles)
            enabled_users = len([u for u in st.session_state.ibm_i_data.user_profiles.values() if u['status'] == '*ENABLED'])
            users_with_issues = len([u for u in st.session_state.ibm_i_data.user_profiles.values() if u.get('pass_none') == '*YES'])
            
            st.metric("Total Users", total_users)
            st.metric("Active Users", enabled_users)
            st.metric("Audit Entries", len(st.session_state.audit_trail))
            
            # System health indicator
            st.markdown("---")
            st.subheader("System Health")
            
            if users_with_issues == 0:
                st.success("All users compliant")
            elif users_with_issues <= 2:
                st.warning(f"{users_with_issues} users need attention")
            else:
                st.error(f"{users_with_issues} users have issues")
            
            # Recent activity
            if st.session_state.audit_trail:
                latest_entry = st.session_state.audit_trail[-1]
                st.caption(f"Last activity: {latest_entry['action']}")
                st.caption(f"Time: {latest_entry['timestamp'][:19]}")
    
    # Breadcrumb navigation
    st.markdown(f"**Home** > **User Management** > **{page}**")
    st.markdown("---")
    
    # Quick actions
    st.header("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Refresh Data", type="secondary"):
            with show_loading_spinner("Refreshing user data..."):
                st.session_state.ibm_i_data.generate_mock_ibm_i_data()
                add_audit_entry("Data Refresh", "User data refreshed successfully")
                st.success("User data refreshed successfully!")
    
    with col2:
        if st.button("Generate Report", type="secondary"):
            with show_loading_spinner("Generating user report..."):
                generate_user_report()
                add_audit_entry("Report Generation", "User report generated successfully")
    
    with col3:
        if check_permission("Admin"):
            if st.button("View Audit Trail", type="secondary"):
                st.session_state.show_audit = True
                st.rerun()
        else:
            st.button("View Audit Trail", type="secondary", disabled=True)
            st.caption("Admin access required")
    
    st.markdown("---")
    
    # About section
    st.header("About")
    st.markdown("""
        **IBM i User Management**
        
        Comprehensive user management and administration tools for IBM i systems.
        
        **Features:**
        - User profile administration
        - Group membership management
        - Access control analysis
        - Security policy enforcement
        - User activity monitoring
        """)
    
    # Main content based on selected page
    if page == "Dashboard":
        show_user_dashboard()
    elif page == "User Profiles":
        show_user_profiles()
    elif page == "Group Management":
        show_group_management()
    elif page == "Access Control":
        show_access_control()
    elif page == "User Activity":
        show_user_activity()
    elif page == "Security Policies":
        show_security_policies()
    elif page == "Compliance Reports":
        show_compliance_reports()
    
    # Show audit trail if requested
    if 'show_audit' not in st.session_state:
        st.session_state.show_audit = False
    
    if st.session_state.show_audit:
        show_audit_trail()
        st.session_state.show_audit = False

def show_user_dashboard():
    """Display the main user management dashboard"""
    
    st.header("User Management Dashboard")
    
    # Show loading state if processing
    if st.session_state.is_loading:
        with st.spinner("Loading dashboard data..."):
            pass
    
    # Key metrics with enhanced styling
    col1, col2, col3, col4 = st.columns(4)
    
    total_users = len(st.session_state.ibm_i_data.user_profiles)
    enabled_users = len([u for u in st.session_state.ibm_i_data.user_profiles.values() if u['status'] == '*ENABLED'])
    disabled_users = total_users - enabled_users
    users_with_issues = len([u for u in st.session_state.ibm_i_data.user_profiles.values() if u.get('pass_none') == '*YES'])
    
    # Calculate percentages for better insights
    enabled_percentage = (enabled_users / total_users * 100) if total_users > 0 else 0
    issues_percentage = (users_with_issues / total_users * 100) if total_users > 0 else 0
    
    with col1:
        st.metric(
            label="Total Users",
            value=total_users,
            delta=None
        )
        st.caption("System-wide user accounts")
    
    with col2:
        st.metric(
            label="Enabled Users",
            value=enabled_users,
            delta=f"{enabled_percentage:.1f}%",
            delta_color="normal"
        )
        st.caption("Active user accounts")
    
    with col3:
        st.metric(
            label="Disabled Users",
            value=disabled_users,
            delta=f"{(disabled_users/total_users*100):.1f}%" if total_users > 0 else "0%",
            delta_color="inverse"
        )
        st.caption("Inactive user accounts")
    
    with col4:
        st.metric(
            label="Users with Issues",
            value=users_with_issues,
            delta=f"{issues_percentage:.1f}%",
            delta_color="inverse"
        )
        st.caption("Security compliance issues")
    
    st.markdown("---")
    
    # User status distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("User Status Distribution")
        
        status_data = {
            'Status': ['Enabled', 'Disabled'],
            'Count': [enabled_users, disabled_users]
        }
        
        df_status = pd.DataFrame(status_data)
        
        fig = px.pie(
            df_status,
            values='Count',
            names='Status',
            color_discrete_map={
                'Enabled': '#44ff44',
                'Disabled': '#ff4444'
            }
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("User Class Distribution")
        
        # Count users by class
        user_classes = {}
        for user in st.session_state.ibm_i_data.user_profiles.values():
            user_class = user.get('user_class', '*USER')
            user_classes[user_class] = user_classes.get(user_class, 0) + 1
        
        if user_classes:
            class_data = {
                'User Class': list(user_classes.keys()),
                'Count': list(user_classes.values())
            }
            
            df_class = pd.DataFrame(class_data)
            
            fig = px.bar(
                df_class,
                x='User Class',
                y='Count',
                title="Users by Class"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent user activity
    st.subheader("Recent User Activity")
    
    # Create mock user activity data
    activity_data = []
    for user_id, profile in st.session_state.ibm_i_data.user_profiles.items():
        activity_data.append({
            'User ID': user_id,
            'Name': profile.get('name', ''),
            'Last Sign On': profile.get('prev_sign_on', '2024-01-01'),
            'Status': profile.get('status', '*ENABLED'),
            'User Class': profile.get('user_class', '*USER'),
            'Issues': 'Default Password' if profile.get('pass_none') == '*YES' else 'None'
        })
    
    df_activity = pd.DataFrame(activity_data)
    st.dataframe(df_activity, use_container_width=True)

def show_user_profiles():
    """Display user profile management interface"""
    
    st.header("User Profile Management")
    
    # Check permissions
    if not check_permission("Analyst"):
        st.error("Access Denied: Analyst or Admin role required to view user profiles.")
        return
    
    # Tabs for different user management functions
    available_tabs = ["User List"]
    
    if check_permission("Admin"):
        available_tabs.extend(["Add User", "Edit User"])
    
    tab1, tab2, tab3 = st.tabs(available_tabs)
    
    with tab1:
        st.subheader("User Profiles")
        
        # Search and filter
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("Search Users", placeholder="Enter user ID or name")
        
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "*ENABLED", "*DISABLED"])
        
        with col3:
            class_filter = st.selectbox("Filter by Class", ["All"] + list(set([u.get('user_class', '*USER') for u in st.session_state.ibm_i_data.user_profiles.values()])))
        
        # Create user list dataframe
        user_list = []
        for user_id, profile in st.session_state.ibm_i_data.user_profiles.items():
            user_list.append({
                'User ID': user_id,
                'Name': profile.get('name', ''),
                'Status': profile.get('status', '*ENABLED'),
                'User Class': profile.get('user_class', '*USER'),
                'Primary Group': profile.get('group', ''),
                'Last Sign On': profile.get('prev_sign_on', '2024-01-01'),
                'Password Expires': profile.get('pass_exp', '*YES'),
                'Issues': 'Default Password' if profile.get('pass_none') == '*YES' else 'None'
            })
        
        df_users = pd.DataFrame(user_list)
        
        # Apply filters
        if search_term:
            df_users = df_users[
                df_users['User ID'].str.contains(search_term, case=False) |
                df_users['Name'].str.contains(search_term, case=False)
            ]
        
        if status_filter != "All":
            df_users = df_users[df_users['Status'] == status_filter]
        
        if class_filter != "All":
            df_users = df_users[df_users['User Class'] == class_filter]
        
        # Display user list
        st.dataframe(df_users, use_container_width=True)
        
        # User statistics
        st.subheader("User Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", len(df_users))
        
        with col2:
            enabled_count = len(df_users[df_users['Status'] == '*ENABLED'])
            st.metric("Enabled Users", enabled_count)
        
        with col3:
            issues_count = len(df_users[df_users['Issues'] != 'None'])
            st.metric("Users with Issues", issues_count)
    
    with tab2:
        if not check_permission("Admin"):
            st.error("Access Denied: Admin role required to add users.")
            return
            
        st.subheader("Add New User")
        
        # Validation helper
        def validate_user_id(user_id):
            if not user_id:
                return False, "User ID is required"
            if len(user_id) < 3:
                return False, "User ID must be at least 3 characters"
            if user_id in st.session_state.ibm_i_data.user_profiles:
                return False, "User ID already exists"
            return True, ""
        
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_user_id = st.text_input("User ID *", placeholder="Enter user ID (min 3 chars)")
                new_user_name = st.text_input("Full Name *", placeholder="Enter full name")
                new_user_class = st.selectbox("User Class", ["*USER", "*SYSOPR", "*SECOFR", "*PGMR"])
                new_user_status = st.selectbox("Status", ["*ENABLED", "*DISABLED"])
            
            with col2:
                new_user_group = st.selectbox("Primary Group", list(st.session_state.ibm_i_data.groups.keys()))
                new_user_lib = st.text_input("Current Library", value="QGPL")
                new_user_exp = st.selectbox("Password Expires", ["*YES", "*NO"])
                new_user_exp_int = st.number_input("Password Expiration (days)", min_value=1, value=90)
            
            # Show validation hints
            if new_user_id:
                is_valid, error_msg = validate_user_id(new_user_id)
                if not is_valid:
                    st.error(f"{error_msg}")
                else:
                    st.success("User ID is valid")
            
            if st.form_submit_button("Add User"):
                # Validate inputs
                is_valid_id, id_error = validate_user_id(new_user_id)
                
                if not is_valid_id:
                    st.error(f"{id_error}")
                    add_audit_entry("User Creation", f"Failed to create user {new_user_id}: {id_error}", new_user_id, "Failed")
                elif not new_user_name:
                    st.error("Full name is required")
                    add_audit_entry("User Creation", f"Failed to create user {new_user_id}: Missing name", new_user_id, "Failed")
                else:
                    with show_loading_spinner("Creating user profile..."):
                        # Add user to the data manager
                        st.session_state.ibm_i_data.user_profiles[new_user_id] = {
                            'name': new_user_name,
                            'limited_cap': '*YES',
                            'init_prog': '*NONE',
                            'cur_lib': new_user_lib,
                            'init_menu': '*NONE',
                            'status': new_user_status,
                            'group': new_user_group,
                            'sup_group': [],
                            'pass_none': '*NO',
                            'pass_exp_int': str(new_user_exp_int),
                            'user_class': new_user_class,
                            'spec_auth': [],
                            'prev_sign_on': datetime.datetime.now().strftime('%Y-%m-%d'),
                            'pass_exp': new_user_exp,
                            'so_att_not_valid': '*NO',
                            'lim_dev_sessions': '*NO',
                            'max_storage': '500000',
                            'storage_used': '0',
                            'attn_prog': '*NONE',
                            'attn_prog_lib': '*LIBL'
                        }
                        
                        # Add to audit trail
                        add_audit_entry(
                            "User Creation", 
                            f"Created user {new_user_id} ({new_user_name}) with class {new_user_class}", 
                            new_user_id
                        )
                        
                        st.success(f"User {new_user_id} created successfully!")
                        st.balloons()
    
    with tab3:
        if not check_permission("Admin"):
            st.error("Access Denied: Admin role required to edit users.")
            return
            
        st.subheader("Edit User")
        
        # Select user to edit
        user_to_edit = st.selectbox("Select User to Edit", list(st.session_state.ibm_i_data.user_profiles.keys()))
        
        if user_to_edit:
            user_profile = st.session_state.ibm_i_data.user_profiles[user_to_edit]
            
            # Show current user info
            st.info(f"**Editing User:** {user_to_edit} - {user_profile.get('name', 'Unknown')}")
            
            with st.form("edit_user"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Full Name *", value=user_profile.get('name', ''))
                    edit_status = st.selectbox("Status", ["*ENABLED", "*DISABLED"], index=0 if user_profile.get('status') == '*ENABLED' else 1)
                    edit_class = st.selectbox("User Class", ["*USER", "*SYSOPR", "*SECOFR", "*PGMR"], 
                                            index=["*USER", "*SYSOPR", "*SECOFR", "*PGMR"].index(user_profile.get('user_class', '*USER')))
                
                with col2:
                    edit_group = st.selectbox("Primary Group", list(st.session_state.ibm_i_data.groups.keys()), 
                                            index=list(st.session_state.ibm_i_data.groups.keys()).index(user_profile.get('group', 'USERS')))
                    edit_lib = st.text_input("Current Library", value=user_profile.get('cur_lib', 'QGPL'))
                    edit_exp = st.selectbox("Password Expires", ["*YES", "*NO"], 
                                          index=0 if user_profile.get('pass_exp') == '*YES' else 1)
                
                # Show what will change
                st.markdown("**Changes to be applied:**")
                changes = []
                if edit_name != user_profile.get('name'):
                    changes.append(f"Name: {user_profile.get('name')} → {edit_name}")
                if edit_status != user_profile.get('status'):
                    changes.append(f"Status: {user_profile.get('status')} → {edit_status}")
                if edit_class != user_profile.get('user_class'):
                    changes.append(f"Class: {user_profile.get('user_class')} → {edit_class}")
                if edit_group != user_profile.get('group'):
                    changes.append(f"Group: {user_profile.get('group')} → {edit_group}")
                
                if changes:
                    for change in changes:
                        st.markdown(f"- {change}")
                else:
                    st.info("No changes detected")
                
                if st.form_submit_button("Update User"):
                    if not edit_name:
                        st.error("Full name is required")
                        add_audit_entry("User Update", f"Failed to update user {user_to_edit}: Missing name", user_to_edit, "Failed")
                    else:
                        with show_loading_spinner("Updating user profile..."):
                            # Track changes for audit
                            change_details = []
                            if edit_name != user_profile.get('name'):
                                change_details.append(f"name: {user_profile.get('name')} → {edit_name}")
                            if edit_status != user_profile.get('status'):
                                change_details.append(f"status: {user_profile.get('status')} → {edit_status}")
                            if edit_class != user_profile.get('user_class'):
                                change_details.append(f"class: {user_profile.get('user_class')} → {edit_class}")
                            if edit_group != user_profile.get('group'):
                                change_details.append(f"group: {user_profile.get('group')} → {edit_group}")
                            
                            # Update user profile
                            user_profile['name'] = edit_name
                            user_profile['status'] = edit_status
                            user_profile['user_class'] = edit_class
                            user_profile['group'] = edit_group
                            user_profile['cur_lib'] = edit_lib
                            user_profile['pass_exp'] = edit_exp
                            
                            # Add to audit trail
                            if change_details:
                                add_audit_entry(
                                    "User Update", 
                                    f"Updated user {user_to_edit}: {', '.join(change_details)}", 
                                    user_to_edit
                                )
                            else:
                                add_audit_entry(
                                    "User Update", 
                                    f"No changes made to user {user_to_edit}", 
                                    user_to_edit,
                                    "Info"
                                )
                            
                            st.success(f"User {user_to_edit} updated successfully!")
                            if change_details:
                                st.balloons()

def show_group_management():
    """Display group management interface"""
    
    st.header("Group Management")
    
    # Tabs for group management
    tab1, tab2, tab3 = st.tabs(["Group List", "Add Group", "Group Members"])
    
    with tab1:
        st.subheader("Groups")
        
        # Create group list
        group_list = []
        for group_id, group_data in st.session_state.ibm_i_data.groups.items():
            group_list.append({
                'Group ID': group_id,
                'Name': group_data.get('name', ''),
                'Status': group_data.get('status', '*ENABLED'),
                'Member Count': len(group_data.get('members', [])),
                'Members': ', '.join(group_data.get('members', []))
            })
        
        df_groups = pd.DataFrame(group_list)
        st.dataframe(df_groups, use_container_width=True)
        
        # Group statistics
        st.subheader("Group Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Groups", len(df_groups))
        
        with col2:
            enabled_groups = len(df_groups[df_groups['Status'] == '*ENABLED'])
            st.metric("Enabled Groups", enabled_groups)
        
        with col3:
            avg_members = df_groups['Member Count'].mean()
            st.metric("Avg Members per Group", f"{avg_members:.1f}")
    
    with tab2:
        st.subheader("Add New Group")
        
        with st.form("add_group"):
            new_group_id = st.text_input("Group ID", placeholder="Enter group ID")
            new_group_name = st.text_input("Group Name", placeholder="Enter group name")
            new_group_status = st.selectbox("Status", ["*ENABLED", "*DISABLED"])
            
            if st.form_submit_button("Add Group"):
                if new_group_id and new_group_name:
                    st.session_state.ibm_i_data.groups[new_group_id] = {
                        'name': new_group_name,
                        'members': [],
                        'status': new_group_status
                    }
                    st.success(f"Group {new_group_id} added successfully!")
                else:
                    st.error("Please fill in all required fields.")
    
    with tab3:
        st.subheader("Group Members")
        
        selected_group = st.selectbox("Select Group", list(st.session_state.ibm_i_data.groups.keys()))
        
        if selected_group:
            group_data = st.session_state.ibm_i_data.groups[selected_group]
            
            st.markdown(f"**Group:** {selected_group} - {group_data.get('name', '')}")
            st.markdown(f"**Status:** {group_data.get('status', '*ENABLED')}")
            st.markdown(f"**Members:** {len(group_data.get('members', []))}")
            
            # Display current members
            if group_data.get('members'):
                st.subheader("Current Members")
                
                member_list = []
                for member_id in group_data['members']:
                    user_profile = st.session_state.ibm_i_data.user_profiles.get(member_id, {})
                    member_list.append({
                        'User ID': member_id,
                        'Name': user_profile.get('name', ''),
                        'Status': user_profile.get('status', '*ENABLED'),
                        'User Class': user_profile.get('user_class', '*USER')
                    })
                
                df_members = pd.DataFrame(member_list)
                st.dataframe(df_members, use_container_width=True)
            else:
                st.info("No members in this group.")
            
            # Add/remove members
            st.subheader("Manage Members")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Add Member**")
                available_users = [uid for uid in st.session_state.ibm_i_data.user_profiles.keys() 
                                 if uid not in group_data.get('members', [])]
                
                if available_users:
                    user_to_add = st.selectbox("Select User to Add", available_users)
                    if st.button("Add to Group"):
                        if 'members' not in group_data:
                            group_data['members'] = []
                        group_data['members'].append(user_to_add)
                        st.success(f"User {user_to_add} added to group {selected_group}!")
                        st.rerun()
                else:
                    st.info("No available users to add.")
            
            with col2:
                st.markdown("**Remove Member**")
                current_members = group_data.get('members', [])
                
                if current_members:
                    user_to_remove = st.selectbox("Select User to Remove", current_members)
                    if st.button("Remove from Group"):
                        group_data['members'].remove(user_to_remove)
                        st.success(f"User {user_to_remove} removed from group {selected_group}!")
                        st.rerun()
                else:
                    st.info("No members to remove.")

def show_access_control():
    """Display access control analysis"""
    
    st.header("Access Control Analysis")
    
    # Create access control auditor
    auditor = IBMiSecurityAuditor()
    auditor.data_manager = st.session_state.ibm_i_data
    
    # Run access control analysis
    if st.button("Run Access Control Analysis"):
        with st.spinner("Analyzing access controls..."):
            results = auditor.run_full_audit()
            st.session_state.access_results = results
    
    if 'access_results' in st.session_state:
        # Display access control results
        st.subheader("Access Control Results")
        
        # Tabs for different access control analyses
        tab1, tab2, tab3 = st.tabs(["Object Authorities", "Special Authorities", "Default Passwords"])
        
        with tab1:
            st.markdown("### Object Authority Analysis")
            
            df_objects = st.session_state.access_results['object_authorities']
            
            # Risk level distribution
            col1, col2 = st.columns(2)
            
            with col1:
                risk_counts = df_objects['risk_level'].value_counts()
                fig = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    title="Object Authorities by Risk Level"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # High risk objects
                high_risk = df_objects[df_objects['risk_level'] == 'High']
                if len(high_risk) > 0:
                    st.warning(f"Found {len(high_risk)} high-risk object authorities!")
                    st.dataframe(high_risk[['object', 'user_group', 'security_issues']], use_container_width=True)
                else:
                    st.success("No high-risk object authorities found!")
            
            # All object authorities
            st.dataframe(df_objects, use_container_width=True)
        
        with tab2:
            st.markdown("### User Profile Analysis")
            
            if 'user_profiles' in st.session_state.access_results:
                df_user_profiles = st.session_state.access_results['user_profiles']
                
                if len(df_user_profiles) > 0:
                    # Users with security issues
                    high_risk_users = df_user_profiles[df_user_profiles['risk_level'] == 'High']
                    if len(high_risk_users) > 0:
                        st.warning(f"Found {len(high_risk_users)} users with high-risk security issues!")
                        st.dataframe(high_risk_users, use_container_width=True)
                    
                    # All user profiles with issues
                    st.dataframe(df_user_profiles, use_container_width=True)
                else:
                    st.success("No user profile security issues found!")
            else:
                st.info("User profile analysis not available in this audit.")
        
        with tab3:
            st.markdown("### System Values Analysis")
            
            if 'system_values' in st.session_state.access_results:
                df_system_values = st.session_state.access_results['system_values']
                
                if len(df_system_values) > 0:
                    # Non-compliant system values
                    non_compliant = df_system_values[df_system_values['compliance_status'] == 'Non-Compliant']
                    if len(non_compliant) > 0:
                        st.warning(f"Found {len(non_compliant)} non-compliant system values!")
                        st.dataframe(non_compliant, use_container_width=True)
                    
                    # All system values
                    st.dataframe(df_system_values, use_container_width=True)
                else:
                    st.success("No system value issues found!")
            else:
                st.info("System values analysis not available in this audit.")

def show_user_activity():
    """Display user activity monitoring"""
    
    st.header("User Activity Monitoring")
    
    # Mock user activity data
    activity_data = []
    
    for user_id, profile in st.session_state.ibm_i_data.user_profiles.items():
        # Generate mock activity data
        last_sign_on = profile.get('prev_sign_on', '2024-01-01')
        days_since_sign_on = (datetime.datetime.now() - datetime.datetime.strptime(last_sign_on, '%Y-%m-%d')).days
        
        activity_data.append({
            'User ID': user_id,
            'Name': profile.get('name', ''),
            'Last Sign On': last_sign_on,
            'Days Since Last Sign On': days_since_sign_on,
            'Status': profile.get('status', '*ENABLED'),
            'User Class': profile.get('user_class', '*USER'),
            'Activity Level': 'Active' if days_since_sign_on <= 30 else 'Inactive' if days_since_sign_on <= 90 else 'Dormant'
        })
    
    df_activity = pd.DataFrame(activity_data)
    
    # Activity overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        active_users = len(df_activity[df_activity['Activity Level'] == 'Active'])
        st.metric("Active Users", active_users)
    
    with col2:
        inactive_users = len(df_activity[df_activity['Activity Level'] == 'Inactive'])
        st.metric("Inactive Users", inactive_users)
    
    with col3:
        dormant_users = len(df_activity[df_activity['Activity Level'] == 'Dormant'])
        st.metric("Dormant Users", dormant_users)
    
    # Activity level distribution
    col1, col2 = st.columns(2)
    
    with col1:
        activity_counts = df_activity['Activity Level'].value_counts()
        fig = px.pie(
            values=activity_counts.values,
            names=activity_counts.index,
            title="User Activity Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Days since last sign on distribution
        fig = px.histogram(
            df_activity,
            x='Days Since Last Sign On',
            title="Days Since Last Sign On Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # User activity table
    st.subheader("User Activity Details")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        activity_filter = st.selectbox("Filter by Activity", ["All"] + list(df_activity['Activity Level'].unique()))
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df_activity['Status'].unique()))
    
    with col3:
        class_filter = st.selectbox("Filter by Class", ["All"] + list(df_activity['User Class'].unique()))
    
    # Apply filters
    filtered_activity = df_activity.copy()
    
    if activity_filter != "All":
        filtered_activity = filtered_activity[filtered_activity['Activity Level'] == activity_filter]
    
    if status_filter != "All":
        filtered_activity = filtered_activity[filtered_activity['Status'] == status_filter]
    
    if class_filter != "All":
        filtered_activity = filtered_activity[filtered_activity['User Class'] == class_filter]
    
    st.dataframe(filtered_activity, use_container_width=True)
    
    # Dormant user recommendations
    dormant_users = df_activity[df_activity['Activity Level'] == 'Dormant']
    if len(dormant_users) > 0:
        st.subheader("Dormant User Recommendations")
        st.warning(f"Found {len(dormant_users)} dormant users. Consider reviewing and potentially disabling these accounts.")
        
        st.dataframe(dormant_users[['User ID', 'Name', 'Days Since Last Sign On', 'Status']], use_container_width=True)

def show_security_policies():
    """Display security policy management"""
    
    st.header("Security Policy Management")
    
    # Security policy configuration
    st.subheader("Password Policy Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Password Settings**")
        
        # Get system values for password policy
        password_policies = {
            'Minimum Length': st.session_state.ibm_i_data.system_values.get('QPWDMINLEN', {}).get('current', '8'),
            'Maximum Length': st.session_state.ibm_i_data.system_values.get('QPWDMAXLEN', {}).get('current', '128'),
            'Expiration Interval': st.session_state.ibm_i_data.system_values.get('QPWDEXPITV', {}).get('current', '90'),
            'Password Level': st.session_state.ibm_i_data.system_values.get('QPWDLVL', {}).get('current', '2'),
            'Security Level': st.session_state.ibm_i_data.system_values.get('QSECURITY', {}).get('current', '40')
        }
        
        for policy, value in password_policies.items():
            st.metric(policy, value)
    
    with col2:
        st.markdown("**Recommended Password Settings**")
        
        recommended_policies = {
            'Minimum Length': '12',
            'Maximum Length': '128',
            'Expiration Interval': '90',
            'Password Level': '2',
            'Security Level': '40'
        }
        
        for policy, value in recommended_policies.items():
            current = password_policies.get(policy, '0')
            status = "✅ Compliant" if current == value else "⚠️ Non-Compliant"
            st.markdown(f"**{policy}:** {value} {status}")
    
    # Security policy recommendations
    st.subheader("Security Policy Recommendations")
    
    recommendations = [
        "**Password Policy:**",
        "- Enforce minimum password length of 12 characters",
        "- Require password complexity (uppercase, lowercase, numbers, special characters)",
        "- Set password expiration to 90 days",
        "- Implement account lockout after failed attempts",
        "",
        "**Access Control Policy:**",
        "- Follow principle of least privilege",
        "- Regular review of user access rights",
        "- Implement role-based access control",
        "- Monitor and log all access attempts",
        "",
        "**User Management Policy:**",
        "- Regular review of user accounts",
        "- Disable unused accounts",
        "- Implement user lifecycle management",
        "- Require manager approval for access changes"
    ]
    
    for rec in recommendations:
        st.markdown(rec)
    
    # Policy compliance report
    st.subheader("Policy Compliance Report")
    
    if st.button("Generate Compliance Report"):
        # Calculate compliance score
        compliance_items = 0
        total_items = len(password_policies)
        
        for policy, current in password_policies.items():
            if current == recommended_policies.get(policy, current):
                compliance_items += 1
        
        compliance_score = (compliance_items / total_items) * 100
        
        st.metric("Password Policy Compliance", f"{compliance_score:.1f}%")
        
        if compliance_score >= 90:
            st.success("Excellent password policy compliance!")
        elif compliance_score >= 70:
            st.warning("Good password policy compliance with room for improvement.")
        else:
            st.error("Password policy compliance needs attention.")

def generate_user_report():
    """Generate comprehensive user report"""
    
    # Create user report data
    report_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'total_users': len(st.session_state.ibm_i_data.user_profiles),
        'enabled_users': len([u for u in st.session_state.ibm_i_data.user_profiles.values() if u['status'] == '*ENABLED']),
        'disabled_users': len([u for u in st.session_state.ibm_i_data.user_profiles.values() if u['status'] == '*DISABLED']),
        'users_with_issues': len([u for u in st.session_state.ibm_i_data.user_profiles.values() if u.get('pass_none') == '*YES']),
        'user_profiles': st.session_state.ibm_i_data.user_profiles,
        'groups': st.session_state.ibm_i_data.groups
    }
    
    # Export as JSON
    json_report = json.dumps(report_data, indent=2)
    st.download_button(
        label="Download User Report (JSON)",
        data=json_report,
        file_name=f"ibm_i_user_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def show_compliance_reports():
    """Display comprehensive compliance framework analysis for user management"""
    
    st.header("Compliance Framework Analysis")
    
    # Run compliance framework analysis
    try:
        compliance_results = st.session_state.ibm_i_auditor.analyze_user_management_compliance()
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
        show_user_framework_details("SOX", compliance_results['SOX'])
    
    with tab2:
        show_user_framework_details("PCI DSS", compliance_results['PCI DSS'])
    
    with tab3:
        show_user_framework_details("HIPAA", compliance_results['HIPAA'])
    
    with tab4:
        show_user_framework_details("ISO 27001", compliance_results['ISO 27001'])
    
    with tab5:
        show_user_framework_details("NIST", compliance_results['NIST'])
    
    with tab6:
        show_user_framework_details("HI-TRUST", compliance_results['HI-TRUST'])
    
    # User Management Impact Analysis
    st.markdown("---")
    st.subheader("User Management Impact Analysis")
    
    # Calculate user management impact metrics
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
    
    # User Management Effort Analysis
    st.markdown("---")
    st.subheader("User Management Effort Analysis")
    
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
    st.subheader("Export User Management Compliance Analysis")
    
    if st.button("Generate User Management Compliance Report"):
        # Create comprehensive compliance report
        report_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'compliance_frameworks': compliance_results,
            'user_management_impact_summary': {
                'high_impact': high_impact_issues,
                'medium_impact': medium_impact_issues,
                'low_impact': low_impact_issues
            },
            'user_management_effort_summary': {
                'high_effort': high_effort,
                'medium_effort': medium_effort,
                'low_effort': low_effort
            }
        }
        
        # Export as JSON
        json_report = json.dumps(report_data, indent=2)
        st.download_button(
            label="Download User Management Compliance Report (JSON)",
            data=json_report,
            file_name=f"ibm_i_user_management_compliance_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def show_user_framework_details(framework_name: str, framework_data: dict):
    """Display detailed information for a specific compliance framework in user management context"""
    
    st.markdown(f"### {framework_data['name']}")
    st.markdown(f"**Description:** {framework_data['description']}")
    
    # Compliance score gauge
    compliance_score = framework_data['compliance_score']
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = compliance_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"{framework_name} User Management Compliance Score"},
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
    st.markdown("#### User Management Compliance Controls")
    
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
        def get_user_control_link(control_id):
            """Get official control documentation link for user management"""
            links = {
                'SOX-UM-001': 'https://www.sec.gov/about/laws/soa2002.pdf',
                'SOX-UM-002': 'https://www.sec.gov/about/laws/soa2002.pdf',
                'SOX-UM-003': 'https://www.sec.gov/about/laws/soa2002.pdf',
                'SOX-UM-004': 'https://www.sec.gov/about/laws/soa2002.pdf',
                'PCI-UM-001': 'https://www.pcisecuritystandards.org/document_library',
                'PCI-UM-002': 'https://www.pcisecuritystandards.org/document_library',
                'PCI-UM-003': 'https://www.pcisecuritystandards.org/document_library',
                'PCI-UM-004': 'https://www.pcisecuritystandards.org/document_library',
                'HIPAA-UM-001': 'https://www.hhs.gov/hipaa/for-professionals/security/',
                'HIPAA-UM-002': 'https://www.hhs.gov/hipaa/for-professionals/security/',
                'HIPAA-UM-003': 'https://www.hhs.gov/hipaa/for-professionals/security/',
                'HIPAA-UM-004': 'https://www.hhs.gov/hipaa/for-professionals/security/',
                'ISO-UM-001': 'https://www.iso.org/isoiec-27001-information-security.html',
                'ISO-UM-002': 'https://www.iso.org/isoiec-27001-information-security.html',
                'ISO-UM-003': 'https://www.iso.org/isoiec-27001-information-security.html',
                'ISO-UM-004': 'https://www.iso.org/isoiec-27001-information-security.html',
                'NIST-UM-001': 'https://www.nist.gov/cyberframework',
                'NIST-UM-002': 'https://www.nist.gov/cyberframework',
                'NIST-UM-003': 'https://www.nist.gov/cyberframework',
                'NIST-UM-004': 'https://www.nist.gov/cyberframework',
                'HITRUST-UM-001': 'https://hitrustalliance.net/csf/',
                'HITRUST-UM-002': 'https://hitrustalliance.net/csf/',
                'HITRUST-UM-003': 'https://hitrustalliance.net/csf/',
                'HITRUST-UM-004': 'https://hitrustalliance.net/csf/'
            }
            return links.get(control_id, '#')
        
        # Add control links
        display_df['control_link'] = display_df['id'].apply(get_user_control_link)
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
    st.markdown("#### User Management Recommendations")
    
    if framework_data['recommendations']:
        for i, rec in enumerate(framework_data['recommendations'], 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.info("No specific user management recommendations at this time.")

if __name__ == "__main__":
    main()
