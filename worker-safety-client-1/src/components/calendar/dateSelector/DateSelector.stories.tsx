import type { ComponentMeta, ComponentStory } from "@storybook/react";

import DateSelector from "./DateSelector";

export default {
  title: "Components/Calendar/DateSelector",
  component: DateSelector,
  argTypes: {
    onTodayClicked: { action: "onTodayClicked" },
    onPreviousDateClicked: { action: "onPreviousDateClicked" },
    onNextDateClicked: { action: "onNextDateClicked" },
  },
} as ComponentMeta<typeof DateSelector>;

const Template: ComponentStory<typeof DateSelector> = args => (
  <DateSelector {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  date: "2021-10-06",
  isPreviousDateDisabled: false,
  isNextDateDisabled: false,
};
