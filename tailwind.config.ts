import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          blue: "#3B82D4",
          purple: "#7C5CD8",
          "dark-blue": "#1E3A6E",
          "near-black": "#0D0F14",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
      backgroundImage: {
        "hero-gradient":
          "radial-gradient(ellipse at 60% 0%, rgba(59,130,212,0.15) 0%, transparent 60%), radial-gradient(ellipse at 20% 80%, rgba(124,92,216,0.12) 0%, transparent 55%)",
        "cta-gradient": "linear-gradient(135deg, #1E3A6E 0%, #3B1F7C 100%)",
      },
      animation: {
        float: "float 4s ease-in-out infinite",
        "count-up": "countUp 0.6s ease-out forwards",
        marquee: "marquee 30s linear infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        marquee: {
          "0%": { transform: "translateX(0%)" },
          "100%": { transform: "translateX(-50%)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
