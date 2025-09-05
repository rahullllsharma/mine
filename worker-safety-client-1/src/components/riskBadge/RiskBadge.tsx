import { Badge, Icon } from "@urbint/silica";
import cx from "classnames";
import {
  getBackgroundColorByRiskLevel,
  getDefaultTextColorByRiskLevel,
  getRiskIcon,
} from "@/utils/risk/";
import { RiskLevel } from "./RiskLevel";

interface RiskBadgeAnimatedProps {
  label: string;
  isCritical?: boolean;
}

const RiskBadgeAnimated = ({
  label,
  isCritical = false,
}: RiskBadgeAnimatedProps): JSX.Element => {
  return (
    <div
      className="flex items-center font-bold shadow-5 h-5 rounded-full px-1.5 py-0.5 w-max uppercase whitespace-nowrap bg-risk-recalculating text-neutral-shade-75"
      role="note"
    >
      {/*<div
        className="animate-spin inline-block border-2 border-r-neutral-shade-75 w-3 h-3 mr-1 rounded-full border-neutral-shade-18"
        role="status"
      />*/}
      <span className="text-tiny m-1">{label}</span>
      {isCritical && (
        <Icon
          name={"warning"}
          className={cx(
            "pointer-events-none text-lg bg-transparent ml-1 leading-none"
          )}
        />
      )}
    </div>
  );
};

export interface RiskBadgeProps {
  risk: RiskLevel;
  label: string;
  isCritical?: boolean;
}

export default function RiskBadge({
  risk,
  label,
  isCritical = false,
}: RiskBadgeProps): JSX.Element {
  if (risk === RiskLevel.RECALCULATING) {
    return (
      <RiskBadgeAnimated label={label?.toUpperCase()} isCritical={isCritical} />
    );
  }

  return (
    <Badge
      className={cx(
        "whitespace-nowrap",
        getBackgroundColorByRiskLevel(risk),
        getDefaultTextColorByRiskLevel(risk)
      )}
      iconStart={getRiskIcon(risk)}
      label={label?.toUpperCase()}
      iconEnd={isCritical ? "warning" : undefined}
    />
  );
}
