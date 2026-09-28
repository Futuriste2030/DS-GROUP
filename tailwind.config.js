/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static_src/js/**/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        grotesk: ['Space Grotesk', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        orange: {
          50: '#faf6e9',
          100: '#f3e9c8',
          500: '#c9a227',
        },
        marine: {
          DEFAULT: '#12314f',
          profond: '#0b1f35',
          clair: '#1e4569',
        },
        orbs: {
          DEFAULT: '#c9a227',
          clair: '#d9bc6b',
          voile: 'rgba(201,162,39,.12)',
        },
        grisbs: {
          100: '#f5f6f9',
          300: '#d6dbe4',
          500: '#6c7891',
          700: '#39485e',
        },
      },
    },
  },
  plugins: [],
}