import type { Hazard } from "../project/Hazard";
import type { WorkType } from "./WorkType";
import type { LibraryActivityGroup } from "./LibraryActivityGroup";

export type LibraryTask = {
  id: string;
  name: string;
  category: string;
  riskLevel?: string;
  isCritical?: boolean;
  hazards: Hazard[];
  activitiesGroups: LibraryActivityGroup[];
  workTypes?: WorkType[];
};
