import type { BarDatum } from "@nivo/bar";
import type { LocationRiskCount, ProjectRiskCount } from "../types";
import { chain, sortBy } from "lodash";
import { getColor } from "@/utils/shared/tailwind";
import {
  getFormattedDate,
  convertToDate,
  getDayRangeBetween,
} from "@/utils/date/helper";
import { groupBy } from "@/container/Utils";

import { RiskLevel } from "@/components/riskBadge/RiskLevel";

// A description for a risk stacked bar chart
// The order is important, as it sets the stacking order in the chart
// (first on bottom, last on top)
export const riskBarChartDescription: {
  key: "High" | "Medium" | "Low";
  level: RiskLevel;
  color?: string;
  hoverColor?: string;
}[] = [
  {
    key: "High",
    level: RiskLevel.HIGH,
    color: getColor(colors => colors.risk.high),
    hoverColor: getColor(colors => colors.risk.hover.high),
  },
  {
    key: "Medium",
    level: RiskLevel.MEDIUM,
    color: getColor(colors => colors.risk.medium),
    hoverColor: getColor(colors => colors.risk.hover.medium),
  },
  {
    key: "Low",
    level: RiskLevel.LOW,
    color: getColor(colors => colors.risk.low),
    hoverColor: getColor(colors => colors.risk.hover.low),
  },
];

function countForRisk(
  riskCounts: LocationRiskCount[] | ProjectRiskCount[],
  riskLevel: RiskLevel
): number {
  const data = chain(riskCounts)
    .filter({ riskLevel: riskLevel })
    .first()
    .value();
  return (data && data.count) || 0;
}

// Converts the api types to the chart's expected data type.
// Essentially: group-by-date, then set the count for each riskLevel
export function prepChartData(
  data: LocationRiskCount[] | ProjectRiskCount[],
  startDate?: string,
  endDate?: string
): BarDatum[] {
  const hasDates = startDate && endDate;
  if (!hasDates) return [];

  const groupedByDate = groupBy(data, "date");
  const dateRange = getDayRangeBetween(startDate as string, endDate as string);

  const chartData = dateRange.map(date => {
    const values = groupedByDate[date];
    const datum: BarDatum = {
      date: getFormattedDate(date, "numeric", "2-digit"),
    };

    if (values) {
      return riskBarChartDescription.reduce((chartDatum, { key, level }) => {
        const count = countForRisk(values, level);
        if (count) {
          chartDatum[key] = count;
        }
        return chartDatum;
      }, datum);
    }
    return datum;
  });

  return sortBy(chartData, ({ date }) => convertToDate(date as string));
}
