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
    page_title="Enterprise Risk Register",
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

    /* Risk level styling */
    .risk-critical { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .risk-high { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
    .risk-medium { background-color: rgba(255, 193, 7, 0.1); border-left: 4px solid #ffc107; }
    .risk-low { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

# Sample risk data
@st.cache_data
def load_risk_data():
    """Load sample enterprise risk register data"""
    risks = [
        # Critical Risks (Score 20-25)
        {"id": "R-007", "asset": "SQL Server", "description": "Audit logging disabled due to storage constraints", 
         "impact": 5, "likelihood": 5, "score": 25, "status": "Closed", "category": "Compliance", 
         "owner": "DBA Team", "review_date": "2024-03-15", "treatment": "Storage expansion completed"},
        
        {"id": "R-017", "asset": "Cloud Storage", "description": "Cloud storage buckets publicly accessible without restriction", 
         "impact": 4, "likelihood": 5, "score": 20, "status": "Open", "category": "Data Protection", 
         "owner": "Cloud Team", "review_date": "2024-02-28", "treatment": "Access controls implementation"},
        
        {"id": "R-018", "asset": "HR SaaS Platform", "description": "Incident response plan does not include platform-specific guidance", 
         "impact": 5, "likelihood": 4, "score": 20, "status": "Closed", "category": "Incident Response", 
         "owner": "Security Team", "review_date": "2024-01-20", "treatment": "Platform-specific procedures added"},
        
        {"id": "R-020", "asset": "Time Tracking System", "description": "Change management bypassed for emergency patches", 
         "impact": 5, "likelihood": 4, "score": 20, "status": "Closed", "category": "Change Management", 
         "owner": "IT Operations", "review_date": "2024-02-10", "treatment": "Emergency change procedures updated"},
        
        {"id": "R-023", "asset": "Legacy CRM", "description": "Compliance documentation incomplete for quarterly audit", 
         "impact": 5, "likelihood": 5, "score": 25, "status": "Open", "category": "Compliance", 
         "owner": "Compliance Team", "review_date": "2024-03-30", "treatment": "Documentation completion"},
        
        # High Risks (Score 12-19)
        {"id": "R-001", "asset": "IBM i", "description": "*ALLOBJ authority granted to test profile; no removal process", 
         "impact": 4, "likelihood": 3, "score": 12, "status": "Open", "category": "Access Control", 
         "owner": "IBM i Team", "review_date": "2024-03-01", "treatment": "Access review process implementation"},
        
        {"id": "R-003", "asset": "AIX LPARs", "description": "Adopted authority used by CL programs with no audit trail", 
         "impact": 3, "likelihood": 4, "score": 12, "status": "Accepted", "category": "Access Control", 
         "owner": "Unix Team", "review_date": "2024-02-15", "treatment": "Risk accepted with monitoring"},
        
        {"id": "R-008", "asset": "JD Edwards", "description": "No defined recovery point objectives (RPO) for system", 
         "impact": 3, "likelihood": 5, "score": 15, "status": "Accepted", "category": "Business Continuity", 
         "owner": "ERP Team", "review_date": "2024-04-01", "treatment": "RPO definition in progress"},
        
        {"id": "R-011", "asset": "Oracle DB", "description": "Backup verification logs missing or incomplete", 
         "impact": 3, "likelihood": 4, "score": 12, "status": "Mitigating", "category": "Data Protection", 
         "owner": "DBA Team", "review_date": "2024-02-28", "treatment": "Automated verification process"},
        
        {"id": "R-012", "asset": "VPN Gateway", "description": "Firewall rulebase allows unrestricted outbound traffic", 
         "impact": 5, "likelihood": 3, "score": 15, "status": "Open", "category": "Network Security", 
         "owner": "Network Team", "review_date": "2024-03-15", "treatment": "Traffic restriction implementation"},
        
        {"id": "R-013", "asset": "Backup Appliance", "description": "Local admin credentials stored in plaintext scripts", 
         "impact": 4, "likelihood": 4, "score": 16, "status": "Accepted", "category": "Access Control", 
         "owner": "Backup Team", "review_date": "2024-01-30", "treatment": "Credential management improvement"},
        
        {"id": "R-014", "asset": "SFTP Server", "description": "No MFA enabled for administrative access", 
         "impact": 4, "likelihood": 3, "score": 12, "status": "Open", "category": "Access Control", 
         "owner": "Infrastructure Team", "review_date": "2024-03-20", "treatment": "MFA implementation"},
        
        {"id": "R-015", "asset": "Email Gateway", "description": "Monitoring system lacks visibility into subsystem logs", 
         "impact": 5, "likelihood": 3, "score": 15, "status": "Closed", "category": "Monitoring", 
         "owner": "Security Team", "review_date": "2024-01-15", "treatment": "Enhanced monitoring implemented"},
        
        {"id": "R-016", "asset": "Firewall Cluster", "description": "Legacy protocol (telnet, SMBv1) still enabled", 
         "impact": 5, "likelihood": 3, "score": 15, "status": "Open", "category": "Network Security", 
         "owner": "Network Team", "review_date": "2024-03-10", "treatment": "Protocol updates"},
        
        {"id": "R-019", "asset": "Remote Desktop Server", "description": "No role-based access control (RBAC) implemented", 
         "impact": 4, "likelihood": 3, "score": 12, "status": "Mitigating", "category": "Access Control", 
         "owner": "Windows Team", "review_date": "2024-02-20", "treatment": "RBAC implementation"},
        
        {"id": "R-021", "asset": "MFA Provider", "description": "Privileged access not time-bound or session-recorded", 
         "impact": 3, "likelihood": 5, "score": 15, "status": "Open", "category": "Access Control", 
         "owner": "Security Team", "review_date": "2024-03-25", "treatment": "Session management enhancement"},
        
        {"id": "R-022", "asset": "Cloud IAM Portal", "description": "System clocks unsynchronized, affecting log correlation", 
         "impact": 5, "likelihood": 3, "score": 15, "status": "Open", "category": "Monitoring", 
         "owner": "Cloud Team", "review_date": "2024-02-25", "treatment": "Time synchronization"},
        
        # Medium Risks (Score 6-11)
        {"id": "R-002", "asset": "JD Edwards", "description": "IFS file share accessible with unauthenticated credentials", 
         "impact": 5, "likelihood": 2, "score": 10, "status": "Mitigating", "category": "Access Control", 
         "owner": "ERP Team", "review_date": "2024-03-05", "treatment": "Authentication implementation"},
        
        {"id": "R-004", "asset": "IBM i", "description": "No formal access review process in place", 
         "impact": 5, "likelihood": 2, "score": 10, "status": "Accepted", "category": "Access Control", 
         "owner": "IBM i Team", "review_date": "2024-04-05", "treatment": "Process development"},
        
        {"id": "R-005", "asset": "AIX LPARs", "description": "Service account uses shared credentials and has elevated access", 
         "impact": 3, "likelihood": 2, "score": 6, "status": "Closed", "category": "Access Control", 
         "owner": "Unix Team", "review_date": "2024-01-10", "treatment": "Individual accounts created"},
        
        {"id": "R-006", "asset": "Windows AD", "description": "Critical patches not applied within required SLA", 
         "impact": 3, "likelihood": 3, "score": 9, "status": "Open", "category": "Patch Management", 
         "owner": "Windows Team", "review_date": "2024-03-12", "treatment": "Patch management improvement"},
        
        {"id": "R-009", "asset": "Linux Web Server", "description": "Antivirus signature updates failing silently for 3+ weeks", 
         "impact": 4, "likelihood": 2, "score": 8, "status": "Closed", "category": "Malware Protection", 
         "owner": "Linux Team", "review_date": "2024-01-25", "treatment": "Update process fixed"},
        
        {"id": "R-010", "asset": "Citrix VDI", "description": "Manual process for deactivating terminated employees' accounts", 
         "impact": 4, "likelihood": 4, "score": 16, "status": "Closed", "category": "Access Control", 
         "owner": "Citrix Team", "review_date": "2024-02-05", "treatment": "Automated deactivation implemented"}
    ]
    
    df = pd.DataFrame(risks)
    df['review_date'] = pd.to_datetime(df['review_date'])
    return df

def calculate_risk_metrics(df):
    """Calculate key risk metrics"""
    total_risks = len(df)
    critical_risks = len(df[df['score'] >= 20])
    high_risks = len(df[(df['score'] >= 12) & (df['score'] < 20)])
    medium_risks = len(df[(df['score'] >= 6) & (df['score'] < 12)])
    low_risks = len(df[df['score'] < 6])
    
    open_risks = len(df[df['status'] == 'Open'])
    closed_risks = len(df[df['status'] == 'Closed'])
    accepted_risks = len(df[df['status'] == 'Accepted'])
    mitigating_risks = len(df[df['status'] == 'Mitigating'])
    
    avg_score = df['score'].mean()
    overdue_reviews = len(df[df['review_date'] < datetime.datetime.now()])
    
    return {
        'total_risks': total_risks,
        'critical_risks': critical_risks,
        'high_risks': high_risks,
        'medium_risks': medium_risks,
        'low_risks': low_risks,
        'open_risks': open_risks,
        'closed_risks': closed_risks,
        'accepted_risks': accepted_risks,
        'mitigating_risks': mitigating_risks,
        'avg_score': avg_score,
        'overdue_reviews': overdue_reviews
    }

def monte_carlo_simulation(df, simulations=10000):
    """Perform Monte Carlo simulation on risk scores"""
    # Create probability distributions for impact and likelihood
    impact_samples = np.random.choice([1, 2, 3, 4, 5], size=simulations, p=[0.1, 0.2, 0.3, 0.25, 0.15])
    likelihood_samples = np.random.choice([1, 2, 3, 4, 5], size=simulations, p=[0.15, 0.25, 0.3, 0.2, 0.1])
    
    # Calculate risk scores
    risk_scores = impact_samples * likelihood_samples
    
    # Calculate percentiles
    percentiles = np.percentile(risk_scores, [5, 25, 50, 75, 95])
    
    return risk_scores, percentiles

def main():
    st.markdown('<h1 class="main-header">Enterprise Risk Register</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_risk_data()
    metrics = calculate_risk_metrics(df)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Status filter
    status_filter = st.sidebar.multiselect(
        "Risk Status",
        options=df['status'].unique(),
        default=df['status'].unique()
    )
    
    # Category filter
    category_filter = st.sidebar.multiselect(
        "Risk Category",
        options=df['category'].unique(),
        default=df['category'].unique()
    )
    
    # Score range filter
    score_range = st.sidebar.slider(
        "Risk Score Range",
        min_value=int(df['score'].min()),
        max_value=int(df['score'].max()),
        value=(int(df['score'].min()), int(df['score'].max()))
    )
    
    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['category'].isin(category_filter)) &
        (df['score'] >= score_range[0]) &
        (df['score'] <= score_range[1])
    ]
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Risks", metrics['total_risks'])
        st.metric("Critical Risks", metrics['critical_risks'], delta=f"{metrics['critical_risks'] - 0}")
    
    with col2:
        st.metric("High Risks", metrics['high_risks'])
        st.metric("Open Risks", metrics['open_risks'], delta=f"{metrics['open_risks'] - 5}")
    
    with col3:
        st.metric("Average Score", f"{metrics['avg_score']:.1f}")
        st.metric("Overdue Reviews", metrics['overdue_reviews'], delta=f"{metrics['overdue_reviews'] - 0}")
    
    with col4:
        st.metric("Closed Risks", metrics['closed_risks'])
        st.metric("Risk Coverage", f"{(metrics['closed_risks'] + metrics['accepted_risks']) / metrics['total_risks'] * 100:.1f}%")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Risk Register", "📊 Analytics", "🎲 Monte Carlo", "📈 Trends", "⚙️ Risk Management"])
    
    with tab1:
        st.header("📋 Risk Register")
        
        # Risk register table
        st.dataframe(
            filtered_df[['id', 'asset', 'description', 'impact', 'likelihood', 'score', 'status', 'category', 'owner', 'review_date']],
            use_container_width=True,
            hide_index=True
        )
        
        # Risk details expander
        with st.expander("🔍 Risk Details"):
            selected_risk = st.selectbox("Select Risk", filtered_df['id'].tolist())
            risk_data = filtered_df[filtered_df['id'] == selected_risk].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Asset:** {risk_data['asset']}")
                st.write(f"**Category:** {risk_data['category']}")
                st.write(f"**Owner:** {risk_data['owner']}")
                st.write(f"**Review Date:** {risk_data['review_date'].strftime('%Y-%m-%d')}")
            
            with col2:
                st.write(f"**Impact:** {risk_data['impact']}/5")
                st.write(f"**Likelihood:** {risk_data['likelihood']}/5")
                st.write(f"**Risk Score:** {risk_data['score']}")
                st.write(f"**Status:** {risk_data['status']}")
            
            st.write(f"**Description:** {risk_data['description']}")
            st.write(f"**Treatment:** {risk_data['treatment']}")
    
    with tab2:
        st.header("📊 Risk Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk distribution by score
            fig_score = px.histogram(
                filtered_df, 
                x='score', 
                nbins=10,
                title="Risk Score Distribution",
                labels={'score': 'Risk Score', 'count': 'Number of Risks'}
            )
            st.plotly_chart(fig_score, use_container_width=True)
            
            # Risk by category
            category_counts = filtered_df['category'].value_counts()
            fig_category = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Risks by Category"
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            # Risk by status
            status_counts = filtered_df['status'].value_counts()
            fig_status = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Risks by Status",
                labels={'x': 'Status', 'y': 'Number of Risks'}
            )
            st.plotly_chart(fig_status, use_container_width=True)
            
            # Risk by asset
            asset_counts = filtered_df['asset'].value_counts().head(10)
            fig_asset = px.bar(
                x=asset_counts.index,
                y=asset_counts.values,
                title="Top 10 Assets by Risk Count",
                labels={'x': 'Asset', 'y': 'Number of Risks'}
            )
            fig_asset.update_xaxes(tickangle=45)
            st.plotly_chart(fig_asset, use_container_width=True)
    
    with tab3:
        st.header("🎲 Monte Carlo Risk Simulation")
        
        st.write("This simulation models risk score distributions using Monte Carlo methods to understand potential risk scenarios.")
        
        # Simulation parameters
        col1, col2 = st.columns(2)
        
        with col1:
            simulations = st.slider("Number of Simulations", 1000, 50000, 10000)
            st.write(f"Running {simulations:,} simulations...")
        
        with col2:
            if st.button("🔄 Run Simulation"):
                with st.spinner("Running Monte Carlo simulation..."):
                    risk_scores, percentiles = monte_carlo_simulation(filtered_df, simulations)
                    
                    # Display results
                    st.subheader("Simulation Results")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("5th Percentile", f"{percentiles[0]:.1f}")
                    with col2:
                        st.metric("25th Percentile", f"{percentiles[1]:.1f}")
                    with col3:
                        st.metric("Median", f"{percentiles[2]:.1f}")
                    with col4:
                        st.metric("75th Percentile", f"{percentiles[3]:.1f}")
                    with col5:
                        st.metric("95th Percentile", f"{percentiles[4]:.1f}")
                    
                    # Histogram of simulation results
                    fig_sim = px.histogram(
                        x=risk_scores,
                        nbins=50,
                        title="Monte Carlo Simulation Results",
                        labels={'x': 'Risk Score', 'y': 'Frequency'}
                    )
                    fig_sim.add_vline(x=percentiles[2], line_dash="dash", line_color="red", annotation_text="Median")
                    st.plotly_chart(fig_sim, use_container_width=True)
                    
                    # Risk level analysis
                    critical_count = np.sum(risk_scores >= 20)
                    high_count = np.sum((risk_scores >= 12) & (risk_scores < 20))
                    medium_count = np.sum((risk_scores >= 6) & (risk_scores < 12))
                    low_count = np.sum(risk_scores < 6)
                    
                    st.subheader("Simulated Risk Level Distribution")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Critical", f"{critical_count:,}", f"{critical_count/simulations*100:.1f}%")
                    with col2:
                        st.metric("High", f"{high_count:,}", f"{high_count/simulations*100:.1f}%")
                    with col3:
                        st.metric("Medium", f"{medium_count:,}", f"{medium_count/simulations*100:.1f}%")
                    with col4:
                        st.metric("Low", f"{low_count:,}", f"{low_count/simulations*100:.1f}%")
    
    with tab4:
        st.header("📈 Risk Trends & Forecasting")
        
        # Simulate trend data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        trend_data = []
        
        for date in dates:
            # Simulate monthly risk counts with some trend
            base_count = 23
            trend_factor = 1 + (date.month - 1) * 0.05  # Slight upward trend
            noise = np.random.normal(0, 2)
            risk_count = max(0, int(base_count * trend_factor + noise))
            
            trend_data.append({
                'date': date,
                'total_risks': risk_count,
                'open_risks': int(risk_count * 0.4),
                'closed_risks': int(risk_count * 0.35),
                'avg_score': 13.8 + np.random.normal(0, 1)
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        # Trend charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_trend = px.line(
                trend_df,
                x='date',
                y=['total_risks', 'open_risks', 'closed_risks'],
                title="Risk Count Trends",
                labels={'value': 'Number of Risks', 'variable': 'Risk Type'}
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            fig_score_trend = px.line(
                trend_df,
                x='date',
                y='avg_score',
                title="Average Risk Score Trend",
                labels={'avg_score': 'Average Risk Score'}
            )
            st.plotly_chart(fig_score_trend, use_container_width=True)
        
        # Forecasting
        st.subheader("🔮 Risk Forecasting")
        
        # Simple forecasting model
        if st.button("📊 Generate Forecast"):
            # Simulate future months
            future_dates = pd.date_range(start='2025-01-01', end='2025-06-30', freq='M')
            forecast_data = []
            
            for date in future_dates:
                # Extend trend with some uncertainty
                base_count = 23
                trend_factor = 1 + (date.month + 11) * 0.05
                uncertainty = np.random.normal(0, 3)
                risk_count = max(0, int(base_count * trend_factor + uncertainty))
                
                forecast_data.append({
                    'date': date,
                    'total_risks': risk_count,
                    'forecast': True
                })
            
            forecast_df = pd.DataFrame(forecast_data)
            
            # Combine historical and forecast
            historical = trend_df[['date', 'total_risks']].copy()
            historical['forecast'] = False
            combined_df = pd.concat([historical, forecast_df])
            
            fig_forecast = px.line(
                combined_df,
                x='date',
                y='total_risks',
                color='forecast',
                title="Risk Count Forecast (Next 6 Months)",
                labels={'total_risks': 'Number of Risks'}
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
    
    with tab5:
        st.header("⚙️ Risk Management Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Risk Treatment Planning")
            
            # Risk treatment status
            treatment_status = filtered_df['status'].value_counts()
            fig_treatment = px.pie(
                values=treatment_status.values,
                names=treatment_status.index,
                title="Risk Treatment Status"
            )
            st.plotly_chart(fig_treatment, use_container_width=True)
            
            # Treatment recommendations
            st.subheader("📋 Treatment Recommendations")
            
            open_risks = filtered_df[filtered_df['status'] == 'Open'].sort_values('score', ascending=False)
            
            for _, risk in open_risks.head(5).iterrows():
                with st.expander(f"{risk['id']}: {risk['asset']} (Score: {risk['score']})"):
                    st.write(f"**Description:** {risk['description']}")
                    st.write(f"**Recommended Action:** {risk['treatment']}")
                    st.write(f"**Owner:** {risk['owner']}")
                    st.write(f"**Review Date:** {risk['review_date'].strftime('%Y-%m-%d')}")
        
        with col2:
            st.subheader("📊 Risk Metrics Dashboard")
            
            # Key Risk Indicators
            st.write("**Key Risk Indicators (KRIs):**")
            
            kri_data = {
                'Metric': ['Total Risks', 'Critical Risks', 'High Risks', 'Average Score', 'Open Risks', 'Overdue Reviews'],
                'Current': [str(metrics['total_risks']), str(metrics['critical_risks']), str(metrics['high_risks']), 
                           f"{metrics['avg_score']:.1f}", str(metrics['open_risks']), str(metrics['overdue_reviews'])],
                'Target': ['<30', '0', '<5', '<10', '<5', '0'],
                'Status': ['✅', '❌', '❌', '❌', '❌', '❌']
            }
            
            kri_df = pd.DataFrame(kri_data)
            st.dataframe(kri_df, use_container_width=True, hide_index=True)
            
            # Risk owner accountability
            st.subheader("👥 Risk Owner Accountability")
            owner_counts = filtered_df['owner'].value_counts()
            fig_owner = px.bar(
                x=owner_counts.index,
                y=owner_counts.values,
                title="Risks by Owner",
                labels={'x': 'Owner', 'y': 'Number of Risks'}
            )
            fig_owner.update_xaxes(tickangle=45)
            st.plotly_chart(fig_owner, use_container_width=True)

if __name__ == "__main__":
    main()
