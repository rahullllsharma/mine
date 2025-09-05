import type { CriticalRisk, Hazard } from "@/api/codecs";
import type { ControlsSectionProps } from "@/components/forms/Jsb/GroupDiscussion/ControlsSection";
import type { PPESectionProps } from "@/components/forms/Jsb/GroupDiscussion/PPESection";
import type { Ewp, RiskLevel } from "@/api/generated/types";
import type * as O from "fp-ts/Option";
import type * as AttachmentsSection from "@/components/forms/Jsb/GroupDiscussion/AttachmentsSection";
import type * as WorkProceduresSection from "@/components/forms/Jsb/GroupDiscussion/WorkProceduresSection";
import type * as EnergySourceControlsSection from "@/components/forms/Jsb/GroupDiscussion/EnergySourceControlsSection";
import type * as JobInformationSection from "@/components/forms/Jsb/GroupDiscussion/JobInformationSection";
import type * as CriticalRiskAreasSection from "@/components/forms/Jsb/GroupDiscussion/CriticalRiskAreasSection";
import type * as MedicalEmergencySection from "@/components/forms/Jsb/GroupDiscussion/MedicalEmergencySection";
import { CrewInformationType } from "@/api/generated/types";

export type Tasks = {
  id: string;
  riskLevel?: RiskLevel;
  name: string;
  hazards: Hazard[];
}[];

export type SiteConditions = {
  id: string;
  name: string;
  hazards: Hazard[];
}[];

export type SignatureFile = {
  displayName: string;
  id: string;
  name: string;
  signedUrl: string;
  size: string;
  url: string;
};

export type CrewSignOffData = {
  type?: string;
  name: string;
  signature: SignatureFile;
  jobTitle: string;
  employeeNumber: string;
};

export type CrewSignOffType = {
  crewList: CrewInformationType[];
};

export type MarshalledDataType =
  | {
      marshalled: true;
      headerData: {
        subTitle?: string;
        risk: string;
        description?: string;
      };
      jobInformationData: JobInformationSection.JobInformationSectionData;
      medicalEmergencyData: MedicalEmergencySection.MedicalEmergencySectionData;
      tasksSectionData: Tasks;
      criticalRisksData: CriticalRiskAreasSection.CriticalRiskAreasSectionData;
      energySourceControlsData: EnergySourceControlsSection.EnergySourceControlsSectionData;
      workProceduresData: WorkProceduresSection.WorkProceduresSectionData;
      siteConditionsData: SiteConditions;
      controlsData: ControlsSectionProps;
      ppeData: PPESectionProps;
      attachmentsData: AttachmentsSection.AttachmentsSectionData;
      crewSignOffData: CrewSignOffType;
    }
  | { marshalled: false };

export type RawTask = {
  id: string;
  risk_level: RiskLevel;
  attributes: {
    name: string;
  };
};

export type ApiData = {
  jsb_metadata: {
    briefing_date_time: string;
  };
  work_location: {
    address: string;
    description: string;
  };
  gps_coordinates: [
    {
      latitude: string;
      longitude: string;
    },
    {
      latitude: string;
      longitude: string;
    }
  ];
  emergency_contacts: [
    {
      name: string;
      phone_number: string;
    },
    {
      name: string;
      phone_number: string;
    }
  ];
  activities: [
    {
      tasks: RawTask[];
    }
  ];
  critical_risk_area_selections: [
    {
      name: CriticalRisk;
    }
  ];
  energy_source_control: {
    arc_flash_category: number;
    clearance_points: string;
    voltages: {
      type: string;
      unit: string;
      value: number;
    }[];
    ewp: Ewp[];
  };
  work_procedure_selections: {
    id:
      | "four_rules_of_cover_up"
      | "sdop_switching_procedures"
      | "toc"
      | "section_0"
      | "distribution_bulletins"
      | "mad"
      | "excavation"
      | "step_touch_potential"
      | "human_perf_toolkit";
    values: [];
  }[];
  site_condition_selections: {
    id: string;
    selected: boolean;
    recommended: boolean;
    attributes: {
      id: string;
      name: string;
      default_multiplier: number;
      archived_at: null;
      handle_code: string;
    };
  }[];
  hazards_and_controls_notes: string;
  other_work_procedures: string;
  additional_ppe: string[];
  photos: {
    id: string;
    name: string;
    displayName: string;
    size: string;
    url: string;
    signedUrl: string;
    date: O.Option<string>;
    time: O.Option<string>;
    category: O.Option<string>;
  }[];
  documents: {
    id: string;
    name: string;
    displayName: string;
    size: string;
    url: string;
    signedUrl: string;
    date: O.Option<string>;
    time: O.Option<string>;
    category: O.Option<string>;
  }[];
  aed_information: {
    location: string;
  };
};
