import type { FieldType, UserFormMode } from "../customisedForm.types";
import type { ErrorType, FieldProperties } from "./textUtils";
import { useEffect, useState } from "react";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { InputRaw } from "@/components/forms/Basic/Input/InputRaw";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { isDisabledMode, disabledField } from "../customisedForm.utils";
import {
  generateErrorMessage,
  getCurrentValidationStatus,
  getValidationPattern,
  sanitizeInput,
  validateInput,
} from "./textUtils";

type Props = {
  content: {
    type: FieldType;
    properties: FieldProperties;
    id?: string;
  };
  inSummary?: boolean;
  onTextboxUpdate: (value: string) => void;
  mode: UserFormMode;
};

export const RenderShortTextInSummary = ({
  properties,
  localValue,
}: {
  properties: FieldProperties;
  localValue: string;
}): JSX.Element => {
  return (
    <div className="flex gap-2 flex-col">
      <ComponentLabel className="text-sm font-semibold cursor-auto">
        {properties.title}
      </ComponentLabel>
      <BodyText className="text-base">{localValue}</BodyText>
    </div>
  );
};

function Text(props: Props) {
  const { properties } = props.content;
  const [localValue, setLocalValue] = useState(properties.user_value || "");
  const { setCWFFormStateDirty } = useCWFFormState();
  const { include_in_widget } = properties;
  const [isDisabledForm] = useState(isDisabledMode(props.mode));
  const { inSummary } = props;
  const [error, setError] = useState<ErrorType>({
    errorAlert: false,
    errorMessage: "",
  });

  const checkErrorAndUpdate = (
    isError: boolean,
    value: string,
    typeOfResponse: string
  ) => {
    typeOfResponse === "allow_special_characters"
      ? setLocalValue(sanitizeInput(value, false))
      : setLocalValue(value);

    if (isError) {
      // If the field is empty to display "This is reqired text"
      const errorMessageType =
        value.trim() === "" && properties.is_mandatory
          ? "non_empty"
          : typeOfResponse;

      setError({
        errorAlert: true,
        errorMessage: generateErrorMessage(errorMessageType),
      });
    } else {
      setError({
        errorAlert: false,
        errorMessage: "",
      });
    }
    //setting form dirty onchange of textbox value
    setCWFFormStateDirty(true);
  };

  useEffect(() => {
    props.onTextboxUpdate(localValue);
  }, [localValue]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        const hasValidationError = getCurrentValidationStatus(
          localValue.trim(),
          properties
        );
        if (hasValidationError) {
          const errorType =
            localValue.trim() === "" && properties.is_mandatory
              ? "non_empty"
              : properties.response_option;

          setError({
            errorMessage: generateErrorMessage(errorType),
            errorAlert: true,
          });
        } else {
          setError({ errorAlert: false, errorMessage: "" });
          props.onTextboxUpdate(localValue.trim());
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [localValue, props, properties]);

  useEffect(() => {
    if (!getCurrentValidationStatus(localValue, properties)) {
      setError({
        errorMessage: "",
        errorAlert: false,
      });
    }
  }, [error.errorAlert, localValue, properties]);

  const onChange = (value: string) => {
    if (value.trim() === "" && properties.is_mandatory) {
      checkErrorAndUpdate(true, value, "non_empty");
      return;
    }

    // If there's a value, check against the validation pattern
    const pattern = getValidationPattern(
      properties.response_option,
      properties.validation
    );
    checkErrorAndUpdate(
      validateInput(value, pattern),
      value,
      properties.response_option
    );
  };

  return (
    <div>
      <InputRaw
        id={props.content?.id}
        disabled={disabledField(props.mode)}
        label={
          properties.title + (properties.is_mandatory && !inSummary ? "*" : "")
        }
        sublabel={properties.sub_label || ""}
        placeholder={properties.placeholder || ""}
        onChange={onChange}
        value={isDisabledForm ? "" : localValue}
        dataTestId="input-text"
        hasError={error.errorAlert}
        includeInWidget={include_in_widget}
        mode={props.mode}
      />

      {error.errorAlert && (
        <p className="text-red-500 mt-2">{error.errorMessage}</p>
      )}
    </div>
  );
}

export default Text;
