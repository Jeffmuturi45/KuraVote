/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './election/**/*.py',
    './static/**/*.js',
  ],

  theme: {
    extend: {

      // ── KuraVote Color Palette ─────────────────────────
      colors: {
        primary: {
          50:  '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',   // --primary-light
          700: '#15803d',
          800: '#166534',   // --primary
          900: '#14532d',   // sidebar dark
          950: '#052e16',
        },
        accent: {
          300: '#fde68a',
          400: '#fbbf24',
          500: '#eab308',   // --accent
          600: '#ca8a04',
        },
        kura: {
          bg:     '#f0fdf4',
          card:   '#ffffff',
          border: '#d1fae5',
          muted:  '#64748b',
          text:   '#1e293b',
        }
      },

      // ── KuraVote Fonts ─────────────────────────────────
      fontFamily: {
        sans:    ['DM Sans', 'sans-serif'],
        heading: ['Sora', 'sans-serif'],
      },

      // ── Border Radius ──────────────────────────────────
      borderRadius: {
        'kura': '14px',
        'kura-sm': '10px',
        'kura-lg': '16px',
      },

      // ── Box Shadows ────────────────────────────────────
      boxShadow: {
        'kura': '0 4px 24px rgba(22, 163, 74, 0.06)',
        'kura-md': '0 8px 32px rgba(22, 163, 74, 0.10)',
      },

      // ── Sidebar width ──────────────────────────────────
      width: {
        'sidebar': '235px',
      },

      // ── Animations ────────────────────────────────────
      keyframes: {
        pulse_kura: {
          '0%, 100%': { opacity: '1' },
          '50%':       { opacity: '0.4' },
        },
        fadeIn: {
          'from': { opacity: '0', transform: 'translateY(8px)' },
          'to':   { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          'from': { transform: 'translateY(100%)', opacity: '0' },
          'to':   { transform: 'translateY(0)',    opacity: '1' },
        },
      },
      animation: {
        'pulse-kura': 'pulse_kura 1.5s infinite',
        'fade-in':    'fadeIn 0.3s ease',
        'slide-up':   'slideUp 0.3s ease',
      },

    },
  },

  plugins: [
    require('@tailwindcss/forms'),
  ],
}