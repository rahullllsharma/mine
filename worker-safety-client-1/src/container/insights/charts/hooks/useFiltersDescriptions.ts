import type { Contractor } from "@/types/project/Contractor";
import type { LibraryDivision } from "@/types/project/LibraryDivision";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { ProjectStatusOption } from "@/types/project/ProjectStatus";
import type { FilterProject } from "../../utils";
import type { ProjectFiltersPayload } from "../../projectFilters/ProjectFilters";
import type { PortfolioFiltersPayload } from "../../portfolioFilters/PortfolioFilters";
import type { FiltersPayload } from "../types";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { InsightsTab } from "../types";

type GenericDictionary = { id: string; name: string }[];

type GetPortfolioFiltersArgs = Required<
  Pick<FiltersDescriptionsParams, "descriptions">
> & {
  filters: PortfolioFiltersPayload;
};

type GetProjectFiltersArgs = Required<
  Pick<FiltersDescriptionsParams, "descriptions">
> & {
  filters: ProjectFiltersPayload;
};

export type FiltersDescriptionsParams = {
  filters?: FiltersPayload;
  tab: InsightsTab;
  descriptions: Partial<{
    projects: FilterProject[];
    regions: LibraryRegion[];
    divisions: LibraryDivision[];
    contractors: Contractor[];
    projectStatusOptions: ProjectStatusOption;
  }>;
};

export type FiltersDescriptionsReturn = {
  [key: string]: string | number | undefined;
}[];

/** Extract ONLY the selected filters names by the selected ids. */
const extractNamesBySelectedFilters = (
  filteredIds: string[] = [],
  originals: GenericDictionary = []
) =>
  originals
    .reduce<string[]>((acc, { id, name }) => {
      if (filteredIds.includes(id)) {
        acc.push(name);
      }
      return acc;
    }, [])
    .join(", ");

/** Extract and format the filters for a PORTFOLIO-type chart */
const getPortfolioFilters = (data: GetPortfolioFiltersArgs) => {
  const {
    workPackage: {
      attributes: {
        name,
        primeContractor,
        division,
        region,
        status,
        startDate: startDateAttr,
        endDate: endDateAttr,
      },
    },
  } = useTenantStore.getState().getAllEntities();

  const {
    projectStatuses,
    projectIds,
    regionIds,
    divisionIds,
    contractorIds,
    startDate,
    endDate,
  } = data.filters;

  const { projectStatusOptions, projects, regions, divisions, contractors } =
    data.descriptions;

  const portfolioFilters = [
    [
      status.label,
      {
        filters: projectStatuses,
        descriptions: projectStatusOptions as unknown as GenericDictionary,
      },
    ],
    [
      name.labelPlural,
      {
        filters: projectIds,
        descriptions: projects,
      },
    ],
    [
      region.labelPlural,
      {
        filters: regionIds,
        descriptions: regions,
      },
    ],
    [
      division.labelPlural,
      {
        filters: divisionIds,
        descriptions: divisions,
      },
    ],
    [
      primeContractor.labelPlural,
      {
        filters: contractorIds,
        descriptions: contractors,
      },
    ],
  ] as const;

  // Loops and filters only the selected filters from a list of all available filters.
  const availableFilters = portfolioFilters.reduce<Record<string, string>>(
    (acc, [filter, { filters, descriptions }]) => {
      if (Array.isArray(filters) && filters.length > 0) {
        acc[filter] = extractNamesBySelectedFilters(filters, descriptions);
      }

      return acc;
    },
    {}
  );

  return [
    {
      [startDateAttr.label]: startDate,
      [endDateAttr.label]: endDate,
      ...availableFilters,
    },
  ];
};

/** Extract and format the filters for a PROJECT-type chart */
const getProjectFilters = ({
  descriptions,
  filters,
}: GetProjectFiltersArgs) => {
  const {
    workPackage: {
      attributes: {
        name: workPackageName,
        externalKey: workPackageNumber,
        startDate,
        endDate,
      },
    },
    location,
  } = useTenantStore.getState().getAllEntities();

  const locationsFilter: Record<string, string> = {};

  const locationsByProject = descriptions?.projects?.find(
    ({ id }) => id === filters.projectId
  );

  if (locationsByProject) {
    locationsFilter[workPackageName.label] = locationsByProject.name;

    // Include the project number
    // TODO: check if this is going to be updated with externalKey
    if (locationsByProject?.number) {
      locationsFilter[workPackageNumber.label] = locationsByProject.number;
    }

    const selectedLocations = extractNamesBySelectedFilters(
      filters.locationIds,
      locationsByProject.locations
    );

    if (selectedLocations) {
      locationsFilter[location.labelPlural] = selectedLocations;
    }
  }

  return [
    {
      [startDate.label]: filters?.startDate,
      [endDate.label]: filters?.endDate,
      ...locationsFilter,
    },
  ];
};

/** Description of the selected filters from tab to tab. */
export const useFiltersDescriptions = ({
  filters = undefined,
  tab,
  descriptions = {},
}: FiltersDescriptionsParams): FiltersDescriptionsReturn => {
  if (!filters) {
    return [];
  }

  return tab === InsightsTab.PROJECT
    ? getProjectFilters({ filters, descriptions } as GetProjectFiltersArgs)
    : getPortfolioFilters({ filters, descriptions } as GetPortfolioFiltersArgs);
};
