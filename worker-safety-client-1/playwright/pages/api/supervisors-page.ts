import type { Page, APIRequestContext } from "@playwright/test";
import { extractProp } from "../../framework/graphql-client";
import { queryGetSupervisors } from "../../framework/queries";
import { BaseAPIPage } from "./base-api-page";

export class SupervisorsAPIPage extends BaseAPIPage {
  supervisorIds: string[] = [];
  supervisorFirstNames: string[];
  supervisorLastNames: string[];
  supervisorNames: string[] = [];

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that gets and stores the Supervisors
   */
  async getSupervisors() {
    const response = await this.graphQLReqWithTestReq(
      "Supervisors",
      queryGetSupervisors
    );
    const {
      data: { supervisors },
    } = JSON.parse(await response.text());
    this.supervisorIds = extractProp(supervisors, "id");
    this.supervisorFirstNames = extractProp(supervisors, "firstName");
    this.supervisorLastNames = extractProp(supervisors, "lastName");
    for (let index = 0; index < this.supervisorFirstNames.length; index++) {
      this.supervisorNames[index] =
        this.supervisorLastNames[index] + " " + this.supervisorLastNames[index];
    }
  }
}
