import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";

export type ReportSectionBlockProps = PropsWithClassName<{
  isInner?: boolean;
}>;

export default function ReportSectionBlock({
  isInner = false,
  children,
  className,
}: ReportSectionBlockProps): JSX.Element {
  return (
    <div
      className={cx("flex flex-col mb-4 gap-4", className, {
        "bg-brand-gray-10 p-4": isInner,
      })}
    >
      {children}
    </div>
  );
}
