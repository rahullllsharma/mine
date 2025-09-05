import type { Page, APIRequestContext } from "@playwright/test";
import { extractProp } from "../../framework/graphql-client";
import { queryGetManagers } from "../../framework/queries";
import { BaseAPIPage } from "./base-api-page";

export class ManagersAPIPage extends BaseAPIPage {
  managerIds: string[];
  managerNames: string[];

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that gets and stores the Managers
   */
  async getManagers() {
    const response = await this.graphQLReqWithTestReq(
      "Managers",
      queryGetManagers
    );
    const {
      data: { managers },
    } = JSON.parse(await response.text());
    this.managerIds = extractProp(managers, "id");
    this.managerNames = extractProp(managers, "name");
  }
}
