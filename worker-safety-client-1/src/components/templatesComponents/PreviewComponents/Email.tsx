import type { FieldType, UserFormMode } from "../customisedForm.types";
import type { FormState } from "@/components/dynamicForm/email";
import { useEffect, useState } from "react";
import { BodyText, ComponentLabel, Icon } from "@urbint/silica";
import { InputRaw } from "@/components/forms/Basic/Input";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { isDisabledMode } from "../customisedForm.utils";
import style from "./previewComponents.module.scss";
import { isEmailValid } from "./textUtils";

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

export const RenderEmailInSummary = (props: {
  properties: FormState;
  localValue: string;
}): JSX.Element => {
  const { properties, localValue } = props;
  return (
    <div className="flex gap-2 flex-col">
      <ComponentLabel className="text-sm font-semibold cursor-auto">
        {properties.title}
      </ComponentLabel>
      <a href={`mailto:${localValue}`} className="flex items-center gap-1">
        <Icon
          name={"mail"}
          className="text-xl bg-transparent text-brand-urbint-50"
        />
        <BodyText className="text-base text-brand-urbint-50">
          {localValue}
        </BodyText>
      </a>
    </div>
  );
};

function Email(props: Props) {
  const {
    response_option,
    is_mandatory,
    title,
    user_value,
    include_in_widget,
  } = props.content.properties;
  const { inSummary } = props;
  const [localValue, setLocalValue] = useState(user_value);
  const [error, setError] = useState<ErrorType>({
    errorAlert: false,
    errorMessage: "",
  });
  const { setCWFFormStateDirty } = useCWFFormState();
  const [isDisabledForm] = useState(isDisabledMode(props.mode));

  const checkErrorAndUpdate = (isError: boolean, value: string) => {
    setLocalValue(value);
    //setting form dirty onchange of Email textbox value
    setCWFFormStateDirty(true);
    if (isError) {
      setError({ errorAlert: true, errorMessage: "Please enter valid email" });
    }
    //
  };

  const onChange = (value: string) => {
    switch (response_option) {
      case "manual_input":
        checkErrorAndUpdate(!isEmailValid(value), value);
        break;
      case "auto_populate_user_email":
        checkErrorAndUpdate(!isEmailValid(value), value);
        break;
    }
  };

  useEffect(() => {
    if (localValue) {
      if (isEmailValid(localValue)) {
        setError({ errorAlert: false, errorMessage: "" });
      } else {
        setError({
          errorAlert: true,
          errorMessage: "Please enter valid email",
        });
      }
    }
  }, [localValue, error.errorAlert]);

  const saveAndContinueErrorCheck = () => {
    if (localValue) {
      if (localValue.trim() !== "" && isEmailValid(localValue)) {
        return true;
      }
    }
    return false;
  };

  useEffect(() => {
    props.onTextboxUpdate(localValue);
  }, [localValue]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (!is_mandatory) {
          props.onTextboxUpdate(localValue);
        } else {
          if (saveAndContinueErrorCheck()) {
            setError(prev => ({ ...prev, errorAlert: false }));
            props.onTextboxUpdate(localValue);
          } else {
            setError({
              errorMessage: "This is required",
              errorAlert: true,
            });
          }
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [error.errorAlert, localValue]);

  return (
    <>
      <div
        id={props.content.id}
        className={
          error.errorAlert
            ? `${style.numberInputBox} ${style.errorTelephoneInput}`
            : style.numberInputBox
        }
      >
        <InputRaw
          disabled={isDisabledForm}
          mode={props.mode}
          type="text"
          label={title + (is_mandatory && !inSummary ? "*" : "")}
          dataTestId="input-email"
          onChange={onChange}
          value={isDisabledForm ? "" : localValue || ""}
          includeInWidget={include_in_widget}
        />
      </div>
      {error.errorAlert && (
        <span className={style.errorMessage}>{error.errorMessage}</span>
      )}
    </>
  );
}

export default Email;
