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
 * The FieldTimePicker built for the worker-safety-client.
 *
 * @description
 * For this project, we can use a simpler component that reuses the native
 * _input[type="time"]_ for everything (agreeded with the design team).
 *
 * It also uses the browser language settings for formatting the time and we can't change to
 * 12/24h, without build it from scratch.
 *
 * **HOWEVER** This component is *NOT* silica ready!
 * For that, we need to build a custom picker that will be consistent across desktop devices while
 * still provinding a good experience for mobile users.
 *
 * @see [MDN input type](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/time)
 */
function FieldTimePicker(
  props: FieldDatePickerProps,
  ref: ForwardedRef<HTMLInputElement>
): JSX.Element {
  return <BaseFieldDateTimePicker {...props} ref={ref} type="time" />;
}

export default forwardRef(FieldTimePicker);
