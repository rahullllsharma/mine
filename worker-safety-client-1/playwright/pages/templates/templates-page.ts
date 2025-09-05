import type { Locator } from "@playwright/test";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

export class TemplatesPage extends BasePage {
  readonly url: string = "/templates";
  readonly createTemplateButton: Locator = this.page.getByRole("button", {
    name: "Create template",
  });

  async createTemplate() {
    await this.createTemplateButton.click();
    await expect(this.page).toHaveURL(this.url + "/create");
  }

  async isOnPage() {
    await expect(this.page).toHaveURL(this.url);
    await expect(
      this.page.getByRole("heading", { name: "Templates" })
    ).toBeVisible();
    await expect(
      this.page.getByRole("tab", { name: "Published" })
    ).toBeVisible();
    await expect(this.page.getByPlaceholder("Search Templates")).toBeVisible();
    await expect(
      this.page.getByRole("button", { name: "Filters" })
    ).toBeVisible();
    await expect(this.createTemplateButton).toBeVisible();
  }
}
