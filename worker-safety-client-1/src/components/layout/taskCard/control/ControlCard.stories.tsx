import type { ComponentMeta, ComponentStory } from "@storybook/react";
import React from "react";
import { noop } from "lodash-es";
import Switch from "@/components/switch/Switch";
import ControlCard from "./ControlCard";

export default {
  title: "Layout/TaskCard/ControlCard",
  component: ControlCard,
} as ComponentMeta<typeof ControlCard>;

const TemplateCardItem: ComponentStory<typeof ControlCard> = args => (
  <ControlCard {...args} />
);

export const Playground = TemplateCardItem.bind({});

Playground.args = {
  label: "Situational Jobsite Awareness",
};

const TemplateCardItemWithAction: ComponentStory<typeof ControlCard> = args => (
  <ControlCard {...args}>
    <Switch stateOverride={true} onToggle={noop} />
  </ControlCard>
);

export const withSwitch = TemplateCardItemWithAction.bind({});

withSwitch.args = {
  label: "Situational Jobsite Awareness",
};

const TemplateCardItemWithActionDisabled: ComponentStory<typeof ControlCard> =
  args => (
    <ControlCard {...args}>
      <Switch isDisabled={true} stateOverride={true} onToggle={noop} />
    </ControlCard>
  );
export const withSwitchDisabled = TemplateCardItemWithActionDisabled.bind({});

withSwitchDisabled.args = {
  label: "Situational Jobsite Awareness",
};
