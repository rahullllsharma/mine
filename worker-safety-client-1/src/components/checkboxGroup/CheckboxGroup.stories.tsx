import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { InputSelectOption } from "../shared/inputSelect/InputSelect";

import CheckboxGroup from "./CheckboxGroup";

export default {
  title: "Components/CheckboxGroup",
  component: CheckboxGroup,
  argTypes: { onSelect: { action: "onSelect" } },
} as ComponentMeta<typeof CheckboxGroup>;

const options: InputSelectOption[] = [
  { id: "m_1", name: "In progress" },
  { id: "m_2", name: "Active" },
  { id: "m_3", name: "Complete" },
];

const Template: ComponentStory<typeof CheckboxGroup> = args => (
  <CheckboxGroup {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  options,
};
