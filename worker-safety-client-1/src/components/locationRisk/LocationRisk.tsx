import type { PropsWithChildren } from "react";
import type { RiskLevel } from "../riskBadge/RiskLevel";
import { Icon } from "@urbint/silica";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import RiskBadge from "../riskBadge/RiskBadge";

export type LocationRiskProps = {
  risk: RiskLevel;
  supervisorRisk?: boolean;
  contractorRisk?: boolean;
  crewRisk?: boolean;
};

type RiskContentProps = PropsWithChildren<{
  text: string;
}>;

const RiskContentLayout = ({
  text,
  children,
}: RiskContentProps): JSX.Element => (
  <div className="flex items-center justify-between p-2 bg-neutral-shade-3 rounded h-9">
    <span className="text-tiny font-medium">{text}</span>
    {children}
  </div>
);

const AtRiskContent = (): JSX.Element => (
  <div className="flex items-center">
    <Icon name="warning_outline" className="text-sm text-data-red-30 mr-0.5" />
    <span className="text-tiny text-data-red-30 font-bold uppercase">
      At risk
    </span>
  </div>
);

export default function LocationRisk({
  risk,
  supervisorRisk,
  contractorRisk,
  crewRisk,
}: LocationRiskProps): JSX.Element {
  const { workPackage, location, task } = useTenantStore(state =>
    state.getAllEntities()
  );
  return (
    <div className="p-4 text-neutral-shade-100 grid gap-y-1">
      <p className="text-sm font-semibold mb-3">{`${location.label} Risk Calculation`}</p>
      <RiskContentLayout text={`${task.label} Risk`}>
        <RiskBadge risk={risk} label={`${risk}`} />
      </RiskContentLayout>
      {supervisorRisk && (
        <RiskContentLayout
          text={workPackage.attributes.primaryAssignedPerson.label}
        >
          <AtRiskContent />
        </RiskContentLayout>
      )}
      {contractorRisk && (
        <RiskContentLayout text={workPackage.attributes.primeContractor.label}>
          <AtRiskContent />
        </RiskContentLayout>
      )}
      {crewRisk && (
        <RiskContentLayout text="Crew">
          <AtRiskContent />
        </RiskContentLayout>
      )}
    </div>
  );
}
