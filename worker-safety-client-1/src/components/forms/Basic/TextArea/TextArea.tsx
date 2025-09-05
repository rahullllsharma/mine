import type * as t from "io-ts";
import type { FormField } from "@/utils/formField";
import { none } from "fp-ts/lib/Option";
import * as E from "fp-ts/lib/Either";
import { InputLayout } from "../Input/InputLayout";

export type TextAreaProps<V> = {
  className?: string;
  label?: string;
  disabled?: boolean;
  htmlFor?: string;
  field: FormField<t.Errors, string, V>;
  onChange: (raw: string) => void;
  rows?: number;
  placeholder?: string;
  required?: boolean;
};

export function TextArea<V>(props: TextAreaProps<V>): JSX.Element {
  return (
    <InputLayout
      className={props.className}
      label={props.label}
      field={props.field}
      disabled={props.disabled}
      icon={none}
    >
      <textarea
        className="flex-auto rounded-md appearance-none focus:outline-none disabled:bg-neutral-light-77 read-only:cursor-default disabled:cursor-not-allowed disabled:opacity-38 min-w-0 p-2"
        disabled={props.disabled}
        value={props.field.raw}
        aria-invalid={E.isLeft(props.field.val)}
        placeholder={props.placeholder}
        onChange={e => props.onChange(e.target.value)}
        rows={props.rows}
        required={props.required ?? false}
      />
    </InputLayout>
  );
}
