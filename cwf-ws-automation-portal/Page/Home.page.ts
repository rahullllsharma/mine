import { Page } from "@playwright/test";
import { HomePageLocators } from "../Locators/HomePageLocators";
import TestBase, { setProjectName, getProjectName } from "../Util/TestBase";
import { expect } from "@playwright/test";
import * as allure from "allure-js-commons";
import * as cred from "../Data/local.cred.json";
import { Environment } from "../types/interfaces";
import { getEnvironmentData, CURRENT_ENV } from "../Data/envConfig";

export default class HomePage {
  private page: Page;
  private tb: TestBase;
  private environmentData: Environment;
  private projectName: string;
  constructor(page: Page) {
    this.page = page;
    this.tb = new TestBase(page);
    this.environmentData = getEnvironmentData();
    this.projectName = getProjectName();
  }

  private getLocator(locatorObj: { mobile: string; desktop: string }): string {
    return this.projectName === "iPad Mini"
      ? locatorObj.mobile
      : locatorObj.desktop;
  }

  public async waitForHomePageLoad() {
    await this.tb.logMessage(
      `Logged in as ${this.environmentData.username} in ${CURRENT_ENV} environment`
    );
    await this.tb.testStep("Waiting for the Home page to load", async () => {
      const locator = this.getLocator(
        HomePageLocators.HomePage_MainHeader_lblWorkPackages
      );
      await this.page.waitForSelector(locator, { timeout: 25000 });
      await this.page.waitForTimeout(10000);
      await this.tb.logSuccess(
        "User is logged in and Home page loaded successfully"
      );
    });
  }

  public async NavigateToFormsListTab() {
    await this.tb.testStep("Navigate to Forms List tab", async () => {
      const btnFormListMainMenu = this.page.locator(
        this.getLocator(HomePageLocators.HomePage_MainMenu_btnFormsList)
      );
      await expect(btnFormListMainMenu).toBeVisible({ timeout: 10000 });
      await btnFormListMainMenu.click();
      await this.page.waitForURL(`${this.environmentData.url}forms`, {
        timeout: 25000,
      });
      await this.page.waitForTimeout(5000);
      const btnHighlightedFormsList = this.page.locator(
        this.getLocator(
          HomePageLocators.HomePage_MainMenu_highlightedFormsListBtn
        )
      );
      await expect(btnHighlightedFormsList).toBeVisible({ timeout: 10000 });
      await this.tb.logSuccess("Navigated to Forms List tab");
    });
  }

  public async navigateToTemplateFormsTab() {
    await this.tb.testStep("Navigate to Template Forms tab", async () => {
      const locator = this.getLocator(
        HomePageLocators.HomePage_MainMenu_btnTemplateForms
      );
      const templateFormsTab = this.page.locator(locator);
      await expect(templateFormsTab).toBeVisible({
        timeout: 10000,
      });
      await templateFormsTab.click();
      await this.page.waitForURL(`${this.environmentData.url}template-forms`);
      await this.page.waitForTimeout(5000);
      // await this.page.goto(`${this.environmentData.url}template-forms/add?templateId=${cred.templateID}`);
      // await this.page.waitForTimeout(10000);
      await this.tb.logSuccess("Navigated to Template Forms tab");
    });
  }

  public async NavigateToMapTab() {
    await this.tb.testStep("Navigate to Map tab", async () => {
      const locator = this.getLocator(
        HomePageLocators.HomePage_MainMenu_btnMap
      );
      const mapTab = this.page.locator(locator);
      await expect(mapTab).toBeVisible({ timeout: 10000 });
      await mapTab.click();
      await this.page.waitForURL(`${this.environmentData.url}map`);
      await this.page.waitForTimeout(15000);
      await this.tb.logSuccess("Navigated to Map tab");
    });
  }

  public async NavigateToInsightsTab() {
    await this.tb.testStep("Navigate to Insights tab", async () => {
      const locator = this.getLocator(
        HomePageLocators.HomePage_MainMenu_btnInsights
      );
      const insightsTab = this.page.locator(locator);
      await expect(insightsTab).toBeVisible({ timeout: 10000 });
      await insightsTab.click();
      await this.page.waitForURL(`${this.environmentData.url}insights`);
      await this.page.waitForTimeout(5000);
      await this.tb.logSuccess("Navigated to Insights tab");
    });
  }

  public async NavigateToTemplatesTab() {
    await this.tb.testStep("Navigate to Templates tab", async () => {
      try {
        const locator = this.getLocator(
          HomePageLocators.HomePage_MainMenu_lblTemplates
        );
        const templatesTab = this.page.locator(locator);
        if (await templatesTab.isVisible({ timeout: 5000 })) {
          await templatesTab.click();
          await this.page.waitForTimeout(5000);
          await this.tb.logSuccess("Navigated to Templates tab");
        } else {
          await this.tb.logMessage("Templates tab not found, skipping");
        }
      } catch (error) {
        await this.tb.logMessage("Templates tab not available, skipping");
      }
    });
  }

  public async getAllAvailableTabs(): Promise<
    Array<{ name: string; locator: string }>
  > {
    const tabs = [];

    // Get all tab buttons
    const allTabButtons = this.page.locator(
      this.getLocator(HomePageLocators.HomePage_MainMenu_btnTabsAll)
    );
    const tabCount = await allTabButtons.count();

    for (let i = 0; i < tabCount; i++) {
      try {
        const tabButton = allTabButtons.nth(i);
        const tabText = await tabButton.textContent();
        const tabName = tabText?.trim() || "";

        if (tabName) {
          const locator = `(${this.getLocator(
            HomePageLocators.HomePage_MainMenu_btnTabsAll
          )})[${i + 1}]`;

          tabs.push({
            name: tabName,
            locator: locator,
          });
        }
      } catch (error) {
        // Skip tabs that can't be read
        continue;
      }
    }

    return tabs;
  }

  public async navigateToTab(
    tabName: string
  ): Promise<{ success: boolean; url?: string }> {
    try {
      const tabs = await this.getAllAvailableTabs();
      const targetTab = tabs.find(
        (tab) =>
          tab.name.toLowerCase().includes(tabName.toLowerCase()) ||
          tabName.toLowerCase().includes(tab.name.toLowerCase())
      );

      if (targetTab) {
        const tabButton = this.page.locator(targetTab.locator);
        await tabButton.click();

        // Wait for tab to be highlighted with dynamic wait up to 20 seconds
        const highlightedTabLocator = this.getHighlightedTabLocator(
          targetTab.name
        );
        const highlightedTab = this.page.locator(highlightedTabLocator);

        try {
          //extended time limit for tab highlighting
          await highlightedTab.waitFor({ state: "visible", timeout: 60000 });

          // Get the actual URL after navigation
          const currentUrl = this.page.url();
          await this.tb.logSuccess(
            `Navigated to ${targetTab.name} tab and validated highlighting. Current URL: ${currentUrl}`
          );
          return { success: true, url: currentUrl };
        } catch (waitError) {
          await this.tb.logFailure(
            `Tab "${targetTab.name}" was clicked but highlighting validation failed after 60 seconds: ${waitError}`
          );
          return { success: false };
        }
      } else {
        await this.tb.logMessage(`Tab "${tabName}" not found`);
        return { success: false };
      }
    } catch (error) {
      await this.tb.logFailure(
        `Failed to navigate to tab "${tabName}": ${error}`
      );
      return { success: false };
    }
  }

  private getHighlightedTabLocator(tabName: string): string {
    // Generic highlighted tab locator for all tabs
    return `//button[@role='tab']/div[contains(@class, 'border-brand-urbint-40')]/span[text()='${tabName}' and @class='text-base mx-1 truncate']`;
  }
}
