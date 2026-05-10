/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],

  safelist: [
    // Bubble background colors
    "bg-blue-500",
    "bg-green-500",
    "bg-orange-500",
    "bg-red-500",
    "bg-purple-500",

    // Bubble text colors
    "text-blue-900",
    "text-green-900",
    "text-orange-900",
    "text-red-900",
    "text-purple-900",

    // Bubble border colors
    "border-blue-200",
    "border-green-200",
    "border-orange-200",
    "border-red-200",
    "border-purple-200",
  ],

  theme: {
    extend: {
      colors: {
        primary: '#AA3BFF',
        'primary-light': '#F3E8FF',
        secondary: '#3B82F6',
        'secondary-light': '#E0F2FE',
        accent: '#FF6BCE',
        'accent-light': '#FFE4F5',
        success: '#22C55E',
        warning: '#FACC15',
        danger: '#EF4444',
        neutral: '#F8FAFC',
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
        '2xl': '32px',
        '3xl': '48px',
      },
      borderRadius: {
        'sm': '6px',
        'md': '12px',
        'lg': '18px',
        'xl': '24px',
        '2xl': '32px',
      },
      fontSize: {
        base: '16px',
      },
      lineHeight: {
        base: '1.6',
      },
    },
  },

  plugins: [],
}
