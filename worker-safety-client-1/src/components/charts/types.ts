import type { RiskLevel } from "@/components/riskBadge/RiskLevel";

// TODO perhaps these types are derived from the graphql via apollo?

export interface LocationRiskCount {
  date: string;
  riskLevel: RiskLevel;
  count: number;
}

export interface ProjectRiskCount {
  date: string;
  riskLevel: RiskLevel;
  count: number;
}
