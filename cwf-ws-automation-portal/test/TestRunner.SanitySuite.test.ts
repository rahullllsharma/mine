import os from "os";
import { test, BrowserContext, Page, chromium } from "@playwright/test";
import TestBase from "../Util/TestBase";
import HomePage from "../Page/Home.page";
import LoginPage from "../Page/Login.page";
import CWFPage from "../Page/cwf.page";
import * as path from "path";
import { setProjectName } from "../Util/TestBase";
import { expect } from "@playwright/test";
import * as cred from "../Data/local.cred.json";
import * as cwfInterfaces from "../types/interfaces";

const fs = require("fs").promises;
const fsSync = require("fs");

// Test Suite 1 - CWF Portal Workflow
test.describe.parallel("CWF Portal workFlow", { tag: "@cwf" }, () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let cwfpage: CWFPage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/cwf-template-form-validation",
      },
      viewport: {
        width: 1200,
        height: 800,
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    cwfpage = new CWFPage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(5000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test(
    "CWF Template Form Rendering Validation, Saved Form Validation and View Form Validation",
    { tag: "@regression" },
    async () => {
      //add
      await homepage.waitForHomePageLoad();
      await cwfpage.captureFormResponse(
        cred.templateID,
        "cwfTemplates",
        "cwfFormsPost"
      );
      await cwfpage.validateAllPagesInJSON();
      //view
      // try {
      //   await cwfpage.validateSavedFormInList();
      //   await cwfpage.viewValidateAllPagesInJSON();
      // } catch (error) {
      //   console.error("Error during Saved Form Validation:", error);
      //   throw error;
      // }
    }
  );

  // test.skip("Validate Updating Report date and time Component", async () => {
  //   await cwfpage.captureFormResponse(
  //     cred.templateID,
  //     "cwfForms",
  //     "cwfFormsPost"
  //   );
  //   await cwfpage.validateAllPagesInJSON();
  //   await cwfpage.updateReportDateComponentfromCalender();
  // });
});

// Test Suite 2 - Template Forms Filter Tests
test.describe.parallel("Template Forms Filter Tests", { tag: "@cwf" }, () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let cwfpage: CWFPage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/template-form-filter",
      },
      viewport: {
        width: 1200,
        height: 800,
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    cwfpage = new CWFPage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(5000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test(
    "Validate Template Forms Filter Functionality",
    { tag: "@filter" },
    async () => {
      // Navigate to template forms page
      await homepage.waitForHomePageLoad();
      await homepage.navigateToTemplateFormsTab();
      await page.waitForTimeout(5000);

      //Verify Search Input box functionality
      // await cwfpage.validateTemplateFormSearchFunctionality();

      await cwfpage.clearAppliedFiltersIfAny();

      // Verify Template Form Filters Option
      await cwfpage.clickOnTemplateFormsFiltersBtn();

      // Validate Apply button is disabled when no filter option is selected.
      await cwfpage.validateApplyBtnDisabled();

      // Verify the message displayed on the portal when result set is empty.
      await cwfpage.validateEmptyFilterFunctionality();

      // Validate the clear all functionality
      await cwfpage.validateClearAllFunctionality();

      // Validate after applying filter result set is displayed accordingly.
      // await cwfpage.validateTemplateFormFilterByName();

      //Verify status filter functionality
      await cwfpage.validateStatusFilterFunctionality();

      //Verify date filter functionality
      await cwfpage.validateDateFilterFunctionality();
    }
  );
});
