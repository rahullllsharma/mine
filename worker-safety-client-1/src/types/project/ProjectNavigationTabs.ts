export enum ProjectNavigationTab {
  DETAILS = "DETAILS",
  LOCATIONS = "LOCATIONS",
  AUDIT = "AUDIT",
}

const ProjectNavigationTabLabel = {
  [ProjectNavigationTab.DETAILS]: "Details",
  [ProjectNavigationTab.LOCATIONS]: "Locations",
  [ProjectNavigationTab.AUDIT]: "History",
};

export const projectNavigationTabOptions = Object.freeze(
  Object.values(ProjectNavigationTab).map(state => ({
    id: state,
    name: ProjectNavigationTabLabel[state],
  }))
);
