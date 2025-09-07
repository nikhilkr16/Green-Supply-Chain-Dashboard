"""
What-If Analysis Simulation Tool
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from models import SimulationEngine
from config import SIMULATION_SCENARIOS, COLOR_PALETTE

st.set_page_config(
    page_title="Simulation Tool",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 What-If Analysis Simulation")

@st.cache_data
def load_data():
    """Load the packaging data"""
    try:
        df = pd.read_csv('data/sample_packaging_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("Sample data not found. Please run data_generator.py first.")
        return pd.DataFrame()

def create_comparison_chart(base_metrics, projected_metrics, improvements):
    """Create comparison charts for simulation results"""
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Reuse Rate Comparison', 'Waste Rate Comparison', 
                       'CO₂ Savings Comparison', 'Cost Savings Comparison'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    categories = ['Current', 'Projected']
    
    # Reuse rate
    fig.add_trace(
        go.Bar(x=categories, y=[base_metrics['reuse_rate'], projected_metrics['reuse_rate']],
               name='Reuse Rate', marker_color=[COLOR_PALETTE["accent"], COLOR_PALETTE["primary"]]),
        row=1, col=1
    )
    
    # Waste rate
    fig.add_trace(
        go.Bar(x=categories, y=[base_metrics['waste_rate'], projected_metrics['waste_rate']],
               name='Waste Rate', marker_color=[COLOR_PALETTE["accent"], COLOR_PALETTE["primary"]]),
        row=1, col=2
    )
    
    # CO2 savings
    fig.add_trace(
        go.Bar(x=categories, y=[base_metrics['co2_saved'], projected_metrics['co2_saved']],
               name='CO₂ Saved', marker_color=[COLOR_PALETTE["accent"], COLOR_PALETTE["primary"]]),
        row=2, col=1
    )
    
    # Cost savings
    fig.add_trace(
        go.Bar(x=categories, y=[base_metrics['cost_savings'], projected_metrics['cost_savings']],
               name='Cost Savings', marker_color=[COLOR_PALETTE["accent"], COLOR_PALETTE["primary"]]),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Current vs Projected Performance")
    fig.update_yaxes(title_text="Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Rate (%)", row=1, col=2)
    fig.update_yaxes(title_text="CO₂ (kg)", row=2, col=1)
    fig.update_yaxes(title_text="Savings ($)", row=2, col=2)
    
    return fig

def create_impact_summary(improvements):
    """Create impact summary cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Reuse Rate Improvement",
            f"{improvements['reuse_rate_improvement']:.1f}%",
            delta=f"{improvements['reuse_rate_improvement']:.1f}%"
        )
    
    with col2:
        st.metric(
            "Waste Rate Reduction", 
            f"{improvements['waste_rate_reduction']:.1f}%",
            delta=f"-{improvements['waste_rate_reduction']:.1f}%"
        )
    
    with col3:
        st.metric(
            "Additional CO₂ Saved",
            f"{improvements['additional_co2_saved']:.0f} kg",
            delta=f"{improvements['additional_co2_saved']:.0f} kg"
        )
    
    with col4:
        st.metric(
            "Additional Cost Savings",
            f"${improvements['additional_cost_savings']:.0f}",
            delta=f"${improvements['additional_cost_savings']:.0f}"
        )

def main():
    """Main simulation interface"""
    
    # Load data
    df = load_data()
    if df.empty:
        st.stop()
    
    st.markdown("""
    Use this tool to simulate the impact of various improvements to your packaging supply chain.
    Adjust the parameters below to see how changes would affect your KPIs.
    """)
    
    # Simulation parameters
    st.header("🎛️ Simulation Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Quick Scenarios")
        scenario = st.selectbox(
            "Select a predefined scenario:",
            options=["Custom"] + list(SIMULATION_SCENARIOS.keys())
        )
        
        if scenario != "Custom":
            reuse_improvement = SIMULATION_SCENARIOS[scenario]["reuse_improvement"]
            waste_reduction = SIMULATION_SCENARIOS[scenario]["waste_reduction"]
            st.info(f"**{scenario} Scenario:**\n- Reuse improvement: {reuse_improvement*100:.0f}%\n- Waste reduction: {waste_reduction*100:.0f}%")
        else:
            reuse_improvement = 0.15
            waste_reduction = 0.20
    
    with col2:
        st.subheader("Custom Parameters")
        
        reuse_improvement = st.slider(
            "Reuse Rate Improvement (%)",
            min_value=0.0,
            max_value=50.0,
            value=reuse_improvement * 100 if scenario != "Custom" else 15.0,
            step=1.0
        ) / 100
        
        waste_reduction = st.slider(
            "Waste Reduction (%)", 
            min_value=0.0,
            max_value=50.0,
            value=waste_reduction * 100 if scenario != "Custom" else 20.0,
            step=1.0
        ) / 100
    
    # Date range for simulation
    st.header("📅 Analysis Period")
    date_range = st.date_input(
        "Select period for simulation",
        value=(df['date'].min(), df['date'].max()),
        min_value=df['date'].min(),
        max_value=df['date'].max()
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_period = df[
            (df['date'] >= pd.Timestamp(start_date)) & 
            (df['date'] <= pd.Timestamp(end_date))
        ]
    else:
        df_period = df
    
    # Run simulation
    if st.button("🚀 Run Simulation", type="primary"):
        with st.spinner("Running simulation..."):
            
            # Initialize simulation engine
            sim_engine = SimulationEngine(df_period)
            
            # Run scenario
            results = sim_engine.run_scenario(reuse_improvement, waste_reduction)
            
            # Display results
            st.header("📊 Simulation Results")
            
            # Impact summary
            st.subheader("Impact Summary")
            create_impact_summary(results['improvements'])
            
            # Comparison charts
            st.subheader("Performance Comparison")
            comparison_fig = create_comparison_chart(
                results['base_metrics'],
                results['projected_metrics'], 
                results['improvements']
            )
            st.plotly_chart(comparison_fig, use_container_width=True)
            
            # Detailed breakdown
            st.header("📋 Detailed Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Current Performance")
                current_df = pd.DataFrame([results['base_metrics']]).T
                current_df.columns = ['Value']
                current_df.index.name = 'Metric'
                st.dataframe(current_df.style.format("{:.2f}"))
            
            with col2:
                st.subheader("Projected Performance")
                projected_df = pd.DataFrame([results['projected_metrics']]).T
                projected_df.columns = ['Value']
                projected_df.index.name = 'Metric'
                st.dataframe(projected_df.style.format("{:.2f}"))
            
            # ROI Analysis
            st.header("💰 Return on Investment Analysis")
            
            # Simplified ROI calculation
            annual_cost_savings = results['improvements']['additional_cost_savings'] * 12  # Annualize
            estimated_investment = annual_cost_savings * 0.3  # Assume 30% of savings as investment
            roi_years = estimated_investment / annual_cost_savings if annual_cost_savings > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Estimated Investment", f"${estimated_investment:,.0f}")
            
            with col2:
                st.metric("Annual Savings", f"${annual_cost_savings:,.0f}")
            
            with col3:
                st.metric("Payback Period", f"{roi_years:.1f} years")
            
            # Environmental Impact
            st.header("🌍 Environmental Impact")
            
            annual_co2_reduction = results['improvements']['additional_co2_saved'] * 12 / 1000  # Convert to tonnes, annualize
            trees_equivalent = annual_co2_reduction * 40  # Rough estimate: 1 tonne CO2 = 40 trees
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Annual CO₂ Reduction", f"{annual_co2_reduction:.1f} tonnes")
            
            with col2:
                st.metric("Equivalent Trees Planted", f"{trees_equivalent:.0f} trees")
            
            # Implementation recommendations
            st.header("💡 Implementation Recommendations")
            
            if reuse_improvement > 0.2:
                st.warning("⚠️ **High reuse improvement target**: Consider phased implementation over 12-18 months")
            
            if waste_reduction > 0.3:
                st.warning("⚠️ **Aggressive waste reduction**: May require significant process changes")
            
            st.success("✅ **Recommended next steps:**")
            st.markdown("""
            1. **Pilot Program**: Start with top-performing facilities
            2. **Technology Investment**: Focus on sorting and cleaning equipment
            3. **Staff Training**: Implement comprehensive recycling training
            4. **Partner Network**: Expand relationships with recycling centers
            5. **Monitoring System**: Implement real-time tracking dashboards
            """)

if __name__ == "__main__":
    main()
