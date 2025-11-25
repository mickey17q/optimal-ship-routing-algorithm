# Ship Routing Optimizer

A comprehensive implementation of optimal ship routing algorithms with interactive web visualization for maritime navigation.

![Ship Routing](https://img.shields.io/badge/Ship-Routing-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)

## 🎯 Project Overview

This project implements multiple pathfinding and optimization algorithms for ship routing, considering:
- **Distance optimization** (shortest path)
- **Weather conditions** (wind, waves, currents)
- **Fuel efficiency** (consumption minimization)
- **Safety** (obstacle avoidance)
- **Real-time visualization** (interactive web interface)

## 🚀 Features

### Algorithms Implemented
1. **Dijkstra's Algorithm** - Classic shortest path (baseline)
2. **A\* Algorithm** - Heuristic-based optimization (faster than Dijkstra)
3. **Weather-Aware A\*** - Incorporates weather cost factors
4. **Fuel-Optimized Routing** - Minimizes fuel consumption

### Interactive Visualization
- Real-time interactive map with Leaflet.js
- Click-to-select waypoints
- Animated route rendering
- Algorithm comparison mode
- Performance metrics dashboard

## 📁 Project Structure

```
ship-routing/
├── backend/
│   ├── grid.py              # Navigation grid system
│   ├── weather.py           # Weather simulation
│   ├── algorithms.py        # Routing algorithms
│   ├── api.py              # Flask REST API
│   ├── requirements.txt    # Python dependencies
│   └── examples/
│       └── example_routes.py
├── frontend/
│   ├── app/
│   │   ├── page.tsx        # Main application
│   │   ├── layout.tsx      # Root layout
│   │   └── globals.css     # Global styles
│   ├── components/
│   │   ├── MapComponent.tsx
│   │   ├── AlgorithmControls.tsx
│   │   └── RouteMetrics.tsx
│   └── package.json
└── docs/
    ├── ALGORITHMS.md        # Algorithm documentation
    └── PROJECT_REPORT.md    # Course project report
```

## 🛠️ Installation

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API server:
```bash
python api.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 📖 Usage

### Web Interface

1. Open `http://localhost:3000` in your browser
2. Click on the map to set the **start point** (green marker)
3. Click again to set the **end point** (red marker)
4. Select an algorithm or enable **Compare Mode**
5. Click **Calculate Route**
6. View the route visualization and metrics

### API Endpoints

#### Calculate Route
```bash
POST http://localhost:5000/api/route
Content-Type: application/json

{
  "start": {"x": 10, "y": 10},
  "goal": {"x": 90, "y": 90},
  "algorithm": "a_star"
}
```

#### Compare Algorithms
```bash
POST http://localhost:5000/api/compare
Content-Type: application/json

{
  "start": {"x": 10, "y": 10},
  "goal": {"x": 90, "y": 90}
}
```

#### Get Grid Information
```bash
GET http://localhost:5000/api/grid
```

#### Get Weather Data
```bash
GET http://localhost:5000/api/weather?x=50&y=50
```

### Python Examples

Run example scenarios:
```bash
cd backend/examples
python example_routes.py
```

## 🧪 Testing

Run the test suite:
```bash
cd backend
pytest tests/
```

## 📊 Algorithm Comparison

| Algorithm | Speed | Optimality | Weather-Aware | Fuel-Optimized |
|-----------|-------|------------|---------------|----------------|
| Dijkstra | Slow | Optimal | ❌ | ❌ |
| A* | Fast | Optimal | ❌ | ❌ |
| Weather-Aware | Fast | Near-Optimal | ✅ | Partial |
| Fuel-Optimized | Fast | Near-Optimal | ✅ | ✅ |

## 🌊 Weather Simulation

The system simulates realistic ocean conditions:
- **Wind Speed & Direction** - Affects ship resistance
- **Wave Height** - Impacts fuel consumption
- **Ocean Currents** - Can assist or hinder navigation
- **Storm Systems** - Localized high-intensity weather

## 🎓 Course Project

This project was developed as a comprehensive course assignment demonstrating:
- Advanced algorithm implementation
- Real-world optimization problems
- Full-stack development
- Interactive data visualization
- Performance analysis

For detailed algorithm theory and analysis, see [ALGORITHMS.md](docs/ALGORITHMS.md)

For the complete project report, see [PROJECT_REPORT.md](docs/PROJECT_REPORT.md)

## 🔧 Technologies Used

### Backend
- Python 3.8+
- NumPy (numerical computations)
- Flask (REST API)
- Flask-CORS (cross-origin support)

### Frontend
- Next.js 14 (React framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Leaflet.js (interactive maps)

## 📈 Performance

Typical performance on 100x100 grid:
- **Dijkstra**: ~50-100ms, explores ~5000 nodes
- **A\***: ~20-40ms, explores ~2000 nodes
- **Weather-Aware**: ~25-45ms, explores ~2500 nodes
- **Fuel-Optimized**: ~30-50ms, explores ~2800 nodes

## 🤝 Contributing

This is a course project, but suggestions are welcome!

## 📝 License

This project is created for educational purposes.


---

**Note**: Ensure both backend and frontend servers are running for full functionality.
