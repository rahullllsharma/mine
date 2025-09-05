import type { TenantEntity, EntityKey } from "@/types/tenant/TenantEntities";
import type { EntityAttributeMap } from "@/store/tenant/types";

const updateAttributes = (
  entities: TenantEntity[],
  key: EntityKey,
  label: string,
  labelPlural: string
) => {
  return entities.map(entity =>
    entity.key === key ? { ...entity, label, labelPlural } : entity
  );
};

const parseEntities = (entities: TenantEntity[]) =>
  new Map(
    entities.map(entity => [
      entity.key,
      {
        ...entity,
        attributes: Object.fromEntries(
          new Map(
            entity.attributes.map(attribute => [attribute.key, attribute])
          )
        ) as EntityAttributeMap,
      },
    ])
  );

export { updateAttributes, parseEntities };
