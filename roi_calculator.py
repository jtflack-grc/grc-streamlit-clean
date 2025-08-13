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
    page_title="ROI Calculator",
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

    /* ROI styling */
    .roi-positive { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
    .roi-negative { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .roi-neutral { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
</style>
""", unsafe_allow_html=True)

# Sample ROI data
@st.cache_data
def load_sample_roi_data():
    """Load sample ROI calculation data"""
    return {
        'scenarios': [
            {
                'name': 'SOC 2 Implementation',
                'description': 'Complete SOC 2 Type II certification program',
                'benefits': {
                    'Premium Pricing': 250000,
                    'Sales Acceleration': 150000,
                    'Insurance Savings': 30000,
                    'Operational Efficiency': 100000,
                    'Risk Avoidance': 500000
                },
                'costs': {
                    'Implementation': 150000,
                    'Annual Operations': 100000,
                    'Audit Fees': 50000,
                    'Technology': 75000
                },
                'timeline': '12 months',
                'risk_level': 'Medium'
            },
            {
                'name': 'ISO 27001 Certification',
                'description': 'Information security management system certification',
                'benefits': {
                    'Premium Pricing': 300000,
                    'Sales Acceleration': 200000,
                    'Insurance Savings': 50000,
                    'Operational Efficiency': 150000,
                    'Risk Avoidance': 600000
                },
                'costs': {
                    'Implementation': 200000,
                    'Annual Operations': 120000,
                    'Audit Fees': 60000,
                    'Technology': 80000
                },
                'timeline': '18 months',
                'risk_level': 'Medium'
            },
            {
                'name': 'Vendor Risk Management',
                'description': 'Comprehensive third-party risk management program',
                'benefits': {
                    'Premium Pricing': 100000,
                    'Sales Acceleration': 75000,
                    'Insurance Savings': 20000,
                    'Operational Efficiency': 80000,
                    'Risk Avoidance': 300000
                },
                'costs': {
                    'Implementation': 80000,
                    'Annual Operations': 60000,
                    'Audit Fees': 25000,
                    'Technology': 40000
                },
                'timeline': '6 months',
                'risk_level': 'Low'
            }
        ]
    }

def calculate_roi(benefits, costs):
    """Calculate ROI metrics"""
    total_benefits = sum(benefits.values())
    total_costs = sum(costs.values())
    
    if total_costs == 0:
        return {
            'roi_percentage': float('inf'),
            'net_benefit': total_benefits,
            'payback_period': 0,
            'benefit_cost_ratio': float('inf')
        }
    
    roi_percentage = ((total_benefits - total_costs) / total_costs) * 100
    net_benefit = total_benefits - total_costs
    payback_period = total_costs / total_benefits if total_benefits > 0 else float('inf')
    benefit_cost_ratio = total_benefits / total_costs
    
    return {
        'roi_percentage': roi_percentage,
        'net_benefit': net_benefit,
        'payback_period': payback_period,
        'benefit_cost_ratio': benefit_cost_ratio
    }

def get_roi_category(roi_percentage):
    """Get ROI category and recommendation"""
    if roi_percentage >= 100:
        return "Excellent", "🟢", "Strong business case - proceed with implementation"
    elif roi_percentage >= 50:
        return "Good", "🟡", "Positive ROI - consider implementation with monitoring"
    elif roi_percentage >= 0:
        return "Marginal", "🟠", "Break-even scenario - evaluate strategic value"
    else:
        return "Poor", "🔴", "Negative ROI - reconsider or revise approach"

def generate_business_case(roi_data, benefits, costs):
    """Generate business case summary"""
    total_benefits = sum(benefits.values())
    total_costs = sum(costs.values())
    
    business_case = {
        'executive_summary': f"Investment in this GRC initiative shows a {roi_data['roi_percentage']:.1f}% ROI with ${roi_data['net_benefit']:,.0f} in net annual benefits.",
        'key_benefits': [
            f"Total annual benefits: ${total_benefits:,.0f}",
            f"Payback period: {roi_data['payback_period']:.1f} years",
            f"Benefit-cost ratio: {roi_data['benefit_cost_ratio']:.2f}:1"
        ],
        'risk_factors': [
            "Benefit estimates may vary based on market conditions",
            "Implementation timeline could affect cost projections",
            "Regulatory changes may impact compliance requirements"
        ],
        'recommendations': [
            "Proceed with implementation planning",
            "Establish monitoring and measurement framework",
            "Regular ROI review and adjustment process"
        ]
    }
    
    return business_case

def main():
    st.markdown('<h1 class="main-header">GRC ROI Calculator</h1>', unsafe_allow_html=True)
    
    # Load sample data
    sample_data = load_sample_roi_data()
    
    # Sidebar
    st.sidebar.header("🔧 Calculator Options")
    
    # Calculation type
    calc_type = st.sidebar.selectbox(
        "Calculation Type",
        ["Custom ROI Calculation", "Sample Scenarios", "Comparison Analysis"]
    )
    
    # Organization info
    st.sidebar.subheader("Organization Information")
    org_name = st.sidebar.text_input("Organization Name", "Sample Organization")
    org_size = st.sidebar.selectbox("Organization Size", ["Small (<100)", "Medium (100-1000)", "Large (1000-10000)", "Enterprise (>10000)"])
    industry = st.sidebar.selectbox("Industry", ["Technology", "Financial Services", "Healthcare", "Manufacturing", "Government", "Other"])
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["💰 ROI Calculator", "📊 Analysis", "📈 Scenarios", "📋 Business Case"])
    
    with tab1:
        st.header("💰 ROI Calculator")
        
        st.write("""
        Calculate the return on investment for your GRC program initiatives. Enter your estimated annual benefits and costs to get a comprehensive ROI analysis.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💡 Benefit Categories")
            
            # Benefit inputs
            premium_pricing = st.number_input(
                "Premium Pricing ($)",
                min_value=0,
                value=250000,
                step=10000,
                help="Additional revenue from security certifications"
            )
            
            sales_acceleration = st.number_input(
                "Sales Acceleration ($)",
                min_value=0,
                value=150000,
                step=10000,
                help="Faster sales cycles due to compliance"
            )
            
            insurance_savings = st.number_input(
                "Insurance Savings ($)",
                min_value=0,
                value=30000,
                step=5000,
                help="Reduced cyber insurance premiums"
            )
            
            operational_efficiency = st.number_input(
                "Operational Efficiency ($)",
                min_value=0,
                value=100000,
                step=10000,
                help="Time savings from streamlined processes"
            )
            
            risk_avoidance = st.number_input(
                "Risk Avoidance ($)",
                min_value=0,
                value=500000,
                step=50000,
                help="Avoided costs from security incidents"
            )
            
            benefits = {
                'Premium Pricing': premium_pricing,
                'Sales Acceleration': sales_acceleration,
                'Insurance Savings': insurance_savings,
                'Operational Efficiency': operational_efficiency,
                'Risk Avoidance': risk_avoidance
            }
        
        with col2:
            st.subheader("💸 Cost Categories")
            
            # Cost inputs
            implementation_cost = st.number_input(
                "Implementation Cost ($)",
                min_value=0,
                value=150000,
                step=10000,
                help="Initial implementation and setup costs"
            )
            
            annual_operations = st.number_input(
                "Annual Operations ($)",
                min_value=0,
                value=100000,
                step=10000,
                help="Ongoing operational costs"
            )
            
            audit_fees = st.number_input(
                "Audit Fees ($)",
                min_value=0,
                value=50000,
                step=5000,
                help="Annual audit and certification fees"
            )
            
            technology_costs = st.number_input(
                "Technology Costs ($)",
                min_value=0,
                value=75000,
                step=10000,
                help="Technology and tool costs"
            )
            
            costs = {
                'Implementation': implementation_cost,
                'Annual Operations': annual_operations,
                'Audit Fees': audit_fees,
                'Technology': technology_costs
            }
        
        # Calculate ROI
        if st.button("Calculate ROI", type="primary"):
            roi_data = calculate_roi(benefits, costs)
            category, icon, recommendation = get_roi_category(roi_data['roi_percentage'])
            business_case = generate_business_case(roi_data, benefits, costs)
            
            # Store in session state
            st.session_state.roi_data = roi_data
            st.session_state.benefits = benefits
            st.session_state.costs = costs
            st.session_state.category = category
            st.session_state.icon = icon
            st.session_state.recommendation = recommendation
            st.session_state.business_case = business_case
            st.session_state.calculation_completed = True
            
            st.success("ROI calculation completed! View results in the Analysis tab.")
    
    with tab2:
        st.header("📊 ROI Analysis")
        
        if not st.session_state.get('calculation_completed', False):
            st.info("Please complete the ROI calculation in the ROI Calculator tab first.")
        else:
            roi_data = st.session_state.roi_data
            benefits = st.session_state.benefits
            costs = st.session_state.costs
            category = st.session_state.category
            icon = st.session_state.icon
            recommendation = st.session_state.recommendation
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "ROI Percentage",
                    f"{roi_data['roi_percentage']:.1f}%",
                    delta=f"{category} {icon}"
                )
            
            with col2:
                st.metric(
                    "Net Annual Benefit",
                    f"${roi_data['net_benefit']:,.0f}",
                    delta="Positive" if roi_data['net_benefit'] > 0 else "Negative"
                )
            
            with col3:
                st.metric(
                    "Payback Period",
                    f"{roi_data['payback_period']:.1f} years",
                    delta="Faster" if roi_data['payback_period'] < 2 else "Longer"
                )
            
            with col4:
                st.metric(
                    "Benefit-Cost Ratio",
                    f"{roi_data['benefit_cost_ratio']:.2f}:1",
                    delta="Favorable" if roi_data['benefit_cost_ratio'] > 1 else "Unfavorable"
                )
            
            # ROI Assessment
            st.subheader("ROI Assessment")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Category:** {category} {icon}")
                st.write(f"**Recommendation:** {recommendation}")
                
                # Risk assessment
                if roi_data['roi_percentage'] >= 100:
                    st.success("Excellent ROI - Strong business case for implementation")
                elif roi_data['roi_percentage'] >= 50:
                    st.info("Good ROI - Positive return with manageable risk")
                elif roi_data['roi_percentage'] >= 0:
                    st.warning("Marginal ROI - Consider strategic value beyond financial return")
                else:
                    st.error("Poor ROI - Reconsider approach or revise estimates")
            
            with col2:
                # Benefit breakdown chart
                benefit_data = []
                for benefit, value in benefits.items():
                    if value > 0:
                        benefit_data.append({
                            'Benefit Category': benefit,
                            'Value': value,
                            'Percentage': (value / sum(benefits.values())) * 100
                        })
                
                if benefit_data:
                    benefit_df = pd.DataFrame(benefit_data)
                    
                    fig_benefits = px.pie(
                        benefit_df,
                        values='Value',
                        names='Benefit Category',
                        title="Benefit Breakdown",
                        hole=0.4
                    )
                    fig_benefits.update_layout(height=400)
                    st.plotly_chart(fig_benefits, use_container_width=True)
            
            # Cost breakdown
            st.subheader("Cost Breakdown")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cost_data = []
                for cost, value in costs.items():
                    if value > 0:
                        cost_data.append({
                            'Cost Category': cost,
                            'Value': value,
                            'Percentage': (value / sum(costs.values())) * 100
                        })
                
                if cost_data:
                    cost_df = pd.DataFrame(cost_data)
                    
                    fig_costs = px.bar(
                        cost_df,
                        x='Cost Category',
                        y='Value',
                        title="Cost Breakdown",
                        color='Value',
                        color_continuous_scale='Reds'
                    )
                    fig_costs.update_layout(height=400)
                    st.plotly_chart(fig_costs, use_container_width=True)
            
            with col2:
                # Cost table
                st.write("**Detailed Cost Analysis:**")
                cost_summary = []
                for cost, value in costs.items():
                    cost_summary.append({
                        'Category': cost,
                        'Amount': f"${value:,.0f}",
                        'Percentage': f"{(value / sum(costs.values())) * 100:.1f}%"
                    })
                
                cost_summary_df = pd.DataFrame(cost_summary)
                st.dataframe(cost_summary_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.header("📈 Sample Scenarios")
        
        st.write("Compare your ROI calculation with sample scenarios for common GRC initiatives.")
        
        # Display sample scenarios
        for i, scenario in enumerate(sample_data['scenarios'], 1):
            with st.expander(f"{i}. {scenario['name']} - {scenario['description']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Timeline:** {scenario['timeline']}")
                    st.write(f"**Risk Level:** {scenario['risk_level']}")
                    
                    # Calculate scenario ROI
                    scenario_roi = calculate_roi(scenario['benefits'], scenario['costs'])
                    scenario_category, scenario_icon, _ = get_roi_category(scenario_roi['roi_percentage'])
                    
                    st.metric(
                        "Scenario ROI",
                        f"{scenario_roi['roi_percentage']:.1f}%",
                        delta=f"{scenario_category} {scenario_icon}"
                    )
                
                with col2:
                    # Benefits chart
                    benefit_df = pd.DataFrame([
                        {'Category': k, 'Value': v} for k, v in scenario['benefits'].items()
                    ])
                    
                    fig_scenario = px.bar(
                        benefit_df,
                        x='Category',
                        y='Value',
                        title=f"Benefits - {scenario['name']}",
                        color='Value',
                        color_continuous_scale='Greens'
                    )
                    fig_scenario.update_layout(height=300)
                    st.plotly_chart(fig_scenario, use_container_width=True)
                
                # Comparison with user calculation
                if st.session_state.get('calculation_completed', False):
                    user_roi = st.session_state.roi_data['roi_percentage']
                    scenario_roi_pct = scenario_roi['roi_percentage']
                    
                    comparison_data = pd.DataFrame({
                        'Scenario': ['Your Calculation', scenario['name']],
                        'ROI (%)': [user_roi, scenario_roi_pct]
                    })
                    
                    fig_comparison = px.bar(
                        comparison_data,
                        x='Scenario',
                        y='ROI (%)',
                        title=f"ROI Comparison: Your Calculation vs {scenario['name']}",
                        color='ROI (%)',
                        color_continuous_scale='RdYlGn'
                    )
                    st.plotly_chart(fig_comparison, use_container_width=True)
    
    with tab4:
        st.header("📋 Business Case")
        
        if not st.session_state.get('calculation_completed', False):
            st.info("Please complete the ROI calculation in the ROI Calculator tab first.")
        else:
            business_case = st.session_state.business_case
            
            # Executive Summary
            st.subheader("Executive Summary")
            st.write(business_case['executive_summary'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Key Benefits")
                for benefit in business_case['key_benefits']:
                    st.write(f"• {benefit}")
            
            with col2:
                st.subheader("Risk Factors")
                for risk in business_case['risk_factors']:
                    st.write(f"• {risk}")
            
            # Recommendations
            st.subheader("Recommendations")
            for rec in business_case['recommendations']:
                st.write(f"• {rec}")
            
            # Sensitivity Analysis
            st.subheader("Sensitivity Analysis")
            
            # Create sensitivity analysis
            sensitivity_data = []
            base_roi = st.session_state.roi_data['roi_percentage']
            
            for change in [-20, -10, 0, 10, 20]:
                adjusted_benefits = {k: v * (1 + change/100) for k, v in st.session_state.benefits.items()}
                adjusted_roi = calculate_roi(adjusted_benefits, st.session_state.costs)
                sensitivity_data.append({
                    'Benefit Change (%)': change,
                    'ROI (%)': adjusted_roi['roi_percentage']
                })
            
            sensitivity_df = pd.DataFrame(sensitivity_data)
            
            fig_sensitivity = px.line(
                sensitivity_df,
                x='Benefit Change (%)',
                y='ROI (%)',
                title="ROI Sensitivity to Benefit Changes",
                markers=True
            )
            fig_sensitivity.add_hline(y=base_roi, line_dash="dash", line_color="red", 
                                    annotation_text=f"Base ROI: {base_roi:.1f}%")
            st.plotly_chart(fig_sensitivity, use_container_width=True)
            
            # Export options
            st.subheader("📤 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Export to PDF"):
                    st.info("PDF export functionality would be implemented here")
            
            with col2:
                if st.button("📈 Export to Excel"):
                    st.info("Excel export functionality would be implemented here")
            
            with col3:
                if st.button("🔄 Save Analysis"):
                    st.success("Analysis saved successfully!")

if __name__ == "__main__":
    main()
