import type { DateTimeFormState } from "../../customisedForm.types";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { formatTimeOnly } from "@/utils/dateTimeFormatters";
import BaseFieldDateTimePicker from "../../BaseFieldDateTimePicker/BaseFieldDateTimePicker";
import { ModalWrapper } from "./DateTime";

export const RenderTimeOnlyComponentInSummary = ({
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
        {formatTimeOnly(localValue.value)}
      </BodyText>
    </div>
  );
};

const TimeOnlyComponent = ({
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
}) => {
  return inSummary ? (
    <RenderTimeOnlyComponentInSummary
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
        type={"time"}
        onChange={e => onChange({ value: e })}
        disabled={isReadOnly}
        value={isDisabledForm ? "" : localValue?.value || ""}
        placeholder={"HH:MM"}
        error={error ? errorMessage : ""}
        includeInWidget={properties.include_in_widget}
      />
    </ModalWrapper>
  );
};

export default TimeOnlyComponent;
