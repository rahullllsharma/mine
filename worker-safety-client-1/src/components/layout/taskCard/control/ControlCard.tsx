import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";

export type ControlProps = PropsWithClassName<{ label: string }>;

export default function Control({
  label,
  children,
  className = "",
}: ControlProps): JSX.Element {
  return (
    <div
      className={cx(
        "flex text-base text-neutral-shade-100 p-3 border-dashed border border-brand-gray-30 rounded",
        className
      )}
      data-testid="controlCard"
    >
      <span className="flex-1">{label}</span>
      {children}
    </div>
  );
}
