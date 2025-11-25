"""
Grid-based navigation system for ship routing.
Handles ocean representation, obstacles, and cost calculations.
"""

import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class Cell:
    """Represents a single cell in the navigation grid."""
    x: int
    y: int
    is_land: bool = False
    base_cost: float = 1.0
    weather_cost: float = 0.0
    
    @property
    def total_cost(self) -> float:
        """Total cost to traverse this cell."""
        if self.is_land:
            return float('inf')
        return self.base_cost + self.weather_cost
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.x == other.x and self.y == other.y
        return False


class NavigationGrid:
    """Grid-based ocean navigation system."""
    
    def __init__(self, width: int, height: int, cell_size_km: float = 10.0):
        """
        Initialize navigation grid.
        
        Args:
            width: Grid width in cells
            height: Grid height in cells
            cell_size_km: Size of each cell in kilometers
        """
        self.width = width
        self.height = height
        self.cell_size_km = cell_size_km
        self.grid = [[Cell(x, y) for y in range(height)] for x in range(width)]
        
    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """Get cell at coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None
    
    def set_land(self, x: int, y: int, is_land: bool = True):
        """Mark a cell as land (obstacle)."""
        cell = self.get_cell(x, y)
        if cell:
            cell.is_land = is_land
    
    def set_land_region(self, x_start: int, y_start: int, x_end: int, y_end: int):
        """Mark a rectangular region as land."""
        for x in range(max(0, x_start), min(self.width, x_end + 1)):
            for y in range(max(0, y_start), min(self.height, y_end + 1)):
                self.set_land(x, y, True)
    
    def add_island(self, center_x: int, center_y: int, radius: int):
        """Add a circular island."""
        for x in range(max(0, center_x - radius), min(self.width, center_x + radius + 1)):
            for y in range(max(0, center_y - radius), min(self.height, center_y + radius + 1)):
                if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2:
                    self.set_land(x, y, True)
    
    def set_weather_cost(self, x: int, y: int, cost: float):
        """Set weather cost for a cell."""
        cell = self.get_cell(x, y)
        if cell:
            cell.weather_cost = cost
    
    def get_neighbors(self, cell: Cell, allow_diagonal: bool = True) -> List[Cell]:
        """
        Get navigable neighboring cells.
        
        Args:
            cell: Current cell
            allow_diagonal: Whether to allow diagonal movement
            
        Returns:
            List of neighboring cells
        """
        neighbors = []
        
        # 4-directional movement
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        # Add diagonal directions if allowed
        if allow_diagonal:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
        
        for dx, dy in directions:
            nx, ny = cell.x + dx, cell.y + dy
            neighbor = self.get_cell(nx, ny)
            
            if neighbor and not neighbor.is_land:
                neighbors.append(neighbor)
        
        return neighbors
    
    def get_distance(self, cell1: Cell, cell2: Cell) -> float:
        """
        Calculate Euclidean distance between two cells in kilometers.
        
        Args:
            cell1: First cell
            cell2: Second cell
            
        Returns:
            Distance in kilometers
        """
        dx = abs(cell1.x - cell2.x)
        dy = abs(cell1.y - cell2.y)
        return np.sqrt(dx**2 + dy**2) * self.cell_size_km
    
    def get_movement_cost(self, from_cell: Cell, to_cell: Cell) -> float:
        """
        Calculate cost of moving from one cell to another.
        
        Args:
            from_cell: Starting cell
            to_cell: Destination cell
            
        Returns:
            Movement cost
        """
        if to_cell.is_land:
            return float('inf')
        
        # Base distance cost
        distance = self.get_distance(from_cell, to_cell)
        
        # Apply cell's total cost multiplier
        return distance * to_cell.total_cost
    
    def is_valid_path(self, path: List[Cell]) -> bool:
        """Check if a path is valid (no land cells)."""
        return all(not cell.is_land for cell in path)
    
    def get_path_length(self, path: List[Cell]) -> float:
        """Calculate total path length in kilometers."""
        if len(path) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(path) - 1):
            total += self.get_distance(path[i], path[i + 1])
        
        return total
    
    def get_path_cost(self, path: List[Cell]) -> float:
        """Calculate total path cost including weather factors."""
        if len(path) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(path) - 1):
            total += self.get_movement_cost(path[i], path[i + 1])
        
        return total
    
    def create_sample_ocean(self):
        """Create a sample ocean with some islands for testing."""
        # Add some islands
        self.add_island(20, 20, 5)
        self.add_island(60, 40, 8)
        self.add_island(40, 70, 6)
        self.add_island(80, 80, 7)
        
        # Add a coastal region
        self.set_land_region(0, 0, 5, self.height - 1)
        self.set_land_region(self.width - 6, 0, self.width - 1, self.height - 1)
    
    def to_array(self) -> np.ndarray:
        """Convert grid to numpy array for visualization (1 = land, 0 = water)."""
        arr = np.zeros((self.width, self.height))
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y].is_land:
                    arr[x, y] = 1
        return arr
    
    def __repr__(self):
        return f"NavigationGrid({self.width}x{self.height}, cell_size={self.cell_size_km}km)"
