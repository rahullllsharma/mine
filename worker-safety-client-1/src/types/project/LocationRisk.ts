import type { RiskLevel } from "@/components/riskBadge/RiskLevel";

export interface LocationRisk {
  totalTaskRiskLevel: RiskLevel;
  isSupervisorAtRisk: boolean;
  isContractorAtRisk: boolean;
  isCrewAtRisk: boolean;
}
