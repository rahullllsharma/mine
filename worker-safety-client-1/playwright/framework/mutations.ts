export const mutationCreateProject = `mutation createProject($project: CreateProjectInput!) {
  createProject(project: $project) {
    id
    name
    locations {
      id
    }
  }
}`;

export const mutationDeleteProject = `mutation deleteProject($deleteProjectId: UUID!) {
  deleteProject(id: $deleteProjectId)
}`;

export const mutationCreateActivity = `mutation CreateActivity($activityData: CreateActivityInput!) {
    createActivity(activityData: $activityData) {
      id
      name
    }
}`;
