import type { SelectCardOption } from "../../select/SelectCard";

export const addSelectedOption = (
  options: SelectCardOption[],
  id: string
): void => {
  const optionToUpdate = options.find(option => option.id === id);
  if (optionToUpdate) {
    optionToUpdate.isSelected = true;
  }
};

export const removeSelectedOption = (
  options: SelectCardOption[],
  id: string
): void => {
  const optionToUpdate = options.find(option => option.id === id);
  if (optionToUpdate) {
    optionToUpdate.isSelected = false;
  }
};
