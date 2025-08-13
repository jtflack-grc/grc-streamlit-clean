import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import random
import json

# Page configuration
st.set_page_config(
    page_title="Security Awareness Training Tracker",
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

# Initialize session state
if 'training_courses' not in st.session_state:
    st.session_state.training_courses = []
if 'employees' not in st.session_state:
    st.session_state.employees = []
if 'training_sessions' not in st.session_state:
    st.session_state.training_sessions = []
if 'completions' not in st.session_state:
    st.session_state.completions = []
if 'campaigns' not in st.session_state:
    st.session_state.campaigns = []

def generate_sample_data():
    """Generate sample security awareness training data"""
    training_courses = [
        {
            'id': 'TC-2024-001',
            'title': 'Phishing Awareness Training',
            'category': 'Social Engineering',
            'duration_minutes': 30,
            'difficulty': 'Beginner',
            'description': 'Learn to identify and avoid phishing attacks',
            'learning_objectives': ['Identify phishing emails', 'Report suspicious activity', 'Protect personal information'],
            'required_frequency': 'Annual',
            'compliance_frameworks': ['SOC 2', 'ISO 27001', 'PCI DSS'],
            'status': 'Active',
            'created_date': datetime.datetime.now() - timedelta(days=365)
        },
        {
            'id': 'TC-2024-002',
            'title': 'Password Security Best Practices',
            'category': 'Access Control',
            'duration_minutes': 20,
            'difficulty': 'Beginner',
            'description': 'Learn secure password creation and management',
            'learning_objectives': ['Create strong passwords', 'Use password managers', 'Enable 2FA'],
            'required_frequency': 'Annual',
            'compliance_frameworks': ['SOC 2', 'ISO 27001', 'NIST CSF'],
            'status': 'Active',
            'created_date': datetime.datetime.now() - timedelta(days=300)
        },
        {
            'id': 'TC-2024-003',
            'title': 'Data Protection and Privacy',
            'category': 'Data Security',
            'duration_minutes': 45,
            'difficulty': 'Intermediate',
            'description': 'Understanding data protection requirements and best practices',
            'learning_objectives': ['GDPR compliance', 'Data classification', 'Secure data handling'],
            'required_frequency': 'Annual',
            'compliance_frameworks': ['GDPR', 'CCPA', 'SOC 2'],
            'status': 'Active',
            'created_date': datetime.datetime.now() - timedelta(days=250)
        },
        {
            'id': 'TC-2024-004',
            'title': 'Incident Response Awareness',
            'category': 'Incident Response',
            'duration_minutes': 25,
            'difficulty': 'Intermediate',
            'description': 'What to do when you suspect a security incident',
            'learning_objectives': ['Recognize security incidents', 'Report procedures', 'Containment steps'],
            'required_frequency': 'Annual',
            'compliance_frameworks': ['SOC 2', 'ISO 27001', 'NIST CSF'],
            'status': 'Active',
            'created_date': datetime.datetime.now() - timedelta(days=200)
        },
        {
            'id': 'TC-2024-005',
            'title': 'Mobile Device Security',
            'category': 'Device Security',
            'duration_minutes': 35,
            'difficulty': 'Beginner',
            'description': 'Securing mobile devices and protecting corporate data',
            'learning_objectives': ['Device encryption', 'App security', 'Public WiFi risks'],
            'required_frequency': 'Annual',
            'compliance_frameworks': ['SOC 2', 'ISO 27001', 'BYOD Policy'],
            'status': 'Active',
            'created_date': datetime.datetime.now() - timedelta(days=150)
        }
    ]
    
    employees = [
        {
            'id': 'EMP-001',
            'name': 'John Smith',
            'email': 'john.smith@company.com',
            'department': 'IT',
            'role': 'System Administrator',
            'hire_date': datetime.datetime(2020, 3, 15),
            'training_level': 'Advanced',
            'status': 'Active'
        },
        {
            'id': 'EMP-002',
            'name': 'Sarah Johnson',
            'email': 'sarah.johnson@company.com',
            'department': 'HR',
            'role': 'HR Manager',
            'hire_date': datetime.datetime(2019, 7, 22),
            'training_level': 'Intermediate',
            'status': 'Active'
        },
        {
            'id': 'EMP-003',
            'name': 'Mike Chen',
            'email': 'mike.chen@company.com',
            'department': 'Finance',
            'role': 'Financial Analyst',
            'hire_date': datetime.datetime(2021, 1, 10),
            'training_level': 'Beginner',
            'status': 'Active'
        },
        {
            'id': 'EMP-004',
            'name': 'Lisa Davis',
            'email': 'lisa.davis@company.com',
            'department': 'Marketing',
            'role': 'Marketing Specialist',
            'hire_date': datetime.datetime(2022, 5, 8),
            'training_level': 'Beginner',
            'status': 'Active'
        },
        {
            'id': 'EMP-005',
            'name': 'David Wilson',
            'email': 'david.wilson@company.com',
            'department': 'IT',
            'role': 'Security Engineer',
            'hire_date': datetime.datetime(2018, 11, 12),
            'training_level': 'Advanced',
            'status': 'Active'
        }
    ]
    
    training_sessions = [
        {
            'id': 'TS-2024-001',
            'course_id': 'TC-2024-001',
            'session_name': 'Phishing Awareness Q1 2024',
            'start_date': datetime.datetime.now() - timedelta(days=90),
            'end_date': datetime.datetime.now() - timedelta(days=60),
            'instructor': 'Security Team',
            'delivery_method': 'Online',
            'max_participants': 100,
            'status': 'Completed',
            'completion_rate': 0.85
        },
        {
            'id': 'TS-2024-002',
            'course_id': 'TC-2024-002',
            'session_name': 'Password Security Q1 2024',
            'start_date': datetime.datetime.now() - timedelta(days=75),
            'end_date': datetime.datetime.now() - timedelta(days=45),
            'instructor': 'IT Security Team',
            'delivery_method': 'Online',
            'max_participants': 100,
            'status': 'Completed',
            'completion_rate': 0.92
        },
        {
            'id': 'TS-2024-003',
            'course_id': 'TC-2024-003',
            'session_name': 'Data Protection Q2 2024',
            'start_date': datetime.datetime.now() - timedelta(days=30),
            'end_date': datetime.datetime.now() + timedelta(days=30),
            'instructor': 'Compliance Team',
            'delivery_method': 'Hybrid',
            'max_participants': 50,
            'status': 'In Progress',
            'completion_rate': 0.45
        }
    ]
    
    completions = [
        {
            'id': 'COMP-001',
            'employee_id': 'EMP-001',
            'course_id': 'TC-2024-001',
            'session_id': 'TS-2024-001',
            'completion_date': datetime.datetime.now() - timedelta(days=70),
            'score': 95,
            'status': 'Passed',
            'certificate_issued': True,
            'next_due_date': datetime.datetime.now() + timedelta(days=275)
        },
        {
            'id': 'COMP-002',
            'employee_id': 'EMP-002',
            'course_id': 'TC-2024-001',
            'session_id': 'TS-2024-001',
            'completion_date': datetime.datetime.now() - timedelta(days=68),
            'score': 88,
            'status': 'Passed',
            'certificate_issued': True,
            'next_due_date': datetime.datetime.now() + timedelta(days=277)
        },
        {
            'id': 'COMP-003',
            'employee_id': 'EMP-003',
            'course_id': 'TC-2024-002',
            'session_id': 'TS-2024-002',
            'completion_date': datetime.datetime.now() - timedelta(days=50),
            'score': 92,
            'status': 'Passed',
            'certificate_issued': True,
            'next_due_date': datetime.datetime.now() + timedelta(days=315)
        },
        {
            'id': 'COMP-004',
            'employee_id': 'EMP-004',
            'course_id': 'TC-2024-003',
            'session_id': 'TS-2024-003',
            'completion_date': datetime.datetime.now() - timedelta(days=10),
            'score': 78,
            'status': 'Passed',
            'certificate_issued': True,
            'next_due_date': datetime.datetime.now() + timedelta(days=355)
        },
        {
            'id': 'COMP-005',
            'employee_id': 'EMP-005',
            'course_id': 'TC-2024-001',
            'session_id': 'TS-2024-001',
            'completion_date': datetime.datetime.now() - timedelta(days=65),
            'score': 100,
            'status': 'Passed',
            'certificate_issued': True,
            'next_due_date': datetime.datetime.now() + timedelta(days=280)
        }
    ]
    
    campaigns = [
        {
            'id': 'CAM-2024-001',
            'name': 'Q1 2024 Security Awareness Campaign',
            'description': 'Comprehensive security awareness training for Q1 2024',
            'start_date': datetime.datetime.now() - timedelta(days=90),
            'end_date': datetime.datetime.now() - timedelta(days=30),
            'target_audience': 'All Employees',
            'courses': ['TC-2024-001', 'TC-2024-002'],
            'status': 'Completed',
            'completion_rate': 0.87,
            'budget': 5000
        },
        {
            'id': 'CAM-2024-002',
            'name': 'Q2 2024 Data Protection Focus',
            'description': 'Data protection and privacy training campaign',
            'start_date': datetime.datetime.now() - timedelta(days=30),
            'end_date': datetime.datetime.now() + timedelta(days=60),
            'target_audience': 'All Employees',
            'courses': ['TC-2024-003', 'TC-2024-004'],
            'status': 'In Progress',
            'completion_rate': 0.45,
            'budget': 3000
        }
    ]
    
    return training_courses, employees, training_sessions, completions, campaigns

def main():
    st.markdown('<h1 class="main-header">Security Awareness Training Tracker</h1>', unsafe_allow_html=True)
    st.markdown("Comprehensive platform for managing security training programs, tracking employee completion, and ensuring compliance")
    
    # Initialize sample data
    if not st.session_state.training_courses:
        courses, employees, sessions, completions, campaigns = generate_sample_data()
        st.session_state.training_courses = courses
        st.session_state.employees = employees
        st.session_state.training_sessions = sessions
        st.session_state.completions = completions
        st.session_state.campaigns = campaigns
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Dashboard", "Training Courses", "Employees", "Training Sessions", "Completions", "Campaigns", "Reports", "Analytics"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Training Courses":
        show_training_courses()
    elif page == "Employees":
        show_employees()
    elif page == "Training Sessions":
        show_training_sessions()
    elif page == "Completions":
        show_completions()
    elif page == "Campaigns":
        show_campaigns()
    elif page == "Reports":
        show_reports()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    st.header("📊 Training Dashboard")
    
    # Calculate key metrics
    total_employees = len(st.session_state.employees)
    total_courses = len(st.session_state.training_courses)
    total_completions = len(st.session_state.completions)
    active_sessions = len([s for s in st.session_state.training_sessions if s['status'] == 'In Progress'])
    
    # Calculate completion rates
    completion_rate = total_completions / (total_employees * total_courses) * 100 if total_employees * total_courses > 0 else 0
    overdue_trainings = len([c for c in st.session_state.completions if c['next_due_date'] < datetime.datetime.now()])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Employees", total_employees)
        st.metric("Active Sessions", active_sessions)
    
    with col2:
        st.metric("Training Courses", total_courses)
        st.metric("Total Completions", total_completions)
    
    with col3:
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
        st.metric("Overdue Trainings", overdue_trainings)
    
    with col4:
        st.metric("Active Campaigns", len([c for c in st.session_state.campaigns if c['status'] == 'In Progress']))
        st.metric("Certificates Issued", len([c for c in st.session_state.completions if c['certificate_issued']]))
    
    # Training progress overview
    st.subheader("Training Progress Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Course completion by department
        df_completions = pd.DataFrame(st.session_state.completions)
        df_employees = pd.DataFrame(st.session_state.employees)
        
        if not df_completions.empty and not df_employees.empty:
            # Merge completions with employee data
            df_merged = df_completions.merge(df_employees, left_on='employee_id', right_on='id', how='left')
            dept_completions = df_merged['department'].value_counts()
            
            fig = px.pie(values=dept_completions.values, names=dept_completions.index, 
                        title="Completions by Department")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Training scores distribution
        if not df_completions.empty:
            fig = px.histogram(df_completions, x='score', nbins=10, 
                             title="Training Score Distribution",
                             labels={'score': 'Score', 'count': 'Number of Completions'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent completions
    st.subheader("Recent Training Completions")
    recent_completions = sorted(st.session_state.completions, key=lambda x: x['completion_date'], reverse=True)[:5]
    
    if recent_completions:
        for completion in recent_completions:
            employee = next((e for e in st.session_state.employees if e['id'] == completion['employee_id']), None)
            course = next((c for c in st.session_state.training_courses if c['id'] == completion['course_id']), None)
            
            if employee and course:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    st.write(f"**{employee['name']}** ({employee['department']})")
                with col2:
                    st.write(f"**{course['title']}**")
                with col3:
                    st.write(f"Score: {completion['score']}%")
                with col4:
                    if completion['status'] == 'Passed':
                        st.write("✅ Passed")
                    else:
                        st.write("❌ Failed")
                st.divider()

def show_training_courses():
    st.header("📚 Training Courses")
    
    # Add new course
    with st.expander("Add New Training Course"):
        with st.form("new_course"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Course Title")
                category = st.selectbox("Category", ["Social Engineering", "Access Control", "Data Security", "Incident Response", "Device Security", "Other"])
                duration = st.number_input("Duration (minutes)", min_value=5, max_value=480, value=30)
                difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
            
            with col2:
                frequency = st.selectbox("Required Frequency", ["One-time", "Monthly", "Quarterly", "Semi-Annual", "Annual"])
                frameworks = st.multiselect("Compliance Frameworks", ["SOC 2", "ISO 27001", "PCI DSS", "GDPR", "HIPAA", "NIST CSF", "CCPA"])
                status = st.selectbox("Status", ["Active", "Inactive", "Draft"])
            
            description = st.text_area("Course Description")
            objectives = st.text_area("Learning Objectives (one per line)")
            
            if st.form_submit_button("Add Course"):
                new_course = {
                    'id': f'TC-{datetime.datetime.now().year}-{len(st.session_state.training_courses)+1:03d}',
                    'title': title,
                    'category': category,
                    'duration_minutes': duration,
                    'difficulty': difficulty,
                    'description': description,
                    'learning_objectives': [obj.strip() for obj in objectives.split('\n') if obj.strip()],
                    'required_frequency': frequency,
                    'compliance_frameworks': frameworks,
                    'status': status,
                    'created_date': datetime.datetime.now()
                }
                st.session_state.training_courses.append(new_course)
                st.success("Training course added successfully!")
    
    # Display courses
    df = pd.DataFrame(st.session_state.training_courses)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(df['category'].unique()))
    with col2:
        difficulty_filter = st.selectbox("Filter by Difficulty", ["All"] + list(df['difficulty'].unique()))
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    if difficulty_filter != "All":
        filtered_df = filtered_df[filtered_df['difficulty'] == difficulty_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Course overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Courses by Category")
        category_counts = df['category'].value_counts()
        fig = px.pie(values=category_counts.values, names=category_counts.index, 
                    title="Training Courses by Category")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Courses by Difficulty")
        difficulty_counts = df['difficulty'].value_counts()
        fig = px.bar(x=difficulty_counts.index, y=difficulty_counts.values, 
                    title="Courses by Difficulty Level")
        st.plotly_chart(fig, use_container_width=True)

def show_employees():
    st.header("👥 Employees")
    
    # Add new employee
    with st.expander("Add New Employee"):
        with st.form("new_employee"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Employee Name")
                email = st.text_input("Email")
                department = st.selectbox("Department", ["IT", "HR", "Finance", "Marketing", "Sales", "Operations", "Legal", "Other"])
            
            with col2:
                role = st.text_input("Role/Position")
                hire_date = st.date_input("Hire Date")
                training_level = st.selectbox("Training Level", ["Beginner", "Intermediate", "Advanced"])
                status = st.selectbox("Status", ["Active", "Inactive", "Terminated"])
            
            if st.form_submit_button("Add Employee"):
                new_employee = {
                    'id': f'EMP-{len(st.session_state.employees)+1:03d}',
                    'name': name,
                    'email': email,
                    'department': department,
                    'role': role,
                    'hire_date': datetime.datetime.combine(hire_date, datetime.time()),
                    'training_level': training_level,
                    'status': status
                }
                st.session_state.employees.append(new_employee)
                st.success("Employee added successfully!")
    
    # Display employees
    df = pd.DataFrame(st.session_state.employees)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        dept_filter = st.selectbox("Filter by Department", ["All"] + list(df['department'].unique()))
    with col2:
        level_filter = st.selectbox("Filter by Training Level", ["All"] + list(df['training_level'].unique()))
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if dept_filter != "All":
        filtered_df = filtered_df[filtered_df['department'] == dept_filter]
    if level_filter != "All":
        filtered_df = filtered_df[filtered_df['training_level'] == level_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Employee overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Employees by Department")
        dept_counts = df['department'].value_counts()
        fig = px.pie(values=dept_counts.values, names=dept_counts.index, 
                    title="Employee Distribution by Department")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Employees by Training Level")
        level_counts = df['training_level'].value_counts()
        fig = px.bar(x=level_counts.index, y=level_counts.values, 
                    title="Employees by Training Level")
        st.plotly_chart(fig, use_container_width=True)

def show_training_sessions():
    st.header("📅 Training Sessions")
    
    # Add new session
    with st.expander("Add New Training Session"):
        with st.form("new_session"):
            col1, col2 = st.columns(2)
            with col1:
                course_id = st.selectbox("Course", [c['id'] for c in st.session_state.training_courses])
                session_name = st.text_input("Session Name")
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
            
            with col2:
                instructor = st.text_input("Instructor")
                delivery_method = st.selectbox("Delivery Method", ["Online", "In-Person", "Hybrid", "Self-Paced"])
                max_participants = st.number_input("Max Participants", min_value=1, max_value=1000, value=50)
                status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed", "Cancelled"])
            
            if st.form_submit_button("Add Session"):
                new_session = {
                    'id': f'TS-{datetime.datetime.now().year}-{len(st.session_state.training_sessions)+1:03d}',
                    'course_id': course_id,
                    'session_name': session_name,
                    'start_date': datetime.datetime.combine(start_date, datetime.time(9, 0)),
                    'end_date': datetime.datetime.combine(end_date, datetime.time(17, 0)),
                    'instructor': instructor,
                    'delivery_method': delivery_method,
                    'max_participants': max_participants,
                    'status': status,
                    'completion_rate': 0.0
                }
                st.session_state.training_sessions.append(new_session)
                st.success("Training session added successfully!")
    
    # Display sessions
    df = pd.DataFrame(st.session_state.training_sessions)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col2:
        method_filter = st.selectbox("Filter by Delivery Method", ["All"] + list(df['delivery_method'].unique()))
    with col3:
        instructor_filter = st.selectbox("Filter by Instructor", ["All"] + list(df['instructor'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if method_filter != "All":
        filtered_df = filtered_df[filtered_df['delivery_method'] == method_filter]
    if instructor_filter != "All":
        filtered_df = filtered_df[filtered_df['instructor'] == instructor_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Session overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sessions by Status")
        status_counts = df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Training Sessions by Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sessions by Delivery Method")
        method_counts = df['delivery_method'].value_counts()
        fig = px.bar(x=method_counts.index, y=method_counts.values, 
                    title="Sessions by Delivery Method")
        st.plotly_chart(fig, use_container_width=True)

def show_completions():
    st.header("✅ Training Completions")
    
    # Add new completion
    with st.expander("Add New Completion"):
        with st.form("new_completion"):
            col1, col2 = st.columns(2)
            with col1:
                employee_id = st.selectbox("Employee", [e['id'] for e in st.session_state.employees])
                course_id = st.selectbox("Course", [c['id'] for c in st.session_state.training_courses])
                session_id = st.selectbox("Session", [s['id'] for s in st.session_state.training_sessions])
                completion_date = st.date_input("Completion Date")
            
            with col2:
                score = st.number_input("Score (%)", min_value=0, max_value=100, value=80)
                status = st.selectbox("Status", ["Passed", "Failed", "In Progress"])
                certificate_issued = st.checkbox("Certificate Issued")
                next_due_date = st.date_input("Next Due Date")
            
            if st.form_submit_button("Add Completion"):
                new_completion = {
                    'id': f'COMP-{len(st.session_state.completions)+1:03d}',
                    'employee_id': employee_id,
                    'course_id': course_id,
                    'session_id': session_id,
                    'completion_date': datetime.datetime.combine(completion_date, datetime.time()),
                    'score': score,
                    'status': status,
                    'certificate_issued': certificate_issued,
                    'next_due_date': datetime.datetime.combine(next_due_date, datetime.time())
                }
                st.session_state.completions.append(new_completion)
                st.success("Training completion added successfully!")
    
    # Display completions
    df = pd.DataFrame(st.session_state.completions)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col2:
        score_filter = st.selectbox("Filter by Score Range", ["All", "90-100", "80-89", "70-79", "60-69", "Below 60"])
    with col3:
        certificate_filter = st.selectbox("Filter by Certificate", ["All", "Issued", "Not Issued"])
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if score_filter != "All":
        if score_filter == "90-100":
            filtered_df = filtered_df[(filtered_df['score'] >= 90) & (filtered_df['score'] <= 100)]
        elif score_filter == "80-89":
            filtered_df = filtered_df[(filtered_df['score'] >= 80) & (filtered_df['score'] < 90)]
        elif score_filter == "70-79":
            filtered_df = filtered_df[(filtered_df['score'] >= 70) & (filtered_df['score'] < 80)]
        elif score_filter == "60-69":
            filtered_df = filtered_df[(filtered_df['score'] >= 60) & (filtered_df['score'] < 70)]
        elif score_filter == "Below 60":
            filtered_df = filtered_df[filtered_df['score'] < 60]
    if certificate_filter != "All":
        if certificate_filter == "Issued":
            filtered_df = filtered_df[filtered_df['certificate_issued'] == True]
        else:
            filtered_df = filtered_df[filtered_df['certificate_issued'] == False]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Completion overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Completions by Status")
        status_counts = df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Training Completions by Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Score Distribution")
        fig = px.histogram(df, x='score', nbins=10, 
                         title="Training Score Distribution",
                         labels={'score': 'Score', 'count': 'Number of Completions'})
        st.plotly_chart(fig, use_container_width=True)

def show_campaigns():
    st.header("📢 Training Campaigns")
    
    # Add new campaign
    with st.expander("Add New Campaign"):
        with st.form("new_campaign"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Campaign Name")
                description = st.text_area("Description")
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
            
            with col2:
                target_audience = st.selectbox("Target Audience", ["All Employees", "IT Staff", "Management", "New Hires", "Specific Department"])
                courses = st.multiselect("Courses", [c['id'] for c in st.session_state.training_courses])
                status = st.selectbox("Status", ["Planned", "In Progress", "Completed", "Cancelled"])
                budget = st.number_input("Budget ($)", min_value=0, value=1000)
            
            if st.form_submit_button("Add Campaign"):
                new_campaign = {
                    'id': f'CAM-{datetime.datetime.now().year}-{len(st.session_state.campaigns)+1:03d}',
                    'name': name,
                    'description': description,
                    'start_date': datetime.datetime.combine(start_date, datetime.time()),
                    'end_date': datetime.datetime.combine(end_date, datetime.time()),
                    'target_audience': target_audience,
                    'courses': courses,
                    'status': status,
                    'completion_rate': 0.0,
                    'budget': budget
                }
                st.session_state.campaigns.append(new_campaign)
                st.success("Training campaign added successfully!")
    
    # Display campaigns
    df = pd.DataFrame(st.session_state.campaigns)
    st.dataframe(df, use_container_width=True)
    
    # Campaign overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Campaigns by Status")
        status_counts = df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Training Campaigns by Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Campaign Budgets")
        if not df.empty:
            fig = px.bar(df, x='name', y='budget', 
                        title="Campaign Budgets",
                        labels={'budget': 'Budget ($)', 'name': 'Campaign'})
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("📊 Reports & Analytics")
    
    # Report options
    report_type = st.selectbox("Select Report Type", [
        "Training Completion Report",
        "Employee Training Status",
        "Course Performance Report",
        "Compliance Report",
        "Campaign Effectiveness Report"
    ])
    
    if report_type == "Training Completion Report":
        st.subheader("Training Completion Report")
        
        df_completions = pd.DataFrame(st.session_state.completions)
        df_employees = pd.DataFrame(st.session_state.employees)
        df_courses = pd.DataFrame(st.session_state.training_courses)
        
        if not df_completions.empty:
            # Merge data
            df_merged = df_completions.merge(df_employees, left_on='employee_id', right_on='id', how='left')
            df_merged = df_merged.merge(df_courses, left_on='course_id', right_on='id', how='left')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Completion Summary**")
                st.write(f"• Total Completions: {len(df_completions)}")
                st.write(f"• Pass Rate: {len(df_completions[df_completions['status'] == 'Passed']) / len(df_completions) * 100:.1f}%")
                st.write(f"• Average Score: {df_completions['score'].mean():.1f}%")
                st.write(f"• Certificates Issued: {len(df_completions[df_completions['certificate_issued'] == True])}")
            
            with col2:
                st.write("**Department Performance**")
                dept_stats = df_merged.groupby('department').agg({
                    'score': ['mean', 'count'],
                    'status': lambda x: (x == 'Passed').sum()
                }).round(2)
                st.dataframe(dept_stats)
    
    # Export functionality
    st.subheader("Export Data")
    export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
    
    if st.button("Export Training Data"):
        if export_format == "CSV":
            # Export completions to CSV
            df_completions = pd.DataFrame(st.session_state.completions)
            csv = df_completions.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="training_completions.csv",
                mime="text/csv"
            )

def show_analytics():
    st.header("📈 Analytics & Insights")
    
    # Calculate metrics
    total_employees = len(st.session_state.employees)
    total_courses = len(st.session_state.training_courses)
    total_completions = len(st.session_state.completions)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Employees", total_employees)
        st.metric("Active Courses", len([c for c in st.session_state.training_courses if c['status'] == 'Active']))
    
    with col2:
        st.metric("Total Courses", total_courses)
        st.metric("Total Completions", total_completions)
    
    with col3:
        completion_rate = total_completions / (total_employees * total_courses) * 100 if total_employees * total_courses > 0 else 0
        st.metric("Overall Completion Rate", f"{completion_rate:.1f}%")
        st.metric("Active Sessions", len([s for s in st.session_state.training_sessions if s['status'] == 'In Progress']))
    
    with col4:
        avg_score = np.mean([c['score'] for c in st.session_state.completions]) if st.session_state.completions else 0
        st.metric("Average Score", f"{avg_score:.1f}%")
        st.metric("Overdue Trainings", len([c for c in st.session_state.completions if c['next_due_date'] < datetime.datetime.now()]))
    
    # Training trends
    st.subheader("Training Trends")
    df_completions = pd.DataFrame(st.session_state.completions)
    if not df_completions.empty:
        df_completions['completion_date'] = pd.to_datetime(df_completions['completion_date'])
        df_completions['month'] = df_completions['completion_date'].dt.to_period('M')
        
        monthly_completions = df_completions.groupby('month').size().reset_index(name='count')
        monthly_completions['month'] = monthly_completions['month'].astype(str)
        
        fig = px.line(monthly_completions, x='month', y='count', 
                      title="Monthly Training Completions",
                      labels={'count': 'Number of Completions', 'month': 'Month'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Course performance
    st.subheader("Course Performance")
    if not df_completions.empty:
        df_courses = pd.DataFrame(st.session_state.training_courses)
        df_merged = df_completions.merge(df_courses, left_on='course_id', right_on='id', how='left')
        
        course_performance = df_merged.groupby('title').agg({
            'score': 'mean',
            'status': lambda x: (x == 'Passed').sum()
        }).round(2)
        
        fig = px.bar(course_performance, x=course_performance.index, y='score', 
                    title="Average Course Scores",
                    labels={'score': 'Average Score (%)', 'title': 'Course'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
