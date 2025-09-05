import type { CommonInputLayoutProps } from "../InputLayout";
import TextMaskInput from "react-text-mask";
import * as O from "fp-ts/lib/Option";

import { InputLayout } from "../InputLayout";

export type TelephoneInputProps<V> = CommonInputLayoutProps<V> & {
  onChange: (raw: string) => void;
  hasError?: boolean;
  errorMessage?: string;
};

function TelephoneInput<V>(props: TelephoneInputProps<V>) {
  const {
    className,
    disabled,
    label,
    field,
    includeInWidget,
    onChange,
    hasError,
    errorMessage,
    mode,
  } = props;
  const { raw } = field;

  const mask = [
    "(",
    /\d/,
    /\d/,
    /\d/,
    ")",
    " ",
    /\d/,
    /\d/,
    /\d/,
    "-",
    /\d/,
    /\d/,
    /\d/,
    /\d/,
  ];

  return (
    <InputLayout
      className={className}
      label={label}
      field={field}
      includeInWidget={includeInWidget}
      disabled={disabled}
      icon={O.some("phone")}
      error={hasError}
      errorMessage={errorMessage}
      mode={mode}
    >
      <TextMaskInput
        mask={mask}
        placeholder="(___) ___-____"
        guide={true}
        disabled={disabled}
        type="text"
        value={raw}
        onChange={e => onChange(e.target.value.replace(/\D/g, ""))}
        className="flex-auto rounded-md appearance-none focus:outline-none disabled:bg-neutral-light-77 read-only:cursor-default disabled:cursor-not-allowed disabled:opacity-38 min-w-0 p-2"
      />
    </InputLayout>
  );
}

export { TelephoneInput };
