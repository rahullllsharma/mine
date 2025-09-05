import type { ChangeEvent, ForwardedRef, FocusEvent } from "react";
import type { IconName } from "@urbint/silica";
import type { InputProps as AllInputProps } from "@/components/shared/input/Input";
import type { FieldProps } from "../../shared/field/Field";
import type { DatePickerProps } from "antd";
import { forwardRef, useState, useEffect } from "react";
import cx from "classnames";
import { isSafari } from "react-device-detect";
import { DatePicker } from "antd";
import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat";
import weekday from "dayjs/plugin/weekday";
import localeData from "dayjs/plugin/localeData";
import updateLocale from "dayjs/plugin/updateLocale";
import { Icon, BodyText } from "@urbint/silica";
import Input from "@/components/shared/input/Input";
import SvgButton from "@/components/templatesComponents/ButtonComponents/SvgButton/SvgButton";
import { getDisplayFormat, getPlaceholder } from "@/utils/dateFormatUtils";
import styles from "./BaseFieldDateTimePicker.module.css";

dayjs.extend(customParseFormat);
dayjs.extend(weekday);
dayjs.extend(localeData);
dayjs.extend(updateLocale);

type InputBaseProps = Pick<
  AllInputProps,
  | "id"
  | "required"
  | "placeholder"
  | "pattern"
  | "onBlur"
  | "min"
  | "max"
  | "disabled"
  | "readOnly"
>;

type InputOwnProps = {
  name: string;
  defaultValue?: string;
  value?: string;
  type: "date" | "time" | "datetime-local";
  onChange?: (e?: string) => void;
  placeholder?: string;
  includeInWidget?: boolean;
};

export type FieldDateTimePickerProps = FieldProps &
  InputBaseProps &
  InputOwnProps;

export const iconByInputType: Record<
  FieldDateTimePickerProps["type"],
  IconName
> = Object.freeze({
  date: "calendar",
  time: "clock",
  "datetime-local": "calendar",
});

const getFormatString = (type: "date" | "time" | "datetime-local"): string => {
  switch (type) {
    case "datetime-local":
      return "YYYY-MM-DDTHH:mm";
    case "time":
      return "HH:mm";
    case "date":
    default:
      return "YYYY-MM-DD";
  }
};

function BaseFieldDateTimePicker(
  {
    type,
    pattern,
    defaultValue,
    value,
    name,
    id,
    min,
    max,
    disabled,
    readOnly,
    onChange,
    onBlur,
    placeholder,
    includeInWidget,
    ...fieldProps
  }: FieldDateTimePickerProps,
  ref: ForwardedRef<any>
): JSX.Element {
  const [hasPlaceholder, setHasPlaceholder] = useState(
    [value, defaultValue].join("").length === 0
  );

  // Parse date value properly based on type (Desktop with dayjs)
  const parseDateValue = (val?: string) => {
    if (!val) return null;

    if (type === "time") {
      // For time-only, create a dayjs object with today's date and the time
      const timeMatch = val.match(/^(\d{1,2}):(\d{2})$/);
      if (timeMatch) {
        const [_, hours, minutes] = timeMatch;
        return dayjs()
          .hour(parseInt(hours))
          .minute(parseInt(minutes))
          .second(0);
      }
      // Try parsing as HH:mm format
      return dayjs(val, "HH:mm").isValid() ? dayjs(val, "HH:mm") : null;
    }

    return dayjs(val).isValid() ? dayjs(val) : null;
  };

  const [selectedDate, setSelectedDate] = useState<dayjs.Dayjs | null>(
    parseDateValue(value || defaultValue)
  );

  // Track the current input value for mobile
  const [inputValue, setInputValue] = useState<string>(
    value || defaultValue || ""
  );

  // Update internal state when external value changes
  useEffect(() => {
    setInputValue(value || "");
    const parsedDate = parseDateValue(value || defaultValue);
    setSelectedDate(parsedDate);
    setHasPlaceholder(!value || value.length === 0);
  }, [value, defaultValue, type]);

  // Desktop date picker change handler
  const handleDesktopChange = (date: dayjs.Dayjs | null) => {
    setHasPlaceholder(!date);
    setSelectedDate(date);

    if (onChange) {
      const formattedDate = date ? date.format(getFormatString(type)) : "";
      onChange(formattedDate);
    }
  };

  // Mobile input change handler
  const handleMobileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const newValue = e?.target?.value;
    setHasPlaceholder(newValue?.length === 0);
    setInputValue(newValue);

    // Call parent onChange handler immediately with the new value
    onChange && onChange(newValue);
  };

  const handleBlur = (e: any) => {
    onBlur && onBlur(e as unknown as FocusEvent<HTMLInputElement>);
  };

  const elemId = id || name;

  const autoPlaceholder = getPlaceholder(type);
  const finalPlaceholder = placeholder || autoPlaceholder;

  const getPickerProps = () => {
    return {
      ref,
      value: selectedDate,
      onChange: handleDesktopChange,
      onBlur: handleBlur,
      disabled,
      placeholder: finalPlaceholder,
      format: getDisplayFormat(type),
      showTime:
        type !== "date"
          ? {
              use12Hours: type === "time" ? false : true,
            }
          : undefined,
      picker: type === "time" ? "time" : "date",
      disabledDate: (current: dayjs.Dayjs) => {
        if (min && current.isBefore(dayjs(min), "day")) return true;
        if (max && current.isAfter(dayjs(max), "day")) return true;
        return false;
      },
      // Enable Ant Design's built-in clear functionality
      allowClear: true,
      // Add inputReadOnly to ensure placeholder is visible
      inputReadOnly: false,
    } as DatePickerProps;
  };
  // Custom label with widget icon if includeInWidget is true
  const renderLabel = () => {
    if (!fieldProps.label) return null;

    return (
      <div className="flex gap-2 mb-1">
        <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal">
          {fieldProps.label}
          {fieldProps.required && " *"}
        </label>
        {includeInWidget && (
          <div className="text-neutrals-tertiary flex gap-2">
            <SvgButton svgPath={"/assets/CWF/widget.svg"} />
            <BodyText className="text-neutrals-tertiary">Widget</BodyText>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={fieldProps.className} id={elemId}>
      {renderLabel()}
      {fieldProps.caption && (
        <p className="text-sm mt-1 text-neutral-shade-75">
          {fieldProps.caption}
        </p>
      )}

      {/* Mobile Input - shown on screens <= 768px */}
      <div className={styles.mobileInput}>
        <Input
          type={readOnly ? "text" : type}
          icon={iconByInputType[type]}
          ref={ref}
          id={elemId}
          name={name}
          pattern={pattern}
          value={inputValue}
          min={min}
          max={max}
          disabled={disabled}
          readOnly={readOnly}
          // Safari doesn't handle very well colors for native pickers when we don't have a value.
          containerClassName={cx({
            ["text-brand-gray-60"]: hasPlaceholder && isSafari,
            ["text-neutral-shade-58"]: hasPlaceholder && !isSafari,
          })}
          className={cx(styles.root, {
            ["text-brand-gray-60"]: hasPlaceholder && isSafari,
            ["text-neutral-shade-58"]: hasPlaceholder && !isSafari,
          })}
          error={
            typeof fieldProps?.error === "boolean"
              ? fieldProps.error
                ? "error"
                : ""
              : fieldProps?.error
          }
          onBlur={handleBlur}
          onChange={handleMobileChange}
          placeholder={finalPlaceholder}
        />
      </div>

      {/* Desktop Input - shown on screens > 768px */}
      <div className={styles.desktopInput}>
        <div style={{ position: "relative" }}>
          <span className={styles.iconLeft}>
            <Icon name={iconByInputType[type]} />
          </span>
          <DatePicker
            {...getPickerProps()}
            className={cx(styles.desktopRoot, styles.withLeftIcon, {
              ["text-brand-gray-60"]: hasPlaceholder && isSafari,
              ["text-neutral-shade-58"]: hasPlaceholder && !isSafari,
            })}
            style={{
              backgroundColor: "white",
              border: "1.5px solid #BDC1C3",
              borderRadius: "4px",
              minHeight: "40px",
              height: "44px",
              padding: "8px 48px",
              width: "100%",
              fontSize: "16px",
              color: "black",
            }}
          />
        </div>
      </div>

      {/* Error display */}
      {fieldProps?.error && (
        <div id={`${elemId}-err`} className="text-red-500 mt-2">
          {fieldProps.error}
        </div>
      )}
    </div>
  );
}

export default forwardRef(BaseFieldDateTimePicker);
