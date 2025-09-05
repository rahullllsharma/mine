import type { ForwardedRef, FocusEvent } from "react";
import type { FieldDateTimePickerProps } from "../customisedForm.types";
import type { DatePickerProps } from "antd";
import { forwardRef, useState, useEffect } from "react";
import cx from "classnames";
import { DatePicker } from "antd";
import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat";
import weekday from "dayjs/plugin/weekday";
import localeData from "dayjs/plugin/localeData";
import updateLocale from "dayjs/plugin/updateLocale";
import { Icon } from "@urbint/silica";
import ReactDatePicker from "react-datepicker";
import Field from "@/components/shared/field/Field";
import { getDisplayFormat, getPlaceholder } from "@/utils/dateFormatUtils";
import "react-datepicker/dist/react-datepicker.css";

dayjs.extend(customParseFormat);
dayjs.extend(weekday);
dayjs.extend(localeData);
dayjs.extend(updateLocale);

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

// Hook to detect mobile devices
const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkIsMobile();
    window.addEventListener("resize", checkIsMobile);

    return () => window.removeEventListener("resize", checkIsMobile);
  }, []);

  return isMobile;
};

function BaseDateTimePicker(
  {
    icon,
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
    mode = "all",
    dateResponseType = "calendar",
    timeResponseType = "manual_input",
    ...fieldProps
  }: FieldDateTimePickerProps,
  ref: ForwardedRef<any>
): JSX.Element {
  const isMobile = useIsMobile();

  // Desktop parsing with dayjs
  const parseDateDesktop = (val?: string) => {
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

  // Mobile parsing with Date
  const parseDateMobile = (val?: string) => {
    if (!val) return null;
    if (type === "time") {
      const [hours, minutes] = val.split(":").map(Number);
      const dateNow = new Date();
      dateNow.setHours(hours, minutes, 0, 0);
      return dateNow;
    }
    const date = new Date(val);
    return isNaN(date.getTime()) ? null : date;
  };

  const parseDate = isMobile ? parseDateMobile : parseDateDesktop;

  const initialValue = () => {
    if (value) return parseDate(value);

    if (isMobile) {
      const dateNow = new Date();

      if (
        type === "date" &&
        dateResponseType === "auto_populate_current_date"
      ) {
        return dateNow;
      }

      if (
        type === "time" &&
        timeResponseType === "auto_populate_current_time"
      ) {
        return dateNow;
      }

      if (type === "datetime-local") {
        if (
          dateResponseType === "auto_populate_current_date" &&
          timeResponseType === "auto_populate_current_time"
        ) {
          return dateNow;
        }

        if (dateResponseType === "auto_populate_current_date") {
          const date = new Date();
          date.setHours(0, 0, 0, 0);
          return date;
        }

        if (timeResponseType === "auto_populate_current_time") {
          return null;
        }
      }

      return null;
    } else {
      if (
        type === "date" &&
        dateResponseType === "auto_populate_current_date"
      ) {
        return dayjs();
      }

      if (
        type === "time" &&
        timeResponseType === "auto_populate_current_time"
      ) {
        return dayjs();
      }

      if (type === "datetime-local") {
        if (
          dateResponseType === "auto_populate_current_date" &&
          timeResponseType === "auto_populate_current_time"
        ) {
          return dayjs();
        }

        if (dateResponseType === "auto_populate_current_date") {
          return dayjs().startOf("day");
        }

        if (timeResponseType === "auto_populate_current_time") {
          return null;
        }
      }

      return null;
    }
  };

  const [selectedDate, setSelectedDate] = useState<any>(initialValue());

  const [hasPlaceholder, setHasPlaceholder] = useState(
    !selectedDate && [value, defaultValue].join("").length === 0
  );

  useEffect(() => {
    const autoDate = dateResponseType === "auto_populate_current_date";
    const autoTime = timeResponseType === "auto_populate_current_time";

    if (!selectedDate && (autoDate || autoTime)) {
      let newDate: any = null;

      if (isMobile) {
        const dateNow = new Date();

        if (type === "date" && autoDate) {
          newDate = dateNow;
        } else if (type === "time" && autoTime) {
          newDate = dateNow;
        } else if (type === "datetime-local") {
          if (autoDate && autoTime) {
            newDate = dateNow;
          } else if (autoDate) {
            newDate = new Date(dateNow);
            newDate.setHours(0, 0, 0, 0);
          } else if (autoTime) {
            newDate = null;
          }
        }
      } else {
        switch (type) {
          case "date":
            if (autoDate) {
              newDate = dayjs();
            }
            break;
          case "time":
            if (autoTime) {
              newDate = dayjs();
            }
            break;
          case "datetime-local":
            if (autoDate && autoTime) {
              newDate = dayjs();
            } else if (autoDate) {
              newDate = dayjs().startOf("day");
            } else if (autoTime) {
              newDate = null;
            }
            break;
        }
      }

      if (newDate) {
        setSelectedDate(newDate);
        setHasPlaceholder(false);

        if (onChange) {
          if (isMobile) {
            let formattedDate = "";
            if (newDate) {
              formattedDate =
                type === "datetime-local"
                  ? newDate.toISOString().slice(0, 16)
                  : type === "time"
                  ? newDate.toTimeString().slice(0, 5)
                  : newDate.toISOString().split("T")[0];
            }
            onChange(formattedDate);
          } else {
            onChange(newDate.format(getFormatString(type)));
          }
        }
      }
    }
  }, [
    dateResponseType,
    timeResponseType,
    type,
    selectedDate,
    onChange,
    isMobile,
  ]);

  const handleDateChange = (date: any) => {
    setSelectedDate(date);
    setHasPlaceholder(!date);

    if (onChange) {
      if (isMobile) {
        let formattedDate = "";
        if (date) {
          if (type === "datetime-local") {
            formattedDate =
              date.getFullYear() +
              "-" +
              (date.getMonth() + 1).toString().padStart(2, "0") +
              "-" +
              date.getDate().toString().padStart(2, "0") +
              "T" +
              date.getHours().toString().padStart(2, "0") +
              ":" +
              date.getMinutes().toString().padStart(2, "0");
          } else if (type === "time") {
            formattedDate = date.toTimeString().slice(0, 5);
          } else {
            formattedDate =
              date.getFullYear() +
              "-" +
              (date.getMonth() + 1).toString().padStart(2, "0") +
              "-" +
              date.getDate().toString().padStart(2, "0");
          }
        }
        onChange(formattedDate);
      } else {
        onChange(date ? date.format(getFormatString(type)) : "");
      }
    }
  };

  const onBlurHandler = (e: any) => {
    if (isMobile) {
      setHasPlaceholder(e?.target?.value?.length === 0);
      onBlur && onBlur(e);
    } else {
      setHasPlaceholder((e?.target as HTMLInputElement)?.value?.length === 0);
      onBlur && onBlur(e as unknown as FocusEvent<HTMLInputElement>);
    }
  };

  const today = isMobile ? new Date() : dayjs();
  const minDate =
    mode === "future"
      ? today
      : min
      ? isMobile
        ? parseDateMobile(String(min))
        : dayjs(min)
      : undefined;
  const maxDate =
    mode === "past"
      ? today
      : max
      ? isMobile
        ? parseDateMobile(String(max))
        : dayjs(max)
      : undefined;

  const elemId = id || name;

  useEffect(() => {
    if (value) {
      const parsedDate = parseDate(value);
      setSelectedDate(parsedDate);
      setHasPlaceholder(!parsedDate);
    }
  }, [value, isMobile]);

  // Use auto-detected placeholder if no custom placeholder is provided
  const autoPlaceholder = getPlaceholder(type);
  const finalPlaceholder = placeholder || autoPlaceholder;

  const getPickerProps = () => {
    const baseProps = {
      ref,
      value: selectedDate,
      onChange: handleDateChange,
      onBlur: onBlurHandler,
      disabled,
      placeholder: finalPlaceholder,
      format: getDisplayFormat(type),
      showTime:
        type !== "date"
          ? {
              use12Hours: type === "time" ? false : true,
            }
          : undefined,
      picker: type === "time" ? "time" : ("date" as const),
      disabledDate: (current: dayjs.Dayjs) => {
        if (minDate && current.isBefore(minDate, "day")) return true;
        if (maxDate && current.isAfter(maxDate, "day")) return true;
        return false;
      },
    } as DatePickerProps;

    return baseProps;
  };

  // Mobile DatePicker props
  const getMobilePickerProps = () => {
    // Convert dayjs to Date for mobile picker
    const mobileMinDate =
      minDate instanceof Date ? minDate : minDate?.toDate?.();
    const mobileMaxDate =
      maxDate instanceof Date ? maxDate : maxDate?.toDate?.();

    return {
      ref,
      showTwoColumnMonthYearPicker: true,
      showTimeSelectOnly: type === "time",
      showTimeSelect: type !== "date",
      selected: selectedDate,
      timeFormat: "HH:mm aa",
      timeIntervals: 1,
      onChange: handleDateChange,
      onBlur: onBlurHandler,
      dateFormat:
        type === "time"
          ? "HH:mm"
          : type === "datetime-local"
          ? "MMM d, yyyy HH:mm a"
          : "MMM d, yyyy",
      disabled,
      readOnly,
      minDate: mobileMinDate,
      maxDate: mobileMaxDate,
      className: cx("border border-gray-300 rounded-md p-2 pl-10 w-full", {
        "placeholder-gray-400": hasPlaceholder,
      }),
      placeholderText: finalPlaceholder,
      isClearable: !disabled,
      showYearDropdown: true,
      showMonthDropdown: true,
      scrollableYearDropdown: true,
      yearDropdownItemNumber: 100,
      todayButton: (
        <div>
          {type !== "date" ? (
            <button
              disabled={
                minDate !== null &&
                minDate !== undefined &&
                minDate > new Date()
              }
              onClick={() => {
                const dateNow = new Date();
                setSelectedDate(dateNow);
                setTimeout(() => handleDateChange(new Date(dateNow)), 0);
              }}
            >
              Now
            </button>
          ) : (
            <button
              disabled={
                minDate !== null &&
                minDate !== undefined &&
                minDate > new Date()
              }
              onClick={() => {
                const todayDate = new Date();
                todayDate.setHours(0, 0, 0, 0);
                setSelectedDate(todayDate);
                setTimeout(() => handleDateChange(new Date(todayDate)), 0);
              }}
            >
              Today
            </button>
          )}
        </div>
      ),
    };
  };

  return (
    <>
      {pattern && <input type="hidden" value={pattern} />}
      {defaultValue && <input type="hidden" value={defaultValue} />}
      <Field {...fieldProps} htmlFor={elemId}>
        <div className="relative flex items-center custom-datepicker">
          <span className="absolute left-3 text-gray-500 z-[1]">
            <Icon
              name={icon || "calendar"}
              className={cx({
                ["opacity-38"]: disabled,
                ["text-neutral-shade-58"]: !disabled,
              })}
            />
          </span>

          {isMobile ? (
            <ReactDatePicker {...getMobilePickerProps()} />
          ) : (
            <DatePicker
              {...getPickerProps()}
              className={cx(
                "border border-gray-300 rounded-md p-2 pl-10 w-full",
                { "placeholder-gray-400": hasPlaceholder }
              )}
            />
          )}
        </div>
      </Field>
    </>
  );
}

export default forwardRef(BaseDateTimePicker);
