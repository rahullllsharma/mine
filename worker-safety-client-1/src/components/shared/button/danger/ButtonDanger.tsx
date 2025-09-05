import type { ForwardedRef } from "react";
import type { ButtonProps } from "../Button";
import type { ButtonSize } from "../ButtonSize";
import { forwardRef } from "react";
import cx from "classnames";
import { getButtonBySize } from "../utils";

export type ButtonDangerProps = ButtonProps & {
  disabled?: boolean;
  size?: ButtonSize;
};

function ButtonDanger(
  { size, className, ...props }: ButtonDangerProps,
  ref: ForwardedRef<HTMLButtonElement>
): JSX.Element {
  const Button = getButtonBySize(size);

  return (
    <Button
      {...props}
      ref={ref}
      className={cx("text-white bg-system-error-40", className)}
    />
  );
}

export default forwardRef(ButtonDanger);
