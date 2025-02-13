import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          DEFAULT: "#05C2DE", // Gologic cyan/blue
          hover: "#04afc8",
        },
        secondary: {
          DEFAULT: "#E64A2B", // Gologic orange/red
          hover: "#d13f23",
        },
        neutral: {
          DEFAULT: "#FFFFFF",
          50: "#F0F0F0",
          100: "#FFFFFF",
          200: "#FFFFFD",
          800: "#1A1A1A",
          900: "#000000",
        },
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)"],
        mono: ["var(--font-geist-mono)"],
      },
    },
  },
  plugins: [],
} satisfies Config;
