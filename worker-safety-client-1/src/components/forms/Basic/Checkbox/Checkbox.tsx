import type { ReactNode } from "react";
import classnames from "classnames";

import { constVoid } from "fp-ts/lib/function";
import styles from "./Checkbox.module.css";

export type CheckboxProps = {
  className?: string;
  labelClassName?: string;
  // name: string;
  // value: string;
  // htmlFor: string;
  checked: boolean;
  disabled?: boolean;
  children?: ReactNode;
  // field: FormField<Errors, string, V>;
  onClick: () => void;
};

function Checkbox({
  className,
  labelClassName,
  // htmlFor,
  // name,
  // value,
  checked,
  disabled,
  // field,
  children,
  onClick,
}: CheckboxProps) {
  // const { raw, val, dirty } = field;
  // const hasError = dirty && isLeft(val);
  return (
    <>
      <div
        onClick={disabled ? constVoid : onClick}
        className={classnames("flex flex-row items-center gap-2", className)}
      >
        <input
          className={classnames(
            "flex-shrink-0",
            styles.root
            // { [styles.error]: hasError },
          )}
          // id={htmlFor}
          // name={name}
          // value={value}
          disabled={disabled}
          type="checkbox"
          checked={checked}
          readOnly
        />
        {/* <label htmlFor={htmlFor}>{children}</label> */}
        <label className={classnames("cursor-pointer", labelClassName)}>
          {children}
        </label>
      </div>

      {/* {hasError && <ErrorMessage field={field} />} */}
    </>
  );
}

export { Checkbox };
