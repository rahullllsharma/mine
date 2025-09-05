import type { StackedBarChartDataDescription } from "@/components/charts/stackedBarChart/types";
import type { FiltersPayload } from "@/container/insights/charts/types";
import type { FiltersDescriptionsReturn } from "../hooks/useFiltersDescriptions";
import cx from "classnames";
import { useState, useEffect, useCallback } from "react";
import { useLazyQuery } from "@apollo/client";

import PortfolioLearningsReasonsNotImplementedCountQuery from "@/graphql/queries/insights/portfolioLearningsReasonsNotImplementedCount.gql";
import ProjectLearningsReasonsNotImplementedCountQuery from "@/graphql/queries/insights/projectLearningsReasonsNotImplementedCount.gql";

import { getColor } from "@/utils/shared/tailwind";
import StackedBarChart from "@/components/charts/stackedBarChart/StackedBarChart";
import { getControlNotPerformedOptions } from "@/container/report/jobHazardAnalysis/constants";

import { InsightsTab } from "@/container/insights/charts/types";
import {
  formatChartDataWithFilters,
  lazyQueryOpts,
} from "@/container/insights/charts/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { useGenerateFilenameChart } from "../hooks/useGenerateFilenameChart";
import { sortByReasons } from "./sortByReasons";

const getColorOptionsByReason = (): {
  [reason: string]: {
    color: string | undefined;
    labelColor: string | undefined;
  };
} => ({
  [getControlNotPerformedOptions()[0].id]: {
    color: getColor(colors => colors.data.purple["60"]),
    labelColor: "#ffffff",
  },
  [getControlNotPerformedOptions()[1].id]: {
    color: getColor(colors => colors.data.purple["40"]),
    labelColor: "#ffffff",
  },
  [getControlNotPerformedOptions()[2].id]: {
    color: getColor(colors => colors.data.purple["30"]),
    labelColor: "#ffffff",
  },
  [getControlNotPerformedOptions()[3].id]: {
    color: getColor(colors => colors.data.purple["20"]),
    labelColor: getColor(colors => colors.neutral.shade["100"]),
  },
});

const reasonsNotImplementedChartDescription: StackedBarChartDataDescription[] =
  [
    {
      key: "count",
      color: datum =>
        getColorOptionsByReason()[datum.indexValue].color || "#E4E0FF",
      labelColor: datum =>
        getColorOptionsByReason()[datum.indexValue].labelColor || "#041E25",
    },
  ];

export type ReasonNotImplementedCount = {
  reason: string;
  count: number;
};

export type ReasonsNotImplementedBarChartProps = {
  tab: InsightsTab;
  filters?: FiltersPayload;
  filtersDescriptions?: FiltersDescriptionsReturn;
  setHasData?: (hasData: boolean) => void;
};

export default function ReasonsNotImplementedBarChart({
  tab,
  filters,
  filtersDescriptions,
  setHasData,
}: ReasonsNotImplementedBarChartProps): JSX.Element | null {
  const { control } = useTenantStore(state => state.getAllEntities());
  const [localHasData, setLocalHasData] = useState<boolean>(false);

  const updateHasData = useCallback(
    (v: boolean) => {
      setLocalHasData(v);
      setHasData && setHasData(v);
    },
    [setLocalHasData, setHasData]
  );

  const [chartData, setChartData] = useState<ReasonNotImplementedCount[]>([]);

  const [getReasonsData] = useLazyQuery(
    tab === InsightsTab.PORTFOLIO
      ? PortfolioLearningsReasonsNotImplementedCountQuery
      : ProjectLearningsReasonsNotImplementedCountQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ portfolioLearnings, projectLearnings }) =>
        setChartData(
          // make sure reasons are sorted as expected
          sortByReasons(
            projectLearnings?.reasonsControlsNotImplemented ||
              portfolioLearnings?.reasonsControlsNotImplemented
          )
        ),
    }
  );

  useEffect(() => {
    if (filters) getReasonsData({ variables: { filters } });
  }, [filters, getReasonsData]);

  const title = `Reasons for ${control.labelPlural.toLowerCase()} not implemented`;

  const formattedChartData = chartData.map(({ reason, count }) => ({
    "Reason for controls not implemented": reason,
    "# of times reason reported": count,
  }));

  const workbookFilename = useGenerateFilenameChart(tab, title, {
    filters: filtersDescriptions,
  });

  return (
    <div className={cx({ ["h-160"]: localHasData })}>
      <StackedBarChart
        chartTitle={title}
        workbookFilename={workbookFilename}
        workbookData={formatChartDataWithFilters({
          chartTitle: title,
          chartData: formattedChartData,
          filtersData: filtersDescriptions,
        })}
        layout="horizontal"
        data={chartData}
        dataDescription={reasonsNotImplementedChartDescription}
        indexBy="reason"
        bottomAxisLabel="# of times reason reported"
        showTooltip={false}
        enableBarLabels
        axisIntegersOnly
        setHasData={updateHasData}
      />
    </div>
  );
}
