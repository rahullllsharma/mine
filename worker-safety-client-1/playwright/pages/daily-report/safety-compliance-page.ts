import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class DailyReportSafetyCompliancePage extends BasePage {
  // Selectors
  readonly headerPlans: Locator = this.getHeaderByText("h5", "Plans");
  readonly headerJobBrief: Locator = this.getHeaderByText("h5", "Job Brief");
  readonly comprehensiveJBCheck: Locator = this.getRadioByText(
    "Was a comprehensive job brief conducted? *NoYes",
    "Yes"
  );
  readonly jobBriefConductedCheck: Locator = this.getRadioByText(
    "Was a Job Brief conducted after changes to work performed? *NoYes",
    "Yes"
  );
  readonly headerWork: Locator = this.getHeaderByText("h5", "Work Methods");
  readonly contractorNavigNGCheck: Locator = this.getRadioByText(
    `Could the ${process.env.CONTRACTOR_LABEL} access & navigate the NG procedures? *NoYes`,
    "Yes"
  );
  readonly headerDigsafe: Locator = this.getHeaderByText(
    "h5",
    "Digsafe / Mark Outs"
  );
  readonly markOutsVerifCheck: Locator = this.getRadioByText(
    "Were all Mark Outs verified? *NoYes",
    "Yes"
  );
  readonly facilitiesPriorExcavationCheck: Locator = this.getRadioByText(
    "Were all Facilities located and exposed prior to excavation? *NoYes",
    "Yes"
  );
  readonly digsafeLocationText: Locator = this.getByText("Digsafe location? *");
  readonly digsafeLocationInput: Locator = this.getInputByName(
    "safetyAndCompliance.digSafeMarkOuts.digSafeMarkOutsLocation"
  );
  readonly headerSystemOperProc: Locator = this.getHeaderByText(
    "h5",
    "System Operating Procedures"
  );
  readonly onsiteCurrentSOPsCheck: Locator = this.getRadioByText(
    "Was the SOPs onsite and current? *NoYes",
    "Yes"
  );
  readonly gasControlsCheck: Locator = this.getRadioByText(
    "Has Gas Controls been notified & has approval been given prior to the steps being performed? *NoYes",
    "Yes"
  );
  readonly textSOP: Locator = this.getByText("SOP# *");
  readonly textSOPInput: Locator = this.getInputByName(
    "safetyAndCompliance.systemOperatingProcedures.sopId"
  );
  readonly textSOPType: Locator = this.getByText("SOP Type *");
  readonly textSOPTypeInput: Locator = this.getInputByName(
    "safetyAndCompliance.systemOperatingProcedures.sopType"
  );
  readonly stepsCalledInText: Locator = this.getByText("Steps called in *");
  readonly stepsCalledInInput: Locator = this.getInputByName(
    "safetyAndCompliance.systemOperatingProcedures.sopStepsCalledIn"
  );
  readonly headerObservers: Locator = this.getHeaderByText(
    "h5",
    "Spotters/Safety Observer"
  );
  readonly textPPE: Locator = this.getHeaderByText("h5", "PPE");
  readonly wearingPPECheck: Locator = this.getRadioByText(
    "Were all crew members and visitors wearing the appropriate PPE? *NoYes",
    "Yes"
  );
  readonly headerOperatorQualifications: Locator = this.getHeaderByText(
    "h5",
    "Operator Qualifications"
  );
  readonly operatorQualificationsCheck: Locator = this.getRadioByText(
    "Were the Operator Qualifications verified? *NoYes",
    "Yes"
  );
  readonly saveContinueBtn: Locator = this.getBtnByText("Save and continue");

  /**
   * Update Safety and Compliance DIR section
   */
  async updateSafetyAndCompliance() {
    console.log("Update Safety And Compliance DIR section");
    await expect(this.headerPlans).toBeVisible();
    await expect(this.headerJobBrief).toBeVisible();
    await this.comprehensiveJBCheck.click();
    await this.jobBriefConductedCheck.click();

    await expect(this.headerWork).toBeVisible();
    await this.contractorNavigNGCheck.click();

    await expect(this.headerDigsafe).toBeVisible();
    await this.markOutsVerifCheck.click();
    await this.facilitiesPriorExcavationCheck.click();

    await expect(this.digsafeLocationText).toBeVisible();
    await this.digsafeLocationInput.fill("Calvão");

    await expect(this.headerSystemOperProc).toBeVisible();
    await this.onsiteCurrentSOPsCheck.click();
    await this.gasControlsCheck.click();
    await expect(this.textSOP).toBeVisible();
    await this.textSOPInput.fill("1234");
    await expect(this.textSOPInput).toBeVisible();
    await this.textSOPTypeInput.fill("Random Type");
    await expect(this.stepsCalledInText).toBeVisible();
    await this.stepsCalledInInput.fill("10");

    await expect(this.headerObservers).toBeVisible();

    await expect(this.textPPE).toBeVisible();
    await this.wearingPPECheck.click();

    await expect(this.headerOperatorQualifications).toBeVisible();
    await this.operatorQualificationsCheck.click();

    await this.saveContinueBtn.click();
  }
}
