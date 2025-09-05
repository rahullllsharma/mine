import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";

export default function ReportSectionWrapper({
  className,
  children,
}: PropsWithClassName): JSX.Element {
  return <div className={cx("mb-4", className)}>{children}</div>;
}
