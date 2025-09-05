import type { ProjectInputs } from "@/types/form/Project";
import type { Location } from "@/types/project/Location";
import type { Project } from "@/types/project/Project";
import { ProjectNavigationTab } from "@/types/project/ProjectNavigationTabs";

export const getLocationsWithActivitiesOrDailyReports = (
  locations: Location[]
): Location[] =>
  locations.filter(
    ({ activities, dailyReports }) =>
      activities.length > 0 || dailyReports.length > 0
  );

export const getProjectDefaults = (project: Project): ProjectInputs => {
  return {
    name: project.name.trim(),
    status: project.status,
    startDate: project.startDate,
    endDate: project.endDate,
    libraryDivisionId: project.libraryDivision?.id,
    libraryRegionId: project.libraryRegion?.id,
    libraryProjectTypeId: project.libraryProjectType?.id,
    tenantWorkTypesId: project.workTypes?.map(workType => workType.id) || [],
    externalKey: project.externalKey,
    description: project.description,
    managerId: project.manager?.id,
    supervisorId: project.supervisor?.id,
    additionalSupervisors: project.additionalSupervisors?.map(
      additionalSupervisor => additionalSupervisor.id
    ),
    contractorId: project.contractor?.id,
    contractReference: project.contractReference,
    libraryAssetTypeId: project.libraryAssetType?.id,
    contractName: project.contractName,
    projectZipCode: project.projectZipCode,
    engineerName: project.engineerName,
    locations: project.locations.map(
      ({
        id,
        name,
        latitude,
        longitude,
        supervisor,
        externalKey,
        additionalSupervisors,
      }) => ({
        id,
        name: name.trim(),
        latitude,
        longitude,
        externalKey,
        supervisorId: supervisor?.id,
        additionalSupervisors: additionalSupervisors?.map(
          additionalSupervisor => additionalSupervisor.id
        ),
      })
    ),
  };
};

const getNavigationTabOption = (index: number): ProjectNavigationTab =>
  Object.values(ProjectNavigationTab)[index];

export const isDetailsNavigationTab = (index: number): boolean =>
  getNavigationTabOption(index) === ProjectNavigationTab.DETAILS;

export const isLocationsNavigationTab = (index: number): boolean =>
  getNavigationTabOption(index) === ProjectNavigationTab.LOCATIONS;

export const isAuditNavigationTab = (index: number): boolean =>
  getNavigationTabOption(index) === ProjectNavigationTab.AUDIT;
