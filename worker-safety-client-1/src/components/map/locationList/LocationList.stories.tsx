import type { ComponentMeta, ComponentStory } from "@storybook/react";
import LocationList from "./LocationList";
import { mockLocations } from "./mock/mockLocations";

export default {
  title: "Components/Map/LocationList",
  component: LocationList,
} as ComponentMeta<typeof LocationList>;
const Template: ComponentStory<typeof LocationList> = args => (
  <LocationList {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  locations: mockLocations,
};
