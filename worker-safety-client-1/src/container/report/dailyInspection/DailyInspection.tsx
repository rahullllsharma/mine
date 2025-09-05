import type { Contractor } from "@/types/project/Contractor";
import type {
  DailyReport as DailyInspectionReportType,
  DailyReportUpdateData,
} from "@/types/report/DailyReport";
import type { JobHazardAnalysisGraphQLPayloadParams } from "../jobHazardAnalysis/transformers/graphQLPayload";
import type { WorkScheduleProps } from "../workSchedule/WorkSchedule";
import type { WorkScheduleGraphQLPayloadParams } from "../workSchedule/transformers/graphQLPayload";
import type {
  DailyInspectionReport,
  DailyInspectionReportForms,
  DailyInspectionReportMultiStep,
  DailyInspectionReportSectionKeys,
  DailyInspectionReportStepProps,
} from "./types";
import type {
  DailyInspectionReportResettableSections,
  DailyReportResponse,
} from "./utils";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { SiteCondition } from "@/api/generated/types";
import Head from "next/head";
import { isEqual, pick, uniqBy } from "lodash-es";
import router from "next/router";
import { useEffect, useState, useContext } from "react";
import { useMutation, useQuery } from "@apollo/client";
import { SourceAppInformation } from "@/api/generated/types";

import PageLayout from "@/components/layout/pageLayout/PageLayout";
import { jobHazardAnalysisFormInputPrefix } from "@/components/report/jobReport/JobReportCard";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import saveDailyReport from "@/graphql/mutations/dailyReport/saveDailyReport.gql";
import updateDailyReportStatus from "@/graphql/mutations/dailyReport/updateDailyReportStatus.gql";
import getContractors from "@/graphql/queries/contractors.gql";
import LocationSiteConditions from "@/graphql/queries/siteConditions.gql";
import LocationTasks from "@/graphql/queries/tasks.gql";
import { orderByName } from "@/graphql/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { DailyReportStatus } from "@/types/report/DailyReportStatus";
import {
  convertDateToString,
  getFormattedLocaleDateTime,
} from "@/utils/date/helper";
import { getUpdatedRouterQuery } from "@/utils/router";
import { stripTypename } from "@/utils/shared";
import { transformTasksToListTasks } from "@/utils/task";
import { FormHistory } from "@/components/forms/FormHistory/FormHistory";
import { FormViewTabStates } from "@/components/forms/Utils";
import useRestMutation from "@/hooks/useRestMutation";
import { config } from "@/config";
import axiosRest from "@/api/restApi";
import { messages } from "@/locales/messages";
import packageJson from "package.json";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";
import AdditionalInformation from "../additionalInformation/AdditionalInformation";
import Crew from "../crew/Crew";
import crewGraphQLPayload from "../crew/transformers/graphQLPayload";
import JobHazardAnalysis from "../jobHazardAnalysis/JobHazardAnalysis";
import jobHazardAnalysisGraphQLPayload from "../jobHazardAnalysis/transformers/graphQLPayload";
import SafetyAndCompliance from "../safetyAndCompliance/SafetyAndCompliance";
import Tasks, { taskFormInputPrefix } from "../tasks/Tasks";
import { transformGraphQLPayload as tasksGraphQLPayload } from "../tasks/utils";
import WorkSchedule, {
  workScheduleFormInputPrefix,
} from "../workSchedule/WorkSchedule";
import workScheduleGraphQLPayload from "../workSchedule/transformers/graphQLPayload";

import { MultiStepFormProvider } from "../multiStepForm/MultiStepForm";
import MultiStep from "../multiStepForm/components/multiStep/MultiStep";
import {
  useMultiStepActions,
  useMultiStepState,
} from "../multiStepForm/hooks/useMultiStep";

import Attachments from "../attachments/Attachments";
import DailyInspectionPageHeader from "./components/dailyInspectionPageHeader/DailyInspectionPageHeader";
import SaveAndCompleteModal from "./components/saveAndCompleteModal/SaveAndCompleteModal";
import {
  applyDefaultsToArrayFields,
  applyRecommendationsToSections,
  defaultSectionIsValidPropBySections,
  getActivityTaskName,
  getStartDateTimeFromSavedReport,
  getWorkScheduleStartDateTime,
  getDailyReportMetadataWithCompletedSections as mergeDailyReportCompletedSectionsWithMetadata,
  preserveDailyReportSections,
  revalidateSectionsBySection,
  shallowReplaceUrlWithPath,
} from "./utils";

const { version: appVersion } = packageJson;

const dailySourceInfo = {
  sourceInformation: SourceAppInformation.WebPortal,
  appVersion: appVersion,
};

const getMetadata = (): DailyInspectionReportMultiStep[] => [
  {
    id: workScheduleFormInputPrefix,
    name: "Work Schedule",
    path: "#work-schedule",
    transformFormDataToSchema: (formData: WorkScheduleGraphQLPayloadParams) =>
      workScheduleGraphQLPayload(formData),
    Component: function WorkScheduleSection({
      project,
      dailyReport,
      defaults: { projectSummaryViewDate },
    }: DailyInspectionReportStepProps) {
      // Format and convert all DATES to the user's locale settings.
      // Project start/end date also need to be converted so the limits are
      // adjusted to the user's settings.
      const projectStartDate = getFormattedLocaleDateTime(
        project.startDate.replace(/-/g, "/") // https://stackoverflow.com/a/31732581
      );

      const projectEndDate = getFormattedLocaleDateTime(
        project.endDate.replace(/-/g, "/") // https://stackoverflow.com/a/31732581
      );
      const defaultProjectDate = getFormattedLocaleDateTime(
        projectSummaryViewDate?.replace(/-/g, "/") // https://stackoverflow.com/a/31732581
      );

      const { endDatetime, startDatetime } =
        dailyReport?.sections?.[workScheduleFormInputPrefix] || {};

      return (
        <WorkSchedule
          startDatetime={
            startDatetime
              ? getFormattedLocaleDateTime(startDatetime)
              : defaultProjectDate
          }
          endDatetime={
            endDatetime
              ? getFormattedLocaleDateTime(endDatetime)
              : defaultProjectDate
          }
          dateLimits={{ projectStartDate, projectEndDate }}
          isCompleted={true}
        />
      );
    },
  },
  {
    id: taskFormInputPrefix,
    name: getActivityTaskName(),
    path: "#tasks",
    transformFormDataToSchema: (
      formData: Required<Pick<DailyInspectionReportForms, "taskSelection">>,
      options
    ) => tasksGraphQLPayload(formData, options),
    Component: function TasksSection({
      location,
      dailyReport,
      defaults: { projectSummaryViewDate = convertDateToString() },
    }: DailyInspectionReportStepProps) {
      const {
        [workScheduleFormInputPrefix]: workSchedule,
        [taskFormInputPrefix]: taskSelection,
      } = dailyReport?.sections || {};

      const { startDatetime = "" } = workSchedule || {};

      // TODO: On read-only view, completed view, we shouldn't need to request this (again)
      // But we only store ids for the tasks selection
      const { data = [] } = useQuery(LocationTasks, {
        // We may need to understand what's the better usage for this.
        fetchPolicy: "cache-and-network",
        variables: {
          locationId: location.id,
          date: startDatetime
            ? convertDateToString(startDatetime)
            : projectSummaryViewDate,
        },
      });
      const tasks = data.tasks || [];

      return (
        <Tasks
          tasks={transformTasksToListTasks(tasks, taskSelection?.selectedTasks)}
          isCompleted={true}
        />
      );
    },
  },
  {
    id: jobHazardAnalysisFormInputPrefix,
    name: `${
      useTenantStore.getState().getAllEntities().control.labelPlural
    } Assessment`,
    path: "#job-hazard-analysis",
    transformFormDataToSchema: (
      formData: Required<Pick<DailyInspectionReportForms, "jobHazardAnalysis">>
    ) =>
      jobHazardAnalysisGraphQLPayload(formData, {
        withDefaultControlValue: false,
      }),
    Component: function JobHazardAnalysisSection({
      location: { id, tasks },
      dailyReport,
      defaults: { projectSummaryViewDate = convertDateToString() },
    }: DailyInspectionReportStepProps) {
      const {
        [workScheduleFormInputPrefix]: workSchedule,
        [taskFormInputPrefix]: taskSelection,
        [jobHazardAnalysisFormInputPrefix]: jobHazardAnalysis,
      } = dailyReport?.sections || {};

      const availableTasks = tasks.filter(task =>
        taskSelection?.selectedTasks.some(
          ({ id: selectedId }) => selectedId === task.id
        )
      );

      const { startDatetime = "" } = workSchedule || {};

      const { data = [] } = useQuery(LocationSiteConditions, {
        fetchPolicy: "cache-and-network",
        variables: {
          locationId: id,
          date: startDatetime
            ? convertDateToString(new Date(startDatetime))
            : projectSummaryViewDate,
          isApplicable: true,
          controlsIsApplicable: true,
        },
      });
      const siteConditions =
        dailyReport?.status === DailyReportStatus.COMPLETE
          ? uniqBy(
              [
                ...(jobHazardAnalysis?.siteConditions || []),
                ...(data?.siteConditions || []),
              ],
              "id"
            )
          : data?.siteConditions || [];
      return (
        <JobHazardAnalysis
          tasks={availableTasks}
          siteConditions={siteConditions}
          defaultValues={jobHazardAnalysis}
          isCompleted={true}
        />
      );
    },
  },
  {
    id: "safetyAndCompliance",
    name: "Safety And Compliance",
    path: "#safety-and-compliance",
    Component: function SafetyAndComplianceSection() {
      return <SafetyAndCompliance isCompleted={true} />;
    },
  },
  {
    id: "crew",
    name: "Crew",
    path: "#crew",
    transformFormDataToSchema: (formData: any) => crewGraphQLPayload(formData),
    Component: function CrewSection() {
      const { data } = useQuery<{ contractors: Contractor[] }>(getContractors, {
        variables: {
          orderBy: [orderByName],
        },
      });
      return <Crew companies={data?.contractors} isCompleted={true} />;
    },
  },
  {
    id: "additionalInformation",
    name: "Additional Information",
    path: "#additional-information",
    Component: function AdditionalInformationSection() {
      return <AdditionalInformation isCompleted={true} />;
    },
  },
  {
    id: "attachments",
    name: "Attachments",
    path: "#attachments",
    Component: function AttachmentsSection() {
      return <Attachments isCompleted={true} />;
    },
  },
];

/**
 * The Daily Inspection Report component.
 *
 * @returns {JSX.Element}
 */
function DailyReport(props: DailyInspectionReport): JSX.Element {
  const {
    project,
    location,
    dailyReport: storedDailyReport,
    projectSummaryViewDate,
  } = props;
  const { markCurrentAs, markSectionsAs, moveForward } = useMultiStepActions();
  const { current, steps } = useMultiStepState();
  const toastCtx = useContext(ToastContext);
  const [selectedTab, setSelectedTab] = useState<FormViewTabStates>(
    FormViewTabStates.FORM
  );
  const [dirFormAuditData, setDirFormAuditData] = useState<[]>([]);

  /**
   * Store the default or updated daily report.
   * This will only include SUCCESSFULLY states and ALWAYS IN SYNC with database.
   */
  const [dailyReport, setDailyReport] = useState<
    DailyInspectionReportType | undefined
  >(storedDailyReport);

  const { data: locationSiteConditions = [] } = useQuery(
    LocationSiteConditions,
    {
      fetchPolicy: "cache-and-network",
      variables: {
        locationId: location.id,
        date: dailyReport?.sections?.workSchedule?.startDatetime
          ? convertDateToString(
              new Date(dailyReport.sections.workSchedule.startDatetime)
            )
          : projectSummaryViewDate,
        isApplicable: true,
        controlsIsApplicable: true,
      },
    }
  );

  /**
   * FIXME: 🩹 this is just workaround for UAT!
   *
   * We need to revert a few things on the MultiStep and it will take some time ... should be done after this!!
   * Stores the CURRENT state of the daily report SECTIONS
   * It stores completed, and with error states.
   * @deprecated
   */
  const [currentDailyReportSections, setCurrentDailyReportSections] = useState<
    Record<string, never> | DailyInspectionReportType["sections"]
  >(storedDailyReport?.sections);

  const [isSaveAndCompleteModalOpen, setIsSaveAndCompleteModalOpen] =
    useState(false);

  const [createOrUpdateDailyReport] = useMutation<{
    saveDailyReport: DailyInspectionReportType;
  }>(saveDailyReport, {
    onError(_err) {
      sessionExpiryHandlerForApolloClient(_err);
      toastCtx?.pushToast("error", "Failed saving section ...");
      markCurrentAs("error");
    },
    onCompleted({ saveDailyReport: savedDailyReport }) {
      // if the `dailyReport` is still not stored then we update the URL
      if (!dailyReport?.id) {
        shallowReplaceUrlWithPath(savedDailyReport);
      }

      // When the section is saved but NOT completed, we cannot update the following sections
      const affectedSections =
        current.status === "completed"
          ? Object.values(
              revalidateSectionsBySection?.[
                current.id as DailyInspectionReportResettableSections
              ] || {}
            )
          : [];

      // FIXME: we should have the internal form data, so we just need to add/replace in the state
      const result = applyDefaultsToArrayFields(
        stripTypename(savedDailyReport)
      ) as DailyInspectionReportType;

      setDailyReport(result);

      // FIXME: 🩹 this is just workaround for UAT!
      // When sections are affected, we need to remove the previous state and update the with the new values.
      setCurrentDailyReportSections(sections => ({
        ...sections,
        ...[current.id, ...affectedSections].reduce(
          (acc, key) => ({
            ...acc,
            [key]:
              result?.sections?.[
                key as unknown as keyof NonNullable<
                  DailyInspectionReportType["sections"]
                >
              ],
          }),
          {}
        ),
      }));

      // the validation already marked the current section, we just need to move it forward if it was set to complete.
      if (current.status === "completed") {
        moveForward();
        if (affectedSections.length > 0) {
          markSectionsAs("default", affectedSections);
        }
      }
    },
  });

  const [
    completeDailyReport,
    { loading: isCompleteDailyReportMutationLoading },
  ] = useMutation<DailyReportUpdateData>(updateDailyReportStatus, {
    ignoreResults: true,
    variables: {
      id: dailyReport?.id,
      status: DailyReportStatus.COMPLETE,
    },
    onError() {
      toastCtx?.pushToast("error", "Error while completing the report ...");
    },
    onCompleted() {
      setIsSaveAndCompleteModalOpen(true);
      toastCtx?.pushToast(
        "success",
        "The daily report was successfully completed."
      );
      router.push({
        pathname: "/projects/[id]",
        query: getUpdatedRouterQuery(
          { id: project.id, startDate: router.query.startDate },
          { key: "source", value: router.query.source }
        ),
      });
    },
  });

  const reopenReportHandler = () => {
    setDailyReport(prevState => {
      if (!prevState) return prevState;
      return {
        ...prevState,
        completedAt: undefined,
        completedBy: undefined,
        status: DailyReportStatus.IN_PROGRESS,
      };
    });
  };

  const onSaveStepSectionHandler = async ({
    sectionIsValid,
    ...formData
  }: DailyInspectionReportForms & { sectionIsValid: boolean }) => {
    // Locally generate the header data for
    // the daily inspect report for the save request.
    const buildHeaderData = (
      _dailyReportFormData: DailyInspectionReportForms
    ) => {
      const dailyReportHeaderData: {
        id?: string;
        projectLocationId: string;
        date?: string;
        [workScheduleFormInputPrefix]?: WorkScheduleProps;
      } = {
        id: dailyReport?.id,
        projectLocationId: location.id,
        date: undefined,
      };

      const isWorkScheduleSection = current.id === workScheduleFormInputPrefix;
      const hasDailyReportInProgress = !!dailyReport?.id;

      if (isWorkScheduleSection) {
        dailyReportHeaderData.date = getWorkScheduleStartDateTime(formData);
      } else if (hasDailyReportInProgress) {
        dailyReportHeaderData.date =
          getStartDateTimeFromSavedReport(dailyReport);
      } else {
        // Implicitly create the Work Schedule section when starting on a different section
        dailyReportHeaderData.date = projectSummaryViewDate;
        dailyReportHeaderData[workScheduleFormInputPrefix] = {
          startDatetime: projectSummaryViewDate,
        } as WorkScheduleProps;
      }

      return dailyReportHeaderData;
    };

    const dailyReportHeaderData: {
      id?: string;
      projectLocationId: string;
      date?: string;
      [workScheduleFormInputPrefix]?: WorkScheduleProps;
    } = buildHeaderData(formData);

    // TODO: This shouldn't be needed! Generics should infer everything...
    const { id: currentSection, transformFormDataToSchema } =
      current as DailyInspectionReportMultiStep;

    const currentFormData = {
      [currentSection]:
        formData[currentSection as keyof DailyInspectionReportForms],
    };

    // TODO: This should be from the step responsibility. For now,
    // Parse raw form data into the section input type.
    let data =
      transformFormDataToSchema?.(currentFormData, { location }) ||
      currentFormData;

    data[currentSection].sectionIsValid = sectionIsValid;

    const getPreservedDailyReportSections = (
      isSectionValid: boolean
    ): DailyReportInputs => {
      if (isSectionValid) {
        if (currentSection === workScheduleFormInputPrefix) {
          const dailyReportStartDate = new Date(
            getFormattedLocaleDateTime(
              dailyReport?.sections?.workSchedule?.startDatetime as string
            )
          ).getDate();
          const dailyReportEndDate = new Date(
            getFormattedLocaleDateTime(
              dailyReport?.sections?.workSchedule?.endDatetime as string
            )
          ).getDate();
          const formDataStartDate = new Date(
            getFormattedLocaleDateTime(
              formData?.workSchedule?.startDatetime as string
            )
          ).getDate();
          const formDataEndDate = new Date(
            getFormattedLocaleDateTime(
              formData?.workSchedule?.endDatetime as string
            )
          ).getDate();

          if (
            dailyReportStartDate !== formDataStartDate ||
            dailyReportEndDate !== formDataEndDate
          ) {
            return preserveDailyReportSections(
              currentSection as DailyInspectionReportResettableSections,
              dailyReport
            );
          }
        } else {
          /**
           * Only apply reset if either:
           * 1. The section is not present in the daily report.
           * 2. The section is present in the daily report but the data is different from the
           */

          if (
            !dailyReport?.sections?.[
              currentSection as DailyInspectionReportSectionKeys
            ]
          ) {
            return preserveDailyReportSections(
              currentSection as DailyInspectionReportResettableSections,
              dailyReport
            );
          }

          if (
            !isEqual(
              data[currentSection],
              dailyReport?.sections?.[
                currentSection as DailyInspectionReportSectionKeys
              ]
            )
          ) {
            return preserveDailyReportSections(
              currentSection as DailyInspectionReportResettableSections,
              dailyReport
            );
          }
        }
      }

      return dailyReport?.sections || {};
    };

    // Reset sections, meaning that any section changed, will reset the following ones.
    const preservedDailyReportSections =
      getPreservedDailyReportSections(sectionIsValid);

    // FIXME: 🩹 this is just workaround for UAT!
    // This removes the current sections in ERROR state with the default value (if has one).
    const preservedDefaultDailyReportSectionsInErrorState = Object.entries(
      preservedDailyReportSections
    ).reduce(
      (acc, [key]) => {
        if (steps.find(k => k.id === key)?.status === "error") {
          acc[key as unknown as DailyInspectionReportSectionKeys] =
            dailyReport?.sections?.[
              key as unknown as DailyInspectionReportSectionKeys
            ] || null;
        }
        return acc;
      },
      {} as {
        [k in DailyInspectionReportSectionKeys]: unknown;
      }
    );

    if (data?.jobHazardAnalysis?.siteConditions) {
      data = {
        ...data,
        [jobHazardAnalysisFormInputPrefix]: {
          ...data[jobHazardAnalysisFormInputPrefix],
          siteConditions: data.jobHazardAnalysis.siteConditions.filter(
            (sc: { id: string }) =>
              locationSiteConditions?.siteConditions
                ?.map((lSc: SiteCondition) => lSc.id)
                .includes(sc.id)
          ),
        },
      };
    }

    // Make sure all sections have a `sectionIsValid` property ...
    const payload = defaultSectionIsValidPropBySections({
      // Preserve the default sections (if has)
      ...preservedDailyReportSections,
      // mutation requires that we send the WHOLE payload again
      // otherwise removes the previously stored section(s).
      ...preservedDefaultDailyReportSectionsInErrorState,
      ...data,
      dailySourceInfo,
    });

    return createOrUpdateDailyReport({
      variables: {
        dailyReportInput: {
          ...dailyReportHeaderData,
          ...payload,
        },
      },
    });
  };

  const { mutate: fetchFormsAuditLogsData, isLoading } = useRestMutation<any>({
    endpoint: `${config.workerSafetyAuditTrailServiceRest}/logs/list/`,
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: data => data,
    mutationOptions: {
      onSuccess: async (response: any) => {
        setDirFormAuditData(response.data);
      },
      onError: error => {
        console.log(error);
        toastCtx?.pushToast("error", messages.SomethingWentWrong);
      },
    },
  });

  useEffect(() => {
    if (dailyReport?.id && selectedTab === FormViewTabStates.HISTORY) {
      const requestData = {
        object_id: dailyReport?.id,
        object_type: "dir",
        order_by: {
          field: "created_at",
          desc: true,
        },
      };
      fetchFormsAuditLogsData(requestData);
    }
  }, [dailyReport?.id, selectedTab]);

  return (
    <>
      <Head>
        <title>Daily Inspection Report | Worker Safety</title>
      </Head>
      <PageLayout
        header={
          <DailyInspectionPageHeader
            id={project.id}
            reportId={dailyReport?.id}
            reportCreatedUserId={dailyReport?.createdBy?.id}
            sections={dailyReport?.sections}
            projectName={project.name}
            projectDescription={project?.description}
            projectNumber={project.externalKey}
            locationId={location.id}
            locationName={location.name}
            isReportSaved={!!dailyReport?.id}
            isReportComplete={
              dailyReport?.status === DailyReportStatus.COMPLETE
            }
            onReopen={reopenReportHandler}
            setSelectedTab={setSelectedTab}
            selectedTab={selectedTab}
          />
        }
      >
        {selectedTab === FormViewTabStates.FORM ? (
          <MultiStep
            UNSAFE_WILL_BE_REMOVED_debugMode={false}
            readOnly={true}
            onStepMount={() => {
              return {
                dailyReport: {
                  ...dailyReport,
                  sections: {
                    // FIXME: 🩹 this is just workaround for UAT!
                    ...pick(currentDailyReportSections, [
                      "workSchedule",
                      "jobHazardAnalysis",
                      "taskSelection",
                    ]),
                  },
                },
                project,
                location,
                defaults: {
                  projectSummaryViewDate,
                },
                form: {
                  // ...defaultValuesSections,
                  // FIXME: 🩹 this is just workaround for UAT!
                  ...pick(currentDailyReportSections, [
                    "crew",
                    "additionalInformation",
                    "safetyAndCompliance",
                    "attachments",
                  ]),
                },
              };
            }}
            onStepSave={onSaveStepSectionHandler}
            onStepUnmount={form => {
              // FIXME: 🩹 this is just workaround for UAT!
              // We shouldn't keep track of what's in the internal state.
              if (current.status === "error") {
                setCurrentDailyReportSections(sections => {
                  let formData = form;
                  // This is needed because this section cannot be used 1 - 1 with RHF (it always needs some sort of parsing)
                  // even when migrate all sections to read from the RHF state.
                  if (current.id === "jobHazardAnalysis") {
                    formData = jobHazardAnalysisGraphQLPayload(
                      form as JobHazardAnalysisGraphQLPayloadParams,
                      { withDefaultControlValue: false }
                    );
                  }

                  return {
                    ...sections,
                    ...(formData as { [x: string]: unknown }),
                  };
                });
              }
            }}
            onComplete={() => setIsSaveAndCompleteModalOpen(true)}
          />
        ) : (
          <div className="pl-8 h-full">
            <FormHistory
              data={dirFormAuditData}
              isAuditDataLoading={isLoading}
              location={location.name}
            />
          </div>
        )}
      </PageLayout>
      <SaveAndCompleteModal
        isLoading={isCompleteDailyReportMutationLoading}
        isOpen={isSaveAndCompleteModalOpen}
        closeModal={() => setIsSaveAndCompleteModalOpen(false)}
        onPrimaryBtnClick={completeDailyReport}
      />
    </>
  );
}

export default function WithMultiFormStepDailyInspection(
  props: DailyInspectionReport
): JSX.Element {
  const steps = mergeDailyReportCompletedSectionsWithMetadata(
    getMetadata(),
    props?.dailyReport
  );

  return (
    <MultiStepFormProvider steps={steps}>
      <DailyReport
        {...props}
        dailyReport={applyRecommendationsToSections({
          dailyReport: applyDefaultsToArrayFields(
            props?.dailyReport
          ) as DailyReportResponse,
          recommendations: props.recommendations,
        })}
      />
    </MultiStepFormProvider>
  );
}
