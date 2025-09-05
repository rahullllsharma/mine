import type { LocationRiskLevelByDate } from "@/components/charts/dailyRiskHeatmap/types";
import type { RiskHeatmapProps } from "@/container/insights/charts/types";
import { useState, useEffect } from "react";
import { useLazyQuery } from "@apollo/client";

import ProjectPlanningLocationRiskLevelByDateQuery from "@/graphql/queries/insights/projectPlanningLocationRiskLevelByDate.gql";
import DailyRiskHeatmap from "@/components/charts/dailyRiskHeatmap/DailyRiskHeatmap";

import {
  formatRiskHeatmapChartsWithFilters,
  lazyQueryOpts,
  getProjectDescriptionFromFilters,
} from "@/container/insights/charts/utils";
import { generateExportedProjectFilename } from "@/utils/files/shared";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

const getLocationNameColumn = (header: string) => ({
  id: "location_name",
  Header: header,
  width: 220,
  value: (locationRisk: LocationRiskLevelByDate) => {
    return locationRisk.locationName;
  },
});

export default function LocationRiskHeatmap({
  filters,
  filtersDescriptions,
  setHasData,
}: RiskHeatmapProps): JSX.Element | null {
  const {
    location: {
      label: locationLabel,
      attributes: { name: locationAttrName },
    },
  } = useTenantStore(state => state.getAllEntities());
  const title = `${locationLabel} risk by day`;

  const [locationHeatmapData, setLocationHeatmapData] = useState<
    LocationRiskLevelByDate[]
  >([]);

  const [getLocationRiskData] = useLazyQuery(
    ProjectPlanningLocationRiskLevelByDateQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ projectPlanning }) =>
        setLocationHeatmapData(projectPlanning.locationRiskLevelByDate),
    }
  );

  useEffect(() => {
    if (filters) getLocationRiskData({ variables: { filters } });
  }, [filters, getLocationRiskData]);

  return (
    <DailyRiskHeatmap
      title={title}
      workbookData={formatRiskHeatmapChartsWithFilters({
        title,
        data: locationHeatmapData,
        filters: filtersDescriptions,
      })}
      workbookFilename={generateExportedProjectFilename({
        title,
        project: getProjectDescriptionFromFilters({
          filters,
          filtersDescriptions,
        }),
      })}
      data={locationHeatmapData}
      columns={[getLocationNameColumn(locationAttrName.label)]}
      startDate={filters?.startDate}
      endDate={filters?.endDate}
      showLegend
      setHasData={setHasData}
    />
  );
}
