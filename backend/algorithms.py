"""
Ship routing pathfinding algorithms.
Implements Dijkstra, A*, Weather-Aware, and Fuel-Optimized routing.
"""

import heapq
import time
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
import numpy as np

from grid import NavigationGrid, Cell
from weather import WeatherSystem


@dataclass
class RouteResult:
    """Result of a routing algorithm."""
    path: List[Cell]
    distance_km: float
    cost: float
    fuel_tons: float
    time_hours: float
    nodes_explored: int
    computation_time_ms: float
    algorithm: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'path': [(cell.x, cell.y) for cell in self.path],
            'distance_km': float(self.distance_km),
            'cost': float(self.cost),
            'fuel_tons': float(self.fuel_tons),
            'time_hours': float(self.time_hours),
            'nodes_explored': self.nodes_explored,
            'computation_time_ms': float(self.computation_time_ms),
            'algorithm': self.algorithm
        }


class ShipRouter:
    """Ship routing algorithms implementation."""
    
    def __init__(self, grid: NavigationGrid, weather: Optional[WeatherSystem] = None):
        """
        Initialize router.
        
        Args:
            grid: Navigation grid
            weather: Weather system (optional)
        """
        self.grid = grid
        self.weather = weather
        self.ship_speed_knots = 20.0  # Average cargo ship speed
    
    def dijkstra(self, start: Cell, goal: Cell) -> RouteResult:
        """
        Dijkstra's shortest path algorithm.
        
        Args:
            start: Starting cell
            goal: Goal cell
            
        Returns:
            RouteResult with optimal path
        """
        start_time = time.time()
        
        # Priority queue: (cost, counter, cell) to avoid comparison issues
        pq = [(0, 0, start)]
        came_from: Dict[Cell, Optional[Cell]] = {start: None}
        cost_so_far: Dict[Cell, float] = {start: 0}
        nodes_explored = 0
        counter = 0
        
        while pq:
            current_cost, _, current = heapq.heappop(pq)
            nodes_explored += 1
            
            if current == goal:
                break
            
            for neighbor in self.grid.get_neighbors(current):
                new_cost = cost_so_far[current] + self.grid.get_movement_cost(current, neighbor)
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    counter += 1
                    heapq.heappush(pq, (new_cost, counter, neighbor))
                    came_from[neighbor] = current
        
        # Reconstruct path
        path = self._reconstruct_path(came_from, start, goal)
        computation_time = (time.time() - start_time) * 1000
        
        return self._create_result(path, nodes_explored, computation_time, 'Dijkstra')
    
    def a_star(self, start: Cell, goal: Cell) -> RouteResult:
        """
        A* algorithm with Euclidean heuristic.
        
        Args:
            start: Starting cell
            goal: Goal cell
            
        Returns:
            RouteResult with optimal path
        """
        start_time = time.time()
        
        def heuristic(cell: Cell) -> float:
            """Euclidean distance heuristic."""
            return self.grid.get_distance(cell, goal)
        
        # Priority queue: (f_score, counter, cell)
        pq = [(0, 0, start)]
        came_from: Dict[Cell, Optional[Cell]] = {start: None}
        g_score: Dict[Cell, float] = {start: 0}
        nodes_explored = 0
        counter = 0
        
        while pq:
            _, _, current = heapq.heappop(pq)
            nodes_explored += 1
            
            if current == goal:
                break
            
            for neighbor in self.grid.get_neighbors(current):
                tentative_g = g_score[current] + self.grid.get_movement_cost(current, neighbor)
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor)
                    counter += 1
                    heapq.heappush(pq, (f_score, counter, neighbor))
                    came_from[neighbor] = current
        
        path = self._reconstruct_path(came_from, start, goal)
        computation_time = (time.time() - start_time) * 1000
        
        return self._create_result(path, nodes_explored, computation_time, 'A*')
    
    def weather_aware_astar(self, start: Cell, goal: Cell) -> RouteResult:
        """
        Weather-aware A* algorithm.
        Considers weather conditions in pathfinding.
        
        Args:
            start: Starting cell
            goal: Goal cell
            
        Returns:
            RouteResult with weather-optimized path
        """
        if not self.weather:
            # Fallback to regular A* if no weather data
            return self.a_star(start, goal)
        
        start_time = time.time()
        
        def heuristic(cell: Cell) -> float:
            """Euclidean distance heuristic."""
            return self.grid.get_distance(cell, goal)
        
        pq = [(0, 0, start)]
        came_from: Dict[Cell, Optional[Cell]] = {start: None}
        g_score: Dict[Cell, float] = {start: 0}
        nodes_explored = 0
        counter = 0
        
        while pq:
            _, _, current = heapq.heappop(pq)
            nodes_explored += 1
            
            if current == goal:
                break
            
            for neighbor in self.grid.get_neighbors(current):
                # Calculate heading for weather cost
                dx = neighbor.x - current.x
                dy = neighbor.y - current.y
                heading = np.arctan2(dy, dx)
                
                # Get weather-adjusted cost
                weather_cost = self.weather.calculate_weather_cost(neighbor, heading)
                movement_cost = self.grid.get_distance(current, neighbor) * weather_cost
                
                tentative_g = g_score[current] + movement_cost
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor)
                    counter += 1
                    heapq.heappush(pq, (f_score, counter, neighbor))
                    came_from[neighbor] = current
        
        path = self._reconstruct_path(came_from, start, goal)
        computation_time = (time.time() - start_time) * 1000
        
        return self._create_result(path, nodes_explored, computation_time, 'Weather-Aware A*')
    
    def fuel_optimized(self, start: Cell, goal: Cell) -> RouteResult:
        """
        Fuel-optimized routing algorithm.
        Minimizes fuel consumption considering distance, weather, and currents.
        
        Args:
            start: Starting cell
            goal: Goal cell
            
        Returns:
            RouteResult with fuel-optimized path
        """
        if not self.weather:
            return self.a_star(start, goal)
        
        start_time = time.time()
        
        def heuristic(cell: Cell) -> float:
            """Fuel-based heuristic."""
            distance = self.grid.get_distance(cell, goal)
            # Estimate minimum fuel needed
            return self.weather.get_fuel_consumption(distance, 1.0, self.ship_speed_knots)
        
        pq = [(0, 0, start)]
        came_from: Dict[Cell, Optional[Cell]] = {start: None}
        fuel_score: Dict[Cell, float] = {start: 0}
        nodes_explored = 0
        counter = 0
        
        while pq:
            _, _, current = heapq.heappop(pq)
            nodes_explored += 1
            
            if current == goal:
                break
            
            for neighbor in self.grid.get_neighbors(current):
                # Calculate heading
                dx = neighbor.x - current.x
                dy = neighbor.y - current.y
                heading = np.arctan2(dy, dx)
                
                # Calculate fuel consumption for this segment
                distance = self.grid.get_distance(current, neighbor)
                weather_cost = self.weather.calculate_weather_cost(neighbor, heading)
                fuel_cost = self.weather.get_fuel_consumption(distance, weather_cost, self.ship_speed_knots)
                
                tentative_fuel = fuel_score[current] + fuel_cost
                
                if neighbor not in fuel_score or tentative_fuel < fuel_score[neighbor]:
                    fuel_score[neighbor] = tentative_fuel
                    f_score = tentative_fuel + heuristic(neighbor)
                    counter += 1
                    heapq.heappush(pq, (f_score, counter, neighbor))
                    came_from[neighbor] = current
        
        path = self._reconstruct_path(came_from, start, goal)
        computation_time = (time.time() - start_time) * 1000
        
        return self._create_result(path, nodes_explored, computation_time, 'Fuel-Optimized')
    
    def _reconstruct_path(self, came_from: Dict[Cell, Optional[Cell]], 
                         start: Cell, goal: Cell) -> List[Cell]:
        """Reconstruct path from came_from dictionary."""
        if goal not in came_from:
            return []
        
        path = []
        current = goal
        
        while current is not None:
            path.append(current)
            current = came_from[current]
        
        path.reverse()
        return path
    
    def _create_result(self, path: List[Cell], nodes_explored: int, 
                      computation_time: float, algorithm: str) -> RouteResult:
        """Create RouteResult from path."""
        if not path:
            return RouteResult(
                path=[], distance_km=0, cost=0, fuel_tons=0,
                time_hours=0, nodes_explored=nodes_explored,
                computation_time_ms=computation_time, algorithm=algorithm
            )
        
        # Calculate metrics
        distance = self.grid.get_path_length(path)
        cost = self.grid.get_path_cost(path)
        
        # Calculate fuel consumption
        fuel = 0.0
        if self.weather:
            for i in range(len(path) - 1):
                segment_dist = self.grid.get_distance(path[i], path[i + 1])
                dx = path[i + 1].x - path[i].x
                dy = path[i + 1].y - path[i].y
                heading = np.arctan2(dy, dx)
                weather_cost = self.weather.calculate_weather_cost(path[i + 1], heading)
                fuel += self.weather.get_fuel_consumption(segment_dist, weather_cost, self.ship_speed_knots)
        else:
            # Estimate without weather
            fuel = distance * 0.15 / 1.852  # Basic estimation
        
        # Calculate time (distance / speed)
        time_hours = (distance / 1.852) / self.ship_speed_knots
        
        return RouteResult(
            path=path,
            distance_km=distance,
            cost=cost,
            fuel_tons=fuel,
            time_hours=time_hours,
            nodes_explored=nodes_explored,
            computation_time_ms=computation_time,
            algorithm=algorithm
        )
    
    def compare_algorithms(self, start: Cell, goal: Cell) -> Dict[str, RouteResult]:
        """
        Compare all algorithms on the same route.
        
        Args:
            start: Starting cell
            goal: Goal cell
            
        Returns:
            Dictionary of algorithm name to RouteResult
        """
        results = {
            'dijkstra': self.dijkstra(start, goal),
            'a_star': self.a_star(start, goal),
        }
        
        if self.weather:
            results['weather_aware'] = self.weather_aware_astar(start, goal)
            results['fuel_optimized'] = self.fuel_optimized(start, goal)
        
        return results
