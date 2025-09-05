import type { ForwardedRef } from "react";
import type { ButtonProps } from "../Button";
import cx from "classnames";
import { forwardRef } from "react";
import Button from "../Button";

function ButtonLarge(
  { className, label, controlStateClass, ...tailProps }: ButtonProps,
  ref: ForwardedRef<HTMLButtonElement>
): JSX.Element {
  const customClassName = `text-lg rounded-md font-semibold ${className}`;

  return (
    <Button
      className={customClassName}
      controlStateClass={cx("px-3 py-1", controlStateClass)}
      label={label}
      ref={ref}
      {...tailProps}
    ></Button>
  );
}

export default forwardRef(ButtonLarge);
