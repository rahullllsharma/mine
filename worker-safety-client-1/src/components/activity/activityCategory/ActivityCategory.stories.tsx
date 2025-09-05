import type { ComponentMeta, ComponentStory } from "@storybook/react";
import ActivityCategory from "./ActivityCategory";

const activityOptions = [
  { id: "1", name: "Concrete replacement" },
  { id: "2", name: "Asphalt replacement" },
  { id: "3", name: "Soft surface" },
];

export default {
  title: "Container/Activity/ActivityCategory",
  component: ActivityCategory,
  decorators: [
    Story => (
      <div className="w-full md:w-[400px] h-[400px]">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof ActivityCategory>;

const Template: ComponentStory<typeof ActivityCategory> = args => (
  <ActivityCategory {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  title: "Site Restoration",
  options: activityOptions,
};
