import type { DailyReport } from "@/types/report/DailyReport";

import { shallowReplaceUrlWithPath } from "./shallowReplaceUrl.utils";

describe(shallowReplaceUrlWithPath.name, () => {
  let cacheHistoryState: History;

  beforeEach(() => {
    cacheHistoryState = window.history;

    Object.defineProperty(window, "history", {
      value: {
        replaceState: jest.fn(),
        pushState: jest.fn(),
        state: {
          as: "pathname/reports",
        },
      },
      writable: true,
    });
  });

  afterEach(() => {
    Object.defineProperties(
      window.history,
      cacheHistoryState as unknown as PropertyDescriptorMap
    );
  });

  it("should append the daily report id to the URL in the browser history", () => {
    shallowReplaceUrlWithPath({ id: "daily-report-id" } as DailyReport);

    expect(global.history.replaceState).toHaveBeenCalledWith(
      {
        url: "pathname/reports/daily-report-id",
        as: "pathname/reports/daily-report-id",
      },
      "",
      "pathname/reports/daily-report-id"
    );
  });

  it("should append the daily report id to the URL with a navigation section in the browser history", () => {
    shallowReplaceUrlWithPath({ id: "daily-report-id#section" } as DailyReport);

    expect(global.history.replaceState).toHaveBeenCalledWith(
      {
        url: "pathname/reports/daily-report-id#section",
        as: "pathname/reports/daily-report-id#section",
      },
      "",
      "pathname/reports/daily-report-id#section"
    );
  });

  it("should append the daily report id for a custom path to the URL in the browser history", () => {
    shallowReplaceUrlWithPath(
      { id: "daily-report-id" } as DailyReport,
      "pathname"
    );

    expect(global.history.replaceState).toHaveBeenCalledWith(
      {
        url: "pathname/daily-report-id/reports",
        as: "pathname/daily-report-id/reports",
      },
      "",
      "pathname/daily-report-id/reports"
    );
  });

  it("throws an error when the daily report is empty", () => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    expect(() => shallowReplaceUrlWithPath()).toThrowError(
      "Missing savedDailyReport.id when attempting to shallow change the url."
    );
  });

  it("throws an error when the daily report does not have an id", () => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    expect(() => shallowReplaceUrlWithPath({})).toThrowError(
      "Missing savedDailyReport.id when attempting to shallow change the url."
    );
  });
});
