import type { PropsWithClassName } from "@/types/Generic";
import type { ForwardedRef, HTMLProps } from "react";
import type { IconName } from "@urbint/silica";
import { forwardRef } from "react";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import ButtonIcon from "../button/icon/ButtonIcon";

// The Field* component will limit that, following the same principles defined on silica.
// Expects all normal props for defined for a HTMLInputElement
export type InputProps = HTMLProps<HTMLInputElement> &
  PropsWithClassName<{
    containerClassName?: string;
    error?: string;
    icon?: IconName;
    allowClear?: boolean;
    clearInputText?: () => void;
  }>;

const containerStaticStyles = `relative flex w-full items-center text-base font-normal text-neutral-shade-100 rounded-md border border-solid`;

function Input(
  {
    icon,
    className,
    containerClassName,
    type = "text",
    error = "",
    disabled,
    readOnly,
    placeholder,
    allowClear,
    clearInputText,
    ...props
  }: InputProps,
  ref: ForwardedRef<HTMLInputElement>
): JSX.Element {
  return (
    <div
      className={cx(containerStaticStyles, containerClassName, {
        ["border-system-error-40 focus-within:ring-system-error-40"]: !!error,
        ["border-neutral-shade-26 rounded-md focus-within:ring-1 focus-within:ring-brand-gray-60 bg-neutral-light-100"]:
          !error && !readOnly,
        ["bg-transparent border-none"]: readOnly,
      })}
    >
      {icon && !readOnly && (
        <Icon
          name={icon}
          className={cx(
            "ml-2 pointer-events-none w-6 h-6 text-xl leading-none bg-white",
            {
              ["opacity-38"]: disabled,
              ["text-neutral-shade-58"]: !disabled,
            }
          )}
        />
      )}
      <input
        {...props}
        ref={ref}
        aria-invalid={!!error}
        aria-errormessage={error}
        type={type}
        disabled={disabled}
        readOnly={readOnly}
        placeholder={readOnly ? undefined : placeholder}
        className={cx(
          "flex-auto rounded-md appearance-none focus:outline-none disabled:bg-neutral-light-77 read-only:cursor-default disabled:cursor-not-allowed disabled:opacity-38 min-w-0",
          className,
          {
            ["bg-transparent"]: readOnly,
            ["p-2"]: !readOnly,
          }
        )}
      ></input>
      {allowClear && props.value && (
        <ButtonIcon
          iconName="close_small"
          className={cx(
            "ml-2 pointer-events-auto w-6 h-6 text-xl leading-none bg-white",
            {
              ["opacity-38"]: disabled,
              ["text-neutral-shade-58"]: !disabled,
            }
          )}
          onClick={clearInputText}
        />
      )}
    </div>
  );
}

export default forwardRef(Input);
