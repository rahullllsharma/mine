import {
  getAPIAccessToken,
  graphQlAxiosRequest,
} from "../../playwright/framework/graphql-client";
import { queryGetProjects } from "../../playwright/framework/queries";
import { mutationDeleteProject } from "../../playwright/framework/mutations";

import configs from "./configs.json";
import { setupScriptEnv } from "./setup";

setupScriptEnv();

getAPIAccessToken().then(async token => {
  const { projectNamePrefix } = configs.projects;

  const projectListResponse = await graphQlAxiosRequest(
    token,
    "getProjectIds",
    queryGetProjects,
    {
      search: projectNamePrefix,
    }
  );

  if (!projectListResponse.data?.projects) {
    return;
  }

  const {
    data: { projects },
  } = projectListResponse;

  for (let i = 0; i < projects.length; i++) {
    const { id: projectId } = projects[i];

    const response = await graphQlAxiosRequest(
      token,
      "deleteProject",
      mutationDeleteProject,
      {
        deleteProjectId: projects[i].id,
      }
    );

    console.log("Query status: ", response.status);
    console.log("Project deleted: ", response.ok);
    console.log("Project id: ", projectId);
  }
});
