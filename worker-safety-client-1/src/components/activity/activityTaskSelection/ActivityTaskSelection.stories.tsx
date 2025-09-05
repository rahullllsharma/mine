import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { CheckboxOption } from "@/components/checkboxGroup/CheckboxGroup";
import type { LibraryTask } from "@/types/task/LibraryTask";
import type { ActivityFilter } from "@/container/activity/addActivityModal/AddActivityModal";
import { useState } from "react";
import { groupBy } from "@/container/Utils";
import ActivityTaskSelection from "./ActivityTaskSelection";

const dummyElements: LibraryTask[] = [
  {
    id: "task 1",
    name: "Rebar Install",
    category: "Civil Work",
    hazards: [],
    activitiesGroups: [
      {
        id: "aa",
        name: "Civil Work group",
      },
    ],
  },
  {
    id: "task 2",
    name: "Concrete Work",
    category: "Civil Work",
    hazards: [],
    activitiesGroups: [
      {
        id: "aa",
        name: "Civil Work group",
      },
    ],
  },
  {
    id: "task3",
    name: "Clearing",
    category: "Clearing & Grading",
    hazards: [],
    activitiesGroups: [
      {
        id: "bb",
        name: "Clearing group",
      },
    ],
  },
];

const activityTasks = groupBy<LibraryTask>(dummyElements, "category");

export default {
  title: "Container/Activity/ActivityTaskSelection",
  component: ActivityTaskSelection,
} as ComponentMeta<typeof ActivityTaskSelection>;

const Template: ComponentStory<typeof ActivityTaskSelection> = () => {
  const defaultState: ActivityFilter[] = Object.keys(activityTasks).map(
    groupName => ({
      groupName,
      values: [],
    })
  );

  const [filters, setFilters] = useState(defaultState);
  const getUpdatedValues = (
    filteredValues: CheckboxOption[],
    newValue: CheckboxOption
  ) => {
    const updatedFilters: CheckboxOption[] = filteredValues;
    if (newValue.isChecked) {
      updatedFilters.push(newValue);
    } else {
      updatedFilters.splice(
        filteredValues.findIndex(item => item.id === newValue.id),
        1
      );
    }
    return updatedFilters;
  };

  const updateFilterHandler = (
    value: CheckboxOption,
    groupName: string
  ): void => {
    setFilters(prevState =>
      prevState.map(filter =>
        filter.groupName === groupName
          ? {
              groupName,
              values: [...getUpdatedValues(filter.values, value)],
            }
          : filter
      )
    );
  };

  return (
    <ActivityTaskSelection
      activityTasks={dummyElements}
      updateFilterHandler={updateFilterHandler}
      filteredTasks={filters}
    />
  );
};

export const Playground = Template.bind({});
