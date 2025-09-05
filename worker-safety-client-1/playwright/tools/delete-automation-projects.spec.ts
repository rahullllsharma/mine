import { test } from "../framework/base-fixtures";

// Variables
let projectNamePrefix;

test.beforeAll(async ({ browserName }, testInfo) => {
  console.log(
    `Lauching ${browserName} browser to run "${testInfo.title}" test on worker ${testInfo.workerIndex}`
  );
  projectNamePrefix = `Automation dummy project `;
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

test.describe.skip("Delete Projects @noTest", () => {
  test("Delete all projects", async ({
    page,
    homePage,
    projectSettingsPage,
  }) => {
    // Navigate to the home page set as baseURL under playwright.config.ts
    await page.goto("/");

    // Make sure user starts from Home Page
    await homePage.userIsHomePage();

    // Collect all the projects starting with "Automation dummy project"
    const automationProjectList = await homePage.getProjectsByPattern(
      projectNamePrefix
    );
    console.log("Projects to be deleted = ", automationProjectList.length);

    // Delete automationProjectList projects
    console.log("Delete Project List = ", automationProjectList);
    for (const autoProjectName of automationProjectList) {
      console.log("Delete Project ", autoProjectName);

      // Make sure user starts from Home Page
      await homePage.userIsHomePage();
      await homePage.openProjectSummaryPage(autoProjectName);
      await projectSettingsPage.openProjectSettings(autoProjectName);
      await projectSettingsPage.deleteProject(autoProjectName);
      await homePage.projectDeleted();
    }
  });
});
