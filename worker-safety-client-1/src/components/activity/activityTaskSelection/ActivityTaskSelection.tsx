import type { CheckboxOption } from "@/components/checkboxGroup/CheckboxGroup";
import type { ChangeEvent } from "react";
import type { LibraryTask } from "@/types/task/LibraryTask";
import type { ActivityFilter } from "@/container/activity/addActivityModal/AddActivityModal";
import { useRef, useState, useEffect, useMemo } from "react";
import { debounce, isEmpty } from "lodash-es";
import { groupByAliasesOrName } from "@/container/Utils";
import Input from "@/components/shared/input/Input";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import ActivityCategory from "../activityCategory/ActivityCategory";

type ActivityTaskSelectionProps = {
  activityTasks: LibraryTask[];
  filteredTasks: ActivityFilter[];
  updateFilterHandler: (value: CheckboxOption, groupName: string) => void;
  isEditing?: boolean;
};

export default function ActivityTaskSelection({
  activityTasks,
  filteredTasks,
  updateFilterHandler,
  isEditing = false,
}: ActivityTaskSelectionProps): JSX.Element {
  const { task, activity } = useTenantStore(state => state.getAllEntities());

  // Group by aliases or name and sort tasks alphabetically within each category
  const tasksByCategory = useMemo(() => {
    const grouped = groupByAliasesOrName<LibraryTask>(activityTasks);

    // Sort tasks alphabetically within each category
    const sortedGrouped: Record<string, LibraryTask[]> = {};
    Object.keys(grouped).forEach(category => {
      sortedGrouped[category] = grouped[category].sort((a, b) =>
        a.name.localeCompare(b.name)
      );
    });

    return sortedGrouped;
  }, [activityTasks]);

  const [activityCategoryList, setActivityCategoryList] =
    useState(tasksByCategory);

  useEffect(() => {
    setActivityCategoryList(tasksByCategory);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activityTasks]);

  const searchRef = useRef<HTMLInputElement>(null);
  const searchValue = searchRef.current?.value || "";

  const getCategoryValues = (groupName: string) => {
    const activityCategory = filteredTasks?.find(
      filter => filter.groupName === groupName
    ) as ActivityFilter;
    return activityCategory?.values;
  };

  const shouldExpandCategory = (groupName: string) => {
    const categoryValues = getCategoryValues(groupName);
    return (
      !!searchValue ||
      (isEditing && categoryValues && categoryValues.length > 0)
    );
  };

  const categorySearchHandler = debounce((e: ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value.toLowerCase();
    const list = Object.entries(tasksByCategory);

    const matchByCategory = list.filter(([key]) =>
      key.toLowerCase().includes(input)
    );
    const matchByTask = list
      .filter(
        ([key, value]) =>
          !key.toLowerCase().includes(input) &&
          value.find(item => item.name.toLowerCase().includes(input))
      )
      .map(([key, value]) => [
        key,
        value.filter(item => item.name.toLowerCase().includes(input)),
      ]);

    setActivityCategoryList(
      Object.fromEntries([...matchByCategory, ...matchByTask])
    );
  }, 250);

  return (
    <div className="flex flex-col gap-4">
      <header>
        <h5 className="mb-2 text-tiny">
          {`Search and select a ${task.label.toLowerCase()} from the list below`}
        </h5>
        <Input
          placeholder={`Search by ${task.label.toLowerCase()} or ${activity.label.toLowerCase()} group`}
          icon="search"
          onChange={categorySearchHandler}
          ref={searchRef}
        />
      </header>
      <section className="border border-brand-gray-40 rounded py-5 px-2">
        {/* For reference: https://beta.reactjs.org/learn/you-might-not-need-an-effect#resetting-all-state-when-a-prop-changes */}
        {/* We use this Fragment to force a re-render when the search text changes in order to expand the Accordion */}
        <div className="h-72 overflow-y-scroll" key={searchValue}>
          {isEmpty(activityCategoryList) ? (
            <p className="p-3 text-tiny">No results found</p>
          ) : (
            Object.keys(activityCategoryList)
              .sort()
              .map(groupName => (
                <ActivityCategory
                  key={activityCategoryList[groupName][0].id}
                  title={groupName}
                  onItemChange={value => updateFilterHandler(value, groupName)}
                  options={activityCategoryList[groupName]}
                  value={getCategoryValues(groupName)}
                  isExpanded={shouldExpandCategory(groupName)}
                />
              ))
          )}
        </div>
      </section>
    </div>
  );
}
