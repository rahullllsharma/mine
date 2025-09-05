/** @type {import('jest').Config} */
module.exports = {
  globalSetup: "./jest.global-setup.js",
  collectCoverageFrom: [
    "src/**/*.{js,jsx,ts,tsx}",
    "!src/**/*.stories.{jsx,tsx}",
    "!src/pages/**/*.{jsx,tsx}",
    "!**/*.config.js",
    "!**/*.d.ts",
    "!**/node_modules/**",
    "!**/src/utils/dev/**",
  ],
  moduleNameMapper: {
    // Handle image imports
    // https://jestjs.io/docs/webpack#handling-static-assets
    "^.+\\.(jpg|jpeg|png|gif|webp|svg)$": "<rootDir>/__mocks__/fileMock.js",

    // https://kulshekhar.github.io/ts-jest/docs/getting-started/paths-mapping/
    "^@/(.*)$": "<rootDir>/src/$1",

    // Handle CSS imports (with CSS modules)
    // https://jestjs.io/docs/webpack#mocking-css-modules
    "^.+\\.module\\.(css|sass|scss)$": "identity-obj-proxy",

    // Handle CSS imports (without CSS modules)
    "^.+\\.(css|sass|scss)$": "<rootDir>/__mocks__/styleMock.js",

    // Map the lodash-es to lodash module
    "lodash-es": "lodash",

    // This helps Jest handle JSON imports
    "\\.json$": "identity-obj-proxy",

    // Fix for ci-info module conflict
    "^ci-info$": "<rootDir>/__mocks__/ci-info.js",
  },
  snapshotSerializers: [
    "@emotion/jest/serializer" /* if needed other snapshotSerializers should go here */,
  ],
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  testMatch: [
    "**/__tests__/**/?(*.)+(spec|test).[jt]s?(x)",
    "**/?(*.)+(spec|test).[jt]s?(x)",
  ],
  testEnvironment: "jsdom",
  testPathIgnorePatterns: [
    "<rootDir>/node_modules/",
    "<rootDir>/.next/",
    "<rootDir>/cypress/",
  ],
  transform: {
    // Use babel-jest to transpile tests with the next/babel preset
    // https://jestjs.io/docs/configuration#transform-objectstring-pathtotransformer--pathtotransformer-object
    "^.+\\.(js|jsx|ts|tsx)$": [
      "@swc/jest",
      {
        jsc: {
          transform: {
            react: {
              runtime: "automatic",
            },
          },
        },
      },
    ],
    "\\.(gql|graphql)$": "<rootDir>/jest-transform-graphql.js",
  },
  transformIgnorePatterns: [
    "/node_modules/",
    "^.+\\.module\\.(css|sass|scss)$",
    "<rootDir>/node_modules/(?!lodash-es)",
    "<rootDir>/node_modules/(?!ci-info)",
  ],
  modulePathIgnorePatterns: ["playwright", "<rootDir>/.*/__mocks__"],
  testEnvironmentOptions: {
    browsers: ["chrome", "firefox", "safari"],
  },
  resolver: "./jest-resolver.js",
};
