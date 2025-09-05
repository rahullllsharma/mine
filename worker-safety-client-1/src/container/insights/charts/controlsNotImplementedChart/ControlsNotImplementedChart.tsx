import type { BarDatum, ComputedDatum } from "@nivo/bar";
import type { StackedBarChartDataDescription } from "@/components/charts/stackedBarChart/types";
import type { ChartItem } from "@/container/insights/chartDrillDown/ChartDrillDown";

import type { ControlDrillDownDatum } from "@/container/insights/charts/controlsNotImplementedChart/mapControlsDrillDownData";
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
    key: "percent",
    color: getColor(colors => colors.brand.urbint["40"]),
    hoverColor: getColor(colors => colors.brand.urbint["50"]),
    selectedColor: getColor(colors => colors.brand.urbint["60"]),
  },
];

export type ControlData = {
  percent: number;
  libraryControl: {
    id: string;
    name: string;
  };
};

type DrillDownChart = {
  title: string;
  data?: ControlDrillDownDatum[];
  label: string;
};

const chartComponent = (
  { title, data, label }: DrillDownChart,
  selected?: ComputedDatum<BarDatum>
): ChartItem => {
  return {
    title,
    content: data && selected && selected.data && (
      <StackedBarChart
        data={data}
        dataDescription={drillDownChartDescription}
        indexBy="name"
        bottomAxisLabel={label}
        leftAxisLabel={`% that '${selected.data.control}' was not implemented`}
        tooltipLabel={datum =>
          `${selected.data.control} was not implemented ${datum.value}% of the time for ${label}: ${datum.data.name}`
        }
        axisIntegersOnly
        smallEmptyState
      />
    ),
  };
};

export type ControlsNotImplementedChartProps = {
  tab: InsightsTab;
  controlsData: { percent: number; libraryControl: { name: string } }[];
  onClick: (bar: ComputedDatum<BarDatum>) => void;
  selected?: ComputedDatum<BarDatum>;
  charts: DrillDownChart[];
  filtersDescriptions?: FiltersDescriptionsReturn;
};

export default function ControlsNotImplementedChart({
  tab,
  controlsData,
  onClick,
  selected,
  charts,
  filtersDescriptions,
}: ControlsNotImplementedChartProps): JSX.Element {
  const { control } = useTenantStore(state => state.getAllEntities());
  const chartTitle = `${control.labelPlural} Not Implemented`;

  const isDownloadableChart = !!selected?.data?.control;

  const chartData = isDownloadableChart
    ? formatDrillDownChartsDataWithFilters({
        type: "control",
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        selected: selected!.data.control as string,
        primaryData: controlsData,
        drilldownData: charts,
        filters: filtersDescriptions,
      })
    : [];

  const workbookFilename = useGenerateFilenameChart(tab, chartTitle, {
    filters: filtersDescriptions,
  });

  if (controlsData.length) {
    return (
      <>
        <div className="h-160">
          <StackedBarChart
            workbookFilename={workbookFilename}
            chartTitle={chartTitle}
            workbookData={chartData}
            workbookDownloadable={isDownloadableChart}
            workbookActionTitle="Please select one chart"
            data={controlsData.map(({ percent, libraryControl }) => {
              return { percent: percent * 100, control: libraryControl.name };
            })}
            dataDescription={drillDownChartDescription}
            indexBy="control"
            bottomAxisLabel={control.label}
            leftAxisLabel={`% of ${control.labelPlural.toLowerCase()} not implemented`}
            tooltipLabel={datum =>
              `${datum.data.control} was not implemented ${datum.value}% of the time`
            }
            leftAxisFormat={(v: number) => `${v}%`}
            onClick={onClick}
            selected={selected}
          />
        </div>
        <ChartDrillDown
          type="control"
          inputValue={selected?.data?.control ?? ""}
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
