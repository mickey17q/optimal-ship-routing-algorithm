'use client'

import { RouteResult } from '@/app/page'

interface RouteMetricsProps {
    routes: Record<string, RouteResult>
    compareMode: boolean
}

export default function RouteMetrics({ routes, compareMode }: RouteMetricsProps) {
    const routeEntries = Object.entries(routes)

    if (routeEntries.length === 0) return null

    // Find best values
    const bestDistance = Math.min(...routeEntries.map(([_, r]) => r.distance_km || 0))
    const bestFuel = Math.min(...routeEntries.map(([_, r]) => r.fuel_tons || 0))
    const bestTime = Math.min(...routeEntries.map(([_, r]) => r.time_hours || 0))
    const fastestComputation = Math.min(...routeEntries.map(([_, r]) => r.computation_time_ms || 0))

    const isBest = (value: number, best: number) => Math.abs(value - best) < 0.01

    const algorithmColors: Record<string, string> = {
        bidirectional: '#00d4ff',
        genetic: '#a855f7',
        a_star: '#3b82f6',
        weather_aware: '#10b981',
        fuel_optimized: '#f59e0b',
        dijkstra: '#6b7280',
    }

    return (
        <div className="metrics-panel">
            <div className="panel-section">
                <div className="section-title">Route Analysis</div>

                {routeEntries.map(([algorithm, result]) => {
                    const color = algorithmColors[algorithm] || '#4a9eff'

                    return (
                        <div
                            key={algorithm}
                            style={{
                                background: 'var(--maritime-dark)',
                                border: '1px solid var(--maritime-border)',
                                borderRadius: '6px',
                                padding: '12px',
                                marginBottom: '10px'
                            }}
                        >
                            {/* Algorithm Header */}
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                marginBottom: '10px',
                                paddingBottom: '8px',
                                borderBottom: '1px solid rgba(255,255,255,0.05)'
                            }}>
                                <div style={{
                                    fontWeight: 600,
                                    fontSize: '14px',
                                    color: color
                                }}>
                                    {result.algorithm}
                                </div>
                                <div style={{ display: 'flex', gap: '4px' }}>
                                    {isBest(result.distance_km || 0, bestDistance) && (
                                        <span style={{
                                            background: 'rgba(59, 130, 246, 0.2)',
                                            color: '#3b82f6',
                                            padding: '2px 6px',
                                            borderRadius: '4px',
                                            fontSize: '10px',
                                            fontWeight: 600
                                        }}>
                                            SHORTEST
                                        </span>
                                    )}
                                    {isBest(result.fuel_tons || 0, bestFuel) && (
                                        <span style={{
                                            background: 'rgba(16, 185, 129, 0.2)',
                                            color: '#10b981',
                                            padding: '2px 6px',
                                            borderRadius: '4px',
                                            fontSize: '10px',
                                            fontWeight: 600
                                        }}>
                                            EFFICIENT
                                        </span>
                                    )}
                                    {isBest(result.computation_time_ms || 0, fastestComputation) && (
                                        <span style={{
                                            background: 'rgba(0, 212, 255, 0.2)',
                                            color: '#00d4ff',
                                            padding: '2px 6px',
                                            borderRadius: '4px',
                                            fontSize: '10px',
                                            fontWeight: 600
                                        }}>
                                            FASTEST
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Metrics Grid */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                                <div className="metric-row" style={{ flexDirection: 'column', alignItems: 'flex-start', padding: 0, border: 'none' }}>
                                    <div className="metric-label">Distance</div>
                                    <div className="metric-value">{(result.distance_km || 0).toFixed(2)} km</div>
                                </div>
                                <div className="metric-row" style={{ flexDirection: 'column', alignItems: 'flex-start', padding: 0, border: 'none' }}>
                                    <div className="metric-label">Fuel</div>
                                    <div className="metric-value">{(result.fuel_tons || 0).toFixed(2)} tons</div>
                                </div>
                                <div className="metric-row" style={{ flexDirection: 'column', alignItems: 'flex-start', padding: 0, border: 'none' }}>
                                    <div className="metric-label">Time</div>
                                    <div className="metric-value">{(result.time_hours || 0).toFixed(2)} hrs</div>
                                </div>
                                <div className="metric-row" style={{ flexDirection: 'column', alignItems: 'flex-start', padding: 0, border: 'none' }}>
                                    <div className="metric-label">Computation</div>
                                    <div className="metric-value">{(result.computation_time_ms || 0).toFixed(1)} ms</div>
                                </div>
                            </div>

                            {/* Additional Info */}
                            <div style={{
                                marginTop: '10px',
                                paddingTop: '8px',
                                borderTop: '1px solid rgba(255,255,255,0.05)',
                                fontSize: '11px',
                                color: 'var(--text-secondary)'
                            }}>
                                Nodes explored: {(result.nodes_explored || 0).toLocaleString()}
                            </div>
                        </div>
                    )
                })}

                {/* Comparison Summary */}
                {compareMode && routeEntries.length > 1 && (
                    <div style={{
                        background: 'rgba(74, 158, 255, 0.1)',
                        border: '1px solid rgba(74, 158, 255, 0.3)',
                        borderRadius: '6px',
                        padding: '12px',
                        marginTop: '10px'
                    }}>
                        <div style={{ fontWeight: 600, marginBottom: '8px', color: 'var(--maritime-accent)' }}>
                            📊 Comparison Summary
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                            <div>Distance range: {bestDistance.toFixed(2)} - {Math.max(...routeEntries.map(([_, r]) => r.distance_km || 0)).toFixed(2)} km</div>
                            <div>Fuel range: {bestFuel.toFixed(2)} - {Math.max(...routeEntries.map(([_, r]) => r.fuel_tons || 0)).toFixed(2)} tons</div>
                            <div style={{ color: '#10b981', fontWeight: 600 }}>
                                Savings: {((Math.max(...routeEntries.map(([_, r]) => r.fuel_tons || 0)) - bestFuel) / Math.max(...routeEntries.map(([_, r]) => r.fuel_tons || 1)) * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
