import type { TaskRiskLevelByDate } from "@/components/charts/dailyRiskHeatmap/types";
import type { RiskHeatmapProps } from "@/container/insights/charts/types";
import { useState, useEffect } from "react";
import { useLazyQuery } from "@apollo/client";

import { orderByLocationName, orderByName } from "@/graphql/utils";

import DailyRiskHeatmap from "@/components/charts/dailyRiskHeatmap/DailyRiskHeatmap";
import ProjectPlanningTaskRiskLevelByDateQuery from "@/graphql/queries/insights/projectPlanningTaskRiskLevelByDate.gql";

import {
  lazyQueryOpts,
  getTaskNameColumn,
  getLocationNameColumn,
  formatRiskHeatmapChartsWithFilters,
  getProjectDescriptionFromFilters,
} from "@/container/insights/charts/utils";
import { generateExportedProjectFilename } from "@/utils/files/shared";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

const getColumns = (taskHeader: string, locationNameHeader: string) => [
  getTaskNameColumn(taskHeader),
  getLocationNameColumn(locationNameHeader),
];

export default function ProjectTaskRiskHeatmap({
  filters,
  filtersDescriptions,
  setHasData,
}: RiskHeatmapProps): JSX.Element | null {
  const { location, task } = useTenantStore(state => state.getAllEntities());

  const title = `${task.label} risk by day`;
  const [taskRiskData, setTaskRiskData] = useState<TaskRiskLevelByDate[]>([]);

  const [getTaskRiskData] = useLazyQuery(
    ProjectPlanningTaskRiskLevelByDateQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ projectPlanning }) =>
        setTaskRiskData(projectPlanning.taskRiskLevelByDate),
    }
  );

  useEffect(() => {
    if (filters)
      getTaskRiskData({
        variables: { filters, taskOrderBy: [orderByLocationName, orderByName] },
      });
  }, [filters, getTaskRiskData]);

  return (
    <DailyRiskHeatmap
      title={title}
      workbookData={formatRiskHeatmapChartsWithFilters({
        title,
        data: taskRiskData,
        filters: filtersDescriptions,
      })}
      workbookFilename={generateExportedProjectFilename({
        title,
        project: getProjectDescriptionFromFilters({
          filters,
          filtersDescriptions,
        }),
      })}
      data={taskRiskData}
      columns={getColumns(task.label, location.attributes.name.label)}
      startDate={filters?.startDate}
      endDate={filters?.endDate}
      setHasData={setHasData}
    />
  );
}
