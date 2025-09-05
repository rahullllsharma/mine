import type {
  CrewMember,
  Ebo,
  EboId,
  Hazard,
  HighEnergyTasksObservations,
  Incident,
  LibraryTask,
  LibraryTaskId,
  SavedEboInfo,
  TaskHazardConnectorId,
  WorkType,
} from "@/api/codecs";
import type {
  EnergyBasedObservationInput,
  EboHazardObservationConceptInput,
  QueryTenantLinkedHazardsLibraryArgs,
} from "@/api/generated/types";
import type { AsyncOperationStatus } from "@/utils/asyncOperationStatus";
import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type * as t from "io-ts";
import type { Api, ApiError, ApiResult } from "@/api/api";
import type { Either } from "fp-ts/lib/Either";
import type { Option } from "fp-ts/lib/Option";
import type { ObservationDetailsData } from "./Summary/observationDetailsSummary";
import type { HazardsData } from "./Summary/hazardsSummary";
import type { HistoricIncidentsData } from "./Summary/historicIncidentsSummary";
import type { AdditionalInformationData } from "./Summary/additionalInformationSummary";
import type { PhotosData } from "./Summary/photosSummary";
import type { Status } from "../Basic/StepItem";
import type {
  NavigationOption,
  SelectStatusAndIcon,
} from "@/components/navigation/Navigation";
import type { RenderOptionFn } from "@/components/shared/select/Select";
import type { Deferred } from "@/utils/deferred";
import type { NonEmptyString } from "io-ts-types";
import type { NonEmptyArray } from "fp-ts/lib/NonEmptyArray";
import type { UserPermission } from "../../../types/auth/AuthUser";
import type { MenuItemProps } from "../../shared/dropdown/Dropdown";
import { v4 as uuid } from "uuid";
import { useCallback, useMemo, useEffect, useState, useContext } from "react";
import { isRight, right } from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import * as E from "fp-ts/lib/Either";
import * as A from "fp-ts/lib/Array";
import * as EQ from "fp-ts/Eq";
import * as M from "fp-ts/lib/Map";
import * as R from "fp-ts/lib/Record";
import * as S from "fp-ts/lib/Set";
import * as Tup from "fp-ts/Tuple";
import * as TE from "fp-ts/lib/TaskEither";
import * as NEA from "fp-ts/lib/NonEmptyArray";
import cx from "classnames";
import { sequenceS } from "fp-ts/lib/Apply";
import * as tt from "io-ts-types";
import { constant, constNull, flow, identity, pipe } from "fp-ts/lib/function";
import { DateTime } from "luxon";
import { isMobile, isTablet } from "react-device-detect";
import router from "next/router";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import { match as matchBoolean } from "fp-ts/lib/boolean";
import { useLazyQuery } from "@apollo/client";
import { Select } from "@/components/shared/select/Select";
import {
  isResolved,
  isUpdating,
  NotStarted,
  Resolved,
  updatingDeferred,
  deferredToOption,
} from "@/utils/deferred";
import { showApiError, showUserApiError } from "@/api/api";
import {
  effectOfAction,
  effectOfAsync,
  effectOfAsync_,
  effectOfFunc,
  effectsBatch,
  mapEffect,
  noEffect,
} from "@/utils/reducerWithEffect";
import { Finished, Started } from "@/utils/asyncOperationStatus";
import { EnergyLevel, ordLibraryTaskId } from "@/api/codecs";
import {
  SourceAppInformation,
  LibraryFilterType,
  FormStatus,
} from "@/api/generated/types";
import Modal from "@/components/shared/modal/Modal";
import Paragraph from "@/components/shared/paragraph/Paragraph";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import NavItem from "@/components/navigation/navItem/NavItem";
import PageHeader from "@/components/layout/pageHeader/PageHeader";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import useLeavePageConfirm from "@/hooks/useLeavePageConfirm";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import useRestMutation from "@/hooks/useRestMutation";
import { config } from "@/config";
import axiosRest from "@/api/restApi";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { messages } from "@/locales/messages";
import TenantWorkTypes from "@/graphql/queries/tenantWorkTypes.gql";
import WorkTypeLinkedLibraryTasks from "@/graphql/queries/workTypeLinkedLibraryTasks.gql";
import { OptionalView } from "../../common/Optional";
import Dropdown from "../../shared/dropdown/Dropdown";
import { StepItem } from "../Basic/StepItem";
import {
  eqNonEmptyString,
  scrollTopEffect,
  snapshotHash,
  FormViewTabStates,
} from "../Utils";
import * as Alert from "../Alert";
import * as Nav from "../Navigation";
import PageLayout from "../../layout/pageLayout/PageLayout";
import ButtonPrimary from "../../shared/button/primary/ButtonPrimary";
import { FormHistory } from "../FormHistory/FormHistory";
import packageJson from "../../../../package.json";
import * as AdditionalInformation from "./AdditionalInformation";
import * as ObservationDetails from "./ObservationDetails";
import * as HighEnergyTasks from "./HighEnergyTasks";
import { getAllTaskIdsFromActivities, getNextSubStep } from "./HighEnergyTasks";
import * as HighEnergyTasksSubSection from "./HighEnergyTaskSubSection/HighEnergyTaskSubSection";
import * as PersonnelSection from "./PersonnelSection";
import * as PhotosSection from "./PhotosSection";
import * as Summary from "./Summary";
import * as HistoricIncidents from "./HistoricIncidents";
import { getTenantName } from "./TenantLabel/LabelOnBasisOfTenant";

export const eqCompletedStep = EQ.contramap((step: string) => step)(EqString);

type Steps = {
  observationDetails: ObservationDetails.Model;
  highEnergyTasks: HighEnergyTasks.Model;
  historicIncidents: HistoricIncidents.Model;
  additionalInformation: AdditionalInformation.Model;
  photos: PhotosSection.Model;
  summary: Summary.Model;
  personnelSection: PersonnelSection.Model;
};

export type StepName = keyof Steps;

const getStepListForTenant = (tenantName: string): StepName[] => {
  if (
    tenantName === "xcelenergy" ||
    tenantName === "test-xcelenergy" ||
    tenantName === "test-xcelenergy1"
  ) {
    return [
      "observationDetails",
      "highEnergyTasks",
      "additionalInformation",
      "historicIncidents",
      "photos",
      "summary",
    ];
  } else {
    return [
      "observationDetails",
      "highEnergyTasks",
      "additionalInformation",
      "historicIncidents",
      "photos",
      "summary",
      "personnelSection",
    ];
  }
};

export type EboSnapshots = Record<StepName, string>;

export type TaskHistoricalIncidents = {
  taskId: LibraryTaskId;
  result: Incident[];
};

const appVersion = packageJson.version;

const stepNames: Record<StepName, string> = {
  observationDetails: "Observation Details",
  highEnergyTasks: "High Energy Tasks",
  historicIncidents: "Historical Incidents",
  additionalInformation: "Additional Information",
  photos: "Photos",
  summary: "Summary",
  personnelSection: "Personnel",
};

export type Model = {
  steps: Steps;
  snapshots: EboSnapshots;
  currentStep: StepName;
  fromStep: Option<StepName>;
  tasks: Deferred<ApiResult<LibraryTask[]>>;
  hazards: Deferred<ApiResult<Hazard[]>>;
  workTypes: Deferred<ApiResult<WorkType[]>>;
  crewMembers: Deferred<ApiResult<CrewMember[]>>;
  eboId: Deferred<ApiResult<Option<EboId>>>;
  selectedTasksIncidents: Deferred<ApiResult<TaskHistoricalIncidents[]>>;
  completedSteps: Set<string>;
  showDeleteEboModal: O.Option<EboId>;
  showCompleteEboModal: boolean;
  showWorkTypeBasedActivityRemovalModal: boolean;
  isRedirectAfterFormSave: boolean;
  creatorUserId: Deferred<ApiResult<Option<NonEmptyString>>>; // refers to user who created this ebo
  completedByUserId: Deferred<ApiResult<Option<NonEmptyString>>>; // refers to user who completed this ebo
  status: Deferred<ApiResult<Option<FormStatus>>>; // refers to the status of form instance
  selectedTab: FormViewTabStates;
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

export const ComponentEffect = (effect: Effect<Action>): WizardEffect => ({
  type: "ComponentEffect",
  effect,
});

const AlertAction = (action: Alert.Action): WizardEffect => ({
  type: "AlertAction",
  action,
});

const NoEffect: WizardEffect = { type: "NoEffect" };

export type eboFormValidationError = { type: "form_validation"; msg: string };

export type eboSectionValidationError = t.Errors | eboFormValidationError;

function toEboInput(
  model: Model
): Either<eboSectionValidationError, EnergyBasedObservationInput> {
  const observationDetailsResult = flow(
    constant(model.steps.observationDetails),
    ObservationDetails.toSaveEboInput
  );

  const mergedHighEnergyTasksResult = () => {
    if (
      isResolved(model.tasks) &&
      E.isRight(model.tasks.value) &&
      isResolved(model.hazards) &&
      isRight(model.hazards.value)
    ) {
      const hazards = model.hazards.value.right;
      const tasks = model.tasks.value.right;
      const { subStepModels } = model.steps.highEnergyTasks;

      const hazardObservationsResult = pipe(
        subStepModels,
        O.map(A.map(HighEnergyTasksSubSection.toSaveEboInput(tasks)(hazards))),
        O.map(A.sequence(E.Applicative)),
        O.map(E.map(obvs => ({ highEnergyTasks: obvs })))
      );

      const highEnergyTasksResult = HighEnergyTasks.toSaveEboInput(tasks)(
        model.steps.highEnergyTasks
      );

      const getHazardsForTask =
        (taskId: LibraryTaskId) =>
        (instanceId: number): EboHazardObservationConceptInput[] =>
          pipe(
            hazardObservationsResult,
            O.fold(
              () => [],
              hazardObservationsResultValue =>
                pipe(
                  hazardObservationsResultValue,
                  E.fold(
                    () => [],
                    hazardObservations =>
                      pipe(
                        hazardObservations.highEnergyTasks,
                        A.findFirst(
                          het =>
                            het.id === taskId && het.instanceId === instanceId
                        ),
                        O.fold(
                          (): EboHazardObservationConceptInput[] => [],
                          (het): EboHazardObservationConceptInput[] =>
                            het.hazards || []
                        )
                      )
                  )
                )
            )
          );

      const getTaskHazardConnectorIdForTask =
        (taskId: LibraryTaskId) =>
        (instanceId: number): TaskHazardConnectorId =>
          pipe(
            subStepModels,
            O.chain(ssms =>
              pipe(
                ssms,
                A.findFirst(
                  ssm => ssm.taskId === taskId && ssm.instanceId === instanceId
                ),
                O.map(ssm => ssm.taskHazardConnectorId)
              )
            ),
            O.getOrElse(() => uuid() as TaskHazardConnectorId) // This section is not needed but utilized as a safeguard on save method.
          );

      return E.right({
        ...(isRight(highEnergyTasksResult) && {
          activities: pipe(
            highEnergyTasksResult.right.activities,
            A.map(activity => ({
              ...activity,
              tasks: pipe(
                activity.tasks,
                A.map(task => ({
                  ...task,
                  taskHazardConnectorId: getTaskHazardConnectorIdForTask(
                    task.id
                  )(task.instanceId),
                  hazards: getHazardsForTask(task.id)(task.instanceId),
                }))
              ),
            }))
          ),
        }),
        ...(O.isSome(hazardObservationsResult) &&
        isRight(hazardObservationsResult.value) &&
        hazardObservationsResult.value.right.highEnergyTasks.length > 0
          ? {
              highEnergyTasks:
                hazardObservationsResult.value.right.highEnergyTasks,
            }
          : { highEnergyTasks: [] }),
      });
    } else {
      return E.right({});
    }
  };

  const historicIncidentsResult = flow(
    constant(model.steps.historicIncidents),
    HistoricIncidents.toSaveEboInput
  );

  const additionalInformationResult = flow(
    constant(model.steps.additionalInformation),
    AdditionalInformation.toSaveEboInput
  );

  const photosResult = flow(
    constant(model.steps.photos),
    PhotosSection.toSaveEboInput
  );

  const personnelResult = flow(
    constant(model.steps.personnelSection),
    PersonnelSection.toSaveEboInput
  );

  switch (model.currentStep) {
    case "observationDetails":
      const _observationDetailsResult = observationDetailsResult();
      const _mergedHighEnergyTasksResult = mergedHighEnergyTasksResult();

      return E.right({
        ...(E.isRight(_observationDetailsResult) && {
          ..._observationDetailsResult.right,
        }),
        ...(E.isRight(_mergedHighEnergyTasksResult) && {
          ..._mergedHighEnergyTasksResult.right,
        }),
      });
    case "highEnergyTasks":
      return mergedHighEnergyTasksResult();
    case "additionalInformation":
      return additionalInformationResult();
    case "historicIncidents":
      return historicIncidentsResult();
    case "photos":
      return photosResult();
    case "personnelSection":
      return personnelResult();
    case "summary":
      return Summary.toSaveEboInput();
  }
}

function toSummaryData(model: Model) {
  const observationDetailsModel = model.steps["observationDetails"];
  const highEnergyTasksModel = model.steps["highEnergyTasks"];
  const historicIncidentsModel = model.steps["historicIncidents"];
  const additionalInformationModel = model.steps["additionalInformation"];
  const photosModel = model.steps["photos"];

  const observationDetails: Either<
    Summary.SummaryDataGenerationError,
    ObservationDetailsData
  > = pipe(
    sequenceS(E.Apply)({
      observationDate: observationDetailsModel.observationDate.val,
      observationTime: observationDetailsModel.observationTime.val,
      departmentObserved: observationDetailsModel.departmentObserved.val,
      workLocation: observationDetailsModel.workLocation.val,
      opCoObserved: observationDetailsModel.opCoType.val,
    }),
    E.map(validatedModel => ({
      observationDate: validatedModel.observationDate.toLocaleString({
        ...DateTime.DATE_FULL,
        weekday: "long",
      }),
      observationTime: validatedModel.observationDate
        .startOf("day")
        .plus(validatedModel.observationTime)
        .setLocale(navigator.language)
        .toLocaleString(DateTime.TIME_SIMPLE),
      workOrderNumber: observationDetailsModel.workOrderNumber,
      workType: observationDetailsModel.workType,
      workLocation:
        validatedModel.workLocation.type === "Location"
          ? validatedModel.workLocation.location
          : "",
      latitude:
        validatedModel.workLocation.type === "Location"
          ? pipe(
              validatedModel.workLocation.coordinates,
              O.fold(
                () => O.none,
                c => O.some(c.latitude)
              )
            )
          : O.some(validatedModel.workLocation.coordinates.latitude),
      longitude:
        validatedModel.workLocation.type === "Location"
          ? pipe(
              validatedModel.workLocation.coordinates,
              O.fold(
                () => O.none,
                c => O.some(c.longitude)
              )
            )
          : O.some(validatedModel.workLocation.coordinates.longitude),
      departmentObserved: pipe(
        observationDetailsModel.departments,
        A.findFirst(d => d.id === validatedModel.departmentObserved.toString()),
        O.map(d => d.attributes.name),
        O.getOrElse(() => "")
      ),
      opCoObserved: pipe(
        observationDetailsModel.OpCos,
        A.findFirst(o => o.id === validatedModel.opCoObserved.toString()),
        O.map(d => d.attributes.name),
        O.getOrElse(() => "")
      ),
      subOpCoObserved: pipe(
        observationDetailsModel.subOpCoType.val,
        E.map(val =>
          pipe(
            observationDetailsModel.OpCos,
            A.findFirst(o => o.id === val),
            O.map(d => d.attributes.name),
            O.getOrElse(() => "")
          )
        ),
        E.getOrElse(() => "")
      ),
    }))
  );

  const createHazardsWithSavedNamesForSummary = (
    libraryHazards: Hazard[],
    subStepModels: HighEnergyTasksSubSection.Model[]
  ): Hazard[] => {
    const savedHazardNames = new Map<string, string>();
    const savedControlNames = new Map<string, string>();

    subStepModels.forEach(subStepModel => {
      subStepModel.savedHazardNames.forEach((savedName, hazardId) => {
        savedHazardNames.set(hazardId, savedName);
      });
      subStepModel.savedControlNames.forEach((savedName, controlId) => {
        savedControlNames.set(controlId, savedName);
      });
    });

    return libraryHazards.map(hazard => ({
      ...hazard,
      name: savedHazardNames.get(hazard.id) || hazard.name,
      controls: hazard.controls.map(control => ({
        ...control,
        name: savedControlNames.get(control.id) || control.name,
      })),
    }));
  };

  const hazards: Either<Summary.SummaryDataGenerationError, HazardsData> = pipe(
    sequenceS(E.Apply)({
      selectedActivityTaskIds: pipe(
        highEnergyTasksModel.selectedActivities,
        E.fromPredicate(
          m => !M.isEmpty(m),
          () => ({ message: "Empty selected tasks" })
        )
      ),
      tasksWithHazards: pipe(
        highEnergyTasksModel.subStepModels,
        E.fromOption(() => ({ message: "No hazards selected" }))
      ),
      tasks: pipe(
        model.tasks,
        (t): Either<Summary.SummaryDataGenerationError, LibraryTask[]> => {
          if (isResolved(t) && E.isRight(t.value)) {
            return E.right(t.value.right);
          } else {
            return E.left({ message: "Tasks not ready" });
          }
        }
      ),
      hazards: pipe(
        model.hazards,
        (t): Either<Summary.SummaryDataGenerationError, Hazard[]> => {
          if (isResolved(t) && E.isRight(t.value)) {
            return E.right(t.value.right);
          } else {
            return E.left({ message: "hazards not ready" });
          }
        }
      ),
    }),
    E.map(validatedModel => ({
      selectedActivityTaskIds: validatedModel.selectedActivityTaskIds,
      tasksWithHazards: validatedModel.tasksWithHazards,
      tasks: validatedModel.tasks,
      hazards: createHazardsWithSavedNamesForSummary(
        validatedModel.hazards,
        validatedModel.tasksWithHazards
      ),
    }))
  );

  const historicIncidents: Either<
    Summary.SummaryDataGenerationError,
    HistoricIncidentsData
  > = pipe(
    sequenceS(E.Apply)({
      selectedIncidentIds: pipe(
        historicIncidentsModel.selectedIncidentIds,
        E.fromPredicate(
          s => !S.isEmpty(s),
          () => ({ message: "Empty selected indicent ids" })
        )
      ),
      tasks: pipe(
        model.tasks,
        (t): Either<Summary.SummaryDataGenerationError, LibraryTask[]> => {
          if (isResolved(t) && E.isRight(t.value)) {
            return E.right(t.value.right);
          } else {
            return E.left({ message: "Tasks not ready" });
          }
        }
      ),
      selectedTaskIncidents: pipe(
        model.selectedTasksIncidents,
        (
          t
        ): Either<
          Summary.SummaryDataGenerationError,
          TaskHistoricalIncidents[]
        > => {
          if (isResolved(t) && E.isRight(t.value)) {
            return E.right(t.value.right);
          } else {
            return E.left({
              message: "Task historical incidents data is not ready",
            });
          }
        }
      ),
    }),
    E.map(validatedModel => ({
      selectedIncidentIds: validatedModel.selectedIncidentIds,
      tasks: validatedModel.tasks,
      selectedTaskIncidents: validatedModel.selectedTaskIncidents,
    }))
  );

  const additionalInformation: Either<
    Summary.SummaryDataGenerationError,
    AdditionalInformationData
  > = pipe(
    sequenceS(E.Apply)({
      notes: pipe(
        additionalInformationModel.notes,
        E.fromPredicate(
          n => E.isRight(tt.NonEmptyString.decode(n)),
          () => ({ message: "No additional information provided" })
        )
      ),
    }),
    E.map(validatedModel => ({
      notes: validatedModel.notes,
    }))
  );

  const photos: Either<Summary.SummaryDataGenerationError, PhotosData> = pipe(
    sequenceS(E.Apply)({
      uploadedFiles: pipe(
        photosModel.uploadedFiles,
        E.fromPredicate(
          up => !M.isEmpty(up),
          () => ({ message: "No photos selected" })
        )
      ),
    }),
    E.map(validatedModel => ({
      uploadedFiles: validatedModel.uploadedFiles,
    }))
  );

  return {
    observationDetails,
    hazards,
    historicIncidents,
    additionalInformation,
    photos,
  };
}

export type Action =
  | {
      type: "NavTo";
      step: StepName;
    }
  | {
      type: "NavToWithFromStep";
      step: StepName;
      from: StepName;
    }
  | {
      type: "NavToHighEnergyTasksSubSection";
      taskId: LibraryTaskId;
      instanceId: number;
    }
  | {
      type: "MoveToNextFormSection";
    }
  | {
      type: "ObservationDetailsAction";
      action: ObservationDetails.Action;
    }
  | {
      type: "HighEnergyTasksAction";
      action: HighEnergyTasks.Action;
    }
  | {
      type: "AdditionalInformationAction";
      action: AdditionalInformation.Action;
    }
  | {
      type: "HistoricIncidentsAction";
      action: HistoricIncidents.Action;
    }
  | {
      type: "PhotosAction";
      action: PhotosSection.Action;
    }
  | {
      type: "SummaryAction";
      action: Summary.Action;
    }
  | {
      type: "PersonnelSectionAction";
      action: PersonnelSection.Action;
    }
  | {
      type: "UpdateHighEnergyTasksModel";
      model: HighEnergyTasks.Model;
    }
  | {
      type: "GetTenantWorkTypes";
      operation: AsyncOperationStatus<ApiResult<WorkType[]>>;
    }
  | {
      type: "GetWorkTypeLinkedTasks";
      workTypeIds: string[];
      operation: AsyncOperationStatus<ApiResult<LibraryTask[]>>;
    }
  | {
      type: "SaveEbo";
      shouldComplete: boolean;
      eboId: Option<EboId>;
      input: EnergyBasedObservationInput;
      operation: AsyncOperationStatus<ApiResult<SavedEboInfo>>;
    }
  | {
      type: "GetTasksHistoricalIncidents";
      taskIds: LibraryTaskId[];
      operation: AsyncOperationStatus<ApiResult<TaskHistoricalIncidents[]>>;
    }
  | {
      type: "GetCrewMembers";
      operation: AsyncOperationStatus<ApiResult<CrewMember[]>>;
    }
  | {
      type: "FormViewStateChange";
      selectedTab: FormViewTabStates;
    }
  | {
      type: "NoAction";
    }
  | {
      type: "DeleteEbo";
      operation: AsyncOperationStatus<ApiResult<boolean>>;
    }
  | {
      type: "ShowDeleteEboModal";
      eboId: O.Option<EboId>;
    }
  | {
      type: "ShowCompleteEboModal";
      value: boolean;
    }
  | {
      type: "ShowWorkTypeBasedActivityRemovalModal";
      value: boolean;
    }
  | {
      type: "ReopenEbo";
      eboId: EboId;
      operation: AsyncOperationStatus<ApiResult<SavedEboInfo>>;
    }
  | {
      type: "GetHazards";
      query: QueryTenantLinkedHazardsLibraryArgs;
      operation: AsyncOperationStatus<ApiResult<Hazard[]>>;
    };

export const NavTo = (step: StepName): Action => ({
  type: "NavTo",
  step,
});

export const NavToWithFromStep =
  (step: StepName) =>
  (from: StepName): Action => ({
    type: "NavToWithFromStep",
    step,
    from,
  });

export const NavToHighEnergyTasksSubSection =
  (taskId: LibraryTaskId) =>
  (instanceId: number): Action => ({
    type: "NavToHighEnergyTasksSubSection",
    taskId,
    instanceId,
  });

export const MoveToNextFormSection = (): Action => ({
  type: "MoveToNextFormSection",
});

export const ObservationDetailsAction = (
  action: ObservationDetails.Action
): Action => ({
  type: "ObservationDetailsAction",
  action,
});

export const HighEnergyTasksAction = (
  action: HighEnergyTasks.Action
): Action => ({
  type: "HighEnergyTasksAction",
  action,
});

export const HighEnergyTasksSubSectionAction = (
  action: HighEnergyTasksSubSection.Action
): HighEnergyTasks.Action => ({
  type: "HighEnergyTasksSubSectionAction",
  action,
});

export const AdditionalInformationAction = (
  action: AdditionalInformation.Action
): Action => ({
  type: "AdditionalInformationAction",
  action,
});

export const HistoricIncidentsAction = (
  action: HistoricIncidents.Action
): Action => ({
  type: "HistoricIncidentsAction",
  action,
});
export const PhotosAction = (action: PhotosSection.Action): Action => ({
  type: "PhotosAction",
  action,
});

export const SummaryAction = (action: Summary.Action): Action => ({
  type: "SummaryAction",
  action,
});

export const PersonnelSectionAction = (
  action: PersonnelSection.Action
): Action => ({
  type: "PersonnelSectionAction",
  action,
});

export const UpdateHighEnergyTasksModel = (
  model: HighEnergyTasks.Model
): Action => ({
  type: "UpdateHighEnergyTasksModel",
  model,
});

export const GetTenantWorkTypes = (
  operation: AsyncOperationStatus<ApiResult<WorkType[]>>
): Action => ({
  type: "GetTenantWorkTypes",
  operation,
});

export const GetWorkTypeLinkedTasks =
  (workTypeIds: string[]) =>
  (operation: AsyncOperationStatus<ApiResult<LibraryTask[]>>): Action => ({
    type: "GetWorkTypeLinkedTasks",
    workTypeIds,
    operation,
  });

export const GetHazards =
  (query: QueryTenantLinkedHazardsLibraryArgs) =>
  (operation: AsyncOperationStatus<ApiResult<Hazard[]>>): Action => ({
    type: "GetHazards",
    query,
    operation,
  });

export const GetTasksHistoricalIncidents =
  (taskIds: LibraryTaskId[]) =>
  (
    operation: AsyncOperationStatus<ApiResult<TaskHistoricalIncidents[]>>
  ): Action => ({
    type: "GetTasksHistoricalIncidents",
    taskIds,
    operation,
  });

export const GetCrewMembers = (
  operation: AsyncOperationStatus<ApiResult<CrewMember[]>>
): Action => ({
  type: "GetCrewMembers",
  operation,
});

export const SaveEbo =
  (eboId: Option<EboId>, input: EnergyBasedObservationInput) =>
  (shouldComplete: boolean) =>
  (operation: AsyncOperationStatus<ApiResult<SavedEboInfo>>): Action => ({
    type: "SaveEbo",
    shouldComplete,
    eboId,
    input,
    operation,
  });

export const DeleteEbo = (
  operation: AsyncOperationStatus<ApiResult<boolean>>
): Action => ({
  type: "DeleteEbo",
  operation,
});

export const ReopenEbo =
  (eboId: EboId) =>
  (operation: AsyncOperationStatus<ApiResult<SavedEboInfo>>): Action => ({
    type: "ReopenEbo",
    eboId,
    operation,
  });

export const getSubStepModel = (
  subStepModels: Option<HighEnergyTasksSubSection.Model[]>,
  subStepTaskId: LibraryTaskId,
  instanceId: number
): Option<HighEnergyTasksSubSection.Model> =>
  pipe(
    subStepModels,
    O.chain(ssms =>
      pipe(
        ssms,
        A.filter(
          ssm => ssm.taskId === subStepTaskId && ssm.instanceId === instanceId
        ),
        A.head
      )
    )
  );

const areAllHighEnergySubStepsCompleted = (model: Model): boolean =>
  pipe(
    model.steps.highEnergyTasks.subStepModels,
    O.fold(
      () => false,
      subStepModels =>
        pipe(
          model.completedSteps,
          S.toArray(OrdString),
          A.filter(a => /^highEnergyTasks:/.test(a)),
          a => a.length === subStepModels.length
        )
    )
  );

export const ShowDeleteEboModal = (eboId: O.Option<EboId>): Action => ({
  type: "ShowDeleteEboModal",
  eboId,
});

export const ShowCompleteEboModal = (value: boolean): Action => ({
  type: "ShowCompleteEboModal",
  value,
});

export const ShowWorkTypeBasedActivityRemovalModal = (
  value: boolean
): Action => ({
  type: "ShowWorkTypeBasedActivityRemovalModal",
  value,
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

const appendStepToCompletedSteps =
  (bool: boolean) => (step: string) => (completedSteps: Array<string>) =>
    pipe(
      bool,
      matchBoolean(
        () => completedSteps,
        () => pipe(completedSteps, A.append(step))
      )
    );

const appendSubStepsToCompletedSteps =
  (highEnergyTasks: Option<HighEnergyTasksObservations[]>) =>
  (completedSteps: Array<string>) => {
    return pipe(
      highEnergyTasks,
      O.fold(
        () => completedSteps,
        hets =>
          pipe(
            hets,
            A.map(het => `highEnergyTasks:${het.id}:${het.instanceId}`),
            A.concat(completedSteps)
          )
      )
    );
  };

const getCompletedSteps = (ebo: O.Option<Ebo>): Set<string> => {
  return pipe(
    ebo,
    O.map(e => e.contents),
    O.fold(
      () => S.empty, // If ebo is None, return an empty Set
      contents =>
        pipe(
          new Array<string>(),
          appendStepToCompletedSteps(O.isSome(contents.details))(
            "observationDetails"
          ),
          appendStepToCompletedSteps(O.isSome(contents.activities))(
            "highEnergyTasks"
          ),
          appendStepToCompletedSteps(O.isSome(contents.additionalInformation))(
            "additionalInformation"
          ),
          appendStepToCompletedSteps(O.isSome(contents.historicIncidents))(
            "historicIncidents"
          ),
          appendStepToCompletedSteps(O.isSome(contents.photos))("photos"),
          appendStepToCompletedSteps(
            O.isSome(contents.summary) && contents.summary.value.viewed
          )("summary"),
          appendStepToCompletedSteps(O.isSome(contents.personnel))(
            "personnelSection"
          ),
          appendSubStepsToCompletedSteps(contents.highEnergyTasks),
          S.fromArray(eqCompletedStep)
        )
    )
  );
};

const generateEboSnapshots = (ebo: Option<Ebo>): EboSnapshots => {
  return {
    observationDetails: pipe(
      ebo,
      ObservationDetails.init,
      ObservationDetails.makeSnapshot,
      snapshotHash
    ),
    highEnergyTasks: pipe(
      ebo,
      HighEnergyTasks.init,
      HighEnergyTasks.makeSnapshot,
      snapshotHash
    ),
    additionalInformation: pipe(
      ebo,
      AdditionalInformation.init,
      AdditionalInformation.makeSnapshot,
      snapshotHash
    ),
    historicIncidents: pipe(
      ebo,
      HistoricIncidents.init,
      HistoricIncidents.makeSnapshot,
      snapshotHash
    ),
    photos: pipe(
      ebo,
      PhotosSection.init,
      PhotosSection.makeSnapshot,
      snapshotHash
    ),
    summary: "",
    personnelSection: pipe(
      ebo,
      PersonnelSection.init,
      PersonnelSection.makeSnapshot,
      snapshotHash
    ),
  };
};

const compareEboSnapshots = (model: Model): boolean => {
  if (model.isRedirectAfterFormSave) return false;

  const eboSectionComparisons: Record<Exclude<StepName, "summary">, boolean> = {
    observationDetails:
      model.snapshots.observationDetails ===
      pipe(
        model.steps.observationDetails,
        ObservationDetails.makeSnapshot,
        snapshotHash
      ),
    highEnergyTasks:
      model.snapshots.highEnergyTasks ===
      pipe(
        model.steps.highEnergyTasks,
        HighEnergyTasks.makeSnapshot,
        snapshotHash
      ),
    additionalInformation:
      model.snapshots.additionalInformation ===
      pipe(
        model.steps.additionalInformation,
        AdditionalInformation.makeSnapshot,
        snapshotHash
      ),
    historicIncidents:
      model.snapshots.historicIncidents ===
      pipe(
        model.steps.historicIncidents,
        HistoricIncidents.makeSnapshot,
        snapshotHash
      ),
    photos:
      model.snapshots.photos ===
      pipe(model.steps.photos, PhotosSection.makeSnapshot, snapshotHash),
    personnelSection:
      model.snapshots.personnelSection ===
      pipe(
        model.steps.personnelSection,
        PersonnelSection.makeSnapshot,
        snapshotHash
      ),
  };

  return pipe(
    eboSectionComparisons,
    R.some(s => s === false)
  );
};

export const init = (data: Option<Ebo>): [Model, Effect<Action>] => {
  const eboId = pipe(
    data,
    O.map(d => d.id)
  );

  const selectedTaskIds = pipe(
    pipe(
      data,
      O.map(e => e.contents)
    ),
    O.chain(a => a.activities),
    O.fold(
      () => new Set<LibraryTaskId>(),
      activities =>
        pipe(
          activities,
          A.map(a =>
            pipe(
              a.tasks,
              A.map(v => v.id)
            )
          ),
          A.flatten,
          r => new Set<LibraryTaskId>(r)
        )
    ),
    S.toArray(ordLibraryTaskId)
  );
  const tenantName = getTenantName();
  const stepList = getStepListForTenant(tenantName);

  return [
    {
      steps: {
        observationDetails: ObservationDetails.init(data),
        highEnergyTasks: HighEnergyTasks.init(data),
        additionalInformation: AdditionalInformation.init(data),
        historicIncidents: HistoricIncidents.init(data),
        photos: PhotosSection.init(data),
        summary: Summary.init(Summary.initiateSummaryModel(data)),
        personnelSection: PersonnelSection.init(data),
      },
      snapshots: pipe(data, generateEboSnapshots),
      currentStep: stepList[0],
      fromStep: O.none,
      tasks: NotStarted(),
      hazards: NotStarted(),
      workTypes: NotStarted(),
      crewMembers: NotStarted(),
      completedSteps: getCompletedSteps(data),
      selectedTasksIncidents: NotStarted(),
      eboId: pipe(eboId, E.right, Resolved),
      showDeleteEboModal: O.none,
      showCompleteEboModal: false,
      showWorkTypeBasedActivityRemovalModal: false,
      isRedirectAfterFormSave: false,
      creatorUserId: pipe(
        data,
        O.map(j => j.createdBy.id),
        right,
        Resolved
      ),
      completedByUserId: pipe(
        data,
        O.chain(j => j.completedBy),
        O.map(u => u.id),
        right,
        Resolved
      ),
      status: pipe(
        data,
        O.map(e => e.status),
        right,
        Resolved
      ),
      selectedTab: FormViewTabStates.FORM,
    },
    effectsBatch([
      flow(Started, GetCrewMembers, effectOfAction)(),
      flow(
        Started,
        GetHazards({ type: LibraryFilterType.Task }),
        effectOfAction
      )(),
      A.isNonEmpty(selectedTaskIds)
        ? flow(
            Started,
            GetTasksHistoricalIncidents(selectedTaskIds),
            effectOfAction
          )()
        : noEffect,
    ]),
  ];
};

const nextStep = (
  currentStep: StepName,
  stepList: StepName[]
): Option<StepName> =>
  pipe(
    stepList,
    A.dropLeftWhile(s => s !== currentStep),
    A.tail,
    O.chain(A.head)
  );

const isHighEnergyTasksStep = (step: StepName): step is "highEnergyTasks" => {
  return step === "highEnergyTasks";
};

const navigateToNextSubStep = (model: Model): Option<[Model, WizardEffect]> => {
  switch (model.currentStep) {
    case "highEnergyTasks": {
      return pipe(
        model.currentStep,
        O.fromPredicate(isHighEnergyTasksStep),
        O.map(currentStep => model.steps[currentStep]),
        O.chain(HighEnergyTasks.withNextSubStep(model.tasks)),
        O.map((highEnergyTasksModel): [Model, WizardEffect] => [
          {
            ...model,
            steps: {
              ...model.steps,
              highEnergyTasks: highEnergyTasksModel,
            },
          },
          ComponentEffect(scrollTopEffect),
        ])
      );
    }
    case "observationDetails":
    case "personnelSection":
    case "historicIncidents":
    case "photos":
    case "additionalInformation":
    case "summary": {
      return O.none;
    }
  }
};

const generateSubStepNavigations =
  (model: Model) =>
  (dispatch: (action: Action) => void) =>
  (shouldReturnComponent = true) =>
  (stepName: StepName): Option<React.ReactNode | NavigationOption[]> => {
    switch (stepName) {
      case "highEnergyTasks": {
        if (
          isResolved(model.tasks) &&
          isRight(model.tasks.value) &&
          isResolved(model.hazards) &&
          isRight(model.hazards.value)
        ) {
          return pipe(
            taskId => flow(NavToHighEnergyTasksSubSection(taskId), dispatch),
            HighEnergyTasks.getSubStepNavigations(
              model.steps[stepName],
              model.completedSteps
            )(model.currentStep)(model.hazards.value.right)(
              model.tasks.value.right
            )(shouldReturnComponent),
            O.of
          );
        } else {
          return O.none;
        }
      }
      case "observationDetails":
      case "personnelSection":
      case "historicIncidents":
      case "photos":
      case "additionalInformation":
      case "summary": {
        return O.none;
      }
    }
  };

// on leaving observationDetails or highEnergyTasks it should flag errorsEnabled property on respective model
const determineStepsByErrorsEnabled = (
  steps: Steps,
  currentStep: StepName,
  actionStep: StepName
) => {
  return {
    ...steps,
    ...(currentStep === "observationDetails" &&
      actionStep !== "observationDetails" && {
        observationDetails: {
          ...steps.observationDetails,
          errorsEnabled: true,
        },
      }),
    ...(currentStep === "highEnergyTasks" &&
      actionStep !== "highEnergyTasks" && {
        highEnergyTasks: {
          ...steps.highEnergyTasks,
          errorsEnabled: true,
        },
      }),
  };
};

export const update =
  (api: Api) =>
  (model: Model, action: Action): [Model, WizardEffect] => {
    const tenantName = getTenantName();
    const stepList = getStepListForTenant(tenantName);

    switch (action.type) {
      case "NavTo":
        switch (action.step) {
          case "highEnergyTasks": {
            return [
              {
                ...model,
                currentStep: action.step,
                fromStep: O.none,
                steps: {
                  ...determineStepsByErrorsEnabled(
                    model.steps,
                    model.currentStep,
                    action.step
                  ),
                  highEnergyTasks: {
                    ...model.steps.highEnergyTasks,
                    subStep: O.none,
                  },
                },
              },
              NoEffect,
            ];
          }
          case "observationDetails":
          case "personnelSection":
          case "photos":
          case "additionalInformation":
          case "historicIncidents":
          case "summary": {
            return [
              {
                ...model,
                currentStep: action.step,
                fromStep: O.none,
                steps: determineStepsByErrorsEnabled(
                  model.steps,
                  model.currentStep,
                  action.step
                ),
              },
              NoEffect,
            ];
          }
        }
      case "NavToWithFromStep": {
        switch (action.step) {
          case "highEnergyTasks": {
            return [
              {
                ...model,
                currentStep: action.step,
                fromStep: O.some(action.from),
                steps: {
                  ...determineStepsByErrorsEnabled(
                    model.steps,
                    model.currentStep,
                    action.step
                  ),
                  highEnergyTasks: {
                    ...model.steps.highEnergyTasks,
                    subStep: O.none,
                  },
                },
              },
              NoEffect,
            ];
          }
          case "observationDetails":
          case "personnelSection":
          case "photos":
          case "additionalInformation":
          case "historicIncidents":
          case "summary": {
            return [
              {
                ...model,
                currentStep: action.step,
                fromStep: O.some(action.from),
                steps: determineStepsByErrorsEnabled(
                  model.steps,
                  model.currentStep,
                  action.step
                ),
              },
              NoEffect,
            ];
          }
        }
      }
      case "NavToHighEnergyTasksSubSection":
        return [
          {
            ...model,
            currentStep: "highEnergyTasks",
            fromStep: O.none,
            steps: {
              ...model.steps,
              highEnergyTasks: {
                ...model.steps.highEnergyTasks,
                subStep: O.of({
                  taskId: action.taskId,
                  instanceId: action.instanceId,
                }),
              },
            },
          },
          NoEffect,
        ];
      case "MoveToNextFormSection":
        return pipe(
          model.fromStep,
          O.fold(
            () => {
              return pipe(
                model,
                navigateToNextSubStep,
                O.alt(() =>
                  pipe(
                    model.currentStep,
                    step => nextStep(step, stepList),
                    O.map((nextStepValue): [Model, WizardEffect] => {
                      return [
                        {
                          ...model,
                          currentStep: nextStepValue,
                        },
                        ComponentEffect(scrollTopEffect),
                      ];
                    })
                  )
                ),
                O.getOrElse((): [Model, WizardEffect] => {
                  return [{ ...model }, NoEffect];
                })
              );
            },
            fromStep => {
              return pipe(
                model,
                m =>
                  isHighEnergyTasksStep(m.currentStep) &&
                  !areAllHighEnergySubStepsCompleted(m),
                matchBoolean(
                  () => [
                    { ...model, currentStep: fromStep, fromStep: O.none },
                    ComponentEffect(scrollTopEffect),
                  ],
                  () => [
                    {
                      ...model,
                      currentStep: model.currentStep,
                      fromStep: O.none,
                      steps: {
                        ...model.steps,
                        highEnergyTasks: {
                          ...model.steps.highEnergyTasks,
                          ...(isResolved(model.tasks) &&
                            E.isRight(model.tasks.value) && {
                              subStep: getNextSubStep(model.tasks.value.right)({
                                ...model.steps.highEnergyTasks,
                                subStep: O.none,
                              }),
                            }),
                        },
                      },
                    },
                    ComponentEffect(scrollTopEffect),
                  ]
                )
              );
            }
          )
        );
      case "ObservationDetailsAction": {
        const [observationDetailsModel, observationDetailsEffect] =
          ObservationDetails.update(
            model.steps.observationDetails,
            action.action
          );

        switch (observationDetailsEffect.type) {
          case "AlertAction": {
            return [
              {
                ...model,
                steps: {
                  ...model.steps,
                  observationDetails: observationDetailsModel,
                },
              },
              AlertAction(observationDetailsEffect.action),
            ];
          }
          case "NoEffect": {
            return [
              {
                ...model,
                steps: {
                  ...model.steps,
                  observationDetails: observationDetailsModel,
                },
              },
              NoEffect,
            ];
          }
        }
      }
      case "HighEnergyTasksAction": {
        const [highEnergyTasksModel, highEnergyTasksEffect] =
          HighEnergyTasks.update(model.steps.highEnergyTasks, action.action);

        return [
          {
            ...model,
            steps: {
              ...model.steps,
              highEnergyTasks: highEnergyTasksModel,
            },
          },
          pipe(
            highEnergyTasksEffect,
            mapEffect(HighEnergyTasksAction),
            ComponentEffect
          ),
        ];
      }
      case "AdditionalInformationAction":
        return [
          {
            ...model,
            steps: {
              ...model.steps,
              additionalInformation: AdditionalInformation.update(
                model.steps.additionalInformation,
                action.action
              ),
            },
          },
          NoEffect,
        ];
      case "PersonnelSectionAction":
        return [
          {
            ...model,
            steps: {
              ...model.steps,
              personnelSection: PersonnelSection.update(
                model.steps.personnelSection,
                action.action
              ),
            },
          },
          NoEffect,
        ];
      case "HistoricIncidentsAction":
        return [
          {
            ...model,
            steps: {
              ...model.steps,
              historicIncidents: HistoricIncidents.update(
                model.steps.historicIncidents,
                action.action
              ),
            },
          },
          NoEffect,
        ];
      case "SummaryAction":
        return [
          {
            ...model,
            steps: {
              ...model.steps,
              summary: Summary.update(model.steps.summary, action.action),
            },
          },
          NoEffect,
        ];
      case "PhotosAction":
        const [photosModel, photosEffect] = PhotosSection.update(api)(
          model.steps.photos,
          action.action
        );

        const summaryModel = pipe(
          photosModel.uploadedFiles,
          M.toArray(PhotosSection.ordFileName),
          A.head,
          O.map(Tup.snd),
          O.filter(
            file =>
              O.isNone(model.steps["summary"].selectedPhoto) ||
              model.steps["summary"].selectedPhoto.value.name !== file.name ||
              !isResolved(
                model.steps["summary"].selectedPhoto.value.uploadPolicy
              )
          ),
          O.map(flow(O.some, Summary.init))
        );

        switch (photosEffect.type) {
          case "ComponentEffect": {
            return [
              {
                ...model,
                steps: {
                  ...model.steps,
                  photos: photosModel,
                  summary: pipe(
                    summaryModel,
                    O.getOrElse(() => model.steps["summary"])
                  ),
                },
              },
              ComponentEffect(mapEffect(PhotosAction)(photosEffect.effect)),
            ];
          }
          case "AlertAction": {
            return [
              { ...model, steps: { ...model.steps, photos: photosModel } },
              AlertAction(photosEffect.action),
            ];
          }
          case "NoEffect": {
            return [
              { ...model, steps: { ...model.steps, photos: photosModel } },
              NoEffect,
            ];
          }
        }
      case "UpdateHighEnergyTasksModel": {
        const updatedModel = {
          ...model,
          steps: { ...model.steps, highEnergyTasks: action.model },
          showWorkTypeBasedActivityRemovalModal: false,
        };

        return [
          updatedModel,
          pipe(
            E.Do,
            E.bindW("eboId", () =>
              pipe(
                model.eboId,
                E.fromPredicate(isResolved, constNull),
                E.chainW(i => i.value)
              )
            ),
            E.bindW("input", () => toEboInput(updatedModel)),
            E.map(({ eboId, input }) =>
              pipe(
                effectOfAction(flow(Started, SaveEbo(eboId, input)(false))()),
                ComponentEffect
              )
            ),
            E.getOrElseW(() => NoEffect)
          ),
        ];
      }
      case "GetTenantWorkTypes":
        switch (action.operation.status) {
          case "Started":
            return [
              { ...model, workTypes: updatingDeferred(model.workTypes) },
              NoEffect,
            ];
          case "Finished":
            return [
              {
                ...model,
                workTypes: Resolved(action.operation.result),
              },
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
      case "GetWorkTypeLinkedTasks":
        switch (action.operation.status) {
          case "Started":
            return [
              { ...model, tasks: updatingDeferred(model.tasks) },
              NoEffect,
            ];
          case "Finished":
            return [
              {
                ...model,
                tasks: Resolved(action.operation.result),
              },
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
      case "GetHazards":
        switch (action.operation.status) {
          case "Started":
            return [
              { ...model, tasks: updatingDeferred(model.tasks) },
              pipe(
                effectOfAsync(
                  api.ebo.getTenantLinkedHazardsLibrary(action.query),
                  flow(Finished, GetHazards(action.query))
                ),
                ComponentEffect
              ),
            ];
          case "Finished":
            const hazardsResult = pipe(
              action.operation.result,
              E.map(
                A.filter(a =>
                  EQ.eqStrict.equals(
                    O.isSome(a.energyLevel) && a.energyLevel.value,
                    EnergyLevel.HighEnergy
                  )
                )
              )
            );
            return [
              { ...model, hazards: Resolved(hazardsResult) },
              pipe(
                hazardsResult,
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
      case "GetTasksHistoricalIncidents":
        switch (action.operation.status) {
          case "Started":
            const fetchingTasksEffect = pipe(
              action.taskIds.map(taskId =>
                pipe(
                  taskId,
                  api.ebo.getHistoricalIncidents,
                  TE.map(result => ({ taskId, result }))
                )
              ),
              TE.sequenceArray,
              TE.map(arr => [...arr])
            );

            return [
              {
                ...model,
                selectedTasksIncidents: updatingDeferred(
                  model.selectedTasksIncidents
                ),
              },
              pipe(
                effectOfAsync(
                  fetchingTasksEffect,
                  flow(Finished, GetTasksHistoricalIncidents(action.taskIds))
                ),
                ComponentEffect
              ),
            ];
          case "Finished": {
            return [
              {
                ...model,
                selectedTasksIncidents: Resolved(
                  pipe(
                    action.operation.result,
                    E.map(a => {
                      if (
                        isUpdating(model.selectedTasksIncidents) &&
                        E.isRight(model.selectedTasksIncidents.value)
                      ) {
                        return [
                          ...a,
                          ...model.selectedTasksIncidents.value.right,
                        ];
                      }
                      return a;
                    })
                  )
                ),
              },
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
        }

      case "GetCrewMembers":
        switch (action.operation.status) {
          case "Started": {
            return [
              { ...model, crewMembers: updatingDeferred(model.crewMembers) },
              pipe(
                effectOfAsync(
                  api.ebo.getCrewMembers,
                  flow(Finished, GetCrewMembers)
                ),
                ComponentEffect
              ),
            ];
          }
          case "Finished":
            return [
              { ...model, crewMembers: Resolved(action.operation.result) },
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
      case "SaveEbo": {
        const next = nextStep(model.currentStep, stepList);

        switch (action.operation.status) {
          case "Started": {
            const sourceInfo = {
              sourceInformation: SourceAppInformation.WebPortal,
              appVersion: appVersion,
            };

            const input = { ...action.input, sourceInfo };

            const saveEboTask = pipe(
              next,
              O.map(() => api.ebo.saveEbo(action.eboId)(input)),
              O.getOrElse(() =>
                pipe(
                  action.eboId,
                  O.fold(
                    () => api.ebo.saveEbo(action.eboId)(input),
                    eboId =>
                      pipe(
                        action.shouldComplete,
                        matchBoolean(
                          () => api.ebo.saveEbo(action.eboId)(input),
                          () => api.ebo.completeEbo(eboId)(input)
                        )
                      )
                  )
                )
              )
            );

            return [
              {
                ...model,
                showCompleteEboModal: false,
                eboId: updatingDeferred(model.eboId),
              },
              pipe(
                effectOfAsync(
                  saveEboTask,
                  flow(
                    Finished,
                    SaveEbo(action.eboId, input)(action.shouldComplete)
                  )
                ),
                ComponentEffect
              ),
            ];
          }
          case "Finished": {
            const result = action.operation.result;

            const getCompletedStepKey = (): string => {
              return EQ.eqStrict.equals(model.currentStep, "highEnergyTasks") &&
                O.isSome(model.steps.highEnergyTasks.subStep)
                ? `${model.currentStep}:${model.steps.highEnergyTasks.subStep.value.taskId}:${model.steps.highEnergyTasks.subStep.value.instanceId}`
                : model.currentStep;
            };

            return [
              {
                ...model,
                eboId: pipe(
                  result,
                  E.map(r => O.some(r.id)),
                  E.alt(() => E.right(action.eboId)),
                  Resolved
                ),
                completedSteps: pipe(
                  result,
                  E.fold(
                    () => model.completedSteps,
                    () =>
                      pipe(
                        model.completedSteps,
                        S.insert(eqCompletedStep)(getCompletedStepKey())
                      )
                  )
                ),
                steps: {
                  ...model.steps,
                  ...(E.isRight(result) && {
                    highEnergyTasks: {
                      ...HighEnergyTasks.init(O.of(result.right)),
                      subStep: model.steps.highEnergyTasks.subStep,
                    },
                  }),
                  historicIncidents: pipe(
                    model.steps.historicIncidents,
                    HistoricIncidents.filterSelectedHistoricalIncidentsBasedOnSelectedActivities(
                      model.steps.highEnergyTasks.selectedActivities
                    )(model.selectedTasksIncidents)
                  ),
                  ...(E.isRight(result) &&
                    model.steps.personnelSection.observer.name !==
                      result.right.createdBy.name && {
                      personnelSection: PersonnelSection.init(
                        O.of(result.right)
                      ),
                    }),
                },
                ...(E.isRight(result) && {
                  snapshots: pipe(result.right, O.of, generateEboSnapshots),
                }),
                isRedirectAfterFormSave: O.isNone(next),
              },
              pipe(
                result,
                E.fold(
                  error => {
                    return flow(
                      showUserApiError,
                      Alert.AlertRequested("error"),
                      AlertAction
                    )(error);
                  },
                  () => {
                    if (O.isSome(next)) {
                      return pipe(
                        effectOfAction(MoveToNextFormSection()),
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
      }
      case "DeleteEbo": {
        switch (action.operation.status) {
          case "Started": {
            const deleteEbo = pipe(
              model.showDeleteEboModal,
              O.fold(
                () => TE.of(false),
                id =>
                  pipe(
                    id,
                    api.ebo.deleteEbo,
                    TE.map(a => a)
                  )
              )
            );

            return [
              model,
              pipe(
                effectOfAsync(deleteEbo, flow(Finished, DeleteEbo)),
                ComponentEffect
              ),
            ];
          }
          case "Finished": {
            const result = action.operation.result;
            return [
              { ...model, showDeleteEboModal: O.none },
              pipe(
                result,
                E.fold(
                  flow(
                    showApiError,
                    Alert.AlertRequested("error"),
                    AlertAction
                  ),
                  () =>
                    ComponentEffect(effectOfAsync_(() => router.push("/forms")))
                )
              ),
            ];
          }
        }
      }
      case "ReopenEbo":
        switch (action.operation.status) {
          case "Started":
            return [
              model,
              pipe(
                effectOfAsync(
                  api.ebo.reopenEbo(action.eboId),
                  flow(Finished, ReopenEbo(action.eboId))
                ),
                ComponentEffect
              ),
            ];

          case "Finished":
            const result = action.operation.result;

            return pipe(
              result,
              E.fold(
                (e: ApiError): [Model, WizardEffect] => [
                  { ...model },
                  pipe(
                    showApiError(e),
                    Alert.AlertRequested("error"),
                    AlertAction
                  ),
                ],
                (eboData): [Model, WizardEffect] => [
                  {
                    ...model,
                    completedByUserId: pipe(
                      eboData.completedBy,
                      O.map(u => u.id),
                      E.right,
                      Resolved
                    ),
                    status: pipe(eboData.status, O.some, E.right, Resolved),
                  },
                  pipe(
                    "Report reopened",
                    Alert.AlertRequested("success"),
                    AlertAction
                  ),
                ]
              )
            );
        }
      case "ShowDeleteEboModal": {
        return [{ ...model, showDeleteEboModal: action.eboId }, NoEffect];
      }
      case "ShowCompleteEboModal": {
        return [{ ...model, showCompleteEboModal: action.value }, NoEffect];
      }
      case "ShowWorkTypeBasedActivityRemovalModal": {
        return [
          { ...model, showWorkTypeBasedActivityRemovalModal: action.value },
          NoEffect,
        ];
      }
      case "FormViewStateChange":
        return [
          {
            ...model,
            selectedTab: action.selectedTab,
          },
          NoEffect,
        ];
      case "NoAction":
        return [{ ...model }, NoEffect];
    }
  };

export type Props = ChildProps<Model, Action> & {
  checkPermission: (permission: UserPermission) => boolean;
  userId: NonEmptyString;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch } = props;
  const [eboFormAuditData, setEboFormAuditData] = useState<[]>([]);
  const toastCtx = useContext(ToastContext);

  const [getTenantWorkTypes] = useLazyQuery(TenantWorkTypes, {
    onCompleted: data => {
      if (data?.tenantWorkTypes) {
        dispatch(
          GetTenantWorkTypes({
            status: "Finished",
            result: E.right(data.tenantWorkTypes),
          })
        );
      }
    },
    onError: error => {
      dispatch(
        GetTenantWorkTypes({
          status: "Finished",
          result: E.left({ type: "RequestError", error: error.message }),
        })
      );
    },
  });

  const [getWorkTypeLinkedTasks] = useLazyQuery(WorkTypeLinkedLibraryTasks, {
    onCompleted: (data: any) => {
      if (data?.tenantAndWorkTypeLinkedLibraryTasks) {
        const selectedWorkTypeIds = pipe(
          model.steps.observationDetails.workType,
          A.map(wt => wt.id)
        );

        dispatch(
          GetWorkTypeLinkedTasks(selectedWorkTypeIds)({
            status: "Finished",
            result: E.right(data.tenantAndWorkTypeLinkedLibraryTasks),
          })
        );
      }
    },
    onError: (error: any) => {
      const selectedWorkTypeIds = pipe(
        model.steps.observationDetails.workType,
        A.map(wt => wt.id)
      );

      dispatch(
        GetWorkTypeLinkedTasks(selectedWorkTypeIds)({
          status: "Finished",
          result: E.left({ type: "RequestError", error: error.message }),
        })
      );
    },
  });

  useEffect(() => {
    getTenantWorkTypes();
  }, [getTenantWorkTypes]);

  useEffect(() => {
    if (model.currentStep === "highEnergyTasks") {
      const selectedWorkTypeIds = pipe(
        model.steps.observationDetails.workType,
        A.map(wt => wt.id)
      );
      if (selectedWorkTypeIds.length > 0) {
        getWorkTypeLinkedTasks({
          variables: {
            tasksLibraryId: null,
            workTypeIds: selectedWorkTypeIds,
            orderBy: [],
            hazardsOrderBy: [],
            controlsOrderBy: [],
          },
        });
      }
    }
  }, [
    model.currentStep,
    model.steps.observationDetails.workType,
    getWorkTypeLinkedTasks,
  ]);

  const handleNavTo = useCallback(
    (step: StepName) => {
      dispatch(NavTo(step));
    },
    [dispatch]
  );

  // check if current user is the creator of the EBO
  const isOwnForm = useMemo(
    () =>
      pipe(
        model.creatorUserId,
        deferredToOption,
        E.fromOption(() => "Creator user id is not available"),
        E.chainW(identity),
        E.map(
          O.fold(
            // if the form hasn't been saved yet, the creator user id is None
            // which means the current user is the owner of the form
            () => true,
            creatorId => eqNonEmptyString.equals(creatorId, props.userId)
          )
        ),
        // if the creator id is not available, we assume the user is not the owner of the form
        E.getOrElseW(() => false)
      ),
    [model.creatorUserId, props.userId]
  );

  const isFormCompleted = useMemo(() => {
    const hasCompletedByUserId = pipe(
      model.completedByUserId,
      deferredToOption,
      O.chain(O.fromEither),
      O.flatten,
      O.isSome
    );

    const isStatusCompleted = pipe(
      model.status,
      deferredToOption,
      O.chain(O.fromEither),
      O.flatten,
      O.map(status => status === FormStatus.Complete),
      O.getOrElse(() => false)
    );

    return hasCompletedByUserId && isStatusCompleted;
  }, [model.completedByUserId, model.status]);

  const isFormCreatorIdPresent = useMemo(
    () =>
      pipe(
        model.creatorUserId,
        deferredToOption,
        O.chain(O.fromEither),
        O.flatten,
        O.isSome
      ),
    [model.creatorUserId]
  );

  const hasEditPermissions =
    props.checkPermission("EDIT_REPORTS") ||
    (props.checkPermission("EDIT_OWN_REPORTS") && isOwnForm);

  const isEditable = !isFormCompleted && hasEditPermissions;

  const hasReopenPermission =
    props.checkPermission("REOPEN_REPORTS") ||
    (props.checkPermission("REOPEN_OWN_REPORT") && isOwnForm);

  const hasDeletePermission =
    props.checkPermission("DELETE_REPORTS") ||
    (props.checkPermission("DELETE_OWN_REPORTS") && isOwnForm);

  useLeavePageConfirm("Discard unsaved changes?", compareEboSnapshots(model));

  const actionsMenuItems: Option<NonEmptyArray<MenuItemProps>> = pipe(
    model.eboId,
    deferredToOption,
    O.chain(O.fromEither),
    O.flatten,
    O.chain(eboId => {
      const reopenEboItem: MenuItemProps = {
        label: "Edit",
        icon: "edit",
        onClick: flow(Started, ReopenEbo(eboId), dispatch),
      };

      const deleteEboItem: MenuItemProps = {
        label: "Delete",
        icon: "trash_empty",
        onClick: flow(constant(O.some(eboId)), ShowDeleteEboModal, dispatch),
      };

      return pipe(
        [
          O.fromPredicate(() => isFormCompleted && hasReopenPermission)(
            reopenEboItem
          ),
          O.fromPredicate(() => isEditable && hasDeletePermission)(
            deleteEboItem
          ),
        ],
        A.compact,
        NEA.fromArray
      );
    })
  );

  type HeaderProps = {
    onClickDelete: O.Option<() => void>;
  };

  const Header = ({ onClickDelete }: HeaderProps): JSX.Element => (
    <PageHeader
      linkText="All forms"
      linkRoute="/forms"
      setSelectedTab={(selectedTab: FormViewTabStates) =>
        dispatch(ChangeFormViewState(selectedTab))
      }
      selectedTab={model.selectedTab}
    >
      <section className="w-full flex flex-1 justify-between">
        <h4 className="text-neutral-shade-100 text-[1.5rem]">
          Energy Based Observation
        </h4>
        {O.isSome(onClickDelete) && (
          <OptionalView
            value={actionsMenuItems}
            render={items => (
              <Dropdown className="z-10" menuItems={[items]}>
                <ButtonIcon iconName="hamburger" />
              </Dropdown>
            )}
          />
        )}
      </section>
    </PageHeader>
  );

  type FooterProps = {
    isEboEditable: boolean;
    label: string;
    disabled: boolean;
    onClick: () => void;
  };

  const Footer = ({
    isEboEditable,
    label,
    disabled,
    onClick,
  }: FooterProps): JSX.Element => (
    <footer
      className={cx("flex flex-col mt-auto md:max-w-screen-lg items-end", {
        "p-4 px-0": !isMobile && !isTablet,
        "p-2.5 h-[54px]": isMobile || isTablet,
      })}
    >
      {isEboEditable && (
        <ButtonPrimary label={label} disabled={disabled} onClick={onClick} />
      )}
    </footer>
  );

  const saveEbo: Either<
    ApiError | t.Errors | eboFormValidationError | null,
    (shouldComplete: boolean) => void
  > = pipe(
    E.Do,
    E.bindW("eboId", () =>
      pipe(
        model.eboId,
        E.fromPredicate(isResolved, constNull),
        E.chainW(i => i.value)
      )
    ),
    E.bindW("input", () => toEboInput(model)),
    E.map(
      ({ eboId, input }) =>
        shouldComplete =>
          dispatch(flow(Started, SaveEbo(eboId, input)(shouldComplete))())
    )
  );

  const shouldFormSectionPreventSaveEboAction = useCallback(() => {
    const tenantName = getTenantName();
    const stepList = getStepListForTenant(tenantName);
    // This section has a validation that checks completeness of every other step.
    const baseEboSteps = pipe(stepList, A.dropRight(1));

    // Checks completed status of each other step in EBO.
    const isBaseEboStepsCompleted = pipe(
      baseEboSteps,
      A.map(step => pipe(model.completedSteps, S.elem(EqString)(step))),
      A.every(baseStepCompleted => baseStepCompleted === true)
    );

    // Checks if at least one high energy tasks and activities is selected
    const isHighEnergyTasksStepDataEmpty = pipe(
      model.steps.highEnergyTasks,
      hets => hets.selectedActivities,
      M.isEmpty
    );

    // Checks if each high energy tasks individual subsection data is valid
    const isHighEnergyTasksSubStepsDataValid = () => {
      const { subStepModels } = model.steps.highEnergyTasks;

      if (
        O.isSome(subStepModels) &&
        isResolved(model.hazards) &&
        isRight(model.hazards.value)
      ) {
        const hazards = model.hazards.value.right;

        return pipe(
          subStepModels.value,
          A.map(HighEnergyTasksSubSection.validateTaskHazardData(hazards)),
          A.sequence(E.Applicative),
          E.fold(
            () => false,
            () => true
          )
        );
      } else {
        return true;
      }
    };

    // Checks if each high energy tasks individual subsection completed status
    // This cannot be controlled with isBaseEboStepsCompleted function
    const isHighEnergyTasksSubStepsCompleted = () => {
      const { subStepModels } = model.steps.highEnergyTasks;

      return pipe(
        subStepModels,
        O.map(subSteps =>
          pipe(
            subSteps,
            A.map(subStep =>
              pipe(
                model.completedSteps,
                S.elem(EqString)(
                  `highEnergyTasks:${subStep.taskId}:${subStep.instanceId}`
                )
              )
            ),
            A.every(isSubStepCompleted => isSubStepCompleted === true)
          )
        ),
        O.getOrElse(() => true)
      );
    };

    switch (model.currentStep) {
      case "observationDetails": {
        const formElementIdsWithError =
          ObservationDetails.getAllFormElementIdWithError(
            model.steps.observationDetails
          );

        if (A.isNonEmpty(formElementIdsWithError)) {
          pipe(
            formElementIdsWithError,
            ObservationDetails.SetFormElementIdsWithError,
            ObservationDetailsAction,
            dispatch
          );

          document
            .getElementById(formElementIdsWithError[0])
            ?.scrollIntoView({ behavior: "smooth" });

          return A.isNonEmpty(formElementIdsWithError);
        }

        const isActivitiesHaveNonSelectedWorkType = pipe(
          model.tasks,
          deferredToOption,
          O.chain(O.fromEither),
          O.map(
            ObservationDetails.isSelectedActivitiesPartOfSelectedWorkTypes(
              model.steps.observationDetails.workType
            )(model.steps.highEnergyTasks.selectedActivities)
          ),
          O.getOrElse(() => false)
        );

        if (M.isEmpty(model.steps.highEnergyTasks.selectedActivities)) {
          return false;
        }

        if (isActivitiesHaveNonSelectedWorkType) {
          pipe(
            !model.showWorkTypeBasedActivityRemovalModal,
            ShowWorkTypeBasedActivityRemovalModal,
            dispatch
          );
          return !model.showWorkTypeBasedActivityRemovalModal;
        }
      }
      case "highEnergyTasks": {
        const { selectedActivities, subStep, subStepModels } =
          model.steps.highEnergyTasks;

        if (O.isNone(subStep)) {
          const isSelectedActivitiesEmpty = pipe(selectedActivities, M.isEmpty);
          pipe(
            isSelectedActivitiesEmpty,
            HighEnergyTasks.ToggleErrorsEnabled,
            HighEnergyTasksAction,
            dispatch
          );
          return isSelectedActivitiesEmpty;
        } else {
          if (
            O.isSome(subStepModels) &&
            O.isSome(subStep) &&
            isResolved(model.hazards) &&
            isRight(model.hazards.value)
          ) {
            const hazards = model.hazards.value.right;
            const currentSubStep = subStep.value;

            const hazardIdsWithError = pipe(
              subStepModels.value,
              A.filter(
                ssm =>
                  ssm.taskId === currentSubStep.taskId &&
                  ssm.instanceId === currentSubStep.instanceId
              ),
              A.chain(
                HighEnergyTasksSubSection.getTaskHazardIdsWithError(hazards)
              )
            );

            if (A.isNonEmpty(hazardIdsWithError)) {
              document
                .getElementById(hazardIdsWithError[0])
                ?.scrollIntoView({ behavior: "smooth" });
            }

            return A.isNonEmpty(hazardIdsWithError);
          }
        }
      }
      case "personnelSection": {
        // Checks if at least one personnel is selected
        const isPersonnelSectionCompleted = pipe(
          model.steps.personnelSection.crewMembers,
          O.fold(
            () => false,
            cls => pipe(cls, A.isNonEmpty)
          )
        );

        const personnelSectionErrors = [];

        if (!isPersonnelSectionCompleted) {
          document
            .getElementById(PersonnelSection.formElementIds.crewMembers)
            ?.scrollIntoView({ behavior: "smooth" });

          personnelSectionErrors.push(
            PersonnelSection.formElementIds.crewMembers
          );
        }

        if (
          !isBaseEboStepsCompleted ||
          isHighEnergyTasksStepDataEmpty ||
          !isHighEnergyTasksSubStepsDataValid() ||
          !isHighEnergyTasksSubStepsCompleted
        ) {
          personnelSectionErrors.push(
            PersonnelSection.HAS_ERROR_ON_OTHER_FORM_SECTIONS
          );
        }

        pipe(
          personnelSectionErrors,
          PersonnelSection.SetSectionErrors,
          PersonnelSectionAction,
          dispatch
        );

        return (
          !isBaseEboStepsCompleted ||
          isHighEnergyTasksStepDataEmpty ||
          !isHighEnergyTasksSubStepsDataValid() ||
          !isHighEnergyTasksSubStepsCompleted() ||
          !isPersonnelSectionCompleted
        );
      }
      case "summary": {
        if (
          tenantName === "xcelenergy" ||
          tenantName === "test-xcelenergy" ||
          tenantName === "test-xcelenergy1"
        ) {
          const summarySectionErrors = [];
          if (
            !isBaseEboStepsCompleted ||
            isHighEnergyTasksStepDataEmpty ||
            !isHighEnergyTasksSubStepsDataValid() ||
            !isHighEnergyTasksSubStepsCompleted
          ) {
            summarySectionErrors.push(Summary.HAS_ERROR_ON_OTHER_FORM_SECTIONS);
          }
          pipe(
            summarySectionErrors,
            Summary.SetSectionErrors,
            SummaryAction,
            dispatch
          );

          return (
            !isBaseEboStepsCompleted ||
            isHighEnergyTasksStepDataEmpty ||
            !isHighEnergyTasksSubStepsDataValid() ||
            !isHighEnergyTasksSubStepsCompleted()
          );
        }
      }

      case "historicIncidents":
      case "photos":
      case "additionalInformation": {
        return false;
      }
    }
  }, [
    model.currentStep,
    model.completedSteps,
    model.hazards,
    model.steps.observationDetails,
    model.steps.personnelSection.crewMembers,
    model.steps.highEnergyTasks,
    model.showWorkTypeBasedActivityRemovalModal,
    model.tasks,
    dispatch,
  ]);

  const isFinalFormStep = useCallback(() => {
    const tenantName = getTenantName();
    const stepList = getStepListForTenant(tenantName);

    return pipe(
      stepList,
      A.last,
      O.map(lastStepName => lastStepName === model.currentStep),
      O.getOrElse(() => false)
    );
  }, [model.currentStep]);

  const handleRemoveActivitiesBasedOnWorkTypes = () => {
    const deferredTasks = pipe(
      model.tasks,
      deferredToOption,
      O.chain(O.fromEither)
    );

    const deferredHazards = pipe(
      model.hazards,
      deferredToOption,
      O.chain(O.fromEither)
    );

    pipe(
      sequenceS(O.Apply)({
        tasks: deferredTasks,
        hazards: deferredHazards,
      }),
      O.map(
        HighEnergyTasks.removeActivitiesBasedOnSelectedWorkTypes(
          model.steps.observationDetails.workType
        )(model.steps.highEnergyTasks)
      ),
      O.map(m => pipe(m, UpdateHighEnergyTasksModel, dispatch))
    );
  };

  const onSaveEbo = (shouldComplete: boolean) => {
    if (shouldFormSectionPreventSaveEboAction()) return null;

    if (
      model.currentStep === "highEnergyTasks" &&
      O.isSome(model.steps.highEnergyTasks.subStep)
    ) {
      const { subStepModels, subStep } = model.steps.highEnergyTasks;
      const currentSubStepModel = getSubStepModel(
        subStepModels,
        subStep.value.taskId,
        subStep.value.instanceId
      );

      if (
        O.isSome(currentSubStepModel) &&
        isResolved(model.hazards) &&
        E.isRight(model.hazards.value)
      ) {
        const recommendedHazards =
          HighEnergyTasksSubSection.getRecommendedHazards(
            model.hazards.value.right,
            currentSubStepModel.value.selectedHazards,
            currentSubStepModel.value.taskId
          );

        // Control logic for Recommended Hazards Dialog
        if (
          O.isNone(currentSubStepModel.value.recommendedHazardDialog) &&
          !A.isEmpty(recommendedHazards)
        ) {
          return flow(
            HighEnergyTasksSubSection.ShowRecommendedHazardDialog,
            HighEnergyTasksSubSectionAction,
            HighEnergyTasksAction,
            dispatch
          )();
        }

        // Control logic for at least one hazard is observed
        if (M.isEmpty(currentSubStepModel.value.selectedHazards)) {
          return pipe(
            "NO_HAZARD_SELECTED",
            HighEnergyTasksSubSection.ShowError,
            HighEnergyTasksSubSectionAction,
            HighEnergyTasksAction,
            dispatch
          );
        }
      }
    }

    return pipe(
      saveEbo,
      E.fold(
        () => console.log("something went wrong while saving ebo to backend"),
        saveEboAction =>
          pipe(
            isFinalFormStep() && !model.showCompleteEboModal,
            matchBoolean(
              () => saveEboAction(shouldComplete),
              () => pipe(true, ShowCompleteEboModal, dispatch)
            )
          )
      )
    );
  };

  const hasActiveSubStep = useCallback(
    (step: StepName) => {
      switch (step) {
        case "highEnergyTasks": {
          return O.isSome(model.steps[step].subStep);
        }
        case "observationDetails":
        case "personnelSection":
        case "historicIncidents":
        case "photos":
        case "additionalInformation":
        case "summary": {
          return false;
        }
      }
    },
    [model.steps]
  );

  const renderOptionFn: RenderOptionFn<NavigationOption> = ({
    listboxOptionProps: { selected },
    option: { name, icon, status, isSubStep },
  }) => (
    <NavItem
      as="li"
      icon={icon}
      name={name}
      status={status}
      markerType="left"
      isSelected={selected}
      isSubStep={isSubStep}
    />
  );

  const wizardNavigation = useMemo(() => {
    const tenantName = getTenantName();
    const stepList = getStepListForTenant(tenantName);

    const isCurrentStep = (step: StepName): boolean => {
      switch (step) {
        case "highEnergyTasks": {
          return (
            EQ.eqStrict.equals(step, model.currentStep) &&
            EQ.eqStrict.equals(model.steps.highEnergyTasks.subStep, O.none)
          );
        }
        case "observationDetails":
        case "personnelSection":
        case "historicIncidents":
        case "photos":
        case "additionalInformation":
        case "summary": {
          return EQ.eqStrict.equals(step, model.currentStep);
        }
      }
    };

    const isCompleted = (step: StepName): boolean =>
      pipe(model.completedSteps, S.elem(eqCompletedStep)(step));

    const hasErrorStep = (step: StepName): boolean => {
      switch (step) {
        case "observationDetails": {
          return pipe(
            model.steps.observationDetails,
            ObservationDetails.validateEboInput,
            E.isLeft
          );
        }
        case "highEnergyTasks":
          return (
            (model.steps.highEnergyTasks.errorsEnabled ||
              isFormCreatorIdPresent) &&
            M.isEmpty(model.steps.highEnergyTasks.selectedActivities)
          );
        case "personnelSection":
          return pipe(
            model.steps.personnelSection.crewMembers,
            O.map(A.isEmpty),
            O.getOrElse(() => isFormCreatorIdPresent)
          );
        case "historicIncidents":
        case "photos":
        case "additionalInformation":
        case "summary": {
          return false;
        }
      }
    };

    const getStatus = (step: StepName): Status => {
      if (
        step === "highEnergyTasks" &&
        isCurrentStep(step) &&
        hasErrorStep(step)
      )
        return "error";

      if (
        step === "observationDetails" &&
        (model.steps.observationDetails.errorsEnabled ||
          isFormCreatorIdPresent) &&
        hasErrorStep(step)
      )
        return "error";

      if (!isCurrentStep(step) && hasErrorStep(step)) return "error";
      if (isCompleted(step)) {
        return isCurrentStep(step) ? "saved_current" : "saved";
      } else {
        return isCurrentStep(step) ? "current" : "default";
      }
    };

    const getSelectStatusAndIcon = (step: StepName): SelectStatusAndIcon => {
      const status = getStatus(step);
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

    const selectOptions: NavigationOption[] = stepList.map((step, index) => {
      const { status, icon } = getSelectStatusAndIcon(step);
      const subSteps = pipe(
        step,
        generateSubStepNavigations(model)(dispatch)(false)
      );

      return {
        name: stepNames[step],
        id: index,
        status,
        icon,
        subOptions: pipe(
          subSteps,
          O.fold(() => [], identity)
        ),
      };
    });

    return (
      <>
        <Select
          className={cx(
            "!absolute md:hidden block pb-4 w-[calc(100%-24px)] pt-4"
          )}
          options={selectOptions}
          onSelect={({ id, isSubStep, onSelect }) =>
            isSubStep ? onSelect?.() : handleNavTo(stepList[id])
          }
          defaultOption={pipe(
            selectOptions,
            A.lookup(stepList.indexOf(model.currentStep)),
            O.fold(() => undefined, identity)
          )}
          optionsClassNames="py-2"
          renderOptionFn={renderOptionFn}
        />
        {pipe(
          stepList,
          A.map(step => {
            const subStepNavigations = pipe(
              step,
              generateSubStepNavigations(model)(dispatch)()
            );

            return (
              <div key={step.toString()} className="md:block hidden w-full">
                <StepItem
                  status={getStatus(step)}
                  key={step.toString()}
                  onClick={() => handleNavTo(step)}
                  label={stepNames[step]}
                />
                {O.isSome(subStepNavigations) && (
                  <div className="pl-4 w-full flex flex-col gap-2">
                    {subStepNavigations.value}
                  </div>
                )}
              </div>
            );
          })
        )}
      </>
    );
  }, [model, hasActiveSubStep, dispatch, handleNavTo]);

  const eboFormId = pipe(
    model.eboId,
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
        setEboFormAuditData(response.data);
      },
      onError: error => {
        console.log(error);
        toastCtx?.pushToast("error", messages.SomethingWentWrong);
      },
    },
  });

  useEffect(() => {
    if (eboFormId && model.selectedTab === FormViewTabStates.HISTORY) {
      const requestData = {
        object_id: eboFormId,
        object_type: "ebo",
        order_by: {
          field: "created_at",
          desc: true,
        },
      };
      fetchFormsAuditLogsData(requestData);
    }
  }, [eboFormId, model.selectedTab]);

  return (
    <PageLayout
      className="md:mt-6 md:pl-6 flex-1 overflow-hidden w-full max-w-screen-lg"
      sectionPadding="none"
      header={
        <Header
          onClickDelete={
            isResolved(model.eboId) && E.isRight(model.eboId.value)
              ? pipe(
                  model.eboId.value.right,
                  O.map(eboId => {
                    return () =>
                      pipe(O.some(eboId), ShowDeleteEboModal, dispatch);
                  })
                )
              : O.none
          }
        />
      }
      footer={
        model.selectedTab === FormViewTabStates.FORM && (
          <Footer
            isEboEditable={isEditable}
            label={
              isFinalFormStep() ? "Save and complete" : "Save and continue"
            }
            disabled={false}
            onClick={() => onSaveEbo(false)}
          />
        )
      }
    >
      {model.selectedTab === FormViewTabStates.FORM ? (
        <Nav.View wizardNavigation={wizardNavigation}>
          <StepView
            {...props}
            saveEbo={() => onSaveEbo(false)}
            isReadOnly={!isEditable}
          />
        </Nav.View>
      ) : (
        <FormHistory data={eboFormAuditData} isAuditDataLoading={isLoading} />
      )}
      <Modal
        title="Warning"
        isOpen={model.showWorkTypeBasedActivityRemovalModal}
        closeModal={() =>
          pipe(false, ShowWorkTypeBasedActivityRemovalModal, dispatch)
        }
      >
        <div className="mb-10">
          <Paragraph
            text={
              "Removal of any work types will result in the removal of related task, hazards and controls. Are you sure you want to do this?"
            }
          />
        </div>
        <div className="flex justify-end gap-3">
          <ButtonRegular
            label="Cancel"
            onClick={() =>
              pipe(false, ShowWorkTypeBasedActivityRemovalModal, dispatch)
            }
          />
          <ButtonDanger
            label="Remove and continue"
            onClick={handleRemoveActivitiesBasedOnWorkTypes}
          />
        </div>
      </Modal>
      <Modal
        title="Complete/Submit form?"
        isOpen={model.showCompleteEboModal}
        closeModal={() => pipe(false, ShowCompleteEboModal, dispatch)}
      >
        <div className="flex flex-col gap-4">
          <p>Are you sure you want to complete/submit this form?</p>
          <div className="flex justify-end gap-3 mt-8">
            <ButtonSecondary
              label="Save and finish later"
              onClick={() => onSaveEbo(false)}
            />
            <ButtonPrimary
              label="Complete Report"
              onClick={() => onSaveEbo(true)}
            />
          </div>
        </div>
      </Modal>
      <Modal
        title={`Are you sure you want to do this?`}
        isOpen={O.isSome(model.showDeleteEboModal)}
        closeModal={() => pipe(O.none, ShowDeleteEboModal, dispatch)}
      >
        <div className="mb-10">
          <Paragraph
            text={
              "Deleting this Energy Based Observation will remove all the associated details as well as remove it from any future reports. "
            }
          />
        </div>
        <div className="flex justify-end gap-3">
          <ButtonRegular
            label="Cancel"
            onClick={() => pipe(O.none, ShowDeleteEboModal, dispatch)}
          />

          <ButtonDanger
            label="Delete"
            onClick={flow(Started, DeleteEbo, dispatch)}
          />
        </div>
      </Modal>
    </PageLayout>
  );
}

type StepViewProps = Props & {
  saveEbo: () => void;
  isReadOnly: boolean;
};

function StepView(props: StepViewProps): JSX.Element {
  const { model, dispatch } = props;

  switch (model.currentStep) {
    case "observationDetails":
      return (
        <ObservationDetails.View
          model={model.steps[model.currentStep]}
          workTypes={pipe(
            model.workTypes,
            deferredToOption,
            O.chain(O.fromEither)
          )}
          dispatch={flow(ObservationDetailsAction, dispatch)}
          isReadOnly={props.isReadOnly}
        />
      );
    case "highEnergyTasks":
      if (
        isResolved(model.tasks) &&
        E.isRight(model.tasks.value) &&
        isResolved(model.hazards) &&
        isRight(model.hazards.value)
      ) {
        const { subStep, subStepModels } = model.steps[model.currentStep];

        if (O.isNone(subStep)) {
          const tasks = model.tasks.value.right;
          const selectedWorkTypes = model.steps.observationDetails.workType;

          const refineTasksWithSelectedWorkTypes = tasks;

          return (
            <HighEnergyTasks.View
              model={model.steps[model.currentStep]}
              dispatch={a => {
                pipe(a, HighEnergyTasksAction, dispatch);
                if (a.type === "TasksSelected") {
                  pipe(
                    a.selectedActivities,
                    Started,
                    pipe(
                      a.selectedActivities,
                      M.toArray(OrdString),
                      A.map(([_, activityItem]) =>
                        S.toArray(ordLibraryTaskId)(activityItem.taskIds)
                      ),
                      A.flatten,
                      GetTasksHistoricalIncidents
                    ),
                    dispatch
                  );
                }
              }}
              tasks={refineTasksWithSelectedWorkTypes}
              hazards={model.hazards.value.right}
              selectedWorkTypes={selectedWorkTypes}
              isReadOnly={props.isReadOnly}
            />
          );
        } else {
          const subStepTask = subStep.value;

          const subStepModel = getSubStepModel(
            subStepModels,
            subStepTask.taskId,
            subStepTask.instanceId
          );

          if (
            O.isSome(subStepModel) &&
            isResolved(model.hazards) &&
            isRight(model.hazards.value)
          ) {
            return (
              <HighEnergyTasksSubSection.View
                tasks={model.tasks.value.right}
                hazards={model.hazards.value.right}
                model={subStepModel.value}
                dispatch={flow(
                  HighEnergyTasksSubSectionAction,
                  HighEnergyTasksAction,
                  dispatch
                )}
                saveEbo={props.saveEbo}
                isReadOnly={props.isReadOnly}
                originalTaskNames={
                  model.steps.highEnergyTasks.originalTaskNames
                }
              />
            );
          } else {
            return <div>Invalid case for sub step</div>;
          }
        }
      } else if (isResolved(model.tasks) && E.isLeft(model.tasks.value)) {
        return <div>Error: {model.tasks.value.left.type}</div>;
      } else {
        return <div>Loading...</div>;
      }
    case "additionalInformation":
      return (
        <AdditionalInformation.View
          model={model.steps[model.currentStep]}
          dispatch={flow(AdditionalInformationAction, dispatch)}
          isReadOnly={props.isReadOnly}
        />
      );
    case "historicIncidents":
      const selectedTaskIdsNotEmpty = !M.isEmpty(
        model.steps.highEnergyTasks.selectedActivities
      );

      const selectedTasksIncidentsResolved =
        isResolved(model.selectedTasksIncidents) &&
        E.isRight(model.selectedTasksIncidents.value);
      const selectedTasksIncidents =
        isResolved(model.selectedTasksIncidents) &&
        E.isRight(model.selectedTasksIncidents.value) &&
        model.selectedTasksIncidents.value.right;
      if (
        isResolved(model.tasks) &&
        E.isRight(model.tasks.value) &&
        (selectedTaskIdsNotEmpty ? selectedTasksIncidentsResolved : true)
      ) {
        return (
          <HistoricIncidents.View
            model={model.steps[model.currentStep]}
            dispatch={flow(HistoricIncidentsAction, dispatch)}
            selectedTaskIds={pipe(
              model.steps.highEnergyTasks.selectedActivities,
              getAllTaskIdsFromActivities,
              S.fromArray(ordLibraryTaskId)
            )}
            tasks={model.tasks.value.right}
            selectedTaskIncidents={
              selectedTasksIncidents ? selectedTasksIncidents : []
            }
            isReadOnly={props.isReadOnly}
            originalTaskNames={model.steps.highEnergyTasks.originalTaskNames}
          />
        );
      } else if (isResolved(model.tasks) && E.isLeft(model.tasks.value)) {
        return <div>Error: {model.tasks.value.left.type}</div>;
      } else {
        return <div>Loading...</div>;
      }
    case "photos":
      return (
        <PhotosSection.View
          model={model.steps[model.currentStep]}
          dispatch={flow(PhotosAction, dispatch)}
          isReadOnly={props.isReadOnly}
        />
      );
    case "summary":
      const data = toSummaryData(model);
      return (
        <Summary.View
          model={model.steps[model.currentStep]}
          dispatch={flow(SummaryAction, dispatch)}
          observationDetails={{
            data: data.observationDetails,
            onClickEdit: () =>
              dispatch(NavToWithFromStep("observationDetails")("summary")),
          }}
          hazards={{
            data: data.hazards,
            onClickEdit: () =>
              dispatch(NavToWithFromStep("highEnergyTasks")("summary")),
            onTaskClickEdit: taskId =>
              flow(NavToHighEnergyTasksSubSection(taskId), dispatch),
            originalTaskNames: model.steps.highEnergyTasks.originalTaskNames,
            isReadOnly: props.isReadOnly,
          }}
          historicIncidents={{
            data: data.historicIncidents,
            onClickEdit: () =>
              dispatch(NavToWithFromStep("historicIncidents")("summary")),
          }}
          additionalInformation={{
            data: data.additionalInformation,
            onClickEdit: () =>
              dispatch(NavToWithFromStep("additionalInformation")("summary")),
          }}
          photos={{
            data: data.photos,
            onClickEdit: () => dispatch(NavToWithFromStep("photos")("summary")),
            model: model.steps["summary"],
            dispatch: flow(SummaryAction, dispatch),
          }}
          isReadOnly={props.isReadOnly}
        />
      );
    case "personnelSection":
      if (isResolved(model.crewMembers) && E.isRight(model.crewMembers.value)) {
        return (
          <PersonnelSection.View
            model={model.steps[model.currentStep]}
            crewLeaders={model.crewMembers.value.right}
            dispatch={flow(PersonnelSectionAction, dispatch)}
            isReadOnly={props.isReadOnly}
          />
        );
      } else if (
        isResolved(model.crewMembers) &&
        E.isLeft(model.crewMembers.value)
      ) {
        return <div>Error: {model.crewMembers.value.left.type}</div>;
      } else {
        return <div>Loading...</div>;
      }
  }
}
