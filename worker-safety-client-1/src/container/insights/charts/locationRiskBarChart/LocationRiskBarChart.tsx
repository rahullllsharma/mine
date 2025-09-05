import type { LegendLabelDatum, BarTooltipProps, BarDatum } from "@nivo/bar";
import type { FiltersPayload } from "@/container/insights/charts/types";
import type { FiltersDescriptionsReturn } from "../hooks/useFiltersDescriptions";
import cx from "classnames";
import { useState, useEffect, useCallback } from "react";
import { useLazyQuery } from "@apollo/client";
import lowerCase from "lodash/lowerCase";

import StackedBarChart from "@/components/charts/stackedBarChart/StackedBarChart";
import ProjectPlanningLocationRiskCountQuery from "@/graphql/queries/insights/projectPlanningLocationRiskCount.gql";
import ProjectLearningsLocationRiskCountQuery from "@/graphql/queries/insights/projectLearningsLocationRiskCount.gql";
import {
  prepChartData,
  riskBarChartDescription,
} from "@/components/charts/utils";
import { InsightsMode } from "@/container/insights/charts/types";
import {
  formatChartDataWithFilters,
  lazyQueryOpts,
  getProjectDescriptionFromFilters,
} from "@/container/insights/charts/utils";
import { generateExportedProjectFilename } from "@/utils/files/shared";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export type LocationRiskBarChartProps = {
  mode: InsightsMode;
  filters?: FiltersPayload;
  filtersDescriptions?: FiltersDescriptionsReturn;
  setHasData?: (hasData: boolean) => void;
};

export default function LocationRiskBarChart({
  mode,
  filters,
  filtersDescriptions,
  setHasData,
}: LocationRiskBarChartProps): JSX.Element | null {
  const { location } = useTenantStore(state => state.getAllEntities());
  const [localHasData, setLocalHasData] = useState<boolean>(false);

  const updateHasData = useCallback(
    (v: boolean) => {
      setLocalHasData(v);
      setHasData && setHasData(v);
    },
    [setLocalHasData, setHasData]
  );

  const [chartData, setChartData] = useState<BarDatum[]>([]);

  const [getLocationRiskCount] = useLazyQuery(
    mode === InsightsMode.PLANNING
      ? ProjectPlanningLocationRiskCountQuery
      : ProjectLearningsLocationRiskCountQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ projectPlanning, projectLearnings }) =>
        setChartData(
          prepChartData(
            projectPlanning?.locationRiskLevelOverTime ||
              projectLearnings?.locationRiskLevelOverTime,
            filters?.startDate,
            filters?.endDate
          )
        ),
    }
  );

  useEffect(() => {
    if (filters) getLocationRiskCount({ variables: { filters } });
  }, [filters, getLocationRiskCount]);

  const legendLabel = useCallback(
    (datum: LegendLabelDatum<BarDatum>) => `${datum.id} risk`,
    []
  );

  const tooltipLabel = useCallback(
    (datum: BarTooltipProps<BarDatum>) => {
      const riskLabel = lowerCase(datum.id.toString());
      return `${datum.value} ${riskLabel} risk ${
        datum.value === 1
          ? location.label.toLowerCase()
          : location.labelPlural.toLowerCase()
      }`;
    },
    [location.label, location.labelPlural]
  );

  const title = `${location.label} risk over time`;

  return (
    <div className={cx({ ["h-160"]: localHasData })}>
      <StackedBarChart
        chartTitle={title}
        workbookFilename={generateExportedProjectFilename({
          title,
          project: getProjectDescriptionFromFilters({
            filters,
            filtersDescriptions,
          }),
        })}
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
        leftAxisLabel={`# of ${location.labelPlural}`}
        tooltipLabel={tooltipLabel}
        axisIntegersOnly
        enableBarLabels
        setHasData={updateHasData}
      />
    </div>
  );
}
