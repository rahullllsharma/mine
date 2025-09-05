import fs from "fs";
import path from "path";
import { faker } from "@faker-js/faker";
import { getFormattedDate } from "../../../playwright/framework/common-actions";
import configs from "../configs.json";

type GenericObject = { id: string; name: string };
type AllActivitiesData = { activities: ActivityData[] };
type ActivityData = GenericObject & { tasks: TaskData[] };
type TaskData = GenericObject & { libraryTask: LibraryTaskData };
type LibraryTaskData = GenericObject & { hazards: HazardData[] };
type ParsedTasks = {
  libraryTaskId: string;
  hazards: ParsedHazards[];
};
type HazardData = GenericObject & { controls: ControlData[] };
type ParsedHazards = {
  libraryHazardId: string;
  isApplicable: boolean;
  controls: ParsedControls[];
};
type ControlData = GenericObject;
type ParsedControls = { libraryControlId: string; isApplicable: boolean };

type CreateProjectData = {
  managersData: { managers: GenericObject[] };
  supervisorsData: { supervisors: GenericObject[] };
  contractorsData: { contractors: GenericObject[] };
  projectTypesData: { projectTypesLibrary: GenericObject[] };
  divisionsData: { divisionsLibrary: GenericObject[] };
  regionsData: { regionsLibrary: GenericObject[] };
  projectNamePrefix: string;
};

type CreateActivityData = {
  projectLocationId: string;
  allActivitiesData: AllActivitiesData;
};

const STATUS = ["ACTIVE", "PENDING", "COMPLETED"];
const _ACTIVITY_NAMES = ["Field coating"];
const ACTIVITY_STATUS = [
  "NOT_STARTED",
  "IN_PROGRESS",
  "COMPLETE",
  "NOT_COMPLETED",
];

const getRandomEntry = (itemsLength: number) =>
  Math.floor(Math.random() * itemsLength);

const _seedTenTasks = JSON.parse(
  fs.readFileSync(
    path.join(__dirname, "../../../playwright/data/activityWithTasks.json"),
    "utf-8"
  )
);

function createProjectData({
  managersData,
  supervisorsData,
  contractorsData,
  projectTypesData,
  divisionsData,
  regionsData,
  projectNamePrefix,
}: CreateProjectData) {
  const managersDataLength = managersData.managers.length;
  const supervisorsDataLength = supervisorsData.supervisors.length;
  const contractorsDataLength = contractorsData.contractors.length;
  const projectTypesDataLength = projectTypesData.projectTypesLibrary.length;
  const divisionsDataLength = divisionsData.divisionsLibrary.length;
  const regionsDataLength = regionsData.regionsLibrary.length;
  const statusLength = STATUS.length;

  const dataValue = faker.datatype.number({
    min: 0,
    max: 123,
  });
  const projectName = configs.environment.includes("h1.")
    ? `${projectNamePrefix}${faker.random.numeric(4)}`
    : `${projectNamePrefix} ${faker.random.word()} - ${faker.random.numeric()}`;
  const optionalProps = configs.environment.includes("h1.")
    ? {}
    : {
        contractorId:
          contractorsData.contractors[getRandomEntry(contractorsDataLength)].id,
      };
  const projectData = {
    project: {
      name: projectName,
      externalKey: faker.datatype
        .number({
          min: 10000,
          max: 99999,
        })
        .toString(),
      libraryProjectTypeId:
        projectTypesData.projectTypesLibrary[
          getRandomEntry(projectTypesDataLength)
        ].id,
      status: STATUS[getRandomEntry(statusLength)],
      startDate: getFormattedDate(dataValue, "past"),
      endDate: getFormattedDate(dataValue, "future"),
      libraryDivisionId:
        divisionsData.divisionsLibrary[getRandomEntry(divisionsDataLength)].id,
      libraryRegionId:
        regionsData.regionsLibrary[getRandomEntry(regionsDataLength)].id,
      managerId: managersData.managers[getRandomEntry(managersDataLength)].id,
      supervisorId:
        supervisorsData.supervisors[getRandomEntry(supervisorsDataLength)].id,
      locations: [
        {
          name: faker.address.streetAddress(true).toString(),
          latitude: faker.address.latitude(45.5497, 42.9946).toString(),
          longitude: faker.address.longitude(-77.2169, -81.4905).toString(),
          supervisorId:
            supervisorsData.supervisors[getRandomEntry(supervisorsDataLength)]
              .id,
        },
      ],
      ...optionalProps,
    },
  };

  return projectData;
}

function prepareActivityData(allActivitiesData: AllActivitiesData) {
  const allActivitiesDataLength = allActivitiesData.activities.length;
  const { name: activityName, tasks: seedTasks } =
    allActivitiesData.activities[getRandomEntry(allActivitiesDataLength)];

  const parsedSeedTasks = seedTasks.reduce<ParsedTasks[]>((acc, curr) => {
    const {
      libraryTask: { id, hazards },
    } = curr;
    const parsedHazards = hazards.reduce<ParsedHazards[]>(
      (accHazards, currHazards) => {
        const { id: libraryHazardId, controls } = currHazards;
        const parsedControls = controls.reduce<ParsedControls[]>(
          (accControls, currControls) => {
            const { id: libraryControlId } = currControls;
            accControls.push({ libraryControlId, isApplicable: true });
            return accControls;
          },
          []
        );
        accHazards.push({
          libraryHazardId,
          isApplicable: true,
          controls: parsedControls,
        });
        return accHazards;
      },
      []
    );
    acc.push({ libraryTaskId: id, hazards: parsedHazards });
    return acc;
  }, []);
  return { seedTasks: parsedSeedTasks, activityName };
}

function createActivityData({
  projectLocationId,
  allActivitiesData,
}: CreateActivityData) {
  const activityStatusLength = ACTIVITY_STATUS.length;
  const { seedTasks, activityName } = prepareActivityData(allActivitiesData);
  const activityData = {
    activityData: {
      startDate: getFormattedDate(1, "past"),
      locationId: projectLocationId,
      name: activityName,
      endDate: getFormattedDate(1, "future"),
      status: ACTIVITY_STATUS[getRandomEntry(activityStatusLength)],
      tasks: seedTasks,
    },
  };
  return activityData;
}

export { createProjectData, createActivityData, prepareActivityData };
