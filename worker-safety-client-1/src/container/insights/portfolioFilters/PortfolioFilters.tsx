import type { Contractor } from "@/types/project/Contractor";
import type { LibraryDivision } from "@/types/project/LibraryDivision";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { ProjectStatusOption } from "@/types/project/ProjectStatus";
import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import type { FilterProject } from "../utils";
import { useEffect, useReducer, useState } from "react";
import MultiSelect from "@/components/shared/inputSelect/multiSelect/MultiSelect";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { futureTimeFrameData, getTimeFrame, pastTimeFrameData } from "../utils";
import TimeFrame from "../timeFrame/TimeFrame";

export type PortfolioFiltersPayload = {
  projectIds: string[];
  projectStatuses: string[];
  startDate: string;
  endDate: string;
  regionIds: string[];
  divisionIds: string[];
  contractorIds: string[];
};

export type PortfolioFiltersProps = {
  projects: FilterProject[];
  projectStatuses: ProjectStatusOption;
  regions: LibraryRegion[];
  divisions: LibraryDivision[];
  contractors: Contractor[];
  timeFrameMode?: "past" | "future";
  onChange: (filters: PortfolioFiltersPayload) => void;
};

type FilterActionKind =
  | "PROJECTS"
  | "STATUS"
  | "REGIONS"
  | "DIVISIONS"
  | "CONTRACTORS";

type FilterAction = {
  type: FilterActionKind;
  payload: string[];
};

type FilterState = Omit<PortfolioFiltersPayload, "startDate" | "endDate">;

const defaultFilters: FilterState = {
  projectIds: [],
  projectStatuses: [],
  regionIds: [],
  divisionIds: [],
  contractorIds: [],
};

const filterReducer = (state: FilterState, action: FilterAction) => {
  switch (action.type) {
    case "PROJECTS":
      return { ...state, projectIds: action.payload };

    case "STATUS":
      return { ...state, projectStatuses: action.payload };

    case "REGIONS":
      return { ...state, regionIds: action.payload };

    case "DIVISIONS":
      return { ...state, divisionIds: action.payload };

    case "CONTRACTORS":
      return { ...state, contractorIds: action.payload };

    default:
      return defaultFilters;
  }
};

export default function PortfolioFilters({
  projects,
  projectStatuses,
  regions,
  divisions,
  contractors,
  timeFrameMode = "past",
  onChange,
}: PortfolioFiltersProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const timeFrameOptions =
    timeFrameMode === "past" ? pastTimeFrameData : futureTimeFrameData;
  const [filtersState, dispatchFilterAction] = useReducer(
    filterReducer,
    defaultFilters
  );
  const [timeFrame, setTimeFrame] = useState<string[]>(
    getTimeFrame(timeFrameOptions[0].numberOfDays)
  );

  useEffect(() => {
    const [startDate, endDate] = timeFrame;
    onChange({
      ...filtersState,
      startDate,
      endDate,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtersState, timeFrame]);

  const stateUpdatedHandler = (
    options: readonly InputSelectOption[],
    type: FilterActionKind
  ): void => {
    dispatchFilterAction({ type, payload: options.map(option => option.id) });
  };

  const timeFrameSelectedHandler = (startDate: string, endDate: string): void =>
    setTimeFrame([startDate, endDate]);

  return (
    <>
      <div className="grid grid-cols-3 xl:grid-cols-5 gap-3">
        <MultiSelect
          options={projects}
          placeholder={`All ${workPackage.labelPlural.toLowerCase()}`}
          isClearable
          onSelect={options => stateUpdatedHandler(options, "PROJECTS")}
        />

        <MultiSelect
          options={projectStatuses}
          placeholder={`All ${workPackage.attributes.status.labelPlural}`}
          isClearable
          onSelect={options => stateUpdatedHandler(options, "STATUS")}
        />
        <TimeFrame
          title=""
          options={timeFrameOptions}
          onChange={timeFrameSelectedHandler}
        />
        {workPackage.attributes.region.visible && (
          <MultiSelect
            options={regions}
            placeholder={`All ${workPackage.attributes.region.labelPlural.toLowerCase()}`}
            isClearable
            onSelect={options => stateUpdatedHandler(options, "REGIONS")}
          />
        )}
        {workPackage.attributes.division.visible && (
          <MultiSelect
            options={divisions}
            placeholder={`All ${workPackage.attributes.division.labelPlural.toLowerCase()}`}
            isClearable
            onSelect={options => stateUpdatedHandler(options, "DIVISIONS")}
          />
        )}
        <MultiSelect
          options={contractors}
          placeholder={`All ${workPackage.attributes.primeContractor.labelPlural.toLowerCase()}`}
          isClearable
          onSelect={options => stateUpdatedHandler(options, "CONTRACTORS")}
        />
      </div>
    </>
  );
}
