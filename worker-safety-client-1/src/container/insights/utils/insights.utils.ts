import type { Project } from "@/types/project/Project";
import type { Location } from "@/types/project/Location";
import type { TimeFrameOption } from "../timeFrame/TimeFrame";
import { DateTime } from "luxon";
import { convertDateToString, getDate } from "@/utils/date/helper";

type FilterProject = Pick<Project, "id" | "name" | "externalKey" | "number"> & {
  locations: FilterLocations;
};

type FilterLocations = Pick<Location, "id" | "name">[];

const pastTimeFrameData: Readonly<TimeFrameOption[]> = Object.freeze([
  { id: "1", name: "Previous 2 weeks", numberOfDays: -14 },
  { id: "2", name: "Previous 30 days", numberOfDays: -30 },
  { id: "3", name: "Previous 90 days", numberOfDays: -90 },
]);

const futureTimeFrameData: Readonly<TimeFrameOption[]> = Object.freeze([
  { id: "1", name: "Next 2 weeks", numberOfDays: 14 },
  { id: "2", name: "Next week", numberOfDays: 7 },
]);

const getFormattedDate = function (
  date?: Date,
  options: { format: string } = { format: "yyyy-MM-dd" }
) {
  if (!date || !DateTime.fromISO(date.toISOString()).isValid) {
    return null;
  }

  return DateTime.fromISO(date?.toISOString()).toFormat(options.format);
};

const getTimeFrame = (days: number): string[] => {
  const today = convertDateToString();
  const startDate =
    days > 0 ? today : getDate(today, days, { includeToday: true });
  const endDate =
    days > 0 ? getDate(today, days, { includeToday: true }) : today;

  return [startDate, endDate];
};

// Export types
export type { FilterProject, FilterLocations };

// Export functions
export {
  pastTimeFrameData,
  futureTimeFrameData,
  getTimeFrame,
  getFormattedDate,
};
