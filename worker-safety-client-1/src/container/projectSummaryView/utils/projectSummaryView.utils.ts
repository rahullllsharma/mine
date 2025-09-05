import type { RouterLink } from "@/types/Generic";
import type { Location } from "@/types/project/Location";
import { useRouter } from "next/router";
import {
  ProjectViewTab,
  projectViewTabOptions,
} from "@/types/project/ProjectViewTabs";
import { getUpdatedRouterQuery } from "@/utils/router";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

type ProjectViewTabOption = { id: ProjectViewTab; name: string };
type BreadcrumbData = {
  title: string;
  link: string;
};

const projectViewTabOptionsValues = Object.values(projectViewTabOptions);
const projectViewTabValues = Object.values(ProjectViewTab);

const getProjectViewTab = (id: ProjectViewTab): ProjectViewTabOption => {
  const tabOption = projectViewTabOptions.find(option => option.id === id) as {
    id: ProjectViewTab;
    name: string;
  };

  return {
    ...tabOption,
    name:
      id === ProjectViewTab.TASKS
        ? useTenantStore.getState().getAllEntities().task.labelPlural
        : tabOption.name,
  };
};

const getProjectTabIndex = (
  viewTab: ProjectViewTab = ProjectViewTab.DAILY_PLAN
): number => {
  let tab = 0;

  if (viewTab) {
    const index = projectViewTabValues.findIndex(option => option === viewTab);
    if (index !== -1) {
      tab = index;
    }
  }

  return tab;
};

const getProjectSourceById = (id: number): string => {
  return projectViewTabOptionsValues[id].id;
};

function useGetProjectUrl(projectId: string): RouterLink {
  const { locationId, activeTab, source } = useRouter().query;

  return {
    pathname: "/projects/[id]",
    query: getUpdatedRouterQuery(
      { id: projectId, location: locationId, activeTab },
      { key: "source", value: source }
    ),
  };
}

const getBreadcrumbDetails = (
  workPackageLabel: string,
  source?: string
): BreadcrumbData => {
  const isSourceMap = source === "map";
  return {
    title: isSourceMap ? "Map" : `${workPackageLabel}`,
    link: isSourceMap ? "/map" : "/projects",
  };
};

const getLocationById = (locations: Location[], locationId?: string) => {
  const location = locations.find(({ id }) => id === locationId);
  return location ?? locations[0];
};

export {
  getProjectViewTab,
  getProjectTabIndex,
  getProjectSourceById,
  useGetProjectUrl,
  getBreadcrumbDetails,
  getLocationById,
};
