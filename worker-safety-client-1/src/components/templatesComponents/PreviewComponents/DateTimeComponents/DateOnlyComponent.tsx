import type { DateTimeFormState } from "../../customisedForm.types";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { formatDateOnly, formatDateTime } from "@/utils/dateTimeFormatters";
import { getPlaceholder } from "@/utils/dateFormatUtils";
import BaseFieldDateTimePicker from "../../BaseFieldDateTimePicker/BaseFieldDateTimePicker";
import { formatDateTimeLocal } from "../dateUtils";
import { ModalWrapper } from "./DateTime";

export const RenderDateOnlyComponentInSummary = ({
  properties,
  localValue,
}: {
  properties: DateTimeFormState;
  localValue?: any;
}) => {
  return (
    <div className="flex gap-2 flex-col">
      <ComponentLabel className="text-sm font-semibold cursor-auto">
        {properties.title}
      </ComponentLabel>
      <BodyText className="text-base">
        {properties.selected_type === "date_time"
          ? formatDateTime(localValue.value)
          : formatDateOnly(localValue.value)}
      </BodyText>
    </div>
  );
};

const DateOnlyComponent = ({
  id,
  properties,
  inSummary,
  onChange,
  isReadOnly,
  isDisabledForm,
  localValue,
  error,
  errorMessage,
  withConfirmationDialog,
  isModalOpen,
  handleConfirm,
  handleCancel,
  reportDate,
  state,
}: {
  id: string;
  properties: DateTimeFormState;
  inSummary?: boolean;
  onChange: (value: any) => void;
  isReadOnly: boolean;
  isDisabledForm: boolean;
  localValue: any;
  error: boolean;
  errorMessage: string;
  withConfirmationDialog?: boolean;
  isModalOpen: boolean;
  handleConfirm: () => void;
  handleCancel: () => void;
  reportDate?: boolean;
  state: any;
}) => {
  return inSummary ? (
    <RenderDateOnlyComponentInSummary
      properties={properties}
      localValue={localValue}
    />
  ) : (
    <ModalWrapper
      withConfirmationDialog={withConfirmationDialog}
      isModalOpen={isModalOpen}
      handleConfirm={handleConfirm}
      handleCancel={handleCancel}
    >
      <BaseFieldDateTimePicker
        id={id}
        name={
          properties.title + (properties.is_mandatory && !inSummary ? "*" : "")
        }
        label={
          properties.title + (properties.is_mandatory && !inSummary ? "*" : "")
        }
        type={
          properties.selected_type === "date_time" ? "datetime-local" : "date"
        }
        onChange={e => onChange({ value: e })}
        disabled={isReadOnly}
        mode="all"
        value={isDisabledForm ? "" : localValue?.value || ""}
        {...(reportDate && {
          max: formatDateTimeLocal(
            state.form?.work_package_data?.endDate ?? null
          ),
        })}
        placeholder={
          properties.selected_type === "date_time"
            ? getPlaceholder("datetime-local")
            : getPlaceholder("date")
        }
        {...(properties.date_validation === "allow_past_date" && {
          mode: "past",
        })}
        {...(properties.date_validation === "allow_future_date" && {
          mode: "future",
        })}
        error={error ? errorMessage : ""}
        includeInWidget={properties.include_in_widget}
      />
    </ModalWrapper>
  );
};

export default DateOnlyComponent;
