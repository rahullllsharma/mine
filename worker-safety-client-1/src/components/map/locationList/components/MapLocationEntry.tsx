import type { Project } from "@/types/project/Project";
import type { LocationCardDynamicProps } from "@/hooks/useTenantFeatures";
import type { MapLocation } from "@/types/project/Location";

import LocationCard from "@/components/layout/locationCard/LocationCard";
import { getCardOptionalProps } from "@/components/layout/locationCard/utils";

function MapLocationEntry(
  location: MapLocation,
  displayLocationCardDynamicProps: LocationCardDynamicProps,
  locationCardClick?: (location: MapLocation) => void
) {
  const { id, riskLevel, name, supervisor, project, activities } =
    location as MapLocation;
  const {
    name: ProjectName,
    libraryProjectType,
    libraryDivision,
    libraryRegion,
  } = project as Project;

  const { slots, identifier } = getCardOptionalProps({
    workPackageType: libraryProjectType?.name,
    division: libraryDivision?.name,
    region: libraryRegion?.name,
    primaryAssignedPersonLocation: supervisor?.name,
    activities,
    displayLocationCardDynamicProps,
  });

  return (
    <li
      key={id}
      className="border-t border-brand-gray-20 first:border-t-0 last:border-b-0"
    >
      <button
        className="p-2 text-left w-full"
        onClick={() => locationCardClick?.(location)}
      >
        <LocationCard
          risk={riskLevel}
          title={name}
          description={ProjectName}
          slots={slots}
          identifier={identifier}
          isCritical={
            activities?.some(data => data.isCritical === true) || false
          }
        />
      </button>
    </li>
  );
}

export { MapLocationEntry };
