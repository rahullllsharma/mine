import type { ValidKeys } from "@/container/admin/tenantAttributes/types";

const MANDATORY_FIELDS = ["visible", "required"];

function isMandatoryField(mandatory: boolean, key: ValidKeys) {
  return mandatory && MANDATORY_FIELDS.includes(key);
}

function shouldUpdateNonVisibleFields(key: ValidKeys) {
  return key === "visible";
}

export { isMandatoryField, shouldUpdateNonVisibleFields };
