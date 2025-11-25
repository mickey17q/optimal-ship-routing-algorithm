'use client'

interface AlgorithmControlsProps {
    selectedAlgorithm: string
    onAlgorithmChange: (algorithm: string) => void
    compareMode: boolean
    onCompareModeChange: (compare: boolean) => void
    onCalculate: () => void
    onClear: () => void
    isCalculating: boolean
}

export default function AlgorithmControls({
    selectedAlgorithm,
    onAlgorithmChange,
    onCalculate,
    onClear,
    isCalculating,
    compareMode,
    onCompareModeChange,
}: AlgorithmControlsProps) {
    const algorithms = [
        {
            value: 'bidirectional',
            name: 'Bidirectional A*',
            badge: 'NEW',
            desc: '2-3× faster than A*. Searches from both start and goal simultaneously.',
            icon: '⚡',
            color: '#00d4ff'
        },
        {
            value: 'genetic',
            name: 'Genetic Algorithm',
            badge: 'ADVANCED',
            desc: 'Multi-objective optimization balancing distance, fuel, safety, and time.',
            icon: '🧬',
            color: '#a855f7'
        },
        {
            value: 'a_star',
            name: 'A* Algorithm',
            badge: 'OPTIMAL',
            desc: 'Heuristic-based pathfinding with guaranteed optimal solution.',
            icon: '🎯',
            color: '#3b82f6'
        },
        {
            value: 'weather_aware',
            name: 'Weather-Aware A*',
            badge: 'SMART',
            desc: 'Considers weather conditions, storms, and sea state for safer routing.',
            icon: '🌊',
            color: '#10b981'
        },
        {
            value: 'fuel_optimized',
            name: 'Fuel-Optimized',
            badge: 'ECO',
            desc: 'Minimizes fuel consumption and carbon emissions for green shipping.',
            icon: '⛽',
            color: '#f59e0b'
        },
        {
            value: 'dijkstra',
            name: 'Dijkstra',
            badge: 'CLASSIC',
            desc: 'Traditional shortest path algorithm, explores all possibilities.',
            icon: '📍',
            color: '#6b7280'
        },
    ]

    return (
        <>
            {/* Top Bar */}
            <div className="top-bar">
                <div className="logo">
                    <span>🚢</span>
                    <span>Advanced Ship Routing System</span>
                </div>
                <div style={{ marginLeft: 'auto', fontSize: '13px', color: '#9ca3af' }}>
                    6 Algorithms | Real-time Optimization
                </div>
            </div>

            {/* Control Panel */}
            <div className="control-panel">
                {/* Instructions */}
                <div className="panel-section">
                    <div className="section-title">Quick Start</div>
                    <div className="info-badge">
                        <div style={{ fontWeight: 600, marginBottom: '6px' }}>📍 How to use:</div>
                        <ol style={{ paddingLeft: '16px', margin: 0 }}>
                            <li>Click map to set start point</li>
                            <li>Click again for destination</li>
                            <li>Select algorithm below</li>
                            <li>Click Calculate Route</li>
                        </ol>
                    </div>
                </div>

                {/* Algorithm Selection */}
                <div className="panel-section">
                    <div className="section-title">Select Routing Algorithm</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {algorithms.map((algo) => (
                            <div
                                key={algo.value}
                                className={`algorithm-card ${selectedAlgorithm === algo.value ? 'active' : ''}`}
                                onClick={() => onAlgorithmChange(algo.value)}
                            >
                                <div className="algorithm-header">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <span style={{ fontSize: '18px' }}>{algo.icon}</span>
                                        <span className="algorithm-name">{algo.name}</span>
                                    </div>
                                    <span className="algorithm-badge" style={{ background: algo.color }}>
                                        {algo.badge}
                                    </span>
                                </div>
                                <div className="algorithm-desc">{algo.desc}</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Compare Mode */}
                <div className="panel-section">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px' }}>
                                Compare All Algorithms
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                                Run all 6 algorithms simultaneously
                            </div>
                        </div>
                        <div
                            className={`toggle-switch ${compareMode ? 'active' : ''}`}
                            onClick={() => onCompareModeChange(!compareMode)}
                        >
                            <div className="toggle-knob"></div>
                        </div>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="panel-section">
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <button
                            onClick={onCalculate}
                            disabled={isCalculating}
                            className="btn-primary"
                        >
                            {isCalculating ? (
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                                    <div className="loading-spinner"></div>
                                    Calculating Route...
                                </div>
                            ) : (
                                <>🗺️ Calculate Optimal Route</>
                            )}
                        </button>
                        <button onClick={onClear} className="btn-secondary">
                            🗑️ Clear Points
                        </button>
                    </div>
                </div>

                {/* Innovation Highlight */}
                <div className="panel-section">
                    <div className="section-title">Innovation Highlights</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                        <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: 'var(--maritime-accent)' }}>⚡ Bidirectional A*:</strong> Novel implementation, 2-3× faster
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: '#a855f7' }}>🧬 Genetic Algorithm:</strong> Multi-objective optimization
                        </div>
                        <div>
                            <strong style={{ color: '#10b981' }}>🌊 Weather-Aware:</strong> Real-time condition analysis
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
