// global-setup.ts
import type { FullConfig } from "@playwright/test";
import { chromium } from "@playwright/test";
import { getAPIAccessToken } from "./framework/graphql-client";

async function globalSetup(config: FullConfig) {
  console.log("Global Setup started");
  // Get baseURL and storageState from playwright.config.ts
  const { baseURL, storageState } = config.projects[0].use;
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  // Get API_TOKEN using axios
  process.env.API_TOKEN = await getAPIAccessToken();
  try {
    await context.tracing.start({ screenshots: true, snapshots: true });
    await page.goto(baseURL!);
    // await page.goto(`${process.env.BASEURL}`);
    await page.locator('input[name="username"]').click();
    await page.fill('input[name="username"]', `${process.env.PW_USERNAME}`);
    await page.locator('input[name="username"]').press("Tab");
    await page.fill('input[name="password"]', `${process.env.PW_PASSWORD}`);
    await page.locator('input:has-text("Sign In")').click();
    await context.storageState({ path: storageState as string });
    await context.tracing.stop({
      path: "./playwright/report/setup/setup-trace.zip",
    });
    await page.close();
  } catch (error) {
    console.log(error);
    await context.tracing.stop({
      path: "./playwright/report/setup/failed-setup-trace.zip",
    });
    await page.close();
    throw error;
  }
  console.log("Global Setup ended");
}

export default globalSetup;
