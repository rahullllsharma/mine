import type { Option } from "fp-ts/lib/Option";
import * as O from "fp-ts/lib/Option";

export type OptionalViewProps<T> = {
  value: Option<T>;
  render: (value: T) => JSX.Element;
  renderNone?: () => JSX.Element;
};

export function OptionalView<T>({
  value,
  render,
  renderNone,
}: OptionalViewProps<T>): JSX.Element {
  const renderNoneFn = renderNone ?? (() => <></>);

  return O.isSome(value) ? render(value.value) : renderNoneFn();
}
