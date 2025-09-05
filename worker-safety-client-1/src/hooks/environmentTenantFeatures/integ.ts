import type { FeaturesMap, Features, TenantsList } from "../useTenantFeatures";

// Only contains overrides from the default behavior
export const integ: FeaturesMap = new Map<TenantsList, Features>([
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
  [
    "urbint",
    {
      // Integration and Staging tenants
      displayJSB: true,
      displayFormsList: true,
      displayAddEbo: true,
      displayAddJsb: true,
      displayAddCriticalActivity: true,
      displayProjectTaskRiskHeatmap: false,
      displayTemplatesList: true,
      displayTemplateFormsList: true,
    },
  ],
  [
    "automation-integration",
    {
      // Integration tenant
      displayJSB: true,
      displayFormsList: true,
      displayAddEbo: true,
      displayAddJsb: true,
      displayAddCriticalActivity: true,
      displayProjectTaskRiskHeatmap: false,
      displayTemplatesList: true,
      displayTemplateFormsList: true,
    },
  ],
]);
