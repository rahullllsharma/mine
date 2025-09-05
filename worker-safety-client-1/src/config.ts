import getConfig from "next/config";

const prc = getConfig()?.publicRuntimeConfig;

export const config = {
  workerSafetyServiceUrlGraphQL:
    prc?.WORKER_SAFETY_SERVICE_URL_GRAPH_QL ?? "http://localhost:8001",
  workerSafetyServiceUrlRest:
    prc?.WORKER_SAFETY_SERVICE_URL_REST ?? "http://127.0.0.1:8000",
  workerSafetyAuditTrailServiceRest:
    prc?.WORKER_SAFETY_AUDIT_TRAIL_SERVICE_REST ?? "http://127.0.0.1:7001",
  workerSafetyCustomWorkFlowUrlRest:
    prc?.WORKER_SAFETY_CUSTOM_WORKFLOW_URL_REST ?? "http://localhost:5001",
  keycloakUrl: prc?.KC_URL ?? "http://localhost:8080/auth",
  keycloakRealm: prc?.KC_REALM, // ?? "asgard",
  keycloakClientId: prc?.KC_CLIENT, // ?? "worker-safety-asgard",
  appEnv: prc?.APP_ENV, // ?? "development",
  datadogClientAppId: prc?.DD_CLIENT_APPLICATION_ID, // ?? "",
  datadogClientToken: prc?.DD_CLIENT_TOKEN, // ?? "",
  datadogClientSite: prc?.DD_CLIENT_SITE ?? "datadoghq.com",
  datadogClientSampleRate: prc?.DD_SAMPLE_RATE ?? 0,
  datadogClientPremiumSampleRate: prc?.DD_PREMIUM_SAMPLE_RATE ?? 0,
  datadogClientService: prc?.DD_SERVICE, // ?? "",
  datadogClientServiceVersion: prc?.DD_VERSION, //?? "",
  datadogClientEnv: prc?.DD_ENV, // ?? "",
  datadogRUMEnabled: prc?.DD_RUM_ENABLED,
  workerSafetyMapboxAccessToken:
    prc?.WORKER_SAFETY_MAPBOX_ACCESS_TOKEN ??
    "pk.eyJ1IjoidXJiaW50LWVuZyIsImEiOiJjbGZsbnZjdGgwM244M3Btb2F0Ym8ya2VkIn0.5Ca4InOhNXx_iZgi4lT7HA",
  fullStoryEnabled: prc?.USER_ANALYTICS_ENABLED,
  pendoEnabled: prc?.USER_ANALYTICS_ENABLED,
  pendoToken: "e93ecea8-64b5-4109-5d0f-37b800c18478",
  experimentalFeatures: prc?.EXPERIMENTAL_FEATURES,
  tinyMceApiKey:
    prc?.TINYMCE_API_KEY ?? "vxq07amit7wfrl9xawsmz8kc9w7xo57v9jnbxxqqobxguyd4",
  powerBi: {
    authenticationMode: "ServicePrincipal",
    authorityUrl: "https://login.microsoftonline.com/",
    scopeBase: "https://analysis.windows.net/powerbi/api/.default",
    powerBiApiUrl: "https://api.powerbi.com/",
    clientId: prc?.POWER_BI_CLIENT_ID,
    clientSecret: prc?.POWER_BI_CLIENT_SECRET,
    tenantId: prc?.POWER_BI_TENANT_ID,
    workspaceId: prc?.POWER_BI_WORKSPACE_ID,
  },
  FEATURE_FLAG_CLIENT_ID: prc?.FEATURE_FLAG_CLIENT_ID ?? "",
};
