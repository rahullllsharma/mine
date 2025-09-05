// @ts-check
"use strict";

// eslint-disable-next-line @typescript-eslint/no-var-requires
const path = require("path");
// eslint-disable-next-line @typescript-eslint/no-var-requires
const fs = require("fs");
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { spawnSync } = require("child_process");

const TEMP_FILE = path.resolve("tmp-jest-preview-stylesheet.js");

/**
 * Parse and transform css into jest-preview
 *
 * While working with transformers, one must transpile the stylesheet with tailwind and postcss and inject to the
 * jest-preview. Due to the jest transformers nature, by only working synchronously, and postcss, that needs some async
 * plugins, we need to use the same workaround as found in the jest-preview source code.
 *
 * @borrows https://github.com/nvh95/jest-preview/blob/main/src/transform.ts#L273
 */
module.exports = {
  process(src) {
    // Create a temporarily script to parse from the css files found and create a stylesheet.
    fs.writeFileSync(
      TEMP_FILE,
      `
      const path = require('path')
        , fs = require('fs')
        , postcss = require('postcss')
        , postcssImport = require('postcss-import')
        , postcssUrl = require('postcss-url')
        , tailwind = require('tailwindcss')
        , autoprefixer = require('autoprefixer');

      const processor = postcss([
        postcssImport({
          resolve(id) {
            // this is the issue with "~@", not being caught by the original plugin
            if (/urbint/gi.test(id)) {
              const newPath = path.resolve("./node_modules", id.replace("~", ""));
              return newPath;
            }
            return id;
          },
        }),
        postcssUrl,
        tailwind,
        autoprefixer
        ]).process(${JSON.stringify(src)}).then(result => {
          // the processed stylesheet is outputted to the console
          console.log('css|||', result.css, '|||');
        })
      `
    );

    // This is the trick, it will spawn a brand new context, execute the script and wait for it to finish.
    // Postcss will execute the async plugins and output the result to the console.
    const output = spawnSync("node", [TEMP_FILE], { encoding: "utf-8" });

    // Manage exceptions
    fs.unlink(TEMP_FILE, error => {
      if (error) {
        throw error;
      }
    });

    if (output.stderr) {
      console.error(output.stderr);
    }

    if (output.error) {
      throw output.error;
    }

    // grab everything inside the `css|||<string>|||`
    const result = output.stdout
      .trim()
      .replace(
        /(.|\n)*?css\|\|\|((.|\n)*?)\|\|\|/gim,
        (_a, _b, stylesheet) => stylesheet
      );

    return {
      // Inject the parsed stylesheet
      code: `
        const styleContent = ${JSON.stringify(result)};
        const style = document.createElement("style");
        style.appendChild(document.createTextNode(styleContent));
        document.head.appendChild(style);
        module.exports = {};
        `,
    };
  },
};
