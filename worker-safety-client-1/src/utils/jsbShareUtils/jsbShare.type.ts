import type { JobSafetyBriefing } from "@/types/natgrid/jobsafetyBriefing";

export type Status =
  | "default"
  | "current"
  | "saved"
  | "saved_current"
  | "error";

export type PageListItemType = {
  label: string;
  status: Status;
  id: number;
};

export type PageListComponentType = {
  listItems: PageListItemType[];
  onSelectOfPage: (page: PageListItemType) => void;
  activePage: number;
  rawStatus?: string;
};

export type HazardsLibraryType = {
  id: string;
  imageUrl: string;
};

export type JSBSharePageDetailsType = {
  data: JobSafetyBriefing;
  hazardsLibrary: HazardsLibraryType[];
  createdAt: string;
  onUpdate: () => void;
};

export type SharePageSiteConditionDetailsType = {
  id: string;
  selected: boolean;
  name: string;
  recommended: boolean;
};
