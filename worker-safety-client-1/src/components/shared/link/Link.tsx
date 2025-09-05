import type { IconName } from "@urbint/silica";
import type { AnchorHTMLAttributes, ForwardedRef } from "react";
import { Icon } from "@urbint/silica";
import React, { forwardRef } from "react";
import cx from "classnames";

export type LinkProps = Omit<
  AnchorHTMLAttributes<HTMLAnchorElement>,
  "children"
> & {
  label?: string | number;
  iconLeft?: IconName;
  iconRight?: IconName;
  allowWrapping?: boolean;
};

const staticStyles =
  "font-medium text-brand-urbint-50 leading-5 cursor-pointer inline-flex items-center active:text-brand-urbint-60 hover:text-brand-urbint-40";

function Link(
  {
    className,
    label,
    iconLeft,
    iconRight,
    allowWrapping = false,
    ...props
  }: LinkProps,
  ref: ForwardedRef<HTMLAnchorElement>
) {
  return (
    <a ref={ref} {...props} className={cx(staticStyles, className)}>
      {iconLeft && <Icon name={iconLeft} className="text-lg leading-5 mr-1" />}
      {label && (
        <span className={cx({ truncate: !allowWrapping })}>{label}</span>
      )}
      {iconRight && (
        <Icon name={iconRight} className="text-lg leading-5 ml-1" />
      )}
    </a>
  );
}

export default forwardRef(Link);
