import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class DailyReportControlsAssessmentPage extends BasePage {
  // Selectors
  readonly headerSiteConditions: Locator = this.getHeaderByText(
    "h5",
    "Site Conditions"
  );
  readonly siteConditionsText: Locator = this.getByText(
    `There are currently no site conditions that have been selected between the set ${process.env.CONTRACTOR_LABEL} start and end dates.`
  );
  readonly siteConditionsSwitch: Locator = this.page.getByRole("switch", {
    name: "Applicable?",
  });
  readonly headerTasks: Locator = this.getByText(
    `There are currently no activity tasks that have been selected between the set ${process.env.CONTRACTOR_LABEL} start and end dates.`
  );
  readonly tasksText: Locator = this.getHeaderByText("h5", "Tasks");
  readonly saveContinueBtn: Locator = this.getBtnByText("Save and continue");

  /**
   * Update Controls Assessment DIR section
   */
  async updateControlsAssessment() {
    console.log("Update Controls Assessment DIR section");
    await expect(this.headerSiteConditions).toBeVisible();
    const visibleSiteCondText: boolean =
      await this.siteConditionsText.isVisible();
    if (!visibleSiteCondText) {
      await this.siteConditionsSwitch.click();
    }
    await expect(this.headerTasks).toBeVisible();
    await expect(this.tasksText).toBeVisible();

    await this.saveContinueBtn.click();
  }
}
