import { test } from "../framework/base-fixtures";

test.skip("HAR test @noTest", async ({ page }) => {
  test.skip(({ browserName }) => browserName !== "chromium", "Chromium only!");
  try {
    await page.routeFromHAR("./har.zip");
  } catch (error) {
    console.log(error);
  }
});
