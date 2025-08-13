import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Policy Management System",
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

if 'policies' not in st.session_state:
    st.session_state.policies = []

def generate_sample_data():
    policy_types = ['Information Security Policy', 'Access Control Policy', 'Data Protection Policy']
    statuses = ['Draft', 'Under Review', 'Approved', 'Published']
    categories = ['Security', 'Compliance', 'Operations']
    
    sample_policies = []
    for i in range(15):
        created_date = datetime.datetime.now() - timedelta(days=random.randint(30, 365))
        status = random.choice(statuses)
        
        policy = {
            'id': f'POL-{2024:04d}-{i+1:03d}',
            'title': f'{random.choice(policy_types)}',
            'version': f'{random.randint(1, 5)}.{random.randint(0, 9)}',
            'category': random.choice(categories),
            'status': status,
            'owner': f'Department {random.randint(1, 5)}',
            'created_date': created_date,
            'review_date': created_date + timedelta(days=365),
            'risk_level': random.choice(['Low', 'Medium', 'High', 'Critical']),
            'training_completion': random.randint(70, 100),
            'violations': random.randint(0, 10)
        }
        sample_policies.append(policy)
    
    return sample_policies

if not st.session_state.policies:
    st.session_state.policies = generate_sample_data()

def calculate_metrics(policies):
    df = pd.DataFrame(policies)
    return {
        'total_policies': len(policies),
        'active_policies': len(df[df['status'].isin(['Approved', 'Published'])]),
        'draft_policies': len(df[df['status'] == 'Draft']),
        'avg_training_completion': df['training_completion'].mean(),
        'total_violations': df['violations'].sum()
    }

def main():
    st.markdown('<h1 class="main-header">Policy Management System</h1>', unsafe_allow_html=True)
    
    page = st.sidebar.selectbox("Navigation", ["Dashboard", "Policy Management", "Analytics"])
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Policy Management":
        show_policy_management()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    st.header("Policy Management Dashboard")
    
    metrics = calculate_metrics(st.session_state.policies)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Policies", metrics['total_policies'])
    with col2: st.metric("Active Policies", metrics['active_policies'])
    with col3: st.metric("Draft Policies", metrics['draft_policies'])
    with col4: st.metric("Avg Training", f"{metrics['avg_training_completion']:.1f}%")
    
    df = pd.DataFrame(st.session_state.policies)
    
    col1, col2 = st.columns(2)
    with col1:
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts)
        st.write("Policy Status Distribution")
    
    with col2:
        risk_counts = df['risk_level'].value_counts()
        st.bar_chart(risk_counts)
        st.write("Policy Risk Levels")

def show_policy_management():
    st.header("Policy Management")
    
    with st.expander("Add New Policy"):
        with st.form("new_policy"):
            title = st.text_input("Policy Title")
            category = st.selectbox("Category", ['Security', 'Compliance', 'Operations'])
            owner = st.text_input("Policy Owner")
            
            if st.form_submit_button("Create Policy"):
                if title:
                    new_policy = {
                        'id': f'POL-{datetime.datetime.now().year:04d}-{len(st.session_state.policies)+1:03d}',
                        'title': title,
                        'version': '1.0',
                        'category': category,
                        'status': 'Draft',
                        'owner': owner,
                        'created_date': datetime.datetime.now(),
                        'review_date': datetime.datetime.now() + timedelta(days=365),
                        'risk_level': 'Medium',
                        'training_completion': 0,
                        'violations': 0
                    }
                    st.session_state.policies.append(new_policy)
                    st.success("Policy created!")
                    st.rerun()
    
    # Policy list
    st.subheader("Policy List")
    
    status_filter = st.selectbox("Status Filter", ['All'] + list(set([p['status'] for p in st.session_state.policies])))
    
    filtered_policies = st.session_state.policies
    if status_filter != 'All':
        filtered_policies = [p for p in filtered_policies if p['status'] == status_filter]
    
    for policy in filtered_policies:
        with st.expander(f"{policy['id']} - {policy['title']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Status:** {policy['status']}")
                st.write(f"**Category:** {policy['category']}")
                st.write(f"**Owner:** {policy['owner']}")
            with col2:
                st.write(f"**Risk Level:** {policy['risk_level']}")
                st.write(f"**Training:** {policy['training_completion']}%")
                st.write(f"**Violations:** {policy['violations']}")

def show_analytics():
    st.header("Analytics")
    
    df = pd.DataFrame(st.session_state.policies)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Training Completion by Category:**")
        training_by_category = df.groupby('category')['training_completion'].mean()
        st.bar_chart(training_by_category)
    
    with col2:
        st.write("**Violations by Risk Level:**")
        violations_by_risk = df.groupby('risk_level')['violations'].sum()
        st.bar_chart(violations_by_risk)

if __name__ == "__main__":
    main()
