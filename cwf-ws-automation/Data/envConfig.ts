import dotenv from "dotenv";
import * as envInterfaces from "../types/interfaces";
dotenv.config();

import { getCurrentTenant } from "./tenantConfig";
//set the current environment here
export const CURRENT_ENV: "integ" | "staging" | "production" = "integ";
export const CURRENT_TENANT = getCurrentTenant();

export const envConfig: envInterfaces.EnvConfig = {
  environment: {
    integ: {
      url: process.env.INTEG_URL || "",
      username: process.env.INTEG_USERNAME || "",
      password: process.env.INTEG_PASSWORD || "",
    },
    staging: {
      url: process.env.STAGING_URL || "",
      username: process.env.STAGING_USERNAME || "",
      password: process.env.STAGING_PASSWORD || "",
    },
    production: {
      url: process.env.PROD_URL || "",
      username: process.env.PROD_USERNAME || "",
      password: process.env.PROD_PASSWORD || "",
    },
  },
};

export const apiURLToCapture: envInterfaces.ApiUrlConfig = {
  url: {
    cwfTemplates: {
      integ: "https://cwf-api.integ.urbinternal.com/templates/",
      staging: "https://cwf-api.staging.urbinternal.com/templates/",
      production: "https://cwf-api.urbint.com/templates/",
    },
    cwfTemplatesSaveAndComplete: {
      integ: "https://cwf-api.integ.urbinternal.com/forms/",
      staging: "https://cwf-api.staging.urbinternal.com/forms/",
      production: "https://cwf-api.urbint.com/forms/",
    },
  },
};

export function getCurrentEnvUrl() {
  const baseUrl =
    envConfig.environment[CURRENT_ENV as keyof typeof envConfig.environment]
      .url;
  return buildTenantUrl(baseUrl, CURRENT_TENANT);
}

export function buildTenantUrl(baseUrl: string, tenant: string): string {
  // Extract the base domain from the environment URL
  const urlParts = baseUrl.split("//");
  if (urlParts.length !== 2) {
    throw new Error(`Invalid URL format: ${baseUrl}`);
  }

  const domain = urlParts[1];
  const domainParts = domain.split(".");

  // Build tenant-specific URL
  // Format: https://{tenant}.ws.{environment}.urbinternal.com/
  if (CURRENT_ENV === "staging") {
    return `https://${tenant}.ws.staging.urbinternal.com/`;
  } else if (CURRENT_ENV === "integ") {
    return `https://${tenant}.ws.integ.urbinternal.com/`;
  } else if (CURRENT_ENV === "production") {
    return `https://${tenant}.ws.urbint.com/`;
  }

  throw new Error(`Unsupported environment: ${CURRENT_ENV}`);
}

export function getURLForService(service: keyof envInterfaces.ApiCategories) {
  return apiURLToCapture.url[service][
    CURRENT_ENV as keyof typeof envConfig.environment
  ];
}

export function getEnvironmentData() {
  return envConfig.environment[
    CURRENT_ENV as keyof typeof envConfig.environment
  ];
}
