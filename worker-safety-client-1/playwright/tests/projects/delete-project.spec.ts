import { test } from "../../framework/base-fixtures";

test.beforeAll(async ({ browserName }, testInfo) => {
  console.log(
    `Lauching ${browserName} browser to run "${testInfo.title}" test on worker ${testInfo.workerIndex}`
  );
});

test.beforeEach(async ({ isMobile }, testInfo) => {
  console.log(
    `Started "${testInfo.title}" test on worker ${testInfo.workerIndex}`
  );
  // Skip this test for Mobile
  test.fixme(isMobile, "Add project is not supported for mobile");
});
test.afterEach(async ({ page }, testInfo) => {
  console.log(
    `Ended "${testInfo.title}" test with status=${testInfo.status} on worker ${testInfo.workerIndex}`
  );
  if (testInfo.status !== testInfo.expectedStatus)
    console.log(`Test did not run as expected, ended up at ${page.url()}`);
});

test.describe("Delete Project @smoke", () => {
  test("Delete project", async ({
    page,
    createProjectAPIPage,
    homePage,
    projectSettingsPage,
  }) => {
    console.log(`Deleting "${createProjectAPIPage.projectName}" project`);

    // Navigate to the home page set as baseURL under playwright.config.ts
    await page.goto("/");

    await homePage.openProjectSummaryPage(createProjectAPIPage.projectName);
    await projectSettingsPage.openProjectSettings(
      createProjectAPIPage.projectName
    );
    await projectSettingsPage.deleteProject(createProjectAPIPage.projectName);
    await homePage.projectDeleted();
  });
});
