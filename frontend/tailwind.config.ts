import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Cascadia Code", "monospace"],
      },
      colors: {
        border: {
          DEFAULT: "#27272a",
          muted: "#18181b",
          hover: "#3f3f46",
        },
        bg: {
          primary: "#09090b",
          secondary: "#18181b",
          tertiary: "#27272a",
          elevated: "#3f3f46",
          card: "#18181b",
        },
        text: {
          primary: "#fafafa",
          secondary: "#a1a1aa",
          muted: "#71717a",
        },
        accent: {
          DEFAULT: "#6366f1",
          hover: "#818cf8",
          foreground: "#ffffff",
        },
        success: {
          DEFAULT: "#10b981",
          foreground: "#ffffff",
          muted: "rgba(16, 185, 129, 0.1)",
        },
        warning: {
          DEFAULT: "#f59e0b",
          foreground: "#ffffff",
          muted: "rgba(245, 158, 11, 0.1)",
        },
        danger: {
          DEFAULT: "#ef4444",
          foreground: "#ffffff",
          muted: "rgba(239, 68, 68, 0.1)",
        },
        info: {
          DEFAULT: "#3b82f6",
          foreground: "#ffffff",
          muted: "rgba(59, 130, 246, 0.1)",
        },
      },
      boxShadow: {
        glow: "0 0 20px rgba(99, 102, 241, 0.15)",
        "glow-sm": "0 0 10px rgba(99, 102, 241, 0.1)",
        card: "0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2)",
        "card-hover": "0 4px 6px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.2)",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "scale-in": "scaleIn 0.2s ease-out",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
      },
      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};

export default config;
