"""
Bidirectional A* - Advanced pathfinding algorithm.
Faster than traditional A* by searching from both start and goal simultaneously.
"""

import heapq
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass

from grid import NavigationGrid, Cell
from weather import WeatherSystem


@dataclass
class BiDirectionalResult:
    """Result from bidirectional A* search."""
    path: List[Cell]
    distance_km: float
    fuel_tons: float
    time_hours: float
    cost: float
    nodes_explored: int
    computation_time_ms: float
    algorithm: str = "Bidirectional A*"
    
    def to_dict(self):
        return {
            'algorithm': self.algorithm,
            'path': [(cell.x, cell.y) for cell in self.path],
            'distance_km': self.distance_km,
            'fuel_tons': self.fuel_tons,
            'time_hours': self.time_hours,
            'cost': self.cost,
            'nodes_explored': self.nodes_explored,
            'computation_time_ms': self.computation_time_ms
        }


class BidirectionalAStar:
    """
    Bidirectional A* algorithm - searches from both start and goal.
    
    Advantages:
    - 2-3x faster than regular A*
    - Explores fewer nodes
    - Better for long-distance routes
    """
    
    def __init__(self, grid: NavigationGrid, weather: WeatherSystem = None):
        self.grid = grid
        self.weather = weather
    
    def search(self, start: Cell, goal: Cell) -> Optional[BiDirectionalResult]:
        """
        Bidirectional A* search.
        Searches from both start and goal until they meet.
        """
        start_time = time.time()
        
        # Forward search (from start)
        forward_open = [(0, start)]
        forward_came_from = {start: None}
        forward_g_score = {start: 0}
        
        # Backward search (from goal)
        backward_open = [(0, goal)]
        backward_came_from = {goal: None}
        backward_g_score = {goal: 0}
        
        forward_closed = set()
        backward_closed = set()
        
        meeting_point = None
        best_path_cost = float('inf')
        
        nodes_explored = 0
        
        while forward_open and backward_open:
            # Expand forward search
            if forward_open:
                _, current_forward = heapq.heappop(forward_open)
                
                if current_forward in backward_closed:
                    # Paths met!
                    total_cost = forward_g_score[current_forward] + backward_g_score[current_forward]
                    if total_cost < best_path_cost:
                        best_path_cost = total_cost
                        meeting_point = current_forward
                    break
                
                if current_forward not in forward_closed:
                    forward_closed.add(current_forward)
                    nodes_explored += 1
                    
                    for neighbor in self.grid.get_neighbors(current_forward):
                        if neighbor.is_land or neighbor in forward_closed:
                            continue
                        
                        tentative_g = forward_g_score[current_forward] + self.grid.get_movement_cost(current_forward, neighbor)
                        
                        if neighbor not in forward_g_score or tentative_g < forward_g_score[neighbor]:
                            forward_g_score[neighbor] = tentative_g
                            forward_came_from[neighbor] = current_forward
                            f_score = tentative_g + self.grid.get_distance(neighbor, goal)
                            heapq.heappush(forward_open, (f_score, neighbor))
            
            # Expand backward search
            if backward_open:
                _, current_backward = heapq.heappop(backward_open)
                
                if current_backward in forward_closed:
                    # Paths met!
                    total_cost = forward_g_score[current_backward] + backward_g_score[current_backward]
                    if total_cost < best_path_cost:
                        best_path_cost = total_cost
                        meeting_point = current_backward
                    break
                
                if current_backward not in backward_closed:
                    backward_closed.add(current_backward)
                    nodes_explored += 1
                    
                    for neighbor in self.grid.get_neighbors(current_backward):
                        if neighbor.is_land or neighbor in backward_closed:
                            continue
                        
                        tentative_g = backward_g_score[current_backward] + self.grid.get_movement_cost(current_backward, neighbor)
                        
                        if neighbor not in backward_g_score or tentative_g < backward_g_score[neighbor]:
                            backward_g_score[neighbor] = tentative_g
                            backward_came_from[neighbor] = current_backward
                            f_score = tentative_g + self.grid.get_distance(neighbor, start)
                            heapq.heappush(backward_open, (f_score, neighbor))
        
        if meeting_point is None:
            return None
        
        # Reconstruct path
        path = []
        
        # Forward path (start to meeting point)
        current = meeting_point
        while current is not None:
            path.append(current)
            current = forward_came_from[current]
        path.reverse()
        
        # Backward path (meeting point to goal)
        current = backward_came_from[meeting_point]
        while current is not None:
            path.append(current)
            current = backward_came_from[current]
        
        # Calculate metrics
        distance = sum(self.grid.get_distance(path[i], path[i+1]) for i in range(len(path)-1))
        
        fuel = 0
        for i in range(len(path) - 1):
            segment_dist = self.grid.get_distance(path[i], path[i+1])
            if self.weather:
                import numpy as np
                dx = path[i+1].x - path[i].x
                dy = path[i+1].y - path[i].y
                heading = np.arctan2(dy, dx)
                weather_cost = self.weather.calculate_weather_cost(path[i+1], heading)
                fuel += self.weather.get_fuel_consumption(segment_dist, weather_cost, 20.0)
            else:
                fuel += segment_dist * 0.15 / 1.852
        
        time_hours = (distance / 1.852) / 20.0
        cost = best_path_cost
        
        computation_time = (time.time() - start_time) * 1000
        
        return BiDirectionalResult(
            path=path,
            distance_km=distance,
            fuel_tons=fuel,
            time_hours=time_hours,
            cost=cost,
            nodes_explored=nodes_explored,
            computation_time_ms=computation_time
        )
