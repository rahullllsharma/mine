/**
 * This is in progress config file, so it's very likely that something is missing, since we've only tested with one suite
 * If something is missing or incorrect, please extend the configuration.
 */

// eslint-disable-next-line @typescript-eslint/no-var-requires
const nextJest = require("next/jest");
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { configureNextJestPreview } = require("jest-preview");

/** @type {import('next/jest')} */
const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  // dir: "./../../"
});

/** @type {import('jest').Config} */
const customJestConfig = {
  rootDir: "./../",
  verbose: true,
  globalSetup: "<rootDir>/jest.global-setup.js",
  moduleNameMapper: {
    // https://kulshekhar.github.io/ts-jest/docs/getting-started/paths-mapping/
    "^@/(.*)$": "<rootDir>/src/$1",

    // Map the lodash-es to lodash module
    "lodash-es": "lodash",
  },
  resolver: "<rootDir>/jest-resolver.js",
  setupFilesAfterEnv: ["<rootDir>/jest-preview/jest.setup.js"],
  moduleDirectories: ["node_modules", "<rootDir>/"],
  transform: {
    "\\.module\\.(css|sass|scss)$":
      "<rootDir>/jest-preview/transforms/jest.transform.css.js",
    "\\.(css|scss|sass|less)$":
      "<rootDir>/jest-preview/transforms/jest.transform.css.js",
    "\\.(gql|graphql)$": "<rootDir>/jest-transform-graphql.js",
  },
  transformIgnorePatterns: ["<rootDir>/node_modules/(?!lodash-es)"],
  testEnvironment: "jsdom",
};

// NOTE: `configureNextJestPreview` accepts the final configuration for Jest.
// Modifying its return value before exporting might break `jest-preview`.
module.exports = configureNextJestPreview(createJestConfig(customJestConfig));
