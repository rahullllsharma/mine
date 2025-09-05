import { useState } from "react";

type ApplicableState = { [key: string]: boolean };

export function useCardStateManagement(): [
  ApplicableState,
  (id: string, state: boolean) => void
] {
  const [value, setValue] = useState<ApplicableState>({});

  function customSetValue(id: string, state: boolean) {
    setValue((prevState: ApplicableState) => {
      return {
        ...prevState,
        [id]: state,
      };
    });
  }

  return [value, customSetValue];
}
