import type { Locator } from "@playwright/test";
import { faker } from "@faker-js/faker";
import { expect } from "@playwright/test";
import { BasePage } from "../base-page";

// Test Data Variables
const streetAddress = faker.address.streetAddress(true);
const latitudeValue = faker.address.latitude(46, 30);
const longitudeValue = faker.address.longitude(-73, -123);
const locationAddrPH = "Ex\\. 3rd street between Main and Broadway";
const _latitudePH = "Ex\\. 34\\.054913";
const _longitudePH = "Ex\\. -62\\.136754";

export class ProjectLocationsPage extends BasePage {
  // Selectors
  readonly locationsHeader: Locator = this.getByTestIdText(
    "location-header",
    `${process.env.LOCATION_LABEL}(s)`
  );
  readonly locationName: Locator = this.getByTestIdLabelText(
    "location-name",
    `${process.env.LOCATION_LABEL} Name *`
  );
  readonly locationPH: Locator = this.getInputByPlaceHolder(
    `${locationAddrPH}`
  );
  readonly locationLatitude: Locator = this.getByTestIdLabelText(
    "location-latitude",
    `Latitude *`
  );
  readonly locationLatitudeInput: Locator = this.getByTestId(
    "location-latitude >> input"
  );
  readonly locationLongitude: Locator = this.getByTestIdLabelText(
    "location-longitude",
    `Longitude *`
  );
  readonly locationLongitudeInput: Locator = this.getByTestId(
    "location-longitude >> input"
  );
  readonly locationAssignedPersonText: Locator = this.getByTestIdLabelText(
    "location-primary-assigned-person",
    `Primary ${process.env.LOCATION_SUPERVISOR_LABEL}`
  );
  readonly locationAssignedPersonSelect: Locator = this.getByTestId(
    "location-primary-assigned-person >> div[role='button']"
  );
  readonly locationAssignedPersonOpt: Locator = this.getDivOptByText(
    `${process.env.PW_SUPERVISOR}`
  );

  /**
   * Update Location(s) section
   */
  public async updateLocations() {
    try {
      console.log(`Update Locations`);
      await expect(this.locationsHeader).toBeVisible();
      await expect(this.locationName).toBeVisible();

      await this.locationPH.fill(streetAddress);

      await expect(this.locationLatitude).toBeVisible();
      await this.locationLatitudeInput.fill(latitudeValue);
      await expect(this.locationLongitude).toBeVisible();
      await this.locationLongitudeInput.fill(longitudeValue);

      await expect(this.locationAssignedPersonText).toBeVisible();
      await this.locationAssignedPersonSelect.click();
      await this.locationAssignedPersonOpt.click();
    } catch (error) {
      console.log(error);
    }
  }
}
