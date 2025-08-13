import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta, date
import random
import json
import calendar

# Page configuration
st.set_page_config(
    page_title="Compliance Calendar",
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
if 'compliance_events' not in st.session_state:
    st.session_state.compliance_events = []
if 'regulatory_deadlines' not in st.session_state:
    st.session_state.regulatory_deadlines = []
if 'audit_schedules' not in st.session_state:
    st.session_state.audit_schedules = []
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'holidays' not in st.session_state:
    st.session_state.holidays = []

def generate_sample_data():
    """Generate sample compliance calendar data"""
    compliance_events = [
        {
            'id': 'CE-2024-001',
            'title': 'SOC 2 Type II Audit Kickoff',
            'event_type': 'Audit',
            'framework': 'SOC 2',
            'start_date': datetime.datetime.now() + timedelta(days=30),
            'end_date': datetime.datetime.now() + timedelta(days=35),
            'priority': 'High',
            'assigned_to': 'IT Security Team',
            'description': 'Kickoff meeting for SOC 2 Type II audit with Deloitte',
            'location': 'Conference Room A',
            'status': 'Scheduled',
            'reminder_days': 7
        },
        {
            'id': 'CE-2024-002',
            'title': 'Quarterly Access Review Due',
            'event_type': 'Compliance',
            'framework': 'SOX',
            'start_date': datetime.datetime.now() + timedelta(days=15),
            'end_date': datetime.datetime.now() + timedelta(days=15),
            'priority': 'Critical',
            'assigned_to': 'IT Security Team',
            'description': 'Quarterly access review for privileged accounts',
            'location': 'Online',
            'status': 'Pending',
            'reminder_days': 3
        },
        {
            'id': 'CE-2024-003',
            'title': 'PCI DSS Annual Assessment',
            'event_type': 'Assessment',
            'framework': 'PCI DSS',
            'start_date': datetime.datetime.now() + timedelta(days=60),
            'end_date': datetime.datetime.now() + timedelta(days=65),
            'priority': 'High',
            'assigned_to': 'Compliance Team',
            'description': 'Annual PCI DSS compliance assessment',
            'location': 'Main Office',
            'status': 'Scheduled',
            'reminder_days': 14
        },
        {
            'id': 'CE-2024-004',
            'title': 'Security Awareness Training',
            'event_type': 'Training',
            'framework': 'General',
            'start_date': datetime.datetime.now() + timedelta(days=10),
            'end_date': datetime.datetime.now() + timedelta(days=10),
            'priority': 'Medium',
            'assigned_to': 'HR Team',
            'description': 'Annual security awareness training for all employees',
            'location': 'Training Center',
            'status': 'Scheduled',
            'reminder_days': 5
        },
        {
            'id': 'CE-2024-005',
            'title': 'GDPR Data Protection Review',
            'event_type': 'Review',
            'framework': 'GDPR',
            'start_date': datetime.datetime.now() + timedelta(days=45),
            'end_date': datetime.datetime.now() + timedelta(days=47),
            'priority': 'High',
            'assigned_to': 'Legal Team',
            'description': 'Annual GDPR data protection impact assessment',
            'location': 'Legal Department',
            'status': 'Scheduled',
            'reminder_days': 10
        }
    ]
    
    regulatory_deadlines = [
        {
            'id': 'RD-2024-001',
            'title': 'SOX 404 Certification',
            'regulation': 'SOX',
            'deadline': datetime.datetime.now() + timedelta(days=90),
            'frequency': 'Annual',
            'description': 'Management certification of internal controls',
            'responsible_party': 'CFO',
            'status': 'Pending',
            'priority': 'Critical',
            'consequences': 'Financial penalties, regulatory scrutiny'
        },
        {
            'id': 'RD-2024-002',
            'title': 'PCI DSS SAQ Submission',
            'regulation': 'PCI DSS',
            'deadline': datetime.datetime.now() + timedelta(days=120),
            'frequency': 'Annual',
            'description': 'Self-Assessment Questionnaire submission',
            'responsible_party': 'Compliance Officer',
            'status': 'In Progress',
            'priority': 'High',
            'consequences': 'Loss of payment processing ability'
        },
        {
            'id': 'RD-2024-003',
            'title': 'GDPR Data Processing Register',
            'regulation': 'GDPR',
            'deadline': datetime.datetime.now() + timedelta(days=30),
            'frequency': 'Quarterly',
            'description': 'Update data processing activities register',
            'responsible_party': 'DPO',
            'status': 'Pending',
            'priority': 'High',
            'consequences': 'Fines up to 4% of global revenue'
        },
        {
            'id': 'RD-2024-004',
            'title': 'HIPAA Security Assessment',
            'regulation': 'HIPAA',
            'deadline': datetime.datetime.now() + timedelta(days=180),
            'frequency': 'Annual',
            'description': 'Annual HIPAA security rule assessment',
            'responsible_party': 'Security Officer',
            'status': 'Scheduled',
            'priority': 'High',
            'consequences': 'OCR penalties, breach notification requirements'
        },
        {
            'id': 'RD-2024-005',
            'title': 'ISO 27001 Surveillance Audit',
            'regulation': 'ISO 27001',
            'deadline': datetime.datetime.now() + timedelta(days=150),
            'frequency': 'Semi-Annual',
            'description': 'Surveillance audit for ISO 27001 certification',
            'responsible_party': 'ISMS Manager',
            'status': 'Scheduled',
            'priority': 'Medium',
            'consequences': 'Certification suspension'
        }
    ]
    
    audit_schedules = [
        {
            'id': 'AS-2024-001',
            'audit_name': 'SOC 2 Type II',
            'auditor': 'Deloitte',
            'start_date': datetime.datetime.now() + timedelta(days=30),
            'end_date': datetime.datetime.now() + timedelta(days=90),
            'scope': 'Information Security Controls',
            'status': 'Scheduled',
            'lead_auditor': 'Sarah Johnson',
            'prep_meeting': datetime.datetime.now() + timedelta(days=25),
            'kickoff_meeting': datetime.datetime.now() + timedelta(days=30),
            'exit_meeting': datetime.datetime.now() + timedelta(days=85)
        },
        {
            'id': 'AS-2024-002',
            'audit_name': 'Internal Security Audit',
            'auditor': 'Internal Audit Team',
            'start_date': datetime.datetime.now() + timedelta(days=15),
            'end_date': datetime.datetime.now() + timedelta(days=45),
            'scope': 'IT Security Controls',
            'status': 'In Progress',
            'lead_auditor': 'Mike Chen',
            'prep_meeting': datetime.datetime.now() + timedelta(days=10),
            'kickoff_meeting': datetime.datetime.now() + timedelta(days=15),
            'exit_meeting': datetime.datetime.now() + timedelta(days=40)
        },
        {
            'id': 'AS-2024-003',
            'audit_name': 'PCI DSS Assessment',
            'auditor': 'KPMG',
            'start_date': datetime.datetime.now() + timedelta(days=60),
            'end_date': datetime.datetime.now() + timedelta(days=75),
            'scope': 'Payment Card Security',
            'status': 'Scheduled',
            'lead_auditor': 'David Wilson',
            'prep_meeting': datetime.datetime.now() + timedelta(days=55),
            'kickoff_meeting': datetime.datetime.now() + timedelta(days=60),
            'exit_meeting': datetime.datetime.now() + timedelta(days=70)
        }
    ]
    
    reminders = [
        {
            'id': 'REM-2024-001',
            'event_id': 'CE-2024-001',
            'title': 'SOC 2 Audit Prep Meeting',
            'reminder_date': datetime.datetime.now() + timedelta(days=23),
            'reminder_type': 'Email',
            'recipients': ['it.security@company.com', 'compliance@company.com'],
            'message': 'SOC 2 Type II audit preparation meeting in 7 days',
            'status': 'Pending'
        },
        {
            'id': 'REM-2024-002',
            'event_id': 'CE-2024-002',
            'title': 'Access Review Due',
            'reminder_date': datetime.datetime.now() + timedelta(days=12),
            'reminder_type': 'SMS',
            'recipients': ['it.security@company.com'],
            'message': 'Quarterly access review due in 3 days',
            'status': 'Pending'
        },
        {
            'id': 'REM-2024-003',
            'event_id': 'RD-2024-001',
            'title': 'SOX Certification Deadline',
            'reminder_date': datetime.datetime.now() + timedelta(days=80),
            'reminder_type': 'Email',
            'recipients': ['cfo@company.com', 'compliance@company.com'],
            'message': 'SOX 404 certification due in 10 days',
            'status': 'Pending'
        }
    ]
    
    holidays = [
        {
            'id': 'HOL-2024-001',
            'name': 'New Year\'s Day',
            'date': datetime.datetime(2024, 1, 1),
            'type': 'Federal Holiday',
            'description': 'Office closed'
        },
        {
            'id': 'HOL-2024-002',
            'name': 'Martin Luther King Jr. Day',
            'date': datetime.datetime(2024, 1, 15),
            'type': 'Federal Holiday',
            'description': 'Office closed'
        },
        {
            'id': 'HOL-2024-003',
            'name': 'Memorial Day',
            'date': datetime.datetime(2024, 5, 27),
            'type': 'Federal Holiday',
            'description': 'Office closed'
        },
        {
            'id': 'HOL-2024-004',
            'name': 'Independence Day',
            'date': datetime.datetime(2024, 7, 4),
            'type': 'Federal Holiday',
            'description': 'Office closed'
        },
        {
            'id': 'HOL-2024-005',
            'name': 'Labor Day',
            'date': datetime.datetime(2024, 9, 2),
            'type': 'Federal Holiday',
            'description': 'Office closed'
        }
    ]
    
    return compliance_events, regulatory_deadlines, audit_schedules, reminders, holidays

def main():
    st.markdown('<h1 class="main-header">Compliance Calendar</h1>', unsafe_allow_html=True)
    st.markdown("Comprehensive calendar system for managing compliance deadlines, audit schedules, and regulatory requirements")
    
    # Initialize sample data
    if not st.session_state.compliance_events:
        events, deadlines, schedules, reminders, holidays = generate_sample_data()
        st.session_state.compliance_events = events
        st.session_state.regulatory_deadlines = deadlines
        st.session_state.audit_schedules = schedules
        st.session_state.reminders = reminders
        st.session_state.holidays = holidays
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Calendar View", "Compliance Events", "Regulatory Deadlines", "Audit Schedules", "Reminders", "Holidays", "Reports", "Analytics"]
    )
    
    if page == "Calendar View":
        show_calendar_view()
    elif page == "Compliance Events":
        show_compliance_events()
    elif page == "Regulatory Deadlines":
        show_regulatory_deadlines()
    elif page == "Audit Schedules":
        show_audit_schedules()
    elif page == "Reminders":
        show_reminders()
    elif page == "Holidays":
        show_holidays()
    elif page == "Reports":
        show_reports()
    elif page == "Analytics":
        show_analytics()

def show_calendar_view():
    st.header("📅 Calendar View")
    
    # Calendar controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        view_type = st.selectbox("View Type", ["Monthly", "Weekly", "Daily"])
    
    with col2:
        selected_month = st.selectbox("Month", range(1, 13), index=datetime.datetime.now().month - 1)
    
    with col3:
        selected_year = st.selectbox("Year", range(2024, 2026), index=0)
    
    # Get current date
    current_date = datetime.datetime.now()
    selected_date = datetime.datetime(selected_year, selected_month, 1)
    
    # Display calendar
    if view_type == "Monthly":
        show_monthly_calendar(selected_date)
    elif view_type == "Weekly":
        show_weekly_calendar(selected_date)
    else:
        show_daily_calendar(selected_date)

def show_monthly_calendar(selected_date):
    st.subheader(f"📅 {selected_date.strftime('%B %Y')}")
    
    # Create calendar grid
    cal = calendar.monthcalendar(selected_date.year, selected_date.month)
    
    # Get events for the month
    month_events = [e for e in st.session_state.compliance_events 
                   if e['start_date'].month == selected_date.month and e['start_date'].year == selected_date.year]
    
    # Create calendar display
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Header
    cols = st.columns(7)
    for i, day in enumerate(days):
        cols[i].write(f"**{day}**")
    
    # Calendar body
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                # Check for events on this day
                day_events = [e for e in month_events if e['start_date'].day == day]
                
                # Display day number
                day_text = f"**{day}**"
                
                # Add event indicators
                if day_events:
                    event_indicators = []
                    for event in day_events:
                        if event['priority'] == 'Critical':
                            event_indicators.append("🔴")
                        elif event['priority'] == 'High':
                            event_indicators.append("🟠")
                        elif event['priority'] == 'Medium':
                            event_indicators.append("🟡")
                        else:
                            event_indicators.append("🟢")
                    
                    day_text += f" {' '.join(event_indicators)}"
                
                cols[i].write(day_text)
                
                # Show event details on hover/click
                if day_events:
                    with cols[i].expander(f"Events ({len(day_events)})"):
                        for event in day_events:
                            st.write(f"**{event['title']}**")
                            st.write(f"Type: {event['event_type']}")
                            st.write(f"Priority: {event['priority']}")
                            st.write(f"Assigned: {event['assigned_to']}")

def show_weekly_calendar(selected_date):
    st.subheader(f"📅 Week of {selected_date.strftime('%B %d, %Y')}")
    
    # Get week start (Monday)
    week_start = selected_date - timedelta(days=selected_date.weekday())
    
    # Create weekly view
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for i, day_name in enumerate(days):
        current_date = week_start + timedelta(days=i)
        
        # Get events for this day
        day_events = [e for e in st.session_state.compliance_events 
                     if e['start_date'].date() == current_date.date()]
        
        with st.expander(f"{day_name} - {current_date.strftime('%B %d')} ({len(day_events)} events)"):
            if day_events:
                for event in day_events:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{event['title']}**")
                        st.write(f"Type: {event['event_type']} | Framework: {event['framework']}")
                        st.write(f"Time: {event['start_date'].strftime('%H:%M')} - {event['end_date'].strftime('%H:%M')}")
                        st.write(f"Location: {event['location']}")
                    with col2:
                        if event['priority'] == 'Critical':
                            st.write("🔴 Critical")
                        elif event['priority'] == 'High':
                            st.write("🟠 High")
                        elif event['priority'] == 'Medium':
                            st.write("🟡 Medium")
                        else:
                            st.write("🟢 Low")
                    st.divider()
            else:
                st.write("No events scheduled")

def show_daily_calendar(selected_date):
    st.subheader(f"📅 {selected_date.strftime('%A, %B %d, %Y')}")
    
    # Get events for this day
    day_events = [e for e in st.session_state.compliance_events 
                 if e['start_date'].date() == selected_date.date()]
    
    # Get deadlines for this day
    day_deadlines = [d for d in st.session_state.regulatory_deadlines 
                    if d['deadline'].date() == selected_date.date()]
    
    # Display events
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Events")
        if day_events:
            for event in day_events:
                with st.expander(f"{event['start_date'].strftime('%H:%M')} - {event['title']}"):
                    st.write(f"**Type:** {event['event_type']}")
                    st.write(f"**Framework:** {event['framework']}")
                    st.write(f"**Priority:** {event['priority']}")
                    st.write(f"**Assigned To:** {event['assigned_to']}")
                    st.write(f"**Location:** {event['location']}")
                    st.write(f"**Description:** {event['description']}")
        else:
            st.write("No events scheduled")
    
    with col2:
        st.subheader("⏰ Deadlines")
        if day_deadlines:
            for deadline in day_deadlines:
                with st.expander(f"{deadline['title']}"):
                    st.write(f"**Regulation:** {deadline['regulation']}")
                    st.write(f"**Priority:** {deadline['priority']}")
                    st.write(f"**Responsible:** {deadline['responsible_party']}")
                    st.write(f"**Description:** {deadline['description']}")
                    st.write(f"**Consequences:** {deadline['consequences']}")
        else:
            st.write("No deadlines today")

def show_compliance_events():
    st.header("📋 Compliance Events")
    
    # Add new event
    with st.expander("Add New Compliance Event"):
        with st.form("new_event"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Event Title")
                event_type = st.selectbox("Event Type", ["Audit", "Assessment", "Review", "Training", "Meeting", "Deadline", "Other"])
                framework = st.selectbox("Framework", ["SOC 2", "ISO 27001", "PCI DSS", "GDPR", "HIPAA", "SOX", "NIST CSF", "General"])
                priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
            
            with col2:
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                assigned_to = st.text_input("Assigned To")
                location = st.text_input("Location")
            
            description = st.text_area("Description")
            reminder_days = st.number_input("Reminder (days before)", min_value=0, max_value=365, value=7)
            
            if st.form_submit_button("Add Event"):
                new_event = {
                    'id': f'CE-{datetime.datetime.now().year}-{len(st.session_state.compliance_events)+1:03d}',
                    'title': title,
                    'event_type': event_type,
                    'framework': framework,
                    'start_date': datetime.datetime.combine(start_date, datetime.time(9, 0)),
                    'end_date': datetime.datetime.combine(end_date, datetime.time(17, 0)),
                    'priority': priority,
                    'assigned_to': assigned_to,
                    'description': description,
                    'location': location,
                    'status': 'Scheduled',
                    'reminder_days': reminder_days
                }
                st.session_state.compliance_events.append(new_event)
                st.success("Compliance event added successfully!")
    
    # Display events
    df = pd.DataFrame(st.session_state.compliance_events)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['event_type'].unique()))
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All"] + list(df['priority'].unique()))
    with col3:
        framework_filter = st.selectbox("Filter by Framework", ["All"] + list(df['framework'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['event_type'] == type_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
    if framework_filter != "All":
        filtered_df = filtered_df[filtered_df['framework'] == framework_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Event overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Events by Type")
        type_counts = df['event_type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, 
                    title="Compliance Events by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Events by Priority")
        priority_counts = df['priority'].value_counts()
        fig = px.bar(x=priority_counts.index, y=priority_counts.values, 
                    title="Events by Priority",
                    color=priority_counts.index,
                    color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'})
        st.plotly_chart(fig, use_container_width=True)

def show_regulatory_deadlines():
    st.header("⏰ Regulatory Deadlines")
    
    # Add new deadline
    with st.expander("Add New Regulatory Deadline"):
        with st.form("new_deadline"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Deadline Title")
                regulation = st.selectbox("Regulation", ["SOX", "PCI DSS", "GDPR", "HIPAA", "ISO 27001", "NIST CSF", "CCPA", "Other"])
                deadline = st.date_input("Deadline Date")
                frequency = st.selectbox("Frequency", ["One-time", "Monthly", "Quarterly", "Semi-Annual", "Annual"])
            
            with col2:
                responsible_party = st.text_input("Responsible Party")
                priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
                status = st.selectbox("Status", ["Pending", "In Progress", "Completed", "Overdue"])
            
            description = st.text_area("Description")
            consequences = st.text_area("Consequences of Non-Compliance")
            
            if st.form_submit_button("Add Deadline"):
                new_deadline = {
                    'id': f'RD-{datetime.datetime.now().year}-{len(st.session_state.regulatory_deadlines)+1:03d}',
                    'title': title,
                    'regulation': regulation,
                    'deadline': datetime.datetime.combine(deadline, datetime.time(17, 0)),
                    'frequency': frequency,
                    'description': description,
                    'responsible_party': responsible_party,
                    'status': status,
                    'priority': priority,
                    'consequences': consequences
                }
                st.session_state.regulatory_deadlines.append(new_deadline)
                st.success("Regulatory deadline added successfully!")
    
    # Display deadlines
    df = pd.DataFrame(st.session_state.regulatory_deadlines)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        regulation_filter = st.selectbox("Filter by Regulation", ["All"] + list(df['regulation'].unique()))
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All"] + list(df['priority'].unique()))
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if regulation_filter != "All":
        filtered_df = filtered_df[filtered_df['regulation'] == regulation_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Deadline overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Deadlines by Regulation")
        regulation_counts = df['regulation'].value_counts()
        fig = px.pie(values=regulation_counts.values, names=regulation_counts.index, 
                    title="Regulatory Deadlines by Framework")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Deadlines by Status")
        status_counts = df['status'].value_counts()
        fig = px.bar(x=status_counts.index, y=status_counts.values, 
                    title="Deadlines by Status")
        st.plotly_chart(fig, use_container_width=True)

def show_audit_schedules():
    st.header("🔍 Audit Schedules")
    
    # Add new audit schedule
    with st.expander("Add New Audit Schedule"):
        with st.form("new_schedule"):
            col1, col2 = st.columns(2)
            with col1:
                audit_name = st.text_input("Audit Name")
                auditor = st.text_input("Auditor")
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
            
            with col2:
                scope = st.text_area("Scope")
                lead_auditor = st.text_input("Lead Auditor")
                status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed", "Cancelled"])
            
            prep_meeting = st.date_input("Preparation Meeting Date")
            kickoff_meeting = st.date_input("Kickoff Meeting Date")
            exit_meeting = st.date_input("Exit Meeting Date")
            
            if st.form_submit_button("Add Schedule"):
                new_schedule = {
                    'id': f'AS-{datetime.datetime.now().year}-{len(st.session_state.audit_schedules)+1:03d}',
                    'audit_name': audit_name,
                    'auditor': auditor,
                    'start_date': datetime.datetime.combine(start_date, datetime.time(9, 0)),
                    'end_date': datetime.datetime.combine(end_date, datetime.time(17, 0)),
                    'scope': scope,
                    'status': status,
                    'lead_auditor': lead_auditor,
                    'prep_meeting': datetime.datetime.combine(prep_meeting, datetime.time(10, 0)),
                    'kickoff_meeting': datetime.datetime.combine(kickoff_meeting, datetime.time(9, 0)),
                    'exit_meeting': datetime.datetime.combine(exit_meeting, datetime.time(14, 0))
                }
                st.session_state.audit_schedules.append(new_schedule)
                st.success("Audit schedule added successfully!")
    
    # Display schedules
    df = pd.DataFrame(st.session_state.audit_schedules)
    st.dataframe(df, use_container_width=True)
    
    # Schedule overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Audits by Status")
        status_counts = df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Audit Schedules by Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Audit Timeline")
        if not df.empty:
            df_timeline = df.copy()
            df_timeline['duration_days'] = (df_timeline['end_date'] - df_timeline['start_date']).dt.days
            
            fig = px.bar(df_timeline, x='audit_name', y='duration_days', 
                        title="Audit Duration (Days)",
                        labels={'duration_days': 'Duration (Days)', 'audit_name': 'Audit'})
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

def show_reminders():
    st.header("🔔 Reminders")
    
    # Add new reminder
    with st.expander("Add New Reminder"):
        with st.form("new_reminder"):
            col1, col2 = st.columns(2)
            with col1:
                event_id = st.selectbox("Event", [e['id'] for e in st.session_state.compliance_events])
                title = st.text_input("Reminder Title")
                reminder_date = st.date_input("Reminder Date")
                reminder_type = st.selectbox("Reminder Type", ["Email", "SMS", "Calendar", "Slack"])
            
            with col2:
                recipients = st.text_area("Recipients (comma-separated)")
                message = st.text_area("Message")
                status = st.selectbox("Status", ["Pending", "Sent", "Cancelled"])
            
            if st.form_submit_button("Add Reminder"):
                new_reminder = {
                    'id': f'REM-{datetime.datetime.now().year}-{len(st.session_state.reminders)+1:03d}',
                    'event_id': event_id,
                    'title': title,
                    'reminder_date': datetime.datetime.combine(reminder_date, datetime.time(9, 0)),
                    'reminder_type': reminder_type,
                    'recipients': [r.strip() for r in recipients.split(',') if r.strip()],
                    'message': message,
                    'status': status
                }
                st.session_state.reminders.append(new_reminder)
                st.success("Reminder added successfully!")
    
    # Display reminders
    df = pd.DataFrame(st.session_state.reminders)
    st.dataframe(df, use_container_width=True)
    
    # Reminder overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Reminders by Type")
        type_counts = df['reminder_type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, 
                    title="Reminders by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Reminders by Status")
        status_counts = df['status'].value_counts()
        fig = px.bar(x=status_counts.index, y=status_counts.values, 
                    title="Reminders by Status")
        st.plotly_chart(fig, use_container_width=True)

def show_holidays():
    st.header("🎉 Holidays")
    
    # Add new holiday
    with st.expander("Add New Holiday"):
        with st.form("new_holiday"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Holiday Name")
                holiday_date = st.date_input("Holiday Date")
                holiday_type = st.selectbox("Holiday Type", ["Federal Holiday", "Company Holiday", "Observance", "Other"])
            
            with col2:
                description = st.text_area("Description")
            
            if st.form_submit_button("Add Holiday"):
                new_holiday = {
                    'id': f'HOL-{datetime.datetime.now().year}-{len(st.session_state.holidays)+1:03d}',
                    'name': name,
                    'date': datetime.datetime.combine(holiday_date, datetime.time()),
                    'type': holiday_type,
                    'description': description
                }
                st.session_state.holidays.append(new_holiday)
                st.success("Holiday added successfully!")
    
    # Display holidays
    df = pd.DataFrame(st.session_state.holidays)
    st.dataframe(df, use_container_width=True)
    
    # Holiday overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Holidays by Type")
        type_counts = df['type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, 
                    title="Holidays by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Holidays by Month")
        if not df.empty:
            df['month'] = df['date'].dt.month
            month_counts = df['month'].value_counts().sort_index()
            month_names = [calendar.month_name[i] for i in month_counts.index]
            
            fig = px.bar(x=month_names, y=month_counts.values, 
                        title="Holidays by Month",
                        labels={'x': 'Month', 'y': 'Number of Holidays'})
            st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("📊 Reports & Analytics")
    
    # Report options
    report_type = st.selectbox("Select Report Type", [
        "Compliance Calendar Summary",
        "Upcoming Deadlines Report",
        "Audit Schedule Report",
        "Event Distribution Report",
        "Reminder Status Report"
    ])
    
    if report_type == "Compliance Calendar Summary":
        st.subheader("Compliance Calendar Summary Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Event Summary**")
            st.write(f"• Total Events: {len(st.session_state.compliance_events)}")
            st.write(f"• Upcoming Events: {len([e for e in st.session_state.compliance_events if e['start_date'] > datetime.datetime.now()])}")
            st.write(f"• Critical Events: {len([e for e in st.session_state.compliance_events if e['priority'] == 'Critical'])}")
            st.write(f"• High Priority Events: {len([e for e in st.session_state.compliance_events if e['priority'] == 'High'])}")
        
        with col2:
            st.write("**Deadline Summary**")
            st.write(f"• Total Deadlines: {len(st.session_state.regulatory_deadlines)}")
            st.write(f"• Upcoming Deadlines: {len([d for d in st.session_state.regulatory_deadlines if d['deadline'] > datetime.datetime.now()])}")
            st.write(f"• Overdue Deadlines: {len([d for d in st.session_state.regulatory_deadlines if d['deadline'] < datetime.datetime.now() and d['status'] != 'Completed'])}")
            st.write(f"• Completed Deadlines: {len([d for d in st.session_state.regulatory_deadlines if d['status'] == 'Completed'])}")
    
    elif report_type == "Upcoming Deadlines Report":
        st.subheader("Upcoming Deadlines Report")
        
        upcoming_deadlines = [d for d in st.session_state.regulatory_deadlines 
                            if d['deadline'] > datetime.datetime.now()]
        upcoming_deadlines.sort(key=lambda x: x['deadline'])
        
        if upcoming_deadlines:
            for deadline in upcoming_deadlines[:10]:  # Show next 10
                days_until = (deadline['deadline'] - datetime.datetime.now()).days
                st.write(f"**{deadline['title']}** - {days_until} days until due")
                st.write(f"Regulation: {deadline['regulation']} | Priority: {deadline['priority']}")
                st.write(f"Responsible: {deadline['responsible_party']}")
                st.divider()
        else:
            st.write("No upcoming deadlines")
    
    # Export functionality
    st.subheader("Export Data")
    export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
    
    if st.button("Export Data"):
        if export_format == "CSV":
            # Export to CSV
            df_events = pd.DataFrame(st.session_state.compliance_events)
            csv = df_events.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="compliance_events.csv",
                mime="text/csv"
            )
        elif export_format == "JSON":
            # Export to JSON
            json_data = json.dumps(st.session_state.compliance_events, default=str, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="compliance_events.json",
                mime="application/json"
            )

def show_analytics():
    st.header("📈 Analytics & Insights")
    
    # Calculate metrics
    total_events = len(st.session_state.compliance_events)
    upcoming_events = len([e for e in st.session_state.compliance_events if e['start_date'] > datetime.datetime.now()])
    critical_events = len([e for e in st.session_state.compliance_events if e['priority'] == 'Critical'])
    
    total_deadlines = len(st.session_state.regulatory_deadlines)
    upcoming_deadlines = len([d for d in st.session_state.regulatory_deadlines if d['deadline'] > datetime.datetime.now()])
    overdue_deadlines = len([d for d in st.session_state.regulatory_deadlines if d['deadline'] < datetime.datetime.now() and d['status'] != 'Completed'])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", total_events)
        st.metric("Upcoming Events", upcoming_events)
    
    with col2:
        st.metric("Critical Events", critical_events)
        st.metric("Total Deadlines", total_deadlines)
    
    with col3:
        st.metric("Upcoming Deadlines", upcoming_deadlines)
        st.metric("Overdue Deadlines", overdue_deadlines)
    
    with col4:
        st.metric("Active Audits", len([a for a in st.session_state.audit_schedules if a['status'] == 'In Progress']))
        st.metric("Pending Reminders", len([r for r in st.session_state.reminders if r['status'] == 'Pending']))
    
    # Event trends
    st.subheader("Event Trends")
    df_events = pd.DataFrame(st.session_state.compliance_events)
    if not df_events.empty:
        df_events['start_date'] = pd.to_datetime(df_events['start_date'])
        df_events['month'] = df_events['start_date'].dt.to_period('M')
        
        monthly_events = df_events.groupby('month').size().reset_index(name='count')
        monthly_events['month'] = monthly_events['month'].astype(str)
        
        fig = px.line(monthly_events, x='month', y='count', 
                      title="Monthly Compliance Events",
                      labels={'count': 'Number of Events', 'month': 'Month'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Framework distribution
    st.subheader("Events by Framework")
    if not df_events.empty:
        framework_counts = df_events['framework'].value_counts()
        fig = px.pie(values=framework_counts.values, names=framework_counts.index, 
                    title="Compliance Events by Framework")
        st.plotly_chart(fig, use_container_width=True)
    
    # Priority distribution
    st.subheader("Events by Priority")
    if not df_events.empty:
        priority_counts = df_events['priority'].value_counts()
        fig = px.bar(x=priority_counts.index, y=priority_counts.values, 
                    title="Events by Priority",
                    color=priority_counts.index,
                    color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'})
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
