import { Page, Locator, expect } from "@playwright/test";
import TestBase, { getProjectName } from "../Util/TestBase";
import { getEnvironmentData, CURRENT_ENV } from "../Data/envConfig";
import { Environment } from "../types/interfaces";
import { MapPageLocators } from "../Locators/MapPageLocators";

export default class MapPage {
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

  public async validateMapPageUI() {
    await this.tb.testStep("Validate Map page Search Aside UI", async () => {
      const SearchBoxlocator = this.page.locator(
        this.getLocator(MapPageLocators.Map_txtSearchInput)
      );
      await expect(SearchBoxlocator).toBeVisible({ timeout: 15000 });

      const LocationAsideBarlocator = this.page.locator(
        this.getLocator(MapPageLocators.Map_LocationAsideBar)
      );
      await expect(LocationAsideBarlocator).toBeVisible({ timeout: 15000 });
    });

    await this.tb.testStep(
      "Validate Search Results based off location",
      async () => {
        const noWorkOrderFoundMsg = this.page.locator(
          this.getLocator(MapPageLocators.Map_NoWorkOrderFoundMsg_Lbl)
        );
        const locationCards = this.page.locator(
          this.getLocator(MapPageLocators.Map_LocationCardsInSearchResultsAside)
        );

        try {
          await this.page.waitForTimeout(3000);
          const isNoWorkOrderMsgVisible = await noWorkOrderFoundMsg.isVisible();

          if (isNoWorkOrderMsgVisible) {
            await expect(noWorkOrderFoundMsg).toBeVisible({ timeout: 15000 });

            const resultsCountLbl = this.page.locator(
              this.getLocator(MapPageLocators.Map_ResultsCountLbl)
            );
            const resultsCountLblText = await resultsCountLbl.textContent();
            expect(resultsCountLblText).toBe("0 results");
            await this.tb.captureScreenshot(
              this.page,
              "Map_No_Work_Order_Found_Msg"
            );
            await this.tb.logSuccess(
              "No work orders found message is displayed as expected"
            );
          } else {
            await expect(locationCards).toBeVisible({ timeout: 15000 });
            const cardCount = await locationCards.count();
            const resultsCountLbl = this.page.locator(
              this.getLocator(MapPageLocators.Map_ResultsCountLbl)
            );
            const resultsCountLblText = await resultsCountLbl.textContent();
            expect(resultsCountLblText).toBe(`${cardCount} results`);
            await this.tb.captureScreenshot(
              this.page,
              "Map_Search_Results_After_Searching_Street"
            );
            await this.tb.logSuccess(`Found ${cardCount} location cards`);
          }
        } catch (error) {
          await this.tb.logFailure(
            "Error validating location cards or no work orders message"
          );
          throw error;
        }
      }
    );

    await this.tb.testStep("Validate Map Box UI", async () => {
      const mapBoxCanvas = this.page.locator(
        this.getLocator(MapPageLocators.Map_MapBoxCanvas)
      );
      await expect(mapBoxCanvas).toBeVisible({ timeout: 15000 });

      const mapBoxZoomInBtn = this.page.locator(
        this.getLocator(MapPageLocators.Map_MapBoxZoomInBtn)
      );
      await expect(mapBoxZoomInBtn).toBeVisible({ timeout: 15000 });

      const mapBoxZoomOutBtn = this.page.locator(
        this.getLocator(MapPageLocators.Map_MapBoxZoomOutBtn)
      );
      await expect(mapBoxZoomOutBtn).toBeVisible({ timeout: 15000 });

      const mapBoxFindMyLocationBtn = this.page.locator(
        this.getLocator(MapPageLocators.Map_MapBoxFindMyLocationBtn)
      );
      await expect(mapBoxFindMyLocationBtn).toBeVisible({ timeout: 15000 });

      const mapBoxLocationRiskBox = this.page.locator(
        this.getLocator(MapPageLocators.Map_MapBoxLocationRiskBox)
      );
      await expect(mapBoxLocationRiskBox).toBeVisible({ timeout: 15000 });

      const mapBoxLocationRiskBoxHideUnhideBtn = this.page.locator(
        this.getLocator(MapPageLocators.Map_LocationRiskBox_HideUnhideBtn)
      );
      await expect(mapBoxLocationRiskBoxHideUnhideBtn).toBeVisible({
        timeout: 15000,
      });

      await this.tb.testStep(
        "Validate Map Box Location Risk Box UI",
        async () => {
          const mapBoxLocationRiskBox = this.page.locator(
            this.getLocator(MapPageLocators.Map_MapBoxLocationRiskBox)
          );
          await expect(mapBoxLocationRiskBox).toBeVisible({ timeout: 15000 });

          const mapBoxLocationRiskBoxLbls = this.page.locator(
            this.getLocator(MapPageLocators.Map_LocationRisks_Lbls)
          );

          const mapBoxLocationRiskBoxLblsCount =
            await mapBoxLocationRiskBoxLbls.count();

          await this.tb.logSuccess(
            `Found ${mapBoxLocationRiskBoxLblsCount} location risk box labels`
          );

          const mapBoxLocationRiskBoxLblsText =
            await mapBoxLocationRiskBoxLbls.allTextContents();
          const labels = mapBoxLocationRiskBoxLblsText.join(", ");
          await this.tb.logSuccess(`Location risk box labels text: ${labels}`);
        }
      );

      await this.tb.testStep(
        "Validate Map Box Location Risk Box Hide/Unhide Button",
        async () => {
          const mapBoxLocationRiskBoxHideUnhideBtn = this.page.locator(
            this.getLocator(MapPageLocators.Map_LocationRiskBox_HideUnhideBtn)
          );
          await expect(mapBoxLocationRiskBoxHideUnhideBtn).toBeVisible({
            timeout: 15000,
          });

          await mapBoxLocationRiskBoxHideUnhideBtn.click();
          await this.page.waitForTimeout(200);

          const mapBoxLocationRiskBoxLbls = this.page.locator(
            this.getLocator(MapPageLocators.Map_LocationRisks_Lbls)
          );
          await expect(mapBoxLocationRiskBoxLbls).not.toBeVisible({
            timeout: 15000,
          });
        }
      );

      if(this.projectName === "iPad Mini") {
        await this.tb.testStep(
            "Validate Map Box Manage Map Layers Button",
            async () => {
              const mapBoxManageMapLayersBtn = this.page.locator(
                this.getLocator(MapPageLocators.Map_ManageMapLayersBtn)
              );
              await expect(mapBoxManageMapLayersBtn).toBeVisible({
                timeout: 15000,
              });
    
              await mapBoxManageMapLayersBtn.click();
              await this.page.waitForTimeout(200);
    
              const mapBoxManageMapLayersDropdown = this.page.locator(
                this.getLocator(MapPageLocators.Map_ManageMapLayers_Dropdown)
              );
              await expect(mapBoxManageMapLayersDropdown).toBeVisible({
                timeout: 15000,
              });
    
              const mapBoxManageMapLayersShowLegendLbl = this.page.locator(
                this.getLocator(MapPageLocators.Map_ManageMapLayers_ShowLegendLbl)
              );
              await expect(mapBoxManageMapLayersShowLegendLbl).toBeVisible({
                timeout: 15000,
              });
    
              const mapBoxManageMapLayersShowLegendBtn = this.page.locator(
                this.getLocator(MapPageLocators.Map_ManageMapLayers_ShowLegendBtn)
              );
              await expect(mapBoxManageMapLayersShowLegendBtn).toBeVisible({
                timeout: 15000,
              });
    
              const mapBoxManageMapLayersShowSatteliteLbl = this.page.locator(
                this.getLocator(
                  MapPageLocators.Map_ManageMapLayers_ShowSatelliteLbl
                )
              );
              await expect(mapBoxManageMapLayersShowSatteliteLbl).toBeVisible({
                timeout: 15000,
              });
    
              const mapBoxManageMapLayersShowSatteliteBtn = this.page.locator(
                this.getLocator(
                  MapPageLocators.Map_ManageMapLayers_ShowSatelliteBtn
                )
              );
              await expect(mapBoxManageMapLayersShowSatteliteBtn).toBeVisible({
                timeout: 15000,
              });
    
              await mapBoxManageMapLayersShowLegendBtn.click();
              await this.page.waitForTimeout(200);
    
              const isLegendChecked =
                await mapBoxManageMapLayersShowLegendBtn.getAttribute(
                  "aria-checked"
                );
              expect(isLegendChecked).toBe("false");
              await this.tb.logSuccess(`Legend is checked: ${isLegendChecked}`);
    
              const locationRiskBox = this.page.locator(
                this.getLocator(MapPageLocators.Map_MapBoxLocationRiskBox)
              );
              await expect(locationRiskBox).not.toBeVisible({ timeout: 15000 });
    
              await mapBoxManageMapLayersShowLegendBtn.click();
              await this.page.waitForTimeout(200);
    
              await expect(locationRiskBox).toBeVisible({ timeout: 15000 });
    
              await mapBoxManageMapLayersBtn.click();
              await this.page.waitForTimeout(200);
    
              await expect(mapBoxManageMapLayersDropdown).not.toBeVisible({
                timeout: 15000,
              });
            }
          );
      }
    });
  }

  public async validateMapSearchFunctionality() {
    await this.tb.testStep("Validate Map Search Functionality", async () => {
      const mapSearchInput = this.page.locator(
        this.getLocator(MapPageLocators.Map_txtSearchInput)
      );
      await expect(mapSearchInput).toBeVisible({ timeout: 15000 });

      await mapSearchInput.fill("Street");

      const crossBtnSearchInput = this.page.locator(
        this.getLocator(MapPageLocators.Map_CrossBtnSearchInput)
      );
      await expect(crossBtnSearchInput).toBeVisible({ timeout: 15000 });

      await this.page.keyboard.press("Enter");

      await this.page.waitForTimeout(3000);

      await this.tb.captureScreenshot(
        this.page,
        "Map_Search_Results_After_Searching_Street"
      );

      const locationCards = this.page.locator(
        this.getLocator(MapPageLocators.Map_LocationCardsInSearchResultsAside)
      );

      const locationCardsCount = await locationCards.count();
      await this.tb.logSuccess(
        `Found ${locationCardsCount} location cards after searching 'Street'`
      );

      if (locationCardsCount > 0) {
        const locationCardFirstResult = locationCards.first();
        const locationCardFirstResultText =
          await locationCardFirstResult.textContent();
        await this.tb.logSuccess(
          `Location card first result text: ${locationCardFirstResultText}`
        );
      } else {
        const noWorkOrderFoundMsg = this.page.locator(
          this.getLocator(MapPageLocators.Map_NoWorkOrderFoundMsg_Lbl)
        );
        await expect(noWorkOrderFoundMsg).toBeVisible({ timeout: 15000 });

        await this.tb.logMessage(
          "No location cards found after searching 'Street'"
        );
      }

      await this.tb.testStep("Clear Map Search Input", async () => {
        await crossBtnSearchInput.click();
      });
      await this.page.waitForTimeout(200);
      const mapSearchInputValue = await mapSearchInput.inputValue();
      expect(mapSearchInputValue).toBe("");
      await this.tb.logSuccess(`Map search input value: ${mapSearchInputValue} found empty as expected`);
      await this.page.waitForTimeout(3000);

      await this.tb.captureScreenshot(
        this.page,
        "Map_Search_Results_After_Clearing_Search"
      );

      await this.tb.logSuccess(
        "Map search functionality is working as expected"
      );
    });
  }
}
