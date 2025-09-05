import type { Option } from "fp-ts/Option";
import type { TaskEither } from "fp-ts/TaskEither";
import type {
  Activity,
  ActivityId,
  GpsCoordinates,
  JsbId,
  LibraryRegion,
  LibrarySiteCondition,
  LibraryTask,
  MedicalFacility,
  ProjectLocation,
  ProjectLocationId,
  SavedJsbData,
  SiteCondition,
} from "../codecs";
import type {
  AddActivityTasksInput,
  CreateActivityInput,
  CreateSiteConditionInput,
  RemoveActivityTasksInput,
  SaveJobSafetyBriefingInput,
  Sdk,
} from "../generated/types";
import type { GraphQLClient } from "graphql-request";
import type { ValidDateTime } from "@/utils/validation";
import type { ApiError } from "../api";
import type {
  LastJsbContents,
  LastAdhocJsbContents,
} from "../codecs/lastAddedJobSafetyBriefing";
import * as tt from "io-ts-types";
import * as t from "io-ts";
import * as O from "fp-ts/lib/Option";
import * as A from "fp-ts/lib/Array";
import { constNull, identity, pipe } from "fp-ts/function";
import { JsbFiltersOnEnum, getSdk } from "../generated/types";
import { makeRequest } from "../api";
import {
  activityCodec,
  activityIdCodec,
  librarySiteConditionCodec,
  libraryTaskCodec,
  medicalFacilityCodec,
  projectLocationCodec,
  projectLocationIdCodec,
  lastAddedJobSafetyBriefingCodec,
  siteConditionCodec,
  savedJsbDataCodec,
  siteConditionIdCodec,
  taskIdCodec,
  libraryRegionCodec,
  lastAddedAdhocJobSafetyBriefingCodec,
} from "../codecs";

const projectLocationsDataCodec = t.type({
  projectLocations: t.array(projectLocationCodec),
});

const tasksLibraryDataCodec = t.type({
  tasksLibrary: t.array(libraryTaskCodec),
});

const siteConditionsLibraryDataCodec = t.type({
  siteConditionsLibrary: t.array(librarySiteConditionCodec),
});

export const saveActivityResultCodec = t.type({
  id: activityIdCodec,
  location: t.type({
    id: projectLocationIdCodec,
  }),
});

export const removeOrAddTasksFromActivityResultCodec = t.type({
  id: activityIdCodec,
  name: tt.NonEmptyString,
  tasks: t.array(
    t.type({
      id: taskIdCodec,
      name: tt.NonEmptyString,
    })
  ),
});

export const saveSiteConditionResultCodec = t.type({
  id: siteConditionIdCodec,
  location: t.type({
    id: projectLocationIdCodec,
  }),
});

export type SaveActivityResult = t.TypeOf<typeof saveActivityResultCodec>;

export type RemoveOrAddTasksFromActivityResult = t.TypeOf<
  typeof removeOrAddTasksFromActivityResultCodec
>;

export type SaveSiteConditionResult = t.TypeOf<
  typeof saveSiteConditionResultCodec
>;

export const getLastJsb =
  (sdk: Sdk) =>
  (
    id: Option<ProjectLocationId>
  ): TaskEither<ApiError, Option<LastJsbContents>> => {
    return makeRequest(
      sdk.LastAddedJobSafetyBriefing,
      {
        projectLocationId: pipe(id, O.getOrElseW(constNull)),
        filterOn: pipe(
          id,
          O.fold(
            () => JsbFiltersOnEnum.UserDetails,
            () => JsbFiltersOnEnum.ProjectLocation
          )
        ),
      },
      lastAddedJobSafetyBriefingCodec.decode,
      res =>
        pipe(
          res.lastAddedJobSafetyBriefing,
          O.map(c => c.contents)
        )
    );
  };
export const getLastAdhocJsb =
  (sdk: Sdk) => (): TaskEither<ApiError, Option<LastAdhocJsbContents>> => {
    return makeRequest(
      sdk.LastAddedAdhocJobSafetyBriefing,
      {},
      lastAddedAdhocJobSafetyBriefingCodec.decode,

      res =>
        pipe(
          res.lastAddedAdhocJobSafetyBriefing,
          O.map(c => c.contents)
        )
    );
  };

export const getProjectLocation =
  (sdk: Sdk) =>
  (date: ValidDateTime) =>
  (id: ProjectLocationId): TaskEither<ApiError, Option<ProjectLocation>> =>
    makeRequest(
      sdk.ProjectLocations,
      { id, date: date.toISODate() },
      projectLocationsDataCodec.decode,
      res => A.head(res.projectLocations)
    );

export const getJsb =
  (sdk: Sdk) =>
  (id: JsbId): TaskEither<ApiError, SavedJsbData> =>
    makeRequest(
      sdk.Jsb,
      { id },
      res => savedJsbDataCodec.decode(res.jobSafetyBriefing),
      identity
    );

export const getTasksLibrary = (
  sdk: Sdk
): TaskEither<ApiError, LibraryTask[]> =>
  makeRequest(
    sdk.TasksLibrary,
    undefined,
    tasksLibraryDataCodec.decode,
    ts => ts.tasksLibrary
  );

export const getSiteConditionsLibrary = (sdk: Sdk) =>
  makeRequest(
    sdk.SiteConditionsLibrary,
    undefined,
    siteConditionsLibraryDataCodec.decode,
    res => res.siteConditionsLibrary
  );

export const saveJsb =
  (sdk: Sdk) =>
  (form: SaveJobSafetyBriefingInput): TaskEither<ApiError, SavedJsbData> =>
    makeRequest(
      sdk.SaveJsb,
      { input: form },
      res => savedJsbDataCodec.decode(res.saveJobSafetyBriefing),
      identity
    );

export const completeJsb =
  (sdk: Sdk) =>
  (form: SaveJobSafetyBriefingInput): TaskEither<ApiError, SavedJsbData> =>
    makeRequest(
      sdk.CompleteJsb,
      { input: form },
      res => savedJsbDataCodec.decode(res.completeJobSafetyBriefing),
      identity
    );

export const deleteJsb =
  (sdk: Sdk) =>
  (id: JsbId): TaskEither<ApiError, boolean> =>
    makeRequest(
      sdk.DeleteJsb,
      { id },
      res => t.success(res.deleteJobSafetyBriefing),
      identity
    );

export const reopenJsb =
  (sdk: Sdk) =>
  (id: JsbId): TaskEither<ApiError, SavedJsbData> =>
    makeRequest(
      sdk.ReopenJsb,
      { id },
      res => savedJsbDataCodec.decode(res.reopenJobSafetyBriefing),
      identity
    );

export const saveActivity =
  (sdk: Sdk) =>
  (input: CreateActivityInput): TaskEither<ApiError, SaveActivityResult> =>
    makeRequest(
      sdk.CreateActivity,
      { activityData: input },
      t.type({ createActivity: saveActivityResultCodec }).decode,
      res => res.createActivity
    );

export const removeTasksFromActivity =
  (sdk: Sdk) =>
  (id: ActivityId) =>
  (
    input: RemoveActivityTasksInput
  ): TaskEither<ApiError, RemoveOrAddTasksFromActivityResult> =>
    makeRequest(
      sdk.RemoveTasksFromActivity,
      { id, taskIds: input },
      t.type({
        removeTasksFromActivity: removeOrAddTasksFromActivityResultCodec,
      }).decode,
      res => res.removeTasksFromActivity
    );

export const addTasksToActivity =
  (sdk: Sdk) =>
  (id: ActivityId) =>
  (
    input: AddActivityTasksInput["tasksToBeAdded"]
  ): TaskEither<ApiError, RemoveOrAddTasksFromActivityResult> =>
    makeRequest(
      sdk.AddTasksToActivity,
      { id, newTasks: { tasksToBeAdded: input } },
      t.type({
        addTasksToActivity: removeOrAddTasksFromActivityResultCodec,
      }).decode,
      res => res.addTasksToActivity
    );

export const deleteActivity =
  (sdk: Sdk) =>
  (id: ActivityId): TaskEither<ApiError, boolean> =>
    makeRequest(
      sdk.DeleteActivity,
      { id },
      t.type({ deleteActivity: t.boolean }).decode,
      res => res.deleteActivity
    );

export const saveSiteCondition =
  (sdk: Sdk) =>
  (
    input: CreateSiteConditionInput
  ): TaskEither<ApiError, SaveSiteConditionResult> =>
    makeRequest(
      sdk.CreateSiteCondition,
      { siteConditionData: input },
      t.type({ createSiteCondition: saveSiteConditionResultCodec }).decode,
      res => res.createSiteCondition
    );

export const getActivities =
  (sdk: Sdk) =>
  (projectLocationId: ProjectLocationId): TaskEither<ApiError, Activity[]> =>
    makeRequest(
      sdk.Activities,
      { projectLocationId },
      t.type({
        projectLocations: t.array(
          t.type({
            activities: t.array(activityCodec),
          })
        ),
      }).decode,
      res =>
        pipe(
          res.projectLocations,
          A.head,
          O.fold(
            () => [],
            pl => pl.activities
          )
        )
    );

export const getSiteConditions =
  (sdk: Sdk) =>
  (projectLocationId: Option<ProjectLocationId>) =>
  (date: ValidDateTime): TaskEither<ApiError, SiteCondition[]> =>
    makeRequest(
      sdk.SiteConditions,
      {
        locationId: pipe(projectLocationId, O.getOrElseW(constNull)),
        date: date.toISODate(),
      },
      res => t.array(siteConditionCodec).decode(res.siteConditions),
      identity
    );

export const getLocationSiteConditions =
  (sdk: Sdk) =>
  (gpsCoordinates: GpsCoordinates) =>
  (date: ValidDateTime): TaskEither<ApiError, SiteCondition[]> =>
    makeRequest(
      sdk.LocationSiteConditions,
      {
        siteInput: {
          latitude: gpsCoordinates.latitude,
          longitude: gpsCoordinates.longitude,
          date: date.toISODate(),
        },
      },
      res => t.array(siteConditionCodec).decode(res.locationSiteConditions),
      identity
    );

export const getNearestMedicalFacilities =
  (sdk: Sdk) =>
  (location: GpsCoordinates): TaskEither<ApiError, MedicalFacility[]> =>
    makeRequest(
      sdk.NearestMedicalFacilities,
      location,
      res =>
        pipe(
          res.nearestMedicalFacilities,
          t.array(medicalFacilityCodec).decode
        ),
      identity
    );

export const getLibraryRegions = (
  sdk: Sdk
): TaskEither<ApiError, LibraryRegion[]> =>
  makeRequest(
    sdk.RegionsLibrary,
    undefined,
    res => pipe(res.regionsLibrary, t.array(libraryRegionCodec).decode),
    identity
  );

export interface JsbApi {
  getJsb: (id: JsbId) => TaskEither<ApiError, SavedJsbData>;
  saveJsb: (
    form: SaveJobSafetyBriefingInput
  ) => TaskEither<ApiError, SavedJsbData>;
  completeJsb: (
    form: SaveJobSafetyBriefingInput
  ) => TaskEither<ApiError, SavedJsbData>;
  deleteJsb: (id: JsbId) => TaskEither<ApiError, boolean>;
  reopenJsb: (id: JsbId) => TaskEither<ApiError, SavedJsbData>;
  getTasksLibrary: TaskEither<ApiError, LibraryTask[]>;
  getSiteConditionsLibrary: TaskEither<ApiError, LibrarySiteCondition[]>;
  getLibraryRegions: TaskEither<ApiError, LibraryRegion[]>;
  getProjectLocation: (
    date: ValidDateTime
  ) => (id: ProjectLocationId) => TaskEither<ApiError, Option<ProjectLocation>>;
  saveActivity: (
    input: CreateActivityInput
  ) => TaskEither<ApiError, SaveActivityResult>;
  getActivities: (
    projectLocationId: ProjectLocationId
  ) => TaskEither<ApiError, Activity[]>;
  getSiteConditions: (
    projectLocationId: Option<ProjectLocationId>
  ) => (date: ValidDateTime) => TaskEither<ApiError, SiteCondition[]>;
  getLocationSiteConditions: (
    location: GpsCoordinates
  ) => (date: ValidDateTime) => TaskEither<ApiError, SiteCondition[]>;
  getNearestMedicalFacilities: (
    location: GpsCoordinates
  ) => TaskEither<ApiError, MedicalFacility[]>;
  getLastJsb: (
    id: Option<ProjectLocationId>
  ) => TaskEither<ApiError, Option<LastJsbContents>>;
  getLastAdhocJsb: () => TaskEither<ApiError, Option<LastAdhocJsbContents>>;
  saveSiteCondition: (
    input: CreateSiteConditionInput
  ) => TaskEither<ApiError, SaveSiteConditionResult>;
  removeTasksFromActivity: (
    id: ActivityId
  ) => (
    input: RemoveActivityTasksInput
  ) => TaskEither<ApiError, RemoveOrAddTasksFromActivityResult>;
  addTasksToActivity: (
    id: ActivityId
  ) => (
    input: AddActivityTasksInput["tasksToBeAdded"]
  ) => TaskEither<ApiError, RemoveOrAddTasksFromActivityResult>;
  deleteActivity: (id: ActivityId) => TaskEither<ApiError, boolean>;
}

export const jsbApi = (c: GraphQLClient): JsbApi => ({
  getJsb: getJsb(getSdk(c)),
  completeJsb: completeJsb(getSdk(c)),
  saveJsb: saveJsb(getSdk(c)),
  deleteJsb: deleteJsb(getSdk(c)),
  reopenJsb: reopenJsb(getSdk(c)),
  getTasksLibrary: getTasksLibrary(getSdk(c)),
  getSiteConditionsLibrary: getSiteConditionsLibrary(getSdk(c)),
  getProjectLocation: getProjectLocation(getSdk(c)),
  saveActivity: saveActivity(getSdk(c)),
  getActivities: getActivities(getSdk(c)),
  getSiteConditions: getSiteConditions(getSdk(c)),
  getLocationSiteConditions: getLocationSiteConditions(getSdk(c)),
  getNearestMedicalFacilities: getNearestMedicalFacilities(getSdk(c)),
  getLastJsb: getLastJsb(getSdk(c)),
  getLastAdhocJsb: getLastAdhocJsb(getSdk(c)),
  saveSiteCondition: saveSiteCondition(getSdk(c)),
  removeTasksFromActivity: removeTasksFromActivity(getSdk(c)),
  addTasksToActivity: addTasksToActivity(getSdk(c)),
  deleteActivity: deleteActivity(getSdk(c)),
  getLibraryRegions: getLibraryRegions(getSdk(c)),
});
