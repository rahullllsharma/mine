import type { Dispatch, PropsWithChildren } from "react";
import type {
  MultiStepFormActions,
  MultiStepFormState,
  MultiStepFormStep,
} from "./state/reducer";
import { useMemo, useReducer } from "react";

import MultiStepFormContext from "./context/MultiStepFormContext";
import multiStepFormReducer from "./state/reducer";
import MultiStep from "./components/multiStep/MultiStep";
import { formatSteps } from "./utils";

export type MultiStepFormProps<T = Record<string, unknown>> = {
  steps: MultiStepFormStep<T>[];
  onStepMount?: () => any;
  onStepUnmount?: (data: unknown) => void;
  onStepChange?: (data: unknown) => void;
  onStepSave?: (
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    data: any
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ) => void | Promise<{ data?: any; errors?: any }> | Promise<boolean>;
  onComplete?: (data: unknown) => void;
  UNSAFE_WILL_BE_REMOVED_debugMode?: boolean;
  readOnly?: boolean;
};

export function MultiStepFormProvider({
  steps,
  children,
}: PropsWithChildren<Pick<MultiStepFormProps, "steps">>): JSX.Element {
  const [reducer, dispatch] = useReducer(
    multiStepFormReducer,
    steps,
    formatSteps
  );

  // stabilize internals
  const memoizedReducer = useMemo(() => [reducer, dispatch], [reducer]) as [
    MultiStepFormState,
    Dispatch<MultiStepFormActions>
  ];

  return (
    <MultiStepFormContext.Provider
      value={memoizedReducer}
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      displayName="MultiStepFormContext"
    >
      {children}
    </MultiStepFormContext.Provider>
  );
}

export default function MultiStepForm({
  steps,
  ...props
}: MultiStepFormProps): JSX.Element {
  return (
    <MultiStepFormProvider steps={steps}>
      <MultiStep {...props} />
    </MultiStepFormProvider>
  );
}
