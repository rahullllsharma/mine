import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { LocationCardSkeleton } from "./LocationCardSkeleton";

export default {
  title: "Layout/LocationCardSkeleton",
  component: LocationCardSkeleton,
} as ComponentMeta<typeof LocationCardSkeleton>;

const Template: ComponentStory<typeof LocationCardSkeleton> = () => (
  <LocationCardSkeleton />
);

export const Playground = Template.bind({});
