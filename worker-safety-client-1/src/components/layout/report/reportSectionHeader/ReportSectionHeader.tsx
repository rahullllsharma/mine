import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";

export type ReportSectionHeaderProps = PropsWithClassName<{
  title: string;
  subtitle?: string;
}>;

export default function ReportSectionHeader({
  title,
  subtitle,
  className,
}: ReportSectionHeaderProps): JSX.Element {
  return (
    <div className={cx("mb-4 text-neutral-shade-100", className)}>
      <h5 className="font-semibold">{title}</h5>
      {subtitle && (
        <h6 className="font-normal text-xs text-neutral-shade-75">
          {subtitle}
        </h6>
      )}
    </div>
  );
}
