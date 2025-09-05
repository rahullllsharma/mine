import type { ForwardedRef } from "react";
import type { ButtonProps } from "../Button";
import { forwardRef } from "react";
import Button from "../Button";

function ButtonRegular(
  { className, label, ...tailProps }: ButtonProps,
  ref: ForwardedRef<HTMLButtonElement>
): JSX.Element {
  const customClassName = `text-base rounded-md font-semibold ${className}`;

  return (
    <Button
      className={customClassName}
      controlStateClass="px-2.5 py-2"
      label={label}
      ref={ref}
      {...tailProps}
    ></Button>
  );
}

export default forwardRef(ButtonRegular);
