import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { faker } from "@faker-js/faker";
import { getFormattedDate } from "../../framework/common-actions";
import { BasePage } from "../base-page";

// Test Data Variables
const externalKeyValue = faker.random.numeric(5);
const workPackageTypeList = [
  "Distribution",
  "Facilities",
  "Lining",
  "LNG/CNG",
  "Other",
  "Reg Stations / Heaters",
  "Transmission",
];
const assetTypeList = [
  "CNG",
  "Distribution Piping",
  "Fire Water Main",
  "Global Application",
  "LNG (Liquefied Natural Gas)",
  "Metering",
  "Pipe Lining",
  "Regulator Stations",
  "Tie-in",
  "Transmission Piping",
];
const statusList = ["pending", "active", "completed"];
const divisionList = ["Electric", "Gas"];
const regionList = [
  "DNY (Downstate New York)",
  "NE (New England)",
  "UNY (Upstate New York)",
];

export class ProjectDetailsPage extends BasePage {
  // Selectors
  readonly detailsText: Locator = this.getByTestIdText(
    "work-package-details",
    `${process.env.MAIN_LABEL} details`
  );
  readonly nameText: Locator = this.getByTestIdLabelText(
    "work-package-name",
    `${process.env.MAIN_LABEL} Name *`
  );
  readonly nameInput: Locator = this.getByTestId("work-package-name >> input");
  readonly externalKeyText: Locator = this.getByTestIdLabelText(
    "work-package-external-key",
    `${process.env.NUMBER_LABEL}`
  );
  readonly externalKeyInput: Locator = this.getByTestId(
    "work-package-external-key >> input"
  );
  readonly workPackageTypeText: Locator = this.getByTestIdLabelText(
    "work-package-type",
    `${process.env.MAIN_LABEL} Type`
  );
  readonly workPackageTypeSelect: Locator = this.getByTestId(
    "work-package-type >> button"
  );
  readonly workPackageTypeOpt: Locator = this.getListByRoleOption(
    workPackageTypeList[0]
  );
  readonly assetTypeText: Locator = this.getByTestIdLabelText(
    "work-package-asset-type",
    `Asset Type`
  );
  readonly assetTypeSelect: Locator = this.getByTestId(
    "work-package-asset-type >> button"
  );
  readonly assetTypeOpt: Locator = this.getListByRoleOption(assetTypeList[0]);
  readonly statusText: Locator = this.getByTestIdLabelText(
    "work-package-status",
    `Status *`
  );
  readonly statusSelect: Locator = this.getByTestId(
    "work-package-status >> button"
  );
  readonly statusOpt: Locator = this.getListByRoleOption(statusList[1]);
  readonly startDate: Locator = this.getByTestIdLabelText(
    "work-package-start-date",
    `Start Date *`
  );
  readonly startDateInput: Locator = this.getInputByName("startDate");
  readonly endDate: Locator = this.getByTestIdLabelText(
    "work-package-end-date",
    `End Date *`
  );
  readonly endDateInput: Locator = this.getInputByName("endDate");
  readonly division: Locator = this.getByTestIdLabelText(
    "work-package-division",
    `Division`
  );
  readonly divisionSelect: Locator = this.getByTestId(
    "work-package-division >> button"
  );
  readonly divisionOpt: Locator = this.getListByRoleOption(divisionList[0]);
  readonly region: Locator = this.getByTestIdLabelText(
    "work-package-region",
    `Region`
  );
  readonly regionSelect: Locator = this.getByTestId(
    "work-package-region >> button"
  );
  readonly regionOpt: Locator = this.getListByRoleOption(regionList[0]);

  /**
   * Update Project details section
   * @param  {string} ProjName
   */
  public async updateProjectDetails(projName: string) {
    console.log(`Update ${projName} Project Details`);
    const StartDate = getFormattedDate(10, "past");
    console.log("The Project Start date is", StartDate);
    const EndDate = getFormattedDate(10, "future");
    console.log("The Project End date is", EndDate);

    await expect(this.detailsText).toBeVisible();

    await expect(this.nameText).toBeVisible();
    await this.nameInput.fill(projName);

    await expect(this.externalKeyText).toBeVisible();
    await this.externalKeyInput.fill(externalKeyValue);

    await expect(this.workPackageTypeText).toBeVisible();
    await this.workPackageTypeSelect.click();
    await this.workPackageTypeOpt.click();

    await expect(this.assetTypeText).toBeVisible();
    await this.assetTypeSelect.click();
    await this.assetTypeOpt.click();

    await expect(this.statusText).toBeVisible();
    await this.statusSelect.click();
    await this.statusOpt.click();

    await expect(this.startDate).toBeVisible();
    await this.startDateInput.fill(StartDate);

    await expect(this.endDate).toBeVisible();
    await this.endDateInput.fill(EndDate);

    await expect(this.division).toBeVisible();
    await this.divisionSelect.click();
    await this.divisionOpt.first().click();

    await expect(this.region).toBeVisible();
    await this.regionSelect.click();
    await this.regionOpt.click();
  }
}
