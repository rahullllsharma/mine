import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { SelectPrimaryOption } from "./SelectPrimary";
import SelectPrimary from "./SelectPrimary";

export default {
  title: "Silica/Select/SelectPrimary",
  component: SelectPrimary,
  argTypes: { onSelect: { action: "selected" } },
} as ComponentMeta<typeof SelectPrimary>;

const DUMMY_LOCATIONS: SelectPrimaryOption[] = [
  { id: 1, name: "5th Street Main Relocation" },
  { id: 2, name: "Kenney Line Construction" },
  { id: 3, name: "Location 3" },
  {
    id: 4,
    name: "Location 4",
    isDisabled: true,
    tooltip: {
      icon: "info_circle_outline",
      text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris facilisis fermentum nulla, quis ultrices metus.",
    },
  },
];

const Template: ComponentStory<typeof SelectPrimary> = args => (
  <SelectPrimary {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  options: DUMMY_LOCATIONS,
  className: "w-72",
  isInvalid: false,
  size: "default",
  placeholder: "Select an option",
};

export const WithSelectedOption = Template.bind({});
WithSelectedOption.args = {
  options: DUMMY_LOCATIONS,
  className: "w-72",
  defaultOption: DUMMY_LOCATIONS[2],
  isInvalid: false,
  size: "default",
  placeholder: "",
};
