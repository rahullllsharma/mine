import type { LibraryTask } from "@/api/codecs";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { SelectedDuplicateActivities } from "../HighEnergyTasks";
import { useCallback } from "react";
import { flow, pipe } from "fp-ts/lib/function";
import { Lens } from "monocle-ts";
import { SectionHeading } from "@urbint/silica";
import * as E from "fp-ts/lib/Either";
import * as M from "fp-ts/lib/Map";
import { updateChildModel } from "@/utils/reducerWithEffect";
import * as SelectTasks from "@/components/forms/Ebo/AddActivity/SelectTasks";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { Dialog } from "../../Basic/Dialog";

export type Model = {
  selectTasks: SelectTasks.Model;
};

export const init = (
  selectedTasksInSection: SelectTasks.SelectedActivities,
  allSelectedActivities: SelectedDuplicateActivities
): Model => ({
  selectTasks: SelectTasks.init(selectedTasksInSection, allSelectedActivities),
});

export type Action =
  | { type: "SelectTasksAction"; action: SelectTasks.Action }
  | { type: "FormError"; error: string };

export const SelectTasksAction = (action: SelectTasks.Action): Action => ({
  type: "SelectTasksAction",
  action,
});

export const FormError = (error: string): Action => ({
  type: "FormError",
  error,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "SelectTasksAction":
      return updateChildModel(
        Lens.fromProp<Model>()("selectTasks"),
        SelectTasks.update
      )(model, action.action);
    case "FormError":
      return model;
  }
};

export type Props = ChildProps<Model, Action> & {
  tasks: LibraryTask[];
  onSubmit: (a: SelectTasks.SelectedActivities) => void;
  onClose: () => void;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, tasks } = props;

  const handleSubmit = useCallback(() => {
    return pipe(
      SelectTasks.result(model.selectTasks),
      E.fold(flow(FormError, dispatch), a =>
        pipe(a, props.onSubmit, props.onClose)
      )
    );
    // props.onSubmit(model.selectTasks.selectedTaskIds);
  }, [dispatch, model.selectTasks, props.onClose, props.onSubmit]);

  return (
    <Dialog
      size="medium"
      header={<DialogHeader onClose={props.onClose} />}
      footer={
        <DialogFooter
          cancelLabel="Cancel"
          submitLabel="Submit"
          onClose={props.onClose}
          onSubmit={handleSubmit}
          disabledPrimaryButton={M.isEmpty(
            model.selectTasks.selectedActivities
          )}
        />
      }
    >
      <SelectTasks.View
        model={model.selectTasks}
        dispatch={flow(SelectTasksAction, dispatch)}
        tasks={tasks}
      />
    </Dialog>
  );
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
  cancelLabel: string;
  submitLabel: string;
  onClose: () => void;
  onSubmit: () => void;
  disabledPrimaryButton?: boolean;
};

const DialogFooter = ({
  cancelLabel,
  submitLabel,
  onClose,
  onSubmit,
  disabledPrimaryButton = false,
}: FooterProps): JSX.Element => (
  <div className="flex flex-row justify-end gap-2">
    <ButtonSecondary label={cancelLabel} onClick={onClose} />
    <ButtonPrimary
      label={submitLabel}
      onClick={onSubmit}
      disabled={disabledPrimaryButton}
    />
  </div>
);
