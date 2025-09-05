import type { DateTimeFormState } from "../../customisedForm.types";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { formatDateOnly, formatDateTime } from "@/utils/dateTimeFormatters";
import { getPlaceholder } from "@/utils/dateFormatUtils";
import BaseFieldDateTimePicker from "../../BaseFieldDateTimePicker/BaseFieldDateTimePicker";
import { formatDateTimeLocal } from "../dateUtils";
import SvgButton from "../../ButtonComponents/SvgButton/SvgButton";
import { ModalWrapper } from "./DateTime";

export const RenderDateRangeComponentInSummary = ({
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
      <BodyText>
        <div className="flex w-full justify-evenly">
          <div className="flex flex-col justify-center w-full gap-2">
            <ComponentLabel className="text-sm font-semibold cursor-auto">
              From
            </ComponentLabel>
            <BodyText className="text-base">
              {properties.selected_type === "date_time"
                ? formatDateTime(localValue.from)
                : formatDateOnly(localValue.from)}
            </BodyText>
          </div>
          <div className="flex flex-col justify-center w-full gap-2">
            <ComponentLabel className="text-sm font-semibold cursor-auto">
              To
            </ComponentLabel>
            <BodyText className="text-base">
              {properties.selected_type === "date_time"
                ? formatDateTime(localValue.to)
                : formatDateOnly(localValue.to)}
            </BodyText>
          </div>
        </div>
      </BodyText>
    </div>
  );
};

const DateRangeComponent = ({
  id,
  properties,
  inSummary,
  onChange,
  isReadOnly,
  isDisabledForm,
  localValue,
  withConfirmationDialog,
  isModalOpen,
  handleConfirm,
  handleCancel,
  reportDate,
  state,
  rangeError,
}: {
  id: string;
  properties: DateTimeFormState;
  inSummary?: boolean;
  onChange: (value: any) => void;
  isReadOnly: boolean;
  isDisabledForm: boolean;
  localValue: any;
  withConfirmationDialog?: boolean;
  isModalOpen: boolean;
  handleConfirm: () => void;
  handleCancel: () => void;
  reportDate?: boolean;
  state: any;
  rangeError: any;
}) => {
  return inSummary ? (
    <RenderDateRangeComponentInSummary
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
      <div className="flex flex-grow flex-col">
        <div className="flex gap-2 mb-1">
          <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal">
            {properties.title}
            {properties.is_mandatory && !inSummary ? "*" : ""}
          </label>
          {properties.include_in_widget && (
            <div className="text-neutrals-tertiary flex gap-2">
              <SvgButton svgPath={"/assets/CWF/widget.svg"} />
              <BodyText className="text-neutrals-tertiary">Widget</BodyText>
            </div>
          )}
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          <BaseFieldDateTimePicker
            id={id}
            name={"From" + (properties.is_mandatory && !inSummary ? "*" : "")}
            label={"From" + (properties.is_mandatory && !inSummary ? "*" : "")}
            type={
              properties.selected_type === "date_time"
                ? "datetime-local"
                : "date"
            }
            onChange={e => onChange({ from: e })}
            disabled={isReadOnly}
            value={isDisabledForm ? "" : localValue?.from || ""}
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
            error={rangeError.from ? rangeError.message : ""}
          />
          <BaseFieldDateTimePicker
            name={"To" + (properties.is_mandatory && !inSummary ? "*" : "")}
            label={"To" + (properties.is_mandatory && !inSummary ? "*" : "")}
            type={
              properties.selected_type === "date_time"
                ? "datetime-local"
                : "date"
            }
            onChange={e => onChange({ to: e })}
            disabled={isReadOnly}
            min={localValue?.from || undefined}
            {...(reportDate && {
              max: formatDateTimeLocal(
                state.form?.work_package_data?.endDate ?? null
              ),
            })}
            value={isDisabledForm ? "" : localValue?.to || ""}
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
            error={rangeError.to ? rangeError.message : ""}
          />
        </div>
      </div>
    </ModalWrapper>
  );
};

export default DateRangeComponent;
