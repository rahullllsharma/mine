import type { Page, APIRequestContext } from "@playwright/test";
import { extractProp } from "../../framework/graphql-client";
import { queryGetContractors } from "../../framework/queries";
import { BaseAPIPage } from "./base-api-page";

export class ContractorsAPIPage extends BaseAPIPage {
  contractorIds: string[];
  contractorNames: string[];

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that gets and stores the Contractors
   */
  async getContractors() {
    const response = await this.graphQLReqWithTestReq(
      "Contractors",
      queryGetContractors
    );
    const {
      data: { contractors },
    } = JSON.parse(await response.text());
    this.contractorIds = extractProp(contractors, "id");
    this.contractorNames = extractProp(contractors, "name");
  }
}
