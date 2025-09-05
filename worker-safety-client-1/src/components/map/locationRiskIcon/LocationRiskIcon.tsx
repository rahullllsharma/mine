import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import {
  getDefaultTextColorByRiskLevel,
  getLocationRiskIconBackgroundColorByRiskLevel,
  getRiskIcon,
} from "@/utils/risk";

export type LocationRiskIconProps = {
  riskLevel: RiskLevel;
  label: string;
  isActive?: boolean;
  isCritical?: boolean;
};

export default function LocationRiskIcon({
  riskLevel,
  label,
  isActive = false,
  isCritical = false,
}: LocationRiskIconProps): JSX.Element {
  const iconName = getRiskIcon(riskLevel) ?? "help_questionmark";
  return (
    <div
      className={cx(
        "flex justify-center items-center w-auto min-w-[1.25rem] h-5 text-base rounded-full shadow-10 hover:ring hover:ring-white",
        getLocationRiskIconBackgroundColorByRiskLevel(riskLevel),
        getDefaultTextColorByRiskLevel(riskLevel),
        {
          "ring ring-white": isActive,
        }
      )}
      role="status"
      aria-label={label}
    >
      <Icon name={iconName} />
      {isCritical && (
        <Icon
          name={"warning"}
          className={cx(
            "pointer-events-none text-lg bg-transparent mx-1 leading-none",
            getDefaultTextColorByRiskLevel(riskLevel)
          )}
        />
      )}
    </div>
  );
}
