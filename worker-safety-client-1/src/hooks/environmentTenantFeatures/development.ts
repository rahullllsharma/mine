import type { FeaturesMap, TenantsList, Features } from "../useTenantFeatures";

// Only contains overrides from the default behavior
export const development: FeaturesMap = new Map<TenantsList, Features>([
  [
    "asgard",
    {
      // Local Dev
      displayJSB: true,
      displayFormsList: true,
      displayAddEbo: true,
      displayAddJsb: true,
      displayAddCriticalActivity: true,
      displayProjectTaskRiskHeatmap: true,
      displayTemplatesList: true,
      displayTemplateFormsList: true,
    },
  ],
]);
