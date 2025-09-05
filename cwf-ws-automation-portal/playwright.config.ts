import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testMatch: ["test/**/*.test.ts"],
  timeout: 500000,
  retries: 1,
  maxFailures: 12,
  workers: 10,
  globalSetup: require.resolve("./Util/global-setup"), // Global setup for persistent context if required
  use: {
    headless: true,
    screenshot: "on",
    video: "retain-on-failure",
    trace: "retain-on-failure",
    actionTimeout: 200000,
    navigationTimeout: 200000,
    permissions: ["geolocation"],
    geolocation: { latitude: 36.2274, longitude: -83.0098 },
  },
  expect: {
    timeout: 250000,
  },
  projects: [
    {
      name: "Desktop Chrome",
      use: {
        browserName: "chromium",
        viewport: { width: 1200, height: 800 },
        launchOptions: {
          args: [
            "--start-maximized",
            "--remote-debugging-port=9222",
            "--window-size=1920,1080",
            "--disable-gpu",
          ],
          slowMo: 30,
        },
      },
    },
    {
      name: "Desktop Edge",
      use: {
        browserName: "chromium",
        channel: "msedge",
        viewport: null,
        launchOptions: {
          args: ["--start-maximized", "--window-size=1920,1080"],
          slowMo: 30,
        },
      },
    },
    // iPad Mini
    {
      name: "iPad Mini",
      use: {
        ...devices["iPad Mini"],
      },
    },

    // {
    //   name: "Mobile Chrome",
    //   use: {
    //    ...devices["iPhone 14 Pro Max"],
    //     viewport: { width: 430, height: 932 },
    //    launchOptions: {
    //      args: ["--remote-debugging-port=9222"],
    //    },
    //   },
    //   },
    //   {
    //     name: "Ipad Chrome",
    //     use: {
    //       browserName: "webkit",
    //      ...devices["iPad Pro 11"],
    //       viewport: { width: 1024, height: 1366 },
    //      launchOptions: {
    //        args: ["--remote-debugging-port=9222"],
    //      },
    //     },
    //     },
    //     {
    //       name: 'Google Chrome',
    //       use: { ...devices['Desktop Chrome'], channel: 'chrome' }, // or 'chrome-beta'
    //     },
  ],

  reporter: [
    ["list"], // Output in the terminal
    ["allure-playwright"], // Allure report generation
  ],
  outputDir: "test-results", // Store all results like logs, screenshots, etc.
});
