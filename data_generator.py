"""
Generate realistic sample data for Green Supply Chain Dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from config import PACKAGING_TYPES, FACILITY_TYPES

def generate_sample_data():
    """Generate realistic sample packaging data"""
    
    # Set random seed for reproducible data
    np.random.seed(42)
    random.seed(42)
    
    # Generate date range (last 12 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Facility data
    facilities = [
        {"id": "BR001", "name": "Brussels Brewery", "type": "Brewery", "lat": 50.8503, "lon": 4.3517, "capacity": 50000},
        {"id": "BR002", "name": "Leuven Brewery", "type": "Brewery", "lat": 50.8798, "lon": 4.7005, "capacity": 75000},
        {"id": "DC001", "name": "Antwerp Distribution", "type": "Distribution Center", "lat": 51.2194, "lon": 4.4025, "capacity": 100000},
        {"id": "DC002", "name": "Ghent Distribution", "type": "Distribution Center", "lat": 51.0500, "lon": 3.7303, "capacity": 80000},
        {"id": "RC001", "name": "Brussels Recycling", "type": "Recycling Center", "lat": 50.8465, "lon": 4.3524, "capacity": 30000},
        {"id": "RC002", "name": "Antwerp Recycling", "type": "Recycling Center", "lat": 51.2213, "lon": 4.4051, "capacity": 40000},
        {"id": "CP001", "name": "Leuven Collection", "type": "Collection Point", "lat": 50.8798, "lon": 4.7005, "capacity": 15000},
        {"id": "CP002", "name": "Ghent Collection", "type": "Collection Point", "lat": 51.0543, "lon": 3.7174, "capacity": 12000}
    ]
    
    data_records = []
    
    for date in date_range:
        for facility in facilities:
            for packaging_type in PACKAGING_TYPES:
                
                # Base production varies by facility type and packaging
                if facility["type"] == "Brewery":
                    base_production = random.randint(500, 2000)
                elif facility["type"] == "Distribution Center":
                    base_production = random.randint(1000, 3000)
                else:  # Recycling/Collection
                    base_production = 0
                
                # Add some seasonal variation and day-of-week effects
                seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365)
                weekly_factor = 1.0 if date.weekday() < 5 else 0.6  # Lower on weekends
                
                total_produced = int(base_production * seasonal_factor * weekly_factor)
                
                if total_produced > 0:
                    # Calculate return rates (varies by packaging type)
                    return_rates = {
                        "Glass Bottles": 0.85,
                        "Aluminum Cans": 0.75,
                        "Plastic Bottles": 0.60,
                        "Cardboard Cartons": 0.40,
                        "Wooden Crates": 0.95
                    }
                    
                    base_return_rate = return_rates.get(packaging_type, 0.7)
                    # Add some randomness
                    actual_return_rate = np.clip(
                        np.random.normal(base_return_rate, 0.1), 0.2, 0.98
                    )
                    
                    total_returned = int(total_produced * actual_return_rate)
                    
                    # Calculate reuse vs recycle (glass bottles have higher reuse)
                    if packaging_type == "Glass Bottles":
                        reuse_rate = np.random.normal(0.7, 0.1)
                    elif packaging_type == "Wooden Crates":
                        reuse_rate = np.random.normal(0.8, 0.1)
                    else:
                        reuse_rate = np.random.normal(0.3, 0.1)
                    
                    reuse_rate = np.clip(reuse_rate, 0.1, 0.9)
                    
                    total_reused = int(total_returned * reuse_rate)
                    total_recycled = total_returned - total_reused
                    total_waste = total_produced - total_returned
                    
                    # Calculate CO2 savings (kg)
                    co2_factors = {
                        "Glass Bottles": 0.5,
                        "Aluminum Cans": 0.8,
                        "Plastic Bottles": 0.3,
                        "Cardboard Cartons": 0.2,
                        "Wooden Crates": 0.1
                    }
                    
                    co2_saved = (total_reused + total_recycled) * co2_factors.get(packaging_type, 0.4)
                    
                    # Calculate cost savings ($)
                    cost_factors = {
                        "Glass Bottles": 0.15,
                        "Aluminum Cans": 0.12,
                        "Plastic Bottles": 0.08,
                        "Cardboard Cartons": 0.05,
                        "Wooden Crates": 0.25
                    }
                    
                    cost_savings = (total_reused + total_recycled) * cost_factors.get(packaging_type, 0.10)
                    
                    record = {
                        'date': date.strftime('%Y-%m-%d'),
                        'facility_id': facility["id"],
                        'facility_name': facility["name"],
                        'facility_type': facility["type"],
                        'packaging_type': packaging_type,
                        'total_produced': total_produced,
                        'total_returned': total_returned,
                        'total_reused': total_reused,
                        'total_recycled': total_recycled,
                        'total_waste': total_waste,
                        'co2_saved': round(co2_saved, 2),
                        'cost_savings': round(cost_savings, 2),
                        'latitude': facility["lat"],
                        'longitude': facility["lon"]
                    }
                    
                    data_records.append(record)
    
    # Filter out records with zero production for cleaner data
    data_records = [r for r in data_records if r['total_produced'] > 0]
    
    return pd.DataFrame(data_records)

def generate_facilities_data():
    """Generate facilities reference data"""
    facilities = [
        {"facility_id": "BR001", "name": "Brussels Brewery", "type": "Brewery", "lat": 50.8503, "lon": 4.3517, "capacity": 50000},
        {"facility_id": "BR002", "name": "Leuven Brewery", "type": "Brewery", "lat": 50.8798, "lon": 4.7005, "capacity": 75000},
        {"facility_id": "DC001", "name": "Antwerp Distribution", "type": "Distribution Center", "lat": 51.2194, "lon": 4.4025, "capacity": 100000},
        {"facility_id": "DC002", "name": "Ghent Distribution", "type": "Distribution Center", "lat": 51.0500, "lon": 3.7303, "capacity": 80000},
        {"facility_id": "RC001", "name": "Brussels Recycling", "type": "Recycling Center", "lat": 50.8465, "lon": 4.3524, "capacity": 30000},
        {"facility_id": "RC002", "name": "Antwerp Recycling", "type": "Recycling Center", "lat": 51.2213, "lon": 4.4051, "capacity": 40000},
        {"facility_id": "CP001", "name": "Leuven Collection", "type": "Collection Point", "lat": 50.8798, "lon": 4.7005, "capacity": 15000},
        {"facility_id": "CP002", "name": "Ghent Collection", "type": "Collection Point", "lat": 51.0543, "lon": 3.7174, "capacity": 12000}
    ]
    
    return pd.DataFrame(facilities)

if __name__ == "__main__":
    # Generate and save sample data
    print("Generating sample packaging data...")
    packaging_data = generate_sample_data()
    packaging_data.to_csv('data/sample_packaging_data.csv', index=False)
    print(f"Generated {len(packaging_data)} records")
    
    print("Generating facilities data...")
    facilities_data = generate_facilities_data()
    facilities_data.to_csv('data/facilities.csv', index=False)
    print(f"Generated {len(facilities_data)} facility records")
    
    print("Sample data generation complete!")
