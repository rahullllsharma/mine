import type {
  EntityKey,
  TenantEntity,
  EntityAttributeKey,
  EntityAttributes,
} from "@/types/tenant/TenantEntities";

type TenantEntityMap = Omit<TenantEntity, "attributes"> & {
  attributes: EntityAttributeMap;
};
type EntityMap = Record<EntityKey, TenantEntityMap>;
type EntityAttributeMap = Record<EntityAttributeKey, EntityAttributes>;

export type { TenantEntityMap, EntityMap, EntityAttributeMap };
