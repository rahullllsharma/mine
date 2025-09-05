import type { Tenant } from "@/types/tenant/Tenant";
import type {
  EntityAttributeKey,
  EntityKey,
  TenantEntity,
} from "@/types/tenant/TenantEntities";
import type { TenantEntityMap, EntityMap } from "./types";
import create from "zustand";
import { parseEntities } from "./utils";

export interface TenantStore {
  tenant: Tenant;
  setTenant: (tenant: Tenant) => void;
  getAllEntities: () => EntityMap;
  getEntityByKey: (key: EntityKey) => TenantEntity;
  getMappingValue: (attribute: EntityAttributeKey, key: string) => string;
}

const defaultTenant: Tenant = {
  name: "",
  displayName: "",
  entities: [],
  workos: [],
};
let entitiesMap = new Map<EntityKey, TenantEntityMap>();

const setEntitiesMap = (entities: TenantEntity[]) => {
  entitiesMap = parseEntities(entities);
};

const useTenantStore = create<TenantStore>()((set, get) => ({
  tenant: defaultTenant,
  setTenant: tenant => {
    set(() => ({ tenant }));
    setEntitiesMap(get().tenant.entities);
  },
  getAllEntities: () => {
    return Object.fromEntries(entitiesMap) as EntityMap;
  },
  getEntityByKey: key =>
    get().tenant.entities.find(section => section.key === key) as TenantEntity,
  getMappingValue: (attribute, key) =>
    get().getAllEntities().workPackage.attributes[attribute].mappings?.[
      key
    ]?.[0] ?? "",
}));

export { useTenantStore };
