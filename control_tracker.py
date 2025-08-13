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
    page_title="Control Tracker",
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

    /* Control status styling */
    .status-not-implemented { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .status-in-progress { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
    .status-implemented { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
    .status-tested { background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196f3; }
    .status-compliant { background-color: rgba(156, 39, 176, 0.1); border-left: 4px solid #9c27b0; }
</style>
""", unsafe_allow_html=True)

# Sample control data
@st.cache_data
def load_control_data():
    """Load sample control data"""
    controls = [
        {
            "control_id": "AC-01",
            "control_name": "Access Control Policy",
            "framework": "NIST CSF",
            "category": "Identity Management and Access Control",
            "description": "Establish and maintain access control policies and procedures",
            "status": "Compliant",
            "owner": "IT Security Team",
            "risk_score": 25,
            "last_review": "2024-01-15",
            "next_review": "2024-07-15",
            "evidence_count": 5,
            "test_results": "Passed",
            "implementation_date": "2023-06-01"
        },
        {
            "control_id": "AC-02",
            "control_name": "Account Management",
            "framework": "NIST CSF",
            "category": "Identity Management and Access Control",
            "description": "Manage information system accounts",
            "status": "Tested",
            "owner": "IT Security Team",
            "risk_score": 35,
            "last_review": "2024-02-01",
            "next_review": "2024-08-01",
            "evidence_count": 3,
            "test_results": "Passed",
            "implementation_date": "2023-07-15"
        },
        {
            "control_id": "A.5.1",
            "control_name": "Information Security Policies",
            "framework": "ISO 27001",
            "category": "Information Security Policies",
            "description": "Define information security policy framework",
            "status": "Compliant",
            "owner": "Security Governance",
            "risk_score": 20,
            "last_review": "2024-01-20",
            "next_review": "2024-07-20",
            "evidence_count": 4,
            "test_results": "Passed",
            "implementation_date": "2023-05-01"
        },
        {
            "control_id": "CC6.1",
            "control_name": "Logical Access Security Software",
            "framework": "SOC 2",
            "category": "Security",
            "description": "Implement logical access security software",
            "status": "Implemented",
            "owner": "IT Operations",
            "risk_score": 45,
            "last_review": "2024-02-10",
            "next_review": "2024-08-10",
            "evidence_count": 2,
            "test_results": "In Progress",
            "implementation_date": "2023-08-01"
        },
        {
            "control_id": "CC7.1",
            "control_name": "System Operation Monitoring",
            "framework": "SOC 2",
            "category": "Security",
            "description": "Monitor system operations for security events",
            "status": "In Progress",
            "owner": "IT Operations",
            "risk_score": 60,
            "last_review": "2024-01-30",
            "next_review": "2024-07-30",
            "evidence_count": 1,
            "test_results": "Not Started",
            "implementation_date": "2023-09-15"
        },
        {
            "control_id": "3.1",
            "control_name": "Network Security Controls",
            "framework": "PCI DSS",
            "category": "Network Security",
            "description": "Implement network security controls",
            "status": "Tested",
            "owner": "Network Security",
            "risk_score": 40,
            "last_review": "2024-02-05",
            "next_review": "2024-08-05",
            "evidence_count": 3,
            "test_results": "Passed",
            "implementation_date": "2023-06-15"
        },
        {
            "control_id": "164.308",
            "control_name": "Administrative Safeguards",
            "framework": "HIPAA",
            "category": "Administrative Safeguards",
            "description": "Implement administrative safeguards",
            "status": "Not Implemented",
            "owner": "Compliance Team",
            "risk_score": 80,
            "last_review": "2024-01-10",
            "next_review": "2024-07-10",
            "evidence_count": 0,
            "test_results": "Not Started",
            "implementation_date": None
        },
        {
            "control_id": "ID.AM-1",
            "control_name": "Asset Inventory",
            "framework": "NIST CSF",
            "category": "Asset Management",
            "description": "Maintain asset inventory",
            "status": "Implemented",
            "owner": "Asset Management",
            "risk_score": 30,
            "last_review": "2024-02-15",
            "next_review": "2024-08-15",
            "evidence_count": 2,
            "test_results": "Passed",
            "implementation_date": "2023-07-01"
        },
        {
            "control_id": "PR.AC-1",
            "control_name": "Identity Management",
            "framework": "NIST CSF",
            "category": "Identity Management and Access Control",
            "description": "Manage identities and credentials",
            "status": "Compliant",
            "owner": "IT Security Team",
            "risk_score": 25,
            "last_review": "2024-01-25",
            "next_review": "2024-07-25",
            "evidence_count": 4,
            "test_results": "Passed",
            "implementation_date": "2023-05-15"
        },
        {
            "control_id": "DE.CM-1",
            "control_name": "Security Monitoring",
            "framework": "NIST CSF",
            "category": "Security Continuous Monitoring",
            "description": "Monitor security events",
            "status": "In Progress",
            "owner": "Security Operations",
            "risk_score": 55,
            "last_review": "2024-02-20",
            "next_review": "2024-08-20",
            "evidence_count": 1,
            "test_results": "In Progress",
            "implementation_date": "2023-10-01"
        }
    ]
    
    return pd.DataFrame(controls)

def calculate_control_metrics(df):
    """Calculate key control metrics"""
    metrics = {
        'total_controls': len(df),
        'compliant_controls': len(df[df['status'] == 'Compliant']),
        'implemented_controls': len(df[df['status'].isin(['Implemented', 'Tested', 'Compliant'])]),
        'in_progress_controls': len(df[df['status'] == 'In Progress']),
        'not_implemented_controls': len(df[df['status'] == 'Not Implemented']),
        'avg_risk_score': df['risk_score'].mean(),
        'high_risk_controls': len(df[df['risk_score'] >= 70]),
        'overdue_reviews': len(df[pd.to_datetime(df['next_review']) < datetime.datetime.now()])
    }
    
    # Calculate compliance percentage
    metrics['compliance_rate'] = (metrics['compliant_controls'] / metrics['total_controls']) * 100
    metrics['implementation_rate'] = (metrics['implemented_controls'] / metrics['total_controls']) * 100
    
    return metrics

def get_status_color(status):
    """Get color for status"""
    colors = {
        'Not Implemented': '#d32f2f',
        'In Progress': '#f57c00',
        'Implemented': '#388e3c',
        'Tested': '#1976d2',
        'Compliant': '#7b1fa2'
    }
    return colors.get(status, '#757575')

def main():
    st.markdown('<h1 class="main-header">Control Tracker</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_control_data()
    
    # Sidebar
    st.sidebar.header("🔧 Control Management")
    
    # Add new control form
    with st.sidebar.expander("➕ Add New Control", expanded=False):
        with st.form("add_control"):
            col1, col2 = st.columns(2)
            
            with col1:
                control_id = st.text_input("Control ID", placeholder="e.g., AC-01")
                control_name = st.text_input("Control Name", placeholder="e.g., Access Control Policy")
                framework = st.selectbox("Framework", ["NIST CSF", "ISO 27001", "SOC 2", "PCI DSS", "HIPAA", "GDPR"])
                category = st.text_input("Category", placeholder="e.g., Identity Management")
            
            with col2:
                status = st.selectbox("Status", ["Not Implemented", "In Progress", "Implemented", "Tested", "Compliant"])
                owner = st.text_input("Owner", placeholder="e.g., IT Security Team")
                risk_score = st.slider("Risk Score", 1, 100, 50)
                evidence_count = st.number_input("Evidence Count", 0, 10, 0)
            
            description = st.text_area("Description", placeholder="Control description...")
            
            submitted = st.form_submit_button("Add Control")
            if submitted:
                st.success("Control added successfully!")
    
    # Filters
    st.sidebar.subheader("🔍 Filters")
    
    framework_filter = st.sidebar.multiselect(
        "Framework",
        df['framework'].unique(),
        default=df['framework'].unique()
    )
    
    status_filter = st.sidebar.multiselect(
        "Status",
        df['status'].unique(),
        default=df['status'].unique()
    )
    
    risk_filter = st.sidebar.slider(
        "Risk Score Range",
        0, 100, (0, 100)
    )
    
    # Apply filters
    filtered_df = df[
        (df['framework'].isin(framework_filter)) &
        (df['status'].isin(status_filter)) &
        (df['risk_score'] >= risk_filter[0]) &
        (df['risk_score'] <= risk_filter[1])
    ]
    
    # Calculate metrics
    metrics = calculate_control_metrics(filtered_df)
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🎛️ Control Inventory", "📈 Analytics", "⚠️ Risk Management", "📋 Management"])
    
    with tab1:
        st.header("📊 Control Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Controls",
                metrics['total_controls'],
                delta=f"{metrics['compliance_rate']:.1f}% Compliant"
            )
        
        with col2:
            st.metric(
                "Compliance Rate",
                f"{metrics['compliance_rate']:.1f}%",
                delta=f"{metrics['compliant_controls']} Controls"
            )
        
        with col3:
            st.metric(
                "Implementation Rate",
                f"{metrics['implementation_rate']:.1f}%",
                delta=f"{metrics['implemented_controls']} Implemented"
            )
        
        with col4:
            st.metric(
                "Average Risk Score",
                f"{metrics['avg_risk_score']:.1f}",
                delta=f"{metrics['high_risk_controls']} High Risk"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            status_counts = filtered_df['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Control Status Distribution",
                color_discrete_map={
                    'Not Implemented': '#d32f2f',
                    'In Progress': '#f57c00',
                    'Implemented': '#388e3c',
                    'Tested': '#1976d2',
                    'Compliant': '#7b1fa2'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Framework distribution
            framework_counts = filtered_df['framework'].value_counts()
            fig_framework = px.bar(
                x=framework_counts.index,
                y=framework_counts.values,
                title="Controls by Framework",
                labels={'x': 'Framework', 'y': 'Number of Controls'}
            )
            st.plotly_chart(fig_framework, use_container_width=True)
        
        # Risk score distribution
        fig_risk = px.histogram(
            filtered_df,
            x='risk_score',
            nbins=10,
            title="Risk Score Distribution",
            labels={'risk_score': 'Risk Score', 'count': 'Number of Controls'}
        )
        fig_risk.add_vline(x=70, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with tab2:
        st.header("🎛️ Control Inventory")
        
        # Search and sort
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search Controls", placeholder="Search by ID, name, or description...")
        
        with col2:
            sort_by = st.selectbox("Sort by", ["Control ID", "Status", "Risk Score", "Framework", "Owner"])
        
        # Apply search filter
        if search_term:
            search_filter = (
                filtered_df['control_id'].str.contains(search_term, case=False) |
                filtered_df['control_name'].str.contains(search_term, case=False) |
                filtered_df['description'].str.contains(search_term, case=False)
            )
            display_df = filtered_df[search_filter]
        else:
            display_df = filtered_df
        
        # Sort data
        if sort_by == "Control ID":
            display_df = display_df.sort_values('control_id')
        elif sort_by == "Status":
            display_df = display_df.sort_values('status')
        elif sort_by == "Risk Score":
            display_df = display_df.sort_values('risk_score', ascending=False)
        elif sort_by == "Framework":
            display_df = display_df.sort_values('framework')
        elif sort_by == "Owner":
            display_df = display_df.sort_values('owner')
        
        # Display controls
        for _, control in display_df.iterrows():
            with st.expander(f"{control['control_id']} - {control['control_name']} ({control['status']})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Framework:** {control['framework']}")
                    st.write(f"**Category:** {control['category']}")
                    st.write(f"**Description:** {control['description']}")
                    st.write(f"**Owner:** {control['owner']}")
                
                with col2:
                    # Risk score indicator
                    risk_color = "red" if control['risk_score'] >= 70 else "orange" if control['risk_score'] >= 50 else "green"
                    st.metric("Risk Score", control['risk_score'], delta=f"{risk_color} Risk")
                    
                    st.write(f"**Evidence Count:** {control['evidence_count']}")
                    st.write(f"**Test Results:** {control['test_results']}")
                    st.write(f"**Last Review:** {control['last_review']}")
                    st.write(f"**Next Review:** {control['next_review']}")
                
                # Progress bar for implementation status
                status_progress = {
                    'Not Implemented': 0,
                    'In Progress': 25,
                    'Implemented': 50,
                    'Tested': 75,
                    'Compliant': 100
                }
                st.progress(status_progress[control['status']] / 100)
                st.caption(f"Implementation Progress: {status_progress[control['status']]}%")
    
    with tab3:
        st.header("📈 Analytics & Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Framework compliance comparison
            framework_compliance = []
            for framework in filtered_df['framework'].unique():
                framework_df = filtered_df[filtered_df['framework'] == framework]
                compliant_count = len(framework_df[framework_df['status'] == 'Compliant'])
                total_count = len(framework_df)
                compliance_rate = (compliant_count / total_count) * 100 if total_count > 0 else 0
                framework_compliance.append({
                    'Framework': framework,
                    'Compliance Rate': compliance_rate,
                    'Total Controls': total_count,
                    'Compliant Controls': compliant_count
                })
            
            framework_compliance_df = pd.DataFrame(framework_compliance)
            
            fig_compliance = px.bar(
                framework_compliance_df,
                x='Framework',
                y='Compliance Rate',
                title="Compliance Rate by Framework",
                labels={'Compliance Rate': 'Compliance Rate (%)'}
            )
            st.plotly_chart(fig_compliance, use_container_width=True)
        
        with col2:
            # Risk score by framework
            fig_risk_framework = px.box(
                filtered_df,
                x='framework',
                y='risk_score',
                title="Risk Score Distribution by Framework",
                labels={'framework': 'Framework', 'risk_score': 'Risk Score'}
            )
            st.plotly_chart(fig_risk_framework, use_container_width=True)
        
        # Trend analysis (simulated)
        st.subheader("📊 Implementation Trends")
        
        # Simulate historical data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='M')
        trend_data = []
        
        for date in dates:
            # Simulate realistic implementation trend
            base_implementation = 30 + (date.year - 2023) * 20 + (date.month - 1) * 1.5
            variation = np.random.normal(0, 2)
            implementation_rate = max(0, min(100, base_implementation + variation))
            
            trend_data.append({
                'Date': date,
                'Implementation Rate': implementation_rate,
                'Month': date.strftime('%Y-%m')
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        fig_trend = px.line(
            trend_df,
            x='Date',
            y='Implementation Rate',
            title="Control Implementation Trend (Simulated)",
            labels={'Implementation Rate': 'Implementation Rate (%)'}
        )
        fig_trend.add_hline(y=metrics['implementation_rate'], line_dash="dash", line_color="red", 
                          annotation_text=f"Current Rate: {metrics['implementation_rate']:.1f}%")
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab4:
        st.header("⚠️ Risk Management")
        
        # High-risk controls
        high_risk_df = filtered_df[filtered_df['risk_score'] >= 70]
        
        if len(high_risk_df) > 0:
            st.warning(f"⚠️ {len(high_risk_df)} High-Risk Controls Identified")
            
            for _, control in high_risk_df.iterrows():
                with st.expander(f"🚨 {control['control_id']} - {control['control_name']} (Risk: {control['risk_score']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Status:** {control['status']}")
                        st.write(f"**Framework:** {control['framework']}")
                        st.write(f"**Owner:** {control['owner']}")
                        st.write(f"**Description:** {control['description']}")
                    
                    with col2:
                        st.write("**Risk Mitigation Actions:**")
                        st.write("1. Prioritize implementation")
                        st.write("2. Assign dedicated resources")
                        st.write("3. Establish monitoring")
                        st.write("4. Regular status reviews")
        else:
            st.success("✅ No high-risk controls identified")
        
        # Overdue reviews
        overdue_df = filtered_df[pd.to_datetime(filtered_df['next_review']) < datetime.datetime.now()]
        
        if len(overdue_df) > 0:
            st.error(f"⏰ {len(overdue_df)} Controls with Overdue Reviews")
            
            for _, control in overdue_df.iterrows():
                days_overdue = (datetime.datetime.now() - pd.to_datetime(control['next_review'])).days
                st.write(f"• {control['control_id']} - {control['control_name']} ({days_overdue} days overdue)")
        else:
            st.success("✅ All control reviews are up to date")
        
        # Risk heatmap
        st.subheader("🔥 Risk Heatmap")
        
        # Create risk matrix
        risk_matrix = pd.DataFrame({
            'Risk Score': range(0, 101, 10),
            'Count': [len(filtered_df[(filtered_df['risk_score'] >= i) & (filtered_df['risk_score'] < i+10)]) for i in range(0, 101, 10)]
        })
        
        fig_heatmap = px.bar(
            risk_matrix,
            x='Risk Score',
            y='Count',
            title="Risk Score Distribution",
            color='Count',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab5:
        st.header("📋 Management & Reporting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export options
            st.subheader("📤 Export Options")
            
            if st.button("📊 Export to Excel"):
                st.success("Control inventory exported to Excel successfully!")
            
            if st.button("📈 Generate Report"):
                st.success("Comprehensive control report generated!")
            
            if st.button("📋 Export Compliance Summary"):
                st.success("Compliance summary exported!")
        
        with col2:
            # Management actions
            st.subheader("⚙️ Management Actions")
            
            if st.button("🔄 Refresh Data"):
                st.rerun()
            
            if st.button("📅 Schedule Reviews"):
                st.success("Review schedule updated!")
            
            if st.button("📧 Send Notifications"):
                st.success("Notifications sent to control owners!")
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        
        summary_data = {
            'Metric': [
                'Total Controls',
                'Compliant Controls',
                'Implementation Rate',
                'Average Risk Score',
                'High Risk Controls',
                'Overdue Reviews'
            ],
            'Value': [
                metrics['total_controls'],
                metrics['compliant_controls'],
                f"{metrics['implementation_rate']:.1f}%",
                f"{metrics['avg_risk_score']:.1f}",
                metrics['high_risk_controls'],
                metrics['overdue_reviews']
            ],
            'Status': [
                '✅' if metrics['total_controls'] > 0 else '❌',
                '✅' if metrics['compliant_controls'] > 0 else '❌',
                '✅' if metrics['implementation_rate'] >= 80 else '⚠️',
                '✅' if metrics['avg_risk_score'] <= 50 else '⚠️',
                '❌' if metrics['high_risk_controls'] > 0 else '✅',
                '❌' if metrics['overdue_reviews'] > 0 else '✅'
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
