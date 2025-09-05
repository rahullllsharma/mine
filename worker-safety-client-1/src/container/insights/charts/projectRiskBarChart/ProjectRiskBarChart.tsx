import type { LegendLabelDatum, BarTooltipProps, BarDatum } from "@nivo/bar";
import type { FiltersPayload } from "@/container/insights/charts/types";
import type { FiltersDescriptionsReturn } from "@/container/insights/charts/hooks/useFiltersDescriptions";
import cx from "classnames";
import { useState, useEffect, useCallback } from "react";
import { useLazyQuery } from "@apollo/client";
import lowerCase from "lodash/lowerCase";

import StackedBarChart from "@/components/charts/stackedBarChart/StackedBarChart";
import PortfolioPlanningProjectRiskCountQuery from "@/graphql/queries/insights/portfolioPlanningProjectRiskCount.gql";
import PortfolioLearningsProjectRiskCountQuery from "@/graphql/queries/insights/portfolioLearningsProjectRiskCount.gql";
import {
  prepChartData,
  riskBarChartDescription,
} from "@/components/charts/utils";
import { InsightsMode, InsightsTab } from "@/container/insights/charts/types";
import {
  formatChartDataWithFilters,
  lazyQueryOpts,
} from "@/container/insights/charts/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { useGenerateFilenameChart } from "../hooks/useGenerateFilenameChart";

export type ProjectRiskBarChartProps = {
  mode: InsightsMode;
  filters?: FiltersPayload;
  filtersDescriptions?: FiltersDescriptionsReturn;
  setHasData?: (hasData: boolean) => void;
};

export default function ProjectRiskBarChart({
  mode,
  filters,
  filtersDescriptions,
  setHasData,
}: ProjectRiskBarChartProps): JSX.Element | null {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const [localHasData, setLocalHasData] = useState<boolean>(false);

  const updateHasData = useCallback(
    (v: boolean) => {
      setLocalHasData(v);
      setHasData && setHasData(v);
    },
    [setLocalHasData, setHasData]
  );

  const [chartData, setChartData] = useState<BarDatum[]>([]);

  const [getProjectRiskCount] = useLazyQuery(
    mode === InsightsMode.PLANNING
      ? PortfolioPlanningProjectRiskCountQuery
      : PortfolioLearningsProjectRiskCountQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ portfolioPlanning, portfolioLearnings }) =>
        setChartData(
          prepChartData(
            portfolioPlanning?.projectRiskLevelOverTime ||
              portfolioLearnings?.projectRiskLevelOverTime,
            filters?.startDate,
            filters?.endDate
          )
        ),
    }
  );

  useEffect(() => {
    if (filters) getProjectRiskCount({ variables: { filters } });
  }, [filters, getProjectRiskCount]);

  const legendLabel = useCallback(
    (datum: LegendLabelDatum<BarDatum>) => `${datum.id} risk`,
    []
  );

  const tooltipLabel = useCallback(
    (datum: BarTooltipProps<BarDatum>) => {
      const riskLabel = lowerCase(datum.id.toString());
      return `${datum.value} ${riskLabel} risk ${
        datum.value === 1
          ? workPackage.label.toLowerCase()
          : workPackage.labelPlural.toLowerCase()
      }`;
    },
    [workPackage.label, workPackage.labelPlural]
  );

  const title = `${workPackage.label} risk over time`;

  // Although the component is called Project, it was only being used in Portfolio tabs.
  const workbookFilename = useGenerateFilenameChart(
    InsightsTab.PORTFOLIO,
    title
  );

  return (
    <div className={cx({ ["h-160"]: localHasData })}>
      <StackedBarChart
        chartTitle={title}
        workbookFilename={workbookFilename}
        workbookData={formatChartDataWithFilters({
          chartData,
          chartTitle: title,
          filtersData: filtersDescriptions,
        })}
        data={chartData}
        dataDescription={riskBarChartDescription}
        indexBy="date"
        legendTitle="Risk level"
        legendLabel={legendLabel}
        bottomAxisLabel="Time frame"
        leftAxisLabel={`# of ${workPackage.labelPlural}`}
        tooltipLabel={tooltipLabel}
        axisIntegersOnly
        enableBarLabels
        setHasData={updateHasData}
      />
    </div>
  );
}
