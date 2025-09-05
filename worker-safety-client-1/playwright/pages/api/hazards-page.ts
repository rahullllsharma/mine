import type { Page, APIRequestContext } from "@playwright/test";
import { extractProp } from "../../framework/graphql-client";
import { queryGetHazardsLibrary } from "../../framework/queries";
import { queryGetHazardsLibraryVars } from "../../framework/variables";
import { BaseAPIPage } from "./base-api-page";

export class HazardsAPIPage extends BaseAPIPage {
  hazardsLibraryId: string[];
  hazardsLibraryName: string[];

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that gets and stores the tasks
   */
  async getHazardsByTask(taskId: string) {
    const response = await this.graphQLReqWithTestReq(
      "HazardsLibrary",
      queryGetHazardsLibrary,
      queryGetHazardsLibraryVars(taskId, "TASK")
    );
    const {
      data: { hazardsLibrary },
    } = JSON.parse(await response.text());
    this.hazardsLibraryId = extractProp(hazardsLibrary, "id");
    this.hazardsLibraryName = extractProp(hazardsLibrary, "name");
  }
}
