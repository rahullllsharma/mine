import type { PropsWithClassName } from "@/types/Generic";

import type { ForwardedRef, HTMLProps } from "react";
import { forwardRef } from "react";
import cx from "classnames";

import styles from "./Checkbox.module.css";

export type CheckboxProps = HTMLProps<HTMLInputElement> &
  PropsWithClassName & {
    hasError?: boolean;
  };

function Checkbox(
  { className, hasError = false, ...props }: CheckboxProps,
  ref: ForwardedRef<HTMLInputElement>
) {
  return (
    <input
      {...props}
      type="checkbox"
      className={cx(
        "flex-shrink-0",
        { "!border-system-error-40": hasError },
        styles.root,
        className
      )}
      ref={ref}
    />
  );
}

export default forwardRef(Checkbox);
