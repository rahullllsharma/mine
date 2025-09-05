import type { ChildProps } from "@/utils/reducerWithEffect";
import type {
  ActivitiesGroupId,
  ActivityId,
  LibraryTask,
  LibraryTaskId,
  ProjectLocationId,
} from "@/api/codecs";
import type { NonEmptyArray } from "fp-ts/lib/NonEmptyArray";
import type { Option } from "fp-ts/lib/Option";
import type * as t from "io-ts";
import type { NonEmptyString } from "io-ts-types";
import type { EditActivityData } from "../Jsb/Tasks";
import type { CreateActivityInput } from "@/api/generated/types";
import { SectionHeading } from "@urbint/silica";
import { flow, identity, pipe } from "fp-ts/lib/function";
import { Lens } from "monocle-ts";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import { useCallback, useMemo } from "react";
import { sequenceS } from "fp-ts/lib/Apply";
import * as S from "fp-ts/lib/Set";
import * as O from "fp-ts/lib/Option";
import * as M from "fp-ts/lib/Map";
import * as SG from "fp-ts/lib/Semigroup";
import {
  eqActivitiesGroupId,
  eqLibraryTaskId,
  ordActivitiesGroupId,
  ordLibraryTaskId,
} from "@/api/codecs";
import { updateChildModel } from "@/utils/reducerWithEffect";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { showValidationError } from "@/utils/validation";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonIcon from "../../shared/button/icon/ButtonIcon";
import { Dialog } from "../Basic/Dialog";
import * as SelectTasks from "./SelectTasks";
import * as ConfigureActivity from "./ConfigureActivity";
import * as NameActivity from "./NameActivity";
import { DateTime } from "luxon";
// type for the stand-alone activity saved to the form instead of a project
export type FormActivity = {
  name: NonEmptyString;
  taskIds: NonEmptyArray<LibraryTaskId>;
};

export type SaveActivityInput =
  | {
      type: "ProjectActivity";
      input: CreateActivityInput;
      removalTasksData: {
        tasks: Option<LibraryTaskId[]>;
        activityId: Option<ActivityId>;
      };
      additionalTasksData: {
        tasks: Option<LibraryTaskId[]>;
        activityId: Option<ActivityId>;
      };
    }
  | {
      type: "FormActivity";
      activity: FormActivity;
    };

export const ProjectActivity =
  (activityId: Option<ActivityId>) =>
  (additionalTasks: Option<LibraryTaskId[]>) =>
  (removalTasks: Option<LibraryTaskId[]>) =>
  (input: CreateActivityInput): SaveActivityInput => ({
    type: "ProjectActivity",
    input,
    removalTasksData: {
      tasks: removalTasks,
      activityId,
    },
    additionalTasksData: {
      tasks: additionalTasks,
      activityId,
    },
  });

export const FormActivity = (activity: FormActivity): SaveActivityInput => ({
  type: "FormActivity",
  activity,
});

type ActivityForm =
  | {
      type: "NameActivity";
      model: NameActivity.Model;
    }
  | {
      type: "ConfigureActivity";
      locationId: ProjectLocationId;
      model: ConfigureActivity.Model;
    };

const activityFormWithName =
  (name: string) =>
  (form: ActivityForm): ActivityForm => {
    switch (form.type) {
      case "NameActivity":
        return {
          ...form,
          model: {
            ...form.model,
            name: NameActivity.formDefinition.name.init(name),
          },
        };
      case "ConfigureActivity":
        return {
          ...form,
          model: {
            ...form.model,
            name: ConfigureActivity.formDefinition.name.init(name),
          },
        };
    }
  };

export type Model = {
  selectTasks: SelectTasks.Model;
  activityForm: ActivityForm;
  step: "selectTasks" | "activityForm";
  isEdit: boolean;
  initialTasks: Option<Map<ActivitiesGroupId, Set<LibraryTaskId>>>;
  activityId: Option<ActivityId>;
  hasChanges: boolean; // Flag to track changes in selectTasks
};

const toCreateActivityInput =
  (tasksLibrary: LibraryTask[]) =>
  (locationId: ProjectLocationId, model: ConfigureActivity.Model) =>
  (selectedTaskIds: Set<LibraryTaskId>): t.Validation<CreateActivityInput> => {
    const r = sequenceS(E.Apply)({
      name: model.name.val,
      startDate: pipe(
        model.startDate.val,
        E.map(d => d.toISODate())
      ),
      endDate: pipe(
        model.endDate.val,
        E.map(d => d.toISODate())
      ),
      locationId: E.right(locationId),
      status: E.right(model.status),
      tasks: pipe(
        tasksLibrary,
        A.filter(
          task => S.elem(eqLibraryTaskId)(task.id)(selectedTaskIds) // check if the task is in the set
        ),
        A.map(task => ({
          libraryTaskId: task.id,
          hazards: pipe(
            task.hazards,
            A.map(h => ({
              libraryHazardId: h.id,
              isApplicable: true,
              controls: pipe(
                h.controls,
                A.map(c => ({
                  libraryControlId: c.id,
                  isApplicable: true,
                }))
              ),
            }))
          ),
        })),
        E.right
      ),
    });

    return r;
  };

export const init = (
  locationId: Option<ProjectLocationId>,
  selectedTasks: Option<Map<ActivitiesGroupId, Set<LibraryTaskId>>>,
  initActivityData: Option<EditActivityData>
): Model => {
  return {
    selectTasks: SelectTasks.init(
      pipe(
        selectedTasks,
        O.fold(
          () => new Map<ActivitiesGroupId, Set<LibraryTaskId>>(),
          sT => sT
        )
      )
    ),
    activityForm: pipe(
      locationId,
      O.fold(
        (): ActivityForm => ({
          type: "NameActivity",
          model: NameActivity.init(
            pipe(
              initActivityData,
              O.fold(
                () => "",
                dt =>
                  pipe(
                    dt,
                    E.fold(
                      at => at.name,
                      () => ""
                    )
                  )
              )
            )
          ),
        }),
        (lid): ActivityForm => ({
          type: "ConfigureActivity",
          locationId: lid,
          model: ConfigureActivity.init(
            pipe(
              initActivityData,
              O.fold(
                () => ({
                  startDate: DateTime.now().toISODate(),
                  endDate: DateTime.now().toISODate(),
                }),
                a =>
                  pipe(
                    a,
                    E.fold(
                      () => ({}),
                      act => ({
                        name: act.name,
                        startDate: pipe(
                          act.startDate,
                          O.fold(
                            () => DateTime.now().toISODate(),
                            d =>
                              pipe(
                                d.toISODate(),
                                O.fromNullable,
                                O.fold(
                                  () => DateTime.now().toISODate(),
                                  identity
                                )
                              )
                          )
                        ),
                        endDate: pipe(
                          act.endDate,
                          O.fold(
                            () => DateTime.now().toISODate(),
                            d =>
                              pipe(
                                d.toISODate(),
                                O.fromNullable,
                                O.fold(
                                  () => DateTime.now().toISODate(),
                                  identity
                                )
                              )
                          )
                        ),
                        status: act.status,
                      })
                    )
                  )
              )
            )
          ),
        })
      )
    ),
    step: "selectTasks",
    isEdit: pipe(selectedTasks, O.isSome),
    initialTasks: selectedTasks,
    activityId: pipe(
      initActivityData,
      O.fold(
        () => O.none,
        dt =>
          pipe(
            dt,
            E.fold(
              () => O.none,
              a => pipe(a.id, O.fromNullable)
            )
          )
      )
    ),
    hasChanges: false, // Initialize hasChanges to false
  };
};

export type Action =
  | {
      type: "TasksSelected";
      name: string;
      taskIds: NonEmptyArray<LibraryTaskId>;
    }
  | {
      type: "NavigatedBack";
    }
  | {
      type: "SelectTasksAction";
      action: SelectTasks.Action;
    }
  | {
      type: "ConfigureActivityAction";
      action: ConfigureActivity.Action;
    }
  | {
      type: "NameActivityAction";
      action: NameActivity.Action;
    }
  | {
      type: "FormError";
      error: string;
    };

export const TasksSelected =
  (name: string) =>
  (taskIds: NonEmptyArray<LibraryTaskId>): Action => ({
    type: "TasksSelected",
    name,
    taskIds,
  });

export const NavigatedBack = (): Action => ({
  type: "NavigatedBack",
});

export const SelectTasksAction = (action: SelectTasks.Action): Action => ({
  type: "SelectTasksAction",
  action,
});

export const ConfigureActivityAction = (
  action: ConfigureActivity.Action
): Action => ({
  type: "ConfigureActivityAction",
  action,
});

export const NameActivityAction = (action: NameActivity.Action): Action => ({
  type: "NameActivityAction",
  action,
});

export const FormError = (error: string): Action => ({
  type: "FormError",
  error,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "TasksSelected": {
      return model.step === "selectTasks"
        ? {
            ...model,
            step: "activityForm",
            activityForm: pipe(
              model.activityForm,
              activityFormWithName(action.name)
            ),
          }
        : model;
    }
    case "NavigatedBack":
      return model.step === "activityForm"
        ? {
            ...model,
            step: "selectTasks",
          }
        : model;

    case "FormError": {
      switch (model.step) {
        case "selectTasks":
          return model;
        case "activityForm":
          return model.activityForm.type === "ConfigureActivity"
            ? {
                ...model,
                activityForm: {
                  ...model.activityForm,
                  model: ConfigureActivity.withDirtyForm(
                    model.activityForm.model
                  ),
                },
              }
            : {
                ...model,
                activityForm: {
                  ...model.activityForm,
                  model: NameActivity.withDirtyForm(model.activityForm.model),
                },
              };
      }
    }

    case "SelectTasksAction": {
      return {
        ...model,
        ...updateChildModel(
          Lens.fromProp<Model>()("selectTasks"),
          SelectTasks.update
        )(model, action.action),
        hasChanges: true, // Set hasChanges to true when SelectTasksAction is triggered
      };
    }

    case "ConfigureActivityAction": {
      return model.activityForm.type === "ConfigureActivity"
        ? {
            ...model,
            activityForm: {
              ...model.activityForm,
              model: ConfigureActivity.update(
                model.activityForm.model,
                action.action
              ),
            },
          }
        : model;
    }

    case "NameActivityAction": {
      return model.activityForm.type === "NameActivity"
        ? {
            ...model,
            activityForm: {
              ...model.activityForm,
              model: NameActivity.update(
                model.activityForm.model,
                action.action
              ),
            },
          }
        : model;
    }
  }
};

export type Props = ChildProps<Model, Action> & {
  tasks: LibraryTask[];
  saveActivity: (a: SaveActivityInput) => void;
  onClose: () => void;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch } = props;

  // for group name lookup
  // a similar structure is also used in SelectTasks.tsx
  // maybe if it's worth extracting to a common place
  // but the performance hit is insignificant
  const groupNamesMap = useMemo(
    () =>
      pipe(
        props.tasks,
        A.chain(task =>
          pipe(
            task.activitiesGroups,
            O.fold(() => [], identity)
          )
        ),
        A.map((m): [ActivitiesGroupId, NonEmptyString] => [m.id, m.name]),
        M.fromFoldable(
          eqActivitiesGroupId,
          SG.first<NonEmptyString>(),
          A.Foldable
        )
      ),
    [props.tasks]
  );

  const onBack: () => void =
    model.step === "activityForm"
      ? flow(NavigatedBack, dispatch)
      : props.onClose;

  const completeStep = useCallback(() => {
    const selectedActivityGroupNames = pipe(
      model.selectTasks.selectedTaskIds,
      M.keys(ordActivitiesGroupId),
      A.filterMap(groupId =>
        M.lookup(eqActivitiesGroupId)(groupId)(groupNamesMap)
      )
    );

    const saveActivityFn = () => {
      const removalTasks = pipe(
        model.initialTasks,
        O.fold(
          () => O.none,
          initialTasks =>
            pipe(
              initialTasks,
              M.mapWithIndex((groupId, tasks) =>
                pipe(
                  tasks,
                  S.difference(eqLibraryTaskId)(
                    pipe(
                      model.selectTasks.selectedTaskIds,
                      M.lookup(eqActivitiesGroupId)(groupId),
                      O.fold(() => S.empty, identity)
                    )
                  ),
                  S.toArray(ordLibraryTaskId),
                  A.map(taskId => taskId)
                )
              ),
              M.toArray(ordActivitiesGroupId),
              A.map(([_, taskIds]) => taskIds),
              A.flatten,
              O.fromPredicate(A.isNonEmpty)
            )
        )
      );

      const additionalTasks = pipe(
        model.initialTasks,
        O.fold(
          () => O.none,
          initialTasks =>
            pipe(
              model.selectTasks.selectedTaskIds,
              M.mapWithIndex((groupId, tasks) =>
                pipe(
                  tasks,
                  S.difference(eqLibraryTaskId)(
                    pipe(
                      initialTasks,
                      M.lookup(eqActivitiesGroupId)(groupId),
                      O.fold(() => S.empty, identity)
                    )
                  ),
                  S.toArray(ordLibraryTaskId),
                  A.map(taskId => taskId)
                )
              ),
              M.toArray(ordActivitiesGroupId),
              A.map(([_, taskIds]) => taskIds),
              A.flatten,
              O.fromPredicate(A.isNonEmpty)
            )
        )
      );

      if (
        O.isSome(removalTasks) &&
        O.isSome(additionalTasks) &&
        model.activityForm.type === "ConfigureActivity"
      ) {
        const input1 = pipe(
          SelectTasks.result(model.selectTasks), // get and validate task selection
          E.chain(
            flow(
              S.fromArray(eqLibraryTaskId), // convert task ids list to set
              toCreateActivityInput(props.tasks)(
                // validate activity form
                model.activityForm.locationId,
                model.activityForm.model
              ),
              E.mapLeft(showValidationError) // convert validation error to string
            )
          ),
          E.map(pipe(removalTasks, ProjectActivity(model.activityId)(O.none)))
        );
        const input2 = pipe(
          SelectTasks.result(model.selectTasks), // get and validate task selection
          E.chain(
            flow(
              S.fromArray(eqLibraryTaskId), // convert task ids list to set
              toCreateActivityInput(props.tasks)(
                // validate activity form
                model.activityForm.locationId,
                model.activityForm.model
              ),
              E.mapLeft(showValidationError) // convert validation error to string
            )
          ),
          E.map(
            pipe(O.none, ProjectActivity(model.activityId)(additionalTasks))
          )
        );

        pipe(
          input1,
          E.fold(flow(FormError, dispatch), a => pipe(a, props.saveActivity))
        );

        return pipe(
          input2,
          E.fold(flow(FormError, dispatch), a =>
            pipe(a, props.saveActivity, props.onClose)
          )
        );
      }

      // input type depends on whether we have a locationId (locationId indicates whether we have a project or not)
      // if we do, we're creating an input for adding an activity to a project
      // if we don't, we're creating an input for adding an activity to a form
      const input =
        model.activityForm.type === "ConfigureActivity"
          ? pipe(
              SelectTasks.result(model.selectTasks), // get and validate task selection
              E.chain(
                flow(
                  S.fromArray(eqLibraryTaskId), // convert task ids list to set
                  toCreateActivityInput(props.tasks)(
                    // validate activity form
                    model.activityForm.locationId,
                    model.activityForm.model
                  ),
                  E.mapLeft(showValidationError) // convert validation error to string
                )
              ),
              E.map(
                pipe(
                  removalTasks,
                  ProjectActivity(model.activityId)(additionalTasks)
                )
              )
            )
          : pipe(
              sequenceS(E.Apply)({
                name: pipe(
                  model.activityForm.model.name.val,
                  E.mapLeft(showValidationError)
                ),
                taskIds: SelectTasks.result(model.selectTasks),
              }),
              E.map(FormActivity)
            );

      return pipe(
        input,
        E.fold(flow(FormError, dispatch), a =>
          pipe(a, props.saveActivity, props.onClose)
        )
      );
    };

    switch (model.step) {
      case "selectTasks":
        if (model.isEdit) {
          return saveActivityFn();
        }

        return pipe(
          SelectTasks.result(model.selectTasks),
          E.fold(
            flow(FormError, dispatch),
            flow(
              TasksSelected(selectedActivityGroupNames.join(" + ")),
              dispatch
            )
          )
        );
      case "activityForm": {
        return saveActivityFn();
      }
    }
  }, [model, props, dispatch]);

  const nextButtonLabel =
    model.step === "activityForm"
      ? "Add Activity"
      : model.isEdit
      ? "Save Activity"
      : "Next";

  return (
    <Dialog
      size="medium"
      header={<DialogHeader onClose={props.onClose} />}
      footer={
        <DialogFooter
          nextLabel={nextButtonLabel}
          backLabel={model.step === "activityForm" ? "Back" : "Cancel"}
          onNext={completeStep}
          onBack={onBack}
          disabled={!model.hasChanges} // Disable the button when no changes
        />
      }
    >
      <StepView {...props} />
    </Dialog>
  );
}

function StepView(props: Props): JSX.Element {
  const { model, dispatch, tasks } = props;

  switch (model.step) {
    case "selectTasks":
      return (
        <SelectTasks.View
          model={model.selectTasks}
          dispatch={flow(SelectTasksAction, dispatch)}
          tasks={tasks}
        />
      );

    case "activityForm":
      return model.activityForm.type === "ConfigureActivity" ? (
        <ConfigureActivity.View
          model={model.activityForm.model}
          dispatch={flow(ConfigureActivityAction, dispatch)}
        />
      ) : (
        <NameActivity.View
          model={model.activityForm.model}
          dispatch={flow(NameActivityAction, dispatch)}
        />
      );
  }
}

type HeaderProps = {
  onClose: () => void;
};
const DialogHeader = ({ onClose }: HeaderProps): JSX.Element => (
  <div className="flex flex-row justify-between">
    <SectionHeading className="text-xl font-semibold">
      Add an Activity
    </SectionHeading>
    <ButtonIcon iconName="close_big" onClick={onClose} />
  </div>
);

type FooterProps = {
  nextLabel: string;
  backLabel: string;
  onNext: () => void;
  onBack: () => void;
  disabled: boolean;
};
const DialogFooter = ({
  nextLabel,
  backLabel,
  onNext,
  onBack,
  disabled,
}: FooterProps): JSX.Element => (
  <div className="flex flex-row justify-end gap-2">
    <ButtonSecondary label={backLabel} onClick={onBack} />
    <ButtonPrimary label={nextLabel} disabled={disabled} onClick={onNext} />
  </div>
);
