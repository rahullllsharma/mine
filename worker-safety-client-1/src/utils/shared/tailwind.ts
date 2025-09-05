// TODO research next.js tailwind resolve support
// blog for doing preval with craco/babel: https://marabesi.com/web/2021/10/31/sharing-tailwind-config-elsewhere-for-variable-access.html
// tailwind docs recommend using preval: https://tailwindcss.com/docs/configuration#referencing-in-java-script
// babel-preval plugin: https://github.com/kentcdodds/babel-plugin-preval
// next-preval plugin: https://github.com/ricokahler/next-plugin-preval
// next + babel?: https://nextjs.org/docs/advanced-features/customizing-babel-config

// import resolveConfig from "tailwindcss/resolveConfig";
// import tailwindConfig from "tailwind.config.js";
// export const fullConfig = resolveConfig(tailwindConfig);

// duplicated from the tailwind.config.js for now
export const fullConfig = {
  theme: {
    colors: {
      brand: {
        urbint: {
          10: "#F0FBFE",
          20: "#C8EEF9",
          30: "#61B9D1",
          40: "#00A0CC",
          50: "#007899",
          60: "#003F53",
        },
        gray: {
          10: "#F7F8F8",
        },
      },
      data: {
        teal: {
          30: "#088574",
          40: "#1C7D72",
        },
        purple: {
          10: "#E4E0FF",
          20: "#C4BCF5",
          30: "#705FE3",
          40: "#4F3EBB",
          50: "#2B1F7A",
          60: "#1D1452",
        },
      },
      risk: {
        high: "#D44242",
        medium: "#EEBF13",
        low: "#238914",
        unknown: "rgba(4, 30, 37, 0.07)",
        recalculating: "rgba(4, 30, 37, 0.07)",
        hover: {
          high: "#A82424",
          medium: "#753E0A",
          low: "#295E21",
        },
      },
      neutral: {
        shade: {
          100: "#041E25",
          75: "rgba(4, 30, 37, 0.75)",
          58: "rgba(4, 30, 37, 0.58)",
          38: "rgba(4, 30, 37, 0.38)",
          26: "rgba(4, 30, 37, 0.26)",
          18: "rgba(4, 30, 37, 0.18)",
          7: "rgba(4, 30, 37, 0.07)",
          3: "rgba(4, 30, 37, 0.03)",
        },
      },
    },
  },
};

/**
 * Return a color from the tailwind config.
 *
 */
// a helper for pulling a color off the typescript config
// TODO it'd be nice to support a path, like `"risk.high-hover"` or `"data.teal.40"`
export function getColor(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  toColor: (colors: any) => string | undefined
): string | undefined {
  return toColor(fullConfig.theme.colors);
}
