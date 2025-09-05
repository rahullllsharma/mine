import type { ValidDateTime } from "@/utils/validation";
import type { LibrarySiteCondition } from "@/types/siteCondition/LibrarySiteCondition";
import type {
  ApiData,
  MarshalledDataType,
  SiteConditions,
  Tasks,
} from "@/types/jsbShare/jsbShare";
import type * as WorkProceduresSection from "@/components/forms/Jsb/GroupDiscussion/WorkProceduresSection";
import type * as EnergySourceControlsSection from "@/components/forms/Jsb/GroupDiscussion/EnergySourceControlsSection";
import type * as CriticalRiskAreasSection from "@/components/forms/Jsb/GroupDiscussion/CriticalRiskAreasSection";
import type { MedicalFacility } from "@/api/codecs";
import type {
  Ewp,
  JobSafetyBriefingLayout,
  LibraryTask,
  ProjectLocation,
} from "@/api/generated/types";
import * as O from "fp-ts/Option";
import { pipe } from "fp-ts/lib/function";
import { DateTime } from "luxon";
import { medicalFacilityCodec } from "@/api/codecs";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";

export function transformEWP(
  ewps: ApiData["energy_source_control"]["ewp"]
): Ewp[] {
  return ewps.map(ewp => ({
    id: ewp.id,
    metadata: {
      completed: O.fromNullable(
        DateTime.fromISO(ewp.metadata.completed) as ValidDateTime
      ),
      issued: DateTime.fromISO(ewp.metadata.issued) as ValidDateTime,
      issuedBy: ewp.metadata.issuedBy,
      procedure: ewp.metadata.procedure,
      receivedBy: ewp.metadata.receivedBy,
      remote: ewp.metadata.remote,
    },
    equipmentInformation: ewp.equipmentInformation,
    referencePoints: ewp.referencePoints,
  }));
}

export function marshallData(
  jsb: JobSafetyBriefingLayout,
  projectLocation: ProjectLocation | null,
  tasksLibrary: LibraryTask[],
  siteConditionsLibrary: LibrarySiteCondition[]
): MarshalledDataType {
  const generateSelectedMedicalFacility = (): O.Option<MedicalFacility> => {
    return pipe(
      jsb.nearestMedicalFacility,
      medicalFacilityCodec.decode,
      O.fromEither,
      O.alt(() =>
        pipe(
          { description: jsb.customNearestMedicalFacility?.address },
          medicalFacilityCodec.decode,
          a => a,
          O.fromEither
        )
      )
    );
  };

  const returnData: MarshalledDataType = {
    marshalled: true,
    headerData: {
      subTitle: `${projectLocation?.project?.name || ""}${
        projectLocation?.name ? ` • ${projectLocation.name}` : ""
      }`,

      risk: projectLocation?.riskLevel || RiskLevel.LOW,
      description: projectLocation?.project?.description as string,
    },
    jobInformationData: {
      briefingDateTime: DateTime.fromISO(
        jsb.jsbMetadata?.briefingDateTime
      ) as ValidDateTime,
      address: jsb?.workLocation?.address || "",
      workLocationDescription: jsb?.workLocation?.description || "",
      gpsCoordinates: O.fromNullable(
        jsb.gpsCoordinates?.map(({ latitude, longitude }) => ({
          latitude: Number(latitude),
          longitude: Number(longitude),
        }))[0]
      ),
      woCoordinates: O.fromNullable(
        projectLocation
          ? {
              latitude: Number(projectLocation.latitude),
              longitude: Number(projectLocation.longitude),
            }
          : null
      ),
      operatingHq: O.of(jsb.workLocation?.operatingHq ?? ""),
      isAdHocJsb: projectLocation ? false : true,
    },
    medicalEmergencyData: {
      emergencyContactName: jsb.emergencyContacts?.[0]?.name || "",
      emergencyContactPhone: jsb.emergencyContacts?.[0]?.phoneNumber || "",
      emergencyContactName2: jsb.emergencyContacts?.[1]?.name || "",
      emergencyContactPhone2: jsb.emergencyContacts?.[1]?.phoneNumber || "",
      selectedMedicalFacility: generateSelectedMedicalFacility(),
      selectedMedicalDevice: jsb.aedInformation?.location || "",
    },
    tasksSectionData: (jsb.taskSelections
      ?.map(({ id: taskId }) => {
        const task = tasksLibrary.find(({ id }) => id === taskId);
        return task
          ? {
              id: taskId,
              riskLevel: task?.riskLevel,
              name: task?.name || "",
              hazards: task?.hazards || [],
            }
          : null;
      })
      .flat()
      .filter((task): task is NonNullable<typeof task> => task !== null) ||
      []) as unknown as Tasks,
    criticalRisksData: {
      risks: (jsb.criticalRiskAreaSelections?.map(risk => risk.name) ||
        []) as unknown as CriticalRiskAreasSection.CriticalRiskAreasSectionData["risks"],
    },

    energySourceControlsData: {
      arcFlashCategory: O.fromNullable(
        jsb.energySourceControl?.arcFlashCategory
      ),
      clearancePoints: O.fromNullable(
        jsb.energySourceControl?.clearancePoints || null
      ),

      primaryVoltage: O.fromNullable(
        jsb.energySourceControl?.voltages
          ?.filter(voltage => voltage.type === "PRIMARY")
          ?.map(voltage => voltage.valueStr)
          ?.filter((value): value is string => value !== undefined)?.length
          ? jsb.energySourceControl?.voltages
              .filter(voltage => voltage.type === "PRIMARY")
              .map(voltage => voltage.valueStr)
              .filter((value): value is string => value !== undefined)
          : null
      ),

      secondaryVoltage:
        (jsb.energySourceControl?.voltages
          ?.filter(voltage => voltage.type === "SECONDARY")
          ?.map(voltage => voltage.valueStr)
          ?.filter((value): value is string => value !== undefined) ||
          []) ??
        [],

      transmissionVoltage: O.fromNullable(
        jsb.energySourceControl?.voltages?.find(
          voltage => voltage.type === "TRANSMISSION"
        )?.valueStr
      ),

      ewps: transformEWP(
        jsb.energySourceControl?.ewp || []
      ) as unknown as EnergySourceControlsSection.EnergySourceControlsSectionData["ewps"],
    },
    workProceduresData: {
      workProcedures: (jsb.workProcedureSelections ||
        []) as unknown as WorkProceduresSection.WorkProceduresSectionData["workProcedures"],
      otherWorkProcedures: jsb.otherWorkProcedures || "",
    },

    siteConditionsData: (jsb.siteConditionSelections
      ?.filter(({ selected }) => selected)
      ?.map(({ id }) => {
        const siteCondition = siteConditionsLibrary.find(
          ({ id: libraryId }) => libraryId === id
        );
        return {
          id,
          name: siteCondition?.name,
          hazards: siteCondition?.hazards || [],
        };
      }) || []) as unknown as SiteConditions,

    controlsData: {
      notes: jsb.hazardsAndControlsNotes || "",
    },
    ppeData: {
      directControl: jsb.additionalPpe || [],
    },
    attachmentsData: {
      photos: jsb.photos as unknown as ApiData["photos"],
      documents: (jsb.documents || []).map(
        ({ date, time, category, ...rest }) => ({
          ...rest,
          date: O.fromNullable(date),
          time: O.fromNullable(time),
          category: O.fromNullable(category),
        })
      ) as unknown as ApiData["documents"],
    },

    crewSignOffData: {
      crewList: jsb.crewSignOff || [],
    },
  };

  return { ...returnData };
}
