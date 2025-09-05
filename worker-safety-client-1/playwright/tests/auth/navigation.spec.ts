import { test } from "../../framework/base-fixtures";

test.beforeEach(async ({}, testInfo) => {
  console.log(
    `Started "${testInfo.title}" test on worker ${testInfo.workerIndex}`
  );
});
test.afterEach(async ({ page }, testInfo) => {
  console.log(
    `Ended "${testInfo.title}" test with status=${testInfo.status} on worker ${testInfo.workerIndex}`
  );
  if (testInfo.status !== testInfo.expectedStatus)
    console.log(`Test did not run as expected, ended up at ${page.url()}`);
});

// Navigation
test.describe("Navigation @smoke", () => {
  // User is able to navigate to the tabs available for his specific role
  test("Navigate between tabs", async ({ page, homePage, isMobile }) => {
    // Navigate to the home page set as baseURL under playwright.config.ts
    await page.goto("/");
    // Skip this test for Mobile
    test.fixme(isMobile, "Tabs aren't supported for mobile");
    await homePage.userIsHomePage();
    await homePage.tabsAvailable();
  });
});
