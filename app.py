"""
Green Supply Chain Dashboard - AB InBev
Main Streamlit application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import numpy as np

from models import DataProcessor, SimulationEngine, PackagingData
from config import (
    DASHBOARD_TITLE, COLOR_PALETTE, SIMULATION_SCENARIOS,
    REUSE_TARGET, WASTE_REDUCTION_TARGET, CO2_REDUCTION_TARGET
)

# Page configuration
st.set_page_config(
    page_title="Green Supply Chain Dashboard",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00A651;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #00A651;
        margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00A651;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
    }
    .status-good { color: #28A745; }
    .status-warning { color: #FFC107; }
    .status-danger { color: #DC3545; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the packaging data"""
    try:
        df = pd.read_csv('data/sample_packaging_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("Sample data not found. Please run data_generator.py first.")
        return pd.DataFrame()

@st.cache_data
def load_facilities():
    """Load and cache facilities data"""
    try:
        return pd.read_csv('data/facilities.csv')
    except FileNotFoundError:
        st.error("Facilities data not found. Please run data_generator.py first.")
        return pd.DataFrame()

def create_kpi_card(value, label, target=None, format_str="{:.1f}"):
    """Create a KPI card with status indicator"""
    if target:
        if value >= target:
            status_class = "status-good"
            icon = "✅"
        elif value >= target * 0.8:
            status_class = "status-warning"
            icon = "⚠️"
        else:
            status_class = "status-danger"
            icon = "❌"
    else:
        status_class = "status-good"
        icon = "📊"
    
    formatted_value = format_str.format(value)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-value {status_class}">{icon} {formatted_value}</div>
        <div class="kpi-label">{label}</div>
        {f'<small>Target: {format_str.format(target)}</small>' if target else ''}
    </div>
    """, unsafe_allow_html=True)

def create_gauge_chart(value, title, max_value=100, color="green"):
    """Create a gauge chart for KPIs"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': max_value * 0.8},
        gauge = {
            'axis': {'range': [None, max_value]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, max_value * 0.6], 'color': "lightgray"},
                {'range': [max_value * 0.6, max_value * 0.8], 'color': "yellow"},
                {'range': [max_value * 0.8, max_value], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def create_map(facilities_df, packaging_df):
    """Create map visualization of facilities and flows"""
    
    # Calculate center point
    center_lat = facilities_df['lat'].mean()
    center_lon = facilities_df['lon'].mean()
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9)
    
    # Add facility markers
    facility_colors = {
        'Brewery': 'red',
        'Distribution Center': 'blue', 
        'Recycling Center': 'green',
        'Collection Point': 'orange'
    }
    
    for _, facility in facilities_df.iterrows():
        # Get performance data for this facility
        facility_data = packaging_df[packaging_df['facility_id'] == facility['facility_id']]
        if not facility_data.empty:
            total_produced = facility_data['total_produced'].sum()
            total_reused = facility_data['total_reused'].sum()
            reuse_rate = (total_reused / total_produced * 100) if total_produced > 0 else 0
            
            popup_text = f"""
            <b>{facility['name']}</b><br>
            Type: {facility['type']}<br>
            Total Produced: {total_produced:,}<br>
            Reuse Rate: {reuse_rate:.1f}%
            """
            
            folium.Marker(
                location=[facility['lat'], facility['lon']],
                popup=popup_text,
                icon=folium.Icon(
                    color=facility_colors.get(facility['type'], 'gray'),
                    icon='industry'
                )
            ).add_to(m)
    
    return m

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown(f'<div class="main-header">♻️ {DASHBOARD_TITLE}</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    facilities_df = load_facilities()
    
    if df.empty:
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['date'].min(), df['date'].max()),
        min_value=df['date'].min(),
        max_value=df['date'].max()
    )
    
    # Facility type filter
    facility_types = st.sidebar.multiselect(
        "Facility Types",
        options=df['facility_type'].unique(),
        default=df['facility_type'].unique()
    )
    
    # Packaging type filter
    packaging_types = st.sidebar.multiselect(
        "Packaging Types", 
        options=df['packaging_type'].unique(),
        default=df['packaging_type'].unique()
    )
    
    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[
            (df['date'] >= pd.Timestamp(start_date)) & 
            (df['date'] <= pd.Timestamp(end_date)) &
            (df['facility_type'].isin(facility_types)) &
            (df['packaging_type'].isin(packaging_types))
        ]
    else:
        df_filtered = df[
            (df['facility_type'].isin(facility_types)) &
            (df['packaging_type'].isin(packaging_types))
        ]
    
    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Process data
    processor = DataProcessor([])  # We'll use the dataframe directly
    processor.df = df_filtered
    kpis = processor.calculate_kpis()
    
    # Main KPIs section
    st.header("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_kpi_card(
            kpis.reuse_rate, 
            "Reuse Rate (%)", 
            target=REUSE_TARGET,
            format_str="{:.1f}%"
        )
    
    with col2:
        create_kpi_card(
            kpis.waste_rate,
            "Waste Rate (%)",
            target=None,
            format_str="{:.1f}%"
        )
    
    with col3:
        create_kpi_card(
            kpis.co2_saved_total,
            "CO₂ Saved (tonnes)",
            target=CO2_REDUCTION_TARGET,
            format_str="{:.0f}"
        )
    
    with col4:
        create_kpi_card(
            kpis.cost_savings_total,
            "Cost Savings ($)",
            target=None,
            format_str="${:,.0f}"
        )
    
    # Gauge charts
    st.header("🎯 Performance Gauges")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        gauge1 = create_gauge_chart(kpis.reuse_rate, "Reuse Rate (%)", 100, COLOR_PALETTE["primary"])
        st.plotly_chart(gauge1, use_container_width=True)
    
    with col2:
        gauge2 = create_gauge_chart(kpis.recovery_rate, "Recovery Rate (%)", 100, COLOR_PALETTE["secondary"])
        st.plotly_chart(gauge2, use_container_width=True)
    
    with col3:
        gauge3 = create_gauge_chart(kpis.efficiency_score, "Efficiency Score", 100, COLOR_PALETTE["accent"])
        st.plotly_chart(gauge3, use_container_width=True)
    
    # Time series analysis
    st.header("📈 Trends Analysis")
    
    time_series = processor.get_time_series_data()
    
    # Create time series chart
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Reuse Rate Over Time', 'Waste Rate Over Time', 
                       'CO₂ Savings Over Time', 'Cost Savings Over Time'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Reuse rate
    fig.add_trace(
        go.Scatter(x=time_series['date'], y=time_series['reuse_rate'],
                  name='Reuse Rate', line=dict(color=COLOR_PALETTE["primary"])),
        row=1, col=1
    )
    
    # Waste rate
    fig.add_trace(
        go.Scatter(x=time_series['date'], y=time_series['waste_rate'],
                  name='Waste Rate', line=dict(color=COLOR_PALETTE["accent"])),
        row=1, col=2
    )
    
    # CO2 savings
    fig.add_trace(
        go.Scatter(x=time_series['date'], y=time_series['co2_saved'],
                  name='CO₂ Saved', line=dict(color=COLOR_PALETTE["success"])),
        row=2, col=1
    )
    
    # Cost savings
    fig.add_trace(
        go.Scatter(x=time_series['date'], y=time_series['cost_savings'],
                  name='Cost Savings', line=dict(color=COLOR_PALETTE["warning"])),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Rate (%)", row=1, col=2)
    fig.update_yaxes(title_text="CO₂ (kg)", row=2, col=1)
    fig.update_yaxes(title_text="Savings ($)", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Facility and packaging performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("🏭 Facility Performance")
        facility_perf = processor.get_facility_performance()
        
        # Top performers
        top_facilities = facility_perf.nlargest(5, 'reuse_rate')
        
        fig_facility = px.bar(
            top_facilities,
            x='facility_name',
            y='reuse_rate',
            color='reuse_rate',
            color_continuous_scale='Greens',
            title="Top 5 Facilities by Reuse Rate"
        )
        fig_facility.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_facility, use_container_width=True)
        
        # Display facility table
        st.subheader("Facility Performance Details")
        st.dataframe(
            facility_perf[['facility_name', 'reuse_rate', 'waste_rate', 'co2_saved', 'cost_savings']]
            .round(2)
            .style.background_gradient(subset=['reuse_rate'], cmap='RdYlGn')
        )
    
    with col2:
        st.header("📦 Packaging Performance")
        packaging_perf = processor.get_packaging_performance()
        
        # Packaging type comparison
        fig_packaging = px.bar(
            packaging_perf,
            x='packaging_type',
            y=['reuse_rate', 'waste_rate'],
            title="Reuse vs Waste Rate by Packaging Type",
            barmode='group',
            color_discrete_map={
                'reuse_rate': COLOR_PALETTE["primary"],
                'waste_rate': COLOR_PALETTE["accent"]
            }
        )
        fig_packaging.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_packaging, use_container_width=True)
        
        # Display packaging table
        st.subheader("Packaging Performance Details")
        st.dataframe(
            packaging_perf[['packaging_type', 'reuse_rate', 'waste_rate', 'co2_saved', 'cost_savings']]
            .round(2)
            .style.background_gradient(subset=['reuse_rate'], cmap='RdYlGn')
        )

if __name__ == "__main__":
    main()
