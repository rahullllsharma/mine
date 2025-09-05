import type { BarDatum, ComputedDatum } from "@nivo/bar";
import type { StackedBarChartDataDescription } from "@/components/charts/stackedBarChart/types";
import type { ChartItem } from "@/container/insights/chartDrillDown/ChartDrillDown";

import type { HazardDrillDownDatum } from "@/container/insights/charts/applicableHazardsChart/mapHazardsDrillDownData";
import type { FiltersDescriptionsReturn } from "../hooks/useFiltersDescriptions";
import type { InsightsTab } from "../types";
import EmptyChart from "@/components/emptyChart/EmptyChart";
import { getColor } from "@/utils/shared/tailwind";
import ChartDrillDown from "@/container/insights/chartDrillDown/ChartDrillDown";
import StackedBarChart from "@/components/charts/stackedBarChart/StackedBarChart";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { useGenerateFilenameChart } from "../hooks/useGenerateFilenameChart";
import { formatDrillDownChartsDataWithFilters } from "../utils";

const drillDownChartDescription: StackedBarChartDataDescription[] = [
  {
    key: "count",
    color: getColor(colors => colors.brand.urbint["40"]),
    hoverColor: getColor(colors => colors.brand.urbint["50"]),
    selectedColor: getColor(colors => colors.brand.urbint["60"]),
  },
];

export type HazardData = {
  count: number;
  libraryHazard: {
    id: string;
    name: string;
  };
};

type DrillDownChart = {
  title: string;
  data?: HazardDrillDownDatum[];
  label: string;
};

const wasApplicableTimes = (value: number) =>
  `was applicable ${value} ${value === 1 ? "time" : "times"}`;

const chartComponent = (
  { title, data, label }: DrillDownChart,
  selected?: ComputedDatum<BarDatum>
): ChartItem => ({
  title,
  content: data && selected && selected.data && (
    <StackedBarChart
      data={data}
      dataDescription={drillDownChartDescription}
      indexBy="name"
      bottomAxisLabel={label}
      leftAxisLabel={`# of times '${selected.data.hazard}' was applicable`}
      tooltipLabel={datum =>
        `${selected.data.hazard} ${wasApplicableTimes(
          datum.value
        )} for ${label}: ${datum.data.name}`
      }
      axisIntegersOnly
      smallEmptyState
    />
  ),
});

export type ApplicableHazardsChartProps = {
  tab: InsightsTab;
  hazardsData: { count: number; libraryHazard: { name: string } }[];
  onClick: (bar: ComputedDatum<BarDatum>) => void;
  selected?: ComputedDatum<BarDatum>;
  charts: DrillDownChart[];
  filtersDescriptions?: FiltersDescriptionsReturn;
};

export default function ApplicableHazardsChart({
  tab,
  hazardsData,
  onClick,
  selected,
  charts,
  filtersDescriptions,
}: ApplicableHazardsChartProps): JSX.Element {
  const { hazard } = useTenantStore(state => state.getAllEntities());
  const isDownloadableChart = !!selected?.data?.hazard;
  const chartData = isDownloadableChart
    ? formatDrillDownChartsDataWithFilters({
        type: "hazard",
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        selected: selected!.data.hazard as string,
        primaryData: hazardsData,
        drilldownData: charts,
        filters: filtersDescriptions,
      })
    : [];

  const chartTitle = `Applicable ${hazard.labelPlural}`;

  const workbookFilename = useGenerateFilenameChart(tab, chartTitle, {
    filters: filtersDescriptions,
  });

  if (hazardsData.length) {
    return (
      <>
        <div className="h-160">
          <StackedBarChart
            workbookFilename={workbookFilename}
            chartTitle={chartTitle}
            workbookData={chartData}
            workbookDownloadable={isDownloadableChart}
            workbookActionTitle="Please select one chart"
            data={hazardsData.map(({ count, libraryHazard }) => {
              return { count: count, hazard: libraryHazard.name };
            })}
            dataDescription={drillDownChartDescription}
            indexBy="hazard"
            bottomAxisLabel={hazard.label}
            leftAxisLabel={`# of times ${hazard.label.toLowerCase()} was applicable`}
            tooltipLabel={datum =>
              `${datum.data.hazard} ${wasApplicableTimes(datum.value)}`
            }
            onClick={onClick}
            selected={selected}
            axisIntegersOnly
          />
        </div>
        <ChartDrillDown
          type="hazard"
          inputValue={selected?.data?.hazard ?? ""}
          charts={charts.map(chart => chartComponent(chart, selected))}
        />
      </>
    );
  }

  return (
    <EmptyChart
      title={chartTitle}
      description="There is currently no data available for this chart"
    />
  );
}
