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
    page_title="Business Continuity Management",
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
if 'business_processes' not in st.session_state:
    st.session_state.business_processes = []
if 'recovery_plans' not in st.session_state:
    st.session_state.recovery_plans = []
if 'disaster_scenarios' not in st.session_state:
    st.session_state.disaster_scenarios = []
if 'recovery_tests' not in st.session_state:
    st.session_state.recovery_tests = []
if 'critical_assets' not in st.session_state:
    st.session_state.critical_assets = []

def generate_sample_data():
    """Generate sample business continuity data"""
    business_processes = [
        {
            'id': 'BP-001',
            'name': 'Customer Order Processing',
            'department': 'Sales',
            'criticality': 'Critical',
            'rto_hours': 4,
            'rpo_hours': 1,
            'dependencies': ['Payment System', 'Inventory System'],
            'recovery_team': 'Sales Recovery Team',
            'backup_systems': ['Cloud-based Order System', 'Manual Process'],
            'status': 'Active'
        },
        {
            'id': 'BP-002',
            'name': 'Payment Processing',
            'department': 'Finance',
            'criticality': 'Critical',
            'rto_hours': 2,
            'rpo_hours': 0.5,
            'dependencies': ['Banking Systems', 'Security Infrastructure'],
            'recovery_team': 'Finance Recovery Team',
            'backup_systems': ['Secondary Payment Gateway', 'Manual Reconciliation'],
            'status': 'Active'
        },
        {
            'id': 'BP-003',
            'name': 'Employee Payroll',
            'department': 'HR',
            'criticality': 'High',
            'rto_hours': 24,
            'rpo_hours': 4,
            'dependencies': ['HR Database', 'Banking Systems'],
            'recovery_team': 'HR Recovery Team',
            'backup_systems': ['Cloud HR System', 'Manual Payroll'],
            'status': 'Active'
        },
        {
            'id': 'BP-004',
            'name': 'Email Communication',
            'department': 'IT',
            'criticality': 'High',
            'rto_hours': 8,
            'rpo_hours': 2,
            'dependencies': ['Email Servers', 'Internet Connectivity'],
            'recovery_team': 'IT Recovery Team',
            'backup_systems': ['Cloud Email', 'Mobile Communication'],
            'status': 'Active'
        },
        {
            'id': 'BP-005',
            'name': 'Website Operations',
            'department': 'Marketing',
            'criticality': 'Medium',
            'rto_hours': 48,
            'rpo_hours': 24,
            'dependencies': ['Web Servers', 'Content Management'],
            'recovery_team': 'Marketing Recovery Team',
            'backup_systems': ['CDN', 'Static Site'],
            'status': 'Active'
        }
    ]
    
    recovery_plans = [
        {
            'id': 'RP-001',
            'name': 'Data Center Recovery Plan',
            'type': 'Infrastructure',
            'last_updated': datetime.datetime.now() - timedelta(days=30),
            'next_review': datetime.datetime.now() + timedelta(days=60),
            'status': 'Current',
            'version': '2.1',
            'owner': 'IT Director',
            'approval_status': 'Approved'
        },
        {
            'id': 'RP-002',
            'name': 'Remote Work Continuity Plan',
            'type': 'Workplace',
            'last_updated': datetime.datetime.now() - timedelta(days=15),
            'next_review': datetime.datetime.now() + timedelta(days=45),
            'status': 'Current',
            'version': '1.3',
            'owner': 'HR Director',
            'approval_status': 'Approved'
        },
        {
            'id': 'RP-003',
            'name': 'Supply Chain Recovery Plan',
            'type': 'Operations',
            'last_updated': datetime.datetime.now() - timedelta(days=7),
            'next_review': datetime.datetime.now() + timedelta(days=30),
            'status': 'Current',
            'version': '1.0',
            'owner': 'Operations Manager',
            'approval_status': 'Pending Review'
        }
    ]
    
    disaster_scenarios = [
        {
            'id': 'DS-001',
            'name': 'Data Center Outage',
            'type': 'Infrastructure',
            'probability': 'Medium',
            'impact': 'High',
            'mitigation_measures': ['Redundant Systems', 'Cloud Backup', 'Secondary Site'],
            'response_time': '2 hours',
            'recovery_time': '24 hours'
        },
        {
            'id': 'DS-002',
            'name': 'Cyber Attack',
            'type': 'Security',
            'probability': 'High',
            'impact': 'Critical',
            'mitigation_measures': ['Security Monitoring', 'Incident Response', 'Backup Systems'],
            'response_time': '1 hour',
            'recovery_time': '48 hours'
        },
        {
            'id': 'DS-003',
            'name': 'Natural Disaster',
            'type': 'Environmental',
            'probability': 'Low',
            'impact': 'Critical',
            'mitigation_measures': ['Geographic Redundancy', 'Insurance', 'Remote Work'],
            'response_time': '4 hours',
            'recovery_time': '72 hours'
        }
    ]
    
    recovery_tests = []
    test_types = ['Tabletop Exercise', 'Functional Test', 'Full Recovery Test', 'Walkthrough']
    results = ['Passed', 'Failed', 'Partially Passed', 'Scheduled']
    
    for i in range(15):
        test_date = datetime.datetime.now() - timedelta(days=random.randint(30, 365))
        next_test = test_date + timedelta(days=random.randint(90, 365))
        
        test = {
            'id': f'RT-{2024:04d}-{i+1:03d}',
            'name': f'Recovery Test {i+1}',
            'type': random.choice(test_types),
            'test_date': test_date,
            'next_test_date': next_test,
            'result': random.choice(results),
            'participants': random.randint(5, 25),
            'duration_hours': random.randint(2, 8),
            'cost': random.randint(1000, 10000),
            'lessons_learned': f'Key lesson from test {i+1}',
            'improvements': f'Improvement identified in test {i+1}'
        }
        recovery_tests.append(test)
    
    critical_assets = [
        {
            'id': 'CA-001',
            'name': 'Primary Data Center',
            'type': 'Infrastructure',
            'location': 'Main Campus',
            'criticality': 'Critical',
            'backup_location': 'Secondary Data Center',
            'recovery_time': '4 hours',
            'last_assessment': datetime.datetime.now() - timedelta(days=60),
            'next_assessment': datetime.datetime.now() + timedelta(days=30)
        },
        {
            'id': 'CA-002',
            'name': 'Customer Database',
            'type': 'Data',
            'location': 'Cloud',
            'criticality': 'Critical',
            'backup_location': 'Secondary Cloud Region',
            'recovery_time': '2 hours',
            'last_assessment': datetime.datetime.now() - timedelta(days=30),
            'next_assessment': datetime.datetime.now() + timedelta(days=60)
        },
        {
            'id': 'CA-003',
            'name': 'Payment Processing System',
            'type': 'Application',
            'location': 'Primary Data Center',
            'criticality': 'Critical',
            'backup_location': 'Cloud-based System',
            'recovery_time': '1 hour',
            'last_assessment': datetime.datetime.now() - timedelta(days=15),
            'next_assessment': datetime.datetime.now() + timedelta(days=45)
        }
    ]
    
    return business_processes, recovery_plans, disaster_scenarios, recovery_tests, critical_assets

def main():
    st.markdown('<h1 class="main-header">Business Continuity Management System</h1>', unsafe_allow_html=True)
    st.markdown("Comprehensive business continuity planning, testing, and management platform")
    
    # Initialize sample data
    if not st.session_state.business_processes:
        bp, rp, ds, rt, ca = generate_sample_data()
        st.session_state.business_processes = bp
        st.session_state.recovery_plans = rp
        st.session_state.disaster_scenarios = ds
        st.session_state.recovery_tests = rt
        st.session_state.critical_assets = ca
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Dashboard", "Business Processes", "Recovery Plans", "Disaster Scenarios", 
         "Recovery Testing", "Critical Assets", "BCM Metrics", "Reports"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Business Processes":
        show_business_processes()
    elif page == "Recovery Plans":
        show_recovery_plans()
    elif page == "Disaster Scenarios":
        show_disaster_scenarios()
    elif page == "Recovery Testing":
        show_recovery_testing()
    elif page == "Critical Assets":
        show_critical_assets()
    elif page == "BCM Metrics":
        show_bcm_metrics()
    elif page == "Reports":
        show_reports()

def show_dashboard():
    st.header("📊 Business Continuity Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Critical Processes",
            value=len([bp for bp in st.session_state.business_processes if bp['criticality'] == 'Critical']),
            delta="2"
        )
    
    with col2:
        st.metric(
            label="Recovery Plans",
            value=len(st.session_state.recovery_plans),
            delta="1"
        )
    
    with col3:
        st.metric(
            label="Tests This Year",
            value=len([rt for rt in st.session_state.recovery_tests if rt['test_date'].year == 2024]),
            delta="3"
        )
    
    with col4:
        avg_rto = np.mean([bp['rto_hours'] for bp in st.session_state.business_processes])
        st.metric(
            label="Avg RTO (hours)",
            value=f"{avg_rto:.1f}",
            delta="-2.5"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Process Criticality Distribution")
        criticality_counts = pd.DataFrame(st.session_state.business_processes)['criticality'].value_counts()
        fig = px.pie(values=criticality_counts.values, names=criticality_counts.index, 
                    title="Business Process Criticality")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Recovery Time Objectives")
        df_processes = pd.DataFrame(st.session_state.business_processes)
        fig = px.bar(df_processes, x='name', y='rto_hours', 
                    title="RTO by Business Process",
                    labels={'rto_hours': 'RTO (hours)', 'name': 'Process'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Recent Recovery Tests**")
        recent_tests = sorted(st.session_state.recovery_tests, 
                            key=lambda x: x['test_date'], reverse=True)[:5]
        for test in recent_tests:
            st.write(f"• {test['name']} - {test['result']} ({test['test_date'].strftime('%Y-%m-%d')})")
    
    with col2:
        st.write("**Upcoming Reviews**")
        upcoming_reviews = [rp for rp in st.session_state.recovery_plans 
                          if rp['next_review'] > datetime.datetime.now()]
        upcoming_reviews.sort(key=lambda x: x['next_review'])
        for plan in upcoming_reviews[:5]:
            st.write(f"• {plan['name']} - {plan['next_review'].strftime('%Y-%m-%d')}")

def show_business_processes():
    st.header("🏢 Business Processes")
    
    # Add new process
    with st.expander("Add New Business Process"):
        with st.form("new_process"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Process Name")
                department = st.selectbox("Department", ["Sales", "Finance", "HR", "IT", "Marketing", "Operations"])
                criticality = st.selectbox("Criticality", ["Critical", "High", "Medium", "Low"])
            
            with col2:
                rto_hours = st.number_input("RTO (hours)", min_value=0.5, max_value=168.0, value=24.0)
                rpo_hours = st.number_input("RPO (hours)", min_value=0.1, max_value=168.0, value=4.0)
                recovery_team = st.text_input("Recovery Team")
            
            dependencies = st.text_area("Dependencies (comma-separated)")
            backup_systems = st.text_area("Backup Systems (comma-separated)")
            
            if st.form_submit_button("Add Process"):
                new_process = {
                    'id': f'BP-{len(st.session_state.business_processes)+1:03d}',
                    'name': name,
                    'department': department,
                    'criticality': criticality,
                    'rto_hours': rto_hours,
                    'rpo_hours': rpo_hours,
                    'dependencies': [d.strip() for d in dependencies.split(',') if d.strip()],
                    'recovery_team': recovery_team,
                    'backup_systems': [b.strip() for b in backup_systems.split(',') if b.strip()],
                    'status': 'Active'
                }
                st.session_state.business_processes.append(new_process)
                st.success("Business process added successfully!")
    
    # Display processes
    df = pd.DataFrame(st.session_state.business_processes)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        dept_filter = st.selectbox("Filter by Department", ["All"] + list(df['department'].unique()))
    with col2:
        crit_filter = st.selectbox("Filter by Criticality", ["All"] + list(df['criticality'].unique()))
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if dept_filter != "All":
        filtered_df = filtered_df[filtered_df['department'] == dept_filter]
    if crit_filter != "All":
        filtered_df = filtered_df[filtered_df['criticality'] == crit_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Process details
    if st.checkbox("Show Process Details"):
        selected_process = st.selectbox("Select Process", df['name'].tolist())
        process = next((p for p in st.session_state.business_processes if p['name'] == selected_process), None)
        
        if process:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Process ID:** {process['id']}")
                st.write(f"**Department:** {process['department']}")
                st.write(f"**Criticality:** {process['criticality']}")
                st.write(f"**RTO:** {process['rto_hours']} hours")
                st.write(f"**RPO:** {process['rpo_hours']} hours")
            
            with col2:
                st.write(f"**Recovery Team:** {process['recovery_team']}")
                st.write(f"**Status:** {process['status']}")
                st.write("**Dependencies:**")
                for dep in process['dependencies']:
                    st.write(f"  - {dep}")
                st.write("**Backup Systems:**")
                for backup in process['backup_systems']:
                    st.write(f"  - {backup}")

def show_recovery_plans():
    st.header("📋 Recovery Plans")
    
    # Add new plan
    with st.expander("Add New Recovery Plan"):
        with st.form("new_plan"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Plan Name")
                plan_type = st.selectbox("Plan Type", ["Infrastructure", "Workplace", "Operations", "Security", "Data"])
                owner = st.text_input("Plan Owner")
            
            with col2:
                version = st.text_input("Version", value="1.0")
                approval_status = st.selectbox("Approval Status", ["Draft", "Pending Review", "Approved", "Archived"])
            
            if st.form_submit_button("Add Plan"):
                new_plan = {
                    'id': f'RP-{len(st.session_state.recovery_plans)+1:03d}',
                    'name': name,
                    'type': plan_type,
                    'last_updated': datetime.datetime.now(),
                    'next_review': datetime.datetime.now() + timedelta(days=90),
                    'status': 'Current',
                    'version': version,
                    'owner': owner,
                    'approval_status': approval_status
                }
                st.session_state.recovery_plans.append(new_plan)
                st.success("Recovery plan added successfully!")
    
    # Display plans
    df = pd.DataFrame(st.session_state.recovery_plans)
    st.dataframe(df, use_container_width=True)
    
    # Plan status overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Plan Status Distribution")
        status_counts = df['approval_status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Recovery Plan Approval Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Plans by Type")
        type_counts = df['type'].value_counts()
        fig = px.bar(x=type_counts.index, y=type_counts.values, 
                    title="Recovery Plans by Type")
        st.plotly_chart(fig, use_container_width=True)

def show_disaster_scenarios():
    st.header("⚠️ Disaster Scenarios")
    
    # Add new scenario
    with st.expander("Add New Disaster Scenario"):
        with st.form("new_scenario"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Scenario Name")
                scenario_type = st.selectbox("Scenario Type", ["Infrastructure", "Security", "Environmental", "Human", "Technology"])
                probability = st.selectbox("Probability", ["Low", "Medium", "High", "Critical"])
            
            with col2:
                impact = st.selectbox("Impact", ["Low", "Medium", "High", "Critical"])
                response_time = st.text_input("Response Time", value="2 hours")
                recovery_time = st.text_input("Recovery Time", value="24 hours")
            
            mitigation_measures = st.text_area("Mitigation Measures (comma-separated)")
            
            if st.form_submit_button("Add Scenario"):
                new_scenario = {
                    'id': f'DS-{len(st.session_state.disaster_scenarios)+1:03d}',
                    'name': name,
                    'type': scenario_type,
                    'probability': probability,
                    'impact': impact,
                    'mitigation_measures': [m.strip() for m in mitigation_measures.split(',') if m.strip()],
                    'response_time': response_time,
                    'recovery_time': recovery_time
                }
                st.session_state.disaster_scenarios.append(new_scenario)
                st.success("Disaster scenario added successfully!")
    
    # Display scenarios
    df = pd.DataFrame(st.session_state.disaster_scenarios)
    st.dataframe(df, use_container_width=True)
    
    # Risk matrix
    st.subheader("Risk Matrix")
    risk_matrix = pd.crosstab(df['probability'], df['impact'], margins=True)
    st.dataframe(risk_matrix, use_container_width=True)

def show_recovery_testing():
    st.header("🧪 Recovery Testing")
    
    # Add new test
    with st.expander("Add New Recovery Test"):
        with st.form("new_test"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Test Name")
                test_type = st.selectbox("Test Type", ["Tabletop Exercise", "Functional Test", "Full Recovery Test", "Walkthrough"])
                test_date = st.date_input("Test Date")
            
            with col2:
                participants = st.number_input("Number of Participants", min_value=1, max_value=100, value=10)
                duration_hours = st.number_input("Duration (hours)", min_value=1, max_value=24, value=4)
                cost = st.number_input("Cost ($)", min_value=0, max_value=50000, value=5000)
            
            result = st.selectbox("Result", ["Passed", "Failed", "Partially Passed", "Scheduled"])
            lessons_learned = st.text_area("Lessons Learned")
            improvements = st.text_area("Improvements")
            
            if st.form_submit_button("Add Test"):
                new_test = {
                    'id': f'RT-{datetime.datetime.now().year:04d}-{len(st.session_state.recovery_tests)+1:03d}',
                    'name': name,
                    'type': test_type,
                    'test_date': datetime.datetime.combine(test_date, datetime.time()),
                    'next_test_date': datetime.datetime.combine(test_date, datetime.time()) + timedelta(days=365),
                    'result': result,
                    'participants': participants,
                    'duration_hours': duration_hours,
                    'cost': cost,
                    'lessons_learned': lessons_learned,
                    'improvements': improvements
                }
                st.session_state.recovery_tests.append(new_test)
                st.success("Recovery test added successfully!")
    
    # Display tests
    df = pd.DataFrame(st.session_state.recovery_tests)
    st.dataframe(df, use_container_width=True)
    
    # Test analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Test Results Distribution")
        result_counts = df['result'].value_counts()
        fig = px.pie(values=result_counts.values, names=result_counts.index, 
                    title="Recovery Test Results")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Test Types")
        type_counts = df['type'].value_counts()
        fig = px.bar(x=type_counts.index, y=type_counts.values, 
                    title="Recovery Tests by Type")
        st.plotly_chart(fig, use_container_width=True)

def show_critical_assets():
    st.header("🔧 Critical Assets")
    
    # Add new asset
    with st.expander("Add New Critical Asset"):
        with st.form("new_asset"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Asset Name")
                asset_type = st.selectbox("Asset Type", ["Infrastructure", "Data", "Application", "Network", "Physical"])
                location = st.text_input("Location")
            
            with col2:
                criticality = st.selectbox("Criticality", ["Critical", "High", "Medium", "Low"])
                backup_location = st.text_input("Backup Location")
                recovery_time = st.text_input("Recovery Time", value="4 hours")
            
            if st.form_submit_button("Add Asset"):
                new_asset = {
                    'id': f'CA-{len(st.session_state.critical_assets)+1:03d}',
                    'name': name,
                    'type': asset_type,
                    'location': location,
                    'criticality': criticality,
                    'backup_location': backup_location,
                    'recovery_time': recovery_time,
                    'last_assessment': datetime.datetime.now(),
                    'next_assessment': datetime.datetime.now() + timedelta(days=90)
                }
                st.session_state.critical_assets.append(new_asset)
                st.success("Critical asset added successfully!")
    
    # Display assets
    df = pd.DataFrame(st.session_state.critical_assets)
    st.dataframe(df, use_container_width=True)
    
    # Asset overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Assets by Type")
        type_counts = df['type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, 
                    title="Critical Assets by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Assets by Criticality")
        crit_counts = df['criticality'].value_counts()
        fig = px.bar(x=crit_counts.index, y=crit_counts.values, 
                    title="Critical Assets by Criticality")
        st.plotly_chart(fig, use_container_width=True)

def show_bcm_metrics():
    st.header("📈 BCM Metrics & KPIs")
    
    # Calculate metrics
    total_processes = len(st.session_state.business_processes)
    critical_processes = len([bp for bp in st.session_state.business_processes if bp['criticality'] == 'Critical'])
    avg_rto = np.mean([bp['rto_hours'] for bp in st.session_state.business_processes])
    avg_rpo = np.mean([bp['rpo_hours'] for bp in st.session_state.business_processes])
    
    total_tests = len(st.session_state.recovery_tests)
    passed_tests = len([rt for rt in st.session_state.recovery_tests if rt['result'] == 'Passed'])
    test_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Processes", total_processes)
        st.metric("Critical Processes", critical_processes)
    
    with col2:
        st.metric("Avg RTO (hours)", f"{avg_rto:.1f}")
        st.metric("Avg RPO (hours)", f"{avg_rpo:.1f}")
    
    with col3:
        st.metric("Total Tests", total_tests)
        st.metric("Test Success Rate", f"{test_success_rate:.1f}%")
    
    with col4:
        st.metric("Recovery Plans", len(st.session_state.recovery_plans))
        st.metric("Critical Assets", len(st.session_state.critical_assets))
    
    # Trend analysis
    st.subheader("Testing Trends")
    df_tests = pd.DataFrame(st.session_state.recovery_tests)
    df_tests['test_date'] = pd.to_datetime(df_tests['test_date'])
    df_tests['month'] = df_tests['test_date'].dt.to_period('M')
    
    monthly_tests = df_tests.groupby('month').size().reset_index(name='count')
    monthly_tests['month'] = monthly_tests['month'].astype(str)
    
    fig = px.line(monthly_tests, x='month', y='count', 
                  title="Monthly Recovery Tests",
                  labels={'count': 'Number of Tests', 'month': 'Month'})
    st.plotly_chart(fig, use_container_width=True)
    
    # RTO/RPO analysis
    st.subheader("RTO/RPO Analysis")
    df_processes = pd.DataFrame(st.session_state.business_processes)
    
    fig = px.scatter(df_processes, x='rto_hours', y='rpo_hours', 
                    color='criticality', size='rto_hours',
                    title="RTO vs RPO by Process Criticality",
                    labels={'rto_hours': 'RTO (hours)', 'rpo_hours': 'RPO (hours)'})
    st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("📊 Reports & Analytics")
    
    # Report options
    report_type = st.selectbox("Select Report Type", [
        "Business Continuity Summary",
        "Recovery Testing Report",
        "Critical Asset Assessment",
        "Disaster Scenario Analysis",
        "Compliance Report"
    ])
    
    if report_type == "Business Continuity Summary":
        st.subheader("Business Continuity Summary Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Executive Summary**")
            st.write(f"• Total Business Processes: {len(st.session_state.business_processes)}")
            st.write(f"• Critical Processes: {len([bp for bp in st.session_state.business_processes if bp['criticality'] == 'Critical'])}")
            st.write(f"• Recovery Plans: {len(st.session_state.recovery_plans)}")
            st.write(f"• Critical Assets: {len(st.session_state.critical_assets)}")
        
        with col2:
            st.write("**Key Metrics**")
            avg_rto = np.mean([bp['rto_hours'] for bp in st.session_state.business_processes])
            avg_rpo = np.mean([bp['rpo_hours'] for bp in st.session_state.business_processes])
            st.write(f"• Average RTO: {avg_rto:.1f} hours")
            st.write(f"• Average RPO: {avg_rpo:.1f} hours")
            
            total_tests = len(st.session_state.recovery_tests)
            passed_tests = len([rt for rt in st.session_state.recovery_tests if rt['result'] == 'Passed'])
            if total_tests > 0:
                success_rate = (passed_tests / total_tests * 100)
                st.write(f"• Test Success Rate: {success_rate:.1f}%")
    
    elif report_type == "Recovery Testing Report":
        st.subheader("Recovery Testing Report")
        
        df_tests = pd.DataFrame(st.session_state.recovery_tests)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Test Statistics**")
            st.write(f"• Total Tests: {len(df_tests)}")
            st.write(f"• Passed Tests: {len(df_tests[df_tests['result'] == 'Passed'])}")
            st.write(f"• Failed Tests: {len(df_tests[df_tests['result'] == 'Failed'])}")
            st.write(f"• Total Cost: ${df_tests['cost'].sum():,}")
        
        with col2:
            st.write("**Test Types**")
            type_counts = df_tests['type'].value_counts()
            for test_type, count in type_counts.items():
                st.write(f"• {test_type}: {count}")
    
    # Export functionality
    st.subheader("Export Data")
    export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
    
    if st.button("Export Data"):
        if export_format == "CSV":
            # Export to CSV
            df_processes = pd.DataFrame(st.session_state.business_processes)
            csv = df_processes.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="business_processes.csv",
                mime="text/csv"
            )
        elif export_format == "JSON":
            # Export to JSON
            json_data = json.dumps(st.session_state.business_processes, default=str, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="business_processes.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
