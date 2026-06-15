/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0B6E6E',
          dark: '#085858',
          light: '#E6F2F2',
        },
        accent: '#E07A5F',
        surface: '#FFFFFF',
        bg: '#F7F5F2',
        muted: '#64748B',
        border: '#E2E8F0',
        text: '#334155',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
