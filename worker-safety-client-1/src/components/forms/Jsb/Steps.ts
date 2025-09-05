import type { Either } from "fp-ts/lib/Either";
import type { Option } from "fp-ts/lib/Option";
import type * as GroupDiscussion from "./GroupDiscussion/GroupDiscussion";
import * as O from "fp-ts/lib/Option";
import * as A from "fp-ts/lib/Array";
import * as R from "fp-ts/lib/Record";
import { identity, pipe } from "fp-ts/lib/function";
import * as ControlsAssessment from "../Jsb/ControlsAssessment";
import { snapshotHash } from "../Utils";
import * as CrewSignOff from "./CrewSignOff";
import * as EnergySourceControls from "./EnergySourceControls";
import * as MedicalEmergency from "./MedicalEmergency";
import * as SiteConditions from "./SiteConditions";
import * as Tasks from "./Tasks";
import * as WorkProcedures from "./WorkProcedures";
import * as AttachmentsSection from "./AttachmentsSection";
import * as JobInformation from "./JobInformation";

export type Steps = {
  jobInformation: JobInformation.Model;
  medicalEmergency: MedicalEmergency.Model;
  energySourceControls: EnergySourceControls.Model;
  tasks: Tasks.Model;
  workProcedures: WorkProcedures.Model;
  siteConditions: SiteConditions.Model;
  controlsAssessment: ControlsAssessment.Model;
  attachments: AttachmentsSection.Model;
  groupDiscussion: Either<string, GroupDiscussion.GroupDiscussionData>;
  crewSignOff: CrewSignOff.Model;
};

export type StepName = keyof Steps;

// Defines the steps displayed in the wizard and their order.
export const stepList: StepName[] = [
  "jobInformation",
  "medicalEmergency",
  "tasks",
  "energySourceControls",
  "workProcedures",
  "siteConditions",
  "controlsAssessment",
  "attachments",
  "groupDiscussion",
  "crewSignOff",
];

export const nextStep = (currentStep: StepName): Option<StepName> =>
  pipe(
    stepList,
    A.dropLeftWhile(s => s !== currentStep),
    A.tail,
    O.chain(A.head)
  );

export const stepNames: Record<StepName, string> = {
  jobInformation: "Job Information",
  medicalEmergency: "Medical & Emergency",
  energySourceControls: "Energy Source Controls",
  tasks: "Tasks & Critical Risks",
  workProcedures: "Work Procedures",
  siteConditions: "Site Conditions",
  controlsAssessment: "Controls Assessment",
  attachments: "Attachments",
  groupDiscussion: "Group Discussion",
  crewSignOff: "Sign-Off",
};

export const checkUnsavedChanges = (
  stepsModel: Steps,
  stepHashes: Record<StepName, string>
): boolean => {
  const unsavedChanges: Record<StepName, boolean> = {
    jobInformation:
      pipe(
        stepsModel.jobInformation,
        JobInformation.makeSnapshot,
        snapshotHash
      ) !== stepHashes.jobInformation,
    medicalEmergency:
      pipe(
        stepsModel.medicalEmergency,
        MedicalEmergency.makeSnapshot,
        snapshotHash
      ) !== stepHashes.medicalEmergency,
    energySourceControls:
      pipe(
        stepsModel.energySourceControls,
        EnergySourceControls.makeSnapshot,
        snapshotHash
      ) !== stepHashes.energySourceControls,
    tasks:
      pipe(stepsModel.tasks, Tasks.makeSnapshot, snapshotHash) !==
      stepHashes.tasks,
    workProcedures:
      pipe(
        stepsModel.workProcedures,
        WorkProcedures.makeSnapshot,
        snapshotHash
      ) !== stepHashes.workProcedures,
    siteConditions:
      pipe(
        stepsModel.siteConditions,
        SiteConditions.makeSnapshot,
        snapshotHash
      ) !== stepHashes.siteConditions,
    controlsAssessment:
      pipe(
        stepsModel.controlsAssessment,
        ControlsAssessment.makeSnapshot,
        snapshotHash
      ) !== stepHashes.controlsAssessment,

    attachments:
      pipe(
        stepsModel.attachments,
        AttachmentsSection.makeSnapshot,
        snapshotHash
      ) !== stepHashes.attachments,
    groupDiscussion: false,
    crewSignOff:
      pipe(stepsModel.crewSignOff, CrewSignOff.makeSnapshot, snapshotHash) !==
      stepHashes.crewSignOff,
  };
  return pipe(unsavedChanges, R.some(identity));
};

export function setFormDirty(steps: Steps, currentStep: StepName): Steps {
  switch (currentStep) {
    case "jobInformation":
      return {
        ...steps,
        jobInformation: JobInformation.setFormDirty(steps.jobInformation),
      };
    case "medicalEmergency":
      return {
        ...steps,
        medicalEmergency: MedicalEmergency.setFormDirty(steps.medicalEmergency),
      };

    case "energySourceControls":
      return {
        ...steps,
        energySourceControls: EnergySourceControls.setFormDirty(
          steps.energySourceControls
        ),
      };

    case "tasks":
      return {
        ...steps,
        tasks: {
          ...steps.tasks,
          errorsEnabled: true,
        },
      };

    case "workProcedures":
      return {
        ...steps,
        workProcedures: WorkProcedures.setFormDirty(steps.workProcedures),
      };

    case "siteConditions":
      return steps;

    case "controlsAssessment":
      return steps;

    case "attachments":
      return steps;

    case "groupDiscussion":
      return steps;

    case "crewSignOff":
      return {
        ...steps,
        crewSignOff: CrewSignOff.setFormDirty(steps.crewSignOff),
      };
  }
}
