import type { Tenant } from "@/types/tenant/Tenant";
import { isEqual } from "lodash-es";
import { useTenantStore } from "./useTenantStore.store";

const originalState = useTenantStore.getState();

const dummyTenant: Tenant = {
  name: "urbint",
  displayName: "Urbint",
  entities: [
    {
      key: "workPackage",
      label: "Work Package",
      labelPlural: "Work Packages",
      defaultLabel: "Work Package",
      defaultLabelPlural: "Work Packages",
      attributes: [
        {
          key: "name",
          label: "Project Name",
          labelPlural: "Project Names",
          defaultLabel: "Work Package Name",
          defaultLabelPlural: "Work Package Names",
          mandatory: true,
          visible: true,
          required: true,
          filterable: true,
          mappings: null,
        },
        {
          key: "status",
          label: "Project Status",
          labelPlural: "Project Statuses",
          defaultLabel: "Status",
          defaultLabelPlural: "Statuses",
          mandatory: true,
          visible: true,
          required: true,
          filterable: false,
          mappings: {
            pending: ["Pending"],
            active: ["Active"],
            completed: ["Completed"],
          },
        },
      ],
    },
    {
      key: "location",
      label: "Location",
      labelPlural: "Locations",
      defaultLabel: "Location",
      defaultLabelPlural: "Locations",
      attributes: [],
    },
    {
      key: "activity",
      label: "Activity",
      labelPlural: "Activities",
      defaultLabel: "Activity",
      defaultLabelPlural: "Activities",
      attributes: [],
    },
  ],
  workos: [],
};

describe(useTenantStore.name, () => {
  beforeEach(() => {
    useTenantStore.setState(originalState);
    const { setTenant } = useTenantStore.getState();
    setTenant(dummyTenant);
  });

  describe("setTenant", () => {
    it("should set the tenant", () => {
      const { tenant } = useTenantStore.getState();

      expect(tenant.name).toEqual("urbint");
      expect(tenant.entities).toHaveLength(3);
    });
  });

  describe("getAllEntities", () => {
    it("should get all the tenant attributes", () => {
      const { getAllEntities } = useTenantStore.getState();

      const entities = getAllEntities();

      expect(
        isEqual(
          Object.values(entities).map(entity => entity.key),
          dummyTenant.entities.map(entity => entity.key)
        )
      );
    });
  });

  describe("getEntityByKey", () => {
    it("should return a section based on a given ID", () => {
      const { getEntityByKey } = useTenantStore.getState();
      const attributes = getEntityByKey("workPackage");

      expect(attributes.key).toBe("workPackage");
    });
  });

  describe("getMappingValue", () => {
    describe('when the attribute has a "mappings" array', () => {
      it('should return the mapping value based on the "key" provided', () => {
        const { getMappingValue } = useTenantStore.getState();
        const value = getMappingValue("status", "pending");

        expect(value).toBe("Pending");
      });

      it('should return an empty value if the provided "key" doesn"t exist', () => {
        const { getMappingValue } = useTenantStore.getState();
        const value = getMappingValue("status", "inactive");

        expect(value).toBe("");
      });
    });

    describe('when the attribute doesn\'t have a "mappings" array', () => {
      it("should return an empty value", () => {
        const { getMappingValue } = useTenantStore.getState();
        const value = getMappingValue("name", "pending");

        expect(value).toBe("");
      });
    });
  });
});
