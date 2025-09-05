import type { LocationInputType } from "../customisedForm.types";
import router from "next/router";
import {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { BodyText } from "@urbint/silica";
import axiosRest from "@/api/customFlowApi";
import { UserLocationCoordinates } from "@/components/dynamicForm/LocationComponent/CWFLocation";
import CWFLocationMapView from "@/components/dynamicForm/LocationComponent/CWFLocationMapView";
import LocationMapViewModal from "@/components/dynamicForm/LocationComponent/LocationMapViewModal";
import { InputRaw } from "@/components/forms/Basic/Input";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { config } from "@/config";
import useRestMutation from "@/hooks/useRestMutation";
import { messages } from "@/locales/messages";
import { UserFormModeTypes } from "../customisedForm.types";
import { debounce } from "../customisedForm.utils";
import SvgButton from "../ButtonComponents/SvgButton/SvgButton";
import LocationSearchUsingAPI from "./MapComponents/LocationSearchUsingAPI";
import { isFormDisabled } from "./textUtils";

function LocationInput(props: LocationInputType) {
  const {
    is_mandatory,
    title,
    user_value,
    is_show_map_preview,
    include_in_widget,
  } = props.content.properties;
  const name = user_value?.name;
  const gps_coordinates = user_value?.gps_coordinates;
  const locationForwardRef = useRef(false);
  const locationReverseRef = useRef(false);
  const [isLocationMapViewModalOpen, setIsLocationMapViewModalOpen] =
    useState(false);
  const [location, setLocation] = useState(name ?? "");
  const [latitude, setLatitude] = useState(gps_coordinates?.latitude ?? "");
  const [longitude, setLongitude] = useState(gps_coordinates?.longitude ?? "");
  const [userLocationLatitude, setUserLocationLatitude] = useState("");
  const [userLocationLongitude, setUserLocationLongitude] = useState("");
  const { inSummary } = props;
  const toastCtx = useContext(ToastContext);

  const handleGeolocationError = (message: string) => {
    toastCtx?.pushToast("error", message);
  };
  const handleLocationMapViewModal = () => {
    setIsLocationMapViewModalOpen(!isLocationMapViewModalOpen);
  };

  const { mutate: reverseGeoCode } = useRestMutation<{
    lat: number;
    lng: number;
  }>({
    endpoint: data =>
      `https://api.mapbox.com/search/geocode/v6/reverse?longitude=${data.lng}&latitude=${data.lat}&access_token=${config.workerSafetyMapboxAccessToken}`,
    method: "get",
    axiosInstance: axiosRest,
    mutationOptions: {
      onSuccess: (response: any, variables: { lat: number; lng: number }) => {
        const { features } = response.data;
        if (features && features.length > 0) {
          const address = features[0].properties.full_address ?? "";

          setLatitude(variables.lat.toString());
          setLongitude(variables.lng.toString());
          setLocation(address);
        }
        locationReverseRef.current = false;
      },
      onError: (error: any) => {
        handleGeolocationError("Error during reverse geocoding");
        console.error("Error during reverse geocoding", error);
        locationReverseRef.current = false;
      },
    },
  });
  const debouncedReverseGeoCode = useCallback(
    debounce((lat: number, lng: number) => {
      reverseGeoCode({ lat, lng });
    }, 1500),
    []
  );
  const handleLatitudeChange = (value: string) => {
    if (checkValidCoordinates(value, "latitude")) return;

    locationReverseRef.current = true;
    locationForwardRef.current = false;
    setLatitude(value);
  };

  const handleLongitudeChange = (value: string) => {
    if (checkValidCoordinates(value, "longitude")) return;
    locationReverseRef.current = true;
    locationForwardRef.current = false;
    setLongitude(value);
  };

  const handleOnLocationChange = (value: string) => {
    locationForwardRef.current = true;
    locationReverseRef.current = false;
    setLocation(value);
  };
  const renderLabelAndComponent = (component: any) => (
    <>
      {component && (
        <div>
          <div className="flex gap-2 mb-1">
            <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal">
              {title}
              {is_mandatory && !inSummary ? "*" : ""}
            </label>
            {include_in_widget && props.mode === "BUILD" && (
              <div className="text-neutrals-tertiary flex gap-2">
                <SvgButton svgPath={"/assets/CWF/widget.svg"} />
                <BodyText className="text-neutrals-tertiary">Widget</BodyText>
              </div>
            )}
          </div>
          {component}
        </div>
      )}
    </>
  );
  const setCurrentLocation = () => {
    locationReverseRef.current = true;
    locationForwardRef.current = false;

    if (navigator.geolocation && locationReverseRef.current) {
      navigator.geolocation.getCurrentPosition(
        async position => {
          const { latitude: lat, longitude: lng } = position.coords;
          debouncedReverseGeoCode(lat, lng);
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

  useEffect(() => {
    if (navigator.geolocation && router.pathname.includes("/template-forms")) {
      navigator.geolocation.getCurrentPosition(
        async position => {
          const { latitude: lat, longitude: lng } = position.coords;
          setUserLocationLatitude(String(lat));
          setUserLocationLongitude(String(lng));
        },
        _err => {
          handleGeolocationError(messages.mapErrorNoPermissions);
          console.log(_err.message);
        }
      );
    }
  }, []);

  const localValue = useMemo(() => {
    return {
      name: location,
      gps_coordinates:
        latitude && longitude
          ? {
              latitude: Number(latitude),
              longitude: Number(longitude),
            }
          : null,
    };
  }, [latitude, longitude, location]);

  useEffect(() => {
    props.onChange(localValue);
  }, [localValue]);

  const checkValidCoordinates = (
    coordinate: string,
    coordinateType: string
  ) => {
    switch (coordinateType) {
      case "latitude":
        if (
          coordinate &&
          (Number(coordinate) < -90 || Number(coordinate) > 90)
        ) {
          handleGeolocationError("Latitude must be between -90 to 90");
          return true;
        }
        break;
      case "longitude":
        if (
          coordinate &&
          (Number(coordinate) < -180 || Number(coordinate) > 180)
        ) {
          handleGeolocationError("Longitude must be between -180 to 180");
          return true;
        }
        break;
      default:
        handleGeolocationError("Invalid coordinate type.");
        return true;
    }
    return false;
  };

  useEffect(() => {
    if (
      !latitude ||
      !longitude ||
      locationForwardRef.current ||
      !locationReverseRef.current
    )
      return;

    const lat = Number(latitude);
    const lng = Number(longitude);

    if (
      !isNaN(lat) &&
      !isNaN(lng) &&
      lat >= -90 &&
      lat <= 90 &&
      lng >= -180 &&
      lng <= 180
    ) {
      debouncedReverseGeoCode(lat, lng);
    }
  }, [latitude, longitude]);

  const handleOnCoordinateClear = (coordinateType: UserLocationCoordinates) => {
    if (coordinateType === UserLocationCoordinates.LATITUDE) {
      setLatitude("");
    } else {
      setLongitude("");
    }
  };

  return renderLabelAndComponent(
    <div className="flex flex-col gap-2" id={props.content.id}>
      <div className="flex flex-col md:flex-row gap-4">
        <div className="w-full">
          <LocationSearchUsingAPI
            mode={props.mode}
            onChange={handleOnLocationChange}
            properties={props.content.properties}
            value={location}
            setLatitude={setLatitude}
            setLongitude={setLongitude}
            userLocationLatitude={Number(userLocationLatitude)}
            userLocationLongitude={Number(userLocationLongitude)}
          />
        </div>
        <div className="w-auto" style={{ isolation: "isolate" }}>
          <div
            className="inline-block"
            style={{ isolation: "isolate", position: "relative", zIndex: 1 }}
            onClick={e => e.stopPropagation()}
          >
            <ButtonSecondary
              iconStart="target"
              disabled={isFormDisabled(props.mode)}
              label="Locate Me"
              className="flex justify-end gap-2 w-full sm:w-auto focus:outline-none focus:ring-2 focus:ring-brand-gray-60 focus:ring-offset-1 active:ring-2 active:ring-brand-gray-60"
              onClick={e => {
                e.stopPropagation();
                e.preventDefault();
                setCurrentLocation();
              }}
              style={{ isolation: "isolate" }}
            />
          </div>
        </div>
      </div>
      {props.mode !== UserFormModeTypes.BUILD && (
        <div className="flex flex-col md:flex-row  gap-5">
          <div className="w-full ">
            <InputRaw
              type="number"
              label="Latitude"
              disabled={isFormDisabled(props.mode)}
              clearIcon={true}
              value={latitude}
              onChange={handleLatitudeChange}
              onClear={() =>
                handleOnCoordinateClear(UserLocationCoordinates.LATITUDE)
              }
            />
          </div>
          <div className="w-full ">
            <InputRaw
              type="number"
              label="Longitude"
              disabled={isFormDisabled(props.mode)}
              clearIcon={true}
              value={longitude}
              onChange={handleLongitudeChange}
              onClear={() =>
                handleOnCoordinateClear(UserLocationCoordinates.LONGITUDE)
              }
            />
          </div>
        </div>
      )}
      {is_show_map_preview && latitude && longitude && (
        <div className="flex flex-row gap-6">
          <div
            className="relative w-full cursor-pointer group"
            onClick={handleLocationMapViewModal}
          >
            <CWFLocationMapView
              selectedLocationLatitude={latitude.toString()}
              selectedLocationLongitude={longitude.toString()}
              modalMapView={true}
            />
          </div>
        </div>
      )}
      {is_show_map_preview && latitude && longitude && (
        <LocationMapViewModal
          latitude={latitude.toString()}
          longitude={longitude.toString()}
          isOpen={isLocationMapViewModalOpen}
          closeModal={handleLocationMapViewModal}
          location={location}
          locationDescription={""}
          modalMapView={false}
        />
      )}
    </div>
  );
}

export default LocationInput;
