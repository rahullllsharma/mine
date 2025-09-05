/* eslint-disable @typescript-eslint/no-explicit-any */
import type { StackedBarChartDataDescription } from "../types";
import type { BarTooltipProps, BarDatum, ComputedDatum } from "@nivo/bar";
import type { Theme } from "@nivo/core";
import { chain, maxBy, partial, includes } from "lodash";
import isEqual from "lodash/isEqual";
import pick from "lodash/pick";
import { CustomLegendSymbolShape } from "../LegendSymbolShape";

export const datumTotal = (keys: string[], datum: BarDatum): number =>
  chain(Object.keys(datum))
    .filter(key => includes(keys, key))
    .map(key => datum[key])
    .sum()
    .value();

export const calcMaxValue = (data: BarDatum[], keys: string[]): number => {
  const largestDatum = maxBy(data, partial(datumTotal, keys));
  return largestDatum ? datumTotal(keys, largestDatum) : 0;
};

export const buildKeysAndColors = (
  dataDescription: StackedBarChartDataDescription[]
): {
  keys: string[];
  descByKey: { [key: string]: StackedBarChartDataDescription };
} => {
  const keys = dataDescription
    .map(({ key }) => key)
    .filter((x): x is string => !!x);
  const descByKey: { [key: string]: StackedBarChartDataDescription } = {};
  dataDescription.map(desc => {
    desc.hoverColor = desc.hoverColor || desc.color;
    desc.selectedColor = desc.selectedColor || desc.hoverColor || desc.color;
    descByKey[desc.key] = desc;
  });

  return { keys, descByKey };
};

type Threshold = {
  maxWidth: number;
  minBarCount: number;
  xAxisFactor?: number;
};

type ChartDimensions = {
  width: number;
  barCount: number;
};

const thresholds: Threshold[] = [
  { maxWidth: 850, minBarCount: 14, xAxisFactor: 1 },
  { maxWidth: 1500, minBarCount: 25, xAxisFactor: 1 },
  { maxWidth: 700, minBarCount: 25, xAxisFactor: 2 },
  { maxWidth: 500, minBarCount: 25, xAxisFactor: 3 },
  { maxWidth: 4000, minBarCount: 50, xAxisFactor: 1 },
  { maxWidth: 1800, minBarCount: 50, xAxisFactor: 2 },
  { maxWidth: 900, minBarCount: 50, xAxisFactor: 3 },
  { maxWidth: 700, minBarCount: 50, xAxisFactor: 4 },
  { maxWidth: 500, minBarCount: 50, xAxisFactor: 7 },
];

const hasMetThreshold: (
  dims: ChartDimensions,
  threshold: Threshold
) => boolean = ({ barCount, width }, { maxWidth, minBarCount }) =>
  barCount >= minBarCount && width <= maxWidth;

// rotate to preventing x-axis label collisions
export const shouldRotateXLabels = (dims: ChartDimensions): boolean =>
  thresholds.some(thresh => hasMetThreshold(dims, thresh));

// return a factor to filter x-axis ticks by
export const calcXAxisFactor = (dims: ChartDimensions): number =>
  maxBy(
    thresholds.filter(partial(hasMetThreshold, dims)),
    ({ xAxisFactor }) => xAxisFactor
  )?.xAxisFactor || 1;

const fallbackBarColor = "#00ff00";

export const theme: Theme = {
  legends: {
    text: {
      fontSize: 13,
      fontFamily: "Inter, sans-serif",
    },
  },
  axis: {
    legend: {
      text: {
        fontSize: 16,
        fontFamily: "Inter, sans-serif",
        fontWeight: "bold",
      },
    },
  },
};

export const renderTooltip = (
  datum: BarTooltipProps<BarDatum>,
  tooltipLabel?: (datum: BarTooltipProps<BarDatum>) => string
): JSX.Element => {
  const label = tooltipLabel
    ? tooltipLabel(datum)
    : `${datum.id}: ${datum.value}`;
  return (
    <div
      className={
        "bg-white p-2 rounded-sm shadow-10 text-base font-semibold break-words max-w-[10rem]"
      }
    >
      {label}
    </div>
  );
};

export const legendDescription = (descByKey: {
  [key: string]: StackedBarChartDataDescription;
}): any => ({
  dataFrom: "keys",
  anchor: "right",
  direction: "column",
  justify: false,
  translateX: 120,
  translateY: 0,
  itemsSpacing: 8,
  itemWidth: 100,
  itemHeight: 40,
  symbolSize: 34,
  symbolShape: function LegendSymbolWrapper({ ...props }: any) {
    return (
      <CustomLegendSymbolShape
        {...props}
        fill={descByKey[props.id].color || "#000"}
      />
    );
  },
});

const isSelected = (
  multipleKeys: boolean,
  selected: ComputedDatum<BarDatum> | undefined,
  data: ComputedDatum<BarDatum>
) => {
  if (selected) {
    // in a non-'stacked' (only one key) context, the indexValue
    // is compared - this survives across filter changes that update
    // chart data
    const fields = multipleKeys ? ["id", "index"] : ["indexValue"];
    return isEqual(pick(selected, fields), pick(data, fields));
  }
  return false;
};

export const colorForDatum = (
  datum: ComputedDatum<BarDatum>,
  descByKey: { [key: string]: StackedBarChartDataDescription },
  selected?: ComputedDatum<BarDatum>,
  hovering = false
): string => {
  const datumIsSelected = isSelected(
    Object.keys(descByKey).length > 1,
    selected,
    datum
  );
  let colorOrFn;
  if (datumIsSelected) {
    colorOrFn = descByKey[datum.id].selectedColor;
  } else if (hovering) {
    colorOrFn = descByKey[datum.id].hoverColor;
  } else {
    colorOrFn = descByKey[datum.id].color;
  }

  if (typeof colorOrFn == "function") {
    return colorOrFn(datum) || fallbackBarColor;
  }
  return colorOrFn || fallbackBarColor;
};

export const barAriaLabel = function (datum: ComputedDatum<BarDatum>): string {
  return datum.id + ": " + datum.formattedValue + " for: " + datum.indexValue;
};
