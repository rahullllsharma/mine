import { Page, Locator, expect } from "@playwright/test";
import TestBase, { setProjectName, getProjectName } from "../Util/TestBase";
import { getEnvironmentData, CURRENT_ENV } from "../Data/envConfig";
import { Environment } from "../types/interfaces";
import { WorkPackagePageLocators } from "../Locators/WorkPackagePageLocators";

let workPageUniqueNameCode: string | null = null;

export default class WorkPackagePage {
  private page: Page;
  private tb: TestBase;
  private currentEnv: string;
  private projectName: string;
  private environmentData: Environment;

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

  public async fillWorkOrderOrProjectName(value: string) {
    if (!workPageUniqueNameCode) {
      workPageUniqueNameCode = Math.floor(100 + Math.random() * 900).toString();
    }
    const uniqueValue = `${value}${workPageUniqueNameCode}`;
    const locator = this.page.locator(
      this.getLocator(WorkPackagePageLocators.WorkOrderOrProjectNameInput)
    );
    await expect(locator).toBeVisible();
    await locator.fill(uniqueValue);
    await expect(locator).toHaveValue(uniqueValue);
  }

  public async fillProjectNumberOrKey(value: string) {
    const locator = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ProjectNumberOrKeyInput)
    );
    await expect(locator).toBeVisible();
    await locator.fill(value);
    await expect(locator).toHaveValue(value);
  }

  public async selectProjectType(optionText: string) {
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ProjectTypeDropdown)
    );
    await expect(dropdown).toBeVisible();
    await dropdown.click();
    const option = this.page.getByRole("option", { name: optionText });
    await expect(option).toBeVisible();
    await option.click();
    await expect(dropdown).toContainText(optionText);
  }

  public async selectWorkTypes(optionText1: string, optionText2: string) {
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.WorkTypesDropdown)
    );
    await expect(dropdown).toBeVisible({ timeout: 5000 });
    await dropdown.click();
    const option1 = this.page.getByRole("option", {
      name: optionText1,
      exact: true,
    });
    await expect(option1).toBeVisible({ timeout: 5000 });
    await option1.click();
    const option2 = this.page.getByRole("option", {
      name: optionText2,
      exact: true,
    });
    await expect(option2).toBeVisible({ timeout: 5000 });
    await option2.click();
    await dropdown.click();
    await this.page.waitForTimeout(200);
  }

  public async selectAssetType(optionText: string) {
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AssetTypeDropdown)
    );
    await expect(dropdown).toBeVisible();
    await dropdown.click();
    const option = this.page.getByRole("option", { name: optionText });
    await expect(option).toBeVisible();
    await option.click();
    await expect(dropdown).toContainText(optionText);
  }

  public async selectStatus(optionText: string) {
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.StatusDropdown)
    );
    await expect(dropdown).toBeVisible();
    await dropdown.click();
    const option = this.page.getByRole("option", { name: optionText });
    await expect(option).toBeVisible();
    await option.click();
    await expect(dropdown).toContainText(optionText);
  }

  public async fillProjectZipCode(value: string) {
    const locator = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ProjectZipCodeInput)
    );
    await expect(locator).toBeVisible();
    await locator.fill(value);
    await expect(locator).toHaveValue(value);
  }

  public async fillStartDate(value: string) {
    const locator = this.page.locator(
      this.getLocator(WorkPackagePageLocators.StartDateInput)
    );
    await expect(locator).toBeVisible();
    await locator.fill(value);
    await expect(locator).toHaveValue(value);
  }

  public async fillEndDate(value: string) {
    const locator = this.page.locator(
      this.getLocator(WorkPackagePageLocators.EndDateInput)
    );
    await expect(locator).toBeVisible();
    await locator.fill(value);
    await expect(locator).toHaveValue(value);
  }

  public async selectAreaOrDivision(optionText: string) {
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AreaOrDivisionDropdown)
    );
    await expect(dropdown).toBeVisible();
    await dropdown.click();
    const option = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AreaOrDivisionOption)
    );
    await expect(option).toBeVisible();
    await this.tb.logMessage(
      `Selecting ${await option.innerText()} from area/division dropdown`
    );
    await option.click();
  }

  public async selectOperatingHQorRegion(optionText: string) {
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.OperatingHQorRegionDropdown)
    );
    await expect(dropdown).toBeVisible();
    await dropdown.click();
    const option = this.page.locator(
      this.getLocator(WorkPackagePageLocators.OperatingHQorRegionOption)
    );
    await expect(option).toBeVisible();
    await this.tb.logMessage(
      `Selecting ${await option.innerText()} from operating HQ/region dropdown`
    );
    await option.click();
  }

  public async fillDescription(value: string) {
    const locator = this.page.locator(
      this.getLocator(WorkPackagePageLocators.DescriptionTextarea)
    );
    await expect(locator).toBeVisible();
    await locator.fill(value);
    await expect(locator).toHaveValue(value);
  }

  public async fillEngineerName(value: string) {
    const locator = this.page.locator(
      this.getLocator(WorkPackagePageLocators.EngineerNameInput)
    );
    await expect(locator).toBeVisible();
    await locator.fill(value);
    await expect(locator).toHaveValue(value);
  }

  public async fillContractReferenceNumber(value: string) {
    const locator = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ContractReferenceNumberInput)
    );
    await expect(locator).toBeVisible();
    await locator.fill(value);
    await expect(locator).toHaveValue(value);
  }

  public async fillContractName(value: string) {
    const locator = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ContractNameInput)
    );
    await expect(locator).toBeVisible();
    await locator.fill(value);
    await expect(locator).toHaveValue(value);
  }

  public async selectContractor(optionText: string) {
    if (this.currentEnv === "integ" || this.currentEnv === "staging") {
      const dropdown = this.page.locator(
        this.getLocator(WorkPackagePageLocators.ContractorDropdown)
      );
      await expect(dropdown).toBeVisible();
      await dropdown.click();
      const option = this.page.locator(
        this.getLocator(WorkPackagePageLocators.ContractorOption)
      );
      await expect(option).toBeVisible();
      await this.tb.logMessage(
        `Selecting ${await option.innerText()} from contractor dropdown`
      );
      await option.click();
    } else {
      await this.tb.logMessage(
        "Contractor dropdown is not visible in this environment"
      );
    }
  }

  public async addLocation(
    name: string,
    lat: string,
    long: string,
    primarySupervisor: string,
    additionalSupervisor: string
  ) {
    const nameInput = this.page.locator(
      this.getLocator(WorkPackagePageLocators.LocationNameInput)
    );
    const latInput = this.page.locator(
      this.getLocator(WorkPackagePageLocators.LocationLatInput)
    );
    const longInput = this.page.locator(
      this.getLocator(WorkPackagePageLocators.LocationLongInput)
    );

    await expect(nameInput).toBeVisible();
    await nameInput.fill(name);
    await expect(nameInput).toHaveValue(name);
    await expect(latInput).toBeVisible();
    await latInput.fill(lat);
    await expect(latInput).toHaveValue(lat);
    await expect(longInput).toBeVisible();
    await longInput.fill(long);
    await expect(longInput).toHaveValue(long);

    // Primary Supervisor
    if (this.currentEnv === "staging" || this.currentEnv === "production") {
      const primaryDropdown = this.page.locator(
        this.getLocator(
          WorkPackagePageLocators.LocationPrimarySupervisorDropdown
        )
      );
      await expect(primaryDropdown).toBeVisible();
      await primaryDropdown.click();
      const primaryOption = this.page.locator(
        this.getLocator(WorkPackagePageLocators.LocationPrimarySupervisorOption)
      );
      await expect(primaryOption).toBeVisible();
      await primaryOption.click();
    }

    // Additional Supervisor
    const additionalDropdown = this.page.locator(
      this.getLocator(
        WorkPackagePageLocators.LocationAdditionalSupervisorDropdown
      )
    );
    await expect(additionalDropdown).toBeVisible();
    await additionalDropdown.click();
    const additionalOption = this.page.locator(
      this.getLocator(
        WorkPackagePageLocators.LocationAdditionalSupervisorOption
      )
    );
    await expect(additionalOption).toBeVisible();
    await additionalOption.click();
  }

  public async clickAddLocationButton() {
    const btn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AddLocationButton)
    );
    await expect(btn).toBeVisible();
    await btn.click();
  }

  public async selectProjectManager(optionText: string) {
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ProjectManagerDropdown)
    );
    await expect(dropdown).toBeVisible();
    await dropdown.click();
    const option = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ProjectManagerOption)
    );
    await expect(option).toBeVisible();
    await this.tb.logMessage(
      `Selecting ${await option.innerText()} from project manager dropdown`
    );
    await option.click();
  }

  public async selectPrimarySupervisor(optionText: string) {
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.PrimarySupervisorDropdown)
    );
    await expect(dropdown).toBeVisible();
    await dropdown.click();
    const option = this.page.locator(
      this.getLocator(WorkPackagePageLocators.PrimarySupervisorOption)
    );
    await expect(option).toBeVisible();
    await this.tb.logMessage(
      `Selecting ${await option.innerText()} from primary supervisor dropdown`
    );
    await option.click();
  }

  public async selectAdditionalSupervisor(optionText: string) {
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AdditionalSupervisorDropdown)
    );
    await expect(dropdown).toBeVisible();
    await dropdown.click();
    const option = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AdditionalSupervisorOption)
    );
    await expect(option).toBeVisible();
    await this.tb.logMessage(
      `Selecting ${await option.innerText()} from additional supervisor dropdown`
    );
    await option.click();
  }

  public async removeAdditionalSupervisor() {
    const btn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.RemoveAdditionalSupervisorButton)
    );
    await expect(btn).toBeVisible();
    await btn.click();
  }

  public async clickSave() {
    const saveBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SaveButton)
    );
    await expect(saveBtn).toBeVisible();
    await saveBtn.click();
    await this.page.waitForTimeout(2000);
  }

  public async deleteWorkPackage(workOrderName: string) {
    const settingsBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SettingsButton)
    );
    await expect(settingsBtn).toBeVisible();
    await settingsBtn.click();

    await this.page.waitForTimeout(2000);

    const deleteBtnIcon = this.page.locator(
      this.getLocator(WorkPackagePageLocators.DeleteButtonIcon)
    );
    await expect(deleteBtnIcon).toBeVisible({ timeout: 10000 });
    await deleteBtnIcon.click();

    const deletProjectPopUp = this.page.locator(
      this.getLocator(WorkPackagePageLocators.DeleteProjectPopup)
    );
    await expect(deletProjectPopUp).toBeVisible({ timeout: 10000 });

    const deleteProjectBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.DeleteProjectButton)
    );
    await expect(deleteProjectBtn).toBeVisible({ timeout: 10000 });
    await deleteProjectBtn.click();
    await this.page.waitForTimeout(2000);
  }

  public async clickAddWorkPackageButton() {
    const btn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AddWorkPackageButton)
    );
    await expect(btn).toBeVisible({ timeout: 20000 });
    await btn.click();
  }

  public async searchWorkPackage(name: string) {
    const searchInput = this.page.locator(
      this.getLocator(WorkPackagePageLocators.WorkPackageSearchInput)
    );
    await expect(searchInput).toBeVisible({ timeout: 20000 });
    const searchValue = workPageUniqueNameCode
      ? `${name}${workPageUniqueNameCode}`
      : name;
    await searchInput.fill(searchValue);
    await this.page.waitForTimeout(5000);
    await searchInput.press("Enter");
  }

  public async clearWorkPackageSearch() {
    const searchInput = this.page.locator(
      this.getLocator(WorkPackagePageLocators.WorkPackageSearchInput)
    );
    await expect(searchInput).toBeVisible({ timeout: 20000 });
    await searchInput.fill("");
    await searchInput.press("Enter");
    await this.page.waitForTimeout(2000);
  }

  public async selectTab(tab: "Active" | "Pending" | "Completed") {
    let tabLocator;
    if (tab === "Active") tabLocator = WorkPackagePageLocators.ActiveTab;
    else if (tab === "Pending") tabLocator = WorkPackagePageLocators.PendingTab;
    else tabLocator = WorkPackagePageLocators.CompletedTab;
    const tabBtn = this.page.locator(this.getLocator(tabLocator));
    await expect(tabBtn).toBeVisible({ timeout: 10000 });
    await tabBtn.click();
    await this.page.waitForTimeout(2000);
  }

  public async getFirstResultRowText(): Promise<string | null> {
    const row = this.page.locator(
      this.getLocator(WorkPackagePageLocators.WorkPackageResultRow)
    );
    if (await row.isVisible().catch(() => false)) {
      return await row.first().innerText();
    }
    return null;
  }

  public async isNoProjectsMessageVisible(): Promise<boolean> {
    const msg = this.page.locator(
      this.getLocator(WorkPackagePageLocators.NoProjectsMessage)
    );
    return await msg.isVisible().catch(() => false);
  }

  public async clickFirstResultRow(name: string) {
    const row = this.page.locator(
      this.getLocator(WorkPackagePageLocators.WorkPackageResultRow)
    );
    await expect(row).toBeVisible({ timeout: 20000 });

    const resultRowText = await row.first().innerText();
    try {
      expect(resultRowText).toContain(
        workPageUniqueNameCode ? `${name}${workPageUniqueNameCode}` : name
      );
      await this.tb.logSuccess(
        `Work order ${resultRowText} found in the list and matches unique work order name`
      );
      await row.first().click();
    } catch (err) {
      await this.tb.logFailure(
        `Work order ${resultRowText} not found in the list`
      );
      throw err;
    }
  }

  public async waitForFirstWorkOrderInList(tb: TestBase): Promise<boolean> {
    let found = false;
    for (let attempt = 1; attempt <= 3; attempt++) {
      const firstWorkOrderLink = this.page.locator(
        this.getLocator(WorkPackagePageLocators.WorkPackageResultRow)
      );
      if (
        await firstWorkOrderLink.isVisible({ timeout: 5000 }).catch(() => false)
      ) {
        found = true;
        break;
      }
      await tb.logMessage(
        `First work order not visible, attempt ${attempt}, scrolling...`
      );
      await this.page.mouse.wheel(0, 300 * attempt);
      await this.page.waitForTimeout(1000);
    }
    return found;
  }

  public async clickFirstWorkOrderInList(): Promise<string | null> {
    const firstWorkOrderLink = this.page.locator(
      this.getLocator(WorkPackagePageLocators.WorkPackageResultRow)
    );
    const workOrderText = await firstWorkOrderLink.textContent();
    await firstWorkOrderLink.click();
    await expect(this.page).toHaveURL(/\/projects\//, { timeout: 20000 });
    return workOrderText;
  }

  public async openSettingsForWorkOrder() {
    const settingsBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SettingsButton)
    );
    await expect(settingsBtn).toBeVisible({ timeout: 20000 });
    await settingsBtn.click();
    await expect(this.page).toHaveURL(/\/settings$/, { timeout: 20000 });
    await this.page.waitForTimeout(3000);
  }

  public async editDescriptionAndSave(): Promise<string> {
    const descBox = this.page.locator(
      this.getLocator(WorkPackagePageLocators.DescriptionTextarea)
    );
    await descBox.scrollIntoViewIfNeeded();
    await expect(descBox).toBeVisible({ timeout: 20000 });
    const oldValue = await descBox.inputValue();
    const newValue = oldValue === "Test updated" ? "Test" : "Test updated";
    await descBox.fill(newValue);
    await expect(descBox).toHaveValue(newValue, { timeout: 10000 });
    const saveBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SaveButton)
    );
    await expect(saveBtn).toBeVisible({ timeout: 20000 });
    await saveBtn.click();
    await this.page.waitForTimeout(3000);
    const toast = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ToastMessage)
    );
    if (await toast.isVisible({ timeout: 5000 }).catch(() => false)) {
      // Optionally log
    }
    return newValue;
  }

  public async goToHistoryTabAndVerifyUpdate(dateTimeString: string) {
    const historyTab = this.page.locator(
      this.getLocator(WorkPackagePageLocators.HistoryTabButton)
    );
    await expect(historyTab).toBeVisible({ timeout: 20000 });
    await historyTab.click();
    await this.page.waitForTimeout(4000);
    const historyHeader = this.page.locator(
      this.getLocator(WorkPackagePageLocators.HistoryHeader)
    );
    await expect(historyHeader).toBeVisible({ timeout: 20000 });

    const match = dateTimeString.match(
      /^(.+?)(?:,| at) (\d{1,2}:\d{2} [AP]M) GMT\+5:30$/
    );
    if (!match)
      throw new Error("Unrecognized dateTimeString format: " + dateTimeString);
    const [, date, time] = match;

    const locatorStr = this.getLocator(
      WorkPackagePageLocators.HistoryDateTimeEntry.flexible(date, time)
    );
    const dateTimeLocator = this.page.locator(locatorStr);
    await expect(dateTimeLocator).toBeVisible({ timeout: 10000 });
  }

  public async openFirstProjectIfAvailable(tb: TestBase): Promise<boolean> {
    const firstProjectLink = this.page.locator(
      this.getLocator(WorkPackagePageLocators.WorkPackageResultRow)
    );
    if (await firstProjectLink.isVisible().catch(() => false)) {
      await firstProjectLink.click();
      await this.page.waitForTimeout(2000);
      await expect(this.page).toHaveURL(/\/projects\//);
      await tb.logSuccess("First project opened and details screen validated.");
      return true;
    } else {
      await tb.logMessage("No projects available in the list to open.");
      return false;
    }
  }

  public async addActivity(activityTypes: string[], subActivities: string[][]) {
    const today = new Date();
    const endDate = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate() + 3
    )
      .toISOString()
      .split("T")[0];
    const addBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AddMenuButton)
    );
    await expect(addBtn).toBeVisible();
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        await addBtn.click();
        const activityMenu = this.page.getByRole("menuitem", {
          name: "Activity",
        });
        await this.page.waitForTimeout(1000);
        await expect(activityMenu).toBeVisible({ timeout: 5000 });
        break;
      } catch (error) {
        if (attempt === 3) {
          throw new Error(
            `Failed to click add button and show menu after 3 attempts: ${error}`
          );
        }
        await this.page.waitForTimeout(1000);
      }
    }
    const activityMenu = this.page.getByRole("menuitem", { name: "Activity" });
    await expect(activityMenu).toBeVisible();
    await activityMenu.click();
    await this.page.waitForTimeout(2000);
    for (let i = 0; i < activityTypes.length; i++) {
      const typeBtn = this.page.getByRole("button", {
        name: new RegExp(activityTypes[i], "i"),
      });
      await expect(typeBtn).toBeVisible();
      await typeBtn.click();
      for (const sub of subActivities[i]) {
        const subCheckbox = this.page.getByRole("checkbox", {
          name: new RegExp(sub, "i"),
        });
        await expect(subCheckbox).toBeVisible();
        await subCheckbox.check();
      }
    }
    const nextBtn = this.page.getByRole("button", {
      name: "Next",
      exact: true,
    });
    await expect(nextBtn).toBeVisible();
    await nextBtn.click();
    await this.page.waitForTimeout(1000);
    const endDateInput = this.page.getByLabel(/End date/i);
    await endDateInput.fill(endDate);
    await this.page.waitForTimeout(500);
    const addActivityBtn = this.page.getByRole("button", {
      name: /Add Activity/i,
      exact: true,
    });
    await expect(addActivityBtn).toBeEnabled();
    await addActivityBtn.click();
    const activityMenuRetryCheck = this.page.getByRole("menuitem", {
      name: "Activity",
    });
    const isMenuVisible = await activityMenuRetryCheck
      .isVisible({ timeout: 3000 })
      .catch(() => false);
    if (isMenuVisible) {
      await addActivityBtn.click();
    }
    await this.page.waitForTimeout(3000);
  }

  public async isActivityListed(activityName: string): Promise<boolean> {
    const entry = this.page.getByText(activityName, { exact: true }).nth(0);
    return await entry.isVisible({ timeout: 10000 }).catch(() => false);
  }

  public async openEditActivityModal(
    activityName: string,
    tb: TestBase
  ): Promise<void> {
    const menuBtnLocator = `(//div[contains(@class, "flex") and .//div[contains(text(), "${activityName}")]]//button[contains(@id, "headlessui-menu-button")])[1]`;
    const editMenuLocator = "//button[contains(.,'Edit Activity')]";
    await this.page.waitForTimeout(5000);
    const menuBtn = this.page.locator(menuBtnLocator);
    await expect(menuBtn).toBeVisible({ timeout: 10000 });
    await menuBtn.click({ force: true });
    const editMenu = this.page.locator(editMenuLocator);
    await expect(editMenu).toBeVisible({ timeout: 10000 });
    await editMenu.click({ force: true });
    const nameInput = this.page.getByLabel(/Activity name/i);
    await expect(nameInput).toBeVisible({ timeout: 2000 });
    await this.page.waitForTimeout(1500);
    const isStillVisible = await nameInput.isVisible();
    if (isStillVisible) {
      await tb.logSuccess(`Modal opened successfully`);
    } else {
      throw new Error(
        `Failed to open edit activity modal for activity: ${activityName}`
      );
    }
  }

  public async editActivity(activityName: string, newName: string) {
    const today = new Date();
    const newEndDate = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate() + 4
    )
      .toISOString()
      .split("T")[0];
    const nameInput = this.page.getByLabel(/Activity name/i);
    await nameInput.fill(newName);
    const endDateInput = this.page.getByLabel(/End date/i);
    await endDateInput.fill(newEndDate);
    const saveBtn = this.page.getByRole("button", {
      name: /Save Activity/i,
      exact: true,
    });
    await expect(saveBtn).toBeEnabled();
    await saveBtn.click();
    await this.page.waitForTimeout(4000);
  }

  public async deleteActivity(activityName: string, tb: TestBase) {
    const menuBtnLocator = `(//div[contains(@class, "flex") and .//div[contains(text(), "${activityName}")]]//button[contains(@id, "headlessui-menu-button")])[1]`;
    const deleteMenuLocator = "//button[contains(.,'Delete Activity')]";
    await tb.testStep("Open three dots menu and delete activity", async () => {
      await this.page.waitForTimeout(2500);
      const deleteMenu = await (async () => {
        let lastError;
        for (let i = 0; i < 3; i++) {
          try {
            const menuBtn = this.page.locator(menuBtnLocator);
            await menuBtn.click({ force: true });
            const menuItem = this.page.locator(deleteMenuLocator);
            await menuItem.waitFor({ state: "visible", timeout: 2000 });
            return menuItem;
          } catch (err) {
            lastError = err;
            await this.page.waitForTimeout(500);
          }
        }
        throw lastError;
      })();
      await deleteMenu.click();
      const confirmBtn = this.page.locator(
        "(//div[contains(@class,'flex justify-end')]//button)[2]"
      );
      await confirmBtn.click();
      await this.page.waitForTimeout(3000);
      const activity = this.page.getByText(activityName, { exact: true });
      await expect(activity).not.toBeVisible({ timeout: 10000 });
    });
  }

  public async addSiteCondition(tb: TestBase): Promise<string> {
    const addBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AddMenuButton)
    );
    await expect(addBtn).toBeVisible({ timeout: 10000 });
    await this.page.waitForTimeout(2000);
    await addBtn.click();
    const siteConditionMenu = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SiteConditionMenuItem)
    );
    await expect(siteConditionMenu).toBeVisible({ timeout: 10000 });
    await siteConditionMenu.click();
    const dropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SiteConditionDropdown)
    );
    await expect(dropdown).toBeEnabled({ timeout: 15000 });
    await dropdown.click();
    const firstOption = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SiteConditionFirstOption)
    );
    await expect(firstOption).toBeVisible({ timeout: 8000 });
    const selectedName = (await firstOption.textContent()) || "";
    await tb.logMessage(`Selected option: ${selectedName}`);
    await firstOption.click();
    const continueBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SiteConditionContinueButton)
    );
    await expect(continueBtn).toBeEnabled();
    await continueBtn.click();
    await this.page.waitForTimeout(1000);
    const switches = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SiteConditionSwitch)
    );
    await expect(switches).toBeVisible();
    const addSCBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AddSiteConditionButton)
    );
    await expect(addSCBtn).toBeEnabled();
    await addSCBtn.click();
    await expect(this.page.getByText("Site Condition added")).toBeVisible({
      timeout: 8000,
    });
    await this.page.waitForTimeout(3000);
    const siteCondList = this.page.locator(
      this.getLocator(
        WorkPackagePageLocators.SiteConditionListEntry(selectedName)
      )
    );
    await expect(siteCondList).toBeVisible({ timeout: 8000 });
    return selectedName;
  }

  public async isSiteConditionListed(name: string): Promise<boolean> {
    const entry = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SiteConditionListEntry(name))
    );
    return await entry.isVisible({ timeout: 8000 }).catch(() => false);
  }

  public async editSiteCondition(
    name: string,
    tb: TestBase
  ): Promise<{ hazard: string; control: string }> {
    const editBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.EditSiteConditionButton(name))
    );
    await expect(editBtn).toBeVisible();
    await editBtn.click();
    await this.page.waitForTimeout(3000);
    const addHazardBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AddHazardButton)
    );
    await expect(addHazardBtn).toBeVisible();
    await addHazardBtn.click();
    const removeHazardBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.RemoveHazardButton)
    );
    await expect(removeHazardBtn).toBeVisible();
    await removeHazardBtn.click();
    await addHazardBtn.click();
    const hazardDropdown = this.page.locator(
      this.getLocator(WorkPackagePageLocators.HazardDropdown)
    );
    await expect(hazardDropdown).toBeVisible();
    const arrowDownButton = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ArrowDownButton)
    );
    await expect(arrowDownButton).toBeVisible();
    await arrowDownButton.click();
    await this.page.waitForSelector(
      "//div[contains(@id, 'react-select') and contains(@id, 'listbox') and contains(@class, 'absolute')]"
    );
    const hazardOption = this.page.locator(
      this.getLocator(WorkPackagePageLocators.HazardOption)
    );
    await expect(hazardOption).toBeVisible();
    const hazardText = await hazardOption.textContent();
    await tb.logMessage(`Selected Hazard: ${hazardText}`);
    await hazardOption.click();
    const addControlBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.AddControlButton)
    );
    await expect(addControlBtn).toBeVisible();
    await addControlBtn.click();
    const controlSelector = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ControlSelector)
    );
    await expect(controlSelector).toBeVisible();
    const removeControlBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.RemoveControlButton)
    );
    await expect(removeControlBtn).toBeVisible();
    await removeControlBtn.click();
    await this.page.waitForTimeout(500);
    const controlSelectorAfterAdd = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ControlSelector)
    );
    await addControlBtn.click();
    await this.page.waitForTimeout(500);
    await expect(controlSelectorAfterAdd).toBeVisible();
    await controlSelectorAfterAdd.click();
    const controlOption = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ControlOption)
    );
    await expect(controlOption).toBeVisible();
    const controlText = await controlOption.textContent();
    await tb.logMessage(`Selected Control: ${controlText}`);
    await controlOption.click();
    const saveBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SaveSiteConditionButton)
    );
    await expect(saveBtn).toBeEnabled();
    await saveBtn.click();
    await expect(this.page.getByText("Site Condition saved")).toBeVisible({
      timeout: 8000,
    });
    return { hazard: hazardText || "", control: controlText || "" };
  }

  public async validateSiteConditionInSummary(
    name: string,
    hazard: string,
    control: string,
    tb: TestBase
  ) {
    const summaryBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SummaryViewButton)
    );
    await expect(summaryBtn).toBeVisible();
    await summaryBtn.click();
    await this.page.waitForTimeout(3000);
    const siteCondBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.ExpandSiteConditionButton)
    );
    await expect(siteCondBtn).toBeVisible();
    const ariaExpandedAttribute = await siteCondBtn.getAttribute(
      "aria-expanded"
    );
    if (ariaExpandedAttribute === "false") {
      await siteCondBtn.click();
    }
    const selectedSiteCond = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SiteConditionListEntry(name))
    );
    await expect(selectedSiteCond).toBeVisible();
    await selectedSiteCond.click();
    await expect(this.page.getByText(hazard ?? "")).toBeVisible();
    await expect(this.page.getByText(control ?? "")).toBeVisible();
    await tb.logSuccess("Hazard and control validated in summary view");
  }

  public async deleteSiteCondition(name: string) {
    const editBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.EditSiteConditionButton(name))
    );
    await expect(editBtn).toBeVisible();
    await editBtn.click();
    await this.page.waitForTimeout(3000);
    const removeBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.RemoveSiteConditionButton)
    );
    await expect(removeBtn).toBeVisible();
    await removeBtn.click();
    const confirmBtn = this.page.locator(
      this.getLocator(WorkPackagePageLocators.DeleteSiteConditionConfirm)
    );
    await expect(confirmBtn).toBeEnabled({ timeout: 8000 });
    await confirmBtn.click();
    await expect(this.page.getByText("Site Condition deleted")).toBeVisible({
      timeout: 8000,
    });
  }

  public async isSiteConditionNotListed(name: string): Promise<boolean> {
    const entry = this.page.locator(
      this.getLocator(WorkPackagePageLocators.SiteConditionListEntry(name))
    );
    return !(await entry.isVisible({ timeout: 8000 }).catch(() => false));
  }

  public async isWorkPackageNotListed(workOrder: string) {
    // Use the search input to search for the work order
    const searchInputLocator = this.getLocator(
      WorkPackagePageLocators.WorkPackageSearchInput
    );
    await this.page.waitForSelector(searchInputLocator, { timeout: 20000 });
    const searchInput = this.page.locator(searchInputLocator);
    await expect(searchInput).toBeVisible({ timeout: 20000 });
    const searchValue = workPageUniqueNameCode
      ? `${workOrder}${workPageUniqueNameCode}`
      : workOrder;
    await searchInput.fill(searchValue);
    await this.page.waitForTimeout(3000);
    await searchInput.press("Enter");
    const resultRow = this.page.locator(
      this.getLocator(WorkPackagePageLocators.WorkPackageResultRow)
    );
    await expect(resultRow).toBeHidden({ timeout: 10000 });
    const noProjectsMsg = this.page.locator(
      this.getLocator(WorkPackagePageLocators.NoProjectsMessage)
    );
    await expect(noProjectsMsg).toBeVisible({ timeout: 10000 });
  }
}
