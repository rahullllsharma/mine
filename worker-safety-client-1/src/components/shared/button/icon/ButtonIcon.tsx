import { IconSpinner } from "@/components/iconSpinner";
import type { IconName } from "@urbint/silica";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import type { ButtonHTMLAttributes, ForwardedRef } from "react";
import { forwardRef } from "react";

export type ButtonIconProps = Omit<
  ButtonHTMLAttributes<HTMLButtonElement>,
  "children"
> & {
  iconName: IconName;
  loading?: boolean;
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
};

function ButtonIcon(
  { iconName, className, loading = false, ...props }: ButtonIconProps,
  ref: ForwardedRef<HTMLButtonElement>
): JSX.Element {
  return (
    <button
      {...props}
      disabled={props.disabled || loading}
      ref={ref}
      className={cx(
        "text-xl text-neutral-shade-75 disabled:text-neutral-shade-38 disabled:cursor-not-allowed",
        className
      )}
    >
      {loading ? <IconSpinner className="flex" /> : <Icon name={iconName} />}
    </button>
  );
}

export default forwardRef(ButtonIcon);
