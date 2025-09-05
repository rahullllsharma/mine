import { getFeatureLabels } from "@/utils/featureLabels";
import { getEnv } from "@/utils/env";
import environmentTenantFeatures from "./environmentTenantFeatures";

// TODO: These values might be incomplete
const HYDRO_ONE_TENANT_VALUES = ["hydro1", "uat-hydroone", "hydroone"];
const NATGRID_TENANT_VALUES = ["uat-natgrid", "natgrid"];

export type LocationCardDynamicProps = {
  identifier: string;
  slot3: string;
};

export type TenantsList =
  | "asgard"
  | "exelon"
  | "xcelenergy"
  | "test-xcelenergy"
  | "test-xcelenergy1"
  | "test-georgia-power"
  | "georgia-power"
  | "hydro"
  | "natgrid"
  | "urbint"
  | "ws-demo"
  | "uat"
  | "test-ng"
  | "ng"
  | "automation-integration"
  | "dominion"
  | "test-dominion"
  | "test-preprod";

export type Features = {
  displayLearnings?: boolean;
  displayInspections?: boolean;
  displayProjectsAsLandingPage?: boolean;
  displayFormsAsLandingPage?: boolean;
  displayTemplateFormsAsLandingPage?: boolean;
  displayWorkPackage?: boolean;
  displayMap?: boolean;
  displayJSB?: boolean;
  displayFormsList?: boolean;
  displayAddForm?: boolean;
  displayAddEbo?: boolean;
  displayAddJsb?: boolean;
  displayPlannings?: boolean;
  displayInsights?: boolean;
  displayAddCriticalActivity?: boolean;
  displayProjectTaskRiskHeatmap?: boolean;
  displayTemplatesList?: boolean;
  displayTemplateFormsList?: boolean;
};
type DisplayProps = {
  displayLocationCardDynamicProps: LocationCardDynamicProps;
};

type TenantFeatures = Features & DisplayProps;

export type FeaturesMap = Map<TenantsList, Features>;

const defaultFeatures: Features = {
  displayLearnings: true, // Default On
  displayInspections: true, // Default On
  displayProjectsAsLandingPage: true, // Default On
  displayFormsAsLandingPage: false, // Default Off
  displayTemplateFormsAsLandingPage: false, // Default Off
  displayJSB: false, // Default Off
  displayFormsList: false, // Default Off
  displayAddForm: true, // Default On
  displayAddEbo: false, // Default Off
  displayAddJsb: false, // Default Off
  displayWorkPackage: true, // Default On
  displayMap: true, // Default On
  displayPlannings: true, //Default On
  displayInsights: true, // Default On
  displayAddCriticalActivity: false, // Default
  displayProjectTaskRiskHeatmap: true, // Default On
  displayTemplatesList: false, // Default Off
  displayTemplateFormsList: false, // Default Off
};

/**
 * This function mimics the response form launchDarkly.
 * LaunchDarkly supports a feature flag as JSON.
 */
// TODO: When LaunchDarkly is implemented this function will be able to be removed.
const getLocationCardDynamicProps = (
  tenant: string
): LocationCardDynamicProps => {
  const { VALUES } = getFeatureLabels();

  if (HYDRO_ONE_TENANT_VALUES.includes(tenant)) {
    return {
      identifier: VALUES.ACTIVITY,
      slot3: VALUES.ACTIVITY,
    };
  }

  if (NATGRID_TENANT_VALUES.includes(tenant)) {
    return {
      identifier: VALUES.WORK_PACKAGE,
      slot3: VALUES.LOCATION,
    };
  }

  return {
    identifier: VALUES.WORK_PACKAGE,
    slot3: VALUES.LOCATION,
  };
};

/**
 * This is a temporary file that should be removed once feature flags are in use
 */
function useTenantFeatures(tenant: string): TenantFeatures {
  const tenantFeaturesMap = environmentTenantFeatures[getEnv()];
  const tenantFeatureKey = Array.from(tenantFeaturesMap.keys()).find(
    featureKey => tenant.includes(featureKey)
  ) as TenantsList | undefined;

  const locationCardDynamicProps = getLocationCardDynamicProps(tenant);

  if (tenantFeatureKey) {
    const tenantFeatures = tenantFeaturesMap.get(tenantFeatureKey);
    if (tenantFeatures) {
      return {
        ...defaultFeatures,
        ...tenantFeatures,
        displayLocationCardDynamicProps: locationCardDynamicProps,
      };
    }
  }

  return {
    ...defaultFeatures,
    displayLocationCardDynamicProps: locationCardDynamicProps,
  };
}

export { useTenantFeatures };
