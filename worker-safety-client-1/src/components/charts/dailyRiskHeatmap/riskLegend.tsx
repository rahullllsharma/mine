/* eslint-disable @typescript-eslint/no-explicit-any */
import cx from "classnames";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { getBackgroundColorByRiskLevel, sentenceCap } from "@/utils/risk";

function legendLabel(level: RiskLevel, index: number): JSX.Element {
  return (
    <div key={index} className="flex flex-row items-center py-2">
      <div
        className={cx(
          "w-[37px] h-[37px] rounded",
          getBackgroundColorByRiskLevel(level)
        )}
      />
      <span className="pl-2 whitespace-nowrap">
        {sentenceCap(`${level} risk`)}
      </span>
    </div>
  );
}

const riskLevels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH];

export function riskLegend(): JSX.Element {
  return (
    <div className="pt-11 pl-2">
      <span className="font-semibold text-sm">Risk level</span>
      {riskLevels.map(legendLabel)}
    </div>
  );
}
