import type { DailyReport } from "@/types/report/DailyReport";
import type { WithEmptyStateProps } from "../withEmptyState";
import cx from "classnames";
import TaskHeader from "@/components/layout/taskCard/header/TaskHeader";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import {
  canEditOwnReport,
  canEditReports,
  canViewReports,
} from "@/container/report/dailyInspection/permissions";
import { DailyReportStatus } from "@/types/report/DailyReportStatus";
import { getFormattedDate, getFormattedShortTime } from "@/utils/date/helper";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { getMenuIcon } from "./utils";

const getHeaderCardText = (dailyReport: DailyReport) => {
  const isInProgress = dailyReport.status === DailyReportStatus.IN_PROGRESS;

  let infoText = `${getFormattedDate(
    dailyReport.createdAt as string,
    "long"
  )} at ${getFormattedShortTime(dailyReport.createdAt ?? "")} by ${
    dailyReport.createdBy?.name
  }`;

  let subHeaderText = `Created on ${infoText}`;

  if (!isInProgress) {
    infoText = `${getFormattedDate(
      dailyReport.completedAt as string,
      "long"
    )} at ${getFormattedShortTime(dailyReport.completedAt ?? "")} by ${
      dailyReport.completedBy?.name
    }`;

    subHeaderText = `Completed ${infoText}`;
  }

  return subHeaderText;
};

type DailyReportsSectionsProps = {
  dailyReport: DailyReport;
  onClick: (dailyReport: DailyReport) => void;
};

function DailyReportsSection({
  dailyReport,
  onClick,
}: DailyReportsSectionsProps): JSX.Element {
  const { me } = useAuthStore();
  const isInProgress = dailyReport.status === DailyReportStatus.IN_PROGRESS;
  const isReportComplete = dailyReport.status === DailyReportStatus.COMPLETE;

  const subHeaderText = getHeaderCardText(dailyReport);

  const isEditAllowed =
    canEditReports(me) || canEditOwnReport(me, dailyReport.createdBy.id);

  // users that can't edit, still can view reports, if the reports are completed
  const isViewAllowed = canViewReports(me) && isReportComplete;

  const viewReportFn =
    isEditAllowed || isViewAllowed ? () => onClick(dailyReport) : undefined;

  const taskHeader = (
    <TaskHeader
      icon={isInProgress ? "pie_chart_25" : "circle_check"}
      iconClassName={cx({
        ["text-brand-gray-60"]: isInProgress,
        ["text-brand-urbint-40"]: !isInProgress,
      })}
      headerText="Daily Inspection Report"
      subHeaderText={subHeaderText}
      onClick={viewReportFn}
      // The menu should be hidden if the user can not use it. Following
      // approach is a tradeoff of and does appear opaque
      menuIcon={getMenuIcon(me, dailyReport)}
      onMenuClicked={viewReportFn}
    />
  );

  return (
    <TaskCard
      className={cx({
        ["border-brand-gray-60"]: isInProgress,
        ["border-brand-urbint-40"]: !isInProgress,
      })}
      isOpen
      taskHeader={taskHeader}
    />
  );
}

export type DailyReportsProps = WithEmptyStateProps<DailyReport>;

export default function DailyReports({
  elements,
  onElementClick,
}: DailyReportsProps): JSX.Element {
  return (
    <>
      {elements.map(report => (
        <DailyReportsSection
          key={report.id}
          dailyReport={report}
          onClick={onElementClick}
        />
      ))}
    </>
  );
}
