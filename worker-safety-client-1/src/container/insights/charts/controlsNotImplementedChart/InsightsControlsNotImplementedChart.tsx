import type { BarDatum, ComputedDatum } from "@nivo/bar";
import type { ControlData } from "@/container/insights/charts/controlsNotImplementedChart/ControlsNotImplementedChart";
import type { ControlsDrillDownData } from "@/container/insights/charts/controlsNotImplementedChart/mapControlsDrillDownData";
import type { FiltersPayload } from "@/container/insights/charts/types";
import type { FiltersDescriptionsReturn } from "../hooks/useFiltersDescriptions";
import { useState, useEffect, useMemo, useCallback } from "react";
import { useLazyQuery } from "@apollo/client";

import PortfolioLearningsControlsNotImplementedQuery from "@/graphql/queries/insights/portfolioLearningsControlsNotImplemented.gql";
import ProjectLearningsControlsNotImplementedQuery from "@/graphql/queries/insights/projectLearningsControlsNotImplemented.gql";
import ProjectLearningsControlsDrillDownQuery from "@/graphql/queries/insights/projectLearningsControlsDrillDown.gql";
import PortfolioLearningsControlsDrillDownQuery from "@/graphql/queries/insights/portfolioLearningsControlsDrillDown.gql";
import ControlsNotImplementedChart from "@/container/insights/charts/controlsNotImplementedChart/ControlsNotImplementedChart";
import { mapControlsDrillDownData } from "@/container/insights/charts/controlsNotImplementedChart/mapControlsDrillDownData";

import { InsightsTab } from "@/container/insights/charts/types";
import { lazyQueryOpts } from "@/container/insights/charts/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export type InsightsControlsNotImplementedChartProps = {
  tab: InsightsTab;
  filters?: FiltersPayload;
  filtersDescriptions?: FiltersDescriptionsReturn;
  setHasData?: (hasData: boolean) => void;
};

export default function InsightsControlsNotImplementedChart({
  tab,
  filters,
  filtersDescriptions,
  setHasData,
}: InsightsControlsNotImplementedChartProps): JSX.Element | null {
  const { workPackage, location, task, hazard } = useTenantStore(state =>
    state.getAllEntities()
  );

  const [selectedControl, setSelectedControl] =
    useState<ComputedDatum<BarDatum>>();
  const [controlsData, setControlsData] = useState<ControlData[]>([]);

  useEffect(
    () => setHasData && setHasData(controlsData.length > 0),
    [controlsData, setHasData]
  );

  const [controlsDrillDownData, setControlsDrillDownData] =
    useState<ControlsDrillDownData>({});

  const [getControlsData] = useLazyQuery(
    tab === InsightsTab.PORTFOLIO
      ? PortfolioLearningsControlsNotImplementedQuery
      : ProjectLearningsControlsNotImplementedQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ portfolioLearnings, projectLearnings }) =>
        setControlsData(
          projectLearnings?.notImplementedControls ||
            portfolioLearnings?.notImplementedControls
        ),
    }
  );

  const [getControlsDrillDownData] = useLazyQuery(
    tab === InsightsTab.PORTFOLIO
      ? PortfolioLearningsControlsDrillDownQuery
      : ProjectLearningsControlsDrillDownQuery,
    {
      ...lazyQueryOpts,
      onCompleted: ({ projectLearnings, portfolioLearnings }) => {
        if (projectLearnings)
          setControlsDrillDownData(mapControlsDrillDownData(projectLearnings));
        else if (portfolioLearnings)
          setControlsDrillDownData(
            mapControlsDrillDownData(portfolioLearnings)
          );
      },
    }
  );

  const controlSelectedHandler = useCallback(
    (datum: ComputedDatum<BarDatum>) => {
      if (datum.indexValue === selectedControl?.indexValue) {
        setSelectedControl(undefined);
        setControlsDrillDownData({});
      } else {
        setSelectedControl(datum);

        const selectedControlData = controlsData.find(
          ({ libraryControl }) => libraryControl.name === datum.data.control
        );

        if (selectedControlData) {
          getControlsDrillDownData({
            variables: {
              filters,
              libraryControlId: selectedControlData.libraryControl.id,
            },
          });
        }
      }
    },
    [
      selectedControl,
      getControlsDrillDownData,
      setSelectedControl,
      filters,
      controlsData,
    ]
  );

  useEffect(() => {
    // reset selection + data when the tab or filters are updated
    setSelectedControl(undefined);
    setControlsData([]);
    setControlsDrillDownData({});

    if (filters) getControlsData({ variables: { filters } });
  }, [tab, filters, getControlsData]);

  const charts = useMemo(() => {
    return [
      tab === InsightsTab.PORTFOLIO
        ? {
            title: `By ${workPackage.label}`,
            data: controlsDrillDownData.byProject,
            label: workPackage.attributes.name.label,
          }
        : {
            title: `By ${location.label}`,
            data: controlsDrillDownData.byLocation,
            label: location.attributes.name.label,
          },
      {
        title: `By ${hazard.label}`,
        data: controlsDrillDownData.byHazard,
        label: hazard.label,
      },
      {
        title: `By ${task.label}`,
        data: controlsDrillDownData.byTask,
        label: task.label,
      },
      {
        title: `By ${task.label} Type`,
        data: controlsDrillDownData.byTaskType,
        label: `${task.label} Type`,
      },
    ];
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, controlsDrillDownData]);

  return (
    <ControlsNotImplementedChart
      tab={tab}
      controlsData={controlsData}
      onClick={controlSelectedHandler}
      selected={selectedControl}
      charts={charts}
      filtersDescriptions={filtersDescriptions}
    />
  );
}
