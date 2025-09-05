import { IconSpinner } from "@/components/iconSpinner";
import cx from "classnames";
import type { ButtonHTMLAttributes, ForwardedRef } from "react";
import { forwardRef } from "react";

export type SvgButtonProps = Omit<
  ButtonHTMLAttributes<HTMLButtonElement>,
  "children"
> & {
  svgPath: string;
  loading?: boolean;
};

function SvgButton(
  { svgPath, className, loading = false, ...props }: SvgButtonProps,
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
      {loading ? (
        <IconSpinner className="flex" />
      ) : (
        <img src={svgPath} width="23px" height="20px" />
      )}
    </button>
  );
}

export default forwardRef(SvgButton);
