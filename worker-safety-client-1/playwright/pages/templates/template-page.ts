import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class TemplatePage extends BasePage {
  readonly url: string = "/templates/create";
  readonly nameInput: Locator = this.page.getByPlaceholder(
    "Enter the form name *"
  );
  readonly checkMarkButton: Locator = this.page
    .locator('header:not([data-testid="navbar"])')
    .filter({ hasText: "Click on ✔ icon to confirm the title name" })
    .getByRole("button")
    .first();
  readonly xMarkButton: Locator = this.page
    .locator('header:not([data-testid="navbar"])')
    .filter({ hasText: "Click on ✔ icon to confirm the title name" })
    .getByRole("button")
    .nth(1);
  readonly nameEditButton: Locator = this.page
    .locator('header:not([data-testid="navbar"])')
    .filter({ hasNotText: "Click on ✔ icon to confirm the title name" })
    .getByRole("button");
  readonly addPageButton: Locator = this.page.locator(
    "#headlessui-menu-button-49"
  );

  async fillTemplateName(templateName: string) {
    console.log(`Fill ${templateName} Template Name`);

    // validate initial state
    await expect(this.nameInput).toHaveValue("");
    await expect(this.checkMarkButton).toBeVisible({ visible: false });
    await expect(this.xMarkButton).toBeVisible({ visible: false });

    // fill the input field
    await this.nameInput.fill(templateName);

    // validate the state after filling the name
    await expect(this.checkMarkButton).toBeVisible();
    await expect(this.checkMarkButton.locator("i")).toHaveClass("ci-check_big");
    await expect(this.xMarkButton).toBeVisible();
    await expect(this.xMarkButton.locator("i")).toHaveClass("ci-close_big");

    // save the name
    await this.checkMarkButton.click();

    // validate the state after saving the name
    await expect(this.checkMarkButton).toBeVisible({ visible: false });
    await expect(this.xMarkButton).toBeVisible({ visible: false });
    await this.nameInput.isHidden();
    await this.page
      .locator('header:not([data-testid="navbar"])')
      .filter({ hasText: templateName });
  }

  async updateTemplateName(templateName: string) {
    console.log(`Update ${templateName} Template Name`);

    // click on edit button
    await this.nameEditButton.click();
    await expect(this.checkMarkButton).toBeVisible();
    await expect(this.xMarkButton).toBeVisible();

    // refill the input field
    await this.nameInput.fill(templateName);

    // save
    await this.checkMarkButton.click();

    // validate state
    await this.nameInput.isHidden();
    await this.page
      .locator('header:not([data-testid="navbar"])')
      .filter({ hasText: templateName });
  }

  async clearTemplateName() {
    console.log(`Clear Template Name`);

    // click on edit button
    await this.nameEditButton.click();
    await expect(this.checkMarkButton).toBeVisible();
    await expect(this.xMarkButton).toBeVisible();

    // clear text with x mark button
    await this.xMarkButton.click();
    await expect(this.nameInput).toHaveValue("");
    await expect(this.checkMarkButton).toBeVisible({ visible: false });
    await expect(this.xMarkButton).toBeVisible({ visible: false });
  }

  async addPage() {
    await this.addPageButton.click();
  }

  async isOnPage() {
    await expect(this.page).toHaveURL(this.url);
    await expect(this.nameInput).toBeVisible();
    await expect(
      this.page.getByRole("button", { name: "Close" })
    ).toBeVisible();
    await expect(this.page.getByRole("button", { name: "Save" })).toBeVisible();
    await expect(
      this.page.getByRole("button", { name: "Preview" })
    ).toBeVisible();
    await expect(
      this.page.getByRole("button", { name: "Publish" })
    ).toBeVisible();
  }

  async isBlankPage() {
    await this.isOnPage();

    await expect(this.nameInput).toBeEmpty();
    await expect(
      this.page.getByRole("heading", { name: "No Pages added" })
    ).toBeVisible();
  }
}
