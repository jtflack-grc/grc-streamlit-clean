import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import random
import json

# Page configuration
st.set_page_config(
    page_title="Data Privacy Management",
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_subjects' not in st.session_state:
    st.session_state.data_subjects = []
if 'privacy_requests' not in st.session_state:
    st.session_state.privacy_requests = []
if 'data_processing_activities' not in st.session_state:
    st.session_state.data_processing_activities = []
if 'privacy_impact_assessments' not in st.session_state:
    st.session_state.privacy_impact_assessments = []
if 'data_breaches' not in st.session_state:
    st.session_state.data_breaches = []
if 'consent_records' not in st.session_state:
    st.session_state.consent_records = []

def generate_sample_data():
    """Generate sample data privacy management data"""
    data_subjects = [
        {
            'id': 'DS-001',
            'name': 'John Smith',
            'email': 'john.smith@company.com',
            'category': 'Employee',
            'data_types': ['Personal', 'Employment', 'Financial'],
            'consent_status': 'Active',
            'data_retention_date': datetime.datetime.now() + timedelta(days=365),
            'last_updated': datetime.datetime.now() - timedelta(days=30)
        },
        {
            'id': 'DS-002',
            'name': 'Jane Doe',
            'email': 'jane.doe@company.com',
            'category': 'Customer',
            'data_types': ['Personal', 'Financial', 'Transaction'],
            'consent_status': 'Active',
            'data_retention_date': datetime.datetime.now() + timedelta(days=730),
            'last_updated': datetime.datetime.now() - timedelta(days=15)
        },
        {
            'id': 'DS-003',
            'name': 'Bob Johnson',
            'email': 'bob.johnson@company.com',
            'category': 'Vendor',
            'data_types': ['Personal', 'Business'],
            'consent_status': 'Expired',
            'data_retention_date': datetime.datetime.now() + timedelta(days=180),
            'last_updated': datetime.datetime.now() - timedelta(days=60)
        },
        {
            'id': 'DS-004',
            'name': 'Alice Brown',
            'email': 'alice.brown@company.com',
            'category': 'Customer',
            'data_types': ['Personal', 'Marketing'],
            'consent_status': 'Withdrawn',
            'data_retention_date': datetime.datetime.now() + timedelta(days=30),
            'last_updated': datetime.datetime.now() - timedelta(days=7)
        }
    ]
    
    privacy_requests = [
        {
            'id': 'PR-001',
            'data_subject_id': 'DS-001',
            'request_type': 'Access',
            'description': 'Request for personal data access',
            'status': 'Completed',
            'submitted_date': datetime.datetime.now() - timedelta(days=10),
            'completed_date': datetime.datetime.now() - timedelta(days=8),
            'response_time_hours': 48
        },
        {
            'id': 'PR-002',
            'data_subject_id': 'DS-002',
            'request_type': 'Deletion',
            'description': 'Right to be forgotten request',
            'status': 'In Progress',
            'submitted_date': datetime.datetime.now() - timedelta(days=5),
            'completed_date': None,
            'response_time_hours': None
        },
        {
            'id': 'PR-003',
            'data_subject_id': 'DS-003',
            'request_type': 'Correction',
            'description': 'Update personal information',
            'status': 'Completed',
            'submitted_date': datetime.datetime.now() - timedelta(days=15),
            'completed_date': datetime.datetime.now() - timedelta(days=14),
            'response_time_hours': 24
        },
        {
            'id': 'PR-004',
            'data_subject_id': 'DS-004',
            'request_type': 'Portability',
            'description': 'Data portability request',
            'status': 'Pending',
            'submitted_date': datetime.datetime.now() - timedelta(days=2),
            'completed_date': None,
            'response_time_hours': None
        }
    ]
    
    data_processing_activities = [
        {
            'id': 'DPA-001',
            'activity_name': 'Employee Payroll Processing',
            'description': 'Processing employee salary and benefits data',
            'legal_basis': 'Contract',
            'data_categories': ['Personal', 'Financial', 'Employment'],
            'retention_period': '7 years',
            'risk_level': 'Medium',
            'status': 'Active'
        },
        {
            'id': 'DPA-002',
            'activity_name': 'Customer Marketing',
            'description': 'Marketing communications and analytics',
            'legal_basis': 'Consent',
            'data_categories': ['Personal', 'Marketing', 'Behavioral'],
            'retention_period': '2 years',
            'risk_level': 'Low',
            'status': 'Active'
        },
        {
            'id': 'DPA-003',
            'activity_name': 'Vendor Management',
            'description': 'Third-party vendor relationship management',
            'legal_basis': 'Legitimate Interest',
            'data_categories': ['Personal', 'Business'],
            'retention_period': '5 years',
            'risk_level': 'Medium',
            'status': 'Active'
        },
        {
            'id': 'DPA-004',
            'activity_name': 'Security Monitoring',
            'description': 'IT security and access monitoring',
            'legal_basis': 'Legitimate Interest',
            'data_categories': ['Personal', 'Technical'],
            'retention_period': '1 year',
            'risk_level': 'High',
            'status': 'Active'
        }
    ]
    
    privacy_impact_assessments = [
        {
            'id': 'PIA-001',
            'activity_id': 'DPA-001',
            'assessment_date': datetime.datetime.now() - timedelta(days=90),
            'risk_score': 6,
            'risk_level': 'Medium',
            'findings': ['Data encryption required', 'Access controls need review'],
            'status': 'Completed',
            'next_review': datetime.datetime.now() + timedelta(days=275)
        },
        {
            'id': 'PIA-002',
            'activity_id': 'DPA-002',
            'assessment_date': datetime.datetime.now() - timedelta(days=60),
            'risk_score': 4,
            'risk_level': 'Low',
            'findings': ['Consent mechanism needs improvement'],
            'status': 'In Progress',
            'next_review': datetime.datetime.now() + timedelta(days=305)
        },
        {
            'id': 'PIA-003',
            'activity_id': 'DPA-003',
            'assessment_date': datetime.datetime.now() - timedelta(days=30),
            'risk_score': 7,
            'risk_level': 'Medium',
            'findings': ['Data sharing agreements need updates'],
            'status': 'Completed',
            'next_review': datetime.datetime.now() + timedelta(days=335)
        }
    ]
    
    data_breaches = [
        {
            'id': 'DB-001',
            'incident_date': datetime.datetime.now() - timedelta(days=45),
            'discovery_date': datetime.datetime.now() - timedelta(days=44),
            'breach_type': 'Unauthorized Access',
            'affected_records': 150,
            'severity': 'Medium',
            'status': 'Resolved',
            'notification_required': False,
            'regulatory_reporting': False
        },
        {
            'id': 'DB-002',
            'incident_date': datetime.datetime.now() - timedelta(days=90),
            'discovery_date': datetime.datetime.now() - timedelta(days=89),
            'breach_type': 'Data Loss',
            'affected_records': 25,
            'severity': 'Low',
            'status': 'Resolved',
            'notification_required': False,
            'regulatory_reporting': False
        },
        {
            'id': 'DB-003',
            'incident_date': datetime.datetime.now() - timedelta(days=15),
            'discovery_date': datetime.datetime.now() - timedelta(days=14),
            'breach_type': 'System Compromise',
            'affected_records': 500,
            'severity': 'High',
            'status': 'Under Investigation',
            'notification_required': True,
            'regulatory_reporting': True
        }
    ]
    
    consent_records = [
        {
            'id': 'CR-001',
            'data_subject_id': 'DS-001',
            'consent_type': 'Marketing Communications',
            'consent_date': datetime.datetime.now() - timedelta(days=365),
            'consent_status': 'Active',
            'withdrawal_date': None,
            'consent_method': 'Online Form'
        },
        {
            'id': 'CR-002',
            'data_subject_id': 'DS-002',
            'consent_type': 'Data Processing',
            'consent_date': datetime.datetime.now() - timedelta(days=180),
            'consent_status': 'Active',
            'withdrawal_date': None,
            'consent_method': 'Email'
        },
        {
            'id': 'CR-003',
            'data_subject_id': 'DS-003',
            'consent_type': 'Third-party Sharing',
            'consent_date': datetime.datetime.now() - timedelta(days=730),
            'consent_status': 'Expired',
            'withdrawal_date': None,
            'consent_method': 'Contract'
        },
        {
            'id': 'CR-004',
            'data_subject_id': 'DS-004',
            'consent_type': 'Marketing Communications',
            'consent_date': datetime.datetime.now() - timedelta(days=90),
            'consent_status': 'Withdrawn',
            'withdrawal_date': datetime.datetime.now() - timedelta(days=7),
            'consent_method': 'Online Form'
        }
    ]
    
    return data_subjects, privacy_requests, data_processing_activities, privacy_impact_assessments, data_breaches, consent_records

def main():
    st.markdown('<h1 class="main-header">Data Privacy Management</h1>', unsafe_allow_html=True)
    st.markdown("Comprehensive platform for managing data privacy compliance, data subject rights, privacy impact assessments, and GDPR/CCPA compliance")
    
    # Initialize sample data
    if not st.session_state.data_subjects:
        subjects, requests, activities, pias, breaches, consents = generate_sample_data()
        st.session_state.data_subjects = subjects
        st.session_state.privacy_requests = requests
        st.session_state.data_processing_activities = activities
        st.session_state.privacy_impact_assessments = pias
        st.session_state.data_breaches = breaches
        st.session_state.consent_records = consents
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Dashboard", "Data Subject Management", "Privacy Requests", "Data Processing Activities", "Privacy Impact Assessments", "Data Breaches", "Consent Management", "Reports"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Data Subject Management":
        show_data_subject_management()
    elif page == "Privacy Requests":
        show_privacy_requests()
    elif page == "Data Processing Activities":
        show_data_processing_activities()
    elif page == "Privacy Impact Assessments":
        show_privacy_impact_assessments()
    elif page == "Data Breaches":
        show_data_breaches()
    elif page == "Consent Management":
        show_consent_management()
    elif page == "Reports":
        show_reports()

def show_dashboard():
    st.header("Privacy Dashboard")
    
    # Calculate key metrics
    total_subjects = len(st.session_state.data_subjects)
    active_consents = len([s for s in st.session_state.data_subjects if s['consent_status'] == 'Active'])
    pending_requests = len([r for r in st.session_state.privacy_requests if r['status'] == 'Pending'])
    active_breaches = len([b for b in st.session_state.data_breaches if b['status'] == 'Under Investigation'])
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Data Subjects", total_subjects)
        st.metric("Active Consents", active_consents, f"{active_consents}/{total_subjects}")
    
    with col2:
        st.metric("Pending Requests", pending_requests)
        avg_response_time = np.mean([r['response_time_hours'] for r in st.session_state.privacy_requests if r['response_time_hours']])
        st.metric("Avg Response Time", f"{avg_response_time:.1f} hours")
    
    with col3:
        st.metric("Active Breaches", active_breaches)
        total_activities = len(st.session_state.data_processing_activities)
        st.metric("Processing Activities", total_activities)
    
    with col4:
        completed_pias = len([p for p in st.session_state.privacy_impact_assessments if p['status'] == 'Completed'])
        st.metric("Completed PIAs", completed_pias)
        avg_risk_score = np.mean([p['risk_score'] for p in st.session_state.privacy_impact_assessments])
        st.metric("Avg Risk Score", f"{avg_risk_score:.1f}/10")
    
    # Dashboard charts
    st.subheader("Privacy Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Consent status distribution
        consent_counts = pd.DataFrame(st.session_state.data_subjects)['consent_status'].value_counts()
        fig = px.pie(values=consent_counts.values, names=consent_counts.index, 
                    title="Data Subject Consent Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Request status distribution
        request_counts = pd.DataFrame(st.session_state.privacy_requests)['status'].value_counts()
        fig = px.bar(x=request_counts.index, y=request_counts.values, 
                    title="Privacy Request Status")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent privacy requests
    st.subheader("Recent Privacy Requests")
    recent_requests = sorted(st.session_state.privacy_requests, key=lambda x: x['submitted_date'], reverse=True)[:5]
    
    for request in recent_requests:
        subject = next((s for s in st.session_state.data_subjects if s['id'] == request['data_subject_id']), None)
        
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"**{subject['name'] if subject else 'Unknown Subject'}**")
        with col2:
            st.write(f"**{request['request_type']}** - {request['description']}")
        with col3:
            if request['status'] == 'Completed':
                st.write("Completed")
            elif request['status'] == 'In Progress':
                st.write("Active")
            else:
                st.write("Pending")
        with col4:
            st.write(f"{request['submitted_date'].strftime('%m/%d')}")
        st.divider()

def show_data_subject_management():
    st.header("Data Subject Management")
    
    # Add new data subject
    with st.expander("Add New Data Subject"):
        with st.form("new_subject"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
                email = st.text_input("Email")
                category = st.selectbox("Category", ["Employee", "Customer", "Vendor", "Partner", "Other"])
            with col2:
                data_types = st.multiselect("Data Types", ["Personal", "Financial", "Employment", "Marketing", "Transaction", "Business", "Technical"])
                consent_status = st.selectbox("Consent Status", ["Active", "Expired", "Withdrawn", "Pending"])
                retention_date = st.date_input("Data Retention Date")
            
            if st.form_submit_button("Add Data Subject"):
                new_subject = {
                    'id': f'DS-{len(st.session_state.data_subjects)+1:03d}',
                    'name': name,
                    'email': email,
                    'category': category,
                    'data_types': data_types,
                    'consent_status': consent_status,
                    'data_retention_date': datetime.datetime.combine(retention_date, datetime.time()),
                    'last_updated': datetime.datetime.now()
                }
                st.session_state.data_subjects.append(new_subject)
                st.success("Data subject added successfully!")
    
    # Display data subjects
    df = pd.DataFrame(st.session_state.data_subjects)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(df['category'].unique()))
    with col2:
        consent_filter = st.selectbox("Filter by Consent Status", ["All"] + list(df['consent_status'].unique()))
    with col3:
        search_term = st.text_input("Search by name or email")
    
    # Apply filters
    filtered_df = df.copy()
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    if consent_filter != "All":
        filtered_df = filtered_df[filtered_df['consent_status'] == consent_filter]
    if search_term:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False) |
            filtered_df['email'].str.contains(search_term, case=False)
        ]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Data subject analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Subjects by Category")
        category_counts = filtered_df['category'].value_counts()
        fig = px.bar(x=category_counts.index, y=category_counts.values, 
                    title="Data Subjects by Category")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Consent Status Distribution")
        consent_counts = filtered_df['consent_status'].value_counts()
        fig = px.pie(values=consent_counts.values, names=consent_counts.index, 
                    title="Consent Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_privacy_requests():
    st.header("Privacy Request Management")
    
    # Add new privacy request
    with st.expander("Add New Privacy Request"):
        with st.form("new_request"):
            col1, col2 = st.columns(2)
            with col1:
                data_subject_id = st.selectbox("Data Subject", [s['id'] for s in st.session_state.data_subjects])
                request_type = st.selectbox("Request Type", ["Access", "Deletion", "Correction", "Portability", "Objection"])
                description = st.text_area("Description")
            with col2:
                status = st.selectbox("Status", ["Pending", "In Progress", "Completed", "Rejected"])
                submitted_date = st.date_input("Submitted Date")
            
            if st.form_submit_button("Add Request"):
                new_request = {
                    'id': f'PR-{len(st.session_state.privacy_requests)+1:03d}',
                    'data_subject_id': data_subject_id,
                    'request_type': request_type,
                    'description': description,
                    'status': status,
                    'submitted_date': datetime.datetime.combine(submitted_date, datetime.time()),
                    'completed_date': None,
                    'response_time_hours': None
                }
                st.session_state.privacy_requests.append(new_request)
                st.success("Privacy request added successfully!")
    
    # Display privacy requests
    df = pd.DataFrame(st.session_state.privacy_requests)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['request_type'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        date_filter = st.date_input("Filter by Date")
    
    # Apply filters
    filtered_df = df.copy()
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['request_type'] == type_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if date_filter:
        filtered_df = filtered_df[filtered_df['submitted_date'].dt.date == date_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Request analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Requests by Type")
        type_counts = filtered_df['request_type'].value_counts()
        fig = px.bar(x=type_counts.index, y=type_counts.values, 
                    title="Privacy Requests by Type")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Request Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Request Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_data_processing_activities():
    st.header("Data Processing Activities")
    
    # Add new activity
    with st.expander("Add New Processing Activity"):
        with st.form("new_activity"):
            col1, col2 = st.columns(2)
            with col1:
                activity_name = st.text_input("Activity Name")
                description = st.text_area("Description")
                legal_basis = st.selectbox("Legal Basis", ["Consent", "Contract", "Legitimate Interest", "Legal Obligation", "Vital Interest", "Public Task"])
            with col2:
                data_categories = st.multiselect("Data Categories", ["Personal", "Financial", "Employment", "Marketing", "Transaction", "Business", "Technical"])
                retention_period = st.text_input("Retention Period")
                risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
                status = st.selectbox("Status", ["Active", "Inactive", "Under Review"])
            
            if st.form_submit_button("Add Activity"):
                new_activity = {
                    'id': f'DPA-{len(st.session_state.data_processing_activities)+1:03d}',
                    'activity_name': activity_name,
                    'description': description,
                    'legal_basis': legal_basis,
                    'data_categories': data_categories,
                    'retention_period': retention_period,
                    'risk_level': risk_level,
                    'status': status
                }
                st.session_state.data_processing_activities.append(new_activity)
                st.success("Processing activity added successfully!")
    
    # Display activities
    df = pd.DataFrame(st.session_state.data_processing_activities)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        basis_filter = st.selectbox("Filter by Legal Basis", ["All"] + list(df['legal_basis'].unique()))
    with col2:
        risk_filter = st.selectbox("Filter by Risk Level", ["All"] + list(df['risk_level'].unique()))
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if basis_filter != "All":
        filtered_df = filtered_df[filtered_df['legal_basis'] == basis_filter]
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Activity analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Activities by Legal Basis")
        basis_counts = filtered_df['legal_basis'].value_counts()
        fig = px.bar(x=basis_counts.index, y=basis_counts.values, 
                    title="Processing Activities by Legal Basis")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Risk Level Distribution")
        risk_counts = filtered_df['risk_level'].value_counts()
        fig = px.pie(values=risk_counts.values, names=risk_counts.index, 
                    title="Risk Level Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_privacy_impact_assessments():
    st.header("Privacy Impact Assessments")
    
    # Add new PIA
    with st.expander("Add New PIA"):
        with st.form("new_pia"):
            col1, col2 = st.columns(2)
            with col1:
                activity_id = st.selectbox("Processing Activity", [a['id'] for a in st.session_state.data_processing_activities])
                assessment_date = st.date_input("Assessment Date")
                risk_score = st.slider("Risk Score", 1, 10, 5)
            with col2:
                risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
                findings = st.text_area("Findings (comma-separated)")
                status = st.selectbox("Status", ["Draft", "In Progress", "Completed", "Under Review"])
                next_review = st.date_input("Next Review Date")
            
            if st.form_submit_button("Add PIA"):
                new_pia = {
                    'id': f'PIA-{len(st.session_state.privacy_impact_assessments)+1:03d}',
                    'activity_id': activity_id,
                    'assessment_date': datetime.datetime.combine(assessment_date, datetime.time()),
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'findings': [f.strip() for f in findings.split(',')] if findings else [],
                    'status': status,
                    'next_review': datetime.datetime.combine(next_review, datetime.time())
                }
                st.session_state.privacy_impact_assessments.append(new_pia)
                st.success("PIA added successfully!")
    
    # Display PIAs
    df = pd.DataFrame(st.session_state.privacy_impact_assessments)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        risk_filter = st.selectbox("Filter by Risk Level", ["All"] + list(df['risk_level'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        score_filter = st.slider("Risk Score Range", 1, 10, (1, 10))
    
    # Apply filters
    filtered_df = df.copy()
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    filtered_df = filtered_df[(filtered_df['risk_score'] >= score_filter[0]) & (filtered_df['risk_score'] <= score_filter[1])]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # PIA analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Score Distribution")
        fig = px.histogram(filtered_df, x='risk_score', nbins=10, 
                          title="Risk Score Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("PIA Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="PIA Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_data_breaches():
    st.header("Data Breach Management")
    
    # Add new breach
    with st.expander("Add New Data Breach"):
        with st.form("new_breach"):
            col1, col2 = st.columns(2)
            with col1:
                incident_date = st.date_input("Incident Date")
                discovery_date = st.date_input("Discovery Date")
                breach_type = st.selectbox("Breach Type", ["Unauthorized Access", "Data Loss", "System Compromise", "Malware", "Phishing", "Other"])
            with col2:
                affected_records = st.number_input("Affected Records", min_value=1, value=1)
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                status = st.selectbox("Status", ["Under Investigation", "Contained", "Resolved", "Closed"])
                notification_required = st.checkbox("Notification Required")
                regulatory_reporting = st.checkbox("Regulatory Reporting Required")
            
            if st.form_submit_button("Add Breach"):
                new_breach = {
                    'id': f'DB-{len(st.session_state.data_breaches)+1:03d}',
                    'incident_date': datetime.datetime.combine(incident_date, datetime.time()),
                    'discovery_date': datetime.datetime.combine(discovery_date, datetime.time()),
                    'breach_type': breach_type,
                    'affected_records': affected_records,
                    'severity': severity,
                    'status': status,
                    'notification_required': notification_required,
                    'regulatory_reporting': regulatory_reporting
                }
                st.session_state.data_breaches.append(new_breach)
                st.success("Data breach added successfully!")
    
    # Display breaches
    df = pd.DataFrame(st.session_state.data_breaches)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['breach_type'].unique()))
    with col2:
        severity_filter = st.selectbox("Filter by Severity", ["All"] + list(df['severity'].unique()))
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['breach_type'] == type_filter]
    if severity_filter != "All":
        filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Breach analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Breaches by Type")
        type_counts = filtered_df['breach_type'].value_counts()
        fig = px.bar(x=type_counts.index, y=type_counts.values, 
                    title="Data Breaches by Type")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Breach Severity Distribution")
        severity_counts = filtered_df['severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index, 
                    title="Breach Severity Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_consent_management():
    st.header("Consent Management")
    
    # Add new consent record
    with st.expander("Add New Consent Record"):
        with st.form("new_consent"):
            col1, col2 = st.columns(2)
            with col1:
                data_subject_id = st.selectbox("Data Subject", [s['id'] for s in st.session_state.data_subjects])
                consent_type = st.text_input("Consent Type")
                consent_date = st.date_input("Consent Date")
            with col2:
                consent_status = st.selectbox("Consent Status", ["Active", "Expired", "Withdrawn"])
                withdrawal_date = st.date_input("Withdrawal Date (if applicable)")
                consent_method = st.selectbox("Consent Method", ["Online Form", "Email", "Contract", "Phone", "In-Person"])
            
            if st.form_submit_button("Add Consent"):
                new_consent = {
                    'id': f'CR-{len(st.session_state.consent_records)+1:03d}',
                    'data_subject_id': data_subject_id,
                    'consent_type': consent_type,
                    'consent_date': datetime.datetime.combine(consent_date, datetime.time()),
                    'consent_status': consent_status,
                    'withdrawal_date': datetime.datetime.combine(withdrawal_date, datetime.time()) if withdrawal_date else None,
                    'consent_method': consent_method
                }
                st.session_state.consent_records.append(new_consent)
                st.success("Consent record added successfully!")
    
    # Display consent records
    df = pd.DataFrame(st.session_state.consent_records)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Consent Type", ["All"] + list(df['consent_type'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['consent_status'].unique()))
    with col3:
        method_filter = st.selectbox("Filter by Method", ["All"] + list(df['consent_method'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['consent_type'] == type_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['consent_status'] == status_filter]
    if method_filter != "All":
        filtered_df = filtered_df[filtered_df['consent_method'] == method_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Consent analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Consent Status Distribution")
        status_counts = filtered_df['consent_status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Consent Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Consent by Method")
        method_counts = filtered_df['consent_method'].value_counts()
        fig = px.bar(x=method_counts.index, y=method_counts.values, 
                    title="Consent Collection Methods")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("Privacy Reports")
    
    # Report options
    report_type = st.selectbox("Select Report Type", [
        "Privacy Compliance Summary",
        "Data Subject Rights Report",
        "Processing Activities Report",
        "Breach Incident Report",
        "Consent Management Report",
        "Regulatory Compliance Report"
    ])
    
    if report_type == "Privacy Compliance Summary":
        st.subheader("Privacy Compliance Summary")
        
        # Calculate summary metrics
        total_subjects = len(st.session_state.data_subjects)
        active_consents = len([s for s in st.session_state.data_subjects if s['consent_status'] == 'Active'])
        pending_requests = len([r for r in st.session_state.privacy_requests if r['status'] == 'Pending'])
        active_breaches = len([b for b in st.session_state.data_breaches if b['status'] == 'Under Investigation'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Data Subject Overview**")
            st.write(f"• Total Data Subjects: {total_subjects}")
            st.write(f"• Active Consents: {active_consents}")
            st.write(f"• Consent Rate: {(active_consents/total_subjects*100):.1f}%")
            st.write(f"• Pending Requests: {pending_requests}")
        
        with col2:
            st.write("**Compliance Status**")
            st.write(f"• Active Breaches: {active_breaches}")
            st.write(f"• Processing Activities: {len(st.session_state.data_processing_activities)}")
            st.write(f"• Completed PIAs: {len([p for p in st.session_state.privacy_impact_assessments if p['status'] == 'Completed'])}")
            st.write(f"• Overall Compliance: Strong")
    
    # Export functionality
    st.subheader("Export Data")
    export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
    
    if st.button("Export Privacy Data"):
        if export_format == "CSV":
            df_subjects = pd.DataFrame(st.session_state.data_subjects)
            csv = df_subjects.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="data_privacy_subjects.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
