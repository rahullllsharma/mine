import { expect, Page } from "@playwright/test";
import { LoginPageLocators } from "../Locators/LoginPageLocators";
import TestBase, { setProjectName, getProjectName } from "../Util/TestBase";
import * as allure from "allure-js-commons";
import { getEnvironmentData, CURRENT_ENV } from "../Data/envConfig";
import { Environment } from "../types/interfaces";

export default class LoginPage {
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

  public async EnterEmailId() {
    await this.tb.testStep("Enter the Email Id in Login page ", async () => {
      const EmailId = this.environmentData.username;
      const emailLocator = this.page.locator(
        this.getLocator(LoginPageLocators.LoginPage_txtUserName)
      );
      await expect(emailLocator).toBeVisible({ timeout: 15000 });
      await emailLocator.fill(EmailId);
      await this.tb.logSuccess("Entered the Email Id in Login page");
    });
  }

  public async EnterPassword() {
    await this.tb.testStep("Enter the Password in Login page ", async () => {
      const Password = this.environmentData.password;
      const passwordLocator = this.page.locator(
        this.getLocator(LoginPageLocators.LoginPage_txtPwd)
      );
      await expect(passwordLocator).toBeVisible({ timeout: 15000 });
      await passwordLocator.fill(Password);
      await this.tb.logSuccess("Entered the Password in Login page");
    });
  }

  public async ClickLoginBtn() {
    await this.tb.testStep("Click on Login Button in Login page ", async () => {
      const loginBtn_locator = this.page.locator(
        this.getLocator(LoginPageLocators.LoginPage_btnSignIn)
      );
      await expect(loginBtn_locator).toBeVisible({ timeout: 15000 });
      await loginBtn_locator.click();
      await this.tb.logSuccess("Clicked on Login Button in Login page");
    });
  }
  public async Login() {
    await this.EnterEmailId();
    await this.EnterPassword();
    await this.ClickLoginBtn();
  }
  public async getURL() {
    return this.page.url();
  }
}
