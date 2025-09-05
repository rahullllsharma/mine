import { test } from "../framework/base-fixtures";

let numOfIterations = 1;
const projectsEachIter = 10;
const projectNameToSearch = "9999";

test.describe.skip("Delete all automation projects using the API", () => {
  test.skip(({ browserName }) => browserName !== "chromium", "Chromium only!");

  test("Get the list of automation projects", async ({ projectAPIPage }) => {
    console.log("Get all automation projects Ids...");
    await projectAPIPage.getProject(projectNameToSearch);
    console.log(`Got ${projectAPIPage.projectsIds.length} projects`);
    numOfIterations = projectAPIPage.projectsIds.length / projectsEachIter;
    console.log(`numOfIterations needed = ${numOfIterations.toFixed(0)}`);
  });

  for (let index1 = 1; index1 <= numOfIterations; index1++) {
    test(`User can execute deleteProject mutation ${index1}`, async ({
      projectAPIPage,
    }) => {
      console.log("Deleting all automation projects...");
      await projectAPIPage.getProject(projectNameToSearch);
      console.log(`Got ${projectAPIPage.projectsIds.length} projects`);
      for (let index2 = 0; index2 < projectsEachIter; index2++) {
        await projectAPIPage.mutationDeleteProjectsById(
          projectAPIPage.projectsIds[index2]
        );
        console.log(
          `Project with UUID ${projectAPIPage.projectsIds[index2]} is deleted`
        );
      }
    });
  }
});
