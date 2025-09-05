import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { InputSelectOption } from "../InputSelect";
import MultiSelect from "./MultiSelect";

export default {
  title: "Silica/Select/MultiSelect",
  component: MultiSelect,
} as ComponentMeta<typeof MultiSelect>;

const DUMMY_OPTIONS: InputSelectOption[] = [
  { id: "m_1", name: "César Teixeira" },
  { id: "m_2", name: "João Centeno" },
  { id: "m_3", name: "João Lemos" },
  { id: "m_4", name: "José Silva" },
  { id: "m_5", name: "Paulo Sousa" },
];

const Template: ComponentStory<typeof MultiSelect> = args => (
  <MultiSelect {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  options: DUMMY_OPTIONS,
  className: "w-72",
  placeholder: "Select supervisors",
  isClearable: false,
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  options: DUMMY_OPTIONS,
  className: "w-72",
  placeholder: "Select supervisors",
  icon: "user",
};

export const WithDefaultOptions = Template.bind({});
WithDefaultOptions.args = {
  options: DUMMY_OPTIONS,
  className: "w-72",
  defaultOption: [DUMMY_OPTIONS[1], DUMMY_OPTIONS[2]],
};
