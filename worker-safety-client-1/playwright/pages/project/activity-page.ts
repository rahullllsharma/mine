import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { getCloseFormattedDate } from "../../framework/common-actions";
import { BasePage } from "../base-page";

export class ActivityPage extends BasePage {
  // Selectors
  readonly projectAddActivityButton: Locator = this.page.getByRole("button", {
    name: "Add an activity",
  });
  readonly selectActivity: Locator = this.page.getByRole("button", {
    name: /^Demolition/,
  });
  readonly selectTask: Locator = this.page.getByLabel(
    "Demo of retired facilities"
  );
  readonly pressNextButton: Locator = this.page.getByRole("button", {
    name: "Next",
    exact: true,
  });
  readonly startDateInput: Locator = this.getInputByName("startDate");
  readonly endDateInput: Locator = this.getInputByName("endDate");
  readonly addActivityButton: Locator = this.page.getByRole("button", {
    name: "Add Activity",
  });
  readonly activityAddedBanner: Locator = this.getByText("Activity added");
  readonly addedActivity: Locator = this.page.getByRole("button", {
    name: /^Demo of retired facilities/,
  });

  /**
   * Update Contract information section
   */
  async addActivity() {
    const StartDate = getCloseFormattedDate(0, "recent");
    const EndDate = getCloseFormattedDate(1, "soon");
    console.log(`Create activity`);
    await this.projectAddActivityButton.click();
    await this.selectActivity.click();
    await this.selectTask.click();
    await this.pressNextButton.click();
    await this.startDateInput.fill(StartDate);
    await this.endDateInput.fill(EndDate);
    await this.pressNextButton.click();
    await this.addActivityButton.click();
  }

  async activityCreated() {
    await expect(this.activityAddedBanner).toBeVisible();
    await this.activityAddedBanner.click();
    await expect(this.addedActivity).toBeVisible();
  }
}
