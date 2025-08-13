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
    page_title="Control Testing Management",
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

    /* Test status styling */
    .status-pass { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
    .status-fail { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .status-in-progress { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
    .status-planned { background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196f3; }
    .priority-high { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .priority-medium { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
    .priority-low { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

# Sample control testing data
@st.cache_data
def load_control_testing_data():
    """Load sample control testing data"""
    tests = [
        {
            "test_id": "CTRL-001",
            "test_name": "User Access Control Test",
            "control_tested": "CTRL-001",
            "test_type": "Access Management",
            "result": "Fail",
            "corrective_action": "Pending update",
            "evidence_status": "Available",
            "priority": "High",
            "tester": "IT Security Team",
            "test_date": "2024-01-15",
            "due_date": "2024-02-15",
            "framework_mappings": ["NIST CSF PR.AC-1", "ISO 27001 A.9.1.1", "SOC 2 CC6.1"],
            "scope": "All privileged accounts across systems",
            "methodology": "Automated access review with manual verification",
            "findings": "Inconsistent access review processes",
            "recommendations": "Implement automated access review system",
            "evidence_link": "Internal SharePoint",
            "finding_logged": False
        },
        {
            "test_id": "CTRL-002",
            "test_name": "Patch Compliance Sampling",
            "control_tested": "CTRL-002",
            "test_type": "Vulnerability Management",
            "result": "Fail",
            "corrective_action": "N/A",
            "evidence_status": "Available",
            "priority": "High",
            "tester": "Infrastructure Team",
            "test_date": "2024-01-20",
            "due_date": "2024-02-20",
            "framework_mappings": ["NIST CSF DE.CM-1", "ISO 27001 A.12.6.1", "SOC 2 CC7.1"],
            "scope": "Critical systems patch compliance",
            "methodology": "Automated scanning with manual verification",
            "findings": "Delayed patch deployment on critical systems",
            "recommendations": "Implement automated patch management",
            "evidence_link": "Internal SharePoint",
            "finding_logged": False
        },
        {
            "test_id": "CTRL-004",
            "test_name": "Change Management Review",
            "control_tested": "CTRL-004",
            "test_type": "Change Control",
            "result": "Fail",
            "corrective_action": "Pending update",
            "evidence_status": "Available",
            "priority": "Medium",
            "tester": "IT Operations",
            "test_date": "2024-01-25",
            "due_date": "2024-02-25",
            "framework_mappings": ["NIST CSF PR.IP-1", "ISO 27001 A.12.1.2", "SOC 2 CC8.1"],
            "scope": "All system changes and modifications",
            "methodology": "Documentation review and process verification",
            "findings": "Inconsistent change documentation",
            "recommendations": "Standardize change management procedures",
            "evidence_link": "Internal SharePoint",
            "finding_logged": False
        },
        {
            "test_id": "CTRL-005",
            "test_name": "Data Retention Evaluation",
            "control_tested": "CTRL-005",
            "test_type": "Data Management",
            "result": "Fail",
            "corrective_action": "Pending update",
            "evidence_status": "Available",
            "priority": "Medium",
            "tester": "Data Governance Team",
            "test_date": "2024-02-01",
            "due_date": "2024-03-01",
            "framework_mappings": ["NIST CSF PR.DS-3", "ISO 27001 A.18.1.3", "SOC 2 CC6.2"],
            "scope": "Data retention policies and procedures",
            "methodology": "Policy review and implementation verification",
            "findings": "Inconsistent data retention practices",
            "recommendations": "Implement automated data lifecycle management",
            "evidence_link": "Internal SharePoint",
            "finding_logged": True
        },
        {
            "test_id": "CTRL-006",
            "test_name": "Incident Response Tabletop",
            "control_tested": "CTRL-006",
            "test_type": "Incident Response",
            "result": "Fail",
            "corrective_action": "Pending update",
            "evidence_status": "Available",
            "priority": "High",
            "tester": "Security Operations",
            "test_date": "2024-02-05",
            "due_date": "2024-03-05",
            "framework_mappings": ["NIST CSF RS.RP-1", "ISO 27001 A.16.1.1", "SOC 2 CC7.1"],
            "scope": "Incident response procedures and team readiness",
            "methodology": "Tabletop exercise with scenario simulation",
            "findings": "Response procedures need improvement",
            "recommendations": "Enhance incident response procedures",
            "evidence_link": "Internal SharePoint",
            "finding_logged": True
        },
        {
            "test_id": "CTRL-007",
            "test_name": "System Logging Verification",
            "control_tested": "CTRL-007",
            "test_type": "System Monitoring",
            "result": "Fail",
            "corrective_action": "N/A",
            "evidence_status": "Available",
            "priority": "Medium",
            "tester": "IT Security Team",
            "test_date": "2024-02-10",
            "due_date": "2024-03-10",
            "framework_mappings": ["NIST CSF DE.AE-1", "ISO 27001 A.12.4.1", "SOC 2 CC7.1"],
            "scope": "System logging and monitoring capabilities",
            "methodology": "Log analysis and monitoring verification",
            "findings": "Incomplete logging on critical systems",
            "recommendations": "Implement comprehensive logging strategy",
            "evidence_link": "Internal SharePoint",
            "finding_logged": True
        },
        {
            "test_id": "CTRL-008",
            "test_name": "Backup and Restore Verification",
            "control_tested": "CTRL-008",
            "test_type": "Data Protection",
            "result": "Fail",
            "corrective_action": "Pending update",
            "evidence_status": "Available",
            "priority": "High",
            "tester": "Infrastructure Team",
            "test_date": "2024-02-15",
            "due_date": "2024-03-15",
            "framework_mappings": ["NIST CSF PR.DS-4", "ISO 27001 A.12.3.1", "SOC 2 CC6.2"],
            "scope": "Backup procedures and recovery capabilities",
            "methodology": "Backup testing and recovery simulation",
            "findings": "Inconsistent backup verification",
            "recommendations": "Implement automated backup verification",
            "evidence_link": "Internal SharePoint",
            "finding_logged": True
        },
        {
            "test_id": "CTRL-009",
            "test_name": "Security Awareness Review",
            "control_tested": "CTRL-009",
            "test_type": "Security Awareness",
            "result": "Pass",
            "corrective_action": "N/A",
            "evidence_status": "Available",
            "priority": "Low",
            "tester": "HR Security Team",
            "test_date": "2024-02-20",
            "due_date": "2024-03-20",
            "framework_mappings": ["NIST CSF PR.AT-1", "ISO 27001 A.7.2.2", "SOC 2 CC9.1"],
            "scope": "Security awareness training effectiveness",
            "methodology": "Training completion and knowledge assessment",
            "findings": "Training program effective",
            "recommendations": "Continue current training program",
            "evidence_link": "Internal SharePoint",
            "finding_logged": True
        }
    ]
    
    df = pd.DataFrame(tests)
    df['test_date'] = pd.to_datetime(df['test_date'])
    df['due_date'] = pd.to_datetime(df['due_date'])
    return df

def calculate_testing_metrics(df):
    """Calculate key control testing metrics"""
    today = datetime.datetime.now()
    
    metrics = {
        'total_tests': len(df),
        'passed_tests': len(df[df['result'] == 'Pass']),
        'failed_tests': len(df[df['result'] == 'Fail']),
        'in_progress_tests': len(df[df['result'] == 'In Progress']),
        'planned_tests': len(df[df['result'] == 'Planned']),
        'overdue_tests': len(df[df['due_date'] < today]),
        'high_priority_tests': len(df[df['priority'] == 'High']),
        'tests_with_findings': len(df[df['finding_logged'] == True]),
        'avg_completion_rate': (len(df[df['result'].isin(['Pass', 'Fail'])]) / len(df)) * 100 if len(df) > 0 else 0
    }
    
    return metrics

def main():
    st.markdown('<h1 class="main-header">Control Testing Management</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_control_testing_data()
    metrics = calculate_testing_metrics(df)
    
    # Sidebar
    st.sidebar.header("🧪 Control Testing")
    
    # Add new test form
    with st.sidebar.expander("➕ Add New Test", expanded=False):
        with st.form("add_test"):
            col1, col2 = st.columns(2)
            
            with col1:
                test_id = st.text_input("Test ID", placeholder="e.g., CTRL-001")
                test_name = st.text_input("Test Name", placeholder="e.g., User Access Control Test")
                control_tested = st.text_input("Control Tested", placeholder="e.g., CTRL-001")
                test_type = st.selectbox("Test Type", ["Access Management", "Vulnerability Management", "Change Control", "Data Management", "Incident Response", "System Monitoring", "Data Protection", "Security Awareness"])
            
            with col2:
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                result = st.selectbox("Result", ["Planned", "In Progress", "Pass", "Fail"])
                tester = st.text_input("Tester", placeholder="e.g., IT Security Team")
                evidence_status = st.selectbox("Evidence Status", ["Available", "Pending", "Not Available"])
            
            scope = st.text_area("Scope", placeholder="Describe the test scope...")
            methodology = st.text_area("Methodology", placeholder="Describe the testing methodology...")
            
            col1, col2 = st.columns(2)
            with col1:
                test_date = st.date_input("Test Date", value=datetime.date.today())
            with col2:
                due_date = st.date_input("Due Date", value=datetime.date.today() + timedelta(days=30))
            
            submitted = st.form_submit_button("Add Test")
            if submitted:
                st.success("Control test added successfully!")
    
    # Filters
    st.sidebar.subheader("🔍 Filters")
    
    result_filter = st.sidebar.multiselect(
        "Result",
        df['result'].unique(),
        default=df['result'].unique()
    )
    
    test_type_filter = st.sidebar.multiselect(
        "Test Type",
        df['test_type'].unique(),
        default=df['test_type'].unique()
    )
    
    priority_filter = st.sidebar.multiselect(
        "Priority",
        df['priority'].unique(),
        default=df['priority'].unique()
    )
    
    # Apply filters
    filtered_df = df[
        (df['result'].isin(result_filter)) &
        (df['test_type'].isin(test_type_filter)) &
        (df['priority'].isin(priority_filter))
    ]
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📋 Test List", "🔍 Test Details", "📈 Analytics", "📋 Reports"])
    
    with tab1:
        st.header("📊 Control Testing Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tests", metrics['total_tests'])
        
        with col2:
            st.metric("Pass Rate", f"{metrics['avg_completion_rate']:.1f}%")
        
        with col3:
            st.metric("Failed Tests", metrics['failed_tests'])
        
        with col4:
            st.metric("Overdue Tests", metrics['overdue_tests'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Result distribution
            result_counts = df['result'].value_counts()
            fig_result = px.pie(
                values=result_counts.values,
                names=result_counts.index,
                title="Test Results Distribution"
            )
            st.plotly_chart(fig_result, use_container_width=True)
        
        with col2:
            # Test type distribution
            type_counts = df['test_type'].value_counts()
            fig_type = px.bar(
                x=type_counts.index,
                y=type_counts.values,
                title="Tests by Type",
                labels={'x': 'Test Type', 'y': 'Count'}
            )
            st.plotly_chart(fig_type, use_container_width=True)
        
        # Priority vs Result matrix
        st.subheader("🎯 Priority vs Result Matrix")
        
        priority_result_matrix = pd.crosstab(df['priority'], df['result'])
        fig_matrix = px.imshow(
            priority_result_matrix,
            title="Priority vs Result Matrix",
            labels={'x': 'Result', 'y': 'Priority'},
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
        
        # Timeline view
        st.subheader("📅 Testing Timeline")
        
        # Calculate days to due date
        today = datetime.datetime.now()
        df['days_to_due'] = (df['due_date'] - today).dt.days
        
        fig_timeline = px.scatter(
            df,
            x='days_to_due',
            y='priority',
            color='result',
            hover_data=['test_name', 'tester'],
            title="Testing Timeline (Days to Due Date)",
            labels={'days_to_due': 'Days to Due Date', 'priority': 'Priority'}
        )
        fig_timeline.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Today")
        fig_timeline.add_vline(x=7, line_dash="dash", line_color="orange", annotation_text="7 Days")
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    with tab2:
        st.header("📋 Control Test List")
        
        # Display filtered tests
        if len(filtered_df) > 0:
            # Format data for display
            display_df = filtered_df.copy()
            display_df['test_date'] = display_df['test_date'].dt.strftime('%Y-%m-%d')
            display_df['due_date'] = display_df['due_date'].dt.strftime('%Y-%m-%d')
            display_df['finding_logged'] = display_df['finding_logged'].map({True: 'Yes', False: 'No'})
            
            st.dataframe(
                display_df[['test_id', 'test_name', 'test_type', 'result', 'priority', 'tester', 'due_date', 'finding_logged']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No tests found matching the selected filters.")
    
    with tab3:
        st.header("🔍 Test Details")
        
        # Select test for detailed view
        if len(filtered_df) > 0:
            selected_test = st.selectbox(
                "Select Test for Detailed View",
                filtered_df['test_name'].tolist()
            )
            
            test_data = filtered_df[filtered_df['test_name'] == selected_test].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Test Information")
                st.write(f"**Test ID:** {test_data['test_id']}")
                st.write(f"**Control Tested:** {test_data['control_tested']}")
                st.write(f"**Test Type:** {test_data['test_type']}")
                st.write(f"**Result:** {test_data['result']}")
                st.write(f"**Priority:** {test_data['priority']}")
                st.write(f"**Tester:** {test_data['tester']}")
                st.write(f"**Test Date:** {test_data['test_date'].strftime('%Y-%m-%d')}")
                st.write(f"**Due Date:** {test_data['due_date'].strftime('%Y-%m-%d')}")
            
            with col2:
                st.subheader("Test Details")
                st.write(f"**Scope:** {test_data['scope']}")
                st.write(f"**Methodology:** {test_data['methodology']}")
                st.write(f"**Findings:** {test_data['findings']}")
                st.write(f"**Recommendations:** {test_data['recommendations']}")
                st.write(f"**Corrective Action:** {test_data['corrective_action']}")
                st.write(f"**Evidence Status:** {test_data['evidence_status']}")
                st.write(f"**Evidence Link:** {test_data['evidence_link']}")
                st.write(f"**Finding Logged:** {'Yes' if test_data['finding_logged'] else 'No'}")
            
            # Framework mappings
            st.subheader("Framework Mappings")
            for mapping in test_data['framework_mappings']:
                st.write(f"• {mapping}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📝 Update Test", key=f"update_{test_data['test_id']}"):
                    st.success(f"Test {test_data['test_id']} updated!")
            
            with col2:
                if st.button("📋 Generate Report", key=f"report_{test_data['test_id']}"):
                    st.success(f"Report generated for {test_data['test_id']}!")
            
            with col3:
                if st.button("📎 View Evidence", key=f"evidence_{test_data['test_id']}"):
                    st.success(f"Evidence opened for {test_data['test_id']}!")
        else:
            st.warning("No tests available for detailed view.")
    
    with tab4:
        st.header("📈 Testing Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Test completion trend
            st.subheader("📊 Test Completion Trend")
            
            # Group by month
            monthly_tests = df.groupby(df['test_date'].dt.to_period('M')).size()
            
            fig_trend = px.line(
                x=monthly_tests.index.astype(str),
                y=monthly_tests.values,
                title="Monthly Test Completion",
                labels={'x': 'Month', 'y': 'Number of Tests'}
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Pass rate by test type
            st.subheader("📊 Pass Rate by Test Type")
            
            pass_rate_by_type = df.groupby('test_type')['result'].apply(
                lambda x: (x == 'Pass').sum() / len(x) * 100
            ).reset_index()
            pass_rate_by_type.columns = ['Test Type', 'Pass Rate (%)']
            
            fig_pass_rate = px.bar(
                pass_rate_by_type,
                x='Test Type',
                y='Pass Rate (%)',
                title="Pass Rate by Test Type"
            )
            st.plotly_chart(fig_pass_rate, use_container_width=True)
        
        # Framework compliance
        st.subheader("🏛️ Framework Compliance")
        
        # Simulate framework compliance data
        frameworks = ['NIST CSF', 'ISO 27001', 'SOC 2', 'PCI DSS', 'HIPAA']
        compliance_scores = [85, 78, 92, 65, 88]
        
        fig_framework = px.bar(
            x=frameworks,
            y=compliance_scores,
            title="Framework Compliance Scores",
            labels={'x': 'Framework', 'y': 'Compliance Score (%)'}
        )
        st.plotly_chart(fig_framework, use_container_width=True)
        
        # Risk-based testing analysis
        st.subheader("⚠️ Risk-Based Testing Analysis")
        
        # Simulate risk scores
        risk_data = []
        for _, test in filtered_df.iterrows():
            risk_score = random.randint(1, 100)
            risk_data.append({
                'Test': test['test_name'],
                'Risk Score': risk_score,
                'Priority': test['priority'],
                'Result': test['result']
            })
        
        risk_df = pd.DataFrame(risk_data)
        
        fig_risk = px.scatter(
            risk_df,
            x='Risk Score',
            y='Test',
            color='Result',
            size='Risk Score',
            title="Risk Score vs Test Results",
            labels={'Risk Score': 'Risk Score', 'Test': 'Test Name'}
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with tab5:
        st.header("📋 Reports & Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export options
            st.subheader("📤 Export Options")
            
            if st.button("📊 Export to Excel"):
                st.success("Control testing report exported to Excel successfully!")
            
            if st.button("📈 Generate Executive Summary"):
                st.success("Executive summary generated!")
            
            if st.button("📋 Export Test Results"):
                st.success("Test results exported!")
        
        with col2:
            # Management actions
            st.subheader("⚙️ Management Actions")
            
            if st.button("🔄 Refresh Data"):
                st.rerun()
            
            if st.button("📧 Send Reminders"):
                st.success("Reminders sent to testers!")
            
            if st.button("📅 Schedule Reviews"):
                st.success("Review schedule updated!")
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        
        summary_data = {
            'Metric': [
                'Total Tests',
                'Passed Tests',
                'Failed Tests',
                'In Progress',
                'Planned',
                'Overdue Tests',
                'High Priority',
                'Tests with Findings',
                'Average Completion Rate'
            ],
            'Value': [
                str(metrics['total_tests']),
                str(metrics['passed_tests']),
                str(metrics['failed_tests']),
                str(metrics['in_progress_tests']),
                str(metrics['planned_tests']),
                str(metrics['overdue_tests']),
                str(metrics['high_priority_tests']),
                str(metrics['tests_with_findings']),
                f"{metrics['avg_completion_rate']:.1f}%"
            ],
            'Status': [
                '✅' if metrics['total_tests'] > 0 else '❌',
                '✅' if metrics['passed_tests'] > 0 else '❌',
                '⚠️' if metrics['failed_tests'] > 0 else '✅',
                '⚠️' if metrics['in_progress_tests'] > 0 else '✅',
                '⚠️' if metrics['planned_tests'] > 0 else '✅',
                '❌' if metrics['overdue_tests'] > 0 else '✅',
                '⚠️' if metrics['high_priority_tests'] > 0 else '✅',
                '⚠️' if metrics['tests_with_findings'] > 0 else '✅',
                '✅' if metrics['avg_completion_rate'] >= 80 else '⚠️'
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
