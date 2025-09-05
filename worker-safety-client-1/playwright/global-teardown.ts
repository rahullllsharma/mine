// global-setup.ts
import type { FullConfig } from "@playwright/test";
import { chromium } from "@playwright/test";

async function globalTeardown(config: FullConfig) {
  console.log("Global Teardown started");
  // Get baseURL and storageState from playwright.config.ts
  const { baseURL, storageState } = config.projects[0].use;
  const browser = await chromium.launch();
  const context = await browser.newContext({ storageState });
  const page = await context.newPage();
  try {
    await context.tracing.start({ screenshots: true, snapshots: true });
    await page.goto(baseURL!);
    await page.locator("data-testid=dropdown").click();
    await page.locator("text='Logout'").click();
    await context.tracing.stop({
      path: "./playwright/report/teardown/teardown-trace.zip",
    });
    await page.close();
  } catch (error) {
    console.log(error);
    await context.tracing.stop({
      path: "./playwright/report/teardown/failed-teardown-trace.zip",
    });
    await page.close();
    throw error;
  }
  console.log("Global Teardown ended");
}

export default globalTeardown;
