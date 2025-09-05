import type { IconName } from "@urbint/silica";
import classnames from "classnames";
import { RiskLevel } from "@/api/generated/types";
import { RiskLevel as RiskBadgeRiskLevel } from "@/components/riskBadge/RiskLevel";

const convertRiskLevelToRiskBadgeRiskLevel = (
  riskLevel: RiskLevel
): RiskBadgeRiskLevel => {
  switch (riskLevel) {
    case RiskLevel.High:
      return RiskBadgeRiskLevel.HIGH;
    case RiskLevel.Medium:
      return RiskBadgeRiskLevel.MEDIUM;
    case RiskLevel.Low:
      return RiskBadgeRiskLevel.LOW;
    case RiskLevel.Unknown:
      return RiskBadgeRiskLevel.UNKNOWN;
    case RiskLevel.Recalculating:
      return RiskBadgeRiskLevel.RECALCULATING;
  }
};

const getBackgroundColorByRiskLevel = (risk: RiskLevel): string => {
  return classnames({
    "bg-risk-high": risk === RiskLevel.High,
    "bg-risk-medium": risk === RiskLevel.Medium,
    "bg-risk-low": risk === RiskLevel.Low,
    "bg-risk-unknown": risk === RiskLevel.Unknown,
    "bg-risk-recalculating": risk === RiskLevel.Recalculating,
  });
};

const getDefaultTextColorByRiskLevel = (risk: RiskLevel): string => {
  switch (risk) {
    case RiskLevel.High:
    case RiskLevel.Low:
      return "text-white";
    case RiskLevel.Medium:
      return "text-neutral-shade-100";
    case RiskLevel.Unknown:
    case RiskLevel.Recalculating:
      return "text-neutral-shade-75";
  }
};

const getRiskIcon = (risk?: RiskLevel): IconName | undefined => {
  switch (risk) {
    case RiskLevel.High:
      return "chevron_up";
    case RiskLevel.Medium:
      return "tilde";
    case RiskLevel.Low:
      return "chevron_down";
    default:
      return undefined;
  }
};

const getBorderColorByRiskLevel = (risk: RiskLevel): string => {
  return classnames({
    "border-risk-high": risk === RiskLevel.High,
    "border-risk-medium": risk === RiskLevel.Medium,
    "border-risk-low": risk === RiskLevel.Low,
    "border-risk-unknown": risk === RiskLevel.Unknown,
  });
};

export {
  convertRiskLevelToRiskBadgeRiskLevel,
  getBackgroundColorByRiskLevel,
  getDefaultTextColorByRiskLevel,
  getBorderColorByRiskLevel,
  getRiskIcon,
};
