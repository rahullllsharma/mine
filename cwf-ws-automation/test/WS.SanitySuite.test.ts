import os from "os";
import * as fs from "fs";
import {
  test,
  BrowserContext,
  Page,
  Locator,
  chromium,
  expect,
  Browser,
} from "@playwright/test";
import TestBase, { setProjectName } from "../Util/TestBase";
import HomePage from "../Page/Home.page";
import LoginPage from "../Page/Login.page";
import WorkPackagePage from "../Page/WorkPackage.page";
import MapPage from "../Page/Map.page";
import * as path from "path";
import { CURRENT_ENV } from "../Data/envConfig";
import workPackageData from "../Data/workPackageSample.data.json";
import AdminPage from "../Page/Admin.page";
import InsightsPage from "../Page/Insights.page";
import FormListPage from "../Page/FormList.page";

const normalizeText = (text: string, isPDFContent: boolean = false): string => {
  let cleanedText = text;

  if (isPDFContent) {
    // Remove only PDF-specific headers/footers and metadata
    cleanedText = cleanedText
      .replace(/\d{1,2}\/\d{1,2}\/\d{2,4},\s*\d{1,2}:\d{2}\s*[AP]M/g, "") // Removes date/time stamps
      .replace(/Worker Safety \| Urbint/g, "") // Removes the branding text
      .replace(/https?:\/\/[^\s]+/g, "") // Removes URLs
      .replace(/Page \d+ of \d+/g, "") // Removes page numbers
      .replace(/\d+\/\d+/g, "") // Removes page numbers like "1/8"
      .replace(/GMT\+?\d{1,3}:?\d{0,2}/g, "") // Remove timezone info
      .replace(/Thursday, July 31, 2025, \d+/g, "Thursday, July 31, 2025"); // Clean up malformed dates
  } else {
    // Remove main navigation bar pattern first (before individual term removal)
    cleanedText = cleanedText
      .replace(/^.*workersafety.*map.*cwf.*forms.*insights.*templates.*admin.*logout.*version.*alljobsafetybriefingjobinformationmedical&emergencytasks&criticalrisksenergysourcecontrolsworkproceduressiteconditionscontrolsassessmentattachmentsjsbsummarysign-off/gi, "") // Remove the complete navigation bar
      .replace(/^.*workersafety\s*map\s*cwf\s*forms\s*insights\s*templates\s*admin\s*na\s*logout\s*version.*all\s*job\s*safety\s*briefing\s*job\s*information\s*medical\s*&\s*emergency\s*tasks\s*&\s*critical\s*risks\s*energy\s*source\s*controls\s*work\s*procedures\s*site\s*conditions\s*controls\s*assessment\s*attachments\s*jsb\s*summary\s*sign-off/gi, "") // Remove navigation with spaces
      .replace(/work orders/gi, "") // Remove navigation text
      .replace(/v1 forms/gi, "") // Remove navigation text
      .replace(/all job safety briefing/gi, "") // Remove navigation breadcrumb
      .replace(/unknown form history/gi, "") // Remove navigation breadcrumb
      .replace(/group discussion/gi, "") // Remove navigation breadcrumb
      .replace(/workersafety/gi, "") // Remove header text
      .replace(/urbint/gi, "") // Remove branding
      .replace(/edit/gi, "") // Remove edit buttons
      .replace(/share/gi, "") // Remove share buttons
      .replace(/\s*~\s*/g, " ") // Clean up ~ symbols from risk levels
      .replace(/\(\d+\)/g, ""); // Remove attachment counts in parentheses for better matching
    // NOTE: Keep JSB section names like "Job Information", "Medical & Emergency" etc. as they are content
  }
  
  // Remove all spaces for better comparison (content comparison file shows this works correctly)
  return cleanedText.replace(/\s+/g, "").trim().toLowerCase();
};

test.describe
  .parallel("Sanity Checklist - Work Package - Work Order Search All Tabs", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let workPackagePage: WorkPackagePage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/work-package-search-all-tabs",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    workPackagePage = new WorkPackagePage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
    await tb.clearNetworkLogs();
  });

  test("Search for a Work Order in Active, Pending, and Completed tabs", async () => {
    await tb.testStep("Verify Projects page loaded after login", async () => {
      await expect(page).toHaveURL(/.*projects/);
      await homepage.waitForHomePageLoad();
      await tb.startNetworkMonitoring();
    });
    // Active tab search
    await tb.testStep("Search for 'Automation' in Active tab", async () => {
      await workPackagePage.selectTab("Active");
      await workPackagePage.searchWorkPackage("Automation");
      let resultText = null;
      if (await workPackagePage.getFirstResultRowText()) {
        resultText = await workPackagePage.getFirstResultRowText();
        await tb.logSuccess(`Received result: '${resultText}' in Active tab.`);
      } else if (await workPackagePage.isNoProjectsMessageVisible()) {
        resultText = "No projects found";
        await tb.logSuccess(`Received message: '${resultText}' in Active tab.`);
      } else {
        await tb.logFailure(
          "Neither result row nor 'no projects found' message was visible in Active tab."
        );
      }
      await tb.captureScreenshot(page, "active-tab");
      await expect(
        (await workPackagePage.getFirstResultRowText()) !== null ||
          (await workPackagePage.isNoProjectsMessageVisible())
      ).toBeTruthy();
    });

    // Pending tab search
    await tb.testStep(
      "Switch to Pending tab and search for 'Automation'",
      async () => {
        await workPackagePage.selectTab("Pending");
        await workPackagePage.searchWorkPackage("Automation");
        let resultText = null;
        if (await workPackagePage.getFirstResultRowText()) {
          resultText = await workPackagePage.getFirstResultRowText();
          await tb.logSuccess(
            `Received result: '${resultText}' in Pending tab.`
          );
        } else if (await workPackagePage.isNoProjectsMessageVisible()) {
          resultText = "No projects found";
          await tb.logSuccess(
            `Received message: '${resultText}' in Pending tab.`
          );
        } else {
          await tb.logFailure(
            "Neither result row nor 'no projects found' message was visible in Pending tab."
          );
        }
        await tb.captureScreenshot(page, "pending-tab");
        await expect(
          (await workPackagePage.getFirstResultRowText()) !== null ||
            (await workPackagePage.isNoProjectsMessageVisible())
        ).toBeTruthy();
      }
    );

    // Completed tab search
    await tb.testStep(
      "Switch to Completed tab and search for 'Automation'",
      async () => {
        await workPackagePage.selectTab("Completed");
        await workPackagePage.searchWorkPackage("Automation");
        let resultText = null;
        if (await workPackagePage.getFirstResultRowText()) {
          resultText = await workPackagePage.getFirstResultRowText();
          await tb.logSuccess(
            `Received result: '${resultText}' in Completed tab.`
          );
        } else if (await workPackagePage.isNoProjectsMessageVisible()) {
          resultText = "No projects found";
          await tb.logSuccess(
            `Received message: '${resultText}' in Completed tab.`
          );
        } else {
          await tb.logFailure(
            "Neither result row nor 'no projects found' message was visible in Completed tab."
          );
        }
        await tb.captureScreenshot(page, "completed-tab");
        await expect(
          (await workPackagePage.getFirstResultRowText()) !== null ||
            (await workPackagePage.isNoProjectsMessageVisible())
        ).toBeTruthy();
      }
    );
    await tb.logErrorCalls();
});



// test.describe
//   .only("Sanity Checklist - PDF Download - JSB Summary validation", () => {
//   let context: BrowserContext;
//   let page: Page;
//   let tb: TestBase;
//   let loginpage: LoginPage;
//   let homepage: HomePage;
//   let formslistpage: FormListPage;

//   test.beforeEach(async ({ browser }, testInfo) => {
//     context = await browser.newContext({
//       recordVideo: {
//         dir: "test-results/videos/jsb-summary-validation",
//       },
//     });
//     page = await context.newPage();
//     setProjectName(testInfo.project.name);
//     tb = new TestBase(page);
//     loginpage = new LoginPage(page);
//     homepage = new HomePage(page);
//     formslistpage = new FormListPage(page);
//     await tb.goto();
//     await loginpage.Login();
//     await page.waitForTimeout(2000);
//   });

//   test.afterEach(async () => {
//     await context.close();
//   });

//   test("Should validate content of saved PDF against the web summary page", async () => {
//     await tb.testStep("Verify Home page loaded after login", async () => {
//       await expect(page).toHaveURL(/.*projects/);
//       await homepage.waitForHomePageLoad();
//     });

//     await tb.testStep("Navigate to the main Forms List page", async () => {
//       await homepage.NavigateToFormsListTab();
//       // Optional: Add a check to ensure the Forms page has loaded
//       await expect(page.getByRole('heading', { name: 'Forms' })).toBeVisible();
//     });


//     await tb.testStep("Navigate to and open the most recent completed JSB form", async () => {
//       await formslistpage.RecentCompletedJSBForm(); 
//        await formslistpage.verifyJSBLabelsAndButtons(
//           "Job Safety Briefing",
//           "Job Information",
//           "Medical & Emergency",
//           "Tasks & Critical Risks",
//           "Energy Source Controls",
//           "Work Procedures",
//           "Site Conditions",
//           "Controls Assessment",
//           "Attachments",
//           "JSB Summary",
//           "Sign-Off"
//         );
//       await formslistpage.isRightSideSectionVisible();
//       await tb.logSuccess("Successfully opened a completed JSB form.");
//     });

//     await tb.testStep("Compare web content with manually saved PDF content", async () => {
//       // 1. Get the text content from the web page
//       const webContent = await formslistpage.getSummaryPageContent();
//       const normalizedWebContent = normalizeText(webContent);
//       const manualPdfPath = path.join(process.cwd(), "manual_summary.pdf");
//       const pdfContent = await tb.readPdfContent(manualPdfPath);
//       const normalizedPdfContent = normalizeText(pdfContent);

//       expect(normalizedPdfContent, "The PDF content should contain all the web page content.")
//         .toContain(normalizedWebContent);
      
//       await tb.logSuccess("Validation successful: PDF content matches web page content.");
//     });
//     });
//       await tb.testStep("Visually validate the JSB Summary print preview", async () => {
//       // Use a try...finally block to ensure we always navigate back
//       try {
//         await formslistpage.triggerPrintPreview();
//         await page.waitForTimeout(10000); 
//         page.locator('body');
        


//         // await expect(page).toHaveScreenshot('jsb-summary-screenshot.png', {
//         //   fullPage: true,
//         //   maxDiffPixels: 100
//         // });

//         await tb.logSuccess("JSB Summary image matches the baseline screenshot.");
//       } finally {
//         // 4. This block will ALWAYS run. Navigate back to the application.
//         await page.goBack();
//         await tb.logMessage("Navigated back from print preview.");
//       }
// });
//   });
//   });



test.describe
  .parallel("Sanity Checklist - Work Package - Work Order Edit/History", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let workPackagePage: WorkPackagePage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/work-package-edit-history",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    workPackagePage = new WorkPackagePage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test("Edit work order details and verify history", async () => {
    let updatedTimeAndDateString = "";
    await tb.testStep("Wait for home page load", async () => {
      await homepage.waitForHomePageLoad();
      await expect(page).toHaveURL(/.*projects/);
    });

    await tb.testStep("Navigate to Projects page and Active tab", async () => {
      await workPackagePage.selectTab("Active");
    });

    let workOrderFound = false;
    await tb.testStep(
      "Wait for first work order link (cell-based)",
      async () => {
        workOrderFound = await workPackagePage.waitForFirstWorkOrderInList(tb);
        if (!workOrderFound) {
          await tb.logFailure(
            "No work order found in Active tab after retries. Skipping edit/history test."
          );
          await page.screenshot({
            path: `test-results/screenshots/no-workorder-found.png`,
            fullPage: true,
          });
        } else {
          await tb.logSuccess(
            "Work order found in Active tab. Proceeding with edit/history test."
          );
        }
      }
    );
    if (!workOrderFound) return;

    let workOrderText: string | null = null;
    await tb.testStep(
      "Click first work order and wait for navigation",
      async () => {
        workOrderText = await workPackagePage.clickFirstWorkOrderInList();
        await tb.logSuccess(`Navigated to work order: ${workOrderText}`);
      }
    );

    await tb.testStep("Open settings for the work order", async () => {
      await workPackagePage.openSettingsForWorkOrder();
      await tb.captureScreenshot(page, "settings-page");
      await tb.logSuccess("Settings page loaded");
    });

    await tb.testStep("Edit Description and save", async () => {
      await workPackagePage.editDescriptionAndSave();
      updatedTimeAndDateString =
        new Date()
          .toLocaleString("en-US", {
            timeZone: "Asia/Kolkata",
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "numeric",
            minute: "2-digit",
            hour12: true,
          })
          .replace(" at ", ", ") + " GMT+5:30";
      await tb.captureScreenshot(page, "description-updated");
      await tb.logSuccess("Description updated and saved");
    });

    await tb.testStep("Go to History tab and verify update", async () => {
      await workPackagePage.goToHistoryTabAndVerifyUpdate(
        updatedTimeAndDateString
      );
      await tb.captureScreenshot(page, "history-tab");
      await tb.logSuccess("History tab shows the description update");
    });
  });
});

test.describe
  .parallel("Sanity Checklist - Work Package - Work Order Creation and Deletion", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let workPackagePage: WorkPackagePage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/work-package-creation-and-deletion",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    workPackagePage = new WorkPackagePage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test("Should create a work package and then delete it", async ({}, testInfo) => {
    if (testInfo.project.name === "iPad Mini") {
      await tb.logMessage(
        "iPad device detected, so no work order creation allowed."
      );
      test.skip();
    }
    const {
      workOrder,
      projectNumber,
      projectType,
      workType1,
      workType2,
      assetType,
      status,
      projectZip,
      startDate,
      endDate,
      area,
      operatingHQ,
      description,
      engineerName,
      contractRef,
      contractName,
      contractor,
      location1Name,
      location1Lat,
      location1Long,
      location2Name,
      location2Lat,
      location2Long,
      primaryLocationSupervisor,
      additionalLocationSupervisor,
      projectManager,
      primarySupervisor,
      additionalSupervisor,
    } = workPackageData;

    await tb.testStep(
      "Wait for home page and click Add Work Package",
      async () => {
        await homepage.waitForHomePageLoad();
        await expect(page.getByTestId("add-work-package-button")).toBeVisible({
          timeout: 20000,
        });
        await page.getByTestId("add-work-package-button").click();
        await page.waitForURL(/projects\/create/);
      }
    );

    await tb.testStep("Fill work package details", async () => {
      await workPackagePage.fillWorkOrderOrProjectName(workOrder);
      await workPackagePage.fillProjectNumberOrKey(projectNumber);
      await workPackagePage.selectProjectType(projectType);
      await workPackagePage.selectWorkTypes(workType1, workType2);
      await workPackagePage.selectAssetType(assetType);
      await workPackagePage.selectStatus(status);
      await workPackagePage.fillProjectZipCode(projectZip);
      await workPackagePage.fillStartDate(startDate);
      await workPackagePage.fillEndDate(endDate);
      await workPackagePage.selectAreaOrDivision(area);
      await workPackagePage.selectOperatingHQorRegion(operatingHQ);
      await workPackagePage.fillDescription(description);
      await workPackagePage.selectProjectManager(projectManager);
      await workPackagePage.selectPrimarySupervisor(primarySupervisor);
      await workPackagePage.selectAdditionalSupervisor(additionalSupervisor);
      await workPackagePage.fillEngineerName(engineerName);
      await workPackagePage.fillContractReferenceNumber(contractRef);
      await workPackagePage.fillContractName(contractName);
      await workPackagePage.selectContractor(contractor);
      await tb.captureScreenshot(page, "work-package-details");
    });

    await tb.testStep("Add locations", async () => {
      await workPackagePage.addLocation(
        location1Name,
        location1Lat,
        location1Long,
        primaryLocationSupervisor,
        additionalLocationSupervisor
      );

      await workPackagePage.clickAddLocationButton();
      await workPackagePage.addLocation(
        location2Name,
        location2Lat,
        location2Long,
        primaryLocationSupervisor,
        additionalLocationSupervisor
      );
      await tb.captureScreenshot(page, "locations-added");
      await page.waitForTimeout(200);
      await tb.logSuccess("Locations added successfully");
    });

    await tb.testStep("Click save button", async () => {
      await workPackagePage.clickSave();
      await page.waitForTimeout(3000);
      await tb.logSuccess("Save button clicked successfully");
    });

    await tb.testStep("Verify work package creation", async () => {
      await workPackagePage.searchWorkPackage(workOrder);
      await tb.testStep(
        "Verify Work Package displayed in the table after search",
        async () => {
          try {
            await workPackagePage.clickFirstResultRow(workOrder);
            await page.waitForURL(/\/projects\/.*/, { timeout: 20000 });
            await tb.captureScreenshot(page, "saved-work-package-details");
            await tb.logSuccess("Successfully opened work package details");
          } catch (error: unknown) {
            await tb.logFailure("Failed to find or click work package link");
            throw new Error(
              `Work package \"${workOrder}\" not found or not clickable: ${
                error instanceof Error ? error.message : String(error)
              }`
            );
          }
        }
      );
    });

    await tb.testStep("Delete work package and verify deletion", async () => {
      await workPackagePage.deleteWorkPackage(workOrder);
      await tb.testStep("Verify work package deletion", async () => {
        await workPackagePage.isWorkPackageNotListed(workOrder);
        await tb.logSuccess("Work package deleted successfully");
      });
    });
  });
});

test.describe
  .parallel("Sanity Checklist - Work Package - Add Edit Delete Activities", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let workPackagePage: WorkPackagePage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/work-package-add-edit-delete-activities",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    workPackagePage = new WorkPackagePage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test("Add, edit, and delete an activity in a project", async () => {
    await tb.testStep("Verify Home page loaded after login", async () => {
      await expect(page).toHaveURL(/.*projects/);
      await homepage.waitForHomePageLoad();
    });
    let projectOpened = false;
    await tb.testStep(
      "Open first project if available and validate details screen",
      async () => {
        projectOpened = await workPackagePage.openFirstProjectIfAvailable(tb);
      }
    );
    if (!projectOpened) return;
    // Add Activity
    await tb.testStep("Click Add... and select Activity", async () => {
      await workPackagePage.addActivity(
        ["Cable work", "Excavate"],
        [
          [
            "Fault locate on cable",
            "Install, pull, maintain, or remove cable or elbow",
          ],
          ["Grade"],
        ]
      );
      await tb.captureScreenshot(page, "activity-added");
    });

    // Edit Activity
    await tb.testStep("Open three dots menu and edit activity", async () => {
      await workPackagePage.openEditActivityModal("Cable work + Excavate", tb);
      await workPackagePage.editActivity(
        "Cable work + Excavate",
        "Cable work + Excavate Updated Act"
      );
      await tb.captureScreenshot(page, "activity-edited");
    });

    await tb.testStep("Validate updated activity is listed", async () => {
      const updatedName = "Cable work + Excavate Updated Act";
      await page.waitForTimeout(2000);
      const isListed = await workPackagePage.isActivityListed(updatedName);
      await expect(isListed).toBeTruthy();
    });

    // Delete Activity
    await tb.testStep("Delete Activity", async () => {
      await workPackagePage.deleteActivity(
        "Cable work + Excavate Updated Act",
        tb
      );
      await tb.captureScreenshot(page, "activity-deleted");
    });
  });
});

test.describe
  .parallel("Sanity Checklist - Work Package - Add, Edit, Delete Site Conditions", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let workPackagePage: WorkPackagePage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/work-package-add-edit-delete-site-conditions",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    workPackagePage = new WorkPackagePage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test("Add, Edit, and Delete Site Condition", async () => {
    let selectedSiteConditionName: string;
    let hazardOptionText: string | null;
    let controlOptionText: string | null;

    await tb.testStep("Verify Home page loaded after login", async () => {
      await expect(page).toHaveURL(/.*projects/);
      await homepage.waitForHomePageLoad();
    });

    // Open first project
    await tb.testStep(
      "Open first project and validate details screen",
      async () => {
        const projectOpened = await workPackagePage.openFirstProjectIfAvailable(
          tb
        );
        if (!projectOpened) {
          return;
        }
      }
    );

    // Add Site Condition
    await tb.testStep("Add a new Site Condition", async () => {
      selectedSiteConditionName = await workPackagePage.addSiteCondition(tb);
      const isListed = await workPackagePage.isSiteConditionListed(
        selectedSiteConditionName
      );
      await tb.captureScreenshot(page, "site-condition-added");
      await expect(isListed).toBeTruthy();
    });

    // Edit Site Condition
    await tb.testStep("Edit the added Site Condition", async () => {
      const result = await workPackagePage.editSiteCondition(
        selectedSiteConditionName,
        tb
      );
      hazardOptionText = result.hazard;
      controlOptionText = result.control;
    });

    // Validate in summary view
    await tb.testStep(
      "Validate hazard and control in summary view",
      async () => {
        await workPackagePage.validateSiteConditionInSummary(
          selectedSiteConditionName,
          hazardOptionText ?? "",
          controlOptionText ?? "",
          tb
        );
        await tb.captureScreenshot(page, "site-condition-summary");
      }
    );

    // Delete Site Condition
    await tb.testStep("Delete the Site Condition", async () => {
      await workPackagePage.deleteSiteCondition(selectedSiteConditionName);
      const isNotListed = await workPackagePage.isSiteConditionNotListed(
        selectedSiteConditionName
      );
      await expect(isNotListed).toBeTruthy();
      await tb.captureScreenshot(page, "site-condition-deleted");
      await tb.logSuccess("Site Condition deleted successfully");
    });
  });
});

test.describe
  .parallel("Sanity Checklist - Insights - Add, Edit, Delete Insights", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let adminPage: AdminPage;
  let insightsPage: InsightsPage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/insights-add-edit-delete",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    adminPage = new AdminPage(page);
    insightsPage = new InsightsPage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test("Add, Edit, and Delete Insights", async ({}, testInfo) => {
    if (testInfo.project.name === "iPad Mini") {
      await tb.logMessage(
        "Mobile device detected, so no access to admin and insights reports allowed."
      );
      test.skip();
    }
    await tb.testStep("Verify Home page loaded after login", async () => {
      await expect(page).toHaveURL(/.*projects/);
      await homepage.waitForHomePageLoad();
    });

    await tb.testStep("Navigate to Admin page", async () => {
      await adminPage.navigateToAdminPage();
    });

    await tb.testStep(
      "Verify Insights button is visible and clickable",
      async () => {
        await adminPage.verifyInsightsButton();
      }
    );

    await tb.testStep(
      "Validate Insights page UI (header, button, table)",
      async () => {
        await adminPage.validateInsightsPageUI();
        await tb.captureScreenshot(page, "insights-page-ui");
      }
    );

    await tb.testStep("Verify Add Insights functionality", async () => {
      await adminPage.verifyAndClickAddInsightsButton();
      await adminPage.verifyCancelButtonForPopUp();
      await adminPage.verifyMandatoryFieldErrors();
      await adminPage.fillInsightsDetailsAndSubmit();
      await adminPage.verifyInsightsAddedSuccessfully();
      await tb.captureScreenshot(page, "insight-added");
    });

    await tb.testStep(
      "Validated added insight is listed in Insights Page",
      async () => {
        await adminPage.navigateToInsightsPage();
        await insightsPage.validateInsightsPageUI();
        await insightsPage.verifyAddedInsightIsListed();
        await insightsPage.verifyAddedInsightsDetails();
      }
    );

    await tb.testStep("Edit visibility of the added insight", async () => {
      await adminPage.navigateToAdminPage();
      await adminPage.verifyInsightsButton();
      await adminPage.editVisibilityOfAddedInsight();
    });

    await tb.testStep(
      "Validate the visibility of the insight in the insights page",
      async () => {
        await adminPage.navigateToInsightsPage();
        await insightsPage.validateInsightsPageUI();
        await insightsPage.editedInsightIsNotVisible();
      }
    );

    await tb.testStep("Edit name of the added insight", async () => {
      await adminPage.navigateToAdminPage();
      await adminPage.verifyInsightsButton();
      await adminPage.editNameOfAddedInsightAndMakeItVisible();
    });

    await tb.testStep("Validate the updated name of the insight", async () => {
      await adminPage.navigateToInsightsPage();
      await insightsPage.validateInsightsPageUI();
      await insightsPage.verifyEditedInsightHasUpdatedName();
    });

    await tb.testStep("Delete the added insight", async () => {
      await adminPage.navigateToAdminPage();
      await adminPage.verifyInsightsButton();
      await adminPage.deleteAddedInsight();
    });
  });
});

test.describe
  .parallel("Sanity Checklist - Forms List - Add, Edit, Delete Hardcoded JSB Form", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let formslistpage: FormListPage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/forms-list-jsb-add-edit-delete",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    formslistpage = new FormListPage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test("Verify addition of JSB Form and filling test details and submitting", async () => {
    await tb.testStep("Verify Home page loaded after login", async () => {
      await expect(page).toHaveURL(/.*projects/);
      await homepage.waitForHomePageLoad();
    });

    await tb.testStep("Navigate to Forms List Tab", async () => {
      await homepage.NavigateToFormsListTab();
    });

    await tb.testStep(
      "Verify Add Form Button is visible and clickable",
      async () => {
        await formslistpage.verifyAddFormButton(
          "Add Form",
          "Energy Based Observation",
          "Job Safety Briefing"
        );
        await page.waitForTimeout(1000);
      }
    );

    await tb.testStep(
      "Navigate to Job Safety Briefing form page and validate labels",
      async () => {
        await formslistpage.ClickJobSafetyBriefingBtn();
        await formslistpage.verifyJSBLabelsAndButtons(
          "Job Safety Briefing",
          "Job Information",
          "Medical & Emergency",
          "Tasks & Critical Risks",
          "Energy Source Controls",
          "Work Procedures",
          "Site Conditions",
          "Controls Assessment",
          "Attachments",
          "JSB Summary",
          "Sign-Off"
        );
      }
    );

    await tb.testStep("Fill the Job Information tab and submit", async () => {
      await formslistpage.ClickJobInformationTabInJSB();
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.JSB_JobInfo_CheckForReqFields();
      await formslistpage.JSB_JobInfo_GenInfo_VerifyCurrentDateWithFormat();
      await formslistpage.JSB_JobInfo_GenInfo_VerifyDatePickerBoxFunctionality();
      await page.waitForTimeout(2000);
      await formslistpage.JSB_JobInfo_GenInfo_VerifyDateSelectorFunctionality(
        "2025-05-31"
      );
      await formslistpage.JSB_JobInfo_GenInfo_VerifyBriefingTimeSelector();
      await formslistpage.JSB_JobInfo_GenInfo_VerifyTimeSelectorFunctionality(
        "14:48"
      );
      await formslistpage.JSB_JobInfo_GPSCo_VerifyUseCurrentLocationBtn();
      await formslistpage.JSB_JobInfo_GPSCo_VerifyFillingCustomLatLng(
        "34.1787",
        "-78.4449"
      );
      await formslistpage.JSB_JobInfo_WorkLoc_VerifyAddressTextBox(
        "Temp Automation Address xyz abc."
      );
      await formslistpage.JSB_JobInfo_WorkLoc_VerifyMultipleAddressTextBox(
        "Temp address line 1\nTemp Address Line 2\nAddress line 3\naddress line 4\naddress line 5\nscope of work line 1\nscope of work line 2"
      );
      await formslistpage.JSB_JobInfo_WorkLoc_OperatingHQ();
      await tb.captureScreenshot(page, "job-information-tab");
      await formslistpage.JSB_JobInfo_ClickSaveAndContinueBtn();
    });

    await tb.testStep("Fill Medical & Emergency tab and submit", async () => {
      await formslistpage.JSB_MedAndEmer_VerifyTabHighlightedAutomatically();
      await formslistpage.isRightSideSectionVisible();
      const isContactsFieldFilled =
        await formslistpage.JSB_MedAndEmer_VerifyEmergencyContactFields();
      if (isContactsFieldFilled) {
        await tb.logMessage(
          "Emergency Contact Details found already prefilled, Hence not required to fill manually"
        );
      } else {
        await tb.logMessage(
          "Emergency Contact Details were not found prefilled, thus filling it manually"
        );
        await formslistpage.FillEmergencyContact1Details("Sparsh Test");
        await formslistpage.FillEmergencyContact1PhoneNumberDetails(
          "1234214242"
        );
        await formslistpage.FillEmergencyContact2Details("Vandana Test");
        await formslistpage.FillEmergencyContact2PhoneNumberDetails(
          "1234299129"
        );
      }
      await formslistpage.SelectOtherOptionInNearestMedFacilitiesDropdown();
      await formslistpage.EnterCustomNearestMedFacility("Test Facility");
      // await formslistpage.JSB_MedAndEmer_VerifyAEDLocationDropdownBox();
      // await formslistpage.JSB_MedAndEmer_EnterOtherAEDLocation("Test AED Location");
      await tb.captureScreenshot(page, "medical-and-emergency-tab");
      await formslistpage.JSB_MedAndEmer_ClickSaveAndContinueBtn();
    });

    await tb.testStep(
      "Fill Tasks & Critical Risks tab and submit",
      async () => {
        await formslistpage.JSB_TasksAndCriRisks_VerifyTabHighlightedAutomatically();
        await formslistpage.isRightSideSectionVisible();
        await formslistpage.VerifyReqCheckTasksAndCriRisks();
        await formslistpage.VerifyHyperlinkToCriRisksAreaDocs();
        // await formslistpage.CheckCriticalRiskAreasToggles();
        await formslistpage.JSB_TasksAndCriRisks_ClickAddActivityButton();
        await formslistpage.VerifyCancelButtonInAddActivityPopUp();
        await formslistpage.JSB_TasksAndCriRisks_ClickAddActivityButton();
        await formslistpage.JSB_TasksAndCriRisks_VerifyTasksButtonsAndCountLabel();
        await formslistpage.JSB_TasksAndCriRisks_VerifySubTasksInAddActivityPopUp();
        await formslistpage.JSB_TasksAndCriRisks_VerifySearchBoxFunctionality(
          "Excavate"
        );
        // await formslistpage.JSB_TasksAndCriRisks_VerifySearchBoxFunctionality(
        //   "Pole work"
        // );
        // await formslistpage.JSB_TasksAndCriRisks_VerifySearchBoxFunctionality(
        //   "Meter work"
        // );
        await formslistpage.JSB_TasksAndCriRisks_clickNextButtonInAddActivityPopUp();
        await formslistpage.JSB_TasksAndCriRisks_VerifyActivityNameScreenInPopUp(
          "Excavate"
        );
        await formslistpage.JSB_TasksAndCriRisks_ClickAddActivityBtnInPopUp();
        await formslistpage.JSB_TasksAndCriRisks_VerifySelectedTasks();
        await tb.captureScreenshot(page, "tasks-and-critical-risks-tab");
        await formslistpage.JSB_JobInfo_ClickSaveAndContinueBtn();
      }
    );

    await tb.testStep(
      "Fill Energy Source Controls tab and Submit",
      async () => {
        await formslistpage.JSB_EnergySrcCtrl_VerifyTabHighlightedAutomatically();
        await formslistpage.isRightSideSectionVisible();
        await formslistpage.JSB_EnergySrcCtrl_VerifyArcFlashCategory();
        await formslistpage.JSB_EnergySrcCtrl_SelectArcFlashCategory();
        await formslistpage.JSB_EnergySrcCtrl_VerifyPrimaryVoltage();
        await formslistpage.JSB_EnergySrcCtrl_SelectPrimaryVoltage();
        await formslistpage.JSB_EnergySrcCtrl_VerifySecondaryVoltage();
        await formslistpage.JSB_EnergySrcCtrl_SelectSecondaryVoltage();
        await formslistpage.JSB_EnergySrcCtrl_VerifyTransmissionVoltage();
        await formslistpage.JSB_EnergySrcCtrl_SelectTransmissionVoltage();
        await formslistpage.JSB_EnergySrcCtrl_VerifyClearancePoints();
        await formslistpage.JSB_EnergySrcCtrl_VerifyAddAdditionalEWPFunctionality();
        await formslistpage.JSB_EnergySrcCtrl_EWP_VerifyReqChecks();
        await formslistpage.JSB_EnergySrcCtrl_AddEWPDetails(
          "Test EWP",
          "04:14",
          "18:23",
          "Test Proc",
          "Test Issuer",
          "Test Receiver",
          "Test Ref Point 1",
          "Test Ref Point 2",
          "Test Circuit Breaker",
          "Test Switch",
          "Test Transformer"
        );
        await tb.captureScreenshot(page, "energy-source-controls-tab");
        await formslistpage.JSB_EnergySrcCtrl_ClickSaveAndContinueBtn();
      }
    );

    await tb.testStep("Fill Work Procedures tab and submit", async () => {
      await formslistpage.JSB_WorkProcedures_VerifyTabHighlightedAutomatically();
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.JSB_WorkProcedures_VerifyReqFieldChecks();
      await formslistpage.JSB_WorkProcedures_VerifyDistributionBulletins();
      await formslistpage.JSB_WorkProcedures_SelectDistributionBulletins();
      await formslistpage.JSB_WorkProcedures_VerifyRulesOfCoverUp();
      await formslistpage.JSB_WorkProcedures_VerifyMADLinkAndPopUpBox();
      await formslistpage.JSB_WorkProcedures_ClickCheckBoxMADAndVerifyReqCheck();
      await formslistpage.JSB_WorkProcedures_VerifyMADDropdown();
      await formslistpage.JSB_WorkProcedures_SelectMADOption();
      await formslistpage.JSB_WorkProcedures_VerifySDOPHyperlink();
      await formslistpage.JSB_WorkProcedures_VerifySDOPCheckBox();
      await formslistpage.JSB_WorkProcedures_VerifyTOCRequestFormHyperlink();
      await formslistpage.JSB_WorkProcedures_VerifyTOCCheckBox();
      await formslistpage.JSB_WorkProcedures_VerifyStepTouchPotential();
      await formslistpage.JSB_WorkProcedures_VerifyOtherWorkProceduresInputField(
        "Other Work Procedure Testing Line 1\nOther Work Procedure Testing Line 2\nOther Work Procedure Testing Line 3\nOther Work Procedure Testing Line 4\nSpecial Precaution 1\nSpecial Precaution 2"
      );
      await tb.captureScreenshot(page, "work-procedures-tab");
      await formslistpage.JSB_WorkProcedures_SaveAndContinue();
    });

    await tb.testStep("Validate Site Conditions tab and submit", async () => {
      await formslistpage.JSB_SiteConditions_VerifyTabHighlightedAutomatically();
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.JSB_SiteConditions_VerifyIfProceedsToNextTabWithoutError();
      await formslistpage.JSB_SiteConditions_VerifyAllSiteConditionsButton();
      await formslistpage.JSB_SiteConditions_VerifyAddSiteConditionsButton();
      await formslistpage.JSB_SiteConditions_CloseSiteConditionsPopUp();
      await formslistpage.JSB_SiteConditions_VerifyApplicableSideCondnCount();
      await formslistpage.JSB_SiteConditions_AddSiteConditionsUsingPopUp();
      await tb.captureScreenshot(page, "site-conditions-tab");
      await formslistpage.JSB_SiteConditions_SaveAndContinue();
    });

    await tb.testStep(
      "Validate Controls Assessment Tab and Submit",
      async () => {
        await formslistpage.JSB_ControlAssessment_VerifyTabHighlightedAutomatically();
        await formslistpage.isRightSideSectionVisible();
        await formslistpage.JSB_ControlAssessment_LogAvailableHeadingsOnControlAssessmentTab();
        await formslistpage.JSB_ControlAssessment_VerifyRecControlsChkBoxFunctionality();
        await formslistpage.JSB_ControlAssessment_VerifyOtherControlsDropdown();
        await formslistpage.JSB_ControlAssessment_VerifyCrossButtonOtherControlsSelections();
        await formslistpage.JSB_ControlAssessment_SelectOtherControlsFromDropdown();
        await formslistpage.JSB_ControlAssessment_VerifyAdditionalInformationInputField(
          "Additional Info Testing Line 1\nAdditional Info Testing Line 2\nAdditional Info Testing Line 3\nAdditional Info Testing Line 4\nExample Control 1\nExample Control 2"
        );
        await tb.captureScreenshot(page, "control-assessment-tab");
        await formslistpage.JSB_ControlAssessment_SaveAndContinue();
      }
    );

    await tb.testStep("Validate Attachments Tab and Submit", async () => {
      await formslistpage.JSB_Attachments_VerifyTabHighlightedAutomatically();
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.JSB_Attachments_VerifyIfProceedsToNextTabWithoutError();
      await formslistpage.JSB_Attachments_VerifyPhotoAdditionUsingAddPhotosBtn();
      await formslistpage.JSB_Attachments_VerifyPhotosDeletion();
      await formslistpage.JSB_Attachments_VerifyDocumentsAdditionUsingAddDocumentsBtn();
      await formslistpage.JSB_Attachments_VerifyMenuButtonForRecentlyUploadedDoc();
      await formslistpage.JSB_Attachments_VerifyDownloadButtonForRecentlyUploadedDoc();
      await formslistpage.JSB_Attachments_VerifyEditButtonForRecentlyUploadedDoc(
        "Test Doc"
      );
      await formslistpage.JSB_Attachments_VerifyDocumentsDeletion();
      await tb.captureScreenshot(page, "attachments-tab");
      await formslistpage.JSB_Attachments_ClickSaveAndContinueBtn();
    });


    await tb.testStep("Validate JSB Summary Tab and Submit", async () => {
      await formslistpage.JSB_Summary_VerifyTabHighlightedAutomatically();
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.JSB_Summary_VerifyQRCodeFunctionality();
      await formslistpage.JSB_Summary_ClickSaveAndContinueBtn();
    });

    await tb.testStep("Validate Sign-Off Tab and submit", async () => {
      await formslistpage.JSB_SignOff_VerifyTabHighlightedAutomatically();
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.JSB_SignOff_VerifySearchByNameOrIdFieldFunctionality();
      await formslistpage.JSB_SignOff_VerifyAddOtherNameInputFunctionality(
        "testauto"
      );
      await formslistpage.JSB_SignOff_VerifyAddSignForOtherName("testauto");
      await formslistpage.JSB_SignOff_VerifyAddNameBtnFunctionality();
      await formslistpage.JSB_SignOff_VerifyDeleteSignAndResign();
      await tb.captureScreenshot(page, "sign-off-tab");
      await formslistpage.JSB_SignOff_ClickSaveAndContinueBtn();
    });

    await tb.testStep("Validate JSB Form Submission", async () => {
      await formslistpage.JSB_VerifyCompleteFormButtonFunctionality();
      await tb.captureScreenshot(page, "jsb-form-submission");
    });
  });
});
  });

test.describe
  .parallel("Sanity Checklist - Maps - Global Search, Quick Filter, Search Area and Filter", async () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let mappage: MapPage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/maps",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    mappage = new MapPage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test("Verify Map Global Search, Quick Filter, Search Area and Filter Functionality", async () => {
    await tb.testStep("Verify Home page loaded after login", async () => {
      await expect(page).toHaveURL(/.*projects/);
      await homepage.waitForHomePageLoad();
    });

    await tb.testStep(
      "Navigate to Map Tab and wait for it to load",
      async () => {
        await homepage.NavigateToMapTab();
        await mappage.validateMapPageUI();
      }
    );

    await tb.testStep("Validate Map Search Functionality", async () => {
      await mappage.validateMapSearchFunctionality();
    });
  });
});

test.describe
  .parallel("Sanity Checklist - Forms List - Add, Edit, Delete Hardcoded EBO Form", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let formslistpage: FormListPage;

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/forms-list-ebo-add-edit-delete",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    formslistpage = new FormListPage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test("Verify addition of EBO Form and filling test details and submitting", async () => {
    await tb.testStep("Verify Home page loaded after login", async () => {
      await expect(page).toHaveURL(/.*projects/);
      await homepage.waitForHomePageLoad();
    });

    await tb.testStep("Navigate to Forms List Tab", async () => {
      await homepage.NavigateToFormsListTab();
    });

    await tb.testStep(
      "Verify Add Form Button is visible and clickable",
      async () => {
        await formslistpage.verifyAddFormButton(
          "Add Form",
          "Energy Based Observation",
          "Job Safety Briefing"
        );
        await page.waitForTimeout(1000);
      }
    );

    await tb.testStep(
      "Navigate to Energy Based Observation form page and validate labels",
      async () => {
        await formslistpage.ClickEnergyBasedObservationBtn();
        await formslistpage.verifyEBOLabelsAndButtons(
          "Energy Based Observation",
          "Observation Details",
          "High Energy Tasks",
          "Additional Information",
          "Historical Incidents",
          "Photos",
          "Summary",
          "Personnel"
        );
      }
    );

    await tb.testStep(
      "Fill the Observation Details tab and submit",
      async () => {
        await formslistpage.ClickObservationDetailsTabInEBO();
        await formslistpage.isRightSideSectionVisible();
        await formslistpage.EBO_ValidateHECARulesComponent();
        await formslistpage.EBO_ObservationDetails_CheckForReqFields();
        await formslistpage.EBO_ObservationDetails_VerifyDateSelection();
        await formslistpage.EBO_ObservationDetails_VerifyObservationTimeSelector();
        await formslistpage.EBO_ObservationDetails_FillWONumberInputField();
        await formslistpage.EBO_ObservationDetails_VerifyOpCoObservedDropdown();
        await formslistpage.EBO_ObservationDetails_SelectOpCoObserved();
        await formslistpage.EBO_ObservationDetails_VerifyDepartmentObservedDropdown();
        await formslistpage.EBO_ObservationDetails_SelectDepartmentObserved();
        await formslistpage.EBO_ObservationDetails_VerifyWorkTypeDropdown();
        await formslistpage.EBO_ObservationDetails_SelectWorkType();
        await formslistpage.EBO_ObservationDetails_VerifyUseCurrentLocationBtn();
        await formslistpage.JSB_JobInfo_GPSCo_VerifyFillingCustomLatLng(
          "34.1787",
          "-78.4449"
        );
        await formslistpage.EBO_ClickSaveAndContinueBtn(
          "EBO Observation Details"
        );
      }
    );

    await tb.testStep("Fill High Energy Tasks tab and submit", async () => {
      await formslistpage.EBO_VerifyBlueTickAndBlueBorderOnSavedTab_ObservationDetails();
      await page.waitForTimeout(2000);
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.EBO_VerifyReqCheckHighEnergyTasks();
      await formslistpage.JSB_TasksAndCriRisks_ClickAddActivityButton();
      await formslistpage.VerifyCancelButtonInAddActivityPopUp();
      await formslistpage.JSB_TasksAndCriRisks_ClickAddActivityButton();
      await formslistpage.JSB_TasksAndCriRisks_VerifyTasksButtonsAndCountLabel();
      await formslistpage.JSB_TasksAndCriRisks_VerifySubTasksInAddActivityPopUp();
      const selectedSubTask =
        await formslistpage.EBO_VerifySearchBoxFunctionality_HighEnergyTasks(
          "Excavate"
        );
      await formslistpage.JSB_TasksAndCriRisks_clickNextButtonInAddActivityPopUp();
      await formslistpage.EBO_HET_VerifyAddedActivityTitleAndSubPage(
        selectedSubTask || ""
      );
      await formslistpage.EBO_ClickSaveAndContinueBtn("High Energy Tasks");
    });

    await tb.testStep(
      "Verify additional sub page for the added activity",
      async () => {
        const ifObservedHazardsFound =
          await formslistpage.EBO_VerifyUIForAddedSubpage();
        if (ifObservedHazardsFound) {
          await formslistpage.EBO_VerifyHazardObservedComponent();
        }
        await formslistpage.EBO_ClickSaveAndContinueBtn(
          "Subpage for the added activity"
        );
        const ifPopUpForRecommendedHEHFound =
          await formslistpage.EBO_ValidatePopUpForRecommendedHighEnergyHazards();
        if (ifPopUpForRecommendedHEHFound) {
          await formslistpage.EBO_ClickSaveAndContinueBtn(
            "Subpage for the added activity"
          );
        }
      }
    );

    await tb.testStep(
      "Fill Additional Information tab and submit",
      async () => {
        await formslistpage.EBO_VerifyBlueTickAndBlueBorderOnSavedTab_HighEnergyTasks();
        await formslistpage.isRightSideSectionVisible();
        await formslistpage.EBO_AdditionalInfo_VerifyUI();
        await formslistpage.EBO_ClickSaveAndContinueBtn(
          "Additional Information"
        );
      }
    );

    await tb.testStep(
      "Validate Historical Incidents tab and submit",
      async () => {
        await formslistpage.EBO_VerifyBlueTickAndBlueBorderOnSavedTab_AdditionalInfo();
        await formslistpage.isRightSideSectionVisible();
        await formslistpage.EBO_HistoricalIncidents_VerifyUI();
        await formslistpage.EBO_ClickSaveAndContinueBtn("Historical Incidents");
      }
    );

    await tb.testStep("Validate Photos tab and submit", async () => {
      await formslistpage.EBO_VerifyBlueTickAndBlueBorderOnSavedTab_HistoricalIncidents();
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.EBO_Attachments_VerifyPhotoAdditionUsingAddPhotosBtn();
      await formslistpage.EBO_Attachments_VerifyPhotosDeletion();
      await formslistpage.EBO_ClickSaveAndContinueBtn("Photos");
    });

    await tb.testStep("Validate Summary tab and Submit", async () => {
      await formslistpage.EBO_VerifyBlueTickAndBlueBorderOnSavedTab_Photos();
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.EBO_Summary_VerifyUI();
      await formslistpage.EBO_ClickSaveAndContinueBtn("Summary");
    });

    await tb.testStep("Validate Personnel tab and submit", async () => {
      await formslistpage.EBO_VerifyBlueTickAndBlueBorderOnSavedTab_Summary();
      await formslistpage.isRightSideSectionVisible();
      await formslistpage.EBO_Personnel_VerifyUI();
      await formslistpage.EBO_Personnel_VerifyRequiredFields();
      await formslistpage.EBO_Personnel_VerifyCrewMembersDropdown();
      await formslistpage.EBO_ClickSaveAndContinueBtn("Personnel");
    });

    await tb.testStep("Validate EBO Form Submission", async () => {
    await formslistpage.JSB_VerifyCompleteFormButtonFunctionality();
    });
  });
});


test.describe.only("Sanity Checklist - PDF Content Validation", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let formslistpage: FormListPage;
  let webContent: string;
  let normalizedWebContent: string;
  let webAttachments: {photos: number, documents: number, details: string};

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/jsb-summary-validation",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    formslistpage = new FormListPage(page);
    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test("Should validate content of saved PDF against the web summary page", async () => {
    await tb.testStep("Verify Home page loaded after login", async () => {
      await expect(page).toHaveURL(/.*projects/);
      await homepage.waitForHomePageLoad();
    });

    await tb.testStep("Navigate to the main Forms List page", async () => {
      await homepage.NavigateToFormsListTab();
      await expect(page.getByRole('heading', { name: 'Forms' })).toBeVisible();
    });

    await tb.testStep("Navigate to and open the most recent completed JSB form", async () => {
      await formslistpage.RecentCompletedJSBForm(); 
      await formslistpage.isRightSideSectionVisible();
      await tb.logSuccess("Successfully opened a completed JSB form.");
    });

    await tb.testStep("Open the JSB Summary page and extract web content", async () => {
      await formslistpage.openSummaryPage();
      await tb.logSuccess("JSB Summary page is visible.");      
      await page.waitForTimeout(5000);
      
      // Extract web content BEFORE triggering print preview to avoid navigation issues
      webContent = await formslistpage.getSummaryPageContent();
      normalizedWebContent = normalizeText(webContent, false);
      
      // Get attachment information from JSB Summary specifically
      webAttachments = await formslistpage.getSummaryPageAttachmentInfo();
      
      await tb.logSuccess("Successfully extracted web content before triggering print preview.");
      
      // Now trigger the print preview for manual PDF download
      await formslistpage.triggerPrintPreview();
      
      // Give extra time for manual download process
      await tb.logSuccess("Waiting for manual PDF download to complete...");
      await page.waitForTimeout(10000); // 10 seconds for manual save
      
    });

    await tb.testStep("Comprehensive JSB Summary vs PDF Content Validation", async () => {
      // Use the pre-extracted web content to avoid navigation issues
      // webContent, normalizedWebContent, and webAttachments are already available from the previous step

      // 3. Define the path to the PDF (either automatically downloaded or manually saved)
      let manualPdfPath = path.join(process.cwd(), "Worker Safety _ Urbint.pdf");
      
      // Debug: Log the expected path and check if file exists
      await tb.logSuccess(`Looking for PDF at: ${manualPdfPath}`);
      await tb.logSuccess(`Current working directory: ${process.cwd()}`);
      
      // Wait longer for PDF download to complete with enhanced monitoring
      await page.waitForTimeout(5000);
      
      // Enhanced PDF download waiting with file stability check
      const waitForPdfDownload = async (filePath: string, maxWaitTime: number = 60000): Promise<boolean> => {
        const startTime = Date.now();
        let lastSize = -1;
        let stableCount = 0;
        const requiredStableChecks = 3; // File size must be stable for 3 checks
        
        while (Date.now() - startTime < maxWaitTime) {
          try {
            if (fs.existsSync(filePath)) {
              const stats = fs.statSync(filePath);
              const currentSize = stats.size;
              
              if (currentSize > 0) {
                if (currentSize === lastSize) {
                  stableCount++;
                  if (stableCount >= requiredStableChecks) {
                    await tb.logSuccess(`PDF download completed. Final size: ${currentSize} bytes`);
                    return true;
                  }
                } else {
                  stableCount = 0; // Reset if size is still changing
                }
                lastSize = currentSize;
                await tb.logSuccess(`PDF downloading... Current size: ${currentSize} bytes (stable checks: ${stableCount}/${requiredStableChecks})`);
              } else {
                await tb.logSuccess(`PDF file exists but is empty, continuing to wait...`);
              }
            } else {
              await tb.logSuccess(`PDF file not yet created, waiting...`);
            }
          } catch (error) {
            await tb.logSuccess(`Error checking PDF file: ${error}`);
          }
          
          await page.waitForTimeout(1000); // Check every second
        }
        
        return false;
      };
      
      // List all PDF files in the current directory for debugging
      try {
        const files = fs.readdirSync(process.cwd());
        const pdfFiles = files.filter(file => file.toLowerCase().endsWith('.pdf'));
        await tb.logSuccess(`PDF files found in directory: ${pdfFiles.join(', ')}`);
      } catch (dirError) {
        await tb.logSuccess(`Error reading directory: ${dirError}`);
      }

      // Wait for PDF download to complete with enhanced stability checking
      await tb.logSuccess(`Waiting for PDF download to complete at: ${manualPdfPath}`);
      const downloadCompleted = await waitForPdfDownload(manualPdfPath, 60000); // Wait up to 60 seconds
      
      if (!downloadCompleted) {
        // Fallback to original retry mechanism if enhanced check fails
        await tb.logSuccess("Enhanced download check timed out, falling back to basic retry mechanism...");
        
        let pdfFound = false;
        let retryCount = 0;
        const maxRetries = 5; // Increased from 3 to 5
        
        while (!pdfFound && retryCount < maxRetries) {
          await tb.logSuccess(`Checking for PDF at: ${manualPdfPath} (attempt ${retryCount + 1})`);
          if (fs.existsSync(manualPdfPath)) {
            const stats = fs.statSync(manualPdfPath);
            if (stats.size > 0) {
              pdfFound = true;
              await tb.logSuccess(`PDF found on attempt ${retryCount + 1} with size: ${stats.size} bytes`);
              break;
            } else {
              await tb.logSuccess(`PDF exists but is empty (${stats.size} bytes), continuing to wait...`);
            }
          }
          
          if (!pdfFound) {
            retryCount++;
            const waitTime = Math.min(3000 * retryCount, 10000); // Exponential backoff, max 10 seconds
            await tb.logSuccess(`PDF not found or empty, retrying in ${waitTime/1000} seconds... (attempt ${retryCount}/${maxRetries})`);
            await page.waitForTimeout(waitTime);
          }
        }
        
        if (!pdfFound) {
          await tb.logFailure(`PDF file not found at: ${manualPdfPath} after ${maxRetries} attempts`);
          await tb.logFailure("Please ensure the PDF was downloaded automatically or manually save it as 'Worker Safety _ Urbint.pdf' in the project root directory.");
          throw new Error(`PDF file not found after enhanced waiting. Expected path: ${manualPdfPath}`);
        }
      }

      // 4. Read the text content from the PDF
      const pdfContent = await tb.readPdfContent(manualPdfPath);
      const normalizedPdfContent = normalizeText(pdfContent, true);

      // 5. Get attachment information from PDF
      const pdfAttachments = await tb.getPdfAttachmentInfo(manualPdfPath);

      // Debug: Log content lengths and sample content
      console.log(`📊 COMPREHENSIVE CONTENT EXTRACTION RESULTS:`);
      console.log(`   Web JSB Summary length: ${normalizedWebContent.length} characters`);
      console.log(`   PDF content length: ${normalizedPdfContent.length} characters`);
      console.log(`   Web content sample: ${normalizedWebContent.substring(0, 300)}...`);
      console.log(`   PDF content sample: ${normalizedPdfContent.substring(0, 300)}...`);
      console.log(`   Web attachments: ${webAttachments.photos} photos, ${webAttachments.documents} documents`);
      console.log(`   PDF attachments: ${pdfAttachments.photos} photos, ${pdfAttachments.documents} documents`);
      
      await tb.logSuccess(`Web JSB Summary length: ${normalizedWebContent.length} characters`);
      await tb.logSuccess(`PDF content length: ${normalizedPdfContent.length} characters`);
      await tb.logSuccess(`Web attachments: ${webAttachments.photos} photos, ${webAttachments.documents} documents`);
      await tb.logSuccess(`PDF attachments: ${pdfAttachments.photos} photos, ${pdfAttachments.documents} documents`);
      
      // 6.a Build JSON from raw contents and compare
      const webJson = tb.buildWebSummaryJSON(webContent);
      const pdfJson = tb.buildPdfSummaryJSON(pdfContent);
      const jsonCompare = tb.compareJSBSummaries(webJson, pdfJson);

      // Persist JSON artifacts for inspection
      fs.writeFileSync('web_summary.json', JSON.stringify(webJson, null, 2));
      fs.writeFileSync('pdf_summary.json', JSON.stringify(pdfJson, null, 2));
      fs.writeFileSync('json_compare_summary.json', JSON.stringify(jsonCompare, null, 2));

      await tb.logSuccess(`🧩 JSON comparison: ${jsonCompare.matchPercentage}% (${jsonCompare.matchedKeys}/${jsonCompare.totalKeys})`);
      if (jsonCompare.missingInWeb.length) {
        await tb.logFailure(`JSON missing in Web: ${jsonCompare.missingInWeb.join(', ')}`);
      }
      if (jsonCompare.missingInPdf.length) {
        await tb.logFailure(`JSON missing in PDF: ${jsonCompare.missingInPdf.join(', ')}`);
      }
      for (const m of jsonCompare.mismatches.slice(0, 10)) {
        await tb.logFailure(`JSON mismatch ${m.key}: sim=${m.similarity}% | web="${m.web}" | pdf="${m.pdf}"`);
      }

      // 6. Validate all JSB sections are present in both web and PDF
      const requiredJSBSections = [
        "Job Information",
        "Medical & Emergency",
        "Tasks",
        "Energy Source Controls", 
        "Work Procedures",
        "Site Conditions",
        "Attachments"
      ];

      let webSectionsFound = 0;
      let pdfSectionsFound = 0;
      const webMissingSections = [];
      const pdfMissingSections = [];

      for (const section of requiredJSBSections) {
        // Remove spaces from section names to match normalized content
        const normalizedSection = section.replace(/\s+/g, "").toLowerCase();
        const webHasSection = normalizedWebContent.includes(normalizedSection);
        const pdfHasSection = normalizedPdfContent.includes(normalizedSection);
        
        if (webHasSection) {
          webSectionsFound++;
        } else {
          webMissingSections.push(section);
        }
        
        if (pdfHasSection) {
          pdfSectionsFound++;
        } else {
          pdfMissingSections.push(section);
        }
      }

      await tb.logSuccess(`✅ Web sections found: ${webSectionsFound}/${requiredJSBSections.length}`);
      await tb.logSuccess(`✅ PDF sections found: ${pdfSectionsFound}/${requiredJSBSections.length}`);
      
      if (webMissingSections.length > 0) {
        await tb.logSuccess(`⚠️ Web missing sections: ${webMissingSections.join(', ')}`);
      }
      if (pdfMissingSections.length > 0) {
        await tb.logSuccess(`⚠️ PDF missing sections: ${pdfMissingSections.join(', ')}`);
      }

      // 7. Compare content similarity (character-based since spaces are removed)
      // Use substring matching for better comparison of space-removed content
      const webLength = normalizedWebContent.length;
      const pdfLength = normalizedPdfContent.length;
      
      // Calculate how much of the web content appears in the PDF
      let matchedChars = 0;
      const chunkSize = 10; // Compare in chunks of 10 characters
      
      for (let i = 0; i <= webLength - chunkSize; i += chunkSize) {
        const webChunk = normalizedWebContent.substring(i, i + chunkSize);
        if (normalizedPdfContent.includes(webChunk)) {
          matchedChars += chunkSize;
        }
      }
      
      const contentMatchPercentage = (matchedChars / webLength) * 100;
      
      await tb.logSuccess(`📊 Content preservation: ${contentMatchPercentage.toFixed(1)}% of web content found in PDF`);

      console.log(`📊 COMPREHENSIVE VALIDATION RESULTS:`);
      console.log(`   Web sections: ${webSectionsFound}/${requiredJSBSections.length} (${(webSectionsFound/requiredJSBSections.length*100).toFixed(1)}%)`);
      console.log(`   PDF sections: ${pdfSectionsFound}/${requiredJSBSections.length} (${(pdfSectionsFound/requiredJSBSections.length*100).toFixed(1)}%)`);
      console.log(`   Content preservation: ${contentMatchPercentage.toFixed(1)}%`);
      console.log(`   Attachment validation: Web(${webAttachments.photos}p,${webAttachments.documents}d) vs PDF(${pdfAttachments.photos}p,${pdfAttachments.documents}d)`);
      
            // 8. Content Analysis and Discrepancy Reporting (Focus on detecting errors, not pass/fail)
      
      // Basic sanity checks - ensure both sources have content
      expect(normalizedWebContent.length, "Web JSB Summary should contain substantial content").toBeGreaterThan(100);
      expect(normalizedPdfContent.length, "PDF should contain substantial JSB summary content").toBeGreaterThan(100);
      
      // Attachment comparison for discrepancy detection
      const attachmentMatch = (webAttachments.photos === pdfAttachments.photos && webAttachments.documents === pdfAttachments.documents);
      
      // Comprehensive discrepancy reporting
      await tb.logSuccess(`📊 CONTENT VALIDATION ANALYSIS:`);
      await tb.logSuccess(`   • Web sections found: ${webSectionsFound}/${requiredJSBSections.length} (${((webSectionsFound/requiredJSBSections.length)*100).toFixed(1)}%)`);
      await tb.logSuccess(`   • PDF sections found: ${pdfSectionsFound}/${requiredJSBSections.length} (${((pdfSectionsFound/requiredJSBSections.length)*100).toFixed(1)}%)`);
      await tb.logSuccess(`   • Text content similarity: ${contentMatchPercentage.toFixed(1)}%`);
      await tb.logSuccess(`   • JSON field match: ${jsonCompare.matchPercentage}% (${jsonCompare.matchedKeys}/${jsonCompare.totalKeys} fields)`);
      await tb.logSuccess(`   • Attachment match: ${attachmentMatch ? 'YES' : 'NO'} - Web(${webAttachments.photos}p,${webAttachments.documents}d) vs PDF(${pdfAttachments.photos}p,${pdfAttachments.documents}d)`);
      
      // Report potential issues for investigation (informational alerts)
      if (contentMatchPercentage < 50) {
        await tb.logSuccess(`🔍 LOW TEXT SIMILARITY: ${contentMatchPercentage.toFixed(1)}% - May indicate extraction or formatting differences`);
      }
      if (jsonCompare.matchPercentage < 70) {
        await tb.logSuccess(`🔍 LOW FIELD MATCH: ${jsonCompare.matchPercentage}% - Review structural content differences`);
      }
      if (!attachmentMatch) {
        await tb.logSuccess(`🔍 ATTACHMENT MISMATCH: Different counts between web and PDF`);
      }
      
      // ===== VALIDATION ASSERTIONS - FAIL THE TEST IF CRITICAL ISSUES FOUND =====
      
      // Calculate total issues for accurate reporting
      const totalIssues = jsonCompare.missingInWeb.length + jsonCompare.missingInPdf.length + jsonCompare.mismatches.length + pdfMissingSections.length;
      
      if (totalIssues > 0) {
        await tb.logFailure(`❌ VALIDATION FAILED: Found ${totalIssues} total issues between Web and PDF`);
      }
      
      // 1. Check for fields that exist in PDF but are missing in Web
      if (jsonCompare.missingInWeb.length > 0) {
        const missingFields = jsonCompare.missingInWeb.join(', ');
        await tb.logFailure(`❌ Web is missing ${jsonCompare.missingInWeb.length} fields that exist in PDF: ${missingFields}`);
        expect(jsonCompare.missingInWeb.length, `Web is missing these fields that exist in PDF: ${missingFields}`).toBe(0);
      }
      
      // 2. Check for fields that exist in Web but are missing in PDF  
      if (jsonCompare.missingInPdf.length > 0) {
        const missingFields = jsonCompare.missingInPdf.join(', ');
        await tb.logFailure(`❌ PDF is missing ${jsonCompare.missingInPdf.length} fields that exist in Web: ${missingFields}`);
        expect(jsonCompare.missingInPdf.length, `PDF is missing these fields that exist in Web: ${missingFields}`).toBe(0);
      }
      
      // 3. Check for content mismatches between Web and PDF
      if (jsonCompare.mismatches.length > 0) {
        await tb.logFailure(`❌ Found ${jsonCompare.mismatches.length} content mismatches between Web and PDF:`);
        for (const mismatch of jsonCompare.mismatches) {
          await tb.logFailure(`   • ${mismatch.key}: Web="${mismatch.web}" | PDF="${mismatch.pdf}" | Similarity=${mismatch.similarity}%`);
        }
        const mismatchDetails = jsonCompare.mismatches.map(m => `${m.key}(${m.similarity}%): Web="${m.web}" vs PDF="${m.pdf}"`).join('\n   ');
        expect(jsonCompare.mismatches.length, `Found content mismatches between Web and PDF:\n   ${mismatchDetails}`).toBe(0);
      }
      
      // 4. Check for sections that exist in Web but are missing in PDF
      if (pdfMissingSections.length > 0) {
        const missingSections = pdfMissingSections.join(', ');
        await tb.logFailure(`❌ PDF is missing ${pdfMissingSections.length} JSB sections that exist in Web: ${missingSections}`);
        expect(pdfMissingSections.length, `PDF is missing these JSB sections that exist in Web: ${missingSections}`).toBe(0);
      }
      
      // // 5. Overall content preservation check - PDF should contain most of the Web content
      // if (contentMatchPercentage < 90) {
      //   await tb.logFailure(`❌ Low content preservation: Only ${contentMatchPercentage.toFixed(1)}% of Web content found in PDF`);
      //   expect(contentMatchPercentage, `PDF should preserve at least 90% of Web content, but only found ${contentMatchPercentage.toFixed(1)}%`).toBeGreaterThanOrEqual(90);
      // }
      
      // // 6. JSON field match should be high
      // if (jsonCompare.matchPercentage < 95) {
      //   await tb.logFailure(`❌ Low JSON field match: Only ${jsonCompare.matchPercentage}% of fields match between Web and PDF`);
      //   expect(jsonCompare.matchPercentage, `Web vs PDF field match should be at least 95%, but got ${jsonCompare.matchPercentage}%`).toBeGreaterThanOrEqual(95);
      // }
        
        // Wait and then log the actual compared texts for user review
        await tb.logSuccess("⏳ Preparing detailed content comparison for review...");
        await page.waitForTimeout(2000);
        
        // Save detailed comparison to file for complete review
//         const comparisonContent = `📄 ========== DETAILED CONTENT COMPARISON ==========
// 🌐 WEB JSB SUMMARY CONTENT (Normalized - ${normalizedWebContent.length} chars):
// ${"=".repeat(80)}
// ${normalizedWebContent}
// ${"=".repeat(80)}

// 📋 PDF CONTENT (Normalized - ${normalizedPdfContent.length} chars):
// ${"=".repeat(80)}
// ${normalizedPdfContent}
// ${"=".repeat(80)}

// 📊 ANALYSIS:
// - Content Match: ${contentMatchPercentage.toFixed(1)}%
// - Web Sections: ${webSectionsFound}/${requiredJSBSections.length}
// - PDF Sections: ${pdfSectionsFound}/${requiredJSBSections.length}
// - Web Attachments: ${webAttachments.photos} photos, ${webAttachments.documents} documents
// - PDF Attachments: ${pdfAttachments.photos} photos, ${pdfAttachments.documents} documents

// 📄 ========== END CONTENT COMPARISON ==========`;
        
//         fs.writeFileSync('content_comparison_detailed.txt', comparisonContent);
        
//         await tb.logSuccess("📄 ========== DETAILED CONTENT COMPARISON ==========");
//         await tb.logSuccess("🌐 WEB JSB SUMMARY CONTENT (Normalized):");
//         await tb.logSuccess("=" .repeat(80));
//         await tb.logSuccess(normalizedWebContent);
//         await tb.logSuccess("=" .repeat(80));
        
//         await tb.logSuccess("📋 PDF CONTENT (Normalized):");
//         await tb.logSuccess("=" .repeat(80));
//         await tb.logSuccess(normalizedPdfContent);
//         await tb.logSuccess("=" .repeat(80));
//         await tb.logSuccess("📄 ========== END CONTENT COMPARISON ==========");
//         await tb.logSuccess(`💾 Complete detailed comparison saved to: content_comparison_detailed.txt`);
    });
  });
});

