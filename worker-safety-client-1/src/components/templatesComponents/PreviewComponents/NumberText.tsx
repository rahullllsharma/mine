import type { FieldType, UserFormMode } from "../customisedForm.types";
import type { FormState } from "@/components/dynamicForm/numberInput";
import { useEffect, useState } from "react";
import { ComponentLabel } from "@urbint/silica";
import { InputRaw } from "@/components/forms/Basic/Input/InputRaw";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { ALLOWED_KEYS_FOR_NUMBER_TYPE } from "@/utils/customisedFormUtils/customisedForm.constants";
import { disabledField, isDisabledMode } from "../customisedForm.utils";
import style from "./previewComponents.module.scss";

type Props = {
  content: {
    type: FieldType;
    properties: any;
    id?: string;
  };
  onTextboxUpdate: (textboxUpdate: string) => void;
  mode: UserFormMode;
  inSummary?: boolean;
};

type ErrorType = {
  errorAlert: boolean;
  errorMessage: string;
};

export const RenderNumberTextInSummary = (props: {
  properties: FormState;
  localValue: string;
}): JSX.Element => {
  const { properties, localValue } = props;
  return (
    <div className="flex gap-2 flex-col">
      <ComponentLabel className="text-sm font-semibold cursor-auto">
        {properties.title}
      </ComponentLabel>
      <div className="flex flex-row content-center items-center text-base">
        {localValue}
        {properties.display_units ? ` ${properties.unit_name}` : null}
      </div>
    </div>
  );
};

function NumberText(props: Props) {
  const { properties } = props.content;
  const [error, setError] = useState<ErrorType>({
    errorAlert: false,
    errorMessage: "",
  });
  const [localValue, setLocalValue] = useState(properties.user_value || "");
  const { setCWFFormStateDirty } = useCWFFormState();
  const [isDisabledForm] = useState(isDisabledMode(props.mode));
  const { inSummary } = props;
  const { include_in_widget } = properties;
  const checkErrorAndUpdate = (isError: boolean, value: string) => {
    setLocalValue(value);
    setCWFFormStateDirty(true);
    //TODO: We need to add validation for regex in future,currently only validating mandatory fields
    if (isError && value.trim() === "") {
      setError({
        errorAlert: true,
        errorMessage: "This is a required value",
      });
    }
  };

  const validateInput = (value: string, pattern: RegExp) => {
    return !pattern.test(value);
  };

  const onChange = (value: string) => {
    switch (properties.response_option) {
      case "allowDecimals":
        checkErrorAndUpdate(validateInput(value, /^-?\d+(\.\d+)?$/), value);
        break;
      case "allowNegativeNumbers":
        checkErrorAndUpdate(validateInput(value, /^-?\d+$/), value);
        break;
    }
  };

  useEffect(() => {
    props.onTextboxUpdate(localValue);
  }, [localValue]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (localValue.trim() === "" && properties.is_mandatory) {
          setError({
            errorMessage: "This is required",
            errorAlert: true,
          });
        } else {
          setError(prev => ({ ...prev, errorAlert: false }));
          props.onTextboxUpdate(localValue);
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [localValue, props]);

  useEffect(() => {
    if (localValue.trim() != "") {
      setError({
        errorMessage: "",
        errorAlert: false,
      });
    }
  }, [error.errorAlert, localValue]);

  return (
    <>
      <div className={style.numberInputBox} id={props.content.id}>
        <InputRaw
          disabled={disabledField(props.mode)}
          type="number"
          label={
            properties.title +
            (properties.is_mandatory && !inSummary ? "*" : "")
          }
          mode={props.mode}
          includeInWidget={include_in_widget}
          onChange={onChange}
          value={isDisabledForm ? "" : localValue}
          dataTestId="input-number"
          hasError={error.errorAlert}
          onKeyDown={e => {
            const isNumber = e.key >= "0" && e.key <= "9";
            if (!isNumber && !ALLOWED_KEYS_FOR_NUMBER_TYPE.includes(e.key)) {
              e.preventDefault();
            }
          }}
        />
        {properties.display_units ? (
          <p className={style.numberInputBox__unitSection}>
            {properties.unit_name}
          </p>
        ) : null}
      </div>
      {error.errorAlert && properties.is_mandatory && (
        <p className="text-red-500 mt-2">{error.errorMessage}</p>
      )}
    </>
  );
}

export default NumberText;
