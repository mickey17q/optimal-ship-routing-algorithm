"""
Weather simulation and cost calculations for ship routing.
Simulates wind, waves, and ocean currents.
"""

import numpy as np
from typing import Tuple
from grid import NavigationGrid, Cell


class WeatherSystem:
    """Simulates weather conditions and calculates routing costs."""
    
    def __init__(self, grid: NavigationGrid, seed: int = 42):
        """
        Initialize weather system.
        
        Args:
            grid: Navigation grid
            seed: Random seed for reproducibility
        """
        self.grid = grid
        self.rng = np.random.RandomState(seed)
        
        # Weather intensity maps
        self.wind_speed = np.zeros((grid.width, grid.height))
        self.wind_direction = np.zeros((grid.width, grid.height))
        self.wave_height = np.zeros((grid.width, grid.height))
        self.current_speed = np.zeros((grid.width, grid.height))
        self.current_direction = np.zeros((grid.width, grid.height))
        
    def generate_weather_pattern(self, pattern_type: str = 'moderate'):
        """
        Generate weather patterns across the grid.
        
        Args:
            pattern_type: 'calm', 'moderate', 'stormy'
        """
        if pattern_type == 'calm':
            wind_base, wind_var = 5, 3
            wave_base, wave_var = 0.5, 0.3
            current_base, current_var = 0.5, 0.2
        elif pattern_type == 'moderate':
            wind_base, wind_var = 15, 8
            wave_base, wave_var = 2.0, 1.0
            current_base, current_var = 1.0, 0.5
        else:  # stormy
            wind_base, wind_var = 30, 15
            wave_base, wave_var = 5.0, 2.5
            current_base, current_var = 2.0, 1.0
        
        # Generate smooth weather patterns using Perlin-like noise
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                # Use sine waves for smooth patterns
                noise_x = np.sin(x / 10.0) * np.cos(y / 15.0)
                noise_y = np.cos(x / 12.0) * np.sin(y / 8.0)
                
                # Wind
                self.wind_speed[x, y] = max(0, wind_base + wind_var * noise_x)
                self.wind_direction[x, y] = (noise_y + 1) * np.pi  # 0 to 2π
                
                # Waves (correlated with wind)
                self.wave_height[x, y] = max(0, wave_base + wave_var * noise_x)
                
                # Ocean currents
                self.current_speed[x, y] = max(0, current_base + current_var * noise_y)
                self.current_direction[x, y] = (noise_x + 1) * np.pi
    
    def add_storm(self, center_x: int, center_y: int, radius: int, intensity: float = 2.0):
        """
        Add a localized storm system.
        
        Args:
            center_x: Storm center X coordinate
            center_y: Storm center Y coordinate
            radius: Storm radius in cells
            intensity: Storm intensity multiplier
        """
        for x in range(max(0, center_x - radius), min(self.grid.width, center_x + radius + 1)):
            for y in range(max(0, center_y - radius), min(self.grid.height, center_y + radius + 1)):
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                if distance <= radius:
                    # Storm intensity decreases with distance from center
                    factor = intensity * (1 - distance / radius)
                    self.wind_speed[x, y] += 20 * factor
                    self.wave_height[x, y] += 3 * factor
    
    def calculate_weather_cost(self, cell: Cell, heading: float) -> float:
        """
        Calculate weather-related cost for a cell.
        
        Args:
            cell: Grid cell
            heading: Ship heading in radians (0 = East, π/2 = North)
            
        Returns:
            Weather cost multiplier (1.0 = no impact, higher = worse conditions)
        """
        x, y = cell.x, cell.y
        
        if cell.is_land:
            return 0.0
        
        # Base cost from wave height (rough seas slow down ships)
        wave_cost = 1.0 + (self.wave_height[x, y] / 10.0)
        
        # Wind impact (headwind vs tailwind)
        wind_dir = self.wind_direction[x, y]
        wind_speed = self.wind_speed[x, y]
        
        # Calculate relative wind angle
        wind_angle = abs(((heading - wind_dir + np.pi) % (2 * np.pi)) - np.pi)
        
        # Headwind increases cost, tailwind decreases it
        wind_factor = np.cos(wind_angle)  # -1 (headwind) to 1 (tailwind)
        wind_cost = 1.0 - (wind_factor * wind_speed / 100.0)
        
        # Current impact
        current_dir = self.current_direction[x, y]
        current_speed = self.current_speed[x, y]
        
        current_angle = abs(((heading - current_dir + np.pi) % (2 * np.pi)) - np.pi)
        current_factor = np.cos(current_angle)
        current_cost = 1.0 - (current_factor * current_speed / 50.0)
        
        # Combine all factors
        total_cost = wave_cost * wind_cost * current_cost
        
        return max(0.1, total_cost)  # Ensure positive cost
    
    def apply_weather_to_grid(self):
        """Apply weather costs to all grid cells."""
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell = self.grid.get_cell(x, y)
                if cell and not cell.is_land:
                    # Use average heading (East) for general weather cost
                    avg_cost = self.calculate_weather_cost(cell, 0.0)
                    cell.weather_cost = avg_cost - 1.0  # Store as additional cost
    
    def get_fuel_consumption(self, distance_km: float, weather_cost: float, 
                            ship_speed_knots: float = 20.0) -> float:
        """
        Calculate fuel consumption for a route segment.
        
        Args:
            distance_km: Distance in kilometers
            weather_cost: Weather cost multiplier
            ship_speed_knots: Ship speed in knots
            
        Returns:
            Fuel consumption in tons
        """
        # Convert km to nautical miles
        distance_nm = distance_km / 1.852
        
        # Base fuel consumption (tons per nautical mile)
        # Typical cargo ship: ~0.15 tons/nm at 20 knots
        base_consumption = 0.15
        
        # Weather increases fuel consumption
        fuel = distance_nm * base_consumption * weather_cost
        
        return fuel
    
    def get_weather_info(self, x: int, y: int) -> dict:
        """Get weather information for a specific cell."""
        if not (0 <= x < self.grid.width and 0 <= y < self.grid.height):
            return {}
        
        return {
            'wind_speed': float(self.wind_speed[x, y]),
            'wind_direction': float(self.wind_direction[x, y]),
            'wave_height': float(self.wave_height[x, y]),
            'current_speed': float(self.current_speed[x, y]),
            'current_direction': float(self.current_direction[x, y])
        }
    
    def __repr__(self):
        avg_wind = np.mean(self.wind_speed)
        avg_wave = np.mean(self.wave_height)
        return f"WeatherSystem(avg_wind={avg_wind:.1f}kts, avg_wave={avg_wave:.1f}m)"
