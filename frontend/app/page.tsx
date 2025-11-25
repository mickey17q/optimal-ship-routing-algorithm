'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import AlgorithmControls from '@/components/AlgorithmControls'
import RouteMetrics from '@/components/RouteMetrics'

// Dynamically import map component (Leaflet doesn't work with SSR)
const MapComponent = dynamic(() => import('@/components/MapComponent'), {
    ssr: false,
    loading: () => (
        <div className="w-full h-full flex items-center justify-center bg-ocean-900">
            <div className="text-white text-xl">Loading map...</div>
        </div>
    ),
})

export interface RoutePoint {
    x: number
    y: number
}

export interface RouteResult {
    path: [number, number][]
    distance_km: number
    cost: number
    fuel_tons: number
    time_hours: number
    nodes_explored: number
    computation_time_ms: number
    algorithm: string
}

export default function Home() {
    const [startPoint, setStartPoint] = useState<RoutePoint | null>(null)
    const [endPoint, setEndPoint] = useState<RoutePoint | null>(null)
    const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>('a_star')
    const [routes, setRoutes] = useState<Record<string, RouteResult>>({})
    const [isCalculating, setIsCalculating] = useState(false)
    const [compareMode, setCompareMode] = useState(false)
    const [gridSize, setGridSize] = useState(100)

    const calculateRoute = async () => {
        if (!startPoint || !endPoint) {
            alert('Please select both start and end points on the map')
            return
        }

        setIsCalculating(true)
        setRoutes({})

        try {
            let endpoint = compareMode ? '/api/compare' : '/api/route'
            // Use /api/route/advanced for genetic algorithm
            if (!compareMode && selectedAlgorithm === 'genetic') {
                endpoint = '/api/route/advanced'
            }
            const startPayload = { lat: startPoint.y, lon: startPoint.x }
            const goalPayload = { lat: endPoint.y, lon: endPoint.x }

            let body = compareMode
                ? { start: startPayload, goal: goalPayload }
                : { start: startPayload, goal: goalPayload, algorithm: selectedAlgorithm }

            // Add default preferences for genetic algorithm
            if (!compareMode && selectedAlgorithm === 'genetic') {
                body = {
                    ...body,
                    preferences: {
                        distance: 0.25,
                        fuel: 0.35,
                        safety: 0.25,
                        time: 0.15,
                    },
                }
            }

            const response = await fetch(`http://localhost:5000${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            })

            if (!response.ok) {
                const error = await response.json()
                throw new Error(error.error || 'Failed to calculate route')
            }

            const data = await response.json()

            if (compareMode) {
                setRoutes(data)
            } else {
                setRoutes({ [selectedAlgorithm]: data })
            }
        } catch (error) {
            console.error('Error calculating route:', error)
            alert(error instanceof Error ? error.message : 'Failed to calculate route')
        } finally {
            setIsCalculating(false)
        }
    }

    const clearRoute = () => {
        setRoutes({})
        setStartPoint(null)
        setEndPoint(null)
    }

    return (
        <main className="flex min-h-screen flex-col bg-gradient-to-br from-ocean-900 via-ocean-800 to-ocean-900">
            {/* Header */}
            <header className="glass-dark text-white p-6 shadow-lg z-10">
                <div className="max-w-7xl mx-auto">
                    <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-ocean-300 to-ocean-100 bg-clip-text text-transparent">
                        Ship Routing Optimizer
                    </h1>
                    <p className="text-ocean-200">
                        Advanced pathfinding algorithms for optimal maritime navigation
                    </p>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex flex-col lg:flex-row gap-4 p-4">
                {/* Controls Panel */}
                <div className="lg:w-96 space-y-4">
                    <AlgorithmControls
                        selectedAlgorithm={selectedAlgorithm}
                        onAlgorithmChange={setSelectedAlgorithm}
                        compareMode={compareMode}
                        onCompareModeChange={setCompareMode}
                        onCalculate={calculateRoute}
                        onClear={clearRoute}
                        isCalculating={isCalculating}
                        hasPoints={!!startPoint && !!endPoint}
                    />

                    {Object.keys(routes).length > 0 && (
                        <RouteMetrics routes={routes} compareMode={compareMode} />
                    )}
                </div>

                {/* Map */}
                <div className="flex-1 glass-dark rounded-lg overflow-hidden shadow-2xl min-h-[600px]">
                    <MapComponent
                        startPoint={startPoint}
                        endPoint={endPoint}
                        onStartPointChange={setStartPoint}
                        onEndPointChange={setEndPoint}
                        routes={routes}
                        gridSize={gridSize}
                    />
                </div>
            </div>

            {/* Footer */}
            <footer className="glass-dark text-white p-4 text-center text-sm z-10">
                <p className="text-ocean-200">
                    Ship Routing Algorithm Course Project • Dijkstra • A* • Weather-Aware • Fuel-Optimized
                </p>
            </footer>
        </main>
    )
}
