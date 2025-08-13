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
    page_title="Security Metrics Dashboard",
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
if 'security_metrics' not in st.session_state:
    st.session_state.security_metrics = []
if 'kpi_targets' not in st.session_state:
    st.session_state.kpi_targets = []
if 'security_events' not in st.session_state:
    st.session_state.security_events = []
if 'vulnerabilities' not in st.session_state:
    st.session_state.vulnerabilities = []
if 'compliance_metrics' not in st.session_state:
    st.session_state.compliance_metrics = []
if 'incident_metrics' not in st.session_state:
    st.session_state.incident_metrics = []

def generate_sample_data():
    """Generate sample security metrics data"""
    security_metrics = [
        {
            'id': 'MET-001',
            'metric_name': 'Mean Time to Detect (MTTD)',
            'value': 2.5,
            'unit': 'hours',
            'target': 4.0,
            'status': 'Exceeding',
            'category': 'Detection',
            'date': datetime.datetime.now() - timedelta(days=1)
        },
        {
            'id': 'MET-002',
            'metric_name': 'Mean Time to Respond (MTTR)',
            'value': 6.2,
            'unit': 'hours',
            'target': 8.0,
            'status': 'On Track',
            'category': 'Response',
            'date': datetime.datetime.now() - timedelta(days=1)
        },
        {
            'id': 'MET-003',
            'metric_name': 'Security Awareness Training Completion',
            'value': 87.5,
            'unit': '%',
            'target': 90.0,
            'status': 'Needs Attention',
            'category': 'Awareness',
            'date': datetime.datetime.now() - timedelta(days=1)
        },
        {
            'id': 'MET-004',
            'metric_name': 'Vulnerability Remediation Rate',
            'value': 92.3,
            'unit': '%',
            'target': 95.0,
            'status': 'On Track',
            'category': 'Vulnerability',
            'date': datetime.datetime.now() - timedelta(days=1)
        },
        {
            'id': 'MET-005',
            'metric_name': 'Phishing Click Rate',
            'value': 3.2,
            'unit': '%',
            'target': 5.0,
            'status': 'Exceeding',
            'category': 'Awareness',
            'date': datetime.datetime.now() - timedelta(days=1)
        },
        {
            'id': 'MET-006',
            'metric_name': 'Security Incident Count',
            'value': 12,
            'unit': 'incidents',
            'target': 15,
            'status': 'Exceeding',
            'category': 'Incident',
            'date': datetime.datetime.now() - timedelta(days=1)
        }
    ]
    
    kpi_targets = [
        {
            'id': 'KPI-001',
            'metric_name': 'MTTD',
            'target_value': 4.0,
            'current_value': 2.5,
            'unit': 'hours',
            'status': 'Exceeding',
            'priority': 'High'
        },
        {
            'id': 'KPI-002',
            'metric_name': 'MTTR',
            'target_value': 8.0,
            'current_value': 6.2,
            'unit': 'hours',
            'status': 'On Track',
            'priority': 'High'
        },
        {
            'id': 'KPI-003',
            'metric_name': 'Training Completion',
            'target_value': 90.0,
            'current_value': 87.5,
            'unit': '%',
            'status': 'Needs Attention',
            'priority': 'Medium'
        },
        {
            'id': 'KPI-004',
            'metric_name': 'Vulnerability Remediation',
            'target_value': 95.0,
            'current_value': 92.3,
            'unit': '%',
            'status': 'On Track',
            'priority': 'High'
        }
    ]
    
    security_events = [
        {
            'id': 'EVT-001',
            'event_type': 'Failed Login Attempts',
            'severity': 'Medium',
            'count': 45,
            'source': 'Active Directory',
            'date': datetime.datetime.now() - timedelta(hours=2)
        },
        {
            'id': 'EVT-002',
            'event_type': 'Suspicious Network Activity',
            'severity': 'High',
            'count': 12,
            'source': 'Firewall',
            'date': datetime.datetime.now() - timedelta(hours=4)
        },
        {
            'id': 'EVT-003',
            'event_type': 'Malware Detection',
            'severity': 'Critical',
            'count': 3,
            'source': 'EDR',
            'date': datetime.datetime.now() - timedelta(hours=6)
        },
        {
            'id': 'EVT-004',
            'event_type': 'Data Access Violation',
            'severity': 'High',
            'count': 8,
            'source': 'DLP',
            'date': datetime.datetime.now() - timedelta(hours=8)
        }
    ]
    
    vulnerabilities = [
        {
            'id': 'VUL-001',
            'title': 'SQL Injection Vulnerability',
            'severity': 'Critical',
            'cvss_score': 9.8,
            'status': 'Open',
            'affected_systems': 5,
            'date_discovered': datetime.datetime.now() - timedelta(days=2)
        },
        {
            'id': 'VUL-002',
            'title': 'Outdated SSL Certificate',
            'severity': 'Medium',
            'cvss_score': 5.5,
            'status': 'In Progress',
            'affected_systems': 12,
            'date_discovered': datetime.datetime.now() - timedelta(days=5)
        },
        {
            'id': 'VUL-003',
            'title': 'Weak Password Policy',
            'severity': 'High',
            'cvss_score': 7.2,
            'status': 'Open',
            'affected_systems': 25,
            'date_discovered': datetime.datetime.now() - timedelta(days=1)
        },
        {
            'id': 'VUL-004',
            'title': 'Missing Security Patches',
            'severity': 'Medium',
            'cvss_score': 6.1,
            'status': 'In Progress',
            'affected_systems': 8,
            'date_discovered': datetime.datetime.now() - timedelta(days=3)
        }
    ]
    
    compliance_metrics = [
        {
            'id': 'COMP-001',
            'framework': 'ISO 27001',
            'compliance_score': 87.5,
            'target_score': 90.0,
            'status': 'On Track',
            'last_assessment': datetime.datetime.now() - timedelta(days=30)
        },
        {
            'id': 'COMP-002',
            'framework': 'SOC 2',
            'compliance_score': 92.3,
            'target_score': 95.0,
            'status': 'On Track',
            'last_assessment': datetime.datetime.now() - timedelta(days=45)
        },
        {
            'id': 'COMP-003',
            'framework': 'GDPR',
            'compliance_score': 95.8,
            'target_score': 95.0,
            'status': 'Exceeding',
            'last_assessment': datetime.datetime.now() - timedelta(days=60)
        },
        {
            'id': 'COMP-004',
            'framework': 'PCI DSS',
            'compliance_score': 89.2,
            'target_score': 90.0,
            'status': 'On Track',
            'last_assessment': datetime.datetime.now() - timedelta(days=15)
        }
    ]
    
    incident_metrics = [
        {
            'id': 'INC-001',
            'incident_type': 'Phishing Attack',
            'severity': 'Medium',
            'status': 'Resolved',
            'resolution_time': 4.5,
            'date': datetime.datetime.now() - timedelta(days=7)
        },
        {
            'id': 'INC-002',
            'incident_type': 'Data Breach Attempt',
            'severity': 'High',
            'status': 'Under Investigation',
            'resolution_time': None,
            'date': datetime.datetime.now() - timedelta(days=2)
        },
        {
            'id': 'INC-003',
            'incident_type': 'Malware Infection',
            'severity': 'Critical',
            'status': 'Resolved',
            'resolution_time': 8.2,
            'date': datetime.datetime.now() - timedelta(days=14)
        },
        {
            'id': 'INC-004',
            'incident_type': 'Unauthorized Access',
            'severity': 'High',
            'status': 'Resolved',
            'resolution_time': 6.1,
            'date': datetime.datetime.now() - timedelta(days=10)
        }
    ]
    
    return security_metrics, kpi_targets, security_events, vulnerabilities, compliance_metrics, incident_metrics

def main():
    st.markdown('<h1 class="main-header">Security Metrics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Comprehensive platform for tracking security KPIs, metrics, and performance indicators across the organization")
    
    # Initialize sample data
    if not st.session_state.security_metrics:
        metrics, kpis, events, vulns, compliance, incidents = generate_sample_data()
        st.session_state.security_metrics = metrics
        st.session_state.kpi_targets = kpis
        st.session_state.security_events = events
        st.session_state.vulnerabilities = vulns
        st.session_state.compliance_metrics = compliance
        st.session_state.incident_metrics = incidents
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Dashboard", "KPI Tracking", "Security Events", "Vulnerability Metrics", "Compliance Metrics", "Incident Analytics", "Trends", "Reports"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "KPI Tracking":
        show_kpi_tracking()
    elif page == "Security Events":
        show_security_events()
    elif page == "Vulnerability Metrics":
        show_vulnerability_metrics()
    elif page == "Compliance Metrics":
        show_compliance_metrics()
    elif page == "Incident Analytics":
        show_incident_analytics()
    elif page == "Trends":
        show_trends()
    elif page == "Reports":
        show_reports()

def show_dashboard():
    st.header("Dashboard Overview")
    
    # Calculate key metrics
    total_metrics = len(st.session_state.security_metrics)
    exceeding_targets = len([m for m in st.session_state.security_metrics if m['status'] == 'Exceeding'])
    on_track = len([m for m in st.session_state.security_metrics if m['status'] == 'On Track'])
    needs_attention = len([m for m in st.session_state.security_metrics if m['status'] == 'Needs Attention'])
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Metrics", total_metrics)
        st.metric("Exceeding Targets", exceeding_targets, f"{exceeding_targets}/{total_metrics}")
    
    with col2:
        st.metric("On Track", on_track, f"{on_track}/{total_metrics}")
        st.metric("Needs Attention", needs_attention, f"{needs_attention}/{total_metrics}")
    
    with col3:
        avg_mttd = np.mean([m['value'] for m in st.session_state.security_metrics if m['metric_name'] == 'Mean Time to Detect (MTTD)'])
        avg_mttr = np.mean([m['value'] for m in st.session_state.security_metrics if m['metric_name'] == 'Mean Time to Respond (MTTR)'])
        st.metric("Avg MTTD", f"{avg_mttd:.1f} hours")
        st.metric("Avg MTTR", f"{avg_mttr:.1f} hours")
    
    with col4:
        training_completion = next((m['value'] for m in st.session_state.security_metrics if m['metric_name'] == 'Security Awareness Training Completion'), 0)
        phishing_rate = next((m['value'] for m in st.session_state.security_metrics if m['metric_name'] == 'Phishing Click Rate'), 0)
        st.metric("Training Completion", f"{training_completion:.1f}%")
        st.metric("Phishing Click Rate", f"{phishing_rate:.1f}%")
    
    # Dashboard charts
    st.subheader("Performance Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = pd.DataFrame(st.session_state.security_metrics)['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Metric Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category distribution
        category_counts = pd.DataFrame(st.session_state.security_metrics)['category'].value_counts()
        fig = px.bar(x=category_counts.index, y=category_counts.values, 
                    title="Metrics by Category")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent security events
    st.subheader("Recent Security Events")
    recent_events = sorted(st.session_state.security_events, key=lambda x: x['date'], reverse=True)[:5]
    
    for event in recent_events:
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"**{event['event_type']}**")
        with col2:
            st.write(f"**{event['source']}** - {event['count']} events")
        with col3:
            if event['severity'] == 'Critical':
                st.write("Critical")
            elif event['severity'] == 'High':
                st.write("High")
            else:
                st.write("Medium")
        with col4:
            st.write(f"{event['date'].strftime('%H:%M')}")
        st.divider()

def show_kpi_tracking():
    st.header("KPI Tracking")
    
    # Add new KPI
    with st.expander("Add New KPI"):
        with st.form("new_kpi"):
            col1, col2 = st.columns(2)
            with col1:
                metric_name = st.text_input("Metric Name")
                target_value = st.number_input("Target Value", min_value=0.0, value=90.0)
                unit = st.text_input("Unit", value="%")
            with col2:
                current_value = st.number_input("Current Value", min_value=0.0, value=85.0)
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                status = st.selectbox("Status", ["On Track", "Needs Attention", "At Risk", "Exceeding"])
            
            if st.form_submit_button("Add KPI"):
                new_kpi = {
                    'id': f'KPI-{len(st.session_state.kpi_targets)+1:03d}',
                    'metric_name': metric_name,
                    'target_value': target_value,
                    'current_value': current_value,
                    'unit': unit,
                    'status': status,
                    'priority': priority
                }
                st.session_state.kpi_targets.append(new_kpi)
                st.success("KPI added successfully!")
    
    # Display KPIs
    df = pd.DataFrame(st.session_state.kpi_targets)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All"] + list(df['priority'].unique()))
    with col3:
        metric_filter = st.selectbox("Filter by Metric", ["All"] + list(df['metric_name'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
    if metric_filter != "All":
        filtered_df = filtered_df[filtered_df['metric_name'] == metric_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # KPI analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Performance vs Target")
        performance_data = filtered_df.copy()
        performance_data['performance_ratio'] = performance_data['current_value'] / performance_data['target_value']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=performance_data['metric_name'], y=performance_data['current_value'], 
                            name='Current Value'))
        fig.add_trace(go.Bar(x=performance_data['metric_name'], y=performance_data['target_value'], 
                            name='Target Value'))
        fig.update_layout(title="KPI Performance vs Target", barmode='group')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("KPI Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="KPI Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_security_events():
    st.header("Security Events")
    
    # Add new event
    with st.expander("Add New Security Event"):
        with st.form("new_event"):
            col1, col2 = st.columns(2)
            with col1:
                event_type = st.text_input("Event Type")
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                count = st.number_input("Event Count", min_value=1, value=1)
            with col2:
                source = st.text_input("Event Source")
                date = st.date_input("Event Date")
                time = st.time_input("Event Time")
            
            if st.form_submit_button("Add Event"):
                new_event = {
                    'id': f'EVT-{len(st.session_state.security_events)+1:03d}',
                    'event_type': event_type,
                    'severity': severity,
                    'count': count,
                    'source': source,
                    'date': datetime.datetime.combine(date, time)
                }
                st.session_state.security_events.append(new_event)
                st.success("Security event added successfully!")
    
    # Display events
    df = pd.DataFrame(st.session_state.security_events)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.selectbox("Filter by Severity", ["All"] + list(df['severity'].unique()))
    with col2:
        source_filter = st.selectbox("Filter by Source", ["All"] + list(df['source'].unique()))
    with col3:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['event_type'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if severity_filter != "All":
        filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
    if source_filter != "All":
        filtered_df = filtered_df[filtered_df['source'] == source_filter]
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['event_type'] == type_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Event analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Events by Severity")
        severity_counts = filtered_df['severity'].value_counts()
        fig = px.bar(x=severity_counts.index, y=severity_counts.values, 
                    title="Security Events by Severity",
                    color=severity_counts.index,
                    color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Events by Source")
        source_counts = filtered_df['source'].value_counts()
        fig = px.pie(values=source_counts.values, names=source_counts.index, 
                    title="Events by Source")
        st.plotly_chart(fig, use_container_width=True)

def show_vulnerability_metrics():
    st.header("Vulnerability Metrics")
    
    # Add new vulnerability
    with st.expander("Add New Vulnerability"):
        with st.form("new_vulnerability"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Vulnerability Title")
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                cvss_score = st.number_input("CVSS Score", min_value=0.0, max_value=10.0, value=7.0)
            with col2:
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "False Positive"])
                affected_systems = st.number_input("Affected Systems", min_value=1, value=1)
                date_discovered = st.date_input("Date Discovered")
            
            if st.form_submit_button("Add Vulnerability"):
                new_vuln = {
                    'id': f'VUL-{len(st.session_state.vulnerabilities)+1:03d}',
                    'title': title,
                    'severity': severity,
                    'cvss_score': cvss_score,
                    'status': status,
                    'affected_systems': affected_systems,
                    'date_discovered': datetime.datetime.combine(date_discovered, datetime.time())
                }
                st.session_state.vulnerabilities.append(new_vuln)
                st.success("Vulnerability added successfully!")
    
    # Display vulnerabilities
    df = pd.DataFrame(st.session_state.vulnerabilities)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.selectbox("Filter by Severity", ["All"] + list(df['severity'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        cvss_filter = st.slider("CVSS Score Range", 0.0, 10.0, (0.0, 10.0))
    
    # Apply filters
    filtered_df = df.copy()
    if severity_filter != "All":
        filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    filtered_df = filtered_df[(filtered_df['cvss_score'] >= cvss_filter[0]) & (filtered_df['cvss_score'] <= cvss_filter[1])]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Vulnerability analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vulnerabilities by Severity")
        severity_counts = filtered_df['severity'].value_counts()
        fig = px.bar(x=severity_counts.index, y=severity_counts.values, 
                    title="Vulnerabilities by Severity",
                    color=severity_counts.index,
                    color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("CVSS Score Distribution")
        fig = px.histogram(filtered_df, x='cvss_score', nbins=10, 
                          title="CVSS Score Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_compliance_metrics():
    st.header("Compliance Metrics")
    
    # Add new compliance metric
    with st.expander("Add New Compliance Metric"):
        with st.form("new_compliance"):
            col1, col2 = st.columns(2)
            with col1:
                framework = st.text_input("Framework")
                compliance_score = st.number_input("Compliance Score", min_value=0.0, max_value=100.0, value=85.0)
                target_score = st.number_input("Target Score", min_value=0.0, max_value=100.0, value=90.0)
            with col2:
                status = st.selectbox("Status", ["On Track", "Needs Attention", "At Risk", "Exceeding"])
                last_assessment = st.date_input("Last Assessment Date")
            
            if st.form_submit_button("Add Compliance Metric"):
                new_compliance = {
                    'id': f'COMP-{len(st.session_state.compliance_metrics)+1:03d}',
                    'framework': framework,
                    'compliance_score': compliance_score,
                    'target_score': target_score,
                    'status': status,
                    'last_assessment': datetime.datetime.combine(last_assessment, datetime.time())
                }
                st.session_state.compliance_metrics.append(new_compliance)
                st.success("Compliance metric added successfully!")
    
    # Display compliance metrics
    df = pd.DataFrame(st.session_state.compliance_metrics)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        framework_filter = st.selectbox("Filter by Framework", ["All"] + list(df['framework'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if framework_filter != "All":
        filtered_df = filtered_df[filtered_df['framework'] == framework_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Compliance analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Compliance Scores by Framework")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=filtered_df['framework'], y=filtered_df['compliance_score'], 
                            name='Current Score'))
        fig.add_trace(go.Bar(x=filtered_df['framework'], y=filtered_df['target_score'], 
                            name='Target Score'))
        fig.update_layout(title="Compliance Scores by Framework", barmode='group')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Compliance Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Compliance Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_incident_analytics():
    st.header("Incident Analytics")
    
    # Add new incident
    with st.expander("Add New Incident"):
        with st.form("new_incident"):
            col1, col2 = st.columns(2)
            with col1:
                incident_type = st.text_input("Incident Type")
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                status = st.selectbox("Status", ["Open", "Under Investigation", "Resolved", "Closed"])
            with col2:
                resolution_time = st.number_input("Resolution Time (hours)", min_value=0.0, value=4.0)
                date = st.date_input("Incident Date")
            
            if st.form_submit_button("Add Incident"):
                new_incident = {
                    'id': f'INC-{len(st.session_state.incident_metrics)+1:03d}',
                    'incident_type': incident_type,
                    'severity': severity,
                    'status': status,
                    'resolution_time': resolution_time,
                    'date': datetime.datetime.combine(date, datetime.time())
                }
                st.session_state.incident_metrics.append(new_incident)
                st.success("Incident added successfully!")
    
    # Display incidents
    df = pd.DataFrame(st.session_state.incident_metrics)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.selectbox("Filter by Severity", ["All"] + list(df['severity'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['incident_type'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if severity_filter != "All":
        filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['incident_type'] == type_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Incident analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Incidents by Severity")
        severity_counts = filtered_df['severity'].value_counts()
        fig = px.bar(x=severity_counts.index, y=severity_counts.values, 
                    title="Incidents by Severity",
                    color=severity_counts.index,
                    color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Resolution Time Analysis")
        resolved_incidents = filtered_df[filtered_df['resolution_time'].notna()]
        if not resolved_incidents.empty:
            fig = px.box(resolved_incidents, x='severity', y='resolution_time', 
                        title="Resolution Time by Severity")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No resolved incidents to display")

def show_trends():
    st.header("Trends Analysis")
    
    # Generate trend data
    dates = pd.date_range(start=datetime.datetime.now() - timedelta(days=30), 
                         end=datetime.datetime.now(), freq='D')
    
    # Simulate trend data
    mttd_trend = [2.5 + np.random.normal(0, 0.5) for _ in range(len(dates))]
    mttr_trend = [6.2 + np.random.normal(0, 1.0) for _ in range(len(dates))]
    training_trend = [87.5 + np.random.normal(0, 2.0) for _ in range(len(dates))]
    
    trend_data = pd.DataFrame({
        'date': dates,
        'MTTD': mttd_trend,
        'MTTR': mttr_trend,
        'Training_Completion': training_trend
    })
    
    # Trend charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("MTTD Trend")
        fig = px.line(trend_data, x='date', y='MTTD', title="Mean Time to Detect Trend")
        fig.add_hline(y=4.0, line_dash="dash", line_color="red", annotation_text="Target")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("MTTR Trend")
        fig = px.line(trend_data, x='date', y='MTTR', title="Mean Time to Respond Trend")
        fig.add_hline(y=8.0, line_dash="dash", line_color="red", annotation_text="Target")
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Training Completion Trend")
    fig = px.line(trend_data, x='date', y='Training_Completion', title="Training Completion Trend")
    fig.add_hline(y=90.0, line_dash="dash", line_color="red", annotation_text="Target")
    st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("Security Reports")
    
    # Report options
    report_type = st.selectbox("Select Report Type", [
        "Executive Summary",
        "KPI Performance Report",
        "Security Events Summary",
        "Vulnerability Assessment Report",
        "Compliance Status Report",
        "Incident Analysis Report"
    ])
    
    if report_type == "Executive Summary":
        st.subheader("Executive Summary")
        
        # Calculate summary metrics
        total_metrics = len(st.session_state.security_metrics)
        exceeding_targets = len([m for m in st.session_state.security_metrics if m['status'] == 'Exceeding'])
        on_track = len([m for m in st.session_state.security_metrics if m['status'] == 'On Track'])
        needs_attention = len([m for m in st.session_state.security_metrics if m['status'] == 'Needs Attention'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Overall Performance**")
            st.write(f"• Total Metrics Tracked: {total_metrics}")
            st.write(f"• Exceeding Targets: {exceeding_targets}")
            st.write(f"• On Track: {on_track}")
            st.write(f"• Needs Attention: {needs_attention}")
        
        with col2:
            st.write("**Key Highlights**")
            avg_mttd = np.mean([m['value'] for m in st.session_state.security_metrics if m['metric_name'] == 'Mean Time to Detect (MTTD)'])
            avg_mttr = np.mean([m['value'] for m in st.session_state.security_metrics if m['metric_name'] == 'Mean Time to Respond (MTTR)'])
            st.write(f"• Average MTTD: {avg_mttd:.1f} hours")
            st.write(f"• Average MTTR: {avg_mttr:.1f} hours")
            st.write(f"• Security Posture: Strong")
            st.write(f"• Risk Level: Low")
    
    # Export functionality
    st.subheader("Export Data")
    export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
    
    if st.button("Export Security Metrics"):
        if export_format == "CSV":
            df_metrics = pd.DataFrame(st.session_state.security_metrics)
            csv = df_metrics.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="security_metrics.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
