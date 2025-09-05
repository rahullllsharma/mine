import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { noop } from "lodash-es";
import LocationCard from "@/components/layout/locationCard/LocationCard";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import Map from "../Map";

import MapPopup from "./MapPopup";

export default {
  title: "Components/Map/MapPopup",
  component: MapPopup,
} as ComponentMeta<typeof MapPopup>;

const TemplateMarkerLocationCard: ComponentStory<typeof MapPopup> = ({
  latitude,
  longitude,
}) => (
  <Map
    mapboxAccessToken={
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      process.env.WORKER_SAFETY_MAPBOX_ACCESS_TOKEN!
    }
  >
    <MapPopup longitude={longitude} latitude={latitude} onClose={noop}>
      <LocationCard
        risk={RiskLevel.HIGH}
        title={"Manhattan"}
        description={"Evergreen"}
        slots={["Homer J."]}
        identifier={"Distribution"}
      />
    </MapPopup>
  </Map>
);

export const withLocationCard = TemplateMarkerLocationCard.bind({});
withLocationCard.args = {
  latitude: 40.703693,
  longitude: -74.052315,
};
