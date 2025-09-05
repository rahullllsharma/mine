import type { HazardData } from "../task/TaskData";

export type SiteConditionData = {
  librarySiteConditionId: string;
  hazards?: HazardData[];
};
