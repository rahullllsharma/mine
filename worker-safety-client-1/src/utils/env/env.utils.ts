import { config } from "@/config";
import { REALM_PROD_LIST } from "@/constants";

enum Environments {
  development = "development",
  integ = "integ",
  staging = "staging",
  production = "production",
  preprod = "preprod",
}

function isProdEnv() {
  return config.appEnv === "prod" || config.appEnv === "production";
}

function getEnv(): Environments {
  return config.appEnv || Environments.development;
}

function getRealm(isProd: boolean) {
  if (isProd && Object.keys(REALM_PROD_LIST).includes(config.keycloakRealm)) {
    return REALM_PROD_LIST[config.keycloakRealm];
  }

  return config.keycloakRealm;
}

/**
 * Takes comma separated list of features
 */
function getExperimentalFeatures(): string[] {
  return config.experimentalFeatures?.split(",") ?? [];
}

function isFeatureEnabled(featureName: string) {
  return getExperimentalFeatures().some(feature => feature === featureName);
}

export { isProdEnv, getEnv, getRealm, isFeatureEnabled };
