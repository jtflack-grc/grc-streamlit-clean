#!/usr/bin/env python3
"""
GRC Compliance Dashboard
=======================

Real-time compliance monitoring and reporting dashboard
built with Streamlit and Plotly for interactive visualization.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="GRC Compliance Dashboard",
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

def compliance_dashboard():
    st.markdown('<h1 class="main-header">GRC Compliance Dashboard</h1>', unsafe_allow_html=True)
    st.write("Real-time compliance monitoring and reporting")
    
    # Sample compliance data
    frameworks = ['ISO 27001', 'SOC 2', 'NIST CSF', 'GDPR', 'PCI DSS']
    compliance_scores = [85, 92, 78, 88, 95]
    last_assessment = [datetime.now() - timedelta(days=30), 
                      datetime.now() - timedelta(days=15),
                      datetime.now() - timedelta(days=45),
                      datetime.now() - timedelta(days=20),
                      datetime.now() - timedelta(days=10)]
    
    # Create compliance dataframe
    compliance_df = pd.DataFrame({
        'Framework': frameworks,
        'Compliance Score': compliance_scores,
        'Last Assessment': last_assessment
    })
    
    # Overall compliance score
    overall_score = sum(compliance_scores) / len(compliance_scores)
    
    st.header("Overall Compliance Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Score", f"{overall_score:.1f}%")
    
    with col2:
        compliant_frameworks = sum(1 for score in compliance_scores if score >= 80)
        st.metric("Compliant Frameworks", f"{compliant_frameworks}/{len(frameworks)}")
    
    with col3:
        next_assessment = min(last_assessment) + timedelta(days=90)
        st.metric("Next Assessment", next_assessment.strftime("%Y-%m-%d"))
    
    # Compliance chart
    st.header("Framework Compliance Scores")
    
    fig = px.bar(compliance_df, x='Framework', y='Compliance Score',
                 color='Compliance Score',
                 color_continuous_scale='RdYlGn',
                 title="Compliance Scores by Framework")
    
    fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                  annotation_text="Compliance Threshold")
    
    st.plotly_chart(fig)
    
    # Control effectiveness
    st.header("Control Effectiveness")
    
    control_categories = ['Access Control', 'Data Protection', 'Incident Response', 
                         'Business Continuity', 'Vendor Management']
    effectiveness_scores = [88, 92, 75, 82, 90]
    
    control_df = pd.DataFrame({
        'Control Category': control_categories,
        'Effectiveness': effectiveness_scores
    })
    
    fig2 = px.pie(control_df, values='Effectiveness', names='Control Category',
                  title="Control Effectiveness Distribution")
    
    st.plotly_chart(fig2)
    
    # Recent findings
    st.header("Recent Audit Findings")
    
    findings_data = {
        'Finding': ['Weak password policy', 'Missing backup testing', 'Incomplete vendor assessment'],
        'Severity': ['Medium', 'High', 'Low'],
        'Status': ['Open', 'In Progress', 'Closed'],
        'Due Date': ['2024-02-15', '2024-01-30', '2024-01-15']
    }
    
    findings_df = pd.DataFrame(findings_data)
    st.dataframe(findings_df)
    
    # Action items
    st.header("Action Items")
    
    action_items = [
        "Implement multi-factor authentication for all critical systems",
        "Establish quarterly backup testing procedures",
        "Complete vendor risk assessment for new suppliers",
        "Update incident response playbook",
        "Conduct security awareness training"
    ]
    
    for i, item in enumerate(action_items, 1):
        st.write(f"{i}. {item}")

if __name__ == "__main__":
    compliance_dashboard()
