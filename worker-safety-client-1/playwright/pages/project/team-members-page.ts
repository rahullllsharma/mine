import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class ProjectTeamMembersPage extends BasePage {
  // Selectors
  readonly teamMembers: Locator = this.getByTestIdText(
    "work-package-team-members",
    `${process.env.MAIN_LABEL} team members`
  );
  readonly managerText: Locator = this.getByTestIdLabelText(
    "work-package-manager",
    "Project Manager"
  );
  readonly managerSelect: Locator = this.getByTestId(
    "work-package-manager >> div[role='button']"
  );
  readonly managerOpt: Locator = this.getDivOptByText(
    `${process.env.PW_MANAGER}`
  );
  readonly supervisorText: Locator = this.getByTestIdLabelText(
    "work-package-assigned-person",
    `Primary ${process.env.SUPERVISOR_LABEL}`
  );
  readonly supervisorSelect: Locator = this.getByTestId(
    "work-package-assigned-person >> div[role='button']"
  );
  readonly supervisorOpt: Locator = this.getDivOptByText(
    `${process.env.PW_SUPERVISOR}`
  );

  /**
   * Update project team members section
   */
  public async updateProjectTeamMembers() {
    try {
      console.log(`Update Project Team Members`);
      await expect(this.teamMembers).toBeVisible();

      await expect(this.managerText).toBeVisible();
      await this.managerSelect.click();
      await this.managerOpt.click();

      await expect(this.supervisorText).toBeVisible();
      await this.supervisorSelect.click();
      await this.supervisorOpt.click();
    } catch (error) {
      console.log(error);
    }
  }
}
