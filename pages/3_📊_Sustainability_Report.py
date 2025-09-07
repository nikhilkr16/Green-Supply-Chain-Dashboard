"""
Sustainability Impact Report Generator
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import base64
from io import BytesIO

from config import COLOR_PALETTE, CO2_REDUCTION_TARGET, REUSE_TARGET

st.set_page_config(
    page_title="Sustainability Report",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sustainability Impact Report")

@st.cache_data
def load_data():
    """Load packaging data"""
    try:
        df = pd.read_csv('data/sample_packaging_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("Sample data not found. Please run data_generator.py first.")
        return pd.DataFrame()

def calculate_environmental_impact(df):
    """Calculate comprehensive environmental impact metrics"""
    
    if df.empty:
        return {}
    
    # Basic metrics
    total_produced = df['total_produced'].sum()
    total_returned = df['total_returned'].sum()
    total_reused = df['total_reused'].sum()
    total_recycled = df['total_recycled'].sum()
    total_waste = df['total_waste'].sum()
    total_co2_saved = df['co2_saved'].sum()
    
    # Rates
    reuse_rate = (total_reused / total_produced * 100) if total_produced > 0 else 0
    recycling_rate = (total_recycled / total_produced * 100) if total_produced > 0 else 0
    waste_rate = (total_waste / total_produced * 100) if total_produced > 0 else 0
    recovery_rate = (total_returned / total_produced * 100) if total_produced > 0 else 0
    
    # Environmental calculations
    # CO2 impact (assuming saved CO2 vs if everything was new production)
    co2_per_unit_avoided = 0.5  # kg CO2 per unit if not reused/recycled
    total_co2_avoided = (total_reused + total_recycled) * co2_per_unit_avoided
    
    # Water savings (liters per unit)
    water_per_unit_saved = {
        'Glass Bottles': 15,
        'Aluminum Cans': 25,
        'Plastic Bottles': 8,
        'Cardboard Cartons': 5,
        'Wooden Crates': 2
    }
    
    water_saved = 0
    for packaging_type in df['packaging_type'].unique():
        type_data = df[df['packaging_type'] == packaging_type]
        saved_units = type_data['total_reused'].sum() + type_data['total_recycled'].sum()
        water_saved += saved_units * water_per_unit_saved.get(packaging_type, 10)
    
    # Energy savings (kWh per unit)
    energy_per_unit_saved = {
        'Glass Bottles': 0.8,
        'Aluminum Cans': 2.5,
        'Plastic Bottles': 0.6,
        'Cardboard Cartons': 0.3,
        'Wooden Crates': 0.1
    }
    
    energy_saved = 0
    for packaging_type in df['packaging_type'].unique():
        type_data = df[df['packaging_type'] == packaging_type]
        saved_units = type_data['total_reused'].sum() + type_data['total_recycled'].sum()
        energy_saved += saved_units * energy_per_unit_saved.get(packaging_type, 1.0)
    
    # Waste diverted from landfill
    landfill_diversion_rate = recovery_rate
    landfill_waste_avoided = total_returned  # units
    
    # Circular economy score (0-100)
    circular_score = (reuse_rate * 0.5) + (recycling_rate * 0.3) + ((100 - waste_rate) * 0.2)
    
    return {
        'total_produced': total_produced,
        'total_returned': total_returned,
        'total_reused': total_reused,
        'total_recycled': total_recycled,
        'total_waste': total_waste,
        'reuse_rate': reuse_rate,
        'recycling_rate': recycling_rate,
        'waste_rate': waste_rate,
        'recovery_rate': recovery_rate,
        'co2_saved': total_co2_saved / 1000,  # Convert to tonnes
        'co2_avoided': total_co2_avoided / 1000,  # Convert to tonnes
        'water_saved': water_saved / 1000,  # Convert to cubic meters
        'energy_saved': energy_saved,  # kWh
        'landfill_waste_avoided': landfill_waste_avoided,
        'circular_score': circular_score
    }

def create_impact_dashboard(metrics):
    """Create comprehensive impact visualization"""
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Packaging Flow (units)', 'Recovery Rates (%)',
            'Environmental Savings', 'Circular Economy Score',
            'CO₂ Impact (tonnes)', 'Resource Conservation'
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "indicator"}],
            [{"type": "bar"}, {"type": "bar"}]
        ]
    )
    
    # 1. Packaging flow
    categories = ['Produced', 'Returned', 'Reused', 'Recycled', 'Waste']
    values = [metrics['total_produced'], metrics['total_returned'], 
              metrics['total_reused'], metrics['total_recycled'], metrics['total_waste']]
    colors = [COLOR_PALETTE['info'], COLOR_PALETTE['primary'], COLOR_PALETTE['success'], 
              COLOR_PALETTE['secondary'], COLOR_PALETTE['danger']]
    
    fig.add_trace(
        go.Bar(x=categories, y=values, marker_color=colors, name="Flow"),
        row=1, col=1
    )
    
    # 2. Recovery rates
    rate_categories = ['Reuse Rate', 'Recycling Rate', 'Waste Rate']
    rate_values = [metrics['reuse_rate'], metrics['recycling_rate'], metrics['waste_rate']]
    rate_colors = [COLOR_PALETTE['primary'], COLOR_PALETTE['secondary'], COLOR_PALETTE['danger']]
    
    fig.add_trace(
        go.Bar(x=rate_categories, y=rate_values, marker_color=rate_colors, name="Rates"),
        row=1, col=2
    )
    
    # 3. Environmental savings
    env_categories = ['Water Saved (m³)', 'Energy Saved (kWh)']
    env_values = [metrics['water_saved'], metrics['energy_saved']]
    
    fig.add_trace(
        go.Scatter(x=env_categories, y=env_values, mode='markers+text',
                  marker=dict(size=20, color=COLOR_PALETTE['success']),
                  text=[f"{v:.0f}" for v in env_values], textposition="top center",
                  name="Savings"),
        row=2, col=1
    )
    
    # 4. Circular economy score gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=metrics['circular_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Circular Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': COLOR_PALETTE['primary']},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "yellow"},
                    {'range': [75, 100], 'color': "lightgreen"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4},
                             'thickness': 0.75, 'value': 90}
            }
        ),
        row=2, col=2
    )
    
    # 5. CO2 impact
    co2_categories = ['CO₂ Saved', 'CO₂ Avoided']
    co2_values = [metrics['co2_saved'], metrics['co2_avoided']]
    
    fig.add_trace(
        go.Bar(x=co2_categories, y=co2_values, 
               marker_color=[COLOR_PALETTE['success'], COLOR_PALETTE['primary']], 
               name="CO₂"),
        row=3, col=1
    )
    
    # 6. Resource conservation
    resource_categories = ['Units Diverted from Landfill']
    resource_values = [metrics['landfill_waste_avoided']]
    
    fig.add_trace(
        go.Bar(x=resource_categories, y=resource_values,
               marker_color=[COLOR_PALETTE['warning']], name="Conservation"),
        row=3, col=2
    )
    
    fig.update_layout(height=1000, showlegend=False, title_text="Sustainability Impact Dashboard")
    
    return fig

def generate_report_summary(metrics, period_days):
    """Generate executive summary text"""
    
    # Annualize metrics
    annual_factor = 365 / period_days if period_days > 0 else 1
    
    summary = f"""
    ## Executive Summary
    
    **Reporting Period**: {period_days} days
    
    ### 🎯 Key Achievements
    
    - **{metrics['recovery_rate']:.1f}%** packaging recovery rate achieved
    - **{metrics['co2_saved'] * annual_factor:.0f} tonnes** of CO₂ emissions saved annually
    - **{metrics['water_saved'] * annual_factor:.0f} m³** of water conserved annually
    - **{metrics['energy_saved'] * annual_factor:.0f} kWh** of energy saved annually
    
    ### ♻️ Circular Economy Performance
    
    - **Reuse Rate**: {metrics['reuse_rate']:.1f}% (Target: {REUSE_TARGET}%)
    - **Recycling Rate**: {metrics['recycling_rate']:.1f}%
    - **Waste Reduction**: {100 - metrics['waste_rate']:.1f}%
    - **Circular Economy Score**: {metrics['circular_score']:.0f}/100
    
    ### 🌍 Environmental Impact
    
    - **{metrics['landfill_waste_avoided']:,.0f} units** diverted from landfill
    - **{metrics['co2_avoided'] * annual_factor:.0f} tonnes** of CO₂ emissions avoided through reuse/recycling
    - Equivalent to planting **{metrics['co2_avoided'] * annual_factor * 40:.0f} trees** annually
    
    ### 📈 Performance vs Targets
    
    """
    
    # Target analysis
    if metrics['reuse_rate'] >= REUSE_TARGET:
        summary += f"✅ **Reuse target exceeded** by {metrics['reuse_rate'] - REUSE_TARGET:.1f} percentage points\n\n"
    else:
        summary += f"⚠️ **Reuse target gap** of {REUSE_TARGET - metrics['reuse_rate']:.1f} percentage points\n\n"
    
    if metrics['co2_saved'] * annual_factor >= CO2_REDUCTION_TARGET:
        summary += f"✅ **CO₂ reduction target achieved**\n\n"
    else:
        summary += f"📊 **CO₂ target progress**: {(metrics['co2_saved'] * annual_factor / CO2_REDUCTION_TARGET * 100):.0f}% complete\n\n"
    
    return summary

def create_packaging_breakdown(df):
    """Create detailed packaging type breakdown"""
    
    packaging_metrics = df.groupby('packaging_type').agg({
        'total_produced': 'sum',
        'total_returned': 'sum',
        'total_reused': 'sum',
        'total_recycled': 'sum',
        'total_waste': 'sum',
        'co2_saved': 'sum'
    }).reset_index()
    
    packaging_metrics['reuse_rate'] = (
        packaging_metrics['total_reused'] / packaging_metrics['total_produced'] * 100
    )
    packaging_metrics['recovery_rate'] = (
        packaging_metrics['total_returned'] / packaging_metrics['total_produced'] * 100
    )
    packaging_metrics['waste_rate'] = (
        packaging_metrics['total_waste'] / packaging_metrics['total_produced'] * 100
    )
    
    return packaging_metrics

def export_to_excel(metrics, df, packaging_breakdown):
    """Export report data to Excel"""
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Executive summary
        summary_data = pd.DataFrame([metrics])
        summary_data.to_excel(writer, sheet_name='Executive Summary', index=False)
        
        # Raw data
        df.to_excel(writer, sheet_name='Raw Data', index=False)
        
        # Packaging breakdown
        packaging_breakdown.to_excel(writer, sheet_name='Packaging Analysis', index=False)
        
        # Time series
        time_series = df.groupby('date').agg({
            'total_produced': 'sum',
            'total_returned': 'sum',
            'total_reused': 'sum',
            'total_waste': 'sum',
            'co2_saved': 'sum'
        }).reset_index()
        time_series.to_excel(writer, sheet_name='Time Series', index=False)
    
    return output.getvalue()

def main():
    """Main sustainability report interface"""
    
    # Load data
    df = load_data()
    if df.empty:
        st.stop()
    
    st.markdown("""
    Generate comprehensive sustainability impact reports to track environmental performance,
    demonstrate progress toward targets, and communicate achievements to stakeholders.
    """)
    
    # Report configuration
    st.header("⚙️ Report Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Date range
        date_range = st.date_input(
            "Report Period",
            value=(df['date'].max() - timedelta(days=90), df['date'].max()),
            min_value=df['date'].min(),
            max_value=df['date'].max()
        )
    
    with col2:
        # Report type
        report_type = st.selectbox(
            "Report Type",
            ["Executive Summary", "Detailed Analysis", "Regulatory Compliance", "Investor Report"]
        )
    
    # Apply date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[
            (df['date'] >= pd.Timestamp(start_date)) & 
            (df['date'] <= pd.Timestamp(end_date))
        ]
        period_days = (end_date - start_date).days + 1
    else:
        df_filtered = df
        period_days = (df['date'].max() - df['date'].min()).days + 1
    
    if df_filtered.empty:
        st.warning("No data available for selected period.")
        return
    
    # Calculate metrics
    metrics = calculate_environmental_impact(df_filtered)
    
    # Generate report
    if st.button("📊 Generate Report", type="primary"):
        
        with st.spinner("Generating sustainability report..."):
            
            # Report header
            st.markdown("---")
            st.markdown(f"# 🌱 Sustainability Impact Report")
            st.markdown(f"**Report Type**: {report_type}")
            st.markdown(f"**Period**: {date_range[0]} to {date_range[1]} ({period_days} days)")
            st.markdown(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            st.markdown("---")
            
            # Executive summary
            summary_text = generate_report_summary(metrics, period_days)
            st.markdown(summary_text)
            
            # Impact dashboard
            st.header("📊 Impact Dashboard")
            impact_fig = create_impact_dashboard(metrics)
            st.plotly_chart(impact_fig, use_container_width=True)
            
            # Detailed metrics
            st.header("📋 Detailed Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("♻️ Circular Economy")
                st.metric("Reuse Rate", f"{metrics['reuse_rate']:.1f}%")
                st.metric("Recycling Rate", f"{metrics['recycling_rate']:.1f}%") 
                st.metric("Recovery Rate", f"{metrics['recovery_rate']:.1f}%")
                st.metric("Circular Score", f"{metrics['circular_score']:.0f}/100")
            
            with col2:
                st.subheader("🌍 Environmental")
                st.metric("CO₂ Saved", f"{metrics['co2_saved']:.1f} tonnes")
                st.metric("CO₂ Avoided", f"{metrics['co2_avoided']:.1f} tonnes")
                st.metric("Water Saved", f"{metrics['water_saved']:.0f} m³")
                st.metric("Energy Saved", f"{metrics['energy_saved']:.0f} kWh")
            
            with col3:
                st.subheader("📦 Operations")
                st.metric("Total Produced", f"{metrics['total_produced']:,}")
                st.metric("Total Returned", f"{metrics['total_returned']:,}")
                st.metric("Waste Diverted", f"{metrics['landfill_waste_avoided']:,}")
                st.metric("Waste Rate", f"{metrics['waste_rate']:.1f}%")
            
            # Packaging type analysis
            st.header("📦 Packaging Type Analysis")
            
            packaging_breakdown = create_packaging_breakdown(df_filtered)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Reuse rate by packaging type
                fig_reuse = px.bar(
                    packaging_breakdown.sort_values('reuse_rate', ascending=True),
                    x='reuse_rate',
                    y='packaging_type',
                    orientation='h',
                    title="Reuse Rate by Packaging Type",
                    color='reuse_rate',
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig_reuse, use_container_width=True)
            
            with col2:
                # CO2 savings by packaging type
                fig_co2 = px.pie(
                    packaging_breakdown,
                    values='co2_saved',
                    names='packaging_type',
                    title="CO₂ Savings by Packaging Type"
                )
                st.plotly_chart(fig_co2, use_container_width=True)
            
            # Performance table
            st.subheader("Performance Summary Table")
            display_cols = ['packaging_type', 'total_produced', 'reuse_rate', 'recovery_rate', 'waste_rate', 'co2_saved']
            st.dataframe(
                packaging_breakdown[display_cols].round(2)
                .style.background_gradient(subset=['reuse_rate', 'recovery_rate'], cmap='RdYlGn')
                .background_gradient(subset=['waste_rate'], cmap='RdYlGn_r')
                .format({'total_produced': '{:,}', 'co2_saved': '{:.1f}'})
            )
            
            # Recommendations
            st.header("💡 Recommendations")
            
            # Generate recommendations based on performance
            recommendations = []
            
            if metrics['reuse_rate'] < REUSE_TARGET:
                gap = REUSE_TARGET - metrics['reuse_rate']
                recommendations.append(f"🎯 **Increase reuse rate by {gap:.1f}% to meet target**")
                recommendations.append("   - Improve packaging collection systems")
                recommendations.append("   - Enhance cleaning and quality control processes")
            
            if metrics['waste_rate'] > 15:
                recommendations.append("⚠️ **Address high waste rate**")
                recommendations.append("   - Analyze waste causes and implement prevention measures")
                recommendations.append("   - Improve consumer education on proper returns")
            
            low_performing_packaging = packaging_breakdown[packaging_breakdown['reuse_rate'] < 50]
            if not low_performing_packaging.empty:
                packaging_list = ", ".join(low_performing_packaging['packaging_type'].tolist())
                recommendations.append(f"📦 **Focus improvement efforts on: {packaging_list}**")
                recommendations.append("   - Review packaging design for reusability")
                recommendations.append("   - Enhance return incentives for these types")
            
            if metrics['circular_score'] < 75:
                recommendations.append("♻️ **Improve overall circular economy performance**")
                recommendations.append("   - Implement comprehensive circular design principles")
                recommendations.append("   - Expand partnership network for returns and recycling")
            
            for rec in recommendations:
                st.markdown(rec)
            
            if not recommendations:
                st.success("✅ **Excellent performance!** Continue current practices and explore advanced optimization opportunities.")
            
            # Export options
            st.header("📥 Export Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Excel export
                excel_data = export_to_excel(metrics, df_filtered, packaging_breakdown)
                st.download_button(
                    label="📊 Download Excel Report",
                    data=excel_data,
                    file_name=f"sustainability_report_{start_date}_{end_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                # PDF export note
                st.info("💡 **PDF Export**: Use your browser's print function to save this report as PDF")
            
            st.markdown("---")
            st.markdown("*Report generated by Green Supply Chain Dashboard - AB InBev*")

if __name__ == "__main__":
    main()
