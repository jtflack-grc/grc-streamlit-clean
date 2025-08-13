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
    page_title="Audit Management System",
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
if 'audits' not in st.session_state:
    st.session_state.audits = []
if 'findings' not in st.session_state:
    st.session_state.findings = []
if 'auditors' not in st.session_state:
    st.session_state.auditors = []
if 'audit_plans' not in st.session_state:
    st.session_state.audit_plans = []
if 'evidence' not in st.session_state:
    st.session_state.evidence = []

def generate_sample_data():
    """Generate sample audit management data"""
    audits = [
        {
            'id': 'AUD-2024-001',
            'name': 'SOC 2 Type II Audit',
            'type': 'External',
            'framework': 'SOC 2',
            'scope': 'Information Security Controls',
            'start_date': datetime.datetime.now() - timedelta(days=60),
            'end_date': datetime.datetime.now() - timedelta(days=30),
            'status': 'Completed',
            'auditor': 'Deloitte',
            'lead_auditor': 'Sarah Johnson',
            'rating': 'Clean Opinion',
            'findings_count': 3,
            'critical_findings': 0,
            'high_findings': 1,
            'medium_findings': 2,
            'low_findings': 0
        },
        {
            'id': 'AUD-2024-002',
            'name': 'ISO 27001 Internal Audit',
            'type': 'Internal',
            'framework': 'ISO 27001',
            'scope': 'Information Security Management System',
            'start_date': datetime.datetime.now() - timedelta(days=30),
            'end_date': datetime.datetime.now() - timedelta(days=15),
            'status': 'In Progress',
            'auditor': 'Internal Audit Team',
            'lead_auditor': 'Mike Chen',
            'rating': 'In Progress',
            'findings_count': 8,
            'critical_findings': 1,
            'high_findings': 3,
            'medium_findings': 3,
            'low_findings': 1
        },
        {
            'id': 'AUD-2024-003',
            'name': 'PCI DSS Compliance Audit',
            'type': 'External',
            'framework': 'PCI DSS',
            'scope': 'Payment Card Data Security',
            'start_date': datetime.datetime.now() - timedelta(days=90),
            'end_date': datetime.datetime.now() - timedelta(days=45),
            'status': 'Completed',
            'auditor': 'KPMG',
            'lead_auditor': 'David Wilson',
            'rating': 'Compliant',
            'findings_count': 5,
            'critical_findings': 0,
            'high_findings': 2,
            'medium_findings': 2,
            'low_findings': 1
        },
        {
            'id': 'AUD-2024-004',
            'name': 'GDPR Compliance Review',
            'type': 'Internal',
            'framework': 'GDPR',
            'scope': 'Data Protection and Privacy',
            'start_date': datetime.datetime.now() - timedelta(days=15),
            'end_date': datetime.datetime.now() + timedelta(days=15),
            'status': 'Planned',
            'auditor': 'Internal Audit Team',
            'lead_auditor': 'Lisa Rodriguez',
            'rating': 'Not Started',
            'findings_count': 0,
            'critical_findings': 0,
            'high_findings': 0,
            'medium_findings': 0,
            'low_findings': 0
        },
        {
            'id': 'AUD-2024-005',
            'name': 'HITRUST CSF Assessment',
            'type': 'External',
            'framework': 'HITRUST CSF',
            'scope': 'Healthcare Information Security',
            'start_date': datetime.datetime.now() + timedelta(days=30),
            'end_date': datetime.datetime.now() + timedelta(days=90),
            'status': 'Planned',
            'auditor': 'Coalfire',
            'lead_auditor': 'Robert Thompson',
            'rating': 'Not Started',
            'findings_count': 0,
            'critical_findings': 0,
            'high_findings': 0,
            'medium_findings': 0,
            'low_findings': 0
        }
    ]
    
    findings = [
        {
            'id': 'FND-2024-001',
            'audit_id': 'AUD-2024-001',
            'title': 'Access Review Not Performed Quarterly',
            'description': 'Quarterly access reviews were not performed for all privileged accounts',
            'severity': 'High',
            'category': 'Access Control',
            'control_id': 'CC6.1',
            'status': 'Open',
            'assigned_to': 'IT Security Team',
            'due_date': datetime.datetime.now() + timedelta(days=30),
            'remediation_plan': 'Implement automated quarterly access review process',
            'evidence_required': 'Access review reports, approval documentation'
        },
        {
            'id': 'FND-2024-002',
            'audit_id': 'AUD-2024-001',
            'title': 'Vendor Risk Assessment Incomplete',
            'description': 'Vendor risk assessments missing for 3 critical vendors',
            'severity': 'Medium',
            'category': 'Vendor Management',
            'control_id': 'CC9.1',
            'status': 'In Progress',
            'assigned_to': 'Procurement Team',
            'due_date': datetime.datetime.now() + timedelta(days=45),
            'remediation_plan': 'Complete vendor risk assessments for all critical vendors',
            'evidence_required': 'Vendor assessment reports, risk treatment plans'
        },
        {
            'id': 'FND-2024-003',
            'audit_id': 'AUD-2024-001',
            'title': 'Security Awareness Training Overdue',
            'description': 'Annual security awareness training not completed for 15% of employees',
            'severity': 'Medium',
            'category': 'Training',
            'control_id': 'CC2.1',
            'status': 'Open',
            'assigned_to': 'HR Team',
            'due_date': datetime.datetime.now() + timedelta(days=20),
            'remediation_plan': 'Schedule and complete training for remaining employees',
            'evidence_required': 'Training completion reports, attendance records'
        },
        {
            'id': 'FND-2024-004',
            'audit_id': 'AUD-2024-002',
            'title': 'Critical Security Patch Missing',
            'description': 'Critical security patch CVE-2024-1234 not applied to production systems',
            'severity': 'Critical',
            'category': 'System Security',
            'control_id': 'A.12.6.1',
            'status': 'In Progress',
            'assigned_to': 'IT Operations',
            'due_date': datetime.datetime.now() + timedelta(days=7),
            'remediation_plan': 'Apply critical security patch during next maintenance window',
            'evidence_required': 'Patch deployment logs, system scan results'
        },
        {
            'id': 'FND-2024-005',
            'audit_id': 'AUD-2024-002',
            'title': 'Incident Response Plan Not Tested',
            'description': 'Incident response plan has not been tested in the last 12 months',
            'severity': 'High',
            'category': 'Incident Response',
            'control_id': 'A.16.1.5',
            'status': 'Open',
            'assigned_to': 'Security Team',
            'due_date': datetime.datetime.now() + timedelta(days=60),
            'remediation_plan': 'Schedule and conduct incident response tabletop exercise',
            'evidence_required': 'Exercise documentation, lessons learned report'
        }
    ]
    
    auditors = [
        {
            'id': 'AUD-001',
            'name': 'Sarah Johnson',
            'firm': 'Deloitte',
            'specialization': 'SOC 2, ISO 27001',
            'experience_years': 8,
            'certifications': ['CISA', 'CISSP', 'ISO 27001 Lead Auditor'],
            'contact': 'sarah.johnson@deloitte.com',
            'status': 'Active'
        },
        {
            'id': 'AUD-002',
            'name': 'Mike Chen',
            'firm': 'Internal Audit Team',
            'specialization': 'Internal Audits, Risk Management',
            'experience_years': 5,
            'certifications': ['CIA', 'CRMA'],
            'contact': 'mike.chen@company.com',
            'status': 'Active'
        },
        {
            'id': 'AUD-003',
            'name': 'David Wilson',
            'firm': 'KPMG',
            'specialization': 'PCI DSS, Financial Audits',
            'experience_years': 12,
            'certifications': ['CISA', 'QSA', 'CISM'],
            'contact': 'david.wilson@kpmg.com',
            'status': 'Active'
        },
        {
            'id': 'AUD-004',
            'name': 'Lisa Rodriguez',
            'firm': 'Internal Audit Team',
            'specialization': 'Privacy, GDPR, Data Protection',
            'experience_years': 6,
            'certifications': ['CIPP/E', 'CIA'],
            'contact': 'lisa.rodriguez@company.com',
            'status': 'Active'
        },
        {
            'id': 'AUD-005',
            'name': 'Robert Thompson',
            'firm': 'Coalfire',
            'specialization': 'HITRUST, Healthcare Security',
            'experience_years': 10,
            'certifications': ['HITRUST CCSFP', 'CISSP', 'HCISPP'],
            'contact': 'robert.thompson@coalfire.com',
            'status': 'Active'
        }
    ]
    
    audit_plans = [
        {
            'id': 'AP-2024-001',
            'name': '2024 Annual Audit Plan',
            'year': 2024,
            'status': 'Approved',
            'total_audits': 12,
            'completed_audits': 3,
            'in_progress_audits': 1,
            'planned_audits': 8,
            'budget': 250000,
            'spent': 75000,
            'owner': 'Chief Audit Executive'
        },
        {
            'id': 'AP-2024-002',
            'name': 'Q2 2024 Audit Plan',
            'year': 2024,
            'status': 'In Progress',
            'total_audits': 4,
            'completed_audits': 1,
            'in_progress_audits': 2,
            'planned_audits': 1,
            'budget': 80000,
            'spent': 45000,
            'owner': 'Audit Manager'
        },
        {
            'id': 'AP-2024-003',
            'name': 'Compliance Audit Plan',
            'year': 2024,
            'status': 'Draft',
            'total_audits': 6,
            'completed_audits': 2,
            'in_progress_audits': 0,
            'planned_audits': 4,
            'budget': 120000,
            'spent': 40000,
            'owner': 'Compliance Director'
        }
    ]
    
    evidence = [
        {
            'id': 'EVD-2024-001',
            'audit_id': 'AUD-2024-001',
            'finding_id': 'FND-2024-001',
            'type': 'Documentation',
            'name': 'Access Review Policy',
            'description': 'Updated access review policy with quarterly review requirements',
            'upload_date': datetime.datetime.now() - timedelta(days=5),
            'uploaded_by': 'IT Security Team',
            'status': 'Approved',
            'file_size': '2.5 MB'
        },
        {
            'id': 'EVD-2024-002',
            'audit_id': 'AUD-2024-001',
            'finding_id': 'FND-2024-002',
            'type': 'Report',
            'name': 'Vendor Risk Assessment Report',
            'description': 'Completed vendor risk assessment for Vendor A',
            'upload_date': datetime.datetime.now() - timedelta(days=3),
            'uploaded_by': 'Procurement Team',
            'status': 'Under Review',
            'file_size': '1.8 MB'
        },
        {
            'id': 'EVD-2024-003',
            'audit_id': 'AUD-2024-002',
            'finding_id': 'FND-2024-004',
            'type': 'Screenshot',
            'name': 'Patch Deployment Log',
            'description': 'Screenshot showing successful patch deployment',
            'upload_date': datetime.datetime.now() - timedelta(days=1),
            'uploaded_by': 'IT Operations',
            'status': 'Approved',
            'file_size': '0.5 MB'
        }
    ]
    
    return audits, findings, auditors, audit_plans, evidence

def main():
    st.markdown('<h1 class="main-header">Audit Management System</h1>', unsafe_allow_html=True)
    st.markdown("Comprehensive audit planning, execution, and findings management platform")
    
    # Initialize sample data
    if not st.session_state.audits:
        audits, findings, auditors, audit_plans, evidence = generate_sample_data()
        st.session_state.audits = audits
        st.session_state.findings = findings
        st.session_state.auditors = auditors
        st.session_state.audit_plans = audit_plans
        st.session_state.evidence = evidence
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Dashboard", "Audits", "Findings", "Auditors", "Audit Plans", "Evidence", "Reports", "Analytics"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Audits":
        show_audits()
    elif page == "Findings":
        show_findings()
    elif page == "Auditors":
        show_auditors()
    elif page == "Audit Plans":
        show_audit_plans()
    elif page == "Evidence":
        show_evidence()
    elif page == "Reports":
        show_reports()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    st.header("📊 Audit Management Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_audits = len(st.session_state.audits)
        completed_audits = len([a for a in st.session_state.audits if a['status'] == 'Completed'])
        st.metric(
            label="Total Audits",
            value=total_audits,
            delta=f"{completed_audits} completed"
        )
    
    with col2:
        total_findings = len(st.session_state.findings)
        open_findings = len([f for f in st.session_state.findings if f['status'] == 'Open'])
        st.metric(
            label="Total Findings",
            value=total_findings,
            delta=f"{open_findings} open"
        )
    
    with col3:
        critical_findings = len([f for f in st.session_state.findings if f['severity'] == 'Critical'])
        high_findings = len([f for f in st.session_state.findings if f['severity'] == 'High'])
        st.metric(
            label="Critical/High Findings",
            value=critical_findings + high_findings,
            delta=f"{critical_findings} critical"
        )
    
    with col4:
        avg_completion_time = np.mean([30, 45, 60, 90])  # Sample completion times
        st.metric(
            label="Avg Completion (days)",
            value=f"{avg_completion_time:.0f}",
            delta="-5 days"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Audit Status Distribution")
        status_counts = pd.DataFrame(st.session_state.audits)['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Audit Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Findings by Severity")
        severity_counts = pd.DataFrame(st.session_state.findings)['severity'].value_counts()
        fig = px.bar(x=severity_counts.index, y=severity_counts.values, 
                    title="Findings by Severity",
                    color=severity_counts.index,
                    color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Recent Audits**")
        recent_audits = sorted(st.session_state.audits, 
                             key=lambda x: x['start_date'], reverse=True)[:5]
        for audit in recent_audits:
            st.write(f"• {audit['name']} - {audit['status']} ({audit['start_date'].strftime('%Y-%m-%d')})")
    
    with col2:
        st.write("**Recent Findings**")
        recent_findings = sorted(st.session_state.findings, 
                               key=lambda x: x.get('due_date', datetime.datetime.now()), reverse=True)[:5]
        for finding in recent_findings:
            st.write(f"• {finding['title']} - {finding['severity']} ({finding['status']})")

def show_audits():
    st.header("🔍 Audits")
    
    # Add new audit
    with st.expander("Add New Audit"):
        with st.form("new_audit"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Audit Name")
                audit_type = st.selectbox("Audit Type", ["Internal", "External", "Third Party"])
                framework = st.selectbox("Framework", ["SOC 2", "ISO 27001", "PCI DSS", "GDPR", "HITRUST CSF", "NIST CSF", "Other"])
                scope = st.text_area("Scope")
            
            with col2:
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                auditor = st.text_input("Auditor")
                lead_auditor = st.text_input("Lead Auditor")
            
            if st.form_submit_button("Add Audit"):
                new_audit = {
                    'id': f'AUD-{datetime.datetime.now().year}-{len(st.session_state.audits)+1:03d}',
                    'name': name,
                    'type': audit_type,
                    'framework': framework,
                    'scope': scope,
                    'start_date': datetime.datetime.combine(start_date, datetime.time()),
                    'end_date': datetime.datetime.combine(end_date, datetime.time()),
                    'status': 'Planned',
                    'auditor': auditor,
                    'lead_auditor': lead_auditor,
                    'rating': 'Not Started',
                    'findings_count': 0,
                    'critical_findings': 0,
                    'high_findings': 0,
                    'medium_findings': 0,
                    'low_findings': 0
                }
                st.session_state.audits.append(new_audit)
                st.success("Audit added successfully!")
    
    # Display audits
    df = pd.DataFrame(st.session_state.audits)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['type'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        framework_filter = st.selectbox("Filter by Framework", ["All"] + list(df['framework'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['type'] == type_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if framework_filter != "All":
        filtered_df = filtered_df[filtered_df['framework'] == framework_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Audit details
    if st.checkbox("Show Audit Details"):
        selected_audit = st.selectbox("Select Audit", df['name'].tolist())
        audit = next((a for a in st.session_state.audits if a['name'] == selected_audit), None)
        
        if audit:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Audit ID:** {audit['id']}")
                st.write(f"**Type:** {audit['type']}")
                st.write(f"**Framework:** {audit['framework']}")
                st.write(f"**Status:** {audit['status']}")
                st.write(f"**Rating:** {audit['rating']}")
            
            with col2:
                st.write(f"**Auditor:** {audit['auditor']}")
                st.write(f"**Lead Auditor:** {audit['lead_auditor']}")
                st.write(f"**Start Date:** {audit['start_date'].strftime('%Y-%m-%d')}")
                st.write(f"**End Date:** {audit['end_date'].strftime('%Y-%m-%d')}")
                st.write(f"**Findings:** {audit['findings_count']} total")
            
            st.write("**Scope:**")
            st.write(audit['scope'])

def show_findings():
    st.header("⚠️ Findings")
    
    # Add new finding
    with st.expander("Add New Finding"):
        with st.form("new_finding"):
            col1, col2 = st.columns(2)
            with col1:
                audit_id = st.selectbox("Audit", [a['id'] for a in st.session_state.audits])
                title = st.text_input("Finding Title")
                severity = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"])
                category = st.selectbox("Category", ["Access Control", "Vendor Management", "Training", "System Security", "Incident Response", "Data Protection", "Network Security", "Physical Security"])
            
            with col2:
                control_id = st.text_input("Control ID")
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
                assigned_to = st.text_input("Assigned To")
                due_date = st.date_input("Due Date")
            
            description = st.text_area("Description")
            remediation_plan = st.text_area("Remediation Plan")
            evidence_required = st.text_area("Evidence Required")
            
            if st.form_submit_button("Add Finding"):
                new_finding = {
                    'id': f'FND-{datetime.datetime.now().year}-{len(st.session_state.findings)+1:03d}',
                    'audit_id': audit_id,
                    'title': title,
                    'description': description,
                    'severity': severity,
                    'category': category,
                    'control_id': control_id,
                    'status': status,
                    'assigned_to': assigned_to,
                    'due_date': datetime.datetime.combine(due_date, datetime.time()),
                    'remediation_plan': remediation_plan,
                    'evidence_required': evidence_required
                }
                st.session_state.findings.append(new_finding)
                st.success("Finding added successfully!")
    
    # Display findings
    df = pd.DataFrame(st.session_state.findings)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.selectbox("Filter by Severity", ["All"] + list(df['severity'].unique()))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(df['category'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if severity_filter != "All":
        filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Finding details
    if st.checkbox("Show Finding Details"):
        selected_finding = st.selectbox("Select Finding", df['title'].tolist())
        finding = next((f for f in st.session_state.findings if f['title'] == selected_finding), None)
        
        if finding:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Finding ID:** {finding['id']}")
                st.write(f"**Audit ID:** {finding['audit_id']}")
                st.write(f"**Severity:** {finding['severity']}")
                st.write(f"**Category:** {finding['category']}")
                st.write(f"**Control ID:** {finding['control_id']}")
            
            with col2:
                st.write(f"**Status:** {finding['status']}")
                st.write(f"**Assigned To:** {finding['assigned_to']}")
                st.write(f"**Due Date:** {finding['due_date'].strftime('%Y-%m-%d')}")
            
            st.write("**Description:**")
            st.write(finding['description'])
            st.write("**Remediation Plan:**")
            st.write(finding['remediation_plan'])
            st.write("**Evidence Required:**")
            st.write(finding['evidence_required'])

def show_auditors():
    st.header("👥 Auditors")
    
    # Add new auditor
    with st.expander("Add New Auditor"):
        with st.form("new_auditor"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Auditor Name")
                firm = st.text_input("Firm")
                specialization = st.text_input("Specialization")
                experience_years = st.number_input("Experience (years)", min_value=0, max_value=50, value=5)
            
            with col2:
                certifications = st.text_area("Certifications (comma-separated)")
                contact = st.text_input("Contact Email")
                status = st.selectbox("Status", ["Active", "Inactive", "Retired"])
            
            if st.form_submit_button("Add Auditor"):
                new_auditor = {
                    'id': f'AUD-{len(st.session_state.auditors)+1:03d}',
                    'name': name,
                    'firm': firm,
                    'specialization': specialization,
                    'experience_years': experience_years,
                    'certifications': [c.strip() for c in certifications.split(',') if c.strip()],
                    'contact': contact,
                    'status': status
                }
                st.session_state.auditors.append(new_auditor)
                st.success("Auditor added successfully!")
    
    # Display auditors
    df = pd.DataFrame(st.session_state.auditors)
    st.dataframe(df, use_container_width=True)
    
    # Auditor overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Auditors by Firm")
        firm_counts = df['firm'].value_counts()
        fig = px.pie(values=firm_counts.values, names=firm_counts.index, 
                    title="Auditors by Firm")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Experience Distribution")
        fig = px.histogram(df, x='experience_years', nbins=10,
                          title="Auditor Experience Distribution",
                          labels={'experience_years': 'Years of Experience'})
        st.plotly_chart(fig, use_container_width=True)

def show_audit_plans():
    st.header("📋 Audit Plans")
    
    # Add new audit plan
    with st.expander("Add New Audit Plan"):
        with st.form("new_plan"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Plan Name")
                year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.datetime.now().year)
                total_audits = st.number_input("Total Audits", min_value=1, max_value=100, value=12)
                budget = st.number_input("Budget ($)", min_value=0, max_value=1000000, value=100000)
            
            with col2:
                owner = st.text_input("Plan Owner")
                status = st.selectbox("Status", ["Draft", "Under Review", "Approved", "In Progress", "Completed"])
            
            if st.form_submit_button("Add Plan"):
                new_plan = {
                    'id': f'AP-{year}-{len(st.session_state.audit_plans)+1:03d}',
                    'name': name,
                    'year': year,
                    'status': status,
                    'total_audits': total_audits,
                    'completed_audits': 0,
                    'in_progress_audits': 0,
                    'planned_audits': total_audits,
                    'budget': budget,
                    'spent': 0,
                    'owner': owner
                }
                st.session_state.audit_plans.append(new_plan)
                st.success("Audit plan added successfully!")
    
    # Display plans
    df = pd.DataFrame(st.session_state.audit_plans)
    st.dataframe(df, use_container_width=True)
    
    # Plan overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Plan Status Distribution")
        status_counts = df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Audit Plan Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Budget vs Spent")
        fig = px.bar(df, x='name', y=['budget', 'spent'], 
                    title="Budget vs Spent by Plan",
                    barmode='group')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_evidence():
    st.header("📄 Evidence")
    
    # Add new evidence
    with st.expander("Add New Evidence"):
        with st.form("new_evidence"):
            col1, col2 = st.columns(2)
            with col1:
                audit_id = st.selectbox("Audit", [a['id'] for a in st.session_state.audits])
                finding_id = st.selectbox("Finding", [f['id'] for f in st.session_state.findings])
                evidence_type = st.selectbox("Evidence Type", ["Documentation", "Report", "Screenshot", "Log", "Policy", "Procedure", "Training Record", "Other"])
                name = st.text_input("Evidence Name")
            
            with col2:
                uploaded_by = st.text_input("Uploaded By")
                status = st.selectbox("Status", ["Under Review", "Approved", "Rejected", "Pending"])
                file_size = st.text_input("File Size", value="1.0 MB")
            
            description = st.text_area("Description")
            
            if st.form_submit_button("Add Evidence"):
                new_evidence = {
                    'id': f'EVD-{datetime.datetime.now().year}-{len(st.session_state.evidence)+1:03d}',
                    'audit_id': audit_id,
                    'finding_id': finding_id,
                    'type': evidence_type,
                    'name': name,
                    'description': description,
                    'upload_date': datetime.datetime.now(),
                    'uploaded_by': uploaded_by,
                    'status': status,
                    'file_size': file_size
                }
                st.session_state.evidence.append(new_evidence)
                st.success("Evidence added successfully!")
    
    # Display evidence
    df = pd.DataFrame(st.session_state.evidence)
    st.dataframe(df, use_container_width=True)
    
    # Evidence overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evidence by Type")
        type_counts = df['type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, 
                    title="Evidence by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Evidence Status")
        status_counts = df['status'].value_counts()
        fig = px.bar(x=status_counts.index, y=status_counts.values, 
                    title="Evidence Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("📊 Reports & Analytics")
    
    # Report options
    report_type = st.selectbox("Select Report Type", [
        "Audit Summary Report",
        "Findings Report",
        "Compliance Report",
        "Auditor Performance Report",
        "Budget Report"
    ])
    
    if report_type == "Audit Summary Report":
        st.subheader("Audit Summary Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Executive Summary**")
            st.write(f"• Total Audits: {len(st.session_state.audits)}")
            st.write(f"• Completed Audits: {len([a for a in st.session_state.audits if a['status'] == 'Completed'])}")
            st.write(f"• In Progress Audits: {len([a for a in st.session_state.audits if a['status'] == 'In Progress'])}")
            st.write(f"• Planned Audits: {len([a for a in st.session_state.audits if a['status'] == 'Planned'])}")
        
        with col2:
            st.write("**Key Metrics**")
            st.write(f"• Total Findings: {len(st.session_state.findings)}")
            st.write(f"• Critical Findings: {len([f for f in st.session_state.findings if f['severity'] == 'Critical'])}")
            st.write(f"• High Findings: {len([f for f in st.session_state.findings if f['severity'] == 'High'])}")
            st.write(f"• Open Findings: {len([f for f in st.session_state.findings if f['status'] == 'Open'])}")
    
    elif report_type == "Findings Report":
        st.subheader("Findings Report")
        
        df_findings = pd.DataFrame(st.session_state.findings)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Findings Statistics**")
            st.write(f"• Total Findings: {len(df_findings)}")
            st.write(f"• Open Findings: {len(df_findings[df_findings['status'] == 'Open'])}")
            st.write(f"• In Progress: {len(df_findings[df_findings['status'] == 'In Progress'])}")
            st.write(f"• Resolved: {len(df_findings[df_findings['status'] == 'Resolved'])}")
        
        with col2:
            st.write("**Severity Breakdown**")
            severity_counts = df_findings['severity'].value_counts()
            for severity, count in severity_counts.items():
                st.write(f"• {severity}: {count}")
    
    # Export functionality
    st.subheader("Export Data")
    export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
    
    if st.button("Export Data"):
        if export_format == "CSV":
            # Export to CSV
            df_audits = pd.DataFrame(st.session_state.audits)
            csv = df_audits.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="audits.csv",
                mime="text/csv"
            )
        elif export_format == "JSON":
            # Export to JSON
            json_data = json.dumps(st.session_state.audits, default=str, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="audits.json",
                mime="application/json"
            )

def show_analytics():
    st.header("📈 Analytics & Insights")
    
    # Calculate metrics
    total_audits = len(st.session_state.audits)
    completed_audits = len([a for a in st.session_state.audits if a['status'] == 'Completed'])
    completion_rate = (completed_audits / total_audits * 100) if total_audits > 0 else 0
    
    total_findings = len(st.session_state.findings)
    open_findings = len([f for f in st.session_state.findings if f['status'] == 'Open'])
    resolution_rate = ((total_findings - open_findings) / total_findings * 100) if total_findings > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Audit Completion Rate", f"{completion_rate:.1f}%")
        st.metric("Total Audits", total_audits)
    
    with col2:
        st.metric("Findings Resolution Rate", f"{resolution_rate:.1f}%")
        st.metric("Total Findings", total_findings)
    
    with col3:
        st.metric("Critical Findings", len([f for f in st.session_state.findings if f['severity'] == 'Critical']))
        st.metric("High Findings", len([f for f in st.session_state.findings if f['severity'] == 'High']))
    
    with col4:
        st.metric("Active Auditors", len([a for a in st.session_state.auditors if a['status'] == 'Active']))
        st.metric("Evidence Items", len(st.session_state.evidence))
    
    # Trend analysis
    st.subheader("Audit Trends")
    df_audits = pd.DataFrame(st.session_state.audits)
    df_audits['start_date'] = pd.to_datetime(df_audits['start_date'])
    df_audits['month'] = df_audits['start_date'].dt.to_period('M')
    
    monthly_audits = df_audits.groupby('month').size().reset_index(name='count')
    monthly_audits['month'] = monthly_audits['month'].astype(str)
    
    fig = px.line(monthly_audits, x='month', y='count', 
                  title="Monthly Audit Volume",
                  labels={'count': 'Number of Audits', 'month': 'Month'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Framework analysis
    st.subheader("Audits by Framework")
    framework_counts = df_audits['framework'].value_counts()
    fig = px.bar(x=framework_counts.index, y=framework_counts.values, 
                title="Audits by Framework")
    st.plotly_chart(fig, use_container_width=True)
    
    # Findings analysis
    st.subheader("Findings by Category")
    df_findings = pd.DataFrame(st.session_state.findings)
    category_counts = df_findings['category'].value_counts()
    fig = px.pie(values=category_counts.values, names=category_counts.index, 
                title="Findings by Category")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
