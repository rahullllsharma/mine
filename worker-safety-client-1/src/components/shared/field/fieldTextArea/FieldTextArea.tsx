import type { ChangeEvent, ForwardedRef } from "react";
import type { FieldProps } from "../Field";
import cx from "classnames";
import React, { forwardRef, useEffect } from "react";
import Field from "../Field";
import Paragraph from "../../paragraph/Paragraph";

export type FieldTextAreaProps = FieldProps & {
  id?: string;
  name?: string;
  initialValue?: string;
  placeholder?: string;
  isDisabled?: boolean;
  readOnly?: boolean;
  hasError?: boolean;
  value?: string;
  onChange: (value: string) => void;
  rows?: number;
};

const setElementHeight = (el: HTMLTextAreaElement): void => {
  el.style.height = "inherit";
  el.style.height = `${el.scrollHeight}px`;
};

function FieldTextArea(
  {
    id,
    name,
    initialValue = "",
    placeholder,
    isDisabled = false,
    readOnly,
    hasError = false,
    onChange,
    value,
    rows,
    ...fieldProps
  }: FieldTextAreaProps,
  ref: ForwardedRef<HTMLTextAreaElement>
): JSX.Element {
  const onChangeHandler = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setElementHeight(e.target);
    onChange(e.target.value);
  };

  const shouldUpdateHeight = name && initialValue && !readOnly;

  useEffect(() => {
    if (shouldUpdateHeight) {
      const textAreaElement = document.querySelector(`[name="${name}"]`);
      setElementHeight(textAreaElement as HTMLTextAreaElement);
    }
  }, [shouldUpdateHeight, name]);

  return (
    <Field {...fieldProps} htmlFor={id}>
      {readOnly ? (
        <Paragraph text={initialValue} className="whitespace-pre-wrap" />
      ) : (
        <textarea
          id={id}
          name={name}
          className={cx(
            "w-full max-h-36 text-base text-neutral-shade-100 outline-none focus:border-brand-gray-60 disabled:cursor-not-allowed min-h-12 border border-neutral-shade-37 rounded resize-y py-1 px-2",
            {
              ["border-system-error-40 focus-within:ring-system-error-40"]:
                hasError,
            }
          )}
          defaultValue={initialValue}
          disabled={isDisabled}
          onChange={onChangeHandler}
          aria-label="FieldTextArea"
          ref={ref}
          placeholder={placeholder}
          value={value}
          rows={rows}
        />
      )}
    </Field>
  );
}

export default forwardRef(FieldTextArea);
