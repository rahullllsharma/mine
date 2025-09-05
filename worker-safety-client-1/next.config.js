/** @type {import('next').NextConfig} */

// eslint-disable-next-line @typescript-eslint/no-var-requires
const path = require("path");

// eslint-disable-next-line @typescript-eslint/no-var-requires
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

module.exports = withBundleAnalyzer({
  images: {
    domains: [
      "storage.googleapis.com",
      "restore-build-artefacts.s3.amazonaws.com",
    ],
  },
  webpack: config => {
    config.module.rules.push({
      test: /\.(graphql|gql)$/,
      exclude: /node_modules/,
      loader: "graphql-tag/loader",
    });
    return config;
  },
  swcMinify: true,
  reactStrictMode: true,
  serverRuntimeConfig: {
    WORKER_SAFETY_PUBLIC_FOLDER: path.join(__dirname, "/public"),
    APOLLO_LOGGER: process.env.APOLLO_LOGGER,
  },
  publicRuntimeConfig: {
    APP_ENV: process.env.APP_ENV ?? process.env.DD_ENV ?? "development",
    APOLLO_LOGGER: process.env.APOLLO_LOGGER,
    WORKER_SAFETY_SERVICE_URL_GRAPH_QL:
      process.env.WORKER_SAFETY_SERVICE_URL_GRAPH_QL,
    WORKER_SAFETY_SERVICE_URL_REST: process.env.WORKER_SAFETY_SERVICE_URL_REST,
    WORKER_SAFETY_CUSTOM_WORKFLOW_URL_REST:
      process.env.WORKER_SAFETY_CUSTOM_WORKFLOW_URL_REST,
    KC_URL: process.env.KC_URL,
    KC_REALM: process.env.KC_REALM,
    KC_CLIENT: process.env.KC_CLIENT,
    WORKER_SAFETY_MAPBOX_ACCESS_TOKEN:
      process.env.WORKER_SAFETY_MAPBOX_ACCESS_TOKEN,
    USER_ANALYTICS_ENABLED: process.env.USER_ANALYTICS_ENABLED,
    DD_CLIENT_APPLICATION_ID: process.env.DD_CLIENT_APPLICATION_ID,
    DD_CLIENT_TOKEN: process.env.DD_CLIENT_TOKEN,
    DD_CLIENT_SITE: process.env.DD_CLIENT_SITE,
    DD_SAMPLE_RATE: process.env.DD_SAMPLE_RATE,
    DD_PREMIUM_SAMPLE_RATE: process.env.DD_PREMIUM_SAMPLE_RATE,
    DD_SERVICE: process.env.DD_SERVICE,
    DD_VERSION: process.env.DD_VERSION,
    DD_ENV: process.env.DD_ENV,
    DD_RUM_ENABLED: process.env.DD_RUM_ENABLED,
    EXPERIMENTAL_FEATURES: process.env.EXPERIMENTAL_FEATURES,
    TINYMCE_API_KEY: process.env.TINYMCE_API_KEY,
    POWER_BI_CLIENT_ID: process.env.POWER_BI_CLIENT_ID,
    POWER_BI_CLIENT_SECRET: process.env.POWER_BI_CLIENT_SECRET,
    POWER_BI_TENANT_ID: process.env.POWER_BI_TENANT_ID,
    POWER_BI_WORKSPACE_ID: process.env.POWER_BI_WORKSPACE_ID,
    FEATURE_FLAG_CLIENT_ID: process.env.FEATURE_FLAG_CLIENT_ID,
    WORKER_SAFETY_AUDIT_TRAIL_SERVICE_REST:
      process.env.WORKER_SAFETY_AUDIT_TRAIL_SERVICE_REST,
  },
});
