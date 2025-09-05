import type { NavigationStatus } from "@/components/navigation/Navigation";

export type MultiStepFormStep<T = Record<string, unknown>> = T & {
  id: string;
  path: string;
  name: string;
  isSelected?: boolean;
  status?: NavigationStatus;
  // FIXME: Infer type from component props or passing a generic...
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Component: (props: any) => JSX.Element;
};

export type MultiStepFormStateItem = Required<MultiStepFormStep>;

export type MultiStepFormState = MultiStepFormStateItem[];

export type MultiStepFormActions =
  | { type: "MOVE_FORWARD_AND_COMPLETE" }
  | { type: "CHANGE_ACTIVE_STATUS"; value: NavigationStatus }
  | {
      type: "CHANGE_SECTIONS_STATUS";
      value: { status: NavigationStatus; sections: string[] };
    }
  | { type: "JUMP_TO"; value: string }
  | { type: "NEXT" }
  | { type: "BACK" };

type MultiStepFormReducer = (
  state: MultiStepFormState,
  action: MultiStepFormActions
) => MultiStepFormState;

const multiStepFormReducer: MultiStepFormReducer = (state, action) => {
  switch (action.type) {
    case "NEXT":
    case "MOVE_FORWARD_AND_COMPLETE": {
      const currentIndex = state.findIndex(step => step.isSelected);
      const nextIndex =
        state.length <= currentIndex + 1 ? currentIndex : currentIndex + 1;

      const currentStep = state[currentIndex];
      const nextStep = state[nextIndex];

      return state.map(step => ({
        ...step,
        isSelected: step.id === nextStep.id,
        status:
          step.id === currentStep.id &&
          action.type === "MOVE_FORWARD_AND_COMPLETE"
            ? "completed"
            : step.status,
      }));
    }

    case "BACK": {
      const previousStepIndex = state.findIndex(step => step.isSelected) - 1;

      if (previousStepIndex < 0) {
        return state;
      }

      const previousStep = state[previousStepIndex];
      return state.map(step => ({
        ...step,
        isSelected: step.id === previousStep.id,
      }));
    }

    case "JUMP_TO": {
      return state.map(step => ({
        ...step,
        isSelected: step.id === action.value,
      }));
    }

    case "CHANGE_SECTIONS_STATUS": {
      const { status, sections } = action.value;

      return state.map(step => {
        if (sections.includes(step.id)) {
          step.status = status;
        }

        return step;
      });
    }

    default:
      return state;
  }
};

export default multiStepFormReducer;
