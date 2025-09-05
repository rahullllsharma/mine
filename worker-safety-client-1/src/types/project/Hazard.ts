import type { Control } from "./Control";
import type { CreatedBy } from "./CreatedBy";

export interface Hazard {
  id: string;
  name: string;
  isApplicable: boolean;
  controls: Control[];
  libraryHazard?: {
    id: string;
  };
  createdBy?: CreatedBy;
}
