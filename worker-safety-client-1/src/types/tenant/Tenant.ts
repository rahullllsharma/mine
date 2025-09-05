import type { TenantEntity } from "./TenantEntities";

type Tenant = {
  name: string;
  displayName: string;
  entities: TenantEntity[];
  workos: string[];
};

export type { Tenant };
