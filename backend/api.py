## REMOVE DUPLICATE BLOCK ABOVE
"""
Enhanced Flask API with all advanced features.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

from grid import NavigationGrid, Cell
from weather import WeatherSystem
from algorithms import ShipRouter
from genetic_optimizer import GeneticRouteOptimizer
from safety_zones import SafetyManager
from carbon_tracker import CarbonTracker
from route_learning import RouteLearningSystem


app = Flask(__name__)
CORS(app)

def configure_bbox():
    """Set the grid's geographic bounding box from frontend."""
    data = request.json
    lat_min = data.get('lat_min')
    lat_max = data.get('lat_max')
    lon_min = data.get('lon_min')
    lon_max = data.get('lon_max')
    if None in (lat_min, lat_max, lon_min, lon_max):
        return jsonify({'error': 'Missing bbox values'}), 400
    map_bbox['lat_min'] = float(lat_min)
    map_bbox['lat_max'] = float(lat_max)
    map_bbox['lon_min'] = float(lon_min)
    map_bbox['lon_max'] = float(lon_max)
    return jsonify({'status': 'ok', 'bbox': map_bbox})

# Register configure_bbox route after app is created
app.add_url_rule('/api/configure_bbox', 'configure_bbox', configure_bbox, methods=['POST'])

# Global instances
grid = None
weather = None
router = None
genetic_optimizer = None
safety_manager = None
carbon_tracker = None
learning_system = None

# Geographic mapping settings: map geographic bbox to grid indices
map_bbox = {
    'lat_min': None,
    'lat_max': None,
    'lon_min': None,
    'lon_max': None,
}

import math


def initialize_system(grid_size=100, weather_pattern='moderate'):
    """Initialize the enhanced navigation system."""
    global grid, weather, router, genetic_optimizer, safety_manager, carbon_tracker, learning_system
    
    # Create grid
    grid = NavigationGrid(grid_size, grid_size, cell_size_km=10.0)
    grid.create_sample_ocean()
    
    # Create weather system
    weather = WeatherSystem(grid)
    weather.generate_weather_pattern(weather_pattern)
    weather.add_storm(50, 50, 15, intensity=1.5)
    weather.apply_weather_to_grid()
    
    # Create safety manager with realistic scenarios
    safety_manager = SafetyManager(grid)
    safety_manager.create_realistic_scenario()
    
    # Create router
    router = ShipRouter(grid, weather)
    
    # Create genetic optimizer
    genetic_optimizer = GeneticRouteOptimizer(grid, weather, population_size=50, generations=30)
    
    # Create carbon tracker
    carbon_tracker = CarbonTracker(weather)
    
    # Create learning system
    learning_system = RouteLearningSystem(grid)
    learning_system.import_learning_data()  # Load previous learning if exists
    
    print(f"✅ Enhanced system initialized: {grid}, {weather}")
    print(f"✅ Safety zones: {len(safety_manager.danger_zones)} danger zones")

    # Set a default geographic bounding box centered near English Channel by default
    # This maps lat/lon to grid indices. These can be adjusted later if needed.
    center_lat = 51.2
    center_lon = 2.7
    total_km = grid_size * grid.cell_size_km
    deg_lat_span = total_km / 111.0
    # Avoid division by zero for cos(latitude)
    deg_lon_span = total_km / (111.0 * max(0.1, abs(math.cos(math.radians(center_lat)))))

    map_bbox['lat_min'] = center_lat - deg_lat_span / 2
    map_bbox['lat_max'] = center_lat + deg_lat_span / 2
    map_bbox['lon_min'] = center_lon - deg_lon_span / 2
    map_bbox['lon_max'] = center_lon + deg_lon_span / 2

    print(f"Mapped geographic bbox to grid: {map_bbox}")


def _latlon_to_cell_indices(lat: float, lon: float):
    """Convert geographic lat/lon into grid cell indices (x, y).

    Uses the configured `map_bbox` and clamps into valid grid range.
    """
    if not grid:
        return None, None

    lat_min = map_bbox['lat_min']
    lat_max = map_bbox['lat_max']
    lon_min = map_bbox['lon_min']
    lon_max = map_bbox['lon_max']

    if None in (lat_min, lat_max, lon_min, lon_max):
        return None, None

    # Normalize lon/lat to 0..1 inside bbox
    fx = (lon - lon_min) / (lon_max - lon_min)
    fy = (lat - lat_min) / (lat_max - lat_min)

    # Convert to indices
    ix = int(round(fx * (grid.width - 1)))
    iy = int(round(fy * (grid.height - 1)))

    # Clamp
    ix = max(0, min(grid.width - 1, ix))
    iy = max(0, min(grid.height - 1, iy))

    return ix, iy


def _cell_to_latlon(cell: Cell):
    """Convert a `Cell` into geographic (lat, lon) using configured bbox."""
    if not grid:
        return None, None

    lon_min = map_bbox['lon_min']
    lon_max = map_bbox['lon_max']
    lat_min = map_bbox['lat_min']
    lat_max = map_bbox['lat_max']

    fx = cell.x / (grid.width - 1) if grid.width > 1 else 0
    fy = cell.y / (grid.height - 1) if grid.height > 1 else 0

    lon = lon_min + fx * (lon_max - lon_min)
    lat = lat_min + fy * (lat_max - lat_min)

    return lat, lon


def _result_to_geo(result):
    """Convert a RouteResult-like object to a serializable dict with geographic path."""
    d = result.to_dict()
    # Replace path cell indices with lat/lon pairs [lon, lat]
    try:
        geo_path = []
        for x, y in d.get('path', []):
            cell = grid.get_cell(int(x), int(y))
            if cell:
                lat, lon = _cell_to_latlon(cell)
                geo_path.append([lon, lat])
        d['path'] = geo_path
    except Exception:
        # If conversion fails, leave path as-is
        pass
    return d


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Enhanced Ship Routing API',
        'features': [
            'Traditional Algorithms (Dijkstra, A*, Weather-Aware, Fuel-Optimized)',
            'Genetic Algorithm (Multi-objective)',
            'Safety Zones (Pirate/Military avoidance)',
            'Carbon Emission Tracking',
            'ML-based Route Learning'
        ]
    })


@app.route('/api/route', methods=['POST', 'OPTIONS'])
def calculate_route():
    """
    Calculate route using traditional algorithms.
    
    Request body:
    {
        "start": {"x": 10, "y": 10},
        "goal": {"x": 90, "y": 90},
        "algorithm": "a_star"  // or "dijkstra", "weather_aware", "fuel_optimized"
    }
    """
    if request.method == 'OPTIONS':
        return '', 200
        
    if not router:
        return jsonify({'error': 'System not initialized'}), 500
    
    data = request.json

    # Accept either grid indices {x,y} or geographic coords {lat, lon}
    def _resolve_point(pt):
        if 'x' in pt and 'y' in pt:
            return int(pt['x']), int(pt['y'])
        if 'lat' in pt and 'lon' in pt:
            ix, iy = _latlon_to_cell_indices(float(pt['lat']), float(pt['lon']))
            return ix, iy
        return None, None

    start_x, start_y = _resolve_point(data.get('start', {}))
    goal_x, goal_y = _resolve_point(data.get('goal', {}))

    start_cell = grid.get_cell(start_x, start_y) if start_x is not None else None
    goal_cell = grid.get_cell(goal_x, goal_y) if goal_x is not None else None
    
    if not start_cell or not goal_cell:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    if start_cell.is_land or goal_cell.is_land:
        return jsonify({'error': 'Start or goal is on land'}), 400
    
    algorithm = data.get('algorithm', 'a_star').lower()
    
    try:
        if algorithm == 'dijkstra':
            result = router.dijkstra(start_cell, goal_cell)
        elif algorithm == 'a_star':
            result = router.a_star(start_cell, goal_cell)
        elif algorithm == 'bidirectional':
            from bidirectional_astar import BidirectionalAStar
            bi_astar = BidirectionalAStar(grid, weather)
            result = bi_astar.search(start_cell, goal_cell)
            if not result:
                return jsonify({'error': 'No path found'}), 404
        elif algorithm == 'weather_aware':
            result = router.weather_aware_astar(start_cell, goal_cell)
        elif algorithm == 'fuel_optimized':
            result = router.fuel_optimized(start_cell, goal_cell)
        else:
            return jsonify({'error': f'Unknown algorithm: {algorithm}'}), 400
        
        # Convert path coordinates to geographic lat/lon for frontend
        return jsonify(_result_to_geo(result))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/route/advanced', methods=['POST'])
def calculate_advanced_route():
    """
    Calculate route with advanced features.
    
    Request body:
    {
        "start": {"x": 10, "y": 10},
        "goal": {"x": 90, "y": 90},
        "algorithm": "genetic",  // or traditional algorithms
        "preferences": {
            "distance_weight": 0.25,
            "fuel_weight": 0.35,
            "safety_weight": 0.25,
            "time_weight": 0.15
        }
    }
    """
    if not all([router, genetic_optimizer, safety_manager, carbon_tracker]):
        return jsonify({'error': 'System not initialized'}), 500
    
    data = request.json

    def _resolve_point(pt):
        if 'x' in pt and 'y' in pt:
            return int(pt['x']), int(pt['y'])
        if 'lat' in pt and 'lon' in pt:
            return _latlon_to_cell_indices(float(pt['lat']), float(pt['lon']))
        return None, None

    start_x, start_y = _resolve_point(data.get('start', {}))
    goal_x, goal_y = _resolve_point(data.get('goal', {}))

    start_cell = grid.get_cell(start_x, start_y) if start_x is not None else None
    goal_cell = grid.get_cell(goal_x, goal_y) if goal_x is not None else None
    
    if not start_cell or not goal_cell:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    algorithm = data.get('algorithm', 'genetic')
    
    try:
        if algorithm == 'genetic':
            preferences = data.get('preferences', {
                'distance': 0.25, 'fuel': 0.35, 'safety': 0.25, 'time': 0.15
            })
            
            route = genetic_optimizer.optimize(start_cell, goal_cell, preferences)
            
            # Calculate emissions
            emissions = carbon_tracker.calculate_emissions(route.waypoints, route.fuel)
            
            # Get safety score
            safety_score = safety_manager.get_route_safety_score(route.waypoints)
            
            # Get learning predictions
            prediction = learning_system.predict_route_performance(route.waypoints)
            
            # Record for learning
            learning_system.record_route(route.waypoints, {
                'distance': route.distance,
                'fuel': route.fuel,
                'time': route.time
            })
            
            geo_path = []
            for cell in route.waypoints:
                lat, lon = _cell_to_latlon(cell)
                geo_path.append([lon, lat])

            return jsonify({
                'algorithm': 'Genetic Algorithm',
                'path': geo_path,
                'distance_km': route.distance,
                'fuel_tons': route.fuel,
                'time_hours': route.time,
                'fitness': route.fitness,
                'safety_score': safety_score,
                'emissions': emissions.to_dict(),
                'ml_prediction': prediction,
                'green_suggestions': carbon_tracker.get_green_routing_suggestions(emissions)
            })
        else:
            # Use traditional algorithms
            result = router.a_star(start_cell, goal_cell)
            emissions = carbon_tracker.calculate_emissions(result.path, result.fuel_tons)
            safety_score = safety_manager.get_route_safety_score(result.path)
            
            res = _result_to_geo(result)
            res.update({'safety_score': safety_score, 'emissions': emissions.to_dict()})
            return jsonify(res)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/safety/zones', methods=['GET'])
def get_safety_zones():
    """Get all danger zones."""
    if not safety_manager:
        return jsonify({'error': 'System not initialized'}), 500
    
    zones = []
    for zone in safety_manager.danger_zones:
        zones.append({
            'center': {'x': zone.center_x, 'y': zone.center_y},
            'radius': zone.radius,
            'danger_level': zone.danger_level,
            'type': zone.zone_type
        })
    
    return jsonify({'zones': zones, 'danger_map': safety_manager.get_danger_map().tolist()})


@app.route('/api/emissions/compare', methods=['POST'])
def compare_emissions():
    """Compare emissions with other transport modes."""
    data = request.json
    distance = data.get('distance_km', 1000)
    fuel_tons = data.get('fuel_tons', 50)
    
    emissions = carbon_tracker.calculate_emissions([], fuel_tons)
    comparison = carbon_tracker.compare_with_alternatives(distance, emissions)
    
    return jsonify({
        'ship_emissions': emissions.to_dict(),
        'comparison': comparison,
        'slow_steaming': carbon_tracker.calculate_slow_steaming_impact(fuel_tons, 10)
    })


@app.route('/api/learning/recommendations', methods=['POST'])
def get_learning_recommendations():
    """Get ML-based route recommendations."""
    data = request.json

    def _resolve_point(pt):
        if 'x' in pt and 'y' in pt:
            return int(pt['x']), int(pt['y'])
        if 'lat' in pt and 'lon' in pt:
            return _latlon_to_cell_indices(float(pt['lat']), float(pt['lon']))
        return None, None

    start_x, start_y = _resolve_point(data.get('start', {}))
    goal_x, goal_y = _resolve_point(data.get('goal', {}))

    start_cell = grid.get_cell(start_x, start_y) if start_x is not None else None
    goal_cell = grid.get_cell(goal_x, goal_y) if goal_x is not None else None
    
    recommendations = learning_system.get_recommendations(start_cell, goal_cell)
    
    return jsonify({
        'recommendations': recommendations,
        'total_routes_learned': len(learning_system.route_history)
    })


@app.route('/api/compare', methods=['POST'])
def compare_routes():
    """Compare all algorithms including genetic."""
    if not all([router, genetic_optimizer]):
        return jsonify({'error': 'System not initialized'}), 500
    
    data = request.json
    start_x = data['start']['x']
    start_y = data['start']['y']
    goal_x = data['goal']['x']
    goal_y = data['goal']['y']
    
    start_cell = grid.get_cell(start_x, start_y)
    goal_cell = grid.get_cell(goal_x, goal_y)
    
    if not start_cell or not goal_cell:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    try:
        # Traditional algorithms
        results = router.compare_algorithms(start_cell, goal_cell)
        
        # Add genetic algorithm
        genetic_route = genetic_optimizer.optimize(start_cell, goal_cell)
        
        results_dict = {name: _result_to_geo(result) for name, result in results.items()}

        # Add genetic result (converted to geo)
        geo_path = []
        for cell in genetic_route.waypoints:
            lat, lon = _cell_to_latlon(cell)
            geo_path.append([lon, lat])

        results_dict['genetic'] = {
            'algorithm': 'Genetic Algorithm',
            'path': geo_path,
            'distance_km': genetic_route.distance,
            'fuel_tons': genetic_route.fuel,
            'time_hours': genetic_route.time,
            'fitness': genetic_route.fitness,
            'safety_score': genetic_route.safety
        }

        return jsonify(results_dict)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    initialize_system()
    print("\n🚀 Starting Enhanced Ship Routing API server...")
    print("📍 API available at http://localhost:5000")
    print("\n✨ New Features:")
    print("   - Genetic Algorithm optimization")
    print("   - Pirate & danger zone avoidance")
    print("   - Carbon emission tracking")
    print("   - ML-based route learning")
    app.run(debug=True, port=5000)
