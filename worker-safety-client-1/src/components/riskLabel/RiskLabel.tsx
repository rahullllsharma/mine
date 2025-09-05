import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { Badge } from "@urbint/silica";
import cx from "classnames";
import { getRiskIcon, getTextColorByRiskLevel } from "@/utils/risk/";

export interface RiskLabelProps {
  risk: RiskLevel;
  label: string;
  isCritical?: boolean;
}

export default function RiskLabel({
  risk,
  label,
  isCritical = false,
}: RiskLabelProps): JSX.Element {
  return (
    <Badge
      className={cx(
        "whitespace-nowrap bg-white shadow-none",
        getTextColorByRiskLevel(risk),
        "text-base"
      )}
      iconStart={getRiskIcon(risk)}
      label={label}
      iconEnd={isCritical ? "warning" : undefined}
    />
  );
}
