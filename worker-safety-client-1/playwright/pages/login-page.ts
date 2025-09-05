import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "./base-page";

export class LoginPage extends BasePage {
  // Selectors
  readonly username: Locator = this.getInputByName("username");
  readonly password: Locator = this.getInputByName("password");
  readonly signInButton: Locator = this.page.locator("input", {
    hasText: "Sign In",
  });
  readonly invalidCredentialsText: Locator = this.page.locator(
    "#input-error:has-text('Invalid username or password.')"
  );

  async login(email: any, password: any) {
    await this.username.fill(email);
    await this.password.fill(password);
    await this.signInButton.click();
  }

  async wrongCredentialsValidation() {
    await expect(this.invalidCredentialsText).toBeVisible();
  }
}
