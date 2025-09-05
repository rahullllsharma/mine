import type { TaskRiskLevelByDate } from "@/components/charts/dailyRiskHeatmap/types";
import type { RiskHeatmapProps } from "@/container/insights/charts/types";
import { useState, useEffect } from "react";
import { useLazyQuery } from "@apollo/client";

import DailyRiskHeatmap from "@/components/charts/dailyRiskHeatmap/DailyRiskHeatmap";
import { orderByName, orderByProjectName } from "@/graphql/utils";
import PortfolioPlanningTaskRiskLevelByDateQuery from "@/graphql/queries/insights/portfolioPlanningTaskRiskLevelByDate.gql";
import {
  lazyQueryOpts,
  getTaskNameColumn,
  getProjectNameColumn,
  formatRiskHeatmapChartsWithFilters,
  getProjectDescriptionFromFilters,
} from "@/container/insights/charts/utils";
import { generateExportedProjectFilename } from "@/utils/files/shared";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

const getColumns = (taskHeader: string, projectNameHeader: string) => [
  getTaskNameColumn(taskHeader),
  getProjectNameColumn(projectNameHeader),
];

export default function PortfolioTaskRiskHeatmap({
  filters,
  filtersDescriptions,
  setHasData,
}: RiskHeatmapProps): JSX.Element | null {
  const { workPackage, task } = useTenantStore(state => state.getAllEntities());

  const title = `${task.label} risk by day`;
  const [taskRiskData, setTaskRiskData] = useState<TaskRiskLevelByDate[]>([]);

  const [getTaskRiskData] = useLazyQuery(
    PortfolioPlanningTaskRiskLevelByDateQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ portfolioPlanning }) =>
        setTaskRiskData(portfolioPlanning.taskRiskLevelByDate),
    }
  );

  useEffect(() => {
    if (filters)
      getTaskRiskData({
        variables: { filters, taskOrderBy: [orderByProjectName, orderByName] },
      });
  }, [filters, getTaskRiskData]);

  return (
    <DailyRiskHeatmap
      title={title}
      workbookFilename={generateExportedProjectFilename({
        title,
        project: getProjectDescriptionFromFilters({
          filters,
          filtersDescriptions,
        }),
      })}
      workbookData={formatRiskHeatmapChartsWithFilters({
        title,
        data: taskRiskData,
        filters: filtersDescriptions,
      })}
      data={taskRiskData}
      columns={getColumns(task.label, workPackage.attributes.name.label)}
      startDate={filters?.startDate}
      endDate={filters?.endDate}
      setHasData={setHasData}
    />
  );
}
