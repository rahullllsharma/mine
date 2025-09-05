import type { SeverityValues } from "@/container/activity/historicIncidentsModal/Severity";

export interface Incident {
  id: string;
  description: string;
  incidentDate: string;
  incidentType: string;
  severity: keyof typeof SeverityValues;
  severityCode?: string;
}
