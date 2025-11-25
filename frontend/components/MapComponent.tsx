'use client'

import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { RoutePoint, RouteResult } from '@/app/page'

interface MapComponentProps {
    startPoint: RoutePoint | null
    endPoint: RoutePoint | null
    onStartPointChange: (point: RoutePoint | null) => void
    onEndPointChange: (point: RoutePoint | null) => void
    routes: Record<string, RouteResult>
    gridSize: number
}

export default function MapComponent({
    startPoint,
    endPoint,
    onStartPointChange,
    onEndPointChange,
    routes,
    gridSize,
}: MapComponentProps) {
    const mapRef = useRef<L.Map | null>(null)
    const markersRef = useRef<L.Marker[]>([])
    const routeLayersRef = useRef<L.Polyline[]>([])

    useEffect(() => {
        if (mapRef.current) return // Map already initialized

        // Initialize map with geographic CRS and maritime tiles
        const map = L.map('map', {
            center: [51.2, 2.7], // center near example from MarineTraffic
            zoom: 6,
            minZoom: 2,
            maxZoom: 18,
            zoomControl: true,
        })

        // Add OpenStreetMap base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19,
        }).addTo(map)

        // Add OpenSeaMap seamark overlay for maritime features
        L.tileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenSeaMap contributors',
            maxZoom: 18,
            opacity: 0.9,
        }).addTo(map)

        // Sync bounding box with backend
        const syncBBox = () => {
            const bounds = map.getBounds()
            const lat_min = bounds.getSouth()
            const lat_max = bounds.getNorth()
            const lon_min = bounds.getWest()
            const lon_max = bounds.getEast()
            fetch('http://localhost:5000/api/configure_bbox', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat_min, lat_max, lon_min, lon_max }),
            })
        }
        map.on('moveend', syncBBox)
        syncBBox()

        mapRef.current = map

        return () => {
            map.remove()
            mapRef.current = null
        }
    }, [gridSize])

    // Separate effect for click handler to access current state
    useEffect(() => {
        if (!mapRef.current) return

        const handleClick = (e: L.LeafletMouseEvent) => {
            const lat = Number(e.latlng.lat.toFixed(6))
            const lng = Number(e.latlng.lng.toFixed(6))

            const point: RoutePoint = { x: lng, y: lat }

            if (!startPoint) {
                onStartPointChange(point)
            } else if (!endPoint) {
                onEndPointChange(point)
            } else {
                // Reset and start new route
                onStartPointChange(point)
                onEndPointChange(null)
            }
        }

        mapRef.current.on('click', handleClick)

        return () => {
            if (mapRef.current) {
                mapRef.current.off('click', handleClick)
            }
        }
    }, [startPoint, endPoint, gridSize, onStartPointChange, onEndPointChange])

    // Update markers
    useEffect(() => {
        if (!mapRef.current) return

        // Clear existing markers
        markersRef.current.forEach((marker) => marker.remove())
        markersRef.current = []

        // Create custom icons
        const startIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div class="w-8 h-8 bg-green-500 rounded-full border-4 border-white shadow-lg flex items-center justify-center text-white font-bold pulse-marker">S</div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 16],
        })

        const endIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div class="w-8 h-8 bg-red-500 rounded-full border-4 border-white shadow-lg flex items-center justify-center text-white font-bold pulse-marker">E</div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 16],
        })

        // Add start marker
        if (startPoint) {
            const marker = L.marker([startPoint.y, startPoint.x], { icon: startIcon })
                .addTo(mapRef.current!)
                .bindPopup(`Start: (${startPoint.y.toFixed(4)}, ${startPoint.x.toFixed(4)})`)
            markersRef.current.push(marker)
        }

        // Add end marker
        if (endPoint) {
            const marker = L.marker([endPoint.y, endPoint.x], { icon: endIcon })
                .addTo(mapRef.current!)
                .bindPopup(`End: (${endPoint.y.toFixed(4)}, ${endPoint.x.toFixed(4)})`)
            markersRef.current.push(marker)
        }
    }, [startPoint, endPoint])

    // Update routes and add animated ship
    useEffect(() => {
        if (!mapRef.current) return

        // Clear existing routes
        routeLayersRef.current.forEach((layer) => layer.remove())
        routeLayersRef.current = []

        // Algorithm colors
        const algorithmColors: Record<string, string> = {
            dijkstra: '#9333ea',
            a_star: '#3b82f6',
            weather_aware: '#10b981',
            fuel_optimized: '#f59e0b',
        }

        // Draw routes with animated ship
        Object.entries(routes).forEach(([algorithm, result], index) => {
            if (result.path && result.path.length > 0) {
                const latLngs: L.LatLngExpression[] = result.path.map(([x, y]) => [y, x])
                const color = algorithmColors[algorithm] || '#6366f1'

                // Draw route path with glow effect and hover popup on each segment
                const polyline = L.polyline(latLngs, {
                    color: color,
                    weight: 5,
                    opacity: 0.85,
                    className: 'route-path route-glow',
                    dashArray: index === 0 ? 'none' : '8 8',
                }).addTo(mapRef.current!)

                polyline.bindPopup(
                    `<div style='min-width:180px'>`
                    + `<strong style='font-size:1.1em;color:${color}'>${result.algorithm}</strong><br/>`
                    + `<span style='color:#e0e8f8'>Distance:</span> <b>${result.distance_km.toFixed(2)} km</b><br/>`
                    + `<span style='color:#e0e8f8'>Fuel:</span> <b>${result.fuel_tons.toFixed(2)} tons</b><br/>`
                    + `<span style='color:#e0e8f8'>Time:</span> <b>${result.time_hours.toFixed(2)} hours</b>`
                    + `</div>`
                )

                polyline.on('mouseover', function() {
                    polyline.openPopup();
                });
                polyline.on('mouseout', function() {
                    polyline.closePopup();
                });

                routeLayersRef.current.push(polyline)

                // Add animated ship marker on the first route
                if (index === 0 && latLngs.length > 1) {
                    let currentIndex = 0

                    // Create custom SVG ship icon
                    const shipSVG = `<svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <ellipse cx="18" cy="30" rx="8" ry="3" fill="#1a2d4f" opacity="0.3"/>
                        <path d="M18 6 L30 24 L18 20 L6 24 Z" fill="${color}" stroke="#fff" stroke-width="2"/>
                        <rect x="16" y="10" width="4" height="8" rx="2" fill="#fff"/>
                        <circle cx="18" cy="14" r="1.5" fill="#1a2d4f"/>
                    </svg>`;
                    const shipIcon = L.divIcon({
                        className: 'ship-marker',
                        html: `<div class="ship-icon" style="width:36px;height:36px;transform:rotate(0deg);">${shipSVG}</div>`,
                        iconSize: [36, 36],
                        iconAnchor: [18, 18],
                    });

                    const shipMarker = L.marker(latLngs[0], { icon: shipIcon })
                        .addTo(mapRef.current!)
                        .bindPopup(`<strong style='color:${color}'>${result.algorithm}</strong><br/>In Transit`)

                    // Animate ship movement
                    const animateShip = () => {
                        if (currentIndex < latLngs.length - 1) {
                            currentIndex++
                            const currentPos = latLngs[currentIndex] as L.LatLngTuple
                            const prevPos = latLngs[currentIndex - 1] as L.LatLngTuple

                            // Calculate rotation angle
                            const dx = currentPos[1] - prevPos[1]
                            const dy = currentPos[0] - prevPos[0]
                            const angle = Math.atan2(dx, -dy) * (180 / Math.PI)

                            // Update ship position and rotation
                            shipMarker.setLatLng(currentPos)
                            shipMarker.setIcon(L.divIcon({
                                className: 'ship-marker',
                                html: `<div class="ship-icon" style="width:36px;height:36px;transform:rotate(${angle}deg);transition:transform 0.5s;">${shipSVG}</div>`,
                                iconSize: [36, 36],
                                iconAnchor: [18, 18],
                            }))

                            setTimeout(animateShip, 100) // Move every 100ms
                        } else {
                            // Loop back to start
                            currentIndex = 0
                            setTimeout(animateShip, 2000) // Wait 2s before restarting
                        }
                    }

                    // Start animation after a short delay
                    setTimeout(animateShip, 1000)
                }
            }
        })
    }, [routes])

    return (
        <div className="relative w-full h-full">
            <div id="map" className="w-full h-full rounded-lg shadow-2xl border border-[#1a2d4f]" style={{boxShadow: '0 0 40px #0a1a2f88'}} />

            {/* Legend - MarineTraffic style */}
            {Object.keys(routes).length > 0 && (
                <div className="absolute bottom-6 right-6 bg-[#16243aee] backdrop-blur-lg border border-[#2a3d5f] shadow-lg p-5 rounded-xl text-white text-base space-y-3 z-[1000]" style={{minWidth: 220}}>
                    <div className="font-bold mb-2 text-lg tracking-wide" style={{letterSpacing: '0.04em'}}>Route Algorithms</div>
                    {Object.entries(routes).map(([algorithm, result]) => (
                        <div key={algorithm} className="flex items-center gap-3">
                            <div
                                className="w-6 h-2 rounded-full border border-[#2a3d5f]"
                                style={{
                                    backgroundColor:
                                        {
                                            dijkstra: '#9333ea',
                                            a_star: '#3b82f6',
                                            weather_aware: '#10b981',
                                            fuel_optimized: '#f59e0b',
                                        }[algorithm] || '#6366f1',
                                }}
                            />
                            <span className="font-semibold" style={{color: '#e0e8f8'}}>{result.algorithm}</span>
                        </div>
                    ))}
                    <div className="mt-3 text-xs text-[#a0b8d8]">Click route for details</div>
                </div>
            )}

            {/* Instructions - glassy panel */}
            {!startPoint && (
                <div className="absolute top-6 left-6 bg-[#16243aee] backdrop-blur-lg border border-[#2a3d5f] shadow-lg p-5 rounded-xl text-white text-base z-[1000]">
                    <div className="font-bold mb-1 text-lg">📍 Click to set start point</div>
                    <div className="text-[#a0b8d8] text-sm">Select a location on the map to begin routing</div>
                </div>
            )}
            {startPoint && !endPoint && (
                <div className="absolute top-6 left-6 bg-[#16243aee] backdrop-blur-lg border border-[#2a3d5f] shadow-lg p-5 rounded-xl text-white text-base z-[1000]">
                    <div className="font-bold mb-1 text-lg">📍 Click to set end point</div>
                    <div className="text-[#a0b8d8] text-sm">Select a destination to calculate route</div>
                </div>
            )}
        </div>
    )
}
