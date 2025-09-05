import type { FiltersDescriptionsReturn } from "./useFiltersDescriptions";
import {
  generateExportedProjectFilename,
  generateExportedPortfolioFilename,
} from "@/utils/files/shared";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { InsightsTab } from "../types";

export type UseGenerateFilenameChartOptions = {
  filters?: FiltersDescriptionsReturn;
};

/**
 * Generates the file name for the chart by tab and chart name
 */
export const useGenerateFilenameChart = (
  tab: InsightsTab,
  title: string,
  options?: UseGenerateFilenameChartOptions
): string => {
  const {
    getAllEntities,
    tenant: { name: tenantName },
  } = useTenantStore(state => state);

  if (tab === InsightsTab.PORTFOLIO) {
    return generateExportedPortfolioFilename({
      tenant: tenantName,
      title,
    });
  }

  const { filters = [] } = options || {};
  const {
    workPackage: {
      attributes: { name, externalKey },
    },
  } = getAllEntities();

  return generateExportedProjectFilename({
    title,
    project: {
      name: (filters?.[0]?.[name.label] || "") as string,
      number: (filters?.[0]?.[externalKey.label] || 0) as string,
    },
  });
};
