export interface Form {
  __typename?: string;
  id: string;
  formId?: string;
  status: string;
  completedAt?: string;
  createdAt?: string;
  date?: string;
  location?: {
    name: string;
    id: string;
  };
  createdBy?: {
    id: string;
    name: string;
  };
  workPackage?: {
    name: string;
    id: string;
  };
  updatedBy?: {
    id: string;
    name: string;
  };
  updatedAt?: string;
  locationName?: string;
  contents?: {
    workLocation?: {
      description?: string;
    };
  };
  operatingHq?: string;
  multipleLocation?: number;
  supervisor?: { id: string; name: string; email: string }[];
}

export interface FormsListFilterOptions {
  formNames: string[];
  formIds: string[];
  operatingHqs: string[];
  updatedByUsers: { id: string; name: string }[];
  workPackages: { id: string; name: string }[];
  createdByUsers: { id: string; name: string }[];
  locations: { id: string; name: string }[];
  supervisors: { id: string; name: string }[];
}
