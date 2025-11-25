"""
Advanced Genetic Algorithm for multi-objective ship routing optimization.
This is a novel approach combining evolutionary computation with maritime routing.
"""

import numpy as np
from typing import List, Tuple, Dict
import random
from dataclasses import dataclass

from grid import NavigationGrid, Cell
from weather import WeatherSystem


@dataclass
class Route:
    """Represents a route chromosome in genetic algorithm."""
    waypoints: List[Cell]
    fitness: float = 0.0
    distance: float = 0.0
    fuel: float = 0.0
    safety: float = 0.0
    time: float = 0.0


class GeneticRouteOptimizer:
    """
    Genetic Algorithm for multi-objective route optimization.
    
    Novel Features:
    - Multi-objective fitness (distance, fuel, safety, time)
    - Adaptive mutation rates
    - Elitism with diversity preservation
    - Constraint handling for obstacles
    """
    
    def __init__(self, grid: NavigationGrid, weather: WeatherSystem,
                 population_size: int = 100, generations: int = 50):
        self.grid = grid
        self.weather = weather
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        
    def optimize(self, start: Cell, goal: Cell, 
                 weights: Dict[str, float] = None) -> Route:
        """
        Run genetic algorithm to find optimal route.
        
        Args:
            start: Starting cell
            goal: Goal cell
            weights: Objective weights {'distance': 0.3, 'fuel': 0.4, 'safety': 0.2, 'time': 0.1}
        """
        if weights is None:
            weights = {'distance': 0.25, 'fuel': 0.35, 'safety': 0.25, 'time': 0.15}
        
        # Initialize population
        population = self._initialize_population(start, goal)
        
        best_route = None
        best_fitness = float('-inf')
        
        for generation in range(self.generations):
            # Evaluate fitness
            for route in population:
                route.fitness = self._calculate_fitness(route, weights)
                
                if route.fitness > best_fitness:
                    best_fitness = route.fitness
                    best_route = route
            
            # Selection
            parents = self._tournament_selection(population)
            
            # Crossover
            offspring = self._crossover(parents)
            
            # Mutation (adaptive)
            self.mutation_rate = 0.1 * (1 - generation / self.generations) + 0.01
            offspring = self._mutate(offspring, start, goal)
            
            # Elitism: Keep best 10%
            population.sort(key=lambda r: r.fitness, reverse=True)
            elite_size = int(0.1 * self.population_size)
            population = population[:elite_size] + offspring[:self.population_size - elite_size]
        
        return best_route
    
    def _initialize_population(self, start: Cell, goal: Cell) -> List[Route]:
        """Create initial population with diverse routes."""
        population = []
        
        for _ in range(self.population_size):
            # Generate random waypoints between start and goal
            num_waypoints = random.randint(5, 15)
            waypoints = [start]
            
            current = start
            for i in range(num_waypoints):
                # Move towards goal with randomness
                progress = (i + 1) / (num_waypoints + 1)
                target_x = int(start.x + (goal.x - start.x) * progress)
                target_y = int(start.y + (goal.y - start.y) * progress)
                
                # Add randomness
                target_x += random.randint(-5, 5)
                target_y += random.randint(-5, 5)
                
                # Ensure valid cell
                target_x = max(0, min(self.grid.width - 1, target_x))
                target_y = max(0, min(self.grid.height - 1, target_y))
                
                cell = self.grid.get_cell(target_x, target_y)
                if cell and not cell.is_land:
                    waypoints.append(cell)
            
            waypoints.append(goal)
            
            route = Route(waypoints=waypoints)
            self._evaluate_route(route)
            population.append(route)
        
        return population
    
    def _evaluate_route(self, route: Route):
        """Calculate route metrics."""
        if len(route.waypoints) < 2:
            route.distance = float('inf')
            route.fuel = float('inf')
            route.safety = 0.0
            route.time = float('inf')
            return
        
        distance = 0.0
        fuel = 0.0
        safety = 1.0
        
        for i in range(len(route.waypoints) - 1):
            current = route.waypoints[i]
            next_cell = route.waypoints[i + 1]
            
            # Distance
            segment_dist = self.grid.get_distance(current, next_cell)
            distance += segment_dist
            
            # Fuel (with weather)
            if self.weather:
                dx = next_cell.x - current.x
                dy = next_cell.y - current.y
                heading = np.arctan2(dy, dx)
                weather_cost = self.weather.calculate_weather_cost(next_cell, heading)
                fuel += self.weather.get_fuel_consumption(segment_dist, weather_cost, 20.0)
                
                # Safety (inverse of weather severity)
                safety *= (1.0 / weather_cost)
            else:
                fuel += segment_dist * 0.15 / 1.852
        
        route.distance = distance
        route.fuel = fuel
        route.safety = safety / len(route.waypoints)
        route.time = (distance / 1.852) / 20.0  # hours
    
    def _calculate_fitness(self, route: Route, weights: Dict[str, float]) -> float:
        """Multi-objective fitness function."""
        # Normalize objectives (lower is better, so invert)
        max_distance = 2000.0  # km
        max_fuel = 200.0  # tons
        max_time = 100.0  # hours
        
        distance_score = 1.0 - min(route.distance / max_distance, 1.0)
        fuel_score = 1.0 - min(route.fuel / max_fuel, 1.0)
        safety_score = route.safety
        time_score = 1.0 - min(route.time / max_time, 1.0)
        
        # Weighted sum
        fitness = (weights['distance'] * distance_score +
                  weights['fuel'] * fuel_score +
                  weights['safety'] * safety_score +
                  weights['time'] * time_score)
        
        # Penalty for invalid routes
        if any(wp.is_land for wp in route.waypoints):
            fitness *= 0.1
        
        return fitness
    
    def _tournament_selection(self, population: List[Route], 
                             tournament_size: int = 5) -> List[Route]:
        """Select parents using tournament selection."""
        parents = []
        
        for _ in range(self.population_size):
            tournament = random.sample(population, tournament_size)
            winner = max(tournament, key=lambda r: r.fitness)
            parents.append(winner)
        
        return parents
    
    def _crossover(self, parents: List[Route]) -> List[Route]:
        """Order crossover for route chromosomes."""
        offspring = []
        
        for i in range(0, len(parents) - 1, 2):
            if random.random() < self.crossover_rate:
                parent1 = parents[i]
                parent2 = parents[i + 1]
                
                # Single-point crossover
                min_len = min(len(parent1.waypoints), len(parent2.waypoints))
                if min_len > 2:
                    point = random.randint(1, min_len - 1)
                    
                    child1_waypoints = parent1.waypoints[:point] + parent2.waypoints[point:]
                    child2_waypoints = parent2.waypoints[:point] + parent1.waypoints[point:]
                    
                    child1 = Route(waypoints=child1_waypoints)
                    child2 = Route(waypoints=child2_waypoints)
                    
                    self._evaluate_route(child1)
                    self._evaluate_route(child2)
                    
                    offspring.extend([child1, child2])
                else:
                    offspring.extend([parent1, parent2])
            else:
                offspring.extend([parents[i], parents[i + 1]])
        
        return offspring
    
    def _mutate(self, offspring: List[Route], start: Cell, goal: Cell) -> List[Route]:
        """Mutate routes by modifying waypoints."""
        for route in offspring:
            if random.random() < self.mutation_rate:
                if len(route.waypoints) > 2:
                    # Choose mutation type
                    mutation_type = random.choice(['modify', 'add', 'remove'])
                    
                    if mutation_type == 'modify':
                        # Modify a random waypoint
                        idx = random.randint(1, len(route.waypoints) - 2)
                        current = route.waypoints[idx]
                        
                        new_x = current.x + random.randint(-3, 3)
                        new_y = current.y + random.randint(-3, 3)
                        new_x = max(0, min(self.grid.width - 1, new_x))
                        new_y = max(0, min(self.grid.height - 1, new_y))
                        
                        new_cell = self.grid.get_cell(new_x, new_y)
                        if new_cell and not new_cell.is_land:
                            route.waypoints[idx] = new_cell
                    
                    elif mutation_type == 'add' and len(route.waypoints) < 20:
                        # Add a waypoint
                        idx = random.randint(1, len(route.waypoints) - 1)
                        prev = route.waypoints[idx - 1]
                        next_wp = route.waypoints[idx]
                        
                        mid_x = (prev.x + next_wp.x) // 2 + random.randint(-2, 2)
                        mid_y = (prev.y + next_wp.y) // 2 + random.randint(-2, 2)
                        mid_x = max(0, min(self.grid.width - 1, mid_x))
                        mid_y = max(0, min(self.grid.height - 1, mid_y))
                        
                        mid_cell = self.grid.get_cell(mid_x, mid_y)
                        if mid_cell and not mid_cell.is_land:
                            route.waypoints.insert(idx, mid_cell)
                    
                    elif mutation_type == 'remove' and len(route.waypoints) > 3:
                        # Remove a waypoint
                        idx = random.randint(1, len(route.waypoints) - 2)
                        route.waypoints.pop(idx)
                    
                    self._evaluate_route(route)
        
        return offspring
