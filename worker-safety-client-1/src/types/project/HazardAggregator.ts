import type { LibraryTask } from "../task/LibraryTask";
import type { LibrarySiteCondition } from "../siteCondition/LibrarySiteCondition";
import type { TaskStatus } from "../task/TaskStatus";
import type { Hazard } from "./Hazard";
import type { CreatedBy } from "./CreatedBy";
import type { Activity } from "../activity/Activity";
import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import type { Incident } from "./Incident";

// Base for all tasks, site conditions and possible activities
type BaseHazardAggregator = {
  id: string;
  name: string;
  hazards: Hazard[];
  createdBy?: CreatedBy;
  incidents?: Incident[];
};

/**
 * Retro compatibility with the old tasks
 * @deprecated
 */
type HazardAggregator = BaseHazardAggregator & {
  startDate: string;
  endDate: string;
  riskLevel: RiskLevel;
  libraryTask?: LibraryTask;
  librarySiteCondition?: LibrarySiteCondition;
  status: TaskStatus;
  isManuallyAdded: boolean;
};

/**
 * FIXME: Extract into several aggregators (task, site conditions, and probably activities)
 *
 * For tasks with the activity parent, we can't assume that `startDate`, etc will exist and are deprecated
 * That's information from the actual Activity.
 *
 * Maybe on https://urbint.atlassian.net/browse/WSAPP-995 ?
 */
type TaskHazardAggregator = BaseHazardAggregator &
  Pick<HazardAggregator, "libraryTask" | "riskLevel"> & {
    activity?: Activity; // | null; // This can be nullable
  };

// type SiteConditionHazardAggregator = BaseHazardAggregator & {
//   librarySiteCondition?: LibrarySiteCondition;
//   status: TaskStatus;
// }

export type { HazardAggregator, TaskHazardAggregator };
