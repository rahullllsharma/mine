import type { FormField } from "@/utils/formField";
import type { IconName } from "@urbint/silica";
import type { Option } from "fp-ts/lib/Option";
import type * as t from "io-ts";
import * as O from "fp-ts/lib/Option";
import * as E from "fp-ts/lib/Either";
import cx from "classnames";
import { InputLayout } from "./InputLayout";

type CommonInputProps<V> = {
  id?: string;
  className?: string;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  hasError?: boolean;
  htmlFor?: string;
  field: FormField<t.Errors, string, V>;
  onChange: (raw: string) => void;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  placeholder?: string;
};

type InputDateTimeType = "date" | "time" | "datetime-local";
type InputDefaultType = "text" | "number";

export type InputProps<V> = CommonInputProps<V> &
  (
    | {
        type: InputDefaultType;
        icon?: IconName;
      }
    | {
        type: InputDateTimeType;
      }
  );

function getIcon<T>(props: InputProps<T>): Option<IconName> {
  switch (props.type) {
    case "text":
    case "number":
      return props.icon ? O.some(props.icon) : O.none;
    case "date":
    case "datetime-local":
      return O.some("calendar");
    case "time":
      return O.some("clock");
  }
}

function Input<V>(props: InputProps<V>) {
  const {
    id,
    className,
    type = "text",
    disabled,
    hasError = false,
    required = false,
    label,
    field,
    onChange,
    placeholder = "",
    onKeyDown,
  } = props;
  const { raw } = field;

  const icon = getIcon(props);

  return (
    <InputLayout
      id={id}
      className={className}
      label={label}
      field={field}
      disabled={disabled}
      icon={icon}
    >
      <input
        disabled={disabled}
        type={type}
        required={required}
        value={raw}
        aria-invalid={E.isLeft(field.val)}
        onChange={e => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        className={cx(
          "flex-auto appearance-none rounded-md",
          "min-w-0 p-2 h-9",
          "focus:outline-none read-only:cursor-default",
          "disabled:bg-neutral-light-77 disabled:cursor-not-allowed disabled:opacity-38",
          { ["border-system-error-50"]: hasError }
        )}
        placeholder={placeholder}
      />
    </InputLayout>
  );
}

export { Input };
