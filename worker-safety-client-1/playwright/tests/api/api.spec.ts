import { test, expect } from "../../framework/base-fixtures";
import { parseEntities } from "../../../src/store/tenant/utils";
import {
  extractProp,
  getAPIAccessToken,
  graphQLRequest,
} from "../../framework/graphql-client";
import {
  queryPermissions,
  queryGetProjects,
  queryGetManagers,
  queryGetContractors,
  queryGetSupervisors,
  queryActivityTasks,
  queryHazardsControlsLibrary,
} from "../../framework/queries";
import {
  mutationCreateProject,
  mutationDeleteProject,
  mutationCreateActivity,
} from "../../framework/mutations";
import {
  queryGetProjectsVars,
  queryHazardsControlsLibraryVars,
  mutationCreateProjectVars,
  mutationDeleteProjectVars,
  mutationCreateActivityVars,
} from "../../framework/variables";
// import Permissions from "./../../../src/graphql/queries/permissions.gql";

// Variables
let tokenAPI;
let projectsIds;

test.beforeAll(async () => {
  console.log("Get the API token before executing the API tests...");
  tokenAPI = await getAPIAccessToken();
});

test.describe.skip("API", () => {
  test.skip(({ browserName }) => browserName !== "chromium", "Chromium only!");

  test("User can execute Permissions query", async ({ request }) => {
    const response = await graphQLRequest(
      request,
      tokenAPI,
      "Permissions",
      queryPermissions
    );
    expect(response.ok()).toBeTruthy();

    // Parsing Data Example
    const {
      data: {
        me: {
          tenant: {
            configurations: { entities },
          },
        },
      },
    } = JSON.parse(await response.text());

    console.log("entities=", entities);
    console.log("entitiesJSON=", JSON.stringify(entities));

    const entitiesObj = parseEntities(entities);
    const entitiesObjEntries = Object.fromEntries(entitiesObj);
    console.log("entitiesObj=", entitiesObjEntries);
    console.log(
      "entitiesObj.workPackage.defaultLabel=",
      entitiesObjEntries.workPackage.defaultLabel
    );
    console.log(
      "entitiesObj.workPackage.attributes=",
      entitiesObjEntries.workPackage.attributes
    );
  });

  test("User can execute Supervisors query", async ({ request }) => {
    const response = await graphQLRequest(
      request,
      tokenAPI,
      "Supervisors",
      queryGetSupervisors
    );
    expect(response.ok()).toBeTruthy();
    console.log("response", (await response.body()).toString());

    const {
      data: { supervisors },
    } = JSON.parse(await response.text());

    console.log("supervisors =========", JSON.stringify(supervisors));

    const supervisorIds = extractProp(supervisors, "id");

    console.log("IDs =========", JSON.stringify(supervisorIds));
  });

  test("User can execute Managers query", async ({ request }) => {
    const response = await graphQLRequest(
      request,
      tokenAPI,
      "Managers",
      queryGetManagers
    );
    expect(response.ok()).toBeTruthy();
    console.log("response", (await response.body()).toString());
  });

  test("User can execute Contractors query", async ({ request }) => {
    const response = await graphQLRequest(
      request,
      tokenAPI,
      "Contractors",
      queryGetContractors
    );
    expect(response.ok()).toBeTruthy();
    console.log("response", (await response.body()).toString());
  });

  test("User can execute createProject mutation", async ({ request }) => {
    for (let index = 0; index < 1; index++) {
      const response = await graphQLRequest(
        request,
        tokenAPI,
        "createProject",
        mutationCreateProject,
        mutationCreateProjectVars
      );
      expect(response.ok()).toBeTruthy();
      console.log("response", (await response.body()).toString());
    }
  });

  test("User can execute getProject", async ({ request }) => {
    const response = await graphQLRequest(
      request,
      tokenAPI,
      "getProjectIds",
      queryGetProjects,
      queryGetProjectsVars("Automation")
    );
    expect(response.ok()).toBeTruthy();
    console.log("response", (await response.body()).toString());

    const {
      data: { projects },
    } = JSON.parse(await response.text());

    projectsIds = extractProp(projects, "id");
    console.log("projectsIds =========", JSON.stringify(projectsIds));
  });

  test("User can execute deleteProject", async ({ request }) => {
    for (let index = 0; index < projectsIds.length; index++) {
      const response = await graphQLRequest(
        request,
        tokenAPI,
        "deleteProject",
        mutationDeleteProject,
        mutationDeleteProjectVars(projectsIds[index])
      );
      expect(response.ok()).toBeTruthy();
      console.log("response", (await response.body()).toString());
    }
  });

  test("User can execute ActivityTasks", async ({ request }) => {
    for (let index = 0; index < projectsIds.length; index++) {
      const response = await graphQLRequest(
        request,
        tokenAPI,
        "ActivityTasks",
        queryActivityTasks
      );
      expect(response.ok()).toBeTruthy();
      console.log("response", (await response.body()).toString());
    }
  });

  test("User can execute HazardsControlsLibrary", async ({ request }) => {
    const response = await graphQLRequest(
      request,
      tokenAPI,
      "HazardsControlsLibrary",
      queryHazardsControlsLibrary,
      queryHazardsControlsLibraryVars
    );
    expect(response.ok()).toBeTruthy();
    console.log("response", (await response.body()).toString());
  });

  test("User can execute mutationCreateActivity", async ({ request }) => {
    for (let index = 0; index < projectsIds.length; index++) {
      const response = await graphQLRequest(
        request,
        tokenAPI,
        "CreateActivity",
        mutationCreateActivity,
        mutationCreateActivityVars
      );
      expect(response.ok()).toBeTruthy();
      console.log("response", (await response.body()).toString());
    }
  });
});
