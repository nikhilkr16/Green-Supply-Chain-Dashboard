# Green Supply Chain Dashboard - AB InBev

A comprehensive sustainability tracking and optimization platform for packaging waste management and circular supply chain operations.

<img width="1819" height="905" alt="image" src="https://github.com/user-attachments/assets/a02eaadc-fb13-4fe5-b60c-3bed19a1da27" />

Project Link : https://green-supply-chain-dashboard.streamlit.app/

## 🌟 Overview

The Green Supply Chain Dashboard helps AB InBev track, visualize, and optimize packaging usage, waste, and recovery rates across their supply chain. It provides real-time insights for managers to identify bottlenecks in recycling/reuse and simulate the impact of waste reduction strategies.

## 🎯 Key Features

### 📊 Main Dashboard
- **Real-time KPIs**: Reuse rates, waste rates, CO₂ savings, cost savings
- **Performance Gauges**: Visual indicators for key metrics vs targets
- **Trend Analysis**: Time series visualization of performance over time
- **Facility Performance**: Ranking and analysis of facility-level metrics
- **Packaging Analysis**: Performance breakdown by packaging type

### 🔬 Simulation Tool
- **What-If Analysis**: Test impact of improvement scenarios
- **Predefined Scenarios**: Conservative, Moderate, and Aggressive improvement plans
- **Custom Parameters**: Adjust reuse improvement and waste reduction percentages
- **ROI Analysis**: Calculate payback periods and investment requirements
- **Environmental Impact**: Project CO₂ reduction and resource savings

### 🗺️ Reverse Logistics Tracker
- **Interactive Map**: Visualize facility network and material flows
- **Flow Analysis**: Track daily return flows and trends
- **Capacity Utilization**: Monitor facility capacity usage
- **Route Optimization**: Distance matrix and optimization recommendations
- **Performance Alerts**: Identify underperforming facilities and processes

### 📊 Sustainability Report
- **Comprehensive Reports**: Executive summaries and detailed analysis
- **Environmental Metrics**: CO₂, water, and energy savings calculations
- **Circular Economy Scoring**: Performance assessment against circular principles
- **Packaging Breakdown**: Detailed analysis by packaging type
- **Export Options**: Excel reports and PDF generation

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate sample data**:
   ```bash
   python data_generator.py
   ```

4. **Launch the dashboard**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 📁 Project Structure

```
green-supply-chain/
├── app.py                          # Main dashboard application
├── config.py                       # Configuration settings
├── models.py                       # Data models and processing logic
├── data_generator.py               # Sample data generation
├── requirements.txt                # Python dependencies
├── data/                          # Data storage directory
│   ├── sample_packaging_data.csv  # Generated sample data
│   └── facilities.csv             # Facility reference data
├── pages/                         # Streamlit multi-page components
│   ├── 1_🔬_Simulation_Tool.py    # What-if analysis tool
│   ├── 2_🗺️_Reverse_Logistics.py  # Logistics tracking and mapping
│   └── 3_📊_Sustainability_Report.py # Report generator
└── README.md                      # This file
```

## 📋 Data Model

### Packaging Data
- **Date**: Transaction date
- **Facility Information**: ID, name, type, location
- **Packaging Type**: Glass bottles, aluminum cans, plastic bottles, etc.
- **Volume Metrics**: Produced, returned, reused, recycled, waste
- **Impact Metrics**: CO₂ savings, cost savings

### Facility Types
- **Brewery**: Production facilities
- **Distribution Center**: Regional distribution hubs
- **Recycling Center**: Processing and recycling facilities
- **Collection Point**: Consumer return locations

## 🎛️ Key Performance Indicators

### Operational KPIs
- **Reuse Rate**: Percentage of returned packaging reused directly
- **Recovery Rate**: Percentage of produced packaging returned
- **Waste Rate**: Percentage of produced packaging that becomes waste
- **Efficiency Score**: Weighted average of key performance metrics

### Environmental KPIs
- **CO₂ Savings**: Emissions saved through reuse and recycling
- **Water Conservation**: Water saved vs new production
- **Energy Savings**: Energy saved vs new production
- **Landfill Diversion**: Units diverted from landfill disposal

### Financial KPIs
- **Cost Savings**: Direct cost savings from reuse and recycling
- **Transportation Efficiency**: Units moved per kilometer
- **ROI**: Return on investment for improvement initiatives

## 🔧 Configuration

Key settings can be modified in `config.py`:

- **Targets**: Reuse targets, waste reduction goals, CO₂ targets
- **Packaging Types**: Supported packaging categories
- **Simulation Scenarios**: Predefined improvement scenarios
- **Colors**: Dashboard color scheme
- **Data Paths**: File locations for data storage

## 📊 Sample Data

The system includes a data generator that creates realistic sample data:

- **8 Facilities** across Belgium (breweries, distribution centers, recycling centers)
- **5 Packaging Types** with different performance characteristics
- **12 Months** of daily transaction data
- **Seasonal Variations** and operational patterns
- **Performance Variability** across facilities and packaging types

## 🌍 Environmental Impact Calculations

### CO₂ Savings
- **Reuse**: Avoids energy-intensive production processes
- **Recycling**: Reduces raw material extraction and processing
- **Transportation**: Optimized routing reduces fuel consumption

### Resource Conservation
- **Water**: Significant savings in glass and aluminum packaging
- **Energy**: Reduced manufacturing energy requirements
- **Raw Materials**: Decreased virgin material consumption

### Circular Economy Metrics
- **Material Flow Analysis**: Track material loops and leakage
- **Circularity Indicators**: Measure progress toward circular economy
- **Waste Hierarchy**: Prioritize reduce, reuse, recycle

## 🔮 Simulation Capabilities

### Scenario Analysis
- **Conservative**: 5% reuse improvement, 10% waste reduction
- **Moderate**: 15% reuse improvement, 20% waste reduction
- **Aggressive**: 25% reuse improvement, 35% waste reduction
- **Custom**: User-defined parameters

### Impact Projections
- **Performance Metrics**: Projected KPI improvements
- **Environmental Benefits**: CO₂, water, and energy savings
- **Financial Returns**: Cost savings and ROI analysis
- **Implementation Timeline**: Phased rollout recommendations

## 📈 Success Metrics

The dashboard tracks progress against key success metrics:

### Environmental Targets
- **CO₂ Reduction**: 1,000 tonnes/year target
- **Reuse Rate**: 85% target for glass bottles
- **Waste Reduction**: 20% overall waste reduction
- **Recovery Rate**: 90% target for all packaging

### Operational Targets
- **Cycle Time**: Reduce reverse logistics cycle time
- **Cost Efficiency**: Lower transportation and processing costs
- **Quality**: Maintain high standards for reused packaging

## 🔧 Customization

### Adding New Data Sources
1. Update data models in `models.py`
2. Modify data processing in `DataProcessor` class
3. Add new visualizations in dashboard pages

### Custom KPIs
1. Define calculation logic in `models.py`
2. Add visualization components in dashboard pages
3. Update configuration settings in `config.py`

### Integration Options
- **ERP Systems**: Connect to existing enterprise systems
- **IoT Sensors**: Real-time data from production lines
- **Third-party APIs**: External data sources for benchmarking

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
- **Streamlit Cloud**: Easy cloud deployment
- **Docker**: Containerized deployment
- **Enterprise**: On-premises deployment options

## 🤝 Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate documentation for new features
3. Include sample data generators for new data types
4. Test all functionality before deployment

## 📞 Support

For technical support or feature requests:
- Review the documentation in this README
- Check the configuration options in `config.py`
- Examine the data models in `models.py`
- Test with the provided sample data

## 📄 License

This project is designed for AB InBev's internal sustainability tracking and optimization needs.

---

**Built with**: Python, Streamlit, Plotly, Pandas, Folium
**Version**: 1.0.0
**Last Updated**: January 2025
