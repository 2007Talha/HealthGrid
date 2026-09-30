/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        command: {
          950: '#ffffff',      // Page background → white
          900: '#f8fafc',      // Surface → slate-50
          850: '#ffffff',      // Card background → white
          800: '#f1f5f9',      // Elevated surface → slate-100
          700: '#e2e8f0',      // Border → slate-200
          600: '#cbd5e1',      // Secondary border → slate-300
          500: '#94a3b8',      // Muted text → slate-400
          400: '#64748b',      // Tertiary text → slate-500
        },
        primary: {
          DEFAULT: '#2563eb',  // Blue-600
          hover: '#1d4ed8',    // Blue-700
          light: '#dbeafe',    // Blue-100
          dark: '#1e40af',     // Blue-800
        },
        accent: {
          DEFAULT: '#ea580c',  // Orange-600
          hover: '#c2410c',    // Orange-700
          light: '#ffedd5',    // Orange-100
        },
        risk: {
          critical: '#dc2626', // Red-600
          high: '#ea580c',     // Orange-600
          warning: '#ca8a04',  // Yellow-600
          normal: '#16a34a',   // Green-600
          info: '#2563eb',     // Blue-600
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Menlo', 'monospace'],
      }
    },
  },
  plugins: [],
}
