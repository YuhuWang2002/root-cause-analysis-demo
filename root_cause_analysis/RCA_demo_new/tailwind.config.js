/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0D7377',
          light: '#14A3A8',
          dark: '#095456',
        },
        accent: {
          DEFAULT: '#FF6B35',
          light: '#FF8F66',
          dark: '#E55520',
        },
        success: '#36B37E',
        warning: '#FFAB00',
        error: '#FF5630',
        info: '#4C9AFF',
        node: {
          data: '#6554C0',
          process: '#00B8D9',
          analysis: '#FF991F',
          result: '#36B37E',
        },
      },
      fontFamily: {
        display: ['Noto Serif SC', 'Source Han Serif SC', 'serif'],
        body: ['Noto Sans SC', 'Source Han Sans SC', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'card': '0 2px 8px rgba(26, 29, 33, 0.08), 0 4px 16px rgba(26, 29, 33, 0.04)',
        'card-hover': '0 8px 24px rgba(26, 29, 33, 0.12), 0 16px 48px rgba(26, 29, 33, 0.08)',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
    },
  },
  plugins: [],
}
