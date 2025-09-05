import type { FormState } from "@/components/dynamicForm/phoneNumber";
import type { FieldType, UserFormMode } from "../customisedForm.types";
import { useEffect, useState } from "react";
import { BodyText, ComponentLabel, Icon } from "@urbint/silica";
import { TelephoneInput } from "@/components/forms/Basic/Input";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { fieldDef } from "@/utils/formField";
import { validPhoneNumberCodec } from "@/utils/validation";
import formatTextToPhone from "@/utils/formatTextToPhone";
import {
  isDisabledMode,
  disabledField,
  isValidPhoneNumberFormat,
} from "../customisedForm.utils";

type Content = {
  type: FieldType;
  properties: FormState;
  id?: string;
};

type Props = {
  content: Content;
  mode: UserFormMode;
  inSummary?: boolean;
  onChange: (value: any) => void;
};

type ErrorType = {
  errorAlert: boolean;
  errorMessage: string;
};

export const RenderPhoneNumberInSummary = (props: {
  properties: FormState;
  localValue: string;
}): JSX.Element => {
  const { properties, localValue } = props;

  const getCorrectPhoneNumberFormat = (phoneNumber: string) => {
    if (isValidPhoneNumberFormat(phoneNumber)) {
      return phoneNumber;
    }
    return formatTextToPhone(phoneNumber);
  };

  return (
    <div className="flex gap-2 flex-col">
      <ComponentLabel className="text-sm font-semibold cursor-auto">
        {properties.title}
      </ComponentLabel>
      <div className="flex flex-row items-center">
        <a
          href={`tel:${getCorrectPhoneNumberFormat(localValue)}`}
          className="text-base flex flex-row gap-1 items-center"
        >
          <Icon name="phone" className="text-[20px] text-brand-urbint-50" />
          <BodyText className="text-base text-brand-urbint-50">
            {getCorrectPhoneNumberFormat(localValue)}
          </BodyText>
        </a>
      </div>
    </div>
  );
};

function PhoneNumber(props: Props) {
  const { content, mode, inSummary, onChange } = props;
  const { properties } = content;
  const { include_in_widget } = properties;
  const [localValue, setLocalValue] = useState(properties.user_value || "");
  const [isDisabledForm] = useState(isDisabledMode(mode));
  const [error, setError] = useState<ErrorType>({
    errorAlert: false,
    errorMessage: "",
  });
  const { setCWFFormStateDirty } = useCWFFormState();

  useEffect(() => {
    if (localValue) {
      if (localValue?.length > 9) {
        setError({ errorAlert: false, errorMessage: "" });
      } else {
        setError({ errorAlert: true, errorMessage: "Invalid phone number" });
      }
    }
  }, [localValue]);

  const inputValidation = (value: string) => {
    if (value.length > 9) {
      setError({ errorAlert: false, errorMessage: "" });
      return true;
    } else {
      if (!value && properties.is_mandatory) {
        setError({ errorAlert: true, errorMessage: "This is required" });
      } else if (value) {
        setError({ errorAlert: true, errorMessage: "Invalid phone number" });
      }
      return false;
    }
  };
  const updateValue = (value: string) => {
    setLocalValue(value);
    setCWFFormStateDirty(true);
  };
  useEffect(() => {
    props.onChange(localValue);
  }, [localValue]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (properties.is_mandatory) {
          if (inputValidation(localValue)) {
            setError(prev => ({ ...prev, errorAlert: false }));
            onChange(localValue);
          } else {
            const errorMessage =
              localValue === "" ? "This is required" : "Invalid phone number";

            setError({
              errorMessage,
              errorAlert: true,
            });
          }
        } else {
          // For non-mandatory fields, only update if valid
          inputValidation(localValue) && onChange(localValue);
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [error.errorAlert, localValue]);

  return (
    <div id={content.id}>
      <TelephoneInput
        field={
          isDisabledForm
            ? fieldDef(validPhoneNumberCodec.decode).init("")
            : fieldDef(validPhoneNumberCodec.decode).init(localValue)
        }
        onChange={updateValue}
        label={
          properties.title + (properties.is_mandatory && !inSummary ? "*" : "")
        }
        includeInWidget={include_in_widget}
        disabled={disabledField(mode)}
        hasError={error.errorAlert}
        errorMessage={error.errorMessage}
        mode={mode}
      />
    </div>
  );
}

export default PhoneNumber;
