import type {
  ActivitiesGroup,
  ActivitiesGroupId,
  Activity,
  ActivityId,
  CriticalRisk,
  Jsb,
  LibraryTask,
  LibraryTaskId,
  ProjectLocationId,
} from "@/api/codecs";
import type {
  CreateActivityInput,
  SaveJobSafetyBriefingInput,
} from "@/api/generated/types";
import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type { Option } from "fp-ts/Option";
import type { NonEmptyString } from "io-ts-types";
import type { StepSnapshot } from "../Utils";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import type { NonEmptyArray } from "fp-ts/lib/NonEmptyArray";
import type { Either } from "fp-ts/lib/Either";
import * as Eq from "fp-ts/lib/Eq";
import { SectionHeading } from "@urbint/silica";
import * as A from "fp-ts/Array";
import * as O from "fp-ts/Option";
import * as M from "fp-ts/lib/Map";
import * as S from "fp-ts/lib/Set";
import * as E from "fp-ts/lib/Either";
import {
  constFalse,
  constVoid,
  constant,
  flow,
  pipe,
} from "fp-ts/lib/function";
import { Fragment, useCallback, useMemo } from "react";
import * as SG from "fp-ts/lib/Semigroup";
import { identity } from "io-ts";
import { Eq as EqString } from "fp-ts/lib/string";
import { isString } from "lodash-es";
import {
  activityIdCodec,
  eqActivitiesGroupId,
  eqCriticalRisk,
  eqLibraryTaskId,
  ordCriticalRisk,
  ordLibraryTaskId,
} from "@/api/codecs";
import { RiskLevel } from "@/api/generated/types";
import Link from "@/components/shared/link/Link";
import { noEffect } from "@/utils/reducerWithEffect";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import { DeleteActivityModal } from "@/container/activity/deleteActivityModal/DeleteActivityModal";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import { Checkbox } from "../Basic/Checkbox";
import { RiskToggleCard } from "../Basic/RiskToggleCard";
import { TaskCard } from "../Basic/TaskCard";
import StepLayout from "../StepLayout";
import {
  eqNonEmptyString,
  ordNonEmptyString,
  snapshotMap,
  taskRiskLevels,
} from "../Utils";
import * as AddActivityDialog from "./../AddActivity/Dialog";

export type Model = {
  selectedTaskIds: Set<LibraryTaskId>;
  criticalRiskAreas: Set<CriticalRisk>;
  formActivities: Map<NonEmptyString, LibraryTaskId[]>; // stand-alone activities independent of project location
  dialog: Option<AddActivityDialog.Model>;
  editActivity: O.Option<LibraryTask[]>;
  showDeleteActivityModel: Option<
    { id: ActivityId; libraryTaskIds: LibraryTaskId[] } | NonEmptyString
  >;
  deleteActivityGroup: boolean;
  errorsEnabled: boolean;
};

export type TaskErrors = "NO_TASK_SELECTED";

export const taskErrorTexts = (error: TaskErrors) => {
  switch (error) {
    case "NO_TASK_SELECTED": {
      return "At least one activity and task must be added to complete the Job Safety Briefing";
    }
  }
};

export const withSelectedTaskIds =
  (ids: Set<LibraryTaskId>) =>
  (model: Model): Model => ({
    ...model,
    selectedTaskIds: pipe(model.selectedTaskIds, S.union(eqLibraryTaskId)(ids)),
  });

export function makeSnapshot(model: Model): StepSnapshot {
  return {
    selectedTaskIds: pipe(model.selectedTaskIds, S.toArray(ordLibraryTaskId)),
    criticalRiskAreas: pipe(
      model.criticalRiskAreas,
      S.toArray(ordCriticalRisk)
    ),
    formActivities: snapshotMap(model.formActivities),
  };
}

export const toSaveJsbInput =
  (relevantActivities: Activity[], allLibraryTasks: LibraryTask[]) =>
  (model: Model): SaveJobSafetyBriefingInput => {
    // to make sure we don't save "hidden" tasks, that are not visible in the UI anymore (maybe due to a changed briefing date or some other filtering),
    // but are still selected in the model (e.g. from a previously saved selection)
    // we intersect the selected task ids with the task ids from the relevant activities that can come from 2 sources:
    // 1. activities from the project location
    // 2. activities from the saved stan-alone form activities (added if there is no project location for this JSB)

    const getTaskNameById = new Map(
      allLibraryTasks?.map(task => [task.id, task.name] as const)
    );

    // task ids from saved form activities
    const formActivitiesTaskIds = pipe(
      // combine all task ids from the formActivities Map
      // that contains multiple lists of task ids into a single Set
      model.formActivities,
      M.foldMap(ordNonEmptyString)(
        S.getUnionMonoid(eqLibraryTaskId) // defines how to combine Sets
      )(
        S.fromArray(eqLibraryTaskId) // defines how to map an array of task ids to a Set
      )
    );

    // task ids from activities from the project location
    const projectLocationActivitiesTaskIds = pipe(
      relevantActivities,
      A.chain(a => a.tasks),
      A.map(t => t.libraryTask.id),
      S.fromArray(eqLibraryTaskId)
    );

    const relevantTasksIds = pipe(
      formActivitiesTaskIds,
      S.union(eqLibraryTaskId)(projectLocationActivitiesTaskIds)
    );

    const activities = pipe(
      model.formActivities,
      M.toArray(ordNonEmptyString),
      A.map(([name, taskIds]) => ({
        name,
        tasks: taskIds.map(id => ({
          id,
          name: getTaskNameById.get(id) ?? "",
          fromWorkOrder: false,
          riskLevel: RiskLevel.Unknown,
        })),
      }))
    );

    const taskSelections = pipe(
      model.selectedTaskIds,
      S.intersection(eqLibraryTaskId)(relevantTasksIds),
      S.toArray(ordLibraryTaskId),
      A.map(taskId => ({
        id: taskId,
        name: getTaskNameById.get(taskId) ?? "",
        fromWorkOrder: false,
        riskLevel: RiskLevel.Unknown,
      }))
    );

    const recommendedTaskSelections = pipe(
      relevantTasksIds,
      S.toArray(ordLibraryTaskId),
      // Map each task ID to its selection object
      A.map(taskId => ({
        id: taskId,
        name: getTaskNameById.get(taskId) ?? "",
        fromWorkOrder: S.elem(eqLibraryTaskId)(taskId)(
          projectLocationActivitiesTaskIds
        ),
        riskLevel: RiskLevel.Unknown,
        // Set recommended to true only if the task is from project i.e if it has loaction ID
        recommended: S.elem(eqLibraryTaskId)(taskId)(
          projectLocationActivitiesTaskIds
        ),
        // Set selected based on whether the task ID is in selectedTaskIds
        selected: S.elem(eqLibraryTaskId)(taskId)(model.selectedTaskIds),
      }))
    );

    const criticalRiskAreaSelections = pipe(
      model.criticalRiskAreas,
      S.toArray(ordCriticalRisk),
      A.map(name => ({ name }))
    );

    return {
      taskSelections,
      recommendedTaskSelections,
      criticalRiskAreaSelections,
      activities,
    };
  };

export const init = (jsb: Option<Jsb>, activities: Activity[]): Model => {
  const r = {
    selectedTaskIds: pipe(
      jsb,
      O.chain(j => j.taskSelections),
      O.fold(
        () =>
          // if no selection was previously saved, preselect all tasks from the activities
          pipe(
            activities,
            A.chain(a => a.tasks),
            A.map(t => t.libraryTask.id),
            S.fromArray(eqLibraryTaskId)
          ),
        flow(
          A.map(x => x.id),
          S.fromArray(eqLibraryTaskId)
        )
      )
    ),
    criticalRiskAreas: pipe(
      jsb,
      O.chain(j => j.criticalRiskAreaSelections),
      O.fold(
        () => new Set<CriticalRisk>(),
        flow(
          A.map(x => x.name),
          S.fromArray(ordCriticalRisk)
        )
      )
    ),
    dialog: O.none,
    formActivities: pipe(
      jsb,
      O.chain(j => j.activities),
      O.fold(
        () => new Map<NonEmptyString, LibraryTaskId[]>(),
        acts =>
          pipe(
            acts,
            // map to a list of tuples with activity name and task ids
            A.map((a): [NonEmptyString, LibraryTaskId[]] => [
              a.name,
              a.tasks.map(t => t.id),
            ]),
            // init a Map from the list of tuples
            M.fromFoldable(
              eqNonEmptyString, // using this eq instance for key comparison
              A.getSemigroup<LibraryTaskId>(), // using this semigroup instance for combining task ids of duplicate keys
              A.Foldable // using the Foldable instance of Array (because we're passing in tuples inside an Array)
            )
          )
      )
    ),
    showDeleteActivityModel: O.none,
    deleteActivityGroup: false,
    editActivity: O.none,
    errorsEnabled: false,
  };

  return r;
};

export type EditActivityData = Either<AddActivityDialog.FormActivity, Activity>;

export type Action =
  | {
      type: "TaskToggled";
      taskId: LibraryTaskId;
    }
  | {
      type: "TasksSelected";
      taskIds: LibraryTaskId[];
    }
  | {
      type: "TasksCleared";
      taskIds: LibraryTaskId[];
    }
  | {
      type: "AddActivityOpened";
      locationId: Option<ProjectLocationId>;
    }
  | {
      type: "AddActivityClosed";
    }
  | {
      type: "CriticalRiskToggled";
      risk: CriticalRisk;
    }
  | {
      type: "AddActivityDialogAction";
      action: AddActivityDialog.Action;
    }
  | {
      type: "FormActivityAdded";
      activity: AddActivityDialog.FormActivity;
    }
  | {
      type: "DeleteActivityGroupAction";
      value: boolean;
      deleteActivity: (id: ActivityId) => void;
      isStandAloneJsb: boolean;
    }
  | {
      type: "EditActivityOpened";
      activityItem: LibraryTask[];
      locationId: Option<ProjectLocationId>;
      activityData: Option<EditActivityData>;
    }
  | {
      type: "ShowDeleteActivityGroupModalAction";
      value: O.Option<
        { id: ActivityId; libraryTaskIds: LibraryTaskId[] } | NonEmptyString
      >;
    };

export const TaskToggled = (taskId: LibraryTaskId): Action => ({
  type: "TaskToggled",
  taskId,
});

export const TasksSelected = (taskIds: LibraryTaskId[]): Action => ({
  type: "TasksSelected",
  taskIds,
});

export const TasksCleared = (taskIds: LibraryTaskId[]): Action => ({
  type: "TasksCleared",
  taskIds,
});

export const AddActivityOpened = (
  locationId: Option<ProjectLocationId>
): Action => ({
  type: "AddActivityOpened",
  locationId,
});

export const EditActivityOpened =
  (locationId: Option<ProjectLocationId>) =>
  (activityData: Option<EditActivityData>) =>
  (activityItem: LibraryTask[]): Action => ({
    type: "EditActivityOpened",
    activityItem,
    locationId,
    activityData,
  });

export const AddActivityClosed = (): Action => ({
  type: "AddActivityClosed",
});

export const CriticalRiskToggled = (risk: CriticalRisk): Action => ({
  type: "CriticalRiskToggled",
  risk,
});

export const AddActivityDialogAction = (
  action: AddActivityDialog.Action
): Action => ({
  type: "AddActivityDialogAction",
  action,
});

export const FormActivityAdded = (
  activity: AddActivityDialog.FormActivity
): Action => ({
  type: "FormActivityAdded",
  activity,
});

export const ShowDeleteActivityGroupModalAction = (
  value: O.Option<
    { id: ActivityId; libraryTaskIds: LibraryTaskId[] } | NonEmptyString
  >
): Action => ({
  type: "ShowDeleteActivityGroupModalAction",
  value,
});

export const DeleteActivityGroupAction =
  (isStandAloneJsb: boolean) =>
  (deleteActivity: (id: ActivityId) => void) =>
  (value: boolean): Action => ({
    type: "DeleteActivityGroupAction",
    value,
    deleteActivity,
    isStandAloneJsb,
  });

export const update = (
  model: Model,
  action: Action
): [Model, Effect<Action>] => {
  switch (action.type) {
    case "TaskToggled":
      return [
        {
          ...model,
          selectedTaskIds: S.toggle(eqLibraryTaskId)(action.taskId)(
            model.selectedTaskIds
          ),
        },
        noEffect,
      ];

    case "TasksSelected":
      return [
        {
          ...model,
          selectedTaskIds: pipe(
            action.taskIds,
            S.fromArray(eqLibraryTaskId),
            S.union(eqLibraryTaskId)(model.selectedTaskIds)
          ),
        },
        noEffect,
      ];

    case "TasksCleared":
      return [
        {
          ...model,
          selectedTaskIds: S.difference(eqLibraryTaskId)(
            S.fromArray(eqLibraryTaskId)(action.taskIds)
          )(model.selectedTaskIds),
        },
        noEffect,
      ];

    case "AddActivityOpened":
      if (O.isSome(action.locationId)) {
        return [
          {
            ...model,
            dialog: O.some(
              AddActivityDialog.init(action.locationId, O.none, O.none)
            ),
          },
          noEffect,
        ];
      }
      return [
        {
          ...model,
          dialog: O.some(
            AddActivityDialog.init(action.locationId, O.none, O.none)
          ),
          editActivity: O.none,
        },
        noEffect,
      ];
    case "EditActivityOpened":
      return [
        {
          ...model,
          dialog: O.some(
            AddActivityDialog.init(
              action.locationId,
              pipe(
                action.activityItem,
                A.chain(a =>
                  pipe(
                    a.activitiesGroups,
                    O.fold(
                      () => [],
                      aGr => pipe(aGr, identity)
                    )
                  )
                ),
                A.uniq(
                  Eq.contramap((act: ActivitiesGroup) => act.id)(EqString)
                ),
                A.map((actGr): [ActivitiesGroupId, Set<LibraryTaskId>] => [
                  actGr.id,
                  pipe(
                    actGr.tasks,
                    A.map(t => t.id),
                    A.intersection(eqLibraryTaskId)(
                      pipe(
                        action.activityItem,
                        A.map(a => a.id)
                      )
                    ),
                    S.fromArray(eqLibraryTaskId)
                  ),
                ]),
                M.fromFoldable(
                  eqActivitiesGroupId,
                  S.getUnionSemigroup(eqLibraryTaskId),
                  A.Foldable
                ),
                O.of
              ),
              action.activityData
            )
          ),
          editActivity: O.some(action.activityItem),
        },
        noEffect,
      ];

    case "AddActivityClosed":
      return [{ ...model, dialog: O.none }, noEffect];

    case "ShowDeleteActivityGroupModalAction":
      return [
        {
          ...model,
          showDeleteActivityModel: pipe(action.value),
          deleteActivityGroup: false,
        },
        noEffect,
      ];

    case "DeleteActivityGroupAction":
      pipe(
        model.showDeleteActivityModel,
        O.fold(
          () => constVoid,
          val =>
            isString(val)
              ? constVoid
              : pipe(
                  val.id,
                  activityIdCodec.decode,
                  E.fold(
                    () => constVoid,
                    id =>
                      action.isStandAloneJsb
                        ? constVoid
                        : action.deleteActivity(id)
                  )
                )
        )
      );

      return [
        {
          ...model,
          showDeleteActivityModel: O.none,
          deleteActivityGroup: false,
          formActivities: pipe(
            model.showDeleteActivityModel,
            O.fold(
              () => model.formActivities,
              val =>
                isString(val)
                  ? action.isStandAloneJsb
                    ? M.deleteAt(eqNonEmptyString)(val)(model.formActivities)
                    : model.formActivities
                  : model.formActivities
            )
          ),
          selectedTaskIds: pipe(
            model.showDeleteActivityModel,
            O.fold(
              () => model.selectedTaskIds,
              val =>
                isString(val)
                  ? pipe(
                      model.formActivities,
                      M.lookup(eqNonEmptyString)(val),
                      O.fold(
                        () => model.selectedTaskIds,
                        ids =>
                          S.difference(eqLibraryTaskId)(model.selectedTaskIds)(
                            S.fromArray(eqLibraryTaskId)(ids)
                          )
                      )
                    )
                  : S.difference(eqLibraryTaskId)(model.selectedTaskIds)(
                      S.fromArray(eqLibraryTaskId)(val.libraryTaskIds)
                    )
            )
          ),
        },
        noEffect,
      ];

    case "CriticalRiskToggled":
      return [
        {
          ...model,
          criticalRiskAreas: S.toggle(ordCriticalRisk)(action.risk)(
            model.criticalRiskAreas
          ),
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
    case "FormActivityAdded":
      const uniqueTaskIds = Array.from(new Set(action.activity.taskIds));
      const isEditing = O.isSome(model.editActivity);

      if (isEditing) {
        const existingTaskIds =
          model.formActivities.get(action.activity.name) || [];

        const updatedFormActivities = new Map(model.formActivities);
        updatedFormActivities.set(action.activity.name, uniqueTaskIds);

        const removedTaskIds = existingTaskIds.filter(
          taskId => !uniqueTaskIds.includes(taskId)
        );

        const addedTaskIds = uniqueTaskIds.filter(
          taskId => !existingTaskIds.includes(taskId)
        );

        const selectedTaskIds = new Set(model.selectedTaskIds);
        const removedTaskIdsSet = new Set(removedTaskIds);
        const addedTaskIdsSet = new Set(addedTaskIds);
        removedTaskIdsSet.forEach(taskId => selectedTaskIds.delete(taskId));
        addedTaskIdsSet.forEach(taskId => selectedTaskIds.add(taskId));
        const updatedSelectedTaskIds = selectedTaskIds;

        return [
          {
            ...model,
            formActivities: updatedFormActivities,
            selectedTaskIds: updatedSelectedTaskIds,
          },
          noEffect,
        ];
      } else {
        const existingTaskIds =
          model.formActivities.get(action.activity.name) || [];

        const combinedTaskIds = Array.from(
          new Set([...existingTaskIds, ...uniqueTaskIds])
        );

        return [
          {
            ...model,
            formActivities: pipe(
              model.formActivities,
              M.insertAt(eqNonEmptyString)(
                action.activity.name,
                combinedTaskIds
              )
            ),
            selectedTaskIds: pipe(
              combinedTaskIds,
              S.fromArray(eqLibraryTaskId),
              S.union(eqLibraryTaskId)(model.selectedTaskIds)
            ),
          },
          noEffect,
        ];
      }
  }
};

// type ActivityItem = {
//   // id: NonEmptyString;
//   name: NonEmptyString;
//   taskIds: LibraryTaskId[];
// };
// const eqActivityItemById = Eq.contramap((a: ActivityItem) => a.id)(
//   eqString
// );
// const ordActivityItemById = Ord.contramap((a: ActivityItem) => a.id)(
//   ordString
// );

export type Props = ChildProps<Model, Action> & {
  locationId: Option<ProjectLocationId>;
  tasks: LibraryTask[];
  activities: Activity[];
  isReadOnly: boolean;
  saveActivity: (
    a: CreateActivityInput,
    removalTasksData: {
      tasks: Option<LibraryTaskId[]>;
      activityId: Option<ActivityId>;
    },
    additionalTasksData: {
      tasks: Option<LibraryTaskId[]>;
      activityId: Option<ActivityId>;
    }
  ) => void;
  deleteActivity: (id: ActivityId) => void;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  const tasksLibrary = useMemo(
    () =>
      pipe(
        props.tasks,
        A.map((task): [LibraryTaskId, LibraryTask] => [task.id, task]),
        M.fromFoldable(eqLibraryTaskId, SG.first<LibraryTask>(), A.Foldable)
      ),
    [props.tasks]
  );

  const saveActivity = useCallback(
    (input: AddActivityDialog.SaveActivityInput) => {
      switch (input.type) {
        case "ProjectActivity":
          return props.saveActivity(
            input.input,
            input.removalTasksData,
            input.additionalTasksData
          );
        case "FormActivity":
          return pipe(input.activity, FormActivityAdded, dispatch);
      }
    },
    [props, dispatch]
  );

  const riskLevels = useMemo(
    () => taskRiskLevels(props.activities, tasksLibrary),
    [props.activities, tasksLibrary]
  );

  const activityTasks: Map<NonEmptyString, LibraryTask[]> = useMemo(
    () =>
      pipe(
        props.activities,
        A.filter(activity => activity.tasks.length > 0),
        A.map((activity): [NonEmptyString, LibraryTaskId[]] => [
          activity.name,
          activity.tasks.map(t => t.libraryTask.id),
        ]),
        M.fromFoldable(
          eqNonEmptyString,
          A.getSemigroup<LibraryTaskId>(),
          A.Foldable
        ),
        M.union(
          eqNonEmptyString,
          A.getUnionMonoid<LibraryTaskId>(eqLibraryTaskId)
        )(model.formActivities),
        M.map(A.filterMap(tid => M.lookup(eqLibraryTaskId)(tid)(tasksLibrary)))
      ),
    [model.formActivities, props.activities, tasksLibrary]
  );

  // const lookupActivity = useCallback(
  //   (id: ActivityId) =>
  //     pipe(
  //       props.activities,
  //       A.findFirst(a => a.id === id)
  //     ),
  //   [props.activities]
  // );

  const allTasksSelected = useCallback(
    (activityName: NonEmptyString) =>
      pipe(
        activityTasks,
        M.lookup(eqNonEmptyString)(activityName),
        O.fold(
          constFalse,
          A.every(t => S.elem(eqLibraryTaskId)(t.id)(model.selectedTaskIds))
        )
      ),
    [activityTasks, model.selectedTaskIds]
  );

  // const isActivitySelected = useCallback(
  //   (activityName: NonEmptyString) =>
  //     pipe(
  //       // lookupActivity(id),

  //       O.map(allTasksSelected),
  //       O.getOrElse(() => false)
  //     ),
  //   [lookupActivity, allTasksSelected]
  // );

  const toggleActivity = useCallback(
    (activityName: NonEmptyString) =>
      pipe(
        activityTasks,
        M.lookup(eqNonEmptyString)(activityName),
        O.fold((): LibraryTaskId[] => [], flow(A.map(t => t.id))),
        allTasksSelected(activityName) ? TasksCleared : TasksSelected,
        dispatch
      ),
    [activityTasks, allTasksSelected, dispatch]
  );

  const taskRiskLevel = useCallback(
    (tid: LibraryTaskId) => {
      return pipe(
        M.lookup(eqLibraryTaskId)(tid)(riskLevels),
        O.getOrElse(() =>
          pipe(
            M.lookup(eqLibraryTaskId)(tid)(tasksLibrary),
            O.fold(
              () => RiskLevel.Unknown,
              task => task.riskLevel
            )
          )
        )
      );
    },
    [riskLevels, tasksLibrary]
  );

  const riskCard = useCallback(
    (risk: CriticalRisk) => (
      <RiskToggleCard
        risk={risk}
        checked={S.elem(eqCriticalRisk)(risk)(model.criticalRiskAreas)}
        disabled={isReadOnly}
        onClick={flow(constant(risk), CriticalRiskToggled, dispatch)}
      />
    ),
    [model.criticalRiskAreas, dispatch, isReadOnly]
  );

  const getMenuOptions = (
    activity: LibraryTask[],
    activityData: Option<EditActivityData>
  ): MenuItemProps[][] => {
    return [
      [
        {
          icon: "edit",
          label: `Edit`,
          onClick: () =>
            pipe(
              activity,
              flow(EditActivityOpened(props.locationId)(activityData), dispatch)
            ),
        },
      ],
      [
        {
          icon: "trash_empty",
          label: `Delete`,
          onClick: () =>
            pipe(
              activityData,
              O.fold(
                // eslint-disable-next-line @typescript-eslint/no-empty-function
                () => {},
                a =>
                  pipe(
                    a,
                    E.fold(
                      act =>
                        pipe(
                          act.name,
                          O.of,
                          ShowDeleteActivityGroupModalAction,
                          dispatch
                        ),
                      at =>
                        pipe(
                          {
                            id: at.id,
                            libraryTaskIds: at.tasks.map(t => t.libraryTask.id),
                          },
                          O.of,
                          ShowDeleteActivityGroupModalAction,
                          dispatch
                        )
                    )
                  )
              )
            ),
        },
      ],
    ];
  };

  return (
    <>
      <StepLayout>
        <div className="flex flex-row justify-between px-4 md:px-0">
          <SectionHeading className="text-xl font-semibold">
            Tasks Selection
          </SectionHeading>
          {isReadOnly ? (
            <></>
          ) : (
            <ButtonSecondary
              onClick={flow(
                constant(props.locationId),
                AddActivityOpened,
                dispatch
              )}
              label="Add Activity"
              iconStart="plus_circle_outline"
            />
          )}
        </div>
        {M.toArray(ordNonEmptyString)(activityTasks).map(
          ([activityName, a]) => (
            <div
              key={activityName}
              className="flex flex-col gap-5 px-4 md:px-0"
            >
              <div className="flex flex-1 justify-between align-middle">
                <Checkbox
                  className="w-full gap-4"
                  checked={allTasksSelected(activityName)}
                  disabled={isReadOnly}
                  onClick={() => toggleActivity(activityName)}
                >
                  {activityName}
                </Checkbox>
                <Dropdown
                  menuItems={getMenuOptions(
                    a,
                    pipe(
                      props.activities,
                      A.findFirst(act => act.name === activityName),
                      O.map(E.right),
                      O.alt(() =>
                        pipe(
                          model.formActivities,
                          M.lookup(eqNonEmptyString)(activityName),
                          O.map(taskIds =>
                            E.left({
                              name: activityName,
                              taskIds: taskIds as NonEmptyArray<LibraryTaskId>,
                            })
                          )
                        )
                      )
                    )
                  )}
                >
                  <ButtonIcon
                    disabled={isReadOnly}
                    iconName="more_horizontal"
                  />
                </Dropdown>
              </div>
              {pipe(
                M.lookup(eqNonEmptyString)(activityName)(activityTasks),
                O.fold(
                  () => [<></>],
                  A.map(task => (
                    <Fragment key={task.id}>
                      <Checkbox
                        className="w-full gap-4"
                        labelClassName="w-full"
                        checked={S.elem(eqLibraryTaskId)(task.id)(
                          model.selectedTaskIds
                        )}
                        disabled={isReadOnly}
                        onClick={flow(constant(task.id), TaskToggled, dispatch)}
                      >
                        <TaskCard
                          title={task.name}
                          risk={pipe(
                            props.locationId,
                            O.fold(
                              () => taskRiskLevel(task.id),
                              _ => task.riskLevel
                            )
                          )}
                        />
                      </Checkbox>
                    </Fragment>
                  ))
                )
              )}
            </div>
          )
        )}
        {S.isEmpty(model.selectedTaskIds) && (
          <div className="mt-4">
            <p className="font-semibold text-md">
              You currently have no Activities
            </p>
            <p className="text-sm">
              Please click the button above to select the Activities you will be
              working on today
            </p>
          </div>
        )}
        {model.errorsEnabled && S.isEmpty(model.selectedTaskIds) && (
          <div className="font-semibold text-system-error-40 text-sm mt-4">
            {taskErrorTexts("NO_TASK_SELECTED")}
          </div>
        )}
        <div className=" px-4 md:px-0">
          <SectionHeading className="text-xl font-semibold mb-6">
            Critical Risk Areas
          </SectionHeading>

          <Link
            className="mb-5"
            label="View Critical Risk Area documentation"
            iconLeft="external_link"
            href="https://soco365.sharepoint.com/:w:/s/TRNCorpSafetySubCom/safetyandhealthmanagementsystem/EeBBxGGb0tRJuVmpfj-lvmwBAZcLee5be537p2_Vd3QP1w?e=Kx4KI9"
            target="_blank"
          />

          <div className="grid grid-cols-2 gap-4">
            {riskCard("ArcFlash")}
            {riskCard("HoistedLoads")}
            {riskCard("FallOrFallArrest")}
            {riskCard("LineOfFire")}
            {riskCard("ExposureToEnergy")}
            {riskCard("CollisionLossOfControl")}
            {riskCard("ConfinedSpace")}
            {riskCard("MobileEquipment")}
            {riskCard("FireOrExplosion")}
            {riskCard("TrenchingOrExcavation")}
          </div>
        </div>
      </StepLayout>

      {O.isSome(model.dialog) && (
        <AddActivityDialog.View
          model={model.dialog.value}
          dispatch={flow(AddActivityDialogAction, dispatch)}
          tasks={props.tasks}
          onClose={flow(AddActivityClosed, dispatch)}
          saveActivity={saveActivity}
        />
      )}

      {O.isSome(model.showDeleteActivityModel) && (
        <DeleteActivityModal
          activityId={
            isString(model.showDeleteActivityModel.value)
              ? model.showDeleteActivityModel.value
              : model.showDeleteActivityModel.value.id
          }
          onModalClose={() =>
            pipe(O.none, flow(ShowDeleteActivityGroupModalAction, dispatch))
          }
          onConfirm={O.some(() =>
            pipe(
              true,
              DeleteActivityGroupAction(O.isNone(props.locationId))(
                props.deleteActivity
              ),
              dispatch
            )
          )}
        />
      )}
    </>
  );
}
