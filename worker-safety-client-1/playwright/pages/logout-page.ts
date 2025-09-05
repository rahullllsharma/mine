import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "./base-page";

export class LogoutPage extends BasePage {
  // Selectors
  readonly signInText: Locator = this.getByText("Sign in to your account");

  /**
   * Function that validates if the user is logged out
   */
  async userIsLoggedOut() {
    // await expect(this.page.url()).toContain(process.env.KEYCLOAK_URL);
    console.log("Being redirect to", process.env.KEYCLOAK_URL);
    await expect(this.page).toHaveURL(new RegExp(process.env.KEYCLOAK_URL));
    await expect(this.signInText).toBeVisible();
  }
}
