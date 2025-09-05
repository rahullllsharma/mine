import type { APIRequestContext, Page } from "@playwright/test";
import { extractProp } from "../../framework/graphql-client";
import { queryGetTasksLibrary } from "../../framework/queries";
import { BaseAPIPage } from "./base-api-page";

export class TasksAPIPage extends BaseAPIPage {
  tasksLibraryId: string[];
  tasksLibraryName: string[];

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that gets and stores the tasks
   */
  async getTasksLibrary() {
    const response = await this.graphQLReqWithTestReq(
      "TasksLibrary",
      queryGetTasksLibrary
    );
    const {
      data: { tasksLibrary },
    } = JSON.parse(await response.text());
    this.tasksLibraryId = extractProp(tasksLibrary, "id");
    this.tasksLibraryName = extractProp(tasksLibrary, "name");
    const {
      data: {
        // tasksLibrary: [{ hazards }],
      },
    } = await response.json();
    const {
      data: {
        tasksLibrary: [
          {
            // hazards: [{ controls }],
          },
        ],
      },
    } = await response.json();
  }
}
