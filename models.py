"""
Data models for Green Supply Chain Dashboard
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np

@dataclass
class PackagingData:
    """Model for packaging usage and waste data"""
    date: datetime
    facility_id: str
    facility_name: str
    facility_type: str
    packaging_type: str
    total_produced: int
    total_returned: int
    total_reused: int
    total_recycled: int
    total_waste: int
    co2_saved: float
    cost_savings: float
    latitude: float
    longitude: float

@dataclass
class Facility:
    """Model for facility information"""
    facility_id: str
    name: str
    facility_type: str
    latitude: float
    longitude: float
    capacity: int
    operational_since: datetime

@dataclass 
class KPIMetrics:
    """Model for KPI calculations"""
    reuse_rate: float
    waste_rate: float
    recovery_rate: float
    co2_saved_total: float
    cost_savings_total: float
    efficiency_score: float

class DataProcessor:
    """Handles data processing and KPI calculations"""
    
    def __init__(self, data: List[PackagingData]):
        self.data = data
        self.df = self._to_dataframe()
    
    def _to_dataframe(self) -> pd.DataFrame:
        """Convert list of PackagingData to DataFrame"""
        return pd.DataFrame([
            {
                'date': item.date,
                'facility_id': item.facility_id,
                'facility_name': item.facility_name,
                'facility_type': item.facility_type,
                'packaging_type': item.packaging_type,
                'total_produced': item.total_produced,
                'total_returned': item.total_returned,
                'total_reused': item.total_reused,
                'total_recycled': item.total_recycled,
                'total_waste': item.total_waste,
                'co2_saved': item.co2_saved,
                'cost_savings': item.cost_savings,
                'latitude': item.latitude,
                'longitude': item.longitude
            }
            for item in self.data
        ])
    
    def calculate_kpis(self) -> KPIMetrics:
        """Calculate overall KPI metrics"""
        total_produced = self.df['total_produced'].sum()
        total_returned = self.df['total_returned'].sum()
        total_reused = self.df['total_reused'].sum()
        total_waste = self.df['total_waste'].sum()
        
        reuse_rate = (total_reused / total_produced * 100) if total_produced > 0 else 0
        waste_rate = (total_waste / total_produced * 100) if total_produced > 0 else 0
        recovery_rate = (total_returned / total_produced * 100) if total_produced > 0 else 0
        
        co2_saved_total = self.df['co2_saved'].sum()
        cost_savings_total = self.df['cost_savings'].sum()
        
        # Calculate efficiency score (weighted average of key metrics)
        efficiency_score = (
            (reuse_rate * 0.4) + 
            ((100 - waste_rate) * 0.3) + 
            (recovery_rate * 0.3)
        )
        
        return KPIMetrics(
            reuse_rate=reuse_rate,
            waste_rate=waste_rate,
            recovery_rate=recovery_rate,
            co2_saved_total=co2_saved_total,
            cost_savings_total=cost_savings_total,
            efficiency_score=efficiency_score
        )
    
    def get_facility_performance(self) -> pd.DataFrame:
        """Get performance metrics by facility"""
        facility_stats = self.df.groupby(['facility_id', 'facility_name']).agg({
            'total_produced': 'sum',
            'total_returned': 'sum', 
            'total_reused': 'sum',
            'total_waste': 'sum',
            'co2_saved': 'sum',
            'cost_savings': 'sum'
        }).reset_index()
        
        facility_stats['reuse_rate'] = (
            facility_stats['total_reused'] / facility_stats['total_produced'] * 100
        )
        facility_stats['waste_rate'] = (
            facility_stats['total_waste'] / facility_stats['total_produced'] * 100
        )
        facility_stats['recovery_rate'] = (
            facility_stats['total_returned'] / facility_stats['total_produced'] * 100
        )
        
        return facility_stats
    
    def get_packaging_performance(self) -> pd.DataFrame:
        """Get performance metrics by packaging type"""
        packaging_stats = self.df.groupby('packaging_type').agg({
            'total_produced': 'sum',
            'total_returned': 'sum',
            'total_reused': 'sum', 
            'total_waste': 'sum',
            'co2_saved': 'sum',
            'cost_savings': 'sum'
        }).reset_index()
        
        packaging_stats['reuse_rate'] = (
            packaging_stats['total_reused'] / packaging_stats['total_produced'] * 100
        )
        packaging_stats['waste_rate'] = (
            packaging_stats['total_waste'] / packaging_stats['total_produced'] * 100
        )
        
        return packaging_stats
    
    def get_time_series_data(self) -> pd.DataFrame:
        """Get time series data for trend analysis"""
        time_series = self.df.groupby('date').agg({
            'total_produced': 'sum',
            'total_returned': 'sum',
            'total_reused': 'sum',
            'total_waste': 'sum',
            'co2_saved': 'sum',
            'cost_savings': 'sum'
        }).reset_index()
        
        time_series['reuse_rate'] = (
            time_series['total_reused'] / time_series['total_produced'] * 100
        )
        time_series['waste_rate'] = (
            time_series['total_waste'] / time_series['total_produced'] * 100
        )
        
        return time_series.sort_values('date')

class SimulationEngine:
    """Handles what-if analysis simulations"""
    
    def __init__(self, base_data: pd.DataFrame):
        self.base_data = base_data.copy()
        
    def run_scenario(self, reuse_improvement: float, waste_reduction: float) -> Dict:
        """
        Run simulation scenario
        
        Args:
            reuse_improvement: Percentage improvement in reuse rate (0.1 = 10%)
            waste_reduction: Percentage reduction in waste (0.1 = 10%)
        """
        simulated_data = self.base_data.copy()
        
        # Apply improvements
        simulated_data['total_reused'] = (
            simulated_data['total_reused'] * (1 + reuse_improvement)
        ).astype(int)
        
        simulated_data['total_waste'] = (
            simulated_data['total_waste'] * (1 - waste_reduction)
        ).astype(int)
        
        # Ensure totals are consistent
        simulated_data['total_recycled'] = (
            simulated_data['total_returned'] - simulated_data['total_reused']
        ).clip(lower=0)
        
        # Calculate new CO2 and cost savings
        additional_reuse = simulated_data['total_reused'] - self.base_data['total_reused']
        waste_reduction_amount = self.base_data['total_waste'] - simulated_data['total_waste']
        
        # Estimate additional savings (simplified calculation)
        co2_factor = 0.5  # kg CO2 per unit
        cost_factor = 0.10  # $ per unit
        
        simulated_data['co2_saved'] = (
            self.base_data['co2_saved'] + 
            (additional_reuse + waste_reduction_amount) * co2_factor
        )
        
        simulated_data['cost_savings'] = (
            self.base_data['cost_savings'] + 
            (additional_reuse + waste_reduction_amount) * cost_factor
        )
        
        # Calculate impact metrics
        base_kpis = self._calculate_scenario_kpis(self.base_data)
        new_kpis = self._calculate_scenario_kpis(simulated_data)
        
        return {
            'base_metrics': base_kpis,
            'projected_metrics': new_kpis,
            'improvements': {
                'reuse_rate_improvement': new_kpis['reuse_rate'] - base_kpis['reuse_rate'],
                'waste_rate_reduction': base_kpis['waste_rate'] - new_kpis['waste_rate'],
                'additional_co2_saved': new_kpis['co2_saved'] - base_kpis['co2_saved'],
                'additional_cost_savings': new_kpis['cost_savings'] - base_kpis['cost_savings']
            }
        }
    
    def _calculate_scenario_kpis(self, data: pd.DataFrame) -> Dict:
        """Calculate KPIs for scenario data"""
        total_produced = data['total_produced'].sum()
        total_reused = data['total_reused'].sum()
        total_waste = data['total_waste'].sum()
        
        return {
            'reuse_rate': (total_reused / total_produced * 100) if total_produced > 0 else 0,
            'waste_rate': (total_waste / total_produced * 100) if total_produced > 0 else 0,
            'co2_saved': data['co2_saved'].sum(),
            'cost_savings': data['cost_savings'].sum()
        }
