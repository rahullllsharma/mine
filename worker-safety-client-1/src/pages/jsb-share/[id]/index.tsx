import type { DocumentNode } from "@apollo/client";
import type { MarshalledDataType } from "@/types/jsbShare/jsbShare";
import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import type { EnergySourceControlsSectionData } from "@/components/forms/Jsb/GroupDiscussion/EnergySourceControlsSection";
import { useEffect } from "react";
import { useRouter } from "next/router";
import { BodyText, Icon, SectionSubheading } from "@urbint/silica";
import { DateTime } from "luxon";
import { isMobileOnly } from "react-device-detect";
import cx from "classnames";
import * as O from "fp-ts/lib/Option";
import { useLazyQuery } from "@apollo/client";
import * as AttachmentsSection from "@/components/forms/Jsb/GroupDiscussion/AttachmentsSection";
import * as WorkProceduresSection from "@/components/forms/Jsb/GroupDiscussion/WorkProceduresSection";
import * as EnergySourceControlsSection from "@/components/forms/Jsb/GroupDiscussion/EnergySourceControlsSection";
import * as JobInformationSection from "@/components/forms/Jsb/GroupDiscussion/JobInformationSection";
import * as CriticalRiskAreasSection from "@/components/forms/Jsb/GroupDiscussion/CriticalRiskAreasSection";
import * as MedicalEmergencySection from "@/components/forms/Jsb/GroupDiscussion/MedicalEmergencySection";
import * as ControlsSection from "@/components/forms/Jsb/GroupDiscussion/ControlsSection";
import { PPESection } from "@/components/forms/Jsb/GroupDiscussion/PPESection";
import ShareWidget from "@/components/forms/Jsb/ShareWidget";
import Loader from "@/components/shared/loader/Loader";
import { GroupDiscussionSection } from "@/components/forms/Basic/GroupDiscussionSection";
import { Card } from "@/components/forms/Basic/Card";
import siteConditionLibraryQuery from "@/graphql/queries/siteConditionLibrary.gql";
import { marshallData } from "@/utils/jsbShare";
import PageHeader from "@/components/layout/pageHeader/PageHeader";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import { ProjectDescriptionHeader } from "@/container/projectSummaryView/PojectDescriptionHeader";
import CrewSignOffSection from "@/components/forms/Jsb/GroupDiscussion/CrewSignOffSection";
import LinkComponent from "@/components/templatesComponents/LinkComponent";
import PageNotFound from "@/pages/404";
import { FieldGroup } from "@/components/shared/FieldGroup";
import Link from "@/components/shared/link/Link";
import taskLibraryQuery from "../../../../graphql/tasksLibrary.gql";
import projectLocationsQuery from "../../../../graphql/projectLocations.gql";
import * as file from "../../../../graphql/jsb.gql";
import OpenCard from "./utils/OpenCard";
import print from "./printpdf.module.scss";

const NETWORK_POLICY = "no-cache";
const STANDARD_PPE = [
  "Hard Hat",
  "Gloves",
  "Safety toe shoes",
  "Safety glasses",
  "Safety vest",
];

export default function JSBShareId() {
  const {
    query: { id, locationId, printPage },
  } = useRouter();

  const [fetchJsb, { data: jsbData, loading: isLoadingJsb }] = useLazyQuery(
    (file as unknown as { Jsb: DocumentNode }).Jsb,
    {
      fetchPolicy: NETWORK_POLICY,
    }
  );

  const [fetchProjectLocations, { data: projectLocationsData }] = useLazyQuery(
    projectLocationsQuery,
    {
      fetchPolicy: NETWORK_POLICY,
    }
  );

  const [
    fetchTasksLibrary,
    { data: tasksLibraryData, loading: isLoadingTasks },
  ] = useLazyQuery(taskLibraryQuery, {
    fetchPolicy: NETWORK_POLICY,
  });

  const [
    fetchSiteConditionsLibrary,
    { data: siteConditionsLibraryData, loading: isLoadingSiteConditions },
  ] = useLazyQuery(siteConditionLibraryQuery, {
    fetchPolicy: NETWORK_POLICY,
  });

  useEffect(() => {
    if (id) {
      fetchJsb({ variables: { id } });
    }
  }, [id, fetchJsb]);

  useEffect(() => {
    if (locationId) {
      fetchProjectLocations({ variables: { id: locationId } });
    }
  }, [locationId, fetchProjectLocations]);

  useEffect(() => {
    fetchTasksLibrary();
    fetchSiteConditionsLibrary();
  }, [fetchTasksLibrary, fetchSiteConditionsLibrary]);

  const isLoading = isLoadingJsb || isLoadingTasks || isLoadingSiteConditions;
  const jsb = jsbData?.jobSafetyBriefing || {};
  const projectLocations = projectLocationsData?.projectLocations || [];
  const tasksLibrary = tasksLibraryData?.tasksLibrary || [];
  const siteConditionsLibrary =
    siteConditionsLibraryData?.siteConditionsLibrary || [];

  const missingParams = !id;
  const invalidData = !jsb.id;

  if (isLoading) {
    return <Loader />;
  }

  if (missingParams || invalidData) {
    return <PageNotFound />;
  }

  const data = marshallData(
    jsb.contents,
    locationId && projectLocations.length ? projectLocations[0] : null,
    tasksLibrary,
    siteConditionsLibrary
  );

  return (
    <>
      {jsb ? (
        <div className="flex flex-col items-center bg-brand-gray-10">
          <div className="w-full flex flex-col items-center overflow-scroll">
            {printPage ? (
              <DataDisplayComponent
                data={data}
                updatedAt={DateTime.fromISO(jsb.updatedAt)}
                printPdf={!!printPage}
                id={id as string}
                locationId={locationId as string}
              />
            ) : (
              <MarshalledDataDisplay
                data={data}
                updatedAt={DateTime.fromISO(jsb.updatedAt)}
                id={id as string}
                locationId={locationId as string}
              />
            )}
          </div>
        </div>
      ) : (
        <Loader />
      )}
    </>
  );
}

const DataDisplayComponent = ({
  data,
  updatedAt,
  printPdf,
  id,
  locationId,
}: {
  data: MarshalledDataType;
  updatedAt: DateTime;
  printPdf: boolean;
  id: string;
  locationId: string;
}) => {
  useEffect(() => {
    if (printPdf) {
      const originalBodyStyle = document.body.style.overflowY;
      const nextElement = document.getElementById("__next");
      const headerElement = document.querySelector("header");
      const originalNextStyle = nextElement?.style.height || "";

      const handleImageLoad = () => {
        const images = document.querySelectorAll("img");
        const allImagesLoaded = Array.from(images).every(img => img.complete);

        if (allImagesLoaded) {
          window.print();
        }
      };

      const handlePageLoad = () => {
        if (headerElement) headerElement.style.display = "none";

        document.body.style.overflowY = "auto";
        if (nextElement) {
          nextElement.style.height = "auto";
          nextElement.style.position = "static";
        }

        handleImageLoad();
        const images = document.querySelectorAll("img");
        images.forEach(img => {
          if (!img.complete) {
            img.addEventListener("load", handleImageLoad);
            img.addEventListener("error", handleImageLoad);
          }
        });

        return () => {
          document.body.style.overflowY = originalBodyStyle;
          if (nextElement) nextElement.style.height = originalNextStyle;
          if (headerElement) headerElement.style.display = "block";
          images.forEach(img => {
            img.removeEventListener("load", handleImageLoad);
            img.removeEventListener("error", handleImageLoad);
          });
        };
      };

      if (document.readyState === "complete") {
        handlePageLoad();
      } else {
        window.addEventListener("load", handlePageLoad);
      }

      return () => {
        window.removeEventListener("load", handlePageLoad);
      };
    }
  }, []);

  const isNonEmptyValue = (value: any): boolean => {
    if (Array.isArray(value)) {
      return value.length > 0;
    } else if (O.isSome(value)) {
      return true;
    }
    return false;
  };

  const checkNullValuesEnergySource = (
    energyData: EnergySourceControlsSectionData
  ): boolean => {
    return Object.values(energyData).some(isNonEmptyValue);
  };

  const { query } = useRouter();
  const isAdhocJSB = !Boolean(query.locationId);
  const groupDiscussionLabelName = isAdhocJSB
    ? "JSB Summary"
    : "Group Discussion";

  const humanTraffickingHotline = "1-888-373-7888";
  return data.marshalled ? (
    <div
      className={cx(
        {
          "overflow-auto p-6 max-w-[764px] bg-white h-[calc(100vh-96px)] mt-4 mb-8":
            !printPdf,
        },
        print.document
      )}
    >
      {printPdf && (
        <div className={cx(print.linkComponentParent, "mt-5")}>
          <LinkComponent
            href={`/jsb?locationId=${locationId || ""}&jsbId=${id}`}
            labelName={"Go Back"}
          />
        </div>
      )}

      {printPdf && <DetailsPageHeader data={data} />}

      <SectionSubheading className="font-medium text-[22px]">
        {groupDiscussionLabelName}
      </SectionSubheading>
      <div className="flex pb-4">
        <BodyText>
          The information below is to support the team read out. If any
          information needs to be updated, you can still make edits to this
          information by navigating back to the section.
        </BodyText>
        <ShareWidget withAction={false} />
      </div>
      <div className="text-xs font-normal text-neutral-shade-75 mt-0.5">
        {`Last updated at: ${updatedAt.toLocaleString(
          DateTime.DATE_HUGE
        )}, ${updatedAt.toLocaleString(DateTime.TIME_WITH_SHORT_OFFSET)}`}
      </div>
      <div className="flex flex-col gap-4">
        <JobInformationSection.View {...data.jobInformationData} />
        <MedicalEmergencySection.View {...data.medicalEmergencyData} />
        <div className="page-break"></div>

        {printPdf ? (
          data.tasksSectionData.length > 0 ? (
            <GroupDiscussionSection title="Tasks">
              <div className="flex flex-col gap-4">
                {data.tasksSectionData.map(task => (
                  <OpenCard
                    key={task.id}
                    name={task.name}
                    riskLevel={task.riskLevel}
                    hazards={task.hazards}
                  />
                ))}
              </div>
            </GroupDiscussionSection>
          ) : null
        ) : (
          <GroupDiscussionSection title="Tasks">
            <div className="flex flex-col gap-4">
              {data.tasksSectionData.map(task => (
                <Card
                  key={`${task.id}`}
                  name={task.name}
                  riskLevel={task.riskLevel}
                  hazards={task.hazards}
                />
              ))}
            </div>
          </GroupDiscussionSection>
        )}

        {printPdf ? (
          data.criticalRisksData.risks.length ? (
            <CriticalRiskAreasSection.View {...data.criticalRisksData} />
          ) : null
        ) : (
          <CriticalRiskAreasSection.View {...data.criticalRisksData} />
        )}

        {printPdf ? (
          checkNullValuesEnergySource(data.energySourceControlsData) ? (
            <EnergySourceControlsSection.View
              {...data.energySourceControlsData}
            />
          ) : null
        ) : (
          <EnergySourceControlsSection.View
            {...data.energySourceControlsData}
          />
        )}

        {printPdf ? (
          data.workProceduresData.workProcedures.length > 0 ? (
            <WorkProceduresSection.View {...data.workProceduresData} />
          ) : null
        ) : (
          <WorkProceduresSection.View {...data.workProceduresData} />
        )}

        <div className="page-break"></div>

        {printPdf ? (
          data.siteConditionsData.length > 0 ? (
            <GroupDiscussionSection title="Site Conditions">
              <div className="flex flex-col gap-4">
                {data.siteConditionsData.map(siteCondition => (
                  <OpenCard
                    key={siteCondition.id}
                    name={siteCondition.name}
                    hazards={siteCondition.hazards}
                  />
                ))}
              </div>
            </GroupDiscussionSection>
          ) : null
        ) : (
          <GroupDiscussionSection title="Site Conditions">
            <div className="flex flex-col gap-4">
              {data.siteConditionsData.map(siteCondition => (
                <Card
                  key={siteCondition.id}
                  name={siteCondition.name}
                  hazards={siteCondition.hazards}
                />
              ))}
            </div>
          </GroupDiscussionSection>
        )}

        {printPdf ? (
          data.controlsData.notes != "" ? (
            <ControlsSection.View {...data.controlsData} />
          ) : null
        ) : (
          <ControlsSection.View {...data.controlsData} />
        )}

        {printPdf ? (
          data.ppeData.directControl.length > 0 ? (
            <PPESection {...data.ppeData} />
          ) : (
            <div className="bg-white p-4">
              <BodyText className="text-base font-semibold text-neutral-shade-75 mb-2">
                Standard Required PPE
              </BodyText>
              <div className="flex flex-wrap gap-1">
                {STANDARD_PPE.map(item => (
                  <span
                    key={item}
                    className="bg-brand-urbint-10 border rounded border-brand-urbint-30 px-1.5 py-0.5 text-base font-normal text-neutral-shade-100"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )
        ) : (
          <PPESection {...data.ppeData} />
        )}

        <AttachmentsSection.View {...data.attachmentsData} />

        <FieldGroup>
          <div className="p-4 flex flex-col gap-3 bg-brand-gray-10">
            <div className="bg-white p-4 flex flex-col justify-center items-center gap-2">
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
        </FieldGroup>
        {printPdf ? (
          <CrewSignOffSection crewSignOffData={data.crewSignOffData} />
        ) : null}
      </div>
      <div className="h-40" />
    </div>
  ) : null;
};

const DetailsPageHeader = ({ data }: { data: MarshalledDataType }) => {
  return data.marshalled ? (
    <PageHeader className="w-full">
      <div className="w-full flex flex-row justify-between">
        <div className="flex flex-col w-full">
          <div className="flex w-full items-center">
            <h4 className="text-neutral-shade-100 mr-3 font-normal">
              Job Safety Briefing
            </h4>
            <span className="inline-flex items-center">
              <RiskBadge
                risk={data.headerData.risk as RiskLevel}
                label={data.headerData.risk}
              />
            </span>
          </div>
          <h3 className="block text-sm text-neutral-shade-58">
            {data.headerData.subTitle}
          </h3>
          <div className="mt-3 w-full">
            <ProjectDescriptionHeader
              maxCharacters={isMobileOnly ? 35 : 80}
              description={data.headerData.description}
            />
          </div>
        </div>
      </div>
    </PageHeader>
  ) : null;
};

function MarshalledDataDisplay({
  data,
  updatedAt,
  id,
  locationId,
}: {
  data: MarshalledDataType;
  updatedAt: DateTime;
  id: string;
  locationId: string;
}) {
  return data.marshalled ? (
    <>
      <DetailsPageHeader data={data} />
      <DataDisplayComponent
        data={data}
        updatedAt={updatedAt}
        printPdf={false}
        id={id}
        locationId={locationId}
      />
    </>
  ) : null;
}
