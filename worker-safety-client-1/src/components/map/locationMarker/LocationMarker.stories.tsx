import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import Map from "../Map";
import LocationMarker from "./LocationMarker";

export default {
  title: "Components/Map/LocationMarker",
  component: LocationMarker,
} as ComponentMeta<typeof LocationMarker>;

const TemplateMarker: ComponentStory<typeof LocationMarker> = ({
  latitude,
  longitude,
  riskLevel,
}) => (
  <Map
    mapboxAccessToken={
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      process.env.WORKER_SAFETY_MAPBOX_ACCESS_TOKEN!
    }
  >
    <LocationMarker
      longitude={longitude}
      latitude={latitude}
      riskLevel={riskLevel}
    />
  </Map>
);

export const Playground = TemplateMarker.bind({});
Playground.args = {
  latitude: 40.703693,
  longitude: -74.052315,
  riskLevel: RiskLevel.HIGH,
};
