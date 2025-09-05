import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class DailyReportAdditionalInfoPage extends BasePage {
  // Selectors
  readonly headerProgressUpd: Locator = this.getHeaderByText(
    "h5",
    "Progress Updates"
  );
  readonly commentsText: Locator = this.getByText("Comments");
  readonly lessonsLearned: Locator = this.getHeaderByText(
    "h5",
    "Lessons Learned"
  );
  readonly saveContinueBtn: Locator = this.getBtnByText("Save and continue");

  /**
   * Update Additional Information DIR section
   */
  async updateAdditionalInformation() {
    console.log("Update Additional Information DIR section");
    await expect(this.headerProgressUpd).toBeVisible();
    await expect(this.commentsText.first()).toBeVisible();

    await expect(this.lessonsLearned).toBeVisible();
    await expect(this.commentsText.nth(1)).toBeVisible();

    await this.saveContinueBtn.click();
  }
}
