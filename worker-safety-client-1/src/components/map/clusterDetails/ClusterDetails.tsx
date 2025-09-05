import type { ProjectDetailsProps } from "./components/ProjectDetails";
import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import ProjectDetails from "./components/ProjectDetails";
import { getLabelWithRiskIcon } from "./utils";

type ClusterProjectRiskInfo =
  | ProjectDetailsProps
  | Partial<Record<keyof ProjectDetailsProps, never>>;

type ClusterDetailsProps = ClusterProjectRiskInfo & {
  totalTitle: string;
  totals: Partial<
    Record<Exclude<RiskLevel, RiskLevel.RECALCULATING>, number | undefined>
  >;
};

function ClusterDetails({
  totalTitle,
  totals,
  ...addressDetails
}: ClusterDetailsProps): JSX.Element {
  return (
    <div className="p-3 inline-block max-w-xs rounded shadow-20">
      {addressDetails.riskLevel && <ProjectDetails {...addressDetails} />}
      <footer>
        <h5 className="text-sm font-bold mb-1">{totalTitle}</h5>
        <ul className="inline-flex gap-1">
          {(Object.entries(totals) as [RiskLevel, number][]).map(
            ([key, value]) =>
              value ? (
                <li
                  key={key}
                  data-testid={`cluster-detail-risk-badge-${key.toLowerCase()}`}
                >
                  <RiskBadge
                    risk={key}
                    label={getLabelWithRiskIcon({
                      risk: key,
                      label: value.toString(),
                    })}
                  />
                </li>
              ) : null
          )}
        </ul>
      </footer>
    </div>
  );
}

export default ClusterDetails;
