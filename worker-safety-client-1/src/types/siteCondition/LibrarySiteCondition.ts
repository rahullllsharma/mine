import type { Hazard } from "../project/Hazard";

export type LibrarySiteCondition = {
  id: string;
  name: string;
  hazards: Hazard[];
};
