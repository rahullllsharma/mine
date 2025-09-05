/* eslint-disable @typescript-eslint/no-explicit-any */
import type { AxisProps, AxisTickProps } from "@nivo/axes";
import type { BarDatum } from "@nivo/bar";
import uniq from "lodash/uniq";
import { scaleLinear } from "d3-scale";
import { useTheme } from "@nivo/core";
import { animated } from "@react-spring/web";
import { getFormattedDate } from "@/utils/date/helper";
import { shouldRotateXLabels, calcXAxisFactor } from "./utils";

type XAxisTickProps = {
  tick: AxisTickProps<string>;
  width: number;
  barCount: number;
};

function XAxisTick({ tick, width, barCount }: XAxisTickProps) {
  const {
    value: _value,
    format,
    lineX,
    lineY,
    textBaseline,
    textAnchor,
    animatedProps,
  } = tick;

  const theme = useTheme();
  const value = format?.(_value) ?? _value;
  // subtract magic number to get to useful column widths
  const tickLabelWidth = (width - 180) / barCount;
  const tickOverlap = 6;

  return (
    <animated.g
      transform={`translate(${tick.x},${tick.y})`}
      style={{ opacity: animatedProps.opacity }}
    >
      <line
        x1={0}
        x2={lineX}
        y1={-tickOverlap}
        y2={lineY}
        style={theme.axis.ticks.line}
      />
      {tick.rotate === 0 ? (
        <foreignObject
          x={`-${tickLabelWidth / 2}`}
          y="16"
          height="50"
          width={tickLabelWidth}
        >
          <div
            style={{
              ...theme.axis.ticks.text,
              width: tickLabelWidth,
            }}
            className="text-sm text-center line-clamp-2"
            title={value}
          >
            {value}
          </div>
        </foreignObject>
      ) : (
        <animated.text
          dominantBaseline={textBaseline}
          textAnchor={textAnchor}
          transform={animatedProps.textTransform}
          style={theme.axis.ticks.text}
        >
          <tspan>
            <title>{value}</title>
            {value}
          </tspan>
        </animated.text>
      )}
    </animated.g>
  );
}

const valueFormat: (
  value: string | number | Date
) => string | number | undefined = value => {
  if (value instanceof Date) {
    return getFormattedDate(value, "numeric", "2-digit");
  }
  return value;
};

const allXAxisTickValues = (data: BarDatum[], indexBy: string) =>
  uniq(data.map(datum => datum[indexBy]));

type IndexByAxisTickValueProps = {
  axisIntegersOnly: boolean;
  maxValueWithPadding: number;
  indexByAxisTickCount: number;
};

const indexByAxisTickValues = ({
  axisIntegersOnly,
  maxValueWithPadding,
  indexByAxisTickCount,
}: IndexByAxisTickValueProps) => {
  let vals = scaleLinear()
    .domain([0, maxValueWithPadding])
    .ticks(indexByAxisTickCount)
    .filter((val: number) => val !== 0);

  if (axisIntegersOnly) {
    vals = vals.filter(Number.isInteger);
  }
  return vals;
};

type AxisBottomProps = {
  width: number;
  data: BarDatum[];
  layout: "horizontal" | "vertical";
  indexBy: string;
  axisIntegersOnly: boolean;
  maxValueWithPadding: number;
  indexByAxisTickCount: number;
  bottomAxisLabel?: string;
};

export function axisBottom({
  width,
  data,
  layout,
  indexBy,
  axisIntegersOnly,
  maxValueWithPadding,
  indexByAxisTickCount,
  bottomAxisLabel,
}: AxisBottomProps): AxisProps<any> {
  const barCount = data.length;
  const rotate = shouldRotateXLabels({ barCount, width });
  const xAxisFactor = calcXAxisFactor({ barCount, width });
  const xAxisTickValues = allXAxisTickValues(data, indexBy).filter(
    (_val, i) => {
      return i % xAxisFactor === 0;
    }
  );

  const axisBot: AxisProps<any> = {
    tickSize: 8,
    tickPadding: 5,
    // rotate the x-axis labels to prevent colliding labels
    tickRotation: rotate ? 45 : 0,
    legend: bottomAxisLabel,
    legendPosition: "middle",
    legendOffset: rotate ? 64 : 58,
    format: valueFormat,
  };

  if (layout === "vertical") {
    axisBot.renderTick = (tick: AxisTickProps<string>) =>
      XAxisTick({ tick, width, barCount });
    axisBot.tickValues = xAxisTickValues;
  } else {
    axisBot.tickValues = indexByAxisTickValues({
      axisIntegersOnly,
      maxValueWithPadding,
      indexByAxisTickCount,
    });
  }

  return axisBot;
}

type linesAcc = {
  lines: string[];
  currLine: string;
};

// a modified version of the helper found here:
// https://github.com/plouc/nivo/issues/353#issuecomment-456163387
export const breakIntoTspans = (
  value: string,
  maxLineLength = 36
): JSX.Element[] => {
  const words = value.split(" ");
  const maxLines = 2;

  //reduce the words into lines of maxLineLength
  const assembledLines: linesAcc = words.reduce(
    (acc: linesAcc, word: string) => {
      // if the current line isn't empty and the word + current line is larger than the allowed line size
      // create a new line and update current line
      if ((word + acc.currLine).length > maxLineLength && acc.currLine !== "") {
        return {
          lines: acc.lines.concat([acc.currLine]),
          currLine: word,
        };
      }
      //otherwise add the word to the current line
      return {
        ...acc,
        currLine: acc.currLine + " " + word,
      };
    },
    { lines: [], currLine: "" }
  );

  // add the ending state of current line (the last line) to lines
  const allLines = assembledLines.lines.concat([assembledLines.currLine]);

  // only take `maxLines`
  const lines = allLines.slice(0, maxLines);
  const children: JSX.Element[] = [];
  const dy = 21; // space between lines

  // build a list of <tspan>s, increasing dy for each
  lines.forEach((line, i) => {
    // if on the last line and within 3 of the max length, add ellipsis
    const lineText =
      i === 1 && allLines.length > maxLines
        ? line.slice(0, maxLineLength - 3) + "..."
        : line;
    children.push(
      <tspan x={0} dy={dy * i} key={i}>
        {lineText.trim()}
      </tspan>
    );
  });

  return children;
};

type AxisLeftProps = {
  layout: "horizontal" | "vertical";
  axisIntegersOnly: boolean;
  maxValueWithPadding: number;
  indexByAxisTickCount: number;
  leftAxisLabel?: string;
  leftAxisFormat?: (val: number) => string;
};

export function axisLeft({
  layout,
  axisIntegersOnly,
  maxValueWithPadding,
  indexByAxisTickCount,
  leftAxisLabel,
  leftAxisFormat,
}: AxisLeftProps): AxisProps<any> {
  const axisProps: AxisProps<any> = {
    tickPadding: 5,
    legend: leftAxisLabel ? breakIntoTspans(leftAxisLabel) : undefined,
    legendPosition: "middle",
    legendOffset: -70,
    format: leftAxisFormat,
  };

  if (layout === "vertical") {
    axisProps.tickValues = indexByAxisTickValues({
      axisIntegersOnly,
      maxValueWithPadding,
      indexByAxisTickCount,
    });
    axisProps.tickSize = 14;
    axisProps.tickRotation = 0;
  } else {
    axisProps.tickSize = 0;
  }

  return axisProps;
}
