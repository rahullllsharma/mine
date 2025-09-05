import type { Dictionary } from "lodash";
import type { Hazard } from "../types/project/Hazard";
import { groupBy as lodashGroupBy } from "lodash-es";

export const countTotalControls = (hazard: Hazard[]): number =>
  hazard.reduce((acc, hazardItem) => acc + hazardItem.controls.length, 0);

/**
 * Creates an object indexed by the value matching the identity
 *
 * Key might be undefined if there is no identity found in the collection
 *
 * e.g.:
 * ```ts
 * groupBy(
 *  [
 *    { a: "aaaa", b: "bbbb", c: { d: "identityKey" } },
 *    { a: "aaaa", b: "bbbb", c: { d: "identityKey" } },
 *    { a: "aaaa", b: "bbbb", c: { d: "identityKeyOther" } },
 *  ],
 *  "c.d"
 *  )
 * ```
 *
 * Result
 * ```ts
 *   {
 *    identityKey: [
 *      { a: 'aaaa', b: 'bbbb', c: [Object] },
 *      { a: 'aaaa', b: 'bbbb', c: [Object] }
 *    ],
 *    identityKeyOther: [ { a: 'aaaa', b: 'bbbb', c: [Object] } ]
 *  }
 * ```
 *
 * @param elements
 * @param identity
 * @returns
 */
export function groupBy<T>(
  elements: T[],
  identity: string
): Dictionary<[T, ...T[]]> {
  return lodashGroupBy<T>(elements, identity);
}

/**
 * Groups items by aliases or group names in a simple, readable way.
 * Tasks are deduplicated within each group based on their base task ID.
 *
 * @param elements Array of items to group
 * @returns Object with alias or name as keys and arrays of items as values
 */
export function groupByAliasesOrName<
  T extends {
    id: string;
    activitiesGroups?: { id?: string; name?: string; aliases?: string[] }[];
  }
>(elements: T[]): Record<string, T[]> {
  const grouped: Record<string, T[]> = {};

  // Helper to extract base task ID (removes any suffix after double underscore)
  const getBaseTaskId = (taskId: string): string => {
    if (!taskId.includes("__")) return taskId;
    const parts = taskId.split("__");
    return parts.length >= 3 ? parts[1] : parts[0];
  };

  // Helper to get valid aliases or fallback to group name
  const getGroupKeys = (group: {
    id?: string;
    name?: string;
    aliases?: string[];
  }): string[] => {
    const validAliases = (group.aliases || [])
      .map(alias => alias?.trim())
      .filter(Boolean);

    // Always include valid aliases
    const keys = [...validAliases];

    // If we have no valid aliases OR if we have some invalid aliases, also include group name
    const hasInvalidAliases = (group.aliases || []).some(
      alias => !alias?.trim()
    );
    if (validAliases.length === 0 || hasInvalidAliases) {
      const groupName = group.name?.trim();
      if (groupName) {
        keys.push(groupName);
      }
    }

    return keys;
  };

  // Process each element and group by aliases/names
  elements.forEach(item => {
    const baseTaskId = getBaseTaskId(item.id);

    (item.activitiesGroups || []).forEach(group => {
      const groupKeys = getGroupKeys(group);

      groupKeys.forEach(key => {
        if (!key) return;

        // Initialize group if it doesn't exist
        if (!grouped[key]) {
          grouped[key] = [];
        }

        // Check if this task already exists in this group
        const existingTaskIndex = grouped[key].findIndex(
          existingItem => getBaseTaskId(existingItem.id) === baseTaskId
        );

        if (existingTaskIndex === -1) {
          // Add new task to group
          grouped[key].push({ ...item, activitiesGroups: [group] });
        } else {
          // Merge activity groups for existing task
          const existingTask = grouped[key][existingTaskIndex];
          const currentGroupId = group.id;
          const existingGroupIds =
            existingTask.activitiesGroups?.map(g => g.id) || [];

          if (currentGroupId && !existingGroupIds.includes(currentGroupId)) {
            grouped[key][existingTaskIndex] = {
              ...existingTask,
              activitiesGroups: [
                ...(existingTask.activitiesGroups || []),
                group,
              ],
            };
          }
        }
      });
    });
  });

  return grouped;
}
