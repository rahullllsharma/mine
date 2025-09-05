import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { AuditCardLoader } from "./AuditCardLoader";

export default {
  title: "Layout/AuditTrail/AuditCardLoader",
  component: AuditCardLoader,
} as ComponentMeta<typeof AuditCardLoader>;

const Template: ComponentStory<typeof AuditCardLoader> = () => (
  <AuditCardLoader />
);

export const Playground = Template.bind({});
Playground.args = {};
