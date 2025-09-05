import type { HazardKeyInput } from "../form/HazardInput";

export type TaskInputs = {
  libraryTaskId: string;
  startDate: string;
  endDate: string;
  status: { id: string; name: string };
  hazards?: HazardKeyInput;
};
