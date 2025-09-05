export type HazardDrillDownDatum = {
  count: number;
  name: string;
};

export type HazardsDrillDownData = {
  byProject?: HazardDrillDownDatum[];
  byLocation?: HazardDrillDownDatum[];
  bySiteCondition?: HazardDrillDownDatum[];
  byTask?: HazardDrillDownDatum[];
  byTaskType?: HazardDrillDownDatum[];
};

type CountByProject = {
  count: number;
  project: { name: string };
};

type CountByLocation = {
  count: number;
  location: { name: string };
};

type CountBySiteCondition = {
  count: number;
  librarySiteCondition: { name: string };
};

type CountByTask = {
  count: number;
  libraryTask: { name: string; category: string };
};

export type APIHazardsDrillDownData = {
  applicableHazardsByProject?: CountByProject[];
  applicableHazardsByLocation?: CountByLocation[];
  applicableHazardsBySiteCondition?: CountBySiteCondition[];
  applicableHazardsByTask?: CountByTask[];
  applicableHazardsByTaskType?: CountByTask[];
};

export function mapHazardsDrillDownData({
  applicableHazardsByProject = [],
  applicableHazardsByLocation = [],
  applicableHazardsBySiteCondition = [],
  applicableHazardsByTask = [],
  applicableHazardsByTaskType = [],
}: APIHazardsDrillDownData): HazardsDrillDownData {
  return {
    byProject: applicableHazardsByProject.map(({ count, project }) => ({
      count: count,
      name: project.name,
    })),
    byLocation: applicableHazardsByLocation.map(({ count, location }) => ({
      count: count,
      name: location.name,
    })),
    bySiteCondition: applicableHazardsBySiteCondition.map(
      ({ count, librarySiteCondition }) => ({
        count: count,
        name: librarySiteCondition.name,
      })
    ),
    byTask: applicableHazardsByTask.map(({ count, libraryTask }) => ({
      count: count,
      name: libraryTask.name,
    })),
    byTaskType: applicableHazardsByTaskType.map(({ count, libraryTask }) => ({
      count: count,
      name: libraryTask.category,
    })),
  };
}
