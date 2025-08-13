import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Control Gap Analysis",
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

    /* Gap severity styling */
    .gap-critical { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .gap-high { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
    .gap-medium { background-color: rgba(255, 193, 7, 0.1); border-left: 4px solid #ffc107; }
    .gap-low { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

# Sample framework data
@st.cache_data
def load_framework_data():
    """Load sample framework and control data"""
    frameworks = [
        {"id": "ISO27001", "name": "ISO 27001", "version": "2022", "type": "Information Security"},
        {"id": "SOC2", "name": "SOC 2", "version": "2017", "type": "Trust Services"},
        {"id": "NIST", "name": "NIST CSF", "version": "2.0", "type": "Cybersecurity"},
        {"id": "PCI", "name": "PCI DSS", "version": "4.0", "type": "Payment Security"},
        {"id": "HIPAA", "name": "HIPAA", "version": "1996", "type": "Healthcare"}
    ]
    
    controls = [
        # ISO 27001 Controls
        {"id": "ISO-A.5.1", "name": "Information Security Policy", "framework": "ISO27001", "domain": "Policies", "category": "Governance"},
        {"id": "ISO-A.6.1", "name": "Information Security Roles", "framework": "ISO27001", "domain": "Organization", "category": "Governance"},
        {"id": "ISO-A.7.1", "name": "Screening", "framework": "ISO27001", "domain": "Human Resources", "category": "People"},
        {"id": "ISO-A.8.1", "name": "Inventory of Assets", "framework": "ISO27001", "domain": "Asset Management", "category": "Assets"},
        {"id": "ISO-A.9.1", "name": "Access Control Policy", "framework": "ISO27001", "domain": "Access Control", "category": "Access"},
        {"id": "ISO-A.10.1", "name": "Cryptographic Controls Policy", "framework": "ISO27001", "domain": "Cryptography", "category": "Protection"},
        {"id": "ISO-A.11.1", "name": "Physical Security Perimeters", "framework": "ISO27001", "domain": "Physical Security", "category": "Physical"},
        {"id": "ISO-A.12.1", "name": "Operational Procedures", "framework": "ISO27001", "domain": "Operations", "category": "Operations"},
        {"id": "ISO-A.13.1", "name": "Network Security Management", "framework": "ISO27001", "domain": "Communications", "category": "Network"},
        {"id": "ISO-A.14.1", "name": "Security Requirements", "framework": "ISO27001", "domain": "System Development", "category": "Development"},
        
        # SOC 2 Controls
        {"id": "SOC-CC1", "name": "Control Environment", "framework": "SOC2", "domain": "Control Environment", "category": "Governance"},
        {"id": "SOC-CC2", "name": "Communication and Information", "framework": "SOC2", "domain": "Communication", "category": "Governance"},
        {"id": "SOC-CC3", "name": "Risk Assessment", "framework": "SOC2", "domain": "Risk Assessment", "category": "Risk"},
        {"id": "SOC-CC4", "name": "Monitoring Activities", "framework": "SOC2", "domain": "Monitoring", "category": "Monitoring"},
        {"id": "SOC-CC5", "name": "Control Activities", "framework": "SOC2", "domain": "Control Activities", "category": "Controls"},
        {"id": "SOC-CC6", "name": "Logical and Physical Access", "framework": "SOC2", "domain": "Access Control", "category": "Access"},
        {"id": "SOC-CC7", "name": "System Operations", "framework": "SOC2", "domain": "Operations", "category": "Operations"},
        {"id": "SOC-CC8", "name": "Change Management", "framework": "SOC2", "domain": "Change Management", "category": "Change"},
        {"id": "SOC-CC9", "name": "Risk Mitigation", "framework": "SOC2", "domain": "Risk Mitigation", "category": "Risk"},
        
        # NIST CSF Controls
        {"id": "NIST-ID.AM-1", "name": "Asset Inventory", "framework": "NIST", "domain": "Identify", "category": "Asset Management"},
        {"id": "NIST-ID.AM-2", "name": "Software Platforms", "framework": "NIST", "domain": "Identify", "category": "Asset Management"},
        {"id": "NIST-ID.AM-3", "name": "Organizational Communication", "framework": "NIST", "domain": "Identify", "category": "Business Environment"},
        {"id": "NIST-PR.AC-1", "name": "Identity Management", "framework": "NIST", "domain": "Protect", "category": "Access Control"},
        {"id": "NIST-PR.AC-2", "name": "Physical Access Control", "framework": "NIST", "domain": "Protect", "category": "Access Control"},
        {"id": "NIST-PR.AC-3", "name": "Remote Access", "framework": "NIST", "domain": "Protect", "category": "Access Control"},
        {"id": "NIST-DE.AE-1", "name": "Baseline Network Operations", "framework": "NIST", "domain": "Detect", "category": "Anomalies"},
        {"id": "NIST-RS.RP-1", "name": "Response Plan Execution", "framework": "NIST", "domain": "Respond", "category": "Response Planning"},
        {"id": "NIST-RC.RP-1", "name": "Recovery Plan Execution", "framework": "NIST", "domain": "Recover", "category": "Recovery Planning"}
    ]
    
    return pd.DataFrame(frameworks), pd.DataFrame(controls)

# Sample gap data
@st.cache_data
def load_gap_data():
    """Load sample gap analysis data"""
    gaps = [
        # Critical Gaps
        {"id": "GAP-001", "control_id": "ISO-A.8.1", "control_name": "Inventory of Assets", "framework": "ISO27001", 
         "gap_type": "Missing", "severity": "Critical", "risk_score": 95, "status": "Open",
         "description": "No comprehensive asset inventory exists for IT infrastructure", 
         "business_impact": "Unable to track and protect critical assets", "current_state": "No inventory process",
         "target_state": "Automated asset discovery and tracking", "remediation_priority": "Immediate",
         "estimated_cost": 50000, "estimated_effort": "3 months", "owner": "IT Operations", "created_date": "2024-01-15"},
        
        {"id": "GAP-002", "control_id": "SOC-CC6", "control_name": "Logical and Physical Access", "framework": "SOC2", 
         "gap_type": "Incomplete", "severity": "Critical", "risk_score": 90, "status": "In Progress",
         "description": "MFA not implemented for all privileged accounts", 
         "business_impact": "High risk of unauthorized access to critical systems", "current_state": "MFA on 60% of accounts",
         "target_state": "MFA on 100% of privileged accounts", "remediation_priority": "Immediate",
         "estimated_cost": 25000, "estimated_effort": "2 months", "owner": "Security Team", "created_date": "2024-01-20"},
        
        # High Gaps
        {"id": "GAP-003", "control_id": "ISO-A.9.1", "control_name": "Access Control Policy", "framework": "ISO27001", 
         "gap_type": "Ineffective", "severity": "High", "risk_score": 75, "status": "Open",
         "description": "Access control policy not consistently enforced across systems", 
         "business_impact": "Inconsistent access controls increase security risk", "current_state": "Policy exists but not enforced",
         "target_state": "Automated policy enforcement", "remediation_priority": "High",
         "estimated_cost": 35000, "estimated_effort": "4 months", "owner": "Security Team", "created_date": "2024-02-01"},
        
        {"id": "GAP-004", "control_id": "NIST-PR.AC-1", "control_name": "Identity Management", "framework": "NIST", 
         "gap_type": "Missing", "severity": "High", "risk_score": 80, "status": "Open",
         "description": "No centralized identity management system", 
         "business_impact": "Manual user provisioning and deprovisioning", "current_state": "Manual processes",
         "target_state": "Automated identity lifecycle management", "remediation_priority": "High",
         "estimated_cost": 75000, "estimated_effort": "6 months", "owner": "IT Operations", "created_date": "2024-02-10"},
        
        {"id": "GAP-005", "control_id": "SOC-CC8", "control_name": "Change Management", "framework": "SOC2", 
         "gap_type": "Incomplete", "severity": "High", "risk_score": 70, "status": "In Progress",
         "description": "Emergency changes bypass formal change management process", 
         "business_impact": "Uncontrolled changes increase system instability", "current_state": "Emergency procedures exist but not followed",
         "target_state": "Streamlined emergency change process", "remediation_priority": "High",
         "estimated_cost": 15000, "estimated_effort": "2 months", "owner": "Change Management", "created_date": "2024-02-15"},
        
        # Medium Gaps
        {"id": "GAP-006", "control_id": "ISO-A.12.1", "control_name": "Operational Procedures", "framework": "ISO27001", 
         "gap_type": "Incomplete", "severity": "Medium", "risk_score": 55, "status": "Open",
         "description": "Documentation for critical operational procedures is outdated", 
         "business_impact": "Inconsistent operational practices", "current_state": "Outdated documentation",
         "target_state": "Current, accessible procedures", "remediation_priority": "Medium",
         "estimated_cost": 10000, "estimated_effort": "3 months", "owner": "IT Operations", "created_date": "2024-02-20"},
        
        {"id": "GAP-007", "control_id": "NIST-DE.AE-1", "control_name": "Baseline Network Operations", "framework": "NIST", 
         "gap_type": "Missing", "severity": "Medium", "risk_score": 60, "status": "Open",
         "description": "No baseline established for network traffic patterns", 
         "business_impact": "Unable to detect anomalous network activity", "current_state": "No baseline monitoring",
         "target_state": "Automated baseline monitoring", "remediation_priority": "Medium",
         "estimated_cost": 20000, "estimated_effort": "4 months", "owner": "Network Team", "created_date": "2024-03-01"},
        
        {"id": "GAP-008", "control_id": "SOC-CC4", "control_name": "Monitoring Activities", "framework": "SOC2", 
         "gap_type": "Ineffective", "severity": "Medium", "risk_score": 50, "status": "Remediated",
         "description": "Security monitoring alerts not properly configured", 
         "business_impact": "Delayed incident detection and response", "current_state": "Basic monitoring in place",
         "target_state": "Optimized alert configuration", "remediation_priority": "Medium",
         "estimated_cost": 12000, "estimated_effort": "2 months", "owner": "Security Team", "created_date": "2024-01-10"},
        
        # Low Gaps
        {"id": "GAP-009", "control_id": "ISO-A.5.1", "control_name": "Information Security Policy", "framework": "ISO27001", 
         "gap_type": "Incomplete", "severity": "Low", "risk_score": 30, "status": "Open",
         "description": "Policy review schedule not documented", 
         "business_impact": "Policies may become outdated", "current_state": "No review schedule",
         "target_state": "Annual policy review process", "remediation_priority": "Low",
         "estimated_cost": 5000, "estimated_effort": "1 month", "owner": "Compliance Team", "created_date": "2024-03-05"},
        
        {"id": "GAP-010", "control_id": "NIST-RC.RP-1", "control_name": "Recovery Plan Execution", "framework": "NIST", 
         "gap_type": "Missing", "severity": "Low", "risk_score": 25, "status": "Open",
         "description": "No disaster recovery testing schedule", 
         "business_impact": "Recovery procedures not validated", "current_state": "No testing program",
         "target_state": "Quarterly DR testing", "remediation_priority": "Low",
         "estimated_cost": 8000, "estimated_effort": "2 months", "owner": "Business Continuity", "created_date": "2024-03-10"}
    ]
    
    df = pd.DataFrame(gaps)
    df['created_date'] = pd.to_datetime(df['created_date'])
    return df

def calculate_gap_metrics(df):
    """Calculate key gap analysis metrics"""
    total_gaps = len(df)
    open_gaps = len(df[df['status'] == 'Open'])
    in_progress_gaps = len(df[df['status'] == 'In Progress'])
    remediated_gaps = len(df[df['status'] == 'Remediated'])
    
    critical_gaps = len(df[df['severity'] == 'Critical'])
    high_gaps = len(df[df['severity'] == 'High'])
    medium_gaps = len(df[df['severity'] == 'Medium'])
    low_gaps = len(df[df['severity'] == 'Low'])
    
    avg_risk_score = df['risk_score'].mean()
    total_cost = df['estimated_cost'].sum()
    
    remediation_rate = (remediated_gaps / total_gaps * 100) if total_gaps > 0 else 0
    
    return {
        'total_gaps': total_gaps,
        'open_gaps': open_gaps,
        'in_progress_gaps': in_progress_gaps,
        'remediated_gaps': remediated_gaps,
        'critical_gaps': critical_gaps,
        'high_gaps': high_gaps,
        'medium_gaps': medium_gaps,
        'low_gaps': low_gaps,
        'avg_risk_score': avg_risk_score,
        'total_cost': total_cost,
        'remediation_rate': remediation_rate
    }

def generate_remediation_plan(df):
    """Generate prioritized remediation plan"""
    # Filter open and in-progress gaps
    active_gaps = df[df['status'].isin(['Open', 'In Progress'])].copy()
    
    # Calculate priority score based on severity, risk score, and business impact
    severity_scores = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
    active_gaps['priority_score'] = active_gaps['severity'].map(severity_scores) * active_gaps['risk_score'] / 25
    
    # Sort by priority score
    active_gaps = active_gaps.sort_values('priority_score', ascending=False)
    
    return active_gaps

def main():
    st.markdown('<h1 class="main-header">Control Gap Analysis</h1>', unsafe_allow_html=True)
    
    # Load data
    frameworks_df, controls_df = load_framework_data()
    gaps_df = load_gap_data()
    metrics = calculate_gap_metrics(gaps_df)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Framework filter
    framework_filter = st.sidebar.multiselect(
        "Framework",
        options=gaps_df['framework'].unique(),
        default=gaps_df['framework'].unique()
    )
    
    # Status filter
    status_filter = st.sidebar.multiselect(
        "Status",
        options=gaps_df['status'].unique(),
        default=gaps_df['status'].unique()
    )
    
    # Severity filter
    severity_filter = st.sidebar.multiselect(
        "Severity",
        options=gaps_df['severity'].unique(),
        default=gaps_df['severity'].unique()
    )
    
    # Gap type filter
    gap_type_filter = st.sidebar.multiselect(
        "Gap Type",
        options=gaps_df['gap_type'].unique(),
        default=gaps_df['gap_type'].unique()
    )
    
    # Apply filters
    filtered_df = gaps_df[
        (gaps_df['framework'].isin(framework_filter)) &
        (gaps_df['status'].isin(status_filter)) &
        (gaps_df['severity'].isin(severity_filter)) &
        (gaps_df['gap_type'].isin(gap_type_filter))
    ]
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Gaps", metrics['total_gaps'])
        st.metric("Critical Gaps", metrics['critical_gaps'], delta=f"{metrics['critical_gaps'] - 0}")
    
    with col2:
        st.metric("Open Gaps", metrics['open_gaps'])
        st.metric("In Progress", metrics['in_progress_gaps'])
    
    with col3:
        st.metric("Remediated", metrics['remediated_gaps'])
        st.metric("Remediation Rate", f"{metrics['remediation_rate']:.1f}%")
    
    with col4:
        st.metric("Avg Risk Score", f"{metrics['avg_risk_score']:.1f}")
        st.metric("Total Cost", f"${metrics['total_cost']:,.0f}")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Gap Register", "📊 Analytics", "🎯 Remediation Plan", "🔗 Framework Mapping", "⚙️ Gap Management"])
    
    with tab1:
        st.header("📋 Gap Register")
        
        # Gap register table
        st.dataframe(
            filtered_df[['id', 'control_name', 'framework', 'gap_type', 'severity', 'risk_score', 'status', 'owner', 'created_date']],
            use_container_width=True,
            hide_index=True
        )
        
        # Gap details expander
        with st.expander("🔍 Gap Details"):
            selected_gap = st.selectbox("Select Gap", filtered_df['id'].tolist())
            gap_data = filtered_df[filtered_df['id'] == selected_gap].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Control:** {gap_data['control_name']}")
                st.write(f"**Framework:** {gap_data['framework']}")
                st.write(f"**Gap Type:** {gap_data['gap_type']}")
                st.write(f"**Owner:** {gap_data['owner']}")
            
            with col2:
                st.write(f"**Severity:** {gap_data['severity']}")
                st.write(f"**Risk Score:** {gap_data['risk_score']}/100")
                st.write(f"**Status:** {gap_data['status']}")
                st.write(f"**Created:** {gap_data['created_date'].strftime('%Y-%m-%d')}")
            
            st.write(f"**Description:** {gap_data['description']}")
            st.write(f"**Business Impact:** {gap_data['business_impact']}")
            st.write(f"**Current State:** {gap_data['current_state']}")
            st.write(f"**Target State:** {gap_data['target_state']}")
            st.write(f"**Estimated Cost:** ${gap_data['estimated_cost']:,.0f}")
            st.write(f"**Estimated Effort:** {gap_data['estimated_effort']}")
    
    with tab2:
        st.header("📊 Gap Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gap distribution by severity
            severity_counts = filtered_df['severity'].value_counts()
            fig_severity = px.pie(
                values=severity_counts.values,
                names=severity_counts.index,
                title="Gaps by Severity"
            )
            st.plotly_chart(fig_severity, use_container_width=True)
            
            # Gap by framework
            framework_counts = filtered_df['framework'].value_counts()
            fig_framework = px.bar(
                x=framework_counts.index,
                y=framework_counts.values,
                title="Gaps by Framework",
                labels={'x': 'Framework', 'y': 'Number of Gaps'}
            )
            st.plotly_chart(fig_framework, use_container_width=True)
        
        with col2:
            # Gap by status
            status_counts = filtered_df['status'].value_counts()
            fig_status = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Gaps by Status",
                labels={'x': 'Status', 'y': 'Number of Gaps'}
            )
            st.plotly_chart(fig_status, use_container_width=True)
            
            # Risk score distribution
            fig_risk = px.histogram(
                filtered_df,
                x='risk_score',
                nbins=10,
                title="Risk Score Distribution",
                labels={'risk_score': 'Risk Score', 'count': 'Number of Gaps'}
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        
        # Trend analysis
        st.subheader("📈 Gap Trends")
        
        # Simulate trend data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        trend_data = []
        
        for date in dates:
            # Simulate monthly gap counts with some trend
            base_count = 10
            trend_factor = 1 + (date.month - 1) * 0.02  # Slight upward trend
            noise = np.random.normal(0, 1)
            gap_count = max(0, int(base_count * trend_factor + noise))
            
            trend_data.append({
                'date': date,
                'total_gaps': gap_count,
                'open_gaps': int(gap_count * 0.6),
                'remediated_gaps': int(gap_count * 0.2),
                'avg_risk_score': 65 + np.random.normal(0, 5)
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_trend = px.line(
                trend_df,
                x='date',
                y=['total_gaps', 'open_gaps', 'remediated_gaps'],
                title="Gap Count Trends",
                labels={'value': 'Number of Gaps', 'variable': 'Gap Type'}
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            fig_score_trend = px.line(
                trend_df,
                x='date',
                y='avg_risk_score',
                title="Average Risk Score Trend",
                labels={'avg_risk_score': 'Average Risk Score'}
            )
            st.plotly_chart(fig_score_trend, use_container_width=True)
    
    with tab3:
        st.header("🎯 Remediation Plan")
        
        # Generate remediation plan
        remediation_plan = generate_remediation_plan(filtered_df)
        
        st.subheader("Prioritized Remediation Plan")
        
        # Display prioritized gaps
        for idx, gap in remediation_plan.head(10).iterrows():
            with st.expander(f"{gap['id']}: {gap['control_name']} (Priority Score: {gap['priority_score']:.1f})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Framework:** {gap['framework']}")
                    st.write(f"**Severity:** {gap['severity']}")
                    st.write(f"**Risk Score:** {gap['risk_score']}/100")
                    st.write(f"**Owner:** {gap['owner']}")
                
                with col2:
                    st.write(f"**Gap Type:** {gap['gap_type']}")
                    st.write(f"**Status:** {gap['status']}")
                    st.write(f"**Estimated Cost:** ${gap['estimated_cost']:,.0f}")
                    st.write(f"**Estimated Effort:** {gap['estimated_effort']}")
                
                st.write(f"**Description:** {gap['description']}")
                st.write(f"**Business Impact:** {gap['business_impact']}")
                st.write(f"**Current State:** {gap['current_state']}")
                st.write(f"**Target State:** {gap['target_state']}")
        
        # Cost analysis
        st.subheader("💰 Cost Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost by severity
            cost_by_severity = filtered_df.groupby('severity')['estimated_cost'].sum().reset_index()
            fig_cost_severity = px.bar(
                cost_by_severity,
                x='severity',
                y='estimated_cost',
                title="Remediation Cost by Severity",
                labels={'estimated_cost': 'Estimated Cost ($)', 'severity': 'Severity'}
            )
            st.plotly_chart(fig_cost_severity, use_container_width=True)
        
        with col2:
            # Cost by framework
            cost_by_framework = filtered_df.groupby('framework')['estimated_cost'].sum().reset_index()
            fig_cost_framework = px.pie(
                values=cost_by_framework['estimated_cost'],
                names=cost_by_framework['framework'],
                title="Remediation Cost by Framework"
            )
            st.plotly_chart(fig_cost_framework, use_container_width=True)
        
        # Resource allocation
        st.subheader("👥 Resource Allocation")
        
        owner_workload = filtered_df.groupby('owner').agg({
            'id': 'count',
            'estimated_cost': 'sum',
            'risk_score': 'mean'
        }).reset_index()
        owner_workload.columns = ['Owner', 'Gap Count', 'Total Cost', 'Avg Risk Score']
        
        st.dataframe(owner_workload, use_container_width=True, hide_index=True)
    
    with tab4:
        st.header("🔗 Framework Mapping")
        
        # Framework comparison
        st.subheader("Framework Coverage Analysis")
        
        # Create framework coverage matrix
        framework_coverage = filtered_df.groupby(['framework', 'severity']).size().unstack(fill_value=0)
        
        fig_coverage = px.imshow(
            framework_coverage,
            title="Framework Coverage Matrix",
            labels=dict(x="Severity", y="Framework", color="Number of Gaps"),
            aspect="auto"
        )
        st.plotly_chart(fig_coverage, use_container_width=True)
        
        # Control mapping
        st.subheader("Control Mapping")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Available frameworks
            st.write("**Available Frameworks:**")
            for _, framework in frameworks_df.iterrows():
                st.write(f"- {framework['name']} ({framework['version']}) - {framework['type']}")
        
        with col2:
            # Available controls
            st.write("**Sample Controls by Framework:**")
            for framework in controls_df['framework'].unique():
                framework_controls = controls_df[controls_df['framework'] == framework]
                st.write(f"**{framework}:** {len(framework_controls)} controls")
                for _, control in framework_controls.head(3).iterrows():
                    st.write(f"  - {control['id']}: {control['name']}")
        
        # Gap type analysis by framework
        st.subheader("Gap Type Analysis by Framework")
        
        gap_type_framework = filtered_df.groupby(['framework', 'gap_type']).size().unstack(fill_value=0)
        
        fig_gap_type = px.bar(
            gap_type_framework,
            title="Gap Types by Framework",
            labels={'value': 'Number of Gaps', 'variable': 'Gap Type'}
        )
        st.plotly_chart(fig_gap_type, use_container_width=True)
    
    with tab5:
        st.header("⚙️ Gap Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Add New Gap")
            
            # Form for adding new gap
            with st.form("new_gap_form"):
                control_name = st.text_input("Control Name")
                framework = st.selectbox("Framework", frameworks_df['name'].tolist())
                gap_type = st.selectbox("Gap Type", ["Missing", "Incomplete", "Ineffective"])
                severity = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"])
                risk_score = st.slider("Risk Score", 1, 100, 50)
                description = st.text_area("Description")
                owner = st.text_input("Owner")
                
                submitted = st.form_submit_button("Add Gap")
                if submitted:
                    st.success("Gap added successfully!")
        
        with col2:
            st.subheader("📊 Gap Metrics Dashboard")
            
            # Key Performance Indicators
            st.write("**Key Performance Indicators (KPIs):**")
            
            kpi_data = {
                'Metric': ['Total Gaps', 'Critical Gaps', 'High Gaps', 'Remediation Rate', 'Avg Risk Score', 'Total Cost'],
                'Current': [str(metrics['total_gaps']), str(metrics['critical_gaps']), str(metrics['high_gaps']), 
                           f"{metrics['remediation_rate']:.1f}%", f"{metrics['avg_risk_score']:.1f}", f"${metrics['total_cost']:,.0f}"],
                'Target': ['<20', '0', '<5', '>80%', '<50', '<$200K'],
                'Status': ['❌', '❌', '❌', '❌', '❌', '❌']
            }
            
            kpi_df = pd.DataFrame(kpi_data)
            st.dataframe(kpi_df, use_container_width=True, hide_index=True)
            
            # Gap owner accountability
            st.subheader("👥 Gap Owner Accountability")
            owner_counts = filtered_df['owner'].value_counts()
            fig_owner = px.bar(
                x=owner_counts.index,
                y=owner_counts.values,
                title="Gaps by Owner",
                labels={'x': 'Owner', 'y': 'Number of Gaps'}
            )
            fig_owner.update_xaxes(tickangle=45)
            st.plotly_chart(fig_owner, use_container_width=True)

if __name__ == "__main__":
    main()
