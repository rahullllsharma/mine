import type { APIRequestContext, Page } from "@playwright/test";
import { getFormattedDate } from "../../framework/common-actions";
import { mutationCreateActivity } from "../../framework/mutations";
import { mutationCreateActivitySeedTenTasksVarsTyped } from "../../framework/variables";
import { BaseAPIPage } from "./base-api-page";
import { ControlsAPIPage } from "./controls-page";
import { HazardsAPIPage } from "./hazards-page";
import { TasksAPIPage } from "./tasks-page";

export class ActivityAPIPage extends BaseAPIPage {
  readonly tasksAPIPage = new TasksAPIPage(this.page, this.request);
  readonly hazardsAPIPage = new HazardsAPIPage(this.page, this.request);
  readonly controlsAPIPage = new ControlsAPIPage(this.page, this.request);

  // Test Data
  // activityName = "Civil work";
  // activityName = "Trenching / excavating";
  // activityName = "Welding / joining";
  activityName = "Field coating";
  activityStatus = "NOT_STARTED";
  activityStartDate: string = getFormattedDate(1, "past");
  activityEndDate: string = getFormattedDate(1, "future");

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that creates one or more activities
   */
  async createActivityByLocationId(locationId: string, seedTasks: any) {
    await this.prepareActivityData();
    await this.mutationCreateActivityByLocationId(locationId, seedTasks);
  }

  /**
   * Function that gets all the required data to create an activity
   */
  async prepareActivityData() {
    await this.tasksAPIPage.getTasksLibrary();
    await this.hazardsAPIPage.getHazardsByTask(
      this.tasksAPIPage.tasksLibraryId[0]
    );
    await this.controlsAPIPage.getControlsByHazardId(
      this.hazardsAPIPage.hazardsLibraryId[0]
    );
  }

  /**
   * Function that calls the createActivity mutation by Project location
   */
  async mutationCreateActivityByLocationId(
    projectLocationId: string,
    seedTasks: any
  ) {
    const _response = await this.graphQLReqWithTestReq(
      "CreateActivity",
      mutationCreateActivity,
      mutationCreateActivitySeedTenTasksVarsTyped(
        this.activityStartDate,
        projectLocationId,
        this.activityName,
        this.activityEndDate,
        this.activityStatus,
        seedTasks
      )
    );
  }
}
