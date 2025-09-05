import type { UserFormMode } from "../../customisedForm.types";
import { useEffect, useMemo, useState } from "react";
import { InputRaw } from "@/components/forms/Basic/Input";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import { UserFormModeTypes } from "../../customisedForm.types";

type LatLongPops = {
  onChange: (raw: any) => void;
  mode: UserFormMode;
  value: any;
  properties: any;
};

function LatLong({ onChange, mode, value, properties }: LatLongPops) {
  const [lat, setLat] = useState(value?.latitude || "");
  const [lng, setLng] = useState(value?.longitude || "");

  const localValue = useMemo(
    () => (lat && lng ? { latitude: lat, longitude: lng } : null),
    [lat, lng]
  );

  const [error, setError] = useState(false);

  useEffect(() => {
    onChange(localValue);
  }, [localValue]);

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

  const onLatLng = (type: string, _value: string) => {
    if (type === "LAT") {
      setLat(_value);
    } else {
      setLng(_value);
    }
    // onChange(LatLng);
  };

  return (
    <>
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex flex-1 flex-col gap-3">
          <InputRaw
            label="Current Latitude"
            dataTestId="input-latitude"
            type="number"
            disabled={
              mode === UserFormModeTypes.BUILD ||
              mode === UserFormModeTypes.PREVIEW ||
              mode === UserFormModeTypes.PREVIEW_PROPS
            }
            placeholder="Ex. 34.054913"
            onChange={(_value: string) => onLatLng("LAT", _value)}
            hasError={error}
          />
        </div>
        <div className="flex flex-1 flex-col gap-3">
          <InputRaw
            label="Current Longitude"
            dataTestId="input-longitude"
            type="number"
            disabled={
              mode === UserFormModeTypes.BUILD ||
              mode === UserFormModeTypes.PREVIEW ||
              mode === UserFormModeTypes.PREVIEW_PROPS
            }
            onChange={(_value: string) => onLatLng("LONG", _value)}
            placeholder="Ex. -62.136754"
            hasError={error}
          />
        </div>
      </div>
      {error && properties.is_mandatory && (
        <p className="text-red-500 mt-2">This is required</p>
      )}
    </>
  );
}

export default LatLong;
