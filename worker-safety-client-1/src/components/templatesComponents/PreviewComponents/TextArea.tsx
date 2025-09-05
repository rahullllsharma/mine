import type { FieldType, UserFormMode } from "../customisedForm.types";
import type { ErrorType, FieldProperties } from "./textUtils";
import { useState, useEffect } from "react";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { TextAreaRaw } from "@/components/forms/Basic/TextArea/TextAreaRaw";
import {
  formEventEmitter,
  FORM_EVENTS,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { isDisabledMode, disabledField } from "../customisedForm.utils";
import {
  generateErrorMessage,
  validateInput,
  getCurrentValidationStatus,
  getValidationPattern,
} from "./textUtils";

type Props = {
  content: {
    type: FieldType;
    properties: FieldProperties;
  };
  onTextboxUpdate: (value: string) => void;
  mode: UserFormMode;
  inSummary?: boolean;
};

export const RenderTextAreaInSummary = ({
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

function TextArea(props: Props) {
  const { properties } = props.content;
  const { include_in_widget } = properties;
  const [localValue, setLocalValue] = useState(properties.user_value || "");
  const [error, setError] = useState<ErrorType>({
    errorAlert: false,
    errorMessage: "",
  });
  const { inSummary } = props;
  const { setCWFFormStateDirty } = useCWFFormState();

  const checkErrorAndUpdate = (
    isError: boolean,
    value: string,
    typeOfResponse: string
  ) => {
    setLocalValue(value);
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
          setError({
            errorMessage: generateErrorMessage(
              localValue.trim() === "" && properties.is_mandatory
                ? "non_empty"
                : properties.response_option
            ),
            errorAlert: true,
          });
        } else {
          setError(prev => ({ ...prev, errorAlert: false }));
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
    <div className="mb-8">
      <TextAreaRaw
        disabled={disabledField(props.mode)}
        label={
          properties.title + (properties.is_mandatory && !inSummary ? "*" : "")
        }
        sublabel={properties.sub_label || ""}
        placeholder={properties.placeholder || ""}
        onChange={onChange}
        value={isDisabledMode(props.mode) ? "" : localValue}
        hasError={error.errorAlert}
        mode={props.mode}
        includeInWidget={include_in_widget}
      />
      {error.errorAlert && <p className="text-red-500">{error.errorMessage}</p>}
    </div>
  );
}

export default TextArea;
