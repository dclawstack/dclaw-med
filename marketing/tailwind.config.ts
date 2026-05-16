import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // DKube brand palette from /colors_and_type.css
        brand: {
          900: "#4A3878",
          800: "#5C4A8E",
          700: "#7660A8", // primary
          600: "#8773B5",
          500: "#9384BD",
          400: "#B0A4CE",
          300: "#C9C0DE",
          200: "#E2DCEE",
          100: "#F1EEF8",
          50: "#F8F6FB",
        },
        ink: "#0F0F12",
        body: "#404049",
        meta: "#5A5A66",
      },
      fontFamily: {
        sans: [
          "Poppins",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "ui-monospace",
          "SF Mono",
          "Menlo",
          "Consolas",
          "Liberation Mono",
          "monospace",
        ],
      },
      maxWidth: {
        container: "1280px",
      },
      boxShadow: {
        brand: "0 12px 28px rgba(118, 96, 168, 0.28)",
        soft: "0 8px 20px rgba(15, 15, 18, 0.08)",
        card: "0 2px 6px rgba(15, 15, 18, 0.06)",
      },
      borderRadius: {
        pill: "999px",
      },
    },
  },
  plugins: [],
};

export default config;
