import { RiskLevel } from "@/components/riskBadge/RiskLevel";

export const sampleRiskCountData = [
  {
    date: "2022-01-29",
    riskLevel: RiskLevel.HIGH,
    count: 10,
  },
  {
    date: "2022-01-29",
    riskLevel: RiskLevel.MEDIUM,
    count: 20,
  },
  {
    date: "2022-01-29",
    riskLevel: RiskLevel.LOW,
    count: 30,
  },
  {
    date: "2022-01-30",
    riskLevel: RiskLevel.HIGH,
    count: 5,
  },
  {
    date: "2022-01-30",
    riskLevel: RiskLevel.MEDIUM,
    count: 10,
  },
  {
    date: "2022-01-30",
    riskLevel: RiskLevel.LOW,
    count: 20,
  },
  {
    date: "2022-02-01",
    riskLevel: RiskLevel.HIGH,
    count: 1,
  },
  // skipping medium
  {
    date: "2022-02-01",
    riskLevel: RiskLevel.LOW,
    // set Low to zero
    count: 0,
  },
];
