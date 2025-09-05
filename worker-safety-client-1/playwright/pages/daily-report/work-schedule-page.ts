import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { getFormattedDateTime } from "../../framework/common-actions";
import { BasePage } from "../base-page";

export class DailyReportWorkSchedulePage extends BasePage {
  // Selectors
  readonly headerReportDetails: Locator = this.getHeaderByText(
    "h3",
    "Daily Report Details"
  );
  readonly workStartDayTimeText: Locator = this.getByText(
    "Contractor Work Start Day and time *"
  );
  readonly workStartScheduleDateTime: Locator = this.getInputByName(
    "workSchedule\\.startDatetime"
  );
  readonly workEndDayTimeText: Locator = this.getByText(
    "Contractor Work End Day and time *"
  );
  readonly workEndScheduleDateTime: Locator = this.getInputByName(
    "workSchedule\\.endDatetime"
  );
  readonly saveContinueBtn: Locator = this.getBtnByText("Save and continue");

  /**
   * Update Work Schedule DIR section
   */
  async updateWorkSchedule() {
    console.log("Update Work Schedule DIR section");
    const startDateTime = getFormattedDateTime(1, "past");
    console.log("The Daily Report Start date and time is", startDateTime);

    const endDateTime = getFormattedDateTime(1, "future");
    console.log("The Daily Report End date and time is", endDateTime);

    // TODO: Review when WSAPP-799 is fixed
    await expect(this.headerReportDetails).toBeVisible();
    await expect(this.workStartDayTimeText).toBeVisible();
    await this.workStartDayTimeText.click();
    await this.workStartScheduleDateTime.fill(startDateTime);

    await expect(this.workEndDayTimeText).toBeVisible();
    await this.workEndScheduleDateTime.fill(endDateTime);

    await this.saveContinueBtn.click();
  }
}
