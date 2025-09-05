type EntityKey =
  | "workPackage"
  | "location"
  | "activity"
  | "task"
  | "hazard"
  | "control"
  | "siteCondition"
  | "templateForm"
  | "formList";

type EntityAttributeKey =
  | "name"
  | "externalKey"
  | "workPackageType"
  | "status"
  | "primeContractor"
  | "otherContractor"
  | "startDate"
  | "endDate"
  | "division"
  | "region"
  | "zipCode"
  | "description"
  | "assetType"
  | "projectManager"
  | "primaryAssignedPerson"
  | "additionalAssignedPerson"
  | "contractName"
  | "contractReferenceNumber"
  | "crew"
  | "criticalActivity"
  | "libraryActivityType"
  | "formName"
  | "formId"
  | "location"
  | "status"
  | "workPackage"
  | "createdBy"
  | "createdOn"
  | "updatedBy"
  | "updatedOn"
  | "completedOn"
  | "date"
  | "operatingHQ"
  | "region"
  | "reportDate"
  | "Project"
  | "supervisor"
  | "workTypes";

type CommonAttributes = {
  label: string;
  labelPlural: string;
  defaultLabel: string;
  defaultLabelPlural: string;
};

type EntityAttributes = CommonAttributes & {
  key: EntityAttributeKey;
  visible: boolean;
  required: boolean;
  filterable: boolean;
  mandatory: boolean;
  mappings: Record<string, string[]> | null;
};

type TenantEntity = CommonAttributes & {
  key: EntityKey;
  attributes: EntityAttributes[];
};

export type { EntityKey, EntityAttributeKey, TenantEntity, EntityAttributes };
