import type { BarDatum, LegendLabelDatum } from "@nivo/bar";

import type { StackedBarChartProps } from "./StackedBarChart";
import type { StackedBarChartDataDescription } from "./types";
import { render, screen, fireEvent } from "@testing-library/react";
import { getFormattedDate } from "@/utils/date/helper";
import { chartRenderHelper } from "@/utils/dev/jest";
import StackedBarChart from "./StackedBarChart";
import {
  buildKeysAndColors,
  calcMaxValue,
  shouldRotateXLabels,
  calcXAxisFactor,
} from "./utils";

const basicData = [
  { id: "123", AB: 12, BC: 0, CA: 32 },
  { id: "456", AB: 16, BC: 22, CA: 16 },
];

const basicDataDescription = [
  { key: "AB", color: "#000000" },
  { key: "BC", color: "#ffffff" },
  { key: "CA", color: "#ffffff" },
];

const defaultProps = {
  workbookFilename: "sample",
  data: basicData,
  dataDescription: basicDataDescription,
  indexBy: "key",
};

// a helper that wraps the resize hack to get the chart to render
const renderChart = (props: StackedBarChartProps): HTMLElement => {
  const triggerResize = chartRenderHelper();
  const res = render(<StackedBarChart {...props} />);
  triggerResize();
  return res.container;
};

describe(StackedBarChart.name, () => {
  describe("when passed empty data", () => {
    it("does not crash", () => {
      renderChart(defaultProps);
    });
  });

  describe("renders the chart title", () => {
    it("renders a chart title", async () => {
      const chartTitle = "some chart title";
      renderChart({ ...defaultProps, chartTitle });
      await screen.findByText(chartTitle);
    });
  });

  describe("renders the chart legend", () => {
    it("renders a legend title", async () => {
      const legendTitle = "some legend title";
      renderChart({ ...defaultProps, legendTitle });
      await screen.findByText(legendTitle);
    });

    it("renders the legend keys", async () => {
      const dataDescription = [{ key: "AB" }, { key: "BC" }, { key: "CA" }];
      renderChart({
        ...defaultProps,
        legendTitle: "some legend title",
        dataDescription,
      });
      await screen.findByText("AB");
      await screen.findByText("BC");
      await screen.findByText("CA");
    });

    it("renders the legend keys with a custom label", async () => {
      const dataDescription = [{ key: "AB" }, { key: "BC" }, { key: "CA" }];
      renderChart({
        ...defaultProps,
        dataDescription,
        legendTitle: "some legend title",
        legendLabel: (datum: LegendLabelDatum<BarDatum>) => `${datum.id} label`,
      });
      await screen.findByText("AB label");
      await screen.findByText("BC label");
      await screen.findByText("CA label");
    });

    it("should not render legend when `legendTitle` is not set", async () => {
      const dataDescription = [{ key: "AB" }, { key: "BC" }, { key: "CA" }];
      renderChart({
        ...defaultProps,
        dataDescription,
        //  no legendTitle is set, so no legend should show up
        legendLabel: (datum: LegendLabelDatum<BarDatum>) => `${datum.id} label`,
      });
      expect(screen.queryByText("label")).not.toBeInTheDocument();
    });
  });

  describe("renders the axes labels", () => {
    it("renders the x-axis label", async () => {
      const bottomAxisLabel = "some bottom axis label";
      renderChart({ ...defaultProps, bottomAxisLabel });
      await screen.findByText(bottomAxisLabel);
    });

    it("renders the y-axis label", async () => {
      const leftAxisLabel = "some left axis label";
      renderChart({ ...defaultProps, leftAxisLabel });
      await screen.findByText(leftAxisLabel);
    });
  });
});

describe("renders some data", () => {
  it("renders bars with some aria-labels", async () => {
    const data = [
      { id: "123", val: 12, anotherVal: 32 },
      { id: "456", val: 22, anotherVal: 16 },
    ];
    const dataDescription = [
      { key: "val", color: "#000000" },
      { key: "anotherVal", color: "#ffffff" },
    ];
    const indexBy = "id";
    const container = renderChart({
      workbookFilename: "sample",
      data,
      dataDescription,
      indexBy,
    });

    const labels = [
      "val: 12 for: 123",
      "anotherVal: 32 for: 123",
      "val: 22 for: 456",
      "anotherVal: 16 for: 456",
    ];
    labels.map(label => {
      const bar = container.querySelector(`rect[aria-label="${label}"]`);
      expect(bar).not.toBeNull();
    });
  });
});

describe("renders tooltips", () => {
  it("renders a custom tooltip", async () => {
    const data = [
      { id: "123", val: 12, anotherVal: 32 },
      { id: "456", val: 22, anotherVal: 16 },
    ];
    const dataDescription = [
      { key: "val", color: "#000000" },
      { key: "anotherVal", color: "#ffffff" },
    ];
    const indexBy = "id";
    const container = renderChart({
      data,
      dataDescription,
      indexBy,
      workbookFilename: "sample",
      tooltipLabel: datum => {
        const riskLabel = datum.id.toString();
        return `${datum.value} for ${riskLabel}`;
      },
    });

    const ariaLabel = "val: 12 for: 123";
    const bar = container.querySelector(`rect[aria-label="${ariaLabel}"]`);
    fireEvent.mouseOver(bar as Element);
    await screen.findByText(/12 for val/);
  });
});

describe("renders dates", () => {
  it("renders with dates on the x-axis", async () => {
    const date = new Date();
    const formattedDate = getFormattedDate(date, "numeric", "2-digit");
    const data = [
      { date, val: 12 },
      { date, val: 22 },
    ];
    const dataDescription = [{ key: "val" }];
    const indexBy = "date";
    // the BarDatum claims to not support js `Dates` as a type...
    // but the nivo code does, so here we cast as `any`
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    renderChart({ data, dataDescription, indexBy } as any);
    await screen.findByText(formattedDate);
  });
});

describe("buildKeysAndColors", () => {
  const sampleDataDesc: StackedBarChartDataDescription[] = [
    { key: "AB", color: "#ffffff", hoverColor: "#000000" },
    { key: "BC", color: "#999999", hoverColor: "#888888" },
    { key: "CA", color: "#333333", hoverColor: "#222222" },
  ];
  it("converts a dataDescription to keys and colors", () => {
    const { keys } = buildKeysAndColors(sampleDataDesc);

    expect(keys).toStrictEqual(["AB", "BC", "CA"]);
  });
  it("builds a descByKey map for looking up a hover color", () => {
    const { descByKey } = buildKeysAndColors(sampleDataDesc);

    expect(descByKey["AB"].hoverColor).toStrictEqual("#000000");
    expect(descByKey["BC"].hoverColor).toStrictEqual("#888888");
    expect(descByKey["CA"].hoverColor).toStrictEqual("#222222");
  });

  describe("filling in missing colors", () => {
    const dataDesc: StackedBarChartDataDescription[] = [
      { key: "AB", color: "#ffffff" },
      { key: "BC", color: "#999999", hoverColor: "#888888" },
      { key: "CD", color: "#999999", selectedColor: "#444444" },
      {
        key: "DE",
        color: "#333333",
        hoverColor: "#222222",
        selectedColor: "#444444",
      },
    ];
    const { descByKey } = buildKeysAndColors(dataDesc);
    it("sets missing colors, does not overwrite set colors", () => {
      expect(descByKey["AB"].color).toBe("#ffffff");
      expect(descByKey["AB"].hoverColor).toBe("#ffffff");
      expect(descByKey["AB"].selectedColor).toBe("#ffffff");

      expect(descByKey["BC"].color).toBe("#999999");
      expect(descByKey["BC"].hoverColor).toBe("#888888");
      expect(descByKey["BC"].selectedColor).toBe("#888888");

      expect(descByKey["CD"].color).toBe("#999999");
      expect(descByKey["CD"].hoverColor).toBe("#999999");
      expect(descByKey["CD"].selectedColor).toBe("#444444");

      expect(descByKey["DE"].color).toBe("#333333");
      expect(descByKey["DE"].hoverColor).toBe("#222222");
      expect(descByKey["DE"].selectedColor).toBe("#444444");
    });
  });
});

describe("calcMaxValue", () => {
  describe("determines the expected maxValue", () => {
    it.each([
      {
        keys: ["High", "Medium"],
        data: [
          { id: "a", High: 3, Medium: 2 },
          { id: "b", High: 7, Medium: 2 },
          { id: "b", High: 4, Medium: 3 },
        ],
        expectedMax: 9,
      },
      {
        keys: ["Key1", "Key2", "Key3", "Key5"],
        data: [
          { id: "a", Key1: 3, Key2: 2 },
          { id: "b", Key1: 7, Key2: 2 },
          { id: "c", Key3: 2, Key5: 7 },
          { id: "d", Key1: 5, Key3: 4 },
        ],
        expectedMax: 9,
      },
      {
        keys: ["Key1", "Key2", "Key3", "Key5"],
        data: [
          { id: "a", Key1: 3, Key2: 2 },
          { id: "b", Key1: 7, Key2: 2 },
          { id: "c", Key3: 2, Key5: 7 },
          { id: "d", Key1: 5, Key3: 4 },
          { id: "3", Key1: 15, Key3: 4 },
        ],
        expectedMax: 19,
      },
    ] as {
      keys: string[];
      data: BarDatum[];
      expectedMax: number;
    }[])(
      "only uses keys: $keys to calc the max: $expectedMax",
      ({ keys, data, expectedMax }) =>
        expect(calcMaxValue(data, keys)).toStrictEqual(expectedMax)
    );
  });
});

describe("xAxis rotation and skipping", () => {
  describe("rotates and skips x-axis labels when applicable", () => {
    it.each([
      { barCount: 14, width: 800, shouldRotate: true, factor: 1 },
      { barCount: 14, width: 900, shouldRotate: false, factor: 1 },
      { barCount: 30, width: 900, shouldRotate: true, factor: 1 },
      { barCount: 30, width: 600, shouldRotate: true, factor: 2 },
      { barCount: 30, width: 400, shouldRotate: true, factor: 3 },
      { barCount: 90, width: 1000, shouldRotate: true, factor: 2 },
      { barCount: 90, width: 800, shouldRotate: true, factor: 3 },
      { barCount: 90, width: 600, shouldRotate: true, factor: 4 },
    ])(
      "barCount: $barCount and width: $width should rotate: $shouldRotate with xFactor: $factor",
      ({ barCount, width, shouldRotate, factor }) => {
        const rotate = shouldRotateXLabels({ barCount, width });
        expect(shouldRotate).toBe(rotate);
        const xFactor = calcXAxisFactor({ barCount, width });
        expect(factor).toBe(xFactor);
      }
    );
  });
});
