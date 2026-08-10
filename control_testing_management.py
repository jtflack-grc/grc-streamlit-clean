import streamlit as st
import demo_kit
import portfolio_skin
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
    page_title="Control Testing Management · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)



# Sample control testing data
@st.cache_data
def load_control_testing_data():
    """Load sample control testing data (FY26 demo set)."""
    tests = [
        {
            "test_id": "CT-2026-001",
            "test_name": "Privileged Access Quarterly Review",
            "control_tested": "AC-02 Privileged Account Management",
            "test_type": "Access Management",
            "result": "Pass",
            "corrective_action": "N/A",
            "evidence_status": "Available",
            "priority": "High",
            "tester": "Maya Chen · IT Security",
            "test_date": "2026-05-12",
            "due_date": "2026-05-30",
            "framework_mappings": ["NIST CSF PR.AA-01", "ISO 27001 A.8.2", "SOC 2 CC6.1"],
            "scope": "Domain admins, break-glass, and cloud root accounts",
            "methodology": "Sampled 100% of privileged accounts; reconciled to ticketing approvals",
            "findings": "All sampled accounts had current manager attestation and ticket trail",
            "recommendations": "Keep quarterly cadence; add SaaS admin roles next cycle",
            "evidence_link": "GRC/Evidence/AC-02/2026-Q2",
            "finding_logged": False,
        },
        {
            "test_id": "CT-2026-002",
            "test_name": "Critical Patch SLA Sampling",
            "control_tested": "VM-01 Patch Management",
            "test_type": "Vulnerability Management",
            "result": "Fail",
            "corrective_action": "Remediate overdue CVEs on ERP hosts by 2026-08-22",
            "evidence_status": "Available",
            "priority": "High",
            "tester": "Jordan Blake · Infrastructure",
            "test_date": "2026-06-18",
            "due_date": "2026-07-02",
            "framework_mappings": ["NIST CSF ID.RA-01", "ISO 27001 A.8.8", "SOC 2 CC7.1"],
            "scope": "Critical/High CVEs on production Windows & Linux",
            "methodology": "Scanner export + 25-host sample with change-record match",
            "findings": "4 of 25 sampled hosts exceeded 30-day critical patch SLA",
            "recommendations": "Stand up emergency CAB lane for critical CVEs; alert on SLA breach",
            "evidence_link": "GRC/Evidence/VM-01/2026-Q2",
            "finding_logged": True,
        },
        {
            "test_id": "CT-2026-003",
            "test_name": "Change CAB Completeness Review",
            "control_tested": "CM-03 Change Control",
            "test_type": "Change Control",
            "result": "Pass",
            "corrective_action": "N/A",
            "evidence_status": "Available",
            "priority": "Medium",
            "tester": "Priya Nair · IT Operations",
            "test_date": "2026-06-25",
            "due_date": "2026-07-10",
            "framework_mappings": ["NIST CSF PR.PS-01", "ISO 27001 A.8.32", "SOC 2 CC8.1"],
            "scope": "Production changes logged in ServiceNow (May–Jun)",
            "methodology": "40-change sample: approval, backout, and post-impl notes",
            "findings": "39/40 changes met CAB documentation; one emergency change late-filed",
            "recommendations": "Auto-prompt emergency change closeout within 48h",
            "evidence_link": "GRC/Evidence/CM-03/2026-Q2",
            "finding_logged": False,
        },
        {
            "test_id": "CT-2026-004",
            "test_name": "Data Retention Policy Spot Check",
            "control_tested": "DM-04 Retention & Disposal",
            "test_type": "Data Management",
            "result": "In Progress",
            "corrective_action": "Pending Legal review of legal-hold exceptions",
            "evidence_status": "Pending",
            "priority": "Medium",
            "tester": "Sam Ortiz · Data Governance",
            "test_date": "2026-07-28",
            "due_date": "2026-08-15",
            "framework_mappings": ["NIST CSF PR.DS-01", "ISO 27001 A.8.10", "SOC 2 CC6.5"],
            "scope": "SharePoint / file-share retention labels for PII repositories",
            "methodology": "Policy walkthrough + sample of 15 repositories vs retention schedule",
            "findings": "3 repositories missing disposal evidence; legal holds under review",
            "recommendations": "Enforce retention labels via DLP; quarterly disposal attestation",
            "evidence_link": "GRC/Evidence/DM-04/2026-Q3",
            "finding_logged": True,
        },
        {
            "test_id": "CT-2026-005",
            "test_name": "Incident Response Tabletop (Ransomware)",
            "control_tested": "IR-01 Incident Response Plan",
            "test_type": "Incident Response",
            "result": "Pass",
            "corrective_action": "N/A — minor playbook updates tracked",
            "evidence_status": "Available",
            "priority": "High",
            "tester": "Alex Rivera · SecOps",
            "test_date": "2026-07-09",
            "due_date": "2026-07-20",
            "framework_mappings": ["NIST CSF RS.MA-01", "ISO 27001 A.5.24", "SOC 2 CC7.3"],
            "scope": "IR leadership, Legal, Comms, and on-call engineers",
            "methodology": "2-hour tabletop with injects; scored against playbook steps",
            "findings": "Detection→containment path met RTO targets; Comms templates need refresh",
            "recommendations": "Update external notification templates; re-run in Q4",
            "evidence_link": "GRC/Evidence/IR-01/2026-Q3",
            "finding_logged": False,
        },
        {
            "test_id": "CT-2026-006",
            "test_name": "Central Logging Coverage Test",
            "control_tested": "MON-02 Security Logging",
            "test_type": "System Monitoring",
            "result": "Fail",
            "corrective_action": "Onboard missing DMZ hosts to SIEM by 2026-08-29",
            "evidence_status": "Available",
            "priority": "High",
            "tester": "Maya Chen · IT Security",
            "test_date": "2026-07-22",
            "due_date": "2026-08-05",
            "framework_mappings": ["NIST CSF DE.CM-01", "ISO 27001 A.8.15", "SOC 2 CC7.2"],
            "scope": "Auth, firewall, and privileged activity logs for Tier-0/Tier-1 systems",
            "methodology": "Asset inventory vs SIEM source list; sample event validation",
            "findings": "6 DMZ jump hosts not forwarding auth logs; gaps >14 days",
            "recommendations": "Mandatory SIEM onboarding checklist in build pipeline",
            "evidence_link": "GRC/Evidence/MON-02/2026-Q3",
            "finding_logged": True,
        },
        {
            "test_id": "CT-2026-007",
            "test_name": "Backup Restore Drill — ERP",
            "control_tested": "BC-05 Backup & Recovery",
            "test_type": "Data Protection",
            "result": "Pass",
            "corrective_action": "N/A",
            "evidence_status": "Available",
            "priority": "High",
            "tester": "Jordan Blake · Infrastructure",
            "test_date": "2026-06-04",
            "due_date": "2026-06-20",
            "framework_mappings": ["NIST CSF PR.DS-11", "ISO 27001 A.8.13", "SOC 2 CC6.1"],
            "scope": "ERP production DB restore to isolated test environment",
            "methodology": "Full restore + integrity check against known checksum set",
            "findings": "Restore completed in 3h 40m (RTO target 4h); checksums matched",
            "recommendations": "Document runbook timings; include app-tier smoke tests next drill",
            "evidence_link": "GRC/Evidence/BC-05/2026-Q2",
            "finding_logged": False,
        },
        {
            "test_id": "CT-2026-008",
            "test_name": "Security Awareness Completion Audit",
            "control_tested": "AT-01 Security Training",
            "test_type": "Security Awareness",
            "result": "Pass",
            "corrective_action": "N/A",
            "evidence_status": "Available",
            "priority": "Low",
            "tester": "Taylor Kim · People Ops",
            "test_date": "2026-05-28",
            "due_date": "2026-06-15",
            "framework_mappings": ["NIST CSF PR.AT-01", "ISO 27001 A.6.3", "SOC 2 CC1.4"],
            "scope": "All active employees + contractors >30 days tenure",
            "methodology": "LMS export vs HRIS headcount; phish-sim click-rate review",
            "findings": "97.8% completion; phish click-rate 4.1% (target <6%)",
            "recommendations": "Target remediations for two late-joining contractor cohorts",
            "evidence_link": "GRC/Evidence/AT-01/2026-Q2",
            "finding_logged": False,
        },
        {
            "test_id": "CT-2026-009",
            "test_name": "MFA Enforcement — Remote Access",
            "control_tested": "AC-07 Remote Access MFA",
            "test_type": "Access Management",
            "result": "In Progress",
            "corrective_action": "N/A",
            "evidence_status": "Pending",
            "priority": "High",
            "tester": "Alex Rivera · SecOps",
            "test_date": "2026-08-04",
            "due_date": "2026-08-22",
            "framework_mappings": ["NIST CSF PR.AA-03", "ISO 27001 A.8.5", "SOC 2 CC6.1"],
            "scope": "VPN, SSO, and privileged jump-host MFA policies",
            "methodology": "IdP policy export + 50-user login sample",
            "findings": "Testing underway — 2 legacy service accounts flagged for review",
            "recommendations": "Pending final sample closeout",
            "evidence_link": "GRC/Evidence/AC-07/2026-Q3",
            "finding_logged": False,
        },
        {
            "test_id": "CT-2026-010",
            "test_name": "Vendor SOC 2 Evidence Review",
            "control_tested": "TP-02 Third-Party Assurance",
            "test_type": "Change Control",
            "result": "Planned",
            "corrective_action": "N/A",
            "evidence_status": "Not Available",
            "priority": "Medium",
            "tester": "Priya Nair · IT Operations",
            "test_date": "2026-08-18",
            "due_date": "2026-09-12",
            "framework_mappings": ["NIST CSF GV.SC-01", "ISO 27001 A.5.19", "SOC 2 CC9.2"],
            "scope": "Top 10 critical SaaS vendors with SOC 2 Type II reports",
            "methodology": "Bridge-letter + CUEC mapping to internal complementary controls",
            "findings": "Scheduled — evidence pack requested from vendors",
            "recommendations": "N/A until fieldwork starts",
            "evidence_link": "GRC/Evidence/TP-02/2026-Q3",
            "finding_logged": False,
        },
        {
            "test_id": "CT-2026-011",
            "test_name": "Firewall Rule Recertification",
            "control_tested": "NS-03 Network ACL Review",
            "test_type": "System Monitoring",
            "result": "Planned",
            "corrective_action": "N/A",
            "evidence_status": "Not Available",
            "priority": "Medium",
            "tester": "Jordan Blake · Infrastructure",
            "test_date": "2026-08-25",
            "due_date": "2026-09-19",
            "framework_mappings": ["NIST CSF PR.IR-01", "ISO 27001 A.8.20", "SOC 2 CC6.6"],
            "scope": "Internet-facing and DMZ firewall rulebases",
            "methodology": "Owner attestation + unused-rule analysis from 90-day hit counts",
            "findings": "Not started",
            "recommendations": "N/A",
            "evidence_link": "GRC/Evidence/NS-03/2026-Q3",
            "finding_logged": False,
        },
        {
            "test_id": "CT-2026-012",
            "test_name": "Encryption at Rest — Cloud Storage",
            "control_tested": "CR-01 Encryption Standards",
            "test_type": "Data Protection",
            "result": "Pass",
            "corrective_action": "N/A",
            "evidence_status": "Available",
            "priority": "Medium",
            "tester": "Sam Ortiz · Data Governance",
            "test_date": "2026-07-15",
            "due_date": "2026-07-31",
            "framework_mappings": ["NIST CSF PR.DS-02", "ISO 27001 A.8.24", "SOC 2 CC6.1"],
            "scope": "S3 / Blob / GCS buckets tagged as Confidential or Restricted",
            "methodology": "CSPM query for default encryption + CMK usage sample",
            "findings": "100% of in-scope buckets encrypted; 82% using customer-managed keys",
            "recommendations": "Migrate remaining SSE-S3 buckets to CMK by Q4",
            "evidence_link": "GRC/Evidence/CR-01/2026-Q3",
            "finding_logged": False,
        },
    ]

    df = pd.DataFrame(tests)
    df["test_date"] = pd.to_datetime(df["test_date"])
    df["due_date"] = pd.to_datetime(df["due_date"])
    return df


def calculate_testing_metrics(df):
    """Calculate key control testing metrics"""
    today = datetime.datetime.now()
    completed = df[df["result"].isin(["Pass", "Fail"])]
    pass_rate = (len(completed[completed["result"] == "Pass"]) / len(completed) * 100) if len(completed) else 0.0
    open_statuses = {"In Progress", "Planned", "Fail"}
    overdue = df[(df["due_date"] < today) & (df["result"].isin(open_statuses))]

    return {
        "total_tests": len(df),
        "passed_tests": len(df[df["result"] == "Pass"]),
        "failed_tests": len(df[df["result"] == "Fail"]),
        "in_progress_tests": len(df[df["result"] == "In Progress"]),
        "planned_tests": len(df[df["result"] == "Planned"]),
        "overdue_tests": len(overdue),
        "high_priority_tests": len(df[df["priority"] == "High"]),
        "tests_with_findings": len(df[df["finding_logged"] == True]),
        "pass_rate": pass_rate,
        "avg_completion_rate": (len(completed) / len(df) * 100) if len(df) else 0.0,
    }

def main():
    portfolio_skin.page_header(
        title="Control Testing Management",
        lede="Interactive GRC tool — #RUNGRCRaleigh build-in-public.",
        kicker="Controls",
    )
    
    # Load data
    df = load_control_testing_data()
    metrics = calculate_testing_metrics(df)
    
    # Sidebar
    st.sidebar.header("Controls")
    seed = demo_kit.seed_controls()
    st.sidebar.markdown("---")
    st.sidebar.subheader("Control Testing")
    
    # Add new test form
    with st.sidebar.expander("Add New Test", expanded=False):
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
    st.sidebar.subheader("Filters")
    
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
    
    # Main content — data first, charts after
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Test List", "Dashboard", "Test Details", "Analytics", "Reports"])

    with tab1:
        st.header("Control Test List")

        if len(filtered_df) > 0:
            display_df = filtered_df.copy()
            display_df["test_date"] = display_df["test_date"].dt.strftime("%Y-%m-%d")
            display_df["due_date"] = display_df["due_date"].dt.strftime("%Y-%m-%d")
            display_df["finding_logged"] = display_df["finding_logged"].map({True: "Yes", False: "No"})

            st.dataframe(
                display_df[
                    [
                        "test_id",
                        "test_name",
                        "control_tested",
                        "test_type",
                        "result",
                        "priority",
                        "tester",
                        "test_date",
                        "due_date",
                        "finding_logged",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("No tests found matching the selected filters.")

    with tab2:
        st.header("Control Testing Dashboard")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tests", metrics["total_tests"])
        with col2:
            st.metric("Pass Rate", f"{metrics['pass_rate']:.1f}%")
        with col3:
            st.metric("Failed Tests", metrics["failed_tests"])
        with col4:
            st.metric("Overdue Open", metrics["overdue_tests"])

        # Snapshot table before charts
        st.subheader("Current Test Snapshot")
        snap = filtered_df.copy()
        snap["due_date"] = snap["due_date"].dt.strftime("%Y-%m-%d")
        st.dataframe(
            snap[["test_id", "test_name", "result", "priority", "tester", "due_date"]],
            use_container_width=True,
            hide_index=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            result_counts = df["result"].value_counts()
            fig_result = px.pie(
                values=result_counts.values,
                names=result_counts.index,
                title="Test Results Distribution",
            )
            st.plotly_chart(fig_result, use_container_width=True)

        with col2:
            type_counts = df["test_type"].value_counts()
            fig_type = px.bar(
                x=type_counts.index,
                y=type_counts.values,
                title="Tests by Type",
                labels={"x": "Test Type", "y": "Count"},
            )
            st.plotly_chart(fig_type, use_container_width=True)

        st.subheader("Priority vs Result Matrix")
        priority_result_matrix = pd.crosstab(df["priority"], df["result"])
        fig_matrix = px.imshow(
            priority_result_matrix,
            title="Priority vs Result Matrix",
            labels={"x": "Result", "y": "Priority"},
            color_continuous_scale="Reds",
        )
        st.plotly_chart(fig_matrix, use_container_width=True)

        st.subheader("Testing Timeline")
        today = datetime.datetime.now()
        timeline_df = df.copy()
        timeline_df["days_to_due"] = (timeline_df["due_date"] - today).dt.days
        fig_timeline = px.scatter(
            timeline_df,
            x="days_to_due",
            y="priority",
            color="result",
            hover_data=["test_name", "tester"],
            title="Testing Timeline (Days to Due Date)",
            labels={"days_to_due": "Days to Due Date", "priority": "Priority"},
        )
        fig_timeline.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Today")
        fig_timeline.add_vline(x=7, line_dash="dash", line_color="orange", annotation_text="7 Days")
        st.plotly_chart(fig_timeline, use_container_width=True)

    with tab3:
        st.header("Test Details")
        
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
                if st.button("Update Test", key=f"update_{test_data['test_id']}"):
                    st.success(f"Test {test_data['test_id']} updated!")
            
            with col2:
                if st.button("Generate Report", key=f"report_{test_data['test_id']}"):
                    st.success(f"Report generated for {test_data['test_id']}!")
            
            with col3:
                if st.button("View Evidence", key=f"evidence_{test_data['test_id']}"):
                    st.success(f"Evidence opened for {test_data['test_id']}!")
        else:
            st.warning("No tests available for detailed view.")
    
    with tab4:
        st.header("Testing Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Test completion trend
            st.subheader("Test Completion Trend")
            
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
            st.subheader("Pass Rate by Test Type")
            
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
        st.subheader("Framework Compliance")
        
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
        st.subheader("Risk-Based Testing Analysis")
        
        # Simulate risk scores
        risk_data = []
        rng = np.random.default_rng(seed)
        for _, test in filtered_df.iterrows():
            risk_score = int(rng.integers(1, 101))
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
        st.header("Reports & Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Export Options")
            export_df = filtered_df.copy()
            for col in ("test_date", "due_date"):
                if col in export_df.columns:
                    export_df[col] = export_df[col].astype(str)
            if "framework_mappings" in export_df.columns:
                export_df["framework_mappings"] = export_df["framework_mappings"].apply(
                    lambda v: "; ".join(v) if isinstance(v, (list, tuple)) else v
                )
            demo_kit.csv_download(
                export_df,
                "control_tests_filtered.csv",
                label="Download filtered tests",
            )
        
        with col2:
            # Management actions
            st.subheader("Management Actions")
            
            if st.button("Refresh Data"):
                st.rerun()
            
            if st.button("Send Reminders"):
                st.success("Reminders sent to testers!")
            
            if st.button("Schedule Reviews"):
                st.success("Review schedule updated!")
        
        # Summary statistics
        st.subheader("Summary Statistics")
        
        summary_data = {
            'Metric': [
                'Total Tests',
                'Passed Tests',
                'Failed Tests',
                'In Progress',
                'Planned',
                'Overdue Tests',
                'High Priority',
                "Tests with Findings",
                "Pass Rate (completed)",
            ],
            "Value": [
                str(metrics['total_tests']),
                str(metrics['passed_tests']),
                str(metrics['failed_tests']),
                str(metrics['in_progress_tests']),
                str(metrics['planned_tests']),
                str(metrics['overdue_tests']),
                str(metrics['high_priority_tests']),
                str(metrics['tests_with_findings']),
                f"{metrics['pass_rate']:.1f}%"
            ],
            "Status": [
                "",
                "",
                "",
                "",
                "",
                "Attention" if metrics["overdue_tests"] > 0 else "OK",
                "",
                "",
                "OK" if metrics["pass_rate"] >= 70 else "Attention",
            ],
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
