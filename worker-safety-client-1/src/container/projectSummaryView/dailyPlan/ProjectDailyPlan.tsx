import type { Location } from "@/types/project/Location";
import type { Project } from "@/types/project/Project";
import type { RouterLink } from "@/types/Generic";
import type { CriticalActivityType } from "../../report/dailyInspection/types";
import { useRouter } from "next/router";
import Calendar from "@/components/calendar/Calendar";
import { ProjectViewTab } from "@/types/project/ProjectViewTabs";
import { getUpdatedRouterQuery } from "@/utils/router";
import { LocationDetails } from "../locationDetails/LocationDetails";

type ProjectDailyPlanProps = {
  project: Project;
  location: Location;
  onDateSelect: (date: string) => void;
  currentDate: string;
  onAddTask: () => void;
  onAddSiteCondition: () => void;
  onAddDailyReport: () => void;
  onAddActivity: () => void;
  isCritical?: boolean;
  dateRangeNavigator: (initialDate: string, finalDate: string) => void;
  criticalActivityData?: CriticalActivityType[];
};

export default function ProjectDailyPlan({
  project,
  location,
  onDateSelect,
  currentDate,
  onAddTask,
  onAddSiteCondition,
  onAddDailyReport,
  onAddActivity,
  isCritical = false,
  dateRangeNavigator,
  criticalActivityData,
}: ProjectDailyPlanProps): JSX.Element {
  const router = useRouter();
  const { id, startDate, endDate, riskLevel } = project;
  const buildRoute = (
    type: "tasks" | "siteConditions" | "reports",
    param: { key: string; value: string }
  ): RouterLink => {
    return {
      pathname: `/projects/[id]/locations/[locationId]/${type}/[${param.key}]`,
      query: getUpdatedRouterQuery(
        {
          id,
          locationId: location.id,
          [param.key]: param.value,
          activeTab: ProjectViewTab.DAILY_PLAN,
          startDate: currentDate,
          pathOrigin: "workPackage",
        },
        { key: "source", value: router.query.source }
      ),
    };
  };

  return (
    <>
      <Calendar
        startDate={startDate}
        endDate={endDate}
        onDateSelect={onDateSelect}
        defaultDate={currentDate}
        isCritical={isCritical}
        dateRangeNavigator={dateRangeNavigator}
        criticalActivityData={criticalActivityData}
        riskLevel={riskLevel}
      />

      <LocationDetails
        projectStartDate={startDate}
        projectEndDate={endDate}
        location={location}
        onTaskClick={task =>
          router.push(
            buildRoute("tasks", {
              key: "taskId",
              value: task.id,
            })
          )
        }
        onAddTask={onAddTask}
        onSiteConditionClick={siteCondition =>
          router.push(
            buildRoute("siteConditions", {
              key: "siteConditionId",
              value: siteCondition.id,
            })
          )
        }
        onAddSiteCondition={onAddSiteCondition}
        onAddDailyReport={onAddDailyReport}
        onDailyReportClick={dailyReport =>
          router.push(
            buildRoute("reports", {
              key: "dailyReportId",
              value: dailyReport.id,
            })
          )
        }
        onAddActivity={onAddActivity}
        projectId={id}
        startDate={currentDate}
      />
    </>
  );
}
