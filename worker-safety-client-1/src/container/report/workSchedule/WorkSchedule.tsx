import type {
  FieldValues,
  UnpackNestedValue,
  UseFormGetValues,
  ControllerRenderProps,
} from "react-hook-form";
import { useCallback, useEffect, useState } from "react";
import { Controller, useFormContext } from "react-hook-form";

import { FieldRules } from "@/components/shared/field/FieldRules";

import { messages } from "@/locales/messages";
import {
  isDateWithinRange,
  getFormattedShortDateTime,
  getFormattedFullDateTime,
} from "@/utils/date/helper";

import FieldDateTimePicker from "@/components/shared/field/fieldDateTimePicker/FieldDateTimePicker";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { greaterThanDate } from "./utils";
import { ConfirmDateChangeModal } from "./ConfirmDateChangeModal";

// We should expose the types without the prefix for other components
// bonus point: if matches the description in the graphql mutation!
export const workScheduleFormInputPrefix = "workSchedule";

const FORM_INPUT_NAMES = Object.freeze({
  startDatetime: `${workScheduleFormInputPrefix}.startDatetime` as const,
  endDatetime: `${workScheduleFormInputPrefix}.endDatetime` as const,
});

// Auxilary types - useful for creating and exposing the actual WorkSchedule types
type Form = typeof FORM_INPUT_NAMES;
type WorkScheduleFormValues = UnpackNestedValue<WorkScheduleFormData>;

export type WorkScheduleFormData = {
  -readonly [k in Form[keyof Form]]: string;
};

type WorkScheduleFormDataKeys = {
  -readonly [key in keyof Form]: string;
};

export type WorkScheduleProps = {
  dateLimits: {
    projectStartDate: string;
    projectEndDate: string;
  };
  isCompleted?: boolean;
} & WorkScheduleFormDataKeys;

/**
 * Validates if the date is greater than the end date.
 * It will return true or a message.
 *
 */
const validateGreaterThanEndDateWithErrorMsg =
  (
    getFormValue: UseFormGetValues<WorkScheduleFormValues>,
    primeContractor: string
  ) =>
  (start: string) => {
    const result = greaterThanDate({
      start,
      end: getFormValue(FORM_INPUT_NAMES.endDatetime),
    });

    return (
      result ||
      messages.startDateTimeGreaterThanEnd.replace(
        "{contractor}",
        primeContractor
      )
    );
  };

/**
 * Check if a datetime is within the start and end dates for the project.
 *
 * Most likely, this won't be called because the other validation function will pickup both the data & time now.
 * However, it could be useful for edge cases.
 */
const validateIsDateInRange =
  (
    { projectStartDate, projectEndDate }: WorkScheduleProps["dateLimits"],
    primeContractor: string,
    label: "Start" | "End" = "Start"
  ) =>
  (date: string) => {
    const result = isDateWithinRange(projectStartDate, projectEndDate, date);

    return (
      result ||
      messages.dateTimeNotInProjectRange
        .replace("{contractor}", primeContractor)
        .replace("{label}", label)
        .replace("{startDatetime}", getFormattedShortDateTime(projectStartDate))
        .replace("{endDatetime}", getFormattedShortDateTime(projectEndDate))
    );
  };

type ControllerRenderPropsField =
  | ControllerRenderProps<FieldValues, typeof FORM_INPUT_NAMES.startDatetime>
  | ControllerRenderProps<FieldValues, typeof FORM_INPUT_NAMES.endDatetime>
  | undefined;

/**
 * The work schedule section, reusable.
 * Although being used on the Daily Inspection Report, this can be used anywhere.
 *
 * All dates, so `startDatetime`, `endDatetime` and project limits need to be
 * properly formatted and adjusted to the local user's timezone.
 */
export default function WorkSchedule({
  dateLimits,
  startDatetime,
  endDatetime,
  isCompleted,
}: WorkScheduleProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const { projectStartDate, projectEndDate } = dateLimits;
  const { clearErrors, getValues, watch, setValue } = useFormContext();
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [revertDateChange, setRevertDateChange] = useState(false);
  const [localValue, setLocalValue] = useState<string | undefined>();
  const [localField, setLocalField] = useState<ControllerRenderPropsField>();
  const [endDateResetValue, setEndDateResetValue] = useState<
    string | undefined
  >();

  const resetEndDateOnStartDateChange = useCallback(
    function (value: string) {
      // TODO: this will at least reset the end date to match the start date
      const currentEndDateTime = getValues(FORM_INPUT_NAMES.endDatetime) || "";

      const shouldUpdateEndDateTime =
        new Date(value) > new Date(currentEndDateTime);

      if (shouldUpdateEndDateTime) {
        setEndDateResetValue(currentEndDateTime);
        setValue(FORM_INPUT_NAMES.endDatetime, value, {
          shouldValidate: false,
        });
        clearErrors();
      }
    },
    [getValues, setValue, clearErrors]
  );

  useEffect(() => {
    if (revertDateChange) {
      localField?.onChange(localValue);

      if (localField?.name === FORM_INPUT_NAMES.startDatetime) {
        setValue(FORM_INPUT_NAMES.endDatetime, endDateResetValue, {
          shouldValidate: false,
        });
        setEndDateResetValue(undefined);
      }

      setLocalValue(undefined);
      setLocalField(undefined);
      setRevertDateChange(false);
      setShowConfirmModal(false);
    }
  }, [
    revertDateChange,
    localField,
    localValue,
    resetEndDateOnStartDateChange,
    setValue,
    setEndDateResetValue,
    endDateResetValue,
  ]);

  const calcMinValForEndDatetime = isCompleted
    ? undefined
    : watch(FORM_INPUT_NAMES.startDatetime) ?? projectStartDate;

  // Config rules for pickers
  const configRulesForInput = (label: "Start" | "End") => ({
    ...FieldRules.REQUIRED,
    validate: {
      isDateInRange: validateIsDateInRange(
        {
          projectStartDate,
          projectEndDate,
        },
        workPackage.attributes.primeContractor.label,
        label
      ),
    },
  });
  const startDateTimeRules = configRulesForInput("Start");

  // Event handlers
  const handleStartDateTimeChange = (
    field: ControllerRenderProps<
      FieldValues,
      typeof FORM_INPUT_NAMES.startDatetime
    >
  ): ((e?: string | undefined) => void) | undefined => {
    return (e = "") => {
      resetEndDateOnStartDateChange(e);
      if (
        new Date(e).getDate() !==
        new Date(getValues(FORM_INPUT_NAMES.startDatetime)).getDate()
      ) {
        setLocalValue(getValues(FORM_INPUT_NAMES.startDatetime));
        setLocalField(field);
      }
      field.onChange(e);
    };
  };

  const handleEndDateTimeChange = (
    field: ControllerRenderProps<
      FieldValues,
      typeof FORM_INPUT_NAMES.endDatetime
    >
  ): ((e?: string | undefined) => void) | undefined => {
    return (e = "") => {
      if (
        new Date(e).getDate() !==
        new Date(getValues(FORM_INPUT_NAMES.endDatetime)).getDate()
      ) {
        setLocalValue(getValues(FORM_INPUT_NAMES.endDatetime));
        setLocalField(field);
      }
      field.onChange(e);
    };
  };

  // Make sure dates default are changed (set without format) on daily report reopen
  useEffect(() => {
    if (!isCompleted) {
      setValue(FORM_INPUT_NAMES.startDatetime, startDatetime);
      setValue(FORM_INPUT_NAMES.endDatetime, endDatetime);
    }
  }, [isCompleted]);

  return (
    <>
      <h3 className="text-xl font-semibold text-neutral-shade-100">
        Daily Report Details
      </h3>
      <div className="mt-4" data-testid="work-schedule-section">
        <div className="flex flex-col gap-4 p-4 bg-brand-gray-10">
          <Controller
            rules={
              isCompleted
                ? undefined
                : {
                    ...startDateTimeRules,
                    validate: {
                      greaterThanEndDate:
                        validateGreaterThanEndDateWithErrorMsg(
                          getValues as unknown as UseFormGetValues<WorkScheduleFormValues>,
                          workPackage.attributes.primeContractor.label
                        ),
                      ...startDateTimeRules.validate,
                    },
                  }
            }
            name={FORM_INPUT_NAMES.startDatetime}
            defaultValue={
              // we need to format the date for the value
              // otherwise it will display the date as we get from the payload, YYYY-MM-DDThh:ss
              isCompleted
                ? getFormattedFullDateTime(startDatetime)
                : startDatetime
            }
            render={({ field, fieldState: { error } }) => (
              <FieldDateTimePicker
                {...field}
                label={`${workPackage.attributes.primeContractor.label} Work Start Day and time`}
                error={error?.message}
                min={isCompleted ? undefined : projectStartDate}
                max={isCompleted ? undefined : projectEndDate}
                required
                readOnly={isCompleted}
                onChange={handleStartDateTimeChange(field)}
                onBlur={() => localValue && setShowConfirmModal(true)}
              />
            )}
          />
        </div>
        <div className="flex flex-col gap-4 p-4 bg-brand-gray-10">
          <Controller
            rules={isCompleted ? undefined : configRulesForInput("End")}
            name={FORM_INPUT_NAMES.endDatetime}
            defaultValue={
              // we need to format the date for the value
              // otherwise it will display the date as we get from the payload, YYYY-MM-DDThh:ss
              isCompleted ? getFormattedFullDateTime(endDatetime) : endDatetime
            }
            render={({ field, fieldState: { error } }) => (
              <FieldDateTimePicker
                {...field}
                label={`${workPackage.attributes.primeContractor.label} Work End Day and time`}
                error={error?.message}
                min={calcMinValForEndDatetime}
                max={isCompleted ? undefined : projectEndDate}
                required
                readOnly={isCompleted}
                onChange={handleEndDateTimeChange(field)}
                onBlur={() => localValue && setShowConfirmModal(true)}
              />
            )}
          />
        </div>

        {showConfirmModal && (
          <ConfirmDateChangeModal
            onConfirm={() => {
              // Note: Keep the new date changes
              clearErrors();
              setLocalValue(undefined);
              setLocalField(undefined);
              setShowConfirmModal(false);
            }}
            onCancel={() => {
              // Note: Revert the form date changes to original dates
              setRevertDateChange(true);
            }}
          />
        )}
      </div>
    </>
  );
}
