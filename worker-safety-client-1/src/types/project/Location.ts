import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import type { User } from "../User";
import type { Activity } from "../activity/Activity";
import type { DailyReport } from "../report/DailyReport";
import type {
  HazardAggregator,
  TaskHazardAggregator,
} from "./HazardAggregator";
import type { LocationRisk } from "./LocationRisk";
import type { Project } from "./Project";
import type { Jsb } from "@/api/codecs";

export interface Location {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  externalKey?: string;
  siteConditions: HazardAggregator[];
  tasks: TaskHazardAggregator[];
  dailyReports: DailyReport[];
  supervisor?: User;
  additionalSupervisors?: User[];
  riskCalculation: LocationRisk;
  riskLevel: RiskLevel;
  activities: Activity[];
  project?:{id?:string};
  jobSafetyBriefings: {
    id: string;
    name: string;
    status: string;
    contents: {
      emergencyContacts: {
        name: string;
        phoneNumber: string;
        primary: boolean;
      }[];
      nearestMedicalFacility: Jsb["nearestMedicalFacility"];
      aedInformation: {
        location: string;
      };
      workLocation: {
        address: string;
      };
      gpsCoordinates: {
        latitude: number;
        longitude: number;
      };
      jsbMetadata: {
        briefingDateTime: string;
      };
      energySourceControl: {
        ewp: {
          id: string;
          equipmentInformation: {
            circuitBreaker: string;
          }[];
        }[];
      };
    };
  }[];
}

export interface MapLocation extends Location {
  project: Project;
  datedActivities?: Activity[];
}
