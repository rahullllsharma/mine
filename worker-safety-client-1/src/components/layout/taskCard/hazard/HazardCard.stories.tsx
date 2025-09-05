import type { ComponentMeta, ComponentStory } from "@storybook/react";

import { noop } from "lodash-es";
import Switch from "@/components/switch/Switch";
import ControlCard from "../control/ControlCard";
import HazardCard from "./HazardCard";

export default {
  title: "Layout/TaskCard/HazardCard",
  component: HazardCard,
} as ComponentMeta<typeof HazardCard>;

const header = "Getting Struck by Moving Vehicles";

const TemplateCardItem: ComponentStory<typeof HazardCard> = args => (
  <HazardCard {...args}>
    <ControlCard label="Traffic control devices & a spotter" />
  </HazardCard>
);

export const withControl = TemplateCardItem.bind({});

withControl.args = {
  header,
};

const TemplateCardActionItem: ComponentStory<typeof HazardCard> = args => (
  <HazardCard {...args}>
    <ControlCard label="Traffic control devices & a spotter">
      <Switch stateOverride={true} onToggle={noop} />
    </ControlCard>
  </HazardCard>
);

export const withControlAndAction = TemplateCardActionItem.bind({});

withControlAndAction.args = {
  header: (
    <>
      <div className="flex-1">{header}</div>
      <Switch stateOverride={true} onToggle={noop} />
    </>
  ),
};
