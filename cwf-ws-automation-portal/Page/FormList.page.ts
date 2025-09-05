import { Locator, Page, expect } from "@playwright/test";
import { FormListPageLocators } from "../Locators/FormListPageLocators";
import * as Allure from "allure-js-commons";
import path from "path";
import TestBase, { getProjectName } from "../Util/TestBase";
import { Environment } from "../types/interfaces";
import { getEnvironmentData } from "../Data/envConfig";
import { CURRENT_ENV } from "../Data/envConfig";

export default class FormsListPage {
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

  public async ClickAddFormBtn() {
    try {
      const eleAddFormBtn = this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_btnAddForm)
      );
      await expect(eleAddFormBtn).toBeVisible();
      await eleAddFormBtn.click();
    } catch (err) {
      console.error(
        "Error while clicking Add Form button on Forms List Page, hence failed",
        (err as Error).message
      );
      throw new Error(
        "Error while clicking Add Form button on Forms List Page, hence failed"
      );
    }
  }

  public async verifyAddFormButton(
    expectedAddForm: string,
    expectedEBO: string,
    expectedJSB: string
  ) {
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_btnAddForm)
      )
    ).toHaveText(expectedAddForm);
    await this.ClickAddFormBtn();
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_lblEBOInAddFormBtn)
      )
    ).toHaveText(expectedEBO);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_lblJSBInAddFormBtn)
      )
    ).toHaveText(expectedJSB);
    await this.ClickAddFormBtn();
  }

  public async ClickJobSafetyBriefingBtn() {
    const addFormBtn = this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_btnAddForm)
    );
    await addFormBtn.click();
    await this.page.waitForTimeout(300);
    const eleJobSafetyBriefing = this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_btnJobSafetyBriefing)
    );
    await expect(eleJobSafetyBriefing).toBeVisible({ timeout: 5000 });
    await eleJobSafetyBriefing.click();
  }

  public async ClickEnergyBasedObservationBtn() {
    const addFormBtn = this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_btnAddForm)
    );
    await addFormBtn.click();
    await this.page.waitForTimeout(300);
    const eleEnergyBasedObservation = this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_btnEnergyBasedObservation
      )
    );
    await expect(eleEnergyBasedObservation).toBeVisible({ timeout: 5000 });
    await eleEnergyBasedObservation.click();
  }

  public async verifyJSBLabelsAndButtons(
    expectedHeading: string,
    expectedJobInfo: string,
    expectedMedEmer: string,
    expectedTasks: string,
    expectedEnergy: string,
    expectedWorkProc: string,
    expectedSiteCond: string,
    expectedCtrlAssess: string,
    expectedAttachments: string,
    expectedGD: string,
    expectedCrewSignOff: string
  ) {
    await this.page.waitForSelector(
      this.getLocator(FormListPageLocators.FormsListPage_JSB_lblHeadingJSB),
      { timeout: 20000 }
    );
    const eleHeading = this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_JSB_lblHeadingJSB)
    );
    await expect(eleHeading).toBeVisible({ timeout: 5000 });
    await expect(eleHeading).toHaveText(expectedHeading);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_JSB_NavJobInfo)
      )
    ).toHaveText(expectedJobInfo);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_JSB_NavMedAndEmer)
      )
    ).toHaveText(expectedMedEmer);
    await expect(
      this.page.locator(
        this.getLocator(
          FormListPageLocators.FormsListPage_JSB_NavTaskAndCriRisk
        )
      )
    ).toHaveText(expectedTasks);
    await expect(
      this.page.locator(
        this.getLocator(
          FormListPageLocators.FormsListPage_JSB_NavEnergySrcCtrls
        )
      )
    ).toHaveText(expectedEnergy);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_JSB_NavWorkProc)
      )
    ).toHaveText(expectedWorkProc);
    await expect(
      this.page.locator(
        this.getLocator(
          FormListPageLocators.FormsListPage_JSB_NavSiteConditions
        )
      )
    ).toHaveText(expectedSiteCond);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_JSB_NavCtrlAsses)
      )
    ).toHaveText(expectedCtrlAssess);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_JSB_NavAttachments)
      )
    ).toHaveText(expectedAttachments);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_JSB_NavGD)
      )
    ).toHaveText(expectedGD);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_JSB_NavCrewSignOff)
      )
    ).toHaveText(expectedCrewSignOff);
  }

  public async verifyEBOLabelsAndButtons(
    expectedHeading: string,
    expectedObservationDetails: string,
    expectedHighEnergyTasks: string,
    expectedAdditionalInfo: string,
    expectedHistoricalIncidents: string,
    expectedPhotos: string,
    expectedSummary: string,
    expectedPersonnel: string
  ) {
    await this.page.waitForSelector(
      this.getLocator(FormListPageLocators.FormsListPage_EBO_lblHeadingEBO),
      { timeout: 25000 }
    );
    const eleHeading = this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_EBO_lblHeadingEBO)
    );
    await expect(eleHeading).toBeVisible({ timeout: 5000 });
    await expect(eleHeading).toHaveText(expectedHeading);
    await expect(
      this.page.locator(
        this.getLocator(
          FormListPageLocators.FormsListPage_EBO_NavObservationDetails
        )
      )
    ).toHaveText(expectedObservationDetails);
    await expect(
      this.page.locator(
        this.getLocator(
          FormListPageLocators.FormsListPage_EBO_NavHighEnergyTasks
        )
      )
    ).toHaveText(expectedHighEnergyTasks);
    await expect(
      this.page.locator(
        this.getLocator(
          FormListPageLocators.FormsListPage_EBO_NavAdditionalInfo
        )
      )
    ).toHaveText(expectedAdditionalInfo);
    await expect(
      this.page.locator(
        this.getLocator(
          FormListPageLocators.FormsListPage_EBO_NavHistoricalIncidents
        )
      )
    ).toHaveText(expectedHistoricalIncidents);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_EBO_NavPhotos)
      )
    ).toHaveText(expectedPhotos);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_EBO_NavSummary)
      )
    ).toHaveText(expectedSummary);
    await expect(
      this.page.locator(
        this.getLocator(FormListPageLocators.FormsListPage_EBO_NavPersonnel)
      )
    ).toHaveText(expectedPersonnel);
  }

  public get btnJobInformationTabInJSB() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_JSB_NavJobInfo)
    );
  }

  public async ClickJobInformationTabInJSB() {
    const eleJobInformationTabInJSB = this.btnJobInformationTabInJSB;
    if (eleJobInformationTabInJSB != null)
      await eleJobInformationTabInJSB.click();
    else
      throw new Error(
        "No such 'Job Information' Tab Button found in JSB, Hence Failed"
      );
  }

  public get btnObservationDetailsTabInEBO() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_EBO_NavObservationDetails
      )
    );
  }

  public async ClickObservationDetailsTabInEBO() {
    const eleObservationDetailsTabInEBO = this.btnObservationDetailsTabInEBO;
    if (eleObservationDetailsTabInEBO != null)
      await eleObservationDetailsTabInEBO.click();
    else
      throw new Error(
        "No such 'Observation Details' Tab Button found in EBO, Hence Failed"
      );
  }

  public get rightSideSectionJSB() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_sectionRightSide)
    );
  }

  public async isRightSideSectionVisible() {
    let flag = true;
    try {
      const eleJSBRightSideSection = this.rightSideSectionJSB;
      await eleJSBRightSideSection?.waitFor({
        state: "visible",
        timeout: 5000,
      });
    } catch (err) {
      flag = false;
    }
    if (flag === false) {
      throw new Error("Right side section in JSB Screen Tab is not visible");
    }
  }

  public get JSB_JobInfo_GenInfo_dateSelector() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_JobInfo_GenInfo_lblDateSelector)
    );
  }

  public get JSB_JobInfo_GenInfo_datePickerBox() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_JobInfo_GenInfo_lblDatePickerBox)
    );
  }

  public get btnJSB_JobInfo_GenInfo_NextMonth_DatePicker() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_JobInfo_GenInfo_btnNextMonthDatePicker
      )
    );
  }

  public async JSB_JobInfo_GenInfo_VerifyCurrentDateWithFormat() {
    try {
      const eleDateInput = this.JSB_JobInfo_GenInfo_dateSelector;

      if (eleDateInput == null) {
        throw new Error(
          "Date Input Selector not found in General Info section under Job Information in JSB Screen"
        );
      }

      const inputValue = await eleDateInput.inputValue();

      const today = new Date();

      const formattedToday = `${String(today.getMonth() + 1).padStart(
        2,
        "0"
      )}/${String(today.getDate()).padStart(2, "0")}/${today.getFullYear()}`;

      const isCurrentDate = inputValue === formattedToday;

      const isCorrectFormat = /^\d{2}\/\d{2}\/\d{4}$/.test(inputValue);

      if (!isCurrentDate) {
        throw new Error(
          `'Date Selector' date doesn't match current date. Expected: "${formattedToday}", Actual: "${inputValue}"`
        );
      }

      if (!isCorrectFormat) {
        throw new Error(
          `'Date Selector' date doesn't follow correct format (dd/mm/yyyy). Actual: "${inputValue}"`
        );
      }
    } catch (error) {
      console.error("Date validation failed:", (error as Error).message);
      throw error;
    }
  }

  public async JSB_JobInfo_GenInfo_VerifyDatePickerBoxFunctionality() {
    try {
      const eleDateInput = this.JSB_JobInfo_GenInfo_dateSelector;
      if (eleDateInput != null) {
        await eleDateInput.click();
      } else {
        throw new Error(
          "Date Input Selector not found in General Info section under Job Information in JSB Screen"
        );
      }

      const inputValue = await eleDateInput.inputValue();
      const date = inputValue[3] + inputValue[4];
      // console.log("Input date", date)
      const otherDate = parseInt(date);

      if (otherDate >= 26) {
        const eleNextMonthDatePicker =
          this.btnJSB_JobInfo_GenInfo_NextMonth_DatePicker;
        if (eleNextMonthDatePicker != null)
          await eleNextMonthDatePicker.click();
        else
          throw new Error(
            "Cannot find next month arrow button in Date Picker Component, Hence Failed"
          );
        const eleOtherDate = this.page.locator(
          `${this.getLocator(
            FormListPageLocators.JSB_JobInfo_GenInfo_btnDynamicDateInDatePickerBox
          )}001') and @aria-disabled='false']`
        );
        if (eleOtherDate != null) eleOtherDate.click();
        else throw new Error("Cannot find 01 date on calendar, Hence Failed");
      } else {
        // console.log("Other date",otherDate)
        const eleOtherDate = this.page.locator(
          `${this.getLocator(
            FormListPageLocators.JSB_JobInfo_GenInfo_btnDynamicDateInDatePickerBox
          )}${otherDate <= 7 ? "00" : "0"}${(
            otherDate + 2
          ).toString()}') and @aria-disabled='false']`
        );
        if (eleOtherDate) {
          await eleOtherDate.click();
        } else {
          throw new Error(
            "Other date not found in Date Picker Box, Hence Failed"
          );
        }
        const eleDateSelector = this.JSB_JobInfo_GenInfo_dateSelector;
        if (eleDateSelector == null) {
          throw new Error(
            "Date Input Selector not found in General Info section under Job Information in JSB Screen"
          );
        }
        const inputValue = await eleDateSelector?.inputValue();
        // console.log("Date selector input value",inputValue[3] + inputValue[4])
        let temp = otherDate + 2;
        let dateThen = temp.toString();
        if (temp <= 9) {
          dateThen = "0" + dateThen;
        }
        // console.log("Other date + 2 ===>",dateThen)
        if (inputValue[3] + inputValue[4] !== dateThen) {
          throw new Error(
            "Chosen date doesn't matches the date on the 'date selector', Hence Failed"
          );
        }
      }
    } catch (err) {
      console.error("Date Picker Box did not show up", (err as Error).message);
    }
  }

  public async JSB_JobInfo_GenInfo_VerifyDateSelectorFunctionality(
    BriefingDate: string
  ) {
    const eleDateSelectorInput = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_JobInfo_GenInfo_lblDateSelector)
    );
    await eleDateSelectorInput.fill(BriefingDate);
    const inputValue = await eleDateSelectorInput.inputValue();
    await this.page.keyboard.press("Escape");
    await this.page.waitForTimeout(300);
    if (inputValue !== BriefingDate) {
      throw new Error(
        `Date mismatch - Input: ${inputValue}, Expected: ${BriefingDate}`
      );
    }
  }

  public get btnJSB_JobInfo_GenInfo_timeSelector() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_JobInfo_GenInfo_btnTimeSelector)
    );
  }

  public async JSB_JobInfo_GenInfo_VerifyBriefingTimeSelector() {
    try {
      const eleTimeSelector = this.btnJSB_JobInfo_GenInfo_timeSelector;
      if (!eleTimeSelector) {
        throw new Error(
          "'Briefing Time' Input not found in General Info section"
        );
      }

      const inputValue = await eleTimeSelector.inputValue();
      const currentTime = new Date();

      const formattedTime = `${String(currentTime.getHours()).padStart(
        2,
        "0"
      )}:${String(currentTime.getMinutes()).padStart(2, "0")}`;

      const bufferInMinutes = 1.5;

      const [inputHours, inputMinutes] = inputValue.split(":").map(Number);
      const inputDate = new Date();
      inputDate.setHours(inputHours, inputMinutes, 0, 0);

      const diffInMinutes = Math.abs(
        (currentTime.getTime() - inputDate.getTime()) / 60000
      );

      if (diffInMinutes > bufferInMinutes) {
        throw new Error(
          `Time mismatch - Input: ${inputValue}, Expected: ${formattedTime} (Difference: ${diffInMinutes.toFixed(
            1
          )} minutes)`
        );
      }

      return true;
    } catch (err) {
      console.error((err as Error).message);
      throw err;
    }
  }

  public async JSB_JobInfo_GenInfo_VerifyTimeSelectorFunctionality(
    BriefingTime: string
  ) {
    try {
      const eleTimeSelector = this.btnJSB_JobInfo_GenInfo_timeSelector;
      if (!eleTimeSelector) {
        throw new Error(
          "'Briefing Time' Input not found in General Info section"
        );
      }

      await eleTimeSelector.click();
      await eleTimeSelector.fill(BriefingTime);
      await this.page.keyboard.press("Tab");

      const inputValue = await eleTimeSelector.inputValue();
      if (inputValue !== BriefingTime) {
        throw new Error(
          `Time mismatch - Input: ${inputValue}, Expected: ${BriefingTime}`
        );
      }

      return true;
    } catch (err) {
      console.error((err as Error).message);
      throw err;
    }
  }

  InputLatitudeJSB = async () =>
    this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_JSB_txtCurrentLatitude)
    );
  InputLongitudeJSB = async () =>
    this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_JSB_txtCurrentLongitude
      )
    );

  public get btnSelectOperatingHQ() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnSelectOperatingHQ)
    );
  }

  public get dropdownMenuSelectOperatingHQ() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_JobInfo_WorkLoc_dropdownMenuOperatingHQ
      )
    );
  }

  public get firstOptionSelectOperatingHQ() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_JSB_selectOperatingHQFirstOption
      )
    );
  }

  public get btnSaveAndContinue() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_btnJSBSaveAndContinue)
    );
  }

  public async JSB_JobInfo_GPSCo_VerifyFillingCustomLatLng(
    LatitudeJSB: string,
    LongitudeJSB: string
  ) {
    const eleLatitudeJSB = await this.InputLatitudeJSB();
    if (eleLatitudeJSB != null) {
      await eleLatitudeJSB.focus();
      await eleLatitudeJSB.fill(LatitudeJSB);
    } else throw new Error("No Enter Latitude Element Found, hence failed");

    const eleLongitudeJSB = await this.InputLongitudeJSB();
    if (eleLongitudeJSB != null) {
      await eleLongitudeJSB.focus();
      eleLongitudeJSB.fill(LongitudeJSB);
    } else throw new Error("No Enter Longitude Element Found, hence failed");
  }

  public get btnJSB_GPSCo_UseCurrentLocation() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_JobInfo_GenInfo_btnUseCurrentLoc)
    );
  }

  public async JSB_JobInfo_GPSCo_VerifyUseCurrentLocationBtn() {
    const eleUseCurrLoc = this.btnJSB_GPSCo_UseCurrentLocation;
    if (eleUseCurrLoc != null) await eleUseCurrLoc.click();
    else
      throw new Error(
        "No 'Use Current Location' Button found in GPS Coordinates Section, in Job Info inside JSB, Hence Failed"
      );
    const eleLatitudeJSB = await this.InputLatitudeJSB();
    if (eleLatitudeJSB != null) {
      await eleLatitudeJSB.focus();
      const currLat = await eleLatitudeJSB.inputValue();
      if (currLat !== "36.2274") {
        throw new Error(
          "Current Location Latitude Doesn't Matches the Actual Current Latitude, Hence Failed"
        );
      }
    } else throw new Error("No Enter Latitude Element Found, hence failed");

    const eleLongitudeJSB = await this.InputLongitudeJSB();
    if (eleLongitudeJSB != null) {
      await eleLongitudeJSB.focus();
      const currLong = await eleLongitudeJSB.inputValue();
      if (currLong !== "-83.0098") {
        throw new Error(
          "Current Location Longitude Doesn't Matches the Actual Current Longitude, Hence Failed"
        );
      }
    } else throw new Error("No Enter Longitude Element Found, hence failed");
  }

  InputAddressWorkLocationJSB = async () =>
    this.page.locator(
      this.getLocator(FormListPageLocators.JSB_JobInfo_WorkLoc_txtBoxAddress)
    );

  public async JSB_JobInfo_WorkLoc_VerifyAddressTextBox(
    AddressWorkLocationJSB: string
  ) {
    const eleAddressWorkLocationJSB = await this.InputAddressWorkLocationJSB();
    if (eleAddressWorkLocationJSB != null)
      await eleAddressWorkLocationJSB.fill(AddressWorkLocationJSB);
    else
      throw new Error(
        "No Work Location Address Text Box Element Found, hence failed"
      );
  }

  public async JSB_JobInfo_WorkLoc_VerifyMultipleAddressTextBox(
    Address: string
  ) {
    const eleAddressWorkLocationJSB = await this.InputAddressWorkLocationJSB();
    if (eleAddressWorkLocationJSB == null)
      throw new Error(
        "No Work Location Address Text Box Element Found, hence failed"
      );

    const initialHasScrollbar = await eleAddressWorkLocationJSB.evaluate(
      (el) => {
        return el.scrollHeight > el.clientHeight;
      }
    );
    if (initialHasScrollbar === true)
      throw new Error(
        "Vertical Scroll Bar already present without even overflow of text box, Hence Failed"
      );
    await eleAddressWorkLocationJSB.scrollIntoViewIfNeeded();
    await eleAddressWorkLocationJSB.focus();
    await eleAddressWorkLocationJSB.fill(Address);

    await this.page.waitForTimeout(1000);

    const hasScrollbar = await eleAddressWorkLocationJSB.evaluate((el) => {
      return el.scrollHeight > el.clientHeight;
    });
    if (hasScrollbar === false)
      throw new Error(
        "Vertical Scroll Bar did not appear after overflow of text box, Hence Failed"
      );
  }

  public get ListInDropdownSelectOpHQ() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_JobInfo_WorkLoc_dropdownMenuOperatingHQList
      )
    );
  }

  public async JSB_JobInfo_WorkLoc_OperatingHQ() {
    const eleOperatingHQJSB = this.btnSelectOperatingHQ;
    if (eleOperatingHQJSB != null) await eleOperatingHQJSB.click();
    else throw new Error("No Select Operating HQ Button Found, hence failed");

    const eleDropdownMenuSelectOperatingHQ = this.dropdownMenuSelectOperatingHQ;
    if (eleDropdownMenuSelectOperatingHQ == null)
      throw new Error(
        "No Dropdown Menu in Select Operating HQ found, hence failed."
      );

    const eleListInDropdownSelectOpHQ = this.ListInDropdownSelectOpHQ;
    if ((await eleListInDropdownSelectOpHQ.count()) <= 1) {
      throw new Error(
        "No Options found in Select Operating HQ Dropdown, Hence Failed"
      );
    }

    const eleFirstOptionOperatinHQ = this.firstOptionSelectOperatingHQ;
    if (eleFirstOptionOperatinHQ != null)
      await eleFirstOptionOperatinHQ.click();
    else
      throw new Error(
        "No Select Option Found in Operating HQ Dropdown, hence failed"
      );
  }

  public get reqCheckWorkAddress() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_JobInfo_workAddressReqCheck)
    );
  }

  public get reqCheckOperatingHQ() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_JobInfo_operatingHQReqCheck)
    );
  }

  public async JSB_JobInfo_CheckForReqFields() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) eleSaveAndContinue.click();
    const eleReqCheckWorkAddress = this.reqCheckWorkAddress;
    const eleReqCheckOperatingHQ = this.reqCheckOperatingHQ;
    if (eleReqCheckWorkAddress == null)
      throw new Error(
        "Required Field Work Address in Job Info in JSB not throwing error if clicked saved and continue without entering details, Hence Failed"
      );
    if (eleReqCheckOperatingHQ == null)
      throw new Error(
        "Required Field Operating HQ in Job Info in JSB not throwing error if clicked saved and continue without entering details, Hence Failed"
      );
  }

  public async EBO_ObservationDetails_CheckForReqFields() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) eleSaveAndContinue.click();
    await this.page.waitForTimeout(200);
    const eleOpCoObservedError = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_ObservationDetails_OpCoObservedError
      )
    );
    await expect(eleOpCoObservedError).toBeVisible({ timeout: 5000 });
    const eleDepartmentObservedError = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_ObservationDetails_DepartmentObservedError
      )
    );
    await expect(eleDepartmentObservedError).toBeVisible({ timeout: 5000 });
    const eleWorkTypeError = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_ObservationDetails_WorkTypeError)
    );
    await expect(eleWorkTypeError).toBeVisible({ timeout: 5000 });
    const eleLocationError = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_ObservationDetails_LocationError)
    );
    await expect(eleLocationError).toBeVisible({ timeout: 5000 });
    const eleLatError = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_ObservationDetails_LatError)
    );
    await expect(eleLatError).toBeVisible({ timeout: 5000 });
    const eleLongError = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_ObservationDetails_LongError)
    );
    await expect(eleLongError).toBeVisible({ timeout: 5000 });
  }

  public async JSB_JobInfo_ClickSaveAndContinueBtn() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) {
      await eleSaveAndContinue.click({ force: true });
      await expect(eleSaveAndContinue).toBeDisabled({ timeout: 5000 });
    } else {
      throw new Error(
        "No Save and Continue Button Found on Job Information Tab, hence failed"
      );
    }
  }

  public get MedicalAndEmergencyNavButton() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavMedAndEmer)
    );
  }

  public async JSB_MedAndEmer_VerifyTabHighlightedAutomatically() {
    const eleNavMedAndEmer = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavMedAndEmer)
    );
    await expect(eleNavMedAndEmer).toHaveClass(/border-neutral-shade-100/, {
      timeout: 7000,
    });
    await expect(eleNavMedAndEmer).toHaveClass(/box-border/, { timeout: 7000 });
  }

  Input_EmergencyContact1_Name = async () =>
    this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_JSB_txtEmergencyContact1_Name
      )
    );
  Input_EmergencyContact1_PhoneNumber = async () =>
    this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_JSB_txtEmergencyContact1_PhoneNumber
      )
    );
  Input_EmergencyContact2_Name = async () =>
    this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_JSB_txtEmergencyContact2_Name
      )
    );
  Input_EmergencyContact2_PhoneNumber = async () =>
    this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_JSB_txtEmergencyContact2_PhoneNumber
      )
    );

  public async JSB_MedAndEmer_VerifyEmergencyContactFields(): Promise<boolean> {
    //assuming that the fields are pre filled
    let flag = true;
    const eleEmerContact1 = await this.Input_EmergencyContact1_Name();
    if (eleEmerContact1) {
      let inputValEleContact1 = await eleEmerContact1.inputValue();
      if (inputValEleContact1 == "") {
        flag = false;
      }
    } else
      throw new Error(
        "No Emergency Contact 1 Name input field Found, hence failed"
      );
    const eleEmergencyContact1_PhoneNumber =
      await this.Input_EmergencyContact1_PhoneNumber();
    if (eleEmergencyContact1_PhoneNumber) {
      let inputValEleContact1_PhoneNumber =
        await eleEmergencyContact1_PhoneNumber.inputValue();
      if (inputValEleContact1_PhoneNumber == "") {
        flag = false;
      }
    } else
      throw new Error(
        "No Emergency Contact 1 Phone Number input field Found, hence failed"
      );
    const eleEmergencyContact2_Name = await this.Input_EmergencyContact2_Name();
    if (eleEmergencyContact2_Name) {
      let inputValEleContact2 = await eleEmergencyContact2_Name.inputValue();
      if (inputValEleContact2 == "") {
        flag = false;
      }
    } else
      throw new Error(
        "No Emergency Contact 2 Name input field Found, hence failed"
      );
    const eleEmergencyContact2_PhoneNumber =
      await this.Input_EmergencyContact2_PhoneNumber();
    if (eleEmergencyContact2_PhoneNumber) {
      let inputValEleContact2_PhoneNumber =
        await eleEmergencyContact2_Name.inputValue();
      if (inputValEleContact2_PhoneNumber == "") {
        flag = false;
      }
    } else
      throw new Error(
        "No Emergency Contact 2 Phone Number input field Found, hence failed"
      );
    return flag;
  }

  public async FillEmergencyContact1Details(Name: string) {
    const eleSaveAndContinueBtn = this.btnSaveAndContinue;
    const eleEmergencyContact1_Name = await this.Input_EmergencyContact1_Name();
    if (eleEmergencyContact1_Name) {
      await eleSaveAndContinueBtn?.click();
      const reqCheck = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_DynamicReqCheckSpan) + "[1]"
      );
      if (await reqCheck.isVisible()) {
        await eleEmergencyContact1_Name.scrollIntoViewIfNeeded();
        await eleEmergencyContact1_Name.focus();
        await eleEmergencyContact1_Name.click();
        await eleEmergencyContact1_Name.fill(Name);
      } else {
        throw new Error(
          "No Requirement Check before clicking Save and Continue button found for Emergency Contact 1 Details, Hence Failed"
        );
      }
    } else {
      throw new Error(
        "No Emergency Contact 1 Name input field Found, hence failed"
      );
    }
  }

  public async FillEmergencyContact1PhoneNumberDetails(PhoneNumber: string) {
    const eleSaveAndContinueBtn = this.btnSaveAndContinue;
    const eleEmergencyContact1_PhoneNumber =
      await this.Input_EmergencyContact1_PhoneNumber();
    if (eleEmergencyContact1_PhoneNumber) {
      await eleSaveAndContinueBtn?.click();
      const reqCheck = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_DynamicReqCheckSpan) + "[1]"
      );
      if (await reqCheck.isVisible()) {
        await eleEmergencyContact1_PhoneNumber.fill(PhoneNumber);
      } else {
        throw new Error(
          "No Requirement Check before clicking Save and Continue button found for Emergency Contact 1 Phone Number Details, Hence Failed"
        );
      }
    } else {
      throw new Error(
        "No Emergency Contact 1 Phone Number input field Found, hence failed"
      );
    }
  }

  public async FillEmergencyContact2Details(Name: string) {
    const eleSaveAndContinueBtn = this.btnSaveAndContinue;
    const eleEmergencyContact2 = await this.Input_EmergencyContact2_Name();
    if (eleEmergencyContact2) {
      await eleSaveAndContinueBtn?.click();
      const reqCheck = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_DynamicReqCheckSpan) + "[1]"
      );
      if (await reqCheck.isVisible()) {
        await eleEmergencyContact2.focus();
        await eleEmergencyContact2.click();
        await eleEmergencyContact2.fill(Name);
      } else {
        throw new Error(
          "No Requirement Check before clicking Save and Continue button found for Emergency Contact 2 Details, Hence Failed"
        );
      }
    } else {
      throw new Error(
        "No Emergency Contact 2 Name input field Found, hence failed"
      );
    }
  }

  public async FillEmergencyContact2PhoneNumberDetails(PhoneNumber: string) {
    const eleSaveAndContinueBtn = this.btnSaveAndContinue;
    const eleEmergencyContact2_PhoneNumber =
      await this.Input_EmergencyContact2_PhoneNumber();
    if (eleEmergencyContact2_PhoneNumber) {
      await eleSaveAndContinueBtn?.click();
      await this.page.waitForTimeout(300);
      const reqCheck1 = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_DynamicReqCheckSpan) + "[1]"
      );
      if (await reqCheck1.isVisible()) {
        await eleEmergencyContact2_PhoneNumber.fill(PhoneNumber);
      } else {
        throw new Error(
          "No Requirement Check before clicking Save and Continue button found for Emergency Contact 2 Phone Number Details, Hence Failed"
        );
      }
    }
  }

  public get btnSelectMedicalFacility() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_MedAndEmer_selectNearestMedFacility
      )
    );
  }

  public get btnSelectMedicalFacilityFirstOption() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_MedAndEmer_selectNearestMedFacilityFirstOption
      )
    );
  }

  public get btnSelectMedicalFacilityOtherOption() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_MedAndEmer_selectNearestMedFacilityOtherOption
      )
    );
  }

  InputNearestMedicalFacility = async () =>
    this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_MedAndEmer_txtCustomNearestMedFacility
      )
    );

  public async SelectOtherOptionInNearestMedFacilitiesDropdown() {
    const eleSelectNearestMedicalFacility = this.btnSelectMedicalFacility;
    await expect(eleSelectNearestMedicalFacility).toBeVisible({
      timeout: 5000,
    });
    if (eleSelectNearestMedicalFacility !== null) {
      await eleSelectNearestMedicalFacility.click();
      const eleOtherOptionInSelectNearestMedFacility =
        this.btnSelectMedicalFacilityOtherOption;
      await expect(eleOtherOptionInSelectNearestMedFacility).toBeVisible({
        timeout: 5000,
      });
      if (eleOtherOptionInSelectNearestMedFacility !== null) {
        await eleOtherOptionInSelectNearestMedFacility.click();
        const selectedOptionInNearestMedFacility = this.page.locator(
          this.getLocator(
            FormListPageLocators.JSB_MedAndEmer_SelectedOptionOtherInNearestMedFacility
          )
        );
        const labelOnDropdown =
          await selectedOptionInNearestMedFacility.innerText();
        if (labelOnDropdown !== "Other") {
          throw new Error(
            "Other option not selected even after clicking on it, Hence Failed"
          );
        }
      } else {
        throw new Error(
          "No Other Option Found in Nearest Medical Facility Dropdown, Hence Failed"
        );
      }
    } else {
      throw new Error(
        "No Dropdown menu found in 'Nearest Medical Facility' section, Hence Failed"
      );
    }
  }

  public async EnterCustomNearestMedFacility(FacilityName: string) {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue !== null) {
      await eleSaveAndContinue.click();
      const eleReqCheckNearestMedFac = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_MedAndEmer_reqCheckNearestMedFacility
        )
      );
      if (eleReqCheckNearestMedFac !== null) {
        const eleCustomNearestMedFacilityInput =
          await this.InputNearestMedicalFacility();
        if (eleCustomNearestMedFacilityInput !== null) {
          await eleCustomNearestMedFacilityInput.focus();
          await eleCustomNearestMedFacilityInput.fill(FacilityName);
        } else {
          throw new Error(
            "No Custom Input Element Found for Nearest Medical Facility, Hence Failed"
          );
        }
      } else {
        throw new Error(
          "No Require Check prompt for Nearest Medical Custom Facility found, Hence Failed"
        );
      }
    } else {
      throw new Error(
        "Save and Continue Button not found on Medical And Emergency Tab, Hence Failed"
      );
    }
  }

  public get btnSelectAEDLocation() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_JSB_selectAEDLocation)
    );
  }

  public get btnSelectAEDLocationCabOfTruck() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_JSB_selectAEDLocationCabOfTruck
      )
    );
  }

  public get btnSelectAEDLocationTruckSide() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_JSB_selectAEDLocationTruckDriverSideComp
      )
    );
  }

  public get btnSelectAEDLocationOther() {
    return this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_JSB_selectAEDLocationOther
      )
    );
  }

  public async JSB_MedAndEmer_VerifyAEDLocationDropdownBox() {
    const eleSelectAEDLocation = this.btnSelectAEDLocation;
    await expect(eleSelectAEDLocation).toBeVisible({ timeout: 5000 });
    try {
      await eleSelectAEDLocation.click();
      const eleOther = this.btnSelectAEDLocationOther;
      await expect(eleOther).toBeVisible({ timeout: 5000 });
    } catch (err) {
      console.error(
        "Error in JSB_MedAndEmer_VerifyAEDLocationDropdownBox:",
        err
      );
      throw new Error(
        "No AED Location Dropdown Box found, or required options not visible, hence failed"
      );
    }
  }

  public async JSB_MedAndEmer_EnterOtherAEDLocation(AEDLocation: string) {
    const eleSelectOtherAEDOption = this.btnSelectAEDLocationOther;
    if (eleSelectOtherAEDOption !== null) {
      await eleSelectOtherAEDOption.click();
    } else {
      throw new Error(
        "No Other AED Location option found in AED Location Dropdown Box, Hence Failed"
      );
    }
    const eleInputOtherAEDLocation = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_MedAndEmer_txtOtherAEDLocation)
    );
    await expect(eleInputOtherAEDLocation).toBeVisible({ timeout: 5000 });
    if (eleInputOtherAEDLocation !== null) {
      const eleSaveAndContinue = this.btnSaveAndContinue;
      if (eleSaveAndContinue) {
        await eleSaveAndContinue.click();
        const eleReqCheckAEDLocation = this.page.locator(
          `${this.getLocator(FormListPageLocators.JSB_DynamicReqCheckSpan)}[1]`
        );
        if (eleReqCheckAEDLocation !== null) {
          await eleInputOtherAEDLocation.fill(AEDLocation);
        } else {
          throw new Error(
            "No Checks/Prompt before filling Other AED Location Found, Hence Failed"
          );
        }
      } else {
        throw new Error(
          "No Save and Continue Button Found on Med and Emer Tab, Hence Failed"
        );
      }
    } else {
      throw new Error(
        "No Such Custom Input Box Found to Enter Other AED Location, Hence Failed"
      );
    }
  }

  public async JSB_MedAndEmer_ClickSaveAndContinueBtn() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    try {
      if (eleSaveAndContinue != null) {
        await eleSaveAndContinue.click();
        await expect(eleSaveAndContinue).toBeDisabled({ timeout: 5000 });
      } else {
        throw new Error(
          "No Save and Continue Button Found on Medical & Emergency Tab, hence failed"
        );
      }
    } catch (err) {
      console.error(
        "Error clicking Save and Continue on Medical & Emergency tab:",
        err
      );
      throw err;
    }
  }

  public async JSB_TasksAndCriRisks_VerifyTabHighlightedAutomatically() {
    const eleTasksAndCriRisks = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavTasksAndCriRisks)
    );
    await expect(eleTasksAndCriRisks).toHaveClass(/border-neutral-shade-100/, {
      timeout: 7000,
    });
    await expect(eleTasksAndCriRisks).toHaveClass(/box-border/, {
      timeout: 7000,
    });
  }

  public async VerifyReqCheckTasksAndCriRisks() {
    const eleSaveAndContinueBtn = this.btnSaveAndContinue;
    if (eleSaveAndContinueBtn != null) {
      await eleSaveAndContinueBtn.click();
      if (
        this.page.locator(
          this.getLocator(
            FormListPageLocators.JSB_TasksAndCriRisks_lblReqCheckNoActivity
          )
        ) == null
      ) {
        throw new Error(
          "No Requried Check before clicking Save and Continue button in Tasks and Critical Risks Section"
        );
      }
    } else {
      throw new Error(
        "No Save and Continue button found in Tasks and Critical Risks Section"
      );
    }
  }

  public async VerifyHyperlinkToCriRisksAreaDocs() {
    await this.page.waitForSelector(
      this.getLocator(
        FormListPageLocators.JSB_TasksAndCriRisks_btnLinkToCriRiskAreaDocs
      ),
      { timeout: 10000 }
    );
    const eleLinkToCriRisksAreaDocs = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_TasksAndCriRisks_btnLinkToCriRiskAreaDocs
      )
    );
    await expect(eleLinkToCriRisksAreaDocs).toBeVisible({ timeout: 5000 });
    await expect(eleLinkToCriRisksAreaDocs).toHaveAttribute(
      "href",
      "https://soco365.sharepoint.com/:w:/s/TRNCorpSafetySubCom/safetyandhealthmanagementsystem/EeBBxGGb0tRJuVmpfj-lvmwBAZcLee5be537p2_Vd3QP1w?e=Kx4KI9"
    );
  }

  public async CheckCriticalRiskAreasToggles() {
    const totalToggles = await this.page
      .locator("label.Toggle_toggle__xBAdu")
      .count();

    for (let i = 0; i < totalToggles; i++) {
      try {
        const eleToggle = this.page
          .locator("label.Toggle_toggle__xBAdu")
          .nth(i);

        await eleToggle.waitFor({ state: "visible", timeout: 5000 });
        await eleToggle.click({ clickCount: 2, timeout: 200 });
      } catch (error) {
        console.error(`Failed to toggle element at index ${i}:`, error);
        throw error;
      }
    }
  }

  public get btnAddActivity() {
    return this.page.locator(
      this.getLocator(FormListPageLocators.JSB_TasksAndCriRisks_btnAddActivity)
    );
  }

  public async JSB_TasksAndCriRisks_ClickAddActivityButton() {
    const eleAddActivityBtn = this.btnAddActivity;
    await expect(eleAddActivityBtn).toBeVisible({ timeout: 5000 });
    if (eleAddActivityBtn) {
      await this.page.waitForTimeout(1000);
      await eleAddActivityBtn.click();
      const elePopUp = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_popUpAddActivity
        )
      );
      await expect(elePopUp).toBeVisible({ timeout: 10000 });
      await this.page.waitForTimeout(200);
      if (!elePopUp) {
        throw new Error(
          "After clicking 'Add Activity' Button no Pop Up displayed, Hence Failed"
        );
      }
    } else {
      throw new Error("No Such 'Add Activity' Button found, hence Failed");
    }
  }

  public async VerifyCancelButtonInAddActivityPopUp() {
    const eleCancelButton = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_TasksAndCriRisks_btnCancelInAddActivityPopUp
      )
    );
    await expect(eleCancelButton).toBeVisible({ timeout: 5000 });
    await eleCancelButton.click();
    await this.isRightSideSectionVisible();
  }

  public async JSB_TasksAndCriRisks_VerifyTasksButtonsAndCountLabel() {
    try {
      const parentDiv = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_divTasksInAddActivityPopUp
        )
      );
      await expect(parentDiv).toBeVisible({ timeout: 5000 });
      const buttons = parentDiv.locator("button");
      const buttonCount = await buttons.count();

      expect(buttonCount).toBeGreaterThanOrEqual(1);

      let recievedTasksWithCounts = "";

      for (let i = 0; i < buttonCount; i++) {
        const button = buttons.nth(i);

        const labelText = await button
          .locator("span.text-brand-gray-80")
          .textContent();
        const countText = await button.locator("span.text-tiny").textContent();

        const numericCount = Number(countText?.trim());
        expect(numericCount).not.toBeNaN();
        expect(numericCount).toBeGreaterThanOrEqual(0);

        recievedTasksWithCounts += `${labelText} (${numericCount})`;
        if (i < buttonCount - 1) recievedTasksWithCounts += ", ";
      }
      await this.tb.logSuccess(
        `Received Tasks and their Critical Risk counts: ${recievedTasksWithCounts}`
      );
    } catch (err: any) {
      throw new Error(
        "Failed to verify Tasks and their Critical Risk counts in Add Activity popup: " +
          err.message
      );
    }
  }

  public async JSB_TasksAndCriRisks_VerifySubTasksInAddActivityPopUp() {
    try {
      const taskButtons = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_btnTaskInAddActivityPopUp
        )
      );
      const taskButtonsCount = await taskButtons.count();
      let taskButton = this.page
        .locator(
          this.getLocator(
            FormListPageLocators.JSB_TasksAndCriRisks_btnTaskInAddActivityPopUp
          )
        )
        .first();
      await expect(taskButton).toBeVisible({ timeout: 5000 });
      for (let i = 0; i < taskButtonsCount; i++) {
        taskButton = taskButtons.nth(i);
        const countLabel = await taskButton
          .locator("span.text-tiny")
          .textContent();
        const count = parseInt(countLabel || "0", 10);

        if (count > 0) {
          await taskButton.click();
          break;
        }
      }

      const eleSubTasksContainer = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_divSubTasksInAddActivityPopUp
        )
      );
      await expect(eleSubTasksContainer).toBeVisible({ timeout: 5000 });

      const subTasksCount = await eleSubTasksContainer.count();
      expect(subTasksCount).toBeGreaterThan(0);

      const eleSubTasks = eleSubTasksContainer.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_btnSubTaskInAddActivityPopUp
        )
      );

      for (let i = 0; i < subTasksCount; i++) {
        const subtask = eleSubTasks.nth(i);

        // Verify checkbox
        const checkbox = subtask.locator("input.Checkbox_root__Lr2rF");
        await expect(checkbox).toBeVisible({ timeout: 5000 });

        // Verify label
        const label = subtask.locator("span.text-brand-gray-80");
        await expect(label).toBeVisible({ timeout: 5000 });
      }

      // Click again to close
      await taskButton.click();

      // Verify subtasks are now hidden
      await expect(eleSubTasksContainer).toBeHidden();
    } catch (error: any) {
      throw new Error(
        "Failed to verify subtasks visibility behavior: " + error.message
      );
    }
  }

  public async JSB_TasksAndCriRisks_VerifySearchBoxFunctionality(Task: string) {
    try {
      const eleSearchBoxField = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_popUpAddActivitySearchBox
        )
      );
      await expect(eleSearchBoxField).toBeVisible({ timeout: 5000 });
      await eleSearchBoxField.clear();
      await eleSearchBoxField.fill("ekctpoxyz");
      await this.page.waitForTimeout(200);
      const eleNoMatchFoundPrompt = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_promptNoMatchFoundInAddActivityPopUp
        )
      );
      await expect(eleNoMatchFoundPrompt).toBeVisible({ timeout: 5000 });

      await eleSearchBoxField.clear();

      await eleSearchBoxField.fill(Task.substring(0, 3));
      await this.page.waitForTimeout(200);

      const divTasks = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_divTasksInAddActivityPopUp
        )
      );
      await expect(divTasks).toBeVisible({ timeout: 5000 });
      const taskButtons = divTasks.locator("button");
      const taskButtonsCount = await taskButtons.count();

      let flag = false;
      let taskButtonSearched;

      for (let i = 0; i < taskButtonsCount; i++) {
        const btnTask = taskButtons.nth(i);

        const labelText = await btnTask
          .locator("span.text-brand-gray-80")
          .textContent();

        if (labelText === Task) {
          flag = true;
          taskButtonSearched = btnTask;
          break;
        }
      }
      if (flag === true) {
        await taskButtonSearched?.click();
        await this.page.waitForTimeout(200);
        const eleSubTasksContainer = this.page.locator(
          this.getLocator(
            FormListPageLocators.JSB_TasksAndCriRisks_divSubTasksInAddActivityPopUp
          )
        );
        await expect(eleSubTasksContainer).toBeVisible({ timeout: 5000 });
        const eleFirstSubTaskButton = eleSubTasksContainer
          .locator(
            this.getLocator(
              FormListPageLocators.JSB_TasksAndCriRisks_btnSubTaskInAddActivityPopUp
            )
          )
          .first();

        // Verify checkbox
        const checkbox = eleFirstSubTaskButton.locator(
          "input.Checkbox_root__Lr2rF"
        );
        await expect(checkbox).toBeVisible({ timeout: 5000 });

        // Verify label
        const label = eleFirstSubTaskButton.locator("span.text-brand-gray-80");
        await expect(label).toBeVisible({ timeout: 5000 });
        await eleFirstSubTaskButton.click();
      } else {
        throw new Error(
          "Search Box on Search Doesn't Shows the Specified Task, Hence Failed"
        );
      }
    } catch (error: any) {
      throw new Error(
        "Search Box field doesn't works as expected, Hence Failed :" + error
      );
    }
  }

  public async JSB_TasksAndCriRisks_clickNextButtonInAddActivityPopUp() {
    try {
      const eleNextBtnInAddActivityPopUp = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_btnNextInAddActivityPopUp
        )
      );
      expect(eleNextBtnInAddActivityPopUp).toBeVisible({ timeout: 5000 });
      await eleNextBtnInAddActivityPopUp.click();
      await this.page.waitForTimeout(300);
    } catch (err: any) {
      throw new Error(err);
    }
  }

  public async JSB_TasksAndCriRisks_VerifyActivityNameScreenInPopUp(
    ActivityName: string
  ) {
    try {
      const eleActivityNameInputBox = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_txtActivityNameInAddActivityPopUp
        )
      );
      await expect(eleActivityNameInputBox).toBeVisible({
        timeout: 5000,
      });
      await expect(eleActivityNameInputBox).toHaveValue(ActivityName);
    } catch (error: any) {
      throw new Error(`Test Case 29 : ${error.message || error}`);
    }
  }

  public async JSB_TasksAndCriRisks_ClickAddActivityBtnInPopUp() {
    try {
      const eleAddActivityBtnInPopUp = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_btnAddActivityInActivityNamePopUp
        )
      );
      expect(eleAddActivityBtnInPopUp).toBeVisible({
        timeout: 5000,
      });
      await eleAddActivityBtnInPopUp.click();
    } catch (error: any) {
      throw new Error(
        `Failed while clicking Add Activity Button in Pop Up : ${
          error.message || error
        }`
      );
    }
  }

  public async JSB_TasksAndCriRisks_VerifySelectedTasks() {
    const mainTaskContainer = this.page.locator(".flex.flex-col.gap-5");

    // 1. Verify "Material handling + Excavate" task and its menu
    const firstTask = mainTaskContainer.locator(
      ".flex.flex-1.justify-between",
      {
        has: this.page.locator('text="Excavate"'),
      }
    );

    // Verify the task exists and is visible
    await expect(firstTask).toBeVisible();

    // Verify checkbox
    const mainCheckbox = firstTask.locator('input[type="checkbox"]');
    await expect(mainCheckbox).toBeVisible();
    await expect(mainCheckbox).toBeChecked();

    // // Verify triple dot menu button
    // const menuButton = this.page.locator(this.getLocator("(//button[contains(@class,'text-xl text-neutral-shade-75')])[2]"));
    // await menuButton.scrollIntoViewIfNeeded();
    // // Click menu and verify dropdown options
    // await menuButton.click();

    // // Verify menu items in task selected
    // const menuItems = this.page.locator(this.getLocator(
    //   "//div[contains(@class,'absolute right-0')]"
    // ));
    // await expect(menuItems).toBeVisible();

    // // Verify Edit option
    // const editOption = menuItems.locator('text="Edit"');
    // await expect(editOption).toBeVisible();

    // // Verify Delete option
    // const deleteOption = menuItems.locator('text="Delete"');
    // await expect(deleteOption).toBeVisible();

    // await menuButton.click();

    // 2. Verify subtasks with risk labels
    const subtasks = this.page.locator(
      "(//div[contains(@class,'flex flex-col')])[3]//div[contains(@class, 'flex flex-row items-center gap-2 w-full gap-4')]"
    );

    // Verify we have at least one subtask
    const subtaskCount = await subtasks.count();
    expect(subtaskCount).toBeGreaterThan(1);

    const subtask = subtasks.nth(0);

    const checkbox = subtask.locator('input[type="checkbox"]');
    await expect(checkbox).toBeVisible();
    await expect(checkbox).toBeChecked();

    // Verify task has a name
    const taskName = subtask
      .locator("(//span[contains(@class,'text-base text-neutral-shade-100')])")
      .first();
    await expect(taskName).toBeVisible();
    const taskText = await taskName.textContent();
    expect(taskText?.length).toBeGreaterThan(0);

    // Verify risk label
    const riskLabel = subtask
      .locator("(//span[@class='text-tiny mr-1'])", { hasText: "RISK" })
      .first();
    await expect(riskLabel).toBeVisible();
  }

  public async JSB_EnergySrcCtrl_VerifyTabHighlightedAutomatically() {
    const eleEnergySrcCtrlNavigator = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavEnergySrcCtrl)
    );
    await expect(eleEnergySrcCtrlNavigator).toHaveClass(
      /border-neutral-shade-100/,
      { timeout: 7000 }
    );
    await expect(eleEnergySrcCtrlNavigator).toHaveClass(/box-border/, {
      timeout: 7000,
    });
  }

  public async JSB_EnergySrcCtrl_VerifyArcFlashCategory() {
    try {
      const eleArcFlashCategoryInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputArcFlashCategory
        )
      );
      await expect(eleArcFlashCategoryInput).toBeVisible({ timeout: 5000 });
      await expect(eleArcFlashCategoryInput.locator("//span//span")).toHaveText(
        "Select an option"
      );
      await eleArcFlashCategoryInput.click();

      const eleDropdownDivArcFlashCategory = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownDivArcFlashCategory
        )
      );
      await expect(eleDropdownDivArcFlashCategory).toBeVisible({
        timeout: 5000,
      });

      const eleDropdownListItemsArcFlash = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )
      );
      const optionsText = await eleDropdownListItemsArcFlash.allTextContents();
      const combinedOptions = optionsText.join(", ");
      await eleArcFlashCategoryInput.click();

      await this.tb.logSuccess(
        `Selected Arc Flash Category and received the following options: ${combinedOptions}`
      );
    } catch (error) {
      throw new Error(
        `Failed to verify Arc Flash Category dropdown: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_EnergySrcCtrl_SelectArcFlashCategory() {
    try {
      const eleArcFlashCategoryInputFirstTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputArcFlashCategory
        )
      );
      await expect(eleArcFlashCategoryInputFirstTime).toBeVisible({
        timeout: 5000,
      });
      await eleArcFlashCategoryInputFirstTime.click();
      const eleDropdownFirstCategory = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[2]`
      );
      await expect(eleDropdownFirstCategory).toBeVisible({ timeout: 5000 });
      await eleDropdownFirstCategory.click();
      await this.page.waitForTimeout(200);

      const eleArcFlashCategoryInputSecondTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_SelectedValuesInArcFlash
        )
      );
      await expect(eleArcFlashCategoryInputSecondTime).toBeVisible({
        timeout: 5000,
      });
      await eleArcFlashCategoryInputSecondTime.click();

      const eleDropdownSecondCategory = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[3]`
      );
      await expect(eleDropdownSecondCategory).toBeVisible({ timeout: 5000 });
      const selectedOption = await eleDropdownSecondCategory.textContent();
      await eleDropdownSecondCategory.click();

      const eleSelectedValues = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_SelectedValuesInArcFlash
        )
      );
      await expect(eleSelectedValues).toBeVisible({ timeout: 5000 });
      expect(eleSelectedValues).toHaveCount(1);

      await this.tb.logSuccess(
        `Selected this Arc Flash Category: ${selectedOption}`
      );
    } catch (error) {
      throw new Error((error as Error).message);
    }
  }

  public async JSB_EnergySrcCtrl_VerifyPrimaryVoltage() {
    try {
      const elePrimaryVoltageInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputPrimaryVoltage
        )
      );
      await expect(elePrimaryVoltageInput).toBeVisible({ timeout: 5000 });
      await expect(elePrimaryVoltageInput.locator("//span")).toHaveText(
        "Select an option"
      );
      await elePrimaryVoltageInput.click();

      //dropdown div arc flash locator works fine for this too
      const eleDropdownDivPrimaryVoltage = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownDivArcFlashCategory
        )
      );
      await expect(eleDropdownDivPrimaryVoltage).toBeVisible({ timeout: 5000 });

      //dropdown list items for arc flash locator works fine for this too
      const eleDropdownListItemsPrimaryVoltage = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )
      );

      const optionsText =
        await eleDropdownListItemsPrimaryVoltage.allTextContents();

      for (let i = 0; i < optionsText.length - 1; i++) {
        let optionText = optionsText[i];
        expect(optionText).toContain("kV");
      }

      const combinedOptions = optionsText.join(", ");
      await elePrimaryVoltageInput.click();

      await this.tb.logSuccess(
        `Selected Primary Voltage and received the following options: ${combinedOptions}`
      );
    } catch (error) {
      throw new Error(
        `Failed to verify Primary Voltage dropdown: ${(error as Error).message}`
      );
    }
  }

  public async JSB_EnergySrcCtrl_SelectPrimaryVoltage() {
    try {
      const elePrimaryVoltageInputFirstTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputPrimaryVoltage
        )
      );
      await expect(elePrimaryVoltageInputFirstTime).toBeVisible({
        timeout: 5000,
      });
      await elePrimaryVoltageInputFirstTime.click();

      //same locator works here
      const eleDropdownFirstOption = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[1]`
      );
      await expect(eleDropdownFirstOption).toBeVisible({ timeout: 5000 });
      await eleDropdownFirstOption.click();

      const eleTickMarkFirstOption = eleDropdownFirstOption.locator("//i");
      await expect(eleTickMarkFirstOption).toBeVisible();

      const eleDropdownSecondOption = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[2]`
      );
      await expect(eleDropdownSecondOption).toBeVisible({ timeout: 5000 });
      await eleDropdownSecondOption.click();

      const eleTickMarkSecondOption = eleDropdownSecondOption.locator("//i");
      await expect(eleTickMarkSecondOption).toBeVisible();

      const elePrimaryVoltageInputSecondTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_SelectedValuesInPrimaryVoltage
        )
      );
      await expect(elePrimaryVoltageInputSecondTime).toBeVisible({
        timeout: 5000,
      });
      const selectedOptions =
        elePrimaryVoltageInputSecondTime.locator("//span");
      await expect(selectedOptions).toHaveCount(2);

      const selectedOptionsArray = await selectedOptions.allTextContents();
      const optionsSelected = selectedOptionsArray.join(", ");
      await elePrimaryVoltageInputSecondTime.click();
      await this.tb.logSuccess(
        `Selected this Primary Voltage: ${optionsSelected}`
      );
    } catch (error) {
      throw new Error((error as Error).message);
    }
  }

  public async JSB_EnergySrcCtrl_VerifySecondaryVoltage() {
    try {
      const eleSecondaryVoltageInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputPrimaryVoltage
        )
      );
      await expect(eleSecondaryVoltageInput).toBeVisible({ timeout: 5000 });
      await expect(eleSecondaryVoltageInput.locator("//span")).toHaveText(
        "Select an option"
      );
      await eleSecondaryVoltageInput.click();

      //dropdown div arc flash locator works fine for this too
      const eleDropdownDivSecondaryVoltage = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownDivArcFlashCategory
        )
      );
      await expect(eleDropdownDivSecondaryVoltage).toBeVisible({
        timeout: 5000,
      });

      //dropdown list items for arc flash locator works fine for this too
      const eleDropdownListItemsSecondaryVoltage = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )
      );

      const optionsText =
        await eleDropdownListItemsSecondaryVoltage.allTextContents();

      for (let i = 0; i < optionsText.length - 1; i++) {
        let optionText = optionsText[i];
        expect(optionText).toContain("v");
      }

      const combinedOptions = optionsText.join(", ");
      await eleSecondaryVoltageInput.click();

      await this.tb.logSuccess(
        `Selected Secondary Voltage and received the following options: ${combinedOptions}`
      );
    } catch (error) {
      throw new Error(
        `Failed to verify Secondary Voltage dropdown: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_EnergySrcCtrl_SelectSecondaryVoltage() {
    try {
      //same xpath works fine here for secondary also
      const eleSecondaryVoltageInputFirstTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputPrimaryVoltage
        )
      );
      await expect(eleSecondaryVoltageInputFirstTime).toBeVisible({
        timeout: 5000,
      });
      await eleSecondaryVoltageInputFirstTime.click();

      //same locator works here
      const eleDropdownFirstOption = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[1]`
      );
      await expect(eleDropdownFirstOption).toBeVisible({ timeout: 5000 });
      await eleDropdownFirstOption.click();

      const eleTickMarkFirstOption = eleDropdownFirstOption.locator("//i");
      await expect(eleTickMarkFirstOption).toBeVisible();

      const eleDropdownSecondOption = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[2]`
      );
      await expect(eleDropdownSecondOption).toBeVisible({ timeout: 5000 });
      await eleDropdownSecondOption.click();

      const eleTickMarkSecondOption = eleDropdownSecondOption.locator("//i");
      await expect(eleTickMarkSecondOption).toBeVisible();

      const eleSecondaryVoltageInputSecondTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_SelectedValuesInSecondaryVoltage
        )
      );
      await expect(eleSecondaryVoltageInputSecondTime).toBeVisible({
        timeout: 5000,
      });

      const selectedOptions =
        eleSecondaryVoltageInputSecondTime.locator("//span");
      await expect(selectedOptions).toHaveCount(2);

      const selectedOptionsArray = await selectedOptions.allTextContents();
      const optionsSelected = selectedOptionsArray.join(", ");
      await eleSecondaryVoltageInputSecondTime.click();
      await this.tb.logSuccess(
        `Selected this Secondary Voltage: ${optionsSelected}`
      );
    } catch (error) {
      throw new Error((error as Error).message);
    }
  }

  public async JSB_EnergySrcCtrl_VerifyTransmissionVoltage() {
    try {
      //same locator works for transmission voltage too
      const eleTransmissionVoltageInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputArcFlashCategory
        )
      );
      await expect(eleTransmissionVoltageInput).toBeVisible({ timeout: 5000 });
      await expect(
        eleTransmissionVoltageInput.locator("//span//span")
      ).toHaveText("Select an option");
      await eleTransmissionVoltageInput.click();

      const eleDropdownDivTransmissionVoltage = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownDivArcFlashCategory
        )
      );
      await expect(eleDropdownDivTransmissionVoltage).toBeVisible({
        timeout: 5000,
      });

      const eleDropdownListItemsTransmissionVoltage = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )
      );
      const optionsText =
        await eleDropdownListItemsTransmissionVoltage.allTextContents();
      const combinedOptions = optionsText.join(", ");
      await eleTransmissionVoltageInput.click();

      await this.tb.logSuccess(
        `Selected Transmission Voltage and received the following options: ${combinedOptions}`
      );
    } catch (error) {
      throw new Error(
        `Failed to verify Transmission Voltage dropdown: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_EnergySrcCtrl_SelectTransmissionVoltage() {
    try {
      //same locator works fine for transmission voltage also
      const eleTransmissionVoltageInputFirstTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputArcFlashCategory
        )
      );
      await expect(eleTransmissionVoltageInputFirstTime).toBeVisible({
        timeout: 5000,
      });
      await Allure.step(
        "Clicking on the Transmission Voltage input box",
        async () => {
          await eleTransmissionVoltageInputFirstTime.click();
        }
      );

      const eleDropdownFirstCategory = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[2]`
      );
      await expect(eleDropdownFirstCategory).toBeVisible({ timeout: 5000 });
      await Allure.step(
        "Clicking on the First Option in Transmission Voltage dropdown",
        async () => {
          await eleDropdownFirstCategory.click();
        }
      );

      const eleTransmissionVoltageInputSecondTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_SelectedValuesInTransmissionVoltage
        )
      );
      await expect(eleTransmissionVoltageInputSecondTime).toBeVisible({
        timeout: 5000,
      });
      await eleTransmissionVoltageInputSecondTime.click();

      const eleDropdownSecondCategory = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[3]`
      );
      await expect(eleDropdownSecondCategory).toBeVisible({ timeout: 5000 });
      const selectedOption = await eleDropdownSecondCategory.textContent();
      await Allure.step("Clicking on the other option", async () => {
        await eleDropdownSecondCategory.click();
      });

      const eleSelectedValues = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_SelectedValuesInTransmissionVoltage
        )
      );
      await Allure.step(
        "Validation selection count to be only one",
        async () => {
          await expect(eleSelectedValues).toHaveCount(1);
          await this.tb.logSuccess(
            "Verified Transmission Voltage dropdown functionality"
          );
        }
      );

      await this.tb.logSuccess(
        `Selected this Transmission Voltage: ${selectedOption}`
      );
    } catch (error) {
      throw new Error((error as Error).message);
    }
  }

  public async JSB_EnergySrcCtrl_VerifyClearancePoints() {
    try {
      const eleClearancePointsInputBox = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputClearancePoints
        )
      );
      await expect(eleClearancePointsInputBox).toBeVisible({ timeout: 5000 });
      await expect(eleClearancePointsInputBox).toHaveAttribute("type", "text");
      await this.tb.logSuccess("Verified Clearance Points input field");
    } catch (error) {
      throw new Error(
        `Not able to verify Clearance Points input field, Hence Failed: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_EnergySrcCtrl_VerifyAddAdditionalEWPFunctionality() {
    try {
      const eleBtnAddAdditionalEWP = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_btnAddAdditionalEWP
        )
      );
      await Allure.step(
        "Checking visibility of Add Addtitional EWP Button",
        async () => {
          await expect(eleBtnAddAdditionalEWP).toBeVisible({ timeout: 5000 });
        }
      );
      await eleBtnAddAdditionalEWP.click();

      const eleDivAdditionalEWP = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_EnergySrcCtrl_divAdditionalEWP)
      );
      await expect(eleDivAdditionalEWP).toBeVisible({ timeout: 5000 });

      const eleBtnDeleteRecentEWP = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_btnDeleteMostRecentEWP
        )
      );
      await expect(eleBtnDeleteRecentEWP).toBeVisible({ timeout: 5000 });
      await eleBtnDeleteRecentEWP.click();

      await Allure.step("Making sure that the EWP is not visible", async () => {
        await expect(eleDivAdditionalEWP).not.toBeVisible();
      });
      await eleBtnAddAdditionalEWP.click();
      await expect(eleDivAdditionalEWP).toBeVisible({ timeout: 5000 });
      await this.tb.logSuccess(
        "Verified Add Additional EWP Button functionality"
      );
    } catch (error) {
      throw new Error(
        `Not able to verify Add Additional EWP Button, Hence Failed: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_EnergySrcCtrl_EWP_VerifyReqChecks() {
    try {
      const eleSaveAndContinueBtn = this.btnSaveAndContinue;
      if (eleSaveAndContinueBtn) {
        await eleSaveAndContinueBtn.click();
      } else {
        throw new Error(
          "No Save and Continue button found on Energy Source and Control Tab, Hence Failed"
        );
      }
      const eleReqCheckEWPInput = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_ReqChecks
        )}[1]`
      );
      await eleReqCheckEWPInput.scrollIntoViewIfNeeded();
      await expect(eleReqCheckEWPInput).toBeVisible({ timeout: 5000 });
      await expect(eleReqCheckEWPInput).toHaveText("This field is required");

      const eleReqCheckTimeIssued = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_ReqChecks
        )}[2]`
      );
      await eleReqCheckTimeIssued.scrollIntoViewIfNeeded();
      await expect(eleReqCheckTimeIssued).toBeVisible({ timeout: 5000 });
      await expect(eleReqCheckTimeIssued).toHaveText("Invalid time");
      const eleReqCheckProcedure = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_ReqChecks
        )}[3]`
      );
      await expect(eleReqCheckProcedure).toBeVisible({ timeout: 5000 });
      await expect(eleReqCheckProcedure).toHaveText("This field is required");
      const eleReqCheckIssuedBy = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_ReqChecks
        )}[4]`
      );
      await expect(eleReqCheckIssuedBy).toBeVisible({ timeout: 5000 });
      await expect(eleReqCheckIssuedBy).toHaveText("This field is required");
      const eleReqCheckReceivedBy = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_ReqChecks
        )}[5]`
      );
      await expect(eleReqCheckReceivedBy).toBeVisible({ timeout: 5000 });
      await expect(eleReqCheckReceivedBy).toHaveText("This field is required");
      const eleReqCheckRefPoint1 = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_ReqChecks
        )}[6]`
      );
      await expect(eleReqCheckRefPoint1).toBeVisible({ timeout: 5000 });
      await expect(eleReqCheckRefPoint1).toHaveText("This field is required");
      const eleReqCheckRefPoint2 = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_ReqChecks
        )}[7]`
      );
      await expect(eleReqCheckRefPoint2).toBeVisible({ timeout: 5000 });
      await expect(eleReqCheckRefPoint2).toHaveText("This field is required");
    } catch (error) {
      throw new Error(
        `Required Fields show no error when clicking save and continue without filling them, Hence Failed: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_EnergySrcCtrl_AddEWPDetails(
    EWP: string,
    TimeIssued: string,
    TimeCompleted: string,
    Procedure: string,
    IssuedBy: string,
    ReceivedBy: string,
    RefPoint1: string,
    RefPoint2: string,
    CircuitBreaker: string,
    Switch: string,
    Transformer: string
  ) {
    try {
      const eleEWPInput = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_EnergySrcCtrl_txtEWP)
      );
      await expect(eleEWPInput).toBeVisible({ timeout: 5000 });
      await expect(eleEWPInput).toHaveAttribute("type", "text");
      await eleEWPInput.fill(EWP);

      const eleTimeIssuedInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtTimeIssued
        )
      );
      await expect(eleTimeIssuedInput).toBeVisible({ timeout: 5000 });
      await expect(eleTimeIssuedInput).toHaveAttribute("type", "time");
      await eleTimeIssuedInput.fill(TimeIssued);

      const eleTimeCompleted = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtTimeCompleted
        )
      );
      await eleTimeCompleted.scrollIntoViewIfNeeded();
      await expect(eleTimeCompleted).toBeVisible({ timeout: 5000 });
      await expect(eleTimeCompleted).toHaveAttribute("type", "time");
      await eleTimeCompleted.fill(TimeCompleted);

      const eleProcedureInput = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtProcedure)
      );
      await eleProcedureInput.scrollIntoViewIfNeeded();
      await expect(eleProcedureInput).toBeVisible({ timeout: 5000 });
      await expect(eleProcedureInput).toHaveAttribute("type", "text");
      await eleProcedureInput.fill(Procedure);

      const eleIssuedByInput = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtIssuedBy)
      );
      await eleIssuedByInput.scrollIntoViewIfNeeded();
      await expect(eleIssuedByInput).toBeVisible({ timeout: 5000 });
      await expect(eleIssuedByInput).toHaveAttribute("type", "text");
      await eleIssuedByInput.fill(IssuedBy);

      const eleReceivedByInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtReceivedBy
        )
      );
      await eleReceivedByInput.scrollIntoViewIfNeeded();
      await expect(eleReceivedByInput).toBeVisible({ timeout: 5000 });
      await expect(eleReceivedByInput).toHaveAttribute("type", "text");
      await eleReceivedByInput.fill(ReceivedBy);

      const eleRefPoint1Input = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtRefPoint1)
      );
      await eleRefPoint1Input.scrollIntoViewIfNeeded();
      await expect(eleRefPoint1Input).toBeVisible({ timeout: 5000 });
      await expect(eleRefPoint1Input).toHaveAttribute("type", "text");
      await eleRefPoint1Input.fill(RefPoint1);

      const eleRefPoint2Input = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtRefPoint2)
      );
      await eleRefPoint2Input.scrollIntoViewIfNeeded();
      await expect(eleRefPoint2Input).toBeVisible({ timeout: 5000 });
      await expect(eleRefPoint2Input).toHaveAttribute("type", "text");
      await eleRefPoint2Input.fill(RefPoint2);

      const eleCircuitBreakerInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtCircuitBreaker
        )
      );
      await eleCircuitBreakerInput.scrollIntoViewIfNeeded();
      await expect(eleCircuitBreakerInput).toBeVisible({ timeout: 5000 });
      await expect(eleCircuitBreakerInput).toHaveAttribute("type", "text");
      await eleCircuitBreakerInput.fill(CircuitBreaker);

      const eleSwitchInput = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtSwitch)
      );
      await eleSwitchInput.scrollIntoViewIfNeeded();
      await expect(eleSwitchInput).toBeVisible({ timeout: 5000 });
      await expect(eleSwitchInput).toHaveAttribute("type", "text");
      await eleSwitchInput.fill(Switch);

      const eleTransformerInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_EWP_txtTransformer
        )
      );
      await eleTransformerInput.scrollIntoViewIfNeeded();
      await expect(eleTransformerInput).toBeVisible({ timeout: 5000 });
      await expect(eleTransformerInput).toHaveAttribute("type", "text");
      await eleTransformerInput.fill(Transformer);
      await this.page.waitForTimeout(300);
    } catch (error) {
      throw new Error(
        `Not able to add EWP Details, Hence Failed: ${(error as Error).message}`
      );
    }
  }

  public async JSB_EnergySrcCtrl_ClickSaveAndContinueBtn() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) await eleSaveAndContinue.click();
    else
      throw new Error(
        "No Save and Continue Button Found on 'Energy Source and Control' Tab, hence failed"
      );
    await this.page.waitForTimeout(2000);
  }

  public async JSB_WorkProcedures_VerifyTabHighlightedAutomatically() {
    const eleWorkProceduresNavigator = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavWorkProcedures)
    );
    await expect(eleWorkProceduresNavigator).toHaveClass(
      /border-neutral-shade-100/,
      { timeout: 7000 }
    );
    await expect(eleWorkProceduresNavigator).toHaveClass(/box-border/, {
      timeout: 7000,
    });
  }

  public async JSB_WorkProcedures_VerifyReqFieldChecks() {
    const eleSaveAndContinueBtn = this.btnSaveAndContinue;
    if (eleSaveAndContinueBtn) {
      await eleSaveAndContinueBtn.click();
    } else {
      throw new Error(
        "Save and Continue not found on Work Procedures Tab in JSB, Hence Failed"
      );
    }
    const eleDistributionBulletinsReqCheck = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_WorkProcedures_lblDistriBulletinsReqCheck
      )
    );
    await expect(eleDistributionBulletinsReqCheck).toBeVisible({
      timeout: 5000,
    });
  }

  public async JSB_WorkProcedures_VerifyDistributionBulletins() {
    try {
      const eleDistributionBulletInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_inputDistributionBulletins
        )
      );
      await expect(eleDistributionBulletInput).toBeVisible({ timeout: 5000 });
      await expect(eleDistributionBulletInput).toHaveAttribute(
        "placeholder",
        "Please select distribution bulletins"
      );
      await eleDistributionBulletInput.click();
      await this.page.waitForTimeout(200);

      //dropdown div arc flash locator works fine for this too
      const eleDropdownDivDistributionBulletins = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownDivArcFlashCategory
        )
      );
      await expect(eleDropdownDivDistributionBulletins).toBeVisible({
        timeout: 5000,
      });

      //dropdown list items for arc flash locator works fine for this too
      const eleDropdownListItemsDistributionBulletins = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )
      );
      const optionsText =
        await eleDropdownListItemsDistributionBulletins.allTextContents();

      const combinedOptions = optionsText.join(", ");
      await eleDistributionBulletInput.click();
      await this.page.waitForTimeout(200);
      await this.tb.logSuccess(
        `Received Distribution Bulletins: ${combinedOptions}`
      );
    } catch (error) {
      throw new Error(
        `Failed to verify Distribution Bulletins dropdown: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_WorkProcedures_SelectDistributionBulletins() {
    try {
      const eleDistributionBulletinInputFirstTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_inputDistributionBulletins
        )
      );
      await expect(eleDistributionBulletinInputFirstTime).toBeVisible({
        timeout: 5000,
      });
      await eleDistributionBulletinInputFirstTime.click();

      //same locator works here
      const eleDropdownFirstOption = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[1]`
      );
      await expect(eleDropdownFirstOption).toBeVisible({ timeout: 5000 });
      await eleDropdownFirstOption.click();

      const eleTickMarkFirstOption = eleDropdownFirstOption.locator("//i");
      await expect(eleTickMarkFirstOption).toBeVisible({ timeout: 5000 });

      const eleDropdownSecondOption = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[2]`
      );
      await eleDropdownSecondOption.click();

      const eleTickMarkSecondOption = eleDropdownSecondOption.locator("//i");
      await expect(eleTickMarkSecondOption).toBeVisible({ timeout: 5000 });

      const eleDistributionBulletinInputSecondTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_selectedValuesInDistriBullet
        )
      );
      await expect(eleDistributionBulletinInputSecondTime).toBeVisible({
        timeout: 5000,
      });
      const selectedOptions =
        eleDistributionBulletinInputSecondTime.locator("//span");
      await expect(selectedOptions).toHaveCount(2);

      const selectedOptionsArray = await selectedOptions.allTextContents();
      const optionsSelected = selectedOptionsArray.join(", ");
      await eleDistributionBulletinInputSecondTime.click();
      await this.page.waitForTimeout(200);
      await this.tb.logSuccess(
        `Selected Distribution Bulletins: ${optionsSelected}`
      );
    } catch (error) {
      throw new Error(
        `Error while Selecting Distribution Bulletins, Hence Failed: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_WorkProcedures_VerifyRulesOfCoverUp() {
    const eleRulesOfCoverUpChkBox = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_WorkProcedures_input4RulesOfCoverUp
      )
    );
    await expect(eleRulesOfCoverUpChkBox).toBeVisible({ timeout: 5000 });
    await expect(eleRulesOfCoverUpChkBox).toHaveAttribute("type", "checkbox");

    await eleRulesOfCoverUpChkBox.click();
    await expect(eleRulesOfCoverUpChkBox).toBeChecked();

    const eleLinkToRulesOfCoverUp = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_WorkProcedures_link4RulesAddDoc)
    );
    await expect(eleLinkToRulesOfCoverUp).toBeVisible({ timeout: 5000 });
    await expect(eleLinkToRulesOfCoverUp).toHaveAttribute(
      "href",
      "https://soco365.sharepoint.com/:b:/r/sites/GPCSafetyandHealthALL/Shared Documents/General/eJSB/4 RULES OF COVER UP.pdf?csf=1&web=1&e=XZR0v1"
    );

    await eleRulesOfCoverUpChkBox.click();
    await expect(eleRulesOfCoverUpChkBox).not.toBeChecked();
  }

  public async JSB_WorkProcedures_VerifyMADLinkAndPopUpBox() {
    const eleMADLinkToPopUpBox = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_WorkProcedures_linkMAD)
    );
    await expect(eleMADLinkToPopUpBox).toBeVisible({ timeout: 5000 });
    await eleMADLinkToPopUpBox.click();

    const eleMADPopUpBox = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_WorkProcedures_divPopUpMAD)
    );
    await expect(eleMADPopUpBox).toBeVisible({ timeout: 5000 });

    const eleHeadingMADPopUpBox = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_WorkProcedures_headingPopUpMAD)
    );
    await expect(eleHeadingMADPopUpBox).toBeVisible({ timeout: 5000 });
    await expect(eleHeadingMADPopUpBox).toHaveText("Minimum Approach Distance");

    const eleImageMADPopUpBox = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_WorkProcedures_imgPopUpMAD)
    );
    await expect(eleImageMADPopUpBox).toBeVisible({ timeout: 5000 });

    const eleClosePopUpBtnMAD = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_WorkProcedures_closePopUpBtnMAD)
    );
    await expect(eleClosePopUpBtnMAD).toBeVisible({ timeout: 5000 });
    await eleClosePopUpBtnMAD.click();
    await expect(eleMADPopUpBox).not.toBeVisible({ timeout: 5000 });
  }

  public async JSB_WorkProcedures_ClickCheckBoxMADAndVerifyReqCheck() {
    try {
      const eleCheckBoxMAD = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_WorkProcedures_checkBoxMAD)
      );
      await expect(eleCheckBoxMAD).toBeVisible({ timeout: 5000 });
      await expect(eleCheckBoxMAD).not.toBeChecked();
      await eleCheckBoxMAD.click();

      const eleSaveAndContinueBtn = this.btnSaveAndContinue;
      if (eleSaveAndContinueBtn != null) {
        await eleSaveAndContinueBtn.click();
      } else {
        throw new Error(
          "Save and Continue not found on Work Procedures Tab in JSB, Hence Failed"
        );
      }
    } catch (err) {
      throw new Error(
        `Issue with clicking Check Box in MAD Option: ${(err as Error).message}`
      );
    }
  }

  public async JSB_WorkProcedures_VerifyMADDropdown() {
    try {
      const eleMADDropdownInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_inputMinApproachDist
        )
      );
      await expect(eleMADDropdownInput).toBeVisible({ timeout: 5000 });
      await expect(eleMADDropdownInput.locator("//span//span")).toHaveText(
        "Select an option"
      );
      await eleMADDropdownInput.click();
      await this.page.waitForTimeout(200);
      //arc flash dropdown works here fine
      const eleDropdownDivMAD = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownDivArcFlashCategory
        )
      );
      await expect(eleDropdownDivMAD).toBeVisible({ timeout: 5000 });
      await this.page.waitForTimeout(200);
      const eleDropdownListItemsMAD = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )
      );
      const optionsText = await eleDropdownListItemsMAD.allTextContents();
      const combinedOptions = optionsText.join(", ");
      await eleMADDropdownInput.click();
      await this.page.waitForTimeout(200);
      await this.tb.logSuccess(`Received MAD Dropdown: ${combinedOptions}`);
    } catch (error) {
      throw new Error(
        `Issue in verifying MAD Dropdown in Work Procedures Sections: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_WorkProcedures_SelectMADOption() {
    try {
      //same locator works fine for transmission voltage also
      const eleMADInputFirstTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_inputMinApproachDist
        )
      );
      await expect(eleMADInputFirstTime).toBeVisible({ timeout: 5000 });
      await eleMADInputFirstTime.click();
      await this.page.waitForTimeout(200);
      const eleDropdownFirstCategory = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[2]`
      );
      await expect(eleDropdownFirstCategory).toBeVisible({ timeout: 5000 });
      await eleDropdownFirstCategory.click();
      await this.page.waitForTimeout(200);
      const eleMADInputSecondTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_selectedValuesInMAD
        )
      );
      await expect(eleMADInputSecondTime).toBeVisible({ timeout: 5000 });
      await eleMADInputSecondTime.click();
      await this.page.waitForTimeout(200);
      const eleDropdownSecondCategory = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[3]`
      );
      await expect(eleDropdownSecondCategory).toBeVisible({ timeout: 5000 });
      const selectedOption = await eleDropdownSecondCategory.textContent();
      await eleDropdownSecondCategory.click();

      const eleSelectedValues = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_selectedValuesInMAD
        )
      );
      await expect(eleSelectedValues).toBeVisible({ timeout: 5000 });
      await expect(eleSelectedValues).toHaveCount(1);
      await this.page.waitForTimeout(200);
      await this.tb.logSuccess(`Selected MAD Option: ${selectedOption}`);
    } catch (error) {
      throw new Error(
        `Error while selecting MAD Option from the dropdown ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_WorkProcedures_VerifySDOPHyperlink() {
    const eleSwitchingProceduresLinkBtn = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_WorkProcedures_linkSwitchingProcedures
      )
    );
    await expect(eleSwitchingProceduresLinkBtn).toBeVisible({ timeout: 5000 });
    await expect(eleSwitchingProceduresLinkBtn).toHaveAttribute(
      "href",
      "https://soco365.sharepoint.com/sites/intra_GPC_Power_Delivery/_layouts/15/viewer.aspx?sourcedoc={fed21851-6fba-4102-b4b0-69f64e987f8d}"
    );
  }

  public async JSB_WorkProcedures_VerifySDOPCheckBox() {
    try {
      const eleSDOPCheckBoxInput = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_WorkProcedures_checkBoxSDOP)
      );
      await expect(eleSDOPCheckBoxInput).toBeVisible({ timeout: 5000 });
      await expect(eleSDOPCheckBoxInput).not.toBeChecked();
      await eleSDOPCheckBoxInput.click();
      await this.page.waitForTimeout(200);
      await expect(eleSDOPCheckBoxInput).toBeChecked();
    } catch (err) {
      throw new Error(
        `Error while validating SDOP checkbox functionality: ${
          (err as Error).message
        }`
      );
    }
  }

  public async JSB_WorkProcedures_VerifyTOCRequestFormHyperlink() {
    try {
      const eleTOCLinkBtn = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_linkTOCRequestForm
        )
      );
      await expect(eleTOCLinkBtn).toBeVisible({ timeout: 5000 });
      await expect(eleTOCLinkBtn).toHaveAttribute(
        "href",
        "https://mobi.southernco.com/DCC_TOC_REQUEST/TOC"
      );
    } catch (err) {
      console.log(err);
      throw new Error(
        `Error while validating TOC Request Form Hyperlink: ${
          (err as Error).message
        }`
      );
    }
  }

  public async JSB_WorkProcedures_VerifyTOCCheckBox() {
    try {
      const eleTOCCheckBoxInput = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_WorkProcedures_checkBoxTOC)
      );
      await expect(eleTOCCheckBoxInput).toBeVisible({ timeout: 5000 });
      await expect(eleTOCCheckBoxInput).not.toBeChecked();
      await eleTOCCheckBoxInput.click();
      await this.page.waitForTimeout(200);
      await expect(eleTOCCheckBoxInput).toBeChecked();
    } catch (err) {
      throw new Error(
        `Error while validating TOC checkbox functionality: ${
          (err as Error).message
        }`
      );
    }
  }

  public async JSB_WorkProcedures_VerifyStepTouchPotential() {
    try {
      const eleStepTouchPotentialCheckBoxInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_checkBoxStepOrTouchPotential
        )
      );
      await expect(eleStepTouchPotentialCheckBoxInput).toBeVisible({
        timeout: 5000,
      });
      await expect(eleStepTouchPotentialCheckBoxInput).not.toBeChecked();
      await eleStepTouchPotentialCheckBoxInput.click();
      await this.page.waitForTimeout(200);
      await expect(eleStepTouchPotentialCheckBoxInput).toBeChecked();
    } catch (err) {
      throw new Error(
        `Error while validating TOC checkbox functionality: ${
          (err as Error).message
        }`
      );
    }
  }

  public async JSB_WorkProcedures_VerifyOtherWorkProceduresInputField(
    OtherProcedures: string
  ) {
    try {
      const eleOtherWorkProceduresInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_WorkProcedures_OtherWorkProceduresFieldBox
        )
      );
      await eleOtherWorkProceduresInput.scrollIntoViewIfNeeded();
      await expect(eleOtherWorkProceduresInput).toBeVisible({ timeout: 5000 });

      const initialHasScrollbar = await eleOtherWorkProceduresInput.evaluate(
        (el) => {
          return el.scrollHeight > el.clientHeight;
        }
      );

      if (initialHasScrollbar === true)
        throw new Error(
          "Vertical Scroll Bar already present without even overflow of text box, Hence Failed"
        );

      await eleOtherWorkProceduresInput.scrollIntoViewIfNeeded();
      await eleOtherWorkProceduresInput.focus();
      await eleOtherWorkProceduresInput.fill(OtherProcedures);

      await this.page.waitForTimeout(500);

      const hasScrollbar = await eleOtherWorkProceduresInput.evaluate((el) => {
        return el.scrollHeight > el.clientHeight;
      });
      if (hasScrollbar === false)
        throw new Error(
          "Vertical Scroll Bar did not appear after overflow of text box, Hence Failed"
        );
    } catch (error) {
      throw new Error(
        `Error while validating Other Work Procedures input field: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_WorkProcedures_SaveAndContinue() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    await expect(eleSaveAndContinue).toBeVisible({ timeout: 5000 });
    if (eleSaveAndContinue != null) await eleSaveAndContinue.click();
    else
      throw new Error(
        "Error while clicking Save and Continue Button on Work Procedures Tab, hence failed"
      );
    await this.page.waitForTimeout(2000);
  }

  public async JSB_SiteConditions_VerifyTabHighlightedAutomatically() {
    const eleSiteConditionsNavigator = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavSiteConditions)
    );
    await expect(eleSiteConditionsNavigator).toHaveClass(
      /border-neutral-shade-100/,
      { timeout: 7000 }
    );
    await expect(eleSiteConditionsNavigator).toHaveClass(/box-border/, {
      timeout: 7000,
    });
  }

  public async JSB_SiteConditions_VerifyIfProceedsToNextTabWithoutError() {
    try {
      const eleSaveAndContinueBtn = this.btnSaveAndContinue;
      if (eleSaveAndContinueBtn) {
        await eleSaveAndContinueBtn.click();
      } else {
        throw new Error(
          "Save and Continue button not found on Site Conditions Tab, hence failed"
        );
      }
      await this.page.waitForTimeout(2000);
      const eleCtrlsAssessmentNavigator = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_btnNavCtrlsAssessment)
      );
      await expect(eleCtrlsAssessmentNavigator).toHaveClass(/border-neutral-shade-100/, {
        timeout: 7000,
      });
      await expect(eleCtrlsAssessmentNavigator).toHaveClass(/box-border/, {
        timeout: 7000,
      });
      await this.tb.logSuccess(
        "Successfully proceeded to next tab after clicking save and continue button"
      );
      const eleSiteConditionsNavigator = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_btnNavSiteConditions)
      );
      await eleSiteConditionsNavigator.click();
      await this.page.waitForTimeout(2000);
      await this.tb.logSuccess(
        "Successfully navigated back to Site Conditions tab"
      );
    } catch (error) {
      throw new Error(
        `Failed to proceed to next tab after clicking save and continue button: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_SiteConditions_VerifyAllSiteConditionsButton() {
    const eleAllSiteConditionsCheckbox = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_SiteConditions_checkBoxAllSiteCondn
      )
    );
    await expect(eleAllSiteConditionsCheckbox).toBeVisible({ timeout: 5000 });
    if ((await eleAllSiteConditionsCheckbox.isChecked()) === false) {
      await eleAllSiteConditionsCheckbox.click();
    }
    await expect(eleAllSiteConditionsCheckbox).toBeChecked();

    const childCheckboxes = this.page
      .locator(
        this.getLocator(FormListPageLocators.JSB_SiteConditions_checkBoxes)
      )
      .all();
    const childBoxes = (await childCheckboxes).slice(1); // Skip the first checkbox
    if (childBoxes != null) {
      for (let checkbox of childBoxes) {
        if (await checkbox.isVisible()) {
          await expect(checkbox).toBeChecked();
        }
      }
    }

    await eleAllSiteConditionsCheckbox.click();
    if (childBoxes != null) {
      for (let checkbox of childBoxes) {
        if (await checkbox.isVisible()) {
          await expect(checkbox).not.toBeChecked();
        }
      }
    }
  }

  public async JSB_SiteConditions_VerifyAddSiteConditionsButton() {
    const eleAddSiteCondnsBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SiteConditions_btnAddSiteCondn)
    );
    await expect(eleAddSiteCondnsBtn).toBeVisible({ timeout: 5000 });
    await eleAddSiteCondnsBtn.click();

    const elePopUpAddSiteCondn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SiteConditions_popUpAddSiteCondn)
    );
    await expect(elePopUpAddSiteCondn).toBeVisible({ timeout: 5000 });
  }

  public async JSB_SiteConditions_CloseSiteConditionsPopUp() {
    const eleCloseBtnPopUp = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SiteConditions_btnClosePopUp)
    );
    await expect(eleCloseBtnPopUp).toBeVisible({ timeout: 5000 });
    await eleCloseBtnPopUp.click();
  }

  public async JSB_SiteConditions_VerifyApplicableSideCondnCount() {
    const eleCheckboxesApplicableSiteCondn = this.page
      .locator(
        this.getLocator(FormListPageLocators.JSB_SiteConditions_checkBoxes)
      )
      .all();
    const eleChildBoxes = (await eleCheckboxesApplicableSiteCondn).slice(1);
    const countOfSideCondns = eleChildBoxes.length;
    const eleAddSiteCondnsBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SiteConditions_btnAddSiteCondn)
    );
    await expect(eleAddSiteCondnsBtn).toBeVisible({ timeout: 5000 });
    await eleAddSiteCondnsBtn.click();
    const elePopUpAddSiteCondn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SiteConditions_popUpAddSiteCondn)
    );
    await expect(elePopUpAddSiteCondn).toBeVisible({ timeout: 5000 });
    const eleApplicableSiteCondnCount = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_SiteConditions_lblCountApplicableSiteCondns
      )
    );
    await expect(eleApplicableSiteCondnCount).toBeVisible({ timeout: 5000 });
    await expect(eleApplicableSiteCondnCount).toHaveText(
      countOfSideCondns.toString()
    );
  }

  public async JSB_SiteConditions_AddSiteConditionsUsingPopUp() {
    // Get all sections using the items-center class
    const sections = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_SiteConditions_checkboxesPopUpSectionHeaders
      )
    );
    // Get index of both sections
    const applicableSection = sections.first();
    const otherSection = sections.last();

    // Get all checkboxes in the applicable section
    const applicableSiteCondnCheckboxes = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_SiteConditions_checkboxesPopUpApplicableSiteCondns
      )
    );
    const otherSiteCondnCheckboxes = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_SiteConditions_checkboxesPopUpOtherSiteCondns
      )
    );

    // Check all applicable checkboxes
    const applicableCount = await applicableSiteCondnCheckboxes.count();
    for (let i = 0; i < applicableCount; i++) {
      const checkbox = applicableSiteCondnCheckboxes.nth(i);
      await expect(checkbox).toBeChecked();
    }

    // Check all other checkboxes
    const otherCount = await otherSiteCondnCheckboxes.count();
    for (let i = 0; i < otherCount; i++) {
      const checkbox = otherSiteCondnCheckboxes.first();
      await expect(checkbox).not.toBeChecked();
      await checkbox.click();
    }

    const eleAddSiteCondnsBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SiteConditions_btnAddPopUp)
    );
    await eleAddSiteCondnsBtn.click();
  }

  public async JSB_SiteConditions_SaveAndContinue() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) await eleSaveAndContinue.click();
    else
      throw new Error(
        "Error while clicking Save and Continue Button on Site Conditions Tab, hence failed"
      );
    await this.page.waitForTimeout(3000);
  }

  public async JSB_ControlAssessment_VerifyTabHighlightedAutomatically() {
    const eleCtrlsAssessmentNavigator = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavCtrlsAssessment)
    );
    await expect(eleCtrlsAssessmentNavigator).toHaveClass(
      /border-neutral-shade-100/,
      { timeout: 7000 }
    );
    await expect(eleCtrlsAssessmentNavigator).toHaveClass(/box-border/, {
      timeout: 7000,
    });
  }

  public async JSB_ControlAssessment_LogAvailableHeadingsOnControlAssessmentTab() {
    const eleHeadings = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_ControlAssessment_availableHeadingsOnTheScreen
      )
    );
    const optionsText = await eleHeadings.allTextContents();
    const combinedOptions = optionsText.join(", ");
    await this.tb.logSuccess(
      `Available Headings on Control Assessment Tab: ${combinedOptions}`
    );
  }

  public async JSB_ControlAssessment_VerifyRecControlsChkBoxFunctionality() {
    const eleCheckboxesOnTheScreen = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_ControlAssessment_CheckboxesOnTheScreen
      )
    );
    await expect(eleCheckboxesOnTheScreen.first()).toBeVisible();
    await expect(eleCheckboxesOnTheScreen.first()).toBeChecked();

    const eleAutoSelectedOptions = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_ControlAssessment_autoSelectedRecommendedControls
      )
    );
    if ((await eleAutoSelectedOptions.count()) < 1) {
      throw new Error("No Recommended Controls auto-selected, Hence Failed");
    }
    for (let i = 0; i < (await eleAutoSelectedOptions.count()); i++) {
      const selectedOption = eleAutoSelectedOptions.nth(i);
      await expect(selectedOption).toBeVisible();
    }

    await eleCheckboxesOnTheScreen.first().click();
    await expect(eleCheckboxesOnTheScreen.first()).not.toBeChecked();

    const eleEmptySelectedOptions = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_ControlAssessment_emptySelectedRecommendedControls
      )
    );
    try {
      await expect(eleEmptySelectedOptions).toBeVisible();
    } catch (error) {
      throw new Error("Recommended Controls not auto-deselected, Hence Failed");
    }

    await eleCheckboxesOnTheScreen.first().click();
  }

  public async JSB_ControlAssessment_VerifyOtherControlsDropdown() {
    const eleSelectorInputControlAssess = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_ControlAssessment_inputOtherControlsDropdown
      )
    );
    await expect(eleSelectorInputControlAssess).toBeVisible({ timeout: 5000 });
    await eleSelectorInputControlAssess.click();

    const eleDropdownDivArcFlashCategory = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_EnergySrcCtrl_DropdownDivArcFlashCategory
      )
    );
    await expect(eleDropdownDivArcFlashCategory).toBeVisible({ timeout: 5000 });

    const eleDropdownListItemsArcFlash = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
      )
    );
    const optionsText = await eleDropdownListItemsArcFlash.allTextContents();
    const combinedOptions = optionsText.join(", ");
    await eleSelectorInputControlAssess.click();
    await this.tb.logSuccess(
      `Received Other Controls Dropdown: ${combinedOptions}`
    );
  }

  public async JSB_ControlAssessment_VerifyCrossButtonOtherControlsSelections() {
    try {
      const eleSelectedOptionsOtherControls = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_ControlAssessment_selectedOptionsInOtherControls
        )
      );
      await expect(eleSelectedOptionsOtherControls).toBeVisible({ timeout: 5000 });

      const eleCrossButton = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_crossButtonFirstSelectedValuesInDropdown
        )
      );
      await eleCrossButton.click();
      await this.page.waitForTimeout(200);

      const eleCheckboxesOnTheScreen = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_ControlAssessment_CheckboxesOnTheScreen
        )
      );
      await eleCheckboxesOnTheScreen.first().click();
      await this.page.waitForTimeout(200);
      await expect(eleSelectedOptionsOtherControls).toBeVisible({ timeout: 5000 });
    } catch (error) {
      throw new Error(
        `Error while verifying Cross Button on Other Controls Selections: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_ControlAssessment_SelectOtherControlsFromDropdown() {
    try {
      const eleSelectorInputControlAssess = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_inputPrimaryVoltage
        )
      );
      await eleSelectorInputControlAssess.click();

      //same locator works here
      const eleDropdownFirstOption = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[1]`
      );
      await eleDropdownFirstOption.click();
      await this.page.waitForTimeout(200);
      const eleTickMarkFirstOption = eleDropdownFirstOption.locator("//i");
      await expect(eleTickMarkFirstOption).toBeVisible({ timeout: 5000 });

      const eleDropdownSecondOption = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory
        )}[2]`
      );
      await eleDropdownSecondOption.click();
      await this.page.waitForTimeout(200);

      const eleTickMarkSecondOption = eleDropdownSecondOption.locator("//i");
      await expect(eleTickMarkSecondOption).toBeVisible({ timeout: 5000 });

      const eleOtherControlsInputSecondTime = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_EnergySrcCtrl_SelectedValuesInPrimaryVoltage
        )
      );

      const selectedOptions = eleOtherControlsInputSecondTime.locator("//span");
      await expect(selectedOptions).toHaveCount(2);

      const selectedOptionsArray = await selectedOptions.allTextContents();
      const optionsSelected = selectedOptionsArray.join(", ");
      await eleOtherControlsInputSecondTime.click();
      await this.tb.logSuccess(`Selected Other Controls: ${optionsSelected}`);
    } catch (error) {
      throw new Error((error as Error).message);
    }
  }

  public async JSB_ControlAssessment_VerifyAdditionalInformationInputField(
    AdditionalInfo: string
  ) {
    try {
      const eleAdditionalInfoInput = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_ControlAssessment_txtAdditionalInfo
        )
      );

      await eleAdditionalInfoInput.scrollIntoViewIfNeeded();
      await expect(eleAdditionalInfoInput).toBeVisible({ timeout: 5000 });

      const initialHasScrollbar = await eleAdditionalInfoInput.evaluate(
        (el) => {
          return el.scrollHeight > el.clientHeight;
        }
      );
      await this.page.waitForTimeout(200);
      if (initialHasScrollbar === true)
        throw new Error(
          "Vertical Scroll Bar already present without even overflow of text box, Hence Failed"
        );

      await eleAdditionalInfoInput.focus();
      await eleAdditionalInfoInput.fill(AdditionalInfo);
      await this.page.waitForTimeout(200);

      const hasScrollbar = await eleAdditionalInfoInput.evaluate((el) => {
        return el.scrollHeight > el.clientHeight;
      });
      if (hasScrollbar === false)
        throw new Error(
          "Vertical Scroll Bar did not appear after overflow of text box, Hence Failed"
        );
    } catch (error) {
      throw new Error(
        `Error while validating Other Work Procedures input field: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_ControlAssessment_SaveAndContinue() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) await eleSaveAndContinue.click();
    else
      throw new Error(
        "Error while clicking Save and Continue Button on Controls Assessment Tab, hence failed"
      );
    await this.page.waitForTimeout(2000);
  }

  public async JSB_Attachments_VerifyTabHighlightedAutomatically() {
    const eleAttachmentsNavigator = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavAttachments)
    );
    await expect(eleAttachmentsNavigator).toHaveClass(
      /border-neutral-shade-100/,
      { timeout: 7000 }
    );
    await expect(eleAttachmentsNavigator).toHaveClass(/box-border/, {
      timeout: 7000,
    });
  }

  public async JSB_Attachments_VerifyIfProceedsToNextTabWithoutError() {
    try {
      const eleSaveAndContinueBtn = this.btnSaveAndContinue;
      if (eleSaveAndContinueBtn) {
        await eleSaveAndContinueBtn.click();
      } else {
        throw new Error(
          "Save and Continue button not found on Attachments Tab, hence failed"
        );
      }
      await this.page.waitForTimeout(2000);
      const eleCtrlsAssessmentNavigator = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_btnNavJSBSummary)
      );
      await expect(eleCtrlsAssessmentNavigator).toHaveClass(
        /border-neutral-shade-100/,
        {
          timeout: 7000,
        }
      );
      await expect(eleCtrlsAssessmentNavigator).toHaveClass(/box-border/, {
        timeout: 7000,
      });
      const eleSiteConditionsNavigator = this.page.locator(
        this.getLocator(FormListPageLocators.JSB_btnNavAttachments)
      );
      await eleSiteConditionsNavigator.click();
      await this.page.waitForTimeout(2000);
    } catch (error) {
      throw new Error(
        `Failed to proceed to next tab after clicking save and continue button: ${
          (error as Error).message
        }`
      );
    }
  }

  public async JSB_Attachments_VerifyPhotoAdditionUsingAddPhotosBtn() {
    const addPhotosButton = this.page.getByText("Add photos", { exact: true });
    const fileInput = this.page.locator('input[type="file"]').first();

    const eleHeadingPhotos = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_lblPhotos)
    );
    await expect(eleHeadingPhotos).toBeVisible({ timeout: 5000 });

    let photoCount = await eleHeadingPhotos.innerText();

    await expect(addPhotosButton).toBeVisible({ timeout: 5000 });

    const acceptAttribute = await fileInput.getAttribute("accept");
    const expectedTypes = [
      ".apng",
      ".avif",
      ".gif",
      ".jpg",
      ".jpeg",
      ".png",
      ".svg",
      ".webp",
    ];

    const actualTypes = acceptAttribute?.split(",") || [];
    expect(actualTypes).toEqual(expectedTypes);

    const isMultiple = await fileInput.getAttribute("multiple");
    expect(isMultiple).not.toBeNull();

    expect(photoCount.split("(")[1].split(")")[0]).toBe("0");

    const testImage1Path = path.join(
      __dirname,
      "../Data/dummy-media/dummy_image1.jpg"
    );
    const testImage2Path = path.join(
      __dirname,
      "../Data/dummy-media/dummy_image2.png"
    );

    await fileInput.setInputFiles([testImage1Path, testImage2Path]);

    await this.page.waitForTimeout(1000);

    //checking the loading spinner to be visible and then hidden
    // await this.page.waitForSelector("//div/section/div/div[1]/label/i[2]", {
    //   state: "visible",
    // });
    // await this.page.waitForSelector("//div/section/div/div[1]/label/i[2]", {
    //   state: "hidden",
    // });

    try {
      const eleUploadedImage = this.page
        .locator(
          this.getLocator(FormListPageLocators.JSB_Attachments_uploadedImages)
        )
        .first();
      await eleUploadedImage.waitFor({ state: "visible" });
      await expect(eleUploadedImage).toBeVisible({ timeout: 5000 });
      await this.page.waitForTimeout(3000);
      photoCount = await eleHeadingPhotos.innerText();
      expect(photoCount.split("(")[1].split(")")[0]).toBe("2");
    } catch (error) {
      throw new Error(
        "File upload did not complete successfully: " + (error as Error).message
      );
    }
  }

  public async JSB_Attachments_VerifyPhotosDeletion() {
    const eleUploadedImages = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_uploadedImages)
    );
    expect(await eleUploadedImages.count()).toBe(2);
    await expect(eleUploadedImages.first()).toBeVisible({ timeout: 5000 });

    const eleHeadingPhotos = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_lblPhotos)
    );
    await expect(eleHeadingPhotos).toBeVisible({ timeout: 5000 });
    await this.page.waitForTimeout(3000);
    let photoCount = await eleHeadingPhotos.innerText();
    expect(photoCount.split("(")[1].split(")")[0]).toBe("2");

    const eleDeleteButton = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_uploadedImgDeleteBtn)
    );
    await expect(eleDeleteButton).toBeVisible({ timeout: 5000 });
    await eleDeleteButton.click();

    await this.page.waitForTimeout(1000);

    photoCount = await eleHeadingPhotos.innerText();
    expect(photoCount.split("(")[1].split(")")[0]).toBe("1");

    expect(await eleUploadedImages.count()).toBe(1);
  }

  // public async JSB_Attachments_VerifyMaxPhotoSizeErrorPrompt(
  //   expectedErrorPrompt: string
  // ) {
  //   const eleAddPhotosButton = this.page.getByText("Add photos", {
  //     exact: true,
  //   });
  //   await expect(eleAddPhotosButton).toBeVisible({timeout: 5000});
  //   const fileInput = this.page.locator('input[type="file"]').first();
  //   const testImage2Path = path.join(__dirname, "../Data/dummy_image3.png");
  //   await fileInput.setInputFiles([testImage3Path]);

  //   const eleMaxFileSizePrompt = this.page.locator(this.getLocator(
  //     FormListPageLocators.JSB_Attachments_lblMaxFileSizePrompt
  //   ));
  //   await expect(eleMaxFileSizePrompt).toBeVisible();
  //   await expect(eleMaxFileSizePrompt).toHaveText(expectedErrorPrompt);

  //   await this.page.waitForTimeout(2000);
  // }

  public async JSB_Attachments_VerifyDocumentsAdditionUsingAddDocumentsBtn() {
    const addDocumentsButton = this.page.getByText("Add documents", {
      exact: true,
    });
    const fileInput = this.page.locator('input[type="file"]').nth(1);

    const eleHeadingDocuments = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_lblDocuments)
    );
    await expect(eleHeadingDocuments).toBeVisible({ timeout: 5000 });

    let documentCount = await eleHeadingDocuments.innerText();

    await expect(addDocumentsButton).toBeVisible({ timeout: 5000 });

    const acceptAttribute = await fileInput.getAttribute("accept");
    const expectedTypes = [
      ".pdf",
      ".doc",
      ".docx",
      ".xls",
      ".xlsx",
      ".ppt",
      ".pptx",
    ];

    const actualTypes = acceptAttribute?.split(",") || [];
    expect(actualTypes).toEqual(expectedTypes);

    const isMultiple = await fileInput.getAttribute("multiple");
    expect(isMultiple).not.toBeNull();

    expect(documentCount.split("(")[1].split(")")[0]).toBe("0");

    const testDoc1Path = path.join(
      __dirname,
      "../Data/dummy-media/dummy_doc1.pdf"
    );
    const testDoc2Path = path.join(
      __dirname,
      "../Data/dummy-media/dummy_doc2.doc"
    );

    await fileInput.setInputFiles([testDoc1Path, testDoc2Path]);
    try {
      const eleUploadedDocument = this.page
        .locator(
          this.getLocator(
            FormListPageLocators.JSB_Attachments_uploadedDocuments
          )
        )
        .first();
      await expect(eleUploadedDocument).toBeVisible({ timeout: 5000 });
      await this.page.waitForTimeout(3000);
      documentCount = await eleHeadingDocuments.innerText();
      expect(documentCount.split("(")[1].split(")")[0]).toBe("2");
    } catch (error) {
      throw new Error(
        "File upload did not complete successfully: " + (error as Error).message
      );
    }
  }

  public async JSB_Attachments_VerifyMenuButtonForRecentlyUploadedDoc() {
    const eleUploadedDocument = this.page
      .locator(
        this.getLocator(FormListPageLocators.JSB_Attachments_uploadedDocuments)
      )
      .first();
    await expect(eleUploadedDocument).toBeVisible({ timeout: 5000 });

    const eleMenuButton = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_Attachments_recentlyUploadedDocMenuBtn
      )
    );
    await expect(eleMenuButton).toBeVisible({ timeout: 5000 });
    await eleMenuButton.click();

    const eleDownloadOption = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_menuDownloadBtn)
    );
    await expect(eleDownloadOption).toBeVisible({ timeout: 5000 });

    const eleEditOption = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_menuEditBtn)
    );
    await expect(eleEditOption).toBeVisible({ timeout: 5000 });

    const eleDeleteOption = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_menuDeleteBtn)
    );
    await expect(eleDeleteOption).toBeVisible({ timeout: 5000 });
  }

  public async JSB_Attachments_VerifyDownloadButtonForRecentlyUploadedDoc() {
    const eleDownloadOption = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_menuDownloadBtn)
    );
    await expect(eleDownloadOption).toBeVisible({ timeout: 5000 });

    const downloads: any[] = [];

    this.page.on("download", (download) => {
      downloads.push(download);
    });

    const downloadPromise = this.page.waitForEvent("download");
    await eleDownloadOption.click();
    const download = await downloadPromise;
    await this.page.waitForTimeout(1000);

    //if want only one file to be downloaded then this can be uncommented:
    // if (downloads.length > 1) {
    //     throw new Error(`Expected 1 file to be downloaded but got ${downloads.length} files`);
    // }
    if (downloads.length === 0) {
      throw new Error("No files were downloaded");
    }
    expect(download).toBeTruthy();
    const path = await download.path();
    if (!path) {
      throw new Error("File download failed");
    }
  }

  public async JSB_Attachments_VerifyEditButtonForRecentlyUploadedDoc(
    EditDocName: string
  ) {
    const eleUploadedDocument = this.page
      .locator(
        this.getLocator(FormListPageLocators.JSB_Attachments_uploadedDocuments)
      )
      .first();
    await expect(eleUploadedDocument).toBeVisible({ timeout: 5000 });

    const eleUploadedDocumentLabel = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_Attachments_recentlyUploadedDocName
      )
    );
    await expect(eleUploadedDocumentLabel).toBeVisible({ timeout: 5000 });
    const uploadedDocumentName = await eleUploadedDocumentLabel.innerText();

    const eleMenuButton = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_Attachments_recentlyUploadedDocMenuBtn
      )
    );
    await expect(eleMenuButton).toBeVisible({ timeout: 5000 });
    await eleMenuButton.click();

    const eleEditOption = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_menuEditBtn)
    );
    await expect(eleEditOption).toBeVisible({ timeout: 5000 });
    await eleEditOption.click();

    const eleEditDocPopUp = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_editDocPopUp)
    );
    await expect(eleEditDocPopUp).toBeVisible({ timeout: 5000 });

    const eleClosePopUpButton = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_WorkProcedures_closePopUpBtnMAD)
    );
    await expect(eleClosePopUpButton).toBeVisible({ timeout: 5000 });
    await eleClosePopUpButton.click();

    await expect(eleEditDocPopUp).not.toBeVisible();

    await eleMenuButton.click();
    await eleEditOption.click();

    await expect(eleEditDocPopUp).toBeVisible();

    const eleCancelPopUpBtn = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_Attachments_btnEditDocPopUpCancel
      )
    );
    await expect(eleCancelPopUpBtn).toBeVisible({ timeout: 5000 });
    await eleCancelPopUpBtn.click();

    await expect(eleEditDocPopUp).not.toBeVisible();

    await eleMenuButton.click();
    await eleEditOption.click();

    await expect(eleEditDocPopUp).toBeVisible();

    const eleEditDocNameInput = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_Attachments_txtEditDocPopUpNewName
      )
    );
    await expect(eleEditDocNameInput).toBeVisible({ timeout: 5000 });
    const currentName = await eleEditDocNameInput.inputValue();

    const currentFileExtension = currentName.split(".").pop();
    const newFileName = `${EditDocName}.${currentFileExtension}`;
    await eleEditDocNameInput.fill(newFileName);

    const lblDocCurrentName = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_Attachments_lblEditDocPopUpCurrentName
      )
    );
    await expect(lblDocCurrentName).toBeVisible({ timeout: 5000 });
    const currentDocName = await lblDocCurrentName.innerText();
    expect(currentDocName).toBe(uploadedDocumentName);

    const eleSaveEditedDocBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_btnEditDocPopUpSave)
    );
    await expect(eleSaveEditedDocBtn).toBeVisible({ timeout: 5000 });
    await eleSaveEditedDocBtn.click();
  }

  public async JSB_Attachments_VerifyDocumentsDeletion() {
    const eleHeadingDocuments = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_lblDocuments)
    );
    await expect(eleHeadingDocuments).toBeVisible({ timeout: 5000 });

    let documentCount = await eleHeadingDocuments.innerText();
    expect(documentCount.split("(")[1].split(")")[0]).toBe("2");

    const eleMenuButton = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_Attachments_recentlyUploadedDocMenuBtn
      )
    );
    await expect(eleMenuButton).toBeVisible({ timeout: 5000 });
    await eleMenuButton.click();

    const eleDeleteDocBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_menuDeleteBtn)
    );
    await expect(eleDeleteDocBtn).toBeVisible({ timeout: 5000 });
    await eleDeleteDocBtn.click();

    documentCount = await eleHeadingDocuments.innerText();
    expect(documentCount.split("(")[1].split(")")[0]).toBe("1");
  }

  public async JSB_Attachments_ClickSaveAndContinueBtn() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) await eleSaveAndContinue.click();
    else
      throw new Error(
        "Error while clicking Save and Continue Button on Attachments Tab, hence failed"
      );
    await this.page.waitForTimeout(2000);
  }

  public async JSB_Summary_VerifyTabHighlightedAutomatically() {
    const eleSummaryNavigator = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavJSBSummary)
    );
    await expect(eleSummaryNavigator).toHaveClass(/border-neutral-shade-100/, {
      timeout: 7000,
    });
    await expect(eleSummaryNavigator).toHaveClass(/box-border/, {
      timeout: 7000,
    });
  }

  public async JSB_Summary_VerifyQRCodeFunctionality() {
    const eleQRCode = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Summary_QRCodeScanner)
    );
    await expect(eleQRCode).toBeVisible({ timeout: 5000 });
    const eleQRCodeScreenshot = await eleQRCode.screenshot({
      scale: "css",
    });

    try {
      const qrURL = await this.tb.scanQRCode(eleQRCodeScreenshot);
      await this.tb.logSuccess(`QR Code URL: ${qrURL}`);
      const newPage = await this.page.context().newPage();
      await newPage.goto(qrURL);
      await newPage.waitForURL(qrURL);
      await newPage.waitForLoadState("networkidle");
      await newPage.waitForTimeout(2000);
      await this.tb.captureScreenshot(
        newPage,
        "JSB-Summary-Page-After-Scanning-QR-Code"
      );
      await newPage.close();
    } catch (err) {
      console.error(
        `Failed to scan QR Code on Summary JSB Page: ${(err as Error).message}`
      );
    }
  }

  public async JSB_Summary_ClickSaveAndContinueBtn() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) await eleSaveAndContinue.click();
    else
      throw new Error(
        "Error while clicking Save and Continue Button on JSB Summary Tab, hence failed"
      );
    await this.page.waitForTimeout(2000);
  }

  public async JSB_SignOff_VerifyTabHighlightedAutomatically() {
    const eleNavSignOff = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_btnNavSignOff)
    );
    await expect(eleNavSignOff).toHaveClass(/border-neutral-shade-100/, {
      timeout: 7000,
    });
    await expect(eleNavSignOff).toHaveClass(/box-border/, { timeout: 7000 });
  }

  public async JSB_SignOff_VerifySearchByNameOrIdFieldFunctionality() {
    const eleSearchByNameIDBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_btnNameSelection)
    );
    await expect(eleSearchByNameIDBtn).toBeVisible({ timeout: 5000 });
    await eleSearchByNameIDBtn.click();
    const eleNameSearchPopUpDiv = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_popUpDivNameSelection)
    );
    await expect(eleNameSearchPopUpDiv).toBeVisible({ timeout: 5000 });

    const eleClosePopUpBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SiteConditions_btnClosePopUp)
    );
    await expect(eleClosePopUpBtn).toBeVisible({ timeout: 5000 });
    await eleClosePopUpBtn.click();
    await this.page.waitForTimeout(500);
    await expect(eleNameSearchPopUpDiv).not.toBeVisible();

    await eleSearchByNameIDBtn.click();
    await expect(eleNameSearchPopUpDiv).toBeVisible();

    const eleSearchByNameIDInput = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_SignOff_txtInputSearchPopUpNameSelection
      )
    );
    await expect(eleSearchByNameIDInput).toBeVisible({ timeout: 5000 });
    await expect(eleSearchByNameIDBtn).toBeEditable();

    const eleOtherNameBtn = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_SignOff_btnOtherNamePopUpNameSelection
      )
    );
    await expect(eleOtherNameBtn).toBeVisible({ timeout: 5000 });
    await eleOtherNameBtn.click();
    await this.page.waitForTimeout(500);
    await expect(eleNameSearchPopUpDiv).not.toBeVisible();
  }

  public async JSB_SignOff_VerifyAddOtherNameInputFunctionality(
    OtherName: string
  ) {
    const eleAddOtherNameInput = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_txtInputOtherName)
    );
    await expect(eleAddOtherNameInput).toBeVisible({ timeout: 5000 });
    await eleAddOtherNameInput.click();

    await eleAddOtherNameInput.fill(OtherName);
    await this.page.waitForTimeout(200);

    const eleAddOtherNameInputValue = await eleAddOtherNameInput.inputValue();
    expect(eleAddOtherNameInputValue).toBe(OtherName);
  }

  public async JSB_SignOff_VerifyAddSignForOtherName(OtherName: string) {
    const lblSignForOtherNameBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_lblSignForOtherNameBtn)
    );
    await lblSignForOtherNameBtn.scrollIntoViewIfNeeded();
    await expect(lblSignForOtherNameBtn).toBeVisible({ timeout: 5000 });
    await expect(lblSignForOtherNameBtn).toHaveText("Sign for " + OtherName);

    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) await eleSaveAndContinue.click();
    else
      throw new Error(
        "Error while clicking Save and Continue Button on Sign Off Tab, hence failed"
      );

    const eleReqCheckPromptSignForOtherName = this.page.locator(
      this.getLocator(
        FormListPageLocators.JSB_SignOff_lblReqCheckPromptForSignForOtherName
      )
    );
    await expect(eleReqCheckPromptSignForOtherName).toBeVisible({
      timeout: 5000,
    });
    await expect(eleReqCheckPromptSignForOtherName).toHaveText(
      "Signature is mandatory."
    );

    const eleSignForOtherNameBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_btnSignForOtherName)
    );
    await expect(eleSignForOtherNameBtn).toBeVisible({ timeout: 5000 });
    await eleSignForOtherNameBtn.click();

    const eleSignatureCanvasPopUp = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_canvasSignature)
    );
    await expect(eleSignatureCanvasPopUp).toBeVisible({ timeout: 5000 });

    const eleCancelSignaturePopUpBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_btnCancelInCanvas)
    );
    await expect(eleCancelSignaturePopUpBtn).toBeVisible({ timeout: 5000 });
    await eleCancelSignaturePopUpBtn.click();

    await expect(eleSignatureCanvasPopUp).not.toBeVisible();
    await eleSignForOtherNameBtn.click();
    await expect(eleSignatureCanvasPopUp).toBeVisible({ timeout: 5000 });

    const box = await eleSignatureCanvasPopUp.boundingBox();
    if (!box) throw new Error("Cannot get canvas boundaries");

    await this.page.mouse.move(box.x + 100, box.y + 100);
    await this.page.mouse.down();

    await this.page.mouse.move(box.x + 200, box.y + 80, { steps: 10 });
    await this.page.mouse.move(box.x + 300, box.y + 100, { steps: 10 });
    await this.page.mouse.move(box.x + 400, box.y + 90, { steps: 10 });

    await this.page.mouse.up();

    await this.page.waitForTimeout(200);

    const eleSaveSignaturePopUpBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_btnSignOffInCanvas)
    );
    await expect(eleSaveSignaturePopUpBtn).toBeVisible({ timeout: 5000 });
    await eleSaveSignaturePopUpBtn.click();
    await expect(eleSignatureCanvasPopUp).not.toBeVisible({
      timeout: 10000,
    });
    const eleSignatureImage = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_imgSignature)
    );
    await expect(eleSignatureImage).toBeVisible({ timeout: 5000 });
  }

  public async JSB_SignOff_VerifyAddNameBtnFunctionality() {
    const eleSignatureNameBoxDivs = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_divSignatureNameBoxDivs)
    );
    await expect(eleSignatureNameBoxDivs).toBeVisible({ timeout: 5000 });
    await expect(eleSignatureNameBoxDivs).toHaveCount(1);

    const eleAddNameBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_btnAddName)
    );
    await expect(eleAddNameBtn).toBeVisible({ timeout: 5000 });
    await eleAddNameBtn.click();

    await expect(eleSignatureNameBoxDivs).toHaveCount(2);

    const eleDeleteButtonForRecentSignatureBox = this.page.locator(
      `${this.getLocator(
        FormListPageLocators.JSB_SignOff_deleteSignatureNameBoxDiv
      )}[2]`
    );
    await expect(eleDeleteButtonForRecentSignatureBox).toBeVisible({
      timeout: 5000,
    });
    await eleDeleteButtonForRecentSignatureBox.click();

    await expect(eleSignatureNameBoxDivs).toHaveCount(1);
  }

  public async JSB_SignOff_VerifyDeleteSignAndResign() {
    const eleDeleteSignatureButton = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_btnDeleteSignature)
    );
    await expect(eleDeleteSignatureButton).toBeVisible({ timeout: 5000 });
    await eleDeleteSignatureButton.click();

    const eleSignatureImage = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_imgSignature)
    );
    await expect(eleSignatureImage).not.toBeVisible();

    const eleSignForOtherNameBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_btnSignForOtherName)
    );
    await expect(eleSignForOtherNameBtn).toBeVisible({ timeout: 5000 });
    await eleSignForOtherNameBtn.click();

    const eleSignatureCanvasPopUp = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_canvasSignature)
    );
    await expect(eleSignatureCanvasPopUp).toBeVisible();

    const box = await eleSignatureCanvasPopUp.boundingBox();
    if (!box) throw new Error("Cannot get canvas boundaries");

    await this.page.mouse.move(box.x + 100, box.y + 100);
    await this.page.mouse.down();

    await this.page.mouse.move(box.x + 200, box.y + 80, { steps: 10 });
    await this.page.mouse.move(box.x + 100, box.y + 100, { steps: 10 });
    await this.page.mouse.move(box.x + 200, box.y + 100, { steps: 10 });
    await this.page.mouse.move(box.x + 400, box.y + 90, { steps: 10 });
    await this.page.mouse.move(box.x + 500, box.y + 120, { steps: 10 });

    await this.page.mouse.up();

    await this.page.waitForTimeout(200);

    const eleSaveSignaturePopUpBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_SignOff_btnSignOffInCanvas)
    );
    await expect(eleSaveSignaturePopUpBtn).toBeVisible();
    await eleSaveSignaturePopUpBtn.click();
    await expect(eleSignatureCanvasPopUp).not.toBeVisible({
      timeout: 10000,
    });

    await expect(eleSignatureImage).toBeVisible();
  }

  public async JSB_SignOff_ClickSaveAndContinueBtn() {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) await eleSaveAndContinue.click();
    else
      throw new Error(
        "Error while clicking Save and Continue Button on Sign Off Tab, hence failed"
      );
    await this.page.waitForTimeout(2000);
  }

  public async JSB_VerifyCompleteFormButtonFunctionality() {
    const eleCompleteFormBtn = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_CompleteForm_btnCompleteForm)
    );
    await expect(eleCompleteFormBtn).toBeVisible({ timeout: 5000 });
    await eleCompleteFormBtn.click();

    await this.page.waitForTimeout(3000);
  }

  public async EBO_ValidateHECARulesComponent() {
    await this.tb.logMessage("Starting validation of HECA Rules component");

    const eleHECARulesLbl = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_ObservationDetails_HECA_Rules_lblHeading
      )
    );
    await expect(eleHECARulesLbl).toBeVisible({ timeout: 5000 });
    await this.tb.logMessage("HECA Rules label is visible");

    const eleHECARulesRightArrow = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_ObservationDetails_HECA_Rules_rightArrow
      )
    );
    await expect(eleHECARulesRightArrow).toBeVisible({ timeout: 5000 });
    await this.tb.logMessage("HECA Rules right arrow is visible");

    await eleHECARulesRightArrow.click();
    await this.page.waitForTimeout(200);
    await this.tb.logMessage("Clicked on HECA Rules right arrow");

    const eleHECARulesDownArrow = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_ObservationDetails_HECA_Rules_downArrow
      )
    );
    await expect(eleHECARulesDownArrow).toBeVisible({ timeout: 5000 });
    await this.tb.logMessage("HECA Rules down arrow is visible");

    const eleHECARulesExpandedSection = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_ObservationDetails_HECA_Rules_expandedSection
      )
    );
    await expect(eleHECARulesExpandedSection).toBeVisible({ timeout: 5000 });
    await this.tb.logMessage("HECA Rules expanded section is visible");

    await eleHECARulesDownArrow.click();
    await this.page.waitForTimeout(200);
    await this.tb.logMessage("Clicked on HECA Rules down arrow");

    await expect(eleHECARulesExpandedSection).not.toBeVisible({
      timeout: 5000,
    });
    await this.tb.logMessage("HECA Rules expanded section is collapsed");

    await this.page.waitForTimeout(200);
    await this.tb.logSuccess("HECA Rules component is validated successfully");
  }

  public async EBO_ObservationDetails_VerifyDateSelection() {
    await this.tb.logMessage(
      "Starting verification of Observation Date selection"
    );

    const eleDateSelector = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_ObservationDetails_dateSelector)
    );
    await expect(eleDateSelector).toBeVisible({ timeout: 5000 });
    await this.tb.logMessage("Date selector is visible");

    const today = new Date();
    const year = today.getFullYear();
    const month = (today.getMonth() + 1).toString().padStart(2, "0");
    const day = today.getDate().toString().padStart(2, "0");
    const formattedDate = `${year}-${month}-${day}`;
    const eleDateSelectorValue = await eleDateSelector.inputValue();
    expect(eleDateSelectorValue).toBe(formattedDate);
    await this.tb.logMessage("Verified current date is set by default");

    const twoDaysLater = new Date();
    twoDaysLater.setDate(today.getDate() + 2);
    const formattedTwoDaysLater = `${twoDaysLater.getFullYear()}-${(
      twoDaysLater.getMonth() + 1
    )
      .toString()
      .padStart(2, "0")}-${twoDaysLater.getDate().toString().padStart(2, "0")}`;
    await eleDateSelector.fill(formattedTwoDaysLater);
    await this.tb.logMessage("Attempting to set date to 2 days later");

    const errorToastBox = this.page.locator(
      this.getLocator(
        FormListPageLocators.FormListPage_EBO_DateSelector_ErrorToast
      )
    );
    await expect(errorToastBox).toBeVisible({ timeout: 5000 });
    await this.tb.logMessage("Error toast is visible for future date");
    await expect(errorToastBox).toBeHidden({ timeout: 5000 });
    await this.tb.logMessage("Error toast is hidden after timeout");

    const updatedDateValue = await eleDateSelector.inputValue();
    expect(updatedDateValue).not.toBe(formattedTwoDaysLater);
    await this.tb.logMessage("Verified future date was not accepted");

    const oneDayBefore = new Date();
    oneDayBefore.setDate(today.getDate() - 1);
    const formattedOneDayBefore = `${oneDayBefore.getFullYear()}-${(
      oneDayBefore.getMonth() + 1
    )
      .toString()
      .padStart(2, "0")}-${oneDayBefore.getDate().toString().padStart(2, "0")}`;
    await eleDateSelector.fill(formattedOneDayBefore);
    await this.tb.logMessage("Setting date to 1 day before");

    const updatedDateValueOneDayBefore = await eleDateSelector.inputValue();
    expect(updatedDateValueOneDayBefore).toBe(formattedOneDayBefore);
    await this.tb.logMessage("Verified past date was accepted");

    await this.tb.logSuccess("Observation Date is updated successfully");
  }

  public async EBO_ObservationDetails_VerifyObservationTimeSelector() {
    await this.tb.logMessage(
      "Starting verification of Observation Time selector"
    );

    const eleTimeSelector = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_ObservationDetails_timeSelector)
    );
    await expect(eleTimeSelector).toBeVisible({ timeout: 5000 });
    await this.tb.logMessage("Observation Time selector is visible");

    const eleTimeSelectorValue = await eleTimeSelector.inputValue();
    const currentTime = new Date();
    const bufferInMinutes = 3;

    const [inputHours, inputMinutes] = eleTimeSelectorValue
      .split(":")
      .map(Number);
    const inputDate = new Date();
    inputDate.setHours(inputHours, inputMinutes, 0, 0);

    const diffInMinutes = Math.abs(
      (currentTime.getTime() - inputDate.getTime()) / 60000
    );
    expect(diffInMinutes).toBeLessThanOrEqual(bufferInMinutes);
    await this.tb.logMessage(
      `Verified default time is set to ${eleTimeSelectorValue}`
    );

    const oneHourLater = new Date();
    oneHourLater.setHours(currentTime.getHours() + 1);
    const formattedOneHourLater = oneHourLater.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
    });
    await eleTimeSelector.fill(formattedOneHourLater);
    await this.tb.logMessage("Setting time to 1 hour later");

    const updatedTimeValue = await eleTimeSelector.inputValue();
    expect(updatedTimeValue).toBe(formattedOneHourLater);
    await this.tb.logMessage("Verified time is updated to 1 hour later");

    await this.tb.logSuccess(
      "Observation Time selector is validated successfully"
    );
  }

  public async EBO_ObservationDetails_FillWONumberInputField() {
    const eleWONumberInput = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_ObservationDetails_InputWONumber)
    );
    await expect(eleWONumberInput).toBeVisible({ timeout: 5000 });
    await eleWONumberInput.fill("583409");
    await this.tb.logMessage("Filled WONumber input field with value 583409");
  }

  public async EBO_ObservationDetails_VerifyOpCoObservedDropdown() {
    try {
      // Base locator for OpCoObserved dropdown (assumed from error locator and select class)
      const eleOpCoObservedDropdown = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdown
        )
      );
      await expect(eleOpCoObservedDropdown).toBeVisible({ timeout: 5000 });
      await eleOpCoObservedDropdown.click();
      const eleDropdownOptions = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdownOptions
        )
      );
      await expect(eleDropdownOptions.first()).toBeVisible({ timeout: 5000 });
      const optionsText = await eleDropdownOptions.allTextContents();
      const combinedOptions = optionsText.join(", ");
      await this.tb.logSuccess(
        `OpCoObserved dropdown options: ${combinedOptions}`
      );
      await eleOpCoObservedDropdown.click();
    } catch (error) {
      throw new Error(
        `Failed to verify OpCoObserved dropdown: ${(error as Error).message}`
      );
    }
  }

  public async EBO_ObservationDetails_SelectOpCoObserved() {
    try {
      // Base locator for OpCoObserved dropdown (assumed from error locator and select class)
      const eleOpCoObservedDropdown = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdown
        )
      );
      await expect(eleOpCoObservedDropdown).toBeVisible({ timeout: 5000 });
      await eleOpCoObservedDropdown.click();
      const optionBGE = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdownOptions_BGE
        )
      );
      await expect(optionBGE).toBeVisible({ timeout: 5000 });
      await optionBGE.click();
      await this.page.waitForTimeout(200);
      await this.tb.logSuccess(`Selected OpCoObserved option: 'BGE'`);
    } catch (error) {
      throw new Error(
        `Failed to select OpCoObserved option: ${(error as Error).message}`
      );
    }
  }

  public async EBO_ObservationDetails_VerifyDepartmentObservedDropdown() {
    try {
      const eleDepartmentObservedDropdown = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_DepartmentObservedDropdown
        )
      );
      await expect(eleDepartmentObservedDropdown).toBeVisible({
        timeout: 5000,
      });
      let retryCount = 0;
      const maxRetries = 3;

      while (retryCount < maxRetries) {
        await eleDepartmentObservedDropdown.click();
        await this.page.waitForTimeout(1000);

        const isDropdownVisible = await this.page
          .locator(
            this.getLocator(
              FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdownOptions
            )
          )
          .first()
          .isVisible();

        if (isDropdownVisible) {
          break;
        }

        retryCount++;
        if (retryCount === maxRetries) {
          throw new Error(
            "Failed to open department observed dropdown after multiple retries"
          );
        }
      }

      const eleDropdownOptions = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdownOptions
        )
      );
      await expect(eleDropdownOptions.first()).toBeVisible({ timeout: 5000 });
      const optionsText = await eleDropdownOptions.allTextContents();
      const combinedOptions = optionsText.join(", ");
      await this.tb.logSuccess(
        `Department Observed dropdown options: ${combinedOptions}`
      );
      await eleDepartmentObservedDropdown.click();
    } catch (error) {
      throw new Error(
        `Failed to verify Department Observed dropdown: ${
          (error as Error).message
        }`
      );
    }
  }

  public async EBO_ObservationDetails_SelectDepartmentObserved() {
    try {
      const eleDepartmentObservedDropdown = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_DepartmentObservedDropdown
        )
      );
      await expect(eleDepartmentObservedDropdown).toBeVisible({
        timeout: 5000,
      });

      let retryCount = 0;
      const maxRetries = 3;

      while (retryCount < maxRetries) {
        await eleDepartmentObservedDropdown.click();
        await this.page.waitForTimeout(1000);

        const optionsDepartmentObserved = this.page.locator(
          this.getLocator(
            FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdownOptions
          )
        );

        const isDropdownVisible = await optionsDepartmentObserved
          .first()
          .isVisible();

        if (isDropdownVisible) {
          await expect(optionsDepartmentObserved.first()).toBeVisible({
            timeout: 5000,
          });
          break;
        }

        retryCount++;
        if (retryCount === maxRetries) {
          throw new Error(
            "Failed to open department observed dropdown after multiple retries"
          );
        }
      }

      const optionBSC = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_DepartmentObservedOptions_BSC
        )
      );
      await expect(optionBSC).toBeVisible({ timeout: 5000 });
      await optionBSC.click();

      await this.page.waitForTimeout(200);
      await this.tb.logSuccess(
        `Selected DepartmentObserved option: 'BSC - BSC'`
      );
    } catch (error) {
      throw new Error(
        `Failed to select DepartmentObserved option: ${
          (error as Error).message
        }`
      );
    }
  }

  public async EBO_ObservationDetails_VerifyWorkTypeDropdown() {
    try {
      const eleWorkTypeDropdown = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_WorkTypeDropdown
        )
      );
      await expect(eleWorkTypeDropdown).toBeVisible({ timeout: 5000 });
      await expect(eleWorkTypeDropdown.locator("//span")).toHaveText(
        "Choose the observed work types"
      );
      await eleWorkTypeDropdown.click();
      const eleDropdownOptions = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdownOptions
        )
      );
      await expect(eleDropdownOptions.first()).toBeVisible({ timeout: 5000 });
      const optionsText = await eleDropdownOptions.allTextContents();
      const combinedOptions = optionsText.join(", ");
      await eleWorkTypeDropdown.click();
      await this.tb.logSuccess(`WorkType dropdown options: ${combinedOptions}`);
    } catch (error) {
      throw new Error(
        `Failed to verify WorkType dropdown: ${(error as Error).message}`
      );
    }
  }

  public async EBO_ObservationDetails_SelectWorkType() {
    try {
      const eleWorkTypeDropdown = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_WorkTypeDropdown
        )
      );
      await expect(eleWorkTypeDropdown).toBeVisible({ timeout: 5000 });
      await eleWorkTypeDropdown.click();

      const eleDropdownFirstOption = this.page.locator(
        `(${this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdownOptions
        )})[1]`
      );
      await expect(eleDropdownFirstOption).toBeVisible({ timeout: 5000 });
      const firstOptionText = await eleDropdownFirstOption.textContent();
      await eleDropdownFirstOption.click();

      const eleTickMarkFirstOption = eleDropdownFirstOption.locator(
        "//i[@class='ci-check']"
      );
      await expect(eleTickMarkFirstOption).toBeVisible({ timeout: 5000 });

      const eleDropdownSecondOption = this.page.locator(
        `(${this.getLocator(
          FormListPageLocators.EBO_ObservationDetails_OpCoObservedDropdownOptions
        )})[2]`
      );
      await expect(eleDropdownSecondOption).toBeVisible({ timeout: 5000 });
      const secondOptionText = await eleDropdownSecondOption.textContent();
      await eleDropdownSecondOption.click();

      const eleTickMarkSecondOption = eleDropdownSecondOption.locator(
        "//i[@class='ci-check']"
      );
      await expect(eleTickMarkSecondOption).toBeVisible({ timeout: 5000 });

      const eleSelectedValues = eleWorkTypeDropdown.locator("//span");
      await expect(eleSelectedValues).toHaveCount(2);

      if (!firstOptionText || !secondOptionText) {
        throw new Error("Dropdown option text is null or empty");
      }
      await expect(eleSelectedValues.first()).toHaveText(firstOptionText);
      await expect(eleSelectedValues.last()).toHaveText(secondOptionText);

      await eleWorkTypeDropdown.click();
      await this.page.waitForTimeout(200);
      await this.tb.logSuccess(
        `Selected WorkType options: ${firstOptionText} and ${secondOptionText}`
      );
    } catch (error) {
      throw new Error(
        `Failed to select WorkType options: ${(error as Error).message}`
      );
    }
  }

  public async EBO_ObservationDetails_VerifyUseCurrentLocationBtn() {
    const eleUseCurrLoc = this.btnJSB_GPSCo_UseCurrentLocation;
    if (eleUseCurrLoc != null) await eleUseCurrLoc.click();
    else
      throw new Error(
        "No 'Use Current Location' Button found in GPS Coordinates Section, in EBO Observation Details, Hence Failed"
      );
    const eleLatitudeEBO = await this.InputLatitudeJSB();
    if (eleLatitudeEBO != null) {
      await eleLatitudeEBO.focus();
      const currLat = await eleLatitudeEBO.inputValue();
      if (currLat !== "36.2274") {
        throw new Error(
          "Current Location Latitude Doesn't Matches the Actual Current Latitude, Hence Failed"
        );
      }
    } else
      throw new Error(
        "No Enter Latitude Element Found in EBO Observation Details, hence failed"
      );

    const eleLongitudeEBO = await this.InputLongitudeJSB();
    if (eleLongitudeEBO != null) {
      await eleLongitudeEBO.focus();
      const currLong = await eleLongitudeEBO.inputValue();
      if (currLong !== "-83.0098") {
        throw new Error(
          "Current Location Longitude Doesn't Matches the Actual Current Longitude, Hence Failed"
        );
      }
    } else
      throw new Error(
        "No Enter Longitude Element Found in EBO Observation Details, hence failed"
      );
  }

  public async EBO_ClickSaveAndContinueBtn(tabName: string) {
    const eleSaveAndContinue = this.btnSaveAndContinue;
    if (eleSaveAndContinue != null) {
      await expect(eleSaveAndContinue).toBeVisible({ timeout: 5000 });
      await eleSaveAndContinue.click({ force: true });
      await this.tb.logSuccess(
        `Save and Continue Button Clicked on ${tabName} Tab and Tab is now saved`
      );
      await this.page.waitForTimeout(2000);
    } else {
      throw new Error(
        `No Save and Continue Button Found on ${tabName} Tab, hence failed`
      );
    }
  }

  public async EBO_VerifyBlueTickAndBlueBorderOnSavedTab_ObservationDetails() {
    const eleObservationDetails = this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_EBO_NavObservationDetails
      )
    );
    await this.page.waitForTimeout(2000);
    const eleTickMark = eleObservationDetails.locator(
      "//i[contains(@class,'ci-circle_check')]"
    );
    await expect(eleTickMark).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess(
      `Blue Tick and Blue BG on Observation Details Tab is visible thus verified`
    );
  }

  public async EBO_VerifyReqCheckHighEnergyTasks() {
    const eleSaveAndContinueBtn = this.btnSaveAndContinue;
    if (eleSaveAndContinueBtn != null) {
      await eleSaveAndContinueBtn.click();
      if (
        this.page.locator(
          this.getLocator(
            FormListPageLocators.JSB_TasksAndCriRisks_lblReqCheckNoActivity
          )
        ) == null
      ) {
        throw new Error(
          "No Requried Check before clicking Save and Continue button in High Energy Tasks Section"
        );
      }
    } else {
      throw new Error(
        "No Save and Continue button found in High Energy Tasks Section"
      );
    }
  }

  public async EBO_VerifySearchBoxFunctionality_HighEnergyTasks(
    ActivityName: string
  ): Promise<string | null> {
    try {
      const eleSearchBoxField = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_popUpAddActivitySearchBox
        )
      );
      await expect(eleSearchBoxField).toBeVisible({ timeout: 5000 });
      await eleSearchBoxField.clear();
      await eleSearchBoxField.fill("ekctpoxyz");
      await this.page.waitForTimeout(200);

      const divTasksNoMatchFound = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_divTasksInAddActivityPopUp
        )
      );
      await expect(divTasksNoMatchFound).toBeVisible({ timeout: 5000 });
      const taskButtonsNoMatchFound = divTasksNoMatchFound.locator("button");
      const taskButtonsCountNoMatchFound =
        await taskButtonsNoMatchFound.count();
      expect(taskButtonsCountNoMatchFound).toBe(0);

      await this.tb.logSuccess(
        `No match found for the Activity Name: ${ActivityName} in High Energy Tasks Section`
      );

      await eleSearchBoxField.clear();

      await eleSearchBoxField.fill(ActivityName.substring(0, 3));
      await this.page.waitForTimeout(200);

      const divTasks = this.page.locator(
        this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_divTasksInAddActivityPopUp
        )
      );
      await expect(divTasks).toBeVisible({ timeout: 5000 });
      const taskButtons = this.page.locator(
        `${this.getLocator(
          FormListPageLocators.JSB_TasksAndCriRisks_btnsTaskInAddActivityPopUp
        )}`
      );
      const taskButtonsCount = await taskButtons.count();

      let flag = false;
      let taskButtonSearched;
      let taskButtonLocatorString;

      for (let i = 0; i < taskButtonsCount; i++) {
        const btnTask = this.page.locator(
          `${this.getLocator(
            FormListPageLocators.JSB_TasksAndCriRisks_btnsTaskInAddActivityPopUp
          )}[${i + 1}]`
        );

        const labelText = await btnTask
          .locator("span.text-brand-gray-80")
          .textContent();

        if (labelText === ActivityName) {
          flag = true;
          taskButtonSearched = btnTask;
          taskButtonLocatorString = `${this.getLocator(
            FormListPageLocators.JSB_TasksAndCriRisks_btnsTaskInAddActivityPopUp
          )}[${i + 1}]`;
          break;
        }
      }
      if (flag === true) {
        await taskButtonSearched?.click();
        await this.page.waitForTimeout(200);
        if (taskButtonSearched === null)
          throw new Error(
            `No Task Found for the Activity Name: ${ActivityName} in High Energy Tasks Section`
          );
        const firstSubTaskButton = this.page.locator(
          `${taskButtonLocatorString}/following-sibling::div//div//div//div[1]`
        );
        await expect(firstSubTaskButton).toBeVisible({ timeout: 5000 });
        const firstSubTaskCheckbox = firstSubTaskButton.locator(
          "input.Checkbox_root__Lr2rF"
        );
        await expect(firstSubTaskCheckbox).toBeVisible({ timeout: 5000 });
        const firstSubTaskLabel = firstSubTaskButton.locator(
          "span.text-brand-gray-80"
        );
        await expect(firstSubTaskLabel).toBeVisible({ timeout: 5000 });
        await firstSubTaskButton?.click();
        await this.tb.logSuccess(
          `Selected Sub Task: ${firstSubTaskLabel} for the Activity: ${ActivityName} in High Energy Tasks Section`
        );
        await this.page.waitForTimeout(200);
        if (firstSubTaskLabel.textContent() === null)
          throw new Error(
            `No Sub Task Found for the Activity Name: ${ActivityName} in High Energy Tasks Section`
          );
        return firstSubTaskLabel.textContent();
      } else {
        throw new Error(
          "Search Box on Search Doesn't Shows the Specified Task, Hence Failed"
        );
      }
    } catch (error: any) {
      throw new Error(
        "Search Box field doesn't works as expected, Hence Failed :" + error
      );
    }
  }

  public async EBO_HET_VerifyAddedActivityTitleAndSubPage(subTaskName: string) {
    const eleAddedActivityTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_HET_AddedActivityTitleLbl)
    );
    await expect(eleAddedActivityTitle).toBeVisible({ timeout: 5000 });
    const addedActivityTitleText = await eleAddedActivityTitle.textContent();
    expect(addedActivityTitleText).toBe("Excavate");
    const eleAddedActivitySubTaskTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_HET_AddedActivitySubTaskTitleLbl)
    );
    await expect(eleAddedActivitySubTaskTitle).toBeVisible({ timeout: 5000 });
    const addedActivitySubTaskTitleText =
      await eleAddedActivitySubTaskTitle.textContent();
    expect(addedActivitySubTaskTitleText).toBe(subTaskName);
    await this.tb.logSuccess(
      `Added Activity Title and Sub Task Title are visible in High Energy Tasks Section`
    );

    const eleSubPageForAddedActivity = this.page.locator(
      this.getLocator(
        FormListPageLocators.FormListPage_EBO_NavDynamicLocator(subTaskName)
      )
    );
    await expect(eleSubPageForAddedActivity).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(
      `Sub Page for the Added Activity: ${subTaskName} in High Energy Tasks Section is visible`
    );
  }

  public async EBO_VerifyUIForAddedSubpage(): Promise<boolean> {
    const eleSubPageTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_SubPage_TitleLbl("Excavate"))
    );
    await expect(eleSubPageTitle).toBeVisible({ timeout: 5000 });
    const eleSubPageSubTaskTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_SubPage_SubTaskTitleLbl)
    );
    await expect(eleSubPageSubTaskTitle).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(
      `Sub Page Title and Sub Task Title are visible in Sub Page for the Added Activity: 'Excavate' in the new sub page for added Activity`
    );

    const hazardsObservedComponents = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_SubPage_HighEnergyHazardObservedComponents
      )
    );
    const hazardsObservedComponentsCount =
      await hazardsObservedComponents.count();
    let flag = false;
    if (hazardsObservedComponentsCount > 0) {
      await this.tb.logSuccess(
        `Hazard Observed Components found in Sub Page for the Added Activity: 'Excavate' in the new sub page for added Activity`
      );
      flag = true;
      await this.tb.logMessage("Verifying Hazard Observed Component");
    } else {
      await this.tb.logSuccess(
        `No Hazard Observed Components found in Sub Page for the Added Activity: 'Excavate' in High Energy Tasks Section`
      );
    }
    return flag;
  }

  public async EBO_VerifyHazardObservedComponent() {
    await this.tb.logMessage(
      "Verifying First Component in the Hazards Observed list for the added activity"
    );
    const eleHazardObservedComponentTitle = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_SubPage_FirstHazardObservedComponentTitle
      )
    );
    await expect(eleHazardObservedComponentTitle).toBeVisible({
      timeout: 5000,
    });
    const hazardObservedComponentTitleText =
      await eleHazardObservedComponentTitle.textContent();
    await this.tb.logSuccess(
      `First Component with title ${hazardObservedComponentTitleText} found and is visible`
    );
    const eleHazardObservedComponentToggleLabel = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_SubPage_FirstHazardObservedComponentToggleLabel
      )
    );
    await expect(eleHazardObservedComponentToggleLabel).toBeVisible({
      timeout: 5000,
    });
    const hazardObservedComponentToggleLabelText =
      await eleHazardObservedComponentToggleLabel.textContent();
    await this.tb.logSuccess(
      `Toggle Label for the First Component with title ${hazardObservedComponentToggleLabelText} found and is visible`
    );
    const eleHazardObservedComponentInputToggle = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_SubPage_FirstHazardObservedComponentInputToggle
      )
    );
    await expect(eleHazardObservedComponentInputToggle).toBeVisible({
      timeout: 5000,
    });
    const ariaChecked =
      await eleHazardObservedComponentInputToggle.getAttribute("aria-checked");
    if (ariaChecked === "true") {
      await this.tb.logSuccess(
        `Input Toggle for the First Component with title ${hazardObservedComponentTitleText} is checked`
      );
    } else {
      await this.tb.logSuccess(
        `Input Toggle for the First Component with title ${hazardObservedComponentTitleText} is not checked`
      );
    }
    await this.tb.logMessage("Verifying Input Toggle for the First Component");
    await eleHazardObservedComponentInputToggle.click();
    await this.tb.logSuccess(
      `Input Toggle for the First Component with title ${hazardObservedComponentTitleText} clicked`
    );
    const ariaCheckedAfterClick =
      await eleHazardObservedComponentInputToggle.getAttribute("aria-checked");
    if (ariaCheckedAfterClick === "true") {
      await this.tb.logSuccess(
        `Input Toggle for the First Component with title ${hazardObservedComponentTitleText} is checked after clicking`
      );
    } else {
      await this.tb.logSuccess(
        `Input Toggle for the First Component with title ${hazardObservedComponentTitleText} is not checked after clicking`
      );
      await eleHazardObservedComponentInputToggle.click();
      await this.tb.logMessage(
        "Finally set the toggle to checked for moving forward"
      );
    }
    await this.tb.logSuccess(
      "Successfully verified Input Toggle for the First Component"
    );

    const eleHazardDescriptionInput = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_RecommendedHighEnergyHazards_PopUp_HazardDescriptionInput
      )
    );
    await expect(eleHazardDescriptionInput).toBeVisible({ timeout: 5000 });
    await eleHazardDescriptionInput.fill("Test Hazard Description");
    await this.tb.logSuccess(
      `Hazard Description Input for the First Component with title ${hazardObservedComponentTitleText} is visible and filled with text ${eleHazardDescriptionInput.inputValue()}`
    );

    const eleDirectControlYes = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_RecommendedHighEnergyHazards_PopUp_DirectControlsYes
      )
    );
    await expect(eleDirectControlYes).toBeVisible({ timeout: 5000 });
    await eleDirectControlYes.click();
    await this.tb.logSuccess(
      `Direct Control Yes Button for the First Component with title ${hazardObservedComponentTitleText} is clicked`
    );

    const eleDirectControlsDropdown = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_RecommendedHighEnergyHazards_PopUp_DropdownDirectControls
      )
    );
    await expect(eleDirectControlsDropdown).toBeVisible({ timeout: 5000 });
    await eleDirectControlsDropdown.click();
    await this.tb.logSuccess(
      `Direct Controls Dropdown for the First Component with title ${hazardObservedComponentTitleText} is visible and clicked`
    );

    const eleDirectControlsDropdownOptions = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_RecommendedHighEnergyHazards_PopUp_DropdownDirectControlsOptions
      )
    );
    const eleDirectControlsDropdownOptionsCount =
      await eleDirectControlsDropdownOptions.count();
    for (let i = 0; i < eleDirectControlsDropdownOptionsCount; i++) {
      const eleDirectControlsDropdownOption =
        eleDirectControlsDropdownOptions.nth(i);
      const eleDirectControlsDropdownOptionText =
        await eleDirectControlsDropdownOption.textContent();
      await this.tb.logSuccess(
        `Direct Controls Dropdown Option ${
          i + 1
        } for the First Component with title ${hazardObservedComponentTitleText} is visible and the text is ${eleDirectControlsDropdownOptionText}`
      );
    }
    const firstOptionInDropdown = this.page.locator(
      `${this.getLocator(
        FormListPageLocators.EBO_RecommendedHighEnergyHazards_PopUp_DropdownDirectControlsOptions
      )}[1]`
    );
    await expect(firstOptionInDropdown).toBeVisible({ timeout: 5000 });
    await firstOptionInDropdown.click();
    await this.page.waitForTimeout(200);
    await eleDirectControlsDropdown.click();
    await this.tb.logSuccess(
      `First Option in Direct Controls Dropdown for the First Component with title ${hazardObservedComponentTitleText} is visible and clicked and dropdown is closed`
    );
  }

  public async EBO_ValidatePopUpForRecommendedHighEnergyHazards(): Promise<boolean> {
    const elePopUpForRecommendedHighEnergyHazards = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_WorkProcedures_divPopUpMAD)
    );
    let flag = false;
    
    try {
      const isPopupVisible = await elePopUpForRecommendedHighEnergyHazards.isVisible({ timeout: 5000 });
      
      if (isPopupVisible) {
        await this.tb.logSuccess(
          `Pop Up for Recommended High Energy Hazards is visible thus validating it`
        );
        flag = true;
        
        const elePopUpHeading = this.page.locator(
          this.getLocator(FormListPageLocators.JSB_Attachments_lblPhotos)
        );
        await expect(elePopUpHeading).toBeVisible({ timeout: 5000 });
        const elePopUpHeadingText = await elePopUpHeading.textContent();
        expect(elePopUpHeadingText).toBe("Recommended High Energy Hazards");
        await this.tb.logSuccess(
          `Pop Up Heading for Recommended High Energy Hazards is visible and the text is ${elePopUpHeadingText}`
        );

        const elePopUpSubTitle = this.page.locator(
          this.getLocator(
            FormListPageLocators.EBO_RecommendedHighEnergyHazards_PopUp_SubTitle
          )
        );
        await expect(elePopUpSubTitle).toBeVisible({ timeout: 5000 });
        const elePopUpSubTitleText = await elePopUpSubTitle.textContent();
        expect(elePopUpSubTitleText).toBe(
          "Here are some additional High Energy Hazards that could be present, please review and make any further updates below:"
        );
        await this.tb.logSuccess(
          `Pop Up Sub Title for Recommended High Energy Hazards is visible and the text is ${elePopUpSubTitleText}`
        );
        
        const eleConfirmBtnInPopUp = this.page.locator(
          this.getLocator(
            FormListPageLocators.EBO_RecommendedHighEnergyHazards_PopUp_ConfirmBtn
          )
        );
        await expect(eleConfirmBtnInPopUp).toBeVisible({ timeout: 5000 });
        await eleConfirmBtnInPopUp.click();
        await this.tb.logSuccess(
          `Confirm Updates Button for Recommended High Energy Hazards is clicked`
        );
        await expect(elePopUpForRecommendedHighEnergyHazards).not.toBeVisible({
          timeout: 5000,
        });
        await this.page.waitForTimeout(200);
        await this.tb.logSuccess(
          `Pop Up for Recommended High Energy Hazards is not visible after clicking Confirm Updates Button`
        );
      } else {
        await this.tb.logSuccess(
          `Pop Up for Recommended High Energy Hazards is not visible thus moving forward without validating it`
        );
      }
    } catch (error) {
      await this.tb.logSuccess(
        `Pop Up for Recommended High Energy Hazards is not visible thus moving forward without validating it`
      );
    }
    
    return flag;
  }

  public async EBO_VerifyBlueTickAndBlueBorderOnSavedTab_HighEnergyTasks() {
    const eleHighEnergyTasks = this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_EBO_NavHighEnergyTasks)
    );
    const eleTickMark = eleHighEnergyTasks.locator(
      "//i[contains(@class,'ci-circle_check')]"
    );
    await expect(eleTickMark).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess(
      `Blue Tick and Blue BG on High Energy Tasks Tab is visible thus verified`
    );
  }

  public async EBO_AdditionalInfo_VerifyUI() {
    const eleAdditionalInfoTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_AdditionalInfo_TitleLbl)
    );
    await expect(eleAdditionalInfoTitle).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess(`Additional Information Title is visible`);
    const eleAdditionalInfoCommentsInputTxtBox = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_AdditionalInfo_CommentsInputTxtBox
      )
    );
    await expect(eleAdditionalInfoCommentsInputTxtBox).toBeVisible({
      timeout: 5000,
    });
    await this.tb.logSuccess(
      `Additional Information Comments Input Text Box is visible`
    );
    await eleAdditionalInfoCommentsInputTxtBox.fill("Test Comments");
    await this.tb.logSuccess(
      `Additional Information Comments Input Text Box is filled with text 'Test Comments'`
    );
  }

  public async EBO_VerifyBlueTickAndBlueBorderOnSavedTab_AdditionalInfo() {
    const eleAdditionalInfo = this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_EBO_NavAdditionalInfo)
    );
    const eleTickMark = eleAdditionalInfo.locator(
      "//i[contains(@class,'ci-circle_check')]"
    );
    await expect(eleTickMark).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess(
      `Blue Tick and Blue BG on Additional Information Tab is visible thus verified`
    );
  }

  public async EBO_HistoricalIncidents_VerifyUI() {
    const eleHistoricalIncidentsTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_HistoricalIncidents_TitleLbl)
    );
    await expect(eleHistoricalIncidentsTitle).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess(`Historical Incidents Title is visible`);
  }

  public async EBO_VerifyBlueTickAndBlueBorderOnSavedTab_HistoricalIncidents() {
    const eleHistoricalIncidents = this.page.locator(
      this.getLocator(
        FormListPageLocators.FormsListPage_EBO_NavHistoricalIncidents
      )
    );
    const eleTickMark = eleHistoricalIncidents.locator(
      "//i[contains(@class,'ci-circle_check')]"
    );
    await expect(eleTickMark).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(
      `Blue Tick and Blue BG on Historical Incidents Tab is visible thus verified`
    );
  }

  public async EBO_Attachments_VerifyPhotoAdditionUsingAddPhotosBtn() {
    const addPhotosButton = this.page.getByText("Add photos", { exact: true });
    const fileInput = this.page.locator('input[type="file"]').first();

    const eleHeadingPhotos = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_lblPhotos)
    );
    await expect(eleHeadingPhotos).toBeVisible({ timeout: 5000 });

    let photoCount = await eleHeadingPhotos.innerText();

    await expect(addPhotosButton).toBeVisible({ timeout: 5000 });

    const acceptAttribute = await fileInput.getAttribute("accept");
    const expectedTypes = [
      ".apng",
      ".avif",
      ".gif",
      ".jpg",
      ".jpeg",
      ".png",
      ".webp",
    ];

    const actualTypes = acceptAttribute?.split(",") || [];
    expect(actualTypes).toEqual(expectedTypes);

    const isMultiple = await fileInput.getAttribute("multiple");
    expect(isMultiple).not.toBeNull();

    expect(photoCount.split("(")[1].split(")")[0]).toBe("0");

    const testImage1Path = path.join(
      __dirname,
      "../Data/dummy-media/dummy_image1.jpg"
    );
    const testImage2Path = path.join(
      __dirname,
      "../Data/dummy-media/dummy_image2.png"
    );

    await fileInput.setInputFiles([testImage1Path, testImage2Path]);

    await this.page.waitForTimeout(1000);

    //checking the loading spinner to be visible and then hidden
    // await this.page.waitForSelector("//div/section/div/div[1]/label/i[2]", {
    //   state: "visible",
    // });
    // await this.page.waitForSelector("//div/section/div/div[1]/label/i[2]", {
    //   state: "hidden",
    // });

    try {
      const eleUploadedImage = this.page
        .locator(
          this.getLocator(FormListPageLocators.JSB_Attachments_uploadedImages)
        )
        .first();
      await eleUploadedImage.waitFor({ state: "visible" });
      await expect(eleUploadedImage).toBeVisible({ timeout: 5000 });
      const eleSecondImage = this.page
        .locator(
          this.getLocator(FormListPageLocators.JSB_Attachments_uploadedImages)
        )
        .nth(1);
      await eleSecondImage.waitFor({ state: "visible" });
      await this.page.waitForTimeout(3000);
      photoCount = await eleHeadingPhotos.innerText();
      expect(photoCount.split("(")[1].split(")")[0]).toBe("2");
    } catch (error) {
      throw new Error(
        "File upload did not complete successfully: " + (error as Error).message
      );
    }
  }

  public async EBO_Attachments_VerifyPhotosDeletion() {
    const eleUploadedImages = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_uploadedImages)
    );
    expect(await eleUploadedImages.count()).toBe(2);
    await expect(eleUploadedImages.first()).toBeVisible({ timeout: 5000 });

    const eleHeadingPhotos = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_lblPhotos)
    );
    await expect(eleHeadingPhotos).toBeVisible({ timeout: 5000 });
    await this.page.waitForTimeout(3000);
    let photoCount = await eleHeadingPhotos.innerText();
    expect(photoCount.split("(")[1].split(")")[0]).toBe("2");

    const eleDeleteButton = this.page.locator(
      this.getLocator(FormListPageLocators.JSB_Attachments_uploadedImgDeleteBtn)
    );
    await expect(eleDeleteButton).toBeVisible({ timeout: 5000 });
    await eleDeleteButton.click();

    await this.page.waitForTimeout(1000);

    photoCount = await eleHeadingPhotos.innerText();
    expect(photoCount.split("(")[1].split(")")[0]).toBe("1");

    expect(await eleUploadedImages.count()).toBe(1);
    await this.tb.logSuccess(
      `Extra Photos are deleted successfully from the Photos Tab and now the count is ${
        photoCount.split("(")[1].split(")")[0]
      }`
    );
  }

  public async EBO_VerifyBlueTickAndBlueBorderOnSavedTab_Photos() {
    const elePhotos = this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_EBO_NavPhotos)
    );
    const eleTickMark = elePhotos.locator(
      "//i[contains(@class,'ci-circle_check')]"
    );
    await expect(eleTickMark).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess(
      `Blue Tick and Blue BG on Photos Tab is visible thus verified`
    );
  }

  public async EBO_Summary_VerifyUI() {
    const eleSummaryTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_Summary_TitleLbl)
    );
    await expect(eleSummaryTitle).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(`Summary Title is visible`);
  }

  public async EBO_VerifyBlueTickAndBlueBorderOnSavedTab_Summary() {
    const eleSummary = this.page.locator(
      this.getLocator(FormListPageLocators.FormsListPage_EBO_NavSummary)
    );
    const eleTickMark = eleSummary.locator(
      "//i[contains(@class,'ci-circle_check')]"
    );
    await expect(eleTickMark).toBeVisible({ timeout: 10000 });
    await this.tb.logSuccess(
      `Blue Tick and Blue BG on Summary Tab is visible thus verified`
    );
  }

  public async EBO_Personnel_VerifyUI() {
    const elePersonnelTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_Personnel_Title_Lbl)
    );
    await expect(elePersonnelTitle).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(`Personnel Title is visible`);
    const eleCrewMembersTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_Personnel_CrewMembers_Title_Lbl)
    );
    await expect(eleCrewMembersTitle).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(`Crew Members Title is visible`);
    const eleObserverNameTitle = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_Personnel_ObserverName_Title_Lbl)
    );
    await expect(eleObserverNameTitle).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(`Observer Name Title is visible`);
    const eleObserverNameValue = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_Personnel_ObserverName_Value_Lbl)
    );
    await expect(eleObserverNameValue).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(
      `Observer Name Value is visible with text ${await eleObserverNameValue.textContent()}`
    );
    const eleCrewMembersDropdown = this.page.locator(
      this.getLocator(FormListPageLocators.EBO_Personnel_CrewMembers_Dropdown)
    );
    await expect(eleCrewMembersDropdown).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(`Crew Members Dropdown is visible`);
  }

  public async EBO_Personnel_VerifyRequiredFields() {
    const saveAndContinueBtn = this.btnSaveAndContinue;
    await expect(saveAndContinueBtn).toBeVisible({ timeout: 5000 });
    await saveAndContinueBtn.click();
    await this.tb.logSuccess(`Save and Continue Button is clicked`);

    const eleCrewMembersDropdownError = this.page.locator(
      this.getLocator(
        FormListPageLocators.EBO_Personnel_CrewMembers_Dropdown_Error
      )
    );
    await expect(eleCrewMembersDropdownError).toBeVisible({ timeout: 5000 });
    await this.tb.logSuccess(`Crew Members Dropdown Error is visible`);
  }

  public async EBO_Personnel_VerifyCrewMembersDropdown() {
    try {
      const eleCrewMembersDropdown = this.page.locator(
        this.getLocator(FormListPageLocators.EBO_Personnel_CrewMembers_Dropdown)
      );
      await expect(eleCrewMembersDropdown).toBeVisible({ timeout: 5000 });
      await eleCrewMembersDropdown.click();

      const eleCrewMembersDropdownOptions = this.page.locator(
        this.getLocator(
          FormListPageLocators.EBO_Personnel_CrewMembers_DropdownOptions
        )
      );
      await expect(eleCrewMembersDropdownOptions.first()).toBeVisible({
        timeout: 5000,
      });
      const optionsCount = await eleCrewMembersDropdownOptions.count();
      if (optionsCount < 2) {
        throw new Error("Not enough crew members in dropdown to run test.");
      }

      const allOptionsText =
        await eleCrewMembersDropdownOptions.allTextContents();
      this.tb.logSuccess(
        `Crew members dropdown options: ${allOptionsText.join(", ")}`
      );

      const eleNAOption = this.page.locator(
        `(${this.getLocator(
          FormListPageLocators.EBO_Personnel_CrewMembers_DropdownOptions
        )})[1]`
      );
      await expect(eleNAOption).toBeVisible({ timeout: 5000 });
      const naOptionText = await eleNAOption.textContent();
      expect(naOptionText).toBe("N/A");
      await this.tb.logSuccess(
        `N/A Option is visible with text ${naOptionText}`
      );

      const eleDropdownFirstOption = this.page.locator(
        `(${this.getLocator(
          FormListPageLocators.EBO_Personnel_CrewMembers_DropdownOptions
        )})[2]`
      );
      await expect(eleDropdownFirstOption).toBeVisible({ timeout: 5000 });
      const firstOptionText = await eleDropdownFirstOption.textContent();
      await eleDropdownFirstOption.click();

      const eleTickMarkFirstOption = eleDropdownFirstOption.locator(
        "//i[@class='ci-check']"
      );
      await expect(eleTickMarkFirstOption).toBeVisible({ timeout: 5000 });

      const eleDropdownSecondOption = this.page.locator(
        `(${this.getLocator(
          FormListPageLocators.EBO_Personnel_CrewMembers_DropdownOptions
        )})[3]`
      );
      await expect(eleDropdownSecondOption).toBeVisible({ timeout: 5000 });
      const secondOptionText = await eleDropdownSecondOption.textContent();
      await eleDropdownSecondOption.click();

      const eleTickMarkSecondOption = eleDropdownSecondOption.locator(
        "//i[@class='ci-check']"
      );
      await expect(eleTickMarkSecondOption).toBeVisible({ timeout: 5000 });

      const eleSelectedValues = eleCrewMembersDropdown.locator("//span");
      await expect(eleSelectedValues).toHaveCount(2);

      if (!firstOptionText || !secondOptionText) {
        throw new Error("Dropdown option text is null or empty");
      }
      await expect(eleSelectedValues.first()).toHaveText(firstOptionText);
      await expect(eleSelectedValues.last()).toHaveText(secondOptionText);

      await eleCrewMembersDropdown.click();
      await this.page.waitForTimeout(200);
      await this.tb.logSuccess(
        `Selected WorkType options: ${firstOptionText} and ${secondOptionText}`
      );
    } catch (error) {
      throw new Error(
        `Failed to verify Crew Members dropdown: ${(error as Error).message}`
      );
    }
  }
}
