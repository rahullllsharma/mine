import type { RiskLevelByDate } from "@/components/charts/dailyRiskHeatmap/types";
import { act } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";

export function chartRenderHelper(): () => void {
  // set up a listener so we can force the width/height
  // this is required to get the chart to render in its ResponsiveWrapper
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let listener: ((rect: any) => void) | undefined;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (window as any).ResizeObserver = class ResizeObserver {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    constructor(ls: any) {
      listener = ls;
    }
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    observe() {}
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    disconnect() {}
  };

  function triggerResize(): void {
    act(() => {
      listener &&
        listener([
          {
            contentRect: {
              x: 0,
              y: 0,
              width: 800,
              height: 800,
              top: 100,
              bottom: 0,
              left: 100,
              right: 0,
            },
          },
        ]);
    });
  }
  return triggerResize;
}

export const sampleHeatmapDates = {
  startDate: "2022-01-29",
  endDate: "2022-02-03",
};

// consumed by the DailyRiskHeatmap
export const sampleRiskLevelByDate: RiskLevelByDate[] = [
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
