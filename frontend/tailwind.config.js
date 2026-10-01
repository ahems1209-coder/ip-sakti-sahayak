/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: '#0F172A',     // Deep Slate Navy
          dark: '#1E293B',     // Dark Slate Border/Card
          blue: '#1E3A8A',     // Institutional Blue
          accent: '#D97706',   // Ashoka Saffron / Amber Accent
          emerald: '#059669',  // Verified Status Green
          crimson: '#DC2626',  // Abstention Warning Red
          slate: '#475569',    // Secondary Body Slate
          bg: '#F8FAFC',       // Clean Light Slate Background
          card: '#FFFFFF',     // Clean White Enterprise Card
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
