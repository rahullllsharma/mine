import type { RouterLink } from "@/types/Generic";
import type { Api, ApiError, ApiResult } from "@/api/api";
import type {
  Activity,
  ActivityId,
  GpsCoordinates,
  Hazard,
  Jsb,
  JsbId,
  LibrarySiteCondition,
  LibraryTask,
  LibraryTaskId,
  MedicalFacility,
  ProjectLocation,
  ProjectLocationId,
  SavedJsbData,
  SiteCondition,
  LibraryRegion,
  WorkPackageId,
} from "@/api/codecs";
import type {
  LastJsbContents,
  LastAdhocJsbContents,
} from "@/api/codecs/lastAddedJobSafetyBriefing";
import type {
  CreateActivityInput,
  CreateSiteConditionInput,
  SaveJobSafetyBriefingInput,
} from "@/api/generated/types";
import type {
  NavigationOption,
  SelectStatusAndIcon,
} from "@/components/navigation/Navigation";
import type { AsyncOperationStatus } from "@/utils/asyncOperationStatus";
import type { RenderOptionFn } from "@/components/shared/select/Select";
import type { Deferred } from "@/utils/deferred";
import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type { ValidDateTime } from "@/utils/validation";
import type { Either } from "fp-ts/lib/Either";
import type { Task } from "fp-ts/lib/Task";
import type { Option } from "fp-ts/lib/Option";
import type * as t from "io-ts";
import type { NonEmptyString } from "io-ts-types";
import type { Status } from "../Basic/StepItem";
import type { StepName, Steps } from "./Steps";
import type { UserPermission } from "@/types/auth/AuthUser";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import type { NonEmptyArray } from "fp-ts/lib/NonEmptyArray";
import { Fragment, useContext, useEffect, useMemo, useState } from "react";
import cx from "classnames";
import * as Eq from "fp-ts/Eq";
import * as TE from "fp-ts/TaskEither";
import * as Tup from "fp-ts/Tuple";
import {
  constFalse,
  constNull,
  constant,
  flow,
  identity,
  pipe,
} from "fp-ts/function";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import { isLeft, isRight, right, left } from "fp-ts/lib/Either";
import * as M from "fp-ts/lib/Map";
import * as NEA from "fp-ts/lib/NonEmptyArray";
import * as O from "fp-ts/lib/Option";
import { some } from "fp-ts/lib/Option";
import * as SG from "fp-ts/lib/Semigroup";
import * as S from "fp-ts/lib/Set";
import * as tt from "io-ts-types";
import { Lens } from "monocle-ts";
import router from "next/router";
import { isMobile, isMobileOnly, isTablet } from "react-device-detect";
import { sequenceS } from "fp-ts/lib/Apply";
import { showApiError, showUserApiError } from "@/api/api";
import {
  eqHazardId,
  eqLibrarySiteConditionId,
  eqLibraryTaskId,
  ordLibrarySiteConditionId,
} from "@/api/codecs";
import NavItem from "@/components/navigation/navItem/NavItem";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import Modal from "@/components/shared/modal/Modal";
import { Select } from "@/components/shared/select/Select";
import { ProjectDescriptionHeader } from "@/container/projectSummaryView/PojectDescriptionHeader";
import { Finished, Started } from "@/utils/asyncOperationStatus";
import {
  NotStarted,
  Resolved,
  deferredToOption,
  isInProgress,
  isResolved,
  isUpdating,
  mapDeferred,
  updatingDeferred,
} from "@/utils/deferred";
import { SourceAppInformation, RiskLevel } from "@/api/generated/types";

import {
  effectOfAction,
  effectOfAsync,
  effectOfAsync_,
  effectOfFunc,
  effectOfFunc_,
  effectsBatch,
  mapEffect,
  noEffect,
  updateChildModel,
  updateChildModelEffect,
  withEffect,
} from "@/utils/reducerWithEffect";
import Dropdown from "@/components/shared/dropdown/Dropdown";

import useLeavePageConfirm from "@/hooks/useLeavePageConfirm";
import PageHeader from "@/components/layout/pageHeader/PageHeader";
import useRestMutation from "@/hooks/useRestMutation";
import { config } from "@/config";
import axiosRest from "@/api/restApi";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { messages } from "@/locales/messages";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { OptionalView } from "../../common/Optional";
import PageLayout from "../../layout/pageLayout/PageLayout";
import ButtonIcon from "../../shared/button/icon/ButtonIcon";
import ButtonPrimary from "../../shared/button/primary/ButtonPrimary";
import * as Alert from "../Alert";
import { StepItem } from "../Basic/StepItem";
import * as ControlsAssessment from "../Jsb/ControlsAssessment";
import * as Nav from "../Navigation";
import {
  isSameDay,
  scrollTopEffect,
  snapshotHash,
  FormViewTabStates,
  taskRiskLevels,
} from "../Utils";
import { RiskBadge } from "../Basic/TaskCard/RiskBadge";
import { FormHistory } from "../FormHistory/FormHistory";
import packageJson from "../../../../package.json";
import * as AttachmentsSection from "./AttachmentsSection";
import * as CrewSignOff from "./CrewSignOff";
import * as EnergySourceControls from "./EnergySourceControls";
import * as GroupDiscussion from "./GroupDiscussion/GroupDiscussion";
import * as JobInformation from "./JobInformation";
import * as MedicalEmergency from "./MedicalEmergency";
import * as SiteConditions from "./SiteConditions";
import * as Tasks from "./Tasks";
import * as WorkProcedures from "./WorkProcedures";
import {
  checkUnsavedChanges,
  nextStep,
  setFormDirty,
  stepList,
  stepNames,
} from "./Steps";

const appVersion = packageJson.version;

const defaultSavedSteps: Record<StepName, boolean> = {
  jobInformation: false,
  medicalEmergency: false,
  tasks: false,
  energySourceControls: false,
  workProcedures: false,
  siteConditions: false,
  controlsAssessment: false,
  groupDiscussion: false,
  attachments: false,
  crewSignOff: false,
};

// TODO: to simplify the logic, consider including the "date" parameter of the graphql query used to get project location into the response
export type ProjectLocationData = ProjectLocation & { date: ValidDateTime };
export type MedicalFacilitiesData = GpsCoordinates & {
  nearestMedicalFacilities: MedicalFacility[];
};

type CompleteJsbDialogModel = {
  projectLocationId: Option<ProjectLocationId>;
  projectLocationDate: Option<ValidDateTime>;
  jsbId: Option<JsbId>;
  input: SaveJobSafetyBriefingInput;
};

export type Model = {
  steps: Steps;
  currentStep: StepName;
  savedSteps: Option<Record<StepName, boolean>>; // None represents a new JSB ("clean" state)
  stepHashes: Record<StepName, string>;
  navToStepOnSave: Option<StepName>;
  tasks: Deferred<ApiResult<LibraryTask[]>>;
  siteConditions: Deferred<ApiResult<LibrarySiteCondition[]>>;
  activities: Deferred<ApiResult<Activity[]>>;
  jsbId: Deferred<ApiResult<Option<JsbId>>>;
  creatorUserId: Deferred<ApiResult<Option<NonEmptyString>>>; // refers to user who created this jsb
  completedByUserId: Deferred<ApiResult<Option<NonEmptyString>>>; // refers to user who completed this jsb
  projectLocation: Deferred<Option<ProjectLocationData>>;
  deleteJsbDialog: Option<JsbId>;
  deleteJsb: Deferred<ApiResult<boolean>>;
  nearestMedicalFacilities: Deferred<ApiResult<MedicalFacilitiesData>>;
  locationSiteConditions: Deferred<ApiResult<SiteCondition[]>>; // site conditions based on the current gps coordinates and date
  discardChangesDialog: Option<StepName>;
  completeJsbDialog: Option<CompleteJsbDialogModel>;
  selectedTab: FormViewTabStates;
  libraryRegions: Deferred<ApiResult<LibraryRegion[]>>;
};

export type WizardEffect =
  | {
      type: "ComponentEffect";
      effect: Effect<Action>;
    }
  | {
      type: "AlertAction";
      action: Alert.Action;
    }
  | {
      type: "NoEffect";
    };

const relevantHazards = (model: Model): Either<string, Hazard[]> => {
  const res = pipe(
    E.Do,
    E.bind("taskHazards", () =>
      pipe(
        model.tasks,
        deferredToOption,
        O.chain(O.fromEither),
        E.fromOption(() => "Failed to load tasks"),
        E.map(
          flow(
            A.filter(task =>
              S.elem(eqLibraryTaskId)(task.id)(
                model.steps.tasks.selectedTaskIds
              )
            ),
            A.chain(task => task.hazards)
          )
        )
      )
    ),
    E.bind("siteConditionsHazards", () =>
      pipe(
        model.siteConditions,
        deferredToOption,
        O.chain(O.fromEither),
        E.fromOption(() => "Failed to load site conditions"),
        E.map(
          flow(
            A.filter(sc =>
              S.elem(eqLibrarySiteConditionId)(sc.id)(
                model.steps.siteConditions.selectedIds
              )
            ),
            A.chain(sc => sc.hazards)
          )
        )
      )
    ),
    E.map(({ taskHazards, siteConditionsHazards }) =>
      pipe(
        [...taskHazards, ...siteConditionsHazards],
        A.uniq(Eq.contramap((h: Hazard) => h.id)(eqHazardId))
      )
    )
  );
  return res;
};

export const ComponentEffect = (effect: Effect<Action>): WizardEffect => ({
  type: "ComponentEffect",
  effect,
});
const AlertAction = (action: Alert.Action): WizardEffect => ({
  type: "AlertAction",
  action,
});
const NoEffect: WizardEffect = { type: "NoEffect" };

const jobInformationResult = (
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> =>
  pipe(model.steps.jobInformation, JobInformation.toSaveJsbInput);
const medicalEmergencyResult = (
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> =>
  pipe(model.steps.medicalEmergency, MedicalEmergency.toSaveJsbInput);
const energySourceControlsResult = (
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> =>
  pipe(
    model.steps.jobInformation.briefingDate.val,
    E.chain(date =>
      EnergySourceControls.toSaveJsbInput(
        date,
        model.steps.energySourceControls
      )
    )
  );

const getTasks = (model: Model) => {
  return pipe(
    model.tasks,
    deferredToOption,
    O.chain(O.fromEither),
    O.fold(
      () => [],
      tasks => tasks
    )
  );
};

const tasksResult = (model: Model): t.Validation<SaveJobSafetyBriefingInput> =>
  pipe(
    model.steps.tasks,
    Tasks.toSaveJsbInput(todaysActivities(model), getTasks(model)),
    right
  );

const workProceduresResult = (
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> =>
  pipe(model.steps.workProcedures, WorkProcedures.toSaveJsbInput);

const getSiteConditions = (model: Model) => {
  return pipe(
    model.siteConditions,
    deferredToOption,
    O.chain(O.fromEither),
    O.fold(
      () => [],
      siteCondition => siteCondition
    )
  );
};

const siteConditionsResult = (
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> =>
  pipe(
    model.steps.siteConditions,
    SiteConditions.toSaveJsbInput(getSiteConditions(model)),
    right
  );

const controlsAssessmentResult = (
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> => {
  const hazards = pipe(
    relevantHazards(model),
    O.fromEither,
    O.fold(() => [], identity)
  );

  return pipe(
    model.steps.controlsAssessment,
    ControlsAssessment.toSaveJsbInput(hazards, getTasks(model)),
    right
  );
};

const attachmentsResult = (
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> =>
  pipe(model.steps.attachments, AttachmentsSection.toSaveJsbInput);

const crewSignOffResult = (
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> =>
  pipe(model.steps.crewSignOff, CrewSignOff.toSaveJsbInput);

const groupDiscussionResult = (
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> =>
  pipe(model.steps.groupDiscussion, GroupDiscussion.toSaveJsbInput);

function stepResult(
  step: StepName,
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> {
  switch (step) {
    case "jobInformation":
      return jobInformationResult(model);
    case "medicalEmergency":
      return medicalEmergencyResult(model);
    case "energySourceControls":
      return energySourceControlsResult(model);
    case "tasks": {
      // Based on the selected tasks, JSB form generates a preselectedControls for relevant hazards of the tasks
      // On saving tasks to backend, these should be also saved as GroupDiscussion renders information from response of the SaveJSB query.

      if (S.isEmpty(model.steps.tasks.selectedTaskIds)) {
        return left([]);
      }

      const hazards = relevantHazards(model);
      const controlsAssessmentLens = Lens.fromPath<Model>()([
        "steps",
        "controlsAssessment",
      ]);

      const updatedModel = E.isRight(hazards)
        ? controlsAssessmentLens.modify(
            ControlsAssessment.preselectControls(hazards.right)
          )(model)
        : model;

      const tasksResultWithControlsAssessmentResult = pipe(
        sequenceS(E.Apply)({
          tasksResult: tasksResult(updatedModel),
          controlsAssessmentResult: controlsAssessmentResult(updatedModel),
        }),
        E.map(res => ({
          ...res.tasksResult,
          ...res.controlsAssessmentResult,
        }))
      );

      return tasksResultWithControlsAssessmentResult;
    }
    case "workProcedures": {
      return workProceduresResult(model);
    }
    case "siteConditions": {
      // Based on the selected tasks, JSB form generates a preselectedControls for relevant hazards of the site conditions
      // On saving site conditions to backend, these should be also saved as GroupDiscussion renders
      // information from response of the SaveJSB query.
      const hazards = relevantHazards(model);
      const controlsAssessmentLens = Lens.fromPath<Model>()([
        "steps",
        "controlsAssessment",
      ]);

      const updatedModel = E.isRight(hazards)
        ? controlsAssessmentLens.modify(
            ControlsAssessment.preselectControls(hazards.right)
          )(model)
        : model;

      const siteConditionsResultWithControlsAssessmentResult = pipe(
        sequenceS(E.Apply)({
          siteConditionsResult: siteConditionsResult(updatedModel),
          controlsAssessmentResult: controlsAssessmentResult(updatedModel),
        }),
        E.map(res => ({
          ...res.siteConditionsResult,
          ...res.controlsAssessmentResult,
        }))
      );

      return siteConditionsResultWithControlsAssessmentResult;
    }
    case "controlsAssessment": {
      return controlsAssessmentResult(model);
    }
    case "groupDiscussion":
      return groupDiscussionResult(model);
    case "attachments":
      return attachmentsResult(model);
    case "crewSignOff":
      return crewSignOffResult(model);
  }
}

const toJsbInput = (model: Model): t.Validation<SaveJobSafetyBriefingInput> =>
  stepResult(model.currentStep, model);

const todaysActivities = (model: Model) =>
  pipe(
    model.activities,
    deferredToOption,
    O.chain(O.fromEither),
    O.fold(
      () => [],
      A.filter(activity =>
        pipe(
          O.Do,
          O.bind("briefingDate", () =>
            O.fromEither(model.steps.jobInformation.briefingDate.val)
          ),
          O.bind("activityStart", () => activity.startDate),
          O.bind("activityEnd", () => activity.endDate),
          O.fold(
            () => false,
            ({ briefingDate, activityStart, activityEnd }) => {
              const bdMillis = briefingDate.toMillis();

              return (
                bdMillis >= activityStart.toMillis() &&
                bdMillis <= activityEnd.toMillis()
              );
            }
          )
        )
      )
    )
  );

export type Action =
  | {
      type: "NavTo";
      step: StepName;
    }
  | {
      type: "NavToOnSave";
      step: Option<StepName>;
    }
  | {
      type: "JobInformationAction";
      action: JobInformation.Action;
    }
  | {
      type: "MedicalEmergencyAction";
      action: MedicalEmergency.Action;
    }
  | {
      type: "EnergySourceControlsAction";
      action: EnergySourceControls.Action;
    }
  | {
      type: "TasksAction";
      action: Tasks.Action;
    }
  | {
      type: "WorkProceduresAction";
      action: WorkProcedures.Action;
    }
  | {
      type: "SiteConditionsAction";
      action: SiteConditions.Action;
    }
  | {
      type: "ControlsAssessmentAction";
      action: ControlsAssessment.Action;
    }
  | {
      type: "CrewSignOffAction";
      action: CrewSignOff.Action;
    }
  | {
      type: "AttachmentsAction";
      action: AttachmentsSection.Action;
    }
  | {
      type: "ShowDeleteJsbDialog";
      jsbId: JsbId;
    }
  | {
      type: "HideDeleteJsbDialog";
    }
  | {
      type: "ShowDiscardChangesDialog";
      step: StepName;
    }
  | {
      type: "HideDiscardChangesDialog";
    }
  | {
      type: "ShowCompleteJsbDialog";
      projectLocationId: Option<ProjectLocationId>;
      projectLocationDate: Option<ValidDateTime>;
      jsbId: Option<JsbId>;
      input: SaveJobSafetyBriefingInput;
    }
  | {
      type: "HideCompleteJsbDialog";
    }
  | {
      type: "DeleteJsb";
      jsbId: JsbId;
      operation: AsyncOperationStatus<ApiResult<boolean>>;
    }
  | {
      type: "ReopenJsb";
      jsbId: JsbId;
      operation: AsyncOperationStatus<ApiResult<SavedJsbData>>;
    }
  | {
      type: "GetTasks";
      operation: AsyncOperationStatus<ApiResult<LibraryTask[]>>;
    }
  | {
      type: "GetSiteConditions";
      operation: AsyncOperationStatus<ApiResult<LibrarySiteCondition[]>>;
    }
  | {
      type: "GetLocationSiteConditions";
      gpsCoordinates: GpsCoordinates;
      date: ValidDateTime;
      operation: AsyncOperationStatus<ApiResult<SiteCondition[]>>;
    }
  | {
      type: "GetNearestMedicalFacilities";
      location: GpsCoordinates;
      operation: AsyncOperationStatus<ApiResult<MedicalFacility[]>>;
    }
  | {
      type: "SaveJsb";
      complete: boolean;
      jsbId: Option<JsbId>;
      projectLocationId: Option<ProjectLocationId>;
      projectLocationDate: Option<ValidDateTime>;
      input: SaveJobSafetyBriefingInput;
      operation: AsyncOperationStatus<
        ApiResult<readonly [SavedJsbData, Option<ProjectLocationData>]>
      >;
    }
  | {
      type: "SaveActivity";
      input: CreateActivityInput;
      removalTasksData: {
        tasks: Option<LibraryTaskId[]>;
        activityId: Option<ActivityId>;
      };
      additionalTasksData: {
        tasks: Option<LibraryTaskId[]>;
        activityId: Option<ActivityId>;
      };
      projectLocationId: Option<ProjectLocationId>;
      operation: AsyncOperationStatus<ApiResult<[ActivityId, Activity[]]>>;
    }
  | {
      type: "DeleteActivity";
      activityId: ActivityId;
      operation: AsyncOperationStatus<ApiResult<[ActivityId, Activity[]]>>;
      projectLocationId: Option<ProjectLocationId>;
    }
  | {
      type: "SaveSiteCondition";
      input: CreateSiteConditionInput;
      operation: AsyncOperationStatus<ApiResult<LibrarySiteCondition[]>>;
    }
  | {
      type: "GetLibraryRegions";
      operation: AsyncOperationStatus<ApiResult<LibraryRegion[]>>;
    }
  | {
      type: "FormSaveAttempted";
    }
  | {
      type: "FormViewStateChange";
      selectedTab: FormViewTabStates;
    }
  | {
      type: "NoAction";
    };

export const NavTo = (step: StepName): Action => ({
  type: "NavTo",
  step,
});

export const NavToOnSave = (step: Option<StepName>): Action => ({
  type: "NavToOnSave",
  step,
});

export const JobInformationAction = (
  action: JobInformation.Action
): Action => ({
  type: "JobInformationAction",
  action,
});

export const MedicalEmergencyAction = (
  action: MedicalEmergency.Action
): Action => ({
  type: "MedicalEmergencyAction",
  action,
});

export const EnergySourceControlsAction = (
  action: EnergySourceControls.Action
): Action => ({
  type: "EnergySourceControlsAction",
  action,
});

export const TasksAction = (action: Tasks.Action): Action => ({
  type: "TasksAction",
  action,
});

export const WorkProceduresAction = (
  action: WorkProcedures.Action
): Action => ({
  type: "WorkProceduresAction",
  action,
});

export const SiteConditionsAction = (
  action: SiteConditions.Action
): Action => ({
  type: "SiteConditionsAction",
  action,
});

export const ControlsAssessmentAction = (
  action: ControlsAssessment.Action
): Action => ({
  type: "ControlsAssessmentAction",
  action,
});

export const CrewSignOffAction = (action: CrewSignOff.Action): Action => ({
  type: "CrewSignOffAction",
  action,
});

export const AttachmentsAction = (
  action: AttachmentsSection.Action
): Action => ({
  type: "AttachmentsAction",
  action,
});

export const ShowDeleteJsbDialog = (jsbId: JsbId): Action => ({
  type: "ShowDeleteJsbDialog",
  jsbId,
});

export const HideDeleteJsbDialog = (): Action => ({
  type: "HideDeleteJsbDialog",
});

export const ShowDiscardChangesDialog = (step: StepName): Action => ({
  type: "ShowDiscardChangesDialog",
  step,
});

export const HideDiscardChangesDialog = (): Action => ({
  type: "HideDiscardChangesDialog",
});

export const ShowCompleteJsbDialog = (
  projectLocationId: Option<ProjectLocationId>,
  projectLocationDate: Option<ValidDateTime>,
  jsbId: Option<JsbId>,
  input: SaveJobSafetyBriefingInput
): Action => ({
  type: "ShowCompleteJsbDialog",
  projectLocationId,
  projectLocationDate,
  jsbId,
  input,
});

export const HideCompleteJsbDialog = (): Action => ({
  type: "HideCompleteJsbDialog",
});

export const DeleteJsb =
  (jsbId: JsbId) =>
  (operation: AsyncOperationStatus<ApiResult<boolean>>): Action => ({
    type: "DeleteJsb",
    jsbId,
    operation,
  });

export const ReopenJsb =
  (jsbId: JsbId) =>
  (operation: AsyncOperationStatus<ApiResult<SavedJsbData>>): Action => ({
    type: "ReopenJsb",
    jsbId,
    operation,
  });

export const GetTasks = (
  operation: AsyncOperationStatus<ApiResult<LibraryTask[]>>
): Action => ({
  type: "GetTasks",
  operation,
});

export const GetSiteConditions = (
  operation: AsyncOperationStatus<ApiResult<LibrarySiteCondition[]>>
): Action => ({
  type: "GetSiteConditions",
  operation,
});
export const GetLibraryRegions = (
  operation: AsyncOperationStatus<ApiResult<LibraryRegion[]>>
): Action => ({
  type: "GetLibraryRegions",
  operation,
});

export const GetLocationSiteConditions =
  (gpsCoordinates: GpsCoordinates) =>
  (date: ValidDateTime) =>
  (operation: AsyncOperationStatus<ApiResult<SiteCondition[]>>): Action => ({
    type: "GetLocationSiteConditions",
    gpsCoordinates,
    date,
    operation,
  });

export const GetNearestMedicalFacilities =
  (location: GpsCoordinates) =>
  (operation: AsyncOperationStatus<ApiResult<MedicalFacility[]>>): Action => ({
    type: "GetNearestMedicalFacilities",
    location,
    operation,
  });

export const SaveJsb =
  (complete: boolean) =>
  (
    projectLocationId: Option<ProjectLocationId>,
    projectLocationDate: Option<ValidDateTime>,
    jsbId: Option<JsbId>,
    input: SaveJobSafetyBriefingInput
  ) =>
  (
    operation: AsyncOperationStatus<
      ApiResult<readonly [SavedJsbData, Option<ProjectLocationData>]>
    >
  ): Action => ({
    type: "SaveJsb",
    complete,
    jsbId,
    projectLocationId,
    projectLocationDate,
    input,
    operation,
  });

export const SaveActivity =
  (input: CreateActivityInput) =>
  (removalTasksData: {
    tasks: Option<LibraryTaskId[]>;
    activityId: Option<ActivityId>;
  }) =>
  (additionalTasksData: {
    tasks: Option<LibraryTaskId[]>;
    activityId: Option<ActivityId>;
  }) =>
  (projectLocationId: Option<ProjectLocationId>) =>
  (
    operation: AsyncOperationStatus<ApiResult<[ActivityId, Activity[]]>>
  ): Action => ({
    type: "SaveActivity",
    input,
    removalTasksData,
    operation,
    projectLocationId,
    additionalTasksData,
  });

export const DeleteActivity =
  (activityId: ActivityId) =>
  (projectLocationId: Option<ProjectLocationId>) =>
  (
    operation: AsyncOperationStatus<ApiResult<[ActivityId, Activity[]]>>
  ): Action => ({
    type: "DeleteActivity",
    activityId,
    operation,
    projectLocationId,
  });

export const SaveSiteCondition =
  (input: CreateSiteConditionInput) =>
  (
    operation: AsyncOperationStatus<ApiResult<LibrarySiteCondition[]>>
  ): Action => ({
    type: "SaveSiteCondition",
    input,
    operation,
  });

export const FormSaveAttempted = (): Action => ({
  type: "FormSaveAttempted",
});

export const ChangeFormViewState = (
  selectedTab: FormViewTabStates
): Action => ({
  type: "FormViewStateChange",
  selectedTab,
});

export const NoAction = (): Action => ({
  type: "NoAction",
});

const updateJobInformation = flow(
  updateChildModel(
    Lens.fromPath<Model>()(["steps", "jobInformation"]),
    JobInformation.update
  ),
  withEffect(noEffect)
);

const updateMedicalEmergency = updateChildModelEffect(
  Lens.fromPath<Model>()(["steps", "medicalEmergency"]),
  MedicalEmergencyAction,
  MedicalEmergency.update
);

const updateEnergySourceControls = flow(
  updateChildModel(
    Lens.fromPath<Model>()(["steps", "energySourceControls"]),
    EnergySourceControls.update
  ),
  withEffect(noEffect)
);

const updateTasks = updateChildModelEffect(
  Lens.fromPath<Model>()(["steps", "tasks"]),
  TasksAction,
  Tasks.update
);

const updateWorkProcedures = updateChildModelEffect(
  Lens.fromPath<Model>()(["steps", "workProcedures"]),
  WorkProceduresAction,
  WorkProcedures.update
);

const updateSiteConditions = flow(
  updateChildModel(
    Lens.fromPath<Model>()(["steps", "siteConditions"]),
    SiteConditions.update
  ),
  withEffect(noEffect)
);

const updateControlsAssessment = flow(
  updateChildModel(
    Lens.fromPath<Model>()(["steps", "controlsAssessment"]),
    ControlsAssessment.update
  ),
  withEffect(noEffect)
);

const updateCrewSignOff = (api: Api) =>
  updateChildModelEffect(
    Lens.fromPath<Model>()(["steps", "crewSignOff"]),
    CrewSignOffAction,
    CrewSignOff.update(api)
  );

export type InitData = {
  readonly projectLocation: Option<ProjectLocation>;
  readonly jsbData: Option<SavedJsbData>;
  readonly dateTime: ValidDateTime;
  readonly lastJsb: Option<LastJsbContents>;
  readonly lastAdhocJsb: Option<LastAdhocJsbContents>;
};

function checkSavedSteps(jsb: Jsb): Record<StepName, boolean> {
  return {
    jobInformation: O.isSome(jsb.jsbMetadata),
    medicalEmergency: O.isSome(jsb.emergencyContacts),
    tasks: O.isSome(jsb.taskSelections),
    energySourceControls: O.isSome(jsb.energySourceControl),
    workProcedures: O.isSome(jsb.workProcedureSelections),
    siteConditions: O.isSome(jsb.siteConditionSelections),
    controlsAssessment: O.isSome(jsb.controlAssessmentSelections),
    attachments: O.isSome(jsb.documents),
    groupDiscussion: O.isSome(jsb.groupDiscussion),
    crewSignOff: O.isSome(jsb.crewSignOff),
  };
}

function hashStepSnapshots(stepModels: Steps): Record<StepName, string> {
  return {
    jobInformation: pipe(
      stepModels.jobInformation,
      JobInformation.makeSnapshot,
      snapshotHash
    ),
    medicalEmergency: pipe(
      stepModels.medicalEmergency,
      MedicalEmergency.makeSnapshot,
      snapshotHash
    ),
    tasks: pipe(stepModels.tasks, Tasks.makeSnapshot, snapshotHash),
    energySourceControls: pipe(
      stepModels.energySourceControls,
      EnergySourceControls.makeSnapshot,
      snapshotHash
    ),
    workProcedures: pipe(
      stepModels.workProcedures,
      WorkProcedures.makeSnapshot,
      snapshotHash
    ),
    siteConditions: pipe(
      stepModels.siteConditions,
      SiteConditions.makeSnapshot,
      snapshotHash
    ),
    controlsAssessment: pipe(
      stepModels.controlsAssessment,
      ControlsAssessment.makeSnapshot,
      snapshotHash
    ),
    groupDiscussion: "", // no snapshot for group discussion because there's no data saved
    attachments: pipe(
      stepModels.attachments,
      AttachmentsSection.makeSnapshot,
      snapshotHash
    ),
    crewSignOff: pipe(
      stepModels.crewSignOff,
      CrewSignOff.makeSnapshot,
      snapshotHash
    ),
  };
}

export function init(data: InitData): [Model, Effect<Action>] {
  const { jsbData, projectLocation, dateTime, lastJsb, lastAdhocJsb } = data;

  const jsbId = pipe(
    jsbData,
    O.map(j => j.id)
  );

  const jsbUpdatedAt = pipe(
    jsbData,
    O.chain(j => j.updatedAt)
  );

  const jsbContents = pipe(
    jsbData,
    O.map(j => j.contents)
  );

  const activities = pipe(
    projectLocation,
    O.map(pl => pl.activities),
    O.getOrElse((): Activity[] => [])
  );

  const jsbCreatedAt = pipe(
    jsbData,
    O.chain(j => j.createdAt)
  );

  const stepModels: Steps = {
    jobInformation: JobInformation.init(
      jsbContents,
      projectLocation,
      dateTime,
      jsbCreatedAt,
      lastJsb,
      lastAdhocJsb
    ),
    medicalEmergency: MedicalEmergency.init(jsbContents, lastJsb),
    energySourceControls: EnergySourceControls.init(jsbContents),
    tasks: Tasks.init(jsbContents, activities),
    workProcedures: WorkProcedures.init(jsbContents),
    siteConditions: SiteConditions.init(
      pipe(
        jsbContents,
        O.chain(j => j.siteConditionSelections),
        O.map(
          flow(
            A.filter(sc => sc.selected),
            A.map(sc => sc.id)
          )
        )
      ),
      pipe(
        projectLocation,
        O.map(pl => pl.siteConditions.map(sc => sc.librarySiteCondition.id))
      )
    ),
    controlsAssessment: ControlsAssessment.init(jsbContents),
    groupDiscussion: GroupDiscussion.init(
      jsbContents,
      projectLocation,
      jsbUpdatedAt
    ),
    attachments: AttachmentsSection.init(jsbContents),
    crewSignOff: CrewSignOff.init(jsbContents),
  };

  return [
    {
      steps: stepModels,
      savedSteps: pipe(jsbContents, O.map(checkSavedSteps)),
      stepHashes: hashStepSnapshots(stepModels),
      currentStep: "jobInformation",
      navToStepOnSave: O.none,
      tasks: NotStarted(),
      siteConditions: NotStarted(),
      jsbId: pipe(jsbId, right, Resolved),
      creatorUserId: pipe(
        jsbData,
        O.map(j => j.createdBy.id),
        right,
        Resolved
      ),
      completedByUserId: pipe(
        jsbData,
        O.chain(j => j.completedBy),
        O.map(u => u.id),
        right,
        Resolved
      ),
      projectLocation: pipe(
        projectLocation,
        O.map(pl => ({ ...pl, date: dateTime })),
        Resolved
      ),
      activities: pipe(activities, E.right, Resolved),
      deleteJsbDialog: O.none,
      deleteJsb: NotStarted(),
      nearestMedicalFacilities: NotStarted(),
      locationSiteConditions: NotStarted(),
      discardChangesDialog: O.none,
      completeJsbDialog: O.none,
      selectedTab: FormViewTabStates.FORM,
      libraryRegions: NotStarted(),
    },
    effectsBatch([
      flow(Started, GetTasks, effectOfAction)(),
      flow(Started, GetSiteConditions, effectOfAction)(),
      flow(Started, GetLibraryRegions, effectOfAction)(),
      pipe(
        O.of(GetLocationSiteConditions),
        O.ap(
          pipe(
            jsbContents,
            O.chain(j => j.gpsCoordinates),
            O.chain(A.head)
          )
        ),
        O.ap(
          pipe(
            jsbContents,
            O.chain(j => j.jsbMetadata),
            O.map(meta => meta.briefingDateTime)
          )
        ),
        O.fold(
          () => noEffect,
          getLocSiteCondsFn =>
            flow(Started, getLocSiteCondsFn, effectOfAction)()
        )
      ),
      pipe(
        jsbContents,
        O.chain(j => j.gpsCoordinates),
        O.chain(A.head),
        O.alt(() =>
          pipe(
            projectLocation,
            O.map(
              (pl): GpsCoordinates => ({
                latitude: pl.latitude,
                longitude: pl.longitude,
              })
            )
          )
        ),
        O.fold(
          () => noEffect,
          coords =>
            flow(
              Started,
              GetNearestMedicalFacilities({
                latitude: coords.latitude,
                longitude: coords.longitude,
              }),
              effectOfAction
            )()
        )
      ),
    ]),
  ];
}

export const redirectToWorkPackage = (
  workPackageId: WorkPackageId
): Task<boolean> => {
  const locationId = tt.NonEmptyString.decode(router.query.locationId);
  const source = tt.NonEmptyString.decode(router.query.source);
  const pathOrigin = tt.NonEmptyString.decode(router.query.pathOrigin);
  if (E.isRight(pathOrigin)) {
    return () => router.push(`/forms`);
  } else if (E.isRight(tt.NonEmptyString.decode(workPackageId))) {
    return () =>
      router.push({
        pathname: `/projects/${workPackageId}`,
        query: {
          ...(E.isRight(locationId) && { location: locationId.right }),
          ...(E.isRight(source) && { source: source.right }),
        },
      });
  } else {
    return () => router.push("/projects");
  }
};

const backToProject = (projectId: Option<tt.NonEmptyString>): Task<boolean> => {
  const locationId = tt.NonEmptyString.decode(router.query.locationId);
  const source = tt.NonEmptyString.decode(router.query.source);
  const pathOrigin = tt.NonEmptyString.decode(router.query.pathOrigin);

  if (E.isRight(pathOrigin) && pathOrigin.right === "forms")
    return () => router.push("/forms");

  if (O.isSome(projectId)) {
    return () =>
      router.push({
        pathname: `/projects/${projectId.value}`,
        query: {
          ...(E.isRight(locationId) && { location: locationId.right }),
          ...(E.isRight(source) && { source: source.right }),
        },
      });
  } else {
    return () => router.push("/forms");
  }
};

const withScrollTopEffect = (e: Effect<Action>): Effect<Action> =>
  effectsBatch([e, scrollTopEffect]);

const determineStepsByErrorsEnabled = (
  steps: Steps,
  currentStep: StepName,
  actionStep: StepName
) => {
  return {
    ...steps,
    ...(currentStep === "crewSignOff" &&
      actionStep !== "crewSignOff" && {
        crewSignOff: {
          ...steps.crewSignOff,
          errorsEnabled: true,
        },
      }),
  };
};

export const update =
  (api: Api) =>
  (model: Model, action: Action): [Model, WizardEffect] => {
    switch (action.type) {
      case "NavTo":
        const newModel: Model = {
          ...model,
          steps: {
            ...determineStepsByErrorsEnabled(
              model.steps,
              model.currentStep,
              action.step
            ),
          },
          currentStep: action.step,
          discardChangesDialog: O.none,
        };

        if (action.step === "controlsAssessment") {
          const controlsAssessmentLens = Lens.fromPath<Model>()([
            "steps",
            "controlsAssessment",
          ]);

          const hazards = relevantHazards(model);

          return [
            E.isRight(hazards)
              ? controlsAssessmentLens.modify(
                  ControlsAssessment.preselectControls(hazards.right)
                )(newModel)
              : newModel,
            pipe(
              hazards,
              E.fold(
                e => effectOfFunc_(() => console.log(e), undefined),
                () => noEffect
              ),
              withScrollTopEffect,
              ComponentEffect
            ),
          ];
        } else if (action.step === "groupDiscussion") {
          return [
            newModel,
            pipe(
              // model,
              // toGroupDiscussionData,
              // E.fold(
              //   err => effectOfFunc_(() => console.error(err), undefined),
              //   () => noEffect
              // ),
              // withScrollTopEffect,
              scrollTopEffect,
              ComponentEffect
            ),
          ];
        } else {
          return [newModel, ComponentEffect(scrollTopEffect)];
        }
      case "NavToOnSave": {
        return [
          { ...model, navToStepOnSave: action.step },
          ComponentEffect(scrollTopEffect),
        ];
      }
      case "JobInformationAction":
        return pipe(
          updateJobInformation(model, action.action),
          Tup.mapSnd(ComponentEffect)
        );
      case "MedicalEmergencyAction":
        return pipe(
          updateMedicalEmergency(model, action.action),
          Tup.mapSnd(ComponentEffect)
        );
      case "EnergySourceControlsAction":
        return pipe(
          updateEnergySourceControls(model, action.action),
          Tup.mapSnd(ComponentEffect)
        );
      case "TasksAction": {
        return pipe(
          updateTasks(model, action.action),
          Tup.mapSnd(ComponentEffect)
        );
      }
      case "WorkProceduresAction":
        return pipe(
          updateWorkProcedures(model, action.action),
          Tup.mapSnd(ComponentEffect)
        );
      case "SiteConditionsAction":
        return pipe(
          updateSiteConditions(model, action.action),
          Tup.mapSnd(ComponentEffect)
        );
      case "ControlsAssessmentAction":
        return pipe(
          updateControlsAssessment(model, action.action),
          Tup.mapSnd(ComponentEffect)
        );
      case "CrewSignOffAction":
        return pipe(
          updateCrewSignOff(api)(model, action.action),
          Tup.mapSnd(ComponentEffect)
        );
      case "AttachmentsAction":
        const [attachmentsModel, attachmentsEffect] = AttachmentsSection.update(
          api
        )(model.steps.attachments, action.action);

        switch (attachmentsEffect.type) {
          case "ComponentEffect": {
            return [
              {
                ...model,
                steps: {
                  ...model.steps,
                  attachments: attachmentsModel,
                },
              },
              ComponentEffect(
                mapEffect(AttachmentsAction)(attachmentsEffect.effect)
              ),
            ];
          }
          case "AlertAction": {
            return [
              {
                ...model,
                steps: {
                  ...model.steps,
                  attachments: attachmentsModel,
                },
              },
              AlertAction(attachmentsEffect.action),
            ];
          }
          case "NoEffect": {
            return [
              {
                ...model,
                steps: { ...model.steps, attachments: attachmentsModel },
              },
              NoEffect,
            ];
          }
        }
      case "ShowDeleteJsbDialog":
        return [{ ...model, deleteJsbDialog: O.some(action.jsbId) }, NoEffect];
      case "HideDeleteJsbDialog":
        return [{ ...model, deleteJsbDialog: O.none }, NoEffect];
      case "ShowDiscardChangesDialog":
        return [
          { ...model, discardChangesDialog: O.some(action.step) },
          NoEffect,
        ];
      case "HideDiscardChangesDialog":
        return [{ ...model, discardChangesDialog: O.none }, NoEffect];
      case "ShowCompleteJsbDialog":
        return [
          {
            ...model,
            completeJsbDialog: O.some({
              projectLocationId: action.projectLocationId,
              projectLocationDate: action.projectLocationDate,
              jsbId: action.jsbId,
              input: action.input,
            }),
          },
          NoEffect,
        ];
      case "HideCompleteJsbDialog":
        return [{ ...model, completeJsbDialog: O.none }, NoEffect];
      case "DeleteJsb":
        switch (action.operation.status) {
          case "Started":
            return [
              { ...model, deleteJsb: updatingDeferred(model.deleteJsb) },
              pipe(
                effectOfAsync(
                  api.jsb.deleteJsb(action.jsbId),
                  flow(Finished, DeleteJsb(action.jsbId))
                ),
                ComponentEffect
              ),
            ];
          case "Finished": {
            const projectId = pipe(
              model.projectLocation,
              deferredToOption,
              O.flatten,
              O.map(pl => pl.project.id)
            );
            return [
              { ...model, deleteJsb: Resolved(action.operation.result) },
              pipe(
                action.operation.result,
                E.fold(
                  _e => noEffect,
                  _r => effectOfAsync_(backToProject(projectId))
                ),
                ComponentEffect
              ),
            ];
          }
        }
      case "ReopenJsb":
        switch (action.operation.status) {
          case "Started":
            return [
              model,
              pipe(
                effectOfAsync(
                  api.jsb.reopenJsb(action.jsbId),
                  flow(Finished, ReopenJsb(action.jsbId))
                ),
                ComponentEffect
              ),
            ];

          case "Finished":
            return pipe(
              action.operation.result,
              E.fold(
                (e: ApiError): [Model, Effect<Action>] => [
                  model,
                  effectOfFunc(flow(showApiError, console.error), e, NoAction),
                ],
                (jsbData): [Model, Effect<Action>] => [
                  {
                    ...model,
                    completedByUserId: pipe(
                      jsbData.completedBy,
                      O.map(u => u.id),
                      E.right,
                      Resolved
                    ),
                  },
                  noEffect,
                ]
              ),
              Tup.mapSnd(ComponentEffect)
            );
        }
      case "GetTasks":
        switch (action.operation.status) {
          case "Started":
            return [
              { ...model, tasks: updatingDeferred(model.tasks) },
              pipe(
                effectOfAsync(
                  api.jsb.getTasksLibrary,
                  flow(Finished, GetTasks)
                ),
                ComponentEffect
              ),
            ];
          case "Finished":
            return [
              { ...model, tasks: Resolved(action.operation.result) },
              pipe(
                action.operation.result,
                E.fold(
                  (e: ApiError) =>
                    effectOfFunc(
                      flow(showApiError, console.error),
                      e,
                      NoAction
                    ),
                  () => noEffect
                ),
                ComponentEffect
              ),
            ];
        }
      case "GetSiteConditions":
        switch (action.operation.status) {
          case "Started": {
            return [
              {
                ...model,
                siteConditions: updatingDeferred(model.siteConditions),
              },
              pipe(
                effectOfAsync(
                  api.jsb.getSiteConditionsLibrary,
                  flow(Finished, GetSiteConditions)
                ),
                ComponentEffect
              ),
            ];
          }
          case "Finished":
            return [
              { ...model, siteConditions: Resolved(action.operation.result) },
              NoEffect,
            ];
        }
      case "GetLibraryRegions":
        switch (action.operation.status) {
          case "Started": {
            return [
              {
                ...model,
                libraryRegions: updatingDeferred(model.libraryRegions),
              },
              pipe(
                effectOfAsync(
                  api.jsb.getLibraryRegions,
                  flow(Finished, GetLibraryRegions)
                ),
                ComponentEffect
              ),
            ];
          }
          case "Finished":
            return [
              { ...model, libraryRegions: Resolved(action.operation.result) },
              NoEffect,
            ];
        }
      case "GetLocationSiteConditions":
        switch (action.operation.status) {
          case "Started": {
            return [
              {
                ...model,
                locationSiteConditions: updatingDeferred(
                  model.locationSiteConditions
                ),
              },
              pipe(
                effectOfAsync(
                  api.jsb.getLocationSiteConditions(action.gpsCoordinates)(
                    action.date
                  ),
                  flow(
                    Finished,
                    GetLocationSiteConditions(action.gpsCoordinates)(
                      action.date
                    )
                  )
                ),
                ComponentEffect
              ),
            ];
          }
          case "Finished": {
            const newSiteConditionIds = pipe(
              action.operation.result,
              O.fromEither,
              O.map(A.map(sc => sc.librarySiteCondition.id))
            );
            const attachedProjectLocation = pipe(
              model.projectLocation,
              deferredToOption,
              O.flatten
            );
            return [
              {
                ...model,
                locationSiteConditions: Resolved(action.operation.result),
                steps: pipe(
                  newSiteConditionIds,
                  // only reinitialize the site conditions if the project location is not attached to the JSB
                  // otherwise it has already been initialized with the site conditions form the project location data
                  O.filter(() => O.isNone(attachedProjectLocation)),
                  O.fold(
                    () => model.steps,
                    scIds => ({
                      ...model.steps,
                      siteConditions: SiteConditions.init(
                        pipe(
                          model.steps.siteConditions.selectedIds,
                          S.toArray(ordLibrarySiteConditionId),
                          O.some
                        ),
                        O.some(scIds)
                      ),
                    })
                  )
                ),
              },
              NoEffect,
            ];
          }
        }
      case "GetNearestMedicalFacilities":
        switch (action.operation.status) {
          case "Started": {
            return [
              {
                ...model,
                nearestMedicalFacilities: updatingDeferred(
                  model.nearestMedicalFacilities
                ),
              },
              pipe(
                effectOfAsync(
                  api.jsb.getNearestMedicalFacilities(action.location),
                  flow(Finished, GetNearestMedicalFacilities(action.location))
                ),
                ComponentEffect
              ),
            ];
          }
          case "Finished":
            return [
              {
                ...model,
                nearestMedicalFacilities: pipe(
                  action.operation.result,
                  E.map(facilities => ({
                    ...action.location,
                    nearestMedicalFacilities: facilities,
                  })),
                  Resolved
                ),
              },
              NoEffect,
            ];
        }
      case "SaveJsb": {
        // TODO: refactor the SaveJSB types and data flow to simplify the code below
        const next = O.isSome(model.navToStepOnSave)
          ? model.navToStepOnSave
          : nextStep(model.currentStep);

        switch (action.operation.status) {
          case "Started": {
            const payload: SaveJobSafetyBriefingInput = {
              ...action.input,
              jsbId: pipe(action.jsbId, O.getOrElseW(constNull)),
              workPackageMetadata: pipe(
                action.projectLocationId,
                O.fold(constNull, id => ({ workPackageLocationId: id }))
              ),
              sourceInfo: {
                sourceInformation: SourceAppInformation.WebPortal,
                appVersion: appVersion,
              },
            };

            // TODO: implement nearest medical facilities update when the coordinates change
            // const lastSavedCoordinates = pipe(
            //   model.nearestMedicalFacilities,
            //   deferredToOption,
            //   O.chain(O.fromEither),
            //   O.map(
            //     (x): GpsCoordinates => ({
            //       latitude: x.latitude,
            //       longitude: x.longitude,
            //     })
            //   )
            // );

            // const didCoordinatesChange = (coords: GpsCoordinates) =>
            //   O.isNone(lastSavedCoordinates) ||
            //   !eqGpsCoordinates.equals(coords, lastSavedCoordinates.value);

            // the purpose of this task is
            // - first, call the appropriate api endpoint to save/complete the JSB
            // - then check if the briefing date has changed and update the project location data if it did
            // that's because project location data (site conditions, activities and tasks) can be different depending on the date
            const saveJsbTask = pipe(
              // O.isSome(next)
              action.complete
                ? api.jsb.completeJsb(payload)
                : api.jsb.saveJsb(payload),
              TE.chain(res => {
                return pipe(
                  O.Do,
                  O.bind("date", () =>
                    pipe(
                      res.contents.jsbMetadata,
                      O.map(meta => meta.briefingDateTime),
                      O.filter(
                        // check if the briefing date is different from the last date used to fetch project location
                        briefingDateTime =>
                          O.isNone(action.projectLocationDate) ||
                          !isSameDay(briefingDateTime)(
                            action.projectLocationDate.value
                          )
                      )
                    )
                  ),
                  // O.bind("coords", () =>
                  //   pipe(
                  //     res.contents.gpsCoordinates,
                  //     O.chain(A.head),
                  //     O.filter(didCoordinatesChange)
                  //   )
                  // ),
                  O.bind("task", ({ date }) =>
                    // if the briefing date is different, fetch the project location data for the new date
                    pipe(
                      action.projectLocationId,
                      O.map(
                        flow(
                          api.jsb.getProjectLocation(date),
                          TE.map(
                            O.map(
                              (pl): ProjectLocationData => ({ ...pl, date })
                            )
                          )
                        )
                      )
                    )
                  ),
                  // O.map(({ date, coords }) => )
                  // map the result of the task to a tuple of the JSB save result and the optional updated project location
                  // if the project location is `none`, it means that we don't need to update it
                  O.fold(
                    () => TE.of([res, O.none] as const),
                    ({ task }) =>
                      pipe(
                        task,
                        TE.map(pl => [res, pl] as const)
                      )
                  )
                );
              })
            );

            return [
              {
                ...model,
                jsbId: updatingDeferred(model.jsbId),
              },
              pipe(
                effectOfAsync(
                  saveJsbTask,
                  flow(
                    Finished,
                    SaveJsb(action.complete)(
                      action.projectLocationId,
                      action.projectLocationDate,
                      action.jsbId,
                      payload
                    )
                  )
                ),
                ComponentEffect
              ),
            ];
          }
          case "Finished":
            const result = action.operation.result;

            // Attention!
            // The Optional type in the input of this function encodes whether or not the project location data has changed
            // None - means it didn't change
            // Some - means it changed
            // TODO: come up with a better type design
            const withUpdatedProjectLocation =
              (
                jsbInfo: SavedJsbData,
                projectLocation: Option<ProjectLocationData>
              ) =>
              (m: Steps): Steps =>
                pipe(
                  projectLocation,
                  O.fold(
                    () => m,
                    pl => ({
                      ...m,
                      siteConditions: SiteConditions.init(
                        pipe(
                          jsbInfo.contents.siteConditionSelections,
                          O.map(
                            flow(
                              A.filter(sc => sc.selected),
                              A.map(sc => sc.id)
                            )
                          )
                        ),
                        O.some(
                          pl.siteConditions.map(
                            sc => sc.librarySiteCondition.id
                          )
                        )
                      ),
                    })
                  )
                );

            const withUpdatedGroupDiscussionData =
              (
                jsbInfo: SavedJsbData,
                projectLocation: Option<ProjectLocationData>
              ) =>
              (m: Steps): Steps => ({
                ...m,
                groupDiscussion: GroupDiscussion.init(
                  O.some(jsbInfo.contents),
                  projectLocation,
                  jsbInfo.updatedAt
                ),
              });

            const updatedSteps = pipe(
              action.operation.result,
              E.fold(
                () => model.steps,
                ([r, pl]) =>
                  pipe(
                    model.steps,
                    withUpdatedProjectLocation(r, pl),
                    withUpdatedGroupDiscussionData(r, pl)
                  )
              )
            );
            const defaultGpsCoordinates: GpsCoordinates = {
              latitude: 0,
              longitude: 0,
            };
            // optional function to get the location site conditions (based on the briefing date and coordinates if available)
            const getLocationSiteConditionFn = pipe(
              result,
              O.fromEither,
              O.chain(([savedJsb, _]) =>
                pipe(
                  O.of(GetLocationSiteConditions),
                  O.ap(
                    pipe(
                      savedJsb.contents.gpsCoordinates,
                      O.chain(A.head),
                      O.alt(() => O.some(defaultGpsCoordinates)) // Provide a default GpsCoordinates if the array is empty
                    )
                  ),
                  O.ap(
                    pipe(
                      savedJsb.contents.jsbMetadata,
                      O.map(meta => meta.briefingDateTime)
                    )
                  )
                )
              )
            );

            return [
              {
                ...model,
                navToStepOnSave: O.none,
                jsbId: pipe(
                  action.operation.result,
                  E.map(([r, _]) => some(r.id)),
                  E.alt(() => E.right(action.jsbId)),
                  Resolved
                ),
                projectLocation: pipe(
                  action.operation.result,
                  O.fromEither,
                  O.chain(([_, pl]) => pl),
                  // fallback to the last available project location in case request fails or no update is needed
                  O.alt(() =>
                    pipe(model.projectLocation, deferredToOption, O.flatten)
                  ),
                  Resolved
                ),
                steps: updatedSteps,
                stepHashes: hashStepSnapshots(updatedSteps),
                savedSteps: pipe(
                  action.operation.result, // check if save succeeded
                  E.fold(
                    () => model.savedSteps, // don't update saved steps if save failed
                    () =>
                      pipe(
                        model.savedSteps,
                        O.getOrElse(() => defaultSavedSteps),
                        ss => ({
                          ...ss,
                          [model.currentStep]: true,
                        }), // set the current step as saved
                        O.some
                      )
                  )
                ),
                locationSiteConditions: pipe(
                  getLocationSiteConditionFn,
                  O.fold(
                    // if there's no function to get the location site conditions, default to empty array (otherwise, last value will be preserved)
                    () => pipe([], E.right, Resolved),
                    _ => model.locationSiteConditions
                  )
                ),
              },
              pipe(
                result,
                E.fold(
                  flow(
                    err => {
                      // TODO: replace this unmanaged side effect
                      console.error(err);
                      return err;
                    },
                    showUserApiError,
                    Alert.AlertRequested("error"),
                    AlertAction
                  ),
                  ([savedJsb, _]) => {
                    if (O.isSome(next)) {
                      return pipe(
                        effectsBatch([
                          pipe(NavTo(next.value), effectOfAction),
                          pipe(
                            savedJsb.contents.gpsCoordinates,
                            O.chain(A.head),
                            O.alt(() =>
                              pipe(
                                // fallback to the coordinates of the project location if it has them
                                model.projectLocation,
                                deferredToOption,
                                O.flatten,
                                O.map(
                                  (pl): GpsCoordinates => ({
                                    latitude: pl.latitude,
                                    longitude: pl.longitude,
                                  })
                                )
                              )
                            ),
                            O.fold(
                              () => noEffect,
                              (coords): Effect<Action> =>
                                flow(
                                  Started,
                                  GetNearestMedicalFacilities(coords),
                                  effectOfAction
                                )()
                            )
                          ),
                          pipe(
                            getLocationSiteConditionFn,
                            O.fold(
                              () => noEffect,
                              getLocSiteCondsFn =>
                                flow(
                                  Started,
                                  getLocSiteCondsFn,
                                  effectOfAction
                                )()
                            )
                          ),
                        ]),
                        ComponentEffect
                      );
                    } else if (O.isSome(savedJsb.workPackage)) {
                      return pipe(
                        effectOfAsync_(
                          redirectToWorkPackage(savedJsb.workPackage.value.id)
                        ),
                        ComponentEffect
                      );
                    } else {
                      return ComponentEffect(
                        effectOfAsync_(() => router.push("/forms"))
                      );
                    }
                  }
                )
              ),
            ];
        }
      }

      case "SaveActivity":
        // TODO: consider moving it inside the Tasks component because that's where the activity is created from
        // but there should be a way to update the list of activities in the parent model once the activity is saved
        // which is absolutely not a Tasks component concern
        // this is why it's here now
        if (O.isSome(action.removalTasksData.tasks)) {
          const removalTaskIds = pipe(
            model.activities,
            // Results in an Either
            deferredToOption,
            O.chain(O.fromEither),
            O.map(activities =>
              pipe(
                activities,
                A.findFirst(
                  a =>
                    a.id ===
                    pipe(
                      action.removalTasksData.activityId,
                      O.fold(() => "", identity)
                    )
                )
              )
            ),
            O.fold(
              () => [],
              at =>
                pipe(
                  at,
                  O.fold(
                    () => [],
                    a =>
                      pipe(
                        a.tasks,
                        A.filter(t =>
                          pipe(
                            action.removalTasksData.tasks,
                            O.fold(() => [], identity)
                          ).includes(t.libraryTask.id)
                        )
                      )
                  )
                )
            ),
            A.map(t => t.id)
          );

          switch (action.operation.status) {
            case "Started": {
              // remove the task from activity and update the list of activities returning results from both calls in a tuple
              const removeTasksFromActivity: TE.TaskEither<
                ApiError,
                [ActivityId, Activity[]]
              > = pipe(
                action.removalTasksData.activityId,
                O.fold(
                  () =>
                    TE.left({
                      type: "RequestError",
                      error: "No activity id",
                    } as ApiError),
                  id =>
                    pipe(
                      action.projectLocationId,
                      O.fold(
                        () =>
                          TE.left({
                            type: "RequestError",
                            error: "No location id",
                          } as ApiError),
                        locId =>
                          pipe(
                            TE.Do,
                            TE.bind("removedActivity", () =>
                              api.jsb.removeTasksFromActivity(pipe(id))({
                                taskIdsToBeRemoved: removalTaskIds,
                              })
                            ),
                            TE.bind("updatedActivities", () =>
                              api.jsb.getActivities(locId)
                            ),
                            TE.map(({ removedActivity, updatedActivities }) => [
                              removedActivity.id,
                              updatedActivities,
                            ])
                          )
                      )
                    )
                )
              );

              return [
                { ...model, activities: updatingDeferred(model.activities) },
                pipe(
                  effectOfAsync(
                    removeTasksFromActivity,
                    flow(
                      Finished,
                      SaveActivity(action.input)(action.removalTasksData)(
                        action.additionalTasksData
                      )(action.projectLocationId)
                    )
                  ),
                  ComponentEffect
                ),
              ];
            }
            case "Finished":
              // get the set of task ids for the newly created activity
              const newTaskIds = pipe(
                action.operation.result,
                O.fromEither,
                O.chain(([actId, acts]) =>
                  pipe(
                    acts,
                    A.findFirst(a => a.id === actId)
                  )
                ),
                O.fold(
                  () => new Set<LibraryTaskId>(),
                  act =>
                    pipe(
                      act.tasks,
                      A.map(t => t.libraryTask.id),
                      S.fromArray(eqLibraryTaskId)
                    )
                )
              );
              return [
                {
                  ...model,
                  activities: pipe(
                    action.operation.result,
                    E.map(Tup.snd), // updated activities is the second item in the tuple
                    Resolved
                  ),
                  steps: {
                    ...model.steps,
                    tasks: pipe(
                      model.steps.tasks,
                      // update the selected tasks to include the newly created ones
                      Tasks.withSelectedTaskIds(newTaskIds)
                    ),
                  },
                },
                pipe(
                  action.operation.result,
                  E.fold(
                    e =>
                      effectOfFunc_(
                        () => console.error(e),
                        undefined
                      ) as Effect<Action>,
                    () => noEffect
                  ),
                  ComponentEffect
                ),
              ];
            default:
              return [model, NoEffect];
          }
        } else if (O.isSome(action.additionalTasksData.tasks)) {
          const inputData = pipe(
            action.additionalTasksData.tasks,
            O.fold(
              () => [],
              tasks =>
                pipe(
                  tasks,
                  A.map(t => ({
                    libraryTaskId: t,
                    hazards: [],
                  }))
                )
            )
          );

          switch (action.operation.status) {
            case "Started": {
              // add the task to activity and update the list of activities returning results from both calls in a tuple
              const addTasksToActivity: TE.TaskEither<
                ApiError,
                [ActivityId, Activity[]]
              > = pipe(
                action.additionalTasksData.activityId,
                O.fold(
                  () =>
                    TE.left({
                      type: "RequestError",
                      error: "No activity id",
                    } as ApiError),
                  id =>
                    pipe(
                      action.projectLocationId,
                      O.fold(
                        () =>
                          TE.left({
                            type: "RequestError",
                            error: "No location id",
                          } as ApiError),
                        locId =>
                          pipe(
                            TE.Do,
                            TE.bind("addedActivity", () =>
                              api.jsb.addTasksToActivity(pipe(id))(inputData)
                            ),
                            TE.bind("updatedActivities", () =>
                              api.jsb.getActivities(locId)
                            ),
                            TE.map(({ addedActivity, updatedActivities }) => [
                              addedActivity.id,
                              updatedActivities,
                            ])
                          )
                      )
                    )
                )
              );

              return [
                { ...model, activities: updatingDeferred(model.activities) },
                pipe(
                  effectOfAsync(
                    addTasksToActivity,
                    flow(
                      Finished,
                      SaveActivity(action.input)(action.removalTasksData)(
                        action.additionalTasksData
                      )(action.projectLocationId)
                    )
                  ),
                  ComponentEffect
                ),
              ];
            }
            case "Finished":
              // get the set of task ids for the newly created activity
              const newTaskIds = pipe(
                action.operation.result,
                O.fromEither,
                O.chain(([actId, acts]) =>
                  pipe(
                    acts,
                    A.findFirst(a => a.id === actId)
                  )
                ),
                O.fold(
                  () => new Set<LibraryTaskId>(),
                  act =>
                    pipe(
                      act.tasks,
                      A.map(t => t.libraryTask.id),
                      S.fromArray(eqLibraryTaskId)
                    )
                )
              );
              return [
                {
                  ...model,
                  activities: pipe(
                    action.operation.result,
                    E.map(Tup.snd), // updated activities is the second item in the tuple
                    Resolved
                  ),
                  steps: {
                    ...model.steps,
                    tasks: pipe(
                      model.steps.tasks,
                      // update the selected tasks to include the newly created ones
                      Tasks.withSelectedTaskIds(newTaskIds)
                    ),
                  },
                },
                pipe(
                  action.operation.result,
                  E.fold(
                    e =>
                      effectOfFunc_(
                        () => console.error(e),
                        undefined
                      ) as Effect<Action>,
                    () => noEffect
                  ),
                  ComponentEffect
                ),
              ];
            default:
              return [model, NoEffect];
          }
        } else {
          switch (action.operation.status) {
            case "Started": {
              // save the activity and update the list of activities returning results from both calls in a tuple
              const saveActivityTask: TE.TaskEither<
                ApiError,
                [ActivityId, Activity[]]
              > = pipe(
                TE.Do,
                TE.bind("savedActivity", () =>
                  api.jsb.saveActivity(action.input)
                ),
                TE.bind("updatedActivities", ({ savedActivity }) =>
                  api.jsb.getActivities(savedActivity.location.id)
                ),
                TE.map(({ savedActivity, updatedActivities }) => [
                  savedActivity.id,
                  updatedActivities,
                ])
              );

              return [
                { ...model, activities: updatingDeferred(model.activities) },
                pipe(
                  effectOfAsync(
                    saveActivityTask,
                    flow(
                      Finished,
                      SaveActivity(action.input)({
                        tasks: O.none,
                        activityId: O.none,
                      })({
                        tasks: O.none,
                        activityId: O.none,
                      })(action.projectLocationId)
                    )
                  ),
                  ComponentEffect
                ),
              ];
            }

            case "Finished":
              // get the set of task ids for the newly created activity
              const newTaskIds = pipe(
                action.operation.result,
                O.fromEither,
                O.chain(([actId, acts]) =>
                  pipe(
                    acts,
                    A.findFirst(a => a.id === actId)
                  )
                ),
                O.fold(
                  () => new Set<LibraryTaskId>(),
                  act =>
                    pipe(
                      act.tasks,
                      A.map(t => t.libraryTask.id),
                      S.fromArray(eqLibraryTaskId)
                    )
                )
              );
              return [
                {
                  ...model,
                  activities: pipe(
                    action.operation.result,
                    E.map(Tup.snd), // updated activities is the second item in the tuple
                    Resolved
                  ),
                  steps: {
                    ...model.steps,
                    tasks: pipe(
                      model.steps.tasks,
                      // update the selected tasks to include the newly created ones
                      Tasks.withSelectedTaskIds(newTaskIds)
                    ),
                  },
                },
                pipe(
                  action.operation.result,
                  E.fold(
                    e =>
                      effectOfFunc_(
                        () => console.error(e),
                        undefined
                      ) as Effect<Action>,
                    () => noEffect as Effect<Action>
                  ),
                  ComponentEffect
                ),
              ];

            default:
              return [model, NoEffect];
          }
        }

      case "DeleteActivity":
        switch (action.operation.status) {
          case "Started":
            // delete the activity and update the list of activities returning results from both calls in a tuple
            const saveActivityTask: TE.TaskEither<
              ApiError,
              [ActivityId, Activity[]]
            > = pipe(
              action.projectLocationId,
              O.fold(
                () =>
                  TE.left({
                    type: "RequestError",
                    error: "No location id",
                  } as ApiError),
                locId =>
                  pipe(
                    TE.Do,
                    TE.bind("deletedActivity", () =>
                      api.jsb.deleteActivity(action.activityId)
                    ),
                    TE.bind("updatedActivities", () =>
                      api.jsb.getActivities(locId)
                    ),
                    TE.map(({ updatedActivities }) => [
                      action.activityId,
                      updatedActivities,
                    ])
                  )
              )
            );

            return [
              { ...model, activities: updatingDeferred(model.activities) },
              pipe(
                effectOfAsync(
                  saveActivityTask,
                  flow(
                    Finished,
                    DeleteActivity(action.activityId)(action.projectLocationId)
                  )
                ),
                ComponentEffect
              ),
            ];

          case "Finished":
            // get the set of task ids for the new activities
            const newTaskIds = pipe(
              action.operation.result,
              O.fromEither,
              O.chain(([actId, acts]) =>
                pipe(
                  acts,
                  A.findFirst(a => a.id === actId)
                )
              ),
              O.fold(
                () => new Set<LibraryTaskId>(),
                act =>
                  pipe(
                    act.tasks,
                    A.map(t => t.libraryTask.id),
                    S.fromArray(eqLibraryTaskId)
                  )
              )
            );
            return [
              {
                ...model,
                activities: pipe(
                  action.operation.result,
                  E.map(Tup.snd), // updated activities is the second item in the tuple
                  Resolved
                ),
                steps: {
                  ...model.steps,
                  tasks: pipe(
                    model.steps.tasks,
                    // update the selected tasks to include the newly created ones
                    Tasks.withSelectedTaskIds(newTaskIds)
                  ),
                },
              },
              pipe(
                action.operation.result,
                E.fold(
                  e =>
                    effectOfFunc_(
                      () => console.error(e),
                      undefined
                    ) as Effect<Action>,
                  () => noEffect as Effect<Action>
                ),
                ComponentEffect
              ),
            ];
        }

      default:
        return [model, NoEffect];

      case "SaveSiteCondition":
        switch (action.operation.status) {
          case "Started": {
            const saveSiteConditionTask: TE.TaskEither<
              ApiError,
              LibrarySiteCondition[]
            > = pipe(
              api.jsb.saveSiteCondition(action.input),
              TE.chain(() => api.jsb.getSiteConditionsLibrary)
            );

            return [
              {
                ...model,
                siteConditions: updatingDeferred(model.siteConditions),
              },
              pipe(
                effectOfAsync(
                  saveSiteConditionTask,
                  flow(Finished, SaveSiteCondition(action.input))
                ),
                ComponentEffect
              ),
            ];
          }
          case "Finished": {
            const result = action.operation.result;
            return [
              {
                ...model,
                siteConditions: Resolved(result),
              },
              pipe(
                result,
                E.fold(
                  e =>
                    effectOfFunc_(
                      () => console.error(e),
                      undefined
                    ) as Effect<Action>,
                  () => noEffect
                ),
                ComponentEffect
              ),
            ];
          }
        }

      case "FormSaveAttempted":
        return [
          { ...model, steps: setFormDirty(model.steps, model.currentStep) },
          NoEffect,
        ];

      case "FormViewStateChange":
        return [
          {
            ...model,
            selectedTab: action.selectedTab,
          },
          NoEffect,
        ];

      case "NoAction":
        return [model, NoEffect];
    }
  };

const stepStatus = (step: StepName, model: Model): Status => {
  const stepSaved = pipe(
    model.savedSteps,
    O.fold(constFalse, ss => ss[step])
  );

  switch (true) {
    case !stepSaved &&
      model.currentStep === "jobInformation" &&
      (step === "jobInformation" || step === "medicalEmergency"):
      return "default";

    case (!stepSaved &&
      model.currentStep === "medicalEmergency" &&
      step === "jobInformation") ||
      (!stepSaved &&
        model.currentStep !== "medicalEmergency" &&
        (step === "jobInformation" || step === "medicalEmergency")):
      return "error";

    case !stepSaved &&
      model.currentStep !== "jobInformation" &&
      model.currentStep !== "medicalEmergency" &&
      model.currentStep !== "tasks" &&
      (step === "jobInformation" ||
        step === "medicalEmergency" ||
        step === "tasks"):
      return "error";

    default:
      if (stepSaved) {
        return pipe(
          stepResult(step, model),
          E.fold(
            (): Status => "error",
            (): Status =>
              model.currentStep === step ? "saved_current" : "saved"
          )
        );
      } else {
        return model.currentStep === step ? "current" : "default";
      }
  }
};

export type Props = ChildProps<Model, Action> & {
  projectLocationId: Option<ProjectLocationId>;
  workPackageLabel: string;
  checkPermission: (permission: UserPermission) => boolean;
  userId: NonEmptyString;
};
export function View(props: Props): JSX.Element {
  const { model, dispatch } = props;
  const [jsbFormAuditData, setJsbFormAuditData] = useState<[]>([]);
  const toastCtx = useContext(ToastContext);

  useLeavePageConfirm(
    "Discard unsaved changes?",
    checkUnsavedChanges(model.steps, model.stepHashes)
  );

  // check if current user is the creator of the JSB
  // const isOwnForm = useMemo(
  //   () =>
  //     pipe(
  //       model.creatorUserId,
  //       deferredToOption,
  //       E.fromOption(() => "Creator user id is not available"),
  //       E.chainW(identity),
  //       E.map(
  //         O.fold(
  //           // if the form hasn't been saved yet, the creator user id is None
  //           // which means the current user is the owner of the form
  //           () => true,
  //           creatorId => eqNonEmptyString.equals(creatorId, props.userId)
  //         )
  //       ),
  //       // if the creator id is not available, we assume the user is not the owner of the form
  //       E.getOrElseW(() => false)
  //     ),
  //   [model.creatorUserId, props.userId]
  // );

  const isFormCompleted = useMemo(
    () =>
      pipe(
        model.completedByUserId,
        deferredToOption,
        O.chain(O.fromEither),
        O.flatten,
        O.isSome
      ),
    [model.completedByUserId]
  );

  // const hasEditPermissions =
  //   props.checkPermission("EDIT_REPORTS") ||
  //   (props.checkPermission("EDIT_OWN_REPORTS") && isOwnForm);

  // const isEditable = !isFormCompleted && hasEditPermissions;
  const isEditable = true; // temporarily disable the "read-only" view

  const hasReopenPermission = props.checkPermission("REOPEN_REPORTS");

  // const hasDeletePermission =
  //   props.checkPermission("DELETE_REPORTS") ||
  //   (props.checkPermission("DELETE_OWN_REPORTS") && isOwnForm);
  const hasDeletePermission = true; // temporarily disable the "delete" permissions check

  const isFinalStep = useMemo(
    () => pipe(model.currentStep, nextStep, O.isNone),
    [model.currentStep]
  );

  const saveJsbInput = toJsbInput(model);

  const pathOrigin: Option<NonEmptyString> = O.fromEither(
    tt.NonEmptyString.decode(router.query.pathOrigin)
  );

  const actionsMenuItems: Option<NonEmptyArray<MenuItemProps>> = pipe(
    model.jsbId,
    deferredToOption,
    O.chain(O.fromEither),
    O.flatten,
    O.chain(jsbId => {
      const reopenJsbItem: MenuItemProps = {
        label: "Edit",
        icon: "edit",
        onClick: flow(Started, ReopenJsb(jsbId), dispatch),
      };

      const deleteJsbItem: MenuItemProps = {
        label: "Delete",
        icon: "trash_empty",
        onClick: flow(constant(jsbId), ShowDeleteJsbDialog, dispatch),
      };

      const downloadJsbItem: MenuItemProps = {
        label: "Download PDF",
        icon: "download",
        onClick: () => {
          const routeHandler = router.query;
          const locationId = routeHandler.locationId;
          if (locationId) {
            router.push(
              `/jsb-share/${jsbId}?locationId=${locationId}&printPage=true`
            );
          } else {
            router.push(`/jsb-share/${jsbId}?printPage=true`);
          }
        },
      };

      return pipe(
        [
          O.fromPredicate(() => isFormCompleted && hasReopenPermission)(
            reopenJsbItem
          ),
          O.fromPredicate(() => isEditable && hasDeletePermission)(
            deleteJsbItem
          ),
          O.fromPredicate(
            () => isFormCompleted && isEditable && hasDeletePermission
          )(downloadJsbItem),
        ],
        A.compact,
        NEA.fromArray
      );
    })
  );

  const generateHeaderLinkRoute = (): string | RouterLink => {
    return pipe(
      pathOrigin,
      O.fold(
        (): string | RouterLink => {
          const locationId = tt.NonEmptyString.decode(router.query.locationId);
          const source = tt.NonEmptyString.decode(router.query.source);
          if (O.isSome(pathOrigin) && pathOrigin.value === "form") {
            return "/forms";
          } else {
            if (O.isSome(projectId)) {
              return {
                pathname: `/projects/${projectId.value}`,
                query: {
                  ...(E.isRight(locationId) && { location: locationId.right }),
                  ...(E.isRight(source) && { source: source.right }),
                },
              };
            } else {
              return "/forms";
            }
          }
        },
        () => "/forms"
      )
    );
  };

  const saveJsb: () => void = pipe(
    E.Do,
    E.bindW("jsbId", () =>
      pipe(
        model.jsbId,
        E.fromPredicate(isResolved, constNull),
        E.chainW(r => r.value)
      )
    ),
    E.bindW("projectLocationDate", () =>
      pipe(
        model.projectLocation,
        E.fromPredicate(isResolved, constNull),
        E.map(r =>
          pipe(
            r.value,
            O.map(pl => pl.date)
          )
        )
      )
    ),
    E.bindW("input", () =>
      pipe(
        nextStep(model.currentStep),
        O.fold(
          // when there is no next step, we need to check that all previous steps are saved before completing the form
          // for that, we can use group discussion data which is populated from the completed and saved steps
          () =>
            pipe(
              model.steps.groupDiscussion,
              E.filterOrElse(
                gd => gd.viewed,
                () => "Group discussion has not been viewed"
              ),
              E.chainW(_ => saveJsbInput)
            ),
          _ => {
            if (
              model.currentStep === "tasks" &&
              S.isEmpty(model.steps.tasks.selectedTaskIds)
            ) {
              return E.left("NO_TASK_SELECTED");
            } else {
              return saveJsbInput;
            }
          }
        )
      )
    ),
    E.fold(
      _ => () => {
        const invalidInputs = document.querySelectorAll(
          "[required]:invalid, [role='select']"
        );
        if (invalidInputs.length > 0) {
          invalidInputs[0].scrollIntoView({
            behavior: "smooth",
          });
        }
        dispatch(FormSaveAttempted());
      },
      ({ jsbId, input, projectLocationDate }) =>
        isFinalStep
          ? () =>
              dispatch(
                ShowCompleteJsbDialog(
                  props.projectLocationId,
                  projectLocationDate,
                  jsbId,
                  input
                )
              )
          : flow(
              Started,
              SaveJsb(false)(
                props.projectLocationId,
                projectLocationDate,
                jsbId,
                input
              ),
              dispatch
            )
    )
  );

  const headerSubTitle = pipe(
    model.projectLocation,
    deferredToOption,
    O.flatten,
    O.chain(r => NEA.fromArray([r.project.name, r.name])),
    O.map(a => a.join(" • "))
  );

  const headerProjectDescription = pipe(
    model.projectLocation,
    deferredToOption,
    O.flatten,
    O.chain(r => r.project.description)
  );

  const projectLocationRiskLevel = pipe(
    model.projectLocation,
    deferredToOption,
    O.flatten,
    O.map(r => r.riskLevel),
    O.getOrElse(() => RiskLevel.Unknown)
  );

  const { formList } = useTenantStore(state => state.getAllEntities());
  const labelSetByAdmin = "All " + formList.labelPlural;

  const Header = (): JSX.Element => (
    <PageHeader
      linkText={
        router.query?.pathOrigin === "forms"
          ? labelSetByAdmin
          : `${props.workPackageLabel} Summary View`
      }
      linkRoute={generateHeaderLinkRoute()}
      setSelectedTab={(selectedTab: FormViewTabStates) =>
        dispatch(ChangeFormViewState(selectedTab))
      }
      selectedTab={model.selectedTab}
    >
      <div className="w-full flex flex-row justify-between">
        <div className="flex flex-col w-full">
          <div className="flex w-full items-center">
            <h4 className="text-neutral-shade-100 mr-3">Job Safety Briefing</h4>
            <span className="inline-flex items-center">
              <RiskBadge
                risk={projectLocationRiskLevel}
                label={projectLocationRiskLevel}
              />
            </span>
          </div>
          <OptionalView
            value={headerSubTitle}
            render={st => (
              <h3 className="block text-sm text-neutral-shade-58">{st}</h3>
            )}
          />
          <OptionalView
            value={headerProjectDescription}
            render={st => (
              <div className="mt-3 w-full">
                <ProjectDescriptionHeader
                  maxCharacters={isMobileOnly ? 35 : 80}
                  description={st}
                />
              </div>
            )}
          />
        </div>
        <OptionalView
          value={actionsMenuItems}
          render={items => (
            <Dropdown className="z-20" menuItems={[items]}>
              <ButtonIcon iconName="hamburger" />
            </Dropdown>
          )}
        />
      </div>
    </PageHeader>
  );

  const Footer = (): JSX.Element => (
    <footer
      className={cx("flex flex-col mt-auto md:max-w-screen-lg items-end", {
        "p-4 px-0": !isMobile && !isTablet,
        "p-2.5 h-[54px]": isMobile || isTablet,
      })}
    >
      {isEditable && (
        <ButtonPrimary
          label={isFinalStep ? "Save and Complete" : "Save and Continue"}
          loading={isInProgress(model.jsbId) || isUpdating(model.jsbId)}
          onClick={saveJsb}
        />
      )}
    </footer>
  );

  const renderOptionFn: RenderOptionFn<NavigationOption> = ({
    listboxOptionProps: { selected },
    option: { name, icon, status },
  }) => (
    <NavItem
      as="li"
      icon={icon}
      name={name}
      status={status}
      markerType="left"
      isSelected={selected}
    />
  );

  const getSelectStatusAndIcon = (step: StepName): SelectStatusAndIcon => {
    const status = stepStatus(step, model);
    switch (status) {
      case "default":
      case "current":
        return { status: "default", icon: "circle" };
      case "error":
        return { status, icon: "error" };
      case "saved":
      case "saved_current":
        return { status: "completed", icon: "circle_check" };
    }
  };

  const selectOptions = stepList.map((step, index) => {
    const { status, icon } = getSelectStatusAndIcon(step);
    return {
      name: stepNames[step],
      id: index,
      status,
      icon,
    };
  });

  const directNavigation = (step: StepName): void => {
    return dispatch(NavTo(step));
  };

  const wizardNavigation = (
    <>
      <Select
        className={cx(
          "!absolute md:hidden block pb-4 pt-4 w-[calc(100%-24px)]"
        )}
        options={selectOptions}
        onSelect={({ id }) => directNavigation(stepList[id])}
        defaultOption={pipe(
          selectOptions,
          A.lookup(stepList.indexOf(model.currentStep)),
          O.fold(() => undefined, identity)
        )}
        optionsClassNames="py-2"
        renderOptionFn={renderOptionFn}
      />
      <div className="md:flex hidden md:gap-2 md:flex-col ">
        {stepList.map(step => (
          <Fragment key={step.toString()}>
            <StepItem
              status={stepStatus(step, model)}
              key={step.toString()}
              onClick={flow(constant(step), directNavigation)}
              label={
                stepNames[step] === "Group Discussion"
                  ? GroupDiscussion.locationCheck().labelName
                  : stepNames[step]
              }
            />
          </Fragment>
        ))}
      </div>
    </>
  );

  const projectId = useMemo(
    () =>
      pipe(
        model.projectLocation,
        deferredToOption,
        O.flatten,
        O.map(pl => pl.project.id)
      ),
    [model.projectLocation]
  );

  const jsbFormId = pipe(
    model.jsbId,
    deferredToOption,
    O.chain(O.fromEither),
    O.flatten,
    O.getOrElse(() => "")
  );

  const { mutate: fetchFormsAuditLogsData, isLoading } = useRestMutation<any>({
    endpoint: `${config.workerSafetyAuditTrailServiceRest}/logs/list/`,
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: data => data,
    mutationOptions: {
      onSuccess: async (response: any) => {
        setJsbFormAuditData(response.data);
      },
      onError: error => {
        console.log(error);
        toastCtx?.pushToast("error", messages.SomethingWentWrong);
      },
    },
  });

  useEffect(() => {
    if (jsbFormId && model.selectedTab === FormViewTabStates.HISTORY) {
      const requestData = {
        object_id: jsbFormId,
        object_type: "jsb",
        order_by: {
          field: "created_at",
          desc: true,
        },
      };
      fetchFormsAuditLogsData(requestData);
    }
  }, [jsbFormId, model.selectedTab]);

  const jsbWorkLocation = pipe(
    model.projectLocation,
    deferredToOption,
    O.flatten,
    O.map(r => r.name),
    O.getOrElse(() => "")
  );

  return (
    <PageLayout
      className="md:mt-6 md:pl-6 flex-1 overflow-hidden w-full max-w-screen-lg"
      sectionPadding="none"
      header={<Header />}
      footer={model.selectedTab === FormViewTabStates.FORM && <Footer />}
    >
      {model.selectedTab === FormViewTabStates.FORM ? (
        <Nav.View wizardNavigation={wizardNavigation}>
          <StepView {...props} isReadOnly={!isEditable} />
        </Nav.View>
      ) : (
        <FormHistory
          data={jsbFormAuditData}
          isAuditDataLoading={isLoading}
          location={jsbWorkLocation}
        />
      )}

      <OptionalView
        value={model.deleteJsbDialog}
        render={id => {
          switch (model.deleteJsb.status) {
            case "NotStarted":
              return (
                <Modal
                  isOpen={true}
                  closeModal={flow(HideDeleteJsbDialog, dispatch)}
                  title="Are you sure you want to delete this JSB?"
                >
                  <div className="flex flex-col gap-4">
                    <p>
                      Once removed, you will no longer have access to edit this
                      specific JSB.
                    </p>
                    <footer className="flex justify-end gap-4 pt-4 pb-0 px-6 w-[calc(100%+48px)] -left-6 relative">
                      <ButtonTertiary
                        label="Cancel"
                        onClick={flow(HideDeleteJsbDialog, dispatch)}
                      />
                      <ButtonDanger
                        label="Delete JSB"
                        onClick={flow(Started, DeleteJsb(id), dispatch)}
                      />
                    </footer>
                  </div>
                </Modal>
              );
            case "InProgress":
            case "Updating":
              return (
                <Modal
                  isOpen={true}
                  closeModal={flow(HideDeleteJsbDialog, dispatch)}
                  title="Deleting"
                />
              );
            case "Resolved":
              return E.isLeft(model.deleteJsb.value) ? (
                <Modal
                  isOpen={true}
                  closeModal={flow(HideDeleteJsbDialog, dispatch)}
                  title="Failed to delete"
                >
                  <div className="flex flex-col gap-4">
                    <p>Please try again</p>
                    <footer className="flex justify-end gap-4 pt-4 pb-0 px-6 w-[calc(100%+48px)] -left-6 relative">
                      <ButtonTertiary
                        label="Cancel"
                        onClick={flow(HideDeleteJsbDialog, dispatch)}
                      />
                    </footer>
                  </div>
                </Modal>
              ) : (
                <></>
              );
          }
        }}
      />

      <OptionalView
        value={model.discardChangesDialog}
        render={step => (
          <Modal
            isOpen={true}
            closeModal={flow(HideDiscardChangesDialog, dispatch)}
            title="Discard changes?"
          >
            <div className="flex flex-col gap-4">
              <p>Current changes will not be saved</p>
              <footer className="flex justify-end gap-4 pt-4 pb-0 px-6 w-[calc(100%+48px)] -left-6 relative">
                <ButtonDanger
                  label="Discard"
                  onClick={flow(constant(step), NavTo, dispatch)}
                />
                <ButtonTertiary
                  label="Cancel"
                  onClick={flow(HideDiscardChangesDialog, dispatch)}
                />
              </footer>
            </div>
          </Modal>
        )}
      />

      <OptionalView
        value={model.completeJsbDialog}
        render={completeModel => (
          <Modal
            isOpen={true}
            closeModal={flow(HideCompleteJsbDialog, dispatch)}
            title="Complete/Submit form?"
          >
            <div className="flex flex-col gap-4">
              <p>Are you sure you want to complete/submit this form?</p>
              <footer className="flex justify-end gap-4 pt-4 pb-0 px-6 w-[calc(100%+48px)] -left-6 relative">
                <ButtonPrimary
                  label="Complete form"
                  onClick={flow(
                    Started,
                    SaveJsb(true)(
                      completeModel.projectLocationId,
                      completeModel.projectLocationDate,
                      completeModel.jsbId,
                      completeModel.input
                    ),
                    dispatch
                  )}
                />
              </footer>
            </div>
          </Modal>
        )}
      />
    </PageLayout>
  );
}

function StepView(props: Props & { isReadOnly: boolean }): JSX.Element {
  const { model, dispatch } = props;
  const hazards = relevantHazards(model);
  const activities = todaysActivities(model);

  const tasksLibrary = useMemo(
    () =>
      pipe(
        model.tasks,
        mapDeferred(
          E.map(
            flow(
              A.map((task): [LibraryTaskId, LibraryTask] => [task.id, task]),
              M.fromFoldable(
                eqLibraryTaskId,
                SG.first<LibraryTask>(),
                A.Foldable
              )
            )
          )
        )
      ),
    [model.tasks]
  );

  const riskLevels = useMemo(
    () =>
      pipe(
        tasksLibrary,
        deferredToOption,
        O.chain(O.fromEither),
        O.fold(
          () => new Map<LibraryTaskId, RiskLevel>(),
          tasks => taskRiskLevels(activities, tasks)
        )
      ),
    [activities, tasksLibrary]
  );

  const medicalFacilities = useMemo(
    () =>
      pipe(
        model.nearestMedicalFacilities,
        mapDeferred(E.map(data => data.nearestMedicalFacilities))
      ),
    [model.nearestMedicalFacilities]
  );

  switch (model.currentStep) {
    case "jobInformation":
      return (
        <JobInformation.View
          model={model.steps[model.currentStep]}
          libraryRegions={model.libraryRegions}
          dispatch={flow(JobInformationAction, dispatch)}
          isReadOnly={props.isReadOnly}
        />
      );
    case "medicalEmergency":
      return (
        <MedicalEmergency.View
          model={model.steps[model.currentStep]}
          dispatch={flow(MedicalEmergencyAction, dispatch)}
          nearestMedicalFacilities={medicalFacilities}
          isReadOnly={props.isReadOnly}
        />
      );
    case "energySourceControls":
      return (
        <EnergySourceControls.View
          model={model.steps[model.currentStep]}
          dispatch={flow(EnergySourceControlsAction, dispatch)}
          isReadOnly={props.isReadOnly}
        />
      );
    case "tasks":
      if (isResolved(model.tasks) && isRight(model.tasks.value)) {
        return (
          <Tasks.View
            model={model.steps[model.currentStep]}
            dispatch={flow(TasksAction, dispatch)}
            locationId={props.projectLocationId}
            tasks={model.tasks.value.right}
            activities={activities}
            saveActivity={(
              a: CreateActivityInput,
              removalTasksData: {
                tasks: Option<LibraryTaskId[]>;
                activityId: Option<ActivityId>;
              },
              additionalTasksData: {
                tasks: Option<LibraryTaskId[]>;
                activityId: Option<ActivityId>;
              }
            ) => {
              flow(
                Started,
                SaveActivity(a)(removalTasksData)(additionalTasksData)(
                  props.projectLocationId
                ),
                dispatch
              )();
            }}
            deleteActivity={(activityId: ActivityId) => {
              flow(
                Started,
                DeleteActivity(activityId)(props.projectLocationId),
                dispatch
              )();
            }}
            isReadOnly={props.isReadOnly}
          />
        );
      } else if (isResolved(model.tasks) && isLeft(model.tasks.value)) {
        return <div>Error: {model.tasks.value.left.type}</div>;
      } else {
        return <div>Loading...</div>;
      }

    case "workProcedures":
      return (
        <WorkProcedures.View
          model={model.steps[model.currentStep]}
          dispatch={flow(WorkProceduresAction, dispatch)}
          isReadOnly={props.isReadOnly}
        />
      );

    case "siteConditions":
      if (
        isResolved(model.siteConditions) &&
        isRight(model.siteConditions.value)
      ) {
        return (
          <SiteConditions.View
            model={model.steps[model.currentStep]}
            dispatch={flow(SiteConditionsAction, dispatch)}
            siteConditions={model.siteConditions.value.right}
            isReadOnly={props.isReadOnly}
            locationId={props.projectLocationId}
            saveSiteCondition={(a: CreateSiteConditionInput) => {
              flow(Started, SaveSiteCondition(a), dispatch)();
            }}
          />
        );
      } else if (
        isResolved(model.siteConditions) &&
        isLeft(model.siteConditions.value)
      ) {
        return <div>Error: {model.siteConditions.value.left.type}</div>;
      } else {
        return <div>Loading...</div>;
      }

    case "controlsAssessment":
      if (
        isRight(hazards) &&
        isResolved(model.tasks) &&
        isRight(model.tasks.value)
      ) {
        return (
          <ControlsAssessment.View
            model={model.steps.controlsAssessment}
            dispatch={flow(ControlsAssessmentAction, dispatch)}
            hazards={hazards.right}
            tasks={model.tasks.value.right}
            isReadOnly={props.isReadOnly}
          />
        );
      } else if (isResolved(model.tasks) && isLeft(model.tasks.value)) {
        return <div>Error: {model.tasks.value.left.type}</div>;
      } else if (isLeft(hazards)) {
        return <div>Error: {hazards.left}</div>;
      } else {
        return <div>Loading...</div>;
      }

    case "attachments":
      return (
        <AttachmentsSection.View
          model={model.steps[model.currentStep]}
          dispatch={flow(AttachmentsAction, dispatch)}
          isReadOnly={props.isReadOnly}
        />
      );

    case "groupDiscussion": {
      return (
        <GroupDiscussion.View
          isReadOnly={props.isReadOnly}
          groupDiscussionData={model.steps.groupDiscussion}
          tasksLibrary={model.tasks}
          siteConditionsLibrary={model.siteConditions}
          riskLevels={riskLevels}
          onClickEdit={(step: StepName) => {
            dispatch(NavToOnSave(O.some(model.currentStep)));
            dispatch(NavTo(step));
          }}
          jsbId={pipe(
            model.jsbId,
            deferredToOption,
            O.chain(O.fromEither),
            O.flatten,
            O.getOrElse(() => "")
          )}
        />
      );
    }

    case "crewSignOff":
      return (
        <CrewSignOff.View
          model={model.steps[model.currentStep]}
          dispatch={flow(CrewSignOffAction, dispatch)}
          isReadOnly={props.isReadOnly}
          jsbId={pipe(
            model.jsbId,
            deferredToOption,
            O.chain(O.fromEither),
            O.flatten,
            O.getOrElse(() => "")
          )}
        />
      );
  }
}
