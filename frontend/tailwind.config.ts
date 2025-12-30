import type { Config } from 'tailwindcss';

export default {
  content: [
    './apps/**/src/**/*.{ts,tsx}',
    './libs/**/src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Celonis-inspired primary blue (updated to match reference)
        primary: {
          DEFAULT: '#0066FF',
          50: '#E8F2FF',
          100: '#C2DBFF',
          200: '#99C2FF',
          300: '#66A3FF',
          400: '#3385FF',
          500: '#0066FF',
          600: '#0052CC',
          700: '#003D99',
          800: '#002966',
          900: '#001433',
        },
        // Semantic colors
        success: {
          DEFAULT: '#36B37E',
          light: '#E3FCEF',
        },
        warning: {
          DEFAULT: '#FAAD14',
          light: '#FFFBE6',
        },
        error: {
          DEFAULT: '#DE350B',
          light: '#FFEBE6',
        },
        // Neutral palette
        neutral: {
          50: '#FAFBFC',
          100: '#F4F5F7',
          200: '#EBECF0',
          300: '#DFE1E6',
          400: '#C1C7D0',
          500: '#97A0AF',
          600: '#5E6C84',
          700: '#42526E',
          800: '#172B4D',
          900: '#091E42',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      // Compact/high-density spacing (8-12-16px scale)
      spacing: {
        '0.5': '2px',
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
      },
      // 6px border radius default (softer per reference)
      borderRadius: {
        none: '0',
        sm: '4px',
        DEFAULT: '6px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        '2xl': '20px',
        full: '9999px',
      },
      fontSize: {
        xs: ['11px', { lineHeight: '16px' }],
        sm: ['12px', { lineHeight: '18px' }],
        base: ['14px', { lineHeight: '22px' }],
        lg: ['16px', { lineHeight: '24px' }],
        xl: ['18px', { lineHeight: '28px' }],
        '2xl': ['20px', { lineHeight: '28px' }],
        '3xl': ['24px', { lineHeight: '32px' }],
        '4xl': ['30px', { lineHeight: '36px' }],
      },
      boxShadow: {
        sm: '0 1px 2px rgba(9, 30, 66, 0.08)',
        DEFAULT: '0 1px 3px rgba(9, 30, 66, 0.1), 0 1px 2px rgba(9, 30, 66, 0.08)',
        md: '0 4px 6px rgba(9, 30, 66, 0.08), 0 2px 4px rgba(9, 30, 66, 0.06)',
        lg: '0 8px 16px rgba(9, 30, 66, 0.1), 0 4px 8px rgba(9, 30, 66, 0.08)',
        xl: '0 16px 24px rgba(9, 30, 66, 0.12), 0 8px 16px rgba(9, 30, 66, 0.08)',
      },
    },
  },
  plugins: [],
} satisfies Config;
