"""
Configuration settings for Green Supply Chain Dashboard
"""

# Dashboard settings
DASHBOARD_TITLE = "Green Supply Chain Dashboard - AB InBev"
COMPANY_NAME = "AB InBev"

# Data file paths
DATA_DIR = "data"
SAMPLE_DATA_FILE = f"{DATA_DIR}/sample_packaging_data.csv"
FACILITIES_DATA_FILE = f"{DATA_DIR}/facilities.csv"

# KPI targets and thresholds
REUSE_TARGET = 85.0  # Target reuse percentage
WASTE_REDUCTION_TARGET = 20.0  # Target waste reduction percentage
CO2_REDUCTION_TARGET = 1000.0  # Target CO2 reduction in tonnes/year

# Packaging types
PACKAGING_TYPES = [
    "Glass Bottles",
    "Aluminum Cans", 
    "Plastic Bottles",
    "Cardboard Cartons",
    "Wooden Crates"
]

# Facility types
FACILITY_TYPES = [
    "Brewery",
    "Distribution Center",
    "Recycling Center",
    "Collection Point"
]

# Colors for visualizations
COLOR_PALETTE = {
    "primary": "#00A651",  # AB InBev Green
    "secondary": "#FFD100",  # AB InBev Yellow
    "accent": "#E31E24",  # AB InBev Red
    "success": "#28A745",
    "warning": "#FFC107", 
    "danger": "#DC3545",
    "info": "#17A2B8"
}

# Simulation parameters
SIMULATION_SCENARIOS = {
    "Conservative": {"reuse_improvement": 0.05, "waste_reduction": 0.10},
    "Moderate": {"reuse_improvement": 0.15, "waste_reduction": 0.20},
    "Aggressive": {"reuse_improvement": 0.25, "waste_reduction": 0.35}
}
