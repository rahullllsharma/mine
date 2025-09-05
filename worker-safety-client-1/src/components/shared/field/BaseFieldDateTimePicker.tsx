import type { ChangeEvent, ForwardedRef, FocusEvent } from "react";

import type { IconName } from "@urbint/silica";

import type { FieldProps } from "./Field";
import type { InputProps as AllInputProps } from "@/components/shared/input/Input";
import { forwardRef, useState } from "react";
import cx from "classnames";

import { isSafari } from "react-device-detect";
import Input from "@/components/shared/input/Input";
import Field from "./Field";
import styles from "./BaseFieldDateTimePicker.module.css";

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
    ...fieldProps
  }: FieldDateTimePickerProps,
  ref: ForwardedRef<HTMLInputElement>
): JSX.Element {
  /* We need this because native input type=date does not support a placeholder attribute
  This allow us to follow the "simulate" a placeholder behavior to implement the HHDS guidelines*/
  const [hasPlaceholder, setHasPlaceholder] = useState(
    [value, defaultValue].join("").length === 0
  );

  const onBlurHandler = (e: FocusEvent<HTMLInputElement>) => {
    setHasPlaceholder(e?.target?.value?.length === 0);
    onBlur && onBlur(e);
  };

  const onChangeHandler = (e: ChangeEvent<HTMLInputElement>) => {
    setHasPlaceholder(e?.target?.value?.length === 0);
    onChange && onChange(e?.target?.value);
  };

  const elemId = id || name;
  return (
    <Field {...fieldProps} htmlFor={elemId}>
      <Input
        type={readOnly ? "text" : type}
        icon={iconByInputType[type]}
        ref={ref}
        id={elemId}
        name={name}
        pattern={pattern}
        defaultValue={defaultValue}
        value={value}
        min={min}
        max={max}
        disabled={disabled}
        readOnly={readOnly}
        // Safari doesn't handle very well colors for native pickers when we don't have a value.
        containerClassName={cx({
          ["text-brand-gray-60"]: hasPlaceholder && isSafari,
          ["text-neutral-shade-58"]: hasPlaceholder && !isSafari,
        })}
        className={styles.root}
        error={fieldProps?.error}
        onBlur={onBlurHandler}
        onChange={onChangeHandler}
        placeholder={placeholder}
      />
    </Field>
  );
}

export default forwardRef(BaseFieldDateTimePicker);
