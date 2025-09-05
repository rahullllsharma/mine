import os from "os";
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
import { CURRENT_ENV, CURRENT_TENANT } from "../Data/envConfig";
import workPackageData from "../Data/workPackageSample.data.json";
import AdminPage from "../Page/Admin.page";
import InsightsPage from "../Page/Insights.page";
import FormListPage from "../Page/FormList.page";
import CWFPage from "../Page/cwf.page";
import dotenv from "dotenv";
dotenv.config();

test.describe("Smoke Suite - Network Monitoring and Navigation", () => {
  let context: BrowserContext;
  let page: Page;
  let tb: TestBase;
  let loginpage: LoginPage;
  let homepage: HomePage;
  let workPackagePage: WorkPackagePage;
  let mapPage: MapPage;
  let adminPage: AdminPage;
  let insightsPage: InsightsPage;
  let formListPage: FormListPage;
  let cwfPage: CWFPage;
  let playAudit: any;

  // Shared variable to store discovered tabs and URLs
  let discoveredTabsWithUrls: Array<{ name: string; url: string }> = [];

  test.beforeEach(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      recordVideo: {
        dir: "test-results/videos/network-monitoring-all-tabs",
      },
    });
    page = await context.newPage();
    setProjectName(testInfo.project.name);
    tb = new TestBase(page);
    loginpage = new LoginPage(page);
    homepage = new HomePage(page);
    workPackagePage = new WorkPackagePage(page);
    mapPage = new MapPage(page);
    adminPage = new AdminPage(page);
    insightsPage = new InsightsPage(page);
    formListPage = new FormListPage(page);
    cwfPage = new CWFPage(page);

    const lighthouse = await import("playwright-lighthouse");
    playAudit = lighthouse.playAudit;

    await tb.goto();
    await loginpage.Login();
    await page.waitForTimeout(2000);
  });

  test.afterEach(async () => {
    await context.close();
    await tb.clearNetworkLogs();
  });

  test("Network Monitoring and Navigation - All Tabs", async () => {
    const performTabSpecificActions = async (
      tab: { name: string; url: string },
      page: Page,
      tb: TestBase
    ) => {
      const tabNameLower = tab.name.toLowerCase();
      const url = tab.url;

      try {
        // Projects/Work Packages tab
        if (url.includes("projects")) {
          await tb.logMessage(
            `Add actions accordingly for ${tab.name} tab`
          );
          await page.waitForTimeout(2000);
        }
        // Map tab
        else if (url.includes("map")) {
          await tb.logMessage(
            `Please add tab actions for: ${tab.name} Tab, based on requirements`
          );
        }
        // Hardcoded Forms List tab
        else if (url.includes("forms") && !url.includes("template")) {
          await tb.logMessage(
            `Performing Forms List tab actions for: ${tab.name}`
          );
        }
        // Template Forms tab
        else if (url.includes("template-forms")) {
          await tb.logMessage(
            `Performing Template Forms tab actions for: ${tab.name}`
          );
          await cwfPage.clickOnTemplateFormsFiltersBtn();
          await cwfPage.validateTemplateFormFilterOptions();
        }
        // Insights tab
        else if (url.includes("insights")) {
          await tb.logMessage(
            `Performing Insights tab actions for: ${tab.name}`
          );
          await insightsPage.validateInsightsPageUI();
        }
        // Admin tab
        else if (url.includes("admin")) {
          await tb.logMessage(`Performing Admin tab actions for: ${tab.name}`);
          await adminPage.verifyInsightsButton();
          await adminPage.validateInsightsPageUI();
        }
        // Templates tab
        else if (url.includes("templates") && !url.includes("template-forms")) {
          await tb.logMessage(
            `Performing Templates tab actions for: ${tab.name}`
          );
          await page.waitForTimeout(2000);
        }
        // Default action for unknown tabs
        else {
          await tb.logMessage(
            `No specific actions defined for ${tab.name} tab, performing basic validation`
          );
          await page.waitForTimeout(2000);
        }
      } catch (error) {
        await tb.logMessage(
          `Error performing actions for ${tab.name} tab: ${error}`
        );
      }
    };

    // Helper function to run Lighthouse performance test for a tab
    const runLighthousePerformanceTest = async (
      tabName: string,
      tabUrl: string,
      tb: TestBase
    ): Promise<any> => {
      // Get cookies from the main authenticated context
      const cookies = await context.cookies();

      try {
        const uniquePort = 9222; // Create a new browser context for Lighthouse test, Single port since we only run once

        const lighthouseContext = await chromium.launchPersistentContext(
          path.join(os.tmpdir(), "pw", String(Math.random())),
          {
            headless: true,
            args: [`--remote-debugging-port=${uniquePort}`],
          }
        );

        const lighthousePage = lighthouseContext.pages()[0];

        try {
          // Set cookies in the Lighthouse context to maintain persistent authentication
          await lighthouseContext.addCookies(cookies);

          const lighthouseResult = await playAudit({
            url: tabUrl,
            page: lighthousePage,
            opts: {
              disableStorageReset: true,
              logLevel: "info",
            },
            config: {
              extends: "lighthouse:default",
              settings: {
                formFactor: "desktop",
                screenEmulation: {
                  mobile: false,
                  width: 1920,
                  height: 1080,
                  deviceScaleFactor: 1,
                  disabled: false,
                },
                onlyCategories: [
                  "performance",
                  "accessibility",
                  "best-practices",
                  "seo",
                ],
                onlyAudits: [
                  "largest-contentful-paint",
                  "first-contentful-paint",
                  "cumulative-layout-shift",
                  "first-input-delay",
                ],
              },
            },
            thresholds: {
              performance: 40,
              accessibility: 70,
              seo: 70,
            },
            port: uniquePort,
            reports:
              process.env.LIGHTHOUSE_HTML === "1"
                ? {
                    formats: {
                      html: true,
                    },
                    directory: "./lighthouse-reports",
                    name: `${tabName.toLowerCase().replace(/\s+/g, "-")}-tab`,
                  }
                : undefined,
          });

          // Extract metrics from Lighthouse result
          const fcpAudit =
            lighthouseResult.lhr.audits["first-contentful-paint"];
          const lcpAudit =
            lighthouseResult.lhr.audits["largest-contentful-paint"];
          const clsAudit =
            lighthouseResult.lhr.audits["cumulative-layout-shift"];
          const perfAudit =
            lighthouseResult.lhr.categories.performance.score * 100;
          const accessibilityAudit =
            lighthouseResult.lhr.categories.accessibility.score * 100;
          const seoAudit = lighthouseResult.lhr.categories.seo.score * 100;
          const tbt = lighthouseResult.lhr.audits["total-blocking-time"];
          const si = lighthouseResult.lhr.audits["speed-index"];

          const result = {
            performance: perfAudit,
            accessibility: accessibilityAudit,
            seo: seoAudit,
            firstContentfulPaint: fcpAudit?.numericValue || 0,
            largestContentfulPaint: lcpAudit?.numericValue || 0,
            speedIndex: si?.numericValue || 0,
            totalBlockingTime: tbt?.numericValue || 0,
            cumulativeLayoutShift: clsAudit?.numericValue || 0,
          };

          await tb.logMessage(`Lighthouse result: ${JSON.stringify(result)}`);
          await tb.logSuccess(`Lighthouse test completed for ${tabName}`);

          return result;
        } finally {
          await lighthouseContext.close();
        }
      } catch (error) {
        await tb.logFailure(`Lighthouse test failed for ${tabName}: ${error}`);
        throw new Error(`Lighthouse test failed for ${tabName}: ${error}`);
      }
    };

    await tb.testStep("Verify Landing page loaded after login", async () => {
      await tb.startNetworkMonitoring();
      await page.waitForTimeout(10000);
      await page.reload();
      await page.waitForTimeout(15000);
      await tb.logSuccess(
        `Testing in ${CURRENT_ENV} environment for tenant: ${CURRENT_TENANT}`
      );
    });

    // Dynamic Tab Discovery and Navigation
    await tb.testStep("Discover and monitor all available tabs", async () => {
      await tb.logMessage(
        "Starting dynamic tab discovery and network monitoring"
      );

      const availableTabs = await homepage.getAllAvailableTabs();
      await tb.logSuccess(
        `Found ${availableTabs.length} tabs: ${availableTabs
          .map((tab) => tab.name)
          .join(", ")}`
      );

      // Monitor each tab dynamically and store URLs for performance testing
      for (const tab of availableTabs) {
        await tb.testStep(
          `Monitor ${tab.name} tab network calls, perform tab-specific actions and run Lighthouse test`,
          async () => {
            await tb.clearNetworkLogs();
            await tb.startNetworkMonitoring();
            await tb.logMessage(
              `Starting network monitoring for ${tab.name} tab`
            );

            // Navigate to the tab
            const navigationResult = await homepage.navigateToTab(tab.name);

            if (navigationResult.success && navigationResult.url) {
              // Store tab and URL for future reference
              discoveredTabsWithUrls.push({
                name: tab.name,
                url: navigationResult.url,
              });

              // Wait for page to be mostly loaded
              await page.waitForLoadState("domcontentloaded");
              // Allow UI to settle
              await page.waitForTimeout(2000);

              // Run Lighthouse performance test
              const performanceMetrics = await runLighthousePerformanceTest(
                tab.name,
                navigationResult.url,
                tb
              );

              // Store result for summary later
              if (!(globalThis as any).performanceResults)
                (globalThis as any).performanceResults = [];
              (globalThis as any).performanceResults.push({
                tabName: tab.name,
                metrics: performanceMetrics,
              });

              // Perform tab-specific actions based on URL patterns
              await performTabSpecificActions(
                { name: tab.name, url: navigationResult.url },
                page,
                tb
              );
              await page.waitForTimeout(3000);

              await tb.captureScreenshot(
                page,
                `${tab.name
                  .toLowerCase()
                  .replace(/\s+/g, "-")}-tab-network-monitoring`
              );
              await tb.logSuccess(
                `${tab.name} tab network monitoring and performance testing completed`
              );
            } else {
              await tb.logMessage(
                `Skipping ${tab.name} tab due to navigation failure`
              );
              throw new Error(
                `Failed due to ${tab.name} tab navigation failure`
              );
            }
          }
        );
      }
    });

    // Log all error calls from all tabs
    await tb.testStep("Log all network error calls", async () => {
      await tb.logErrorCalls();
      await tb.logSuccess("Network monitoring test completed for all tabs");
    });

    // Generate performance summary
    await tb.testStep("Generate Performance Summary", async () => {
      const performanceResults = (globalThis as any).performanceResults || [];

      if (performanceResults.length > 0) {
        await tb.logSuccess(
          `Performance testing completed for ${performanceResults.length} tabs`
        );

        // Log summary of all results
        await tb.logMessage("Performance Summary:");
        for (const result of performanceResults) {
          const metrics = result.metrics;
          await tb.logMessage(
            `  ${result.tabName}: Performance=${metrics.performance}, 
            Accessibility=${metrics.accessibility}, 
            SEO=${metrics.seo},
            LCP=${metrics.largestContentfulPaint.toFixed(
              2
            )}ms, FCP=${metrics.firstContentfulPaint.toFixed(
              2
            )}ms, SI=${metrics.speedIndex.toFixed(2)}ms`
          );
        }

        // Calculate combined averages
        const avgMetrics = {
          LCP:
            performanceResults.reduce(
              (sum: number, r: any) => sum + r.metrics.largestContentfulPaint,
              0
            ) / performanceResults.length,
          FCP:
            performanceResults.reduce(
              (sum: number, r: any) => sum + r.metrics.firstContentfulPaint,
              0
            ) / performanceResults.length,
          CLS:
            performanceResults.reduce(
              (sum: number, r: any) => sum + r.metrics.cumulativeLayoutShift,
              0
            ) / performanceResults.length,
          SI:
            performanceResults.reduce(
              (sum: number, r: any) => sum + r.metrics.speedIndex,
              0
            ) / performanceResults.length,
          TBT:
            performanceResults.reduce(
              (sum: number, r: any) => sum + r.metrics.totalBlockingTime,
              0
            ) / performanceResults.length,
          Performance: Math.round(
            performanceResults.reduce(
              (sum: number, r: any) => sum + r.metrics.performance,
              0
            ) / performanceResults.length
          ),
          Accessibility: Math.round(
            performanceResults.reduce(
              (sum: number, r: any) => sum + r.metrics.accessibility,
              0
            ) / performanceResults.length
          ),
          SEO: Math.round(
            performanceResults.reduce(
              (sum: number, r: any) => sum + r.metrics.seo,
              0
            ) / performanceResults.length
          ),
        };

        await tb.logSuccess("Overall Performance Averages:");
        await tb.logMessage(`  Performance Score: ${avgMetrics.Performance}`);
        await tb.logMessage(
          `  Accessibility Score: ${avgMetrics.Accessibility}`
        );
        await tb.logMessage(`  SEO Score: ${avgMetrics.SEO}`);
        await tb.logMessage(
          `  Largest Contentful Paint: ${avgMetrics.LCP.toFixed(2)} ms`
        );
        await tb.logMessage(
          `  First Contentful Paint: ${avgMetrics.FCP.toFixed(2)} ms`
        );
        await tb.logMessage(`  Speed Index: ${avgMetrics.SI.toFixed(2)} ms`);
        await tb.logMessage(
          `  Total Blocking Time: ${avgMetrics.TBT.toFixed(2)} ms`
        );
        await tb.logMessage(
          `  Cumulative Layout Shift: ${avgMetrics.CLS.toFixed(3)}`
        );
        await tb.logSuccess("Performance summary logged to Allure report");
      } else {
        await tb.logMessage("No performance results to report");
      }
    });
  });
});
