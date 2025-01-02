/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'f1': {
          red: '#E10600',      // Primary F1 red
          dark: '#15151E',     // F1 dark background
          gray: '#949498',     // F1 neutral gray
          carbon: '#2D2D2D',   // Carbon fiber inspired
          silver: '#F3F3F3',   // Light background
        },
        'team': {
          'mercedes': '#00D2BE',
          'redbull': '#0600EF',
          'ferrari': '#DC0000',
          'mclaren': '#FF8700',
          'alpine': '#0090FF',
          'astonmartin': '#006F62',
          'williams': '#005AFF',
          'alfaromeo': '#900000',
          'haas': '#FFFFFF',
          'alphatauri': '#2B4562',
        },
        'accent': {
          yellow: '#FF8700',   // Warning/caution color
          green: '#27F06D',    // Success color
          blue: '#0090FF',     // Info color
          purple: '#7B61FF',   // Alternative accent
        },
        'surface': {
          light: '#FFFFFF',
          dark: '#1F1F1F',
          card: '#FFFFFF',
          hover: '#F8F8F8',
        },
        'status': {
          success: '#00FF87',  // Green flag
          warning: '#FFF200',  // Yellow flag
          danger: '#FF0000',   // Red flag
          neutral: '#F8F8F8',  // White flag
        }
      },
      fontFamily: {
        'formula1': ['Titillium Web', 'sans-serif'],
        'display': ['Racing Sans One', 'cursive'],
        'body': ['Titillium Web', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'carbon-fiber': 'url("/carbon-fiber-pattern.png")',
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
    },
  },
  plugins: [],
}