import type { ForwardedRef } from "react";
import type { InputProps } from "../../input/Input";
import type { FieldProps } from "../Field";
import { forwardRef } from "react";
import Input from "../../input/Input";
import Field from "../Field";

export type FieldInputProps = FieldProps & InputProps;

function FieldInput(
  {
    htmlFor,
    label,
    required,
    caption,
    error,
    containerClassName,
    ...inputProps
  }: FieldInputProps,
  ref: ForwardedRef<HTMLInputElement>
): JSX.Element {
  return (
    <Field
      htmlFor={htmlFor}
      label={label}
      required={required}
      caption={caption}
      error={error}
      className={containerClassName}
    >
      <Input {...inputProps} ref={ref} error={error} />
    </Field>
  );
}

export default forwardRef(FieldInput);
