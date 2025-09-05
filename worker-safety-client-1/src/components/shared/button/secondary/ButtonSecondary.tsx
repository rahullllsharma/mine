import type { ButtonProps } from "../Button";
import type { ButtonSize } from "../ButtonSize";
import type { ForwardedRef } from "react";
import cx from "classnames";
import { forwardRef } from "react";
import { getButtonBySize } from "../utils";

export type ButtonSecondaryProps = ButtonProps & {
  disabled?: boolean;
  size?: ButtonSize;
};

function ButtonSecondary(
  { size, className, ...props }: ButtonSecondaryProps,
  ref: ForwardedRef<HTMLButtonElement>
): JSX.Element {
  const Button = getButtonBySize(size);

  return (
    <Button
      {...props}
      ref={ref}
      className={cx(
        "bg-neutral-light-100 border border-neutral-shade-26 shadow-5 hover:shadow-10 text-neutral-shade-75",
        className
      )}
    />
  );
}
export default forwardRef(ButtonSecondary);
