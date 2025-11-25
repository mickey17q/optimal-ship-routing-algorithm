import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import './leaflet-fix.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'Ship Routing Optimizer',
    description: 'Optimal ship routing algorithms with weather-aware pathfinding',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className={inter.className + ' bg-[#0a1a2f] text-white min-h-screen'} style={{background: 'linear-gradient(135deg, #0a1a2f 0%, #1a2d4f 100%)'}}>
                <div id="maritime-bg" style={{position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', background: 'radial-gradient(ellipse 80% 60% at 60% 40%, #1a2d4f 0%, #0a1a2f 100%)'}}></div>
                <div style={{position: 'relative', zIndex: 1}}>
                    {children}
                </div>
            </body>
        </html>
    )
}
