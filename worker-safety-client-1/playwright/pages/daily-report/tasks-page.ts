import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class DailyReportTasksPage extends BasePage {
  readonly headerTaskSelection: Locator = this.getHeaderByText(
    "h3",
    "Activity task selection"
  );
  readonly selectTasksText: Locator = this.getByText(
    "Select the tasks you were responsible for overseeing at this location."
  );
  readonly saveContinueBtn: Locator = this.getBtnByText("Save and continue");

  /**
   * Update Tasks DIR Section
   */
  async updateTasks() {
    console.log("Update Tasks DIR section");
    // TODO: Review when WSAPP-799 is fixed
    await expect(this.headerTaskSelection).toBeVisible();
    await expect(this.selectTasksText).toBeVisible();

    await this.saveContinueBtn.click();
  }
}
