import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class ProjectSettingsPage extends BasePage {
  // Selectors
  readonly settingsButton: Locator = this.page.locator(".ci-settings_filled");
  readonly deleteButton: Locator = this.page.locator(".ci-trash_empty");
  readonly confirmDeleteButton: Locator = this.getByText(
    `Delete ${process.env.MAIN_LABEL}`
  );

  async openProjectSettings(projectName: string) {
    console.log(`Open ${projectName} Settings`);
    await expect(this.page).toHaveURL(/projects\/.*/);
    await expect(this.page.locator(`text=${projectName}`)).toBeVisible();
    await this.settingsButton.click();
  }

  async deleteProject(projectName: string) {
    console.log(`Deleting ${projectName} Project`);
    await this.deleteButton.click();
    await this.confirmDeleteButton.click();
  }
}
