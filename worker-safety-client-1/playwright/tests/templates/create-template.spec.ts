import { faker } from "@faker-js/faker";
import { test } from "../../framework/base-fixtures";

let templateName;

test.beforeAll(async ({ browserName }, testInfo) => {
  console.log(
    `Lauching ${browserName} browser to run "${testInfo.title}" test on worker ${testInfo.workerIndex}`
  );
  templateName =
    `Automation dummy template ${browserName} ` + faker.datatype.number();
});

test.beforeEach(async ({ page, homePage }, testInfo) => {
  console.log(
    `Started "${testInfo.title}" test on worker ${testInfo.workerIndex}`
  );
  // Navigate to the home page set as baseURL under playwright.config.ts
  await page.goto("/");
  // Navigate to the templates page
  await homePage.openTemplatesPage();
});
test.afterEach(async ({ page }, testInfo) => {
  console.log(
    `Ended "${testInfo.title}" test with status=${testInfo.status} on worker ${testInfo.workerIndex}`
  );
  if (testInfo.status !== testInfo.expectedStatus)
    console.log(`Test did not run as expected, ended up at ${page.url()}`);
});

// Creates a project and deletes it afterwards
test.describe("Create Template @smoke", () => {
  test("Templates page is displayed", async ({ templatesPage }) => {
    // Check if it is on templates page
    await templatesPage.isOnPage();
  });

  test("Create Template displays a blank page", async ({
    templatesPage,
    templatePage,
  }) => {
    // Navigate to the new template page
    await templatesPage.createTemplate();

    // Check if it is on blank template page
    await templatePage.isBlankPage();
  });

  test("Able to enter Template title name", async ({
    templatesPage,
    templatePage,
  }) => {
    // Navigate to the new template page
    await templatesPage.createTemplate();

    // Fill Template Name
    await templatePage.fillTemplateName(templateName);
  });

  test("Able to update Template title name", async ({
    templatesPage,
    templatePage,
  }) => {
    // Navigate to the new template page
    await templatesPage.createTemplate();

    // Fill Template Name
    await templatePage.fillTemplateName(templateName);

    // Update Template Name
    await templatePage.updateTemplateName(templateName);
  });

  test("Able to clear Template title name", async ({
    templatesPage,
    templatePage,
  }) => {
    // Navigate to the new template page
    await templatesPage.createTemplate();

    // Fill Template Name
    await templatePage.fillTemplateName(templateName);

    // Update Template Name
    await templatePage.clearTemplateName();
  });
});
