import { Page, Locator, expect } from "@playwright/test";
import TestBase, { setProjectName, getProjectName } from "../Util/TestBase";
import { getEnvironmentData, CURRENT_ENV } from "../Data/envConfig";
import { Environment } from "../types/interfaces";
import { AdminPageLocators } from "../Locators/AdminPageLocators";
import { HomePageLocators } from "../Locators/HomePageLocators";

const dummyReportName = "Test Report Automation";
const dummyReportURL =
  "https://app.powerbi.com/reportEmbed?reportId=fdbdec2d-fc97-4b41-ab5b-1547db914898&autoAuth=true&ctid=365ac0c2-c69c-4b60-8dec-beafdb74a78c";
const dummyReportDescription = "Report Description";

export default class AdminPage {
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

  public async navigateToAdminPage() {
    const locator = this.page.locator(
      this.getLocator(HomePageLocators.HomePage_MainMenu_btnAdmin)
    );
    await expect(locator).toBeVisible();
    await locator.click();
    await this.page.waitForURL(`${this.environmentData.url}admin/config`, {
      timeout: 20000,
    });
    const highlightedLocator = this.page.locator(
      this.getLocator(HomePageLocators.HomePage_MainMenu_highlightedAdminBtn)
    );
    await expect(highlightedLocator).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Navigated to Admin page");
  }

  public async verifyInsightsButton() {
    const insightsButton = this.page.locator(
      this.getLocator(AdminPageLocators.VerticalNav_btnInsights)
    );
    await expect(insightsButton).toBeVisible({ timeout: 10000 });
    await insightsButton.click();

    const highlightedTabLocator = this.getLocator(
      AdminPageLocators.VerticalNav_btnInsights_highlighted
    );
    await this.page.waitForSelector(highlightedTabLocator);
    const highlightedTab = this.page.locator(highlightedTabLocator);
    await expect(highlightedTab).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Insights button is visible and clickable");
  }

  public async validateInsightsPageUI() {
    await expect(
      this.page.getByRole("heading", { name: "Insights", level: 2 })
    ).toBeVisible();
    await expect(
      this.page.getByText("Create and modify Insights for your organization")
    ).toBeVisible();
    await expect(
      this.page.getByRole("button", { name: "Add Insights" })
    ).toBeVisible();
    await expect(
      this.page.getByTestId("table-header-Report Name")
    ).toBeVisible();
    await expect(this.page.getByTestId("table-header-Url")).toBeVisible();
    await expect(
      this.page.getByTestId("table-header-Created On")
    ).toBeVisible();
    await expect(
      this.page.getByTestId("table-header-Visibility")
    ).toBeVisible();
    await expect(this.page.getByTestId("table-header-actions")).toBeVisible();
    const tableBody = this.page.getByTestId("table-body");
    await expect(tableBody).toBeVisible();
    const rows = await tableBody.locator('[role="row"]').count();
    await this.tb.logSuccess(`Table has ${rows} rows`);
  }

  public async verifyAndClickAddInsightsButton() {
    const addInsightsButton = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_btnAddInsights)
    );
    await expect(addInsightsButton).toBeVisible({ timeout: 10000 });
    await addInsightsButton.click();
    await this.tb.logSuccess("Add Insights button clicked");

    const addInsightsPopUp = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_addInsightsPopUp)
    );
    await expect(addInsightsPopUp).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Add Insights pop up visible");
  }

  public async verifyCancelButtonForPopUp() {
    const cancelButton = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_addInsightsPopUp_btnCancel)
    );
    await expect(cancelButton).toBeVisible({ timeout: 10000 });
    await cancelButton.click();
    await this.tb.logSuccess("Cancel button clicked");
    const addInsightsPopUp = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_addInsightsPopUp)
    );
    await expect(addInsightsPopUp).not.toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Add Insights pop up hidden");

    await this.tb.testStep("Reopen the add insights pop up", async () => {
      const addInsightsButton = this.page.locator(
        this.getLocator(AdminPageLocators.InsightsTab_btnAddInsights)
      );
      await expect(addInsightsButton).toBeVisible({ timeout: 10000 });
      await addInsightsButton.click();
      await this.tb.logSuccess("Add Insights button clicked again");
      const addInsightsPopUp = this.page.locator(
        this.getLocator(AdminPageLocators.InsightsTab_addInsightsPopUp)
      );
      await expect(addInsightsPopUp).toBeVisible({ timeout: 10000 });
      await this.tb.logSuccess("Add Insights pop up visible again");
    });
  }

  public async verifyMandatoryFieldErrors() {
    const addReportBtn = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_addInsightsPopUp_btnAddReport
      )
    );
    await expect(addReportBtn).toBeVisible({ timeout: 10000 });
    await addReportBtn.click();
    await this.tb.logSuccess(
      "Add Report button clicked to validate mandatory fields"
    );

    const reportNameErr = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_mandatoryFieldNameErr)
    );
    await expect(reportNameErr).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Report name error visible");

    const reportURLErr = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_mandatoryFieldURLErr)
    );
    await expect(reportURLErr).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Report URL error visible");
  }

  public async fillInsightsDetailsAndSubmit() {
    const reportName = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_addInsightsPopUp_txtReportName
      )
    );
    await expect(reportName).toBeVisible({ timeout: 10000 });
    await expect(reportName).toBeEditable();
    await expect(reportName).toHaveAttribute("placeholder", "Type Report name");
    await expect(reportName).toHaveValue("");

    await reportName.fill("ab");
    const reportNameErr = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_mandatoryFieldNameErr)
    );
    await expect(reportNameErr).toBeVisible({ timeout: 10000 });
    const reportNameErrText = await reportNameErr.innerText();
    expect(reportNameErrText).toContain(
      "Attribute name should be longer than 3 characters"
    );
    await this.tb.logSuccess(
      "Report name error visible for less than 3 characters"
    );

    await reportName.clear();

    await reportName.fill(dummyReportName);
    await this.tb.logSuccess("Report name filled");

    const reportURL = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_addInsightsPopUp_txtReportURL
      )
    );
    await expect(reportURL).toBeVisible({ timeout: 10000 });
    await expect(reportURL).toBeEditable();
    await expect(reportURL).toHaveAttribute("placeholder", "BI report URL");
    await expect(reportURL).toHaveValue("");

    await reportURL.fill("abkasdnjakd");
    const reportURLErr = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_mandatoryFieldURLErr)
    );
    await expect(reportURLErr).toBeVisible({ timeout: 10000 });
    const reportURLErrText = await reportURLErr.innerText();
    expect(reportURLErrText).toContain("Please enter a valid URL");
    await this.tb.logSuccess("Report URL error visible for invalid URL");

    await reportURL.clear();

    await reportURL.fill(dummyReportURL);
    await this.tb.logSuccess("Report URL filled");

    const descriptionBox = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_addInsightsPopUp_txtReportDescription
      )
    );
    await expect(descriptionBox).toBeVisible({ timeout: 10000 });
    await expect(descriptionBox).toBeEditable();
    await expect(descriptionBox).toHaveAttribute(
      "placeholder",
      "Add brief description of report here"
    );
    await expect(descriptionBox).toHaveValue("");
    await descriptionBox.fill(dummyReportDescription);
    await this.tb.logSuccess("Report description filled");

    const visibilityCheckbox = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_addInsightsPopUp_checkboxVisibility
      )
    );
    await expect(visibilityCheckbox).toBeVisible({ timeout: 10000 });
    await expect(visibilityCheckbox).toHaveAttribute("value", "true");

    const addReportBtn = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_addInsightsPopUp_btnAddReport
      )
    );
    await expect(addReportBtn).toBeVisible({ timeout: 10000 });
    this.createdOnDate = new Date().toLocaleDateString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
    this.createdOnDate = this.createdOnDate.replace(/\b0/g, "");
    await addReportBtn.click();
    await this.tb.logSuccess("Add Report button clicked");
    try {
      const insightAddedSuccessMessage = this.page.getByText(
        "Insight added successfully"
      );
      await expect(insightAddedSuccessMessage).toBeVisible({ timeout: 10000 });
      await this.tb.logSuccess("Insight added successfully message visible");
    } catch (error) {
      await this.tb.logFailure(
        "Insight added successfully message not visible / insight with same name already exists"
      );
      throw new Error(
        "Insight added successfully message not visible: " + error
      );
    }
    await this.page.waitForTimeout(300);
  }

  public async verifyInsightsAddedSuccessfully() {
    const tableBody = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_tableBody)
    );
    await expect(tableBody).toBeVisible({ timeout: 10000 });
    const firstRow = tableBody.locator(
      this.getLocator(AdminPageLocators.InsightsTab_tableRow)
    );
    await expect(firstRow).toBeVisible({ timeout: 10000 });

    const reportNameCell = firstRow.locator(
      this.getLocator(AdminPageLocators.InsightsTab_reportNameCell)
    );
    await expect(reportNameCell).toHaveText(dummyReportName);

    const reportUrlCell = firstRow.locator(
      this.getLocator(AdminPageLocators.InsightsTab_reportURLCell)
    );
    await expect(reportUrlCell).toHaveText(dummyReportURL);

    const createdOnCell = firstRow.locator(
      this.getLocator(AdminPageLocators.InsightsTab_createdOnCell)
    );
    await expect(createdOnCell).toBeVisible({ timeout: 10000 });
    await expect(createdOnCell).toHaveText(this.createdOnDate);

    const visibilityCell = firstRow.locator(
      this.getLocator(AdminPageLocators.InsightsTab_visibilityCell)
    );
    await expect(visibilityCell).toHaveText("Visible");

    const actionThreeDotsButton = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_actionThreeDotsButton)
    );
    await expect(actionThreeDotsButton).toBeVisible({ timeout: 10000 });

    await this.tb.logSuccess(
      "Newly added insight is present as the first row in the table."
    );
  }

  public async navigateToInsightsPage() {
    const insightsButton = this.page.locator(
      this.getLocator(HomePageLocators.HomePage_MainMenu_btnInsights)
    );
    await expect(insightsButton).toBeVisible({ timeout: 10000 });
    await insightsButton.click();
    await this.tb.logSuccess(
      "Clicked on Insights button to navigate to Insights page"
    );

    await this.page.waitForTimeout(3000);

    const highlightedLocator = this.page.locator(
      this.getLocator(HomePageLocators.HomePage_MainMenu_highlightedInsightsBtn)
    );
    await expect(highlightedLocator).toBeVisible();
    await this.tb.logSuccess(
      "Insights button is highlighted and now on Insights page"
    );
  }

  public async editVisibilityOfAddedInsight() {
    const tableBody = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_tableBody)
    );
    await expect(tableBody).toBeVisible({ timeout: 10000 });

    // Wait for table to stabilize
    await this.page.waitForTimeout(1000);

    // Find first row by content instead of position
    const firstRow = this.page
      .locator('div[role="row"]')
      .filter({
        hasText: "Test Report Automation",
      })
      .first();
    await expect(firstRow).toBeVisible({ timeout: 10000 });

    await firstRow.scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(500);

    let actionThreeDotsButton = firstRow.locator(
      "button:has(i.ci-more_horizontal)"
    );

    if ((await actionThreeDotsButton.count()) === 0) {
      actionThreeDotsButton = this.page
        .locator("button:has(i.ci-more_horizontal)")
        .first();
    }

    await expect(actionThreeDotsButton).toBeVisible({ timeout: 10000 });

    await actionThreeDotsButton.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });

    await this.page.waitForTimeout(500);

    const editButton = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_recentInsights_menuItem_editButton
      )
    );
    await expect(editButton).toBeVisible({ timeout: 10000 });
    await editButton.click();

    await this.page.waitForTimeout(500);

    const popUpDiv = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_addInsightsPopUp)
    );
    await expect(popUpDiv).toBeVisible({ timeout: 10000 });

    const visibilityCheckbox = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_addInsightsPopUp_checkboxVisibility
      )
    );
    await expect(visibilityCheckbox).toBeVisible({ timeout: 10000 });
    await expect(visibilityCheckbox).toHaveAttribute("value", "true");
    await visibilityCheckbox.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });
    await expect(visibilityCheckbox).toHaveAttribute("value", "false");

    const saveReportBtn = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_editInsightsPopUp_btnSaveReport
      )
    );
    await expect(saveReportBtn).toBeVisible({ timeout: 10000 });
    await saveReportBtn.click();

    await this.page.waitForTimeout(1000);

    const updateSuccessMessage = this.page.getByText(
      "Insight updated successfully"
    );
    await expect(updateSuccessMessage).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Insight updated successfully message visible");

    // Use the same row reference for consistency
    const visibilityCell = firstRow.locator(
      this.getLocator(AdminPageLocators.InsightsTab_visibilityCell)
    );
    await expect(visibilityCell).toHaveText("Not visible");

    await this.tb.logSuccess(
      "Visibility of the insight is updated to 'Not visible'"
    );
  }

  public async editNameOfAddedInsightAndMakeItVisible() {
    const tableBody = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_tableBody)
    );
    await expect(tableBody).toBeVisible({ timeout: 10000 });
    const firstRow = tableBody.locator(
      this.getLocator(AdminPageLocators.InsightsTab_tableRow)
    );
    await expect(firstRow).toBeVisible({ timeout: 10000 });

    const actionThreeDotsButton = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_actionThreeDotsButton)
    );
    await expect(actionThreeDotsButton).toBeVisible({ timeout: 10000 });
    await actionThreeDotsButton.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });

    const editButton = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_recentInsights_menuItem_editButton
      )
    );
    await expect(editButton).toBeVisible({ timeout: 10000 });
    await editButton.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });

    await this.page.waitForTimeout(300);

    const popUpDiv = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_addInsightsPopUp)
    );
    await expect(popUpDiv).toBeVisible({ timeout: 10000 });

    const reportNameInput = popUpDiv.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_addInsightsPopUp_txtReportName
      )
    );
    await expect(reportNameInput).toBeVisible({ timeout: 10000 });
    await expect(reportNameInput).toHaveValue(dummyReportName);
    await reportNameInput.clear();
    await reportNameInput.fill(dummyReportName + " Edited");

    const visibilityCheckbox = popUpDiv.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_addInsightsPopUp_checkboxVisibility
      )
    );
    await expect(visibilityCheckbox).toBeVisible({ timeout: 10000 });
    await visibilityCheckbox.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });
    await expect(visibilityCheckbox).toHaveAttribute("value", "true");

    const saveReportBtn = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_editInsightsPopUp_btnSaveReport
      )
    );
    await expect(saveReportBtn).toBeVisible({ timeout: 10000 });
    await saveReportBtn.click();

    await this.page.waitForTimeout(300);

    const updateSuccessMessage = this.page.getByText(
      "Insight updated successfully"
    );
    await expect(updateSuccessMessage).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Insight updated successfully message visible");

    const reportNameCell = firstRow.locator(
      this.getLocator(AdminPageLocators.InsightsTab_reportNameCell)
    );
    await expect(reportNameCell).toHaveText(dummyReportName + " Edited");

    await this.tb.logSuccess(
      "Name of the insight is updated to 'Test Report Automation Edited'"
    );
  }

  public async deleteAddedInsight() {
    const tableBody = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_tableBody)
    );
    await expect(tableBody).toBeVisible({ timeout: 10000 });
    const firstRow = tableBody.locator(
      this.getLocator(AdminPageLocators.InsightsTab_tableRow)
    );
    await expect(firstRow).toBeVisible({ timeout: 10000 });

    const actionThreeDotsButton = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_actionThreeDotsButton)
    );
    await expect(actionThreeDotsButton).toBeVisible({ timeout: 10000 });
    await actionThreeDotsButton.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });

    const deleteButton = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_recentInsights_menuItem_deleteButton
      )
    );
    await expect(deleteButton).toBeVisible({ timeout: 10000 });
    await deleteButton.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });

    const deletConfirmationPopUp = this.page.locator(
      this.getLocator(AdminPageLocators.InsightsTab_deleteConfirmationPopUp)
    );
    await expect(deletConfirmationPopUp).toBeVisible({ timeout: 10000 });
    const popUpTitle = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_deleteConfirmationPopUp_title
      )
    );
    await expect(popUpTitle).toBeVisible({ timeout: 10000 });

    const cancelPopUpBtn = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_deleteConfirmationPopUp_btnCancel
      )
    );
    await expect(cancelPopUpBtn).toBeVisible({ timeout: 10000 });
    await cancelPopUpBtn.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });

    await this.tb.logSuccess(
      "Cancel button clicked in delete confirmation pop up"
    );

    await expect(deletConfirmationPopUp).not.toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Delete confirmation pop up cancelled");

    await actionThreeDotsButton.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });
    await deleteButton.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });

    await this.page.waitForTimeout(300);

    await expect(deletConfirmationPopUp).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Delete confirmation pop up visible again");

    const deleteReportBtn = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_deleteConfirmationPopUp_btnDeleteReport
      )
    );
    await expect(deleteReportBtn).toBeVisible({ timeout: 10000 });
    await deleteReportBtn.evaluate((el) => {
      if (el instanceof HTMLElement) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.click();
      }
    });

    await this.page.waitForTimeout(300);

    const updateSuccessMessage = this.page.getByText(
      "Insight deleted successfully"
    );
    await expect(updateSuccessMessage).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess("Insight deleted successfully message visible");

    await this.page.waitForTimeout(300);

    const rowWithInsightName = this.page.locator(
      this.getLocator(
        AdminPageLocators.InsightsTab_rowWithInsightName(
          dummyReportName + " Edited"
        )
      )
    );
    await expect(rowWithInsightName).not.toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess(
      "Row with the insight name 'Test Report Automation Edited' not present in the table"
    );
  }
}
