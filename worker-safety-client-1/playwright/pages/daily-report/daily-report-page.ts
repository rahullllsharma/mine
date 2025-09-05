import type { Page, Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";
import { DailyReportWorkSchedulePage } from "./work-schedule-page";
import { DailyReportTasksPage } from "./tasks-page";
import { DailyReportControlsAssessmentPage } from "./controls-assessment-page";
import { DailyReportSafetyCompliancePage } from "./safety-compliance-page";
import { DailyReportCrewPage } from "./crew-page";
import { DailyReportAdditionalInfoPage } from "./additional-info-page";
import { DailyReportAttachmentsPage } from "./attachments-page";

export class DailyReportPage extends BasePage {
  // Section Pages
  readonly dailyReportWorkSchedulePage: DailyReportWorkSchedulePage;
  readonly dailyReportTasksPage: DailyReportTasksPage;
  readonly dailyReportControlsAssessmentPage: DailyReportControlsAssessmentPage;
  readonly dailyReportSafetyCompliancePage: DailyReportSafetyCompliancePage;
  readonly dailyReportCrewPage: DailyReportCrewPage;
  readonly dailyReportAdditionalInfoPage: DailyReportAdditionalInfoPage;
  readonly dailyReportAttachmentsPage: DailyReportAttachmentsPage;

  // Selectors
  readonly addButton: Locator = this.getBtnByText("Add...");
  readonly addReportButton: Locator = this.getBtnByText("Daily Report");
  readonly dailyReportTitle: Locator = this.getHeaderByText(
    "h2",
    "Daily Inspection Report"
  );
  readonly pressWorkScheduleSection: Locator =
    this.getBtnByTab("Work Schedule");
  readonly pressTasksSection: Locator = this.getBtnByTab("Tasks");
  readonly pressControlsAssessmentSection: Locator = this.getBtnByTab(
    "Controls Assessment"
  );
  readonly pressSafetyComplianceSection: Locator = this.getBtnByTab(
    "Safety And Compliance"
  );
  readonly pressCrewSection: Locator = this.getBtnByTab("Crew");
  readonly pressAdditionalInfoSection: Locator = this.getBtnByTab(
    "Additional Information"
  );
  readonly pressAttachmentsSection: Locator = this.getBtnByTab("Attachments");
  readonly saveAndContinueButton: Locator =
    this.getBtnByText("Save and continue");
  readonly saveAndCompleteButton: Locator =
    this.getBtnByText("Save and complete");
  readonly completeReportBtn: Locator = this.getBtnByText("Complete report");
  readonly successDIRBtn: Locator = this.getBtnByText(
    "The daily report was successfully completed."
  );

  /**
   * Class Constructor
   * - Locators are used to reflect a element on the page with a selector.
   *   @see https://playwright.dev/docs/api/class-locator
   */
  constructor(page: Page) {
    super(page);

    this.dailyReportWorkSchedulePage = new DailyReportWorkSchedulePage(page);
    this.dailyReportTasksPage = new DailyReportTasksPage(page);
    this.dailyReportControlsAssessmentPage =
      new DailyReportControlsAssessmentPage(page);
    this.dailyReportSafetyCompliancePage = new DailyReportSafetyCompliancePage(
      page
    );
    this.dailyReportCrewPage = new DailyReportCrewPage(page);
    this.dailyReportAdditionalInfoPage = new DailyReportAdditionalInfoPage(
      page
    );
    this.dailyReportAttachmentsPage = new DailyReportAttachmentsPage(page);
  }

  /**
   * Function that presses Add Report button to Create a Daily Report
   */
  async pressAddReport() {
    await this.addButton.click();
    await this.addReportButton.click();
    // await expect(this.page).toHaveURL("projects/**");
    await expect(this.dailyReportTitle).toBeVisible();
  }

  /**
   * Function that calls all the necessary functions to create a daily report
   */
  async createDailyReport() {
    await this.dailyReportWorkSchedulePage.updateWorkSchedule();
    await this.dailyReportTasksPage.updateTasks();
    await this.dailyReportControlsAssessmentPage.updateControlsAssessment();
    await this.dailyReportSafetyCompliancePage.updateSafetyAndCompliance();
    await this.dailyReportCrewPage.updateCrew();
    await this.dailyReportAdditionalInfoPage.updateAdditionalInformation();
    await this.dailyReportAttachmentsPage.updateAttachments();
    await this.completeReport();
  }

  /**
   * Function that completes DIR
   */
  async completeReport() {
    await expect(this.saveAndCompleteButton).toBeVisible();
    await this.saveAndCompleteButton.click();
    await this.completeReportBtn.click();
  }

  /**
   * Function that confirms that the report has been created
   */
  async confirmReportCreated() {
    await this.successDIRBtn.click();
  }
}
