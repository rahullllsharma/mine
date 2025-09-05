import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export const messages = Object.freeze({
  required: "This is a required field",
  emptyString: "This field cannot be left blank",
  alphanumeric: "Only alphanumeric characters are allowed",
  url: "Please enter a valid URL",
  date: "Please enter a valid date",
  startDateTimeGreaterThanEnd:
    "{contractor} Work Start Date and time should not be greater than End Date and time",
  dateTimeNotInProjectRange:
    "{contractor} Work {label} Date and time cannot start before {startDatetime} and end after {endDatetime}",
  minCharLength: "Attribute name should be longer than {value} characters.",
  maxCharLength: "Attribute name should be shorter than {value} characters.",
  multiple: "Multiple",
  mapApiError: "Provide a MapBox API key",
  mapTooltipLabel: "My location",
  mapErrorNoPermissions:
    "To enable location services, please update your system/browser settings",
  autoPopulatedSiteConditionMessage:
    "This is an auto-populated Site Condition, and therefore, it cannot be edited or deleted.",
  historicIncidentLabel: "View Historical incidents",
  historicIncidentModalTitle: "Historical incidents",
  historicIncidentModalSeverity: "Severity",
  historicIncidentModalDescription: "Description",
  historicIncidentEmptyTitle: "No historical events found",
  historicIncidentEmptyDescription:
    "There are no historical incidents that match this task with the following severities:",
  historicIncidentEmptyExamples:
    "SIF, P-SIF, Lost Time, Restricted, Recordable",
  RecommendedHazardModalTitle: "Recommended High Energy Hazards",
  RecommendedHazardModalSubTitle:
    "Here are some additional High Energy Hazards that could be present, please review and make any further updates below:",
  EboHistoricalIncidentsSectionTitle: "Historical Incidents",
  EboHistoricalIncidentsSectionSubTitle:
    "Select the incidents below that you would like to review with your team during the safety briefing",
  SomethingWentWrong: "Oops! Something went wrong, please try again later",
  ErrorFetchingTemplatesList: "Error fetching templates list",
  requestTimedOut: "Request timed out",
});

export const getAuditTrailLabels = (): { [key: string]: string } => {
  const { workPackage, task, siteCondition } = useTenantStore
    .getState()
    .getAllEntities();

  return {
    task: task.label,
    site_condition: siteCondition.label,
    project: workPackage.label,
    project_supervisorId: workPackage.attributes.primaryAssignedPerson.label,
    project_startDate: workPackage.attributes.startDate.label,
    project_endDate: workPackage.attributes.endDate.label,
    project_projectZipCode: workPackage.attributes.zipCode.label,
    project_managerId: workPackage.attributes.projectManager.label,
    project_status: workPackage.attributes.status.label,
    project_libraryDivisionId: workPackage.attributes.division.label,
    project_contractorId: workPackage.attributes.primeContractor.label,
    project_description: workPackage.attributes.description.label,
    project_contractReference:
      workPackage.attributes.contractReferenceNumber.label,
    project_name: workPackage.attributes.name.label,
    project_libraryRegionId: workPackage.attributes.region.label,
    project_externalKey: workPackage.attributes.externalKey.label,
    project_workTypeId: workPackage.attributes.workPackageType.label,
    project_contractName: workPackage.attributes.contractName.defaultLabel,
    project_additionalSupervisorIds:
      workPackage.attributes.additionalAssignedPerson.defaultLabelPlural,
    project_libraryAssetTypeId: workPackage.attributes.assetType.label,
    project_status_pending:
      workPackage.attributes.status.mappings?.pending[0] || "Pending",
    project_status_active:
      workPackage.attributes.status.mappings?.active[0] || "Active",
    project_status_complete:
      workPackage.attributes.status.mappings?.completed[0] || "Completed",
    not_started: "Not Started",
    in_progress: "In Progress",
    complete: "Complete",
    not_completed: "Not Completed",

    // attributes not present in tenantStore
    project_engineerName: "Engineer",
    task_status: "status",
    task_startDate: "Start Date",
    task_endDate: "End Date",
    daily_report: "Daily Inspection Report",
  };
};
