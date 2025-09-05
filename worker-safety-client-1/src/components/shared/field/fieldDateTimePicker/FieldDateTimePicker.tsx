import type { ForwardedRef } from "react";
import type { FieldDateTimePickerProps } from "../BaseFieldDateTimePicker";
import { forwardRef } from "react";
import BaseFieldDateTimePicker from "../BaseFieldDateTimePicker";

export type FieldDatePickerProps = Omit<
  FieldDateTimePickerProps,
  "type" | "icon"
> &
  Required<Pick<FieldDateTimePickerProps, "name">>;

/**
 * The FieldDateTimePicker built for the worker-safety-client.
 *
 * @description
 * For this project, we can use a simpler component that reuses the native
 * _input[type="datetime-local"]_ for everything (agreeded with the design team).
 *
 *
 * **HOWEVER** This component is *NOT* silica ready!
 * For that, we need to build a custom picker that will be consistent across desktop devices while
 * still provinding a good experience for mobile users.
 *
 * @see [MDN input type](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/time)
 */
function FieldDateTimePicker(
  props: FieldDatePickerProps,
  ref: ForwardedRef<HTMLInputElement>
): JSX.Element {
  return (
    <BaseFieldDateTimePicker
      {...props}
      ref={ref}
      type="datetime-local"
      // https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/datetime-local#handling_browser_support
      pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}"
    />
  );
}

export default forwardRef(FieldDateTimePicker);
