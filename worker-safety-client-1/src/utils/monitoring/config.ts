import type { config } from "@/config";

export const buildRumConfig = ({
  datadogClientAppId,
  datadogClientToken,
  datadogClientSite,
  datadogClientService,
  datadogClientServiceVersion,
  datadogClientSampleRate,
  datadogClientPremiumSampleRate,
  datadogClientEnv,
}: Pick<
  typeof config,
  | "datadogClientAppId"
  | "datadogClientToken"
  | "datadogClientSite"
  | "datadogClientService"
  | "datadogClientServiceVersion"
  | "datadogClientSampleRate"
  | "datadogClientPremiumSampleRate"
  | "datadogClientEnv"
>): {
  applicationId: string;
  clientToken: string;
  site: string;
  env: string;
  service: string;
  version: string;
  silentMultipleInit: boolean;
  sampleRate: number;
  premiumSampleRate: number;
  trackInteractions: boolean;
  defaultPrivacyLevel: string;
} => ({
  applicationId: datadogClientAppId,
  clientToken: datadogClientToken,
  site: datadogClientSite,
  env: datadogClientEnv,
  service: datadogClientService,
  version: datadogClientServiceVersion,
  silentMultipleInit: true,
  sampleRate: +datadogClientSampleRate,
  premiumSampleRate: +datadogClientPremiumSampleRate,
  trackInteractions: true,
  defaultPrivacyLevel: "mask-user-input",
});
