import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        serif: ["var(--font-playfair)", "Georgia", "serif"],
      },
      colors: {
        brand: {
          DEFAULT: "#E23744",
          hover: "#CB2F3B",
        },
        rating: {
          DEFAULT: "#2E9E5B",
        },
        surface: {
          bg: "#F6F7FB",
          card: "#FFFFFF",
          muted: "#F4F6F8",
        },
        ink: {
          primary: "#1A1A2E",
          secondary: "#555555",
        },
        error: {
          DEFAULT: "#C0392B",
          bg: "#FFF0F0",
          border: "#F0B8B8",
        },
        notice: {
          info: { bg: "#EEF6FF", border: "#B8D4F0" },
          warn: { bg: "#FFF8E6", border: "#F0D78C", text: "#7A5C00" },
        },
      },
      boxShadow: {
        card: "0 4px 24px rgba(0, 0, 0, 0.08)",
      },
      maxWidth: {
        content: "720px",
      },
    },
  },
  plugins: [],
};

export default config;
