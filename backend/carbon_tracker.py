"""
Carbon Emission Tracking and Environmental Impact Analysis.
Novel contribution: Green shipping route optimization.
"""

import numpy as np
from typing import List, Dict
from dataclasses import dataclass

from grid import Cell
from weather import WeatherSystem


@dataclass
class EmissionReport:
    """Environmental impact report for a route."""
    total_co2_tons: float
    total_nox_kg: float
    total_sox_kg: float
    carbon_cost_usd: float
    environmental_score: float  # 0-100, higher is better
    
    def to_dict(self) -> dict:
        return {
            'co2_tons': float(self.total_co2_tons),
            'nox_kg': float(self.total_nox_kg),
            'sox_kg': float(self.total_sox_kg),
            'carbon_cost_usd': float(self.carbon_cost_usd),
            'environmental_score': float(self.environmental_score)
        }


class CarbonTracker:
    """
    Tracks and optimizes carbon emissions for ship routes.
    
    Novel Features:
    - Real emission calculations based on IMO standards
    - Carbon credit cost estimation
    - Green route optimization
    - Comparison with air/road transport
    """
    
    def __init__(self, weather: WeatherSystem = None):
        self.weather = weather
        
        # Emission factors (grams per ton of fuel)
        self.co2_factor = 3114  # g CO2 per kg fuel (IMO standard)
        self.nox_factor = 87    # g NOx per kg fuel
        self.sox_factor = 54    # g SOx per kg fuel (low sulfur)
        
        # Carbon credit price ($/ton CO2)
        self.carbon_price = 50.0
    
    def calculate_emissions(self, path: List[Cell], fuel_tons: float) -> EmissionReport:
        """
        Calculate total emissions for a route.
        
        Args:
            path: Route path
            fuel_tons: Total fuel consumed in tons
        """
        # Convert fuel to kg
        fuel_kg = fuel_tons * 1000
        
        # Calculate emissions
        co2_tons = (fuel_kg * self.co2_factor) / 1_000_000  # Convert g to tons
        nox_kg = (fuel_kg * self.nox_factor) / 1000
        sox_kg = (fuel_kg * self.sox_factor) / 1000
        
        # Calculate carbon cost
        carbon_cost = co2_tons * self.carbon_price
        
        # Environmental score (lower emissions = higher score)
        # Baseline: 100 tons CO2 = score 0, 0 tons = score 100
        environmental_score = max(0, 100 - (co2_tons / 100) * 100)
        
        return EmissionReport(
            total_co2_tons=co2_tons,
            total_nox_kg=nox_kg,
            total_sox_kg=sox_kg,
            carbon_cost_usd=carbon_cost,
            environmental_score=environmental_score
        )
    
    def compare_with_alternatives(self, distance_km: float, 
                                 ship_emissions: EmissionReport) -> Dict[str, float]:
        """
        Compare ship emissions with other transport modes.
        
        Returns CO2 tons for different modes.
        """
        # Emission factors (kg CO2 per ton-km)
        air_factor = 0.602      # Air freight
        truck_factor = 0.062    # Road freight
        rail_factor = 0.022     # Rail freight
        ship_factor = 0.008     # Sea freight (our calculation)
        
        # Assume 1000 tons cargo
        cargo_tons = 1000
        ton_km = distance_km * cargo_tons
        
        return {
            'ship': ship_emissions.total_co2_tons,
            'air': (ton_km * air_factor) / 1000,
            'truck': (ton_km * truck_factor) / 1000,
            'rail': (ton_km * rail_factor) / 1000,
            'ship_advantage_vs_air': ((ton_km * air_factor) / 1000) / ship_emissions.total_co2_tons
        }
    
    def get_green_routing_suggestions(self, emissions: EmissionReport) -> List[str]:
        """Provide suggestions for reducing emissions."""
        suggestions = []
        
        if emissions.total_co2_tons > 50:
            suggestions.append("Consider slow steaming (reduced speed) to save 20-30% fuel")
        
        if emissions.environmental_score < 70:
            suggestions.append("Route through favorable currents to reduce fuel consumption")
            suggestions.append("Avoid high-wave areas to minimize resistance")
        
        suggestions.append(f"Carbon offset cost: ${emissions.carbon_cost_usd:.2f}")
        suggestions.append("Consider LNG fuel for 20-25% emission reduction")
        
        return suggestions
    
    def calculate_slow_steaming_impact(self, base_fuel: float, 
                                      speed_reduction_pct: float = 10) -> Dict[str, float]:
        """
        Calculate impact of slow steaming on emissions and time.
        
        Slow steaming: Reducing speed to save fuel (cubic relationship).
        """
        # Fuel consumption is roughly proportional to speed^3
        speed_factor = (1 - speed_reduction_pct / 100)
        fuel_reduction = 1 - (speed_factor ** 3)
        
        new_fuel = base_fuel * (1 - fuel_reduction)
        fuel_saved = base_fuel - new_fuel
        
        # Time increase is linear with speed reduction
        time_increase_pct = speed_reduction_pct / (1 - speed_reduction_pct / 100)
        
        # Emission reduction
        co2_saved = (fuel_saved * 1000 * self.co2_factor) / 1_000_000
        cost_saved = fuel_saved * 500  # $500/ton fuel
        carbon_credit_saved = co2_saved * self.carbon_price
        
        return {
            'fuel_saved_tons': fuel_saved,
            'fuel_saved_pct': fuel_reduction * 100,
            'co2_saved_tons': co2_saved,
            'cost_saved_usd': cost_saved,
            'carbon_credit_saved_usd': carbon_credit_saved,
            'time_increase_pct': time_increase_pct,
            'total_savings_usd': cost_saved + carbon_credit_saved
        }
