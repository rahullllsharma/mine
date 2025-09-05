import { test as base } from "@playwright/test";
import { BasePage } from "../pages/base-page";
import { LoginPage } from "../pages/login-page";
import { HomePage } from "../pages/home-page";
import { ProjectPage } from "../pages/project/project-page";
import { ProjectDetailsPage } from "../pages/project/details-page";
import { ProjectTeamMembersPage } from "../pages/project/team-members-page";
import { ProjectContractPage } from "../pages/project/contract-page";
import { ProjectLocationsPage } from "../pages/project/locations-page";
import { ProjectSettingsPage } from "../pages/project/settings-page";
import { ActivityPage } from "../pages/project/activity-page";
import { DailyReportPage } from "../pages/daily-report/daily-report-page";
import { DailyReportWorkSchedulePage } from "../pages/daily-report/work-schedule-page";
import { DailyReportTasksPage } from "../pages/daily-report/tasks-page";
import { DailyReportControlsAssessmentPage } from "../pages/daily-report/controls-assessment-page";
import { DailyReportSafetyCompliancePage } from "../pages/daily-report/safety-compliance-page";
import { DailyReportCrewPage } from "../pages/daily-report/crew-page";
import { DailyReportAdditionalInfoPage } from "../pages/daily-report/additional-info-page";
import { DailyReportAttachmentsPage } from "../pages/daily-report/attachments-page";
import { ProjectAPIPage } from "../pages/api/project-page";
import { BaseAPIPage } from "../pages/api/base-api-page";
import { LogoutPage } from "../pages/logout-page";
import { ActivityAPIPage } from "../pages/api/activity-page";
import { TemplatesPage } from "../pages/templates/templates-page";
import { TemplatePage } from "../pages/templates/template-page";

// Declare the types of your fixtures.
type CommonFixtures = {
  basePage: BasePage;
  loginPage: LoginPage;
  homePage: HomePage;
  projectPage: ProjectPage;
  projectDetailsPage: ProjectDetailsPage;
  projectTeamMembersPage: ProjectTeamMembersPage;
  projectContractPage: ProjectContractPage;
  projectLocationsPage: ProjectLocationsPage;
  projectSettingsPage: ProjectSettingsPage;
  activityPage: ActivityPage;
  dailyReportPage: DailyReportPage;
  dailyReportWorkSchedulePage: DailyReportWorkSchedulePage;
  dailyReportTasksPage: DailyReportTasksPage;
  dailyReportControlsAssessmentPage: DailyReportControlsAssessmentPage;
  dailyReportSafetyCompliancePage: DailyReportSafetyCompliancePage;
  dailyReportCrewPage: DailyReportCrewPage;
  dailyReportAdditionalInfoPage: DailyReportAdditionalInfoPage;
  dailyReportAttachmentsPage: DailyReportAttachmentsPage;
  logoutPage: LogoutPage;
  projectAPIPage: ProjectAPIPage;
  prepareProjectDataAPIPage: ProjectAPIPage;
  createProjectAPIPage: ProjectAPIPage;
  baseAPIPage: BaseAPIPage;
  activityAPIPage: ActivityAPIPage;
  templatesPage: TemplatesPage;
  templatePage: TemplatePage;
};

export const test = base.extend<CommonFixtures>({
  basePage: async ({ page }, use) => {
    const basePage = new BasePage(page);
    await use(basePage);
  },
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await use(loginPage);
  },
  homePage: async ({ page }, use) => {
    const homePage = new HomePage(page);
    await use(homePage);
  },
  projectPage: async ({ page }, use) => {
    const projectPage = new ProjectPage(page);
    await use(projectPage);
  },
  projectDetailsPage: async ({ page }, use) => {
    const projectDetailsPage = new ProjectDetailsPage(page);
    await use(projectDetailsPage);
  },
  projectTeamMembersPage: async ({ page }, use) => {
    const projectTeamMembersPage = new ProjectTeamMembersPage(page);
    await use(projectTeamMembersPage);
  },
  projectContractPage: async ({ page }, use) => {
    const projectContractPage = new ProjectContractPage(page);
    await use(projectContractPage);
  },
  projectLocationsPage: async ({ page }, use) => {
    const projectLocationsPage = new ProjectLocationsPage(page);
    await use(projectLocationsPage);
  },
  projectSettingsPage: async ({ page }, use) => {
    const projectSettingsPage = new ProjectSettingsPage(page);
    await use(projectSettingsPage);
  },
  dailyReportPage: async ({ page }, use) => {
    const dailyReportPage = new DailyReportPage(page);
    await use(dailyReportPage);
  },
  dailyReportWorkSchedulePage: async ({ page }, use) => {
    const dailyReportWorkSchedulePage = new DailyReportWorkSchedulePage(page);
    await use(dailyReportWorkSchedulePage);
  },
  dailyReportTasksPage: async ({ page }, use) => {
    const dailyReportTasksPage = new DailyReportTasksPage(page);
    await use(dailyReportTasksPage);
  },
  dailyReportControlsAssessmentPage: async ({ page }, use) => {
    const dailyReportControlsAssessmentPage =
      new DailyReportControlsAssessmentPage(page);
    await use(dailyReportControlsAssessmentPage);
  },
  dailyReportSafetyCompliancePage: async ({ page }, use) => {
    const dailyReportSafetyCompliancePage = new DailyReportSafetyCompliancePage(
      page
    );
    await use(dailyReportSafetyCompliancePage);
  },
  dailyReportCrewPage: async ({ page }, use) => {
    const dailyReportCrewPage = new DailyReportCrewPage(page);
    await use(dailyReportCrewPage);
  },
  dailyReportAdditionalInfoPage: async ({ page }, use) => {
    const dailyReportAdditionalInfoPage = new DailyReportAdditionalInfoPage(
      page
    );
    await use(dailyReportAdditionalInfoPage);
  },
  dailyReportAttachmentsPage: async ({ page }, use) => {
    const dailyReportAttachmentsPage = new DailyReportAttachmentsPage(page);
    await use(dailyReportAttachmentsPage);
  },
  logoutPage: async ({ page }, use) => {
    const logoutPage = new LogoutPage(page);
    await use(logoutPage);
  },
  activityPage: async ({ page }, use) => {
    const activityPage = new ActivityPage(page);
    await use(activityPage);
  },
  baseAPIPage: async ({ page, request }, use) => {
    const baseAPIPage = new BaseAPIPage(page, request);
    await use(baseAPIPage);
  },
  projectAPIPage: async ({ page, request }, use) => {
    const projectAPIPage = new ProjectAPIPage(page, request);
    await use(projectAPIPage);
  },
  createProjectAPIPage: async ({ page, request }, use) => {
    const projectAPIPage = new ProjectAPIPage(page, request);
    await projectAPIPage.createProject();
    await projectAPIPage.getProject(projectAPIPage.projectName);
    await use(projectAPIPage);
  },
  prepareProjectDataAPIPage: async ({ page, request }, use) => {
    const prepareProjectDataAPIPage = new ProjectAPIPage(page, request);
    await prepareProjectDataAPIPage.prepareProjectData();
    await use(prepareProjectDataAPIPage);
  },
  activityAPIPage: async ({ page, request }, use) => {
    const activityAPIPage = new ActivityAPIPage(page, request);
    await use(activityAPIPage);
  },
  templatesPage: async ({ page }, use) => {
    await use(new TemplatesPage(page));
  },
  templatePage: async ({ page }, use) => {
    await use(new TemplatePage(page));
  },
});

export default test;
export { expect } from "@playwright/test";
