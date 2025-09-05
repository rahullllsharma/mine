import type { Project } from "@/types/project/Project";
import type { EntityAttributeMap } from "@/store/tenant/types";
import NextLink from "next/link";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import Link from "@/components/shared/link/Link";
import Table from "@/components/table/Table";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import Tooltip from "../../components/shared/tooltip/Tooltip";

const getColumns = ({
  name: workPackageName,
  primaryAssignedPerson,
  region,
  division,
  workPackageType,
}: EntityAttributeMap) => [
  {
    id: "workPackageName",
    Header: workPackageName.label,
    width: 180,
    // eslint-disable-next-line react/display-name
    accessor: ({ id, name }: Project) => (
      <NextLink
        href={{
          pathname: "/projects/[id]",
          query: { id },
        }}
        passHref
      >
        <Link label={name} allowWrapping />
      </NextLink>
    ),
  },
  {
    id: "todayRisk",
    Header: "Todays risk",
    width: 140,
    // eslint-disable-next-line react/display-name
    accessor: (project: Project) => (
      <Tooltip
        title={
          "The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed"
        }
        position="bottom"
        className="max-w-xl"
      >
        <RiskBadge
          risk={project.riskLevel}
          label={`${project.riskLevel}`}
          isCritical={
            project.locations?.some(({ activities }) =>
              activities?.some(data => data.isCritical === true)
            ) || false
          }
        />
      </Tooltip>
    ),
  },
  ...(primaryAssignedPerson.visible
    ? [
        {
          id: "supervisor",
          Header: "Supervisor",
          width: 120,
          accessor: (project: Project) => project.supervisor?.name,
        },
      ]
    : []),
  ...(region.visible
    ? [
        {
          id: "libraryRegion",
          Header: region.label,
          width: 120,
          // eslint-disable-next-line react/display-name
          accessor: (project: Project) => <>{project.libraryRegion?.name}</>,
        },
      ]
    : []),
  ...(workPackageType.visible
    ? [
        {
          id: "libraryProjectType",
          Header: workPackageType.label,
          width: 100,
          // eslint-disable-next-line react/display-name
          accessor: (project: Project) => (
            <>{project.libraryProjectType?.name}</>
          ),
        },
      ]
    : []),
  ...(division.visible
    ? [
        {
          id: "libraryDivision",
          Header: division.label,
          width: 60,
          // eslint-disable-next-line react/display-name
          accessor: (project: Project) => <>{project.libraryDivision?.name}</>,
        },
      ]
    : []),
];

export default function ProjectTable({
  projects,
  isLoading = false,
}: {
  projects: Project[];
  isLoading?: boolean;
}): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  return (
    <Table
      columns={getColumns(workPackage.attributes)}
      data={projects}
      isLoading={isLoading}
    />
  );
}
