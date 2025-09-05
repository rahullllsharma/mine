import type { Page, APIRequestContext } from "@playwright/test";
import { extractProp } from "../../framework/graphql-client";
import { queryRegionsLibrary } from "../../framework/queries";
import { BaseAPIPage } from "./base-api-page";

export class RegionsAPIPage extends BaseAPIPage {
  divisionsLibraryIds: string[];
  divisionsLibraryNames: string[];
  regionsLibraryIds: string[];
  regionsLibraryNames: string[];

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that gets and stores the Regions
   */
  async getRegionsLibrary() {
    const response = await this.graphQLReqWithTestReq(
      "RegionsLibrary",
      queryRegionsLibrary
    );
    const {
      data: { regionsLibrary },
    } = JSON.parse(await response.text());
    this.regionsLibraryIds = extractProp(regionsLibrary, "id");
    this.regionsLibraryNames = extractProp(regionsLibrary, "name");
  }
}
