/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { BarDatum } from "@nivo/bar";
import type { StackedBarChartDataDescription } from "./types";
import { useState } from "react";
import { flatten, range, random, lowerCase } from "lodash";
import { convertToDate } from "@/utils/date/helper";
import { getColor } from "@/utils/shared/tailwind";

import { getControlNotPerformedOptions } from "@/container/report/jobHazardAnalysis/constants";
import StackedBarChart from "./StackedBarChart";

export default {
  title: "Components/Charts/StackedBarChart",
  component: StackedBarChart,
  argTypes: {
    data: { table: { disable: true } },
    onClick: { action: "clicked" },
  },
  decorators: [
    Story => (
      <div style={{ height: "500px" }}>
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof StackedBarChart>;

const Template: ComponentStory<typeof StackedBarChart> = args => {
  const [selected, setSelected] = useState(undefined);

  const onClick = (datum: any, event: any) => {
    args.onClick?.(datum, event);
    setSelected(datum);
  };

  return <StackedBarChart {...args} selected={selected} onClick={onClick} />;
};

const chartDescription: {
  key: string;
  color?: string;
  hoverColor?: string;
}[] = [
  {
    key: "Unknown",
    color: getColor(colors => colors.data.teal["30"]),
    hoverColor: getColor(colors => colors.data.teal["40"]),
  },
  {
    key: "High",
    color: getColor(colors => colors.risk.high),
    hoverColor: getColor(colors => colors.risk.hover.high),
  },
  {
    key: "Medium",
    color: getColor(colors => colors.risk.medium),
    hoverColor: getColor(colors => colors.risk.hover.medium),
  },
  {
    key: "Low",
    color: getColor(colors => colors.risk.low),
    hoverColor: getColor(colors => colors.risk.hover.low),
  },
];

const dateRange = 14;
const valueRange = 100;
const buildChartData: (n?: number) => BarDatum[] = function (n = dateRange) {
  return flatten(
    range(n).map(i => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const datum: any = {
        date: new Date(
          convertToDate("2022-01-01").getTime() + i * 24 * 60 * 60 * 1000
        ),
      };

      chartDescription.map(({ key }) => {
        datum[key] = random(0, valueRange);
      });

      return datum;
    })
  );
};
const chartData: BarDatum[] = buildChartData();

export const Playground = Template.bind({});
Playground.args = {
  data: chartData,
  dataDescription: chartDescription,
  indexBy: "date",
};

export const EmptyState = Template.bind({});
EmptyState.args = {
  data: [],
  dataDescription: chartDescription,
  indexBy: "date",
  chartProps: { borderWidth: 4, padding: 0 },
};

export const WithTitlesAndAxisLabels = Template.bind({});
WithTitlesAndAxisLabels.args = {
  data: chartData,
  dataDescription: chartDescription,
  indexBy: "date",
  chartTitle: "Location risk over time",
  legendTitle: "Risk level",
  bottomAxisLabel: "Time frame",
  leftAxisLabel: "# of Locations",
  legendLabel: datum => `${datum.id} risk`,
};

export const WithCustomTooltip = Template.bind({});
WithCustomTooltip.args = {
  data: chartData,
  dataDescription: chartDescription,
  indexBy: "date",
  tooltipLabel: datum => {
    const riskLabel = lowerCase(datum.id.toString());
    return `${datum.value} ${riskLabel} risk ${
      datum.value === 1 ? "location" : "locations"
    }`;
  },
};

export const OverwritingChartProps = Template.bind({});
OverwritingChartProps.args = {
  data: chartData,
  dataDescription: chartDescription,
  indexBy: "date",
  chartProps: { borderWidth: 4, padding: 0 },
};

const simpleChartDescription: StackedBarChartDataDescription[] = [
  {
    key: "percent",
    color: getColor(colors => colors.brand.urbint["40"]),
    hoverColor: getColor(colors => colors.brand.urbint["50"]),
    selectedColor: getColor(colors => colors.brand.urbint["60"]),
  },
];

const controlCount = 12;
const simpleChartData: BarDatum[] = range(controlCount).map(i => ({
  control: `Control ${i} with a long name`,
  percent: Math.round(random(0, 1, true) * 100),
}));

const simpleData = simpleChartData
  .sort(({ percent }, { percent: percentB }) => (percent < percentB ? 1 : -1))
  .slice(0, 10);

export const SimpleBarChart = Template.bind({});
SimpleBarChart.args = {
  data: simpleData,
  dataDescription: simpleChartDescription,
  indexBy: "control",
  chartTitle: "Simple Bar Chart",
  bottomAxisLabel: "Control",
  leftAxisLabel: "% of controls not implemented",
  tooltipLabel: datum =>
    `${datum.data.control} was not implemented ${datum.value}% of the time`,
  leftAxisFormat: (v: number) => `${v}%`,
};

const colorByControlNotPerformedOption = {
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
};

const horizontalChartDescription: StackedBarChartDataDescription[] = [
  {
    key: "count",
    color: datum =>
      colorByControlNotPerformedOption[datum.indexValue].color || "#E4E0FF",
    labelColor: datum =>
      colorByControlNotPerformedOption[datum.indexValue].labelColor ||
      "#041E25",
  },
];

const counts = [250, 19, 99, 100];
const horizontalChartData = getControlNotPerformedOptions().map(
  ({ name }, i) => {
    return {
      reason: name,
      count: counts[i],
    };
  }
);

export const HorizontalChart = Template.bind({});
HorizontalChart.args = {
  layout: "horizontal",
  data: horizontalChartData,
  dataDescription: horizontalChartDescription,
  indexBy: "reason",
  chartTitle: "Reasons for controls not implemented",
  bottomAxisLabel: "# of times reason reported",
  showTooltip: false,
  enableBarLabels: true,
};

export const With90Bars = Template.bind({});
With90Bars.args = {
  data: buildChartData(90),
  dataDescription: chartDescription,
  indexBy: "date",
};

export const With30Bars = Template.bind({});
With30Bars.args = {
  data: buildChartData(30),
  dataDescription: chartDescription,
  indexBy: "date",
};
