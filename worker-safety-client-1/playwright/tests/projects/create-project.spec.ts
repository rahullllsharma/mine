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

// Creates a project and deletes it afterwards
test.describe("Projects @smoke", () => {
  test("Create project", async ({
    page,
    homePage,
    projectPage,
    prepareProjectDataAPIPage,
  }) => {
    console.log(`Creating "${projectName}" project`);

    // Navigate to the home page set as baseURL under playwright.config.ts
    await page.goto("/");

    await homePage.userIsHomePage();
    await homePage.addProject();
    await projectPage.createProject(projectName);
    await homePage.projectCreated();
    await prepareProjectDataAPIPage.getProject(projectName);
    await prepareProjectDataAPIPage.mutationDeleteProjectsByIds(
      prepareProjectDataAPIPage.projectsIds
    );
  });
});
