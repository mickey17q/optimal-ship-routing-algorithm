"""
Machine Learning-based Route Prediction and Learning.
Novel: Uses historical route data to predict optimal paths.
"""

import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict
import json

from grid import Cell, NavigationGrid


class RouteLearningSystem:
    """
    ML-based system that learns from historical routes.
    
    Novel Features:
    - Pattern recognition from past voyages
    - Adaptive cost learning
    - Route recommendation based on conditions
    - Performance prediction
    """
    
    def __init__(self, grid: NavigationGrid):
        self.grid = grid
        self.route_history: List[Dict] = []
        self.cell_usage_count = defaultdict(int)
        self.cell_avg_cost = defaultdict(float)
        self.successful_patterns: List[List[Tuple[int, int]]] = []
        
    def record_route(self, path: List[Cell], metrics: Dict):
        """Record a route for learning."""
        route_data = {
            'path': [(cell.x, cell.y) for cell in path],
            'distance': metrics.get('distance', 0),
            'fuel': metrics.get('fuel', 0),
            'time': metrics.get('time', 0),
            'success_score': self._calculate_success_score(metrics)
        }
        
        self.route_history.append(route_data)
        
        # Update cell statistics
        for cell in path:
            key = (cell.x, cell.y)
            self.cell_usage_count[key] += 1
            
            # Update average cost (simple moving average)
            current_avg = self.cell_avg_cost[key]
            n = self.cell_usage_count[key]
            new_cost = cell.total_cost
            self.cell_avg_cost[key] = (current_avg * (n - 1) + new_cost) / n
        
        # Store successful patterns
        if route_data['success_score'] > 0.7:
            self.successful_patterns.append(route_data['path'])
    
    def _calculate_success_score(self, metrics: Dict) -> float:
        """Calculate how successful a route was (0-1)."""
        # Normalize metrics (lower is better)
        distance_score = max(0, 1 - metrics.get('distance', 1000) / 2000)
        fuel_score = max(0, 1 - metrics.get('fuel', 100) / 200)
        time_score = max(0, 1 - metrics.get('time', 50) / 100)
        
        return (distance_score + fuel_score + time_score) / 3
    
    def get_learned_cost(self, cell: Cell) -> float:
        """Get learned cost for a cell based on history."""
        key = (cell.x, cell.y)
        
        if key in self.cell_avg_cost:
            # Blend learned cost with actual cost
            learned = self.cell_avg_cost[key]
            actual = cell.total_cost
            usage = self.cell_usage_count[key]
            
            # More usage = more weight to learned cost
            weight = min(usage / 10.0, 0.8)
            return learned * weight + actual * (1 - weight)
        
        return cell.total_cost
    
    def predict_route_performance(self, path: List[Cell]) -> Dict[str, float]:
        """Predict how well a route will perform based on learning."""
        if not self.route_history:
            return {'confidence': 0.0, 'predicted_score': 0.5}
        
        # Calculate similarity to successful patterns
        path_coords = [(cell.x, cell.y) for cell in path]
        max_similarity = 0.0
        
        for pattern in self.successful_patterns:
            similarity = self._calculate_pattern_similarity(path_coords, pattern)
            max_similarity = max(max_similarity, similarity)
        
        # Predict performance based on cell history
        total_learned_cost = sum(self.get_learned_cost(cell) for cell in path)
        avg_learned_cost = total_learned_cost / len(path) if path else 1.0
        
        # Normalize to 0-1 score
        predicted_score = max(0, min(1, 1 - (avg_learned_cost - 1.0) / 5.0))
        
        return {
            'confidence': min(len(self.route_history) / 50.0, 1.0),
            'predicted_score': predicted_score,
            'pattern_similarity': max_similarity,
            'recommendation': 'good' if predicted_score > 0.7 else 'moderate' if predicted_score > 0.4 else 'poor'
        }
    
    def _calculate_pattern_similarity(self, path1: List[Tuple[int, int]], 
                                     path2: List[Tuple[int, int]]) -> float:
        """Calculate similarity between two paths (0-1)."""
        if not path1 or not path2:
            return 0.0
        
        # Use Jaccard similarity on cell sets
        set1 = set(path1)
        set2 = set(path2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_recommendations(self, start: Cell, goal: Cell) -> List[str]:
        """Get route recommendations based on learning."""
        recommendations = []
        
        if len(self.route_history) < 5:
            recommendations.append("Limited historical data. Building route database...")
            return recommendations
        
        # Find similar historical routes
        similar_routes = []
        for route in self.route_history:
            if len(route['path']) > 0:
                route_start = route['path'][0]
                route_end = route['path'][-1]
                
                # Check if similar start/end
                start_dist = abs(route_start[0] - start.x) + abs(route_start[1] - start.y)
                end_dist = abs(route_end[0] - goal.x) + abs(route_end[1] - goal.y)
                
                if start_dist < 10 and end_dist < 10:
                    similar_routes.append(route)
        
        if similar_routes:
            # Get best performing similar route
            best_route = max(similar_routes, key=lambda r: r['success_score'])
            recommendations.append(
                f"Found {len(similar_routes)} similar historical routes"
            )
            recommendations.append(
                f"Best similar route: {best_route['distance']:.0f}km, "
                f"{best_route['fuel']:.1f}t fuel"
            )
        
        # Identify frequently used cells (popular routes)
        popular_cells = sorted(
            self.cell_usage_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        if popular_cells:
            recommendations.append(
                f"Most used waypoint: ({popular_cells[0][0][0]}, {popular_cells[0][0][1]}) "
                f"- used {popular_cells[0][1]} times"
            )
        
        return recommendations
    
    def export_learning_data(self, filename: str = 'route_learning.json'):
        """Export learned data for persistence."""
        data = {
            'route_history': self.route_history,
            'cell_usage': {f"{k[0]},{k[1]}": v for k, v in self.cell_usage_count.items()},
            'cell_costs': {f"{k[0]},{k[1]}": v for k, v in self.cell_avg_cost.items()},
            'successful_patterns': self.successful_patterns
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_learning_data(self, filename: str = 'route_learning.json'):
        """Import previously learned data."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.route_history = data.get('route_history', [])
            
            # Convert string keys back to tuples
            self.cell_usage_count = defaultdict(int, {
                tuple(map(int, k.split(','))): v 
                for k, v in data.get('cell_usage', {}).items()
            })
            
            self.cell_avg_cost = defaultdict(float, {
                tuple(map(int, k.split(','))): v 
                for k, v in data.get('cell_costs', {}).items()
            })
            
            self.successful_patterns = data.get('successful_patterns', [])
            
            return True
        except FileNotFoundError:
            return False
