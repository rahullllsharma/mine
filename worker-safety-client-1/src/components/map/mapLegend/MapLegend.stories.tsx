import type { ComponentMeta, ComponentStory } from "@storybook/react";
import MapLegend from "./MapLegend";

export default {
  title: "Components/Map/MapLegend",
  component: MapLegend,
} as ComponentMeta<typeof MapLegend>;

const Template: ComponentStory<typeof MapLegend> = args => (
  <MapLegend {...args}>
    <p>hello, you can use this as you like</p>
  </MapLegend>
);

export const Playground = Template.bind({});
Playground.args = {
  header: "map legend title",
};
