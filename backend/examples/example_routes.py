"""
Example routing scenarios for testing and demonstration.
"""

from grid import NavigationGrid, Cell
from weather import WeatherSystem
from algorithms import ShipRouter


def scenario_coastal_route():
    """Short coastal route scenario."""
    print("\n" + "="*60)
    print("SCENARIO 1: Coastal Route")
    print("="*60)
    
    grid = NavigationGrid(50, 50, cell_size_km=5.0)
    grid.create_sample_ocean()
    
    weather = WeatherSystem(grid)
    weather.generate_weather_pattern('calm')
    weather.apply_weather_to_grid()
    
    router = ShipRouter(grid, weather)
    
    start = grid.get_cell(10, 10)
    goal = grid.get_cell(40, 40)
    
    print(f"\nRoute: ({start.x}, {start.y}) -> ({goal.x}, {goal.y})")
    print(f"Grid: {grid}")
    print(f"Weather: {weather}")
    
    results = router.compare_algorithms(start, goal)
    
    print("\n" + "-"*60)
    print("ALGORITHM COMPARISON")
    print("-"*60)
    
    for name, result in results.items():
        print(f"\n{result.algorithm}:")
        print(f"  Distance: {result.distance_km:.2f} km")
        print(f"  Fuel: {result.fuel_tons:.2f} tons")
        print(f"  Time: {result.time_hours:.2f} hours")
        print(f"  Nodes explored: {result.nodes_explored}")
        print(f"  Computation time: {result.computation_time_ms:.2f} ms")
    
    return results


def scenario_transoceanic():
    """Long transoceanic voyage scenario."""
    print("\n" + "="*60)
    print("SCENARIO 2: Transoceanic Voyage")
    print("="*60)
    
    grid = NavigationGrid(100, 100, cell_size_km=50.0)
    grid.create_sample_ocean()
    
    weather = WeatherSystem(grid)
    weather.generate_weather_pattern('moderate')
    weather.apply_weather_to_grid()
    
    router = ShipRouter(grid, weather)
    
    start = grid.get_cell(10, 50)
    goal = grid.get_cell(90, 50)
    
    print(f"\nRoute: ({start.x}, {start.y}) -> ({goal.x}, {goal.y})")
    print(f"Grid: {grid}")
    print(f"Weather: {weather}")
    
    results = router.compare_algorithms(start, goal)
    
    print("\n" + "-"*60)
    print("ALGORITHM COMPARISON")
    print("-"*60)
    
    for name, result in results.items():
        print(f"\n{result.algorithm}:")
        print(f"  Distance: {result.distance_km:.2f} km")
        print(f"  Fuel: {result.fuel_tons:.2f} tons")
        print(f"  Time: {result.time_hours:.2f} hours")
        print(f"  Nodes explored: {result.nodes_explored}")
        print(f"  Computation time: {result.computation_time_ms:.2f} ms")
    
    return results


def scenario_storm_avoidance():
    """Storm avoidance scenario."""
    print("\n" + "="*60)
    print("SCENARIO 3: Storm Avoidance")
    print("="*60)
    
    grid = NavigationGrid(80, 80, cell_size_km=10.0)
    grid.create_sample_ocean()
    
    weather = WeatherSystem(grid)
    weather.generate_weather_pattern('moderate')
    
    # Add a major storm in the middle
    weather.add_storm(40, 40, 20, intensity=2.5)
    weather.apply_weather_to_grid()
    
    router = ShipRouter(grid, weather)
    
    start = grid.get_cell(10, 40)
    goal = grid.get_cell(70, 40)
    
    print(f"\nRoute: ({start.x}, {start.y}) -> ({goal.x}, {goal.y})")
    print(f"Grid: {grid}")
    print(f"Weather: {weather}")
    print(f"Storm center: (40, 40) with radius 20 cells")
    
    results = router.compare_algorithms(start, goal)
    
    print("\n" + "-"*60)
    print("ALGORITHM COMPARISON")
    print("-"*60)
    
    for name, result in results.items():
        print(f"\n{result.algorithm}:")
        print(f"  Distance: {result.distance_km:.2f} km")
        print(f"  Fuel: {result.fuel_tons:.2f} tons")
        print(f"  Time: {result.time_hours:.2f} hours")
        print(f"  Nodes explored: {result.nodes_explored}")
        print(f"  Computation time: {result.computation_time_ms:.2f} ms")
    
    # Compare weather-aware vs basic A*
    if 'a_star' in results and 'weather_aware' in results:
        basic = results['a_star']
        weather_aware = results['weather_aware']
        
        fuel_savings = ((basic.fuel_tons - weather_aware.fuel_tons) / basic.fuel_tons) * 100
        
        print("\n" + "-"*60)
        print("WEATHER-AWARE BENEFITS")
        print("-"*60)
        print(f"Fuel savings: {fuel_savings:.1f}%")
        print(f"Distance difference: {weather_aware.distance_km - basic.distance_km:.2f} km")
    
    return results


def scenario_fuel_comparison():
    """Fuel optimization comparison."""
    print("\n" + "="*60)
    print("SCENARIO 4: Fuel Optimization Comparison")
    print("="*60)
    
    grid = NavigationGrid(100, 100, cell_size_km=20.0)
    grid.create_sample_ocean()
    
    weather = WeatherSystem(grid)
    weather.generate_weather_pattern('stormy')
    weather.add_storm(50, 30, 15, intensity=2.0)
    weather.add_storm(70, 70, 12, intensity=1.8)
    weather.apply_weather_to_grid()
    
    router = ShipRouter(grid, weather)
    
    start = grid.get_cell(10, 10)
    goal = grid.get_cell(90, 90)
    
    print(f"\nRoute: ({start.x}, {start.y}) -> ({goal.x}, {goal.y})")
    print(f"Grid: {grid}")
    print(f"Weather: {weather}")
    
    results = router.compare_algorithms(start, goal)
    
    print("\n" + "-"*60)
    print("ALGORITHM COMPARISON")
    print("-"*60)
    
    for name, result in results.items():
        print(f"\n{result.algorithm}:")
        print(f"  Distance: {result.distance_km:.2f} km")
        print(f"  Fuel: {result.fuel_tons:.2f} tons")
        print(f"  Time: {result.time_hours:.2f} hours")
        print(f"  Nodes explored: {result.nodes_explored}")
        print(f"  Computation time: {result.computation_time_ms:.2f} ms")
    
    # Compare all algorithms
    if len(results) >= 3:
        print("\n" + "-"*60)
        print("OPTIMIZATION SUMMARY")
        print("-"*60)
        
        dijkstra = results.get('dijkstra')
        fuel_opt = results.get('fuel_optimized')
        
        if dijkstra and fuel_opt:
            fuel_savings = ((dijkstra.fuel_tons - fuel_opt.fuel_tons) / dijkstra.fuel_tons) * 100
            print(f"Fuel-optimized vs Dijkstra:")
            print(f"  Fuel savings: {fuel_savings:.1f}%")
            print(f"  Distance difference: {fuel_opt.distance_km - dijkstra.distance_km:.2f} km")
            print(f"  Time difference: {fuel_opt.time_hours - dijkstra.time_hours:.2f} hours")
    
    return results


if __name__ == '__main__':
    print("\n" + "="*60)
    print("SHIP ROUTING ALGORITHM DEMONSTRATION")
    print("="*60)
    
    # Run all scenarios
    scenario_coastal_route()
    scenario_transoceanic()
    scenario_storm_avoidance()
    scenario_fuel_comparison()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
