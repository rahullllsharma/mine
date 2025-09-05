export const TENANT_CONFIG = {
  // Set the current tenant to test
  CURRENT_TENANT: "urbint-integration",

  // Available tenants for different environments
  TENANTS: {
    staging: ["urbint-gas", "staging-exelon", "dominion", "natgrid", "georgia-power","natgrid"],
    integ: ["urbint-integration", "integ-exelon", "integ-dominion"],
    production: [
      "natgrid",
      "georgia-power",
      "exelon",
      "dominion",
      "ng",
      "ws-demo", //demo env
      "uat", //demo env
      "test-dominion", //demo env
      "test-georgia-power", //demo env
      "test-exelon", //demo env
      "test-ng", //demo env
    ],
  },
};

export function getCurrentTenant(): string {
  return TENANT_CONFIG.CURRENT_TENANT;
}

export function getAvailableTenants(environment: string): string[] {
  return (
    TENANT_CONFIG.TENANTS[environment as keyof typeof TENANT_CONFIG.TENANTS] ||
    []
  );
}
