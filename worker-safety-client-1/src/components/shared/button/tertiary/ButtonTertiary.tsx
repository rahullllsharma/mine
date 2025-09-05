import type { ButtonProps } from "../Button";
import type { ButtonSize } from "../ButtonSize";
import type { ForwardedRef } from "react";
import cx from "classnames";
import { forwardRef } from "react";
import { getButtonBySize } from "../utils";

export type ButtonTertiaryProps = ButtonProps & {
  disabled?: boolean;
  size?: ButtonSize;
};

function ButtonTertiary(
  { size, className, ...props }: ButtonTertiaryProps,
  ref: ForwardedRef<HTMLButtonElement>
): JSX.Element {
  const Button = getButtonBySize(size);

  return (
    <Button
      {...props}
      ref={ref}
      className={cx("text-neutral-shade-75", className)}
    />
  );
}

export default forwardRef(ButtonTertiary);
