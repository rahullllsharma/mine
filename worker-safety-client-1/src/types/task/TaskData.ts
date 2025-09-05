// TODO: Should be coming from BE - this is a provisory type definition - https://urbint.atlassian.net/browse/WS-852
export type TaskData = {
  libraryTaskId: string;
  startDate: string;
  endDate: string;
  status: string;
  hazards?: HazardData[];
};

export type HazardData = {
  id?: string;
  libraryHazardId: string;
  isApplicable: boolean;
  controls?: ControlData[];
};

type ControlData = {
  id?: string;
  libraryControlId: string;
  isApplicable: boolean;
};

export type LocationHazardControlSettings = {
  id: string;
  libraryHazardId: string;
  libraryControlId?: string;
  disabled: boolean;
};

export type LocationHazardControlSettingsData = {
  locationId: string;
  libraryHazardId: string;
  libraryControlId: string | null;
};
