"""
Unit tests for ship routing algorithms.
"""

import pytest
import sys
sys.path.insert(0, '..')

from grid import NavigationGrid, Cell
from weather import WeatherSystem
from algorithms import ShipRouter


class TestNavigationGrid:
    """Test navigation grid functionality."""
    
    def test_grid_creation(self):
        """Test basic grid creation."""
        grid = NavigationGrid(50, 50, cell_size_km=10.0)
        assert grid.width == 50
        assert grid.height == 50
        assert grid.cell_size_km == 10.0
    
    def test_cell_access(self):
        """Test cell access and properties."""
        grid = NavigationGrid(10, 10)
        cell = grid.get_cell(5, 5)
        assert cell is not None
        assert cell.x == 5
        assert cell.y == 5
        assert not cell.is_land
    
    def test_land_marking(self):
        """Test marking cells as land."""
        grid = NavigationGrid(10, 10)
        grid.set_land(3, 3, True)
        cell = grid.get_cell(3, 3)
        assert cell.is_land
    
    def test_island_creation(self):
        """Test island creation."""
        grid = NavigationGrid(20, 20)
        grid.add_island(10, 10, 3)
        
        # Center should be land
        assert grid.get_cell(10, 10).is_land
        
        # Edge cells should be land
        assert grid.get_cell(10, 13).is_land
        
        # Outside radius should be water
        assert not grid.get_cell(10, 15).is_land
    
    def test_neighbors(self):
        """Test neighbor finding."""
        grid = NavigationGrid(10, 10)
        cell = grid.get_cell(5, 5)
        neighbors = grid.get_neighbors(cell, allow_diagonal=True)
        
        # Should have 8 neighbors in middle of grid
        assert len(neighbors) == 8
        
        # Corner cell should have 3 neighbors
        corner = grid.get_cell(0, 0)
        corner_neighbors = grid.get_neighbors(corner, allow_diagonal=True)
        assert len(corner_neighbors) == 3
    
    def test_distance_calculation(self):
        """Test distance calculation."""
        grid = NavigationGrid(10, 10, cell_size_km=10.0)
        cell1 = grid.get_cell(0, 0)
        cell2 = grid.get_cell(3, 4)
        
        distance = grid.get_distance(cell1, cell2)
        expected = 50.0  # 5 cells * 10km
        assert abs(distance - expected) < 0.1


class TestWeatherSystem:
    """Test weather simulation."""
    
    def test_weather_creation(self):
        """Test weather system creation."""
        grid = NavigationGrid(50, 50)
        weather = WeatherSystem(grid)
        assert weather.grid == grid
    
    def test_weather_pattern_generation(self):
        """Test weather pattern generation."""
        grid = NavigationGrid(50, 50)
        weather = WeatherSystem(grid)
        weather.generate_weather_pattern('moderate')
        
        # Check that weather data exists
        assert weather.wind_speed.shape == (50, 50)
        assert weather.wave_height.shape == (50, 50)
        
        # Check reasonable values
        assert weather.wind_speed.min() >= 0
        assert weather.wave_height.min() >= 0
    
    def test_storm_addition(self):
        """Test storm system addition."""
        grid = NavigationGrid(50, 50)
        weather = WeatherSystem(grid)
        weather.generate_weather_pattern('calm')
        
        initial_wind = weather.wind_speed[25, 25]
        weather.add_storm(25, 25, 10, intensity=2.0)
        
        # Wind should increase at storm center
        assert weather.wind_speed[25, 25] > initial_wind
    
    def test_fuel_consumption(self):
        """Test fuel consumption calculation."""
        grid = NavigationGrid(50, 50)
        weather = WeatherSystem(grid)
        
        fuel = weather.get_fuel_consumption(100, 1.0, 20.0)
        assert fuel > 0
        
        # Higher weather cost should increase fuel
        fuel_high = weather.get_fuel_consumption(100, 2.0, 20.0)
        assert fuel_high > fuel


class TestAlgorithms:
    """Test routing algorithms."""
    
    @pytest.fixture
    def setup_grid(self):
        """Create a test grid."""
        grid = NavigationGrid(30, 30, cell_size_km=10.0)
        # Add a small obstacle
        grid.add_island(15, 15, 3)
        return grid
    
    @pytest.fixture
    def setup_router(self, setup_grid):
        """Create a router with weather."""
        weather = WeatherSystem(setup_grid)
        weather.generate_weather_pattern('moderate')
        weather.apply_weather_to_grid()
        return ShipRouter(setup_grid, weather)
    
    def test_dijkstra(self, setup_router):
        """Test Dijkstra's algorithm."""
        grid = setup_router.grid
        start = grid.get_cell(5, 5)
        goal = grid.get_cell(25, 25)
        
        result = setup_router.dijkstra(start, goal)
        
        assert len(result.path) > 0
        assert result.path[0] == start
        assert result.path[-1] == goal
        assert result.distance_km > 0
        assert result.nodes_explored > 0
    
    def test_astar(self, setup_router):
        """Test A* algorithm."""
        grid = setup_router.grid
        start = grid.get_cell(5, 5)
        goal = grid.get_cell(25, 25)
        
        result = setup_router.a_star(start, goal)
        
        assert len(result.path) > 0
        assert result.path[0] == start
        assert result.path[-1] == goal
        assert result.distance_km > 0
    
    def test_astar_faster_than_dijkstra(self, setup_router):
        """Test that A* explores fewer nodes than Dijkstra."""
        grid = setup_router.grid
        start = grid.get_cell(5, 5)
        goal = grid.get_cell(25, 25)
        
        dijkstra_result = setup_router.dijkstra(start, goal)
        astar_result = setup_router.a_star(start, goal)
        
        # A* should explore fewer nodes
        assert astar_result.nodes_explored < dijkstra_result.nodes_explored
        
        # But should find same distance (both optimal)
        assert abs(astar_result.distance_km - dijkstra_result.distance_km) < 1.0
    
    def test_weather_aware(self, setup_router):
        """Test weather-aware routing."""
        grid = setup_router.grid
        start = grid.get_cell(5, 5)
        goal = grid.get_cell(25, 25)
        
        result = setup_router.weather_aware_astar(start, goal)
        
        assert len(result.path) > 0
        assert result.path[0] == start
        assert result.path[-1] == goal
    
    def test_fuel_optimized(self, setup_router):
        """Test fuel-optimized routing."""
        grid = setup_router.grid
        start = grid.get_cell(5, 5)
        goal = grid.get_cell(25, 25)
        
        result = setup_router.fuel_optimized(start, goal)
        
        assert len(result.path) > 0
        assert result.fuel_tons > 0
    
    def test_compare_algorithms(self, setup_router):
        """Test algorithm comparison."""
        grid = setup_router.grid
        start = grid.get_cell(5, 5)
        goal = grid.get_cell(25, 25)
        
        results = setup_router.compare_algorithms(start, goal)
        
        assert 'dijkstra' in results
        assert 'a_star' in results
        assert 'weather_aware' in results
        assert 'fuel_optimized' in results
        
        # All should find a path
        for name, result in results.items():
            assert len(result.path) > 0
    
    def test_no_path_through_land(self, setup_grid):
        """Test that algorithms don't path through land."""
        # Create a wall
        for y in range(10, 20):
            setup_grid.set_land(15, y, True)
        
        router = ShipRouter(setup_grid)
        start = setup_grid.get_cell(10, 15)
        goal = setup_grid.get_cell(20, 15)
        
        result = router.a_star(start, goal)
        
        # Should find a path around the wall
        assert len(result.path) > 0
        
        # No path cell should be land
        for cell in result.path:
            assert not cell.is_land


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
