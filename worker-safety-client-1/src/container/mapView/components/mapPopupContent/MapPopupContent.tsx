import type { LocationCardDynamicProps } from "@/hooks/useTenantFeatures";
import type { Project } from "@/types/project/Project";
import type { MapLocation } from "@/types/project/Location";

import LocationCard from "@/components/layout/locationCard/LocationCard";
import { getCardOptionalProps } from "@/components/layout/locationCard/utils";

type MapPopupContentProps = {
  onClick: (location: MapLocation) => void;
  location: MapLocation;
  displayLocationCardDynamicProps: LocationCardDynamicProps;
};

const MapPopupContent = ({
  onClick,
  location,
  displayLocationCardDynamicProps,
}: MapPopupContentProps) => {
  const { name, riskLevel, supervisor, project, activities } = location;
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
  const isCritical =
    activities?.some(data => data.isCritical === true) || false;

  return (
    <button className="text-left w-full" onClick={() => onClick(location)}>
      <LocationCard
        risk={riskLevel}
        title={name}
        description={ProjectName}
        slots={slots}
        identifier={identifier}
        isCritical={isCritical}
      />
    </button>
  );
};

export { MapPopupContent };
