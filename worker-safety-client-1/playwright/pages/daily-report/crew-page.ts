import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class DailyReportCrewPage extends BasePage {
  // Selectors
  readonly headerCrewInfo: Locator = this.getHeaderByText(
    "h5",
    "Crew Information"
  );
  readonly crewInfoText: Locator = this.getByText("Crew Information");
  readonly crewMemberCompany: Locator = this.getByText(
    `Crew member ${process.env.CONTRACTOR_LABEL} company`
  );
  readonly contractorBtn: Locator = this.getBtnByText("Select a contractor");
  readonly contractorOpt: Locator = this.getDivOptByText(
    "AccuWeld Technologies Inc"
  );
  readonly crewForemanNameInput: Locator =
    this.getInputByName("crew\\.foremanName");
  readonly numWeldersText: Locator = this.getByText("# of welders *");
  readonly numWeldersInput: Locator = this.getInputByName("crew\\.nWelders");
  readonly numSafetyProdText: Locator = this.getByText("# of safety prof. *");
  readonly numSafetyProdInput: Locator =
    this.getInputByName("crew\\.nSafetyProf");
  readonly numFlaggersText: Locator = this.getByText("# of flaggers *");
  readonly numFlaggersInput: Locator = this.getInputByName("crew\\.nFlaggers");
  readonly numLaborersText: Locator = this.getByText("# of laborers *");
  readonly numLaborersInput: Locator = this.getInputByName("crew\\.nLaborers");
  readonly numOperatorsText: Locator = this.getByText("# of operators *");
  readonly numOperatorsInput: Locator =
    this.getInputByName("crew\\.nOperators");
  readonly numOtherCrewMembersText: Locator = this.getByText(
    "# of other crew members *"
  );
  readonly numOtherCrewMembersInput: Locator =
    this.getInputByName("crew\\.nOtherCrew");
  readonly totalNumCrewMembersText: Locator = this.getByText(
    "Total # of crew members"
  );
  readonly headerCrewDocuments: Locator = this.getHeaderByText(
    "h6",
    "Crew Documents"
  );
  readonly docUploaded: Locator = this.getByText("No documents uploaded");
  readonly saveContinueBtn: Locator = this.getBtnByText("Save and continue");

  /**
   * Update Crew DIR section
   */
  async updateCrew() {
    console.log("Update Crew DIR section");
    await expect(this.headerCrewInfo).toBeVisible();
    await expect(this.crewInfoText).toBeVisible();
    await expect(this.crewMemberCompany).toBeVisible();

    if (await this.contractorBtn.isVisible()) {
      await this.contractorBtn.click();
      await this.contractorOpt.click();
    }

    await this.crewForemanNameInput.fill("The Man");

    await expect(this.numWeldersText).toBeVisible();
    await this.numWeldersInput.fill("1");

    await expect(this.numSafetyProdText).toBeVisible();
    await this.numSafetyProdInput.fill("1");

    await expect(this.numFlaggersText).toBeVisible();
    await this.numFlaggersInput.fill("1");

    await expect(this.numLaborersText).toBeVisible();
    await this.numLaborersInput.fill("1");

    await expect(this.numOperatorsText).toBeVisible();
    await this.numOperatorsInput.fill("1");

    await expect(this.numOtherCrewMembersText).toBeVisible();
    await this.numOtherCrewMembersInput.fill("1");

    await expect(this.totalNumCrewMembersText).toBeVisible();
    // TODO: Validate that the calculation is correct

    // TODO: Review when WSAPP-799 is fixed
    await expect(this.headerCrewDocuments).toBeVisible();
    await expect(this.docUploaded).toBeVisible();

    // await this.page.locator('text=Crew DocumentsUpload crew info >> button').click();
    await this.saveContinueBtn.click();
  }
}
