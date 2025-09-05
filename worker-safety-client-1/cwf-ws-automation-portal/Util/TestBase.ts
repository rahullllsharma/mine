import { Locator, Page, Response } from "@playwright/test";
import * as allure from "allure-js-commons";
const moment = require("moment");
import * as fs from "fs";
import { getCurrentEnvUrl, CURRENT_ENV } from "../Data/envConfig";
import jsQR from "jsqr";
import { Jimp } from "jimp";

let projectName: string;

export function getProjectName(): string {
  if (!projectName) {
    throw new Error(
      "Project name is not set. Ensure setProjectName is called in beforeAll/beforeEach."
    );
  }
  return projectName;
}
export function setProjectName(name: string): void {
  projectName = name;
}

export default class TestBase {
  private page: Page;
  private networkLogs: Array<{
    url: string;
    status: number;
    method: string;
    timestamp: string;
  }> = [];
  private errorLogs: Array<{
    url: string;
    status: number;
    method: string;
    timestamp: string;
    errorDetails?: string;
  }> = [];

  constructor(page: Page) {
    this.page = page;
  }

  public async goto() {
    const baseURL = getCurrentEnvUrl();
    await this.page.goto(baseURL);
  }

  public async gotoPageURL(pageName: string) {
    const baseURL = getCurrentEnvUrl();
    await this.page.goto(`${baseURL}${pageName}`);
  }

  public get gettxtlogdatetime() {
    return moment(new Date()).format("DD-MMM-YYYY HH:mm:ss");
  }

  public async captureScreenshot(curpage: Page, description?: string) {
    await allure.step(`Captured Screenshot: ${description}`, async () => {
      description = description ?? "Unknown";
      const screenshot = await curpage.screenshot({ fullPage: true });
      await allure.attachment(description, screenshot, "image/png");
    });
  }

  public async ReportScreenShot(curpage: Page, description?: string) {
    const screenshotBuffer = await curpage.screenshot();
    description = description || "Unknown";
    await allure.attachment(description, screenshotBuffer, "image/png");
  }

  public async DeleteAllureResultsFolderData() {
    const parent_AllureResults_dir1 = "./allure-results/";
    if (fs.existsSync(parent_AllureResults_dir1)) {
      fs.readdir(parent_AllureResults_dir1, (err, files) => {
        if (err) throw err;
        for (const file of files) {
          fs.unlinkSync(parent_AllureResults_dir1 + file);
        }
      });
    }
  }

  public async testStepHeading(heading: string) {
    await allure.description(heading);
  }

  public async testStep(
    stepDescription: string,
    actionFunction: () => Promise<void> | void
  ): Promise<void> {
    await allure.step(stepDescription, async () => {
      try {
        await actionFunction();
        await this.logSuccess(`Step Completed: ${stepDescription}`);
      } catch (error) {
        await this.logMessage(`Step failed: ${stepDescription}`);
        throw error;
      }
    });
  }
  public async logMessage(message: string) {
    await allure.step(message, async () => {});
  }

  public parseParams(params: any): object {
    if (typeof params === "string") {
      try {
        return params.trim() ? JSON.parse(params) : {};
      } catch (jsonError) {
        console.warn(`Invalid JSON in Params: ${params}`);
        return {};
      }
    } else if (params !== null && typeof params === "object") {
      return params;
    }
    return {};
  }

  public parseQueryParams(endpoint: string, queryParams: any): string {
    let parsedEndpoint = endpoint;

    // Check if queryParams is a string and parse it to an object
    if (typeof queryParams === "string") {
      try {
        queryParams = JSON.parse(queryParams);
      } catch (jsonError) {
        console.warn(`Invalid JSON in QueryParams: ${queryParams}`);
        queryParams = {};
      }
    }

    // Replace placeholders in the endpoint with the corresponding values from queryParams
    for (const key in queryParams) {
      if (queryParams.hasOwnProperty(key)) {
        const value = queryParams[key];
        const placeholder = `{${key}}`;
        parsedEndpoint = parsedEndpoint.replace(
          new RegExp(placeholder, "g"),
          value
        );
      }
    }

    return parsedEndpoint;
  }

  public formatDuration(duration: number): string {
    const milliseconds = duration % 1000;
    const seconds = Math.floor((duration / 1000) % 60);
    const minutes = Math.floor((duration / (1000 * 60)) % 60);
    const hours = Math.floor((duration / (1000 * 60 * 60)) % 24);

    return `${hours}h ${minutes}m ${seconds}s ${milliseconds}ms`;
  }

  public async getElementText(selector: string): Promise<string> {
    return await allure.step(
      `Getting Element Text at locator: ${selector}`,
      async () => {
        const element = this.page.locator(selector);
        return (await element.textContent()) ?? "";
      }
    );
  }

  public async getInputElementPlaceholder(selector: string): Promise<string> {
    return await this.page.$eval(
      selector,
      (element) => (element as HTMLInputElement).placeholder
    );
  }

  public async validateInputElementPlaceholderText(
    selector: string,
    expectedText: string,
    elementDescription: string,
    pageName: string = "current",
    customPassMessage?: string,
    customFailMessage?: string
  ) {
    const actualText = await this.getInputElementPlaceholder(selector);
    const isPass = actualText === expectedText;
    const result = isPass ? "Pass ✅" : "Fail ❌";

    let message: string;

    if (isPass) {
      message =
        customPassMessage ||
        `${pageName} page contains expected text "${actualText}" for ${elementDescription}`;
    } else {
      message =
        customFailMessage ||
        `${pageName} page shows unexpected text "${actualText}" instead of "${expectedText}" for ${elementDescription}`;
    }

    await allure.step(`Result : ${result} : ${message}`, async () => {});

    return isPass;
  }

  // In TestBase.ts
  public async validateAndLogElementText(
    selector: string,
    expectedText: string,
    elementDescription: string,
    pageName: string = "current",
    customPassMessage?: string,
    customFailMessage?: string
  ) {
    const actualText = await this.getElementText(selector);
    const isPass = actualText.trim() === expectedText.trim();
    const result = isPass ? "Pass ✅" : "Fail ❌";

    let message: string;
    if (isPass) {
      message =
        customPassMessage ||
        `${pageName} page contains expected text "${actualText}" for ${elementDescription}`;
    } else {
      message =
        customFailMessage ||
        `${pageName} page shows unexpected text "${actualText}" instead of "${expectedText}" for ${elementDescription}`;
    }

    await allure.step(`Result : ${result} : ${message}`, async () => {});
  }

  public async logTestCaseAndDescription(
    testCaseId: string,
    description: string
  ) {
    await allure.step(`Test case id : ${testCaseId}`, async () => {});

    await allure.step(`Description : ${description}`, async () => {});
  }

  public async logSuccess(message: string) {
    await allure.step(`Result : Pass ✅ : ${message}`, async () => {});
  }

  public async logFailure(message: string) {
    await allure.step(`Result : Fail ❌ : ${message}`, async () => {});
  }

  public async logTestStart(testCaseId: string, description: string) {
    await this.logTestCaseAndDescription(testCaseId, description);
  }

  public async clickButton(
    locator: Locator,
    buttonName?: string
  ): Promise<void> {
    await allure.step(`Click ${buttonName} Button`, async () => {
      try {
        await locator.click();
        await this.logSuccess(`Successfully clicked ${buttonName} button`);
      } catch (error) {
        await this.logMessage(`Failed to click ${buttonName} button`);
        throw error;
      }
    });
  }

  public ensureBaseURL(baseURL: string | undefined): string {
    if (!baseURL) {
      throw new Error("baseURL is undefined. Please provide a valid baseURL.");
    }
    return baseURL;
  }

  public convertTextToDate(dateText: string): Date {
    try {
      // Remove periods and convert to standard format
      const cleanText = dateText.replace(/\./g, "").replace(",", "");

      // Parse the date using Date constructor
      const parsedDate = new Date(cleanText);

      // Validate the date
      if (isNaN(parsedDate.getTime())) {
        throw new Error(`Invalid date format: ${dateText}`);
      }

      return parsedDate;
    } catch (error) {
      throw new Error(`Error converting date: `);
    }
  }

  public addTimeToCurrentTime(time: Date = new Date()): Date {
    // Create a new Date object with the provided time or current time
    const newTime: Date = new Date(time);
    console.log("New Time is : ", +newTime);
    // Add 5.5 hours (5 hours and 30 minutes)
    newTime.setHours(newTime.getHours() + 5);
    newTime.setMinutes(newTime.getMinutes() + 30);

    return newTime;
  }
  public async checkTimeDifference(timeString: string) {
    const givenTime = new Date(timeString);
    console.log("Given Time is : ", +givenTime);
    const currentTime = new Date();
    console.log("Current Time is : ", +currentTime);
    const diffInMs = Math.abs(currentTime.getTime() - givenTime.getTime());
    const diffInMinutes = diffInMs / (1000 * 60);
    console.log("the differnce time is " + diffInMinutes);
    return {
      isWithinHour: diffInMinutes <= 30,
      diffInMinutes: Math.floor(diffInMinutes),
      diffInHours: Math.floor(diffInMinutes / 60),
    };
  }

  public async startNetworkMonitoring(): Promise<void> {
    await allure.step("Starting network monitoring", async () => {
      this.networkLogs = [];
      this.errorLogs = [];

      // Listen for all responses
      this.page.on("response", async (response) => {
        const url = response.url();
        const status = response.status();
        const method = response.request().method();
        const timestamp = this.gettxtlogdatetime;

        this.networkLogs.push({ url, status, method, timestamp });

        // Log each network call
        await this.logMessage(
          `Network Call: ${method} ${url} - Status: ${status}`
        );

        // Capture non-2XX status codes
        if (status < 200 || status >= 310) {
          let errorDetails = "";
          try {
            const responseBody = await response.text();
            errorDetails = responseBody;
          } catch (e) {
            errorDetails = "Could not get response body";
          }

          const errorLog = {
            url,
            status,
            method,
            timestamp,
            errorDetails,
          };

          this.errorLogs.push(errorLog);

          // Log error to Allure with details
          await allure.step(
            `🚨 Error Response: ${method} ${url} - Status: ${status}`,
            async () => {
              await this.logFailure(
                `API call failed: ${method} ${url} - Status: ${status}`
              );

              // Create a unique filename for each error
              const errorFileName = `error-response-${status}-${Date.now()}.json`;

              // Attach error details as a JSON file
              await allure.attachment(
                errorFileName,
                JSON.stringify(errorLog, null, 2),
                "application/json"
              );
            }
          );
          if (this.errorLogs.length > 0) {
            throw new Error(
              `Network errors detected, thus smoke suite Failed : ${this.errorLogs[0].errorDetails}`
            );
          }
        }
      });
    });
  }

  /**
   * Logs all captured non-2XX network calls to the test report and throws error if any found
   */
  public async logErrorCalls(): Promise<void> {
    await allure.step("Error Network Calls Summary", async () => {
      if (this.errorLogs.length === 0) {
        await this.logSuccess("No error responses were captured");
        return;
      }

      // Group errors by status code
      const errorsByStatus = this.errorLogs.reduce((acc, call) => {
        const status = call.status;
        if (!acc[status]) {
          acc[status] = [];
        }
        acc[status].push(call);
        return acc;
      }, {} as Record<number, typeof this.errorLogs>);

      // Log summary
      await this.logFailure(
        `🚨 Total Error Responses: ${this.errorLogs.length}`
      );

      // Create a summary file with all errors
      const summaryFileName = `error-summary-${Date.now()}.json`;
      await allure.attachment(
        summaryFileName,
        JSON.stringify(this.errorLogs, null, 2),
        "application/json"
      );

      // Log errors by status code
      for (const [status, calls] of Object.entries(errorsByStatus)) {
        await this.logFailure(`🚨 Status ${status}: ${calls.length} calls`);

        // Create a file for each status code group
        const statusFileName = `error-status-${status}-${Date.now()}.json`;
        await allure.attachment(
          statusFileName,
          JSON.stringify(calls, null, 2),
          "application/json"
        );

        // Log details for each error call
        for (const call of calls) {
          await allure.step(
            `Error Details: ${call.method} ${call.url}`,
            async () => {
              await this.logFailure(
                `- ${call.method} ${call.url} (${call.timestamp})`
              );
            }
          );
        }
      }

      // Throw error to fail the test when network errors are detected
      const errorMessage = `🚨 Network monitoring detected ${this.errorLogs.length} error responses. Test failed due to network errors.`;
      throw new Error(errorMessage);
    });
  }

  /**
   * Clears all captured network and error logs
   */
  public clearNetworkLogs(): void {
    this.networkLogs = [];
    this.errorLogs = [];
  }

  public async scanQRCode(screenshot: Buffer): Promise<string> {
    const image = await Jimp.read(screenshot);
    const { width, height, data } = image.bitmap;

    const code = jsQR(new Uint8ClampedArray(data.buffer), width, height);
    if (!code?.data) {
      throw new Error("QR Code not found in the image");
    }
    return code.data;
  }
}
