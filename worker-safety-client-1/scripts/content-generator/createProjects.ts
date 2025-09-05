import {
  getAPIAccessToken,
  graphQlAxiosRequest,
} from "../../playwright/framework/graphql-client";

import {
  queryGetManagers,
  queryGetSupervisors,
  queryGetContractors,
  queryProjectTypesLibrary,
  queryDivisionsLibrary,
  queryRegionsLibrary,
  queryAllActivities,
} from "../../playwright/framework/queries";
import {
  mutationCreateActivity,
  mutationCreateProject,
} from "../../playwright/framework/mutations";

import configs from "./configs.json";
import { setupScriptEnv } from "./setup";
import { createActivityData, createProjectData } from "./utils";

setupScriptEnv();

const delay = (ms: number) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

console.time("timer");
getAPIAccessToken().then(token => {
  Promise.all([
    graphQlAxiosRequest(token, "Managers", queryGetManagers),
    graphQlAxiosRequest(token, "Supervisors", queryGetSupervisors),
    graphQlAxiosRequest(token, "Contractors", queryGetContractors),
    graphQlAxiosRequest(token, "ProjectTypesLibrary", queryProjectTypesLibrary),
    graphQlAxiosRequest(token, "DivisionsLibrary", queryDivisionsLibrary),
    graphQlAxiosRequest(token, "RegionsLibrary", queryRegionsLibrary),
    graphQlAxiosRequest(token, "AllActivities", queryAllActivities),
  ]).then(async response => {
    const [
      managersData,
      supervisorsData,
      contractorsData,
      projectTypesData,
      divisionsData,
      regionsData,
      allActivitiesData,
    ] = response.map(entry => entry.data ?? null);

    const {
      newEntries,
      activitiesPerProject,
      chunks,
      chunkDelay,
      chunkFormationDelay,
      projectNamePrefix,
    } = configs.projects;

    let projectList = [];
    const projectEntries = [];

    for (let i = 0; i < newEntries; i++) {
      const projectData = createProjectData({
        managersData,
        supervisorsData,
        contractorsData,
        projectTypesData,
        divisionsData,
        regionsData,
        projectNamePrefix,
      });

      // form promise array
      projectList.push(
        graphQlAxiosRequest(
          token,
          "createProject",
          mutationCreateProject,
          projectData
        )
      );

      // check if it's chuncking time
      // form array of  promise arrays
      if ((i + 1) % chunks === 0) {
        projectEntries.push(projectList);
        projectList = [];
      }

      await delay(chunkFormationDelay);
    }

    if (projectList.length) {
      projectEntries.push(projectList);
    }

    const resolvedPromises = [];

    while (projectEntries.length) {
      // remove the nested array
      const [projectsChunk] = projectEntries.splice(0, 1);
      const resolvePromisesChunk = await Promise.all(projectsChunk);
      resolvedPromises.push(...resolvePromisesChunk);

      resolvePromisesChunk.forEach(async entry => {
        console.log("Project Query status: ", entry.status);
        console.log("Project created: ", entry.ok);
        console.log("Project id: ", entry.data?.createProject?.id);
        console.log(
          "Project location id: ",
          entry.data?.createProject?.locations[0].id
        );

        const projectLocationId = entry.data?.createProject?.locations[0].id;

        for (let index = 0; index < activitiesPerProject; index++) {
          const activityData = createActivityData({
            projectLocationId,
            allActivitiesData,
          });

          // Add Activity
          const activityResponse = await graphQlAxiosRequest(
            token,
            "CreateActivity",
            mutationCreateActivity,
            activityData
          );
          console.log("Activity Query status: ", activityResponse.status);
          console.log("Activity created: ", activityResponse.ok);
          console.log(
            "Activity id: ",
            activityResponse.data?.createActivity.id
          );
        }
      });

      await delay(chunkDelay);
    }
  });
});

console.timeEnd("timer");
