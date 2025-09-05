import type {
  ActivePageObjType,
  CWFLocationType,
  LocationUserValueType,
  ProjectDetailsType,
  UserFormMode,
  originalLocationValues,
  pendingAction,
} from "@/components/templatesComponents/customisedForm.types";
import { gql, useMutation } from "@apollo/client";
import { ComponentLabel } from "@urbint/silica";
import { capitalize, debounce } from "lodash-es";
import router from "next/router";
import React, { useContext, useEffect, useRef, useState } from "react";
import axiosRest from "@/api/customFlowApi";
import { InputRaw } from "@/components/forms/Basic/Input";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import Input from "@/components/shared/input/Input";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import LocationSearchUsingAPI from "@/components/templatesComponents/PreviewComponents/MapComponents/LocationSearchUsingAPI";
import style from "@/components/templatesComponents/PreviewComponents/previewComponents.module.scss";
import { isFormDisabled } from "@/components/templatesComponents/PreviewComponents/textUtils";
import { config } from "@/config";
import { ConfirmDateChangeModal } from "@/container/report/workSchedule/ConfirmDateChangeModal";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useRestMutation from "@/hooks/useRestMutation";
import { messages } from "@/locales/messages";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import CWFLocationMapView from "./CWFLocationMapView";
import LocationMapViewModal from "./LocationMapViewModal";
import useCWFFormState from "@/hooks/useCWFFormState";

const createLocation = gql`
  mutation createLocationFromLatLon(
    $date: DateTime
    $gpsCoordinates: GPSCoordinatesInput!
    $name: String
  ) {
    createLocationFromLatLon(
      gpsCoordinates: $gpsCoordinates
      date: $date
      name: $name
    ) {
      id
    }
  }
`;

export enum UserLocationCoordinates {
  LATITUDE = "latitude",
  LONGITUDE = "longitude",
}

const CWFLocation = ({
  item,
  mode,
  projectDetails,
  inSummary,
  activePageDetails,
}: {
  item: CWFLocationType;
  activePageDetails: ActivePageObjType;
  section: any;
  mode: UserFormMode;
  projectDetails?: ProjectDetailsType;
  inSummary?: boolean;
}): JSX.Element => {
  const [isLocationMapViewModalOpen, setIsLocationMapViewModalOpen] =
    useState(false);
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const toastCtx = useContext(ToastContext);
  const isTemplateForms = router.pathname.includes("/template-forms");

  const locationData = state.form.component_data?.location_data;
  const { name, gps_coordinates, description } = locationData ?? {};
  const workPackageId = state.form.metadata?.work_package?.id;

  const { setCWFFormStateDirty } = useCWFFormState();

  const {
    latitude: workPackageLocationLatitude,
    longitude: workPackageLocationLongitude,
    location: workPackageLocationId,
  } = router.query || "";

  const [location, setLocation] = useState(name ?? "");
  const [latitude, setLatitude] = useState(gps_coordinates?.latitude ?? "");
  const [longitude, setLongitude] = useState(gps_coordinates?.longitude ?? "");
  const [locationDescription, setLocationDescription] = useState(
    description ?? ""
  );

  const initialLocationData = useRef(locationData);
  localStorage.setItem(
    "location_data",
    JSON.stringify(initialLocationData.current)
  );

  const locationForwardRef = useRef(false);
  const locationReverseRef = useRef(false);
  const isClearingRef = useRef(false);

  const [hasConfirmedChanges, setHasConfirmedChanges] = useState(
    locationData ? locationData.manual_location : false
  );

  const [isEditModeEnabled, setIsEditModeEnabled] = useState(false);

  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [isConfirmationModalOpen, setIsConfirmationModalOpen] = useState(false);
  const [isWorkPackageLocation, setIsWorkPackageLocation] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const [originalValues, setOriginalValues] = useState<originalLocationValues>({
    location: "",
    latitude: "",
    longitude: "",
    locationDescription: "",
  });

  useEffect(() => {
    const currentPage = state.form.contents.find(
      (content: any) => content.id === activePageDetails?.id
    );
    if (currentPage?.properties.page_update_status === "saved") {
      setIsSubmitted(true);
    }
  }, [state.form.contents, activePageDetails?.id]);

  const [pendingAction, setPendingAction] = useState<pendingAction | null>(
    null
  );

  const [validationError, setValidationError] = useState(false);

  const [userLocationLatitude, setUserLocationLatitude] = useState("");
  const [userLocationLongitude, setUserLocationLongitude] = useState("");

  const [createLocationFromLatLon] = useMutation(createLocation);

  const populateFromRouterData = React.useCallback(() => {
    if (
      workPackageLocationLatitude &&
      workPackageLocationLongitude &&
      projectDetails?.project.locations?.[0]?.name
    ) {
      const locationName = projectDetails.project.locations[0].name;
      const lat = workPackageLocationLatitude.toString();
      const lng = workPackageLocationLongitude.toString();

      const locationDataToDispatch: LocationUserValueType = {
        name: locationName,
        gps_coordinates: {
          latitude: lat,
          longitude: lng,
        },
        description: description ?? "",
        manual_location: false,
      };

      dispatch({
        type: CF_REDUCER_CONSTANTS.LOCATION_VALUE_CHANGE,
        payload: locationDataToDispatch,
      });
    }
  }, [
    workPackageLocationLatitude,
    workPackageLocationLongitude,
    projectDetails,
    description,
    dispatch,
  ]);

  useEffect(() => {
    if (isClearingRef.current) {
      isClearingRef.current = false;
      return;
    }

    if (latitude && longitude && !isInitialLoad) {
      return;
    }
    if (locationData) {
      const locationName = name ?? "";
      const lat = gps_coordinates?.latitude ?? "";
      const lng = gps_coordinates?.longitude ?? "";
      const desc = description ?? "";

      setLocation(locationName);
      setLatitude(lat);
      setLongitude(lng);
      setLocationDescription(desc);
      setIsWorkPackageLocation(!!workPackageId);

      setOriginalValues({
        location: locationName,
        latitude: lat,
        longitude: lng,
        locationDescription: desc,
      });

      setIsInitialLoad(false);
    } else if (workPackageLocationId && projectDetails) {
      populateFromRouterData();
      setIsInitialLoad(false);
    } else if (isInitialLoad && !locationData && !workPackageLocationId) {
      setIsInitialLoad(false);
    }
  }, [
    locationData,
    workPackageLocationId,
    projectDetails,
    isInitialLoad,
    populateFromRouterData,
  ]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (item.properties.is_mandatory) {
          if (!state.form.component_data?.location_data?.name.trim()) {
            setValidationError(true);
            return;
          }
        }

        // Create location if manual_location is true and we have GPS coordinates
        const currentLocationData = state.form.component_data?.location_data;
        if (
          currentLocationData?.manual_location &&
          currentLocationData?.gps_coordinates?.latitude &&
          currentLocationData?.gps_coordinates?.longitude
        ) {
          try {
            createLocationFromLatLon({
              variables: {
                date: state.form.properties.report_start_date
                  ? state.form.properties.report_start_date
                  : state.form.created_at,
                name: "createLocationFromLatLon",
                gpsCoordinates: {
                  latitude: parseFloat(
                    currentLocationData.gps_coordinates.latitude
                  ),
                  longitude: parseFloat(
                    currentLocationData.gps_coordinates.longitude
                  ),
                },
              },
            });
          } catch (e) {
            toastCtx?.pushToast("error", "Failed to create location");
          }
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [
    location,
    createLocationFromLatLon,
    toastCtx,
    state.form.component_data?.location_data,
  ]);

  const shouldShowConfirmation = React.useMemo(() => {
    return (
      (workPackageId &&
        !hasConfirmedChanges &&
        !isInitialLoad &&
        mode === UserFormModeTypes.EDIT) ||
      (isSubmitted && !isEditModeEnabled && mode === UserFormModeTypes.EDIT)
    );
  }, [
    workPackageId,
    hasConfirmedChanges,
    isInitialLoad,
    mode,
    isSubmitted,
    isEditModeEnabled,
  ]);

  const handleLocationDispatch = (value: string, type: string) => {
    const newLatitude =
      type === UserLocationCoordinates.LATITUDE ? value : latitude;
    const newLongitude =
      type === UserLocationCoordinates.LONGITUDE ? value : longitude;
    const shouldSetManualLocation =
      !workPackageLocationId || hasConfirmedChanges;
    const manualLocation =
      workPackageId && location == state.form.metadata?.location?.name
        ? false
        : true;
    const revisedValues: LocationUserValueType = {
      name: type === "location" ? value : location,
      gps_coordinates:
        (newLatitude && String(newLatitude).trim() !== "") ||
        (newLongitude && String(newLongitude).trim() !== "")
          ? {
              latitude: newLatitude.toString(),
              longitude: newLongitude.toString(),
            }
          : null,
      description: type === "description" ? value : locationDescription,
      manual_location: workPackageLocationId
        ? shouldSetManualLocation
        : manualLocation,
    };
    const isLocationSame = (
      location1: LocationUserValueType | undefined,
      location2: LocationUserValueType | undefined
    ) => {
      const coords1 = location1?.gps_coordinates;
      const coords2 = location2?.gps_coordinates;

      if (location1?.name !== location2?.name) {
        return false;
      }

      if (!coords1 && !coords2) {
        return true;
      }

      if (!coords1 || !coords2) {
        return false;
      }

      const lat1 = Number(coords1.latitude);
      const lng1 = Number(coords1.longitude);
      const lat2 = Number(coords2.latitude);
      const lng2 = Number(coords2.longitude);

      return lat1 === lat2 && lng1 === lng2;
    };

    if (
      mode === UserFormModeTypes.EDIT &&
      ((hasConfirmedChanges &&
        !isLocationSame(initialLocationData.current, revisedValues)) ||
        (initialLocationData?.current?.description &&
          initialLocationData?.current?.description !==
            revisedValues.description))
    ) {
      setCWFFormStateDirty(true);
    }

    dispatch({
      type: CF_REDUCER_CONSTANTS.LOCATION_VALUE_CHANGE,
      payload: revisedValues,
    });

    if (
      mode === UserFormModeTypes.EDIT &&
      hasConfirmedChanges &&
      !isLocationSame(locationData, revisedValues)
    ) {
      dispatch({
        type: CF_REDUCER_CONSTANTS.SET_SITE_CONDITIONS_HAZARD_DATA,
        payload: [],
      });

      dispatch({
        type: CF_REDUCER_CONSTANTS.SITE_CONDITIONS_VALUE_CHANGE,
        payload: [],
      });
    }
  };
  const handleInputRawChange = (value: string) => {
    if (shouldShowConfirmation) {
      setPendingAction({ type: "inputRaw", value });
      setIsConfirmationModalOpen(true);
      return;
    }

    setLocation(value);
    handleLocationDispatch(value, "location");
  };

  const handleOnLocationChange = (value: string) => {
    locationForwardRef.current = true;
    locationReverseRef.current = false;

    if (value && shouldShowConfirmation) {
      setPendingAction({ type: "locationChange", value });
      setIsConfirmationModalOpen(true);
      return;
    }
    setLocation(value);
    handleLocationDispatch(value, "location");
  };

  const handleGeolocationError = (message: string) => {
    toastCtx?.pushToast("error", message);
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
          if (!isWorkPackageLocation || hasConfirmedChanges) {
            setLocation(address);
            handleLocationDispatch(address, "location");
          }
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

  const debouncedReverseGeoCode = React.useCallback(
    debounce((lat: number, lng: number) => {
      reverseGeoCode({ lat, lng });
    }, 1000),
    []
  );

  useEffect(() => {
    if (
      isInitialLoad ||
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
  }, [latitude, longitude, isInitialLoad]);

  useEffect(() => {
    return () => {
      debouncedReverseGeoCode.cancel();
    };
  }, [debouncedReverseGeoCode]);

  const checkValidCoordinates = (
    coordinate: string,
    coordinateType: string
  ) => {
    switch (coordinateType) {
      case UserLocationCoordinates.LATITUDE:
        if (
          coordinate &&
          (Number(coordinate) < -90 || Number(coordinate) > 90)
        ) {
          handleGeolocationError("Latitude must be between -90 to 90");
          return true;
        }
        break;
      case UserLocationCoordinates.LONGITUDE:
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

  const handleLatitudeChange = (value: string) => {
    locationReverseRef.current = true;
    locationForwardRef.current = false;

    if (checkValidCoordinates(value, UserLocationCoordinates.LATITUDE)) return;

    if (shouldShowConfirmation) {
      setPendingAction({ type: UserLocationCoordinates.LATITUDE, value });
      setIsConfirmationModalOpen(true);
      return;
    }

    setLatitude(value);
    handleLocationDispatch(value, UserLocationCoordinates.LATITUDE);
  };

  const handleLongitudeChange = (value: string) => {
    locationReverseRef.current = true;
    locationForwardRef.current = false;

    if (checkValidCoordinates(value, UserLocationCoordinates.LONGITUDE)) return;

    if (shouldShowConfirmation) {
      setPendingAction({ type: UserLocationCoordinates.LONGITUDE, value });
      setIsConfirmationModalOpen(true);
      return;
    }

    setLongitude(value);
    handleLocationDispatch(value, UserLocationCoordinates.LONGITUDE);
  };

  const handleLocationDescriptionChange = (value: string) => {
    setLocationDescription(value);
    handleLocationDispatch(value, "description");
  };

  const setCurrentLocation = () => {
    if (shouldShowConfirmation) {
      setPendingAction({ type: "currentLocation" });
      setIsConfirmationModalOpen(true);
      return;
    }
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
        }
      );
    } else {
      handleGeolocationError("Geolocation is not supported by this browser.");
    }
  };

  useEffect(() => {
    if (navigator.geolocation && isTemplateForms) {
      navigator.geolocation.getCurrentPosition(
        async position => {
          const { latitude: lat, longitude: lng } = position.coords;
          setUserLocationLatitude(String(lat));
          setUserLocationLongitude(String(lng));
        },
        _err => {
          handleGeolocationError(messages.mapErrorNoPermissions);
        }
      );
    }
  }, []);

  const handleLocationMapViewModal = () => {
    setIsLocationMapViewModalOpen(!isLocationMapViewModalOpen);
  };

  const handleMapRender = React.useMemo(() => {
    return isTemplateForms && latitude && longitude;
  }, [isTemplateForms, latitude, longitude]);

  const handleOnClearInput = () => {
    if (shouldShowConfirmation) {
      setPendingAction({ type: "clear" });
      setIsConfirmationModalOpen(true);
      return;
    }

    isClearingRef.current = true;

    setLocation("");
    setLatitude("");
    setLongitude("");

    const clearedValues: LocationUserValueType = {
      name: "",
      gps_coordinates: null,
      description: locationDescription,
      manual_location: !workPackageLocationId || hasConfirmedChanges,
    };

    dispatch({
      type: CF_REDUCER_CONSTANTS.LOCATION_VALUE_CHANGE,
      payload: clearedValues,
    });
  };

  const handleOnCoordinateClear = (coordinateType: UserLocationCoordinates) => {
    if (shouldShowConfirmation) {
      setPendingAction({
        type: `clear${capitalize(coordinateType)}`,
      });
      setIsConfirmationModalOpen(true);
      return;
    }

    if (coordinateType === UserLocationCoordinates.LATITUDE) {
      setLatitude("");
      handleLocationDispatch("", UserLocationCoordinates.LATITUDE);
    } else {
      setLongitude("");
      handleLocationDispatch("", UserLocationCoordinates.LONGITUDE);
    }
  };

  const handleCancelForLocationChange = () => {
    setIsConfirmationModalOpen(false);
    setPendingAction(null);
    setLocation(originalValues.location);
    setLatitude(originalValues.latitude);
    setLongitude(originalValues.longitude);
    handleLocationDispatch(originalValues.location, "location");
  };

  const handleConfirmForLocationChange = () => {
    setIsConfirmationModalOpen(false);
    setIsEditModeEnabled(true);
    setHasConfirmedChanges(true);
    setIsWorkPackageLocation(false);

    if (pendingAction) {
      switch (pendingAction.type) {
        case "inputRaw":
        case "locationChange":
          setLocation(pendingAction.value!);
          handleLocationDispatch(pendingAction.value!, "location");
          if (pendingAction.type === "locationChange") {
            locationForwardRef.current = true;
            locationReverseRef.current = false;
          }
          break;
        case UserLocationCoordinates.LATITUDE:
          setLatitude(pendingAction.value!);
          handleLocationDispatch(
            pendingAction.value!,
            UserLocationCoordinates.LATITUDE
          );
          locationReverseRef.current = true;
          locationForwardRef.current = false;
          break;
        case UserLocationCoordinates.LONGITUDE:
          setLongitude(pendingAction.value!);
          handleLocationDispatch(
            pendingAction.value!,
            UserLocationCoordinates.LONGITUDE
          );
          locationReverseRef.current = true;
          locationForwardRef.current = false;
          break;
        case "clear":
          isClearingRef.current = true;
          setLocation("");
          setLatitude("");
          setLongitude("");

          const clearedValues: LocationUserValueType = {
            name: "",
            gps_coordinates: null,
            description: locationDescription,
            manual_location: !workPackageLocationId || hasConfirmedChanges,
          };

          dispatch({
            type: CF_REDUCER_CONSTANTS.LOCATION_VALUE_CHANGE,
            payload: clearedValues,
          });
          break;
        case "currentLocation":
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
              }
            );
          } else {
            handleGeolocationError(
              "Geolocation is not supported by this browser."
            );
          }
          break;
        case "clearLatitude":
          setLatitude("");
          handleLocationDispatch("", UserLocationCoordinates.LATITUDE);
          break;
        case "clearLongitude":
          setLongitude("");
          handleLocationDispatch("", UserLocationCoordinates.LONGITUDE);
          break;
        default:
          return;
      }
      setPendingAction(null);
    }
  };

  return (
    <div
      className={`flex flex-col gap-2 ${
        mode === UserFormModeTypes.BUILD ? "" : "bg-gray-100"
      } p-4`}
    >
      <div className="flex flex-col md:flex-row gap-4">
        <div className="w-full">
          <ComponentLabel>
            {item.properties.title ?? "Location"}
            {item.properties.is_mandatory && !inSummary ? "*" : ""}
          </ComponentLabel>
          {isWorkPackageLocation && !hasConfirmedChanges ? (
            <div>
              <InputRaw
                onChange={handleInputRawChange}
                value={location}
                disabled={isFormDisabled(mode)}
                icon={"search"}
                clearIcon={true}
                placeholder="Search Location"
                onClear={handleOnClearInput}
                hasError={validationError}
              />
              {validationError && (
                <span className={style.errorMessage}>{"This is required"}</span>
              )}
            </div>
          ) : (
            <LocationSearchUsingAPI
              mode={mode}
              onChange={handleOnLocationChange}
              properties={item.properties}
              value={location}
              setLatitude={setLatitude}
              setLongitude={setLongitude}
              userLocationLatitude={Number(userLocationLatitude)}
              userLocationLongitude={Number(userLocationLongitude)}
              onClear={handleOnClearInput}
            />
          )}
        </div>
        <div className="mt-6 w-auto isolate">
          <div
            className="inline-block isolate relative z-10"
            onClick={e => e.stopPropagation()}
          >
            <ButtonSecondary
              iconStart="target"
              disabled={isFormDisabled(mode)}
              label="Locate Me"
              className="flex justify-end gap-2 w-full sm:w-auto focus:outline-none focus:ring-2 focus:ring-brand-gray-60 focus:ring-offset-1 active:ring-2 active:ring-brand-gray-60 isolate"
              onClick={e => {
                e.stopPropagation();
                e.preventDefault();
                setCurrentLocation();
              }}
            />
          </div>
        </div>
      </div>
      {mode !== UserFormModeTypes.BUILD && (
        <>
          <div className="flex flex-1  flex-col md:flex-row gap-5">
            <div className="w-full ">
              <InputRaw
                type="number"
                label="Latitude"
                disabled={isFormDisabled(mode)}
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
                disabled={isFormDisabled(mode)}
                clearIcon={true}
                value={longitude}
                onChange={handleLongitudeChange}
                onClear={() =>
                  handleOnCoordinateClear(UserLocationCoordinates.LONGITUDE)
                }
              />
            </div>
          </div>
          <div className="flex flex-row gap-4">
            <div className="w-full">
              <ComponentLabel>Location Description</ComponentLabel>
              <Input
                type="text"
                label="Location Description"
                disabled={isFormDisabled(mode)}
                value={locationDescription}
                onChange={e =>
                  handleLocationDescriptionChange(
                    (e.target as HTMLInputElement).value
                  )
                }
              />
            </div>
          </div>
        </>
      )}
      {handleMapRender && (
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
      <LocationMapViewModal
        latitude={latitude.toString()}
        longitude={longitude.toString()}
        isOpen={isLocationMapViewModalOpen}
        closeModal={handleLocationMapViewModal}
        location={location}
        locationDescription={locationDescription}
        modalMapView={false}
      />
      <ConfirmDateChangeModal
        isOpen={isConfirmationModalOpen}
        onConfirm={handleConfirmForLocationChange}
        onCancel={handleCancelForLocationChange}
        isForLocationCheck={true}
      />
    </div>
  );
};
export default CWFLocation;
