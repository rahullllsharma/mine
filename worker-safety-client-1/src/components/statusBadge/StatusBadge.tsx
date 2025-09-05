import { Badge } from "@urbint/silica";
import cx from "classnames";
import { formatStatusString } from "@/utils/date/helper";

import {
  getBackgroundColorByStatusLevel,
  getDefaultTextColorByStatusLevel,
} from "../../utils/status";

export interface StatusBadgeProps {
  status: string;
  label?: string;
}

export default function StatusBadge({ status }: StatusBadgeProps): JSX.Element {
  return (
    <Badge
      className={cx(
        "whitespace-nowrap normal-case font-medium",
        getBackgroundColorByStatusLevel(status),
        getDefaultTextColorByStatusLevel(status)
      )}
      label={formatStatusString(status)}
    />
  );
}
