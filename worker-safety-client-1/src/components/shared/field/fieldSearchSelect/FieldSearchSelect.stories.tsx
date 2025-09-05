import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { InputSelectOption } from "../../inputSelect/InputSelect";
import FieldSearchSelect from "./FieldSearchSelect";

const DUMMY_TASKS: InputSelectOption[] = [
  { id: "task_1", name: "Cable tray and support install" },
  { id: "task_2", name: "Clearing and grading" },
  { id: "task_3", name: "Control line installation" },
  { id: "task_4", name: "Excavation of soil using hydro-vac" },
];

export default {
  title: "Silica/Field/FieldSearchSelect",
  component: FieldSearchSelect,
} as ComponentMeta<typeof FieldSearchSelect>;

const Template: ComponentStory<typeof FieldSearchSelect> = args => (
  <FieldSearchSelect {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  className: "w-72",
  label: "some label",
  caption: "",
  required: false,
  error: "",
  options: DUMMY_TASKS,
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  className: "w-72",
  label: "some label",
  caption: "",
  required: false,
  error: "",
  options: DUMMY_TASKS,
  icon: "user",
};

export const Readonly = Template.bind({});
Readonly.args = {
  className: "w-72",
  label: "some label",
  caption: "",
  required: false,
  error: "",
  options: DUMMY_TASKS,
  readOnly: true,
  defaultOption: DUMMY_TASKS[1],
};
