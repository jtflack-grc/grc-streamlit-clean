import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import yaml
import json
import base64

# Page configuration
st.set_page_config(
    page_title="Risk Treatment Plan Generator",
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

    /* Treatment strategy styling */
    .treatment-mitigate { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
    .treatment-transfer { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
    .treatment-avoid { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .treatment-accept { background-color: rgba(156, 39, 176, 0.1); border-left: 4px solid #9c27b0; }
    .status-planned { background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196f3; }
    .status-progress { background-color: rgba(255, 193, 7, 0.1); border-left: 4px solid #ffc107; }
    .status-completed { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
    .status-overdue { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
</style>
""", unsafe_allow_html=True)

# Sample treatment plan data
@st.cache_data
def load_treatment_plans():
    """Load sample risk treatment plan data"""
    plans = [
        {
            "plan_id": "TP-2024-001",
            "risk_id": "R-007",
            "title": "SQL Server Audit Logging Implementation",
            "description": "Implement comprehensive audit logging for SQL Server to meet compliance requirements",
            "threat": "Unauthorized access to sensitive data",
            "vulnerability": "Lack of audit trail for database access",
            "existing_controls": ["Basic authentication", "Network segmentation"],
            "impact_rating": 5,
            "likelihood_rating": 5,
            "inherent_risk_score": 25,
            "residual_risk_score": 8,
            "treatment_strategy": "Mitigate",
            "treatment_plan": "1. Enable SQL Server audit logging\n2. Configure audit policies\n3. Implement log monitoring\n4. Set up alerting",
            "plan_owner": "DBA Team",
            "target_date": "2024-03-15",
            "status": "Completed",
            "budget": 15000,
            "effort_hours": 80,
            "priority": "Critical",
            "framework_alignment": ["ISO 27001 A.12.4.1", "SOC 2 CC7.1", "NIST CSF DE.CM-1"],
            "evidence": ["audit_log_config.pdf", "monitoring_setup.docx"],
            "created_date": "2024-01-15",
            "last_updated": "2024-03-15"
        },
        {
            "plan_id": "TP-2024-002",
            "risk_id": "R-017",
            "title": "Cloud Storage Access Control Implementation",
            "description": "Implement proper access controls for cloud storage buckets to prevent public exposure",
            "threat": "Data breach through public cloud storage",
            "vulnerability": "Unrestricted public access to storage buckets",
            "existing_controls": ["Cloud provider security", "Network monitoring"],
            "impact_rating": 4,
            "likelihood_rating": 5,
            "inherent_risk_score": 20,
            "residual_risk_score": 6,
            "treatment_strategy": "Mitigate",
            "treatment_plan": "1. Review current bucket permissions\n2. Implement least privilege access\n3. Enable bucket versioning\n4. Set up access monitoring",
            "plan_owner": "Cloud Team",
            "target_date": "2024-02-28",
            "status": "In Progress",
            "budget": 8000,
            "effort_hours": 40,
            "priority": "High",
            "framework_alignment": ["ISO 27001 A.9.1.1", "SOC 2 CC6.1", "NIST CSF PR.AC-1"],
            "evidence": ["access_review_report.pdf", "implementation_plan.docx"],
            "created_date": "2024-01-20",
            "last_updated": "2024-02-15"
        },
        {
            "plan_id": "TP-2024-003",
            "risk_id": "R-001",
            "title": "IBM i Access Review Process Implementation",
            "description": "Establish formal access review process for IBM i systems to manage *ALLOBJ authority",
            "threat": "Privilege escalation and unauthorized access",
            "vulnerability": "Excessive *ALLOBJ authority granted to test profiles",
            "existing_controls": ["IBM i security features", "Network isolation"],
            "impact_rating": 4,
            "likelihood_rating": 3,
            "inherent_risk_score": 12,
            "residual_risk_score": 4,
            "treatment_strategy": "Mitigate",
            "treatment_plan": "1. Document current access levels\n2. Define access review procedures\n3. Implement automated reviews\n4. Train administrators",
            "plan_owner": "IBM i Team",
            "target_date": "2024-03-01",
            "status": "Planned",
            "budget": 12000,
            "effort_hours": 60,
            "priority": "High",
            "framework_alignment": ["ISO 27001 A.9.2.3", "SOC 2 CC6.1", "NIST CSF PR.AC-1"],
            "evidence": ["access_inventory.xlsx", "review_procedures.docx"],
            "created_date": "2024-01-25",
            "last_updated": "2024-01-25"
        },
        {
            "plan_id": "TP-2024-004",
            "risk_id": "R-012",
            "title": "VPN Gateway Firewall Rule Review",
            "description": "Review and restrict firewall rules on VPN gateway to prevent unrestricted outbound traffic",
            "threat": "Data exfiltration and unauthorized access",
            "vulnerability": "Unrestricted outbound traffic allowed",
            "existing_controls": ["VPN authentication", "Network monitoring"],
            "impact_rating": 5,
            "likelihood_rating": 3,
            "inherent_risk_score": 15,
            "residual_risk_score": 5,
            "treatment_strategy": "Mitigate",
            "treatment_plan": "1. Audit current firewall rules\n2. Define required traffic patterns\n3. Implement restrictive rules\n4. Test connectivity",
            "plan_owner": "Network Team",
            "target_date": "2024-03-15",
            "status": "In Progress",
            "budget": 5000,
            "effort_hours": 30,
            "priority": "High",
            "framework_alignment": ["ISO 27001 A.13.1.1", "SOC 2 CC6.1", "NIST CSF PR.AC-3"],
            "evidence": ["firewall_audit.pdf", "rule_changes.docx"],
            "created_date": "2024-02-01",
            "last_updated": "2024-02-20"
        },
        {
            "plan_id": "TP-2024-005",
            "risk_id": "R-014",
            "title": "SFTP Server MFA Implementation",
            "description": "Implement multi-factor authentication for administrative access to SFTP server",
            "threat": "Unauthorized administrative access",
            "vulnerability": "Single-factor authentication for admin access",
            "existing_controls": ["SFTP encryption", "Network segmentation"],
            "impact_rating": 4,
            "likelihood_rating": 3,
            "inherent_risk_score": 12,
            "residual_risk_score": 4,
            "treatment_strategy": "Mitigate",
            "treatment_plan": "1. Evaluate MFA solutions\n2. Configure MFA integration\n3. Test authentication flow\n4. Train administrators",
            "plan_owner": "Infrastructure Team",
            "target_date": "2024-03-20",
            "status": "Planned",
            "budget": 10000,
            "effort_hours": 50,
            "priority": "Medium",
            "framework_alignment": ["ISO 27001 A.9.3.1", "SOC 2 CC6.1", "NIST CSF PR.AC-7"],
            "evidence": ["mfa_evaluation.pdf", "implementation_plan.docx"],
            "created_date": "2024-02-05",
            "last_updated": "2024-02-05"
        },
        {
            "plan_id": "TP-2024-006",
            "risk_id": "R-023",
            "title": "Legacy CRM Compliance Documentation",
            "description": "Complete compliance documentation for legacy CRM system to meet quarterly audit requirements",
            "threat": "Compliance failure and regulatory penalties",
            "vulnerability": "Incomplete compliance documentation",
            "existing_controls": ["System monitoring", "Access controls"],
            "impact_rating": 5,
            "likelihood_rating": 5,
            "inherent_risk_score": 25,
            "residual_risk_score": 8,
            "treatment_strategy": "Mitigate",
            "treatment_plan": "1. Inventory compliance requirements\n2. Document current controls\n3. Identify gaps\n4. Create remediation plan",
            "plan_owner": "Compliance Team",
            "target_date": "2024-03-30",
            "status": "In Progress",
            "budget": 20000,
            "effort_hours": 100,
            "priority": "Critical",
            "framework_alignment": ["ISO 27001 A.18.1.1", "SOC 2 CC9.1", "NIST CSF ID.AM-1"],
            "evidence": ["compliance_gap_analysis.pdf", "documentation_plan.docx"],
            "created_date": "2024-01-30",
            "last_updated": "2024-02-25"
        }
    ]
    
    df = pd.DataFrame(plans)
    df['target_date'] = pd.to_datetime(df['target_date'])
    df['created_date'] = pd.to_datetime(df['created_date'])
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    return df

def calculate_plan_metrics(df):
    """Calculate key treatment plan metrics"""
    total_plans = len(df)
    critical_plans = len(df[df['priority'] == 'Critical'])
    high_plans = len(df[df['priority'] == 'High'])
    medium_plans = len(df[df['priority'] == 'Medium'])
    
    completed_plans = len(df[df['status'] == 'Completed'])
    in_progress_plans = len(df[df['status'] == 'In Progress'])
    planned_plans = len(df[df['status'] == 'Planned'])
    
    overdue_plans = len(df[df['target_date'] < datetime.datetime.now()])
    total_budget = df['budget'].sum()
    total_effort = df['effort_hours'].sum()
    
    avg_inherent_risk = df['inherent_risk_score'].mean()
    avg_residual_risk = df['residual_risk_score'].mean()
    
    return {
        'total_plans': total_plans,
        'critical_plans': critical_plans,
        'high_plans': high_plans,
        'medium_plans': medium_plans,
        'completed_plans': completed_plans,
        'in_progress_plans': in_progress_plans,
        'planned_plans': planned_plans,
        'overdue_plans': overdue_plans,
        'total_budget': total_budget,
        'total_effort': total_effort,
        'avg_inherent_risk': avg_inherent_risk,
        'avg_residual_risk': avg_residual_risk
    }

def generate_treatment_plan_yaml(plan_data):
    """Generate YAML format treatment plan"""
    yaml_data = {
        'risk_treatment_plan': {
            'plan_id': plan_data['plan_id'],
            'risk_id': plan_data['risk_id'],
            'title': plan_data['title'],
            'description': plan_data['description'],
            'threat': plan_data['threat'],
            'vulnerability': plan_data['vulnerability'],
            'existing_controls': plan_data['existing_controls'],
            'impact_rating': plan_data['impact_rating'],
            'likelihood_rating': plan_data['likelihood_rating'],
            'inherent_risk_score': plan_data['inherent_risk_score'],
            'residual_risk_score': plan_data['residual_risk_score'],
            'treatment_strategy': plan_data['treatment_strategy'],
            'treatment_plan': plan_data['treatment_plan'],
            'plan_owner': plan_data['plan_owner'],
            'target_date': plan_data['target_date'].strftime('%Y-%m-%d'),
            'status': plan_data['status'],
            'budget': plan_data['budget'],
            'effort_hours': plan_data['effort_hours'],
            'priority': plan_data['priority'],
            'framework_alignment': plan_data['framework_alignment'],
            'evidence': plan_data['evidence']
        }
    }
    return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)

def main():
    st.markdown('<h1 class="main-header">Risk Treatment Plan Generator</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_treatment_plans()
    metrics = calculate_plan_metrics(df)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Status filter
    status_filter = st.sidebar.multiselect(
        "Plan Status",
        options=df['status'].unique(),
        default=df['status'].unique()
    )
    
    # Priority filter
    priority_filter = st.sidebar.multiselect(
        "Priority Level",
        options=df['priority'].unique(),
        default=df['priority'].unique()
    )
    
    # Treatment strategy filter
    strategy_filter = st.sidebar.multiselect(
        "Treatment Strategy",
        options=df['treatment_strategy'].unique(),
        default=df['treatment_strategy'].unique()
    )
    
    # Owner filter
    owner_filter = st.sidebar.multiselect(
        "Plan Owner",
        options=df['plan_owner'].unique(),
        default=df['plan_owner'].unique()
    )
    
    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['priority'].isin(priority_filter)) &
        (df['treatment_strategy'].isin(strategy_filter)) &
        (df['plan_owner'].isin(owner_filter))
    ]
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Plans", metrics['total_plans'])
        st.metric("Critical Plans", metrics['critical_plans'], delta=f"{metrics['critical_plans'] - 0}")
    
    with col2:
        st.metric("In Progress", metrics['in_progress_plans'])
        st.metric("Completed", metrics['completed_plans'], delta=f"{metrics['completed_plans'] - 0}")
    
    with col3:
        st.metric("Overdue Plans", metrics['overdue_plans'], delta=f"{metrics['overdue_plans'] - 0}")
        st.metric("Total Budget", f"${metrics['total_budget']:,}")
    
    with col4:
        st.metric("Total Effort", f"{metrics['total_effort']} hrs")
        st.metric("Risk Reduction", f"{metrics['avg_inherent_risk'] - metrics['avg_residual_risk']:.1f} pts")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Treatment Plans", "📊 Analytics", "🛠️ Plan Generator", "📈 Progress Tracking", "⚙️ Management"])
    
    with tab1:
        st.header("📋 Risk Treatment Plans")
        
        # Treatment plans table
        st.dataframe(
            filtered_df[['plan_id', 'risk_id', 'title', 'priority', 'status', 'plan_owner', 'target_date', 'budget']],
            use_container_width=True,
            hide_index=True
        )
        
        # Plan details expander
        with st.expander("🔍 Plan Details"):
            selected_plan = st.selectbox("Select Plan", filtered_df['plan_id'].tolist())
            plan_data = filtered_df[filtered_df['plan_id'] == selected_plan].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Risk ID:** {plan_data['risk_id']}")
                st.write(f"**Title:** {plan_data['title']}")
                st.write(f"**Owner:** {plan_data['plan_owner']}")
                st.write(f"**Priority:** {plan_data['priority']}")
                st.write(f"**Status:** {plan_data['status']}")
                st.write(f"**Target Date:** {plan_data['target_date'].strftime('%Y-%m-%d')}")
            
            with col2:
                st.write(f"**Inherent Risk:** {plan_data['inherent_risk_score']}")
                st.write(f"**Residual Risk:** {plan_data['residual_risk_score']}")
                st.write(f"**Risk Reduction:** {plan_data['inherent_risk_score'] - plan_data['residual_risk_score']} points")
                st.write(f"**Budget:** ${plan_data['budget']:,}")
                st.write(f"**Effort:** {plan_data['effort_hours']} hours")
                st.write(f"**Strategy:** {plan_data['treatment_strategy']}")
            
            st.write(f"**Description:** {plan_data['description']}")
            st.write(f"**Threat:** {plan_data['threat']}")
            st.write(f"**Vulnerability:** {plan_data['vulnerability']}")
            st.write(f"**Treatment Plan:** {plan_data['treatment_plan']}")
            
            # Framework alignment
            st.write("**Framework Alignment:**")
            for framework in plan_data['framework_alignment']:
                st.write(f"- {framework}")
            
            # Evidence
            st.write("**Evidence:**")
            for evidence in plan_data['evidence']:
                st.write(f"- {evidence}")
    
    with tab2:
        st.header("📊 Treatment Plan Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Plans by status
            status_counts = filtered_df['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Plans by Status"
            )
            st.plotly_chart(fig_status, use_container_width=True)
            
            # Plans by priority
            priority_counts = filtered_df['priority'].value_counts()
            fig_priority = px.bar(
                x=priority_counts.index,
                y=priority_counts.values,
                title="Plans by Priority",
                labels={'x': 'Priority', 'y': 'Number of Plans'}
            )
            st.plotly_chart(fig_priority, use_container_width=True)
        
        with col2:
            # Plans by treatment strategy
            strategy_counts = filtered_df['treatment_strategy'].value_counts()
            fig_strategy = px.pie(
                values=strategy_counts.values,
                names=strategy_counts.index,
                title="Plans by Treatment Strategy"
            )
            st.plotly_chart(fig_strategy, use_container_width=True)
            
            # Plans by owner
            owner_counts = filtered_df['plan_owner'].value_counts()
            fig_owner = px.bar(
                x=owner_counts.index,
                y=owner_counts.values,
                title="Plans by Owner",
                labels={'x': 'Owner', 'y': 'Number of Plans'}
            )
            fig_owner.update_xaxes(tickangle=45)
            st.plotly_chart(fig_owner, use_container_width=True)
        
        # Risk reduction analysis
        st.subheader("🎯 Risk Reduction Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk reduction by plan
            risk_reduction = filtered_df['inherent_risk_score'] - filtered_df['residual_risk_score']
            fig_reduction = px.bar(
                x=filtered_df['plan_id'],
                y=risk_reduction,
                title="Risk Reduction by Plan",
                labels={'x': 'Plan ID', 'y': 'Risk Reduction (Points)'}
            )
            fig_reduction.update_xaxes(tickangle=45)
            st.plotly_chart(fig_reduction, use_container_width=True)
        
        with col2:
            # Budget vs effort scatter
            fig_budget_effort = px.scatter(
                filtered_df,
                x='effort_hours',
                y='budget',
                size='inherent_risk_score',
                color='priority',
                title="Budget vs Effort Analysis",
                labels={'effort_hours': 'Effort (Hours)', 'budget': 'Budget ($)'}
            )
            st.plotly_chart(fig_budget_effort, use_container_width=True)
    
    with tab3:
        st.header("🛠️ Plan Generator")
        
        st.write("Create a new risk treatment plan with comprehensive details and automated risk scoring.")
        
        # Plan creation form
        with st.form("new_plan_form"):
            st.subheader("📝 Plan Information")
            
            col1, col2 = st.columns(2)
            with col1:
                plan_id = st.text_input("Plan ID", value="TP-2024-XXX", help="Unique identifier for the treatment plan")
                risk_id = st.text_input("Risk ID", value="R-XXX", help="Associated risk identifier")
                title = st.text_input("Plan Title", placeholder="e.g., SQL Server Audit Logging Implementation")
                plan_owner = st.text_input("Plan Owner", placeholder="e.g., DBA Team")
            
            with col2:
                priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
                treatment_strategy = st.selectbox("Treatment Strategy", ["Mitigate", "Transfer", "Avoid", "Accept"])
                target_date = st.date_input("Target Date", value=datetime.date.today() + timedelta(days=30))
                budget = st.number_input("Budget ($)", min_value=0, value=10000, step=1000)
            
            description = st.text_area("Description", placeholder="Detailed description of the risk and treatment plan...")
            threat = st.text_input("Threat", placeholder="e.g., Unauthorized access to sensitive data")
            vulnerability = st.text_input("Vulnerability", placeholder="e.g., Lack of audit trail for database access")
            
            st.subheader("🎯 Risk Assessment")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                impact_rating = st.selectbox("Impact Rating (1-5)", [1, 2, 3, 4, 5], format_func=lambda x: f"{x} - {'Very Low' if x==1 else 'Low' if x==2 else 'Medium' if x==3 else 'High' if x==4 else 'Very High'}")
            
            with col2:
                likelihood_rating = st.selectbox("Likelihood Rating (1-5)", [1, 2, 3, 4, 5], format_func=lambda x: f"{x} - {'Very Low' if x==1 else 'Low' if x==2 else 'Medium' if x==3 else 'High' if x==4 else 'Very High'}")
            
            with col3:
                inherent_risk_score = impact_rating * likelihood_rating
                st.metric("Inherent Risk Score", inherent_risk_score)
            
            st.subheader("🛡️ Treatment Details")
            
            treatment_plan = st.text_area("Treatment Plan", placeholder="Step-by-step treatment plan...")
            effort_hours = st.number_input("Effort (Hours)", min_value=1, value=40, step=5)
            
            # Framework alignment
            frameworks = st.multiselect(
                "Framework Alignment",
                ["ISO 27001 A.12.4.1", "SOC 2 CC7.1", "NIST CSF DE.CM-1", "ISO 27001 A.9.2.3", "SOC 2 CC6.1", "NIST CSF PR.AC-1"],
                default=["ISO 27001 A.12.4.1", "SOC 2 CC7.1"]
            )
            
            # Evidence tracking
            evidence = st.text_area("Evidence", placeholder="List of evidence files or links...")
            
            submitted = st.form_submit_button("📋 Generate Treatment Plan")
            
            if submitted:
                # Create new plan data
                new_plan = {
                    "plan_id": plan_id,
                    "risk_id": risk_id,
                    "title": title,
                    "description": description,
                    "threat": threat,
                    "vulnerability": vulnerability,
                    "existing_controls": ["Basic controls"],
                    "impact_rating": impact_rating,
                    "likelihood_rating": likelihood_rating,
                    "inherent_risk_score": inherent_risk_score,
                    "residual_risk_score": max(1, inherent_risk_score - 10),  # Estimated reduction
                    "treatment_strategy": treatment_strategy,
                    "treatment_plan": treatment_plan,
                    "plan_owner": plan_owner,
                    "target_date": target_date,
                    "status": "Planned",
                    "budget": budget,
                    "effort_hours": effort_hours,
                    "priority": priority,
                    "framework_alignment": frameworks,
                    "evidence": evidence.split('\n') if evidence else [],
                    "created_date": datetime.datetime.now(),
                    "last_updated": datetime.datetime.now()
                }
                
                # Generate YAML
                yaml_content = generate_treatment_plan_yaml(new_plan)
                
                st.success("✅ Treatment plan generated successfully!")
                
                # Display generated plan
                st.subheader("📄 Generated Treatment Plan")
                st.code(yaml_content, language='yaml')
                
                # Download option
                st.download_button(
                    label="📥 Download YAML",
                    data=yaml_content,
                    file_name=f"{plan_id}_treatment_plan.yaml",
                    mime="text/yaml"
                )
    
    with tab4:
        st.header("📈 Progress Tracking")
        
        # Progress metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            completion_rate = (metrics['completed_plans'] / metrics['total_plans']) * 100 if metrics['total_plans'] > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        with col2:
            on_time_rate = ((metrics['total_plans'] - metrics['overdue_plans']) / metrics['total_plans']) * 100 if metrics['total_plans'] > 0 else 0
            st.metric("On-Time Rate", f"{on_time_rate:.1f}%")
        
        with col3:
            budget_utilization = (metrics['total_budget'] / 100000) * 100  # Assuming 100k budget
            st.metric("Budget Utilization", f"{budget_utilization:.1f}%")
        
        # Timeline analysis
        st.subheader("📅 Timeline Analysis")
        
        # Simulate timeline data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        timeline_data = []
        
        for date in dates:
            # Simulate monthly progress
            base_completed = 2
            progress_factor = 1 + (date.month - 1) * 0.1
            completed = min(metrics['total_plans'], int(base_completed * progress_factor))
            
            timeline_data.append({
                'date': date,
                'completed_plans': completed,
                'in_progress_plans': max(0, metrics['total_plans'] - completed - 1),
                'planned_plans': max(0, 1)
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        
        fig_timeline = px.line(
            timeline_df,
            x='date',
            y=['completed_plans', 'in_progress_plans', 'planned_plans'],
            title="Treatment Plan Progress Timeline",
            labels={'value': 'Number of Plans', 'variable': 'Status'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Risk reduction over time
        st.subheader("🎯 Risk Reduction Progress")
        
        # Simulate risk reduction data
        risk_reduction_data = []
        for i, date in enumerate(dates):
            base_reduction = 50
            reduction_factor = 1 + (i * 0.05)
            total_reduction = min(200, int(base_reduction * reduction_factor))
            
            risk_reduction_data.append({
                'date': date,
                'total_risk_reduction': total_reduction,
                'cumulative_budget': total_reduction * 100  # $100 per risk point
            })
        
        risk_reduction_df = pd.DataFrame(risk_reduction_data)
        
        fig_risk_reduction = px.line(
            risk_reduction_df,
            x='date',
            y='total_risk_reduction',
            title="Cumulative Risk Reduction",
            labels={'total_risk_reduction': 'Risk Points Reduced'}
        )
        st.plotly_chart(fig_risk_reduction, use_container_width=True)
    
    with tab5:
        st.header("⚙️ Treatment Plan Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Management Dashboard")
            
            # Key performance indicators
            st.write("**Key Performance Indicators:**")
            
            kpi_data = {
                'Metric': ['Total Plans', 'Completion Rate', 'On-Time Rate', 'Budget Utilization', 'Risk Reduction', 'Overdue Plans'],
                'Current': [str(metrics['total_plans']), f"{completion_rate:.1f}%", f"{on_time_rate:.1f}%", 
                           f"{budget_utilization:.1f}%", f"{metrics['avg_inherent_risk'] - metrics['avg_residual_risk']:.1f} pts", str(metrics['overdue_plans'])],
                'Target': ['<20', '>80%', '>90%', '<100%', '>15 pts', '0'],
                'Status': ['✅', '❌', '❌', '✅', '❌', '❌']
            }
            
            kpi_df = pd.DataFrame(kpi_data)
            st.dataframe(kpi_df, use_container_width=True, hide_index=True)
            
            # Resource allocation
            st.subheader("💰 Resource Allocation")
            
            resource_data = {
                'Team': ['DBA Team', 'Cloud Team', 'Network Team', 'Security Team', 'Compliance Team'],
                'Plans': [2, 1, 1, 1, 1],
                'Budget': [15000, 8000, 5000, 10000, 20000],
                'Effort': [80, 40, 30, 50, 100]
            }
            
            resource_df = pd.DataFrame(resource_data)
            st.dataframe(resource_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("🚨 Overdue Plans")
            
            overdue_plans = filtered_df[filtered_df['target_date'] < datetime.datetime.now()]
            
            if len(overdue_plans) > 0:
                for _, plan in overdue_plans.iterrows():
                    with st.expander(f"⚠️ {plan['plan_id']}: {plan['title']}"):
                        st.write(f"**Owner:** {plan['plan_owner']}")
                        st.write(f"**Target Date:** {plan['target_date'].strftime('%Y-%m-%d')}")
                        st.write(f"**Days Overdue:** {(datetime.datetime.now() - plan['target_date']).days}")
                        st.write(f"**Priority:** {plan['priority']}")
                        st.write(f"**Status:** {plan['status']}")
            else:
                st.success("✅ No overdue plans!")
            
            st.subheader("📋 Action Items")
            
            # Action items based on plan status
            action_items = []
            
            if metrics['overdue_plans'] > 0:
                action_items.append(f"🔴 Address {metrics['overdue_plans']} overdue plans")
            
            if completion_rate < 80:
                action_items.append(f"🟡 Improve completion rate (currently {completion_rate:.1f}%)")
            
            if on_time_rate < 90:
                action_items.append(f"🟡 Improve on-time delivery (currently {on_time_rate:.1f}%)")
            
            if budget_utilization > 100:
                action_items.append(f"🔴 Review budget allocation (currently {budget_utilization:.1f}%)")
            
            for item in action_items:
                st.write(item)

if __name__ == "__main__":
    main()
