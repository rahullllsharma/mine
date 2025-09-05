import type { ForwardedRef } from "react";
import type { ButtonProps } from "../Button";
import { forwardRef } from "react";
import Button from "../Button";

function ButtonSmall(
  { className, label, ...tailProps }: ButtonProps,
  ref: ForwardedRef<HTMLButtonElement>
): JSX.Element {
  const customClassName = `text-sm rounded-md font-semibold ${className}`;

  return (
    <Button
      className={customClassName}
      controlStateClass="px-2 py-1"
      label={label}
      ref={ref}
      {...tailProps}
    ></Button>
  );
}

export default forwardRef(ButtonSmall);
