import type { Config } from "tailwindcss";
import colors from "tailwindcss/colors";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0b1220",
        muted: "#718096",
        line: "#e4e9f0",
        surface: "#f5f7fb",
        blue: {
          ...colors.blue,
          DEFAULT: "#246bfd",
        },
        cyan: {
          ...colors.cyan,
          DEFAULT: "#16c1c8",
        },
      },
    },
  },
  plugins: [],
};

export default config;
