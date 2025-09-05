import type {
  BarTooltipProps,
  BarDatum,
  BarLayer,
  BarItemProps,
  BarSvgProps,
  LegendLabelDatum,
  ComputedDatum,
} from "@nivo/bar";
import type { WorkbookData } from "@/components/fileDownloadDropdown/providers/spreadsheet";
import type { StackedBarChartDataDescription } from "./types";
import { Bar } from "@nivo/bar";
import { ResponsiveWrapper } from "@nivo/core";
import { useEffect, useMemo, useCallback } from "react";
import EmptyChart from "@/components/emptyChart/EmptyChart";
import ChartHeader from "@/container/insights/charts/chartHeader/ChartHeader";
import { CustomBarComponent } from "./CustomBarComponent";
import { buildChartLayers } from "./chartSvgLayers";
import { axisBottom, axisLeft } from "./chartAxesHelpers";
import {
  calcMaxValue,
  buildKeysAndColors,
  legendDescription,
  colorForDatum,
  renderTooltip,
  theme,
  barAriaLabel,
} from "./utils";

export type StackedBarChartProps = {
  data: BarDatum[];
  dataDescription: StackedBarChartDataDescription[];
  indexBy: string;
  chartTitle?: string;
  legendTitle?: string;
  tooltipLabel?: (datum: BarTooltipProps<BarDatum>) => string;
  showTooltip?: boolean;
  bottomAxisLabel?: string;
  leftAxisLabel?: string;
  indexByAxisTickCount?: number;
  chartProps?: Omit<BarSvgProps<BarDatum>, "data" | "height" | "width">;
  legendLabel?: (datum: LegendLabelDatum<BarDatum>) => string;
  leftAxisFormat?: (val: number) => string;
  onClick?: (
    datum: ComputedDatum<BarDatum> & { color: string },
    event: React.MouseEvent<Element>
  ) => void;
  selected?: ComputedDatum<BarDatum>;
  layout?: "vertical" | "horizontal";
  enableBarLabels?: boolean;
  axisIntegersOnly?: boolean;
  setHasData?: (hasData: boolean) => void;
  smallEmptyState?: boolean;
  workbookData?: WorkbookData;
  workbookDownloadable?: boolean;
  workbookActionTitle?: string;
  workbookFilename?: string;
};

export default function StackedBarChart({
  data,
  dataDescription,
  indexBy,
  chartTitle,
  legendTitle,
  tooltipLabel,
  showTooltip = true,
  bottomAxisLabel,
  leftAxisLabel,
  indexByAxisTickCount = 5,
  chartProps = {},
  legendLabel,
  leftAxisFormat = (val: number) => `${val}`,
  onClick,
  selected,
  layout = "vertical",
  enableBarLabels = false,
  axisIntegersOnly = false,
  setHasData,
  smallEmptyState = false,
  workbookData,
  workbookDownloadable,
  workbookActionTitle,
  workbookFilename,
}: StackedBarChartProps): JSX.Element {
  const { keys, descByKey } = useMemo(
    () => buildKeysAndColors(dataDescription),
    [dataDescription]
  );
  const hasLegend = useMemo(() => Boolean(legendTitle), [legendTitle]);

  const maxValueWithPadding = useMemo(() => {
    const maxValue = calcMaxValue(data, keys);
    return maxValue * 1.1;
  }, [data, keys]); // add a 1/10th of the value

  const hasData = maxValueWithPadding > 0;
  useEffect(() => {
    if (setHasData) setHasData(hasData);
  }, [setHasData, hasData]);

  const margin = useMemo(
    () => ({
      top: 20,
      right: hasLegend ? 174 : 30,
      bottom: 80,
      left: layout === "vertical" ? 96 : 180,
    }),
    [layout, hasLegend]
  );

  const colors = useCallback(
    (datum: ComputedDatum<BarDatum>) =>
      colorForDatum(datum, descByKey, selected),
    [descByKey, selected]
  );

  const onMouseEnter = useCallback(
    (datum, event) => {
      const hoverColor = colorForDatum(datum, descByKey, selected, true);
      event.currentTarget.setAttribute("style", `fill: ${hoverColor};`);
      if (onClick) event.currentTarget.classList.add("cursor-pointer");
    },
    [selected, descByKey, onClick]
  );

  const onMouseLeave = useCallback(
    (datum, event) => {
      const color = colorForDatum(datum, descByKey, selected);
      event.currentTarget.setAttribute("style", `fill: ${color}`);
    },
    [selected, descByKey]
  );

  const layers: BarLayer<BarDatum>[] = useMemo(
    () =>
      buildChartLayers({
        keys,
        legendTitle,
        descByKey,
        layout,
        enableBarLabels,
      }),
    [keys, legendTitle, descByKey, layout, enableBarLabels]
  );

  const barComponent = useCallback(
    (datum: BarItemProps<BarDatum>) => (
      <CustomBarComponent reversedKeys={keys.slice().reverse()} {...datum} />
    ),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [keys, selected]
    // include selected to ensure the bars 'deselect' properly
  );

  const tooltip = useMemo(() => {
    return showTooltip
      ? (datum: BarTooltipProps<BarDatum>) => renderTooltip(datum, tooltipLabel)
      : () => null;
  }, [showTooltip, tooltipLabel]);

  const axisBottomCB = useCallback(
    width =>
      axisBottom({
        width,
        data,
        layout,
        indexBy,
        axisIntegersOnly,
        maxValueWithPadding,
        indexByAxisTickCount,
        bottomAxisLabel,
      }),
    [
      data,
      layout,
      indexBy,
      axisIntegersOnly,
      maxValueWithPadding,
      indexByAxisTickCount,
      bottomAxisLabel,
    ]
  );

  const axisLeftCB = useMemo(
    () =>
      axisLeft({
        layout,
        axisIntegersOnly,
        maxValueWithPadding,
        indexByAxisTickCount,
        leftAxisLabel,
        leftAxisFormat,
      }),
    [
      layout,
      axisIntegersOnly,
      maxValueWithPadding,
      indexByAxisTickCount,
      leftAxisLabel,
      leftAxisFormat,
    ]
  );

  const legends = useMemo(
    () => (hasLegend ? [legendDescription(descByKey)] : []),
    [descByKey, hasLegend]
  );

  if (!hasData) {
    return (
      <EmptyChart
        title={chartTitle || ""}
        description="There is currently no data available for this chart"
        small={smallEmptyState}
      />
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      {chartTitle && workbookFilename ? (
        <ChartHeader
          title={chartTitle}
          chartData={workbookData}
          chartFilename={workbookFilename}
          downloadable={workbookDownloadable}
          actionTitle={workbookActionTitle}
        />
      ) : null}
      <div className="relative w-full h-full">
        <div className="absolute w-full h-full">
          <ResponsiveWrapper>
            {({ width, height }) => (
              <Bar<BarDatum>
                layout={layout}
                onClick={onClick}
                width={width}
                height={height}
                data={data}
                // keys controls the stack order, first key on bottom, last on top
                keys={keys}
                indexBy={indexBy}
                colors={colors}
                theme={theme}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}
                layers={layers}
                margin={margin}
                // space between bars
                padding={0.55}
                // disable horizontal bg lines
                enableGridY={false}
                // disable the default labels here
                // ours are not centered, impled via barLabelsLayer
                enableLabel={false}
                // set a maxValue to pad the top of the chart
                maxValue={maxValueWithPadding}
                borderWidth={1}
                borderColor="#f7f8f8"
                // custom bar component that handles rounding the top corners
                barComponent={barComponent}
                tooltip={tooltip}
                axisBottom={axisBottomCB(width)}
                axisLeft={axisLeftCB}
                {...(legendLabel && hasLegend
                  ? { legendLabel: legendLabel }
                  : {})}
                legends={legends}
                role="application"
                ariaLabel={chartTitle || "Stacked Bar Chart"}
                barAriaLabel={barAriaLabel}
                {...chartProps}
              />
            )}
          </ResponsiveWrapper>
        </div>
      </div>
    </div>
  );
}
