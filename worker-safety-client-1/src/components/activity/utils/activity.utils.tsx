import type { ActivityFilter } from "@/container/activity/addActivityModal/AddActivityModal";
import type { LibraryTask } from "@/types/task/LibraryTask";
import { orderBy } from "lodash-es";

export const buildActivityName = (
  activityFilters: ActivityFilter[]
): string => {
  const names = activityFilters
    .filter(filter => filter.values.length)
    .map(item => item.groupName);

  return names.length > 3
    ? names.sort().slice(0, 2).join(" + ") + " + (multiple)"
    : names.sort().join(" + ");
};

// Common function to extract base task ID from any task ID format
export const extractBaseTaskId = (taskId: string): string => {
  if (!taskId.includes("__")) {
    return taskId;
  }

  const parts = taskId.split("__");
  // For double underscore format: prefix__actualTaskId__suffix
  if (parts.length >= 3) {
    return parts[1];
  }
  // For single underscore format: prefix__actualTaskId
  return parts[0];
};

// (WSAPP-972) - Temporary implementation
// While we don't have BE implementation, we need to duplicate tasks so they can be under more than one activ Group
export const getTaskListWithDuplicates = (data: LibraryTask[]) => {
  const singleGroupTasks = data.filter(
    item => item.activitiesGroups.length === 1
  );
  const multipleGroupTasks: LibraryTask[] = [];

  // we also want to have new different Ids for dup tasks, to prevent UX issues
  data
    .filter(item => item.activitiesGroups.length > 1)
    .forEach(task =>
      task.activitiesGroups.map(group =>
        multipleGroupTasks.push({
          ...task,
          id: `${task.id}__${group.id}`,
          activitiesGroups: [
            {
              id: group.id,
              name: group.name,
              aliases: group.aliases,
            },
          ],
        })
      )
    );

  return [...singleGroupTasks, ...multipleGroupTasks];
};

//  (WSAPP-972) - Temporary implementation
//  after task selection, we need to remove duplicates, even if the user selects them
//  these Ids will be used to fetch the BE for tasks for Review in the last step of Add Activity flow
export const removeDuplicatedTaskIds = (selectedTasks: ActivityFilter[]) => {
  const tasksWithNormalizedIds = selectedTasks.map(task => ({
    ...task,
    values: task.values.map(value => ({
      ...value,
      // Extract the actual task ID from double underscore format: prefix__actualTaskId__suffix
      id: extractBaseTaskId(value.id),
    })),
  }));

  const selectedIds: string[] = [];

  const normalizedTasksList = orderBy(
    tasksWithNormalizedIds,
    "groupName"
  ).reduce((acc: ActivityFilter[], group) => {
    const newGroup: ActivityFilter = {
      ...group,
      values: group.values.filter(value => !selectedIds.includes(value.id)),
    };
    group.values.forEach(value => selectedIds.push(value.id));
    acc.push(newGroup);
    return acc;
  }, []);

  return normalizedTasksList;
};
