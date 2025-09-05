import type { MapLocation } from "@/types/project/Location";
import type { WithLoadingStateProps } from "@/container/projectSummaryView/locationDetails/withLoadingState";
import LocationList from "@/components/map/locationList/LocationList";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { LocationCardSkeleton } from "@/components/layout/locationCard/skeleton/LocationCardSkeleton";
import { withLoadingState } from "@/container/projectSummaryView/locationDetails/withLoadingState";

type LocationProps = WithLoadingStateProps<MapLocation>;

function LocationCardsList({
  elements,
  onElementClick,
}: LocationProps): JSX.Element {
  return (
    <LocationList locations={elements} locationCardClick={onElementClick} />
  );
}

export const LocationCards = withLoadingState<MapLocation, LocationProps>(
  LocationCardsList,
  {
    Empty: function Empty() {
      const { location } = useTenantStore(state => state.getAllEntities());
      return (
        <div className="text-tiny p-8 text-center bg-brand-gray-10 h-full">
          <p>{`There are no ${location.labelPlural.toLowerCase()} based on the map extent, search and filters you've set.`}</p>
        </div>
      );
    },
    Container: function Container({ children }) {
      return <>{children}</>;
    },
    Loading: function Loading() {
      return (
        <ul>
          {Array.from({ length: 10 }, (_, index) => (
            <li
              className="border-t border-brand-gray-20 first:border-t-0 last:border-b-0 p-2"
              key={index}
            >
              <LocationCardSkeleton />
            </li>
          ))}
        </ul>
      );
    },
  }
);
