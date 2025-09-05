import type { Page, APIRequestContext } from "@playwright/test";
import { extractProp } from "../../framework/graphql-client";
import { queryDivisionsLibrary } from "../../framework/queries";
import { BaseAPIPage } from "./base-api-page";

export class DivisionsAPIPage extends BaseAPIPage {
  divisionsLibraryIds: string[];
  divisionsLibraryNames: string[];

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that gets and stores the Divisions
   */
  async getDivisionsLibrary() {
    const response = await this.graphQLReqWithTestReq(
      "DivisionsLibrary",
      queryDivisionsLibrary
    );
    const {
      data: { divisionsLibrary },
    } = JSON.parse(await response.text());
    this.divisionsLibraryIds = extractProp(divisionsLibrary, "id");
    this.divisionsLibraryNames = extractProp(divisionsLibrary, "name");
  }
}
