import type { ComponentMeta, ComponentStory } from "@storybook/react";
import ClusterMarker from "./ClusterMarker";

export default {
  title: "Components/Map/Cluster/ClusterMarker",
  component: ClusterMarker,
} as ComponentMeta<typeof ClusterMarker>;

const Template: ComponentStory<typeof ClusterMarker> = args => (
  <ClusterMarker {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  high: 7,
  medium: 5,
  low: 7,
  unknown: 4,
};
