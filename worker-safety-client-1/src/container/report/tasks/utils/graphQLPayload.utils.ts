import type { TaskSelectionInputs } from "@/types/report/DailyReportInputs";
import type { Location } from "@/types/project/Location";
import type {
  HazardAggregator,
  TaskHazardAggregator,
} from "@/types/project/HazardAggregator";
import { taskFormInputPrefix } from "../Tasks";

export type TasksGraphQLPayloadParams = {
  [taskFormInputPrefix]?: Record<string, true>;
};

export type TasksGraphQLPayloadOptions = { location: Location };

type ReturnedTasksGraphQLPayload = {
  taskSelection: {
    selectedTasks: TaskSelectionInputs[];
  };
};

const filterAndTransformSelectedTasks =
  (taskSelection: TasksGraphQLPayloadParams["taskSelection"]) =>
  // TODO: this should be rewritten to include either the SiteConditionHazardAggregator Or TaskHazardAggregator
  (
    acc: TaskSelectionInputs[],
    { id, name, riskLevel }: HazardAggregator | TaskHazardAggregator
  ) => {
    if (taskSelection?.[id]) {
      acc.push({
        id,
        name,
        riskLevel,
      });
    }

    return acc;
  };

export function transformGraphQLPayload(
  formData: TasksGraphQLPayloadParams,
  options: TasksGraphQLPayloadOptions
): ReturnedTasksGraphQLPayload {
  const { taskSelection } = formData || {};
  const selectedTasks = options.location.tasks.reduce(
    filterAndTransformSelectedTasks(taskSelection),
    [] as TaskSelectionInputs[]
  );

  return {
    [taskFormInputPrefix]: {
      selectedTasks,
    },
  };
}
