import { faker } from "@faker-js/faker";
import { test } from "../../framework/base-fixtures";

let projectName;

test.beforeAll(async ({ browserName }, testInfo) => {
  console.log(
    `Lauching ${browserName} browser to run "${testInfo.title}" test on worker ${testInfo.workerIndex}`
  );
  projectName =
    `Automation dummy project ${browserName} ` + faker.datatype.number();
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

// Creates a project and deletes it afterwards
test.describe("Projects @smoke", () => {
  test("Consult project", async ({ page, homePage, createProjectAPIPage }) => {
    console.log(`Consulting "${projectName}" project`);

    // Navigate to the home page set as baseURL under playwright.config.ts
    await page.goto("/");

    // Navigate to Project Summary page
    await homePage.openProjectSummaryPage(createProjectAPIPage.projectName);

    // Delete Project
    await createProjectAPIPage.mutationDeleteProjectsByIds(
      createProjectAPIPage.projectsIds
    );
  });
});
