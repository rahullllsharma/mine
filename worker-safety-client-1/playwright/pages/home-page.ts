import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "./base-page";

export class HomePage extends BasePage {
  readonly homePageByTenant: string =
    process.env.KEYCLOAK_REALM === "hydro1" ? "/map" : "/projects";

  // Selectors
  readonly homePageLayout: Locator = this.getByTestId("page-layout");
  readonly profileButton: Locator = this.getByTestId("dropdown");
  readonly addWorkPackageButton: Locator = this.getByTestId(
    "add-work-package-button"
  );
  readonly projectAddedBanner: Locator = this.getByText(
    `${process.env.MAIN_LABEL} added`
  );
  readonly projectDeletedBanner: Locator = this.getByText(
    `${process.env.MAIN_LABEL} deleted`
  );
  readonly projectTabButton: Locator = this.getBtnByTab(
    `${process.env.MAIN_LABEL}`
  );
  readonly projectHeader: Locator = this.getHeaderByText(
    "h4",
    `${process.env.MAIN_LABEL}`
  );
  readonly mapTabButton: Locator = this.getBtnByTab("Map");
  readonly mapHeader: Locator = this.getInputByPlaceHolder("Search locations"); // TODO: revisit when WSAPP-799 is fixed
  readonly learningsTabButton: Locator = this.getBtnByTab("Learnings");
  readonly learningsHeader: Locator = this.getHeaderByText("h4", "Learnings");
  readonly planningTabButton: Locator = this.getBtnByTab("Planning");
  readonly planningHeader: Locator = this.getHeaderByText("h4", "Planning");
  readonly logoutButton: Locator = this.getByText("Logout");

  async userIsHomePage() {
    await expect(this.page).toHaveURL(this.homePageByTenant);
    await expect(this.homePageLayout).toBeVisible();
  }

  async addProject() {
    await this.addWorkPackageButton.click();
    await expect(this.page).toHaveURL("projects/create");
  }

  async projectCreated() {
    await expect(this.page).toHaveURL(this.homePageByTenant);
    await expect(this.projectAddedBanner).toBeVisible();
    await this.projectAddedBanner.click();
    // await expect(this.projectAddedBanner).toBeHidden();
  }

  async projectDeleted() {
    await expect(this.page).toHaveURL(this.homePageByTenant);
    await expect(this.projectDeletedBanner).toBeVisible();
    await this.projectDeletedBanner.click();
    // await expect(this.projectDeletedBanner).toBeHidden();
  }

  async tabsAvailable() {
    // Home
    await this.projectTabButton.click();
    await this.projectTabButton.isVisible();
    await expect(this.projectHeader).toBeVisible();

    // Map
    if (process.env.PW_ROLE === "administrator") {
      await this.mapTabButton.click();
      await expect(this.mapHeader).toBeVisible();
      await expect(this.page).toHaveURL("map");
    }

    // Learnings
    await this.learningsTabButton.click();
    await expect(this.learningsHeader).toBeVisible();
    await expect(this.page).toHaveURL("learnings");

    // Planning
    await this.planningTabButton.click();
    await expect(this.planningHeader).toBeVisible();
    await expect(this.page).toHaveURL("planning");
  }

  // Navigate to project summary page
  async openProjectSummaryPage(projectName: string) {
    await expect(this.homePageLayout).toBeVisible();
    await this.page.locator(`a:has-text("${projectName}")`).click();
  }

  // Navigate to templates page
  async openTemplatesPage() {
    await expect(this.homePageLayout).toBeVisible();
    await this.page.getByRole("tab", { name: "Templates" }).click();
  }

  // Get Project List
  async getProjectsByPattern(projectNamePattern: string): Promise<string[]> {
    await expect(this.homePageLayout).toBeVisible();
    return await this.page
      .locator(`a:has-text('${projectNamePattern}')`)
      .allTextContents();
  }

  // Logout
  async logout() {
    await this.profileButton.click();
    await this.logoutButton.click();
  }
}
