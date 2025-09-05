import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";
import { FieldErrorDetectionClassName } from "./utils/field.utils";

export type FieldProps = PropsWithClassName<{
  htmlFor?: string;
  label?: string;
  required?: boolean;
  caption?: string;
  error?: string;
}>;

export default function Field({
  htmlFor,
  label,
  required,
  children,
  caption,
  error,
  className,
}: FieldProps): JSX.Element {
  return (
    <div className={className}>
      {label && (
        <label
          htmlFor={htmlFor}
          className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal"
        >
          {label}
          {required && " *"}
        </label>
      )}
      {children}
      {/* TODO: with `aria-errormessage` to indicate that the span is related with the error in the input */}
      {/* https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-errormessage */}
      {/* catch-error-text is only used for detecting error dom nodes on the rendered screen */}
      {error && (
        <div
          id={`${htmlFor}-err`}
          className={cx("text-red-500 mt-2", FieldErrorDetectionClassName)}
        >
          {error}
        </div>
      )}
      {caption && (
        <p className="text-sm mt-1 text-neutral-shade-75">{caption}</p>
      )}
    </div>
  );
}
