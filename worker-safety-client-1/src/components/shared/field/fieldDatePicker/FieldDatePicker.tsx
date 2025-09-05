import type { ForwardedRef } from "react";
import type { FieldDateTimePickerProps } from "../BaseFieldDateTimePicker";
import { forwardRef } from "react";
import BaseFieldDateTimePicker from "../BaseFieldDateTimePicker";

export type FieldDatePickerProps = Omit<
  FieldDateTimePickerProps,
  "type" | "icon" | "pattern"
> &
  Required<Pick<FieldDateTimePickerProps, "name">>;

/**
 * The FieldDatePicker built for the worker-safety-client.
 *
 * @description
 * For this project, we can use a simpler component that reuses the native
 * _input[type="date"]_ for everything (agreeded with the design team).
 *
 * It also uses the browser language settings for formatting the date.
 *
 * **HOWEVER** This component is *NOT* silica ready!
 * For that, we need to build a custom picker that will be consistent across desktop devices while
 * still provinding a good experience for mobile users.
 *
 * @see [MDN input type](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/date)
 */
function FieldDatePicker(
  props: FieldDatePickerProps,
  ref: ForwardedRef<HTMLInputElement>
): JSX.Element {
  return <BaseFieldDateTimePicker {...props} type="date" ref={ref} />;
}

export default forwardRef(FieldDatePicker);
