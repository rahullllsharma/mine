import type { Page, Locator } from "@playwright/test";
import { BasePage } from "../base-page";
import { ProjectDetailsPage } from "./details-page";
import { ProjectTeamMembersPage } from "./team-members-page";
import { ProjectLocationsPage } from "./locations-page";
import { ProjectContractPage } from "./contract-page";

export class ProjectPage extends BasePage {
  // Section Pages
  readonly projectDetailsPage: ProjectDetailsPage;
  readonly projectTeamMembersPage: ProjectTeamMembersPage;
  readonly projectContractPage: ProjectContractPage;
  readonly projectLocationsPage: ProjectLocationsPage;
  // Selectors
  readonly saveBtn: Locator = this.getBtnByText("Save");

  /**
   * Class Constructor
   * - Locators are used to reflect a element on the page with a selector.
   *   @see https://playwright.dev/docs/api/class-locator
   */
  constructor(page: Page) {
    super(page);

    // Create section page objects
    this.projectDetailsPage = new ProjectDetailsPage(page);
    this.projectTeamMembersPage = new ProjectTeamMembersPage(page);
    this.projectContractPage = new ProjectContractPage(page);
    this.projectLocationsPage = new ProjectLocationsPage(page);

    // Selectors
    this.saveBtn;
  }

  // Create Project
  /**
   * Function that calls all the necessary functions to create a project
   * @param  {string} projName
   */
  async createProject(projName: string) {
    await this.projectDetailsPage.updateProjectDetails(projName);
    await this.projectTeamMembersPage.updateProjectTeamMembers();
    await this.projectContractPage.updateContractInformation();
    await this.projectLocationsPage.updateLocations();
    await this.saveProject();
  }

  /**
   * Save project
   */
  async saveProject() {
    console.log(`Saving the Project`);
    await this.saveBtn.isEnabled();
    await this.saveBtn.click();
  }
}
