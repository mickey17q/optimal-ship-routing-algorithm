/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './pages/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
        './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                ocean: {
                    50: '#e6f7ff',
                    100: '#bae7ff',
                    200: '#91d5ff',
                    300: '#69c0ff',
                    400: '#40a9ff',
                    500: '#1890ff',
                    600: '#096dd9',
                    700: '#0050b3',
                    800: '#003a8c',
                    900: '#002766',
                },
                ship: {
                    primary: '#1e40af',
                    secondary: '#3b82f6',
                    accent: '#60a5fa',
                }
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
        },
    },
    plugins: [],
}
