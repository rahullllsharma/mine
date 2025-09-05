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

test.describe.configure({ mode: "serial" });

// Login
test.describe("Authentication @auth @smoke", () => {
  // Empty storageState.json to make sure user is logged out
  // TODO: review after fix https://github.com/microsoft/playwright/issues/15977
  // test.use({ storageState: undefined });
  test.use({ storageState: "playwright/data/emptyStorageState.json" });
  test("Login and Logout", async ({
    page,
    loginPage,
    homePage,
    logoutPage,
  }) => {
    // Navigate to the home page set as baseURL under playwright.config.ts
    await page.goto("/");

    await loginPage.login(process.env.PW_USERNAME, process.env.PW_PASSWORD);
    await homePage.userIsHomePage();
    await homePage.logout();
    await logoutPage.userIsLoggedOut();
  });
  test("User can't login with invalid credentials", async ({
    page,
    loginPage,
    logoutPage,
  }) => {
    // Navigate to the home page set as baseURL under playwright.config.ts
    await page.goto("/");

    await loginPage.login("wrong", "password");
    await loginPage.wrongCredentialsValidation();
    await logoutPage.userIsLoggedOut();
  });
});
