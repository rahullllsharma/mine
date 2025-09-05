export type ProjectInputs = {
  name: string;
  status: string;
  startDate: string;
  endDate: string;
  minimumTaskDate?: string;
  maximumTaskDate?: string;
  locations: ProjectLocation[];
  libraryDivisionId?: string;
  libraryRegionId?: string;
  libraryProjectTypeId?: string;
  tenantWorkTypesId?: string[];
  externalKey?: string;
  description?: string;
  managerId?: string;
  supervisorId?: string;
  additionalSupervisors?: string[];
  contractorId?: string;
  engineerName?: string;
  projectZipCode?: string;
  contractReference?: string;
  contractName?: string;
  libraryAssetTypeId?: string;
};

export type ProjectLocation = {
  id?: string;
  name: string;
  latitude: number | null;
  longitude: number | null;
  supervisorId?: string;
  additionalSupervisors?: string[];
  externalKey?: string;
};
