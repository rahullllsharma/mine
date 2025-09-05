import type { WorkScheduleInputs } from "@/types/report/DailyReportInputs";
import { isDateValid, getDateAsUTC } from "@/utils/date/helper";
import { workScheduleFormInputPrefix } from "../WorkSchedule";
// import type { Location } from "@/types/project/Location";
// import type { HazardAggregator } from "@/types/project/HazardAggregator";

export type WorkScheduleGraphQLPayloadParams = {
  [workScheduleFormInputPrefix]: Record<string, string | null>;
};

type WorkScheduleInputKeys = keyof WorkScheduleInputs;

type ReturnedTasksGraphQLPayload = {
  workSchedule: WorkScheduleInputs;
};

/**
 * Convert the start and end datetimes selected to UTC and send to the backend
 *
 */
export default function transformGraphQLPayload(
  formData: WorkScheduleGraphQLPayloadParams
): ReturnedTasksGraphQLPayload {
  const { [workScheduleFormInputPrefix]: workSchedule } = formData || {};

  return {
    [workScheduleFormInputPrefix]: Object.entries(workSchedule).reduce(
      (acc, [key, value]) => {
        const valueAsString = value || "";

        acc[key as WorkScheduleInputKeys] = isDateValid(valueAsString)
          ? getDateAsUTC(valueAsString)
          : null;

        return acc;
      },
      {} as Partial<WorkScheduleInputs>
    ) as WorkScheduleInputs,
  };
}
