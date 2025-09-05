import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import RiskLabel from "@/components/riskLabel/RiskLabel";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export type ProjectDetailsProps = {
  riskLevel: RiskLevel;
  projectName: string;
  supervisorName: string;
};

function ProjectDetails({
  supervisorName,
  projectName,
  riskLevel,
}: ProjectDetailsProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  return (
    <section className="pb-2">
      <div className="-ml-2">
        {/* RiskLabel uses the Badge component from Silica which has a inner padding and messes the alignment */}
        {/* FIXME: remove this whenever the Badge is fixed on silica */}
        <RiskLabel risk={riskLevel} label={`${riskLevel} risk`} />
      </div>
      <h5 className="text-base font-semibold text-neutral-shade-100 pt-2">
        {projectName}
      </h5>
      <span className="text-sm text-neutral-shade-75 block">
        {`${workPackage.attributes.primaryAssignedPerson.label}: ${supervisorName}`}
      </span>
    </section>
  );
}

export default ProjectDetails;
