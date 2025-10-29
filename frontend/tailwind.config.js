/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        // existing palette
        primary: '#F9F5F0',   // cream background
        secondary: '#F2EAD3', // soft beige (optional cards)
        accent: '#F4991A',    // dark green (text)
        highlight: '#F4991A', // warm amber highlight

        // your new brand palette
        brand: {
          dark: '#3A3845',
          light: '#F7CCAC',
          medium: '#C69B7B',
          soft: '#826F66',
        },
      },
      boxShadow: {
        soft: '0 4px 12px rgba(0,0,0,0.08)',
        glow: '0 0 20px rgba(244, 153, 26, 0.25)',
      },
    },
  },
  plugins: [],
};
