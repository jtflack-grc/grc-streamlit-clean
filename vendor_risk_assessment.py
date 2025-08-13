#!/usr/bin/env python3
"""
Vendor Risk Assessment Tool
==========================

Comprehensive vendor risk evaluation and scoring tool
built with Streamlit for interactive risk assessment.
"""

import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Vendor Risk Assessment Tool",
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
</style>
""", unsafe_allow_html=True)

def vendor_risk_assessment():
    st.markdown('<h1 class="main-header">Vendor Risk Assessment Tool</h1>', unsafe_allow_html=True)
    st.write("Comprehensive vendor risk evaluation and scoring")
    
    # Vendor assessment criteria
    assessment_criteria = {
        'Financial Risk': {
            'Financial Stability': [1, 5],
            'Credit Rating': [1, 5],
            'Revenue': [1, 5],
            'Profitability': [1, 5]
        },
        'Operational Risk': {
            'Service Quality': [1, 5],
            'Business Continuity': [1, 5],
            'Capacity': [1, 5],
            'Geographic Risk': [1, 5]
        },
        'Security Risk': {
            'Security Controls': [1, 5],
            'Data Protection': [1, 5],
            'Incident Response': [1, 5],
            'Compliance': [1, 5]
        },
        'Strategic Risk': {
            'Strategic Alignment': [1, 5],
            'Innovation': [1, 5],
            'Market Position': [1, 5],
            'Dependency': [1, 5]
        }
    }
    
    # Vendor information
    st.header("Vendor Information")
    
    vendor_name = st.text_input("Vendor Name")
    vendor_type = st.selectbox("Vendor Type", ["Technology", "Professional Services", "Financial", "Manufacturing", "Other"])
    contract_value = st.number_input("Contract Value ($)", 1000, 10000000, 100000)
    contract_duration = st.number_input("Contract Duration (months)", 1, 60, 12)
    
    # Risk assessment
    st.header("Risk Assessment")
    
    scores = {}
    
    for category, criteria in assessment_criteria.items():
        st.subheader(category)
        
        category_scores = {}
        for criterion, (min_val, max_val) in criteria.items():
            score = st.slider(f"{criterion}", min_val, max_val, 3)
            category_scores[criterion] = score
        
        scores[category] = category_scores
    
    # Calculate risk scores
    if st.button("Calculate Risk Score"):
        st.header("Risk Assessment Results")
        
        # Category scores
        category_averages = {}
        for category, criteria_scores in scores.items():
            avg_score = np.mean(list(criteria_scores.values()))
            category_averages[category] = avg_score
        
        # Overall risk score
        overall_score = np.mean(list(category_averages.values()))
        
        # Risk level determination
        if overall_score <= 2:
            risk_level = "Low"
            risk_color = "green"
        elif overall_score <= 3.5:
            risk_level = "Medium"
            risk_color = "orange"
        else:
            risk_level = "High"
            risk_color = "red"
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall Risk Score", f"{overall_score:.2f}/5")
        
        with col2:
            st.metric("Risk Level", risk_level)
        
        with col3:
            st.metric("Contract Value", f"${contract_value:,.0f}")
        
        # Category breakdown
        st.subheader("Risk Category Breakdown")
        
        category_df = pd.DataFrame({
            'Category': list(category_averages.keys()),
            'Average Score': list(category_averages.values())
        })
        
        st.bar_chart(category_df.set_index('Category'))
        
        # Recommendations
        st.subheader("Risk Treatment Recommendations")
        
        if risk_level == "High":
            st.warning("High Risk Vendor - Immediate action required")
            st.write("- Implement additional controls and monitoring")
            st.write("- Consider risk transfer options")
            st.write("- Regular vendor assessments")
            st.write("- Develop exit strategy")
        elif risk_level == "Medium":
            st.info("Medium Risk Vendor - Monitor and review")
            st.write("- Regular monitoring and reporting")
            st.write("- Periodic risk reassessment")
            st.write("- Consider control improvements")
        else:
            st.success("Low Risk Vendor - Standard monitoring")
            st.write("- Continue current monitoring")
            st.write("- Annual risk reassessment")
            st.write("- Standard vendor management")
        
        # Vendor tiering
        st.subheader("Vendor Tiering")
        
        if overall_score <= 2:
            tier = "Tier 1 - Strategic Partner"
        elif overall_score <= 3:
            tier = "Tier 2 - Preferred Vendor"
        elif overall_score <= 4:
            tier = "Tier 3 - Standard Vendor"
        else:
            tier = "Tier 4 - High Risk Vendor"
        
        st.info(f"Recommended Tier: {tier}")
        
        # Export results
        if st.button("Export Assessment"):
            assessment_data = {
                'Vendor Name': vendor_name,
                'Vendor Type': vendor_type,
                'Contract Value': contract_value,
                'Contract Duration': contract_duration,
                'Overall Risk Score': overall_score,
                'Risk Level': risk_level,
                'Vendor Tier': tier,
                'Assessment Date': pd.Timestamp.now()
            }
            
            # Add category scores
            for category, score in category_averages.items():
                assessment_data[f'{category}_Score'] = score
            
            df = pd.DataFrame([assessment_data])
            st.download_button(
                label="Download Assessment Report",
                data=df.to_csv(index=False),
                file_name=f"vendor_assessment_{vendor_name.replace(' ', '_')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    vendor_risk_assessment()
