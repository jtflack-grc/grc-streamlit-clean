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
    page_title="Incident Response Management",
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

    /* Incident severity styling */
    .severity-critical { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .severity-high { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
    .severity-medium { background-color: rgba(255, 193, 7, 0.1); border-left: 4px solid #ffc107; }
    .severity-low { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'incidents' not in st.session_state:
    st.session_state.incidents = []
if 'response_teams' not in st.session_state:
    st.session_state.response_teams = []
if 'playbooks' not in st.session_state:
    st.session_state.playbooks = []

def generate_sample_data():
    """Generate sample incident data"""
    incident_types = [
        'Data Breach', 'Malware Infection', 'Phishing Attack', 'DDoS Attack',
        'Insider Threat', 'Physical Security Breach', 'System Compromise',
        'Social Engineering', 'Ransomware', 'Supply Chain Attack'
    ]
    
    severity_levels = ['Critical', 'High', 'Medium', 'Low']
    statuses = ['Open', 'In Progress', 'Contained', 'Resolved', 'Closed']
    
    sample_incidents = []
    for i in range(20):
        incident_date = datetime.datetime.now() - timedelta(days=random.randint(1, 365))
        status = random.choice(statuses)
        
        # Calculate resolution time based on status
        if status in ['Resolved', 'Closed']:
            resolution_date = incident_date + timedelta(days=random.randint(1, 30))
            resolution_time = (resolution_date - incident_date).days
        else:
            resolution_date = None
            resolution_time = None
        
        incident = {
            'id': f'INC-{2024:04d}-{i+1:03d}',
            'title': f'{random.choice(incident_types)} Incident',
            'description': f'Sample incident description for incident {i+1}',
            'type': random.choice(incident_types),
            'severity': random.choice(severity_levels),
            'status': status,
            'reported_date': incident_date,
            'resolution_date': resolution_date,
            'resolution_time_days': resolution_time,
            'reporter': f'User {random.randint(1, 50)}',
            'assigned_to': f'Team {random.randint(1, 5)}',
            'affected_systems': random.randint(1, 10),
            'affected_users': random.randint(1, 1000),
            'financial_impact': random.randint(1000, 100000),
            'data_compromised': random.choice([True, False]),
            'pii_involved': random.choice([True, False]),
            'regulatory_impact': random.choice(['GDPR', 'HIPAA', 'PCI-DSS', 'None']),
            'lessons_learned': f'Lesson learned from incident {i+1}',
            'prevention_measures': f'Prevention measure for incident {i+1}'
        }
        sample_incidents.append(incident)
    
    return sample_incidents

def generate_response_teams():
    """Generate sample response teams"""
    teams = [
        {
            'id': 'IRT-001',
            'name': 'Security Incident Response Team',
            'lead': 'John Smith',
            'members': ['Alice Johnson', 'Bob Wilson', 'Carol Davis'],
            'specialization': 'General Security Incidents',
            'availability': '24/7',
            'contact': 'sirt@company.com'
        },
        {
            'id': 'IRT-002',
            'name': 'Data Breach Response Team',
            'lead': 'Sarah Miller',
            'members': ['David Brown', 'Emma Garcia', 'Frank Lee'],
            'specialization': 'Data Breaches and Privacy Incidents',
            'availability': 'Business Hours',
            'contact': 'dbrt@company.com'
        },
        {
            'id': 'IRT-003',
            'name': 'Malware Response Team',
            'lead': 'Mike Chen',
            'members': ['Grace Taylor', 'Henry Anderson', 'Ivy Martinez'],
            'specialization': 'Malware and Ransomware Incidents',
            'availability': '24/7',
            'contact': 'mrt@company.com'
        }
    ]
    return teams

def generate_playbooks():
    """Generate sample incident response playbooks"""
    playbooks = [
        {
            'id': 'PB-001',
            'name': 'Data Breach Response Playbook',
            'incident_type': 'Data Breach',
            'severity': ['Critical', 'High'],
            'steps': [
                'Immediate containment and isolation',
                'Preserve evidence and logs',
                'Notify legal and compliance teams',
                'Assess scope and impact',
                'Notify affected parties',
                'Implement remediation measures',
                'Conduct post-incident review'
            ],
            'timeline': '72 hours',
            'stakeholders': ['Legal', 'Compliance', 'IT', 'Communications']
        },
        {
            'id': 'PB-002',
            'name': 'Ransomware Response Playbook',
            'incident_type': 'Ransomware',
            'severity': ['Critical', 'High'],
            'steps': [
                'Isolate affected systems',
                'Assess scope of encryption',
                'Check for data exfiltration',
                'Evaluate backup availability',
                'Decide on ransom payment',
                'Implement recovery procedures',
                'Document lessons learned'
            ],
            'timeline': '24 hours',
            'stakeholders': ['IT', 'Legal', 'Executive', 'Insurance']
        },
        {
            'id': 'PB-003',
            'name': 'Phishing Incident Response Playbook',
            'incident_type': 'Phishing Attack',
            'severity': ['Medium', 'High'],
            'steps': [
                'Remove malicious emails',
                'Block malicious domains/IPs',
                'Scan affected systems',
                'Reset compromised credentials',
                'Educate affected users',
                'Monitor for suspicious activity'
            ],
            'timeline': '4 hours',
            'stakeholders': ['IT', 'Security', 'HR']
        }
    ]
    return playbooks

# Initialize sample data if empty
if not st.session_state.incidents:
    st.session_state.incidents = generate_sample_data()
if not st.session_state.response_teams:
    st.session_state.response_teams = generate_response_teams()
if not st.session_state.playbooks:
    st.session_state.playbooks = generate_playbooks()

def calculate_metrics(incidents):
    """Calculate incident response metrics"""
    df = pd.DataFrame(incidents)
    
    metrics = {
        'total_incidents': len(incidents),
        'open_incidents': len(df[df['status'].isin(['Open', 'In Progress'])]),
        'resolved_incidents': len(df[df['status'].isin(['Resolved', 'Closed'])]),
        'critical_incidents': len(df[df['severity'] == 'Critical']),
        'avg_resolution_time': df['resolution_time_days'].dropna().mean() if not df['resolution_time_days'].dropna().empty else 0,
        'data_breaches': len(df[df['type'] == 'Data Breach']),
        'malware_incidents': len(df[df['type'].isin(['Malware Infection', 'Ransomware'])]),
        'total_financial_impact': df['financial_impact'].sum(),
        'pii_incidents': len(df[df['pii_involved'] == True])
    }
    
    return metrics

def main():
    st.markdown("<h1 class='main-header'>Incident Response Management System</h1>", unsafe_allow_html=True)
    st.markdown("Comprehensive incident tracking, response workflows, and reporting capabilities")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard", "Incident Management", "Response Teams", "Playbooks", "Analytics", "Reports"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Incident Management":
        show_incident_management()
    elif page == "Response Teams":
        show_response_teams()
    elif page == "Playbooks":
        show_playbooks()
    elif page == "Analytics":
        show_analytics()
    elif page == "Reports":
        show_reports()

def show_dashboard():
    """Show main dashboard"""
    st.header("📊 Incident Response Dashboard")
    
    # Calculate metrics
    metrics = calculate_metrics(st.session_state.incidents)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Incidents", metrics['total_incidents'])
    
    with col2:
        st.metric("Open Incidents", metrics['open_incidents'])
    
    with col3:
        st.metric("Critical Incidents", metrics['critical_incidents'])
    
    with col4:
        st.metric("Avg Resolution (Days)", f"{metrics['avg_resolution_time']:.1f}")
    
    # Recent incidents
    st.subheader("Recent Incidents")
    df = pd.DataFrame(st.session_state.incidents)
    recent_incidents = df.sort_values('reported_date', ascending=False).head(10)
    
    if not recent_incidents.empty:
        # Create a formatted display
        for _, incident in recent_incidents.iterrows():
            with st.expander(f"{incident['id']} - {incident['title']} ({incident['status']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Type:** {incident['type']}")
                    st.write(f"**Severity:** {incident['severity']}")
                    st.write(f"**Reported:** {incident['reported_date'].strftime('%Y-%m-%d')}")
                with col2:
                    st.write(f"**Assigned:** {incident['assigned_to']}")
                    st.write(f"**Affected Users:** {incident['affected_users']}")
                    if incident['resolution_time_days']:
                        st.write(f"**Resolution Time:** {incident['resolution_time_days']} days")
    
    # Incident trends
    st.subheader("Incident Trends")
    col1, col2 = st.columns(2)
    
    with col1:
        # Incident type distribution
        type_counts = df['type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, title="Incident Types")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Severity distribution
        severity_counts = df['severity'].value_counts()
        fig = px.bar(x=severity_counts.index, y=severity_counts.values, title="Incident Severity")
        st.plotly_chart(fig, use_container_width=True)

def show_incident_management():
    """Show incident management interface"""
    st.header("📋 Incident Management")
    
    # Add new incident
    with st.expander("➕ Add New Incident", expanded=False):
        with st.form("new_incident"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Incident Title")
                incident_type = st.selectbox("Incident Type", [
                    'Data Breach', 'Malware Infection', 'Phishing Attack', 'DDoS Attack',
                    'Insider Threat', 'Physical Security Breach', 'System Compromise',
                    'Social Engineering', 'Ransomware', 'Supply Chain Attack'
                ])
                severity = st.selectbox("Severity", ['Critical', 'High', 'Medium', 'Low'])
                description = st.text_area("Description")
            
            with col2:
                reporter = st.text_input("Reporter")
                assigned_to = st.selectbox("Assigned To", [team['name'] for team in st.session_state.response_teams])
                affected_systems = st.number_input("Affected Systems", min_value=1, value=1)
                affected_users = st.number_input("Affected Users", min_value=1, value=1)
            
            submitted = st.form_submit_button("Create Incident")
            
            if submitted and title:
                new_incident = {
                    'id': f'INC-{datetime.datetime.now().year:04d}-{len(st.session_state.incidents)+1:03d}',
                    'title': title,
                    'description': description,
                    'type': incident_type,
                    'severity': severity,
                    'status': 'Open',
                    'reported_date': datetime.datetime.now(),
                    'resolution_date': None,
                    'resolution_time_days': None,
                    'reporter': reporter,
                    'assigned_to': assigned_to,
                    'affected_systems': affected_systems,
                    'affected_users': affected_users,
                    'financial_impact': 0,
                    'data_compromised': False,
                    'pii_involved': False,
                    'regulatory_impact': 'None',
                    'lessons_learned': '',
                    'prevention_measures': ''
                }
                st.session_state.incidents.append(new_incident)
                st.success("Incident created successfully!")
                st.rerun()
    
    # Incident list with filters
    st.subheader("Incident List")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox("Status Filter", ['All'] + list(set([inc['status'] for inc in st.session_state.incidents])))
    
    with col2:
        severity_filter = st.selectbox("Severity Filter", ['All'] + list(set([inc['severity'] for inc in st.session_state.incidents])))
    
    with col3:
        type_filter = st.selectbox("Type Filter", ['All'] + list(set([inc['type'] for inc in st.session_state.incidents])))
    
    with col4:
        date_filter = st.date_input("Date Filter", value=datetime.datetime.now().date())
    
    # Filter incidents
    filtered_incidents = st.session_state.incidents
    if status_filter != 'All':
        filtered_incidents = [inc for inc in filtered_incidents if inc['status'] == status_filter]
    if severity_filter != 'All':
        filtered_incidents = [inc for inc in filtered_incidents if inc['severity'] == severity_filter]
    if type_filter != 'All':
        filtered_incidents = [inc for inc in filtered_incidents if inc['type'] == type_filter]
    
    # Display incidents
    df = pd.DataFrame(filtered_incidents)
    if not df.empty:
        # Create a more detailed view
        for _, incident in df.iterrows():
            with st.expander(f"{incident['id']} - {incident['title']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Status:** {incident['status']}")
                    st.write(f"**Severity:** {incident['severity']}")
                    st.write(f"**Type:** {incident['type']}")
                    st.write(f"**Reported:** {incident['reported_date'].strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    st.write(f"**Assigned:** {incident['assigned_to']}")
                    st.write(f"**Affected Systems:** {incident['affected_systems']}")
                    st.write(f"**Affected Users:** {incident['affected_users']}")
                    if incident['resolution_time_days']:
                        st.write(f"**Resolution Time:** {incident['resolution_time_days']} days")
                
                with col3:
                    st.write(f"**Financial Impact:** ${incident['financial_impact']:,}")
                    st.write(f"**Data Compromised:** {'Yes' if incident['data_compromised'] else 'No'}")
                    st.write(f"**PII Involved:** {'Yes' if incident['pii_involved'] else 'No'}")
                    st.write(f"**Regulatory Impact:** {incident['regulatory_impact']}")
                
                # Update incident
                if st.button(f"Update {incident['id']}", key=f"update_{incident['id']}"):
                    st.session_state.editing_incident = incident['id']
                
                if st.session_state.get('editing_incident') == incident['id']:
                    with st.form(f"update_form_{incident['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_status = st.selectbox("Status", ['Open', 'In Progress', 'Contained', 'Resolved', 'Closed'], 
                                                    index=['Open', 'In Progress', 'Contained', 'Resolved', 'Closed'].index(incident['status']))
                            new_severity = st.selectbox("Severity", ['Critical', 'High', 'Medium', 'Low'],
                                                      index=['Critical', 'High', 'Medium', 'Low'].index(incident['severity']))
                            financial_impact = st.number_input("Financial Impact ($)", value=incident['financial_impact'])
                        
                        with col2:
                            data_compromised = st.checkbox("Data Compromised", value=incident['data_compromised'])
                            pii_involved = st.checkbox("PII Involved", value=incident['pii_involved'])
                            regulatory_impact = st.selectbox("Regulatory Impact", ['None', 'GDPR', 'HIPAA', 'PCI-DSS'],
                                                           index=['None', 'GDPR', 'HIPAA', 'PCI-DSS'].index(incident['regulatory_impact']))
                        
                        lessons_learned = st.text_area("Lessons Learned", value=incident['lessons_learned'])
                        prevention_measures = st.text_area("Prevention Measures", value=incident['prevention_measures'])
                        
                        if st.form_submit_button("Update Incident"):
                            # Update incident
                            for i, inc in enumerate(st.session_state.incidents):
                                if inc['id'] == incident['id']:
                                    st.session_state.incidents[i].update({
                                        'status': new_status,
                                        'severity': new_severity,
                                        'financial_impact': financial_impact,
                                        'data_compromised': data_compromised,
                                        'pii_involved': pii_involved,
                                        'regulatory_impact': regulatory_impact,
                                        'lessons_learned': lessons_learned,
                                        'prevention_measures': prevention_measures
                                    })
                                    
                                    # Set resolution date if resolved
                                    if new_status in ['Resolved', 'Closed'] and not inc['resolution_date']:
                                        st.session_state.incidents[i]['resolution_date'] = datetime.datetime.now()
                                        st.session_state.incidents[i]['resolution_time_days'] = (
                                            st.session_state.incidents[i]['resolution_date'] - inc['reported_date']
                                        ).days
                                    
                                    break
                            
                            st.success("Incident updated successfully!")
                            st.rerun()

def show_response_teams():
    """Show response teams management"""
    st.header("👥 Response Teams")
    
    # Add new team
    with st.expander("➕ Add New Response Team", expanded=False):
        with st.form("new_team"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Team Name")
                lead = st.text_input("Team Lead")
                specialization = st.text_input("Specialization")
            
            with col2:
                availability = st.selectbox("Availability", ["24/7", "Business Hours", "On-Call"])
                contact = st.text_input("Contact Email")
                members = st.text_area("Team Members (one per line)")
            
            submitted = st.form_submit_button("Create Team")
            
            if submitted and name:
                new_team = {
                    'id': f'IRT-{len(st.session_state.response_teams)+1:03d}',
                    'name': name,
                    'lead': lead,
                    'members': [member.strip() for member in members.split('\n') if member.strip()],
                    'specialization': specialization,
                    'availability': availability,
                    'contact': contact
                }
                st.session_state.response_teams.append(new_team)
                st.success("Team created successfully!")
                st.rerun()
    
    # Display teams
    st.subheader("Response Teams")
    
    for team in st.session_state.response_teams:
        with st.expander(f"{team['name']} ({team['id']})", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Lead:** {team['lead']}")
                st.write(f"**Specialization:** {team['specialization']}")
                st.write(f"**Availability:** {team['availability']}")
            
            with col2:
                st.write(f"**Contact:** {team['contact']}")
                st.write(f"**Members:** {len(team['members'])}")
                st.write("**Team Members:**")
                for member in team['members']:
                    st.write(f"  - {member}")

def show_playbooks():
    """Show incident response playbooks"""
    st.header("📚 Response Playbooks")
    
    # Add new playbook
    with st.expander("➕ Add New Playbook", expanded=False):
        with st.form("new_playbook"):
            name = st.text_input("Playbook Name")
            incident_type = st.selectbox("Incident Type", [
                'Data Breach', 'Malware Infection', 'Phishing Attack', 'DDoS Attack',
                'Insider Threat', 'Physical Security Breach', 'System Compromise',
                'Social Engineering', 'Ransomware', 'Supply Chain Attack'
            ])
            severity = st.multiselect("Applicable Severity", ['Critical', 'High', 'Medium', 'Low'])
            timeline = st.text_input("Response Timeline")
            steps = st.text_area("Response Steps (one per line)")
            stakeholders = st.text_area("Stakeholders (one per line)")
            
            submitted = st.form_submit_button("Create Playbook")
            
            if submitted and name:
                new_playbook = {
                    'id': f'PB-{len(st.session_state.playbooks)+1:03d}',
                    'name': name,
                    'incident_type': incident_type,
                    'severity': severity,
                    'steps': [step.strip() for step in steps.split('\n') if step.strip()],
                    'timeline': timeline,
                    'stakeholders': [stakeholder.strip() for stakeholder in stakeholders.split('\n') if stakeholder.strip()]
                }
                st.session_state.playbooks.append(new_playbook)
                st.success("Playbook created successfully!")
                st.rerun()
    
    # Display playbooks
    st.subheader("Available Playbooks")
    
    for playbook in st.session_state.playbooks:
        with st.expander(f"{playbook['name']} ({playbook['id']})", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Incident Type:** {playbook['incident_type']}")
                st.write(f"**Severity:** {', '.join(playbook['severity'])}")
                st.write(f"**Timeline:** {playbook['timeline']}")
            
            with col2:
                st.write(f"**Stakeholders:** {len(playbook['stakeholders'])}")
                st.write("**Stakeholders:**")
                for stakeholder in playbook['stakeholders']:
                    st.write(f"  - {stakeholder}")
            
            st.write("**Response Steps:**")
            for i, step in enumerate(playbook['steps'], 1):
                st.write(f"{i}. {step}")

def show_analytics():
    """Show analytics and insights"""
    st.header("📈 Analytics & Insights")
    
    metrics = calculate_metrics(st.session_state.incidents)
    df = pd.DataFrame(st.session_state.incidents)
    
    # Time series analysis
    st.subheader("Incident Trends Over Time")
    
    # Monthly incident counts
    df['month'] = df['reported_date'].dt.to_period('M')
    monthly_counts = df.groupby('month').size().reset_index(name='count')
    monthly_counts['month'] = monthly_counts['month'].astype(str)
    
    fig = px.line(monthly_counts, x='month', y='count', title="Monthly Incident Volume")
    st.plotly_chart(fig, use_container_width=True)
    
    # Resolution time analysis
    st.subheader("Resolution Time Analysis")
    
    resolved_incidents = df[df['resolution_time_days'].notna()]
    if not resolved_incidents.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Resolution time by severity
            avg_resolution_by_severity = resolved_incidents.groupby('severity')['resolution_time_days'].mean()
            fig = px.bar(x=avg_resolution_by_severity.index, y=avg_resolution_by_severity.values,
                        title="Average Resolution Time by Severity")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Resolution time by type
            avg_resolution_by_type = resolved_incidents.groupby('type')['resolution_time_days'].mean().sort_values(ascending=False)
            fig = px.bar(x=avg_resolution_by_type.index, y=avg_resolution_by_type.values,
                        title="Average Resolution Time by Incident Type")
            st.plotly_chart(fig, use_container_width=True)
    
    # Financial impact analysis
    st.subheader("Financial Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Financial impact by severity
        impact_by_severity = df.groupby('severity')['financial_impact'].sum()
        fig = px.pie(values=impact_by_severity.values, names=impact_by_severity.index,
                    title="Financial Impact by Severity")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Financial impact by type
        impact_by_type = df.groupby('type')['financial_impact'].sum().sort_values(ascending=False)
        fig = px.bar(x=impact_by_type.index, y=impact_by_type.values,
                    title="Financial Impact by Incident Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Team performance
    st.subheader("Team Performance")
    
    team_performance = df.groupby('assigned_to').agg({
        'id': 'count',
        'resolution_time_days': 'mean',
        'financial_impact': 'sum'
    }).rename(columns={'id': 'incidents_handled'})
    
    st.dataframe(team_performance, use_container_width=True)

def show_reports():
    """Show reporting interface"""
    st.header("📊 Reports")
    
    # Report generation
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox("Report Type", [
            "Incident Summary Report",
            "Response Time Analysis",
            "Financial Impact Report",
            "Team Performance Report",
            "Compliance Report"
        ])
    
    with col2:
        date_range = st.selectbox("Date Range", [
            "Last 30 Days",
            "Last 90 Days",
            "Last 6 Months",
            "Last Year",
            "All Time"
        ])
    
    if st.button("Generate Report"):
        st.subheader(f"{report_type} - {date_range}")
        
        # Filter data based on date range
        end_date = datetime.datetime.now()
        if date_range == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif date_range == "Last 90 Days":
            start_date = end_date - timedelta(days=90)
        elif date_range == "Last 6 Months":
            start_date = end_date - timedelta(days=180)
        elif date_range == "Last Year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = datetime.datetime.min
        
        filtered_df = df[(df['reported_date'] >= start_date) & (df['reported_date'] <= end_date)]
        
        if report_type == "Incident Summary Report":
            show_incident_summary_report(filtered_df)
        elif report_type == "Response Time Analysis":
            show_response_time_report(filtered_df)
        elif report_type == "Financial Impact Report":
            show_financial_impact_report(filtered_df)
        elif report_type == "Team Performance Report":
            show_team_performance_report(filtered_df)
        elif report_type == "Compliance Report":
            show_compliance_report(filtered_df)

def show_incident_summary_report(df):
    """Show incident summary report"""
    st.write("### Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Incidents", len(df))
    
    with col2:
        st.metric("Open Incidents", len(df[df['status'].isin(['Open', 'In Progress'])]))
    
    with col3:
        st.metric("Critical Incidents", len(df[df['severity'] == 'Critical']))
    
    with col4:
        avg_resolution = df['resolution_time_days'].dropna().mean()
        st.metric("Avg Resolution (Days)", f"{avg_resolution:.1f}" if not pd.isna(avg_resolution) else "N/A")
    
    st.write("### Incident Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**By Type:**")
        type_counts = df['type'].value_counts()
        for incident_type, count in type_counts.items():
            st.write(f"- {incident_type}: {count}")
    
    with col2:
        st.write("**By Severity:**")
        severity_counts = df['severity'].value_counts()
        for severity, count in severity_counts.items():
            st.write(f"- {severity}: {count}")

def show_response_time_report(df):
    """Show response time analysis report"""
    resolved_df = df[df['resolution_time_days'].notna()]
    
    if resolved_df.empty:
        st.warning("No resolved incidents in the selected time period.")
        return
    
    st.write("### Response Time Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Average Resolution Time:** {resolved_df['resolution_time_days'].mean():.1f} days")
        st.write(f"**Median Resolution Time:** {resolved_df['resolution_time_days'].median():.1f} days")
        st.write(f"**Fastest Resolution:** {resolved_df['resolution_time_days'].min():.1f} days")
        st.write(f"**Slowest Resolution:** {resolved_df['resolution_time_days'].max():.1f} days")
    
    with col2:
        st.write("**Resolution Time by Severity:**")
        severity_times = resolved_df.groupby('severity')['resolution_time_days'].mean()
        for severity, time in severity_times.items():
            st.write(f"- {severity}: {time:.1f} days")

def show_financial_impact_report(df):
    """Show financial impact report"""
    st.write("### Financial Impact Analysis")
    
    total_impact = df['financial_impact'].sum()
    st.write(f"**Total Financial Impact:** ${total_impact:,}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Impact by Severity:**")
        severity_impact = df.groupby('severity')['financial_impact'].sum()
        for severity, impact in severity_impact.items():
            st.write(f"- {severity}: ${impact:,}")
    
    with col2:
        st.write("**Impact by Type:**")
        type_impact = df.groupby('type')['financial_impact'].sum().sort_values(ascending=False)
        for incident_type, impact in type_impact.head(5).items():
            st.write(f"- {incident_type}: ${impact:,}")

def show_team_performance_report(df):
    """Show team performance report"""
    st.write("### Team Performance Analysis")
    
    team_performance = df.groupby('assigned_to').agg({
        'id': 'count',
        'resolution_time_days': 'mean',
        'financial_impact': 'sum'
    }).rename(columns={'id': 'incidents_handled'})
    
    st.dataframe(team_performance, use_container_width=True)

def show_compliance_report(df):
    """Show compliance report"""
    st.write("### Compliance Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Regulatory Impact:**")
        regulatory_counts = df['regulatory_impact'].value_counts()
        for regulation, count in regulatory_counts.items():
            st.write(f"- {regulation}: {count} incidents")
    
    with col2:
        st.write("**Data Protection:**")
        pii_incidents = len(df[df['pii_involved'] == True])
        data_compromised = len(df[df['data_compromised'] == True])
        st.write(f"- PII Involved: {pii_incidents} incidents")
        st.write(f"- Data Compromised: {data_compromised} incidents")

if __name__ == "__main__":
    main()
