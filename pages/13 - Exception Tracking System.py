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
    page_title="Exception Tracking System · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)



# Sample exception data
@st.cache_data
def load_exception_data():
    """Load sample exception tracking data"""
    exceptions = [
        {
            "exception_id": "EX-001",
            "system_asset": "IBM i",
            "description": "MFA not implemented due to application compatibility issues",
            "compensating_control": "None",
            "expiration_date": "2025-06-13",
            "risk_accepted": False,
            "status": "Approved",
            "category": "Technical",
            "owner": "IT Security Team",
            "created_date": "2024-01-15",
            "risk_score": 85,
            "business_impact": "High",
            "approval_level": "CISO",
            "review_frequency": "Monthly"
        },
        {
            "exception_id": "EX-002",
            "system_asset": "Citrix VDI",
            "description": "Access review postponed due to staffing limitations",
            "compensating_control": "None",
            "expiration_date": "2025-06-25",
            "risk_accepted": False,
            "status": "Expired",
            "category": "Operational",
            "owner": "IT Operations",
            "created_date": "2024-02-01",
            "risk_score": 65,
            "business_impact": "Medium",
            "approval_level": "IT Manager",
            "review_frequency": "Quarterly"
        },
        {
            "exception_id": "EX-003",
            "system_asset": "Oracle DB",
            "description": "Audit logging disabled temporarily for performance tuning",
            "compensating_control": "None",
            "expiration_date": "2025-07-22",
            "risk_accepted": False,
            "status": "Open",
            "category": "Technical",
            "owner": "Database Team",
            "created_date": "2024-03-10",
            "risk_score": 75,
            "business_impact": "High",
            "approval_level": "CISO",
            "review_frequency": "Weekly"
        },
        {
            "exception_id": "EX-004",
            "system_asset": "VPN Gateway",
            "description": "Legacy OS version unsupported by endpoint protection software",
            "compensating_control": "Manual log review weekly",
            "expiration_date": "2025-07-31",
            "risk_accepted": True,
            "status": "Open",
            "category": "Technical",
            "owner": "Network Team",
            "created_date": "2024-01-20",
            "risk_score": 70,
            "business_impact": "Medium",
            "approval_level": "IT Director",
            "review_frequency": "Monthly"
        },
        {
            "exception_id": "EX-005",
            "system_asset": "Time Tracking System",
            "description": "Privileged account has permanent access due to operational constraints",
            "compensating_control": "Manual log review weekly",
            "expiration_date": "2025-08-19",
            "risk_accepted": True,
            "status": "Under Review",
            "category": "Operational",
            "owner": "HR IT Team",
            "created_date": "2024-02-15",
            "risk_score": 80,
            "business_impact": "High",
            "approval_level": "CISO",
            "review_frequency": "Weekly"
        },
        {
            "exception_id": "EX-006",
            "system_asset": "Cloud IAM Portal",
            "description": "Firewall exceptions granted to vendor-controlled IP range",
            "compensating_control": "Manual log review weekly",
            "expiration_date": "2025-08-06",
            "risk_accepted": True,
            "status": "Open",
            "category": "Technical",
            "owner": "Cloud Team",
            "created_date": "2024-03-01",
            "risk_score": 60,
            "business_impact": "Medium",
            "approval_level": "IT Director",
            "review_frequency": "Monthly"
        },
        {
            "exception_id": "EX-007",
            "system_asset": "Backup Appliance",
            "description": "Critical patch delayed pending vendor validation",
            "compensating_control": "None",
            "expiration_date": "2025-06-13",
            "risk_accepted": False,
            "status": "Open",
            "category": "Technical",
            "owner": "Infrastructure Team",
            "created_date": "2024-01-25",
            "risk_score": 90,
            "business_impact": "Critical",
            "approval_level": "CISO",
            "review_frequency": "Daily"
        },
        {
            "exception_id": "EX-008",
            "system_asset": "Linux Web Server",
            "description": "Monitoring tools excluded due to licensing limits",
            "compensating_control": "None",
            "expiration_date": "2025-07-16",
            "risk_accepted": False,
            "status": "Approved",
            "category": "Technical",
            "owner": "Web Team",
            "created_date": "2024-02-10",
            "risk_score": 55,
            "business_impact": "Low",
            "approval_level": "IT Manager",
            "review_frequency": "Monthly"
        },
        {
            "exception_id": "EX-009",
            "system_asset": "Legacy CRM",
            "description": "Unsupported protocol (SMBv1) still required by legacy application",
            "compensating_control": "Manual log review weekly",
            "expiration_date": "2025-10-08",
            "risk_accepted": True,
            "status": "Under Review",
            "category": "Technical",
            "owner": "Business Systems",
            "created_date": "2024-01-30",
            "risk_score": 85,
            "business_impact": "High",
            "approval_level": "CISO",
            "review_frequency": "Weekly"
        },
        {
            "exception_id": "EX-010",
            "system_asset": "Wireless Controllers",
            "description": "Automated backup encryption paused due to failed script recovery",
            "compensating_control": "Manual log review weekly",
            "expiration_date": "2025-09-17",
            "risk_accepted": True,
            "status": "Open",
            "category": "Technical",
            "owner": "Network Team",
            "created_date": "2024-03-05",
            "risk_score": 70,
            "business_impact": "Medium",
            "approval_level": "IT Director",
            "review_frequency": "Monthly"
        }
    ]
    
    df = pd.DataFrame(exceptions)
    df['expiration_date'] = pd.to_datetime(df['expiration_date'])
    df['created_date'] = pd.to_datetime(df['created_date'])
    return df

def calculate_exception_metrics(df):
    """Calculate key exception metrics"""
    today = datetime.datetime.now()
    
    metrics = {
        'total_exceptions': len(df),
        'open_exceptions': len(df[df['status'] == 'Open']),
        'under_review': len(df[df['status'] == 'Under Review']),
        'approved_exceptions': len(df[df['status'] == 'Approved']),
        'expired_exceptions': len(df[df['status'] == 'Expired']),
        'risk_accepted': len(df[df['risk_accepted'] == True]),
        'expiring_soon': len(df[(df['expiration_date'] - today).dt.days <= 30]),
        'overdue_reviews': len(df[(df['expiration_date'] - today).dt.days < 0]),
        'avg_risk_score': df['risk_score'].mean(),
        'critical_exceptions': len(df[df['business_impact'] == 'Critical'])
    }
    
    return metrics

def main():
    portfolio_skin.page_header(
        title="Exception Tracking System",
        lede="Interactive GRC tool — #RUNGRCRaleigh build-in-public.",
        kicker="Controls",
    )
    
    # Load data
    df = load_exception_data()
    metrics = calculate_exception_metrics(df)
    
    # Sidebar
    st.sidebar.header("Controls")
    seed = demo_kit.seed_controls()
    st.sidebar.markdown("---")
    st.sidebar.subheader("Exception Management")
    
    # Add new exception form
    with st.sidebar.expander("Add New Exception", expanded=False):
        with st.form("add_exception"):
            col1, col2 = st.columns(2)
            
            with col1:
                exception_id = st.text_input("Exception ID", placeholder="e.g., EX-001")
                system_asset = st.text_input("System/Asset", placeholder="e.g., IBM i")
                category = st.selectbox("Category", ["Technical", "Operational", "Compliance"])
                business_impact = st.selectbox("Business Impact", ["Low", "Medium", "High", "Critical"])
                risk_score = st.slider("Risk Score", 1, 100, 50)
            
            with col2:
                status = st.selectbox("Status", ["Open", "Under Review", "Approved", "Expired"])
                risk_accepted = st.checkbox("Risk Accepted")
                approval_level = st.selectbox("Approval Level", ["IT Manager", "IT Director", "CISO"])
                review_frequency = st.selectbox("Review Frequency", ["Daily", "Weekly", "Monthly", "Quarterly"])
            
            description = st.text_area("Description", placeholder="Describe the exception...")
            compensating_control = st.text_area("Compensating Control", placeholder="Describe compensating controls...")
            
            col1, col2 = st.columns(2)
            with col1:
                expiration_date = st.date_input("Expiration Date", value=datetime.date.today() + timedelta(days=90))
            with col2:
                owner = st.text_input("Owner", placeholder="e.g., IT Security Team")
            
            submitted = st.form_submit_button("Add Exception")
            if submitted:
                st.success("Exception added successfully!")
    
    # Filters
    st.sidebar.subheader("Filters")
    
    status_filter = st.sidebar.multiselect(
        "Status",
        df['status'].unique(),
        default=df['status'].unique()
    )
    
    category_filter = st.sidebar.multiselect(
        "Category",
        df['category'].unique(),
        default=df['category'].unique()
    )
    
    risk_accepted_filter = st.sidebar.multiselect(
        "Risk Accepted",
        df['risk_accepted'].unique(),
        default=df['risk_accepted'].unique()
    )
    
    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['category'].isin(category_filter)) &
        (df['risk_accepted'].isin(risk_accepted_filter))
    ]
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Exception List", "Risk Analysis", "Expiration Tracking", "Reports"])
    
    with tab1:
        st.header("Exception Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Exceptions", metrics['total_exceptions'])
        
        with col2:
            st.metric("Open Exceptions", metrics['open_exceptions'])
        
        with col3:
            st.metric("Expiring Soon (30 days)", metrics['expiring_soon'])
        
        with col4:
            st.metric("Overdue Reviews", metrics['overdue_reviews'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            status_counts = df['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Exception Status Distribution"
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Category distribution
            category_counts = df['category'].value_counts()
            fig_category = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="Exceptions by Category",
                labels={'x': 'Category', 'y': 'Count'}
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        # Risk score distribution
        fig_risk_dist = px.histogram(
            df,
            x='risk_score',
            title="Risk Score Distribution",
            labels={'risk_score': 'Risk Score', 'y': 'Count'},
            nbins=10
        )
        st.plotly_chart(fig_risk_dist, use_container_width=True)
        
        # Expiration timeline
        st.subheader("Expiration Timeline")
        
        # Calculate days to expiration
        today = datetime.datetime.now()
        df['days_to_expiration'] = (df['expiration_date'] - today).dt.days
        
        fig_timeline = px.scatter(
            df,
            x='days_to_expiration',
            y='risk_score',
            color='status',
            size='risk_score',
            hover_data=['exception_id', 'system_asset'],
            title="Exception Expiration Timeline",
            labels={'days_to_expiration': 'Days to Expiration', 'risk_score': 'Risk Score'}
        )
        fig_timeline.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Today")
        fig_timeline.add_vline(x=30, line_dash="dash", line_color="orange", annotation_text="30 Days")
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    with tab2:
        st.header("Exception List")
        
        # Display filtered exceptions
        if len(filtered_df) > 0:
            # Format data for display
            display_df = filtered_df.copy()
            display_df['expiration_date'] = display_df['expiration_date'].dt.strftime('%Y-%m-%d')
            display_df['created_date'] = display_df['created_date'].dt.strftime('%Y-%m-%d')
            display_df['risk_accepted'] = display_df['risk_accepted'].map({True: 'Yes', False: 'No'})
            
            st.dataframe(
                display_df[['exception_id', 'system_asset', 'description', 'status', 'risk_accepted', 'expiration_date', 'risk_score', 'owner']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No exceptions found matching the selected filters.")
    
    with tab3:
        st.header("Risk Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk score by category
            fig_risk_category = px.box(
                filtered_df,
                x='category',
                y='risk_score',
                title="Risk Score by Category",
                labels={'category': 'Category', 'risk_score': 'Risk Score'}
            )
            st.plotly_chart(fig_risk_category, use_container_width=True)
        
        with col2:
            # Risk acceptance analysis
            risk_acceptance_counts = filtered_df['risk_accepted'].value_counts()
            fig_risk_acceptance = px.pie(
                values=risk_acceptance_counts.values,
                names=risk_acceptance_counts.index.map({True: 'Accepted', False: 'Not Accepted'}),
                title="Risk Acceptance Distribution"
            )
            st.plotly_chart(fig_risk_acceptance, use_container_width=True)
        
        # High-risk exceptions
        st.subheader("High-Risk Exceptions (Score > 75)")
        high_risk_df = filtered_df[filtered_df['risk_score'] > 75]
        
        if len(high_risk_df) > 0:
            for _, exception in high_risk_df.iterrows():
                with st.expander(f"{exception['exception_id']} - {exception['system_asset']} (Score: {exception['risk_score']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {exception['description']}")
                        st.write(f"**Category:** {exception['category']}")
                        st.write(f"**Business Impact:** {exception['business_impact']}")
                        st.write(f"**Status:** {exception['status']}")
                    
                    with col2:
                        st.write(f"**Compensating Control:** {exception['compensating_control']}")
                        st.write(f"**Risk Accepted:** {'Yes' if exception['risk_accepted'] else 'No'}")
                        st.write(f"**Expiration:** {exception['expiration_date'].strftime('%Y-%m-%d')}")
                        st.write(f"**Owner:** {exception['owner']}")
        else:
            st.info("No high-risk exceptions found.")
    
    with tab4:
        st.header("Expiration Tracking")
        
        # Calculate days to expiration
        today = datetime.datetime.now()
        filtered_df['days_to_expiration'] = (filtered_df['expiration_date'] - today).dt.days
        
        # Expiring soon (within 30 days)
        expiring_soon = filtered_df[filtered_df['days_to_expiration'] <= 30]
        
        if len(expiring_soon) > 0:
            st.subheader("Expiring Soon (Within 30 Days)")
            
            for _, exception in expiring_soon.iterrows():
                days_left = exception['days_to_expiration']
                color = "red" if days_left < 0 else "orange" if days_left <= 7 else "yellow"
                
                with st.expander(f"{exception['exception_id']} - {exception['system_asset']} ({days_left} days left)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {exception['description']}")
                        st.write(f"**Status:** {exception['status']}")
                        st.write(f"**Risk Score:** {exception['risk_score']}")
                    
                    with col2:
                        st.write(f"**Expiration Date:** {exception['expiration_date'].strftime('%Y-%m-%d')}")
                        st.write(f"**Owner:** {exception['owner']}")
                        st.write(f"**Review Frequency:** {exception['review_frequency']}")
                    
                    if st.button(f"Extend {exception['exception_id']}", key=f"extend_{exception['exception_id']}"):
                        st.success(f"Exception {exception['exception_id']} extended by 30 days!")
        else:
            st.success("No exceptions expiring within 30 days.")
        
        # Expiration trend
        st.subheader("Expiration Trend")
        
        # Group by month
        monthly_expirations = filtered_df.groupby(filtered_df['expiration_date'].dt.to_period('M')).size()
        
        fig_trend = px.line(
            x=monthly_expirations.index.astype(str),
            y=monthly_expirations.values,
            title="Monthly Exception Expirations",
            labels={'x': 'Month', 'y': 'Number of Expirations'}
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab5:
        st.header("Reports & Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Export Options")
            export_df = filtered_df.copy()
            for col in ("expiration_date", "created_date"):
                if col in export_df.columns:
                    export_df[col] = export_df[col].astype(str)
            demo_kit.csv_download(
                export_df,
                "exceptions_filtered.csv",
                label="Download filtered exceptions",
            )
        
        with col2:
            # Management actions
            st.subheader("Management Actions")
            
            if st.button("Refresh Data"):
                st.rerun()
            
            if st.button("Send Expiration Notifications"):
                st.success("Expiration notifications sent!")
            
            if st.button("Schedule Reviews"):
                st.success("Review schedule updated!")
        
        # Summary statistics
        st.subheader("Summary Statistics")
        
        summary_data = {
            'Metric': [
                'Total Exceptions',
                'Open Exceptions',
                'Under Review',
                'Approved',
                'Expired',
                'Risk Accepted',
                'Expiring Soon',
                'Overdue Reviews',
                'Average Risk Score',
                'Critical Exceptions'
            ],
            'Value': [
                str(metrics['total_exceptions']),
                str(metrics['open_exceptions']),
                str(metrics['under_review']),
                str(metrics['approved_exceptions']),
                str(metrics['expired_exceptions']),
                str(metrics['risk_accepted']),
                str(metrics['expiring_soon']),
                str(metrics['overdue_reviews']),
                f"{metrics['avg_risk_score']:.1f}",
                str(metrics['critical_exceptions'])
            ],
            'Status': [
                '' if metrics['total_exceptions'] > 0 else '',
                '' if metrics['open_exceptions'] > 0 else '',
                '' if metrics['under_review'] > 0 else '',
                '' if metrics['approved_exceptions'] > 0 else '',
                '' if metrics['expired_exceptions'] > 0 else '',
                '' if metrics['risk_accepted'] > 0 else '',
                '' if metrics['expiring_soon'] > 0 else '',
                '' if metrics['overdue_reviews'] > 0 else '',
                '' if metrics['avg_risk_score'] <= 70 else '',
                '' if metrics['critical_exceptions'] > 0 else ''
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
