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
    page_title="Security Awareness Campaign Manager",
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
if 'campaigns' not in st.session_state:
    st.session_state.campaigns = []
if 'campaign_content' not in st.session_state:
    st.session_state.campaign_content = []
if 'campaign_deliveries' not in st.session_state:
    st.session_state.campaign_deliveries = []
if 'campaign_metrics' not in st.session_state:
    st.session_state.campaign_metrics = []
if 'target_audiences' not in st.session_state:
    st.session_state.target_audiences = []
if 'campaign_schedules' not in st.session_state:
    st.session_state.campaign_schedules = []

def generate_sample_data():
    """Generate sample security awareness campaign data"""
    campaigns = [
        {
            'id': 'CAM-001',
            'name': 'Phishing Awareness Campaign',
            'description': 'Comprehensive phishing awareness training for all employees',
            'status': 'Active',
            'start_date': datetime.datetime.now() - timedelta(days=30),
            'end_date': datetime.datetime.now() + timedelta(days=60),
            'target_audience': 'All Employees',
            'budget': 15000,
            'campaign_type': 'Training',
            'priority': 'High',
            'owner': 'Security Team'
        },
        {
            'id': 'CAM-002',
            'name': 'Password Security Initiative',
            'description': 'Password best practices and multi-factor authentication awareness',
            'status': 'Planning',
            'start_date': datetime.datetime.now() + timedelta(days=15),
            'end_date': datetime.datetime.now() + timedelta(days=90),
            'target_audience': 'IT Staff',
            'budget': 8000,
            'campaign_type': 'Awareness',
            'priority': 'Medium',
            'owner': 'IT Security'
        },
        {
            'id': 'CAM-003',
            'name': 'Data Protection Awareness',
            'description': 'GDPR and data protection compliance training',
            'status': 'Completed',
            'start_date': datetime.datetime.now() - timedelta(days=90),
            'end_date': datetime.datetime.now() - timedelta(days=30),
            'target_audience': 'Data Handlers',
            'budget': 12000,
            'campaign_type': 'Compliance',
            'priority': 'High',
            'owner': 'Compliance Team'
        },
        {
            'id': 'CAM-004',
            'name': 'Social Engineering Defense',
            'description': 'Social engineering attack recognition and prevention',
            'status': 'Active',
            'start_date': datetime.datetime.now() - timedelta(days=15),
            'end_date': datetime.datetime.now() + timedelta(days=45),
            'target_audience': 'Customer Service',
            'budget': 6000,
            'campaign_type': 'Training',
            'priority': 'Medium',
            'owner': 'Security Team'
        }
    ]
    
    campaign_content = [
        {
            'id': 'CONT-001',
            'campaign_id': 'CAM-001',
            'content_type': 'Video',
            'title': 'Phishing Email Recognition',
            'description': 'Interactive video on identifying phishing emails',
            'duration_minutes': 15,
            'file_size_mb': 45,
            'language': 'English',
            'accessibility': 'Yes',
            'status': 'Published'
        },
        {
            'id': 'CONT-002',
            'campaign_id': 'CAM-001',
            'content_type': 'Quiz',
            'title': 'Phishing Quiz',
            'description': 'Interactive quiz to test phishing recognition skills',
            'duration_minutes': 10,
            'file_size_mb': 2,
            'language': 'English',
            'accessibility': 'Yes',
            'status': 'Published'
        },
        {
            'id': 'CONT-003',
            'campaign_id': 'CAM-002',
            'content_type': 'Infographic',
            'title': 'Password Best Practices',
            'description': 'Visual guide to creating strong passwords',
            'duration_minutes': 5,
            'file_size_mb': 8,
            'language': 'English',
            'accessibility': 'Yes',
            'status': 'Draft'
        },
        {
            'id': 'CONT-004',
            'campaign_id': 'CAM-003',
            'content_type': 'Webinar',
            'title': 'GDPR Compliance Training',
            'description': 'Live webinar on GDPR requirements and compliance',
            'duration_minutes': 60,
            'file_size_mb': 120,
            'language': 'English',
            'accessibility': 'Yes',
            'status': 'Published'
        }
    ]
    
    campaign_deliveries = [
        {
            'id': 'DEL-001',
            'campaign_id': 'CAM-001',
            'content_id': 'CONT-001',
            'delivery_method': 'Email',
            'recipient_count': 250,
            'delivered_count': 245,
            'opened_count': 180,
            'completed_count': 165,
            'delivery_date': datetime.datetime.now() - timedelta(days=25),
            'status': 'Completed'
        },
        {
            'id': 'DEL-002',
            'campaign_id': 'CAM-001',
            'content_id': 'CONT-002',
            'delivery_method': 'LMS',
            'recipient_count': 250,
            'delivered_count': 250,
            'opened_count': 200,
            'completed_count': 185,
            'delivery_date': datetime.datetime.now() - timedelta(days=20),
            'status': 'Completed'
        },
        {
            'id': 'DEL-003',
            'campaign_id': 'CAM-003',
            'content_id': 'CONT-004',
            'delivery_method': 'Webinar',
            'recipient_count': 100,
            'delivered_count': 95,
            'opened_count': 85,
            'completed_count': 80,
            'delivery_date': datetime.datetime.now() - timedelta(days=60),
            'status': 'Completed'
        },
        {
            'id': 'DEL-004',
            'campaign_id': 'CAM-004',
            'content_id': 'CONT-001',
            'delivery_method': 'Email',
            'recipient_count': 75,
            'delivered_count': 72,
            'opened_count': 55,
            'completed_count': 45,
            'delivery_date': datetime.datetime.now() - timedelta(days=10),
            'status': 'In Progress'
        }
    ]
    
    campaign_metrics = [
        {
            'campaign_id': 'CAM-001',
            'metric_name': 'Engagement Rate',
            'value': 73.5,
            'target': 75.0,
            'unit': '%',
            'date': datetime.datetime.now() - timedelta(days=1),
            'status': 'On Track'
        },
        {
            'campaign_id': 'CAM-001',
            'metric_name': 'Completion Rate',
            'value': 67.3,
            'target': 70.0,
            'unit': '%',
            'date': datetime.datetime.now() - timedelta(days=1),
            'status': 'Needs Attention'
        },
        {
            'campaign_id': 'CAM-003',
            'metric_name': 'Engagement Rate',
            'value': 84.2,
            'target': 80.0,
            'unit': '%',
            'date': datetime.datetime.now() - timedelta(days=1),
            'status': 'Exceeding'
        },
        {
            'campaign_id': 'CAM-003',
            'metric_name': 'Completion Rate',
            'value': 78.9,
            'target': 75.0,
            'unit': '%',
            'date': datetime.datetime.now() - timedelta(days=1),
            'status': 'Exceeding'
        },
        {
            'campaign_id': 'CAM-004',
            'metric_name': 'Engagement Rate',
            'value': 62.5,
            'target': 70.0,
            'unit': '%',
            'date': datetime.datetime.now() - timedelta(days=1),
            'status': 'Needs Attention'
        }
    ]
    
    target_audiences = [
        {
            'id': 'AUD-001',
            'name': 'All Employees',
            'description': 'Complete employee population',
            'size': 250,
            'department': 'All',
            'risk_level': 'Medium',
            'training_frequency': 'Quarterly'
        },
        {
            'id': 'AUD-002',
            'name': 'IT Staff',
            'description': 'Information technology personnel',
            'size': 25,
            'department': 'IT',
            'risk_level': 'High',
            'training_frequency': 'Monthly'
        },
        {
            'id': 'AUD-003',
            'name': 'Data Handlers',
            'description': 'Employees who handle sensitive data',
            'size': 50,
            'department': 'Multiple',
            'risk_level': 'High',
            'training_frequency': 'Monthly'
        },
        {
            'id': 'AUD-004',
            'name': 'Customer Service',
            'description': 'Customer-facing employees',
            'size': 75,
            'department': 'Customer Service',
            'risk_level': 'Medium',
            'training_frequency': 'Quarterly'
        }
    ]
    
    campaign_schedules = [
        {
            'id': 'SCH-001',
            'campaign_id': 'CAM-001',
            'delivery_date': datetime.datetime.now() + timedelta(days=7),
            'delivery_method': 'Email',
            'target_audience': 'All Employees',
            'content_type': 'Reminder',
            'status': 'Scheduled'
        },
        {
            'id': 'SCH-002',
            'campaign_id': 'CAM-002',
            'delivery_date': datetime.datetime.now() + timedelta(days=15),
            'delivery_method': 'LMS',
            'target_audience': 'IT Staff',
            'content_type': 'Initial',
            'status': 'Scheduled'
        },
        {
            'id': 'SCH-003',
            'campaign_id': 'CAM-004',
            'delivery_date': datetime.datetime.now() + timedelta(days=5),
            'delivery_method': 'Email',
            'target_audience': 'Customer Service',
            'content_type': 'Follow-up',
            'status': 'Scheduled'
        }
    ]
    
    return campaigns, campaign_content, campaign_deliveries, campaign_metrics, target_audiences, campaign_schedules

def main():
    st.markdown('<h1 class="main-header">Security Awareness Campaign Manager</h1>', unsafe_allow_html=True)
    st.markdown("Comprehensive platform for managing security awareness campaigns, content creation, delivery tracking, and effectiveness measurement")
    
    # Initialize sample data
    if not st.session_state.campaigns:
        campaigns, content, deliveries, metrics, audiences, schedules = generate_sample_data()
        st.session_state.campaigns = campaigns
        st.session_state.campaign_content = content
        st.session_state.campaign_deliveries = deliveries
        st.session_state.campaign_metrics = metrics
        st.session_state.target_audiences = audiences
        st.session_state.campaign_schedules = schedules
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Dashboard", "Campaign Management", "Content Management", "Delivery Tracking", "Audience Management", "Metrics & Analytics", "Scheduling", "Reports"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Campaign Management":
        show_campaign_management()
    elif page == "Content Management":
        show_content_management()
    elif page == "Delivery Tracking":
        show_delivery_tracking()
    elif page == "Audience Management":
        show_audience_management()
    elif page == "Metrics & Analytics":
        show_metrics_analytics()
    elif page == "Scheduling":
        show_scheduling()
    elif page == "Reports":
        show_reports()

def show_dashboard():
    st.header("Campaign Dashboard")
    
    # Calculate key metrics
    active_campaigns = len([c for c in st.session_state.campaigns if c['status'] == 'Active'])
    total_campaigns = len(st.session_state.campaigns)
    avg_engagement = np.mean([m['value'] for m in st.session_state.campaign_metrics if m['metric_name'] == 'Engagement Rate'])
    avg_completion = np.mean([m['value'] for m in st.session_state.campaign_metrics if m['metric_name'] == 'Completion Rate'])
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Campaigns", active_campaigns, f"{active_campaigns}/{total_campaigns}")
        st.metric("Total Content", len(st.session_state.campaign_content))
    
    with col2:
        st.metric("Avg Engagement Rate", f"{avg_engagement:.1f}%")
        st.metric("Avg Completion Rate", f"{avg_completion:.1f}%")
    
    with col3:
        total_recipients = sum([d['recipient_count'] for d in st.session_state.campaign_deliveries])
        total_delivered = sum([d['delivered_count'] for d in st.session_state.campaign_deliveries])
        st.metric("Total Recipients", total_recipients)
        st.metric("Total Delivered", total_delivered)
    
    with col4:
        scheduled_deliveries = len([s for s in st.session_state.campaign_schedules if s['status'] == 'Scheduled'])
        st.metric("Scheduled Deliveries", scheduled_deliveries)
        st.metric("Target Audiences", len(st.session_state.target_audiences))
    
    # Campaign overview charts
    st.subheader("Campaign Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Campaign status distribution
        status_counts = pd.DataFrame(st.session_state.campaigns)['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Campaign Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Campaign type distribution
        type_counts = pd.DataFrame(st.session_state.campaigns)['campaign_type'].value_counts()
        fig = px.bar(x=type_counts.index, y=type_counts.values, 
                    title="Campaigns by Type")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent campaign activities
    st.subheader("Recent Campaign Activities")
    recent_deliveries = sorted(st.session_state.campaign_deliveries, key=lambda x: x['delivery_date'], reverse=True)[:5]
    
    for delivery in recent_deliveries:
        campaign = next((c for c in st.session_state.campaigns if c['id'] == delivery['campaign_id']), None)
        content = next((c for c in st.session_state.campaign_content if c['id'] == delivery['content_id']), None)
        
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"**{campaign['name'] if campaign else 'Unknown Campaign'}**")
        with col2:
            st.write(f"**{content['title'] if content else 'Unknown Content'}** - {delivery['delivery_method']}")
        with col3:
            engagement_rate = (delivery['opened_count'] / delivery['delivered_count'] * 100) if delivery['delivered_count'] > 0 else 0
            st.write(f"**{engagement_rate:.1f}%** engagement")
        with col4:
            if delivery['status'] == 'Completed':
                st.write("Completed")
            elif delivery['status'] == 'In Progress':
                st.write("Active")
            else:
                st.write("Scheduled")
        st.divider()

def show_campaign_management():
    st.header("Campaign Management")
    
    # Add new campaign
    with st.expander("Add New Campaign"):
        with st.form("new_campaign"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Campaign Name")
                description = st.text_area("Description")
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
            with col2:
                target_audience = st.selectbox("Target Audience", [a['name'] for a in st.session_state.target_audiences])
                budget = st.number_input("Budget ($)", min_value=0, value=10000)
                campaign_type = st.selectbox("Campaign Type", ["Training", "Awareness", "Compliance", "Reminder"])
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                owner = st.text_input("Campaign Owner")
            
            if st.form_submit_button("Add Campaign"):
                new_campaign = {
                    'id': f'CAM-{len(st.session_state.campaigns)+1:03d}',
                    'name': name,
                    'description': description,
                    'status': 'Planning',
                    'start_date': datetime.datetime.combine(start_date, datetime.time()),
                    'end_date': datetime.datetime.combine(end_date, datetime.time()),
                    'target_audience': target_audience,
                    'budget': budget,
                    'campaign_type': campaign_type,
                    'priority': priority,
                    'owner': owner
                }
                st.session_state.campaigns.append(new_campaign)
                st.success("Campaign added successfully!")
    
    # Display campaigns
    df = pd.DataFrame(st.session_state.campaigns)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col2:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['campaign_type'].unique()))
    with col3:
        priority_filter = st.selectbox("Filter by Priority", ["All"] + list(df['priority'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['campaign_type'] == type_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Campaign analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Campaigns by Status")
        status_counts = df['status'].value_counts()
        fig = px.bar(x=status_counts.index, y=status_counts.values, 
                    title="Campaign Distribution by Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Budget Allocation by Type")
        budget_by_type = df.groupby('campaign_type')['budget'].sum().reset_index()
        fig = px.pie(values=budget_by_type['budget'], names=budget_by_type['campaign_type'], 
                    title="Budget Allocation by Campaign Type")
        st.plotly_chart(fig, use_container_width=True)

def show_content_management():
    st.header("Content Management")
    
    # Add new content
    with st.expander("Add New Content"):
        with st.form("new_content"):
            col1, col2 = st.columns(2)
            with col1:
                campaign_id = st.selectbox("Campaign", [c['id'] for c in st.session_state.campaigns])
                content_type = st.selectbox("Content Type", ["Video", "Quiz", "Infographic", "Webinar", "Document", "Interactive"])
                title = st.text_input("Title")
                description = st.text_area("Description")
            with col2:
                duration_minutes = st.number_input("Duration (minutes)", min_value=1, value=15)
                file_size_mb = st.number_input("File Size (MB)", min_value=0, value=10)
                language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Other"])
                accessibility = st.selectbox("Accessibility", ["Yes", "No", "In Progress"])
                status = st.selectbox("Status", ["Draft", "In Review", "Published", "Archived"])
            
            if st.form_submit_button("Add Content"):
                new_content = {
                    'id': f'CONT-{len(st.session_state.campaign_content)+1:03d}',
                    'campaign_id': campaign_id,
                    'content_type': content_type,
                    'title': title,
                    'description': description,
                    'duration_minutes': duration_minutes,
                    'file_size_mb': file_size_mb,
                    'language': language,
                    'accessibility': accessibility,
                    'status': status
                }
                st.session_state.campaign_content.append(new_content)
                st.success("Content added successfully!")
    
    # Display content
    df = pd.DataFrame(st.session_state.campaign_content)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Content Type", ["All"] + list(df['content_type'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        language_filter = st.selectbox("Filter by Language", ["All"] + list(df['language'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['content_type'] == type_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if language_filter != "All":
        filtered_df = filtered_df[filtered_df['language'] == language_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Content analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Content by Type")
        type_counts = df['content_type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, 
                    title="Content Distribution by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Content Status Distribution")
        status_counts = df['status'].value_counts()
        fig = px.bar(x=status_counts.index, y=status_counts.values, 
                    title="Content by Status")
        st.plotly_chart(fig, use_container_width=True)

def show_delivery_tracking():
    st.header("Delivery Tracking")
    
    # Add new delivery
    with st.expander("Add New Delivery"):
        with st.form("new_delivery"):
            col1, col2 = st.columns(2)
            with col1:
                campaign_id = st.selectbox("Campaign", [c['id'] for c in st.session_state.campaigns])
                content_id = st.selectbox("Content", [c['id'] for c in st.session_state.campaign_content])
                delivery_method = st.selectbox("Delivery Method", ["Email", "LMS", "Webinar", "In-Person", "Social Media"])
                recipient_count = st.number_input("Recipient Count", min_value=1, value=100)
            with col2:
                delivered_count = st.number_input("Delivered Count", min_value=0, value=95)
                opened_count = st.number_input("Opened Count", min_value=0, value=70)
                completed_count = st.number_input("Completed Count", min_value=0, value=65)
                delivery_date = st.date_input("Delivery Date")
                status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed", "Failed"])
            
            if st.form_submit_button("Add Delivery"):
                new_delivery = {
                    'id': f'DEL-{len(st.session_state.campaign_deliveries)+1:03d}',
                    'campaign_id': campaign_id,
                    'content_id': content_id,
                    'delivery_method': delivery_method,
                    'recipient_count': recipient_count,
                    'delivered_count': delivered_count,
                    'opened_count': opened_count,
                    'completed_count': completed_count,
                    'delivery_date': datetime.datetime.combine(delivery_date, datetime.time()),
                    'status': status
                }
                st.session_state.campaign_deliveries.append(new_delivery)
                st.success("Delivery added successfully!")
    
    # Display deliveries
    df = pd.DataFrame(st.session_state.campaign_deliveries)
    
    # Calculate engagement rates
    df['engagement_rate'] = (df['opened_count'] / df['delivered_count'] * 100).fillna(0)
    df['completion_rate'] = (df['completed_count'] / df['delivered_count'] * 100).fillna(0)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        method_filter = st.selectbox("Filter by Method", ["All"] + list(df['delivery_method'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        date_filter = st.date_input("Filter by Date")
    
    # Apply filters
    filtered_df = df.copy()
    if method_filter != "All":
        filtered_df = filtered_df[filtered_df['delivery_method'] == method_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if date_filter:
        filtered_df = filtered_df[filtered_df['delivery_date'].dt.date == date_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Delivery analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Delivery Performance by Method")
        method_performance = filtered_df.groupby('delivery_method').agg({
            'engagement_rate': 'mean',
            'completion_rate': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=method_performance['delivery_method'], y=method_performance['engagement_rate'], 
                            name='Engagement Rate'))
        fig.add_trace(go.Bar(x=method_performance['delivery_method'], y=method_performance['completion_rate'], 
                            name='Completion Rate'))
        fig.update_layout(title="Performance by Delivery Method", barmode='group')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Delivery Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Delivery Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_audience_management():
    st.header("Audience Management")
    
    # Add new audience
    with st.expander("Add New Target Audience"):
        with st.form("new_audience"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Audience Name")
                description = st.text_area("Description")
                size = st.number_input("Audience Size", min_value=1, value=50)
            with col2:
                department = st.text_input("Department")
                risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
                training_frequency = st.selectbox("Training Frequency", ["Monthly", "Quarterly", "Semi-annually", "Annually"])
            
            if st.form_submit_button("Add Audience"):
                new_audience = {
                    'id': f'AUD-{len(st.session_state.target_audiences)+1:03d}',
                    'name': name,
                    'description': description,
                    'size': size,
                    'department': department,
                    'risk_level': risk_level,
                    'training_frequency': training_frequency
                }
                st.session_state.target_audiences.append(new_audience)
                st.success("Target audience added successfully!")
    
    # Display audiences
    df = pd.DataFrame(st.session_state.target_audiences)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        risk_filter = st.selectbox("Filter by Risk Level", ["All"] + list(df['risk_level'].unique()))
    with col2:
        frequency_filter = st.selectbox("Filter by Training Frequency", ["All"] + list(df['training_frequency'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    if frequency_filter != "All":
        filtered_df = filtered_df[filtered_df['training_frequency'] == frequency_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Audience analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Audience Size by Risk Level")
        risk_size = filtered_df.groupby('risk_level')['size'].sum().reset_index()
        fig = px.bar(x=risk_size['risk_level'], y=risk_size['size'], 
                    title="Total Audience Size by Risk Level",
                    color=risk_size['risk_level'],
                    color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Training Frequency Distribution")
        frequency_counts = filtered_df['training_frequency'].value_counts()
        fig = px.pie(values=frequency_counts.values, names=frequency_counts.index, 
                    title="Audience Distribution by Training Frequency")
        st.plotly_chart(fig, use_container_width=True)

def show_metrics_analytics():
    st.header("Metrics & Analytics")
    
    # Add new metric
    with st.expander("Add New Metric"):
        with st.form("new_metric"):
            col1, col2 = st.columns(2)
            with col1:
                campaign_id = st.selectbox("Campaign", [c['id'] for c in st.session_state.campaigns])
                metric_name = st.text_input("Metric Name")
                value = st.number_input("Value", min_value=0.0, value=75.0)
            with col2:
                target = st.number_input("Target", min_value=0.0, value=80.0)
                unit = st.text_input("Unit", value="%")
                status = st.selectbox("Status", ["On Track", "Needs Attention", "At Risk", "Exceeding"])
            
            if st.form_submit_button("Add Metric"):
                new_metric = {
                    'campaign_id': campaign_id,
                    'metric_name': metric_name,
                    'value': value,
                    'target': target,
                    'unit': unit,
                    'date': datetime.datetime.now(),
                    'status': status
                }
                st.session_state.campaign_metrics.append(new_metric)
                st.success("Metric added successfully!")
    
    # Display metrics
    df = pd.DataFrame(st.session_state.campaign_metrics)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        metric_filter = st.selectbox("Filter by Metric", ["All"] + list(df['metric_name'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if metric_filter != "All":
        filtered_df = filtered_df[filtered_df['metric_name'] == metric_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Metrics analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Performance vs Target")
        performance_data = filtered_df.groupby('metric_name').agg({
            'value': 'mean',
            'target': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=performance_data['metric_name'], y=performance_data['value'], 
                            name='Current Performance'))
        fig.add_trace(go.Bar(x=performance_data['metric_name'], y=performance_data['target'], 
                            name='Target'))
        fig.update_layout(title="Performance vs Target by Metric", barmode='group')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Metric Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Metric Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_scheduling():
    st.header("Campaign Scheduling")
    
    # Add new schedule
    with st.expander("Add New Schedule"):
        with st.form("new_schedule"):
            col1, col2 = st.columns(2)
            with col1:
                campaign_id = st.selectbox("Campaign", [c['id'] for c in st.session_state.campaigns])
                delivery_date = st.date_input("Delivery Date")
                delivery_method = st.selectbox("Delivery Method", ["Email", "LMS", "Webinar", "In-Person", "Social Media"])
            with col2:
                target_audience = st.selectbox("Target Audience", [a['name'] for a in st.session_state.target_audiences])
                content_type = st.selectbox("Content Type", ["Initial", "Reminder", "Follow-up", "Assessment"])
                status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed", "Cancelled"])
            
            if st.form_submit_button("Add Schedule"):
                new_schedule = {
                    'id': f'SCH-{len(st.session_state.campaign_schedules)+1:03d}',
                    'campaign_id': campaign_id,
                    'delivery_date': datetime.datetime.combine(delivery_date, datetime.time()),
                    'delivery_method': delivery_method,
                    'target_audience': target_audience,
                    'content_type': content_type,
                    'status': status
                }
                st.session_state.campaign_schedules.append(new_schedule)
                st.success("Schedule added successfully!")
    
    # Display schedules
    df = pd.DataFrame(st.session_state.campaign_schedules)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        method_filter = st.selectbox("Filter by Method", ["All"] + list(df['delivery_method'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        content_filter = st.selectbox("Filter by Content Type", ["All"] + list(df['content_type'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if method_filter != "All":
        filtered_df = filtered_df[filtered_df['delivery_method'] == method_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if content_filter != "All":
        filtered_df = filtered_df[filtered_df['content_type'] == content_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Scheduling analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Scheduled Deliveries by Method")
        method_counts = filtered_df['delivery_method'].value_counts()
        fig = px.bar(x=method_counts.index, y=method_counts.values, 
                    title="Scheduled Deliveries by Method")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Schedule Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Schedule Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("Campaign Reports")
    
    # Report options
    report_type = st.selectbox("Select Report Type", [
        "Campaign Performance Summary",
        "Content Effectiveness Report",
        "Audience Engagement Report",
        "Delivery Performance Report",
        "Budget Utilization Report",
        "Compliance Training Report"
    ])
    
    if report_type == "Campaign Performance Summary":
        st.subheader("Campaign Performance Summary")
        
        # Calculate summary metrics
        total_campaigns = len(st.session_state.campaigns)
        active_campaigns = len([c for c in st.session_state.campaigns if c['status'] == 'Active'])
        completed_campaigns = len([c for c in st.session_state.campaigns if c['status'] == 'Completed'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Campaign Overview**")
            st.write(f"• Total Campaigns: {total_campaigns}")
            st.write(f"• Active Campaigns: {active_campaigns}")
            st.write(f"• Completed Campaigns: {completed_campaigns}")
            st.write(f"• Success Rate: {(completed_campaigns/total_campaigns*100):.1f}%")
        
        with col2:
            st.write("**Performance Metrics**")
            avg_engagement = np.mean([m['value'] for m in st.session_state.campaign_metrics if m['metric_name'] == 'Engagement Rate'])
            avg_completion = np.mean([m['value'] for m in st.session_state.campaign_metrics if m['metric_name'] == 'Completion Rate'])
            st.write(f"• Average Engagement Rate: {avg_engagement:.1f}%")
            st.write(f"• Average Completion Rate: {avg_completion:.1f}%")
            st.write(f"• Total Content Created: {len(st.session_state.campaign_content)}")
            st.write(f"• Total Deliveries: {len(st.session_state.campaign_deliveries)}")
    
    # Export functionality
    st.subheader("Export Data")
    export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
    
    if st.button("Export Campaign Data"):
        if export_format == "CSV":
            df_campaigns = pd.DataFrame(st.session_state.campaigns)
            csv = df_campaigns.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="security_awareness_campaigns.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
