import streamlit as st
import demo_kit
import portfolio_skin
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Analytics Dashboard Enhanced · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)



# Sample analytics data
@st.cache_data
def load_analytics_data(seed: int = 42):
    """Load sample analytics data"""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start='2023-01-01', end='2024-01-15', freq='D')

    risk_data = []
    base_risk = 45
    for date in dates:
        trend = np.sin((date - pd.Timestamp('2023-01-01')).days / 30) * 5
        noise = float(rng.uniform(-3, 3))
        risk_score = max(0, min(100, base_risk + trend + noise))
        risk_data.append({
            'date': date,
            'risk_score': risk_score,
            'category': 'Overall Risk'
        })

    compliance_data = []
    base_compliance = 75
    for date in dates:
        trend = np.sin((date - pd.Timestamp('2023-01-01')).days / 45) * 3
        noise = float(rng.uniform(-2, 2))
        compliance_rate = max(0, min(100, base_compliance + trend + noise))
        compliance_data.append({
            'date': date,
            'compliance_rate': compliance_rate,
            'category': 'Overall Compliance'
        })

    controls = [
        {'name': 'Access Control', 'effectiveness': 85, 'category': 'Security'},
        {'name': 'Data Protection', 'effectiveness': 78, 'category': 'Privacy'},
        {'name': 'Incident Response', 'effectiveness': 72, 'category': 'Security'},
        {'name': 'Vendor Management', 'effectiveness': 68, 'category': 'Risk'},
        {'name': 'Change Management', 'effectiveness': 82, 'category': 'Operations'},
        {'name': 'Backup & Recovery', 'effectiveness': 90, 'category': 'Operations'},
        {'name': 'Security Awareness', 'effectiveness': 75, 'category': 'Security'},
        {'name': 'Audit Logging', 'effectiveness': 88, 'category': 'Compliance'},
        {'name': 'Patch Management', 'effectiveness': 79, 'category': 'Security'},
        {'name': 'Business Continuity', 'effectiveness': 83, 'category': 'Operations'}
    ]
    for c in controls:
        c['effectiveness'] = int(np.clip(c['effectiveness'] + int(rng.integers(-5, 6)), 40, 99))

    frameworks = [
        {'framework': 'ISO 27001', 'compliance': 82, 'controls': 114, 'implemented': 94},
        {'framework': 'SOC 2', 'compliance': 78, 'controls': 67, 'implemented': 52},
        {'framework': 'NIST CSF', 'compliance': 75, 'controls': 108, 'implemented': 81},
        {'framework': 'PCI DSS', 'compliance': 85, 'controls': 78, 'implemented': 66},
        {'framework': 'HIPAA', 'compliance': 88, 'controls': 45, 'implemented': 40}
    ]
    for f in frameworks:
        f['compliance'] = int(np.clip(f['compliance'] + int(rng.integers(-4, 5)), 50, 99))

    vendors = []
    vendor_names = ['TechCorp', 'DataFlow', 'CloudSecure', 'NetWorks', 'SysTech', 'InfoSafe', 'SecureCloud', 'DataTech']
    for name in vendor_names:
        risk_score = int(rng.integers(20, 81))
        compliance_score = int(rng.integers(60, 96))
        vendors.append({
            'vendor_name': name,
            'risk_score': risk_score,
            'compliance_score': compliance_score,
            'contract_value': int(rng.integers(50000, 500001)),
            'risk_tier': 'High' if risk_score > 60 else 'Medium' if risk_score > 30 else 'Low'
        })

    incidents = []
    incident_types = ['Data Breach', 'System Outage', 'Access Violation', 'Malware', 'Phishing', 'Insider Threat']
    severities = ['Low', 'Medium', 'High', 'Critical']
    for _ in range(50):
        incident_date = dates[int(rng.integers(0, len(dates)))]
        incidents.append({
            'date': incident_date,
            'type': str(rng.choice(incident_types)),
            'severity': str(rng.choice(severities)),
            'resolution_time': int(rng.integers(1, 73)),
            'cost': int(rng.integers(1000, 100001))
        })

    return {
        'risk_data': pd.DataFrame(risk_data),
        'compliance_data': pd.DataFrame(compliance_data),
        'controls': pd.DataFrame(controls),
        'frameworks': pd.DataFrame(frameworks),
        'vendors': pd.DataFrame(vendors),
        'incidents': pd.DataFrame(incidents)
    }

def calculate_analytics_metrics(data):
    """Calculate key analytics metrics"""
    current_risk = data['risk_data']['risk_score'].iloc[-1]
    current_compliance = data['compliance_data']['compliance_rate'].iloc[-1]
    avg_control_effectiveness = data['controls']['effectiveness'].mean()
    total_incidents = len(data['incidents'])
    avg_resolution_time = data['incidents']['resolution_time'].mean()
    
    # Calculate trends (comparing last 30 days to previous 30 days)
    recent_risk = data['risk_data']['risk_score'].tail(30).mean()
    previous_risk = data['risk_data']['risk_score'].tail(60).head(30).mean()
    risk_trend = ((recent_risk - previous_risk) / previous_risk) * 100 if previous_risk > 0 else 0
    
    recent_compliance = data['compliance_data']['compliance_rate'].tail(30).mean()
    previous_compliance = data['compliance_data']['compliance_rate'].tail(60).head(30).mean()
    compliance_trend = ((recent_compliance - previous_compliance) / previous_compliance) * 100 if previous_compliance > 0 else 0
    
    metrics = {
        'current_risk': current_risk,
        'current_compliance': current_compliance,
        'avg_control_effectiveness': avg_control_effectiveness,
        'total_incidents': total_incidents,
        'avg_resolution_time': avg_resolution_time,
        'risk_trend': risk_trend,
        'compliance_trend': compliance_trend,
        'total_controls': len(data['controls']),
        'total_vendors': len(data['vendors']),
        'high_risk_vendors': len(data['vendors'][data['vendors']['risk_tier'] == 'High'])
    }
    
    return metrics

def main():
    portfolio_skin.page_header(
        title="Analytics Dashboard Enhanced",
        lede="Interactive GRC tool — #RUNGRCRaleigh build-in-public.",
        kicker="Analytics",
    )
    
    with st.sidebar:
        st.header("Analytics Controls")
        seed = demo_kit.seed_controls()
        st.markdown("---")
        date_range = st.selectbox(
            "Select Date Range",
            ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"],
            index=1,
        )
        st.subheader("Filters")

    data = load_analytics_data(seed)

    with st.sidebar:
        risk_tier_filter = st.multiselect(
            "Risk Tier",
            list(data['vendors']['risk_tier'].unique()),
            default=list(data['vendors']['risk_tier'].unique()),
        )
        severity_filter = st.multiselect(
            "Incident Severity",
            list(data['incidents']['severity'].unique()),
            default=list(data['incidents']['severity'].unique()),
        )
        risk_adjust = st.slider(
            "What-if risk adjust",
            min_value=-15,
            max_value=15,
            value=0,
            step=1,
            help="Shift vendor risk scores to explore tier impact.",
        )
        st.caption("Sample / mock data only.")

    data['vendors'] = data['vendors'].copy()
    data['vendors']['risk_score'] = (data['vendors']['risk_score'] + risk_adjust).clip(0, 100)
    data['vendors']['risk_tier'] = data['vendors']['risk_score'].apply(
        lambda s: 'High' if s > 60 else 'Medium' if s > 30 else 'Low'
    )
    metrics = calculate_analytics_metrics(data)

    filtered_vendors = data['vendors'][data['vendors']['risk_tier'].isin(risk_tier_filter)]
    filtered_incidents = data['incidents'][data['incidents']['severity'].isin(severity_filter)]
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Trends", "Performance", "Deep Dive", "Reports"])
    
    with tab1:
        st.header("Analytics Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trend_icon = "↗" if metrics['risk_trend'] > 0 else "↘" if metrics['risk_trend'] < 0 else "→"
            trend_color = "trend-negative" if metrics['risk_trend'] > 0 else "trend-positive" if metrics['risk_trend'] < 0 else "trend-neutral"
            st.metric(
                "Overall Risk Score", 
                f"{metrics['current_risk']:.1f}",
                f"{trend_icon} {abs(metrics['risk_trend']):.1f}%"
            )
        
        with col2:
            trend_icon = "↗" if metrics['compliance_trend'] > 0 else "↘" if metrics['compliance_trend'] < 0 else "→"
            trend_color = "trend-positive" if metrics['compliance_trend'] > 0 else "trend-negative" if metrics['compliance_trend'] < 0 else "trend-neutral"
            st.metric(
                "Compliance Rate", 
                f"{metrics['current_compliance']:.1f}%",
                f"{trend_icon} {abs(metrics['compliance_trend']):.1f}%"
            )
        
        with col3:
            st.metric("Control Effectiveness", f"{metrics['avg_control_effectiveness']:.1f}%")
        
        with col4:
            st.metric("Total Incidents", metrics['total_incidents'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk trend over time
            fig_risk = px.line(
                data['risk_data'],
                x='date',
                y='risk_score',
                title="Risk Score Trend Over Time",
                labels={'risk_score': 'Risk Score', 'date': 'Date'}
            )
            fig_risk.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            # Compliance trend over time
            fig_compliance = px.line(
                data['compliance_data'],
                x='date',
                y='compliance_rate',
                title="Compliance Rate Trend Over Time",
                labels={'compliance_rate': 'Compliance Rate (%)', 'date': 'Date'}
            )
            fig_compliance.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Target Compliance")
            st.plotly_chart(fig_compliance, use_container_width=True)
        
        # Framework compliance
        st.subheader("Framework Compliance")
        
        fig_frameworks = px.bar(
            data['frameworks'],
            x='framework',
            y='compliance',
            title="Framework Compliance Rates",
            labels={'compliance': 'Compliance Rate (%)', 'framework': 'Framework'},
            color='compliance',
            color_continuous_scale='RdYlGn'
        )
        fig_frameworks.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Target")
        st.plotly_chart(fig_frameworks, use_container_width=True)
        
        # Vendor risk heatmap
        st.subheader("Vendor Risk Analysis")
        
        fig_vendor_heatmap = px.scatter(
            filtered_vendors,
            x='risk_score',
            y='compliance_score',
            size='contract_value',
            color='risk_tier',
            hover_data=['vendor_name'],
            title="Vendor Risk vs Compliance Heatmap",
            labels={'risk_score': 'Risk Score', 'compliance_score': 'Compliance Score (%)'},
            color_discrete_map={
                'Low': '#388e3c',
                'Medium': '#f57c00',
                'High': '#d32f2f'
            }
        )
        fig_vendor_heatmap.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Target Compliance")
        fig_vendor_heatmap.add_vline(x=50, line_dash="dash", line_color="red", annotation_text="Risk Threshold")
        st.plotly_chart(fig_vendor_heatmap, use_container_width=True)
    
    with tab2:
        st.header("Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Control effectiveness by category
            fig_control_category = px.bar(
                data['controls'].groupby('category')['effectiveness'].mean().reset_index(),
                x='category',
                y='effectiveness',
                title="Control Effectiveness by Category",
                labels={'effectiveness': 'Effectiveness (%)', 'category': 'Category'},
                color='effectiveness',
                color_continuous_scale='RdYlGn'
            )
            fig_control_category.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Target")
            st.plotly_chart(fig_control_category, use_container_width=True)
        
        with col2:
            # Incident trends by type
            incident_counts = filtered_incidents['type'].value_counts()
            fig_incident_types = px.pie(
                values=incident_counts.values,
                names=incident_counts.index,
                title="Incidents by Type"
            )
            st.plotly_chart(fig_incident_types, use_container_width=True)
        
        # Incident severity over time
        st.subheader("Incident Severity Trends")
        
        # Group incidents by month and severity
        monthly_incidents = filtered_incidents.copy()
        monthly_incidents['month'] = monthly_incidents['date'].dt.to_period('M')
        monthly_severity = monthly_incidents.groupby(['month', 'severity']).size().reset_index(name='count')
        monthly_severity['month'] = monthly_severity['month'].astype(str)
        
        fig_incident_trend = px.line(
            monthly_severity,
            x='month',
            y='count',
            color='severity',
            title="Incident Severity Trends Over Time",
            labels={'count': 'Number of Incidents', 'month': 'Month', 'severity': 'Severity'}
        )
        st.plotly_chart(fig_incident_trend, use_container_width=True)
        
        # Resolution time analysis
        st.subheader("Incident Resolution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Resolution time by severity
            resolution_by_severity = filtered_incidents.groupby('severity')['resolution_time'].mean().reset_index()
            fig_resolution = px.bar(
                resolution_by_severity,
                x='severity',
                y='resolution_time',
                title="Average Resolution Time by Severity",
                labels={'resolution_time': 'Hours', 'severity': 'Severity'}
            )
            st.plotly_chart(fig_resolution, use_container_width=True)
        
        with col2:
            # Resolution time distribution
            fig_resolution_dist = px.histogram(
                filtered_incidents,
                x='resolution_time',
                title="Resolution Time Distribution",
                labels={'resolution_time': 'Hours', 'count': 'Number of Incidents'},
                nbins=20
            )
            st.plotly_chart(fig_resolution_dist, use_container_width=True)
    
    with tab3:
        st.header("Performance Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Control effectiveness ranking
            st.subheader("Top Performing Controls")
            
            top_controls = data['controls'].nlargest(5, 'effectiveness')
            fig_top_controls = px.bar(
                top_controls,
                x='effectiveness',
                y='name',
                orientation='h',
                title="Top 5 Controls by Effectiveness",
                labels={'effectiveness': 'Effectiveness (%)', 'name': 'Control Name'}
            )
            st.plotly_chart(fig_top_controls, use_container_width=True)
        
        with col2:
            # Areas needing improvement
            st.subheader("Controls Needing Improvement")
            
            bottom_controls = data['controls'].nsmallest(5, 'effectiveness')
            fig_bottom_controls = px.bar(
                bottom_controls,
                x='effectiveness',
                y='name',
                orientation='h',
                title="Controls Needing Improvement",
                labels={'effectiveness': 'Effectiveness (%)', 'name': 'Control Name'}
            )
            st.plotly_chart(fig_bottom_controls, use_container_width=True)
        
        # Performance correlation analysis
        st.subheader("Performance Correlations")
        
        # Create correlation matrix for numerical data
        correlation_data = data['controls'].copy()
        correlation_data['category_encoded'] = pd.Categorical(correlation_data['category']).codes
        
        # Simulate additional metrics for correlation
        correlation_data['implementation_cost'] = np.random.randint(10000, 100000, len(correlation_data))
        correlation_data['maintenance_effort'] = np.random.randint(1, 10, len(correlation_data))
        
        # Calculate correlations
        corr_matrix = correlation_data[['effectiveness', 'implementation_cost', 'maintenance_effort']].corr()
        
        fig_correlation = px.imshow(
            corr_matrix,
            title="Performance Correlation Matrix",
            color_continuous_scale='RdBu',
            aspect="auto"
        )
        st.plotly_chart(fig_correlation, use_container_width=True)
        
        # Performance benchmarking
        st.subheader("Performance Benchmarking")
        
        # Simulate industry benchmarks
        benchmark_data = []
        categories = data['controls']['category'].unique()
        for category in categories:
            category_controls = data['controls'][data['controls']['category'] == category]
            benchmark_data.append({
                'Category': category,
                'Current': category_controls['effectiveness'].mean(),
                'Industry Average': random.uniform(70, 85),
                'Best Practice': random.uniform(85, 95)
            })
        
        benchmark_df = pd.DataFrame(benchmark_data)
        
        fig_benchmark = go.Figure()
        
        for i, category in enumerate(benchmark_df['Category']):
            fig_benchmark.add_trace(go.Bar(
                name=f'{category} - Current',
                x=[category],
                y=[benchmark_df.iloc[i]['Current']],
                marker_color='#1f77b4'
            ))
            fig_benchmark.add_trace(go.Bar(
                name=f'{category} - Industry',
                x=[category],
                y=[benchmark_df.iloc[i]['Industry Average']],
                marker_color='#ff7f0e'
            ))
            fig_benchmark.add_trace(go.Bar(
                name=f'{category} - Best Practice',
                x=[category],
                y=[benchmark_df.iloc[i]['Best Practice']],
                marker_color='#2ca02c'
            ))
        
        fig_benchmark.update_layout(
            title="Performance vs Industry Benchmarks",
            barmode='group',
            yaxis_title="Effectiveness (%)"
        )
        st.plotly_chart(fig_benchmark, use_container_width=True)
    
    with tab4:
        st.header("Deep Dive Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Predictive analytics simulation
            st.subheader("Predictive Analytics")
            
            # Simulate risk prediction
            future_dates = pd.date_range(start='2024-01-16', end='2024-06-30', freq='D')
            predicted_risk = []
            
            for date in future_dates:
                # Simple trend-based prediction
                trend_factor = 0.1 * np.sin((date - pd.Timestamp('2024-01-16')).days / 30)
                predicted_value = metrics['current_risk'] + trend_factor * 10
                predicted_risk.append(max(0, min(100, predicted_value)))
            
            # Combine historical and predicted data
            historical_risk = data['risk_data'][['date', 'risk_score']].copy()
            historical_risk['type'] = 'Historical'
            
            predicted_df = pd.DataFrame({
                'date': future_dates,
                'risk_score': predicted_risk,
                'type': 'Predicted'
            })
            
            combined_risk = pd.concat([historical_risk, predicted_df])
            
            fig_prediction = px.line(
                combined_risk,
                x='date',
                y='risk_score',
                color='type',
                title="Risk Score Prediction (Next 6 Months)",
                labels={'risk_score': 'Risk Score', 'date': 'Date'}
            )
            fig_prediction.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
            st.plotly_chart(fig_prediction, use_container_width=True)
        
        with col2:
            # Anomaly detection
            st.subheader("Anomaly Detection")
            
            # Simulate anomaly detection
            risk_values = data['risk_data']['risk_score'].values
            mean_risk = np.mean(risk_values)
            std_risk = np.std(risk_values)
            
            # Identify anomalies (values beyond 2 standard deviations)
            anomalies = []
            for i, value in enumerate(risk_values):
                if abs(value - mean_risk) > 2 * std_risk:
                    anomalies.append({
                        'date': data['risk_data'].iloc[i]['date'],
                        'risk_score': value,
                        'deviation': (value - mean_risk) / std_risk
                    })
            
            if anomalies:
                anomalies_df = pd.DataFrame(anomalies)
                fig_anomalies = px.scatter(
                    anomalies_df,
                    x='date',
                    y='risk_score',
                    size='deviation',
                    title="Detected Risk Anomalies",
                    labels={'risk_score': 'Risk Score', 'date': 'Date', 'deviation': 'Standard Deviations'}
                )
                fig_anomalies.add_hline(y=mean_risk, line_dash="dash", line_color="blue", annotation_text="Mean")
                st.plotly_chart(fig_anomalies, use_container_width=True)
            else:
                st.success("No anomalies detected in the current dataset!")
        
        # Advanced analytics
        st.subheader("Advanced Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk distribution analysis
            fig_risk_dist = px.histogram(
                data['risk_data'],
                x='risk_score',
                title="Risk Score Distribution",
                labels={'risk_score': 'Risk Score', 'count': 'Frequency'},
                nbins=20
            )
            fig_risk_dist.add_vline(x=mean_risk, line_dash="dash", line_color="red", annotation_text="Mean")
            st.plotly_chart(fig_risk_dist, use_container_width=True)
        
        with col2:
            # Compliance vs Risk correlation
            # Merge risk and compliance data
            merged_data = data['risk_data'].merge(data['compliance_data'], on='date')
            
            fig_correlation = px.scatter(
                merged_data,
                x='risk_score',
                y='compliance_rate',
                title="Risk vs Compliance Correlation",
                labels={'risk_score': 'Risk Score', 'compliance_rate': 'Compliance Rate (%)'}
            )
            
            # Add trend line
            z = np.polyfit(merged_data['risk_score'], merged_data['compliance_rate'], 1)
            p = np.poly1d(z)
            fig_correlation.add_trace(
                go.Scatter(
                    x=merged_data['risk_score'],
                    y=p(merged_data['risk_score']),
                    mode='lines',
                    name='Trend Line',
                    line=dict(color='red', dash='dash')
                )
            )
            
            st.plotly_chart(fig_correlation, use_container_width=True)
    
    with tab5:
        st.header("Reports & Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Report generation
            st.subheader("Generate Reports")
            
            report_type = st.selectbox(
                "Report Type",
                ["Executive Summary", "Detailed Analytics", "Performance Review", "Risk Assessment", "Compliance Report"]
            )
            
            report_format = st.selectbox(
                "Format",
                ["PDF", "Excel", "PowerPoint", "JSON"]
            )
            
            if st.button("Generate Report"):
                st.success(f"{report_type} report generated in {report_format} format!")
            
            # Scheduled reports
            st.subheader("Scheduled Reports")
            
            schedule_frequency = st.selectbox(
                "Frequency",
                ["Daily", "Weekly", "Monthly", "Quarterly"]
            )
            
            if st.button("Schedule Report"):
                st.success(f"Report scheduled for {schedule_frequency} delivery!")
        
        with col2:
            st.subheader("Export Data")
            export_df = filtered_incidents.copy()
            if 'date' in export_df.columns:
                export_df['date'] = export_df['date'].astype(str)
            demo_kit.csv_download(
                export_df, "analytics_incidents_filtered.csv", label="Download filtered incidents"
            )
            demo_kit.csv_download(
                filtered_vendors, "analytics_vendors_filtered.csv", label="Download filtered vendors", key="analytics_vendors_csv"
            )

        # Executive summary
        st.subheader("Executive Summary")
        
        # Key insights
        insights = {
            'Metric': [
                'Overall Risk Level',
                'Compliance Status',
                'Control Effectiveness',
                'Incident Trend',
                'Vendor Risk Exposure',
                'Framework Coverage'
            ],
            'Current Status': [
                'Medium' if metrics['current_risk'] < 50 else 'High',
                'Compliant' if metrics['current_compliance'] > 80 else 'At Risk',
                'Good' if metrics['avg_control_effectiveness'] > 80 else 'Needs Improvement',
                'Decreasing' if len(filtered_incidents) < 25 else 'Stable',
                'Low' if metrics['high_risk_vendors'] < 3 else 'Medium',
                'Comprehensive' if len(data['frameworks']) >= 4 else 'Limited'
            ],
            'Trend': [
                '↘Improving' if metrics['risk_trend'] < 0 else '↗Increasing' if metrics['risk_trend'] > 0 else '→ Stable',
                '↗Improving' if metrics['compliance_trend'] > 0 else '↘Declining' if metrics['compliance_trend'] < 0 else '→ Stable',
                '→ Stable',
                '↘Decreasing',
                '→ Stable',
                '→ Stable'
            ],
            'Recommendation': [
                'Continue current risk mitigation efforts',
                'Focus on compliance gap remediation',
                'Implement control improvement program',
                'Maintain incident response capabilities',
                'Conduct vendor risk reviews',
                'Expand framework coverage'
            ]
        }
        
        insights_df = pd.DataFrame(insights)
        st.dataframe(insights_df, use_container_width=True, hide_index=True)
        
        # Action items
        st.subheader("Key Action Items")
        
        action_items = [
            "Conduct detailed risk assessment for high-risk areas",
            "Review and update compliance controls",
            "Implement control effectiveness improvement program",
            "Enhance incident monitoring and response",
            "Perform vendor risk assessments",
            "Develop framework implementation roadmap"
        ]
        
        for item in action_items:
            st.write(f"• {item}")

if __name__ == "__main__":
    main()
