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
    page_title="Asset Management System",
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
if 'assets' not in st.session_state:
    st.session_state.assets = []
if 'asset_categories' not in st.session_state:
    st.session_state.asset_categories = []
if 'asset_locations' not in st.session_state:
    st.session_state.asset_locations = []
if 'asset_maintenance' not in st.session_state:
    st.session_state.asset_maintenance = []
if 'asset_licenses' not in st.session_state:
    st.session_state.asset_licenses = []

def generate_sample_data():
    """Generate sample asset management data"""
    asset_categories = [
        {'id': 'CAT-001', 'name': 'Laptops', 'description': 'Portable computers and laptops'},
        {'id': 'CAT-002', 'name': 'Desktops', 'description': 'Desktop computers and workstations'},
        {'id': 'CAT-003', 'name': 'Servers', 'description': 'Server hardware and infrastructure'},
        {'id': 'CAT-004', 'name': 'Network Equipment', 'description': 'Routers, switches, and network devices'},
        {'id': 'CAT-005', 'name': 'Mobile Devices', 'description': 'Smartphones and tablets'},
        {'id': 'CAT-006', 'name': 'Software', 'description': 'Software licenses and applications'},
        {'id': 'CAT-007', 'name': 'Peripherals', 'description': 'Monitors, printers, and accessories'}
    ]
    
    asset_locations = [
        {'id': 'LOC-001', 'name': 'Headquarters', 'address': '123 Main St, City, State', 'type': 'Office'},
        {'id': 'LOC-002', 'name': 'Data Center', 'address': '456 Tech Blvd, City, State', 'type': 'Data Center'},
        {'id': 'LOC-003', 'name': 'Branch Office 1', 'address': '789 Branch Ave, City, State', 'type': 'Office'},
        {'id': 'LOC-004', 'name': 'Remote Office', 'address': '321 Remote Rd, City, State', 'type': 'Office'},
        {'id': 'LOC-005', 'name': 'Warehouse', 'address': '654 Storage Way, City, State', 'type': 'Warehouse'}
    ]
    
    assets = [
        {
            'id': 'AST-2024-001',
            'name': 'Dell Latitude 5520',
            'category_id': 'CAT-001',
            'location_id': 'LOC-001',
            'asset_tag': 'LAP-001',
            'serial_number': 'DL123456789',
            'model': 'Latitude 5520',
            'manufacturer': 'Dell',
            'purchase_date': datetime.datetime.now() - timedelta(days=365),
            'warranty_expiry': datetime.datetime.now() + timedelta(days=730),
            'purchase_cost': 1200.00,
            'current_value': 800.00,
            'status': 'In Use',
            'assigned_to': 'John Smith',
            'department': 'IT',
            'criticality': 'High',
            'last_updated': datetime.datetime.now() - timedelta(days=5)
        },
        {
            'id': 'AST-2024-002',
            'name': 'HP EliteDesk 800',
            'category_id': 'CAT-002',
            'location_id': 'LOC-001',
            'asset_tag': 'DESK-001',
            'serial_number': 'HP987654321',
            'model': 'EliteDesk 800 G5',
            'manufacturer': 'HP',
            'purchase_date': datetime.datetime.now() - timedelta(days=400),
            'warranty_expiry': datetime.datetime.now() + timedelta(days=400),
            'purchase_cost': 800.00,
            'current_value': 500.00,
            'status': 'In Use',
            'assigned_to': 'Sarah Johnson',
            'department': 'HR',
            'criticality': 'Medium',
            'last_updated': datetime.datetime.now() - timedelta(days=10)
        },
        {
            'id': 'AST-2024-003',
            'name': 'Cisco Catalyst 9300',
            'category_id': 'CAT-004',
            'location_id': 'LOC-002',
            'asset_tag': 'NET-001',
            'serial_number': 'CS123456789',
            'model': 'Catalyst 9300-48P',
            'manufacturer': 'Cisco',
            'purchase_date': datetime.datetime.now() - timedelta(days=200),
            'warranty_expiry': datetime.datetime.now() + timedelta(days=1095),
            'purchase_cost': 15000.00,
            'current_value': 12000.00,
            'status': 'In Use',
            'assigned_to': 'Network Team',
            'department': 'IT',
            'criticality': 'Critical',
            'last_updated': datetime.datetime.now() - timedelta(days=2)
        },
        {
            'id': 'AST-2024-004',
            'name': 'Dell PowerEdge R740',
            'category_id': 'CAT-003',
            'location_id': 'LOC-002',
            'asset_tag': 'SRV-001',
            'serial_number': 'DL987654321',
            'model': 'PowerEdge R740',
            'manufacturer': 'Dell',
            'purchase_date': datetime.datetime.now() - timedelta(days=150),
            'warranty_expiry': datetime.datetime.now() + timedelta(days=1095),
            'purchase_cost': 8000.00,
            'current_value': 6000.00,
            'status': 'In Use',
            'assigned_to': 'Server Team',
            'department': 'IT',
            'criticality': 'Critical',
            'last_updated': datetime.datetime.now() - timedelta(days=1)
        },
        {
            'id': 'AST-2024-005',
            'name': 'iPhone 15 Pro',
            'category_id': 'CAT-005',
            'location_id': 'LOC-001',
            'asset_tag': 'MOB-001',
            'serial_number': 'IP123456789',
            'model': 'iPhone 15 Pro',
            'manufacturer': 'Apple',
            'purchase_date': datetime.datetime.now() - timedelta(days=100),
            'warranty_expiry': datetime.datetime.now() + timedelta(days=365),
            'purchase_cost': 999.00,
            'current_value': 800.00,
            'status': 'In Use',
            'assigned_to': 'Mike Chen',
            'department': 'Finance',
            'criticality': 'Medium',
            'last_updated': datetime.datetime.now() - timedelta(days=15)
        }
    ]
    
    asset_maintenance = [
        {
            'id': 'MAINT-001',
            'asset_id': 'AST-2024-001',
            'maintenance_type': 'Preventive',
            'description': 'Regular system maintenance and updates',
            'scheduled_date': datetime.datetime.now() + timedelta(days=30),
            'completed_date': None,
            'technician': 'IT Support Team',
            'cost': 50.00,
            'status': 'Scheduled',
            'notes': 'Standard quarterly maintenance'
        },
        {
            'id': 'MAINT-002',
            'asset_id': 'AST-2024-003',
            'maintenance_type': 'Preventive',
            'description': 'Firmware update and configuration review',
            'scheduled_date': datetime.datetime.now() - timedelta(days=5),
            'completed_date': datetime.datetime.now() - timedelta(days=3),
            'technician': 'Network Engineer',
            'cost': 200.00,
            'status': 'Completed',
            'notes': 'Firmware updated successfully'
        },
        {
            'id': 'MAINT-003',
            'asset_id': 'AST-2024-002',
            'maintenance_type': 'Repair',
            'description': 'Hard drive replacement',
            'scheduled_date': datetime.datetime.now() - timedelta(days=20),
            'completed_date': datetime.datetime.now() - timedelta(days=18),
            'technician': 'Hardware Technician',
            'cost': 150.00,
            'status': 'Completed',
            'notes': 'SSD replaced, system restored'
        }
    ]
    
    asset_licenses = [
        {
            'id': 'LIC-001',
            'asset_id': 'AST-2024-001',
            'license_type': 'Operating System',
            'license_key': 'WIN-1234-5678-9012',
            'vendor': 'Microsoft',
            'product': 'Windows 11 Pro',
            'purchase_date': datetime.datetime.now() - timedelta(days=365),
            'expiry_date': datetime.datetime.now() + timedelta(days=730),
            'cost': 199.00,
            'status': 'Active',
            'seats': 1
        },
        {
            'id': 'LIC-002',
            'asset_id': 'AST-2024-001',
            'license_type': 'Antivirus',
            'license_key': 'AV-9876-5432-1098',
            'vendor': 'Symantec',
            'product': 'Endpoint Protection',
            'purchase_date': datetime.datetime.now() - timedelta(days=200),
            'expiry_date': datetime.datetime.now() + timedelta(days=165),
            'cost': 50.00,
            'status': 'Active',
            'seats': 1
        },
        {
            'id': 'LIC-003',
            'asset_id': 'AST-2024-003',
            'license_type': 'Network Management',
            'license_key': 'NET-5555-6666-7777',
            'vendor': 'Cisco',
            'product': 'DNA Center',
            'purchase_date': datetime.datetime.now() - timedelta(days=200),
            'expiry_date': datetime.datetime.now() + timedelta(days=1095),
            'cost': 5000.00,
            'status': 'Active',
            'seats': 1
        }
    ]
    
    return assets, asset_categories, asset_locations, asset_maintenance, asset_licenses

def main():
    st.markdown('<h1 class="main-header">Asset Management System</h1>', unsafe_allow_html=True)
    st.markdown("Comprehensive platform for managing IT assets, tracking lifecycle, and ensuring proper security controls")
    
    # Initialize sample data
    if not st.session_state.assets:
        assets, categories, locations, maintenance, licenses = generate_sample_data()
        st.session_state.assets = assets
        st.session_state.asset_categories = categories
        st.session_state.asset_locations = locations
        st.session_state.asset_maintenance = maintenance
        st.session_state.asset_licenses = licenses
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Dashboard", "Assets", "Categories", "Locations", "Maintenance", "Licenses", "Reports", "Analytics"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Assets":
        show_assets()
    elif page == "Categories":
        show_categories()
    elif page == "Locations":
        show_locations()
    elif page == "Maintenance":
        show_maintenance()
    elif page == "Licenses":
        show_licenses()
    elif page == "Reports":
        show_reports()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    st.header("📊 Asset Dashboard")
    
    # Calculate key metrics
    total_assets = len(st.session_state.assets)
    total_value = sum(asset['current_value'] for asset in st.session_state.assets)
    critical_assets = len([a for a in st.session_state.assets if a['criticality'] == 'Critical'])
    assets_in_use = len([a for a in st.session_state.assets if a['status'] == 'In Use'])
    
    # Calculate warranty and maintenance metrics
    warranty_expiring_soon = len([a for a in st.session_state.assets 
                                if a['warranty_expiry'] < datetime.datetime.now() + timedelta(days=90)])
    scheduled_maintenance = len([m for m in st.session_state.asset_maintenance 
                               if m['status'] == 'Scheduled'])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Assets", total_assets)
        st.metric("Critical Assets", critical_assets)
    
    with col2:
        st.metric("Total Value", f"${total_value:,.2f}")
        st.metric("Assets In Use", assets_in_use)
    
    with col3:
        st.metric("Warranty Expiring Soon", warranty_expiring_soon)
        st.metric("Scheduled Maintenance", scheduled_maintenance)
    
    with col4:
        avg_age = np.mean([(datetime.datetime.now() - asset['purchase_date']).days 
                          for asset in st.session_state.assets])
        st.metric("Average Asset Age", f"{avg_age:.0f} days")
        st.metric("Active Licenses", len([l for l in st.session_state.asset_licenses if l['status'] == 'Active']))
    
    # Asset overview
    st.subheader("Asset Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Assets by category
        df_assets = pd.DataFrame(st.session_state.assets)
        df_categories = pd.DataFrame(st.session_state.asset_categories)
        
        if not df_assets.empty and not df_categories.empty:
            df_merged = df_assets.merge(df_categories, left_on='category_id', right_on='id', how='left')
            category_counts = df_merged['name_y'].value_counts()
            
            fig = px.pie(values=category_counts.values, names=category_counts.index, 
                        title="Assets by Category")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Assets by criticality
        if not df_assets.empty:
            criticality_counts = df_assets['criticality'].value_counts()
            fig = px.bar(x=criticality_counts.index, y=criticality_counts.values, 
                        title="Assets by Criticality",
                        color=criticality_counts.index,
                        color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent activities
    st.subheader("Recent Asset Activities")
    recent_assets = sorted(st.session_state.assets, key=lambda x: x['last_updated'], reverse=True)[:5]
    
    if recent_assets:
        for asset in recent_assets:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.write(f"**{asset['name']}** ({asset['asset_tag']})")
            with col2:
                st.write(f"**{asset['department']}** - {asset['assigned_to']}")
            with col3:
                st.write(f"${asset['current_value']:,.0f}")
            with col4:
                if asset['criticality'] == 'Critical':
                    st.write("🔴 Critical")
                elif asset['criticality'] == 'High':
                    st.write("🟠 High")
                else:
                    st.write("🟡 Medium")
            st.divider()

def show_assets():
    st.header("💻 Assets")
    
    # Add new asset
    with st.expander("Add New Asset"):
        with st.form("new_asset"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Asset Name")
                category_id = st.selectbox("Category", [c['id'] for c in st.session_state.asset_categories])
                location_id = st.selectbox("Location", [l['id'] for l in st.session_state.asset_locations])
                asset_tag = st.text_input("Asset Tag")
                serial_number = st.text_input("Serial Number")
            
            with col2:
                model = st.text_input("Model")
                manufacturer = st.text_input("Manufacturer")
                purchase_date = st.date_input("Purchase Date")
                warranty_expiry = st.date_input("Warranty Expiry")
                purchase_cost = st.number_input("Purchase Cost ($)", min_value=0.0, value=0.0)
            
            col3, col4 = st.columns(2)
            with col3:
                assigned_to = st.text_input("Assigned To")
                department = st.selectbox("Department", ["IT", "HR", "Finance", "Marketing", "Sales", "Operations", "Legal"])
                status = st.selectbox("Status", ["In Use", "In Storage", "Under Maintenance", "Retired", "Lost/Stolen"])
            
            with col4:
                criticality = st.selectbox("Criticality", ["Critical", "High", "Medium", "Low"])
                current_value = st.number_input("Current Value ($)", min_value=0.0, value=0.0)
            
            if st.form_submit_button("Add Asset"):
                new_asset = {
                    'id': f'AST-{datetime.datetime.now().year}-{len(st.session_state.assets)+1:03d}',
                    'name': name,
                    'category_id': category_id,
                    'location_id': location_id,
                    'asset_tag': asset_tag,
                    'serial_number': serial_number,
                    'model': model,
                    'manufacturer': manufacturer,
                    'purchase_date': datetime.datetime.combine(purchase_date, datetime.time()),
                    'warranty_expiry': datetime.datetime.combine(warranty_expiry, datetime.time()),
                    'purchase_cost': purchase_cost,
                    'current_value': current_value,
                    'status': status,
                    'assigned_to': assigned_to,
                    'department': department,
                    'criticality': criticality,
                    'last_updated': datetime.datetime.now()
                }
                st.session_state.assets.append(new_asset)
                st.success("Asset added successfully!")
    
    # Display assets
    df = pd.DataFrame(st.session_state.assets)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        category_filter = st.selectbox("Filter by Category", ["All"] + [c['name'] for c in st.session_state.asset_categories])
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col3:
        criticality_filter = st.selectbox("Filter by Criticality", ["All"] + list(df['criticality'].unique()))
    with col4:
        department_filter = st.selectbox("Filter by Department", ["All"] + list(df['department'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if category_filter != "All":
        category_id = next((c['id'] for c in st.session_state.asset_categories if c['name'] == category_filter), None)
        if category_id:
            filtered_df = filtered_df[filtered_df['category_id'] == category_id]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if criticality_filter != "All":
        filtered_df = filtered_df[filtered_df['criticality'] == criticality_filter]
    if department_filter != "All":
        filtered_df = filtered_df[filtered_df['department'] == department_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Asset overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Assets by Status")
        status_counts = df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Asset Distribution by Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Assets by Department")
        dept_counts = df['department'].value_counts()
        fig = px.bar(x=dept_counts.index, y=dept_counts.values, 
                    title="Assets by Department")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_categories():
    st.header("📂 Asset Categories")
    
    # Add new category
    with st.expander("Add New Category"):
        with st.form("new_category"):
            name = st.text_input("Category Name")
            description = st.text_area("Description")
            
            if st.form_submit_button("Add Category"):
                new_category = {
                    'id': f'CAT-{len(st.session_state.asset_categories)+1:03d}',
                    'name': name,
                    'description': description
                }
                st.session_state.asset_categories.append(new_category)
                st.success("Category added successfully!")
    
    # Display categories
    df = pd.DataFrame(st.session_state.asset_categories)
    st.dataframe(df, use_container_width=True)
    
    # Category overview
    if not df.empty:
        st.subheader("Category Overview")
        fig = px.bar(df, x='name', y=[len([a for a in st.session_state.assets if a['category_id'] == cat['id']]) 
                                    for cat in st.session_state.asset_categories], 
                    title="Assets per Category")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_locations():
    st.header("📍 Asset Locations")
    
    # Add new location
    with st.expander("Add New Location"):
        with st.form("new_location"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Location Name")
                address = st.text_area("Address")
            with col2:
                location_type = st.selectbox("Location Type", ["Office", "Data Center", "Warehouse", "Remote", "Other"])
            
            if st.form_submit_button("Add Location"):
                new_location = {
                    'id': f'LOC-{len(st.session_state.asset_locations)+1:03d}',
                    'name': name,
                    'address': address,
                    'type': location_type
                }
                st.session_state.asset_locations.append(new_location)
                st.success("Location added successfully!")
    
    # Display locations
    df = pd.DataFrame(st.session_state.asset_locations)
    st.dataframe(df, use_container_width=True)
    
    # Location overview
    if not df.empty:
        st.subheader("Location Overview")
        col1, col2 = st.columns(2)
        
        with col1:
            type_counts = df['type'].value_counts()
            fig = px.pie(values=type_counts.values, names=type_counts.index, 
                        title="Locations by Type")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            asset_counts = [len([a for a in st.session_state.assets if a['location_id'] == loc['id']]) 
                           for loc in st.session_state.asset_locations]
            fig = px.bar(df, x='name', y=asset_counts, 
                        title="Assets per Location")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

def show_maintenance():
    st.header("🔧 Asset Maintenance")
    
    # Add new maintenance record
    with st.expander("Add New Maintenance Record"):
        with st.form("new_maintenance"):
            col1, col2 = st.columns(2)
            with col1:
                asset_id = st.selectbox("Asset", [a['id'] for a in st.session_state.assets])
                maintenance_type = st.selectbox("Maintenance Type", ["Preventive", "Repair", "Upgrade", "Inspection"])
                scheduled_date = st.date_input("Scheduled Date")
                technician = st.text_input("Technician")
            
            with col2:
                description = st.text_area("Description")
                cost = st.number_input("Cost ($)", min_value=0.0, value=0.0)
                status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed", "Cancelled"])
                notes = st.text_area("Notes")
            
            if st.form_submit_button("Add Maintenance Record"):
                new_maintenance = {
                    'id': f'MAINT-{len(st.session_state.asset_maintenance)+1:03d}',
                    'asset_id': asset_id,
                    'maintenance_type': maintenance_type,
                    'description': description,
                    'scheduled_date': datetime.datetime.combine(scheduled_date, datetime.time()),
                    'completed_date': None,
                    'technician': technician,
                    'cost': cost,
                    'status': status,
                    'notes': notes
                }
                st.session_state.asset_maintenance.append(new_maintenance)
                st.success("Maintenance record added successfully!")
    
    # Display maintenance records
    df = pd.DataFrame(st.session_state.asset_maintenance)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col2:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['maintenance_type'].unique()))
    with col3:
        technician_filter = st.selectbox("Filter by Technician", ["All"] + list(df['technician'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['maintenance_type'] == type_filter]
    if technician_filter != "All":
        filtered_df = filtered_df[filtered_df['technician'] == technician_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Maintenance overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Maintenance by Status")
        status_counts = df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Maintenance Records by Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Maintenance by Type")
        type_counts = df['maintenance_type'].value_counts()
        fig = px.bar(x=type_counts.index, y=type_counts.values, 
                    title="Maintenance Records by Type")
        st.plotly_chart(fig, use_container_width=True)

def show_licenses():
    st.header("📜 Asset Licenses")
    
    # Add new license
    with st.expander("Add New License"):
        with st.form("new_license"):
            col1, col2 = st.columns(2)
            with col1:
                asset_id = st.selectbox("Asset", [a['id'] for a in st.session_state.assets])
                license_type = st.selectbox("License Type", ["Operating System", "Antivirus", "Office Suite", "Database", "Network Management", "Other"])
                vendor = st.text_input("Vendor")
                product = st.text_input("Product")
            
            with col2:
                license_key = st.text_input("License Key")
                purchase_date = st.date_input("Purchase Date")
                expiry_date = st.date_input("Expiry Date")
                cost = st.number_input("Cost ($)", min_value=0.0, value=0.0)
                seats = st.number_input("Number of Seats", min_value=1, value=1)
                status = st.selectbox("Status", ["Active", "Expired", "Suspended"])
            
            if st.form_submit_button("Add License"):
                new_license = {
                    'id': f'LIC-{len(st.session_state.asset_licenses)+1:03d}',
                    'asset_id': asset_id,
                    'license_type': license_type,
                    'license_key': license_key,
                    'vendor': vendor,
                    'product': product,
                    'purchase_date': datetime.datetime.combine(purchase_date, datetime.time()),
                    'expiry_date': datetime.datetime.combine(expiry_date, datetime.time()),
                    'cost': cost,
                    'status': status,
                    'seats': seats
                }
                st.session_state.asset_licenses.append(new_license)
                st.success("License added successfully!")
    
    # Display licenses
    df = pd.DataFrame(st.session_state.asset_licenses)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col2:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(df['license_type'].unique()))
    with col3:
        vendor_filter = st.selectbox("Filter by Vendor", ["All"] + list(df['vendor'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['license_type'] == type_filter]
    if vendor_filter != "All":
        filtered_df = filtered_df[filtered_df['vendor'] == vendor_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # License overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Licenses by Status")
        status_counts = df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Licenses by Status")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Licenses by Type")
        type_counts = df['license_type'].value_counts()
        fig = px.bar(x=type_counts.index, y=type_counts.values, 
                    title="Licenses by Type")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_reports():
    st.header("📊 Reports & Analytics")
    
    # Report options
    report_type = st.selectbox("Select Report Type", [
        "Asset Inventory Report",
        "Maintenance Schedule Report",
        "License Compliance Report",
        "Asset Value Report",
        "Warranty Expiry Report"
    ])
    
    if report_type == "Asset Inventory Report":
        st.subheader("Asset Inventory Report")
        
        df_assets = pd.DataFrame(st.session_state.assets)
        df_categories = pd.DataFrame(st.session_state.asset_categories)
        df_locations = pd.DataFrame(st.session_state.asset_locations)
        
        if not df_assets.empty:
            # Merge data
            df_merged = df_assets.merge(df_categories, left_on='category_id', right_on='id', how='left')
            df_merged = df_merged.merge(df_locations, left_on='location_id', right_on='id', how='left')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Asset Summary**")
                st.write(f"• Total Assets: {len(df_assets)}")
                st.write(f"• Total Value: ${sum(df_assets['current_value']):,.2f}")
                st.write(f"• Assets In Use: {len(df_assets[df_assets['status'] == 'In Use'])}")
                st.write(f"• Critical Assets: {len(df_assets[df_assets['criticality'] == 'Critical'])}")
            
            with col2:
                st.write("**Department Summary**")
                dept_stats = df_merged.groupby('department').agg({
                    'current_value': ['sum', 'count'],
                    'criticality': lambda x: (x == 'Critical').sum()
                }).round(2)
                st.dataframe(dept_stats)
    
    # Export functionality
    st.subheader("Export Data")
    export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
    
    if st.button("Export Asset Data"):
        if export_format == "CSV":
            # Export assets to CSV
            df_assets = pd.DataFrame(st.session_state.assets)
            csv = df_assets.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="asset_inventory.csv",
                mime="text/csv"
            )

def show_analytics():
    st.header("📈 Analytics & Insights")
    
    # Calculate metrics
    total_assets = len(st.session_state.assets)
    total_value = sum(asset['current_value'] for asset in st.session_state.assets)
    total_cost = sum(asset['purchase_cost'] for asset in st.session_state.assets)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Assets", total_assets)
        st.metric("Critical Assets", len([a for a in st.session_state.assets if a['criticality'] == 'Critical']))
    
    with col2:
        st.metric("Total Value", f"${total_value:,.2f}")
        st.metric("Total Purchase Cost", f"${total_cost:,.2f}")
    
    with col3:
        depreciation = total_cost - total_value
        st.metric("Total Depreciation", f"${depreciation:,.2f}")
        st.metric("Assets In Use", len([a for a in st.session_state.assets if a['status'] == 'In Use']))
    
    with col4:
        avg_age = np.mean([(datetime.datetime.now() - asset['purchase_date']).days 
                          for asset in st.session_state.assets])
        st.metric("Average Asset Age", f"{avg_age:.0f} days")
        st.metric("Active Licenses", len([l for l in st.session_state.asset_licenses if l['status'] == 'Active']))
    
    # Asset value trends
    st.subheader("Asset Value Analysis")
    df_assets = pd.DataFrame(st.session_state.assets)
    if not df_assets.empty:
        df_assets['purchase_date'] = pd.to_datetime(df_assets['purchase_date'])
        df_assets['month'] = df_assets['purchase_date'].dt.to_period('M')
        
        monthly_purchases = df_assets.groupby('month').agg({
            'purchase_cost': 'sum',
            'current_value': 'sum'
        }).reset_index()
        monthly_purchases['month'] = monthly_purchases['month'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_purchases['month'], y=monthly_purchases['purchase_cost'], 
                                mode='lines+markers', name='Purchase Cost'))
        fig.add_trace(go.Scatter(x=monthly_purchases['month'], y=monthly_purchases['current_value'], 
                                mode='lines+markers', name='Current Value'))
        fig.update_layout(title="Asset Value Trends Over Time", xaxis_title="Month", yaxis_title="Value ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Asset distribution
    st.subheader("Asset Distribution Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        if not df_assets.empty:
            dept_value = df_assets.groupby('department')['current_value'].sum().sort_values(ascending=True)
            fig = px.bar(x=dept_value.values, y=dept_value.index, orientation='h',
                        title="Asset Value by Department",
                        labels={'x': 'Value ($)', 'y': 'Department'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not df_assets.empty:
            category_value = df_assets.groupby('category_id')['current_value'].sum()
            category_names = [next((c['name'] for c in st.session_state.asset_categories if c['id'] == cat_id), cat_id) 
                            for cat_id in category_value.index]
            fig = px.pie(values=category_value.values, names=category_names, 
                        title="Asset Value by Category")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
