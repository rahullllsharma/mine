import type {
  MultiStepFormActions,
  MultiStepFormState,
} from "../state/reducer";

import type { Dispatch } from "react";
import { createContext, useContext } from "react";

const MultiStepFormContext = createContext<
  [MultiStepFormState, Dispatch<MultiStepFormActions>] | []
>([]);

export const useMultiStepFormContext = (): [
  MultiStepFormState,
  Dispatch<MultiStepFormActions>
] =>
  useContext(MultiStepFormContext) as unknown as [
    MultiStepFormState,
    Dispatch<MultiStepFormActions>
  ];

export default MultiStepFormContext;
