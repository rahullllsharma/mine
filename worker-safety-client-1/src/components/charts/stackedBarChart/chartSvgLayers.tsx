import type { StackedBarChartDataDescription } from "./types";
import type { BarLayer, BarDatum, ComputedDatum } from "@nivo/bar";

import { getColor } from "@/utils/shared/tailwind";
import { datumTotal } from "./utils";

const grayBg = getColor(colors => colors.brand.gray["10"]);
const blackText = getColor(colors => colors.neutral.shade["100"]) || "#333333";
const whiteText = "#ffffff";

type ContextBar = {
  width: number;
  height: number;
  x: number;
  y: number;
  data: ComputedDatum<BarDatum>;
};

// using a minimal type here - the source is just `any` for now
// https://github.com/plouc/nivo/blob/f83ad7bd26b0df489486771ac9ee28f99fff449f/packages/bar/src/Bar.tsx#L358
export type LayerContext = {
  innerWidth: number;
  innerHeight: number;
  bars: ContextBar[];
};

export const backgroundLayer = (
  layerContext: LayerContext,
  isVertical: boolean
): JSX.Element => (
  <rect
    x={isVertical ? "-7" : "0"} // negative here to overlap with the ticks
    rx="3"
    ry="3"
    width={layerContext.innerWidth}
    height={layerContext.innerHeight}
    fill={grayBg}
  />
);

export const legendTitleLayer = (
  layerContext: LayerContext,
  keysLength: number,
  legendTitle: string
): JSX.Element => (
  <text
    x={layerContext.innerWidth + 20}
    y={layerContext.innerHeight / 2 - (50 * keysLength) / 2}
    style={{
      textAnchor: "start",
      fontWeight: 600,
      fontSize: 14,
    }}
  >
    {legendTitle}
  </text>
);

const getLabelColor = (
  data: ComputedDatum<BarDatum>,
  desc: StackedBarChartDataDescription,
  showOutsideBar: boolean
): string => {
  if (showOutsideBar) {
    return blackText;
  }

  if (typeof desc.labelColor === "function") {
    return desc.labelColor(data) || whiteText;
  }

  return desc.labelColor || whiteText;
};

const showOutsideBarThreshold = 40;

const horizontalBarLabel = (
  i: number,
  bar: ContextBar,
  descByKey: {
    [key: string]: StackedBarChartDataDescription;
  }
): JSX.Element | null => {
  const { width, height, y, data } = bar;
  // should we add the label as an overlay, or outside the bar?
  const shouldShowOutsideBar = width < showOutsideBarThreshold;
  const desc = descByKey[data.id];
  const labelColor = getLabelColor(data, desc, shouldShowOutsideBar);

  const xOffset = shouldShowOutsideBar ? 4 : -10;
  if (data.value) {
    // this case might be impossible (nivo shouldn't render a chart with no data.value)
    // but this is cheap and helps the reader
    return (
      <text
        key={i}
        transform={`translate(${width + xOffset}, ${y + height / 2})`}
        textAnchor={shouldShowOutsideBar ? "start" : "end"}
        dominantBaseline="central"
        fill={labelColor}
        className="text-tiny"
      >{`(${data.value ?? ""})`}</text>
    );
  }
  return null;
};

const verticalBarLabel = (
  i: number,
  bar: ContextBar,
  keys: string[]
): JSX.Element | null => {
  const { width, x, y, data } = bar;

  // for vertical layouts, we only show the label when the total value is zero
  if (
    datumTotal(keys, data.data) === 0 &&
    data.id === keys[0] && // only build this for one of the keys
    width > 8 // only show if we have enough space (prevent text collisions)
  ) {
    const yOffset = 14;
    return (
      <text
        key={i}
        transform={`translate(${x + width / 2}, ${y - yOffset})`}
        textAnchor="middle"
        fill={blackText}
        className="text-tiny"
      >
        (0)
      </text>
    );
  }

  return null;
};

// custom labels recommended as layer: https://github.com/plouc/nivo/issues/146#issuecomment-989837745
// and based on solution: https://github.com/plouc/nivo/issues/146#issuecomment-1009184119
export const barLabelsLayer = (
  layerContext: LayerContext,
  descByKey: {
    [key: string]: StackedBarChartDataDescription;
  },
  layout: "vertical" | "horizontal",
  keys: string[]
): JSX.Element => {
  const { bars } = layerContext;

  return (
    <g>
      {bars.map((bar, i: number) => {
        if (layout === "horizontal") {
          return horizontalBarLabel(i, bar, descByKey);
        }
        return verticalBarLabel(i, bar, keys);
      })}
    </g>
  );
};

type BuildChartLayersProps = {
  keys: string[];
  legendTitle?: string;
  descByKey: { [key: string]: StackedBarChartDataDescription };
  layout: "vertical" | "horizontal";
  enableBarLabels?: boolean;
};

export const buildChartLayers = ({
  keys,
  legendTitle,
  descByKey,
  layout,
  enableBarLabels,
}: BuildChartLayersProps): BarLayer<BarDatum>[] => [
  (computedChart: LayerContext) =>
    backgroundLayer(computedChart, layout === "vertical"),
  "grid",
  "axes",
  "bars",
  enableBarLabels
    ? (computedChart: LayerContext) =>
        barLabelsLayer(computedChart, descByKey, layout, keys)
    : () => null,
  "markers",
  "legends",
  legendTitle
    ? (computedChart: LayerContext) =>
        legendTitleLayer(computedChart, keys.length, legendTitle)
    : () => null,
  "annotations",
];
