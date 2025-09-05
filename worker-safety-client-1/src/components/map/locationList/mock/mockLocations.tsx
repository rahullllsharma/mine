import type { MapLocation } from "@/types/project/Location";
import type { Project } from "@/types/project/Project";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";

const project: Project = {
  id: "7114445f-966a-42e2-aa3b-0e4d5365075d",
  name: "5th Street Main Relocation",
  riskLevel: RiskLevel.HIGH,
  supervisor: { id: "2", name: "Jakob Aminoff" },
  manager: { id: "1", name: "Jakob Aminoff" },
  additionalSupervisors: [],
  contractor: { id: "1", name: "Jakob Aminoff" },
  region: "Northeast",
  status: "Active",
  libraryProjectType: { id: "1", name: "Main replacement" },
  libraryDivision: { id: "1", name: "Gas" },
  libraryRegion: { id: "1", name: "NE (New England)" },
  startDate: "2021-12-28",
  endDate: "2022-12-31",
  externalKey: "123",
  locations: [],
};
export const mockLocations: MapLocation[] = [
  {
    id: "1",
    name: "308 Main Street",
    latitude: 34.054913,
    longitude: -62.136754,
    supervisor: {
      id: "1",
      name: "Bart Simpson",
    },
    riskLevel: RiskLevel.MEDIUM,
    riskCalculation: {
      totalTaskRiskLevel: RiskLevel.UNKNOWN,
      isSupervisorAtRisk: false,
      isContractorAtRisk: false,
      isCrewAtRisk: false,
    },
    siteConditions: [],
    tasks: [],
    dailyReports: [],
    activities: [],
    jobSafetyBriefings: [],
    project,
  },
  {
    id: "1",
    name: "405 Second Street",
    latitude: 34.0913,
    longitude: -32.1354,
    supervisor: {
      id: "2",
      name: "Homer Simpson",
    },
    riskLevel: RiskLevel.LOW,
    riskCalculation: {
      totalTaskRiskLevel: RiskLevel.UNKNOWN,
      isSupervisorAtRisk: false,
      isContractorAtRisk: false,
      isCrewAtRisk: false,
    },
    siteConditions: [],
    tasks: [],
    dailyReports: [],
    activities: [],
    jobSafetyBriefings: [],
    project,
  },
];
