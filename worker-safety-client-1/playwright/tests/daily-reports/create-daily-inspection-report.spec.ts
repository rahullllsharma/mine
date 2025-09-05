import { test } from "../../framework/base-fixtures";

test.beforeAll(async ({ browserName }, testInfo) => {
  console.log(
    `Lauching ${browserName} browser to run "${testInfo.title}" test on worker ${testInfo.workerIndex}`
  );
});

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

test.describe("Daily Reports @smoke", () => {
  test("Create daily inspection report", async ({
    page,
    dailyReportPage,
    homePage,
    createProjectAPIPage,
  }) => {
    console.log("Creating Daily Inspection Report");

    // Navigate to the home page set as baseURL under playwright.config.ts
    await page.goto("/");

    // Navigate to Project Summary page
    await homePage.openProjectSummaryPage(createProjectAPIPage.projectName);

    // Press Add report
    await dailyReportPage.pressAddReport();

    // Create Daily Report
    await dailyReportPage.createDailyReport();

    // Confirm tha the report has been created
    await dailyReportPage.confirmReportCreated();

    // Delete Project
    await createProjectAPIPage.mutationDeleteProjectsByIds(
      createProjectAPIPage.projectsIds
    );
  });
});
