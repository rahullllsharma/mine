import type { Page, APIRequestContext } from "@playwright/test";
import { extractProp } from "../../framework/graphql-client";
import { queryGetControlsLibrary } from "../../framework/queries";
import { queryGetControlsLibraryVars } from "../../framework/variables";
import { BaseAPIPage } from "./base-api-page";

export class ControlsAPIPage extends BaseAPIPage {
  controlsLibraryId: string[];
  controlsLibraryName: string[];

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that gets and stores the tasks
   */
  async getControlsByHazardId(hazardId: string) {
    const response = await this.graphQLReqWithTestReq(
      "ControlsLibrary",
      queryGetControlsLibrary,
      queryGetControlsLibraryVars(hazardId, "TASK")
    );
    const {
      data: { controlsLibrary },
    } = JSON.parse(await response.text());
    this.controlsLibraryId = extractProp(controlsLibrary, "id");
    this.controlsLibraryName = extractProp(controlsLibrary, "name");
  }
}
