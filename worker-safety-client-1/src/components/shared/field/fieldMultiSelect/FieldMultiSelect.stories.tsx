import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { InputSelectOption } from "../../inputSelect/InputSelect";
import FieldMultiSelect from "./FieldMultiSelect";

const DUMMY_OPTIONS: InputSelectOption[] = [
  { id: "m_1", name: "César Teixeira" },
  { id: "m_2", name: "João Centeno" },
  { id: "m_3", name: "João Lemos" },
  { id: "m_4", name: "José Silva" },
  { id: "m_5", name: "Paulo Sousa" },
];

export default {
  title: "Silica/Field/FieldMultiSelect",
  component: FieldMultiSelect,
} as ComponentMeta<typeof FieldMultiSelect>;

const Template: ComponentStory<typeof FieldMultiSelect> = args => (
  <FieldMultiSelect {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  className: "w-72",
  label: "Project managers",
  caption: "",
  required: false,
  error: "",
  options: DUMMY_OPTIONS,
};
