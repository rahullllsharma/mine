import type { UserFormMode } from "../customisedForm.types";
import { UserFormModeTypes } from "../customisedForm.types";

export type FieldProperties = {
  user_value?: string;
  title: string;
  sub_label?: string;
  placeholder?: string;
  is_mandatory?: boolean;
  response_option: string;
  validation?: string[];
  include_in_widget?: boolean;
};

export type ErrorType = {
  errorAlert: boolean;
  errorMessage: string;
};

export const REGEX_VALIDATOR = {
  alphanumeric: /^\s*[a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*\s*$/,
  allow_special_characters: /^/,
} as const;

export const generateErrorMessage = (typeOfResponse: string): string => {
  switch (typeOfResponse) {
    case "non_empty":
      return "This is required";
    case "alphanumeric":
      return "Alphabets and Numbers only allowed";
    case "regex":
      return "Must match the pattern";
    default:
      return "This is required";
  }
};

export const validateInput = (value: string, pattern: RegExp): boolean => {
  return !pattern.test(value);
};

export const sanitizeInput = (value: string, shouldTrim = false): string => {
  const sanitized = value
    .replace(/['";]/g, "") // Remove SQL injection characters
    .replace(/[<>]/g, "") // Remove potential HTML injection characters
    .replace(/javascript:/gi, "") // Remove javascript: protocol
    .replace(/data:/gi, "") // Remove data: protocol
    .replace(/vbscript:/gi, ""); // Remove vbscript: protocol

  return shouldTrim ? sanitized.trim() : sanitized;
};

export const getValidationPattern = (
  responseOption: string,
  validation?: string[]
): RegExp => {
  return responseOption === "regex"
    ? new RegExp(validation?.[0]?.replace(/^\/|\/$/g, "") || "")
    : REGEX_VALIDATOR[responseOption as keyof typeof REGEX_VALIDATOR];
};

export const isFormDisabled = (mode: UserFormMode): boolean => {
  return (
    mode === UserFormModeTypes.BUILD ||
    mode === UserFormModeTypes.PREVIEW ||
    mode === UserFormModeTypes.PREVIEW_PROPS
  );
};

export const getCurrentValidationStatus = (
  value: string,
  properties: FieldProperties
): boolean => {
  if (value.trim() === "" && properties.is_mandatory) {
    return true;
  }

  if (value.trim() !== "") {
    const pattern = getValidationPattern(
      properties.response_option,
      properties.validation
    );
    return validateInput(value, pattern);
  }

  return false;
};

export const isEmailValid = (value: string) => {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(value);
};
