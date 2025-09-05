import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";

export const getDefaultOption = (
  options: RadioGroupOption[],
  needle: string
): RadioGroupOption | undefined => {
  return options.find(option => option.value === needle);
};
