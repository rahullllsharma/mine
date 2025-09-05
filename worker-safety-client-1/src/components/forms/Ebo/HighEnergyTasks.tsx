import type { ReactNode } from "react";
import type { ApiResult } from "@/api/api";
import type { Deferred } from "@/utils/deferred";
import type {
  ActivitiesGroupId,
  Ebo,
  Hazard,
  HazardId,
  LibraryTask,
  LibraryTaskId,
  TaskHazardConnectorId,
  WorkType,
} from "@/api/codecs";
import type { StepSnapshot } from "../Utils";
import type { Option } from "fp-ts/Option";
import type { StepName } from "./Wizard";
import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type { Status } from "../Basic/StepItem";
import type { SelectedHazards } from "./HighEnergyTaskSubSection/HighEnergyTaskSubSection";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import type { SelectedActivities } from "./AddActivity/SelectTasks";
import type { NavigationOption } from "@/components/navigation/Navigation";
import * as O from "fp-ts/Option";
import * as A from "fp-ts/Array";
import * as E from "fp-ts/Either";
import * as EQ from "fp-ts/Eq";
import * as M from "fp-ts/lib/Map";
import * as S from "fp-ts/lib/Set";
import * as Ord from "fp-ts/lib/Ord";
import * as Tup from "fp-ts/lib/Tuple";
import { useMemo } from "react";
import { v4 as uuid } from "uuid";
import { constNull, flow, pipe } from "fp-ts/lib/function";
import { SectionHeading } from "@urbint/silica";
import { Eq as EqString, Ord as OrdString } from "fp-ts/string";
import { Eq as EqNumber, Ord as OrdNumber } from "fp-ts/number";
import { match as matchBoolean } from "fp-ts/boolean";
import { isResolved } from "@/utils/deferred";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import {
  ApplicabilityLevel,
  eqWorkTypeById,
  eqHazardId,
  eqLibraryTaskId,
  ordLibraryTaskId,
} from "@/api/codecs";
import { effectsBatch, mapEffect, noEffect } from "@/utils/reducerWithEffect";
import { DeleteActivityModal } from "@/container/activity/deleteActivityModal/DeleteActivityModal";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import { StepItem } from "../Basic/StepItem";
import StepLayout from "../StepLayout";
import { TaskCard } from "../Basic/TaskCard";
import { snapshotMap, snapshotHash, snapshotHashMap } from "../Utils";
import * as HighEnergyTaskSubSection from "./HighEnergyTaskSubSection/HighEnergyTaskSubSection";
import { eqCompletedStep } from "./Wizard";
import * as AddActivityDialog from "./AddActivity/Dialog";

export type ActivityItem = {
  activityGroup: {
    activityId: ActivitiesGroupId;
    activityName: string;
  };
  taskIds: Set<LibraryTaskId>;
};

type ActivityGroupDuplicateType = ActivityItem & {
  instanceId: number;
};

type InstanceId = number;

export type SelectedActivityTaskIds = Map<InstanceId, ActivityItem>;
export type SelectedDuplicateActivities = Map<string, SelectedActivityTaskIds>;
export type SubStepType = { taskId: LibraryTaskId; instanceId: InstanceId };

export type HighEnergyTaskErrors =
  | "NO_TASK_SELECTED"
  | "NO_WORK_TYPE_SELECTED_IN_OBSERVATION_DETAILS";

export const highEnergyTaskErrorTexts = (error: HighEnergyTaskErrors) => {
  switch (error) {
    case "NO_TASK_SELECTED": {
      return "At least one activity and task must be added to complete the Energy Based Observation";
    }
    case "NO_WORK_TYPE_SELECTED_IN_OBSERVATION_DETAILS": {
      return "Please select at least one Work type in the Observation Details page.";
    }
  }
};

export const ordByTaskName = pipe(
  OrdString,
  Ord.contramap(
    (t: HighEnergyTaskSubSection.Model & { taskName: string }) => t.taskName
  )
);

const ordByLibraryTaskName = pipe(
  OrdString,
  Ord.contramap((t: LibraryTask) => t.name)
);

export const ordByActivityGroupName = pipe(
  OrdString,
  Ord.contramap((s: HighEnergyTaskSubSection.Model) => s.activityName)
);

export type Model = {
  dialog: Option<AddActivityDialog.Model>;
  selectedActivities: SelectedDuplicateActivities;
  editActivity: O.Option<ActivityGroupDuplicateType>;
  subStep: Option<SubStepType>;
  subStepModels: Option<HighEnergyTaskSubSection.Model[]>;
  showDeleteActivityModel: Option<ActivityGroupDuplicateType>;
  deleteActivityGroup: boolean;
  errorsEnabled: boolean;
  originalTaskNames: Map<LibraryTaskId, string>;
  originalTasks: Map<
    LibraryTaskId,
    { id: LibraryTaskId; name: string; riskLevel: string }
  >;
};

const generateActivityKey = (
  activity: SelectedActivityTaskIds | undefined
): number => {
  if (activity && activity.size > 0) {
    return Math.max(...activity.keys()) + 1;
  } else {
    return 0;
  }
};

export const getTaskNameOfTaskId =
  (tasks: LibraryTask[]) => (model: Model) => (taskId: LibraryTaskId) => {
    return pipe(
      model.originalTaskNames.get(taskId),
      O.fromNullable,
      O.alt(() =>
        pipe(
          tasks,
          A.findFirst(task => task.id === taskId),
          O.map(task => task.name)
        )
      ),
      O.getOrElse(() => `[Deleted Task - ${taskId}]`)
    );
  };

export function init(ebo: Option<Ebo>): Model {
  const eboContents = pipe(
    ebo,
    O.map(e => e.contents)
  );

  const selectedActivities = pipe(
    eboContents,
    O.chain(a => a.activities),
    O.fold(
      () => new Map<string, SelectedActivityTaskIds>(),
      activities =>
        pipe(
          activities,
          A.reduce(
            new Map<string, SelectedActivityTaskIds>(),
            (result, curr) => {
              const activity = result.get(curr.name);

              const activityItem: SelectedActivityTaskIds = new Map([
                ...(activity ? activity : []),
                [
                  generateActivityKey(activity),
                  {
                    activityGroup: {
                      activityName: curr.name,
                      activityId: curr.id,
                    },
                    taskIds: pipe(
                      curr.tasks,
                      A.map(t => t.id),
                      S.fromArray(ordLibraryTaskId)
                    ),
                  },
                ],
              ]);

              result.set(curr.name, activityItem);

              return result;
            }
          )
        )
    )
  );

  // Currently this function is not required to be in EBO forms as we are saving both activities and highEnergyTasks
  // together to the backend, which also saves EmptySubStepModels.
  //
  // Keeping it here, if something gets out of sync in the database, as a fail-safe method.
  const generateEmptySubStepModels = (): Option<
    HighEnergyTaskSubSection.Model[]
  > =>
    pipe(
      selectedActivities,
      M.isEmpty,
      matchBoolean(
        () =>
          pipe(
            selectedActivities,
            M.toArray(OrdString),
            A.map(([_, activities]) => M.toArray(OrdNumber)(activities)),
            A.flatten,
            A.map(([instanceId, activityItem]) =>
              pipe(
                S.toArray(ordLibraryTaskId)(activityItem.taskIds),
                A.map(taskId => ({
                  activityName: activityItem.activityGroup.activityName,
                  activityId: activityItem.activityGroup.activityId,
                  taskId,
                  instanceId,
                  taskHazardConnectorId: uuid() as TaskHazardConnectorId,
                }))
              )
            ),
            A.flatten,
            A.map(activityItem =>
              HighEnergyTaskSubSection.init(
                activityItem.activityName,
                activityItem.activityId,
                activityItem.taskId,
                activityItem.instanceId,
                activityItem.taskHazardConnectorId,
                O.none,
                new Map(),
                new Map()
              )
            ),
            O.some
          ),
        () => O.none
      )
    );

  const generateSubStepModels = (): Option<HighEnergyTaskSubSection.Model[]> =>
    pipe(
      eboContents,
      O.chain(ec => ec.activities),
      O.map(activities =>
        pipe(
          activities,
          A.chain(activity =>
            pipe(
              activity.tasks,
              A.map(task =>
                HighEnergyTaskSubSection.init(
                  activity.name,
                  activity.id,
                  task.id,
                  task.instanceId,
                  pipe(
                    task.taskHazardConnectorId,
                    O.fold(
                      () => uuid() as TaskHazardConnectorId,
                      thcId => thcId
                    )
                  ),
                  pipe(
                    task.hazards,
                    HighEnergyTaskSubSection.generateSelectedHazardObservations,
                    O.of
                  ),
                  HighEnergyTaskSubSection.extractSavedHazardNames(
                    task.hazards
                  ),
                  HighEnergyTaskSubSection.extractSavedControlNames(
                    task.hazards
                  )
                )
              )
            )
          )
        )
      ),
      O.filter(A.isNonEmpty)
    );

  const subStepModels = pipe(
    eboContents,
    O.chain(a => a.highEnergyTasks),
    O.fold(generateEmptySubStepModels, generateSubStepModels)
  );

  // Extract original task data from saved EBO data
  const originalTaskNames = pipe(
    eboContents,
    O.chain(a => a.activities),
    O.fold(
      () => new Map<LibraryTaskId, string>(),
      activities =>
        pipe(
          activities,
          A.reduce(new Map<LibraryTaskId, string>(), (result, activity) => {
            pipe(
              activity.tasks,
              A.reduce(result, (taskMap, task) => {
                taskMap.set(task.id, task.name);
                return taskMap;
              })
            );
            return result;
          })
        )
    )
  );

  // Extract complete original task data from saved EBO data
  const originalTasks = pipe(
    eboContents,
    O.chain(a => a.activities),
    O.fold(
      () =>
        new Map<
          LibraryTaskId,
          { id: LibraryTaskId; name: string; riskLevel: string }
        >(),
      activities =>
        pipe(
          activities,
          A.reduce(
            new Map<
              LibraryTaskId,
              { id: LibraryTaskId; name: string; riskLevel: string }
            >(),
            (result, activity) => {
              pipe(
                activity.tasks,
                A.reduce(result, (taskMap, task) => {
                  taskMap.set(task.id, {
                    id: task.id,
                    name: task.name,
                    riskLevel: task.riskLevel,
                  });
                  return taskMap;
                })
              );
              return result;
            }
          )
        )
    )
  );

  return {
    dialog: O.none,
    selectedActivities: selectedActivities,
    subStep: O.none,
    subStepModels: subStepModels,
    showDeleteActivityModel: O.none,
    deleteActivityGroup: false,
    editActivity: O.none,
    errorsEnabled: false,
    originalTaskNames: originalTaskNames,
    originalTasks: originalTasks,
  };
}

export const makeSnapshot = (model: Model): StepSnapshot => {
  return {
    selectedActivities: pipe(
      model.selectedActivities,
      M.map(snapshotHashMap(OrdNumber)),
      snapshotMap
    ),
    subStepModels: pipe(
      model.subStepModels,
      O.map(
        A.map(subStepModel =>
          pipe(
            subStepModel,
            HighEnergyTaskSubSection.makeSnapshot,
            snapshotHash
          )
        )
      ),
      O.getOrElseW(constNull)
    ),
  };
};

export const getNextSubStep =
  (tasks: LibraryTask[]) =>
  (model: Model): Option<SubStepType> => {
    const orderedArrayOfSubStepInformations = pipe(
      model.subStepModels,
      O.map(
        A.map(ssm => ({
          ...ssm,
          taskName: getTaskNameOfTaskId(tasks)(model)(ssm.taskId),
        }))
      ),
      O.map(A.sortBy([ordByActivityGroupName, ordByTaskName])),
      O.map(
        A.map(subStepModel => ({
          taskId: subStepModel.taskId,
          instanceId: subStepModel.instanceId,
        }))
      )
    );

    return pipe(
      model.subStep,
      O.fold(
        () => pipe(orderedArrayOfSubStepInformations, O.chain(A.head)),
        currSubStep =>
          pipe(
            orderedArrayOfSubStepInformations,
            O.fold(
              () => O.none,
              ordSubSteps =>
                pipe(
                  ordSubSteps,
                  A.findIndex(
                    ss =>
                      ss.taskId === currSubStep.taskId &&
                      ss.instanceId === currSubStep.instanceId
                  ),
                  O.fold(
                    () => O.none,
                    currSubStepIndex =>
                      pipe(
                        currSubStepIndex === A.size(ordSubSteps) - 1,
                        matchBoolean(
                          () => O.of(ordSubSteps[currSubStepIndex + 1]),
                          () => O.none
                        )
                      )
                  )
                )
            )
          )
      )
    );
  };

export const withNextSubStep =
  (tasks: Deferred<ApiResult<LibraryTask[]>>) =>
  (model: Model): Option<Model> => {
    if (!isResolved(tasks) || E.isLeft(tasks.value)) return O.none;

    return pipe(
      getNextSubStep(tasks.value.right)(model),
      O.fold(
        () => O.none,
        nextSubStep =>
          pipe(
            model,
            m => ({
              ...m,
              subStep: O.of({
                taskId: nextSubStep.taskId,
                instanceId: nextSubStep.instanceId,
              }),
            }),
            O.of
          )
      )
    );
  };

export const getSubStepNavigations =
  (model: Model, completedSteps: Set<string>) =>
  (currentStep: StepName) =>
  (hazards: Hazard[]) =>
  (tasks: LibraryTask[]) =>
  (shouldReturnComponent = true) =>
  (
    NavToHighEnergyTasksSubSection: (
      taskId: LibraryTaskId
    ) => (instanceId: number) => void
  ) => {
    const getNavigationOfTaskId = (
      taskId: LibraryTaskId,
      instanceId: number
    ) => {
      const navigationKey = `${taskId}:${instanceId}`;
      const completedStepKey = `highEnergyTasks:${navigationKey}`;

      const isSubStepCompleted =
        S.elem(eqCompletedStep)(completedStepKey)(completedSteps);

      const isCurrentSubStep =
        O.isSome(model.subStep) &&
        eqLibraryTaskId.equals(model.subStep.value.taskId, taskId) &&
        EqNumber.equals(model.subStep.value.instanceId, instanceId);

      const subStepModel = pipe(
        model.subStepModels,
        O.chain(models =>
          pipe(
            models,
            A.findFirst(
              m => m.taskId === taskId && m.instanceId === instanceId
            ),
            O.fromNullable,
            O.flatten
          )
        )
      );

      const isTaskHazardFieldsValidForSubStep =
        O.isSome(subStepModel) &&
        E.isLeft(
          HighEnergyTaskSubSection.validateTaskHazardData(hazards)(
            subStepModel.value
          )
        );

      const hasSubStepError =
        O.isSome(subStepModel) && O.isSome(subStepModel.value.error);

      const getSubStepStatus = (): Status => {
        let subStepStatus: Status;

        if (EqString.equals(currentStep, "highEnergyTasks")) {
          if (isSubStepCompleted) {
            subStepStatus = isCurrentSubStep ? "saved_current" : "saved";
          } else {
            subStepStatus = isCurrentSubStep ? "current" : "default";
          }
        } else {
          subStepStatus = isSubStepCompleted ? "saved" : "default";
        }

        if (isTaskHazardFieldsValidForSubStep || hasSubStepError) {
          subStepStatus = "error";
        }

        return subStepStatus;
      };

      if (!shouldReturnComponent) {
        const getSubStepIcon = (status: Status) => {
          switch (status) {
            case "default":
            case "current":
              return "circle";
            case "error":
              return "error";
            case "saved":
            case "saved_current":
              return "circle_check";
          }
        };

        return {
          name: getTaskNameOfTaskId(tasks)(model)(taskId),
          id: `${taskId}:${instanceId}`,
          status: getSubStepStatus(),
          icon: getSubStepIcon(getSubStepStatus()),
          isSubStep: true,
          onSelect: () =>
            pipe(instanceId, NavToHighEnergyTasksSubSection(taskId)),
        };
      }

      return (
        <div className="first:mt-2">
          <StepItem
            status={getSubStepStatus()}
            truncate={true}
            key={navigationKey}
            onClick={() => NavToHighEnergyTasksSubSection(taskId)(instanceId)}
            label={getTaskNameOfTaskId(tasks)(model)(taskId)}
          />
        </div>
      );
    };

    return pipe(
      model.subStepModels,
      O.map(
        A.map(ssm => ({
          ...ssm,
          taskName: getTaskNameOfTaskId(tasks)(model)(ssm.taskId),
        }))
      ),
      O.map(A.sortBy([ordByActivityGroupName, ordByTaskName])),
      O.map(
        A.map(task => {
          return getNavigationOfTaskId(task.taskId, task.instanceId);
        })
      ),
      O.getOrElse((): (ReactNode | NavigationOption)[] => [])
    );
  };

export const getSelectedTasksMap =
  (tasks: LibraryTask[]) => (taskIds: LibraryTaskId[]) =>
    pipe(
      tasks,
      A.reduce(new Map<LibraryTaskId, LibraryTask>(), (map, t) => {
        if (A.elem(eqLibraryTaskId)(t.id, taskIds)) {
          map.set(t.id, t);
        }
        return map;
      })
    );

export const removeActivitiesBasedOnSelectedWorkTypes =
  (workTypes: WorkType[]) =>
  (model: Model) =>
  ({ tasks, hazards }: { tasks: LibraryTask[]; hazards: Hazard[] }): Model => {
    const getWorkTypesByTaskId = (taskId: LibraryTaskId): WorkType[] =>
      pipe(
        tasks,
        A.findFirst(task => task.id === taskId),
        O.chain(task => task.workTypes),
        O.getOrElse((): WorkType[] => [])
      );

    const updatedTaskIdsBasedOnWorkTypes = (
      taskIds: Set<LibraryTaskId>
    ): Set<LibraryTaskId> =>
      pipe(
        taskIds,
        S.toArray(ordLibraryTaskId),
        A.reduce(new Array<LibraryTaskId>(), (acc, taskId) => {
          return pipe(
            getWorkTypesByTaskId(taskId),
            A.map(wt => A.elem(eqWorkTypeById)(wt)(workTypes)),
            A.some(isPresent => isPresent === false),
            matchBoolean(
              () => [...acc, taskId],
              () => [...acc]
            )
          );
        }),
        S.fromArray(eqLibraryTaskId)
      );

    const updatedSelectedActivities = (): SelectedDuplicateActivities =>
      pipe(
        model.selectedActivities,
        M.map(activityMap =>
          pipe(
            activityMap,
            M.map(activityItem => ({
              ...activityItem,
              taskIds: updatedTaskIdsBasedOnWorkTypes(activityItem.taskIds),
            })),
            M.filter(activityItem => !S.isEmpty(activityItem.taskIds))
          )
        ),
        M.filter(activityMap => !M.isEmpty(activityMap))
      );

    return {
      ...model,
      selectedActivities: updatedSelectedActivities(),
      subStep: O.none,
      subStepModels: getSubSteps(updatedSelectedActivities())(hazards)(model),
    };
  };

export const toSaveEboInput = (tasks: LibraryTask[]) => (model: Model) => {
  const ac = pipe(
    model.selectedActivities,
    M.toArray(OrdString),
    A.map(([_, act]) => {
      return pipe(
        act,
        M.toArray(OrdNumber),
        A.map(([instanceId, activity]) => {
          return {
            activityName: activity.activityGroup.activityName,
            activityId: activity.activityGroup.activityId,
            tasks: activity.taskIds,
            instanceId: instanceId,
          };
        })
      );
    }),
    A.flatten,
    A.map(a => {
      return {
        name: a.activityName,
        id: a.activityId,
        tasks: pipe(
          a.tasks,
          S.toArray(ordLibraryTaskId),
          A.map(t => {
            // Try to find the task in the current task list
            const currentTask = pipe(
              tasks,
              A.findFirst(task => task.id === t)
            );

            // If task exists, use its data; otherwise use original task data from saved EBO
            return pipe(
              currentTask,
              O.map(task => ({
                fromWorkOrder: false,
                riskLevel: task.riskLevel,
                id: t,
                name: task.name,
                instanceId: a.instanceId,
              })),
              O.getOrElse(() => {
                // Get original task data from saved EBO
                const originalTask = model.originalTasks.get(t);
                if (originalTask) {
                  return {
                    fromWorkOrder: false,
                    riskLevel: originalTask.riskLevel as any,
                    id: t,
                    name: originalTask.name,
                    instanceId: a.instanceId,
                  };
                }

                // Fallback if no original task data is available
                return {
                  fromWorkOrder: false,
                  riskLevel: "LOW" as any,
                  id: t,
                  name: String(t),
                  instanceId: a.instanceId,
                };
              })
            );
          })
        ),
      };
    })
  );

  return E.of({ activities: ac });
};

export type Action =
  | {
      type: "TasksSelected";
      selectedActivities: SelectedActivities;
      hazards: Hazard[];
      tasks: LibraryTask[];
    }
  | {
      type: "AddActivityOpened";
    }
  | {
      type: "EditActivityOpened";
      activityItem: ActivityGroupDuplicateType;
    }
  | {
      type: "AddActivityClosed";
    }
  | {
      type: "AddActivityDialogAction";
      action: AddActivityDialog.Action;
    }
  | {
      type: "HighEnergyTasksSubSectionAction";
      action: HighEnergyTaskSubSection.Action;
    }
  | {
      type: "ShowDeleteActivityGroupModalAction";
      value: O.Option<ActivityGroupDuplicateType>;
    }
  | {
      type: "DeleteActivityGroupAction";
      value: boolean;
      hazards: Hazard[];
    }
  | { type: "ToggleErrorsEnabled"; value: boolean };

export const TasksSelected =
  (tasks: LibraryTask[]) =>
  (hazards: Hazard[]) =>
  (selectedActivities: SelectedActivities): Action => ({
    type: "TasksSelected",
    selectedActivities,
    hazards,
    tasks,
  });

export const AddActivityOpened = (): Action => ({
  type: "AddActivityOpened",
});

export const EditActivityOpened = (
  activityItem: ActivityGroupDuplicateType
): Action => ({
  type: "EditActivityOpened",
  activityItem,
});

export const AddActivityClosed = (): Action => ({
  type: "AddActivityClosed",
});

export const AddActivityDialogAction = (
  action: AddActivityDialog.Action
): Action => ({
  type: "AddActivityDialogAction",
  action,
});

export const ShowDeleteActivityGroupModalAction = (
  value: O.Option<ActivityGroupDuplicateType>
): Action => ({
  type: "ShowDeleteActivityGroupModalAction",
  value,
});

export const DeleteActivityGroupAction =
  (hazards: Hazard[]) =>
  (value: boolean): Action => ({
    type: "DeleteActivityGroupAction",
    value,
    hazards,
  });

export const ToggleErrorsEnabled = (value: boolean): Action => ({
  type: "ToggleErrorsEnabled",
  value,
});

export const HighEnergyTasksSubSectionAction = (
  action: HighEnergyTaskSubSection.Action
): Action => ({
  type: "HighEnergyTasksSubSectionAction",
  action,
});

const getSubSteps =
  (activitiesAsMap: SelectedDuplicateActivities) =>
  (hazards: Hazard[]) =>
  (model: Model): Option<HighEnergyTaskSubSection.Model[]> => {
    return pipe(
      activitiesAsMap,
      M.toArray(OrdString),
      A.map(([_, activityContents]) => M.toArray(OrdNumber)(activityContents)),
      A.flatten,
      a => a,
      A.map(([instanceId, activityContent]) =>
        pipe(
          S.toArray(ordLibraryTaskId)(activityContent.taskIds),
          A.map(taskId => ({
            instanceId: instanceId,
            activityGroup: activityContent.activityGroup,
            taskId,
          }))
        )
      ),
      A.flatten,
      A.map(subStepContents =>
        pipe(
          model.subStepModels,
          O.map(subStepModels =>
            pipe(
              subStepModels,
              A.filter(
                subStep =>
                  subStep.taskId === subStepContents.taskId &&
                  subStep.instanceId === subStepContents.instanceId
              ),
              A.head,
              O.map(ssm =>
                HighEnergyTaskSubSection.init(
                  subStepContents.activityGroup.activityName,
                  subStepContents.activityGroup.activityId,
                  subStepContents.taskId,
                  subStepContents.instanceId,
                  ssm.taskHazardConnectorId,
                  O.some(ssm.selectedHazards),
                  ssm.savedHazardNames,
                  ssm.savedControlNames
                )
              ),
              O.getOrElse(() =>
                HighEnergyTaskSubSection.init(
                  subStepContents.activityGroup.activityName,
                  subStepContents.activityGroup.activityId,
                  subStepContents.taskId,
                  subStepContents.instanceId,
                  uuid() as TaskHazardConnectorId,
                  O.of(getSelectedHazards(subStepContents.taskId, hazards)),
                  new Map(),
                  new Map()
                )
              )
            )
          ),
          O.getOrElse(() =>
            HighEnergyTaskSubSection.init(
              subStepContents.activityGroup.activityName,
              subStepContents.activityGroup.activityId,
              subStepContents.taskId,
              subStepContents.instanceId,
              uuid() as TaskHazardConnectorId,
              O.of(getSelectedHazards(subStepContents.taskId, hazards)),
              new Map(),
              new Map()
            )
          )
        )
      ),
      O.fromPredicate(A.isNonEmpty)
    );
  };

export const getAllTaskIdsFromActivities = (
  activities: Map<string, SelectedActivityTaskIds>
): LibraryTaskId[] =>
  pipe(
    activities,
    M.toArray(OrdString),
    A.map(([_, a]) => M.toArray(OrdNumber)(a)),
    A.flatten,
    A.map(([__, activityItem]) =>
      S.toArray(ordLibraryTaskId)(activityItem.taskIds)
    ),
    A.flatten
  );

const getSelectedHazards = (
  taskId: LibraryTaskId,
  hazards: Hazard[]
): SelectedHazards =>
  pipe(
    hazards,
    A.reduce(
      new Map<HazardId, HighEnergyTaskSubSection.DuplicateSelectedHazards>(),
      (output, hazard) => {
        const isSelectedHazard = pipe(
          hazard.taskApplicabilityLevels,
          A.exists(
            level =>
              EQ.eqStrict.equals(level.taskId, taskId) &&
              EQ.eqStrict.equals(
                level.applicabilityLevel,
                ApplicabilityLevel.ALWAYS
              )
          )
        );
        if (isSelectedHazard) {
          return M.upsertAt(eqHazardId)(
            hazard.id,
            new Map([[0, HighEnergyTaskSubSection.initialSelectedHazardData]])
          )(output);
        }

        return output;
      }
    )
  );

export const update = (
  model: Model,
  action: Action
): [Model, Effect<Action>] => {
  switch (action.type) {
    case "TasksSelected": {
      const activities = pipe(
        M.toArray(OrdString)(action.selectedActivities),
        A.map(([_, { activityGroup, taskIds }]) => ({
          activityName: activityGroup.activityName,
          activityId: activityGroup.activityId,
          taskIds,
        }))
      );

      const selectedActivities = new Map(model.selectedActivities.entries());

      if (O.isSome(model.editActivity)) {
        const editActivity = model.editActivity.value;
        const editedActivity = pipe(
          activities,
          A.filter(
            a => a.activityName === editActivity.activityGroup.activityName
          ),
          A.head
        );

        const activity = model.selectedActivities.get(
          editActivity.activityGroup.activityName
        );

        if (O.isSome(editedActivity)) {
          const modifiedActivity = new Map([
            ...(activity ? activity : []),
            [
              editActivity.instanceId,
              {
                activityGroup: {
                  activityName: editedActivity.value.activityName,
                  activityId: editedActivity.value.activityId,
                },
                taskIds: editedActivity.value.taskIds,
              },
            ],
          ]);

          selectedActivities.set(
            editActivity.activityGroup.activityName,
            modifiedActivity
          );

          pipe(
            activities,
            A.findIndex(
              a => a.activityName === editActivity.activityGroup.activityName
            ),
            O.map(index => activities.splice(index, 1))
          );
        } else {
          if (activity) {
            activity.delete(editActivity.instanceId);
            if (M.isEmpty(activity)) {
              selectedActivities.delete(
                editActivity.activityGroup.activityName
              );
            }
          }
        }
      }

      const activitiesAsMap = pipe(
        activities,
        A.reduce(selectedActivities, (result, curr) => {
          const activitiesWithActivityName = result.get(curr.activityName);

          return M.upsertAt(EqString)(
            curr.activityName,
            new Map([
              ...(activitiesWithActivityName || []),
              [
                generateActivityKey(activitiesWithActivityName),
                {
                  activityGroup: {
                    activityName: curr.activityName,
                    activityId: curr.activityId,
                  },
                  taskIds: curr.taskIds,
                },
              ],
            ])
          )(result);
        })
      );

      return [
        {
          ...model,
          selectedActivities: activitiesAsMap,
          subStepModels: pipe(
            model,
            getSubSteps(activitiesAsMap)(action.hazards)
          ),
        },
        noEffect,
      ];
    }
    case "AddActivityOpened":
      return [
        {
          ...model,
          dialog: O.some(
            AddActivityDialog.init(new Map(), model.selectedActivities)
          ),
        },
        noEffect,
      ];
    case "EditActivityOpened":
      return [
        {
          ...model,
          dialog: O.some(
            AddActivityDialog.init(
              new Map([
                [
                  action.activityItem.activityGroup.activityName,
                  {
                    activityGroup: action.activityItem.activityGroup,
                    taskIds: action.activityItem.taskIds,
                  },
                ],
              ]),
              model.selectedActivities
            )
          ),
          editActivity: O.some(action.activityItem),
        },
        noEffect,
      ];
    case "AddActivityClosed":
      return [
        {
          ...model,
          dialog: O.none,
          editActivity: O.none,
        },
        noEffect,
      ];
    case "ShowDeleteActivityGroupModalAction":
      return [
        {
          ...model,
          showDeleteActivityModel: action.value,
          deleteActivityGroup: false,
        },
        noEffect,
      ];
    case "DeleteActivityGroupAction":
      const selectedActivities = new Map(model.selectedActivities.entries());
      if (O.isSome(model.showDeleteActivityModel)) {
        const deleteActivity = model.showDeleteActivityModel.value;
        const activity = selectedActivities.get(
          deleteActivity.activityGroup.activityName
        );
        if (activity) {
          activity.delete(deleteActivity.instanceId);
          if (M.isEmpty(activity)) {
            selectedActivities.delete(
              deleteActivity.activityGroup.activityName
            );
          }
        }
      }

      return [
        {
          ...model,
          showDeleteActivityModel: O.none,
          selectedActivities,
          subStepModels: pipe(
            model,
            getSubSteps(selectedActivities)(action.hazards)
          ),
          deleteActivityGroup: false,
          errorsEnabled: M.isEmpty(selectedActivities),
        },
        noEffect,
      ];
    case "AddActivityDialogAction":
      return pipe(
        model.dialog,
        O.fold(
          () => [model, noEffect],
          d => [
            {
              ...model,
              dialog: O.some(AddActivityDialog.update(d, action.action)),
            },
            noEffect,
          ]
        )
      );
    case "HighEnergyTasksSubSectionAction": {
      const eqSubStep =
        (curr: SubStepType) => (ssm: HighEnergyTaskSubSection.Model) =>
          eqLibraryTaskId.equals(curr.taskId, ssm.taskId) &&
          EqNumber.equals(curr.instanceId, ssm.instanceId);

      return pipe(
        model.subStepModels,
        O.fold(
          () => [model, noEffect],
          (subStepModels): [Model, Effect<Action>] => {
            const updatedSubStepModels = pipe(
              subStepModels,
              A.map(ssm =>
                pipe(
                  model.subStep,
                  O.map(
                    (
                      curr
                    ): [
                      HighEnergyTaskSubSection.Model,
                      Effect<HighEnergyTaskSubSection.Action>
                    ] =>
                      pipe(
                        eqSubStep(curr)(ssm),
                        matchBoolean(
                          () => [ssm, noEffect],
                          () =>
                            HighEnergyTaskSubSection.update(ssm, action.action)
                        )
                      )
                  ),
                  O.getOrElse(
                    (): [
                      HighEnergyTaskSubSection.Model,
                      Effect<HighEnergyTaskSubSection.Action>
                    ] => [ssm, noEffect]
                  )
                )
              )
            );

            return [
              {
                ...model,
                subStepModels: pipe(updatedSubStepModels, A.map(Tup.fst), O.of),
              },
              pipe(
                updatedSubStepModels,
                A.map(Tup.snd),
                effectsBatch,
                mapEffect(HighEnergyTasksSubSectionAction)
              ),
            ];
          }
        )
      );
    }
    case "ToggleErrorsEnabled": {
      return [
        {
          ...model,
          errorsEnabled: action.value,
        },
        noEffect,
      ];
    }
  }
};

export type Props = ChildProps<Model, Action> & {
  selectedWorkTypes: WorkType[];
  tasks: LibraryTask[];
  hazards: Hazard[];
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  const generateTasksList = (activityItem: ActivityItem): LibraryTask[] =>
    pipe(
      activityItem.taskIds,
      S.toArray(ordLibraryTaskId),
      A.map(taskId => {
        // First check if we have original task data from saved EBO
        const originalTask = model.originalTasks.get(taskId);
        if (originalTask) {
          return {
            id: originalTask.id,
            name: originalTask.name,
            riskLevel: originalTask.riskLevel as any,
            workTypes: O.none,
            hazards: [],
            activitiesGroups: O.none,
          };
        }

        const existingTask = pipe(
          props.tasks,
          A.findFirst(task => task.id === taskId)
        );

        if (O.isSome(existingTask)) {
          return existingTask.value;
        }
        // Fallback if no task data is available
        return {
          id: taskId,
          name: String(taskId),
          riskLevel: "LOW" as any,
          workTypes: O.none,
          hazards: [],
          activitiesGroups: O.none,
        };
      })
    );

  const getMenuOptions = (
    activity: ActivityGroupDuplicateType
  ): MenuItemProps[][] => {
    return [
      [
        {
          icon: "edit",
          label: `Edit`,
          onClick: () => pipe(activity, flow(EditActivityOpened, dispatch)),
        },
      ],
      [
        {
          icon: "trash_empty",
          label: `Delete`,
          onClick: () =>
            pipe(
              O.some(activity),
              ShowDeleteActivityGroupModalAction,
              dispatch
            ),
        },
      ],
    ];
  };

  const hasNoWorkTypeSelectedError = useMemo(
    () => pipe(props.selectedWorkTypes, A.isEmpty),
    [props.selectedWorkTypes]
  );

  return (
    <>
      <StepLayout>
        <div className="p-4 md:p-0">
          <div className="flex flex-row justify-between">
            <SectionHeading className="text-xl font-semibold">
              Activities
            </SectionHeading>
            {!isReadOnly && (
              <ButtonSecondary
                label="Activities"
                iconStart="plus_circle_outline"
                disabled={hasNoWorkTypeSelectedError}
                onClick={flow(AddActivityOpened, dispatch)}
              />
            )}
          </div>
          {model.errorsEnabled &&
            M.isEmpty(model.selectedActivities) &&
            !hasNoWorkTypeSelectedError && (
              <div className="font-semibold text-system-error-40 text-sm mt-4">
                {highEnergyTaskErrorTexts("NO_TASK_SELECTED")}
              </div>
            )}
          {hasNoWorkTypeSelectedError && (
            <div className="font-semibold text-system-error-40 text-sm mt-4">
              {highEnergyTaskErrorTexts(
                "NO_WORK_TYPE_SELECTED_IN_OBSERVATION_DETAILS"
              )}
            </div>
          )}
          {M.isEmpty(model.selectedActivities) ? (
            <div className="flex flex-col items-center gap-2 mt-12">
              <h4 className="text-lg leading-7 font-semibold text-neutral-shade-100">
                You currently have no activities
              </h4>
              <span className="text-sm text-brand-gray-60 leading-5 max-w-[360px] text-center">
                Please click the button above to select the activities that are
                being observed
              </span>
            </div>
          ) : (
            <div className="flex flex-col gap-5">
              <span className="font-normal text-sm text-neutral-shade-75 leading-5">
                The Task classification (High/Medium/Low) is a relative measure
                representing the likelihood of exposure to high-energy hazards
                while the task is being performed.
              </span>
              {M.toArray(OrdString)(model.selectedActivities).map(
                ([activityName, a]) =>
                  M.toArray(OrdNumber)(a).map(([instanceId, activityItem]) => (
                    <div
                      key={`${activityName}${instanceId}`}
                      className="flex flex-col gap-3 bg-brand-gray-10 p-4 rounded-md"
                    >
                      <div className="flex flex-1 justify-between align-middle">
                        <span className="font-semibold text-neutral-shade-75">
                          {activityItem.activityGroup.activityName}
                        </span>
                        {!isReadOnly && (
                          <Dropdown
                            menuItems={getMenuOptions({
                              instanceId,
                              ...activityItem,
                            })}
                          >
                            <ButtonIcon iconName="more_horizontal" />
                          </Dropdown>
                        )}
                      </div>
                      <div className="flex flex-col gap-2">
                        {pipe(
                          activityItem,
                          generateTasksList,
                          A.sort(ordByLibraryTaskName),
                          A.map((task: LibraryTask) => (
                            <div key={task.id}>
                              <TaskCard
                                title={task.name}
                                risk={task.riskLevel}
                                showRiskInformation={false}
                                showRiskText={false}
                                withLeftBorder={false}
                              />
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  ))
              )}
            </div>
          )}
        </div>
      </StepLayout>
      {O.isSome(model.dialog) && (
        <AddActivityDialog.View
          model={model.dialog.value}
          dispatch={flow(AddActivityDialogAction, dispatch)}
          tasks={props.tasks}
          onSubmit={flow(TasksSelected(props.tasks)(props.hazards), dispatch)}
          onClose={flow(AddActivityClosed, dispatch)}
        />
      )}
      {O.isSome(model.showDeleteActivityModel) && (
        <DeleteActivityModal
          activityId={
            model.showDeleteActivityModel.value.activityGroup.activityName
          }
          onModalClose={() =>
            pipe(O.none, flow(ShowDeleteActivityGroupModalAction, dispatch))
          }
          onConfirm={O.some(() =>
            pipe(true, DeleteActivityGroupAction(props.hazards), dispatch)
          )}
        />
      )}
    </>
  );
}
