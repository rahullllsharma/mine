import type { WorkPackageData } from "@/components/templatesComponents/customisedForm.types";
import { useQuery } from "@apollo/client";
import GetProjectDetails from "@/graphql/queries/getProjectDetails.gql";

interface UseWorkPackageDataProps {
  projectId?: string | string[];
  locationId?: string | string[];
  shouldFetch?: boolean;
}

export const useWorkPackageData = ({
  projectId,
  locationId,
  shouldFetch = true,
}: UseWorkPackageDataProps) => {
  const { data: projectDetails } = useQuery(GetProjectDetails, {
    fetchPolicy: "cache-and-network",
    variables: {
      projectId,
      locationId,
      filterTenantSettings: true,
    },
    skip: !shouldFetch,
  });

  if (!projectDetails) {
    return { workPackageData: undefined, projectDetails };
  }

  const workPackageName = String(projectDetails?.project?.name);
  const locationName = String(projectDetails?.project?.locations?.[0]?.name);
  const projectStartDate = String(projectDetails?.project?.startDate);
  const projectEndDate = String(projectDetails?.project?.endDate);
  const regionData = projectDetails?.project?.libraryRegion
    ? {
        id: projectDetails.project.libraryRegion.id,
        name: projectDetails.project.libraryRegion.name,
      }
    : undefined;

  const workPackageData: WorkPackageData = {
    ...{ workPackageName },
    ...{ locationName },
    ...{ startDate: projectStartDate },
    ...{ endDate: projectEndDate },
    ...{ region: regionData },
  };

  return { workPackageData, projectDetails };
};
