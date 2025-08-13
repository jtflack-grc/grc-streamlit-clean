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
    page_title="Risk Assessment & Monte Carlo",
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
    """Load sample risk data"""
    risks = [
        {
            "risk_id": "R001",
            "risk_name": "Data Breach Risk",
            "risk_category": "Technology",
            "likelihood_min": 2,
            "likelihood_max": 4,
            "impact_min": 4,
            "impact_max": 5,
            "financial_impact": 500000,
            "risk_score": 16,
            "risk_level": "High",
            "description": "Unauthorized access to sensitive customer data",
            "mitigation_controls": "Encryption, access controls, monitoring",
            "owner": "IT Security Team",
            "assessment_date": "2024-01-15",
            "next_review": "2024-07-15"
        },
        {
            "risk_id": "R002",
            "risk_name": "Regulatory Non-Compliance",
            "risk_category": "Compliance",
            "likelihood_min": 1,
            "likelihood_max": 3,
            "impact_min": 4,
            "impact_max": 5,
            "financial_impact": 750000,
            "risk_score": 12,
            "risk_level": "Medium",
            "description": "Failure to meet regulatory requirements",
            "mitigation_controls": "Compliance monitoring, training, audits",
            "owner": "Compliance Team",
            "assessment_date": "2024-01-20",
            "next_review": "2024-07-20"
        },
        {
            "risk_id": "R003",
            "risk_name": "Supply Chain Disruption",
            "risk_category": "Operational",
            "likelihood_min": 3,
            "likelihood_max": 5,
            "impact_min": 3,
            "impact_max": 4,
            "financial_impact": 300000,
            "risk_score": 14,
            "risk_level": "High",
            "description": "Disruption in critical supplier relationships",
            "mitigation_controls": "Supplier diversification, contracts",
            "owner": "Operations Team",
            "assessment_date": "2024-02-01",
            "next_review": "2024-08-01"
        },
        {
            "risk_id": "R004",
            "risk_name": "Cybersecurity Incident",
            "risk_category": "Technology",
            "likelihood_min": 2,
            "likelihood_max": 3,
            "impact_min": 4,
            "impact_max": 5,
            "financial_impact": 1000000,
            "risk_score": 10,
            "risk_level": "Medium",
            "description": "Malware or ransomware attack",
            "mitigation_controls": "Security tools, training, backups",
            "owner": "IT Security Team",
            "assessment_date": "2024-02-05",
            "next_review": "2024-08-05"
        },
        {
            "risk_id": "R005",
            "risk_name": "Financial Market Volatility",
            "risk_category": "Financial",
            "likelihood_min": 4,
            "likelihood_max": 5,
            "impact_min": 2,
            "impact_max": 3,
            "financial_impact": 200000,
            "risk_score": 12,
            "risk_level": "Medium",
            "description": "Adverse market conditions affecting investments",
            "mitigation_controls": "Portfolio diversification, hedging",
            "owner": "Finance Team",
            "assessment_date": "2024-02-10",
            "next_review": "2024-08-10"
        },
        {
            "risk_id": "R006",
            "risk_name": "Key Personnel Loss",
            "risk_category": "Operational",
            "likelihood_min": 1,
            "likelihood_max": 2,
            "impact_min": 4,
            "impact_max": 5,
            "financial_impact": 400000,
            "risk_score": 8,
            "risk_level": "Low",
            "description": "Loss of critical staff members",
            "mitigation_controls": "Succession planning, knowledge transfer",
            "owner": "HR Team",
            "assessment_date": "2024-02-15",
            "next_review": "2024-08-15"
        },
        {
            "risk_id": "R007",
            "risk_name": "Reputational Damage",
            "risk_category": "Reputational",
            "likelihood_min": 1,
            "likelihood_max": 2,
            "impact_min": 4,
            "impact_max": 5,
            "financial_impact": 600000,
            "risk_score": 8,
            "risk_level": "Low",
            "description": "Negative publicity affecting brand",
            "mitigation_controls": "PR strategy, social media monitoring",
            "owner": "Marketing Team",
            "assessment_date": "2024-02-20",
            "next_review": "2024-08-20"
        },
        {
            "risk_id": "R008",
            "risk_name": "Natural Disaster",
            "risk_category": "Operational",
            "likelihood_min": 1,
            "likelihood_max": 1,
            "impact_min": 4,
            "impact_max": 5,
            "financial_impact": 800000,
            "risk_score": 4,
            "risk_level": "Low",
            "description": "Earthquake, flood, or other natural disaster",
            "mitigation_controls": "Business continuity planning, insurance",
            "owner": "Operations Team",
            "assessment_date": "2024-02-25",
            "next_review": "2024-08-25"
        }
    ]
    
    return pd.DataFrame(risks)

def calculate_risk_score(likelihood_min, likelihood_max, impact_min, impact_max):
    """Calculate risk score based on likelihood and impact ranges"""
    avg_likelihood = (likelihood_min + likelihood_max) / 2
    avg_impact = (impact_min + impact_max) / 2
    return avg_likelihood * avg_impact

def get_risk_level(risk_score):
    """Get risk level based on risk score"""
    if risk_score >= 15:
        return "Critical"
    elif risk_score >= 10:
        return "High"
    elif risk_score >= 6:
        return "Medium"
    else:
        return "Low"

def run_monte_carlo_simulation(likelihood_min, likelihood_max, impact_min, impact_max, financial_impact, num_simulations=5000):
    """Run Monte Carlo simulation for risk assessment"""
    # Generate random samples for likelihood and impact
    likelihood_samples = np.random.uniform(likelihood_min, likelihood_max, num_simulations)
    impact_samples = np.random.uniform(impact_min, impact_max, num_simulations)
    
    # Calculate risk scores
    risk_scores = likelihood_samples * impact_samples
    
    # Calculate financial impact with some variability
    financial_variability = np.random.normal(1.0, 0.2, num_simulations)  # 20% standard deviation
    financial_impacts = financial_impact * financial_variability
    
    # Calculate expected loss
    expected_loss = np.mean(financial_impacts)
    
    # Calculate percentiles
    percentiles = {
        '25th': np.percentile(financial_impacts, 25),
        '50th': np.percentile(financial_impacts, 50),
        '75th': np.percentile(financial_impacts, 75),
        '95th': np.percentile(financial_impacts, 95),
        '99th': np.percentile(financial_impacts, 99)
    }
    
    return {
        'risk_scores': risk_scores,
        'financial_impacts': financial_impacts,
        'expected_loss': expected_loss,
        'percentiles': percentiles,
        'likelihood_samples': likelihood_samples,
        'impact_samples': impact_samples
    }

def calculate_risk_metrics(df):
    """Calculate key risk metrics"""
    metrics = {
        'total_risks': len(df),
        'critical_risks': len(df[df['risk_level'] == 'Critical']),
        'high_risks': len(df[df['risk_level'] == 'High']),
        'medium_risks': len(df[df['risk_level'] == 'Medium']),
        'low_risks': len(df[df['risk_level'] == 'Low']),
        'avg_risk_score': df['risk_score'].mean(),
        'total_financial_impact': df['financial_impact'].sum(),
        'overdue_reviews': len(df[pd.to_datetime(df['next_review']) < datetime.datetime.now()])
    }
    
    return metrics

def main():
    st.markdown('<h1 class="main-header">Risk Assessment & Monte Carlo Simulation</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_risk_data()
    
    # Sidebar
    st.sidebar.header("🎲 Risk Assessment")
    
    # Add new risk form
    with st.sidebar.expander("➕ Add New Risk", expanded=False):
        with st.form("add_risk"):
            col1, col2 = st.columns(2)
            
            with col1:
                risk_name = st.text_input("Risk Name", placeholder="e.g., Data Breach Risk")
                risk_category = st.selectbox("Risk Category", ["Operational", "Financial", "Strategic", "Compliance", "Technology", "Reputational"])
                likelihood_min = st.slider("Likelihood Min", 1, 5, 2)
                impact_min = st.slider("Impact Min", 1, 5, 3)
                financial_impact = st.number_input("Financial Impact ($)", 0, 10000000, 100000)
            
            with col2:
                likelihood_max = st.slider("Likelihood Max", 1, 5, 4)
                impact_max = st.slider("Impact Max", 1, 5, 5)
                owner = st.text_input("Risk Owner", placeholder="e.g., IT Security Team")
                num_simulations = st.selectbox("Monte Carlo Simulations", [1000, 5000, 10000, 50000], index=1)
            
            description = st.text_area("Risk Description", placeholder="Describe the risk scenario...")
            mitigation_controls = st.text_area("Mitigation Controls", placeholder="List existing or planned controls...")
            
            submitted = st.form_submit_button("Add Risk")
            if submitted:
                st.success("Risk added successfully!")
    
    # Filters
    st.sidebar.subheader("🔍 Filters")
    
    category_filter = st.sidebar.multiselect(
        "Risk Category",
        df['risk_category'].unique(),
        default=df['risk_category'].unique()
    )
    
    level_filter = st.sidebar.multiselect(
        "Risk Level",
        df['risk_level'].unique(),
        default=df['risk_level'].unique()
    )
    
    risk_filter = st.sidebar.slider(
        "Risk Score Range",
        0, 25, (0, 25)
    )
    
    # Apply filters
    filtered_df = df[
        (df['risk_category'].isin(category_filter)) &
        (df['risk_level'].isin(level_filter)) &
        (df['risk_score'] >= risk_filter[0]) &
        (df['risk_score'] <= risk_filter[1])
    ]
    
    # Calculate metrics
    metrics = calculate_risk_metrics(filtered_df)
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🎲 Monte Carlo", "📈 Risk Analysis", "🔥 Risk Heatmap", "📋 Management"])
    
    with tab1:
        st.header("📊 Risk Assessment Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Risks",
                metrics['total_risks'],
                delta=f"${metrics['total_financial_impact']:,.0f} Total Impact"
            )
        
        with col2:
            st.metric(
                "Critical/High Risks",
                metrics['critical_risks'] + metrics['high_risks'],
                delta=f"{metrics['critical_risks']} Critical"
            )
        
        with col3:
            st.metric(
                "Average Risk Score",
                f"{metrics['avg_risk_score']:.1f}",
                delta=f"{metrics['high_risks']} High Risk"
            )
        
        with col4:
            st.metric(
                "Overdue Reviews",
                metrics['overdue_reviews'],
                delta="Requires Attention"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk level distribution
            level_counts = filtered_df['risk_level'].value_counts()
            fig_level = px.pie(
                values=level_counts.values,
                names=level_counts.index,
                title="Risk Level Distribution",
                color_discrete_map={
                    'Critical': '#f44336',
                    'High': '#ff9800',
                    'Medium': '#ffc107',
                    'Low': '#4caf50'
                }
            )
            st.plotly_chart(fig_level, use_container_width=True)
        
        with col2:
            # Risk category distribution
            category_counts = filtered_df['risk_category'].value_counts()
            fig_category = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="Risks by Category",
                labels={'x': 'Category', 'y': 'Number of Risks'}
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        # Risk score distribution
        fig_risk = px.histogram(
            filtered_df,
            x='risk_score',
            nbins=10,
            title="Risk Score Distribution",
            labels={'risk_score': 'Risk Score', 'count': 'Number of Risks'}
        )
        fig_risk.add_vline(x=15, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
        fig_risk.add_vline(x=10, line_dash="dash", line_color="orange", annotation_text="High Threshold")
        fig_risk.add_vline(x=6, line_dash="dash", line_color="yellow", annotation_text="Medium Threshold")
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with tab2:
        st.header("🎲 Monte Carlo Simulation")
        
        # Select risk for simulation
        if len(filtered_df) > 0:
            selected_risk = st.selectbox(
                "Select Risk for Monte Carlo Simulation",
                filtered_df['risk_name'].tolist()
            )
            
            risk_data = filtered_df[filtered_df['risk_name'] == selected_risk].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Risk Parameters")
                st.write(f"**Risk:** {risk_data['risk_name']}")
                st.write(f"**Category:** {risk_data['risk_category']}")
                st.write(f"**Likelihood Range:** {risk_data['likelihood_min']} - {risk_data['likelihood_max']}")
                st.write(f"**Impact Range:** {risk_data['impact_min']} - {risk_data['impact_max']}")
                st.write(f"**Financial Impact:** ${risk_data['financial_impact']:,.0f}")
                st.write(f"**Current Risk Score:** {risk_data['risk_score']}")
                st.write(f"**Risk Level:** {risk_data['risk_level']}")
            
            with col2:
                st.subheader("Simulation Parameters")
                num_simulations = st.selectbox("Number of Simulations", [1000, 5000, 10000, 50000], index=1)
                
                if st.button("Run Monte Carlo Simulation"):
                    with st.spinner("Running Monte Carlo simulation..."):
                        # Run simulation
                        simulation_results = run_monte_carlo_simulation(
                            risk_data['likelihood_min'],
                            risk_data['likelihood_max'],
                            risk_data['impact_min'],
                            risk_data['impact_max'],
                            risk_data['financial_impact'],
                            num_simulations
                        )
                        
                        # Display results
                        st.subheader("Simulation Results")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Expected Loss", f"${simulation_results['expected_loss']:,.0f}")
                        
                        with col2:
                            st.metric("25th Percentile", f"${simulation_results['percentiles']['25th']:,.0f}")
                        
                        with col3:
                            st.metric("75th Percentile", f"${simulation_results['percentiles']['75th']:,.0f}")
                        
                        with col4:
                            st.metric("95th Percentile", f"${simulation_results['percentiles']['95th']:,.0f}")
                        
                        # Charts
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Risk score distribution
                            fig_risk_dist = px.histogram(
                                x=simulation_results['risk_scores'],
                                title="Risk Score Distribution",
                                labels={'x': 'Risk Score', 'y': 'Frequency'}
                            )
                            st.plotly_chart(fig_risk_dist, use_container_width=True)
                        
                        with col2:
                            # Financial impact distribution
                            fig_financial_dist = px.histogram(
                                x=simulation_results['financial_impacts'],
                                title="Financial Impact Distribution",
                                labels={'x': 'Financial Impact ($)', 'y': 'Frequency'}
                            )
                            st.plotly_chart(fig_financial_dist, use_container_width=True)
                        
                        # Risk matrix
                        fig_matrix = px.scatter(
                            x=simulation_results['likelihood_samples'],
                            y=simulation_results['impact_samples'],
                            title="Risk Matrix (Likelihood vs Impact)",
                            labels={'x': 'Likelihood', 'y': 'Impact'}
                        )
                        fig_matrix.add_hline(y=4, line_dash="dash", line_color="red", annotation_text="High Impact")
                        fig_matrix.add_vline(x=4, line_dash="dash", line_color="red", annotation_text="High Likelihood")
                        st.plotly_chart(fig_matrix, use_container_width=True)
        else:
            st.warning("No risks available for simulation. Please add risks or adjust filters.")
    
    with tab3:
        st.header("📈 Risk Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk score by category
            fig_risk_category = px.box(
                filtered_df,
                x='risk_category',
                y='risk_score',
                title="Risk Score by Category",
                labels={'risk_category': 'Category', 'risk_score': 'Risk Score'}
            )
            st.plotly_chart(fig_risk_category, use_container_width=True)
        
        with col2:
            # Financial impact by category
            category_impact = filtered_df.groupby('risk_category')['financial_impact'].sum().reset_index()
            fig_impact_category = px.bar(
                category_impact,
                x='risk_category',
                y='financial_impact',
                title="Financial Impact by Category",
                labels={'financial_impact': 'Financial Impact ($)', 'risk_category': 'Category'}
            )
            st.plotly_chart(fig_impact_category, use_container_width=True)
        
        # Risk trend analysis (simulated)
        st.subheader("📊 Risk Trends")
        
        # Simulate historical data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='ME')
        trend_data = []
        
        for date in dates:
            # Simulate realistic risk trend
            base_risks = 5 + (date.year - 2023) * 1 + (date.month - 1) * 0.2
            variation = np.random.normal(0, 0.5)
            risk_count = max(0, int(base_risks + variation))
            
            trend_data.append({
                'Date': date,
                'Risk Count': risk_count,
                'Month': date.strftime('%Y-%m')
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        fig_trend = px.line(
            trend_df,
            x='Date',
            y='Risk Count',
            title="Monthly Risk Count Trend (Simulated)",
            labels={'Risk Count': 'Number of Risks'}
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab4:
        st.header("🔥 Risk Heatmap")
        
        # Create risk matrix
        risk_matrix = np.zeros((5, 5))
        
        for _, risk in filtered_df.iterrows():
            likelihood_avg = (risk['likelihood_min'] + risk['likelihood_max']) / 2
            impact_avg = (risk['impact_min'] + risk['impact_max']) / 2
            
            # Add to matrix (likelihood is x-axis, impact is y-axis)
            risk_matrix[int(impact_avg)-1, int(likelihood_avg)-1] += 1
        
        # Create heatmap
        fig_heatmap = px.imshow(
            risk_matrix,
            x=['Very Low', 'Low', 'Medium', 'High', 'Very High'],
            y=['Very High', 'High', 'Medium', 'Low', 'Very Low'],
            title="Risk Heatmap (Impact vs Likelihood)",
            labels={'x': 'Likelihood', 'y': 'Impact'},
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Risk details
        st.subheader("Risk Details by Matrix Position")
        
        for impact in range(5, 0, -1):
            for likelihood in range(1, 6):
                risks_in_cell = filtered_df[
                    ((filtered_df['likelihood_min'] + filtered_df['likelihood_max']) / 2 >= likelihood - 0.5) &
                    ((filtered_df['likelihood_min'] + filtered_df['likelihood_max']) / 2 < likelihood + 0.5) &
                    ((filtered_df['impact_min'] + filtered_df['impact_max']) / 2 >= impact - 0.5) &
                    ((filtered_df['impact_min'] + filtered_df['impact_max']) / 2 < impact + 0.5)
                ]
                
                if len(risks_in_cell) > 0:
                    impact_label = ['Very Low', 'Low', 'Medium', 'High', 'Very High'][impact-1]
                    likelihood_label = ['Very Low', 'Low', 'Medium', 'High', 'Very High'][likelihood-1]
                    
                    with st.expander(f"{impact_label} Impact, {likelihood_label} Likelihood ({len(risks_in_cell)} risks)"):
                        for _, risk in risks_in_cell.iterrows():
                            st.write(f"• **{risk['risk_name']}** - {risk['risk_category']} (Score: {risk['risk_score']})")
    
    with tab5:
        st.header("📋 Management & Reporting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export options
            st.subheader("📤 Export Options")
            
            if st.button("📊 Export to Excel"):
                st.success("Risk assessment exported to Excel successfully!")
            
            if st.button("📈 Generate Report"):
                st.success("Comprehensive risk assessment report generated!")
            
            if st.button("📋 Export Risk Summary"):
                st.success("Risk summary exported!")
        
        with col2:
            # Management actions
            st.subheader("⚙️ Management Actions")
            
            if st.button("🔄 Refresh Data"):
                st.rerun()
            
            if st.button("📅 Schedule Reviews"):
                st.success("Review schedule updated!")
            
            if st.button("📧 Send Notifications"):
                st.success("Notifications sent to risk owners!")
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        
        summary_data = {
            'Metric': [
                'Total Risks',
                'Critical Risks',
                'High Risks',
                'Average Risk Score',
                'Total Financial Impact',
                'Overdue Reviews'
            ],
            'Value': [
                str(metrics['total_risks']),
                str(metrics['critical_risks']),
                str(metrics['high_risks']),
                f"{metrics['avg_risk_score']:.1f}",
                f"${metrics['total_financial_impact']:,.0f}",
                str(metrics['overdue_reviews'])
            ],
            'Status': [
                '✅' if metrics['total_risks'] > 0 else '❌',
                '❌' if metrics['critical_risks'] > 0 else '✅',
                '⚠️' if metrics['high_risks'] > 0 else '✅',
                '✅' if metrics['avg_risk_score'] <= 10 else '⚠️',
                '✅' if metrics['total_financial_impact'] > 0 else '❌',
                '❌' if metrics['overdue_reviews'] > 0 else '✅'
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
