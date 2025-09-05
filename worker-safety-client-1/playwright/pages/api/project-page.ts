import type { Page, APIRequestContext } from "@playwright/test";
import { faker } from "@faker-js/faker";
import { extractProp } from "../../framework/graphql-client";
import {
  queryGetProjects,
  queryProjectTypesLibrary,
} from "../../framework/queries";
import {
  mutationCreateProject,
  mutationDeleteProject,
} from "../../framework/mutations";
import {
  queryGetProjectsVars,
  mutationCreateProjectVarsTyped,
  mutationDeleteProjectVars,
} from "../../framework/variables";
import { getFormattedDate } from "../../framework/common-actions";
import { BaseAPIPage } from "./base-api-page";
import { ManagersAPIPage } from "./managers-page";
import { SupervisorsAPIPage } from "./supervisors-page";
import { ContractorsAPIPage } from "./contractors-page";
import { DivisionsAPIPage } from "./divisions-page";
import { RegionsAPIPage } from "./regions-page";

export class ProjectAPIPage extends BaseAPIPage {
  readonly managersAPIPage = new ManagersAPIPage(this.page, this.request);
  readonly supervisorsAPIPage = new SupervisorsAPIPage(this.page, this.request);
  readonly contractorsAPIPage = new ContractorsAPIPage(this.page, this.request);
  readonly divisionsAPIPage = new DivisionsAPIPage(this.page, this.request);
  readonly regionsAPIPage = new RegionsAPIPage(this.page, this.request);

  tokenAPI: string;
  projectsIds: string[];
  projectsNames: string[];
  projectTypesLibraryIds: string[];
  projectTypesLibraryNames: string[];
  createdProjectId: string[];
  createdProjectName: string[];
  createdProjectLocationId: string[];
  tasksLibraryId: string[];
  tasksLibraryName: string[];
  hazardsLibraryId: string[];
  hazardsLibraryName: string[];
  controlsLibraryId: string[];
  controlsLibraryName: string[];

  // Project Test Data
  projectName: string =
    `Automation dummy project API ` + faker.datatype.number();
  externalKey: string = faker.datatype.number().toString();
  status = "ACTIVE";
  startDate: string = getFormattedDate(10, "past");
  endDate: string = getFormattedDate(10, "future");
  locationName: string = faker.address.streetAddress(true).toString();
  latitude: string = faker.address.latitude(46, 30).toString();
  longitude: string = faker.address.longitude(-73, -123).toString();
  activityName = "Civil work";
  activityStatus = "NOT_STARTED";
  activityStartDate: string = getFormattedDate(1, "past");
  activityEndDate: string = getFormattedDate(1, "future");

  constructor(page: Page, request: APIRequestContext) {
    super(page, request);
  }

  /**
   * Function that create a project
   */
  async createProject() {
    await this.prepareProjectData();
    await this.mutationCreateProject(
      this.projectName,
      this.externalKey,
      this.status,
      this.startDate,
      this.endDate,
      this.locationName,
      this.latitude,
      this.longitude
    );
  }

  /**
   * Function that gets all the required data to create a project
   */
  async prepareProjectData() {
    await this.managersAPIPage.getManagers();
    await this.supervisorsAPIPage.getSupervisors();
    await this.contractorsAPIPage.getContractors();
    await this.divisionsAPIPage.getDivisionsLibrary();
    await this.regionsAPIPage.getRegionsLibrary();
    await this.getProjectTypeLibrary();
  }

  /**
   * Function that gets and stores the Project Types
   */
  async getProjectTypeLibrary() {
    const response = await this.graphQLReqWithTestReq(
      "ProjectTypesLibrary",
      queryProjectTypesLibrary
    );
    const {
      data: { projectTypesLibrary },
    } = JSON.parse(await response.text());
    this.projectTypesLibraryIds = extractProp(projectTypesLibrary, "id");
    this.projectTypesLibraryNames = extractProp(projectTypesLibrary, "name");
  }

  /**
   * Function that gets and stores the Project details
   */
  async getProject(searchStr: string) {
    const response = await this.graphQLReqWithTestReq(
      "getProjectIds",
      queryGetProjects,
      queryGetProjectsVars(searchStr)
    );
    const {
      data: { projects },
    } = JSON.parse(await response.text());
    this.projectsIds = extractProp(projects, "id");
    this.projectsNames = extractProp(projects, "name");
  }

  /**
   * Function that Creates a Project
   */
  async mutationCreateProject(
    projectName: string,
    externalKey: string,
    status: string,
    startDate: string,
    endDate: string,
    locationName: string,
    latitude: string,
    longitude: string
  ) {
    const response = await this.graphQLReqWithTestReq(
      "createProject",
      mutationCreateProject,
      mutationCreateProjectVarsTyped(
        projectName,
        externalKey,
        this.projectTypesLibraryIds[0],
        status,
        startDate,
        endDate,
        this.divisionsAPIPage.divisionsLibraryIds[0],
        this.regionsAPIPage.regionsLibraryIds[0],
        this.managersAPIPage.managerIds[0],
        this.supervisorsAPIPage.supervisorIds[0],
        this.contractorsAPIPage.contractorIds[0],
        locationName,
        latitude,
        longitude
      )
    );
    const {
      data: { createProject },
    } = JSON.parse(await response.text());

    this.createdProjectId = extractProp(createProject, "id");
    this.createdProjectName = extractProp(createProject, "name");

    const {
      data: {
        createProject: { locations },
      },
    } = JSON.parse(await response.text());
    this.createdProjectLocationId = extractProp(locations, "id");
  }

  /**
   * Function that Deletes one or multiple Projects by Id
   */
  async mutationDeleteProjectsByIds(projectsIds: string[]) {
    for (let index = 0; index < projectsIds.length; index++) {
      await this.graphQLReqWithTestReq(
        "deleteProject",
        mutationDeleteProject,
        mutationDeleteProjectVars(projectsIds[index])
      );
    }
  }

  /**
   * Function that Deletes one Project by Id
   */
  async mutationDeleteProjectsById(projectId: string) {
    await this.graphQLReqWithTestReq(
      "deleteProject",
      mutationDeleteProject,
      mutationDeleteProjectVars(projectId)
    );
  }
}
