import {
  test,
  BrowserContext,
  Page,
  chromium,
  Browser,
} from "@playwright/test";
//import TestBase, { ReportFilePaths } from "../Util/TestBase";
import { writeMetricsToHTML } from "../Data/index";
import { setProjectName } from "../Util/TestBase";
import LoginPage from "../Page/Login.page";
import * as path from "path";
import os from "os";

import { threadId } from "worker_threads";
import { json } from "stream/consumers";
import { before } from "node:test";
import { lutimes } from "fs";

let playAudit: any;
let loginpage: LoginPage;
let page: Page;
//let tb: TestBase;
let url: any;
//let context:any;
let browser: Browser;
let environmentData: any;
let environment: any;
const userDataDir = "/path/to/data/dir";
before(async () => {});
test.beforeAll(async ({}, testInfo) => {
  try {
    setProjectName(testInfo.project.name);
  } catch (error) {
    console.error("Error setting project name:", error);
    throw error; // Fail the test explicitly
  }

  const userDataDir = path.join(os.tmpdir(), "pw", String(Math.random()));

  const lighthouse = await import("playwright-lighthouse");
  playAudit = lighthouse.playAudit;

  //const context=await browser.newContext();
  const context = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    args: ["--remote-debugging-port=9222"],
  });

  page = context.pages()[0];
  //tb = new TestBase(page);
  loginpage = new LoginPage(page);
  //await tb.goto();

  await page.waitForTimeout(10000);
  loginpage.Login();
});

test.afterAll(async () => {
  await page.close();
});

test.skip(`Lighthouse performance test with averages for LCP, FCP,Total Blocking Time ,Speed Index and CLS`, async ({
  page,
}, testInfo) => {
  const opts = {
    disableStorageReset: true,
    logLevel: "info",
  };

  const relativePath = process.env.RELATIVE_PATH || "";
  if (!relativePath) {
    throw new Error("RELATIVE_PATH environment variable is not defined!");
  }

  url = await loginpage.getURL();
  const targetURL = `${url}${relativePath}`;
  console.log(`Running Lighthouse test on URL: ${targetURL}`);

  // Store results for multiple runs
  let lcpValues: number[] = [];
  let fcpValues: number[] = [];
  let clsValues: number[] = [];
  let totalBlockingTimeValues = [];
  let speedIndexValues = [];
  let performanceValues: number[] = [];

  // Run Lighthouse 3 times
  for (let i = 0; i < 3; i++) {
    console.log(`Running Lighthouse iteration ${i + 1}...`);

    const LightHouseResult = await playAudit({
      url: targetURL,
      page: page,
      opts,
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
        performance: 20,
        accessibility: 20,
        seo: 20,
      },
      port: 9222,
      reports: {
        formats: {
          html: true,
          json: true,
        },
        directory: "./lighthouse-reports",
        name: relativePath,
      },
    });

    const fcpAudit = LightHouseResult.lhr.audits["first-contentful-paint"];
    const lcpAudit = LightHouseResult.lhr.audits["largest-contentful-paint"];
    const clsAudit = LightHouseResult.lhr.audits["cumulative-layout-shift"];
    const perfAudit = LightHouseResult.lhr.categories.performance.score * 100;
    const tbt = LightHouseResult.lhr.audits["total-blocking-time"];
    const si = LightHouseResult.lhr.audits["speed-index"];
    console.log(`ttbt: ${tbt.numericValue} ms`);
    console.log(`Speed Index: ${si.numericValue} ms`);

    console.log(`Iteration ${i + 1} Results:`);
    console.log(`First Contentful Paint (FCP): ${fcpAudit.numericValue} ms`);
    console.log(`Largest Contentful Paint (LCP): ${lcpAudit.numericValue} ms`);
    console.log(`Cumulative Layout Shift (CLS): ${clsAudit.numericValue} ms`);
    lcpValues.push(lcpAudit.numericValue);
    fcpValues.push(fcpAudit.numericValue);
    clsValues.push(clsAudit.numericValue);
    totalBlockingTimeValues.push(tbt.numericValue);
    speedIndexValues.push(si.numericValue);
    performanceValues.push(perfAudit);
  }

  const avgLCP = lcpValues.reduce((a, b) => a + b, 0) / lcpValues.length;
  const avgFCP = fcpValues.reduce((a, b) => a + b, 0) / fcpValues.length;
  const avgCLS = clsValues.reduce((a, b) => a + b, 0) / clsValues.length;
  const avgTBT =
    totalBlockingTimeValues.reduce((a, b) => a + b, 0) /
    totalBlockingTimeValues.length;
  const avgSI =
    speedIndexValues.reduce((a, b) => a + b, 0) / speedIndexValues.length;
  const avgPerformance =
    performanceValues.reduce((a, b) => a + b, 0) / performanceValues.length;
  const value = Math.round(avgPerformance);
  console.log(`\nAverage Results (3 runs):`);
  console.log(`Average LCP: ${avgLCP} ms`);
  console.log(`Average FCP: ${avgFCP} ms`);
  console.log(`Average CLS: ${avgCLS} ms`);
  console.log(`Average totalBlockingTime: ${avgTBT} ms`);
  console.log(`Average Speed Index: ${avgSI} ms`);
  console.log(`Average performance : ${value} `);

  writeMetricsToHTML({
    LCP: avgLCP,
    FCP: avgFCP,
    CLS: avgCLS,
    SI: avgSI,
    TBT: avgTBT,
    Performance: value,
    relativePath: relativePath,
  });
});
