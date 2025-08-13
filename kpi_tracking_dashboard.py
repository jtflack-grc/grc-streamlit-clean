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
    page_title="KPI Tracking Dashboard",
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

    /* KPI status styling */
    .status-on-track { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
    .status-at-risk { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
    .status-off-track { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .trend-improving { color: #4caf50; }
    .trend-stable { color: #2196f3; }
    .trend-declining { color: #f44336; }
</style>
""", unsafe_allow_html=True)

# Sample KPI data
@st.cache_data
def load_kpi_data():
    """Load sample KPI data"""
    kpis = [
        {
            "kpi_id": "KPI-001",
            "name": "Overall Compliance Rate",
            "category": "Compliance",
            "description": "Percentage of controls meeting compliance requirements",
            "target_value": 80.0,
            "current_value": 67.5,
            "unit": "%",
            "frequency": "Monthly",
            "owner": "CISO",
            "status": "At Risk",
            "trend": "Improving",
            "last_updated": "2024-01-15",
            "historical_data": [65.2, 66.1, 66.8, 67.2, 67.5]
        },
        {
            "kpi_id": "KPI-002",
            "name": "Incident Response Time",
            "category": "Security",
            "description": "Average time to detect and respond to security incidents",
            "target_value": 4.0,
            "current_value": 2.3,
            "unit": "hours",
            "frequency": "Weekly",
            "owner": "Security Operations",
            "status": "On Track",
            "trend": "Improving",
            "last_updated": "2024-01-14",
            "historical_data": [3.2, 2.8, 2.5, 2.4, 2.3]
        },
        {
            "kpi_id": "KPI-003",
            "name": "Risk Assessment Completion",
            "category": "Risk",
            "description": "Percentage of planned risk assessments completed on time",
            "target_value": 90.0,
            "current_value": 85.0,
            "unit": "%",
            "frequency": "Quarterly",
            "owner": "Risk Management",
            "status": "At Risk",
            "trend": "Stable",
            "last_updated": "2024-01-10",
            "historical_data": [82.0, 83.5, 84.2, 84.8, 85.0]
        },
        {
            "kpi_id": "KPI-004",
            "name": "System Availability",
            "category": "Operations",
            "description": "Uptime percentage for critical business systems",
            "target_value": 99.5,
            "current_value": 99.8,
            "unit": "%",
            "frequency": "Daily",
            "owner": "IT Operations",
            "status": "On Track",
            "trend": "Stable",
            "last_updated": "2024-01-15",
            "historical_data": [99.7, 99.8, 99.8, 99.8, 99.8]
        },
        {
            "kpi_id": "KPI-005",
            "name": "Vendor Risk Assessment",
            "category": "Risk",
            "description": "Percentage of critical vendors with current risk assessments",
            "target_value": 95.0,
            "current_value": 78.0,
            "unit": "%",
            "frequency": "Monthly",
            "owner": "Vendor Management",
            "status": "Off Track",
            "trend": "Declining",
            "last_updated": "2024-01-12",
            "historical_data": [82.0, 80.5, 79.2, 78.8, 78.0]
        },
        {
            "kpi_id": "KPI-006",
            "name": "Training Completion Rate",
            "category": "Compliance",
            "description": "Percentage of employees completing required security training",
            "target_value": 95.0,
            "current_value": 92.5,
            "unit": "%",
            "frequency": "Quarterly",
            "owner": "HR Security",
            "status": "At Risk",
            "trend": "Improving",
            "last_updated": "2024-01-08",
            "historical_data": [89.0, 90.2, 91.5, 92.1, 92.5]
        },
        {
            "kpi_id": "KPI-007",
            "name": "Control Testing Schedule",
            "category": "Compliance",
            "description": "Percentage of controls tested according to schedule",
            "target_value": 100.0,
            "current_value": 88.0,
            "unit": "%",
            "frequency": "Monthly",
            "owner": "Internal Audit",
            "status": "At Risk",
            "trend": "Stable",
            "last_updated": "2024-01-13",
            "historical_data": [85.0, 86.5, 87.2, 87.8, 88.0]
        },
        {
            "kpi_id": "KPI-008",
            "name": "Security Incident Frequency",
            "category": "Security",
            "description": "Number of security incidents per month",
            "target_value": 5.0,
            "current_value": 3.0,
            "unit": "incidents",
            "frequency": "Monthly",
            "owner": "Security Operations",
            "status": "On Track",
            "trend": "Improving",
            "last_updated": "2024-01-15",
            "historical_data": [6.0, 5.5, 4.2, 3.5, 3.0]
        },
        {
            "kpi_id": "KPI-009",
            "name": "Audit Finding Closure",
            "category": "Compliance",
            "description": "Percentage of audit findings closed within 90 days",
            "target_value": 85.0,
            "current_value": 72.0,
            "unit": "%",
            "frequency": "Quarterly",
            "owner": "Compliance Team",
            "status": "Off Track",
            "trend": "Declining",
            "last_updated": "2024-01-05",
            "historical_data": [78.0, 76.5, 74.2, 73.1, 72.0]
        },
        {
            "kpi_id": "KPI-010",
            "name": "Data Breach Response Time",
            "category": "Security",
            "description": "Time to contain and remediate data breaches",
            "target_value": 24.0,
            "current_value": 18.5,
            "unit": "hours",
            "frequency": "Incident",
            "owner": "Incident Response",
            "status": "On Track",
            "trend": "Improving",
            "last_updated": "2024-01-11",
            "historical_data": [22.0, 21.2, 20.1, 19.3, 18.5]
        }
    ]
    
    df = pd.DataFrame(kpis)
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    return df

def calculate_kpi_metrics(df):
    """Calculate key KPI metrics"""
    metrics = {
        'total_kpis': len(df),
        'on_track_kpis': len(df[df['status'] == 'On Track']),
        'at_risk_kpis': len(df[df['status'] == 'At Risk']),
        'off_track_kpis': len(df[df['status'] == 'Off Track']),
        'improving_trends': len(df[df['trend'] == 'Improving']),
        'stable_trends': len(df[df['trend'] == 'Stable']),
        'declining_trends': len(df[df['trend'] == 'Declining']),
        'avg_performance': df['current_value'].mean(),
        'target_achievement': (df['current_value'] / df['target_value'] * 100).mean()
    }
    
    return metrics

def get_trend_color(trend):
    """Get color for trend indicators"""
    if trend == 'Improving':
        return '#388e3c'
    elif trend == 'Stable':
        return '#1976d2'
    else:
        return '#d32f2f'

def get_status_color(status):
    """Get color for status indicators"""
    if status == 'On Track':
        return '#388e3c'
    elif status == 'At Risk':
        return '#f57c00'
    else:
        return '#d32f2f'

def main():
    st.markdown('<h1 class="main-header">KPI Tracking Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_kpi_data()
    metrics = calculate_kpi_metrics(df)
    
    # Sidebar
    st.sidebar.header("📊 KPI Management")
    
    # Add new KPI form
    with st.sidebar.expander("➕ Add New KPI", expanded=False):
        with st.form("add_kpi"):
            col1, col2 = st.columns(2)
            
            with col1:
                kpi_id = st.text_input("KPI ID", placeholder="e.g., KPI-001")
                name = st.text_input("KPI Name", placeholder="e.g., Overall Compliance Rate")
                category = st.selectbox("Category", ["Security", "Compliance", "Risk", "Operations"])
                target_value = st.number_input("Target Value", min_value=0.0, value=80.0)
            
            with col2:
                current_value = st.number_input("Current Value", min_value=0.0, value=75.0)
                unit = st.text_input("Unit", placeholder="e.g., %")
                frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "Quarterly", "Annually"])
                owner = st.text_input("Owner", placeholder="e.g., CISO")
            
            status = st.selectbox("Status", ["On Track", "At Risk", "Off Track"])
            trend = st.selectbox("Trend", ["Improving", "Stable", "Declining"])
            description = st.text_area("Description", placeholder="Describe the KPI...")
            
            submitted = st.form_submit_button("Add KPI")
            if submitted:
                st.success("KPI added successfully!")
    
    # Filters
    st.sidebar.subheader("🔍 Filters")
    
    category_filter = st.sidebar.multiselect(
        "Category",
        df['category'].unique(),
        default=df['category'].unique()
    )
    
    status_filter = st.sidebar.multiselect(
        "Status",
        df['status'].unique(),
        default=df['status'].unique()
    )
    
    trend_filter = st.sidebar.multiselect(
        "Trend",
        df['trend'].unique(),
        default=df['trend'].unique()
    )
    
    # Apply filters
    filtered_df = df[
        (df['category'].isin(category_filter)) &
        (df['status'].isin(status_filter)) &
        (df['trend'].isin(trend_filter))
    ]
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📋 KPI List", "📈 Analytics", "🎯 Performance", "📋 Reports"])
    
    with tab1:
        st.header("📊 KPI Dashboard Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total KPIs", metrics['total_kpis'])
        
        with col2:
            st.metric("On Track", metrics['on_track_kpis'], f"{metrics['on_track_kpis']/metrics['total_kpis']*100:.1f}%")
        
        with col3:
            st.metric("At Risk", metrics['at_risk_kpis'], f"{metrics['at_risk_kpis']/metrics['total_kpis']*100:.1f}%")
        
        with col4:
            st.metric("Off Track", metrics['off_track_kpis'], f"{metrics['off_track_kpis']/metrics['total_kpis']*100:.1f}%")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            status_counts = df['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="KPI Status Distribution",
                color_discrete_map={
                    'On Track': '#388e3c',
                    'At Risk': '#f57c00',
                    'Off Track': '#d32f2f'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Category distribution
            category_counts = df['category'].value_counts()
            fig_category = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="KPIs by Category",
                labels={'x': 'Category', 'y': 'Count'},
                color=category_counts.index,
                color_discrete_map={
                    'Security': '#1976d2',
                    'Compliance': '#388e3c',
                    'Risk': '#f57c00',
                    'Operations': '#7b1fa2'
                }
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        # Performance vs Target
        st.subheader("🎯 Performance vs Target")
        
        # Calculate performance percentage
        df['performance_pct'] = (df['current_value'] / df['target_value'] * 100).clip(0, 150)
        
        fig_performance = px.scatter(
            df,
            x='target_value',
            y='current_value',
            color='status',
            size='performance_pct',
            hover_data=['name', 'owner'],
            title="Current vs Target Performance",
            labels={'target_value': 'Target Value', 'current_value': 'Current Value'},
            color_discrete_map={
                'On Track': '#388e3c',
                'At Risk': '#f57c00',
                'Off Track': '#d32f2f'
            }
        )
        
        # Add diagonal line for target
        max_val = max(df['target_value'].max(), df['current_value'].max())
        fig_performance.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name='Target Line',
                showlegend=False
            )
        )
        
        st.plotly_chart(fig_performance, use_container_width=True)
        
        # Trend analysis
        st.subheader("📈 Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            trend_counts = df['trend'].value_counts()
            fig_trend = px.pie(
                values=trend_counts.values,
                names=trend_counts.index,
                title="KPI Trends",
                color_discrete_map={
                    'Improving': '#388e3c',
                    'Stable': '#1976d2',
                    'Declining': '#d32f2f'
                }
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Performance by category
            category_performance = df.groupby('category')['performance_pct'].mean().reset_index()
            fig_cat_perf = px.bar(
                category_performance,
                x='category',
                y='performance_pct',
                title="Average Performance by Category",
                labels={'performance_pct': 'Performance (%)', 'category': 'Category'},
                color='category',
                color_discrete_map={
                    'Security': '#1976d2',
                    'Compliance': '#388e3c',
                    'Risk': '#f57c00',
                    'Operations': '#7b1fa2'
                }
            )
            fig_cat_perf.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target")
            st.plotly_chart(fig_cat_perf, use_container_width=True)
    
    with tab2:
        st.header("📋 KPI List")
        
        # Display filtered KPIs
        if len(filtered_df) > 0:
            # Format data for display
            display_df = filtered_df.copy()
            display_df['last_updated'] = display_df['last_updated'].dt.strftime('%Y-%m-%d')
            # Calculate performance percentage
            display_df['performance_pct'] = (display_df['current_value'] / display_df['target_value'] * 100).round(1)
            
            # Add status and trend indicators
            display_df['Status_Icon'] = display_df['status'].map({
                'On Track': '✅',
                'At Risk': '⚠️',
                'Off Track': '❌'
            })
            
            display_df['Trend_Icon'] = display_df['trend'].map({
                'Improving': '↗️',
                'Stable': '→',
                'Declining': '↘️'
            })
            
            st.dataframe(
                display_df[['kpi_id', 'name', 'category', 'current_value', 'target_value', 'unit', 
                           'performance_pct', 'status', 'trend', 'owner', 'last_updated']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No KPIs found matching the selected filters.")
    
    with tab3:
        st.header("📈 KPI Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Historical trend simulation
            st.subheader("📊 Historical Trends")
            
            # Simulate historical data for selected KPI
            if len(filtered_df) > 0:
                selected_kpi = st.selectbox(
                    "Select KPI for Historical View",
                    filtered_df['name'].tolist()
                )
                
                kpi_data = filtered_df[filtered_df['name'] == selected_kpi].iloc[0]
                
                # Generate historical data
                months = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']
                historical_values = kpi_data['historical_data']
                
                fig_history = px.line(
                    x=months,
                    y=historical_values,
                    title=f"Historical Trend: {selected_kpi}",
                    labels={'x': 'Month', 'y': f'Value ({kpi_data["unit"]})'}
                )
                fig_history.add_hline(y=kpi_data['target_value'], line_dash="dash", line_color="red", annotation_text="Target")
                st.plotly_chart(fig_history, use_container_width=True)
        
        with col2:
            # Performance heatmap
            st.subheader("🔥 Performance Heatmap")
            
            # Create performance matrix
            performance_matrix = df.pivot_table(
                values='performance_pct',
                index='category',
                columns='status',
                aggfunc='mean'
            ).fillna(0)
            
            fig_heatmap = px.imshow(
                performance_matrix,
                title="Performance by Category and Status",
                labels={'x': 'Status', 'y': 'Category'},
                color_continuous_scale='RdYlGn',
                aspect="auto"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Owner accountability
        st.subheader("👥 Owner Accountability")
        
        owner_performance = df.groupby('owner').agg({
            'performance_pct': 'mean',
            'kpi_id': 'count'
        }).reset_index()
        owner_performance.columns = ['Owner', 'Avg Performance (%)', 'KPI Count']
        
        fig_owner = px.scatter(
            owner_performance,
            x='Avg Performance (%)',
            y='KPI Count',
            size='KPI Count',
            color='Owner',
            hover_data=['Owner'],
            title="Owner Performance Overview"
        )
        fig_owner.add_vline(x=100, line_dash="dash", line_color="red", annotation_text="Target")
        st.plotly_chart(fig_owner, use_container_width=True)
        
        # Frequency analysis
        st.subheader("📅 Frequency Analysis")
        
        frequency_counts = df['frequency'].value_counts()
        fig_frequency = px.bar(
            x=frequency_counts.index,
            y=frequency_counts.values,
            title="KPIs by Tracking Frequency",
            labels={'x': 'Frequency', 'y': 'Count'}
        )
        st.plotly_chart(fig_frequency, use_container_width=True)
    
    with tab4:
        st.header("🎯 Performance Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance summary
            st.subheader("📊 Performance Summary")
            
            summary_data = {
                'Metric': [
                    'Total KPIs',
                    'On Track',
                    'At Risk',
                    'Off Track',
                    'Improving Trends',
                    'Stable Trends',
                    'Declining Trends',
                    'Average Performance',
                    'Target Achievement'
                ],
                'Value': [
                    str(metrics['total_kpis']),
                    str(metrics['on_track_kpis']),
                    str(metrics['at_risk_kpis']),
                    str(metrics['off_track_kpis']),
                    str(metrics['improving_trends']),
                    str(metrics['stable_trends']),
                    str(metrics['declining_trends']),
                    f"{metrics['avg_performance']:.1f}",
                    f"{metrics['target_achievement']:.1f}%"
                ],
                'Status': [
                    '✅' if metrics['total_kpis'] > 0 else '❌',
                    '✅' if metrics['on_track_kpis'] > metrics['total_kpis'] * 0.7 else '⚠️',
                    '⚠️' if metrics['at_risk_kpis'] > 0 else '✅',
                    '❌' if metrics['off_track_kpis'] > 0 else '✅',
                    '✅' if metrics['improving_trends'] > metrics['total_kpis'] * 0.5 else '⚠️',
                    '⚠️' if metrics['stable_trends'] > metrics['total_kpis'] * 0.3 else '✅',
                    '❌' if metrics['declining_trends'] > 0 else '✅',
                    '✅' if metrics['avg_performance'] > 80 else '⚠️',
                    '✅' if metrics['target_achievement'] > 90 else '⚠️'
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        with col2:
            # Action items
            st.subheader("⚡ Action Items")
            
            # Identify KPIs needing attention
            attention_kpis = df[df['status'].isin(['At Risk', 'Off Track'])]
            
            if len(attention_kpis) > 0:
                st.write("**KPIs Requiring Attention:**")
                for _, kpi in attention_kpis.iterrows():
                    st.write(f"• **{kpi['name']}** ({kpi['owner']}) - {kpi['status']}")
            else:
                st.success("All KPIs are on track!")
            
            # Management actions
            st.subheader("⚙️ Management Actions")
            
            if st.button("🔄 Refresh Data"):
                st.rerun()
            
            if st.button("📧 Send Alerts"):
                st.success("Alerts sent to KPI owners!")
            
            if st.button("📅 Schedule Reviews"):
                st.success("Review schedule updated!")
        
        # Performance improvement opportunities
        st.subheader("🚀 Improvement Opportunities")
        
        # Find KPIs with declining trends
        declining_kpis = df[df['trend'] == 'Declining']
        
        if len(declining_kpis) > 0:
            st.write("**KPIs with Declining Trends:**")
            
            for _, kpi in declining_kpis.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{kpi['name']}** - {kpi['description']}")
                
                with col2:
                    st.write(f"Owner: {kpi['owner']}")
                
                with col3:
                    if st.button(f"📝 Action Plan", key=f"action_{kpi['kpi_id']}"):
                        st.success(f"Action plan created for {kpi['name']}!")
        else:
            st.success("No KPIs with declining trends!")
    
    with tab5:
        st.header("📋 Reports & Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export options
            st.subheader("📤 Export Options")
            
            if st.button("📊 Export to Excel"):
                st.success("KPI report exported to Excel successfully!")
            
            if st.button("📈 Generate Executive Summary"):
                st.success("Executive summary generated!")
            
            if st.button("📋 Export Performance Report"):
                st.success("Performance report exported!")
            
            if st.button("📊 Generate Dashboard PDF"):
                st.success("Dashboard PDF generated!")
        
        with col2:
            # Report scheduling
            st.subheader("📅 Report Scheduling")
            
            report_frequency = st.selectbox("Report Frequency", ["Daily", "Weekly", "Monthly", "Quarterly"])
            report_type = st.selectbox("Report Type", ["Executive Summary", "Detailed Analysis", "Performance Review", "Trend Analysis"])
            
            if st.button("📅 Schedule Report"):
                st.success(f"{report_type} scheduled for {report_frequency} delivery!")
        
        # Executive dashboard
        st.subheader("👔 Executive Dashboard")
        
        # Key executive metrics
        exec_metrics = {
            'Metric': [
                'Overall Performance Score',
                'Risk Exposure Level',
                'Compliance Status',
                'Security Posture',
                'Operational Efficiency'
            ],
            'Current': [
                f"{metrics['target_achievement']:.1f}%",
                'Medium' if metrics['at_risk_kpis'] + metrics['off_track_kpis'] > 3 else 'Low',
                'Compliant' if metrics['on_track_kpis'] > metrics['total_kpis'] * 0.8 else 'At Risk',
                'Strong' if metrics['improving_trends'] > metrics['total_kpis'] * 0.6 else 'Improving',
                'High' if metrics['avg_performance'] > 85 else 'Medium'
            ],
            'Target': [
                '>90%',
                'Low',
                'Compliant',
                'Strong',
                'High'
            ],
            'Status': [
                '✅' if metrics['target_achievement'] > 90 else '⚠️',
                '✅' if metrics['at_risk_kpis'] + metrics['off_track_kpis'] <= 3 else '⚠️',
                '✅' if metrics['on_track_kpis'] > metrics['total_kpis'] * 0.8 else '⚠️',
                '✅' if metrics['improving_trends'] > metrics['total_kpis'] * 0.6 else '⚠️',
                '✅' if metrics['avg_performance'] > 85 else '⚠️'
            ]
        }
        
        exec_df = pd.DataFrame(exec_metrics)
        st.dataframe(exec_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
