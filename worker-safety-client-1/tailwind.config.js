// eslint-disable-next-line @typescript-eslint/no-var-requires
const silicaTheme = require("@urbint/silica/tailwind-preset");

// eslint-disable-next-line @typescript-eslint/no-var-requires
const sillicaThemev2 = require("@urbint/silica/tailwind-preset-v2");

module.exports = {
  mode: "jit",
  purge: {
    enabled: false,
    // Include WS components and silica components as needed. Otherwise they will be purged.
    content: [
      "./src/(components|container|pages|utils)/**/*.{js,jsx,ts,tsx}",
      "./node_modules/@urbint/silica/dist/index.esm.js",
      "./node_modules/@urbint/silica/dist/index.js",
    ],
  },
  darkMode: false, // or 'media' or 'class'
  presets: [silicaTheme, sillicaThemev2],
  theme: {
    extend: {
      fontFamily: {
        inter: ["Inter"],
      },
      screens: {
        "tab-md": "890px",
      },
      colors: {
        risk: {
          high: silicaTheme.theme.extend.colors.data.red["30"],
          medium: silicaTheme.theme.extend.colors.data.yellow["30"],
          low: silicaTheme.theme.extend.colors.data.green["30"],
          unknown: silicaTheme.theme.extend.colors.neutral.shade["7"],
          recalculating: silicaTheme.theme.extend.colors.neutral.shade["7"],
          hover: {
            high: silicaTheme.theme.extend.colors.data.red["40"],
            medium: silicaTheme.theme.extend.colors.data.yellow["50"],
            low: silicaTheme.theme.extend.colors.data.green["50"],
          },
        },
      },
      opacity: {
        38: "0.38",
      },
      spacing: {
        // TODO: investigate how to reuse spacing e.g.: p-2-5 = 10px
        ["2.5"]: "0.625rem",
        102: "26rem",
      },
      gridTemplateColumns: {
        // home page list card specific column configuration
        "auto-fill-list-card": "repeat(auto-fill, minmax(330px, 1fr))",
        "auto-fit-list-card": "repeat(auto-fit, minmax(0, 1fr))",
        "2-auto-expand": "auto 1fr",
      },
      gridTemplateRows: {
        "2-auto-expand": "minmax(0, auto) minmax(0, 1fr)",
      },
      gridAutoRows: {
        "2-auto-expand": "auto 1fr",
      },
      borderWidth: {
        10: "10px",
      },
      width: {
        78: "18.75rem",
        88: "22rem",
        fit: "fit-content", //Tailwind 2 doesn't support fit-content.
      },
      height: {
        160: "40rem",
      },
    },
  },
  variants: {
    extend: {
      borderStyle: ["first"],
      borderWidth: ["first"],
      margin: ["first"],
      opacity: ["disabled"],
      backgroundColor: ["active", "checked"],
      borderColor: ["checked"],
      cursor: ["disabled", "read-only"],
    },
  },
  plugins: [require("@tailwindcss/line-clamp")],
};
