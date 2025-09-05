import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import type { FilterLocations, FilterProject } from "../utils";
import { useEffect, useState } from "react";
import MultiSelect from "@/components/shared/inputSelect/multiSelect/MultiSelect";
import SearchSelect from "@/components/shared/inputSelect/searchSelect/SearchSelect";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { getTimeFrame, futureTimeFrameData, pastTimeFrameData } from "../utils";
import TimeFrame from "../timeFrame/TimeFrame";

export type ProjectFiltersPayload = {
  projectId: string;
  locationIds: string[];
  startDate: string;
  endDate: string;
};

type ProjectFiltersProps = {
  projects: FilterProject[];
  timeFrameMode?: "past" | "future";
  onChange: (filters: ProjectFiltersPayload) => void;
};

export default function ProjectFilters({
  projects,
  timeFrameMode = "past",
  onChange,
}: ProjectFiltersProps): JSX.Element {
  const { location: locationEntity } = useTenantStore(state =>
    state.getAllEntities()
  );
  const [locationOptions, setLocationsOptions] = useState<FilterLocations>(
    projects[0]?.locations || []
  );
  const timeFrameOptions =
    timeFrameMode === "past" ? pastTimeFrameData : futureTimeFrameData;

  const [project, setProject] = useState<InputSelectOption>(projects[0]);
  const [locations, setLocations] = useState<InputSelectOption[] | null>([]);
  const [timeFrame, setTimeFrame] = useState<string[]>(
    getTimeFrame(timeFrameOptions[0].numberOfDays)
  );

  useEffect(() => {
    const [startDate, endDate] = timeFrame;
    onChange({
      projectId: project?.id || "",
      locationIds: locations?.map(location => location.id) || [],
      startDate,
      endDate,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [project, locations, timeFrame]);

  const projectSelectedHandler = (option: InputSelectOption): void => {
    setProject(option);
    const selectedProject = projects.find(
      proj => option.id === proj.id
    ) as FilterProject;
    setLocationsOptions(selectedProject.locations);
    setLocations(null);
  };

  const locationsSelectedHandler = (
    options: readonly InputSelectOption[]
  ): void => {
    setLocations(options as InputSelectOption[]);
  };

  const timeFrameSelectedHandler = (startDate: string, endDate: string): void =>
    setTimeFrame([startDate, endDate]);

  return (
    <>
      <div className="grid grid-cols-3 xl:grid-cols-5 gap-3">
        <SearchSelect
          options={projects}
          value={project}
          defaultOption={projects[0]}
          onSelect={projectSelectedHandler}
        />
        <MultiSelect
          options={locationOptions}
          placeholder={`All ${locationEntity.labelPlural.toLowerCase()}`}
          value={locations}
          isClearable
          onSelect={locationsSelectedHandler}
        />
        <TimeFrame
          title=""
          options={timeFrameOptions}
          onChange={timeFrameSelectedHandler}
        />
      </div>
    </>
  );
}
