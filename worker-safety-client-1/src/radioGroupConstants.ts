import type { RadioGroupOption } from "./components/shared/radioGroup/RadioGroup";

export const yesOrNoRadioGroupOptions: RadioGroupOption[] = [
  {
    id: 1,
    value: "0",
    description: "No",
  },
  {
    id: 2,
    value: "1",
    description: "Yes",
  },
];

export const notApplicableRadioGroupOptions: RadioGroupOption[] = [
  ...yesOrNoRadioGroupOptions,
  {
    id: -1,
    value: "-1",
    description: "N/A",
  },
];
