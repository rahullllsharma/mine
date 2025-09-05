import type {
  MultiStepFormActions,
  MultiStepFormState,
  MultiStepFormStateItem,
} from "../state/reducer";
import type { Dispatch } from "react";
import type { NavigationStatus } from "@/components/navigation/Navigation";
import { useFormContext } from "react-hook-form";
import { noop } from "lodash-es";
import { useMultiStepFormContext } from "../context/MultiStepFormContext";

const useSafeDispatchMove = (dispatch: Dispatch<MultiStepFormActions>) => {
  const methods = useFormContext();

  if (!methods) {
    return (formActions: MultiStepFormActions) => dispatch(formActions);
  }

  const {
    formState: { isDirty, isSubmitted },
  } = methods;

  const canMoveWithoutConfirmation = !isDirty || isSubmitted;

  if (canMoveWithoutConfirmation) {
    return (formActions: MultiStepFormActions) => dispatch(formActions);
  }

  return (formActions: MultiStepFormActions) =>
    confirm("Discard unsaved changes?") ? dispatch(formActions) : noop();
};

type UseMultiStepActions = {
  moveTo: (section: string) => void;
  moveForward: () => void;
  moveBack: () => void;
  moveForwardAndComplete: () => void;
  markCurrentAs: (status: NavigationStatus) => void;
  markSectionsAs: (status: NavigationStatus, sections: string[]) => void;
};

type UseMultiStepState = {
  steps: MultiStepFormState;
  current: MultiStepFormStateItem;
  areAllStepsCompleted: boolean;
};

export const useMultiStepActions = (): UseMultiStepActions => {
  const [state, dispatch] = useMultiStepFormContext();
  const dispatchMove = useSafeDispatchMove(dispatch);

  return {
    moveTo: (section: string) =>
      dispatchMove({
        type: "JUMP_TO",
        value: section,
      }),
    moveForward: () =>
      dispatchMove({
        type: "NEXT",
      }),
    moveBack: () =>
      dispatchMove({
        type: "BACK",
      }),
    moveForwardAndComplete: () =>
      dispatchMove({
        type: "MOVE_FORWARD_AND_COMPLETE",
      }),
    markCurrentAs: (status: NavigationStatus) =>
      dispatch({
        type: "CHANGE_SECTIONS_STATUS",
        value: {
          status,
          sections: [
            (state.find(step => step.isSelected) as MultiStepFormStateItem).id,
          ],
        },
      }),
    markSectionsAs: (status: NavigationStatus, sections: string[]) =>
      dispatch({
        type: "CHANGE_SECTIONS_STATUS",
        value: { status, sections },
      }),
  };
};

export const useMultiStepState = (): UseMultiStepState => {
  const [state] = useMultiStepFormContext();
  return {
    steps: state,
    current: state.find(step => step.isSelected) as MultiStepFormStateItem,
    areAllStepsCompleted: state.every(step => step.status === "completed"),
  };
};
