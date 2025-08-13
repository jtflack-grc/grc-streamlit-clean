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
    page_title="Third-Party Risk Management",
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
if 'vendors' not in st.session_state:
    st.session_state.vendors = []
if 'vendor_assessments' not in st.session_state:
    st.session_state.vendor_assessments = []
if 'vendor_contracts' not in st.session_state:
    st.session_state.vendor_contracts = []
if 'vendor_incidents' not in st.session_state:
    st.session_state.vendor_incidents = []
if 'vendor_categories' not in st.session_state:
    st.session_state.vendor_categories = []
if 'vendor_contacts' not in st.session_state:
    st.session_state.vendor_contacts = []

def generate_sample_data():
    """Generate sample third-party risk management data"""
    vendors = [
        {
            'id': 'VND-001',
            'name': 'CloudTech Solutions',
            'category': 'Cloud Services',
            'description': 'Cloud infrastructure and hosting services',
            'risk_level': 'Medium',
            'contract_value': 500000,
            'contract_start': datetime.datetime.now() - timedelta(days=365),
            'contract_end': datetime.datetime.now() + timedelta(days=730),
            'status': 'Active',
            'last_assessment': datetime.datetime.now() - timedelta(days=90)
        },
        {
            'id': 'VND-002',
            'name': 'SecureSoft Inc',
            'category': 'Software Vendor',
            'description': 'Security software and tools',
            'risk_level': 'High',
            'contract_value': 250000,
            'contract_start': datetime.datetime.now() - timedelta(days=180),
            'contract_end': datetime.datetime.now() + timedelta(days=545),
            'status': 'Active',
            'last_assessment': datetime.datetime.now() - timedelta(days=60)
        },
        {
            'id': 'VND-003',
            'name': 'DataFlow Systems',
            'category': 'Data Processing',
            'description': 'Data analytics and processing services',
            'risk_level': 'Critical',
            'contract_value': 750000,
            'contract_start': datetime.datetime.now() - timedelta(days=90),
            'contract_end': datetime.datetime.now() + timedelta(days=635),
            'status': 'Active',
            'last_assessment': datetime.datetime.now() - timedelta(days=30)
        },
        {
            'id': 'VND-004',
            'name': 'IT Support Pro',
            'category': 'IT Services',
            'description': 'IT support and maintenance services',
            'risk_level': 'Low',
            'contract_value': 100000,
            'contract_start': datetime.datetime.now() - timedelta(days=730),
            'contract_end': datetime.datetime.now() + timedelta(days=365),
            'status': 'Active',
            'last_assessment': datetime.datetime.now() - timedelta(days=120)
        }
    ]
    
    vendor_assessments = [
        {
            'id': 'VA-001',
            'vendor_id': 'VND-001',
            'assessment_date': datetime.datetime.now() - timedelta(days=90),
            'security_score': 85,
            'compliance_score': 90,
            'financial_score': 95,
            'operational_score': 88,
            'overall_score': 89.5,
            'risk_level': 'Medium',
            'status': 'Completed',
            'next_assessment': datetime.datetime.now() + timedelta(days=275)
        },
        {
            'id': 'VA-002',
            'vendor_id': 'VND-002',
            'assessment_date': datetime.datetime.now() - timedelta(days=60),
            'security_score': 92,
            'compliance_score': 88,
            'financial_score': 85,
            'operational_score': 90,
            'overall_score': 88.8,
            'risk_level': 'High',
            'status': 'Completed',
            'next_assessment': datetime.datetime.now() + timedelta(days=305)
        },
        {
            'id': 'VA-003',
            'vendor_id': 'VND-003',
            'assessment_date': datetime.datetime.now() - timedelta(days=30),
            'security_score': 78,
            'compliance_score': 82,
            'financial_score': 88,
            'operational_score': 85,
            'overall_score': 83.3,
            'risk_level': 'Critical',
            'status': 'In Progress',
            'next_assessment': datetime.datetime.now() + timedelta(days=335)
        },
        {
            'id': 'VA-004',
            'vendor_id': 'VND-004',
            'assessment_date': datetime.datetime.now() - timedelta(days=120),
            'security_score': 95,
            'compliance_score': 92,
            'financial_score': 90,
            'operational_score': 93,
            'overall_score': 92.5,
            'risk_level': 'Low',
            'status': 'Completed',
            'next_assessment': datetime.datetime.now() + timedelta(days=245)
        }
    ]
    
    vendor_contracts = [
        {
            'id': 'VC-001',
            'vendor_id': 'VND-001',
            'contract_number': 'CTR-2024-001',
            'contract_type': 'Service Agreement',
            'start_date': datetime.datetime.now() - timedelta(days=365),
            'end_date': datetime.datetime.now() + timedelta(days=730),
            'value': 500000,
            'currency': 'USD',
            'auto_renewal': True,
            'termination_notice': 90,
            'status': 'Active'
        },
        {
            'id': 'VC-002',
            'vendor_id': 'VND-002',
            'contract_number': 'CTR-2024-002',
            'contract_type': 'License Agreement',
            'start_date': datetime.datetime.now() - timedelta(days=180),
            'end_date': datetime.datetime.now() + timedelta(days=545),
            'value': 250000,
            'currency': 'USD',
            'auto_renewal': False,
            'termination_notice': 60,
            'status': 'Active'
        },
        {
            'id': 'VC-003',
            'vendor_id': 'VND-003',
            'contract_number': 'CTR-2024-003',
            'contract_type': 'Service Agreement',
            'start_date': datetime.datetime.now() - timedelta(days=90),
            'end_date': datetime.datetime.now() + timedelta(days=635),
            'value': 750000,
            'currency': 'USD',
            'auto_renewal': True,
            'termination_notice': 120,
            'status': 'Active'
        },
        {
            'id': 'VC-004',
            'vendor_id': 'VND-004',
            'contract_number': 'CTR-2023-004',
            'contract_type': 'Service Agreement',
            'start_date': datetime.datetime.now() - timedelta(days=730),
            'end_date': datetime.datetime.now() + timedelta(days=365),
            'value': 100000,
            'currency': 'USD',
            'auto_renewal': True,
            'termination_notice': 30,
            'status': 'Active'
        }
    ]
    
    vendor_incidents = [
        {
            'id': 'VI-001',
            'vendor_id': 'VND-001',
            'incident_date': datetime.datetime.now() - timedelta(days=45),
            'incident_type': 'Service Outage',
            'severity': 'Medium',
            'description': 'Cloud service interruption affecting 2% of users',
            'impact': 'Limited service disruption',
            'resolution_time': 4,
            'status': 'Resolved'
        },
        {
            'id': 'VI-002',
            'vendor_id': 'VND-002',
            'incident_date': datetime.datetime.now() - timedelta(days=30),
            'incident_type': 'Security Breach',
            'severity': 'High',
            'description': 'Unauthorized access to vendor systems',
            'impact': 'Potential data exposure',
            'resolution_time': 72,
            'status': 'Under Investigation'
        },
        {
            'id': 'VI-003',
            'vendor_id': 'VND-003',
            'incident_date': datetime.datetime.now() - timedelta(days=15),
            'incident_type': 'Data Processing Error',
            'severity': 'Low',
            'description': 'Minor data processing delay',
            'impact': 'Slight delay in reporting',
            'resolution_time': 2,
            'status': 'Resolved'
        }
    ]
    
    vendor_categories = [
        {
            'id': 'CAT-001',
            'name': 'Cloud Services',
            'description': 'Cloud infrastructure and hosting providers',
            'risk_weight': 0.8,
            'assessment_frequency': 'Quarterly',
            'total_vendors': 1
        },
        {
            'id': 'CAT-002',
            'name': 'Software Vendor',
            'description': 'Software and application providers',
            'risk_weight': 0.9,
            'assessment_frequency': 'Quarterly',
            'total_vendors': 1
        },
        {
            'id': 'CAT-003',
            'name': 'Data Processing',
            'description': 'Data analytics and processing services',
            'risk_weight': 1.0,
            'assessment_frequency': 'Monthly',
            'total_vendors': 1
        },
        {
            'id': 'CAT-004',
            'name': 'IT Services',
            'description': 'IT support and maintenance services',
            'risk_weight': 0.6,
            'assessment_frequency': 'Semi-annually',
            'total_vendors': 1
        }
    ]
    
    vendor_contacts = [
        {
            'id': 'VCT-001',
            'vendor_id': 'VND-001',
            'name': 'John Smith',
            'title': 'Account Manager',
            'email': 'john.smith@cloudtech.com',
            'phone': '+1-555-0101',
            'primary_contact': True
        },
        {
            'id': 'VCT-002',
            'vendor_id': 'VND-002',
            'name': 'Sarah Johnson',
            'title': 'Security Officer',
            'email': 'sarah.johnson@securesoft.com',
            'phone': '+1-555-0102',
            'primary_contact': True
        },
        {
            'id': 'VCT-003',
            'vendor_id': 'VND-003',
            'name': 'Mike Davis',
            'title': 'Operations Director',
            'email': 'mike.davis@dataflow.com',
            'phone': '+1-555-0103',
            'primary_contact': True
        },
        {
            'id': 'VCT-004',
            'vendor_id': 'VND-004',
            'name': 'Lisa Wilson',
            'title': 'Service Manager',
            'email': 'lisa.wilson@itsupport.com',
            'phone': '+1-555-0104',
            'primary_contact': True
        }
    ]
    
    return vendors, vendor_assessments, vendor_contracts, vendor_incidents, vendor_categories, vendor_contacts

def main():
    st.markdown('<h1 class="main-header">Third-Party Risk Management</h1>', unsafe_allow_html=True)
    st.markdown("Comprehensive platform for managing vendor relationships, assessing third-party risks, and ensuring compliance with vendor management requirements")
    
    # Initialize sample data
    if not st.session_state.vendors:
        vendors, assessments, contracts, incidents, categories, contacts = generate_sample_data()
        st.session_state.vendors = vendors
        st.session_state.vendor_assessments = assessments
        st.session_state.vendor_contracts = contracts
        st.session_state.vendor_incidents = incidents
        st.session_state.vendor_categories = categories
        st.session_state.vendor_contacts = contacts
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Dashboard", "Vendor Management", "Risk Assessments", "Contract Management", "Incident Tracking", "Category Management", "Contact Management", "Reports"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Vendor Management":
        show_vendor_management()
    elif page == "Risk Assessments":
        show_risk_assessments()
    elif page == "Contract Management":
        show_contract_management()
    elif page == "Incident Tracking":
        show_incident_tracking()
    elif page == "Category Management":
        show_category_management()
    elif page == "Contact Management":
        show_contact_management()
    elif page == "Reports":
        show_reports()

def show_dashboard():
    st.header("Vendor Risk Dashboard")
    
    # Calculate key metrics
    total_vendors = len(st.session_state.vendors)
    active_vendors = len([v for v in st.session_state.vendors if v['status'] == 'Active'])
    critical_risk = len([v for v in st.session_state.vendors if v['risk_level'] == 'Critical'])
    high_risk = len([v for v in st.session_state.vendors if v['risk_level'] == 'High'])
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Vendors", total_vendors)
        st.metric("Active Vendors", active_vendors, f"{active_vendors}/{total_vendors}")
    
    with col2:
        st.metric("Critical Risk", critical_risk)
        st.metric("High Risk", high_risk)
    
    with col3:
        total_contract_value = sum([v['contract_value'] for v in st.session_state.vendors])
        st.metric("Total Contract Value", f"${total_contract_value:,}")
        avg_assessment_score = np.mean([a['overall_score'] for a in st.session_state.vendor_assessments])
        st.metric("Avg Assessment Score", f"{avg_assessment_score:.1f}")
    
    with col4:
        active_incidents = len([i for i in st.session_state.vendor_incidents if i['status'] == 'Under Investigation'])
        st.metric("Active Incidents", active_incidents)
        overdue_assessments = len([v for v in st.session_state.vendors if v['last_assessment'] < datetime.datetime.now() - timedelta(days=365)])
        st.metric("Overdue Assessments", overdue_assessments)
    
    # Dashboard charts
    st.subheader("Vendor Risk Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk level distribution
        risk_counts = pd.DataFrame(st.session_state.vendors)['risk_level'].value_counts()
        fig = px.pie(values=risk_counts.values, names=risk_counts.index, 
                    title="Vendors by Risk Level")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category distribution
        category_counts = pd.DataFrame(st.session_state.vendors)['category'].value_counts()
        fig = px.bar(x=category_counts.index, y=category_counts.values, 
                    title="Vendors by Category")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent vendor incidents
    st.subheader("Recent Vendor Incidents")
    recent_incidents = sorted(st.session_state.vendor_incidents, key=lambda x: x['incident_date'], reverse=True)[:5]
    
    for incident in recent_incidents:
        vendor = next((v for v in st.session_state.vendors if v['id'] == incident['vendor_id']), None)
        
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"**{vendor['name'] if vendor else 'Unknown Vendor'}**")
        with col2:
            st.write(f"**{incident['incident_type']}** - {incident['description']}")
        with col3:
            if incident['severity'] == 'Critical':
                st.write("Critical")
            elif incident['severity'] == 'High':
                st.write("High")
            else:
                st.write("Medium")
        with col4:
            if incident['status'] == 'Resolved':
                st.write("Resolved")
            else:
                st.write("Active")
        st.divider()

def show_vendor_management():
    st.header("Vendor Management")
    
    # Add new vendor
    with st.expander("Add New Vendor"):
        with st.form("new_vendor"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Vendor Name")
                category = st.selectbox("Category", [c['name'] for c in st.session_state.vendor_categories])
                description = st.text_area("Description")
                risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
            with col2:
                contract_value = st.number_input("Contract Value ($)", min_value=0, value=100000)
                contract_start = st.date_input("Contract Start Date")
                contract_end = st.date_input("Contract End Date")
                status = st.selectbox("Status", ["Active", "Inactive", "Under Review", "Terminated"])
            
            if st.form_submit_button("Add Vendor"):
                new_vendor = {
                    'id': f'VND-{len(st.session_state.vendors)+1:03d}',
                    'name': name,
                    'category': category,
                    'description': description,
                    'risk_level': risk_level,
                    'contract_value': contract_value,
                    'contract_start': datetime.datetime.combine(contract_start, datetime.time()),
                    'contract_end': datetime.datetime.combine(contract_end, datetime.time()),
                    'status': status,
                    'last_assessment': datetime.datetime.now()
                }
                st.session_state.vendors.append(new_vendor)
                st.success("Vendor added successfully!")
    
    # Display vendors
    df = pd.DataFrame(st.session_state.vendors)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(df['category'].unique()))
    with col2:
        risk_filter = st.selectbox("Filter by Risk Level", ["All"] + list(df['risk_level'].unique()))
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Vendor analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vendors by Risk Level")
        risk_counts = filtered_df['risk_level'].value_counts()
        fig = px.bar(x=risk_counts.index, y=risk_counts.values, 
                    title="Vendors by Risk Level",
                    color=risk_counts.index,
                    color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Contract Value by Category")
        value_by_category = filtered_df.groupby('category')['contract_value'].sum().reset_index()
        fig = px.pie(values=value_by_category['contract_value'], names=value_by_category['category'], 
                    title="Contract Value Distribution by Category")
        st.plotly_chart(fig, use_container_width=True)

def show_risk_assessments():
    st.header("Risk Assessments")
    
    # Add new assessment
    with st.expander("Add New Assessment"):
        with st.form("new_assessment"):
            col1, col2 = st.columns(2)
            with col1:
                vendor_id = st.selectbox("Vendor", [v['id'] for v in st.session_state.vendors])
                assessment_date = st.date_input("Assessment Date")
                security_score = st.slider("Security Score", 0, 100, 85)
                compliance_score = st.slider("Compliance Score", 0, 100, 90)
            with col2:
                financial_score = st.slider("Financial Score", 0, 100, 85)
                operational_score = st.slider("Operational Score", 0, 100, 88)
                risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
                status = st.selectbox("Status", ["Draft", "In Progress", "Completed", "Under Review"])
                next_assessment = st.date_input("Next Assessment Date")
            
            if st.form_submit_button("Add Assessment"):
                overall_score = (security_score + compliance_score + financial_score + operational_score) / 4
                new_assessment = {
                    'id': f'VA-{len(st.session_state.vendor_assessments)+1:03d}',
                    'vendor_id': vendor_id,
                    'assessment_date': datetime.datetime.combine(assessment_date, datetime.time()),
                    'security_score': security_score,
                    'compliance_score': compliance_score,
                    'financial_score': financial_score,
                    'operational_score': operational_score,
                    'overall_score': overall_score,
                    'risk_level': risk_level,
                    'status': status,
                    'next_assessment': datetime.datetime.combine(next_assessment, datetime.time())
                }
                st.session_state.vendor_assessments.append(new_assessment)
                st.success("Assessment added successfully!")
    
    # Display assessments
    df = pd.DataFrame(st.session_state.vendor_assessments)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        risk_filter = st.selectbox("Filter by Risk Level", ["All"] + list(df['risk_level'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        score_filter = st.slider("Overall Score Range", 0, 100, (0, 100))
    
    # Apply filters
    filtered_df = df.copy()
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    filtered_df = filtered_df[(filtered_df['overall_score'] >= score_filter[0]) & (filtered_df['overall_score'] <= score_filter[1])]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Assessment analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Assessment Scores by Dimension")
        if not filtered_df.empty:
            scores_data = {
                'Dimension': ['Security', 'Compliance', 'Financial', 'Operational'],
                'Average Score': [
                    filtered_df['security_score'].mean(),
                    filtered_df['compliance_score'].mean(),
                    filtered_df['financial_score'].mean(),
                    filtered_df['operational_score'].mean()
                ]
            }
            scores_df = pd.DataFrame(scores_data)
            fig = px.bar(scores_df, x='Dimension', y='Average Score', 
                        title="Average Assessment Scores by Dimension")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Risk Level Distribution")
        risk_counts = filtered_df['risk_level'].value_counts()
        fig = px.pie(values=risk_counts.values, names=risk_counts.index, 
                    title="Assessment Risk Level Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_contract_management():
    st.header("Contract Management")
    
    # Add new contract
    with st.expander("Add New Contract"):
        with st.form("new_contract"):
            col1, col2 = st.columns(2)
            with col1:
                vendor_id = st.selectbox("Vendor", [v['id'] for v in st.session_state.vendors])
                contract_number = st.text_input("Contract Number")
                contract_type = st.selectbox("Contract Type", ["Service Agreement", "License Agreement", "Purchase Order", "Master Agreement"])
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")
                value = st.number_input("Contract Value", min_value=0, value=100000)
                currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD"])
                auto_renewal = st.checkbox("Auto Renewal")
                termination_notice = st.number_input("Termination Notice (days)", min_value=0, value=30)
                status = st.selectbox("Status", ["Active", "Pending", "Expired", "Terminated"])
            
            if st.form_submit_button("Add Contract"):
                new_contract = {
                    'id': f'VC-{len(st.session_state.vendor_contracts)+1:03d}',
                    'vendor_id': vendor_id,
                    'contract_number': contract_number,
                    'contract_type': contract_type,
                    'start_date': datetime.datetime.combine(start_date, datetime.time()),
                    'end_date': datetime.datetime.combine(end_date, datetime.time()),
                    'value': value,
                    'currency': currency,
                    'auto_renewal': auto_renewal,
                    'termination_notice': termination_notice,
                    'status': status
                }
                st.session_state.vendor_contracts.append(new_contract)
                st.success("Contract added successfully!")
    
    # Display contracts
    df = pd.DataFrame(st.session_state.vendor_contracts)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['contract_type'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        currency_filter = st.selectbox("Filter by Currency", ["All"] + list(df['currency'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['contract_type'] == type_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if currency_filter != "All":
        filtered_df = filtered_df[filtered_df['currency'] == currency_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Contract analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Contract Value by Type")
        value_by_type = filtered_df.groupby('contract_type')['value'].sum().reset_index()
        fig = px.bar(x=value_by_type['contract_type'], y=value_by_type['value'], 
                    title="Contract Value by Type")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Contract Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Contract Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_incident_tracking():
    st.header("Incident Tracking")
    
    # Add new incident
    with st.expander("Add New Incident"):
        with st.form("new_incident"):
            col1, col2 = st.columns(2)
            with col1:
                vendor_id = st.selectbox("Vendor", [v['id'] for v in st.session_state.vendors])
                incident_date = st.date_input("Incident Date")
                incident_type = st.selectbox("Incident Type", ["Service Outage", "Security Breach", "Data Breach", "Performance Issue", "Compliance Violation", "Other"])
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            with col2:
                description = st.text_area("Description")
                impact = st.text_area("Impact Assessment")
                resolution_time = st.number_input("Resolution Time (hours)", min_value=0, value=4)
                status = st.selectbox("Status", ["Open", "Under Investigation", "Resolved", "Closed"])
            
            if st.form_submit_button("Add Incident"):
                new_incident = {
                    'id': f'VI-{len(st.session_state.vendor_incidents)+1:03d}',
                    'vendor_id': vendor_id,
                    'incident_date': datetime.datetime.combine(incident_date, datetime.time()),
                    'incident_type': incident_type,
                    'severity': severity,
                    'description': description,
                    'impact': impact,
                    'resolution_time': resolution_time,
                    'status': status
                }
                st.session_state.vendor_incidents.append(new_incident)
                st.success("Incident added successfully!")
    
    # Display incidents
    df = pd.DataFrame(st.session_state.vendor_incidents)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['incident_type'].unique()))
    with col2:
        severity_filter = st.selectbox("Filter by Severity", ["All"] + list(df['severity'].unique()))
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['incident_type'] == type_filter]
    if severity_filter != "All":
        filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Incident analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Incidents by Type")
        type_counts = filtered_df['incident_type'].value_counts()
        fig = px.bar(x=type_counts.index, y=type_counts.values, 
                    title="Incidents by Type")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Incident Severity Distribution")
        severity_counts = filtered_df['severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index, 
                    title="Incident Severity Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_category_management():
    st.header("Category Management")
    
    # Add new category
    with st.expander("Add New Category"):
        with st.form("new_category"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Category Name")
                description = st.text_area("Description")
            with col2:
                risk_weight = st.slider("Risk Weight", 0.0, 1.0, 0.5, 0.1)
                assessment_frequency = st.selectbox("Assessment Frequency", ["Monthly", "Quarterly", "Semi-annually", "Annually"])
            
            if st.form_submit_button("Add Category"):
                new_category = {
                    'id': f'CAT-{len(st.session_state.vendor_categories)+1:03d}',
                    'name': name,
                    'description': description,
                    'risk_weight': risk_weight,
                    'assessment_frequency': assessment_frequency,
                    'total_vendors': 0
                }
                st.session_state.vendor_categories.append(new_category)
                st.success("Category added successfully!")
    
    # Display categories
    df = pd.DataFrame(st.session_state.vendor_categories)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        frequency_filter = st.selectbox("Filter by Assessment Frequency", ["All"] + list(df['assessment_frequency'].unique()))
    with col2:
        weight_filter = st.slider("Risk Weight Range", 0.0, 1.0, (0.0, 1.0), 0.1)
    
    # Apply filters
    filtered_df = df.copy()
    if frequency_filter != "All":
        filtered_df = filtered_df[filtered_df['assessment_frequency'] == frequency_filter]
    filtered_df = filtered_df[(filtered_df['risk_weight'] >= weight_filter[0]) & (filtered_df['risk_weight'] <= weight_filter[1])]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Category analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Weight Distribution")
        fig = px.bar(filtered_df, x='name', y='risk_weight', 
                    title="Risk Weight by Category")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Assessment Frequency Distribution")
        frequency_counts = filtered_df['assessment_frequency'].value_counts()
        fig = px.pie(values=frequency_counts.values, names=frequency_counts.index, 
                    title="Assessment Frequency Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_contact_management():
    st.header("Contact Management")
    
    # Add new contact
    with st.expander("Add New Contact"):
        with st.form("new_contact"):
            col1, col2 = st.columns(2)
            with col1:
                vendor_id = st.selectbox("Vendor", [v['id'] for v in st.session_state.vendors])
                name = st.text_input("Contact Name")
                title = st.text_input("Title")
            with col2:
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                primary_contact = st.checkbox("Primary Contact")
            
            if st.form_submit_button("Add Contact"):
                new_contact = {
                    'id': f'VCT-{len(st.session_state.vendor_contacts)+1:03d}',
                    'vendor_id': vendor_id,
                    'name': name,
                    'title': title,
                    'email': email,
                    'phone': phone,
                    'primary_contact': primary_contact
                }
                st.session_state.vendor_contacts.append(new_contact)
                st.success("Contact added successfully!")
    
    # Display contacts
    df = pd.DataFrame(st.session_state.vendor_contacts)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        vendor_filter = st.selectbox("Filter by Vendor", ["All"] + list(df['vendor_id'].unique()))
    with col2:
        primary_filter = st.selectbox("Filter by Contact Type", ["All", "Primary", "Secondary"])
    
    # Apply filters
    filtered_df = df.copy()
    if vendor_filter != "All":
        filtered_df = filtered_df[filtered_df['vendor_id'] == vendor_filter]
    if primary_filter == "Primary":
        filtered_df = filtered_df[filtered_df['primary_contact'] == True]
    elif primary_filter == "Secondary":
        filtered_df = filtered_df[filtered_df['primary_contact'] == False]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Contact analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Contacts by Vendor")
        vendor_contact_counts = filtered_df['vendor_id'].value_counts()
        fig = px.bar(x=vendor_contact_counts.index, y=vendor_contact_counts.values, 
                    title="Number of Contacts by Vendor")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Primary vs Secondary Contacts")
        contact_type_counts = filtered_df['primary_contact'].value_counts()
        fig = px.pie(values=contact_type_counts.values, names=['Secondary', 'Primary'], 
                    title="Primary vs Secondary Contacts")
        st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("Vendor Risk Reports")
    
    # Report options
    report_type = st.selectbox("Select Report Type", [
        "Vendor Risk Summary",
        "Assessment Performance Report",
        "Contract Value Report",
        "Incident Analysis Report",
        "Category Risk Report",
        "Compliance Report"
    ])
    
    if report_type == "Vendor Risk Summary":
        st.subheader("Vendor Risk Summary")
        
        # Calculate summary metrics
        total_vendors = len(st.session_state.vendors)
        active_vendors = len([v for v in st.session_state.vendors if v['status'] == 'Active'])
        critical_risk = len([v for v in st.session_state.vendors if v['risk_level'] == 'Critical'])
        high_risk = len([v for v in st.session_state.vendors if v['risk_level'] == 'High'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Vendor Overview**")
            st.write(f"• Total Vendors: {total_vendors}")
            st.write(f"• Active Vendors: {active_vendors}")
            st.write(f"• Critical Risk Vendors: {critical_risk}")
            st.write(f"• High Risk Vendors: {high_risk}")
        
        with col2:
            st.write("**Risk Metrics**")
            total_contract_value = sum([v['contract_value'] for v in st.session_state.vendors])
            st.write(f"• Total Contract Value: ${total_contract_value:,}")
            avg_assessment_score = np.mean([a['overall_score'] for a in st.session_state.vendor_assessments])
            st.write(f"• Average Assessment Score: {avg_assessment_score:.1f}")
            active_incidents = len([i for i in st.session_state.vendor_incidents if i['status'] == 'Under Investigation'])
            st.write(f"• Active Incidents: {active_incidents}")
            st.write(f"• Overall Risk Posture: Moderate")
    
    # Export functionality
    st.subheader("Export Data")
    export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
    
    if st.button("Export Vendor Data"):
        if export_format == "CSV":
            df_vendors = pd.DataFrame(st.session_state.vendors)
            csv = df_vendors.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="vendor_risk_data.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
