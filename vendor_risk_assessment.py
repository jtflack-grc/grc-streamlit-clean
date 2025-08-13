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

def vendor_risk_assessment():
    st.title("Vendor Risk Assessment Tool")
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
            st.metric("Contract Value", f"${contract_value:,}")
        
        # Category breakdown
        st.subheader("Risk Category Breakdown")
        
        category_df = pd.DataFrame({
            'Category': list(category_averages.keys()),
            'Score': list(category_averages.values())
        })
        
        st.bar_chart(category_df.set_index('Category'))
        
        # Recommendations
        st.subheader("Risk Mitigation Recommendations")
        
        if risk_level == "High":
            st.error("High Risk Vendor - Immediate action required")
            st.write("- Implement additional controls")
            st.write("- Consider alternative vendors")
            st.write("- Increase monitoring frequency")
            st.write("- Require security assessments")
        elif risk_level == "Medium":
            st.warning("Medium Risk Vendor - Enhanced due diligence required")
            st.write("- Conduct security assessments")
            st.write("- Implement monitoring controls")
            st.write("- Regular review meetings")
            st.write("- Performance metrics tracking")
        else:
            st.success("Low Risk Vendor - Standard controls acceptable")
            st.write("- Standard contract terms")
            st.write("- Regular performance reviews")
            st.write("- Annual risk reassessment")
        
        # Vendor tier assignment
        st.subheader("Vendor Tier Assignment")
        
        if overall_score <= 2:
            tier = "Tier 3 - Low Risk"
        elif overall_score <= 3.5:
            tier = "Tier 2 - Medium Risk"
        else:
            tier = "Tier 1 - High Risk"
        
        st.info(f"Recommended Tier: {tier}")
        
        # Next steps
        st.subheader("Next Steps")
        
        next_steps = [
            "Complete vendor onboarding process",
            "Establish monitoring and reporting",
            "Schedule regular review meetings",
            "Document risk acceptance or mitigation",
            "Update vendor inventory"
        ]
        
        for i, step in enumerate(next_steps, 1):
            st.write(f"{i}. {step}")

if __name__ == "__main__":
    vendor_risk_assessment()
