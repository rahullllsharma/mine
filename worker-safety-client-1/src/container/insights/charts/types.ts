import type { ProjectFiltersPayload } from "@/container/insights/projectFilters/ProjectFilters";
import type { PortfolioFiltersPayload } from "@/container/insights/portfolioFilters/PortfolioFilters";
import type { FiltersDescriptionsReturn } from "./hooks/useFiltersDescriptions";

export enum InsightsTab {
  PORTFOLIO = "PORTFOLIO",
  PROJECT = "PROJECT",
}

export enum InsightsMode {
  PLANNING = "PLANNING",
  LEARNINGS = "LEARNINGS",
}

export type FiltersPayload = ProjectFiltersPayload | PortfolioFiltersPayload;

export type RiskHeatmapProps = {
  filters?: FiltersPayload;
  filtersDescriptions?: FiltersDescriptionsReturn;
  setHasData?: (hasData: boolean) => void;
};

export type PolymorphicRiskHeatmapProps = RiskHeatmapProps & {
  tab: InsightsTab;
};
