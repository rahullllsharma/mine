import type { ProjectRiskLevelByDate } from "@/components/charts/dailyRiskHeatmap/types";
import type { PolymorphicRiskHeatmapProps } from "@/container/insights/charts/types";
import { useState, useEffect } from "react";
import { useLazyQuery } from "@apollo/client";

import DailyRiskHeatmap from "@/components/charts/dailyRiskHeatmap/DailyRiskHeatmap";
import PortfolioPlanningProjectRiskLevelByDateQuery from "@/graphql/queries/insights/portfolioPlanningProjectRiskLevelByDate.gql";

import {
  formatRiskHeatmapChartsWithFilters,
  lazyQueryOpts,
} from "@/container/insights/charts/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { useGenerateFilenameChart } from "../hooks/useGenerateFilenameChart";

const getProjectNameColumn = (header: string) => ({
  id: "project_name",
  Header: header,
  width: 220,
  value: (projectRisk: ProjectRiskLevelByDate) => {
    return projectRisk.projectName;
  },
});

export default function ProjectRiskHeatmap({
  tab,
  filters,
  filtersDescriptions,
  setHasData,
}: PolymorphicRiskHeatmapProps): JSX.Element | null {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const title = `${workPackage.label} risk by day`;
  const [projectHeatmapData, setProjectHeatmapData] = useState<
    ProjectRiskLevelByDate[]
  >([]);

  const [getProjectRiskData] = useLazyQuery(
    PortfolioPlanningProjectRiskLevelByDateQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ portfolioPlanning }) =>
        setProjectHeatmapData(portfolioPlanning.projectRiskLevelByDate),
    }
  );

  useEffect(() => {
    getProjectRiskData({ variables: { filters } });
  }, [filters, getProjectRiskData]);

  const workbookFilename = useGenerateFilenameChart(tab, title, {
    filters: filtersDescriptions,
  });

  return (
    <DailyRiskHeatmap
      title={title}
      workbookFilename={workbookFilename}
      workbookData={formatRiskHeatmapChartsWithFilters({
        title,
        data: projectHeatmapData,
        filters: filtersDescriptions,
      })}
      data={projectHeatmapData}
      columns={[getProjectNameColumn(workPackage.attributes.name.label)]}
      startDate={filters?.startDate}
      endDate={filters?.endDate}
      showLegend
      setHasData={setHasData}
    />
  );
}
