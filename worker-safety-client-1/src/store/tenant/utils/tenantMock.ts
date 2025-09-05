import type { Tenant } from "@/types/tenant/Tenant";
import type {
  EntityKey,
  EntityAttributeKey,
} from "@/types/tenant/TenantEntities";

const TenantMock: Tenant = {
  name: "urbint",
  displayName: "Urbint",
  entities: [
    {
      key: "workPackage",
      label: "Project",
      labelPlural: "Projects",
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
          key: "externalKey",
          label: "Project Number",
          labelPlural: "Project Numbers",
          defaultLabel: "External Key",
          defaultLabelPlural: "External Keys",
          mandatory: false,
          visible: true,
          required: true,
          filterable: false,
          mappings: null,
        },
        {
          key: "workPackageType",
          label: "Project Type",
          labelPlural: "Project Types",
          defaultLabel: "Work Package Type",
          defaultLabelPlural: "Work Package Types",
          mandatory: false,
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
        {
          key: "primeContractor",
          label: "Contractor",
          labelPlural: "Contractors",
          defaultLabel: "Prime Contractor",
          defaultLabelPlural: "Prime Contractors",
          mandatory: false,
          visible: true,
          required: true,
          filterable: true,
          mappings: null,
        },
        {
          key: "otherContractor",
          label: "Other Contractor",
          labelPlural: "Other Contractors",
          defaultLabel: "Other Contractor",
          defaultLabelPlural: "Other Contractors",
          mandatory: false,
          visible: true,
          required: false,
          filterable: false,
          mappings: null,
        },
        {
          key: "startDate",
          label: "Start Date",
          labelPlural: "Start Dates",
          defaultLabel: "Start Date",
          defaultLabelPlural: "Start Dates",
          mandatory: true,
          visible: true,
          required: true,
          filterable: false,
          mappings: null,
        },
        {
          key: "endDate",
          label: "End Date",
          labelPlural: "End Dates",
          defaultLabel: "End Date",
          defaultLabelPlural: "End Dates",
          mandatory: true,
          visible: true,
          required: true,
          filterable: false,
          mappings: null,
        },
        {
          key: "division",
          label: "Division",
          labelPlural: "Divisions",
          defaultLabel: "Division",
          defaultLabelPlural: "Divisions",
          mandatory: false,
          visible: true,
          required: true,
          filterable: true,
          mappings: null,
        },
        {
          key: "region",
          label: "Region",
          labelPlural: "Regions",
          defaultLabel: "Region",
          defaultLabelPlural: "Regions",
          mandatory: false,
          visible: true,
          required: true,
          filterable: true,
          mappings: null,
        },
        {
          key: "zipCode",
          label: "Project Zip Code",
          labelPlural: "Project Zip Codes",
          defaultLabel: "Work Package Zip Code",
          defaultLabelPlural: "Work Package Zip Codes",
          mandatory: false,
          visible: true,
          required: false,
          filterable: false,
          mappings: null,
        },
        {
          key: "description",
          label: "Description",
          labelPlural: "Descriptions",
          defaultLabel: "Description",
          defaultLabelPlural: "Descriptions",
          mandatory: false,
          visible: true,
          required: false,
          filterable: false,
          mappings: null,
        },
        {
          key: "assetType",
          label: "Asset Type",
          labelPlural: "Asset Types",
          defaultLabel: "Asset Type",
          defaultLabelPlural: "Asset Types",
          mandatory: false,
          visible: true,
          required: false,
          filterable: false,
          mappings: null,
        },
        {
          key: "projectManager",
          label: "Project Manager",
          labelPlural: "Project Managers",
          defaultLabel: "Project Manager",
          defaultLabelPlural: "Project Managers",
          mandatory: false,
          visible: true,
          required: true,
          filterable: false,
          mappings: null,
        },
        {
          key: "primaryAssignedPerson",
          label: "Primary Project Supervisor",
          labelPlural: "Primary Project Supervisors",
          defaultLabel: "Primary Assigned Person",
          defaultLabelPlural: "Primary Assigned Persons",
          mandatory: false,
          visible: true,
          required: true,
          filterable: true,
          mappings: null,
        },
        {
          key: "additionalAssignedPerson",
          label: "Additional Project Supervisor",
          labelPlural: "Additional Project Supervisors",
          defaultLabel: "Additional Assigned Person",
          defaultLabelPlural: "Additional Assigned Persons",
          mandatory: false,
          visible: true,
          required: false,
          filterable: false,
          mappings: null,
        },
        {
          key: "contractName",
          label: "Contract Name",
          labelPlural: "Contract Names",
          defaultLabel: "Contract Name",
          defaultLabelPlural: "Contract Names",
          mandatory: false,
          visible: true,
          required: false,
          filterable: false,
          mappings: null,
        },
        {
          key: "contractReferenceNumber",
          label: "Contract Reference Number",
          labelPlural: "Contract Reference Numbers",
          defaultLabel: "Contract Reference Number",
          defaultLabelPlural: "Contract Reference Numbers",
          mandatory: false,
          visible: true,
          required: false,
          filterable: false,
          mappings: null,
        },
      ],
    },
    {
      key: "location",
      label: "Location",
      labelPlural: "Locations",
      defaultLabel: "Location",
      defaultLabelPlural: "Locations",
      attributes: [
        {
          key: "name",
          label: "Location Name",
          labelPlural: "Location Names",
          defaultLabel: "Location Name",
          defaultLabelPlural: "Location Names",
          mandatory: true,
          visible: true,
          required: true,
          filterable: true,
          mappings: null,
        },
        {
          key: "primaryAssignedPerson",
          label: "Primary Location Supervisor",
          labelPlural: "Primary Location Supervisors",
          defaultLabel: "Primary Project Person",
          defaultLabelPlural: "Primary Project Persons",
          mandatory: false,
          visible: true,
          required: true,
          filterable: true,
          mappings: null,
        },
        {
          key: "additionalAssignedPerson",
          label: "Additional Location Supervisor",
          labelPlural: "Additional Location Supervisors",
          defaultLabel: "Additional Assigned Person",
          defaultLabelPlural: "Additional Assigned Persons",
          mandatory: false,
          visible: true,
          required: false,
          filterable: false,
          mappings: null,
        },
      ],
    },
    {
      key: "activity",
      label: "Activity",
      labelPlural: "Activities",
      defaultLabel: "Activity",
      defaultLabelPlural: "Activities",
      attributes: [
        {
          defaultLabel: "Activity type",
          defaultLabelPlural: "Activity types",
          key: "libraryActivityType",
          label: "Activity type",
          labelPlural: "Activity types",
          mandatory: false,
          mappings: null,
          visible: true,
          required: true,
          filterable: false,
        },
      ],
    },
    {
      key: "task",
      label: "Task",
      labelPlural: "Tasks",
      defaultLabel: "Task",
      defaultLabelPlural: "Tasks",
      attributes: [],
    },
    {
      key: "hazard",
      label: "Hazard",
      labelPlural: "Hazards",
      defaultLabel: "Hazard",
      defaultLabelPlural: "Hazards",
      attributes: [],
    },
    {
      key: "control",
      label: "Control",
      labelPlural: "Controls",
      defaultLabel: "Control",
      defaultLabelPlural: "Controls",
      attributes: [],
    },
    {
      key: "siteCondition",
      label: "Site Condition",
      labelPlural: "Site Conditions",
      defaultLabel: "Site Condition",
      defaultLabelPlural: "Site Conditions",
      attributes: [],
    },
    {
      key: "templateForm",
      label: "Template Form",
      labelPlural: "templateForms",
      defaultLabel: "Template Form",
      defaultLabelPlural: "Template Forms",
      attributes: [],
    },
    
  ],
  workos: [],
};

type FieldToEdit = {
  entity: EntityKey;
  attribute: EntityAttributeKey;
  key: string;
  value: boolean | string;
};

/**
 * This method is just to be used in tests that require the tenantMock.
 *
 * Edits the tenant mock and returns a new object.
 *
 * If you want to edit multiple attributes of an entity, you can add different entries in fieldsToEdit
 * for example:
 *
  editTenantEntitiesAttributesMock([
    {
      entity: "workPackage",
      attribute: "division",
      key: "visible",
      value: false,
    },
    {
      entity: "workPackage",
      attribute: "division",
      key: "required",
      value: false,
    }
  ])
 *
 * the above function call will create a new tenant mock which will edit
 * - find the entity "workPackage"
 * - find the attribute division
 * - and then will update both attributes "visible" and "required"
 *
 */
const editTenantEntitiesAttributesMock = (
  fieldsToEdit: FieldToEdit[]
): Tenant => {
  const newTenantMock = {
    ...TenantMock,
    entities: TenantMock.entities.map(entity => {
      const allEntityAttributesInFieldsToEdit = fieldsToEdit.filter(
        field => field.entity === entity.key
      );

      if (allEntityAttributesInFieldsToEdit.length === 0) {
        return entity;
      }

      const updatedAttributes = entity.attributes.map(attribute => {
        const attributeValuesToEdit = allEntityAttributesInFieldsToEdit.filter(
          entry => entry.attribute === attribute.key
        );

        if (attributeValuesToEdit.length === 0) {
          return attribute;
        }

        const newAttributeValues = attributeValuesToEdit.reduce(
          (acc, curr) => ({ ...acc, [curr.key]: curr.value }),
          {}
        );

        return { ...attribute, ...newAttributeValues };
      });

      return { ...entity, attributes: updatedAttributes };
    }),
  };

  return newTenantMock;
};

export { TenantMock, editTenantEntitiesAttributesMock };
