import type { UserFormMode } from "../../customisedForm.types";
import { useContext, useEffect, useState } from "react";
import { InputRaw } from "@/components/forms/Basic/Input";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { config } from "@/config";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { messages } from "@/locales/messages";
import { UserFormModeTypes } from "../../customisedForm.types";

type CurrentLocationPops = {
  onChange: (raw: any) => void;
  mode: UserFormMode;
  value: string;
  properties: any;
};

function CurrentLocation({
  onChange,
  mode,
  value,
  properties,
}: CurrentLocationPops) {
  const { setCWFFormStateDirty } = useCWFFormState();

  const onChangeOfInput = (_value: string) => {
    setLocation(_value);
    // onChange(_value);
    setCWFFormStateDirty(true);
  };
  const [location, setLocation] = useState(value || "");

  const toastCtx = useContext(ToastContext);

  const [error, setError] = useState(false);

  useEffect(() => {
    onChange(location);
  }, [location]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (location) {
          setError(false);
          onChange(location);
        } else {
          setError(true);
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [location, onChange]);

  useEffect(() => {
    if (error) {
      if (location) {
        setError(false);
      } else {
        setError(true);
      }
    }
  }, [error, location]);

  const handleGeolocationError = (message: string) => {
    toastCtx?.pushToast("error", message);
  };

  const reverseGeoCode = async (lat: number, long: number) => {
    try {
      const response = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${long},${lat}.json?access_token=${config.workerSafetyMapboxAccessToken}`
      );
      return await response.json();
    } catch (_err) {
      handleGeolocationError("Error during reverse geocoding");
      console.error("Error during reverse geocoding", _err);
    }
  };

  const setCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async position => {
          const { latitude, longitude } = position.coords;
          const res = await reverseGeoCode(latitude, longitude);
          const { features } = res;
          if (features.length) {
            const address = res.features[0].place_name;
            // onChange(address);
            setLocation(address);
          } else {
            handleGeolocationError("Invalid latitude & longitude");
          }
        },
        _err => {
          handleGeolocationError(messages.mapErrorNoPermissions);
          console.log(_err.message);
        }
      );
    } else {
      handleGeolocationError("Geolocation is not supported by this browser.");
    }
  };
  return (
    <>
      <InputRaw
        onChange={onChangeOfInput}
        value={location}
        dataTestId="input-current-location-autofill"
        icon={"map"}
        disabled={
          mode === UserFormModeTypes.BUILD ||
          mode === UserFormModeTypes.PREVIEW ||
          mode === UserFormModeTypes.PREVIEW_PROPS
        }
        placeholder="Enter Location"
        hasError={error}
      />
      <div className="flex flex-row">
        <ButtonRegular
          iconStart="target"
          onClick={setCurrentLocation}
          disabled={
            mode === UserFormModeTypes.BUILD ||
            mode === UserFormModeTypes.PREVIEW ||
            mode === UserFormModeTypes.PREVIEW_PROPS
          }
          label="Use my current location"
          className="text-brand-urbint-40"
        />
      </div>
      {error && properties.is_mandatory && (
        <p className="text-red-500 mt-2">This is required</p>
      )}
    </>
  );
}

export default CurrentLocation;
