import type { ComponentMeta, ComponentStory } from "@storybook/react";
import AuditCard from "./AuditCard";

export default {
  title: "Layout/AuditTrail/AuditCard",
  component: AuditCard,
  argTypes: {
    children: { control: false },
  },
} as ComponentMeta<typeof AuditCard>;

const Template: ComponentStory<typeof AuditCard> = args => (
  <AuditCard {...args} />
);

const children = (
  <>
    <span>Created the task: </span>
    <span className="text-brand-urbint-60 font-semibold">
      Loading/Unloading
    </span>
  </>
);

export const Playground = Template.bind({});
Playground.args = {
  username: "Paulo Sousa",
  userRole: "administrator",
  timestamp: "Aug 24, 2022 8:56am EST",
  location: { id: "021", name: "3rd St. between Main and Broadway" },
  children,
};
