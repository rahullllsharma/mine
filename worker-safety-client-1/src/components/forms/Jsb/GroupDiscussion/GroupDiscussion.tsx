import type {
  HazardControl,
  Jsb,
  LibrarySiteCondition,
  LibraryTask,
  LibraryTaskId,
  ProjectLocation,
} from "@/api/codecs";
import type { Option } from "fp-ts/lib/Option";
import type { Either } from "fp-ts/lib/Either";
import type { StepName } from "../Steps";
import type { ApiResult } from "@/api/api";
import type {
  RiskLevel,
  SaveJobSafetyBriefingInput,
} from "@/api/generated/types";
import type { Deferred } from "@/utils/deferred";
import type { ValidDateTime } from "@/utils/validation";
import { SectionHeading, BodyText, Icon } from "@urbint/silica";
import { sequenceS } from "fp-ts/lib/Apply";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import * as A from "fp-ts/lib/Array";
import { flow, identity, pipe } from "fp-ts/lib/function";
import { useMemo } from "react";
import * as t from "io-ts";
import * as Eq from "fp-ts/lib/Eq";
import { DateTime } from "luxon";
import router from "next/router";
import { eqHazardControlId } from "@/api/codecs";
import { deferredToOption } from "@/utils/deferred";
import { OptionalView } from "@/components/common/Optional";
import Link from "@/components/shared/link/Link";
import StepLayout from "../../StepLayout";
import { relevantHazards } from "../../Utils";
import ShareWidget from "../ShareWidget";
import * as JobInformationSection from "./JobInformationSection";
import * as MedicalEmergencySection from "./MedicalEmergencySection";
import * as TasksSection from "./TasksSection";
import * as CriticalRiskAreasSection from "./CriticalRiskAreasSection";
import * as EnergySourceControlsSection from "./EnergySourceControlsSection";
import * as WorkProceduresSection from "./WorkProceduresSection";
import * as SiteConditionsSection from "./SiteConditionsSection";
import * as ControlsSection from "./ControlsSection";
import * as PPESection from "./PPESection";
import * as AttachmentsSection from "./AttachmentsSection";

export type GroupDiscussionData = {
  jobInformation: JobInformationSection.JobInformationSectionData;
  medicalEmergency: MedicalEmergencySection.MedicalEmergencySectionData;
  tasks: TasksSection.TasksSectionData;
  criticalRisks: CriticalRiskAreasSection.CriticalRiskAreasSectionData;
  energySourceControls: EnergySourceControlsSection.EnergySourceControlsSectionData;
  workProcedures: WorkProceduresSection.WorkProceduresSectionData;
  siteConditions: SiteConditionsSection.SiteConditionsSectionData;
  attachments: AttachmentsSection.AttachmentsSectionData;
  updatedAt: Option<ValidDateTime>;
  viewed: boolean;
  controlsAssessment: ControlsSection.ControlsSectionData;
};

export const init = (
  jsb: Option<Jsb>,
  projectLocation: Option<ProjectLocation>,
  updatedAt: Option<ValidDateTime>
): Either<string, GroupDiscussionData> =>
  pipe(
    jsb,
    O.fold(
      () => E.left("jsb is missing"),
      jsbContents =>
        sequenceS(E.Apply)({
          jobInformation: JobInformationSection.init(
            jsbContents,
            projectLocation
          ),
          medicalEmergency: MedicalEmergencySection.init(jsbContents),
          tasks: TasksSection.init(jsbContents),
          criticalRisks: CriticalRiskAreasSection.init(jsbContents),
          energySourceControls: EnergySourceControlsSection.init(jsbContents),
          workProcedures: WorkProceduresSection.init(jsbContents),
          siteConditions: SiteConditionsSection.init(jsbContents),
          attachments: AttachmentsSection.init(jsbContents),
          updatedAt: E.right(pipe(updatedAt)),
          controlsAssessment: ControlsSection.init(jsbContents),
          viewed: pipe(
            jsb,
            O.chain(j => j.groupDiscussion),
            O.fold(
              () => false,
              gd => gd.viewed
            ),
            E.right
          ),
        })
    )
  );

export function toSaveJsbInput(
  groupDiscussionData: Either<string, GroupDiscussionData>
): t.Validation<SaveJobSafetyBriefingInput> {
  return pipe(
    groupDiscussionData,
    E.fold(
      () => ({
        groupDiscussion: { viewed: false }, // group discussion data not available, so it can't be viewed
      }),
      () => ({
        groupDiscussion: { viewed: true },
      })
    ),
    t.type({
      groupDiscussion: t.type({
        viewed: t.literal(true), // we want to validate this as true to confirm the fact that group discussion data has been viewed
      }),
    }).decode
  );
}

export const locationCheck = () => {
  const routeHandler = router.query;
  const isAdhocJSB = !routeHandler.locationId;
  const labelName = isAdhocJSB ? "JSB Summary" : "Group Discussion";
  const text = isAdhocJSB
    ? "The information below is a summary of your JSB to review."
    : "The information below is to support the team read out. ";
  return { labelName, text };
};

export type Props = {
  groupDiscussionData: Either<string, GroupDiscussionData>;
  tasksLibrary: Deferred<ApiResult<LibraryTask[]>>;
  riskLevels: Map<LibraryTaskId, RiskLevel>;
  siteConditionsLibrary: Deferred<ApiResult<LibrarySiteCondition[]>>;
  onClickEdit: (step: StepName) => void;
  jsbId: string;
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const { labelName } = locationCheck();
  const { isReadOnly } = props;
  return (
    <OptionalView
      value={O.fromEither(props.groupDiscussionData)}
      render={gdDataValue => (
        <GroupDiscussionLayout
          {...gdDataValue}
          tasksLibrary={props.tasksLibrary}
          riskLevels={props.riskLevels}
          siteConditionsLibrary={props.siteConditionsLibrary}
          onClickEdit={props.onClickEdit}
          jsbId={props.jsbId}
          isReadOnly={isReadOnly}
        />
      )}
      renderNone={() => (
        <div>
          <SectionHeading className="text-xl font-semibold mb-4">
            {labelName || " "}
          </SectionHeading>
          <BodyText>
            Please complete all sections of the JSB before the
            {" " + labelName || " "}.
          </BodyText>
        </div>
      )}
    />
  );
}

const eqHazardControlById = Eq.contramap((c: HazardControl) => c.id)(
  eqHazardControlId
);
const humanTraffickingHotline = "1-888-373-7888";
type GroupDiscussionLayoutProps = GroupDiscussionData & {
  tasksLibrary: Deferred<ApiResult<LibraryTask[]>>;
  riskLevels: Map<LibraryTaskId, RiskLevel>;
  siteConditionsLibrary: Deferred<ApiResult<LibrarySiteCondition[]>>;
  onClickEdit: (step: StepName) => void;
  jsbId: string;
  isReadOnly: boolean;
};

function GroupDiscussionLayout(props: GroupDiscussionLayoutProps): JSX.Element {
  const { labelName, text } = locationCheck();
  const maybeOnClickEdit = (step: StepName) =>
    props.isReadOnly ? undefined : () => props.onClickEdit(step);
  const ppeCollection = useMemo(
    () =>
      pipe(
        O.Do,
        O.bind("tasks", () =>
          pipe(props.tasksLibrary, deferredToOption, O.chain(O.fromEither))
        ),
        O.bind("siteConditions", () =>
          pipe(
            props.siteConditionsLibrary,
            deferredToOption,
            O.chain(O.fromEither)
          )
        ),
        O.map(({ tasks, siteConditions }) =>
          relevantHazards(tasks)(siteConditions)(props.tasks.taskIds)(
            props.siteConditions.siteConditionIds
          )
        ),
        O.map(
          flow(
            A.chain(hazard => hazard.controls),
            A.uniq(eqHazardControlById),
            A.filterMap(control =>
              pipe(
                control.ppe,
                O.filter(identity),
                O.map(_ => control.name)
              )
            )
          )
        )
      ),
    [
      props.tasksLibrary,
      props.siteConditionsLibrary,
      props.tasks,
      props.siteConditions,
    ]
  );

  return (
    <StepLayout>
      <div className="flex flex-col gap-4 justify-between">
        <SectionHeading className="text-xl font-semibold">
          {labelName || " "}
        </SectionHeading>
        <div className="flex">
          <BodyText>
            {text || " "} If any information needs to be updated, you can still
            make edits to this information by navigating back to the section.
          </BodyText>
          <ShareWidget externalJsbId={props.jsbId} />
        </div>
        <OptionalView
          value={props.updatedAt}
          render={uAt => {
            //need to recreate the date object to remove the timezone lock on uAt
            const unlockedDate = DateTime.fromISO(uAt.toISO() || "");
            return (
              <div className="text-xs font-normal text-neutral-shade-75 mt-0.5">
                <p>
                  {`Last updated at: ${unlockedDate.toLocaleString(
                    DateTime.DATE_HUGE
                  )}, ${unlockedDate.toLocaleString(
                    DateTime.TIME_WITH_SHORT_OFFSET
                  )}`}
                </p>
              </div>
            );
          }}
        />

        <JobInformationSection.View
          {...props.jobInformation}
          onClickEdit={maybeOnClickEdit("jobInformation")}
        />
        <MedicalEmergencySection.View
          {...props.medicalEmergency}
          onClickEdit={maybeOnClickEdit("medicalEmergency")}
        />
        <TasksSection.View
          {...props.tasks}
          tasksLibrary={props.tasksLibrary}
          riskLevels={props.riskLevels}
          onClickEdit={maybeOnClickEdit("tasks")}
        />
        <CriticalRiskAreasSection.View
          {...props.criticalRisks}
          onClickEdit={maybeOnClickEdit("tasks")} // If a different step name is required, change here
        />
        <EnergySourceControlsSection.View
          {...props.energySourceControls}
          onClickEdit={maybeOnClickEdit("energySourceControls")}
        />
        <WorkProceduresSection.View
          {...props.workProcedures}
          onClickEdit={maybeOnClickEdit("workProcedures")}
        />
        <SiteConditionsSection.View
          {...props.siteConditions}
          tasksLibrary={props.tasksLibrary}
          siteConditionsLibrary={props.siteConditionsLibrary}
          onClickEdit={maybeOnClickEdit("siteConditions")}
        />
        <ControlsSection.View
          {...props.controlsAssessment}
          onClickEdit={maybeOnClickEdit("controlsAssessment")}
          notes={props.controlsAssessment?.notes}
        />
        <OptionalView
          value={ppeCollection}
          render={ppe => <PPESection.PPESection directControl={ppe} />}
        />
        <AttachmentsSection.View
          {...props.attachments}
          onClickEdit={maybeOnClickEdit("attachments")}
        />
      </div>
      <div className="p-4 flex flex-col gap-3 bg-brand-gray-10">
        <div className="bg-white p-4 flex flex-col justify-center items-center gap-2 ">
          <Link
            iconRight="external_link"
            label="Human Trafficking Hotline"
            href="https://humantraffickinghotline.org/en"
            target="_blank"
          />

          <div className="flex text-brand-urbint-50 justify-center">
            <a href={`tel:${humanTraffickingHotline}`}>
              <Icon name="phone" className="mr-1" />
              {humanTraffickingHotline}
            </a>
          </div>
        </div>
      </div>
    </StepLayout>
  );
}
