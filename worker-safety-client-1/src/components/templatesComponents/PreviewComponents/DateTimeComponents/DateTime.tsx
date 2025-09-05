import type {
  UserFormMode,
  DateTimeFormState,
  FieldType,
} from "@/components/templatesComponents/customisedForm.types";
import React, { useEffect, useState, useRef, useContext } from "react";
import { useRouter } from "next/router";
import { gql, useMutation } from "@apollo/client";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import { ConfirmDateChangeModal } from "@/container/report/workSchedule/ConfirmDateChangeModal";

import useCWFFormState from "@/hooks/useCWFFormState";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import CustomisedFromStateContext from "../../../../context/CustomisedDataContext/CustomisedFormStateContext";
import { isDisabledMode } from "../../customisedForm.utils";
import {
  hasDateChanged,
  createAutoPopulatedDate,
  createAutoPopulatedValue,
} from "../dateUtils";
import TimeOnlyComponent from "./TimeOnlyComponent";
import DateOnlyComponent from "./DateOnlyComponent";
import DateRangeComponent from "./DateRangeComponent";

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

type Content = {
  id?: string;
  type: FieldType;
  properties: DateTimeFormState;
};
type Props = {
  content: Content;
  mode: UserFormMode;
  onChange: (value: any) => void;
  withConfirmationDialog?: boolean;
  reportDate?: boolean;
  inSummary?: boolean;
};

// Define a separate error state type for date ranges
type DateRangeErrorState = {
  from: boolean;
  to: boolean;
  message: string;
};

const validate = (
  value: { value?: string; from?: string; to?: string },
  properties: DateTimeFormState
): boolean => {
  let isValid = true;
  if (
    properties.selected_type === "date_time" ||
    properties.selected_type === "date_only"
  ) {
    if (properties.date_type === "date_range") {
      if (!value?.from || !value?.to) {
        return true;
      }

      const givenFromDate = new Date(value.from);
      const givenToDate = new Date(value.to);
      const currentDate = new Date();

      if (givenToDate < givenFromDate) {
        return false;
      }

      if (
        properties.date_validation === "allow_future_date" &&
        (givenToDate < currentDate || givenFromDate < currentDate)
      ) {
        isValid = false;
      } else if (
        properties.date_validation === "allow_past_date" &&
        (givenToDate > currentDate || givenFromDate > currentDate)
      ) {
        isValid = false;
      }
    } else {
      const givenDate = new Date(value?.value || "");
      const currentDate = new Date();
      if (
        properties.date_validation === "allow_future_date" &&
        givenDate < currentDate
      ) {
        isValid = false;
      } else if (
        properties.date_validation === "allow_past_date" &&
        givenDate > currentDate
      ) {
        isValid = false;
      }
    }
  }
  return isValid;
};

export const ModalWrapper = ({
  children,
  withConfirmationDialog,
  isModalOpen,
  handleConfirm,
  handleCancel,
}: {
  children: React.ReactNode;
  withConfirmationDialog?: boolean;
  isModalOpen: boolean;
  handleConfirm: () => void;
  handleCancel: () => void;
}) => (
  <>
    {children}
    {withConfirmationDialog ? (
      <ConfirmDateChangeModal
        isOpen={isModalOpen}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    ) : null}
  </>
);

function DateTime(props: Props) {
  const {
    content: { properties },
    mode,
    withConfirmationDialog,
    reportDate,
    inSummary,
  } = props;
  const router = useRouter();
  const { startDate } = router.query;
  const { setCWFFormStateDirty } = useCWFFormState();
  const toastCtx = useContext(ToastContext);
  // For single date fields
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [isDisabledForm] = useState(isDisabledMode(mode));

  // For date range specific error tracking
  const [rangeError, setRangeError] = useState<DateRangeErrorState>({
    from: false,
    to: false,
    message: "",
  });

  const [localValue, setLocalValue] = useState<any>(properties.user_value);
  const [previousValue, setPreviousValue] = useState<any>(
    properties.user_value
  );
  const [newValue, setNewValue] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [manuallyCleared, setManuallyCleared] = useState<{
    from?: boolean;
    to?: boolean;
    value?: boolean;
  }>({});
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const gps_coordinates =
    state.form?.component_data?.location_data?.gps_coordinates;
  const manual_location =
    state?.form?.component_data?.location_data?.manual_location;
  const [createLocationFromLatLon] = useMutation(createLocation);
  // Track if initial auto-population has happened
  const initialAutoPopulateDone = useRef(false);
  // Track if user has manually changed the value after auto-population
  const hasUserManuallyChanged = useRef(false);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (
          properties?.date_type === "date_range" &&
          !localValue?.from &&
          !localValue?.to
        ) {
          props.onChange(null);
        }
        if (properties.is_mandatory) {
          let isValid = false;

          if (properties?.date_type === "date_range") {
            const fromMissing = !localValue?.from;
            const toMissing = !localValue?.to;

            // Update individual field errors
            setRangeError({
              from: fromMissing,
              to: toMissing,
              message: "This is required",
            });

            if (fromMissing || toMissing) {
              isValid = false;
            } else {
              isValid = true;
            }
          } else {
            isValid = Boolean(localValue?.value);
          }

          if (!isValid) {
            if (properties?.date_type !== "date_range") {
              setError(true);
              setErrorMessage("This is required");
            }
            props.onChange(null);
            return;
          }

          if (!validate(localValue, properties)) {
            const validationMessage =
              properties.date_validation === "allow_future_date"
                ? "Only future dates are allowed"
                : properties.date_validation === "allow_past_date"
                ? "Only past dates are allowed"
                : "Invalid date selection";

            if (properties?.date_type === "date_range") {
              setRangeError({
                from: true,
                to: true,
                message: validationMessage,
              });
            } else {
              setError(true);
              setErrorMessage(validationMessage);
            }
            return;
          }

          // Clear errors on valid submission
          if (properties?.date_type === "date_range") {
            setRangeError({
              from: false,
              to: false,
              message: "",
            });
          } else {
            setError(false);
          }
        }

        // Handle report date logic for save and continue
        if (reportDate) {
          const reportDateValue =
            localValue?.from || localValue?.value || startDate;

          dispatch({
            type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
            payload: {
              ...state.form,
              properties: {
                ...state.form.properties,
                report_start_date: reportDateValue,
              },
            },
          });
        }

        props.onChange(localValue);
      }
    );

    return () => {
      token.remove();
    };
  }, [localValue, properties, props.onChange]);

  useEffect(() => {
    if (
      !initialAutoPopulateDone.current &&
      !properties.user_value &&
      mode != UserFormModeTypes.BUILD &&
      mode != UserFormModeTypes.PREVIEW_PROPS &&
      (properties.date_response_type === "auto_populate_current_date" ||
        startDate)
    ) {
      try {
        const date = createAutoPopulatedDate(
          startDate,
          properties.selected_type
        );
        const newValueLocal = createAutoPopulatedValue(
          date,
          properties.date_type,
          properties.selected_type
        );

        setLocalValue(newValueLocal);
        setPreviousValue(newValueLocal);
        //*** Update of local data to user value and properties is handeled in onChange ***
        onChange(newValueLocal, { suppressConfirmation: true });
        initialAutoPopulateDone.current = true;
        // Ensure user hasn't manually changed during auto-population
        hasUserManuallyChanged.current = false;
      } catch (err) {
        console.error("Error auto-populating date:", err);
      }
    }
  }, []);

  // Changes to the onChange function in the DateTime component
  const onChange = (
    value: { value?: string; from?: string; to?: string },
    options?: { suppressConfirmation?: boolean }
  ) => {
    const updated = { ...(localValue || {}) };
    const newManuallyCleared = { ...manuallyCleared };

    if ("from" in value) {
      if (
        value.from === null ||
        value.from === undefined ||
        value.from === ""
      ) {
        updated.from = "";
        newManuallyCleared.from = true;

        // If "from" is empty and field is mandatory, show error
        if (properties.is_mandatory) {
          setRangeError(prev => ({
            ...prev,
            from: true,
            message: "This is required",
          }));
        }
      } else {
        updated.from = value.from;
        newManuallyCleared.from = false;

        // Clear error for "from" field when a value is entered
        setRangeError(prev => ({
          ...prev,
          from: false,
        }));

        // If we're setting a new "from" date and it's after the current "to" date,
        // automatically update the "to" date to match the "from" date
        if (updated.to && new Date(value.from) > new Date(updated.to)) {
          updated.to = value.from;
          newManuallyCleared.to = false;

          // Also clear "to" error if we're auto-updating it
          setRangeError(prev => ({
            ...prev,
            to: false,
          }));
        }
      }
    }

    if ("to" in value) {
      if (value.to === null || value.to === undefined || value.to === "") {
        updated.to = "";
        newManuallyCleared.to = true;

        // If "to" is empty and field is mandatory, show error
        if (properties.is_mandatory) {
          setRangeError(prev => ({
            ...prev,
            to: true,
            message: "This is required",
          }));
        }
      } else {
        updated.to = value.to;
        newManuallyCleared.to = false;

        // Clear error for "to" field when a value is entered
        setRangeError(prev => ({
          ...prev,
          to: false,
        }));
      }
    }

    if ("value" in value) {
      if (
        value.value === null ||
        value.value === undefined ||
        value.value === ""
      ) {
        updated.value = "";
        newManuallyCleared.value = true;

        if (properties.is_mandatory) {
          setError(true);
          setErrorMessage("This is required");
        }
      } else {
        updated.value = value.value;
        newManuallyCleared.value = false;
        setError(false);
      }
    }

    setManuallyCleared(newManuallyCleared);
    setCWFFormStateDirty(true);

    if (properties.date_type === "date_range") {
      if (!updated.from || !updated.to) {
        setLocalValue(updated);
        props.onChange(updated);
        return;
      }
    } else if (!updated.value) {
      setLocalValue(null);
      props.onChange(null);
      return;
    }

    if (validate(updated, properties)) {
      // Handle report date logic
      if (reportDate) {
        const reportDateValue = updated?.from ? updated.from : updated?.value;

        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            properties: {
              ...state.form.properties,
              report_start_date: reportDateValue,
            },
          },
        });
      }

      if (withConfirmationDialog && !options?.suppressConfirmation) {
        // Store the previous value if this is the first change
        if (!newValue) {
          setPreviousValue(localValue);
        }

        const dateChanged = hasDateChanged(localValue, updated);

        // Set the proposed new value
        setNewValue(updated);

        if (dateChanged) {
          setIsModalOpen(true);
        }
        const workPackageId = state.form.metadata?.work_package?.id;
        const componentData = workPackageId
          ? {
              ...state.form.component_data,
              activities_tasks: [],
              site_conditions: [],
              hazards_controls: {
                tasks: [],
                manually_added_hazards: [],
              },
            }
          : {
              ...state.form.component_data,
            };

        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            component_data: componentData,
          },
        });

        // Update local value to show the change in the UI
        setLocalValue(updated);
      } else {
        // Without confirmation, just update directly
        if (
          manual_location &&
          gps_coordinates?.latitude &&
          gps_coordinates?.longitude
        ) {
          try {
            createLocationFromLatLon({
              variables: {
                date: updated.value,
                name: "createLocationFromLatLon",
                gpsCoordinates: {
                  latitude: parseFloat(gps_coordinates.latitude ?? ""),
                  longitude: parseFloat(gps_coordinates.longitude ?? ""),
                },
              },
            });
          } catch (e) {
            toastCtx?.pushToast("error", "Failed to create location");
          }
        }
        setLocalValue(updated);
        props.onChange(updated);
      }

      // Clear errors on valid input
      if (properties.date_type === "date_range") {
        setRangeError({
          from: false,
          to: false,
          message: "",
        });
      } else {
        setError(false);
      }
    } else {
      setLocalValue(updated);

      const validationMessage =
        properties.date_validation === "allow_future_date"
          ? "Only future dates are allowed"
          : properties.date_validation === "allow_past_date"
          ? "Only past dates are allowed"
          : "Invalid date selection";

      if (properties.date_type === "date_range") {
        setRangeError({
          from: true,
          to: true,
          message: validationMessage,
        });
      } else {
        setError(true);
        setErrorMessage(validationMessage);
      }
    }
  };

  const handleConfirm = () => {
    if (
      manual_location &&
      gps_coordinates?.latitude &&
      gps_coordinates?.longitude
    ) {
      try {
        createLocationFromLatLon({
          variables: {
            date: newValue.value,
            name: "createLocationFromLatLon",
            gpsCoordinates: {
              latitude: parseFloat(gps_coordinates.latitude ?? ""),
              longitude: parseFloat(gps_coordinates.longitude ?? ""),
            },
          },
        });
      } catch (e) {
        toastCtx?.pushToast("error", "Failed to create location");
      }
    }
    props.onChange(newValue);
    setIsModalOpen(false);
    setNewValue(null);
  };

  const handleCancel = () => {
    // Revert to the previous value
    setLocalValue(previousValue);
    setIsModalOpen(false);
    setNewValue(null);
  };

  const isReadOnly =
    mode === UserFormModeTypes.BUILD ||
    mode === UserFormModeTypes.PREVIEW ||
    mode === UserFormModeTypes.PREVIEW_PROPS;

  switch (properties.selected_type) {
    case "date_time":
    case "date_only":
      if (properties.date_type === "date_range") {
        return (
          <DateRangeComponent
            id={props.content.id ?? ""}
            properties={properties}
            inSummary={inSummary}
            onChange={onChange}
            isReadOnly={isReadOnly}
            isDisabledForm={isDisabledForm}
            localValue={localValue}
            withConfirmationDialog={withConfirmationDialog}
            isModalOpen={isModalOpen}
            handleConfirm={handleConfirm}
            handleCancel={handleCancel}
            reportDate={reportDate}
            state={state}
            rangeError={rangeError}
          />
        );
      }
      return (
        <DateOnlyComponent
          id={props.content.id ?? ""}
          properties={properties}
          inSummary={inSummary}
          onChange={onChange}
          isReadOnly={isReadOnly}
          isDisabledForm={isDisabledForm}
          localValue={localValue}
          error={error}
          errorMessage={errorMessage}
          withConfirmationDialog={withConfirmationDialog}
          isModalOpen={isModalOpen}
          handleConfirm={handleConfirm}
          handleCancel={handleCancel}
          reportDate={reportDate}
          state={state}
        />
      );
    case "time_only":
      return (
        <TimeOnlyComponent
          id={props.content.id ?? ""}
          properties={properties}
          inSummary={inSummary}
          onChange={onChange}
          isReadOnly={isReadOnly}
          isDisabledForm={isDisabledForm}
          localValue={localValue}
          error={error}
          errorMessage={errorMessage}
          withConfirmationDialog={withConfirmationDialog}
          isModalOpen={isModalOpen}
          handleConfirm={handleConfirm}
          handleCancel={handleCancel}
        />
      );
    default:
      return <span />;
  }
}

export default DateTime;
