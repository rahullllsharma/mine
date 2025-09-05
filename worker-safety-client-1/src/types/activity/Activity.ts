import type { TaskStatus } from "../task/TaskStatus";
import type { TaskHazardAggregator } from "../project/HazardAggregator";
import type { LibraryActivityType } from "../project/LibraryActivityType";
import type { User } from "../User";

type Activity = {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  status: TaskStatus;
  taskCount: number;
  tasks: TaskHazardAggregator[];
  libraryActivityType?: LibraryActivityType;
  supervisors?: User[];
  isCritical?: boolean;
  crticalDescription?: string | null;
};

export type { Activity };
