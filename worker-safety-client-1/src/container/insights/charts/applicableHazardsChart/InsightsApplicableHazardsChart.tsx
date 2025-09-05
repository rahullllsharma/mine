import type { BarDatum, ComputedDatum } from "@nivo/bar";
import type { HazardData } from "@/container/insights/charts/applicableHazardsChart/ApplicableHazardsChart";
import type { HazardsDrillDownData } from "@/container/insights/charts/applicableHazardsChart/mapHazardsDrillDownData";
import type { FiltersPayload } from "@/container/insights/charts/types";
import type { FiltersDescriptionsReturn } from "../hooks/useFiltersDescriptions";
import { useState, useEffect, useMemo, useCallback } from "react";
import { useLazyQuery } from "@apollo/client";

import PortfolioLearningsApplicableHazardsQuery from "@/graphql/queries/insights/portfolioLearningsApplicableHazards.gql";
import ProjectLearningsApplicableHazardsQuery from "@/graphql/queries/insights/projectLearningsApplicableHazards.gql";
import ProjectLearningsHazardsDrillDownQuery from "@/graphql/queries/insights/projectLearningsHazardsDrillDown.gql";
import PortfolioLearningsHazardsDrillDownQuery from "@/graphql/queries/insights/portfolioLearningsHazardsDrillDown.gql";

import ApplicableHazardsChart from "@/container/insights/charts/applicableHazardsChart/ApplicableHazardsChart";
import { mapHazardsDrillDownData } from "@/container/insights/charts/applicableHazardsChart/mapHazardsDrillDownData";

import { InsightsTab } from "@/container/insights/charts/types";
import { lazyQueryOpts } from "@/container/insights/charts/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export type InsightsApplicableHazardsChartProps = {
  tab: InsightsTab;
  filters?: FiltersPayload;
  filtersDescriptions?: FiltersDescriptionsReturn;
  setHasData?: (hasData: boolean) => void;
};

export default function InsightsApplicableHazardsChart({
  tab,
  filters,
  filtersDescriptions,
  setHasData,
}: InsightsApplicableHazardsChartProps): JSX.Element | null {
  const { workPackage, location, task, siteCondition } = useTenantStore(state =>
    state.getAllEntities()
  );

  const [selectedHazard, setSelectedHazard] =
    useState<ComputedDatum<BarDatum>>();
  const [hazardsData, setHazardsData] = useState<HazardData[]>([]);
  const [hazardsDrillDownData, setHazardsDrillDownData] =
    useState<HazardsDrillDownData>({});

  useEffect(
    () => setHasData && setHasData(hazardsData.length > 0),
    [hazardsData, setHasData]
  );

  const [getHazardsData] = useLazyQuery(
    tab === InsightsTab.PORTFOLIO
      ? PortfolioLearningsApplicableHazardsQuery
      : ProjectLearningsApplicableHazardsQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ portfolioLearnings, projectLearnings }) =>
        setHazardsData(
          projectLearnings?.applicableHazards ||
            portfolioLearnings?.applicableHazards
        ),
    }
  );

  const [getHazardsDrillDownData] = useLazyQuery(
    tab === InsightsTab.PORTFOLIO
      ? PortfolioLearningsHazardsDrillDownQuery
      : ProjectLearningsHazardsDrillDownQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ portfolioLearnings, projectLearnings }) => {
        if (projectLearnings)
          setHazardsDrillDownData(mapHazardsDrillDownData(projectLearnings));
        else if (portfolioLearnings)
          setHazardsDrillDownData(mapHazardsDrillDownData(portfolioLearnings));
      },
    }
  );

  const hazardSelectedHandler = useCallback(
    (datum: ComputedDatum<BarDatum>) => {
      if (datum.indexValue === selectedHazard?.indexValue) {
        setSelectedHazard(undefined);
        setHazardsDrillDownData({});
      } else {
        setSelectedHazard(datum);

        const selectedHazardData = hazardsData.find(
          ({ libraryHazard }) => libraryHazard.name === datum.data.hazard
        );

        if (selectedHazardData) {
          getHazardsDrillDownData({
            variables: {
              filters,
              libraryHazardId: selectedHazardData.libraryHazard.id,
            },
          });
        }
      }
    },
    [
      selectedHazard,
      getHazardsDrillDownData,
      setSelectedHazard,
      filters,
      hazardsData,
    ]
  );

  useEffect(() => {
    // reset selection when the tab or filters are updated
    setSelectedHazard(undefined);
    setHazardsData([]);
    setHazardsDrillDownData({});

    if (filters) getHazardsData({ variables: { filters } });
  }, [tab, filters, getHazardsData]);

  const charts = useMemo(() => {
    return [
      tab === InsightsTab.PORTFOLIO
        ? {
            title: `By ${workPackage.label}`,
            data: hazardsDrillDownData.byProject,
            label: workPackage.attributes.name.label,
          }
        : {
            title: `By ${location.label}`,
            data: hazardsDrillDownData.byLocation,
            label: location.attributes.name.label,
          },
      {
        title: `By ${siteCondition.label}`,
        data: hazardsDrillDownData.bySiteCondition,
        label: siteCondition.label,
      },
      {
        title: `By ${task.label}`,
        data: hazardsDrillDownData.byTask,
        label: task.label,
      },
      {
        title: `By ${task.label} Type`,
        data: hazardsDrillDownData.byTaskType,
        label: `${task.label} Type`,
      },
    ];
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, hazardsDrillDownData]);

  return (
    <ApplicableHazardsChart
      tab={tab}
      hazardsData={hazardsData}
      onClick={hazardSelectedHandler}
      selected={selectedHazard}
      charts={charts}
      filtersDescriptions={filtersDescriptions}
    />
  );
}
