export type ControlDrillDownDatum = {
  percent: number;
  name: string;
};

export type ControlsDrillDownData = {
  byProject?: ControlDrillDownDatum[];
  byLocation?: ControlDrillDownDatum[];
  byHazard?: ControlDrillDownDatum[];
  byTask?: ControlDrillDownDatum[];
  byTaskType?: ControlDrillDownDatum[];
};

type PercentByProject = {
  percent: number;
  project: { name: string };
};

type PercentByLocation = {
  percent: number;
  location: { name: string };
};

type PercentByHazard = {
  percent: number;
  libraryHazard: { name: string };
};

type PercentByTask = {
  percent: number;
  libraryTask: { name: string; category: string };
};

export type APIControlsDrillDownData = {
  notImplementedControlsByProject?: PercentByProject[];
  notImplementedControlsByLocation?: PercentByLocation[];
  notImplementedControlsByHazard?: PercentByHazard[];
  notImplementedControlsByTask?: PercentByTask[];
  notImplementedControlsByTaskType?: PercentByTask[];
};

export function mapControlsDrillDownData({
  notImplementedControlsByProject = [],
  notImplementedControlsByLocation = [],
  notImplementedControlsByHazard = [],
  notImplementedControlsByTask = [],
  notImplementedControlsByTaskType = [],
}: APIControlsDrillDownData): ControlsDrillDownData {
  return {
    byProject: notImplementedControlsByProject.map(({ percent, project }) => ({
      percent: percent * 100,
      name: project.name,
    })),
    byLocation: notImplementedControlsByLocation.map(
      ({ percent, location }) => ({
        percent: percent * 100,
        name: location.name,
      })
    ),
    byHazard: notImplementedControlsByHazard.map(
      ({ percent, libraryHazard }) => ({
        percent: percent * 100,
        name: libraryHazard.name,
      })
    ),
    byTask: notImplementedControlsByTask.map(({ percent, libraryTask }) => ({
      percent: percent * 100,
      name: libraryTask.name,
    })),
    byTaskType: notImplementedControlsByTaskType.map(
      ({ percent, libraryTask }) => ({
        percent: percent * 100,
        name: libraryTask.category,
      })
    ),
  };
}
