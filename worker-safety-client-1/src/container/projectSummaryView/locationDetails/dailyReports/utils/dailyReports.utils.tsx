import type { AuthUser } from "@/types/auth/AuthUser";
import type { DailyReport } from "@/types/report/DailyReport";
import {
  canEditReports,
  canEditOwnReport,
  canViewReports,
} from "@/container/report/dailyInspection/permissions";
import { DailyReportStatus } from "@/types/report/DailyReportStatus";

const getMenuIcon = (user: AuthUser, dailyReport: DailyReport) => {
  const { createdBy, status } = dailyReport;
  if (canEditReports(user) || canEditOwnReport(user, createdBy.id)) {
    return "edit";
  } else if (canViewReports(user) && status === DailyReportStatus.COMPLETE) {
    return "show";
  }
  return undefined;
};

export { getMenuIcon };
