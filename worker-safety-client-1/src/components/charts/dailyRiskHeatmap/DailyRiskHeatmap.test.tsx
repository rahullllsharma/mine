import type {
  RiskLevelByDate,
  ProjectRiskLevelByDate,
} from "@/components/charts/dailyRiskHeatmap/types";
import { render, screen, fireEvent } from "@testing-library/react";
import { range } from "lodash";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { sampleRiskLevelByDate, sampleHeatmapDates } from "@/utils/dev/jest";

import DailyRiskHeatmap from "@/components/charts/dailyRiskHeatmap/DailyRiskHeatmap";
import { withDateToRiskLevel } from "@/components/charts/dailyRiskHeatmap/heatmapColumn";
import { getFormattedDate } from "@/utils/date/helper";

function sampleData(
  num: number,
  riskLevelData: RiskLevelByDate[] = sampleRiskLevelByDate
): ProjectRiskLevelByDate[] {
  return range(num).map(i => ({
    projectName: `Project ${i}`,
    riskLevelByDate: riskLevelData,
  }));
}

const col1 = {
  id: "name",
  Header: "column 1",
  value: (entityRisk: ProjectRiskLevelByDate) => entityRisk.projectName,
};
const col2 = {
  id: "another_col",
  Header: "column 2",
  value: (entityRisk: ProjectRiskLevelByDate) =>
    `long column value ${entityRisk.projectName} with a long long name`,
};
const columns = [col1, col2];

const defaultProps = {
  columns,
  title: "Some title",
  workbookFilename: "sample",
  ...sampleHeatmapDates,
};

describe(DailyRiskHeatmap.name, () => {
  const data = sampleData(10);

  it("renders a title and two columns", async () => {
    render(<DailyRiskHeatmap {...defaultProps} data={data} />);
    await screen.findByText(col1.Header);
    await screen.findByText(col2.Header);
  });

  it("renders one column", async () => {
    render(<DailyRiskHeatmap data={data} {...defaultProps} columns={[col1]} />);
    await screen.findByText(col1.Header);
  });

  it("renders another column", async () => {
    render(<DailyRiskHeatmap data={data} {...defaultProps} columns={[col2]} />);
    await screen.findByText(col2.Header);
  });

  it("renders a legend", async () => {
    render(<DailyRiskHeatmap data={data} {...defaultProps} showLegend />);
    await screen.findByText(/Risk level/);
    await screen.findByText(/Low risk/);
    await screen.findByText(/Medium risk/);
    await screen.findByText(/High risk/);
  });

  it("renders data", async () => {
    render(<DailyRiskHeatmap data={data} {...defaultProps} />);
    await screen.findByText("Project 0");
    await screen.findByText("Project 7");
  });

  it("renders day-numbers between dates", async () => {
    render(<DailyRiskHeatmap data={data} {...defaultProps} />);
    await screen.findByText("29");
    await screen.findByText("30");
    await screen.findByText("31");
    await screen.findByText("1");
    await screen.findByText("2");
  });

  describe("with many records", () => {
    const chartData = sampleData(100);
    beforeEach(() => {
      render(<DailyRiskHeatmap data={chartData} {...defaultProps} />);
    });

    it("renders many project names", async () => {
      await screen.findByText("Project 0");
      await screen.findByText("Project 7");
    });

    it("does not render every row", async () => {
      expect(screen.queryByText("Project 77")).not.toBeInTheDocument();
      expect(screen.queryByText("Project 99")).not.toBeInTheDocument();
    });
  });

  describe("renders tooltips on hover", () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let container: any;
    const chartData = sampleData(10);
    beforeEach(() => {
      const res = render(
        <DailyRiskHeatmap data={chartData} {...defaultProps} showLegend />
      );
      container = res.container;
    });

    it("renders a tooltip (high)", async () => {
      const ariaLabel = `High risk on ${getFormattedDate(
        "2022-01-29",
        "long"
      )}`;
      const cell = container.querySelector(`div[aria-label="${ariaLabel}"]`);
      fireEvent.mouseOver(cell);

      // should be 2 including the legend
      const highFound = await screen.findAllByText(/High risk/);
      expect(highFound.length).toBe(2);

      // sanity check
      const lowFound = await screen.findAllByText(/Low risk/);
      expect(lowFound.length).toBe(1);
    });

    it("renders a tooltip (low)", async () => {
      const ariaLabel = `Low risk on ${getFormattedDate("2022-02-01", "long")}`;
      const cell = container.querySelector(`div[aria-label="${ariaLabel}"]`);
      fireEvent.mouseOver(cell);

      // sanity check
      const highFound = await screen.findAllByText(/High risk/);
      expect(highFound.length).toBe(1);

      // should be 2 including the legend
      const lowFound = await screen.findAllByText(/Low risk/);
      expect(lowFound.length).toBe(2);
    });
  });
});

describe("withDateToRiskLevel", () => {
  it("extends riskLevelByDate", () => {
    const riskLevelData: RiskLevelByDate[] = [
      {
        date: "2022-01-29",
        riskLevel: RiskLevel.HIGH,
      },
      {
        date: "2022-01-30",
        riskLevel: RiskLevel.MEDIUM,
      },
      {
        date: "2022-01-31",
        riskLevel: RiskLevel.UNKNOWN,
      },
      {
        date: "2022-02-01",
        riskLevel: RiskLevel.LOW,
      },
      {
        date: "2022-02-02",
        riskLevel: RiskLevel.RECALCULATING,
      },
      {
        date: "2022-02-03",
        riskLevel: RiskLevel.UNKNOWN,
      },
    ];

    const data = sampleData(10, riskLevelData);
    const result = withDateToRiskLevel(data);

    expect(result.length).toBe(data.length);

    const sample = result[0];

    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    expect(sample.dateToRiskLevel!["2022-01-30"]).toBe(RiskLevel.MEDIUM);
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    expect(sample.dateToRiskLevel!["2022-02-03"]).toBe(RiskLevel.UNKNOWN);
  });
});
