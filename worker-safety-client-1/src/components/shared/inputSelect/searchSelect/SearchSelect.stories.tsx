import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { InputSelectOption } from "../InputSelect";
import SearchSelect from "./SearchSelect";

export default {
  title: "Silica/Select/SearchSelect",
  component: SearchSelect,
} as ComponentMeta<typeof SearchSelect>;

const DUMMY_TASKS: InputSelectOption[] = [
  { id: "task_1", name: "Cable tray and support install" },
  { id: "task_2", name: "Clearing and grading" },
  { id: "task_3", name: "Control line installation" },
  { id: "task_4", name: "Excavation of soil using hydro-vac" },
  { id: "task_5", name: "Clearing" },
];

const Template: ComponentStory<typeof SearchSelect> = args => (
  <SearchSelect {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  options: DUMMY_TASKS,
  className: "w-72",
  placeholder: "Select options",
  isInvalid: false,
  isClearable: false,
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  options: DUMMY_TASKS,
  className: "w-72",
  placeholder: "Select options",
  isInvalid: false,
  icon: "user",
};

export const WithDefaultOption = Template.bind({});
WithDefaultOption.args = {
  options: DUMMY_TASKS,
  className: "w-72",
  placeholder: "",
  defaultOption: DUMMY_TASKS[1],
  isInvalid: false,
};
