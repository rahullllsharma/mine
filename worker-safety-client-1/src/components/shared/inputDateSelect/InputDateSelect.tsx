import type { PropsWithClassName } from "@/types/Generic";
import type { IconName } from "@urbint/silica";
import type { ForwardedRef, HTMLProps } from "react";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import React, { forwardRef, useRef } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import ButtonIcon from "../button/icon/ButtonIcon";

// Expects all normal props for defined for a HTMLInputElement
export type InputProps = HTMLProps<HTMLInputElement> &
  PropsWithClassName<{
    containerClassName?: string;
    hasError?: boolean;
    icon?: IconName;
    maxDate?: Date | null;
    minDate?: Date | null;
    dateFormat?: string;
    closeIcon?: boolean;
    onDateChange: (date: Date | null) => void;
    selectedDate: Date | null;
    label?: string;
    hintText?: string;
    hintStyle?: string;
  }>;

const containerStaticStyles =
  "relative flex w-full items-center text-base font-normal text-neutral-shade-100 rounded-md border border-solid";

function InputDateSelect(
  {
    icon,
    className,
    containerClassName,
    hasError = false,
    disabled,
    readOnly,
    placeholder,
    maxDate,
    minDate,
    dateFormat = "MM-dd-yyyy",
    onDateChange,
    selectedDate,
    closeIcon = true,
    label,
    hintText,
    hintStyle,
    ...props
  }: InputProps,
  ref: ForwardedRef<HTMLInputElement>
): JSX.Element {
  const datePickerRef = useRef<DatePicker>(null);

  const handleClearDate = () => {
    onDateChange(null); // Set the selected date to null to clear it
  };

  // Custom input component for DatePicker
  const CustomInput = React.forwardRef<
    HTMLInputElement,
    HTMLProps<HTMLInputElement>
  >((inputProps, customRef) => (
    <div className="relative">
      <input
        {...inputProps}
        {...props}
        ref={customRef}
        className={cx(
          "flex-auto rounded-md appearance-none focus:outline-none",
          "disabled:bg-neutral-light-77 read-only:cursor-default",
          "disabled:cursor-not-allowed disabled:opacity-38 min-w-0 w-full",
          className,
          {
            ["bg-transparent"]: readOnly,
            ["p-2"]: !readOnly,
          }
        )}
      />
      {/* Display the close icon only when a date is selected */}
      {!readOnly && selectedDate && closeIcon && (
        <ButtonIcon
          className="absolute top-0 right-0 px-2 py-0.5 text-sm focus:outline-none"
          iconName="close_big"
          onClick={handleClearDate}
        />
      )}
    </div>
  ));
  CustomInput.displayName = "CustomInput";

  return (
    <>
      {label && (
        <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold leading-normal ">
          {label}
        </label>
      )}
      {hintText && (
        <div className={hintStyle}>
          <span>
            Please select a date between yesterday and two weeks in the future.
          </span>
        </div>
      )}
      <div
        className={cx(containerStaticStyles, containerClassName, {
          ["border-system-error-40 focus-within:ring-system-error-40"]:
            hasError,
          ["border-neutral-shade-26 rounded-md focus-within:ring-1 focus-within:ring-brand-gray-60 bg-neutral-light-100"]:
            !hasError && !readOnly,
          ["bg-transparent border-none"]: readOnly,
        })}
      >
        {icon && !readOnly && (
          <button
            disabled={disabled || readOnly}
            className="ml-2 w-6 h-6 text-xl leading-none bg-white focus:outline-none"
            onClick={() => {
              if (datePickerRef && datePickerRef.current) {
                datePickerRef.current.setOpen(true); // Open the date picker
              }
            }}
          >
            <Icon
              name={icon}
              className={cx({
                ["opacity-38"]: disabled,
                ["text-neutral-shade-58"]: !disabled,
              })}
            />
          </button>
        )}
        {/* wrapper above input field */}
        <DatePicker
          selected={selectedDate}
          maxDate={maxDate}
          minDate={minDate}
          dateFormat={dateFormat}
          onChange={onDateChange}
          placeholderText={readOnly ? "" : placeholder}
          disabled={disabled || readOnly}
          customInput={<CustomInput ref={ref} />}
          className={cx(
            "flex-auto rounded-md appearance-none focus:outline-none disabled:bg-neutral-light-77 read-only:cursor-default disabled:cursor-not-allowed disabled:opacity-38 min-w-0",
            className,
            {
              ["p-2"]: !readOnly,
            }
          )}
          ref={datePickerRef}
        />
      </div>
    </>
  );
}

export default forwardRef(InputDateSelect);
