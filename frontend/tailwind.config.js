/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gv: {
          dark: '#08251B',
          primary: '#0F3E2E',
          secondary: '#1A5D44',
          accent: '#D49419',
          gold: '#EBB328',
          lightGold: '#FEF3C7',
          lightGreen: '#E8F5EE',
          surface: '#F8FAF9',
          border: '#D1E3D8'
        }
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'sans-serif'],
        display: ['Outfit', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 4px 20px -2px rgba(15, 62, 46, 0.08), 0 2px 6px -1px rgba(15, 62, 46, 0.04)',
        'card-hover': '0 10px 25px -3px rgba(15, 62, 46, 0.12), 0 4px 10px -2px rgba(15, 62, 46, 0.06)',
      }
    },
  },
  plugins: [],
}
