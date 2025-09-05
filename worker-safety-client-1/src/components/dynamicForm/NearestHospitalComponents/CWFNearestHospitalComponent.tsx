import type { MedicalFacility } from "@/api/codecs";
import type { ApiResult } from "@/api/api";
import type { Deferred } from "@/utils/deferred";
import type {
  ActivePageObjType,
  CWFNearestHospitalType,
  UserFormMode,
  NearestHospitalUserValueType,
} from "@/components/templatesComponents/customisedForm.types";
import React, { useContext, useEffect, useState, useMemo, useRef } from "react";
import { BodyText, Icon } from "@urbint/silica";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import { Select } from "@/components/forms/Basic/Select";
import { OptionalView } from "@/components/common/Optional";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import { useApi } from "@/api/api";
import { Resolved, InProgress, NotStarted } from "@/utils/deferred";
import Input from "@/components/shared/input/Input";
import { isFormDisabled } from "@/components/templatesComponents/PreviewComponents/textUtils";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import { RenderNearestHospitalInSummary } from "./RenderNearestHospitalInSummary";

const showDistance = (distance: number): string =>
  `${Math.round(distance * 10) / 10}mi`;

const optionToNull = (option: any): any => {
  return option &&
    typeof option === "object" &&
    "_tag" in option &&
    option._tag === "Some"
    ? option.value
    : null;
};

const someValue = (value: any): any => ({ _tag: "Some", value });
const noneValue = (): any => ({ _tag: "None" });

type MedicalFacilityLabel = {
  name: string;
  distance: number | null;
};

type MedicalFacilityValue =
  | {
      type: "Listed";
      facility: MedicalFacility;
    }
  | {
      type: "Other";
    };

type MedicalFacilityOption = {
  label: MedicalFacilityLabel;
  value: MedicalFacilityValue;
};

const eqMedicalFacilityValue = {
  equals: (a: MedicalFacilityValue, b: MedicalFacilityValue): boolean => {
    if (a.type === "Listed" && b.type === "Listed") {
      return a.facility.description === b.facility.description;
    } else {
      return a.type === b.type;
    }
  },
};

const CWFNearestHospital = ({
  item,
  mode,
  inSummary = false,
}: {
  item: CWFNearestHospitalType;
  activePageDetails: ActivePageObjType;
  section: any;
  mode: UserFormMode;
  inSummary?: boolean;
}): JSX.Element => {
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const apiOption = useApi();

  const [nearestMedicalFacilities, setNearestMedicalFacilities] =
    useState<Deferred<ApiResult<MedicalFacility[]>>>(NotStarted);
  const [selectedMedicalFacility, setSelectedMedicalFacility] =
    useState<MedicalFacilityValue | null>(null);
  const [otherMedicalFacilityDescription, setOtherMedicalFacilityDescription] =
    useState("");

  const locationData = state.form.component_data?.location_data;
  const nearestHospitalData = state.form.component_data?.nearest_hospital;

  const [lastCoordinates, setLastCoordinates] = useState<{
    lat?: string;
    lon?: string;
  } | null>(null);

  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const prevLocationDataRef = useRef<{
    lat?: string;
    lon?: string;
  } | null>(null);

  const isMountedRef = useRef(true);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);
  // Auto-select facility when data loads
  useEffect(() => {
    if (
      mode !== UserFormModeTypes.EDIT ||
      nearestMedicalFacilities.status !== "Resolved"
    ) {
      return;
    }

    const facilities = nearestMedicalFacilities.value;

    if ("left" in facilities) {
      if (selectedMedicalFacility?.type !== "Other" && isMountedRef.current) {
        setSelectedMedicalFacility({ type: "Other" });
        setOtherMedicalFacilityDescription("");

        dispatch({
          type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
          payload: {
            name: "",
            phone_number: "",
            other: true,
            distance: "",
            description: "",
          },
        });
      }
      return;
    }

    const facilitiesArray = facilities.right;

    // Check if currently selected facility exists in the new list
    if (selectedMedicalFacility?.type === "Listed") {
      const currentFacilityExists = facilitiesArray.some(
        facility =>
          facility.description === selectedMedicalFacility.facility.description
      );

      if (!currentFacilityExists && isMountedRef.current) {
        if (facilitiesArray.length > 0) {
          // Select the first available facility
          const firstFacility = facilitiesArray[0];
          const facilityValue: MedicalFacilityValue = {
            type: "Listed",
            facility: firstFacility,
          };

          setSelectedMedicalFacility(facilityValue);

          const facilityData: NearestHospitalUserValueType = {
            name: firstFacility.description,
            description: [
              optionToNull(firstFacility.address),
              optionToNull(firstFacility.state),
              optionToNull(firstFacility.city),
              optionToNull(firstFacility.zip),
            ]
              .filter(Boolean)
              .join(", "),
            phone_number: optionToNull(firstFacility.phoneNumber) || "",
            other: false,
            distance: optionToNull(firstFacility.distanceFromJob)
              ? String(
                  showDistance(
                    optionToNull(firstFacility.distanceFromJob) as number
                  )
                )
              : "",
          };

          dispatch({
            type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
            payload: facilityData,
          });
        } else {
          // Switch to "Other" if no facilities are available
          setSelectedMedicalFacility({ type: "Other" });
          setOtherMedicalFacilityDescription("");

          dispatch({
            type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
            payload: {
              name: "",
              phone_number: "",
              other: true,
              distance: "",
              description: "",
            },
          });
        }
        return;
      }
    }

    // If "Other" is selected and facilities are available, select the first facility
    if (
      selectedMedicalFacility?.type === "Other" &&
      facilitiesArray.length > 0 &&
      isMountedRef.current
    ) {
      const firstFacility = facilitiesArray[0];
      const facilityValue: MedicalFacilityValue = {
        type: "Listed",
        facility: firstFacility,
      };

      setSelectedMedicalFacility(facilityValue);

      const facilityData: NearestHospitalUserValueType = {
        name: firstFacility.description,
        description: [
          optionToNull(firstFacility.address),
          optionToNull(firstFacility.state),
          optionToNull(firstFacility.city),
          optionToNull(firstFacility.zip),
        ]
          .filter(Boolean)
          .join(", "),
        phone_number: optionToNull(firstFacility.phoneNumber) || "",
        other: false,
        distance: optionToNull(firstFacility.distanceFromJob)
          ? String(
              showDistance(
                optionToNull(firstFacility.distanceFromJob) as number
              )
            )
          : "",
      };

      dispatch({
        type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
        payload: facilityData,
      });
      return;
    }

    if (
      !selectedMedicalFacility &&
      facilitiesArray.length > 0 &&
      isMountedRef.current
    ) {
      const firstFacility = facilitiesArray[0];
      const facilityValue: MedicalFacilityValue = {
        type: "Listed",
        facility: firstFacility,
      };

      setSelectedMedicalFacility(facilityValue);

      const facilityData: NearestHospitalUserValueType = {
        name: firstFacility.description,
        description: [
          optionToNull(firstFacility.address),
          optionToNull(firstFacility.state),
          optionToNull(firstFacility.city),
          optionToNull(firstFacility.zip),
        ]
          .filter(Boolean)
          .join(", "),
        phone_number: optionToNull(firstFacility.phoneNumber) || "",
        other: false,
        distance: optionToNull(firstFacility.distanceFromJob)
          ? String(
              showDistance(
                optionToNull(firstFacility.distanceFromJob) as number
              )
            )
          : "",
      };

      dispatch({
        type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
        payload: facilityData,
      });
    } else if (
      !selectedMedicalFacility &&
      facilitiesArray.length === 0 &&
      isMountedRef.current
    ) {
      setSelectedMedicalFacility({ type: "Other" });
      setOtherMedicalFacilityDescription("");

      dispatch({
        type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
        payload: {
          name: "",
          phone_number: "",
          other: true,
          distance: "",
          description: "",
        },
      });
    }
  }, [nearestMedicalFacilities, mode]);

  // Update form state when "Other" is selected
  useEffect(() => {
    if (selectedMedicalFacility?.type === "Other" && isMountedRef.current) {
      dispatch({
        type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
        payload: {
          name: otherMedicalFacilityDescription,
          phone_number: "",
          other: true,
          distance: "",
          description: "",
        },
      });
    }
  }, [selectedMedicalFacility?.type, otherMedicalFacilityDescription]);

  // Clear selection when location data is removed
  useEffect(() => {
    const currentLat = locationData?.gps_coordinates?.latitude;
    const currentLon = locationData?.gps_coordinates?.longitude;

    const prevLocationData = prevLocationDataRef.current;
    const hasLocationData = currentLat && currentLon;
    const hadLocationData = prevLocationData?.lat && prevLocationData?.lon;

    if (
      hadLocationData &&
      !hasLocationData &&
      selectedMedicalFacility !== null &&
      isMountedRef.current
    ) {
      setSelectedMedicalFacility(null);
      setOtherMedicalFacilityDescription("");

      dispatch({
        type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
        payload: {
          name: "",
          phone_number: "",
          other: false,
          distance: "",
          description: "",
        },
      });
    }

    prevLocationDataRef.current = {
      lat: currentLat,
      lon: currentLon,
    };
  }, [
    locationData?.gps_coordinates?.latitude,
    locationData?.gps_coordinates?.longitude,
  ]);

  // Reset when coordinates change
  useEffect(() => {
    const currentLat = locationData?.gps_coordinates?.latitude;
    const currentLon = locationData?.gps_coordinates?.longitude;

    if (currentLat && currentLon) {
      const coordinatesChanged =
        lastCoordinates &&
        lastCoordinates.lat &&
        lastCoordinates.lon &&
        (lastCoordinates.lat !== String(currentLat) ||
          lastCoordinates.lon !== String(currentLon));
      if (
        coordinatesChanged &&
        nearestHospitalData?.name &&
        isMountedRef.current
      ) {
        setNearestMedicalFacilities(NotStarted);
        setSelectedMedicalFacility(null);
        setOtherMedicalFacilityDescription("");
        dispatch({
          type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
          payload: {
            name: "",
            phone_number: "",
            other: false,
            distance: "",
            description: "",
          },
        });
      }

      setLastCoordinates({ lat: String(currentLat), lon: String(currentLon) });
    }
  }, [
    locationData?.gps_coordinates?.latitude,
    locationData?.gps_coordinates?.longitude,
  ]);

  // Fetch facilities when location data is available
  useEffect(() => {
    if (mode !== UserFormModeTypes.EDIT) {
      return;
    }
    const apiAvailable =
      apiOption &&
      typeof apiOption === "object" &&
      "_tag" in apiOption &&
      apiOption._tag === "Some";

    if (
      apiAvailable &&
      locationData?.gps_coordinates?.latitude &&
      locationData?.gps_coordinates?.longitude
    ) {
      if (
        nearestMedicalFacilities.status === "NotStarted" &&
        isMountedRef.current
      ) {
        setSelectedMedicalFacility(null);
        setOtherMedicalFacilityDescription("");
      }

      if (isMountedRef.current) {
        setNearestMedicalFacilities(InProgress);
      }
      const api = (apiOption as any).value;
      const coordinates = {
        latitude: parseFloat(locationData.gps_coordinates.latitude),
        longitude: parseFloat(locationData.gps_coordinates.longitude),
      };

      api.jsb
        .getNearestMedicalFacilities(coordinates)()
        .then((result: any) => {
          if (isMountedRef.current) {
            setNearestMedicalFacilities(Resolved(result));
          }
        })
        .catch((apiError: any) => {
          if (isMountedRef.current) {
            const errorResult = { left: { _tag: "Left", value: apiError } };
            setNearestMedicalFacilities(Resolved(errorResult as any));
          }
        });
    }
  }, [
    locationData?.gps_coordinates?.latitude,
    locationData?.gps_coordinates?.longitude,
    mode,
  ]);

  // Fetch when component comes into view
  useEffect(() => {
    if (mode !== UserFormModeTypes.EDIT || !isMountedRef.current) {
      return;
    }

    const apiAvailable =
      apiOption &&
      typeof apiOption === "object" &&
      "_tag" in apiOption &&
      apiOption._tag === "Some";
    if (
      apiAvailable &&
      locationData?.gps_coordinates?.latitude &&
      locationData?.gps_coordinates?.longitude &&
      nearestMedicalFacilities.status === "NotStarted"
    ) {
      setNearestMedicalFacilities(InProgress);
      const api = (apiOption as any).value;
      const coordinates = {
        latitude: parseFloat(locationData.gps_coordinates.latitude),
        longitude: parseFloat(locationData.gps_coordinates.longitude),
      };

      api.jsb
        .getNearestMedicalFacilities(coordinates)()
        .then((result: any) => {
          if (isMountedRef.current) {
            setNearestMedicalFacilities(Resolved(result));
          }
        })
        .catch((apiError: any) => {
          if (isMountedRef.current) {
            const errorResult = { left: { _tag: "Left", value: apiError } };
            setNearestMedicalFacilities(Resolved(errorResult as any));
          }
        });
    }
  }, [mode]);

  // Retry when API becomes available
  useEffect(() => {
    if (mode !== UserFormModeTypes.EDIT || !isMountedRef.current) {
      return;
    }

    const apiAvailable =
      apiOption &&
      typeof apiOption === "object" &&
      "_tag" in apiOption &&
      apiOption._tag === "Some";

    if (
      apiAvailable &&
      locationData?.gps_coordinates?.latitude &&
      locationData?.gps_coordinates?.longitude &&
      nearestMedicalFacilities.status === "NotStarted"
    ) {
      setNearestMedicalFacilities(InProgress);
      const api = (apiOption as any).value;
      const coordinates = {
        latitude: parseFloat(locationData.gps_coordinates.latitude),
        longitude: parseFloat(locationData.gps_coordinates.longitude),
      };

      api.jsb
        .getNearestMedicalFacilities(coordinates)()
        .then((result: any) => {
          if (isMountedRef.current) {
            setNearestMedicalFacilities(Resolved(result));
          }
        })
        .catch((apiError: any) => {
          if (isMountedRef.current) {
            const errorResult = { left: { _tag: "Left", value: apiError } };
            setNearestMedicalFacilities(Resolved(errorResult as any));
          }
        });
    }
  }, [
    apiOption,
    locationData?.gps_coordinates?.latitude,
    locationData?.gps_coordinates?.longitude,
    mode,
  ]);

  // Initialize from existing data
  useEffect(() => {
    if (
      nearestHospitalData &&
      (nearestHospitalData.name || nearestHospitalData.other === true)
    ) {
      if (nearestHospitalData.other === true) {
        setSelectedMedicalFacility({ type: "Other" });
        setOtherMedicalFacilityDescription(nearestHospitalData.name || "");
      } else {
        if (nearestMedicalFacilities.status === "Resolved") {
          const facilities = nearestMedicalFacilities.value;

          if ("left" in facilities) {
            const savedFacility: MedicalFacility = {
              description: nearestHospitalData.name,
              distanceFromJob: nearestHospitalData.distance
                ? someValue(
                    parseFloat(nearestHospitalData.distance.replace("mi", ""))
                  )
                : noneValue(),
              address: noneValue(),
              city: noneValue(),
              phoneNumber: noneValue(),
              state: noneValue(),
              zip: noneValue(),
            };
            setSelectedMedicalFacility({
              type: "Listed",
              facility: savedFacility,
            });
            setOtherMedicalFacilityDescription("");
          } else {
            const facilitiesArray = facilities.right;
            const matchingFacility = facilitiesArray.find(
              facility => facility.description === nearestHospitalData.name
            );

            if (matchingFacility) {
              setSelectedMedicalFacility({
                type: "Listed",
                facility: matchingFacility,
              });
              setOtherMedicalFacilityDescription("");
            } else {
              const savedFacility: MedicalFacility = {
                description: nearestHospitalData.name,
                distanceFromJob: nearestHospitalData.distance
                  ? someValue(
                      parseFloat(nearestHospitalData.distance.replace("mi", ""))
                    )
                  : noneValue(),
                address: noneValue(),
                city: noneValue(),
                phoneNumber: noneValue(),
                state: noneValue(),
                zip: noneValue(),
              };
              setSelectedMedicalFacility({
                type: "Listed",
                facility: savedFacility,
              });
              setOtherMedicalFacilityDescription("");
            }
          }
        } else {
          const savedFacility: MedicalFacility = {
            description: nearestHospitalData.name,
            distanceFromJob: nearestHospitalData.distance
              ? someValue(
                  parseFloat(nearestHospitalData.distance.replace("mi", ""))
                )
              : noneValue(),
            address: noneValue(),
            city: noneValue(),
            phoneNumber: noneValue(),
            state: noneValue(),
            zip: noneValue(),
          };
          const facilitySelection = {
            type: "Listed" as const,
            facility: savedFacility,
          };
          setSelectedMedicalFacility(facilitySelection);
          setOtherMedicalFacilityDescription("");
        }
      }
    } else {
      // No existing data, reset selections
      setSelectedMedicalFacility(null);
      setOtherMedicalFacilityDescription("");
    }
  }, [nearestHospitalData, nearestMedicalFacilities]);

  // Validation on save and continue
  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (item.properties.is_mandatory) {
          if (!state.form.component_data?.nearest_hospital?.name.trim()) {
            setError(true);
            setErrorMessage("This is required");
          }
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [
    selectedMedicalFacility,
    otherMedicalFacilityDescription,
    item.properties.is_mandatory,
    state.form.component_data?.nearest_hospital?.name,
  ]);

  const medicalFacilitiesPlaceholder = useMemo(() => {
    if (mode !== UserFormModeTypes.EDIT) {
      return "Select nearest medical facility";
    }

    if (
      !locationData?.gps_coordinates?.latitude ||
      !locationData?.gps_coordinates?.longitude
    ) {
      return "Select nearest medical facility";
    }

    switch (nearestMedicalFacilities.status) {
      case "NotStarted":
        return nearestHospitalData?.name
          ? "Select nearest medical facility"
          : "Other";
      case "InProgress":
        return "Loading nearest medical facilities...";
      case "Resolved":
        return "Select nearest medical facility";
    }
  }, [locationData, nearestMedicalFacilities, mode, nearestHospitalData?.name]);

  const medicalFacilityOptions = useMemo(() => {
    const otherOption: MedicalFacilityOption = {
      label: { name: "Other", distance: null },
      value: { type: "Other" },
    };

    const savedFacilityOption: MedicalFacilityOption[] = [];
    if (nearestHospitalData?.name && nearestHospitalData.other !== true) {
      const savedFacility: MedicalFacility = {
        description: nearestHospitalData.name,
        distanceFromJob: nearestHospitalData.distance
          ? someValue(
              parseFloat(nearestHospitalData.distance.replace("mi", ""))
            )
          : noneValue(),
        address: noneValue(),
        city: noneValue(),
        phoneNumber: noneValue(),
        state: noneValue(),
        zip: noneValue(),
      };
      savedFacilityOption.push({
        label: {
          name: nearestHospitalData.name,
          distance: nearestHospitalData.distance
            ? parseFloat(nearestHospitalData.distance.replace("mi", ""))
            : null,
        },
        value: { type: "Listed", facility: savedFacility },
      });
    }

    if (
      !locationData?.gps_coordinates?.latitude ||
      !locationData?.gps_coordinates?.longitude
    ) {
      return [...savedFacilityOption, otherOption];
    }

    switch (nearestMedicalFacilities.status) {
      case "NotStarted":
        return [...savedFacilityOption, otherOption];
      case "InProgress":
        return [...savedFacilityOption, otherOption];
      case "Updating":
        return [...savedFacilityOption, otherOption];
      case "Resolved":
        const facilities = nearestMedicalFacilities.value;

        if ("left" in facilities) {
          return [...savedFacilityOption, otherOption];
        } else {
          const facilitiesArray = facilities.right;
          const facilityOptions: MedicalFacilityOption[] = facilitiesArray.map(
            (facility): MedicalFacilityOption => ({
              label: {
                name: facility.description,
                distance: optionToNull(facility.distanceFromJob),
              },
              value: { type: "Listed", facility },
            })
          );

          const uniqueFacilities = facilityOptions.filter(
            facilityOption =>
              facilityOption.label.name !== nearestHospitalData?.name
          );

          const finalOptions = [
            ...savedFacilityOption,
            ...uniqueFacilities,
            otherOption,
          ];
          return finalOptions;
        }
    }
  }, [locationData, nearestMedicalFacilities, nearestHospitalData]);

  const handleMedicalFacilityChange = (value: any) => {
    const nullableValue =
      value &&
      typeof value === "object" &&
      "_tag" in value &&
      value._tag === "Some"
        ? value.value
        : null;
    setSelectedMedicalFacility(nullableValue);
    if (
      value &&
      typeof value === "object" &&
      "_tag" in value &&
      value._tag === "Some"
    ) {
      const facilityValue = value.value;
      if (facilityValue.type === "Listed") {
        const facilityData: NearestHospitalUserValueType = {
          name: facilityValue.facility.description,
          description:
            [
              optionToNull(facilityValue.facility.address),
              optionToNull(facilityValue.facility.state),
              optionToNull(facilityValue.facility.city),
              optionToNull(facilityValue.facility.zip),
            ]
              .filter(Boolean)
              .join(", ") ||
            (nearestHospitalData
              ? [
                  nearestHospitalData?.description,
                  nearestHospitalData?.state,
                  nearestHospitalData?.city,
                  nearestHospitalData?.zip_code,
                ].join(", ")
              : undefined) ||
            undefined,
          phone_number:
            optionToNull(facilityValue.facility.phoneNumber) ||
            nearestHospitalData?.phone_number ||
            "",
          other: false,
          distance:
            optionToNull(facilityValue.facility.distanceFromJob) === null
              ? nearestHospitalData?.distance || ""
              : String(
                  showDistance(
                    optionToNull(
                      facilityValue.facility.distanceFromJob
                    ) as number
                  )
                ),
        };
        dispatch({
          type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
          payload: facilityData,
        });
      } else {
        const facilityData: NearestHospitalUserValueType = {
          name: otherMedicalFacilityDescription,
          phone_number: "",
          other: true,
          distance: "",
        };

        dispatch({
          type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
          payload: facilityData,
        });
      }
    } else {
      dispatch({
        type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
        payload: {
          name: "",
          phone_number: "",
          other: false,
          distance: "",
          description: "",
        },
      });
    }
  };

  const handleOtherDescriptionChange = (value: string) => {
    setOtherMedicalFacilityDescription(value);

    if (
      selectedMedicalFacility !== null &&
      selectedMedicalFacility.type === "Other"
    ) {
      const facilityData: NearestHospitalUserValueType = {
        name: value,
        phone_number: nearestHospitalData?.phone_number || "",
        other: true,
        distance: "",
      };

      dispatch({
        type: CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE,
        payload: facilityData,
      });
    }
  };

  const renderLabel = ({ name, distance }: MedicalFacilityLabel) => (
    <div className="inline-grid sm:flex sm:flex-row sm:justify-between sm:items-center flex-1">
      <span className="truncate max-w-md">{name}</span>
      <OptionalView
        value={distance === null ? noneValue() : someValue(distance)}
        render={(d: number) => (
          <span className="text-sm text-brand-gray-70">{showDistance(d)}</span>
        )}
      />
    </div>
  );

  const optionKey = (value: MedicalFacilityValue): string =>
    value.type === "Listed" ? value.facility.description : "other";

  return (
    <>
      {inSummary ? (
        <RenderNearestHospitalInSummary item={item as CWFNearestHospitalType} />
      ) : (
        <div
          id={item.id}
          className={` flex flex-row gap-4 ${
            mode === UserFormModeTypes.BUILD ? "" : "bg-gray-100 p-4"
          }`}
        >
          <div className="w-full">
            {!inSummary && (
              <div>
                <Select
                  options={medicalFacilityOptions}
                  placeholder={medicalFacilitiesPlaceholder}
                  label={`${item.properties.title ?? "Nearest Hospital"}*`}
                  selected={
                    selectedMedicalFacility
                      ? someValue(selectedMedicalFacility)
                      : noneValue()
                  }
                  disabled={
                    isFormDisabled(mode) ||
                    nearestMedicalFacilities.status === "InProgress"
                  }
                  onSelected={value => {
                    handleMedicalFacilityChange(value);
                  }}
                  valueEq={eqMedicalFacilityValue}
                  renderLabel={renderLabel}
                  optionKey={optionKey}
                />

                <div className="mt-2">
                  {selectedMedicalFacility !== null &&
                    selectedMedicalFacility.type === "Other" && (
                      <OptionalView
                        value={
                          (selectedMedicalFacility !== null &&
                            selectedMedicalFacility.type === "Other") ||
                          !locationData?.gps_coordinates?.latitude ||
                          !locationData?.gps_coordinates?.longitude
                            ? someValue({})
                            : noneValue()
                        }
                        render={() => (
                          <Input
                            label="Please specify the nearest medical facility *"
                            value={otherMedicalFacilityDescription}
                            disabled={isFormDisabled(mode)}
                            error={
                              error &&
                              selectedMedicalFacility?.type === "Other" &&
                              otherMedicalFacilityDescription.trim() === ""
                                ? errorMessage
                                : ""
                            }
                            onChange={e => {
                              handleOtherDescriptionChange(
                                (e.target as HTMLInputElement).value
                              );
                            }}
                          />
                        )}
                      />
                    )}
                </div>
              </div>
            )}
            {error &&
              !state.form.component_data?.nearest_hospital?.name.trim() && (
                <div className="text-red-500 ">{errorMessage}</div>
              )}

            {nearestHospitalData && (
              <div>
                {inSummary && (
                  <BodyText>
                    {item.properties.title ?? "Nearest Hospital"}
                  </BodyText>
                )}
                <div className="flex items-center justify-between bg-gray-100 w-full mt-2 p-2">
                  <div className="flex-1">
                    {((nearestHospitalData.other && inSummary) ||
                      !nearestHospitalData.other) && (
                      <BodyText className="text-sm font-semibold mb-2">
                        {nearestHospitalData.name}
                      </BodyText>
                    )}
                    {nearestHospitalData.description && (
                      <div className="flex items-start gap-2 text-sm text-brand-gray-70">
                        <Icon name="location" />
                        <div>{nearestHospitalData.description}</div>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col items-end gap-2 ml-4">
                    {nearestHospitalData.distance && (
                      <span className="text-sm text-gray-500">
                        {nearestHospitalData.distance}
                      </span>
                    )}
                    {nearestHospitalData.phone_number && (
                      <div className="flex items-center gap-2 text-sm text-brand-urbint-40">
                        <Icon name="phone" />
                        <span>{nearestHospitalData.phone_number}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default CWFNearestHospital;
