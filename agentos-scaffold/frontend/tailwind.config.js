/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // TODO: tune this palette during the real design pass — these are
        // functional placeholders only, per the "minimal animations /
        // no business logic yet" scaffold rule.
        background: "#0B0F19",
        surface: "#111827",
        accent: "#6366F1",
      },
    },
  },
  plugins: [],
};
