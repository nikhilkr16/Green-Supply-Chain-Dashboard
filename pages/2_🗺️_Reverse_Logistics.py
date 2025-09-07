"""
Reverse Logistics Tracking and Mapping
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

from config import COLOR_PALETTE

st.set_page_config(
    page_title="Reverse Logistics",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Reverse Logistics Tracker")

@st.cache_data
def load_data():
    """Load packaging and facilities data"""
    try:
        packaging_df = pd.read_csv('data/sample_packaging_data.csv')
        packaging_df['date'] = pd.to_datetime(packaging_df['date'])
        
        facilities_df = pd.read_csv('data/facilities.csv')
        
        return packaging_df, facilities_df
    except FileNotFoundError:
        st.error("Data files not found. Please run data_generator.py first.")
        return pd.DataFrame(), pd.DataFrame()

def create_flow_map(packaging_df, facilities_df):
    """Create map showing packaging flows between facilities"""
    
    if packaging_df.empty or facilities_df.empty:
        return None
    
    # Calculate center point
    center_lat = facilities_df['lat'].mean()
    center_lon = facilities_df['lon'].mean()
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=9,
        tiles='OpenStreetMap'
    )
    
    # Define colors for facility types
    facility_colors = {
        'Brewery': 'red',
        'Distribution Center': 'blue',
        'Recycling Center': 'green',
        'Collection Point': 'orange'
    }
    
    # Add facility markers with performance data
    for _, facility in facilities_df.iterrows():
        # Get aggregated data for this facility
        facility_data = packaging_df[packaging_df['facility_id'] == facility['facility_id']]
        
        if not facility_data.empty:
            total_produced = facility_data['total_produced'].sum()
            total_returned = facility_data['total_returned'].sum()
            total_reused = facility_data['total_reused'].sum()
            total_recycled = facility_data['total_recycled'].sum()
            total_waste = facility_data['total_waste'].sum()
            
            reuse_rate = (total_reused / total_produced * 100) if total_produced > 0 else 0
            return_rate = (total_returned / total_produced * 100) if total_produced > 0 else 0
            
            # Create popup with detailed information
            popup_html = f"""
            <div style="width:250px">
                <h4 style="color: {facility_colors.get(facility['type'], 'gray')}">
                    {facility['name']}
                </h4>
                <hr>
                <b>Type:</b> {facility['type']}<br>
                <b>Capacity:</b> {facility['capacity']:,} units<br>
                <hr>
                <b>Performance Metrics:</b><br>
                • Total Produced: {total_produced:,}<br>
                • Total Returned: {total_returned:,}<br>
                • Return Rate: {return_rate:.1f}%<br>
                • Reuse Rate: {reuse_rate:.1f}%<br>
                • Total Waste: {total_waste:,}<br>
            </div>
            """
            
            # Determine marker size based on volume
            if total_produced > 0:
                marker_size = min(max(total_produced / 10000, 5), 20)
            else:
                marker_size = 5
            
            folium.CircleMarker(
                location=[facility['lat'], facility['lon']],
                radius=marker_size,
                popup=folium.Popup(popup_html, max_width=300),
                color=facility_colors.get(facility['type'], 'gray'),
                fillColor=facility_colors.get(facility['type'], 'gray'),
                fillOpacity=0.7,
                weight=2
            ).add_to(m)
    
    # Add flow lines between related facilities
    breweries = facilities_df[facilities_df['type'] == 'Brewery']
    recycling_centers = facilities_df[facilities_df['type'] == 'Recycling Center']
    collection_points = facilities_df[facilities_df['type'] == 'Collection Point']
    
    # Draw flows from breweries to recycling centers
    for _, brewery in breweries.iterrows():
        for _, recycling in recycling_centers.iterrows():
            # Calculate flow volume (simplified)
            brewery_data = packaging_df[packaging_df['facility_id'] == brewery['facility_id']]
            if not brewery_data.empty:
                flow_volume = brewery_data['total_returned'].sum()
                if flow_volume > 0:
                    # Line width based on flow volume
                    line_weight = min(max(flow_volume / 50000, 1), 8)
                    
                    folium.PolyLine(
                        locations=[
                            [brewery['lat'], brewery['lon']],
                            [recycling['lat'], recycling['lon']]
                        ],
                        color='green',
                        weight=line_weight,
                        opacity=0.6,
                        popup=f"Flow: {flow_volume:,} units"
                    ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Facility Types</h4>
    <p><i class="fa fa-circle" style="color:red"></i> Brewery</p>
    <p><i class="fa fa-circle" style="color:blue"></i> Distribution Center</p>
    <p><i class="fa fa-circle" style="color:green"></i> Recycling Center</p>
    <p><i class="fa fa-circle" style="color:orange"></i> Collection Point</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_logistics_kpis(packaging_df):
    """Calculate and display logistics KPIs"""
    
    if packaging_df.empty:
        return
    
    # Calculate cycle times (simplified - using date differences)
    packaging_df_sorted = packaging_df.sort_values(['facility_id', 'date'])
    
    # Group by facility and calculate average time between returns
    cycle_times = []
    for facility_id in packaging_df['facility_id'].unique():
        facility_data = packaging_df_sorted[packaging_df_sorted['facility_id'] == facility_id]
        if len(facility_data) > 1:
            date_diffs = facility_data['date'].diff().dt.days.dropna()
            if not date_diffs.empty:
                avg_cycle = date_diffs.mean()
                cycle_times.append(avg_cycle)
    
    avg_cycle_time = np.mean(cycle_times) if cycle_times else 0
    
    # Calculate other logistics metrics
    total_distance = len(packaging_df) * 50  # Simplified: 50km average per transaction
    total_fuel_cost = total_distance * 0.15  # $0.15 per km
    
    # Transportation efficiency
    transport_efficiency = packaging_df['total_returned'].sum() / total_distance if total_distance > 0 else 0
    
    return {
        'avg_cycle_time': avg_cycle_time,
        'total_distance': total_distance,
        'total_fuel_cost': total_fuel_cost,
        'transport_efficiency': transport_efficiency
    }

def create_optimization_recommendations(packaging_df, facilities_df):
    """Generate optimization recommendations based on data analysis"""
    
    recommendations = []
    
    if packaging_df.empty:
        return recommendations
    
    # Analyze facility performance
    facility_performance = packaging_df.groupby(['facility_id', 'facility_name']).agg({
        'total_produced': 'sum',
        'total_returned': 'sum',
        'total_waste': 'sum'
    }).reset_index()
    
    facility_performance['return_rate'] = (
        facility_performance['total_returned'] / facility_performance['total_produced'] * 100
    )
    facility_performance['waste_rate'] = (
        facility_performance['total_waste'] / facility_performance['total_produced'] * 100
    )
    
    # Identify underperforming facilities
    low_return_facilities = facility_performance[facility_performance['return_rate'] < 70]
    high_waste_facilities = facility_performance[facility_performance['waste_rate'] > 20]
    
    if not low_return_facilities.empty:
        recommendations.append({
            'type': 'warning',
            'title': 'Low Return Rate Facilities',
            'message': f"Facilities with return rates below 70%: {', '.join(low_return_facilities['facility_name'].tolist())}",
            'action': 'Consider implementing incentive programs for returns'
        })
    
    if not high_waste_facilities.empty:
        recommendations.append({
            'type': 'danger',
            'title': 'High Waste Facilities', 
            'message': f"Facilities with waste rates above 20%: {', '.join(high_waste_facilities['facility_name'].tolist())}",
            'action': 'Immediate intervention required - review processes and training'
        })
    
    # Check facility distribution
    recycling_centers = facilities_df[facilities_df['type'] == 'Recycling Center']
    if len(recycling_centers) < 3:
        recommendations.append({
            'type': 'info',
            'title': 'Limited Recycling Infrastructure',
            'message': f"Only {len(recycling_centers)} recycling centers in network",
            'action': 'Consider expanding recycling center network to reduce transportation costs'
        })
    
    # Packaging type analysis
    packaging_performance = packaging_df.groupby('packaging_type').agg({
        'total_produced': 'sum',
        'total_returned': 'sum'
    }).reset_index()
    
    packaging_performance['return_rate'] = (
        packaging_performance['total_returned'] / packaging_performance['total_produced'] * 100
    )
    
    low_return_packaging = packaging_performance[packaging_performance['return_rate'] < 60]
    if not low_return_packaging.empty:
        recommendations.append({
            'type': 'warning',
            'title': 'Low Return Rate Packaging Types',
            'message': f"Poor return rates for: {', '.join(low_return_packaging['packaging_type'].tolist())}",
            'action': 'Review packaging design and return incentives for these types'
        })
    
    return recommendations

def main():
    """Main reverse logistics interface"""
    
    # Load data
    packaging_df, facilities_df = load_data()
    
    if packaging_df.empty or facilities_df.empty:
        st.stop()
    
    st.markdown("""
    Track and optimize the reverse flow of packaging materials from consumption back to production.
    This system helps identify bottlenecks and opportunities in your circular supply chain.
    """)
    
    # Filters
    st.header("🔍 Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        # Date range filter
        date_range = st.date_input(
            "Select Date Range",
            value=(packaging_df['date'].min(), packaging_df['date'].max()),
            min_value=packaging_df['date'].min(),
            max_value=packaging_df['date'].max()
        )
    
    with col2:
        # Packaging type filter
        packaging_types = st.multiselect(
            "Packaging Types",
            options=packaging_df['packaging_type'].unique(),
            default=packaging_df['packaging_type'].unique()
        )
    
    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = packaging_df[
            (packaging_df['date'] >= pd.Timestamp(start_date)) & 
            (packaging_df['date'] <= pd.Timestamp(end_date)) &
            (packaging_df['packaging_type'].isin(packaging_types))
        ]
    else:
        df_filtered = packaging_df[packaging_df['packaging_type'].isin(packaging_types)]
    
    # Logistics KPIs
    st.header("📊 Logistics Performance")
    
    logistics_kpis = create_logistics_kpis(df_filtered)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Avg Cycle Time",
            f"{logistics_kpis['avg_cycle_time']:.1f} days"
        )
    
    with col2:
        st.metric(
            "Total Distance",
            f"{logistics_kpis['total_distance']:,} km"
        )
    
    with col3:
        st.metric(
            "Fuel Costs",
            f"${logistics_kpis['total_fuel_cost']:,.0f}"
        )
    
    with col4:
        st.metric(
            "Transport Efficiency",
            f"{logistics_kpis['transport_efficiency']:.1f} units/km"
        )
    
    # Interactive map
    st.header("🗺️ Supply Chain Network")
    
    flow_map = create_flow_map(df_filtered, facilities_df)
    if flow_map:
        st_folium(flow_map, width=1200, height=600)
    else:
        st.error("Unable to create map - check data availability")
    
    # Flow analysis
    st.header("📈 Flow Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily flow trends
        daily_flows = df_filtered.groupby('date').agg({
            'total_returned': 'sum',
            'total_reused': 'sum',
            'total_recycled': 'sum'
        }).reset_index()
        
        fig_flows = px.line(
            daily_flows,
            x='date',
            y=['total_returned', 'total_reused', 'total_recycled'],
            title="Daily Return Flows",
            color_discrete_map={
                'total_returned': COLOR_PALETTE['info'],
                'total_reused': COLOR_PALETTE['primary'],
                'total_recycled': COLOR_PALETTE['secondary']
            }
        )
        fig_flows.update_layout(legend_title="Flow Type")
        st.plotly_chart(fig_flows, use_container_width=True)
    
    with col2:
        # Facility capacity utilization
        facility_utilization = df_filtered.groupby(['facility_id', 'facility_name']).agg({
            'total_returned': 'sum'
        }).reset_index()
        
        # Merge with capacity data
        facility_utilization = facility_utilization.merge(
            facilities_df[['facility_id', 'capacity']], 
            on='facility_id',
            how='left'
        )
        
        facility_utilization['utilization'] = (
            facility_utilization['total_returned'] / facility_utilization['capacity'] * 100
        )
        
        fig_util = px.bar(
            facility_utilization,
            x='facility_name',
            y='utilization',
            title="Facility Capacity Utilization (%)",
            color='utilization',
            color_continuous_scale='RdYlGn'
        )
        fig_util.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_util, use_container_width=True)
    
    # Route optimization section
    st.header("🛣️ Route Optimization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distance matrix (simplified)
        st.subheader("Facility Distance Matrix")
        
        # Create distance matrix between facilities
        distance_matrix = []
        for i, facility1 in facilities_df.iterrows():
            row = []
            for j, facility2 in facilities_df.iterrows():
                # Simplified distance calculation (Euclidean)
                distance = np.sqrt(
                    (facility1['lat'] - facility2['lat'])**2 + 
                    (facility1['lon'] - facility2['lon'])**2
                ) * 111  # Convert to approximate km
                row.append(distance)
            distance_matrix.append(row)
        
        distance_df = pd.DataFrame(
            distance_matrix,
            index=facilities_df['name'],
            columns=facilities_df['name']
        )
        
        st.dataframe(distance_df.round(1).style.background_gradient(cmap='Reds'))
    
    with col2:
        # Optimization suggestions
        st.subheader("Optimization Opportunities")
        
        recommendations = create_optimization_recommendations(df_filtered, facilities_df)
        
        for rec in recommendations:
            if rec['type'] == 'warning':
                st.warning(f"**{rec['title']}**: {rec['message']}\n\n*Action:* {rec['action']}")
            elif rec['type'] == 'danger':
                st.error(f"**{rec['title']}**: {rec['message']}\n\n*Action:* {rec['action']}")
            else:
                st.info(f"**{rec['title']}**: {rec['message']}\n\n*Action:* {rec['action']}")
        
        if not recommendations:
            st.success("✅ No major optimization opportunities identified. System performing well!")
    
    # Performance summary
    st.header("📋 Performance Summary")
    
    # Create summary table
    summary_data = df_filtered.groupby(['facility_type']).agg({
        'total_produced': 'sum',
        'total_returned': 'sum',
        'total_reused': 'sum',
        'total_recycled': 'sum',
        'total_waste': 'sum'
    }).reset_index()
    
    summary_data['return_rate'] = (
        summary_data['total_returned'] / summary_data['total_produced'] * 100
    )
    summary_data['reuse_rate'] = (
        summary_data['total_reused'] / summary_data['total_produced'] * 100
    )
    summary_data['waste_rate'] = (
        summary_data['total_waste'] / summary_data['total_produced'] * 100
    )
    
    st.dataframe(
        summary_data[['facility_type', 'return_rate', 'reuse_rate', 'waste_rate']]
        .round(2)
        .style.background_gradient(subset=['return_rate', 'reuse_rate'], cmap='RdYlGn')
        .background_gradient(subset=['waste_rate'], cmap='RdYlGn_r')
    )

if __name__ == "__main__":
    main()
