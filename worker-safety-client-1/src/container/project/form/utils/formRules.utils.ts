import { FieldRules } from "@/components/shared/field/FieldRules";

//TODO Use the message.ts (still not merged in main) to retrieve the "required" message
const requiredFieldRules = {
  ...FieldRules.REQUIRED,
  ...FieldRules.NOT_ONLY_WHITESPACE,
};

const getRequiredFieldRules = (isRequired: boolean) =>
  isRequired ? requiredFieldRules : {};

export { getRequiredFieldRules, requiredFieldRules };
