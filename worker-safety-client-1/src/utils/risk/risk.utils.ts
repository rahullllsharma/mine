import type { IconName } from "@urbint/silica";
import cx from "classnames";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";

const getTextColorByRiskLevel = (risk?: RiskLevel): string => {
  return cx({
    "text-risk-high": risk === RiskLevel.HIGH,
    "text-risk-medium": risk === RiskLevel.MEDIUM,
    "text-risk-low": risk === RiskLevel.LOW,
    "text-neutral-shade-75":
      risk === RiskLevel.UNKNOWN || risk === RiskLevel.RECALCULATING,
  });
};

const getDefaultTextColorByRiskLevel = (risk: RiskLevel): string => {
  switch (risk) {
    case RiskLevel.MEDIUM:
      return "text-neutral-shade-100";
    case RiskLevel.UNKNOWN:
    case RiskLevel.RECALCULATING:
      return "text-neutral-shade-75";
    default:
      return "text-white";
  }
};

const getBackgroundColorByRiskLevel = (risk: RiskLevel): string => {
  return cx({
    "bg-risk-high": risk === RiskLevel.HIGH,
    "bg-risk-medium": risk === RiskLevel.MEDIUM,
    "bg-risk-low": risk === RiskLevel.LOW,
    "bg-risk-unknown": risk === RiskLevel.UNKNOWN,
    "bg-risk-recalculating": risk === RiskLevel.RECALCULATING,
  });
};

const getBackgroundHoverColorByRiskLevel = (risk: RiskLevel): string => {
  return cx({
    "hover:bg-risk-hover-high": risk === RiskLevel.HIGH,
    "hover:bg-risk-hover-medium": risk === RiskLevel.MEDIUM,
    "hover:bg-risk-hover-low": risk === RiskLevel.LOW,
  });
};

const getBorderColorByRiskLevel = (risk: RiskLevel): string => {
  return cx({
    "border-risk-high": risk === RiskLevel.HIGH,
    "border-risk-medium": risk === RiskLevel.MEDIUM,
    "border-risk-low": risk === RiskLevel.LOW,
    "border-risk-unknown": risk === RiskLevel.UNKNOWN,
  });
};

const getLocationRiskIconBackgroundColorByRiskLevel = (risk: RiskLevel) => {
  switch (risk) {
    case RiskLevel.HIGH:
      return "bg-risk-high";
    case RiskLevel.MEDIUM:
      return "bg-risk-medium";
    case RiskLevel.LOW:
      return "bg-risk-low";
    default:
      return "bg-brand-gray-30";
  }
};

const getRiskIcon = (risk?: RiskLevel): IconName | undefined => {
  switch (risk) {
    case RiskLevel.HIGH:
      return "chevron_up";
    case RiskLevel.MEDIUM:
      return "tilde";
    case RiskLevel.LOW:
      return "chevron_down";
    default:
      return undefined;
  }
};

function sentenceCap(s: string): string {
  return `${s[0].toUpperCase()}${s.substring(1).toLowerCase()}`;
}

export {
  getTextColorByRiskLevel,
  getDefaultTextColorByRiskLevel,
  getBackgroundColorByRiskLevel,
  getBackgroundHoverColorByRiskLevel,
  getBorderColorByRiskLevel,
  getLocationRiskIconBackgroundColorByRiskLevel,
  getRiskIcon,
  sentenceCap,
};
