import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/api/generated/types";

import { TaskCard } from "./TaskCard";

export default {
  title: "JSB/TaskCard",
  component: TaskCard,
} as ComponentMeta<typeof TaskCard>;

export const Playground: ComponentStory<typeof TaskCard> = args => (
  <TaskCard {...args} />
);

Playground.args = {
  title: "Install and tensioning anchors/guys - Rigging loads",
  risk: RiskLevel.High,
};
