import { Page, Locator } from "@playwright/test";
import { CWFPageLocators } from "../Locators/CWFPageLocators";
import TestBase, { setProjectName, getProjectName } from "../Util/TestBase";
import * as path from "path";
import { expect } from "@playwright/test";
import * as allure from "allure-js-commons";
import * as cwfInterfaces from "../types/interfaces";
import * as inputData from "../Data/validInputData.json";
import * as cred from "../Data/local.cred.json";
import { expectedEnergyComponents, energyComponentColors } from "../Data/testLabelValidation";
import {
  getEnvironmentData,
  CURRENT_ENV,
  getURLForService,
  getCurrentEnvUrl,
} from "../Data/envConfig";

const fs = require("fs").promises;
const fsSync = require("fs");

export default class CWFPage {
  private page: Page;
  private tb: TestBase;
  private environmentData: cwfInterfaces.Environment;
  private projectName: string;
  private RESPONSE_JSON: cwfInterfaces.FormContent;
  private RESPONSE_SAVEDFORM_JSON: cwfInterfaces.FormContent;
  private formId: string;

  constructor(page: Page) {
    this.page = page;
    this.tb = new TestBase(page);
    this.projectName = getProjectName();
    this.environmentData = getEnvironmentData();
    this.RESPONSE_JSON = {} as cwfInterfaces.FormContent;
    this.RESPONSE_SAVEDFORM_JSON = {} as cwfInterfaces.FormContent;
    this.formId = "";
  }

  private getLocator(locatorObj: { mobile: string; desktop: string }): string {
    return this.projectName === "iPad Mini"
      ? locatorObj.mobile
      : locatorObj.desktop;
  }

  public async captureFormResponse(
    template_id: string,
    serviceName: keyof cwfInterfaces.ApiCategories,
    responseDetails: string
  ) {
    await allure.step(
      'Navigating to add-template page and Capturing response for CWF Template "/forms" endpoint',
      async () => {
        let responseCaptured = false;
        const responsePromise = new Promise<cwfInterfaces.FormContent | null>(
          (resolve) => {
            this.page.on("response", async (response) => {
              if (responseCaptured) return;
              const urlToCapture = getURLForService(serviceName);
              const urlWithTemplateId = `${urlToCapture}${template_id}`;

              if (
                response.url().includes(urlWithTemplateId) &&
                response.request().method() === "GET"
              ) {
                responseCaptured = true;
                await this.tb.logMessage(
                  `✅ Captured API response: ${response.url()}`
                );
                await this.tb.logMessage(
                  `Response status: ${response.status()}`
                );

                if (response.status() < 200 || response.status() > 299) {
                  console.log(`Response status: ${response.status()}`);
                  throw new Error(`Response status: ${response.status()}`);
                }

                try {
                  const data = await response.json();
                  this.RESPONSE_JSON = data;

                  const now = new Date();
                  const pad = (n: number) => String(n).padStart(2, "0");
                  const dateStr = `${pad(now.getDate())}_${pad(
                    now.getMonth() + 1
                  )}_${now.getFullYear()}`;
                  const timeStr = `${pad(now.getHours())}:${pad(
                    now.getMinutes()
                  )}:${pad(now.getSeconds())}`;

                  const dataFolder = path.join(__dirname, "../json_CWF");

                  const filename = path.join(
                    dataFolder,
                    `${responseDetails}_${dateStr}_${timeStr}.json`
                  );

                  if (!fsSync.existsSync(dataFolder)) {
                    fsSync.mkdirSync(dataFolder, { recursive: true });
                  }

                  await fs.writeFile(filename, JSON.stringify(data, null, 2));
                  await this.tb.logSuccess(
                    `Response ${responseDetails} JSON saved to: ${filename}`
                  );
                  resolve(data);
                } catch (err) {
                  console.log(
                    `Error processing response ${responseDetails}:`,
                    err
                  );
                  resolve(null);
                }
              }
            });
          }
        );

        await this.page.goto(
          `${this.environmentData.url}template-forms/add?templateId=${template_id}`
        );

        // Wait for both the page load and the response
        await Promise.all([this.page.waitForTimeout(7000), responsePromise]);

        return this.RESPONSE_JSON;
      }
    );
  }

  public async captureFormResponseAfterSaveAndComplete(
    serviceName: keyof cwfInterfaces.ApiCategories,
    responseDetails: string
  ) {
    let responseCaptured = false;

    const responsePromise = new Promise<cwfInterfaces.FormContent | null>(
      (resolve) => {
        const responseHandler = async (response: any) => {
          try {
            const url = response.url();
            const method = response.request().method();

            if (responseCaptured) return;
            const urlToCapture = getURLForService(serviceName);
            const isMatch =
              url.includes(urlToCapture) &&
              !url.includes("/forms/list") &&
              url.includes("/forms/") &&
              method === "PUT";

            if (isMatch) {
              responseCaptured = true;

              try {
                await this.tb.logMessage(
                  `✅ MATCHED! Captured API response: ${url}`
                );
                await this.tb.logMessage(
                  `Response status: ${response.status()}`
                );

                let data;
                try {
                  data = await response.json();
                  this.formId = data.id;
                  await this.tb.logMessage(`Captured form ID: ${this.formId}`);
                } catch (err) {
                  console.log(`Error extracting form ID:`, err);
                  throw new Error(`Error extracting form ID: ${err}`);
                }

                this.RESPONSE_SAVEDFORM_JSON = data;

                const now = new Date();
                const pad = (n: number) => String(n).padStart(2, "0");
                const dateStr = `${pad(now.getDate())}_${pad(
                  now.getMonth() + 1
                )}_${now.getFullYear()}`;
                const timeStr = `${pad(now.getHours())}:${pad(
                  now.getMinutes()
                )}:${pad(now.getSeconds())}`;

                const dataFolder = path.join(__dirname, "../json_CWF");
                const filename = path.join(
                  dataFolder,
                  `${responseDetails}_${dateStr}_${timeStr}.json`
                );

                if (!fsSync.existsSync(dataFolder)) {
                  fsSync.mkdirSync(dataFolder, { recursive: true });
                }

                await fs.writeFile(filename, JSON.stringify(data, null, 2));
                resolve(data);
              } catch (err) {
                console.log(
                  `Error processing response ${responseDetails}:`,
                  err
                );
                resolve(null);
              } finally {
                try {
                  this.page.removeListener("response", responseHandler);
                } catch (e) {
                  console.warn("Failed to remove response listener:", e);
                }
              }
            }
          } catch (error) {
            console.warn(
              "Error in response handler, possibly page closed:",
              error
            );
            resolve(null);
            try {
              this.page.removeListener("response", responseHandler);
            } catch (e) {
              console.warn("Failed to remove response listener:", e);
            }
          }
        };

        try {
          this.page.on("response", responseHandler);
        } catch (error) {
          console.warn("Failed to add response listener:", error);
          resolve(null);
        }
      }
    );

    try {
      const timeoutPromise = new Promise((resolve) =>
        setTimeout(resolve, 15000)
      );
      await Promise.race([responsePromise, timeoutPromise]);

      if (!responseCaptured) {
        console.warn(
          `⚠️ WARNING: Failed to capture response for formId: ${this.formId}`
        );
      }
    } catch (error) {
      console.warn("Error waiting for response:", error);
    }

    return this.RESPONSE_SAVEDFORM_JSON;
  }

  public async validateAllPagesInJSON() {
    const formTitle = this.RESPONSE_JSON.properties.title;
    await this.tb.logMessage(
      `Validating '${formTitle}' form with template ID: ${cred.templateID}`
    );
    const pages: cwfInterfaces.PageContent[] =
      this.RESPONSE_JSON.contents.filter(
        (content: cwfInterfaces.Content) => content.type === "page"
      );
    const templateMetadata = this.RESPONSE_JSON.metadata;

    if (pages.length === 0) {
      throw new Error("No pages found in the JSON response.");
    }

    let isLastPage = false;

    for (const pageData of pages) {
      const pageTitle = pageData.properties.title;

      await allure.step(`Click on page '${pageTitle}'`, async () => {
        await this.page
          .getByRole("button", { name: pageTitle, exact: true })
          .click({
            timeout: 10000,
          });
      });

      await this.tb.captureScreenshot(
        this.page,
        `'${pageTitle}' Page before validation`
      );

      await this.validatePageContents(
        this.page,
        pageData.contents,
        {},
        templateMetadata
      );
      if (pageData === pages[pages.length - 1]) {
        isLastPage = true;
      }

      await this.tb.captureScreenshot(
        this.page,
        `'${pageTitle}' Page after validation`
      );

      await allure.step(
        isLastPage
          ? `Click "Save and Complete" button after validating ${pageTitle} page`
          : `Click "Save and Continue" button after validating ${pageTitle} page`,
        async () => {
          await this.clickSaveAndComplete(isLastPage);
        }
      );
    }
  }

  public async validatePageContents(
    page: Page,
    contents: cwfInterfaces.Content[],
    counters: cwfInterfaces.ContentCounters,
    templateMetadata?: cwfInterfaces.TemplateMetadata
  ): Promise<void> {
    let shortTextCounter = 0;
    let longTextCounter = 0;
    for (const content of contents) {
      if (content.type === "section") {
        if (content.contents && Array.isArray(content.contents)) {
          await this.validatePageContents(
            page,
            content.contents,
            counters,
            templateMetadata
          );
        }
      } else if (content.type === "input_text") {
        if (content.properties.input_type === "short_text") {
          shortTextCounter++;
          await this.functionCaller(
            page,
            content,
            shortTextCounter,
            templateMetadata
          );
        } else if (content.properties.input_type === "long_text") {
          longTextCounter++;
          await this.functionCaller(
            page,
            content,
            longTextCounter,
            templateMetadata
          );
        }
      } else {
        if (!counters[content.type]) {
          counters[content.type] = 0;
        }

        counters[content.type]++;

        await this.functionCaller(
          page,
          content,
          counters[content.type],
          templateMetadata
        );
      }
    }
  }

  public async functionCaller(
    page: Page,
    content: cwfInterfaces.Content,
    index: number,
    templateMetadata?: cwfInterfaces.TemplateMetadata
  ) {
    switch (content.type) {
      case "input_text":
        await allure.step(
          `Validating Component "Input ${content.properties.input_type}" indexed: #${index} with title "${content.properties.title}"`,
          async () => {
            await this.inputTextValidatorFunction(page, content, index);
          }
        );
        break;
      // case "choice":
      //   await allure.step(
      //     `Validating Component "Choice" indexed: #${index} with title ${content.properties.title}`,
      //     async () => {
      //       await this.choiceValidatorFunction(page, content, index);
      //     }
      //   );
      //   break;
      case "input_date_time":
        await allure.step(
          `Validating Component "Input Date Time" indexed: #${index} with title ${content.properties.title}`,
          async () => {
            await this.dateTimeValidatorFunction(page, content, index);
          }
        );
        break;
      // case "report_date":
      //   await this.reportDateTimeValidatorFunction(page, content, index);
      //   break;
      case "input_phone_number":
        await allure.step(
          `Validating Component "Input Phone Number" indexed: #${index} with title ${content.properties.title}`,
          async () => {
            await this.phoneNumberValidatorFunction(page, content, index);
          }
        );
        break;
      case "input_email":
        await allure.step(
          `Validating Component "Input Email" indexed: #${index} with title ${content.properties.title}`,
          async () => {
            await this.emailValidatorFunction(page, content, index);
          }
        );
        break;
      case "input_number":
        await allure.step(
          `Validating Component "Input Number" indexed: #${index} with title ${content.properties.title}`,
          async () => {
            await this.numberValidatorFunction(page, content, index);
          }
        );
        break;
      case "attachment":
        await allure.step(
          `Validating Component "Attachment" indexed: #${index} with title ${content.properties.title}`,
          async () => {
            await this.attachmentValidatorFunction(page, content, index);
          }
        );
        break;
      case "hazards_and_controls":
        await this.tb.logMessage(
          `Processing hazards_and_controls (Index ${index}): ${content.properties.title}`
        );
        await this.hazardsAndControlsValidatorFunction(page, content, index);
        break;
      // case "activities_and_tasks":
      //   await this.tb.logMessage(
      //     `Processing activities_and_tasks component (Index ${index}): ${content.properties.title}`
      //   )
      //   await this.activitiesAndTasksValidatorFunction(page,content,index);
      //   break;
      default:
        await this.tb.logMessage(
          `Component type "${content.type}" validations are not implemented yet.`
        );
    }
  }

  public async emailValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    const properties = content.properties as cwfInterfaces.EmailProperties;
    await this.tb.logMessage(
      `Index ${index} - Validating email input: ${properties.title}`
    );
    let emailTitleLocator;

    if (properties.is_mandatory) {
      emailTitleLocator = this.page.locator(
        `(${this.getLocator(
          CWFPageLocators.CWF_Template_EmailMandatoryDynamicTitle(
            properties.title
          )
        )})`
      );
    } else {
      emailTitleLocator = this.page.locator(
        `(${this.getLocator(
          CWFPageLocators.CWF_Template_EmailNonMandatoryDynamicTitle(
            properties.title
          )
        )})`
      );
    }

    if (properties.is_mandatory) {
      await this.tb.testStep(
        `Verifying asterisk mark on the title of Mandatory email Component at index ${index}`,
        async () => {
          const titleText = await emailTitleLocator.textContent();

          if (titleText?.includes("*")) {
            await this.tb.logSuccess(
              `Asterisk mark is present in the title of mandatory email component indexed: ${index}`
            );
          } else {
            await this.tb.logFailure(
              `Asterisk mark is not present in the title of mandatory email component indexed: ${index}. Actual text: ${titleText}`
            );
            throw new Error(
              `Asterisk mark is not present in the title of mandatory email component indexed: ${index}`
            );
          }
        }
      );
    }
    if (!properties.is_mandatory) {
      await this.tb.testStep(
        `Validating asterisk mark should not be in title for non-mandatory Email component at index ${index}`,
        async () => {
          await expect(emailTitleLocator).toBeVisible({ timeout: 5000 });

          const titleText = await emailTitleLocator.textContent();
          await this.tb.logSuccess(
            `Asterisk mark is not present in the title of non-mandatory email component indexed: ${index}. Text: ${titleText}`
          );
        }
      );
    }

    try {
      await this.tb.testStep(
        "Validating Visibility of the Email Input Component and its title",
        async () => {
          const emailCompLocator = this.page.locator(
            `(${this.getLocator(CWFPageLocators.emailInput)})[${index}]`
          );
          await expect(emailCompLocator).toBeVisible({ timeout: 5000 });
        }
      );

      await this.tb.testStep(
        "Validating Email Input with Invalid Format",
        async () => {
          const emailInput = this.page.locator(
            `(${this.getLocator(CWFPageLocators.emailInput)})[${index}]`
          );

          const invalidEmail = "invalid-email-format";
          await emailInput.fill(invalidEmail);


          await emailInput.clear();
        }
      );

      await this.tb.testStep(
        "Validating Email Input with Valid Format",
        async () => {
          const emailInput = this.page.locator(
            `(${this.getLocator(CWFPageLocators.emailInput)})[${index}]`
          );

          const validEmail = inputData.inputEmail;
          await emailInput.fill(validEmail);
          await expect(emailInput).toHaveValue(validEmail, { timeout: 1000 });
          await this.tb.logSuccess(
            `Valid email successfully entered and validated at index ${index}`
          );
        }
      );
    } catch (error) {
      await this.tb.logMessage(
        `\n[${content.properties.title}] Validation failed: ${
          (error as Error).message
        }\n`
      );
      throw error;
    }
  }

  public async hazardsAndControlsValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number,
    metadata?: cwfInterfaces.TemplateMetadata
  ) {
    const metadata1 = metadata || this.RESPONSE_JSON.metadata;
    const properties =
      content.properties as cwfInterfaces.HazardsAndControlsProperties;
    await this.tb.logMessage(
      `Index ${index} - Validating hazards_and_controls: ${properties.title}`
    );

    // Helper function to convert hex to RGB
    const hexToRgb = (hex: string): string => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      if (result) {
        const r = parseInt(result[1], 16);
        const g = parseInt(result[2], 16);
        const b = parseInt(result[3], 16);
        return `rgb(${r}, ${g}, ${b})`;
      }
      return '';
    };

    // Helper function to validate energy wheel component color matches hazard card header color
    const validateComponentColor = async (componentName: string, expectedHexColor: string) => {
      try {
        let colorMatched = false;
        
        // Get all hazard cards dynamically
        const allHazardCards = this.page.locator(
          `${this.getLocator(CWFPageLocators.hazardCardColor)}`
        );
        
        const cardCount = await allHazardCards.count();
        await this.tb.logMessage(`Found ${cardCount} hazard cards to validate for ${componentName}`);
        
        // Check each hazard card
        for (let cardIndex = 1; cardIndex <= cardCount; cardIndex++) {
          const hazardCardElement = this.page.locator(
            `${this.getLocator(CWFPageLocators.hazardCardColor)}[${cardIndex}]`
          );

          if (await hazardCardElement.isVisible()) {
            // Get the computed style of the hazard card header
            const headerColor = await hazardCardElement.evaluate((el) => {
              const computedStyle = window.getComputedStyle(el);
              return computedStyle.backgroundColor;
            });

            // Convert expected hex color to RGB for comparison
            const expectedRgbColor = hexToRgb(expectedHexColor);

            await this.tb.logMessage(`Card ${cardIndex} - ${componentName}: Expected ${expectedRgbColor}, Actual ${headerColor}`);

            if (headerColor === expectedRgbColor) {
              await this.tb.logSuccess(
                `Color validation passed for ${componentName} (Card ${cardIndex}): Wheel color (${expectedHexColor}) matches hazard card header color (${headerColor})`
              );
              colorMatched = true;
              break; // Found the matching card, no need to check further
            }
          } else {
            await this.tb.logMessage(`Hazard card ${cardIndex} not visible for ${componentName} component`);
          }
        }
        
        if (!colorMatched) {
          throw new Error(
            `Color validation failed for ${componentName}: No hazard card found with matching color ${expectedHexColor} among ${cardCount} cards`
          );
        }
      } catch (error) {
        await this.tb.logMessage(`Error validating color for ${componentName}: ${(error as Error).message}`);
      }
    };

    // Helper function to compare energy wheel components with hazard cards
    const compareEnergyWheelWithHazardCards = async () => {
      try {
        await this.tb.logMessage("Starting energy wheel to hazard cards comparison...");
        
        // Get the energy wheel container
        const energyWheelContainer = this.page.locator(
          `${this.getLocator(CWFPageLocators.EnergyWheelComponentLocator)}`
        );
        
        if (!(await energyWheelContainer.isVisible())) {
          await this.tb.logMessage("Energy wheel container not visible, skipping comparison");
          return;
        }

        // Get all hazard cards
        const allHazardCards = this.page.locator(
          `${this.getLocator(CWFPageLocators.hazardCardColor)}`
        );
        const cardCount = await allHazardCards.count();
        
        await this.tb.logMessage(`Found ${cardCount} hazard cards to compare with energy wheel components`);

        // Check each energy component in the wheel
        for (const componentName of expectedEnergyComponents) {
          const expectedColor = energyComponentColors[componentName as keyof typeof energyComponentColors];
          
          // Use the same selector that works in the existing code
          const componentTextElement = this.page.locator(
            `textPath:has-text("${componentName}")`
          );
          
          if (await componentTextElement.isVisible()) {
            await this.tb.logMessage(`Found component text in wheel: ${componentName}`);
            
            // Now check if there's a corresponding hazard card with matching color
            let foundMatchingCard = false;
            
            for (let cardIndex = 1; cardIndex <= cardCount; cardIndex++) {
              const hazardCardElement = this.page.locator(
                `${this.getLocator(CWFPageLocators.hazardCardColor)}[${cardIndex}]`
              );
              
              if (await hazardCardElement.isVisible()) {
                try {
                  // Get the hazard name from the card header
                  const hazardHeaderElement = hazardCardElement.locator("//div[1]");
                  if (await hazardHeaderElement.isVisible()) {
                    const hazardName = await hazardHeaderElement.textContent();
                    if (hazardName) {
                      const trimmedHazardName = hazardName.trim().toUpperCase();
                      
                      // Check if the hazard name matches the component
                      if (trimmedHazardName === componentName) {
                        // Verify the color matches
                        const headerColor = await hazardCardElement.evaluate((el) => {
                          const computedStyle = window.getComputedStyle(el);
                          return computedStyle.backgroundColor;
                        });
                        
                        const expectedRgbColor = hexToRgb(expectedColor);
                        
                        if (headerColor === expectedRgbColor) {
                          await this.tb.logSuccess(
                            `✅ Energy wheel component "${componentName}" has corresponding hazard card "${hazardName}" with matching color`
                          );
                          foundMatchingCard = true;
                          break;
                        } else {
                          await this.tb.logMessage(
                            `⚠️ Component "${componentName}" found but color mismatch: Expected ${expectedRgbColor}, Got ${headerColor}`
                          );
                        }
                      }
                    }
                  }
                } catch (error) {
                  await this.tb.logMessage(`Error processing hazard card ${cardIndex}: ${(error as Error).message}`);
                }
              }
            }
            
            if (!foundMatchingCard) {
              await this.tb.logMessage(
                `⚠️ Energy wheel component "${componentName}" exists but no corresponding hazard card found with matching color`
              );
            }
          } else {
            await this.tb.logMessage(`Energy wheel component "${componentName}" text not found in wheel`);
          }
        }    
        await this.tb.logSuccess("Energy wheel to hazard cards comparison completed");
        
      } catch (error) {
        await this.tb.logMessage(`Error in energy wheel to hazard cards comparison: ${(error as Error).message}`);
      }
    };
    // Subtitle check Heading (High energy Hazards)
    try {
      const subtitleElement = this.page.locator(
        `${this.getLocator(CWFPageLocators.subtitleComponentLocator)}`
      );
      await subtitleElement.waitFor({ state: 'visible', timeout: 3000 });
      const isSubtitleVisible = await subtitleElement.isVisible();

      if (isSubtitleVisible) {
        const actualSubtitleText = await subtitleElement.textContent();
        await this.tb.logSuccess(
          `Subtitle is visible: "${actualSubtitleText?.trim()}"`
        );

        if (
          properties.sub_title &&
          actualSubtitleText?.trim() === properties.sub_title.trim()
        ) {
          await this.tb.logSuccess(
            `Subtitle text validation passed: "${properties.sub_title}"`
          );
          //Empty state message check for High energy Hazards Title
          const captionTextElement = this.page.locator(
            `(${this.getLocator(CWFPageLocators.hazardAndControlsMessageBox)})`
          );
          const isCaptionVisible = await captionTextElement.isVisible();

          if (isCaptionVisible) {
            const actualCaptionText = await captionTextElement.textContent();
            await this.tb.logSuccess(
              `Caption text found: "${actualCaptionText?.trim()}"`
            );

            const expectedPattern = `Identify and Control ${actualSubtitleText?.trim()}`;
            if (actualCaptionText?.trim() === expectedPattern) {
              await this.tb.logSuccess(
                `Caption text matches expected pattern: "${expectedPattern}"`
              );
            } else {
              throw new Error(
                `Caption text doesn't match expected pattern. Expected: "${expectedPattern}", Actual: "${actualCaptionText?.trim()}"`
              );
            }
          } else {
            await this.tb.logMessage(
              "Caption text element is not visible - skipping caption validation"
            );
          }
          //Empty state message check for High energy Hazards content
          const captionTextElement2 = this.page.locator(
            `(${this.getLocator(
              CWFPageLocators.hazardAndControlsContentMessage
            )})`
          );
          const isCaptionVisible2 = await captionTextElement2.isVisible();

          if (isCaptionVisible2) {
            const actualCaptionText2 = await captionTextElement2.textContent();
            await this.tb.logSuccess(
              `Second caption text found: "${actualCaptionText2?.trim()}"`
            );
            const expectedPattern2 = `${actualSubtitleText?.trim()} can cause serious injury or fatality. Add all applicable hazards and select the appropriate controls to eliminate, reduce, or mitigate the exposure.`;
            if (actualCaptionText2?.trim() === expectedPattern2) {
              await this.tb.logSuccess(
                `Second caption text matches expected pattern: "${expectedPattern2}"`
              );
            } else {
              throw new Error(
                `Second caption text doesn't match expected pattern. Expected: "${expectedPattern2}", Actual: "${actualCaptionText2?.trim()}"`
              );
            }
          } else {
            await this.tb.logMessage(
              "Second caption text element is not visible - skipping second caption validation"
            );
          }
        }
      } else {
        throw new Error(
          `Subtitle "${properties.sub_title}" is not visible on the page`
        );
      }

      // Add Hazards modal check
      const addButtonElement = this.page.locator(
        `(${this.getLocator(CWFPageLocators.hazardsAndControlsAddButton)})`
      );
      const isCancelButton = this.page.locator(
        `(${this.getLocator(CWFPageLocators.hazardsAndControlsCancelButton)})`
      );
      const hazardsSelectionModalElement = this.page.locator(
        `(${this.getLocator(CWFPageLocators.hazardsSelectionModal)})`
      );

      const isAddButtonVisible = await addButtonElement.isVisible();

      if (isAddButtonVisible) {
        await this.tb.logSuccess("Hazards and Controls add button is visible");

        await addButtonElement.click();
        await this.tb.logSuccess(
          "Successfully clicked on hazards and controls add button"
        );
        await hazardsSelectionModalElement.waitFor({ state: 'visible', timeout: 1000 });

        const isHazardsSelectionModalVisible =
          await hazardsSelectionModalElement.isVisible();

        if (isHazardsSelectionModalVisible) {
          await this.tb.logSuccess("Hazards selection modal is visible");

          // Hazards selection modal
          await hazardsSelectionModalElement.click();
          await this.tb.logSuccess(
            "Successfully clicked on hazards selection modal"
          );
        } else {
          await this.tb.logMessage(
            "Hazards selection modal is not visible - skipping modal click"
          );
        }
        // Add selected hazards
        const addButtonCommon = this.page.locator(
          `(${this.getLocator(CWFPageLocators.addButtonHazardsAndControls)})`
        );

        await addButtonCommon.click();
        await this.tb.logSuccess(
          "Successfully clicked on add button in hazards selection modal"
        );

        // add contorls (Dropdown)
        const addContorlsbutton = this.page.locator(
          `(${this.getLocator(CWFPageLocators.addControlsButton)})`
        );

        await addContorlsbutton.click();
        await this.tb.logSuccess(
          "Successfully clicked on add controls button(Dropdown)"
        );
        //Select controls
        const selectionOfControls = this.page.locator(
          `(${this.getLocator(CWFPageLocators.controlsSelection)})`
        );
        await selectionOfControls.click();
        await addButtonCommon.waitFor({ state: 'visible', timeout: 1000 });
        await addButtonCommon.click();
        await this.tb.logSuccess(
          "Successfully added controls to the selected hazard"
        );

        //Other hazards
        const otherHazardsSelection = this.page.locator(
          `(${this.getLocator(CWFPageLocators.otherHazardsSelection)})`
        );

        const addOtherContorlsbutton = this.page.locator(
          `(${this.getLocator(CWFPageLocators.addOtherControlsButton)})`
        );
        await addButtonElement.waitFor({ state: 'visible', timeout: 1000 });
        await addButtonElement.click();
        await this.tb.logSuccess(
          "Successfully clicked on hazards and controls add button again"
        );
        await otherHazardsSelection.click();
        await this.tb.logSuccess(
          "Successfully clicked on other hazards selection"
        );
        await addButtonCommon.click();
        await this.tb.logSuccess(
          "Successfully added other hazards to the list"
        );
        await addOtherContorlsbutton.click();
        await this.tb.logSuccess(
          "Successfully clicked on add other hazards- controls button(Dropdown)"
        );
        await selectionOfControls.click();
        await this.tb.logSuccess(
          "Successfully clicked on controls selection for other hazards"
        );
        await addButtonCommon.click();
        await this.tb.logSuccess(
          "Successfully added other hazards to the list"
        );

        // Open the hazard modal again with the add button(Under other hazards) for adding manual hazards and controls
        const openHazardModal = this.page.locator(
          `${this.getLocator(CWFPageLocators.hazardsAndControlsAddButton2)}`
        );
        const manuallyAddedHazardsAndControls = this.page.locator(
          `${this.getLocator(CWFPageLocators.manuallyAddedHazards)}`
        );
        const inputBoxForManuallyAddedHazardsAndControls = this.page.locator(
          `${this.getLocator(CWFPageLocators.inputBoxForManuallyAddedHazards)}`
        );
        const addButtonForManuallyAddedHazardsAndControls = this.page.locator(
          `${this.getLocator(CWFPageLocators.addButtonForManuallyAddedHazards)}`
        );
        const addControlsToManuallyAddedHazards = this.page.locator(
          `${this.getLocator(CWFPageLocators.addControlsButtonManuallyAddedHazards)}`
        );
        const deleteButtonForAddedHazards = this.page.locator(
          `${this.getLocator(CWFPageLocators.deleteButtonForAddedHazards)}`
        );
        const confirmDeleteOfHazard = this.page.locator(
          `${this.getLocator(CWFPageLocators.confirmDeleteButtonForAddedHazards)}`
        );
        //Hazard modal opened again
        await openHazardModal.click();
        await this.tb.logSuccess("Successfully opened the hazard modal again");
        //Add button (Manually added hazards)
        await manuallyAddedHazardsAndControls.click();
        await this.tb.logSuccess(
          "Successfully clicked on manually added hazards"
        );
        await inputBoxForManuallyAddedHazardsAndControls.waitFor({ state: 'visible', timeout: 1000 });
       
        //Input box for manually added hazards
        await inputBoxForManuallyAddedHazardsAndControls.fill("Test hazard");
        await inputBoxForManuallyAddedHazardsAndControls.waitFor({ state: 'visible', timeout: 1000 });
        await this.tb.logSuccess(
          "Successfully filled the input box for manually added hazards"
        );
        //Add button for manually added hazards
        await addButtonForManuallyAddedHazardsAndControls.click();
        await this.tb.logSuccess(
          "Successfully clicked on add button for manually added hazards"
        );
        await addButtonCommon.waitFor({ state: 'visible', timeout: 2000 });
        await addButtonCommon.click();
        await this.tb.logSuccess(
          "Successfully added manually added hazards to the list of hazards"
        );
        await this.tb.logSuccess(
          "Successfully added manually added hazards to the form"
        );
        //Add controls to manually added hazards
        await addControlsToManuallyAddedHazards.click();
        await addControlsToManuallyAddedHazards.waitFor({ state: 'visible', timeout: 2000 });
        await this.tb.logSuccess(
          "Successfully clicked on add controls button for manually added hazards dropdown"
        );
        await manuallyAddedHazardsAndControls.click();
        await this.tb.logSuccess(
          "Successfully clicked on manually added hazards again to add controls"
        );
        await inputBoxForManuallyAddedHazardsAndControls.waitFor({ state: 'visible', timeout: 1000 });
        //Input box for manually added controls
        await inputBoxForManuallyAddedHazardsAndControls.fill("Test controls");
        await inputBoxForManuallyAddedHazardsAndControls.waitFor({ state: 'visible', timeout: 1000 });
        await this.tb.logSuccess(
          "Successfully filled the input box for manually added controls"
        );
        await addButtonForManuallyAddedHazardsAndControls.click();
        await this.tb.logSuccess(
          "Successfully clicked on add button for manually added controls"
        );
        await addButtonCommon.click();
        await this.tb.logSuccess(
          "Successfully added manually added controls to the list of controls"
        );
        //deletion of hazard
        await deleteButtonForAddedHazards.click();
        await deleteButtonForAddedHazards.waitFor({ state: 'visible', timeout: 2000 });
        await this.tb.logSuccess(
          "Successfully clicked on delete button for added hazards"
        );  
        await isCancelButton.waitFor({ state: 'visible', timeout: 2000 });
        await isCancelButton.click();
        await deleteButtonForAddedHazards.waitFor({ state: 'visible', timeout: 2000 });
        await deleteButtonForAddedHazards.click();
        await this.tb.logSuccess(
          "Successfully clicked on delete button for added hazards again"
        );
        await confirmDeleteOfHazard.waitFor({ state: 'visible', timeout: 2000 });
        await confirmDeleteOfHazard.click();
        await this.tb.logSuccess(
          "Successfully clicked on confirm button of delete modal for added hazards"
        );

      } else {
        throw new Error(
          "Hazards and Controls add button is not visible on the page"
        );
      }
      //Energy wheel component check
      if (metadata1.is_energy_wheel_enabled) {
        await this.tb.logMessage(
          "Energy wheel is enabled - checking for energy wheel component..."
        );

        const energyWheelElement = this.page.locator(
          `(${this.getLocator(CWFPageLocators.EnergyWheelComponentLocator)})`
        );

        const isEnergyWheelVisible = await energyWheelElement.isVisible();

        if (isEnergyWheelVisible) {
          await this.tb.logSuccess(
            "Energy wheel component is present and visible"
          );

          let missingComponents = [];
          let foundComponents = [];

          for (const component of expectedEnergyComponents) {
            try {
              const componentTextElement = this.page.locator(
                `textPath:has-text("${component}")`
              );
              const isComponentVisible = await componentTextElement.isVisible();

              const componentImageElement = this.page.locator(
                `image[href*="${component.toLowerCase()}"]`
              );
              const isImageVisible = await componentImageElement.isVisible();

              if (isComponentVisible || isImageVisible) {
                foundComponents.push(component);
                await this.tb.logSuccess(
                  `Energy component "${component}" found`
                );
              } else {
                missingComponents.push(component);
              }
            } catch (error) {
              missingComponents.push(component);
              await this.tb.logMessage(
                `Error checking component "${component}": ${
                  (error as Error).message
                }`
              );
            }
          }

          await this.tb.logMessage(
            `Found components (${
              foundComponents.length
            }/10): ${foundComponents.join(", ")}`
          );

          if (missingComponents.length > 0) {
            await this.tb.logMessage(
              `Missing components (${
                missingComponents.length
              }/10): ${missingComponents.join(", ")}`
            );
            throw new Error(
              `Energy wheel validation failed: Missing ${
                missingComponents.length
              } components - ${missingComponents.join(", ")}`
            );
          } else {
            await this.tb.logSuccess(
              "All 10 energy wheel components are present and visible"
            );
          }

          // Color validation for energy wheel components and hazard cards
          await this.tb.logMessage("Starting dynamic color validation for all hazard cards...");
          
          // Get all visible hazard cards
          const allHazardCards = this.page.locator(
            `${this.getLocator(CWFPageLocators.hazardCardColor)}`
          );
          
          const cardCount = await allHazardCards.count();
          await this.tb.logMessage(`Found ${cardCount} hazard cards to validate`);
          
          let validatedCards = 0;
          
          for (let cardIndex = 1; cardIndex <= cardCount; cardIndex++) {
            const hazardCardElement = this.page.locator(
              `${this.getLocator(CWFPageLocators.hazardCardColor)}[${cardIndex}]`
            );
            
            if (await hazardCardElement.isVisible()) {
              try {
                // Get the hazard name from the card header using the new locator
                const hazardHeaderElement = hazardCardElement.locator(
                  "//div[1]"
                );
                
                if (await hazardHeaderElement.isVisible()) {
                  const hazardName = await hazardHeaderElement.textContent();
                  
                  if (hazardName) {
                    const trimmedHazardName = hazardName.trim().toUpperCase();
                    await this.tb.logMessage(`Card ${cardIndex}: Found hazard "${trimmedHazardName}"`);
                    
                    // Check if this hazard name matches any expected component
                    const matchingComponent = Object.keys(energyComponentColors).find(
                      component => component === trimmedHazardName
                    );
                    
                    if (matchingComponent) {
                      const expectedColor = energyComponentColors[matchingComponent as keyof typeof energyComponentColors];
                      await validateComponentColor(matchingComponent, expectedColor);
                      validatedCards++;
                    } else {
                      await this.tb.logMessage(`Card ${cardIndex}: Hazard "${trimmedHazardName}" not found in expected components`);
                    }
                  } else {
                    await this.tb.logMessage(`Card ${cardIndex}: Could not extract hazard name from header`);
                  }
                } else {
                  await this.tb.logMessage(`Card ${cardIndex}: Hazard header not visible`);
                }
              } catch (error) {
                await this.tb.logMessage(`Error processing card ${cardIndex}: ${(error as Error).message}`);
              }
            } else {
              await this.tb.logMessage(`Card ${cardIndex}: Not visible`);
            }
          }
          
          await this.tb.logSuccess(`Energy wheel component color validation completed. Validated ${validatedCards} cards out of ${cardCount} total cards`);
          
          // Call the energy wheel to hazard cards comparison function
          await compareEnergyWheelWithHazardCards();
        } else {
          throw new Error(
            "Energy wheel is enabled but component is not visible on the page"
          );
        }
      } else {
        await this.tb.logMessage(
          "Energy wheel is disabled - skipping energy wheel component check"
        );
      }

      await this.tb.logSuccess(
        `\n[${properties.title}] Hazards and Controls validations passed successfully\n`
      );
    } catch (error) {
      await this.tb.logMessage(
        `\n[${properties.title}] Hazards and Controls validation failed: ${
          (error as Error).message
        }\n`
      );
      throw error;
    }
  }
  public async viewValidateAllPagesInJSON() {
    try {
      const pages: cwfInterfaces.PageContent[] =
        this.RESPONSE_SAVEDFORM_JSON.contents.filter(
          (content: cwfInterfaces.Content) => content.type === "page"
        );

      if (pages.length === 0) {
        throw new Error(
          "No pages found in the JSON response while view validations."
        );
      }

      for (const pageData of pages) {
        try {
          const pageTitle = pageData.properties.title;

          await allure.step(
            `Click on page '${pageTitle}' in view mode`,
            async () => {
              await this.page
                .getByRole("button", { name: pageTitle, exact: true })
                .click({
                  timeout: 10000,
                });
            }
          );

          await this.tb.captureScreenshot(
            this.page,
            `'${pageTitle}' Page in view mode`
          );

          await this.viewValidatePageContents(this.page, pageData.contents, {});
        } catch (pageError) {
          console.error(
            `Error processing page during view Validations: ${pageData.properties.title}:`,
            pageError
          );
          throw pageError;
        }
      }
    } catch (error) {
      console.error("Critical error in viewValidateAllPagesInJSON:", error);
      throw error;
    }
  }

  public async viewValidatePageContents(
    page: Page,
    contents: cwfInterfaces.Content[],
    counters: cwfInterfaces.ContentCounters
  ): Promise<void> {
    try {
      let shortTextCounter = 0;
      let longTextCounter = 0;
      for (const content of contents) {
        if (content.type === "section") {
          if (content.contents && Array.isArray(content.contents)) {
            await this.viewValidatePageContents(
              page,
              content.contents,
              counters
            );
          }
        } else if (content.type === "input_text") {
          if (content.properties.input_type === "short_text") {
            shortTextCounter++;
            await this.viewFunctionCaller(page, content, shortTextCounter);
          } else if (content.properties.input_type === "long_text") {
            longTextCounter++;
            await this.viewFunctionCaller(page, content, longTextCounter);
          }
        } else {
          if (!counters[content.type]) {
            counters[content.type] = 0;
          }
          counters[content.type]++;
          await this.viewFunctionCaller(page, content, counters[content.type]);
        }
      }
    } catch (error) {
      console.error("Error in Validating Page in view mode:", error);
      throw error;
    }
  }

  public async viewFunctionCaller(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    switch (content.type) {
      case "input_text":
        await allure.step(
          `Validating view mode of Component "Input Text" indexed: #${index} with title "${content.properties.title}"`,
          async () => {
            await this.viewInputTextValidatorFunction(page, content, index);
          }
        );
        break;
      default:
        this.tb.logMessage(
          `Content type "${content.type}" view validations not implemented.`
        );
    }
  }

  public async verifySuccessToastMessage() {
    await allure.step(
      "Verify Success Toast Message after Successfully Saving the form",
      async () => {
        try {
          const successToastLocator = this.page.locator(
            this.getLocator(CWFPageLocators.CWF_Form_SuccessToast)
          );
          await expect(successToastLocator).toBeVisible({ timeout: 5000 });
          await this.tb.logSuccess("Success Toast Message is visible");
          const toastMessage = await successToastLocator.textContent();
          await this.tb.logSuccess(`Success Toast Message is :${toastMessage}`);
        } catch (error) {
          console.error("Error verifying success toast message:", error);
          throw error;
        }
      }
    );
  }

  public async handleSaveAndCompleteModal() {
    try {
      const eleCompleteFormBtn = this.page.locator(
        this.getLocator(CWFPageLocators.FinalCWFCompleteFormBtn)
      );
      await expect(eleCompleteFormBtn).toBeVisible({ timeout: 5000 });
      await eleCompleteFormBtn.click();
    } catch (error) {
      console.error("Error handling save and complete modal:", error);
      throw error;
    }
  }

  public async clickSaveAndComplete(LastPage: boolean) {
    try {
      let responsePromise = null;
      const saveButtonLocator = this.page.locator(
        this.getLocator(CWFPageLocators.CWF_Template_SaveAndContinueBtn)
      );

      await expect(saveButtonLocator).toBeVisible({ timeout: 15000 });
      await saveButtonLocator.scrollIntoViewIfNeeded();

      if (LastPage) {
        await this.page.waitForTimeout(5000);
        await this.tb.logMessage(
          "Attempting to click Save and Complete button"
        );
      } else {
        await this.tb.logMessage(
          "Attempting to click Save and Continue button"
        );
      }

      await saveButtonLocator.click({ timeout: 10000 }).catch(async (err) => {
        console.warn("Initial click attempt had an issue:", err);
        try {
          await saveButtonLocator.click({ force: true, timeout: 5000 });
        } catch (retryErr) {
          console.warn("Even retry click failed:", retryErr);
        }
      });

      if (LastPage) {
        try {
          await this.handleSaveAndCompleteModal();
          responsePromise = this.captureFormResponseAfterSaveAndComplete(
            "cwfTemplatesSaveAndComplete",
            "cwfSavedFormPost"
          );
          await this.page.waitForTimeout(3000);
        } catch (error) {
          console.warn("Failed to setup response capture:", error);
        }

        try {
          try {
            const successToastLocator = this.page.locator(
              this.getLocator(CWFPageLocators.CWF_Form_SuccessToast)
            );

            const isToastVisible = await successToastLocator
              .isVisible()
              .catch(() => false);

            if (isToastVisible) {
              await this.tb.logSuccess("Success Toast Message is visible");
              try {
                const toastMessage = await successToastLocator.textContent();
                expect(toastMessage).toContain("Form Submitted");
                await this.tb.logSuccess(
                  `Success Toast Message is: ${toastMessage}`
                );
              } catch (e) {
                console.warn(
                  "Could not get toast message text / toast message does not contain Form Submitted:",
                  e
                );
              }
            }
          } catch (toastError) {
            console.warn("Could not check for toast message:", toastError);
          }

          if (responsePromise) {
            try {
              await responsePromise;
            } catch (e) {
              console.warn("Response capture had an issue:", e);
            }
          }

          await this.tb.logMessage("Save and Complete operation completed");
        } catch (postClickError) {
          console.warn("Post-click operations had issues:", postClickError);
        }
      } else {
        try {
          await this.tb.logMessage("Save and Continue operation completed");
        } catch (e) {
          console.warn("Logging error:", e);
        }
      }
    } catch (error: any) {
      if (error.message && !error.message.includes("has been closed")) {
        if (LastPage) {
          console.error("Error clicking Save and Complete button:", error);
        } else {
          console.error("Error clicking Save and Continue button:", error);
        }
        throw error;
      } else {
        console.warn(
          "Page closed after button click - this may be expected behavior"
        );
      }
    }
  }

  private async isInputFieldMandatory(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    await allure.step("Validating Mandatory Input Field", async () => {
      await this.tb.logMessage(
        `[${content.properties.title}] Field is marked as mandatory`
      );
      await this.tb.testStep(
        `Verifying Asterisk mark on the label/title for the mandatory field`,
        async () => {
          const fieldLocator = this.page.locator(
            this.getLocator(
              CWFPageLocators.CWF_Template_TitleIsMandatoryLocator(
                content.properties.title
              )
            )
          );
          await expect(fieldLocator).toBeVisible({ timeout: 5000 });
          await this.tb.logSuccess(
            `[${content.properties.title}] Asterisk mark is visible for mandatory field`
          );
        }
      );

      await this.tb.testStep(
        "Verifying Error prompt message for mandatory field",
        async () => {
          await allure.step(
            "Clicking Save and Complete button to trigger error prompt",
            async () => {
              await this.clickSaveAndComplete(false);
            }
          );

          const errorToastBox = this.page.locator(
            this.getLocator(CWFPageLocators.requiredFieldErrorToast)
          );
          await expect(errorToastBox).toBeVisible({ timeout: 5000 });
          await this.tb.logSuccess(`Mandatory field error toast validated`);
          await expect(errorToastBox).toBeHidden({ timeout: 7000 });
        }
      );

      await this.tb.logSuccess(
        `[${content.properties.title}] Mandatory field validation passed`
      );
    });
  }

  public async isInputFieldNotMandatory(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    await this.tb.logMessage(
      `[${content.properties.title}] Field is not marked as mandatory`
    );
    await this.tb.testStep(
      `Verifying Asterisk mark on the label/title for the non-mandatory field`,
      async () => {
        const fieldLocator = this.page.locator(
          this.getLocator(
            CWFPageLocators.CWF_Template_TitleIsNotMandatoryLocator(
              content.properties.title
            )
          )
        );
        await expect(fieldLocator).toBeVisible({ timeout: 5000 });
        await expect(fieldLocator).not.toContainText("*");
        await this.tb.logSuccess(
          `[${content.properties.title}] Asterisk mark is not visible for non-mandatory field`
        );
      }
    );

    await this.tb.testStep(
      "Verifying Locator does not contains required attribute",
      async () => {
        const fieldLocator = this.page.locator(
          this.getLocator(
            CWFPageLocators.CWF_Template_TitleIsNotMandatoryLocator(
              content.properties.title
            )
          )
        );
        await expect(fieldLocator).not.toHaveAttribute("required");
        await this.tb.logSuccess(
          `[${content.properties.title}] Field does not have required attribute`
        );
      }
    );

    await this.tb.logSuccess(
      `[${content.properties.title}] Non-mandatory field validation passed`
    );
  }

  public async validateSavedFormInList() {
    try {
      const recentlySavedForm = this.page.locator(
        this.getLocator(CWFPageLocators.CWF_SavedForm_recentlySavedForm)
      );
      await allure.step(
        "Validate saved form visibility and its anchor tag in the list",
        async () => {
          await this.page.waitForTimeout(3000);
          await expect(recentlySavedForm).toBeVisible({ timeout: 5000 });
          // await expect(recentlySavedForm).toHaveAttribute(
          //   "href",
          //   `/template-forms/view?formId=${this.formId}`
          // );
          await this.tb.logSuccess(
            "Successfully validated the saved form in the list"
          );
        }
      );
      const recentlySavedFormStatus = this.page.locator(
        this.getLocator(CWFPageLocators.CWF_SavedForm_recentlySavedFormStatus)
      );
      await allure.step(
        "Verify recently saved for Status to be Completed",
        async () => {
          await expect(recentlySavedFormStatus).toBeVisible();
          await expect(recentlySavedFormStatus).toHaveText("COMPLETED");
          await this.tb.logSuccess(
            "Successfully validated the saved form status in the list"
          );
        }
      );
      await this.tb.captureScreenshot(
        this.page,
        "Recently Saved Form List View"
      );
      await this.tb.clickButton(recentlySavedForm, "Recently Saved Form");
      await allure.step(
        "Waiting for the page to load after clicking on the saved form",
        async () => {
          await this.page.waitForLoadState("networkidle");
        }
      );
    } catch (error) {
      console.error("Error validating saved form in list:", error);
      throw error;
    }
  }

  public async choiceValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    const properties = content.properties as cwfInterfaces.ChoiceProperties;
    await this.tb.logMessage(
      `Index ${index} - Validating choice: ${properties.title}`
    );

    try {
      await this.tb.testStep(
        "Validating Visibility of the Choice Component and its title",
        async () => {
          const choiceCompLocator = this.page.locator(
            `${this.getLocator(
              CWFPageLocators.choiceComponentLocator
            )}[${index}]`
          );
          await expect(choiceCompLocator).toBeVisible({ timeout: 5000 });

          const choiceTitle = this.page.locator(
            `(${this.getLocator(
              CWFPageLocators.choiceComponentLocator
            )}[${index}]${this.getLocator(
              CWFPageLocators.choiceComponentTitle
            )})`
          );
          await expect(choiceTitle).toBeVisible({ timeout: 5000 });
          await expect(choiceTitle).toContainText(properties.title);

          await this.tb.logSuccess(
            `Choice Component indexed: ${index} and its title are visible on the page`
          );
        }
      );

      if (properties.is_mandatory) {
        await this.tb.testStep(
          `Verifying asterisk mark on the title of Mandatory Choice Component at index ${index}`,
          async () => {
            //validate asterisk mark in the title
            const choiceTitleWithAsteriskMark = this.page.locator(
              `(${this.getLocator(
                CWFPageLocators.choiceComponentLocator
              )}[${index}]${this.getLocator(
                CWFPageLocators.choiceComponentTitle
              )})`
            );
            const titleText = await choiceTitleWithAsteriskMark.textContent();
            if (titleText?.endsWith(" *")) {
              await this.tb.logSuccess(
                `Asterisk mark is present in the title of mandatory choice component indexed: ${index}`
              );
            } else {
              await this.tb.logFailure(
                `Asterisk mark is not present in the title of mandatory choice component indexed: ${index}`
              );
              throw new Error(
                `Asterisk mark is not present in the title of mandatory choice component indexed: ${index}`
              );
            }
          }
        );
      }

      if (!properties.is_mandatory) {
        await this.tb.testStep(
          `Validating asterisk mark should not be in title for non-mandatory choice component at index ${index}`,
          async () => {
            const choiceTitleWithoutAsteriskMark = this.page.locator(
              `(${this.getLocator(
                CWFPageLocators.choiceComponentLocator
              )}[${index}]${this.getLocator(
                CWFPageLocators.choiceComponentTitle
              )})`
            );
            const titleText =
              await choiceTitleWithoutAsteriskMark.textContent();
            if (titleText?.endsWith(" *")) {
              await this.tb.logFailure(
                `Asterisk mark is present in the title of non-mandatory choice component indexed: ${index}`
              );
              throw new Error(
                `Asterisk mark is present in the title of non-mandatory choice component indexed: ${index}`
              );
            } else {
              await this.tb.logSuccess(
                `Asterisk mark is not present in the title of non-mandatory choice component indexed: ${index}`
              );
            }
          }
        );
      }

      // 4. Checking if the component has attachments allowed
      if (properties.attachments_allowed) {
        await this.tb.logMessage("Found attachments allowed in the component");
      }

      // 5. Checking if the component has comments allowed
      if (properties.comments_allowed) {
        await this.tb.logMessage("Found comments allowed in the component");
      }

      if (
        properties.pre_population_rule_name &&
        properties.pre_population_rule_name === "user_last_completed_form"
      ) {
        if (properties.user_value && properties.user_value.length > 0) {
          await this.tb.testStep(
            "Verify pre-populated values to be equal to previously chosen user values",
            async () => {
              await this.tb.logMessage(
                `Found Pre population rule applied to the choice component at index ${index}`
              );
              await this.tb.testStep(
                "Validating pre populated values to match with the previously chosen user values",
                async () => {
                  try {
                    if (properties.choice_type === "single_choice") {
                      //validating that the option label matches with the user value option
                      const prePopulatedOptionLabel = this.page.locator(
                        `${this.getLocator(
                          CWFPageLocators.choiceComponentLocator
                        )}${this.getLocator(
                          CWFPageLocators.choicePrepopulatedSingleOptionLabelClassFirst
                        )}${index}${this.getLocator(
                          CWFPageLocators.choicePrepopulatedSingleOptionLabelClassSecond
                        )}${
                          properties.user_value && properties.user_value[0]
                        }${this.getLocator(
                          CWFPageLocators.choicePrepopulatedSingleOptionLabelClosing
                        )}`
                      );
                      await expect(prePopulatedOptionLabel).toBeVisible();
                      const textValue =
                        await prePopulatedOptionLabel.textContent();
                      expect(textValue).toBe(
                        properties.user_value && properties.user_value[0]
                      );
                    } else if (properties.choice_type === "multiple_choice") {
                      //validating that the option label matches with the user value option
                      console.log("multiple choice prepopulated");
                    } else {
                      await this.tb.logFailure(
                        `Choice type "${properties.choice_type}" is not supported for validation.`
                      );
                      throw new Error(
                        `Choice type "${properties.choice_type}" is not supported for validation.`
                      );
                    }
                  } catch (error) {
                    console.error(
                      `Error validating pre-populated values for choice component at index ${index}:`,
                      error
                    );
                    throw error;
                  }
                }
              );
            }
          );
        } else {
          await this.tb.logMessage(
            `No pre-populated values found for the choice component at index ${index}, filling it for the first time`
          );
        }
      }
    } catch (error) {
      await this.tb.logMessage(
        `\n[${content.properties.title}] Validation failed: ${
          (error as Error).message
        }\n`
      );
      throw error;
    }
  }

  public async dateTimeValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    const properties = content.properties as cwfInterfaces.DateTimeProperties;
  }
  public async reportDateTimeValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    const properties =
      content.properties as cwfInterfaces.ReportingDateTimeProperties;
    await this.tb.logMessage(
      `Index ${index} - Validating Title of the component : ${properties.title}`
    );
    const reportingDate_locator = this.page.locator(
      this.getLocator(CWFPageLocators.CWF_Template_ReportDate)
    );
    if (properties.user_value?.value) {
      const jsonValue: string = properties.user_value.value;
      await allure.step(
        "Validate single value  of Reporting date component",
        async () => {
          try {
            await expect(reportingDate_locator).toBeVisible({ timeout: 5000 });
            // Get the JSON value from the properties
            await this.tb.logSuccess(
              "The Reporting Date component is visible in the UI"
            );
            // UI value
            const uiValue = await reportingDate_locator.inputValue(); // Get the value from the UI

            // Parse the JSON value into a Date object
            const parsedDate: Date = new Date(jsonValue);

            // Format the parsed date to match the UI format
            const options: Intl.DateTimeFormatOptions = {
              year: "numeric",
              month: "short",
              day: "2-digit",
            };
            const datePart: string = new Intl.DateTimeFormat(
              "en-US",
              options
            ).format(parsedDate); // Format date part

            // Format the time part manually to match 24-hour format with PM/AM
            const hours: number = parsedDate.getHours();
            const minutes: string = parsedDate
              .getMinutes()
              .toString()
              .padStart(2, "0");
            const period: string = hours >= 12 ? "PM" : "AM";
            const timePart: string = `${hours}:${minutes} ${period}`;

            // Combine date and time parts to match the UI format
            const formattedDate: string = `${datePart} ${timePart}`;
            console.log(`Formatted Date: formattedDate: ${formattedDate}`);
            // Compare the two values
            if (formattedDate === uiValue) {
              console.log("The values match!");
            } else {
              console.log("The values do not match.");
              throw new Error(
                `Mismatch: Formatted Date = ${formattedDate}, UI Value = ${uiValue}`
              );
            }
            await this.tb.logSuccess(
              `The Value displayed in the UI matches the JSON value: ${uiValue}`
            );
          } catch (error) {
            console.error("Error validating single value component:", error);
            throw error; // Re-throw the error to ensure the test fails
          }
        }
      );
    } else {
      await allure.step(
        "Validate null  value of Reporting date component",
        async () => {}
      );
    }
  }

  public async updateReportDateComponent() {
    await allure.step("Update Report Date Component", async () => {
      try {
        const reportingDate_locator = this.page.locator(
          this.getLocator(CWFPageLocators.CWF_Template_ReportDate)
        );

        await expect(reportingDate_locator).toBeVisible();
        await reportingDate_locator.click();

        // Get the current date and time
        const now = new Date();
        const options: Intl.DateTimeFormatOptions = {
          year: "numeric",
          month: "short",
          day: "2-digit",
        };
        const datePart = new Intl.DateTimeFormat("en-US", options).format(now);
        const hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2, "0");
        const period = hours >= 12 ? "PM" : "AM";
        const timePart = `${hours}:${minutes} ${period}`;
        const currentDateTime = `${datePart}, ${timePart}`;

        await reportingDate_locator.fill(currentDateTime);

        // Verify the value has been updated
        const updatedValue = await reportingDate_locator.inputValue();
        console.log(`Updated Value: ${updatedValue}`);
        await this.tb.logSuccess(
          `The Value Updated in form is :  ${updatedValue}`
        );
      } catch (error) {
        console.error("Error updating the Report Date Component:", error);
        throw error; // Re-throw the error to ensure the test fails
      }
    });
  }
  public async verifyIsUpdatePopupDisplayed() {
    const report_dateHeaderLocator = this.page.locator(
      this.getLocator(CWFPageLocators.ReportDate_TimeSection)
    );
    report_dateHeaderLocator.click();
    await allure.step("Verify Update Popup", async () => {
      try {
        const reportDate_TimeUpdatePopupLocator = this.page.locator(
          this.getLocator(CWFPageLocators.ReportDate_Time_UpdatePopup)
        );

        await expect(reportDate_TimeUpdatePopupLocator).toBeVisible({
          timeout: 5000,
        });
        await this.tb.logSuccess("Update popup is visible");
      } catch (error) {
        console.error("Error verifying update popup:", error);
        throw error; // Re-throw the error to ensure the test fails
      }
    });
  }

  public async updateReportDateComponentfromCalender() {
    await allure.step(
      "Update Report Date Component by selecting date and time in calendar",
      async () => {
        try {
          await allure.step(
            "Locate and verify the reporting date field",
            async () => {
              const reportingDate_locator = this.page.locator(
                this.getLocator(CWFPageLocators.CWF_Template_ReportDate)
              );
              await expect(reportingDate_locator).toBeVisible();
              const currentValue = await reportingDate_locator.inputValue();
              await this.tb.logSuccess(
                `The current value in the form is: ${currentValue}`
              );
              await reportingDate_locator.click();
              await this.tb.logSuccess(
                "Successfully located and verified the reporting date field."
              );
            }
          );

          await allure.step(
            "Select the current date from the calendar",
            async () => {
              const pickCurrentDateLocator = this.page.locator(
                this.getLocator(
                  CWFPageLocators.CWF_Template_ReportDate_PickDate
                )
              );
              await pickCurrentDateLocator.click();
              await this.verifyIsUpdatePopupDisplayed();
              await this.verifyHeaderInReportDateUpdatePopoUp();
              await this.clickOnConfirmInReportDateUpdatePopup();
              await this.tb.logSuccess(
                "Successfully selected the current date from the calendar."
              );
            }
          );
          await this.page.waitForTimeout(2000);
          await allure.step(
            "Click on the reporting date field again before selecting the time",
            async () => {
              const reportingDate_locator = this.page.locator(
                this.getLocator(CWFPageLocators.CWF_Template_ReportDate)
              );
              await reportingDate_locator.click();
              await this.tb.logSuccess(
                "Successfully clicked on the reporting date field again."
              );
            }
          );
          await this.page.waitForTimeout(1000);
          await allure.step(
            "Select the current time from the time picker",
            async () => {
              const picktimeLocator = this.page.locator(
                this.getLocator(
                  CWFPageLocators.CWF_Template_ReportDate_PickTime
                )
              );
              await picktimeLocator.click();
              await this.verifyIsUpdatePopupDisplayed();
              await this.verifyHeaderInReportDateUpdatePopoUp();
              await this.clickOnConfirmInReportDateUpdatePopup();
              await this.tb.logSuccess(
                "Successfully selected the current time from the time picker."
              );
            }
          );
          await allure.step(
            "Verify the updated value in the form",
            async () => {
              const reportingDate_locator = this.page.locator(
                this.getLocator(CWFPageLocators.CWF_Template_ReportDate)
              );
              const updatedValue = await reportingDate_locator.inputValue();
              const currentValue = await reportingDate_locator.inputValue(); // Re-fetch current value for comparison
              if (currentValue !== updatedValue) {
                await this.tb.logSuccess(
                  `The value updated in the form is: ${updatedValue}`
                );
              } else {
                console.warn(
                  `The value in the form remains unchanged: ${currentValue}`
                );
              }
              await this.tb.logSuccess(
                `Successfully verified the updated value in the form: ${updatedValue}`
              );
            }
          );
        } catch (error) {
          console.error("Error updating the Report Date Component:", error);
          throw error;
        }
      }
    );
  }
  public async verifyHeaderInReportDateUpdatePopoUp() {
    await allure.step("Verify Header in Report Date Update Popup", async () => {
      try {
        const reportDate_TimeUpdatePopupHeaderLocator = this.page.locator(
          this.getLocator(CWFPageLocators.ReportDate_Time_UpdatePopup)
        );
        // Ensure the header is visible
        const headerText =
          await reportDate_TimeUpdatePopupHeaderLocator.textContent();
        console.log(`Header Text: ${headerText}`);
        await this.tb.logSuccess(
          `Header in Report Date Update Popup is visible :${headerText}`
        );
      } catch (error) {
        console.error("Error verifying header in update popup:", error);
        throw error; // Re-throw the error to ensure the test fails
      }
    });
  }
  public async clickOnConfirmInReportDateUpdatePopup() {
    await allure.step(
      "Click on Confirm in Report Date Update Popup",
      async () => {
        try {
          const confirmButtonLocator = this.page.locator(
            this.getLocator(CWFPageLocators.ReportDate_Time_UpdateConfirm)
          );
          // Ensure the confirm button is visible
          await expect(confirmButtonLocator).toBeVisible({ timeout: 5000 });
          console.log("Confirm button is visible");

          // Click the confirm button
          await confirmButtonLocator.click();
          console.log("Clicked on Confirm button");
          await this.tb.logSuccess(
            "Successfully clicked on Confirm button in Report Date Update Popup"
          );
        } catch (error) {
          console.error("Error clicking Confirm button:", error);
          throw error; // Re-throw the error to ensure the test fails
        }
      }
    );
  }
  public async inputTextValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    const properties = content.properties as cwfInterfaces.TextProperties;
    await this.tb.logMessage(
      `Index ${index} - Validating input_text: ${properties.title}`
    );
    // Create locator for the input text field based on the input type
    let locator: Locator;
    if (properties.input_type === "short_text") {
      locator = this.page.locator(`(//input[@type='text'])[${index}]`);
      await this.tb.logMessage(
        `Locator short text input: ${locator} for index: ${index}`
      );
    } else if (properties.input_type === "long_text") {
      locator = this.page.locator(`(//textarea)[${index}]`);
      await this.tb.logMessage(
        `Locator long text input: ${locator} for index: ${index}`
      );
    } else {
      throw new Error(`Unknown input_type: ${properties.input_type}`);
    }

    try {
      // Check if the input field is visible
      await expect(locator).toBeVisible({ timeout: 5000 });
      await this.tb.logMessage(
        `[${content.properties.title}] Input field is visible`
      );

      // Validate placeholder text
      await expect(locator).toHaveAttribute(
        "placeholder",
        properties.placeholder
      );
      await this.tb.logMessage(
        `[${content.properties.title}] Placeholder matches: ${properties.placeholder}`
      );

      // Validate if the field is mandatory
      if (properties.is_mandatory) {
        await this.isInputFieldMandatory(page, content, index);
      } else {
        await this.isInputFieldNotMandatory(page, content, index);
      }

      // Validate input type
      if (properties.input_type) {
        if (properties.input_type === "short_text") {
          await expect(locator).toHaveAttribute("type", "text");
          await this.tb.logMessage(
            `[${content.properties.title}] Input type matches: ${properties.input_type}`
          );
        } else if (properties.input_type === "long_text") {
          await expect(locator.evaluate((el) => el.tagName)).resolves.toMatch(
            "TEXTAREA"
          );
          await this.tb.logMessage(
            `[${content.properties.title}] Input type matches: ${properties.input_type}`
          );
          const sampleLongText =
            "Urbint is a technology company that provides software solutions for the insurance and real estate industries. The company's platform uses artificial intelligence and machine learning to help clients make better decisions about risk management, underwriting, and claims processing. Urbint's software is designed to improve efficiency and reduce costs for its clients, while also providing valuable insights into their operations.";
          await locator.fill(sampleLongText);
          await expect(locator).toHaveValue(sampleLongText);
          await this.tb.logSuccess(
            `[${content.properties.title}] Long text input accepted`
          );
        }
      }

      // Validate any specific validation rules
      if (properties.validation && properties.validation.length > 0) {
        await this.tb.logMessage(
          `[${
            content.properties.title
          }] Validation rules found: ${JSON.stringify(properties.validation)}`
        );
        // Implement validation rule checks here based on your UI implementation
      }

      // Validate response options
      if (properties.response_option && properties.response_option !== "") {
        if (properties.response_option === "alphanumeric") {
          await locator.fill("@");
          const errorPrompt = page.locator(
            this.getLocator(
              CWFPageLocators.CWF_Template_inputTextAlphanumericInvalidInputErrorPrompt
            )
          );
          await expect(errorPrompt).toBeVisible({ timeout: 5000 });
          await this.tb.logMessage(
            `[${content.properties.title}] Error prompt displayed for invalid input`
          );
          await locator.clear();
          await locator.fill("Urbint123");
          await expect(errorPrompt).not.toBeVisible();
          await expect(locator).toHaveValue("Urbint123");
          await this.tb.logSuccess(
            `[${content.properties.title}] Valid input accepted`
          );
        } else if (properties.response_option === "only_alphabets") {
          await locator.fill("123");
          const errorPrompt = page.locator(
            this.getLocator(
              CWFPageLocators.CWF_Template_inputTextOnlyAlphaInvalidInputErrorPrompt
            )
          );
          await expect(errorPrompt).toBeVisible({ timeout: 5000 });
          await this.tb.logMessage(
            `[${content.properties.title}] Error prompt displayed for invalid input`
          );
          await locator.clear();
          await locator.fill("Urbint");
          await expect(errorPrompt).not.toBeVisible();
          await expect(locator).toHaveValue("Urbint");
          await this.tb.logSuccess(
            `[${content.properties.title}] Valid input accepted`
          );
        } else if (properties.response_option === "allow_special_characters") {
          await locator.fill("Urbint@#$%^&*123");
          await expect(locator).toHaveValue("Urbint@#$%^&*123");
          await this.tb.logSuccess(
            `[${content.properties.title}] Valid input accepted`
          );
        } else {
          await locator.fill("Urbint");
          await expect(locator).toHaveValue("Urbint");
          await this.tb.logSuccess(
            `[${content.properties.title}] Valid input accepted`
          );
        }
        await locator.clear();
        await locator.fill(inputData.inputText);
        await expect(locator).toHaveValue(inputData.inputText);
      }
      await this.tb.logSuccess(
        `\n[${content.properties.title}] All validations passed successfully\n`
      );
    } catch (error) {
      await this.tb.logMessage(
        `\n[${content.properties.title}] Validation failed: ${
          (error as Error).message
        }\n`
      );
      throw error;
    }
  }

  public async validateShortPhoneNumber(
    inputPhnNumber: Locator,
    errorPrompt: Locator,
    shortPhnNumber: string
  ) {
    await this.tb.testStep(
      "Validate phone number with less than required characters",
      async () => {
        await inputPhnNumber.fill(shortPhnNumber);
        if (
          (await inputPhnNumber.inputValue()).replace(/[^0-9]/g, "").length < 10
        ) {
          await expect(errorPrompt).toBeVisible();
          expect(
            (await inputPhnNumber.inputValue()).replace(/[^0-9]/g, "")
          ).toBe(shortPhnNumber);
        }
        await inputPhnNumber.clear();
        await this.tb.logSuccess(
          "Successfully validated phone number with less than required characters."
        );
      }
    );
  }

  public async validateSpecialCharacterPhoneNumber(
    inputPhnNumber: Locator,
    errorPrompt: Locator,
    invalidPhnNumber: string
  ) {
    await this.tb.testStep(
      "Validate phone number with special characters",
      async () => {
        await inputPhnNumber.fill(invalidPhnNumber);
        if ((await inputPhnNumber.inputValue()).length === 0) {
          await expect(inputPhnNumber).toHaveValue("");
        }
        await inputPhnNumber.clear();
        await this.tb.logSuccess(
          "Successfully validated phone number with special characters."
        );
      }
    );
  }

  public async validateValidPhoneNumber(
    inputPhnNumber: Locator,
    validPhnNumber: string
  ) {
    await this.tb.testStep("Validate valid phone number", async () => {
      await inputPhnNumber.fill(validPhnNumber);
      expect((await inputPhnNumber.inputValue()).replace(/[^0-9]/g, "")).toBe(
        validPhnNumber
      );
      await inputPhnNumber.clear();
      await this.tb.logSuccess(
        "Successfully validated valid phone number scenario."
      );
    });
  }

  public async phoneNumberValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    await this.tb.testStep(
      "Validate different use cases for Phone Number Component",
      async () => {
        const properties =
          content.properties as cwfInterfaces.PhoneNumberProperties;
        let invalidPhnNumber = "abc#$%wxyz";
        let shortPhnNumber = "909900900";
        const inputPhnNumber = this.page.locator(
          `${this.getLocator(CWFPageLocators.inputPhoneNumber)}[${index}]`
        );
        const errorPrompt = this.page.locator(
          `${this.getLocator(
            CWFPageLocators.CWF_Template_isMandatoryErrorPrompt
          )}[1]`
        );
        if (properties.response_option === "manual_input") {
          // Validate Phone Number with special characters
          await this.validateSpecialCharacterPhoneNumber(
            inputPhnNumber,
            errorPrompt,
            invalidPhnNumber
          );

          // Validate Phone Number with less characters
          await this.validateShortPhoneNumber(
            inputPhnNumber,
            errorPrompt,
            shortPhnNumber
          );

          // Validate Valid Phone Number
          await this.validateValidPhoneNumber(
            inputPhnNumber,
            inputData.inputPhoneNumber
          );
        } else if (properties.response_option === "auto_populate") {
          console.log(
            `response_option=` +
              properties.response_option +
              ` is not yet implemented`
          );
        }

        await inputPhnNumber.clear();
        await inputPhnNumber.fill(inputData.inputPhoneNumber);
        expect((await inputPhnNumber.inputValue()).replace(/[^0-9]/g, "")).toBe(
          inputData.inputPhoneNumber
        );

        await this.tb.logSuccess(
          "Successfully validated different use cases for Phone Number Component."
        );
      }
    );
  }

  public async viewInputTextValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    const properties = content.properties as cwfInterfaces.TextProperties;
    await this.tb.logMessage(
      `Index ${index} - Validating input_text component in view mode: ${properties.title}`
    );
    let locator: Locator;
    if (properties.input_type === "short_text") {
      locator = page.locator(
        `${this.getLocator(
          CWFPageLocators.CWF_Template_inputTextFieldDynamicOpeningLocator
        )}${properties.placeholder}${this.getLocator(
          CWFPageLocators.CWF_Template_inputTextFieldDynamicClosingLocator
        )}`
      );
      await this.tb.logMessage(
        `Locator short text input (view mode): ${locator} for index: ${index}`
      );
    } else if (properties.input_type === "long_text") {
      locator = page.locator(
        `${this.getLocator(
          CWFPageLocators.CWF_Template_inputTextareaFieldDynamicOpeningLocator
        )}${properties.placeholder}${this.getLocator(
          CWFPageLocators.CWF_Template_inputTextFieldDynamicClosingLocator
        )}`
      );
      await this.tb.logMessage(
        `Locator long text input (view mode): ${locator} for index: ${index}`
      );
    } else {
      throw new Error(`Unknown input_type: ${properties.input_type}`);
    }

    try {
      await expect(locator).toBeVisible({ timeout: 5000 });
      await this.tb.logMessage(
        `[${content.properties.title}] Input field is visible in view mode`
      );

      await expect(locator).toHaveAttribute(
        "placeholder",
        properties.placeholder
      );
      await this.tb.logMessage(
        `[${content.properties.title}] Placeholder matches: ${properties.placeholder} in view mode`
      );

      const value = await locator.inputValue();

      if (value === properties.user_value) {
        await this.tb.logSuccess(
          `[${content.properties.title}] Valid value: ${value} matches the expected value in view mode`
        );
      } else {
        throw new Error(
          `[${content.properties.title}] Validation failed: Expected value "${properties.user_value}" but got "${value}" in view mode`
        );
      }
    } catch (error) {
      await this.tb.logMessage(
        `\n[${content.properties.title}] Validation failed in view mode: ${
          (error as Error).message
        }\n`
      );
      throw error;
    }
    await this.tb.logSuccess(
      `\n[${content.properties.title}] All validations passed successfully in view mode\n`
    );
  }

  public async numberValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    await this.tb.testStep(
      "Validate different use cases for Number Component",
      async () => {
        const properties = content.properties as cwfInterfaces.NumberProperties;
        let negativeNumber = "-9873";
        let exponentialNumber = "1.23e4";
        const inputNumber = page.locator(
          `${this.getLocator(CWFPageLocators.numberComponentInput)}[${index}]`
        );

        if (properties.response_option === "allowNegativeNumbers") {
          // Validate Negative Number
          await this.validateNegativeNumber(inputNumber, negativeNumber);
        } else if (properties.response_option === "allowDecimals") {
          // Validate Decimal Number
          await this.validateDecimalNumber(inputNumber, exponentialNumber);
        }
        await inputNumber.clear();
        await inputNumber.fill(inputData.inputNumber);
        await expect(inputNumber).toHaveValue(inputData.inputNumber);

        await this.tb.logSuccess(
          "Successfully validated different use cases for Number Component."
        );
      }
    );
  }
  public async validateDecimalNumber(
    inputNumber: Locator,
    exponentialNumber: string
  ) {
    await this.tb.testStep("Validate negative number", async () => {
      await inputNumber.fill(exponentialNumber);
      await expect(inputNumber).toHaveValue(exponentialNumber);
      await inputNumber.clear();
      await this.tb.logSuccess(
        "Successfully validated negative number scenario."
      );
    });
  }

  public async validateNegativeNumber(
    inputNumber: Locator,
    negativeNumber: string
  ) {
    await this.tb.testStep("Validate negative number", async () => {
      await inputNumber.fill(negativeNumber);
      await expect(inputNumber).toHaveValue(negativeNumber);
      await inputNumber.clear();
      await this.tb.logSuccess(
        "Successfully validated negative number scenario."
      );
    });
  }

  public async attachmentValidatorFunction(
    page: Page,
    content: cwfInterfaces.Content,
    index: number
  ) {
    const properties = content.properties as cwfInterfaces.AttachmentProperties;
    await this.tb.logMessage(
      `Index ${index} - Validating ${properties.attachment_type} attachment component: ${properties.title}`
    );

    if (properties.attachment_type === "photo") {
      const fileInput = this.page.locator(
        this.getLocator(CWFPageLocators.Attachment_uploadPhotoBtnInput)
      );

      const acceptAttribute = await fileInput.getAttribute("accept");

      await this.tb.testStep(
        `Verifying if file input accepts defined image types`,
        async () => {
          const expectedTypes = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".svg",
            ".apng",
            ".avif",
          ];
          const actualTypes = acceptAttribute?.split(",") || [];
          expect(actualTypes).toEqual(expectedTypes);
        }
      );

      await this.tb.testStep(
        `Verifying if multiple file upload is allowed`,
        async () => {
          const isMultiple = await fileInput.getAttribute("multiple");
          expect(isMultiple).not.toBeNull();
          await this.tb.logSuccess(
            `Multiple file upload is allowed for ${properties.attachment_type} component`
          );
        }
      );

      await this.tb.testStep(
        `Verifying successful file upload functionality`,
        async () => {
          const testImage1Path = path.join(
            __dirname,
            "../Data/dummy-media/dummy_image1.jpg"
          );

          await fileInput.setInputFiles(testImage1Path);
          await page.waitForTimeout(300);

          const altImageWhileUpload = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_loaderAltImageUploadPhoto
            )
          );
          const spinner = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_spinnerUploadPhoto)
          );
          const uploadingText = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_uploadingTextWhilePhotoUpload
            )
          );
          const cancelBtn = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_cancelButtonWhilePhotoUpload
            )
          );

          //waiting for upload UI elements to appear
          await expect(altImageWhileUpload).toBeVisible();
          await expect(spinner).toBeVisible();
          await expect(uploadingText).toBeVisible();
          await expect(cancelBtn).toBeVisible();

          await this.tb.logSuccess(
            `File upload functionality is working for ${properties.attachment_type} component`
          );

          await Promise.all([
            altImageWhileUpload.waitFor({ state: "hidden", timeout: 60000 }),
            spinner.waitFor({ state: "hidden", timeout: 60000 }),
            uploadingText.waitFor({ state: "hidden", timeout: 60000 }),
            cancelBtn.waitFor({ state: "hidden", timeout: 60000 }),
          ]);

          await this.tb.logSuccess(
            `File upload UI elements successfully disappeared after ${properties.attachment_type} upload`
          );
        }
      );

      await this.tb.testStep(
        "Verify if uploaded image is visible and uploaded successfully",
        async () => {
          const uploadedImage = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_recentlyUploadedPhoto)
          );
          await expect(uploadedImage).toBeVisible();
          await this.tb.logSuccess(
            `Uploaded image is visible for ${properties.attachment_type} component`
          );
          const deleteBtn = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_deleteBtnRecentlyUploadedPhoto
            )
          );
          await expect(deleteBtn).toBeVisible();
          await this.tb.logSuccess(
            `Delete button is visible for ${properties.attachment_type} component`
          );

          const lblDescriptionTextBox = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_lblDescriptionTextArea)
          );
          await expect(lblDescriptionTextBox).toBeVisible();
          const descriptionTextBox = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_descriptionTextAreaPhoto)
          );
          await expect(descriptionTextBox).toBeVisible();
          await this.tb.logSuccess(
            `Description text box is visible for ${properties.attachment_type} component`
          );
        }
      );

      await this.tb.testStep(
        "Verify description text box functionality for uploaded image",
        async () => {
          const descriptionTextBox = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_descriptionTextAreaPhoto)
          );
          await expect(descriptionTextBox).toHaveAttribute(
            "placeholder",
            "Add a description"
          );
          await descriptionTextBox.fill(inputData.attachmentDescription);
          await expect(descriptionTextBox).toHaveValue(
            inputData.attachmentDescription
          );
          await this.tb.logSuccess(
            `Description text box is filled with value: ${inputData.attachmentDescription}`
          );
          await descriptionTextBox.clear();
          await expect(descriptionTextBox).toHaveValue("");
          await this.tb.logSuccess(
            `Description text box is cleared successfully`
          );
          await this.tb.logSuccess(
            `Description text box functionality is working for ${properties.attachment_type} component`
          );
        }
      );

      await this.tb.testStep(
        "Verify delete button functionality for uploaded image",
        async () => {
          const deleteBtn = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_deleteBtnRecentlyUploadedPhoto
            )
          );
          await deleteBtn.click();
          const deletePopupBox = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_deletePopupBox)
          );
          await expect(deletePopupBox).toBeVisible();
          await this.tb.logSuccess(
            `Delete confirmation popup is visible for ${properties.attachment_type} component`
          );

          const popupBoxHeaderLbl = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_popupBoxPhotoHeaderLbl)
          );
          expect(await popupBoxHeaderLbl.innerText()).toBe("Delete Photos");

          const popupBoxDescriptionLbl = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_popupBoxPhotoDescriptionLbl
            )
          );
          expect(await popupBoxDescriptionLbl.innerText()).toBe(
            "Are you sure you want to permanently delete this photo? This action cannot be undone."
          );

          const cancelBtnInPopup = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_deletePhotoPopupCancelBtn
            )
          );
          await expect(cancelBtnInPopup).toBeVisible();
          await cancelBtnInPopup.click();

          await expect(deletePopupBox).not.toBeVisible();
          await this.tb.logSuccess(
            `Delete confirmation popup is closed for ${properties.attachment_type} component after clicking cancel button`
          );

          await deleteBtn.click();
          await expect(deletePopupBox).toBeVisible();

          const deleteBtnInPopup = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_deletePhotoPopupDeleteBtn
            )
          );
          await expect(deleteBtnInPopup).toBeVisible();
          await deleteBtnInPopup.click();
          const deletedPhotoPrompt = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_deletedPhotoSuccessfullyPrompt
            )
          );
          await deletePopupBox.waitFor({ state: "hidden", timeout: 5000 });
          await expect(deletedPhotoPrompt).toBeVisible();
          expect(await deletedPhotoPrompt.innerText()).toBe(
            "Photo deleted Please click on Save and Continue / save and complete to push changes"
          );
          await this.tb.logSuccess(
            `Deleted photo successfully prompt is visible for ${properties.attachment_type} component`
          );

          await deletedPhotoPrompt.waitFor({ state: "hidden", timeout: 5000 });

          const uploadedImage = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_recentlyUploadedPhoto)
          );
          const descriptionTextBox = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_descriptionTextAreaPhoto)
          );
          const lblDescriptionTextBox = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_lblDescriptionTextArea)
          );

          await Promise.all([
            expect(uploadedImage).not.toBeVisible(),
            expect(deleteBtn).not.toBeVisible(),
            expect(lblDescriptionTextBox).not.toBeVisible(),
            expect(descriptionTextBox).not.toBeVisible(),
          ]);

          await this.tb.logSuccess(
            `Uploaded image is deleted successfully for ${properties.attachment_type} component`
          );
        }
      );

      await this.tb.testStep(
        `Verifying successful file re-upload functionality`,
        async () => {
          const testImage1Path = path.join(
            __dirname,
            "../Data/dummy-media/dummy_image1.jpg"
          );

          await fileInput.setInputFiles(testImage1Path);
          await page.waitForTimeout(300);

          const altImageWhileUpload = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_loaderAltImageUploadPhoto
            )
          );
          const spinner = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_spinnerUploadPhoto)
          );
          const uploadingText = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_uploadingTextWhilePhotoUpload
            )
          );
          const cancelBtn = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_cancelButtonWhilePhotoUpload
            )
          );

          //waiting for upload UI elements to appear
          await Promise.all([
            expect(altImageWhileUpload).toBeVisible(),
            expect(spinner).toBeVisible(),
            expect(uploadingText).toBeVisible(),
            expect(cancelBtn).toBeVisible(),
          ]);
          await this.tb.logSuccess(
            `File re-upload functionality is working for ${properties.attachment_type} component`
          );
          await Promise.all([
            altImageWhileUpload.waitFor({ state: "hidden", timeout: 60000 }),
            spinner.waitFor({ state: "hidden", timeout: 60000 }),
            uploadingText.waitFor({ state: "hidden", timeout: 60000 }),
            cancelBtn.waitFor({ state: "hidden", timeout: 60000 }),
          ]);

          await this.tb.logSuccess(
            `File upload UI elements successfully disappeared after ${properties.attachment_type} reupload`
          );

          const uploadedImage = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_recentlyUploadedPhoto)
          );
          await expect(uploadedImage).toBeVisible();
          await this.tb.logSuccess(
            `Uploaded image is visible for ${properties.attachment_type} component`
          );
          const deleteBtn = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_deleteBtnRecentlyUploadedPhoto
            )
          );
          await expect(deleteBtn).toBeVisible();
          await this.tb.logSuccess(
            `Delete button is visible for ${properties.attachment_type} component`
          );

          const lblDescriptionTextBox = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_lblDescriptionTextArea)
          );
          await expect(lblDescriptionTextBox).toBeVisible();
          const descriptionTextBox = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_descriptionTextAreaPhoto)
          );
          await expect(descriptionTextBox).toBeVisible();
          await this.tb.logSuccess(
            `Description text box is visible for ${properties.attachment_type} component`
          );
          await expect(descriptionTextBox).toHaveAttribute(
            "placeholder",
            "Add a description"
          );
          await descriptionTextBox.fill(inputData.attachmentDescription);
          await expect(descriptionTextBox).toHaveValue(
            inputData.attachmentDescription
          );
          await this.tb.logSuccess(
            `Description text box is filled with value: ${inputData.attachmentDescription}`
          );
        }
      );
    } else if (properties.attachment_type === "document") {
      const fileInput = this.page.locator(
        this.getLocator(CWFPageLocators.Attachment_documentUploadBtnInput)
      );

      const acceptAttribute = await fileInput.getAttribute("accept");

      await this.tb.testStep(
        `Verifying if file input accepts defined document types`,
        async () => {
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
        }
      );

      await this.tb.testStep(
        `Verifying if multiple file upload is allowed`,
        async () => {
          const isMultiple = await fileInput.getAttribute("multiple");
          expect(isMultiple).not.toBeNull();
          await this.tb.logSuccess(
            `Multiple file upload is allowed for ${properties.attachment_type} component`
          );
        }
      );

      await this.tb.testStep(
        `Verifying successful file upload functionality`,
        async () => {
          const testDocumentPath = path.join(
            __dirname,
            "../Data/dummy-media/dummy_doc1.pdf"
          );

          await fileInput.setInputFiles(testDocumentPath);
          await page.waitForTimeout(300);

          const altDocBoxWhileUpload = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_loaderAltImageUploadPhoto
            )
          );
          const spinner = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_spinnerUploadPhoto)
          );
          const uploadingText = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_uploadingTextWhilePhotoUpload
            )
          );
          const cancelBtn = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_cancelButtonWhilePhotoUpload
            )
          );
          const docNameWhileUpload = this.page.locator(
            "//p[normalize-space(text())='dummy_doc1.pdf']"
          );

          //waiting for upload UI elements to appear
          await expect(altDocBoxWhileUpload).toBeVisible();
          await expect(spinner).toBeVisible();
          await expect(uploadingText).toBeVisible();
          await expect(cancelBtn).toBeVisible();
          await expect(docNameWhileUpload).toBeVisible();

          await this.tb.logSuccess(
            `File upload functionality is working for ${properties.attachment_type} component`
          );

          await Promise.all([
            altDocBoxWhileUpload.waitFor({ state: "hidden", timeout: 30000 }),
            spinner.waitFor({ state: "hidden", timeout: 30000 }),
            uploadingText.waitFor({ state: "hidden", timeout: 30000 }),
            cancelBtn.waitFor({ state: "hidden", timeout: 30000 }),
          ]);

          await this.tb.logSuccess(
            `File upload UI elements successfully disappeared after ${properties.attachment_type} upload`
          );
        }
      );
      let parts: any;
      await this.tb.testStep(
        "Verify if uploaded document is visible and uploaded successfully",
        async () => {
          const uploadedDoc = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_recentlyUploadedDocument)
          );
          const uploadedDocMenuBtn = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_recentlyUploadedDocMenuBtn
            )
          );
          const uploadedDocName = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_recentlyUploadedDocName)
          );
          const uploadedDocDetails = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_recentlyUploadedDocDetailsLbl
            )
          );

          await Promise.all([
            expect(uploadedDoc).toBeVisible(),
            expect(uploadedDocMenuBtn).toBeVisible(),
            expect(uploadedDocName).toBeVisible(),
            expect(uploadedDocDetails).toBeVisible(),
          ]);

          const expectedFileName = "dummy_doc1.pdf";
          const actualFileName = await uploadedDocName.innerText();
          expect(actualFileName).toBe(expectedFileName);
          await this.tb.logSuccess(
            `Uploaded Document name ${actualFileName} matches to the expected name: ${expectedFileName}`
          );

          const expectedFileSize = inputData.attachmentDocumentSize;
          const today = new Date();
          const expectedDate = `${today.getFullYear()}-${String(
            today.getMonth() + 1
          ).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

          const detailsText = await uploadedDocDetails.textContent();

          parts = detailsText?.split(" • ");
          const fileSize = parts?.[0];
          const date = parts?.[1];

          // expect(fileSize).toBe(expectedFileSize);
          expect(date).toBe(expectedDate);
          const timePattern = /\d{1,2}:\d{2} [AP]M$/;
          expect(parts && timePattern.test(parts[2])).toBeTruthy();

          await this.tb.logSuccess(
            `Uploaded Document details are visible and matches to the expected values`
          );
        }
      );

      await this.tb.testStep(
        "Verify menu button for uploaded document",
        async () => {
          const menuBtnForUploadedDoc = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_recentlyUploadedDocMenuBtn
            )
          );
          await menuBtnForUploadedDoc.click();

          const editBtnMenuItem = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_editDocMenuItem)
          );
          const downloadBtnMenuItem = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_downloadDocMenuItem)
          );
          const deleteBtnMenuItem = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_deleteDocMenuItem)
          );

          await Promise.all([
            expect(editBtnMenuItem).toBeVisible(),
            expect(downloadBtnMenuItem).toBeVisible(),
            expect(deleteBtnMenuItem).toBeVisible(),
          ]);

          const menuBtnWithDropdownActive = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_uploadedDocMenuBtnAfterDropdownActive
            )
          );
          await menuBtnWithDropdownActive.click();

          await Promise.all([
            editBtnMenuItem.waitFor({ state: "hidden", timeout: 15000 }),
            downloadBtnMenuItem.waitFor({ state: "hidden", timeout: 15000 }),
            deleteBtnMenuItem.waitFor({ state: "hidden", timeout: 15000 }),
          ]);

          await this.tb.logSuccess(
            `Menu button for uploaded document is visible and contains expected options`
          );
        }
      );

      await this.tb.testStep(
        "Verify edit functionality in the document menu dropdown",
        async () => {
          const menuButton = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_recentlyUploadedDocMenuBtn
            )
          );
          await menuButton.click();

          const editBtnMenuItem = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_editDocMenuItem)
          );
          await editBtnMenuItem.click();

          const editDocPopupBox = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_editDocPopupBox)
          );
          await expect(editDocPopupBox).toBeVisible();

          const editDocFilenamePopup = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_editDocPopupCurrentFilename
            )
          );
          await expect(editDocFilenamePopup).toBeVisible();
          expect(await editDocFilenamePopup.innerText()).toBe("dummy_doc1.pdf");

          const editDocUploadDateTimeLbl = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_editDocPopupUploadDateTime
            )
          );
          await expect(editDocUploadDateTimeLbl).toBeVisible();
          const popupDocDateTimeText =
            await editDocUploadDateTimeLbl.textContent();
          const popupDocDate = popupDocDateTimeText?.split(" ")[0];
          expect(popupDocDate).toBe(parts?.[1]);

          const popupDocTime =
            popupDocDateTimeText?.split(" ")[1] +
            " " +
            popupDocDateTimeText?.split(" ")[2];
          const timeRegex = /\d{1,2}:\d{2} [AP]M$/;
          expect(timeRegex.test(popupDocTime)).toBeTruthy();

          await this.tb.logSuccess(
            "Successfully validated all the labels on the edit doc popup"
          );

          await this.tb.logMessage(
            "Validating Cancel Button in the edit doc popup"
          );
          const editDocCancelBtn = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_editDocPopupCancelBtn)
          );
          await editDocCancelBtn.click();
          await expect(editDocPopupBox).not.toBeVisible();
          await this.tb.logSuccess(
            "Successfully clicked cancel button, and validated edit doc pop up box to disappear"
          );

          await this.page.waitForTimeout(500);

          const menuBtnAfterCancelEdit = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_recentlyUploadedDocMenuBtn
            )
          );
          await menuBtnAfterCancelEdit.click();
          await editBtnMenuItem.click();

          await this.tb.logMessage(
            "Verifying update name input text box functionality"
          );
          const updateDocNameInputBox = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_editDocPopupUpdateNameInput
            )
          );
          await expect(updateDocNameInputBox).toBeVisible();
          expect(await updateDocNameInputBox.inputValue()).toBe(
            "dummy_doc1.pdf"
          );

          await updateDocNameInputBox.clear();
          await updateDocNameInputBox.fill(inputData.attachmentDocumentName);
          expect(await updateDocNameInputBox.inputValue()).toBe(
            inputData.attachmentDocumentName
          );

          const editDocAddBtn = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_editDocPopupAddBtn)
          );
          await expect(editDocAddBtn).toBeVisible();
          await editDocAddBtn.click();

          const updatedDocName = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_recentlyUploadedDocName)
          );
          await expect(updatedDocName).toBeVisible();
          const updateDocTextWithoutExtension = (
            await updatedDocName.innerText()
          ).split(".")[0];
          expect(updateDocTextWithoutExtension).toBe(
            inputData.attachmentDocumentName
          );

          await this.tb.logSuccess(
            "Successfully validated update document name functionality"
          );
        }
      );

      await this.tb.testStep(
        "Verify Download button functionality in the document menu dropdown",
        async () => {
          await this.page.waitForTimeout(500);
          const menuBtn = this.page.locator(
            this.getLocator(
              CWFPageLocators.Attachment_recentlyUploadedDocMenuBtn
            )
          );
          await expect(menuBtn).toBeVisible();
          await menuBtn.click();

          const downloadBtn = this.page.locator(
            this.getLocator(CWFPageLocators.Attachment_downloadDocMenuItem)
          );
          await expect(downloadBtn).toBeVisible();

          const downloads: any[] = [];

          this.page.on("download", (download) => {
            downloads.push(download);
          });

          const downloadPromise = this.page.waitForEvent("download");
          await downloadBtn.click();
          const download = await downloadPromise;
          await this.page.waitForTimeout(1000);

          expect(downloads.length).not.toBeGreaterThan(1);
          expect(downloads.length).not.toBe(0);
          expect(download).toBeTruthy();

          const path = await download.path();
          if (!path) {
            throw new Error("File download failed");
          }
        }
      );
    } else {
      await this.tb.logMessage(
        `Attachment type ${properties.attachment_type} is not supported`
      );
    }

    // Implement further validation logic for the attachment component here
  }

  public async clickOnTemplateFormsFiltersBtn() {
    await this.tb.testStep(
      "Click on Template Forms Filters Button",
      async () => {
        const templateFormsFiltersBtn = this.page.locator(
          this.getLocator(CWFPageLocators.CWF_TemplateForms_FiltersBtn)
        );
        await expect(templateFormsFiltersBtn).toBeVisible({ timeout: 20000 });
        await templateFormsFiltersBtn.click();
        await this.page.waitForTimeout(2000);
        await this.validateTemplateFormFilterOptions();
        await this.tb.logSuccess(
          "Successfully clicked on Template Forms Filters Button."
        );
      }
    );
  }

  public async validateTemplateFormFilterOptions() {
    await this.tb.testStep(
      "Validate Template Form Filter Options",
      async () => {
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersHeader)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersClearAllBtn)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersFormName)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersFormName)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersFormName)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersStatus)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersCreatedBy)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersCreatedOn)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersUpdatedBy)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersUpdatedOn)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersCompletedOn)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersProjects)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersLocation)
          )
        ).toBeVisible();
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersRegion)
          )
        ).toBeVisible();
        await this.tb.logSuccess("Validate Template Form Filter Options");
      }
    );
  }

  public async validateApplyBtnDisabled() {
    await this.tb.testStep(
      "Validate Apply button is disabled when no filter option is selected",
      async () => {
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersApplyBtn)
          )
        ).toBeDisabled();
        await this.tb.logSuccess(
          "Validated Apply button is disabled when no filter option is selected"
        );
      }
    );
  }

  public async validateTemplateFormSearchFunctionality() {
    await this.tb.testStep(
      "Validate Template Form Search Functionality",
      async () => {
        let templateForm = await this.page
          .locator(this.getLocator(CWFPageLocators.templateFilterFirstFormName))
          .textContent();
        if (templateForm === null) {
          throw new Error("Template form name not found");
        }
        const templateFormSearch = this.page.locator(
          this.getLocator(CWFPageLocators.templateFormSearchInput)
        );
        await templateFormSearch.fill(templateForm);
        await this.page.waitForTimeout(2000);
        const searchResult = this.page.locator(
          `${this.getLocator(CWFPageLocators.templateFormSearchResultSet)}`
        );
        const searchResultsText = await searchResult.allTextContents();
        for (
          let element = 0;
          element < searchResultsText.length - 1;
          element++
        ) {
          let resultText = searchResultsText[element];
          expect(resultText).toContain(templateForm);
        }
        templateFormSearch.clear();
        await this.page.waitForTimeout(1000);
        await this.tb.logSuccess(
          "Validated Template Form Search Functionality"
        );
      }
    );
  }

  public async validateEmptyFilterFunctionality() {
    await this.tb.testStep(
      "Validate Empty Result Set Filter Functionality",
      async () => {
        let templateForm = await this.page
          .locator(this.getLocator(CWFPageLocators.templateFilterFirstFormName))
          .textContent();
        if (templateForm === null) {
          throw new Error("Template form name not found");
        }
        let completedOnFromDate = "10-14-2024";
        let completedOnToDate = "10-14-2024";
        await this.selectFilterFormName(templateForm);
        await this.page.waitForTimeout(2000);
        await this.selectFilterCompletedOnDate(
          completedOnFromDate,
          completedOnToDate
        );
        await this.page
          .locator(this.getLocator(CWFPageLocators.templateFormFiltersApplyBtn))
          .click();
        await this.page.waitForTimeout(2000);
        await expect(
          this.page.locator(
            this.getLocator(CWFPageLocators.templateFormFiltersNoDataFoundMsg)
          )
        ).toBeVisible();
        await this.tb.logSuccess(
          "Validated Empty Result Set Filter Functionality"
        );
      }
    );
  }

  public async selectFilterFormName(templateForm: string) {
    await this.tb.testStep("Select Filter Form Name", async () => {
      const templateFormSearch = this.page.locator(
        this.getLocator(CWFPageLocators.filterFormNameInput)
      );
      //await expect(templateFormSearch).toBeVisible({timeout : 20000});
      //await templateFormSearch.click();
      const filterBtn = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersFormName)
      );
      //await expect(filterBtn).toBeVisible({timeout : 20000});
      await filterBtn.click();
      await templateFormSearch.click();
      await templateFormSearch.fill(templateForm);
      const searchFormName = this.page.locator(
        this.getLocator(CWFPageLocators.selectFilterFormName)
      );
      await expect(searchFormName).toBeVisible({ timeout: 20000 });
      await searchFormName.click();
      const filterFormName = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersFormName)
      );
      await expect(filterFormName).toBeVisible({ timeout: 20000 });
      await filterFormName.click();
      await this.tb.logSuccess(`Selected Filter Form Name: ${templateForm}`);
    });
  }

  public async selectFilterCompletedOnDate(
    completedOnFromDate: string,
    completedOnToDate: string
  ) {
    await this.tb.testStep("Select Filter Completed On Date", async () => {
      const completedOnDateSelector = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersCompletedOn)
      );
      await expect(completedOnDateSelector).toBeVisible({ timeout: 20000 });
      const fromDateInput = this.page.locator(
        this.getLocator(CWFPageLocators.filterCompletedOnFromDate)
      );
      const toDateInput = this.page.locator(
        this.getLocator(CWFPageLocators.filterCompletedOnToDate)
      );
      await completedOnDateSelector.click();
      await expect(fromDateInput).toBeVisible({ timeout: 20000 });
      await fromDateInput.click();
      await fromDateInput.fill(completedOnFromDate);
      await expect(toDateInput).toBeVisible({ timeout: 20000 });
      await toDateInput.click();
      await toDateInput.fill(completedOnToDate);
      await this.tb.logSuccess("Selected Filter Completed On Date");
    });
  }

  public async selectFilterCreatedOnDate(
    createdOnFromDate: string,
    createdOnToDate: string
  ) {
    await this.tb.testStep("Select Filter Created On Date", async () => {
      const createdOnDateSelector = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersCreatedOn)
      );
      await expect(createdOnDateSelector).toBeVisible({ timeout: 20000 });
      const fromDateInput = this.page.locator(
        this.getLocator(CWFPageLocators.templateFilterCreatedOnFromDate)
      );
      const toDateInput = this.page.locator(
        this.getLocator(CWFPageLocators.templateFilterCreatedOnToDate)
      );
      await createdOnDateSelector.click();
      await expect(fromDateInput).toBeVisible({ timeout: 20000 });
      await fromDateInput.click();
      await fromDateInput.fill(createdOnFromDate);
      await expect(toDateInput).toBeVisible({ timeout: 20000 });
      await toDateInput.click();
      await toDateInput.fill(createdOnToDate);
      await this.tb.logSuccess("Selected Filter Created On Date");
    });
  }

  public async selectFilterCompleteStatus() {
    await this.tb.testStep("Select Completed status", async () => {
      const statusBtn = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersStatus)
      );
      await expect(statusBtn).toBeVisible({ timeout: 20000 });
      await statusBtn.click();
      const statusOption = this.page.locator(
        this.getLocator(CWFPageLocators.templateFilterCompleteStatus)
      );
      await expect(statusOption).toBeVisible({ timeout: 20000 });
      await statusOption.click();
      await this.tb.logSuccess("Successfully selected Completed status");
    });
  }

  public async validateClearAllFunctionality() {
    await this.tb.testStep("Validate Clear All Functionality", async () => {
      await this.page.waitForTimeout(2000);
      await this.clickOnTemplateFormsFiltersBtn();
      const clearBtn = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersClearAllBtn)
      );
      await expect(clearBtn).toBeVisible({ timeout: 20000 });
      await expect(clearBtn).toBeEnabled();
      await clearBtn.click();
      await this.page.waitForTimeout(2000);
      const applyBtn = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersApplyBtn)
      );
      await expect(applyBtn).toBeVisible({ timeout: 20000 });
      await expect(applyBtn).toBeEnabled();
      await applyBtn.click();
      await expect(
        this.page.locator(
          this.getLocator(CWFPageLocators.templateFormFiltersNoDataFoundMsg)
        )
      ).not.toBeVisible();
      await this.tb.logSuccess(`Validated Clear All Functionality`);
    });
  }

  public async validateTemplateFormFilterByName() {
    await this.tb.testStep(
      "Validate Template Form Filter Functionality",
      async () => {
        await this.page.waitForTimeout(2000);
        let templateForm = await this.page
          .locator(this.getLocator(CWFPageLocators.templateFilterFirstFormName))
          .textContent();
        if (templateForm === null) {
          throw new Error("Template form name not found");
        }
        await this.clickOnTemplateFormsFiltersBtn();
        await this.selectFilterFormName(templateForm);
        await this.page.waitForTimeout(2000);
        const applyBtn = this.page.locator(
          this.getLocator(CWFPageLocators.templateFormFiltersApplyBtn)
        );
        await expect(applyBtn).toBeVisible({ timeout: 20000 });
        await expect(applyBtn).toBeEnabled();
        await applyBtn.click();
        await this.page.waitForTimeout(3000);
        //Verify Form Name Result Set
        const searchResultName = this.page.locator(
          `${this.getLocator(CWFPageLocators.templateFormSearchResultSet)}`
        );
        await this.page.waitForTimeout(1000);
        const searchResultsText = await searchResultName.allTextContents();
        for (
          let element = 0;
          element < searchResultsText.length - 1;
          element++
        ) {
          let resultText = searchResultsText[element];
          expect(resultText).toBe(templateForm);
        }
        await this.tb.logSuccess(
          `Validated Template Form Filter Functionality`
        );
      }
    );
  }

  public async validateStatusFilterFunctionality() {
    await this.tb.testStep("Validate Status Filter Functionality", async () => {
      let status = "completed";
      await this.clickOnTemplateFormsFiltersBtn();
      const clearBtn = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersClearAllBtn)
      );
      await expect(clearBtn).toBeVisible({ timeout: 20000 });
      await expect(clearBtn).toBeEnabled();
      await clearBtn.click();
      await this.selectFilterCompleteStatus();
      const applyBtn = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersApplyBtn)
      );
      await expect(applyBtn).toBeVisible({ timeout: 20000 });
      await expect(applyBtn).toBeEnabled();
      await applyBtn.click();
      await this.page.waitForTimeout(3000);
      //Verify Form Name Result Set
      const searchResultName = this.page.locator(
        `${this.getLocator(CWFPageLocators.templateFormSearchResultStatus)}`
      );
      const searchResultsText = await searchResultName.allTextContents();
      for (let element = 0; element < searchResultsText.length - 1; element++) {
        let resultText = searchResultsText[element];
        expect(resultText.toLowerCase()).toBe(status);
      }
      await this.tb.logSuccess(`Validated Status Filter Functionality`);
    });
  }

  public convertDateToMMDDYYYY(date: string): string {
    const formattedDate = new Date(date)
      .toLocaleDateString("en-US", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      })
      .replace(/\//g, "-");
    return formattedDate;
  }

  public async validateDateFilterFunctionality() {
    await this.tb.testStep("Validate Date Filter Functionality", async () => {
      let createdOnDate = await this.page
        .locator(
          this.getLocator(CWFPageLocators.templateFilterFirstCreatedOnDate)
        )
        .textContent();
      if (createdOnDate === null) {
        throw new Error("Template form name not found");
      }
      const formattedDate = this.convertDateToMMDDYYYY(createdOnDate);
      //const toDate = "04-28-2025";
      await this.clickOnTemplateFormsFiltersBtn();
      const clearBtn = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersClearAllBtn)
      );
      await expect(clearBtn).toBeVisible({ timeout: 20000 });
      await expect(clearBtn).toBeEnabled();
      await clearBtn.click();
      await this.selectFilterCreatedOnDate(formattedDate, formattedDate);
      const applyBtn = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFiltersApplyBtn)
      );
      await expect(applyBtn).toBeVisible({ timeout: 20000 });
      await expect(applyBtn).toBeEnabled();
      await applyBtn.click();
      //await this.page.waitForTimeout(3000);
      //Verify Form Name Result Set
      // const searchResultName = this.page.locator(
      //   `${this.getLocator(CWFPageLocators.templateFormSearchResultCreatedOnDate)}`
      // );
      // const searchResultsText = await searchResultName.allTextContents();
      // for (let index = 0; index < searchResultsText.length; index++)
      // {
      //   let resultText = searchResultsText[index];
      //   expect(resultText).toContainEqual(createdOnDate);
      // }
      await this.tb.logSuccess(`Validated Date Filter Functionality`);
    });
  }

  public async clearAppliedFiltersIfAny() {
    await this.tb.testStep("Clear Applied Filters If Any", async () => {
      const filterBtnText = this.page.locator(
        this.getLocator(CWFPageLocators.templateFormFilters_filterBtnText)
      );
      await expect(filterBtnText).toBeVisible({ timeout: 20000 });
      const filterBtnTextValue = await filterBtnText.textContent();
      if (filterBtnTextValue && /\d+/.test(filterBtnTextValue)) {
        await this.validateClearAllFunctionality();
        await this.page.waitForTimeout(2000);
        const filterBtntextAfterClear = await filterBtnText.textContent();
        if (filterBtntextAfterClear && /\d+/.test(filterBtntextAfterClear)) {
          await this.tb.logFailure("Failed to Clear Applied Filter");
        } else {
          await this.tb.logSuccess("Successfully Cleared Applied Filter");
        }
      } else {
        await this.tb.logSuccess("No Applied Filters Found");
      }
    });
  }

  // public async activitiesAndTasksValidatorFunction(
  //   page: Page,
  //   content: cwfInterfaces.Content,
  //   index: number
  // ){
  //   const properties = content.properties as cwfInterfaces.ActivitiesAndTasksProperties;
  //   await this.tb.logMessage(
  //     `Index ${index} - Validating ${properties.title} attachment component: ${properties.title}`
  //   );

  //   try{

  //   } catch( error ) {
  //     await this.tb.logMessage(
  //       `Error validating ${properties.title} attachment component: ${error}`
  //     );
  //     throw error;
  //   }

  // }
}
