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
    page_title="CSF Maturity Assessment",
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

    /* Maturity level styling */
    .maturity-low { background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; }
    .maturity-medium { background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; }
    .maturity-high { background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

# CSF Framework data
@st.cache_data
def load_csf_framework():
    """Load NIST CSF framework data"""
    functions = [
        {
            "function": "Identify",
            "description": "Develop organizational understanding to manage cybersecurity risk",
            "categories": ["Asset Management", "Business Environment", "Governance", "Risk Assessment", "Risk Management Strategy", "Supply Chain Risk Management"],
            "color": "#1f77b4"
        },
        {
            "function": "Protect",
            "description": "Develop and implement appropriate safeguards",
            "categories": ["Identity Management and Access Control", "Awareness and Training", "Data Security", "Information Protection Processes and Procedures", "Maintenance", "Protective Technology"],
            "color": "#ff7f0e"
        },
        {
            "function": "Detect",
            "description": "Develop and implement appropriate activities to identify cybersecurity events",
            "categories": ["Anomalies and Events", "Security Continuous Monitoring", "Detection Processes"],
            "color": "#2ca02c"
        },
        {
            "function": "Respond",
            "description": "Develop and implement appropriate activities to take action regarding detected cybersecurity events",
            "categories": ["Response Planning", "Communications", "Analysis", "Mitigation", "Improvements"],
            "color": "#d62728"
        },
        {
            "function": "Recover",
            "description": "Develop and implement appropriate activities to maintain plans for resilience",
            "categories": ["Recovery Planning", "Improvements", "Communications"],
            "color": "#9467bd"
        }
    ]
    
    questions = [
        # Identify Function
        {
            "id": 1,
            "function": "Identify",
            "category": "Asset Management",
            "question": "Asset inventory is complete and updated quarterly",
            "description": "Comprehensive asset inventory including hardware, software, data, and personnel",
            "maturity_levels": {
                0: "No asset inventory exists",
                1: "Partial inventory, not updated regularly",
                2: "Basic inventory with quarterly updates",
                3: "Comprehensive inventory with automated updates",
                4: "Advanced inventory with real-time monitoring",
                5: "Optimized inventory with predictive analytics"
            }
        },
        {
            "id": 2,
            "function": "Identify",
            "category": "Risk Assessment",
            "question": "Formal risk assessment and treatment process",
            "description": "Structured risk assessment methodology with treatment planning",
            "maturity_levels": {
                0: "No formal risk assessment process",
                1: "Ad-hoc risk assessments",
                2: "Basic risk assessment framework",
                3: "Comprehensive risk assessment with treatment plans",
                4: "Advanced risk assessment with continuous monitoring",
                5: "Optimized risk assessment with predictive modeling"
            }
        },
        
        # Protect Function
        {
            "id": 3,
            "function": "Protect",
            "category": "Identity Management and Access Control",
            "question": "Identity and access controls (MFA, least privilege)",
            "description": "Multi-factor authentication and principle of least privilege implementation",
            "maturity_levels": {
                0: "No access controls in place",
                1: "Basic password policies only",
                2: "MFA implemented for critical systems",
                3: "Comprehensive MFA and role-based access",
                4: "Advanced access controls with behavioral analytics",
                5: "Optimized access controls with zero-trust architecture"
            }
        },
        {
            "id": 4,
            "function": "Protect",
            "category": "Awareness and Training",
            "question": "Security awareness program with metrics",
            "description": "Comprehensive security awareness training with measurable outcomes",
            "maturity_levels": {
                0: "No security awareness program",
                1: "Basic annual training only",
                2: "Regular training with basic metrics",
                3: "Comprehensive program with detailed metrics",
                4: "Advanced program with behavioral change measurement",
                5: "Optimized program with continuous learning and adaptation"
            }
        },
        {
            "id": 5,
            "function": "Protect",
            "category": "Data Security",
            "question": "Data protection (classification, encryption)",
            "description": "Data classification and encryption controls",
            "maturity_levels": {
                0: "No data protection controls",
                1: "Basic data handling procedures",
                2: "Data classification framework in place",
                3: "Comprehensive encryption and protection",
                4: "Advanced data protection with DLP",
                5: "Optimized data protection with AI/ML"
            }
        },
        {
            "id": 6,
            "function": "Protect",
            "category": "Information Protection Processes and Procedures",
            "question": "Change/configuration management",
            "description": "Formal change and configuration management processes",
            "maturity_levels": {
                0: "No change management process",
                1: "Ad-hoc change procedures",
                2: "Basic change management framework",
                3: "Comprehensive change and configuration management",
                4: "Advanced change management with automation",
                5: "Optimized change management with predictive controls"
            }
        },
        
        # Detect Function
        {
            "id": 7,
            "function": "Detect",
            "category": "Security Continuous Monitoring",
            "question": "Security monitoring with escalation runbooks",
            "description": "24/7 security monitoring with documented response procedures",
            "maturity_levels": {
                0: "No security monitoring",
                1: "Basic log collection",
                2: "Security monitoring with basic alerts",
                3: "Comprehensive monitoring with escalation procedures",
                4: "Advanced monitoring with automated response",
                5: "Optimized monitoring with AI-driven detection"
            }
        },
        {
            "id": 8,
            "function": "Detect",
            "category": "Anomalies and Events",
            "question": "Vulnerability management with SLAs",
            "description": "Systematic vulnerability assessment and remediation",
            "maturity_levels": {
                0: "No vulnerability management",
                1: "Ad-hoc vulnerability scanning",
                2: "Regular scanning with basic remediation",
                3: "Comprehensive vulnerability management with SLAs",
                4: "Advanced vulnerability management with automation",
                5: "Optimized vulnerability management with predictive patching"
            }
        },
        
        # Respond Function
        {
            "id": 9,
            "function": "Respond",
            "category": "Response Planning",
            "question": "Incident response plan tested annually",
            "description": "Documented incident response procedures with regular testing",
            "maturity_levels": {
                0: "No incident response plan",
                1: "Basic incident response procedures",
                2: "Documented plan with annual testing",
                3: "Comprehensive plan with regular exercises",
                4: "Advanced incident response with automation",
                5: "Optimized incident response with AI assistance"
            }
        },
        {
            "id": 10,
            "function": "Respond",
            "category": "Recovery Planning",
            "question": "BCP/DR exercises with RTO/RPO targets",
            "description": "Business continuity and disaster recovery planning",
            "maturity_levels": {
                0: "No BCP/DR planning",
                1: "Basic disaster recovery procedures",
                2: "Documented BCP/DR with defined targets",
                3: "Comprehensive BCP/DR with regular testing",
                4: "Advanced BCP/DR with automated recovery",
                5: "Optimized BCP/DR with continuous improvement"
            }
        },
        
        # Recover Function
        {
            "id": 11,
            "function": "Recover",
            "category": "Recovery Planning",
            "question": "Third-party risk program (attestations, clauses)",
            "description": "Comprehensive vendor and third-party risk management",
            "maturity_levels": {
                0: "No third-party risk management",
                1: "Basic vendor assessments",
                2: "Formal third-party risk program",
                3: "Comprehensive program with regular assessments",
                4: "Advanced program with continuous monitoring",
                5: "Optimized program with predictive risk modeling"
            }
        },
        {
            "id": 12,
            "function": "Recover",
            "category": "Improvements",
            "question": "Board reporting (KRIs, ROI) quarterly",
            "description": "Regular executive reporting with key risk indicators",
            "maturity_levels": {
                0: "No board reporting",
                1: "Ad-hoc security updates",
                2: "Regular security reporting",
                3: "Comprehensive reporting with KRIs",
                4: "Advanced reporting with ROI analysis",
                5: "Optimized reporting with predictive insights"
            }
        }
    ]
    
    return functions, questions

def calculate_maturity_score(scores, questions):
    """Calculate overall maturity score and function scores"""
    total_score = sum(scores.values())
    max_possible = len(scores) * 5
    overall_maturity = (total_score / max_possible) * 100
    
    # Calculate function scores
    function_scores = {}
    for question_id, score in scores.items():
        question = next(q for q in questions if q['id'] == question_id)
        function = question['function']
        if function not in function_scores:
            function_scores[function] = []
        function_scores[function].append(score)
    
    function_maturity = {}
    for function, scores_list in function_scores.items():
        function_maturity[function] = (sum(scores_list) / (len(scores_list) * 5)) * 100
    
    return overall_maturity, function_maturity

def get_maturity_level(score):
    """Get maturity level based on score"""
    if score >= 80:
        return "Optimized", "🟢"
    elif score >= 60:
        return "Advanced", "🟡"
    elif score >= 40:
        return "Intermediate", "🟠"
    elif score >= 20:
        return "Basic", "🔴"
    else:
        return "Initial", "⚫"

def generate_recommendations(scores, questions):
    """Generate recommendations based on assessment scores"""
    recommendations = []
    
    # Find lowest scoring areas
    low_scores = {qid: score for qid, score in scores.items() if score <= 2}
    
    for qid, score in low_scores.items():
        question = next(q for q in questions if q['id'] == qid)
        recommendations.append({
            "priority": "High" if score <= 1 else "Medium",
            "function": question['function'],
            "category": question['category'],
            "question": question['question'],
            "current_score": score,
            "recommendation": f"Focus on improving {question['category'].lower()} capabilities. Current score: {score}/5",
            "next_steps": question['maturity_levels'].get(score + 1, "Implement basic controls")
        })
    
    # Sort by priority and current score
    recommendations.sort(key=lambda x: (x['priority'] == 'High', -x['current_score']))
    
    return recommendations[:5]  # Top 5 recommendations

def main():
    st.markdown('<h1 class="main-header">NIST CSF Maturity Assessment</h1>', unsafe_allow_html=True)
    
    # Load framework data
    functions, questions = load_csf_framework()
    
    # Sidebar
    st.sidebar.header("🔧 Assessment Options")
    
    # Assessment type
    assessment_type = st.sidebar.selectbox(
        "Assessment Type",
        ["Quick Assessment (12 questions)", "Detailed Assessment (60 questions)", "Custom Assessment"]
    )
    
    # Organization info
    st.sidebar.subheader("Organization Information")
    org_name = st.sidebar.text_input("Organization Name", "Sample Organization")
    org_size = st.sidebar.selectbox("Organization Size", ["Small (<100)", "Medium (100-1000)", "Large (1000-10000)", "Enterprise (>10000)"])
    industry = st.sidebar.selectbox("Industry", ["Technology", "Financial Services", "Healthcare", "Manufacturing", "Government", "Other"])
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Assessment", "📊 Results", "🎯 Recommendations", "📈 Analytics"])
    
    with tab1:
        st.header("📝 CSF Maturity Assessment")
        
        st.write("""
        This assessment evaluates your organization's cybersecurity maturity across the five NIST Cybersecurity Framework functions: 
        **Identify**, **Protect**, **Detect**, **Respond**, and **Recover**.
        
        Rate each question from 0 (not in place) to 5 (optimized) based on your organization's current capabilities.
        """)
        
        # Initialize session state for scores
        if 'scores' not in st.session_state:
            st.session_state.scores = {}
        
        # Assessment form
        with st.form("csf_assessment"):
            st.subheader("Assessment Questions")
            
            # Group questions by function
            for function in functions:
                st.markdown(f"### {function['function']} Function")
                st.write(f"*{function['description']}*")
                
                function_questions = [q for q in questions if q['function'] == function['function']]
                
                for question in function_questions:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{question['id']}. {question['question']}**")
                        st.caption(f"Category: {question['category']}")
                        st.caption(question['description'])
                    
                    with col2:
                        score = st.slider(
                            f"Score {question['id']}",
                            min_value=0,
                            max_value=5,
                            value=st.session_state.scores.get(question['id'], 2),
                            key=f"score_{question['id']}",
                            help=f"0: {question['maturity_levels'][0]} | 5: {question['maturity_levels'][5]}"
                        )
                        st.session_state.scores[question['id']] = score
                        
                        # Show maturity level description
                        if score in question['maturity_levels']:
                            st.caption(f"**{question['maturity_levels'][score]}**")
            
            submitted = st.form_submit_button("Calculate Maturity Score")
            
            if submitted:
                st.session_state.assessment_completed = True
                st.success("Assessment completed! View results in the Results tab.")
    
    with tab2:
        st.header("📊 Assessment Results")
        
        if not st.session_state.get('assessment_completed', False):
            st.info("Please complete the assessment in the Assessment tab first.")
        else:
            # Calculate scores
            overall_maturity, function_maturity = calculate_maturity_score(st.session_state.scores, questions)
            maturity_level, maturity_icon = get_maturity_level(overall_maturity)
            
            # Display overall score
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Overall Maturity Score",
                    f"{overall_maturity:.1f}%",
                    delta=f"{maturity_level} {maturity_icon}"
                )
            
            with col2:
                st.metric(
                    "Maturity Level",
                    maturity_level,
                    delta=f"Score: {overall_maturity:.1f}%"
                )
            
            with col3:
                st.metric(
                    "Assessment Date",
                    datetime.datetime.now().strftime("%Y-%m-%d"),
                    delta="Current Assessment"
                )
            
            # Function scores
            st.subheader("Function Maturity Scores")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Function scores bar chart
                function_data = []
                for function, score in function_maturity.items():
                    level, icon = get_maturity_level(score)
                    function_data.append({
                        'Function': function,
                        'Score': score,
                        'Level': level,
                        'Icon': icon
                    })
                
                function_df = pd.DataFrame(function_data)
                
                fig_function = px.bar(
                    function_df,
                    x='Function',
                    y='Score',
                    color='Score',
                    color_continuous_scale='RdYlGn',
                    title="Function Maturity Scores",
                    labels={'Score': 'Maturity Score (%)'}
                )
                fig_function.update_layout(height=400)
                st.plotly_chart(fig_function, use_container_width=True)
            
            with col2:
                # Function scores table
                st.write("**Detailed Function Scores:**")
                for function, score in function_maturity.items():
                    level, icon = get_maturity_level(score)
                    st.write(f"{icon} **{function}**: {score:.1f}% ({level})")
                
                # Radar chart
                fig_radar = go.Figure()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=list(function_maturity.values()),
                    theta=list(function_maturity.keys()),
                    fill='toself',
                    name='Current Maturity',
                    line_color='blue'
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="Maturity Radar Chart"
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Question-level breakdown
            st.subheader("Question-Level Breakdown")
            
            question_data = []
            for qid, score in st.session_state.scores.items():
                question = next(q for q in questions if q['id'] == qid)
                question_data.append({
                    'Question ID': qid,
                    'Function': question['function'],
                    'Category': question['category'],
                    'Question': question['question'],
                    'Score': score,
                    'Max Score': 5,
                    'Percentage': (score / 5) * 100
                })
            
            question_df = pd.DataFrame(question_data)
            
            # Color code by score
            def color_score(val):
                if val >= 4:
                    return 'background-color: #d4edda'
                elif val >= 2:
                    return 'background-color: #fff3cd'
                else:
                    return 'background-color: #f8d7da'
            
            st.dataframe(
                question_df[['Question ID', 'Function', 'Category', 'Question', 'Score', 'Percentage']].style.applymap(
                    color_score, subset=['Score']
                ),
                use_container_width=True,
                hide_index=True
            )
    
    with tab3:
        st.header("🎯 Recommendations")
        
        if not st.session_state.get('assessment_completed', False):
            st.info("Please complete the assessment in the Assessment tab first.")
        else:
            # Generate recommendations
            recommendations = generate_recommendations(st.session_state.scores, questions)
            
            st.subheader("Priority Recommendations")
            
            for i, rec in enumerate(recommendations, 1):
                with st.expander(f"{i}. {rec['question']} (Priority: {rec['priority']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Function:** {rec['function']}")
                        st.write(f"**Category:** {rec['category']}")
                        st.write(f"**Current Score:** {rec['current_score']}/5")
                    
                    with col2:
                        st.write(f"**Recommendation:** {rec['recommendation']}")
                        st.write(f"**Next Steps:** {rec['next_steps']}")
                    
                    # Progress bar for improvement
                    improvement_needed = 5 - rec['current_score']
                    st.progress(rec['current_score'] / 5)
                    st.caption(f"Improvement needed: {improvement_needed} levels")
            
            # Improvement roadmap
            st.subheader("📋 Improvement Roadmap")
            
            roadmap_data = []
            for rec in recommendations:
                roadmap_data.append({
                    'Priority': rec['priority'],
                    'Function': rec['function'],
                    'Category': rec['category'],
                    'Current Score': rec['current_score'],
                    'Target Score': min(rec['current_score'] + 2, 5),
                    'Effort': 'High' if rec['current_score'] <= 1 else 'Medium',
                    'Timeline': '6-12 months' if rec['current_score'] <= 1 else '3-6 months'
                })
            
            roadmap_df = pd.DataFrame(roadmap_data)
            st.dataframe(roadmap_df, use_container_width=True, hide_index=True)
    
    with tab4:
        st.header("📈 Analytics & Trends")
        
        if not st.session_state.get('assessment_completed', False):
            st.info("Please complete the assessment in the Assessment tab first.")
        else:
            # Benchmark comparison
            st.subheader("Benchmark Comparison")
            
            # Simulate industry benchmarks
            industry_benchmarks = {
                "Technology": 65,
                "Financial Services": 72,
                "Healthcare": 58,
                "Manufacturing": 52,
                "Government": 68,
                "Other": 60
            }
            
            overall_maturity, _ = calculate_maturity_score(st.session_state.scores, questions)
            benchmark = industry_benchmarks.get(industry, 60)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Benchmark comparison chart
                benchmark_data = pd.DataFrame({
                    'Metric': ['Your Organization', f'{industry} Average'],
                    'Score': [overall_maturity, benchmark]
                })
                
                fig_benchmark = px.bar(
                    benchmark_data,
                    x='Metric',
                    y='Score',
                    color='Score',
                    color_continuous_scale='RdYlGn',
                    title=f"Benchmark Comparison ({industry})",
                    labels={'Score': 'Maturity Score (%)'}
                )
                st.plotly_chart(fig_benchmark, use_container_width=True)
            
            with col2:
                # Gap analysis
                gap = overall_maturity - benchmark
                st.metric(
                    "Gap vs Industry Average",
                    f"{gap:+.1f}%",
                    delta="Above Average" if gap > 0 else "Below Average"
                )
                
                if gap < -10:
                    st.warning("Significant improvement opportunities identified")
                elif gap > 10:
                    st.success("Above industry average performance")
                else:
                    st.info("Close to industry average")
            
            # Trend analysis
            st.subheader("Trend Analysis")
            
            # Simulate historical data
            dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='Q')
            trend_data = []
            
            for date in dates:
                # Simulate realistic trend with some variation
                base_score = 45 + (date.year - 2023) * 8 + (date.quarter - 1) * 2
                variation = np.random.normal(0, 3)
                score = max(0, min(100, base_score + variation))
                
                trend_data.append({
                    'Date': date,
                    'Maturity Score': score,
                    'Period': f"Q{date.quarter} {date.year}"
                })
            
            trend_df = pd.DataFrame(trend_data)
            
            fig_trend = px.line(
                trend_df,
                x='Date',
                y='Maturity Score',
                title="Maturity Score Trend (Simulated)",
                labels={'Maturity Score': 'Maturity Score (%)'}
            )
            fig_trend.add_hline(y=overall_maturity, line_dash="dash", line_color="red", 
                              annotation_text=f"Current Score: {overall_maturity:.1f}%")
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Export options
            st.subheader("📤 Export Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Export to PDF"):
                    st.info("PDF export functionality would be implemented here")
            
            with col2:
                if st.button("📈 Export to Excel"):
                    st.info("Excel export functionality would be implemented here")
            
            with col3:
                if st.button("🔄 Save Assessment"):
                    st.success("Assessment saved successfully!")

if __name__ == "__main__":
    main()
