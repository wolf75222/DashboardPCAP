/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      "./templates/**/*.html",
      "./templates/layouts/**/*.html",
      "./templates/charts/**/*.html",
      "./static/src/**/*.js",
      "./node_modules/flowbite/**/*.js",
  ],
  theme: {
      extend: {},
  },
  plugins: [
      require("flowbite/plugin")({
          charts: true,
      }),
  ],
};
