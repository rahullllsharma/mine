import type { LibraryDivision } from "@/types/project/LibraryDivision";
import type { LibraryProjectType } from "@/types/project/LibraryProjectType";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { User } from "@/types/User";
import type { Contractor } from "@/types/project/Contractor";
import type { IconName } from "@urbint/silica";

export type FilterField =
  | "RISK"
  | "REGIONS"
  | "DIVISIONS"
  | "TYPES"
  | "PROJECT"
  | "CONTRACTOR"
  | "SUPERVISOR"
  | "PROJECT_STATUS";

export enum OrderByDirection {
  ASC = "ASC",
  DESC = "DESC",
}

export type MapViewMobileViews = "map" | "list";

export type MapProjectLibraries = {
  projectTypesLibrary: LibraryProjectType[];
  divisionsLibrary: LibraryDivision[];
  regionsLibrary: LibraryRegion[];
  supervisors: User[];
  contractors: Contractor[];
};

export interface LocationVariables {
  startDate?: string | null;
  endDate?: string | null;
  filterBy?: {
    values: string[];
    field: FilterField;
  }[];
  search?: string;
  orderBy?: {
    field: string;
    direction: OrderByDirection;
  }[];
  minX?: number;
  maxX?: number;
  minY?: number;
  maxY?: number;
  limit?: number;
  offset?: number;
}

export interface QuickFilter {
  id: string;
  name: string;
  icon: IconName;
  state: boolean;
}

export type LatLng = {
  lat: number;
  lng: number;
};

export type MapBounds = mapboxgl.LngLatBounds;
