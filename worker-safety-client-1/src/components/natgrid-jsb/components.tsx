/* eslint-disable jsx-a11y/alt-text */
import type { Incident } from "@/api/codecs";
import type { RiskLevel } from "@/api/generated/types";
import type {
  Activity,
  AttachmentSection,
  EnergySourceControl,
  HighEnergyHazard,
  JobSafetyBriefing,
  LowEnergyHazard,
  Task,
  MedicalInformationType,
  NearestHospitalType,
  HistoricIncidentType,
  HistoricIncidents,
  Control,
  HazardList,
  barnLocation,
  UiConfigData,
  StandardOperatingProcedures,
  TaskLib,
} from "@/types/natgrid/jobsafetyBriefing";
import type {
  PageListItemType,
  SharePageSiteConditionDetailsType,
} from "@/utils/jsbShareUtils/jsbShare.type";
import cx from "classnames";
import {
  BodyText,
  CaptionText,
  ComponentLabel,
  Icon,
  SectionHeading,
  Subheading,
} from "@urbint/silica";
import { flatten, groupBy } from "lodash";
import { capitalize, get, isEmpty, map, some, upperCase } from "lodash-es";
import NextLink from "next/link";
import { gql, useQuery } from "@apollo/client";
import Image from "next/image";
import { useMemo, useState } from "react";
import cloneDeep from "lodash/cloneDeep";
import { isMobile, isTablet } from "react-device-detect";
import { getFormattedDate } from "@/utils/date/helper";
import Checkbox from "@/components/shared/checkbox/Checkbox";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import TaskHeader from "@/components/layout/taskCard/header/TaskHeader";
import {
  convertRiskLevelToRiskBadgeRiskLevel,
  getBackgroundColorByRiskLevel,
  getBorderColorByRiskLevel,
} from "@/components/forms/Basic/TaskCard/utils";
import Link from "@/components/shared/link/Link";
import EboIncidentCard, {
  CheckedIcon,
} from "@/components/incidentCard/EboIncidentCard";
import getHistoricIncidents from "@/graphql/queries/getHistoricIncidents.gql";
import Loader from "@/components/shared/loader/Loader";
import { FieldGroup } from "@/components/shared/FieldGroup";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import PostJobBrief from "src/pages/jsb-share/natgrid/[id]/components/PostJobBrief";
import CrewSignOff from "src/pages/jsb-share/natgrid/[id]/components/CrewSignOff";
import LocationInfo from "src/pages/jsb-share/natgrid/[id]/components/LocationInfo";
import { Status } from "@/types/natgrid/jobsafetyBriefing";
import { useAuthStore } from "@/store/auth/useAuthStore.store";

const dt: PageListItemType = {
  label: "test",
  status: "saved",
  id: 2,
};

const TASKS_LIB_QUERY = gql`
  query TasksLibrary($tasksLibraryId: [UUID!]) {
    tasksLibrary(ids: $tasksLibraryId) {
      id
      name
      riskLevel
    }
  }
`;

const FALLBACK_COLOURS: Record<string, string> = {
  biological: "#5CC9E6",
  chemical: "#B7D771",
  temperature: "#E55142",
  gravity: "#28B895",
  motion: "#FADB08",
  mechanical: "#C61D62",
  electrical: "#F7B219",
  pressure: "#AA509E",
  sound: "#72BF4B",
  radiation: "#F1A224",
  unspecified: "#C0C7C9",
  default: "#C0C7C9",
};

const GET_ENERGY_WHEEL_COLOURS = gql`
  query GetEnergyWheelColours {
    uiConfig(formType: NATGRID_JOB_SAFETY_BRIEFING) {
      contents
    }
  }
`;

export const useEnergyColours = () => {
  const { data } = useQuery<UiConfigData>(GET_ENERGY_WHEEL_COLOURS);

  const apiColours = (
    data?.uiConfig?.contents?.energy_wheel_color ?? []
  ).reduce((acc, { name, color }) => {
    acc[name.toLowerCase()] = color;
    return acc;
  }, {} as Record<string, string>);

  return { ...FALLBACK_COLOURS, ...apiColours };
};

const getBackgroundColor = (
  hazardType: string,
  colours: Record<string, string>
) => colours[hazardType.toLowerCase()] ?? colours.default;

const transformToFileProperties = (item: any) => ({
  id: item.id,
  name: item.name,
  displayName: item.displayName,
  size: item.size,
  url: item.url,
  signedUrl: item.signedUrl,
  date: item.date,
  time: item.time,
  category: item.category,
});

const DataDisplayComponent = ({
  data,
  hazardsLibrary,
  createdAt,
  onUpdate,
  status,
  printPdf,
  barnLocation,
  siteCondition,
}: {
  data: JobSafetyBriefing;
  hazardsLibrary: Array<{ id: string; imageUrl: string }>;
  createdAt: string;
  onUpdate: (val: PageListItemType) => void;
  status: Status;
  printPdf: boolean;
  barnLocation: barnLocation;
  siteCondition: SharePageSiteConditionDetailsType[];
}) => {
  const { isManager } = useAuthStore();
  const taskIds = useMemo(
    () => flatten(data?.activities?.map(a => a.tasks.map(t => t.id))),
    [data.activities]
  );

  const { data: taskLib } = useQuery<{ tasksLibrary: TaskLib[] }>(
    TASKS_LIB_QUERY,
    {
      variables: { tasksLibraryId: taskIds },
    }
  );

  // Print functionality moved to page level - removed duplicate useEffect

  return (
    <div
      className={cx(
        {
          "overflow-auto p-2 sm:p-6 max-w-[764px] bg-white h-[calc(100vh-96px)] mb-8 pb-[120px] sm:pb-0":
            !printPdf,
        },
        "bg-white"
      )}
    >
      <SectionHeading className="text-2xl mb-4">
        Group Discussion
      </SectionHeading>
      <DateAndTimeSection
        barnLocationName={barnLocation?.name}
        date={new Date(createdAt)}
      />
      <LocationInfo
        locationInfo={data?.workLocationWithVoltageInfo}
        printPdf={printPdf}
      />
      <MedicalInformation medicalData={data?.medicalInformation} />
      <JobDescriptionSection
        description={get(data, "criticalTasksSelections.jobDescription")}
      />
      <EnergySourceControls energySourceControl={data?.energySourceControl} />
      <SiteConditions
        siteConditions={siteCondition}
        meta={{
          digSafe: data?.siteConditions?.digSafe,
          additionalComments: data?.siteConditions?.additionalComments,
        }}
      />
      <TasksSections
        activities={data?.activities}
        taskLib={taskLib?.tasksLibrary || []}
      />

      <>
        <Subheading className="text-lg font-semibold text-neutral-shade-75">
          Special Precautions
        </Subheading>
        <SectionWrapper>
          <BodyText className="font-medium mb-2">
            How can &quot;Human Factor Events&quot; be reduced?
          </BodyText>

          <ul className="list-disc list-inside pl-4 text-sm">
            <li>What documentation do we have in hand?</li>
            <li>How have we prepared for the job?</li>
            <li>Has the crew performed this job before?</li>
            <li>
              What questions do you have about our risk assessment and
              mitigation plan?
            </li>
            <li>
              In substandard conditions, what additional precautions, safeguards
              or barriers will be used?
            </li>
            <li>What steps have we taken to prevent soft tissue injuries?</li>
          </ul>
          <BodyText className="text-brand-gray-70 mt-2">Notes</BodyText>
          <textarea
            disabled={true}
            className="w-full h-24 border-2 rounded bg-white text-gray-400 p-2"
            value={data?.criticalTasksSelections?.specialPrecautionsNotes}
          />
        </SectionWrapper>
      </>

      <HighEnergyHazardsSection
        data={data}
        hazards={[
          ...(data?.hazardsControl?.tasks ?? []).reduce((acc, task) => {
            const critTasks =
              data?.criticalTasksSelections?.taskSelections || [];
            if (critTasks.some(c => c.id === task.id)) {
              acc = [...acc, ...task.highEnergyHazards];
            }
            return acc;
          }, [] as HighEnergyHazard[]),
          ...(data?.hazardsControl?.manuallyAddedHazards?.highEnergyHazards ||
            []),
        ]}
        hazardsLibrary={hazardsLibrary}
      />

      <OtherHazards
        data={data}
        hazards={[
          ...(data?.hazardsControl?.manuallyAddedHazards?.lowEnergyHazards ||
            []),
          ...(data?.hazardsControl?.customHazards?.lowEnergyHazards || []),
        ]}
        hazardsLibrary={hazardsLibrary}
        additionalComments={data?.hazardsControl?.additionalComments}
      />
      <DocumentsSection documentsData={data?.attachmentSection} />
      <HistoricalIncidents
        historicalIncidents={data?.taskHistoricIncidents}
        tasks={flatten(data?.activities?.map(a => a.tasks))}
        taskSelections={data?.criticalTasksSelections?.taskSelections || []}
      />
      <ReferenceMaterials
        referenceMaterial={data?.standardOperatingProcedure || []}
        generalReferenceMaterials={data?.generalReferenceMaterials || []}
        taskLib={taskLib?.tasksLibrary || []}
        taskSelections={data?.criticalTasksSelections?.taskSelections || []}
      />
      <CrewSignOff
        crewName={data?.crewSignOff?.crewSign}
        crewSign={data?.crewSignOff?.crewSign}
        creatorData={data?.crewSignOff?.creatorSign}
        status={status}
      />
      <PostJobBrief
        DiscussionItem={data?.postJobBrief?.discussionItems}
        postJobDiscussionNotes={data?.postJobBrief?.postJobDiscussionNotes}
      />
      <footer
        className={cx("flex flex-col mt-auto md:max-w-screen-lg items-end", {
          "p-4 px-0": !isMobile && !isTablet,
          "p-2.5 h-[54px]": isMobile || isTablet,
        })}
      >
        {status === Status.IN_PROGRESS || !isManager() ? null : (
          <button
            className="text-center truncate disabled:opacity-38 disabled:cursor-not-allowed 
               text-base rounded-md font-semibold text-white bg-brand-urbint-40
               px-2.5 py-2"
            type="button"
            onClick={() => onUpdate(dt)}
          >
            Supervisor Sign-Off
          </button>
        )}
      </footer>
      <div className="h-40" />
    </div>
  );
};

const DateAndTimeSection = ({
  date,
  barnLocationName,
}: {
  date: Date;
  barnLocationName?: string;
}) => {
  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Details
      </Subheading>
      <SectionWrapper>
        <div className="flex flex-grow">
          <div className="flex  flex-col flex-grow">
            <BodyText className="text-brand-gray-70  font-medium">
              Analysis Date
            </BodyText>
            <BodyText>
              {getFormattedDate(date ?? "", "numeric", "numeric", "numeric")}
            </BodyText>
          </div>
          <div className="flex  flex-col flex-grow">
            <BodyText className="text-brand-gray-70  font-medium">
              Analysis Time
            </BodyText>
            <BodyText>
              {date.toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
                hour12: true,
              })}
            </BodyText>
          </div>
        </div>
        <BodyText className="text-brand-gray-70 mt-2">Barn / Platform</BodyText>
        <BodyText className="text-xm">{barnLocationName}</BodyText>
      </SectionWrapper>
    </>
  );
};

const CommonSection = ({
  title,
  value,
}: {
  title: string;
  value?: string | null;
}) => (
  <div className="flex  flex-col flex-grow">
    <BodyText className="text-brand-gray-70  font-medium">{title}</BodyText>
    <BodyText>{value || "-"}</BodyText>
  </div>
);

const MedicalInformationSection = ({
  description = "",
  address = "",
  city = "",
  state = "",
  zip,
}: NearestHospitalType) => {
  return (
    <div className="flex flex-col flex-grow">
      <BodyText className="text-brand-gray-70 font-medium">
        Nearest hospital/Emergency response:
      </BodyText>
      <BodyText>{description}</BodyText>
      <BodyText>{address}</BodyText>
      <BodyText>{[city, state, zip].filter(Boolean).join(", ")}</BodyText>
    </div>
  );
};

const MedicalInformation = ({
  medicalData,
}: {
  medicalData: MedicalInformationType;
}) => {
  if (isEmpty(medicalData)) {
    return null;
  }
  const nearestHospital = medicalData.nearestHospital;
  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Medical and Emergency Information
      </Subheading>
      <SectionWrapper>
        <div className="flex flex-col gap-3">
          <CommonSection
            title={"Vehicle numbers"}
            value={medicalData?.vehicleNumber?.join(",")}
          />
          <MedicalInformationSection
            description={nearestHospital?.description}
            address={
              nearestHospital?.address ||
              medicalData.customMedicalNearestHospital?.address ||
              "-"
            }
            city={nearestHospital?.city}
            state={nearestHospital?.state}
            zip={nearestHospital?.zip}
          />
          <CommonSection
            title={"AED location:"}
            value={
              medicalData?.aedInformation?.aedLocationName ||
              (medicalData?.customAedLocation as any)?.address ||
              ""
            }
          />
          <CommonSection
            title={"First aid location"}
            value={
              medicalData?.firstAidKitLocation?.firstAidLocationName ||
              medicalData?.customFirstAidKitLocation?.address
            }
          />
          <CommonSection
            title={"Burn kit location"}
            value={
              medicalData?.burnKitLocation?.burnKitLocationName ||
              medicalData?.customBurnKitLocation?.address ||
              ""
            }
          />
          <CommonSection
            title={"Primary Fire Suppression Location"}
            value={
              medicalData?.primaryFireSupressionLocation
                ?.primaryFireSupressionLocationName ||
              medicalData?.customPrimaryFireSupressionLocation?.address ||
              ""
            }
          />
        </div>
      </SectionWrapper>
    </>
  );
};

const JobDescriptionSection = ({ description }: { description: string }) => {
  if (!description) {
    return null;
  }

  const formattedDescription = description.split("\n").map((line, index) => (
    <BodyText key={index}>
      {line}
      {index < description.split("\n").length - 1 && <br />}{" "}
    </BodyText>
  ));

  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Job Description
      </Subheading>
      <SectionWrapper>
        <div className="mt-2">
          <BodyText>{formattedDescription}</BodyText>
        </div>
      </SectionWrapper>
    </>
  );
};

const EnergySourceControls = ({
  energySourceControl,
}: {
  energySourceControl: EnergySourceControl;
}) => {
  if (isEmpty(energySourceControl)) {
    return null;
  }

  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Energy Source Controls
      </Subheading>
      <div className="flex flex-col gap-3">
        <SectionWrapper>
          <div className="flex flex-col gap-4">
            <BodyText className="text-brand-gray-70 font-medium">
              Type of work
            </BodyText>
            <div className="flex flex-row gap-3">
              <div
                className={cx(
                  "flex-grow flex p-2 justify-center rounded border-2 font-medium",
                  {
                    ["bg-brand-urbint-40 text-white "]:
                      energySourceControl.energized,
                    ["bg-white"]: !energySourceControl.energized,
                  }
                )}
              >
                Energized
              </div>
              <div
                className={cx(
                  "flex-grow flex p-2 justify-center rounded border-2 font-medium",
                  {
                    ["bg-brand-urbint-40 text-white "]:
                      energySourceControl.deEnergized,
                    ["bg-white"]: !energySourceControl.deEnergized,
                  }
                )}
              >
                De-energized
              </div>
            </div>

            <div>
              {map(energySourceControl.controls, control => (
                <div key={control.id} className="flex items-center gap-2">
                  <Checkbox id={String(control.id)} checked={true} />
                  <label htmlFor={control.name} className="font-normal">
                    {control.name}
                  </label>
                </div>
              ))}
            </div>
            <div className="flex flex-col gap-2 bg-white p-2">
              <div className="flex flex-col gap-4">
                <BodyText className="text-brand-gray-70 font-medium text-lg">
                  Points of protection
                </BodyText>
                {!isEmpty(energySourceControl.pointsOfProtection) &&
                  energySourceControl.pointsOfProtection.map(control => (
                    <div key={control.id} className="flex items-baseline gap-2">
                      <div className="relative top-0.5">
                        <Checkbox id={String(control.id)} checked={true} />
                      </div>
                      <BodyText className="font-normal flex">
                        <label
                          htmlFor={control.name}
                          className="text-brand-gray-70 font-medium"
                        >
                          {control.name}
                          {control.details && `: ${control.details}`}
                        </label>
                      </BodyText>
                    </div>
                  ))}
              </div>
            </div>

            <div className="flex flex-col gap-2 bg-white p-2">
              <BodyText className="text-brand-gray-70  font-medium text-lg mt-2">
                Clearance and Controls Provisions
              </BodyText>
              <div className="mt-2 flex flex-col gap-2">
                <div>
                  <BodyText className="text-brand-gray-70  font-medium">
                    Which clearance or de-energization method are you using for
                    this work?
                  </BodyText>
                  <BodyText>
                    {energySourceControl.clearanceTypes?.clearanceTypes}
                  </BodyText>
                </div>
                <div>
                  <BodyText className="text-brand-gray-70  font-medium">
                    Red Tag Name/Number
                  </BodyText>
                  <BodyText>{energySourceControl.clearanceNumber}</BodyText>
                </div>
                <div>
                  <ComponentLabel className="text-brand-gray-70  font-medium">
                    Describe controls
                  </ComponentLabel>
                  <BodyText>{energySourceControl.controlsDescription}</BodyText>
                </div>
              </div>
            </div>
          </div>
        </SectionWrapper>
      </div>
    </>
  );
};

const SiteConditions = ({
  siteConditions,
  meta,
}: {
  siteConditions: SharePageSiteConditionDetailsType[];
  meta: { digSafe: string; additionalComments: string };
  printPdf?: boolean;
}) => {
  // if (printPdf) {
  //   return <Loader />;
  // }
  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Site Conditions
      </Subheading>

      <SectionWrapper variant="compact">
        {(siteConditions || [])
          .filter(s => s.selected)
          .map(sc => (
            <TaskCard
              taskHeader={
                <div className="p-2">
                  <TaskHeader headerText={sc.name || ""} />
                </div>
              }
              key={sc.id}
              className={"border-[#3E70D4]"}
            ></TaskCard>
          ))}

        <div className="mt-2">
          <BodyText className="text-brand-gray-70 font-medium">
            Dig safe #
          </BodyText>
          <BodyText>{meta?.digSafe || "-"}</BodyText>
        </div>
        <div className="mt-2">
          <BodyText className="text-brand-gray-70 font-medium">
            Other site conditions and comments
          </BodyText>
          <BodyText>{meta?.additionalComments || "-"}</BodyText>
        </div>
      </SectionWrapper>
    </>
  );
};

const DocumentsSection = ({
  documentsData,
}: {
  documentsData: AttachmentSection;
}) => {
  if (isEmpty(documentsData)) {
    return null;
  }

  const photos = documentsData.photos
    ? documentsData.photos.map(transformToFileProperties)
    : [];

  const documents = documentsData.documents
    ? documentsData.documents.map(transformToFileProperties)
    : [];

  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Documents and Attachments
      </Subheading>
      <SectionWrapper>
        {!isEmpty(documentsData.documentsProvided) && (
          <div className="flex flex-col gap-2 bg-white p-4">
            <SectionHeading className="text-lg font-semibold text-neutral-shade-75">
              Documents provided
            </SectionHeading>
            {documentsData.documentsProvided.map(documentProvided => (
              <div key={documentProvided.id} className="flex flex-col gap-2">
                <div className="flex flex-row items-center gap-2">
                  <Checkbox id={String(documentProvided.id)} checked={true} />
                  <label
                    htmlFor={documentProvided.name}
                    className="text-brand-gray-70 font-medium"
                  >
                    {documentProvided.name}
                  </label>
                </div>
                {documentsData.descriptionDocumentProvided &&
                  documentProvided.name === "Other" && (
                    <>
                      <BodyText className="text-sm text-brand-gray-70 font-bold">
                        Other Information
                      </BodyText>
                      <p>{documentsData.descriptionDocumentProvided}</p>
                    </>
                  )}
              </div>
            ))}
          </div>
        )}
        <SectionHeading className="w-full text-xl font-semibold mt-4">
          Photos ({photos.length})
        </SectionHeading>
        {photos.length > 0 ? (
          <div className="flex flex-col gap-4 p-2">
            {photos.map(f => (
              <div key={f.name} className="flex flex-grow">
                <img src={f.signedUrl} alt={f.name} width="100%" />
              </div>
            ))}
          </div>
        ) : (
          <span className="font-normal text-base">No photos uploaded</span>
        )}
        <div className="w-full mt-3">
          <SectionHeading className="text-xl font-semibold">
            Documents ({documents.length})
          </SectionHeading>
          {documents.length > 0 ? (
            documents.map(f => (
              <div
                className="w-full flex flex-row flex-wrap justify-start items-start gap-4 p-2 border-neutral-shade-18 border rounded mb-2 bg-white"
                key={f.id}
              >
                <Icon name="file_blank_outline" className="text-2xl" />
                <div className="ml-2 flex-1 min-w-0">
                  <p className="text-sm font-semibold text-neutral-shade-100 break-all">
                    {f.displayName}
                  </p>
                  <p className="text-xs text-neutral-shade-58">
                    {[
                      f.size,
                      f.category || null,
                      f.date || null,
                      f.time || null,
                    ]
                      .filter(Boolean)
                      .join(" • ")}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <span className="font-normal text-base">No documents uploaded</span>
          )}
        </div>
      </SectionWrapper>
    </>
  );
};

const TasksSections = ({
  activities,
  taskLib,
}: {
  activities: Activity[];
  taskLib: TaskLib[];
}) => {
  if (isEmpty(activities)) {
    return null;
  }

  // Group activities by name
  const activitiesMap = activities.reduce((acc, activity) => {
    if (acc[activity.name]) {
      acc[activity.name].tasks = cloneDeep([
        ...acc[activity.name].tasks,
        ...activity.tasks,
      ]);
    } else {
      acc[activity.name] = cloneDeep(activity);
    }
    return acc;
  }, {} as Record<string, Activity>);

  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Tasks
      </Subheading>
      <SectionWrapper variant="compact">
        {map(activitiesMap, activity => (
          <div key={activity.name}>
            <BodyText className={"mb-1"}>{activity.name}</BodyText>
            {activity.tasks.map(task => (
              <TaskCard
                taskHeader={
                  <div className="p-2">
                    <TaskHeader
                      headerText={task.name}
                      riskLevel={convertRiskLevelToRiskBadgeRiskLevel(
                        upperCase(
                          taskLib.find(t => t.id === task.id)?.riskLevel ||
                            task.riskLevel
                        ) as RiskLevel
                      )}
                    />
                  </div>
                }
                key={task.id}
                className={getBorderColorByRiskLevel(
                  upperCase(
                    taskLib.find(t => t.id === task.id)?.riskLevel ||
                      task.riskLevel
                  ) as RiskLevel
                )}
              ></TaskCard>
            ))}
          </div>
        ))}
      </SectionWrapper>
    </>
  );
};

const moveHighEnergyHazards = (siteConditionData: any[]) => {
  const allHighEnergyHazards: any[] = [];
  siteConditionData?.forEach(siteCondition => {
    if (Array.isArray(siteCondition.highEnergyHazards)) {
      allHighEnergyHazards.push(...siteCondition.highEnergyHazards);
    }
  });

  return allHighEnergyHazards;
};

const HighEnergyHazardsSection = ({
  hazards,
  data,
}: {
  hazards: HighEnergyHazard[];
  hazardsLibrary: Array<{ imageUrl: string; id: string }>;
  data: JobSafetyBriefing;
}) => {
  const siteConditionData = data?.hazardsControl?.siteConditions;
  const highEnergyHazardsArray = moveHighEnergyHazards(siteConditionData);
  hazards.push(...highEnergyHazardsArray);
  const flattenedHazards = hazards.filter(
    (item): item is HighEnergyHazard => item && !Array.isArray(item)
  );

  const dedupedHazards: HighEnergyHazard[] = [];
  const hazardMap = new Map<string, HighEnergyHazard>();

  for (const hazard of flattenedHazards) {
    const hasCustomControls =
      (hazard.customControls?.controls ?? []).length > 0;
    if (hazardMap.has(hazard.id)) {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      const existingHazard = hazardMap.get(hazard.id)!;
      if (
        !existingHazard.customControls?.controls?.length &&
        hasCustomControls
      ) {
        hazardMap.set(hazard.id, hazard);
      }
    } else {
      hazardMap.set(hazard.id, hazard);
    }
  }
  dedupedHazards.push(...hazardMap.values());
  if (dedupedHazards.length === 0) return null;

  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        High Energy Hazards
      </Subheading>
      <SectionWrapper variant="compact">
        <OtherHazardsCard hazards={[...(dedupedHazards || [])]} />
      </SectionWrapper>
    </>
  );
};

const ReferenceMaterials = ({
  referenceMaterial,
  generalReferenceMaterials,
  taskLib,
  taskSelections,
}: {
  referenceMaterial: StandardOperatingProcedures;
  generalReferenceMaterials: {
    id: string;
    link: string;
    name: string;
  }[];
  taskLib: TaskLib[];
  taskSelections: JobSafetyBriefing["criticalTasksSelections"]["taskSelections"];
}) => {
  const groupedGeneral = useMemo(
    () => groupBy(generalReferenceMaterials, "category"),
    [generalReferenceMaterials]
  );
  const [openCategories, setOpenCategories] = useState<string[]>([]);
  const toggleCategory = (category: string) =>
    setOpenCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Reference Materials
      </Subheading>
      <SectionWrapper variant="compact">
        {referenceMaterial
          .filter(r => some(taskSelections, t => t.id === r.id))
          .map(r => (
            <div
              key={r.id}
              className="rounded bg-white mb-4 flex overflow-hidden"
            >
              <div
                className={`w-[10px] ${getBackgroundColorByRiskLevel(
                  upperCase(
                    taskLib.find(t => t.id === r.id)?.riskLevel || "UNKNOWN"
                  ) as RiskLevel
                )}`}
              ></div>
              <div className={"flex-1 p-2"}>
                <div className={"mb-2"}>
                  <Tooltip
                    title={
                      "The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed"
                    }
                    position="bottom"
                    className="max-w-xl"
                  >
                    <RiskBadge
                      risk={
                        upperCase(
                          taskLib.find(t => t.id === r.id)?.riskLevel ||
                            "UNKNOWN"
                        ) as any
                      }
                      label={
                        upperCase(
                          taskLib.find(t => t.id === r.id)?.riskLevel ||
                            "UNKNOWN"
                        ) as any
                      }
                    />
                  </Tooltip>
                </div>
                <BodyText className="font-medium mb-4">{r.name}</BodyText>
                {r.sops.map(sop => (
                  <div
                    key={sop.id}
                    className="p-4 bg-brand-gray-10 rounded border-black flex justify-between"
                    style={{ borderWidth: 1 }}
                  >
                    <NextLink
                      href={{
                        pathname: sop.link,
                      }}
                      passHref
                    >
                      <Link label={sop.name} allowWrapping />
                    </NextLink>
                    <CheckedIcon />
                  </div>
                ))}
              </div>
            </div>
          ))}
        {isEmpty(referenceMaterial) && (
          <CaptionText>No procedures is selected.</CaptionText>
        )}
        {!isEmpty(generalReferenceMaterials) && (
          <>
            <SectionHeading className="text-lg font-semibold text-neutral-shade-75 mt-2 mb-2">
              General Reference Materials
            </SectionHeading>

            {Object.entries(groupedGeneral).map(([category, items]) => {
              const isOpen = openCategories.includes(category);
              return (
                <div key={category} className="mb-2">
                  <button
                    onClick={() => toggleCategory(category)}
                    className="w-full flex justify-between items-center p-4 bg-white rounded border border-neutral-30"
                  >
                    <span className="font-semibold text-left">{category}</span>
                    <Icon
                      name={isOpen ? "chevron_down" : "chevron_right"}
                      style={{ fontSize: "28px" }}
                    />
                  </button>
                  {isOpen &&
                    items.map(item => (
                      <div
                        key={item.id}
                        className="p-4 bg-brand-gray-10 rounded border border-black flex justify-between mt-2"
                      >
                        <NextLink href={{ pathname: item.link }} passHref>
                          <Link label={item.name} allowWrapping />
                        </NextLink>
                        <CheckedIcon />
                      </div>
                    ))}
                </div>
              );
            })}
          </>
        )}
      </SectionWrapper>
    </>
  );
};

const HistoricalIncidents = ({
  historicalIncidents,
  tasks,
  taskSelections,
}: {
  historicalIncidents: JobSafetyBriefing["taskHistoricIncidents"];
  tasks: Task[];
  taskSelections: JobSafetyBriefing["criticalTasksSelections"]["taskSelections"];
}) => {
  if (isEmpty(historicalIncidents)) {
    return null;
  }

  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Historical Incidents
      </Subheading>
      <SectionWrapper>
        {(tasks || [])
          .filter(t => some(taskSelections, s => s.id === t.id))
          .map(task => (
            <HistoricalIncidentWrapper
              key={task.id}
              task={task}
              historicalIncidents={historicalIncidents}
            />
          ))}
      </SectionWrapper>
    </>
  );
};

const HistoricalIncidentWrapper = ({
  task,
  historicalIncidents,
}: {
  task: Task;
  historicalIncidents: JobSafetyBriefing["taskHistoricIncidents"];
}) => {
  const { data, loading } = useQuery(getHistoricIncidents, {
    variables: { libraryTaskId: task.id },
  });

  if (loading) {
    return <Loader />;
  }
  if (isEmpty(data)) {
    return null;
  }
  const individualTaskHistoricIncident = historicalIncidents?.filter(
    (h: HistoricIncidentType) => task.id === h.id
  );
  const allHistoricalIncidentofTask = data?.historicalIncidents;
  const hoistoricincidentsId =
    individualTaskHistoricIncident[0]?.historicIncidents?.filter(
      (value: string) =>
        allHistoricalIncidentofTask?.some(
          (incident: HistoricIncidents) => incident.id === value
        )
    );

  const incidents = data?.historicalIncidents?.filter(
    (val: HistoricIncidents) => hoistoricincidentsId?.includes(val.id)
  );

  if (isEmpty(incidents)) {
    return null;
  }

  return (
    <div className="p-4 rounded bg-white mt-2">
      <BodyText className="font-medium mb-4">{task.name}</BodyText>
      <div>
        {incidents.map((incident: Incident) => (
          <EboIncidentCard
            key={incident.id}
            incident={incident as unknown as Incident}
            selected={true}
            onSelect={() => {
              console.log("");
            }}
          />
        ))}
      </div>
    </div>
  );
};

export const hexToRgba = (
  hex: string,
  alpha = 1,
  lightenFactor = 0.2
): string => {
  const stripped = hex.replace("#", "");
  const bigint = parseInt(stripped, 16);

  let r = (bigint >> 16) & 255;
  let g = (bigint >> 8) & 255;
  let b = bigint & 255;

  r = Math.min(255, Math.floor(r + (255 - r) * lightenFactor));
  g = Math.min(255, Math.floor(g + (255 - g) * lightenFactor));
  b = Math.min(255, Math.floor(b + (255 - b) * lightenFactor));

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};
export const HazardGroupCard = ({
  energyType,
  hazards = [],
}: {
  energyType: string;
  hazards: any[];
}) => {
  const colours = useEnergyColours();
  const hazardColour = getBackgroundColor(energyType, colours);
  const pillBgColour = hexToRgba(hazardColour, 0.45, 2);
  const pillBorderColour = hexToRgba(hazardColour, 0.7, 0.4);
  if (!hazards.length) return null;
  return (
    <div className="bg-white rounded-lg shadow-md mb-3">
      <div
        style={{ backgroundColor: getBackgroundColor(energyType, colours) }}
        className="rounded-t-lg flex"
      >
        <div className="flex items-center ml-2">
          {energyType !== "unspecified" && (
            <Image
              src={`/assets/JSB/energy-types/${energyType}.png`}
              alt={energyType}
              width={20}
              height={20}
            />
          )}
        </div>
        <Subheading className="text-lg p-1.5 pl-2">
          {capitalize(energyType)}
        </Subheading>
      </div>
      <div className="p-3 flex flex-col gap-4">
        {hazards.map(hazard => {
          const controlsList = [
            ...(hazard.customControls?.controls ?? []),
            ...(hazard.controls?.controls ?? []),
          ];
          return (
            <div key={hazard.id} className="flex flex-col gap-1">
              <BodyText className="text-brand-gray-70 font-medium">
                {hazard.name}
              </BodyText>

              <BodyText className="text-brand-gray-70 font-medium">
                Controls
              </BodyText>

              {controlsList.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {controlsList.map((c: Control) => (
                    <span
                      key={c.id}
                      style={{
                        backgroundColor: pillBgColour,
                        borderColor: pillBorderColour,
                      }}
                      className="p-0.5 rounded border-2 mr-1 mb-1"
                    >
                      {c.name}
                    </span>
                  ))}
                </div>
              ) : (
                <BodyText className="text-brand-gray-70 text-sm">
                  No controls implemented
                </BodyText>
              )}

              <hr className="my-4 border-brand-gray-20" />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const OtherHazardsCard = ({ hazards }: { hazards: HazardList }) => {
  if (!hazards?.length) return null;
  const grouped: Record<string, typeof hazards> = {};
  hazards.forEach(h => {
    (grouped[h.energyTypes] ||= []).push(h);
  });
  return (
    <>
      {Object.entries(grouped).map(([energyType, list]) => (
        <HazardGroupCard
          key={energyType}
          energyType={energyType}
          hazards={list}
        />
      ))}
    </>
  );
};

const OtherHazards = ({
  hazards,
}: {
  hazards: Array<HighEnergyHazard | LowEnergyHazard>;
  hazardsLibrary: Array<{ id: string; imageUrl: string }>;
  additionalComments?: string;
  data: JobSafetyBriefing;
}) => {
  if (isEmpty(hazards)) {
    return null;
  }
  return (
    <>
      <Subheading className="text-lg font-semibold text-neutral-shade-75">
        Other hazards
      </Subheading>
      <SectionWrapper>
        <div className="flex flex-col gap-4">
          <OtherHazardsCard hazards={[...(hazards || [])]} />
        </div>
      </SectionWrapper>
    </>
  );
};

type SectionWrapperProps = {
  title?: string;
  variant?: "default" | "compact";
  children?: React.ReactNode; // Added children prop explicitly
};

const SectionWrapper: React.FC<SectionWrapperProps> = ({
  title,
  children,
  variant = "default",
}) => {
  const paddingClass = variant === "compact" ? "p-1" : "p-2";

  return (
    <FieldGroup className={`${paddingClass} mt-4 mb-4`}>
      {title && (
        <div className="flex justify-between">
          <SectionHeading className="text-lg font-semibold text-neutral-shade-75">
            {title}
          </SectionHeading>
        </div>
      )}
      <div>{children}</div>
    </FieldGroup>
  );
};

export { DataDisplayComponent };
