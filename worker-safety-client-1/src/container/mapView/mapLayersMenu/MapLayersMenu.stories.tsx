import type { ComponentMeta, ComponentStory } from "@storybook/react";
import MapLayersMenu from "./MapLayersMenu";

export default {
  title: "Components/Map/MapLayersMenu",
  component: MapLayersMenu,
} as ComponentMeta<typeof MapLayersMenu>;

const Template: ComponentStory<typeof MapLayersMenu> = () => {
  return <MapLayersMenu />;
};

export const Playground = Template.bind({});
