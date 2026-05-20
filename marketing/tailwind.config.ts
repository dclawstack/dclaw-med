import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Warm red-orange to match the clinician app's primary
        // (frontend globals.css: --primary: oklch(0.63 0.21 25)).
        brand: {
          50:  "#FFF4F0",
          100: "#FDE3D6",
          200: "#F9C3A6",
          300: "#F39A77",
          400: "#EC6E48",
          500: "#DD5532",   // gradient end (lighter)
          600: "#CB4524",
          700: "#DA5138",   // PRIMARY — matches app oklch(0.63 0.21 25)
          800: "#A03517",   // hover / press / gradient start (darker)
          900: "#70240F",
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
        brand: "0 12px 28px rgba(218, 81, 56, 0.28)",
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
