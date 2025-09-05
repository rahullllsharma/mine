/* istanbul ignore file */
import type { HTMLAttributes } from "react";
import type { Project } from "@/types/project/Project";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import RiskBadge from "../riskBadge/RiskBadge";
import Tooltip from "../shared/tooltip/Tooltip";
import CardRow from "./cardRow/CardRow";

type CardItemProps = Pick<HTMLAttributes<HTMLButtonElement>, "onClick"> & {
  project: Project;
  isLoading?: boolean;
};

function CardItemContent({ project }: { project: Project }): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  return (
    <>
      <header className="text-neutral-shade-100 text-lg font-semibold">
        {project.name}
      </header>
      <div className="mt-4">
        <div className="flex text-sm items-center py-1.5">
          <span className="flex-1 text-neutral-shade-100 text-sm font-semibold">
            {`${workPackage.label} Risk`}
          </span>
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
        </div>
        {workPackage.attributes.region.visible && (
          <CardRow label={workPackage.attributes.region.label}>
            {project.libraryRegion?.name}
          </CardRow>
        )}
        {workPackage.attributes.primaryAssignedPerson.visible && (
          <CardRow label="Supervisor">{project.supervisor?.name}</CardRow>
        )}
        {workPackage.attributes.workPackageType.visible && (
          <CardRow label={workPackage.attributes.workPackageType.label}>
            {project.libraryProjectType?.name}
          </CardRow>
        )}
        {workPackage.attributes.division.visible && (
          <CardRow label={workPackage.attributes.division.label}>
            {project.libraryDivision?.name}
          </CardRow>
        )}
      </div>
    </>
  );
}

function CardItemPlaceholder(): JSX.Element {
  const itemRowPlaceholder = (
    <div className="flex border-solid border-t my-1 py-1 text-sm ">
      <span className="flex-1">
        <div className="h-3 rounded animate-pulse w-1/3 bg-gray-300"></div>
      </span>
      <span className="h-3 rounded animate-pulse w-2/5 bg-gray-200"></span>
    </div>
  );
  return (
    <div className="flex-1 p-6">
      <header className="h-5 rounded animate-pulse w-1/2 bg-gray-300" />
      <div className="mt-4">
        {itemRowPlaceholder}
        {itemRowPlaceholder}
        {itemRowPlaceholder}
        {itemRowPlaceholder}
        {itemRowPlaceholder}
      </div>
    </div>
  );
}

export default function CardItem({
  project,
  isLoading,
  onClick,
}: CardItemProps): JSX.Element {
  return (
    <div className="flex rounded bg-white shadow-5">
      {isLoading ? (
        <CardItemPlaceholder />
      ) : (
        <button className="flex-1 p-6 text-left" onClick={onClick}>
          <CardItemContent project={project} />
        </button>
      )}
    </div>
  );
}
