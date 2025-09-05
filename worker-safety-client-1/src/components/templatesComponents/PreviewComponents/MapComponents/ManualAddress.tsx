import type { UserFormMode } from "../../customisedForm.types";
import { useEffect, useState } from "react";
import { InputRaw } from "@/components/forms/Basic/Input";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { UserFormModeTypes } from "../../customisedForm.types";

type ManualAddressPops = {
  onChange: (raw: string) => void;
  mode: UserFormMode;
  value: string;
  properties: any;
};
function ManualAddress({
  onChange,
  mode,
  value,
  properties,
}: ManualAddressPops) {
  const [localValue, setLocalValue] = useState<string>(value);

  const [error, setError] = useState(false);
  const { setCWFFormStateDirty } = useCWFFormState();

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (localValue) {
          setError(false);
          onChange(localValue);
        } else {
          setError(true);
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [localValue, onChange]);

  useEffect(() => {
    if (error) {
      if (localValue) {
        setError(false);
      } else {
        setError(true);
      }
    }
  }, [error, localValue]);

  return (
    <>
      <InputRaw
        onChange={_value => {
          setLocalValue(_value);
          setCWFFormStateDirty(true);
        }}
        icon={"map"}
        disabled={
          mode === UserFormModeTypes.BUILD ||
          mode === UserFormModeTypes.PREVIEW ||
          mode === UserFormModeTypes.PREVIEW_PROPS
        }
        placeholder="Enter Location"
        dataTestId="input-manual-address"
        value={localValue}
        hasError={error}
      />
      {error && properties.is_mandatory && (
        <p className="text-red-500 mt-2">This is required</p>
      )}
    </>
  );
}

export default ManualAddress;
