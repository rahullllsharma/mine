import { Page, Locator, expect } from "@playwright/test";
import TestBase, { setProjectName, getProjectName } from "../Util/TestBase";
import { getEnvironmentData, CURRENT_ENV } from "../Data/envConfig";
import { Environment } from "../types/interfaces";
import { InsightsPageLocators } from "../Locators/InsightsPageLocators";
export default class InsightsPage {
  private page: Page;
  private tb: TestBase;
  private currentEnv: string;
  private projectName: string;
  private environmentData: Environment;
  private createdOnDate: string = "";

  constructor(page: Page) {
    this.page = page;
    this.tb = new TestBase(page);
    this.currentEnv = CURRENT_ENV;
    this.projectName = getProjectName();
    this.environmentData = getEnvironmentData();
  }

  private getLocator(locatorObj: { mobile: string; desktop: string }): string {
    return this.projectName === "iPad Mini"
      ? locatorObj.mobile
      : locatorObj.desktop;
  }

  public async validateInsightsPageUI() {
    const insightsPageTitleLocator = this.getLocator(
      InsightsPageLocators.InsightsPage_lblTitle
    );
    await this.page.waitForSelector(insightsPageTitleLocator);

    const insightsPageTitle = this.page.locator(insightsPageTitleLocator);
    await expect(insightsPageTitle).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Insights page title is correct and visible");

    const sidebarLocator = this.getLocator(InsightsPageLocators.Sidebar);
    const sidebar = this.page.locator(sidebarLocator);
    await expect(sidebar).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Sidebar is visible");

    // const selectedButtonLocator = this.getLocator(
    //   InsightsPageLocators.SelectedButton
    // );
    // const selectedButton = this.page.locator(selectedButtonLocator);
    // if ((await selectedButton.count()) > 0) {
    //   await expect(selectedButton).toBeVisible();
    //   // const selectedText = await selectedButton.first().innerText();
    //   // const mainSectionTitleLocator = this.getLocator(
    //   //   InsightsPageLocators.MainSectionTitle
    //   // );
    //   // const mainSectionTitle = this.page.locator(mainSectionTitleLocator);
    //   // await expect(mainSectionTitle).toHaveText(selectedText);
    //   await this.tb.logSuccess(
    //     "Selected sidebar button's name matches main section title"
    //   );
    // } else {
    //   await this.tb.logSuccess(
    //     "No sidebar buttons present, skipping selected button validation"
    //   );
    // }

    const expandButtonLocator = this.getLocator(
      InsightsPageLocators.ExpandButton
    );
    const expandButton = this.page.locator(expandButtonLocator);
    await expect(expandButton).toBeVisible();
    await this.tb.logSuccess("Expand button is visible on the right");
  }

  public async verifyAddedInsightIsListed() {
    const recentAddedInsightLocator = this.getLocator(
      InsightsPageLocators.RecentAddedInsight
    );
    const recentAddedInsight = this.page.locator(recentAddedInsightLocator);
    await expect(recentAddedInsight).toBeVisible();
    await this.tb.logSuccess("Recent added insight is visible");

    await recentAddedInsight.click();

    const recentAddedInsightNameLocator = this.getLocator(
      InsightsPageLocators.RecentAddedInsightName
    );
    const recentAddedInsightName = this.page.locator(
      recentAddedInsightNameLocator
    );
    await expect(recentAddedInsightName).toBeVisible();

    const recentAddedInsightNameText = await recentAddedInsightName.innerText();
    expect(recentAddedInsightNameText).toBe("Test Report Automation");
    await this.tb.logSuccess(
      "Recent added insight name is correct and matches the added insight name"
    );

    const mainSectionTitleLocator = this.getLocator(
      InsightsPageLocators.MainSectionTitle
    );
    const mainSectionTitle = this.page.locator(mainSectionTitleLocator);
    await expect(mainSectionTitle).toHaveText("Test Report Automation");
    await this.tb.logSuccess(
      "Main section title is correct and matches the added insight name"
    );
  }

  public async verifyAddedInsightsDetails() {
    const addedInsightReportDiv = this.page.locator(
      this.getLocator(InsightsPageLocators.AddedInsightReportDiv)
    );
    await expect(addedInsightReportDiv).toBeVisible({ timeout: 10000 });

    const addedInsightDetailsIFrameLocator = this.page.locator(
      this.getLocator(InsightsPageLocators.AddedInsightDetailsIFrame)
    );
    await expect(addedInsightDetailsIFrameLocator).toBeVisible({
      timeout: 10000,
    });
    await expect(addedInsightDetailsIFrameLocator).toHaveAttribute(
      "src",
      /app\.powerbi\.com\/reportEmbed/
    );
    await expect(addedInsightDetailsIFrameLocator).toHaveAttribute(
      "scrolling",
      "no"
    );
    await expect(addedInsightDetailsIFrameLocator).toHaveAttribute(
      "allowfullscreen",
      "true"
    );

    // Wait for PowerBI network requests
    await this.page.waitForResponse(
      (response) =>
        response.url().includes("app.powerbi.com") && response.status() === 200,
      { timeout: 30000 }
    );
    await this.tb.logSuccess(
      "Added insight details iframe is visible and loaded"
    );
    await this.tb.captureScreenshot(this.page, "added-insight-details-powerbi");
  }

  public async editedInsightIsNotVisible() {
    const notVisibleInsight = this.page.locator(
      this.getLocator(
        InsightsPageLocators.InsightLocatorByName("Test Report Automation")
      )
    );
    await expect(notVisibleInsight).not.toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Edited insight is not visible");
    await this.tb.captureScreenshot(this.page, "edited-insight-not-visible");
  }

  public async verifyEditedInsightHasUpdatedName() {
    const editedInsight = this.page.locator(
      this.getLocator(
        InsightsPageLocators.InsightLocatorByName(
          "Test Report Automation Edited"
        )
      )
    );
    await expect(editedInsight).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Edited insight is visible with updated name");
    await this.tb.captureScreenshot(
      this.page,
      "edited-insight-visible-with-updated-name"
    );
  }
}
