import type { LibraryDivision } from "@/types/project/LibraryDivision";
import type { LibraryProjectType } from "@/types/project/LibraryProjectType";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { User } from "@/types/User";
import type { Contractor } from "@/types/project/Contractor";
import type { MultiOption } from "../multiOptionWrapper/MultiOptionWrapper";
import { useEffect, useState } from "react";
import MultiSelect from "@/components/shared/inputSelect/multiSelect/MultiSelect";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { sentenceCap } from "@/utils/risk";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { projectStatusOptions } from "@/types/project/ProjectStatus";
import Flyover from "@/components/flyover/Flyover";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import { useMapContext } from "../../context/MapProvider";
import MultiOptionWrapper from "../multiOptionWrapper/MultiOptionWrapper";
import MapFilterSection from "./mapFilterSection/MapFilterSection";

type MapFiltersProps = {
  projectTypesLibrary: LibraryProjectType[];
  divisionsLibrary: LibraryDivision[];
  regionsLibrary: LibraryRegion[];
  supervisors: User[];
  contractors: Contractor[];
  isOpen: boolean;
  onClose: () => void;
};

export type FilterField =
  | "RISK"
  | "REGIONS"
  | "DIVISIONS"
  | "TYPES"
  | "PROJECT"
  | "CONTRACTOR"
  | "SUPERVISOR"
  | "PROJECT_STATUS";

export type LocationFilter = {
  field: FilterField;
  values: MultiOption[];
};

const riskLevels = [
  RiskLevel.HIGH,
  RiskLevel.MEDIUM,
  RiskLevel.LOW,
  RiskLevel.UNKNOWN,
];

export const getRiskLevelOptions = riskLevels.map(level => ({
  id: level,
  name: sentenceCap(`${level} risk`),
}));

const defaultState: LocationFilter[] = [
  { field: "RISK", values: [] },
  { field: "TYPES", values: [] },
  { field: "DIVISIONS", values: [] },
  { field: "REGIONS", values: [] },
  { field: "PROJECT", values: [] },
  { field: "CONTRACTOR", values: [] },
  { field: "SUPERVISOR", values: [] },
  { field: "PROJECT_STATUS", values: [] },
];

export default function MapFilters({
  projectTypesLibrary,
  divisionsLibrary,
  regionsLibrary,
  supervisors,
  contractors,
  isOpen,
  onClose,
}: MapFiltersProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const { filters: activeFilters, setFilters } = useMapContext();
  const [locationFilters, setLocationFilters] =
    useState<LocationFilter[]>(activeFilters);
  const statusOptions = projectStatusOptions().map(({ id, name }) => ({
    id: id.toLowerCase(),
    name,
  }));
  useEffect(() => {
    setLocationFilters(activeFilters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  const applyFiltersHandler = () => {
    setFilters([...locationFilters]);
  };

  const clearFiltersHandler = () => {
    setLocationFilters(defaultState);
  };

  const areFiltersSelected =
    locationFilters.some(filter => filter.values.length > 0) ||
    activeFilters.some(filter => filter.values.length > 0);

  const getFilterField = (field: FilterField) => {
    const fieldValue = locationFilters.find(
      filter => filter.field === field
    ) as LocationFilter;

    return fieldValue?.values;
  };

  const getFilterCount = (field: FilterField): number | undefined =>
    locationFilters.find(filter => filter.field === field)?.values.length;

  const filterUpdateHandler = (
    values: MultiOption[],
    field: FilterField
  ): void => {
    setLocationFilters(prevState =>
      prevState.map(filter =>
        filter.field === field ? { field, values } : filter
      )
    );
  };

  const filtersFooter = (
    <div className="flex justify-end gap-4 px-6 py-3">
      <ButtonTertiary label="Cancel" onClick={onClose} />
      <ButtonPrimary
        label="Apply"
        onClick={applyFiltersHandler}
        disabled={!areFiltersSelected}
      />
    </div>
  );

  const reorderFieldValues = (values: MultiOption[]) => {
    // This functions makes sure that if the fieldValues contains a value labelled
    // "Other", it should be the last option in the list.
    // Refer: https://urbint.atlassian.net/browse/WORK-2737
    const otherArray: MultiOption[] = [];
    const nonOtherArray: MultiOption[] = [];

    for (const option of values) {
      if (option.name.toLowerCase() === "other") {
        otherArray.push(option);
      } else {
        nonOtherArray.push(option);
      }
    }

    return [...nonOtherArray, ...otherArray];
  };

  return (
    <Flyover
      isOpen={isOpen}
      title="Filters"
      unmount
      onClose={onClose}
      footer={filtersFooter}
    >
      <>
        {/* TODO This button should be replaced with a Text or Label button but there is still no reference for that in HHV2 */}
        <button
          className="font-semibold px-3 mb-3 text-brand-urbint-50 active:text-brand-urbint-60 hover:text-brand-urbint-40"
          onClick={clearFiltersHandler}
        >
          Clear all
        </button>
        <MapFilterSection title="Risk Level" count={getFilterCount("RISK")}>
          <MultiOptionWrapper
            options={getRiskLevelOptions}
            value={getFilterField("RISK")}
            onSelect={options => filterUpdateHandler(options, "RISK")}
          />
        </MapFilterSection>
        {workPackage.attributes.workPackageType.visible && (
          <MapFilterSection
            title={workPackage.attributes.workPackageType.label}
            count={getFilterCount("TYPES")}
          >
            <MultiSelect
              options={reorderFieldValues(projectTypesLibrary)}
              value={getFilterField("TYPES")}
              onSelect={options =>
                filterUpdateHandler(options as MultiOption[], "TYPES")
              }
              isSearchable
            />
          </MapFilterSection>
        )}
        {workPackage.attributes.division.visible && (
          <MapFilterSection
            title={workPackage.attributes.division.label}
            count={getFilterCount("DIVISIONS")}
          >
            <MultiSelect
              options={divisionsLibrary}
              value={getFilterField("DIVISIONS")}
              onSelect={options =>
                filterUpdateHandler(options as MultiOption[], "DIVISIONS")
              }
              isSearchable
            />
          </MapFilterSection>
        )}
        {workPackage.attributes.region.visible && (
          <MapFilterSection
            title={workPackage.attributes.region.label}
            count={getFilterCount("REGIONS")}
          >
            <MultiSelect
              options={regionsLibrary}
              value={getFilterField("REGIONS")}
              onSelect={options =>
                filterUpdateHandler(options as MultiOption[], "REGIONS")
              }
              isSearchable
            />
          </MapFilterSection>
        )}
        {workPackage.attributes.primaryAssignedPerson.visible && (
          <MapFilterSection
            title="Supervisors"
            count={getFilterCount("SUPERVISOR")}
          >
            <MultiSelect
              options={supervisors}
              value={getFilterField("SUPERVISOR")}
              onSelect={options =>
                filterUpdateHandler(options as MultiOption[], "SUPERVISOR")
              }
              isSearchable
            />
          </MapFilterSection>
        )}
        {workPackage.attributes.primeContractor.visible && (
          <MapFilterSection
            title={workPackage.attributes.primeContractor.labelPlural}
            count={getFilterCount("CONTRACTOR")}
          >
            <MultiSelect
              options={contractors}
              value={getFilterField("CONTRACTOR")}
              onSelect={options =>
                filterUpdateHandler(options as MultiOption[], "CONTRACTOR")
              }
              isSearchable
            />
          </MapFilterSection>
        )}
        {workPackage.attributes.status.visible && (
          <MapFilterSection
            title={workPackage.attributes.status.label}
            count={getFilterCount("PROJECT_STATUS")}
          >
            <MultiOptionWrapper
              options={statusOptions}
              value={getFilterField("PROJECT_STATUS")}
              onSelect={options =>
                filterUpdateHandler(options, "PROJECT_STATUS")
              }
            />
          </MapFilterSection>
        )}
      </>
    </Flyover>
  );
}
