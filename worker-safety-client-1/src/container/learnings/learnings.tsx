import type { FilterProject } from "@/container/insights/utils";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { LibraryDivision } from "@/types/project/LibraryDivision";
import type { Contractor } from "@/types/project/Contractor";
import type { FiltersPayload } from "@/container/insights/charts/types";
import { useState, useMemo } from "react";
import Insights from "@/components/layout/insights/Insights";
import ProjectFilters from "@/container/insights/projectFilters/ProjectFilters";
import PortfolioFilters from "@/container/insights/portfolioFilters/PortfolioFilters";
import { projectStatusOptions } from "@/types/project/ProjectStatus";
import ProjectRiskBarChart from "@/container/insights/charts/projectRiskBarChart/ProjectRiskBarChart";
import LocationRiskBarChart from "@/container/insights/charts/locationRiskBarChart/LocationRiskBarChart";
import ReasonsNotImplementedBarChart from "@/container/insights/charts/reasonsNotImplementedBarChart/ReasonsNotImplementedBarChart";
import InsightsControlsNotImplementedChart from "@/container/insights/charts/controlsNotImplementedChart/InsightsControlsNotImplementedChart";
import InsightsApplicableHazardsChart from "@/container/insights/charts/applicableHazardsChart/InsightsApplicableHazardsChart";
import { InsightsMode, InsightsTab } from "@/container/insights/charts/types";
import { useFiltersDescriptions } from "@/container/insights/charts/hooks/useFiltersDescriptions";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

type LearningsPageProps = {
  projects: FilterProject[];
  regions: LibraryRegion[];
  divisions: LibraryDivision[];
  contractors: Contractor[];
};

export default function LearningsPage({
  projects,
  regions,
  divisions,
  contractors,
}: LearningsPageProps): JSX.Element {
  const { workPackage, location } = useTenantStore(state =>
    state.getAllEntities()
  );
  const [selectedTab, setSelectedTab] = useState(0);
  const [filters, setFilters] = useState<FiltersPayload>();

  const tab = useMemo(
    () => (selectedTab === 0 ? InsightsTab.PORTFOLIO : InsightsTab.PROJECT),
    [selectedTab]
  );

  const filtersDescriptions = useFiltersDescriptions({
    filters,
    tab,
    descriptions: {
      projectStatusOptions: projectStatusOptions(),
      projects,
      regions,
      divisions,
      contractors,
    },
  });

  const [hasRiskBarData, setHasRiskBarData] = useState(false);
  const [hasControlsData, setHasControlsData] = useState(false);
  const [hasHazardsData, setHasHazardsData] = useState(false);
  const [hasReasonsData, setHasReasonsData] = useState(false);

  const projectFilters = (
    <ProjectFilters
      timeFrameMode="past"
      projects={projects}
      onChange={setFilters}
    />
  );

  const portfolioFilters = (
    <PortfolioFilters
      timeFrameMode="past"
      projects={projects}
      projectStatuses={projectStatusOptions()}
      regions={regions}
      divisions={divisions}
      contractors={contractors}
      onChange={setFilters}
    />
  );

  const filterComp =
    tab === InsightsTab.PROJECT ? projectFilters : portfolioFilters;

  const charts = useMemo(
    () =>
      [
        tab === InsightsTab.PROJECT ? (
          <LocationRiskBarChart
            key={"LocationRiskBarChart"}
            mode={InsightsMode.PLANNING}
            filters={filters}
            filtersDescriptions={filtersDescriptions}
            setHasData={setHasRiskBarData}
          />
        ) : (
          <ProjectRiskBarChart
            key={"ProjectRiskBarChart"}
            mode={InsightsMode.LEARNINGS}
            filters={filters}
            filtersDescriptions={filtersDescriptions}
            setHasData={setHasRiskBarData}
          />
        ),
        <InsightsControlsNotImplementedChart
          key={"ControlsNotImplementedChart"}
          tab={tab}
          filters={filters}
          filtersDescriptions={filtersDescriptions}
          setHasData={setHasControlsData}
        />,
        <InsightsApplicableHazardsChart
          key={"ApplicableHazardsChart"}
          tab={tab}
          filters={filters}
          filtersDescriptions={filtersDescriptions}
          setHasData={setHasHazardsData}
        />,
        <ReasonsNotImplementedBarChart
          key={"ProjectRiskBarChart"}
          tab={tab}
          filters={filters}
          filtersDescriptions={filtersDescriptions}
          setHasData={setHasReasonsData}
        />,
      ].filter(comp => !!comp),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [tab, filters]
  );

  const hasData =
    hasRiskBarData || hasControlsData || hasHazardsData || hasReasonsData;

  return (
    <Insights
      filters={filterComp}
      emptyChartsTitle="There are currently no learnings based on the filters you’ve set"
      emptyChartsDescription={`Try changing your filters to include ${
        tab === InsightsTab.PROJECT
          ? location.labelPlural.toLowerCase()
          : workPackage.labelPlural.toLowerCase()
      } that have data associated with it`}
      charts={charts}
      onTabChange={setSelectedTab}
      hasData={hasData}
    />
  );
}
