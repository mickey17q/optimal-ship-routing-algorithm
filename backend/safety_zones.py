"""
Advanced features: Danger zones, pirate areas, and restricted regions.
Novel contribution to maritime routing safety.
"""

import numpy as np
from typing import List, Tuple, Set
from dataclasses import dataclass

from grid import NavigationGrid, Cell


@dataclass
class DangerZone:
    """Represents a dangerous area (pirates, military, etc.)."""
    center_x: int
    center_y: int
    radius: int
    danger_level: float  # 0.0 to 1.0
    zone_type: str  # 'pirate', 'military', 'storm', 'shallow'
    
    def contains(self, cell: Cell) -> bool:
        """Check if cell is in danger zone."""
        distance = np.sqrt((cell.x - self.center_x)**2 + (cell.y - self.center_y)**2)
        return distance <= self.radius
    
    def get_risk(self, cell: Cell) -> float:
        """Get risk level at cell (decreases with distance from center)."""
        distance = np.sqrt((cell.x - self.center_x)**2 + (cell.y - self.center_y)**2)
        if distance > self.radius:
            return 0.0
        # Risk decreases linearly from center
        return self.danger_level * (1.0 - distance / self.radius)


class SafetyManager:
    """Manages safety zones and danger areas for routing."""
    
    def __init__(self, grid: NavigationGrid):
        self.grid = grid
        self.danger_zones: List[DangerZone] = []
        self.safe_corridors: List[Tuple[Cell, Cell]] = []
        
    def add_pirate_zone(self, center_x: int, center_y: int, radius: int, 
                       danger_level: float = 0.8):
        """Add a pirate-infested area."""
        zone = DangerZone(center_x, center_y, radius, danger_level, 'pirate')
        self.danger_zones.append(zone)
    
    def add_military_zone(self, center_x: int, center_y: int, radius: int):
        """Add a restricted military area (absolute no-go)."""
        zone = DangerZone(center_x, center_y, radius, 1.0, 'military')
        self.danger_zones.append(zone)
        
        # Mark as impassable
        for x in range(max(0, center_x - radius), 
                      min(self.grid.width, center_x + radius + 1)):
            for y in range(max(0, center_y - radius), 
                          min(self.grid.height, center_y + radius + 1)):
                if (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                    cell = self.grid.get_cell(x, y)
                    if cell:
                        cell.is_land = True  # Treat as obstacle
    
    def add_shallow_water_zone(self, center_x: int, center_y: int, radius: int):
        """Add shallow water area (risky for large ships)."""
        zone = DangerZone(center_x, center_y, radius, 0.6, 'shallow')
        self.danger_zones.append(zone)
    
    def get_total_risk(self, cell: Cell) -> float:
        """Calculate total risk at a cell from all danger zones."""
        total_risk = 0.0
        for zone in self.danger_zones:
            total_risk += zone.get_risk(cell)
        return min(total_risk, 1.0)  # Cap at 1.0
    
    def apply_safety_costs(self):
        """Apply safety costs to grid cells."""
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell = self.grid.get_cell(x, y)
                if cell and not cell.is_land:
                    risk = self.get_total_risk(cell)
                    # Increase cost based on risk
                    cell.base_cost += risk * 5.0  # High penalty for dangerous areas
    
    def is_safe_route(self, path: List[Cell], max_risk: float = 0.5) -> bool:
        """Check if a route is safe (below risk threshold)."""
        for cell in path:
            if self.get_total_risk(cell) > max_risk:
                return False
        return True
    
    def get_route_safety_score(self, path: List[Cell]) -> float:
        """Calculate overall safety score for a route (0-1, higher is safer)."""
        if not path:
            return 0.0
        
        total_risk = sum(self.get_total_risk(cell) for cell in path)
        avg_risk = total_risk / len(path)
        return 1.0 - avg_risk
    
    def create_realistic_scenario(self):
        """Create a realistic maritime scenario with various danger zones."""
        # Pirate zones (Somalia, Gulf of Guinea style)
        self.add_pirate_zone(20, 30, 8, danger_level=0.9)
        self.add_pirate_zone(75, 60, 6, danger_level=0.7)
        
        # Military restricted zones
        self.add_military_zone(50, 15, 5)
        
        # Shallow water areas
        self.add_shallow_water_zone(35, 70, 10)
        self.add_shallow_water_zone(80, 25, 7)
        
        # Apply costs
        self.apply_safety_costs()
    
    def get_danger_map(self) -> np.ndarray:
        """Get 2D array of danger levels for visualization."""
        danger_map = np.zeros((self.grid.width, self.grid.height))
        
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell = self.grid.get_cell(x, y)
                if cell:
                    danger_map[x, y] = self.get_total_risk(cell)
        
        return danger_map
