import type { PlaywrightTestConfig } from "@playwright/test";
import { devices } from "@playwright/test";
import dotenv from "dotenv";

dotenv.config({
  path:
    process.env.TARGET_ENV === undefined
      ? `${__dirname}/support/config/.env.localhost`
      : `${__dirname}/support/config/.env.${process.env.TARGET_ENV}`,
});

const config: PlaywrightTestConfig = {
  testDir: "./playwright/tests/",
  outputDir: "./playwright/report/artifacts/",

  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,

  /* Timeout values See https://playwright.dev/docs/test-timeouts */
  expect: process.env.CI ? { timeout: 20 * 1000 } : { timeout: 10 * 1000 },

  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI
    ? [
        ["list"],
        ["html", { outputFolder: "./playwright/report/html/", open: "never" }],
        [
          "allure-playwright",
          {
            detail: true,
            outputFolder: "playwright/report/allure-results/",
            suiteTitle: false,
          },
        ],
      ]
    : [
        ["list"],
        [
          "html",
          { outputFolder: "./playwright/report/html/", open: "on-failure" },
        ],
      ],
  /* Resolving authentication */
  globalSetup: require.resolve("./playwright/global-setup"),
  /* Making sure that the session is being dropped */
  globalTeardown: require.resolve("./playwright/global-teardown"),
  /* Maximum number of slow tests is 5. The limit to consider a test slow is 30s. */
  reportSlowTests: { max: 5, threshold: 30000 },
  use: {
    storageState: "./playwright/data/storageState.json",
    baseURL: process.env.BASEURL || "http://localhost:3000/",
    extraHTTPHeaders: {
      Authorization: `Bearer ${process.env.API_TOKEN}`,
    },
    headless: true,
    viewport: { width: 1280, height: 720 },
    /* Uncomment to reduce test speed in headed mode */
    // launchOptions: {
    //   slowMo: 100,
    // },
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
    // {
    //   name: "iphone webkit",
    //   use: devices["iPhone 12"],
    // },
    // {
    //   name: "ipad webkit",
    //   use: devices["iPad (gen 6)"],
    // },
  ],
};
export default config;
