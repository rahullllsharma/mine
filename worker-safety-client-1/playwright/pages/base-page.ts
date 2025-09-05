import type { Locator, Page } from "@playwright/test";

export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  getByTestId(testId: string): Locator {
    return this.page.locator(`data-testid=${testId}`);
  }

  getByTestIdText(testId: string, textInput: string): Locator {
    return this.page.locator(`data-testid=${testId} >> text=${textInput}`);
  }

  getByTestIdLabelText(testId: string, labelText: string): Locator {
    return this.page.locator(
      `data-testid=${testId} >> label:has-text('${labelText}')`
    );
  }

  getInputByPlaceHolder(text: string): Locator {
    return this.page.locator(`[placeholder='${text}']`);
  }

  getBtnByText(btnName: string): Locator {
    return this.page.locator(
      `button:has-text('${btnName}') , div[role=button]:has-text('${btnName}')`
    );
  }

  getDivOptByText(text: string): Locator {
    return this.page.locator(`div[role=option]:has-text('${text}')`);
  }

  getBtnByTab(tabName: string): Locator {
    return this.page.locator(`button[role=tab]:has-text('${tabName}')`);
  }

  getByText(text: string): Locator {
    return this.page.locator(`text=${text}`);
  }

  getListByRoleOption(text: string): Locator {
    return this.page.locator(`li[role="option"]:has-text('${text}')`);
  }

  getHeaderByText(header: string, text: string): Locator {
    return this.page.locator(`${header}:has-text('${text}')`);
  }

  getRadioByText(text: string, value: string): Locator {
    return this.page.locator(
      `text=${text} >> [role=radio]:has-text('${value}')`
    );
  }

  getInputByName(name: string): Locator {
    return this.page.locator(`input[name='${name}']`);
  }
}
