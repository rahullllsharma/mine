export enum ProjectViewTab {
  DAILY_PLAN = "plan",
  TASKS = "tasks",
}

const ProjectViewTabsLabel = {
  [ProjectViewTab.DAILY_PLAN]: "Daily Plan",
  [ProjectViewTab.TASKS]: "Tasks",
};

export const projectViewTabOptions = Object.freeze(
  Object.values(ProjectViewTab).map(state => ({
    id: state,
    name: ProjectViewTabsLabel[state],
  }))
);
