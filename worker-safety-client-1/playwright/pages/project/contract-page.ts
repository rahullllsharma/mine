import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import contractorList from "../../data/contractors.json";
import { BasePage } from "../base-page";

export class ProjectContractPage extends BasePage {
  // Selectors
  readonly contractorInformation: Locator = this.getByTestIdText(
    "work-package-contract-information",
    `Contract information`
  );
  readonly contractorText: Locator = this.getByTestIdLabelText(
    "work-package-contractor",
    `${process.env.CONTRACTOR_LABEL}`
  );
  readonly contractorSelect: Locator = this.getByTestId(
    "work-package-contractor >> div[role='button']"
  );
  readonly contractorOption: Locator = this.getDivOptByText(
    contractorList.contractors[0]
  );

  /**
   * Update Contract information section
   */
  async updateContractInformation() {
    console.log(`Update Contract Information`);
    await expect(this.contractorInformation).toBeVisible();
    await expect(this.contractorText).toBeVisible();
    await this.contractorSelect.click();
    await this.contractorOption.click();
  }
}
