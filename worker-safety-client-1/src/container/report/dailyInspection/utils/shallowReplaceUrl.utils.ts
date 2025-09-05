import type { DailyReport } from "@/types/report/DailyReport";

function shallowReplaceUrlWithPath(
  savedDailyReport: DailyReport,
  replacePath = "/reports"
): void {
  if (typeof savedDailyReport?.id !== "string") {
    throw new Error(
      "Missing savedDailyReport.id when attempting to shallow change the url."
    );
  }

  const dailyReportEditUrl = window.history.state.as.replace(
    replacePath,
    `${replacePath}/${savedDailyReport.id}`
  );

  window.history.replaceState(
    {
      ...window.history.state,
      url: dailyReportEditUrl,
      as: dailyReportEditUrl,
    },
    "",
    dailyReportEditUrl
  );
}

export { shallowReplaceUrlWithPath };
