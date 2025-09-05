import { Badge } from "@urbint/silica";
import classnames from "classnames";
import { RiskLevel } from "@/api/generated/types";
import {
  getBackgroundColorByRiskLevel,
  getDefaultTextColorByRiskLevel,
  getRiskIcon,
} from "../utils";

const RiskBadgeAnimated = ({ label }: { label: string }): JSX.Element => {
  return (
    <div
      className="flex items-center font-bold shadow-5 h-5 rounded-full px-1.5 py-0.5 w-max uppercase whitespace-nowrap bg-risk-recalculating text-neutral-shade-75"
      role="note"
    >
      <span className="text-tiny m-1">{label}</span>
    </div>
  );
};

export type RiskBadgeProps = {
  risk: RiskLevel;
  label: string;
};

function RiskBadge({ risk, label }: RiskBadgeProps) {
  if (risk === RiskLevel.Recalculating) {
    return <RiskBadgeAnimated label={label?.toUpperCase()} />;
  }

  return (
    <Badge
      className={classnames(
        "whitespace-nowrap",
        getBackgroundColorByRiskLevel(risk),
        getDefaultTextColorByRiskLevel(risk)
      )}
      iconStart={getRiskIcon(risk)}
      label={label?.toUpperCase()}
    />
  );
}

export { RiskBadge };
