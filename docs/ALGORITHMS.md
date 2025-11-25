# Ship Routing Algorithms - Theoretical Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Problem Statement](#problem-statement)
3. [Algorithm Descriptions](#algorithm-descriptions)
4. [Complexity Analysis](#complexity-analysis)
5. [Performance Comparison](#performance-comparison)
6. [Use Cases](#use-cases)

## Introduction

Ship routing is a critical optimization problem in maritime logistics. The goal is to find the optimal path between two points while considering multiple factors such as distance, fuel consumption, weather conditions, and safety.

This document provides theoretical background and implementation details for four pathfinding algorithms used in maritime navigation.

## Problem Statement

### Formal Definition

Given:
- A navigation grid **G** of size **W × H**
- Start position **S** = (x₁, y₁)
- Goal position **G** = (x₂, y₂)
- Set of obstacles **O** (land masses, restricted zones)
- Weather conditions **W(x, y)** for each cell
- Ship characteristics (speed, fuel consumption rate)

Find:
- Path **P** = [S, p₁, p₂, ..., pₙ, G] that minimizes a cost function

Cost functions vary by algorithm:
- **Distance**: Minimize total path length
- **Time**: Minimize travel time
- **Fuel**: Minimize fuel consumption
- **Safety**: Avoid hazardous conditions

### Constraints

1. Path must avoid land cells: ∀p ∈ P, p ∉ O
2. Path must be continuous (connected cells)
3. Movement allowed in 8 directions (including diagonals)

## Algorithm Descriptions

### 1. Dijkstra's Algorithm

**Type**: Uninformed search, guaranteed optimal

**Description**: Dijkstra's algorithm explores all possible paths systematically, always expanding the node with the lowest cost so far. It guarantees finding the shortest path but explores many unnecessary nodes.

**Pseudocode**:
```
function Dijkstra(start, goal):
    cost[start] = 0
    priority_queue.push((0, start))
    
    while priority_queue not empty:
        current_cost, current = priority_queue.pop()
        
        if current == goal:
            return reconstruct_path()
        
        for neighbor in get_neighbors(current):
            new_cost = cost[current] + movement_cost(current, neighbor)
            
            if new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                priority_queue.push((new_cost, neighbor))
                came_from[neighbor] = current
    
    return no_path_found
```

**Advantages**:
- Guarantees optimal solution
- Simple to implement
- Works with any non-negative edge weights

**Disadvantages**:
- Explores many unnecessary nodes
- Slower than informed search algorithms
- No domain knowledge utilization

### 2. A\* Algorithm

**Type**: Informed search, guaranteed optimal with admissible heuristic

**Description**: A\* improves upon Dijkstra by using a heuristic function to guide the search toward the goal. It combines the actual cost from start (g-score) with an estimated cost to goal (h-score).

**Cost Function**: f(n) = g(n) + h(n)
- g(n): Actual cost from start to node n
- h(n): Estimated cost from node n to goal (heuristic)

**Heuristic**: Euclidean distance
```
h(n) = √[(n.x - goal.x)² + (n.y - goal.y)²] × cell_size
```

**Pseudocode**:
```
function AStar(start, goal):
    g_score[start] = 0
    f_score[start] = heuristic(start, goal)
    priority_queue.push((f_score[start], start))
    
    while priority_queue not empty:
        current = priority_queue.pop()
        
        if current == goal:
            return reconstruct_path()
        
        for neighbor in get_neighbors(current):
            tentative_g = g_score[current] + movement_cost(current, neighbor)
            
            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                priority_queue.push((f_score[neighbor], neighbor))
                came_from[neighbor] = current
    
    return no_path_found
```

**Advantages**:
- Much faster than Dijkstra
- Still guarantees optimal path
- Efficient exploration

**Disadvantages**:
- Requires good heuristic function
- More complex than Dijkstra

### 3. Weather-Aware A\*

**Type**: Domain-specific informed search

**Description**: Extends A\* to incorporate real-time weather conditions. The movement cost is adjusted based on wind, waves, and currents affecting the ship.

**Enhanced Cost Function**:
```
movement_cost(from, to) = distance × weather_multiplier(to, heading)

weather_multiplier = wave_cost × wind_cost × current_cost

where:
- wave_cost = 1 + (wave_height / 10)
- wind_cost = 1 - (cos(wind_angle) × wind_speed / 100)
- current_cost = 1 - (cos(current_angle) × current_speed / 50)
```

**Weather Factors**:

1. **Wave Height**: Rough seas slow down ships
   - Higher waves → higher fuel consumption
   - Affects ship stability

2. **Wind Direction**: 
   - Headwind (opposite to heading) → increases cost
   - Tailwind (same as heading) → decreases cost
   - Crosswind → moderate impact

3. **Ocean Currents**:
   - Favorable currents → reduced fuel consumption
   - Opposing currents → increased fuel consumption

**Advantages**:
- Realistic maritime routing
- Avoids dangerous weather
- Reduces fuel consumption
- Improves safety

**Disadvantages**:
- Requires weather data
- More computation per node
- May not find absolute shortest path

### 4. Fuel-Optimized Routing

**Type**: Multi-objective optimization

**Description**: Specifically optimizes for minimum fuel consumption rather than shortest distance. Uses fuel consumption as the primary cost metric.

**Fuel Consumption Model**:
```
fuel(segment) = distance_nm × base_consumption × weather_cost

where:
- distance_nm = distance in nautical miles
- base_consumption = 0.15 tons/nm (typical cargo ship)
- weather_cost = combined weather multiplier
```

**Optimization Strategy**:
- Prioritize routes with favorable currents
- Avoid high wave areas
- Accept longer distances if fuel savings justify it
- Balance between distance and weather conditions

**Advantages**:
- Minimizes operational costs
- Reduces emissions
- Environmentally friendly
- Considers real-world economics

**Disadvantages**:
- May result in longer routes
- Requires accurate fuel consumption model
- Weather dependency

## Complexity Analysis

### Time Complexity

| Algorithm | Best Case | Average Case | Worst Case |
|-----------|-----------|--------------|------------|
| Dijkstra | O(E log V) | O(E log V) | O(E log V) |
| A* | O(b^d) | O(b^d) | O(E log V) |
| Weather-Aware | O(b^d) | O(b^d) | O(E log V) |
| Fuel-Optimized | O(b^d) | O(b^d) | O(E log V) |

Where:
- V = number of vertices (grid cells)
- E = number of edges (connections)
- b = branching factor (8 for 8-directional movement)
- d = depth of solution

### Space Complexity

All algorithms: **O(V)** for storing:
- Priority queue
- Cost arrays
- Came-from mapping
- Visited set

### Practical Performance (100×100 grid)

| Algorithm | Nodes Explored | Time (ms) | Memory (MB) |
|-----------|----------------|-----------|-------------|
| Dijkstra | ~5000 | 50-100 | ~2 |
| A* | ~2000 | 20-40 | ~1.5 |
| Weather-Aware | ~2500 | 25-45 | ~1.8 |
| Fuel-Optimized | ~2800 | 30-50 | ~2 |

## Performance Comparison

### Optimality

- **Dijkstra**: Always optimal (shortest distance)
- **A\***: Optimal with admissible heuristic
- **Weather-Aware**: Near-optimal (trades distance for safety/fuel)
- **Fuel-Optimized**: Optimal for fuel consumption (not distance)

### Speed

Ranking (fastest to slowest):
1. A* (best heuristic guidance)
2. Weather-Aware (slightly more computation)
3. Fuel-Optimized (complex cost function)
4. Dijkstra (no heuristic)

### Fuel Efficiency

Ranking (most efficient to least):
1. Fuel-Optimized (designed for this)
2. Weather-Aware (considers conditions)
3. A* (distance-focused)
4. Dijkstra (distance-focused)

## Use Cases

### When to Use Each Algorithm

**Dijkstra**:
- Baseline comparison
- When absolute shortest path is required
- Simple scenarios without weather data
- Educational purposes

**A\***:
- Fast pathfinding needed
- Shortest distance priority
- Calm weather conditions
- Time-critical routing

**Weather-Aware**:
- Storm avoidance
- Safety-critical routes
- Moderate fuel optimization
- Real-world maritime navigation

**Fuel-Optimized**:
- Long-distance voyages
- Cost minimization priority
- Environmental considerations
- Fuel price sensitivity

### Real-World Applications

1. **Commercial Shipping**: Fuel-optimized for cost reduction
2. **Emergency Response**: A\* for fastest arrival
3. **Cruise Ships**: Weather-aware for passenger comfort
4. **Naval Operations**: Weather-aware for safety
5. **Research Vessels**: Fuel-optimized for extended missions

## Conclusion

Each algorithm has its strengths and optimal use cases. The choice depends on priorities:
- **Speed**: A*
- **Fuel**: Fuel-Optimized
- **Safety**: Weather-Aware
- **Simplicity**: Dijkstra

Modern ship routing systems often use hybrid approaches, combining multiple algorithms based on voyage phase, weather conditions, and operational requirements.
