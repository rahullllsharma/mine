import type { ProjectEditProps } from "@/pages/projects/[id]/settings";
import { usePageContext } from "@/context/PageProvider";
import ProjectLocations from "./form/locations/ProjectLocations";
import ProjectDetails from "./form/details/ProjectDetails";
import {
  getLocationsWithActivitiesOrDailyReports,
  isAuditNavigationTab,
  isDetailsNavigationTab,
  isLocationsNavigationTab,
} from "./utils";
import ProjectAudit from "./audit/ProjectAudit";

type ProjectFormEditProps = {
  selectedTab: number;
  readOnly?: boolean;
};

export default function ProjectSettings({
  selectedTab,
  readOnly = false,
}: ProjectFormEditProps): JSX.Element {
  const {
    project: { locations = [], id },
  } = usePageContext<ProjectEditProps>();

  return (
    <>
      {isDetailsNavigationTab(selectedTab) && (
        <ProjectDetails readOnly={readOnly} />
      )}
      {isLocationsNavigationTab(selectedTab) && (
        <ProjectLocations
          readOnly={readOnly}
          locationsBlocked={getLocationsWithActivitiesOrDailyReports(locations)}
        />
      )}
      {isAuditNavigationTab(selectedTab) && <ProjectAudit projectId={id} />}
    </>
  );
}
