/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        sidebar: '#0f1117',
        surface: '#1a1d27',
        card: '#1e2130',
        border: '#2a2d3e',
        accent: '#6366f1',
        'accent-hover': '#5558e3',
      },
      fontFamily: {
        sans: ['system-ui', '-apple-system', 'sans-serif'],
        mono: ['ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
}
