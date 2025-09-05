import type { ComponentMeta, ComponentStory } from "@storybook/react";
import React from "react";

import SelectCard from "./SelectCard";

const CONTROL_LIBRARY = [
  { id: "1", name: "Control 1", isApplicable: true },
  { id: "2", name: "Control 2", isApplicable: true },
  { id: "3", name: "Control 3", isApplicable: true },
];

export default {
  title: "Layout/TaskCard/SelectCard",
  component: SelectCard,
  argTypes: {
    onSelect: { action: "selected" },
    onRemove: { action: "removed" },
  },
} as ComponentMeta<typeof SelectCard>;

const TemplateCardItem: ComponentStory<typeof SelectCard> = args => (
  <SelectCard {...args} />
);

export const Playground = TemplateCardItem.bind({});
Playground.args = {
  options: CONTROL_LIBRARY,
  userInitials: "UB",
  type: "control",
  defaultOption: CONTROL_LIBRARY[1],
  isDisabled: false,
};
