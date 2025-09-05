import type { MapLocation } from "@/types/project/Location";

import { noop } from "lodash-es";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { MapLocationEntry } from "@/components/map/locationList/components/MapLocationEntry";

type LocationListProps = {
  locations: MapLocation[];
  locationCardClick?: (location: MapLocation) => void;
};

export default function LocationList({
  locations,
  locationCardClick = noop,
}: LocationListProps): JSX.Element {
  const {
    tenant: { name: tenantName },
  } = useTenantStore();
  const { displayLocationCardDynamicProps } = useTenantFeatures(tenantName);

  return (
    <ul className="flex flex-col bg-white h-full overflow-y-auto w-full">
      {locations.map(location =>
        MapLocationEntry(
          location,
          displayLocationCardDynamicProps,
          locationCardClick
        )
      )}
    </ul>
  );
}
