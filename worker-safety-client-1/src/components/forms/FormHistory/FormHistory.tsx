import type {
  AuditData,
  Field,
  FormHistoryProps,
  Section,
} from "./FormHistoryType";
import React from "react";
import { capitalize } from "lodash-es";
import router from "next/router";
import { BodyText } from "@urbint/silica";
import { getFormattedDateTimeForFormAudits } from "@/utils/date/helper";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import AuditCard from "@/components/layout/auditTrail/auditCard/AuditCard";
// import { InputRaw } from "../Basic/Input";
import styles from "../../shared/loader/Loader.module.css";
import NestedSection from "./NestedSection";
import RenderFields from "./RenderFields";

const getHistoryEventName = (eventData: AuditData) => {
  if (!eventData || !eventData.object_type) return null;

  const eventMapping: { [key: string]: string } = {
    jsb: "a Job Safety Briefing",
    ebo: "an Energy Based Observation",
    dir: "a Daily Inspection Report",
    cwf: "a Custom Work Flow",
  };

  return eventMapping[eventData.object_type];
};

export const getFormattedEventType = (eventType: string) => {
  if (!eventType) return null;

  const verb = eventType === "create" ? "Add" : eventType;
  const formattedVerb = capitalize(
    verb.endsWith("e") ? `${verb}d` : `${verb}ed`
  );

  return formattedVerb;
};

// Skipping the sections and fields that are not structured yet & showing only the section headings
export const tempMutation = {
  sectionsToBeSkipped: [
    "Source Info",
    "Group Discussion",
    "Completions",
    "Recommended Task Selections",
    "Work Package Metadata",
    "Summary",
  ],

  fieldsToBeSkipped: [
    "State",
    "City",
    "Primary",
    "Signed Url",
    "Display Name",
    "Size",
    "Url",
    "Id",
    "Jsb Id",
    "SHA_256",
    "Recommended",
    "Selected",
    "Metadata",
    "Completed By Id",
    "Mimetype",
    "Md5",
    "Crc32c",
    "Employee Number",
    "Email",
    "External Id",
    "Manager Email",
    "Manager Id",
    "Company Name",
    "Department",
    "Job Title",
    "Manager Name",
    "Transfer Of Control",
    "Hazard Control Connector Id",
    "Instance Id",
    "Task Hazard Connector Id",
    "Activity Id",
    "Risk Level",
    "From Work Order",
    "Full Name",
    "Remote",
    "Control Ids",
    "Hazard Id",
    "Hazards And Controls Notes",
    "Heca Score Hazard Percentage",
    "Heca Score Task Percentage",
    "Heca Score Hazard",
    "Heca Score Task",
  ],
};

const LoaderForAuditHistory = () => {
  return (
    <div className="flex items-center justify-center h-full">
      <div>
        <div className={styles["urb-ripple"]}>
          <div></div>
          <div></div>
        </div>
      </div>
      <span className={styles["urbint-brand-title"]}>Urbint</span>
    </div>
  );
};

const RenderEmptyState = () => {
  return (
    <div className="flex-1 w-full h-full flex justify-center items-center">
      <EmptyContent
        title="You currently have no history"
        description="An audit trail will appear here once updates are made to this form"
      />
    </div>
  );
};

export const shouldRenderNestedSections = (section: Section) => {
  if (tempMutation.sectionsToBeSkipped.includes(section.name)) {
    return false;
  }

  const filteredSections =
    section.sections?.filter(
      subSection => !tempMutation.sectionsToBeSkipped.includes(subSection.name)
    ) || [];

  const filteredFields =
    section.fields?.filter(
      field => !tempMutation.fieldsToBeSkipped.includes(field.name)
    ) || [];

  const hasFilteredContent =
    filteredSections.length > 0 || filteredFields.length > 0;

  return hasFilteredContent;
};

export const getFilteredFields = (fields: Field[]) => {
  if (fields.length === 0) return [];
  return fields.filter(
    field =>
      !tempMutation.fieldsToBeSkipped
        .map(fieldName => fieldName.toLowerCase())
        .includes(field.name.toLowerCase())
  );
};

export function FormHistory({
  data: originalData,
  isAuditDataLoading,
  location = "",
}: FormHistoryProps): JSX.Element {
  const routeHandler = router.query;
  const isFormAdhoc = !routeHandler.locationId;

  // TODO: Hiding the Audit History Search bar until the feature is implemented
  // const handleInputChange = () => {
  //   console.log("Debounced input value for search bar");
  // };

  const shouldShowEmptyState = !originalData?.length;

  return (
    <div className="md:pl-2 flex-1 overflow-hidden max-w-screen-lg bg-white h-full flex flex-col">
      <div className="p-4 sticky top-0 bg-white z-10">
        <h6 className="leading-7 pb-1">History</h6>
        <BodyText className="text-neutral-shade-38 leading-5 text-sm">
          Monitor updates made to your form
        </BodyText>
        {/* Hiding the Audit History Search bar until the feature is implemented */}
        {/* <div className="md:w-96">
          <InputRaw
            placeholder="Search audit history"
            icon="search"
            onChange={handleInputChange}
            clearIcon
          />
        </div> */}
      </div>
      <div className="flex-1 overflow-auto px-4 pb-4">
        {isAuditDataLoading ? (
          <LoaderForAuditHistory />
        ) : shouldShowEmptyState ? (
          <RenderEmptyState />
        ) : (
          originalData.map((audit: AuditData) => {
            const isCreateOrCompleteEvent =
              audit.event_type === "create" || audit.event_type === "complete";
            const isDeleteOrReopenEvent =
              audit.event_type === "delete" || audit.event_type === "reopen";
            return (
              <div key={audit.id}>
                {isCreateOrCompleteEvent ? (
                  <div>
                    <AuditCard
                      username={audit.created_by}
                      userRole={audit.role}
                      timestamp={getFormattedDateTimeForFormAudits(
                        audit.created_at
                      )}
                      location={isFormAdhoc ? "" : location}
                    >
                      <div>
                        <NestedSection
                          sections={audit.sections ?? []}
                          title={
                            <BodyText className="flex gap-1">
                              {getFormattedEventType(audit.event_type)}
                              <BodyText className="font-semibold">
                                {getHistoryEventName(audit)}
                              </BodyText>
                            </BodyText>
                          }
                          level={0}
                          fields={getFilteredFields(audit.fields ?? [])}
                        />
                      </div>
                    </AuditCard>
                  </div>
                ) : isDeleteOrReopenEvent ? (
                  <div className="pt-3">
                    <AuditCard
                      username={audit.created_by}
                      userRole={audit.role}
                      timestamp={getFormattedDateTimeForFormAudits(
                        audit.created_at
                      )}
                      location={isFormAdhoc ? "" : location}
                    >
                      <BodyText className="flex gap-1">
                        {getFormattedEventType(audit.event_type)}
                        <BodyText className="font-semibold">
                          {getHistoryEventName(audit)}
                        </BodyText>
                      </BodyText>
                    </AuditCard>
                  </div>
                ) : (
                  <>
                    {audit.fields &&
                      getFilteredFields(audit.fields)?.length !== 0 &&
                      audit.sections?.length === 0 && (
                        <AuditCard
                          username={audit.created_by}
                          userRole={audit.role}
                          timestamp={getFormattedDateTimeForFormAudits(
                            audit.created_at
                          )}
                          location={isFormAdhoc ? "" : location}
                        >
                          <RenderFields
                            fields={getFilteredFields(audit.fields ?? [])}
                            level={0}
                          />
                        </AuditCard>
                      )}
                    {audit.sections
                      ?.filter(
                        section =>
                          !tempMutation.sectionsToBeSkipped.includes(
                            section.name
                          )
                      )
                      .map((section: Section) => (
                        <div key={audit.id} className="pt-3">
                          <AuditCard
                            username={audit.created_by}
                            userRole={audit.role}
                            timestamp={getFormattedDateTimeForFormAudits(
                              audit.created_at
                            )}
                            location={isFormAdhoc ? "" : location}
                          >
                            {shouldRenderNestedSections(section) ? (
                              <>
                                <NestedSection
                                  sections={section.sections ?? []}
                                  title={
                                    <BodyText className="flex gap-1">
                                      {getFormattedEventType(
                                        section.operation_type
                                      )}
                                      <BodyText className="font-semibold">
                                        {section.name}
                                      </BodyText>
                                    </BodyText>
                                  }
                                  level={0}
                                  fields={section.fields ?? []}
                                />
                                <RenderFields
                                  fields={getFilteredFields(audit.fields ?? [])}
                                  level={0}
                                />
                              </>
                            ) : (
                              <div className="flex items-center">
                                <BodyText>
                                  {getFormattedEventType(
                                    section.operation_type
                                  )}
                                </BodyText>
                                <BodyText className="font-semibold pl-1">
                                  {section.name}
                                </BodyText>
                              </div>
                            )}
                          </AuditCard>
                        </div>
                      ))}
                  </>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default FormHistory;
