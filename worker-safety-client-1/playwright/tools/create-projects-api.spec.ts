import path from "path";
import fs from "fs";
import { faker } from "@faker-js/faker";
import { test } from "../framework/base-fixtures";
import { getFormattedDate } from "../framework/common-actions";

test.describe.skip("Create automation projects using the API", () => {
  test.skip(({ browserName }) => browserName !== "chromium", "Chromium only!");
  test.setTimeout(120000);

  const numOfIterations = 1;
  const projectsEachIter = 10;

  const seedTenTasks = JSON.parse(
    fs.readFileSync(
      path.join(__dirname, "../data/activityWithTasks.json"),
      "utf-8"
    )
  );

  for (let index1 = 1; index1 <= numOfIterations; index1++) {
    test(`User can execute createProject mutation ${index1}`, async ({
      prepareProjectDataAPIPage,
      activityAPIPage,
    }) => {
      for (let index2 = 0; index2 < projectsEachIter; index2++) {
        const increment: number = index2 + projectsEachIter * (index1 - 1);
        // const projectName = "Automation dummy project API " + increment;
        const projectName = 99990000 + increment;
        await prepareProjectDataAPIPage.mutationCreateProject(
          projectName.toString(),
          faker.datatype.number().toString(),
          "PENDING",
          getFormattedDate(10, "past"),
          getFormattedDate(10, "future"),
          faker.address.streetAddress(true).toString(),
          faker.address.latitude(45.5497, 42.9946).toString(),
          faker.address.longitude(-77.2169, -81.4905).toString()
        );
        console.log(
          "Created project with UUID =",
          prepareProjectDataAPIPage.createdProjectLocationId[0]
        );
        await activityAPIPage.createActivityByLocationId(
          prepareProjectDataAPIPage.createdProjectLocationId[0],
          seedTenTasks
        );
        console.log(
          "Created activities inside project with UUID =",
          prepareProjectDataAPIPage.createdProjectLocationId[0]
        );
      }
      console.log("Create Project test ended for index1 =", index1);
    });
  }
});
