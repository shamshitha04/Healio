/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        clinic: {
          cream: "#fffbeb",
          mint: "#a7f3d0",
          sky: "#bae6fd",
          peach: "#fda4af",
          alert: "#f87171",
          ink: "#334155",
        },
      },
      fontFamily: {
        rounded: ["Nunito", "Quicksand", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [],
};

