import type { IconName } from "@urbint/silica";
import type {
  ButtonHTMLAttributes,
  ForwardedRef,
  HTMLAttributes,
  ReactElement,
  ReactNode,
} from "react";
import { Icon } from "@urbint/silica";
import React, { forwardRef } from "react";

import cx from "classnames";
import { IconSpinner } from "@/components/iconSpinner";

export type ButtonProps = Omit<
  HTMLAttributes<HTMLButtonElement>,
  "children"
> & {
  controlStateClass?: string;
  iconStart?: IconName;
  iconEnd?: IconName;
  label?: string | ReactElement;
  disabled?: boolean;
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  type?: ButtonHTMLAttributes<HTMLButtonElement>["type"];
  loading?: boolean;
  labelClassName?: string;
  iconStartClassName?: string;
  children?: ReactNode;
  iconEndClassName?: string;
};

function Button(
  {
    className,
    controlStateClass,
    iconStart,
    iconEnd,
    label,
    type = "button",
    loading = false,
    iconStartClassName = "",
    labelClassName = "",
    children,
    iconEndClassName = "",
    ...tailProps
  }: ButtonProps,
  ref: ForwardedRef<HTMLButtonElement>
): JSX.Element {
  const enableControlClassName = tailProps.disabled
    ? ""
    : "hover:bg-neutral-light-16 focus:bg-neutral-shade-7 active:bg-neutral-shade-7";

  return (
    <button
      className={`text-center truncate disabled:opacity-38 disabled:cursor-not-allowed ${className}`}
      type={type}
      ref={ref}
      {...tailProps}
      disabled={tailProps.disabled || loading}
    >
      <div
        className={`flex items-center justify-center h-full ${enableControlClassName} ${controlStateClass}`}
      >
        {iconStart && <Icon className={iconStartClassName} name={iconStart} />}
        {label && (
          <span className={cx("mx-1 truncate", labelClassName)}>{label}</span>
        )}
        {children}
        {loading && <IconSpinner />}
        {iconEnd && !loading && (
          <Icon name={iconEnd} className={iconEndClassName} />
        )}
      </div>
    </button>
  );
}

export default forwardRef(Button);
