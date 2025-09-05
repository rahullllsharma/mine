import type { CreatedBy } from "./CreatedBy";

export interface Control {
  id: string;
  name: string;
  isApplicable: boolean;
  libraryControl?: {
    id: string;
  };
  createdBy?: CreatedBy;
}
