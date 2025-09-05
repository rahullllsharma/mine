import type {
  FormElementsType,
  InputDateAndTimePropertiesType,
  InputPropertiesType,
  DateTimeValueType,
  InputNumberPropertiesType,
  InputLocationPropertiesType,
} from "@/components/templatesComponents/customisedForm.types";
import { BodyText, ComponentLabel, Icon } from "@urbint/silica";
import formatTextToPhone from "@/utils/formatTextToPhone";
import {
  formatDateOnly,
  formatDateTime,
  formatTimeOnly,
} from "@/utils/dateTimeFormatters";
import LocationInput from "./LocationInput";

const InputTypeDataDisplay = ({ content }: { content: FormElementsType }) => {
  const { type, properties } = content;

  const renderValue = () => {
    const inputProperties = properties as InputPropertiesType;

    if (type === "input_date_time" || type === "report_date") {
      const dateTimeProperties =
        inputProperties as InputDateAndTimePropertiesType;
      if (dateTimeProperties.user_value === null) return null;

      const formatValue = (value: string) => {
        switch (dateTimeProperties.selected_type) {
          case "date_time":
            return formatDateTime(value);
          case "date_only":
            return formatDateOnly(value);
          case "time_only":
            return formatTimeOnly(value);
          default:
            return formatDateTime(value);
        }
      };

      if (
        typeof dateTimeProperties.user_value === "object" &&
        dateTimeProperties.user_value !== null
      ) {
        const dateTimeValue =
          dateTimeProperties.user_value as DateTimeValueType;

        if (dateTimeProperties.date_type === "date_range") {
          if ("from" in dateTimeValue && "to" in dateTimeValue) {
            return (
              <div className="flex flex-col gap-2 p-4">
                <ComponentLabel className="text-sm font-semibold">
                  {properties.title}
                </ComponentLabel>
                <div className="flex flex-row gap-1 w-full justify-between">
                  <div className="flex flex-col gap-1 w-full">
                    <ComponentLabel className="text-sm font-semibold">
                      From
                    </ComponentLabel>
                    <BodyText className="text-base">
                      {formatValue(dateTimeValue.from)}
                    </BodyText>
                  </div>
                  <div className="flex flex-col gap-1 w-full">
                    <ComponentLabel className="text-sm font-semibold">
                      To
                    </ComponentLabel>
                    <BodyText className="text-base">
                      {formatValue(dateTimeValue.to)}
                    </BodyText>
                  </div>
                </div>
              </div>
            );
          }
        } else {
          if ("value" in dateTimeValue) {
            return dateTimeValue.value ? (
              <div className="flex flex-col gap-2 p-4">
                <ComponentLabel className="text-sm font-semibold">
                  {properties.title}
                </ComponentLabel>
                <BodyText className="text-base">
                  {formatValue(dateTimeValue.value)}
                </BodyText>
              </div>
            ) : null;
          }
        }
        return "Date range selected";
      }

      return dateTimeProperties.user_value
        ? formatValue(dateTimeProperties.user_value)
        : null;
    }

    if (type === "input_phone_number" && inputProperties.user_value) {
      if (inputProperties.user_value === null) return null;
      return (
        <div className="flex flex-col gap-2 p-4">
          <ComponentLabel className="text-sm font-semibold">
            {properties.title}
          </ComponentLabel>
          <div className="flex flex-row items-center">
            <a
              href={`tel:${formatTextToPhone(
                String(inputProperties.user_value)
              )}`}
              className="text-base flex flex-row gap-1 items-center"
            >
              <Icon name="phone" className="text-[20px] text-brand-urbint-50" />
              <BodyText className="text-base text-brand-urbint-50">
                {formatTextToPhone(String(inputProperties.user_value))}
              </BodyText>
            </a>
          </div>
        </div>
      );
    }

    if (type === "input_number" && inputProperties.user_value) {
      if (inputProperties.user_value === null) return null;
      const numberProperties = inputProperties as InputNumberPropertiesType;
      const unit =
        numberProperties.unit_name && numberProperties.unit_name !== ""
          ? ` ${numberProperties.unit_name}`
          : "";
      return (
        <div className="flex flex-col gap-2 p-4">
          <ComponentLabel className="text-sm font-semibold">
            {properties.title}
          </ComponentLabel>
          <BodyText className="text-base">{`${inputProperties.user_value}${unit}`}</BodyText>
        </div>
      );
    }

    if (type === "input_location" && inputProperties.user_value) {
      return (
        <LocationInput
          locationProperties={inputProperties as InputLocationPropertiesType}
        />
      );
    }

    if (type === "input_email" && inputProperties.user_value) {
      return (
        <div className="flex flex-col gap-2 p-4">
          <ComponentLabel className="text-sm font-semibold">
            {properties.title}
          </ComponentLabel>
          <a
            href={`mailto:${inputProperties.user_value}`}
            className="flex items-center gap-1"
          >
            <Icon
              name={"mail"}
              className="text-xl bg-transparent text-brand-urbint-50"
            />
            <BodyText className="text-base text-brand-urbint-50">
              {inputProperties.user_value}
            </BodyText>
          </a>
        </div>
      );
    }

    if (type === "input_text" && inputProperties.user_value) {
      return (
        <div className="flex flex-col gap-2 p-4">
          <ComponentLabel className="text-sm font-semibold">
            {properties.title}
          </ComponentLabel>
          <BodyText className="text-base">
            {inputProperties.user_value}
          </BodyText>
        </div>
      );
    }

    if (!inputProperties.user_value) return null;
    return inputProperties.user_value;
  };

  const value = renderValue();
  if (value === null) return null;

  return (
    <div className="flex flex-col rounded-lg">
      <div>{value}</div>
    </div>
  );
};

export default InputTypeDataDisplay;
