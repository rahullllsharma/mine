import type { ComponentMeta, ComponentStory } from "@storybook/react";
import Map from "./Map";

export default {
  title: "Components/Map",
  component: Map,
} as ComponentMeta<typeof Map>;

/**
 * Heads up, don't pass all args back to the component as it could lead to unexpected results.
 */
const TemplateMap: ComponentStory<typeof Map> = ({
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  mapboxAccessToken = process.env.WORKER_SAFETY_MAPBOX_ACCESS_TOKEN!,
  hasZoom,
  mapStyle,
  className,
}) => (
  <section>
    <h4>How to use the Map component?</h4>
    <p>
      The <b>parent</b> component should be responsible to define the size of
      the map.
    </p>
    <p>By default, the map will stretch horizontally and vertically.</p>
    <Map
      mapboxAccessToken={mapboxAccessToken}
      className={className}
      hasZoom={hasZoom}
      mapStyle={mapStyle}
    />
  </section>
);

export const Playground = TemplateMap.bind({});
Playground.args = {};

export const WithCustomSize = TemplateMap.bind({});
WithCustomSize.args = {
  className: "w-[330px] h-[150px]",
};

export const WithNavigationControls = TemplateMap.bind({});
WithNavigationControls.args = {
  hasZoom: true,
};

export const WithStyles = TemplateMap.bind({});
WithStyles.args = {
  mapStyle: "SATELLITE_STREETS",
};
