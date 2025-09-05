import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import type { User } from "../User";
import type { Contractor } from "./Contractor";
import type { LibraryDivision } from "./LibraryDivision";
import type { LibraryProjectType } from "./LibraryProjectType";
import type { LibraryRegion } from "./LibraryRegion";
import type { Location } from "./Location";
import type { LibraryAssetType } from "./LibraryAssetType";
import type { WorkType } from "../task/WorkType";

export interface Project {
  id: string;
  name: string;
  riskLevel: RiskLevel;
  region: string;
  status: string;
  startDate: string;
  endDate: string;
  locations: Location[];
  libraryRegion?: LibraryRegion;
  libraryDivision?: LibraryDivision;
  libraryProjectType?: LibraryProjectType;
  /** @deprecated confirm if the number property will go away eventually, ATM it still exists in the BE type*/
  number?: string;
  externalKey?: string;
  description?: string;
  manager?: User;
  supervisor?: User;
  additionalSupervisors?: User[];
  contractor?: Contractor;
  engineerName?: string;
  projectZipCode?: string;
  contractReference?: string;
  contractName?: string;
  libraryAssetType?: LibraryAssetType;
  minimumTaskDate?: string;
  maximumTaskDate?: string;
  workTypes?: WorkType[];
}
