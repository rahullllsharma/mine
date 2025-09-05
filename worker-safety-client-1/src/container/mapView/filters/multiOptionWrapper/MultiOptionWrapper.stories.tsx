import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import MultiOptionWrapper from "./MultiOptionWrapper";

export default {
  title: "Components/Map/Filters/MultiOptionWrapper",
  component: MultiOptionWrapper,
  argTypes: { onSelect: { action: "onSelect" } },
} as ComponentMeta<typeof MultiOptionWrapper>;

const options: InputSelectOption[] = [
  { id: "m_1", name: "In progress" },
  { id: "m_2", name: "Active" },
  { id: "m_3", name: "Complete" },
  { id: "m_4", name: "Inactive" },
  { id: "m_5", name: "Pending" },
];

const Template: ComponentStory<typeof MultiOptionWrapper> = args => {
  return <MultiOptionWrapper {...args} />;
};

export const Playground = Template.bind({});
Playground.args = {
  options,
};
Playground.argTypes = {
  type: { control: false },
};

export const WithType = Template.bind({});
WithType.args = {
  options,
  type: "multiSelect",
};
