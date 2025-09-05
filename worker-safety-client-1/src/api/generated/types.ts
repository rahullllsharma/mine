import { GraphQLClient } from 'graphql-request';
import * as Dom from 'graphql-request/dist/types.dom';
import gql from 'graphql-tag';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: string;
  String: string;
  Boolean: boolean;
  Int: number;
  Float: number;
  Date: any;
  DateTime: any;
  Decimal: any;
  DictScalar: any;
  JSON: any;
  JSONScalar: any;
  Time: any;
  UUID: any;
  Void: any;
};

export type AedInformation = {
  __typename?: 'AEDInformation';
  location: Scalars['String'];
};

export type AedInformationDataInput = {
  aedLocationName: Scalars['String'];
  id: Scalars['UUID'];
};

export type AedInformationDataType = {
  __typename?: 'AEDInformationDataType';
  aedLocationName: Scalars['String'];
  id: Scalars['UUID'];
};

export type AedInformationInput = {
  location: Scalars['String'];
};

export type Activity = {
  __typename?: 'Activity';
  crew?: Maybe<Crew>;
  criticalDescription?: Maybe<Scalars['String']>;
  endDate?: Maybe<Scalars['Date']>;
  id: Scalars['UUID'];
  isCritical: Scalars['Boolean'];
  libraryActivityType?: Maybe<LibraryActivityType>;
  location: ProjectLocation;
  name: Scalars['String'];
  startDate?: Maybe<Scalars['Date']>;
  status: ActivityStatus;
  supervisors: Array<BaseSupervisor>;
  taskCount: Scalars['Int'];
  tasks: Array<Task>;
};


export type ActivityTasksArgs = {
  date?: InputMaybe<Scalars['Date']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};

export type ActivityConceptInput = {
  name: Scalars['String'];
  tasks: Array<TaskSelectionConceptInput>;
};

export type ActivityConceptType = {
  __typename?: 'ActivityConceptType';
  name: Scalars['String'];
  tasks: Array<TaskSelectionConcept>;
};

export enum ActivityStatus {
  Complete = 'COMPLETE',
  InProgress = 'IN_PROGRESS',
  NotCompleted = 'NOT_COMPLETED',
  NotStarted = 'NOT_STARTED'
}

export type AddActivityTasksInput = {
  tasksToBeAdded?: Array<CreateTaskInput>;
};

export type AdditionalInformationSection = {
  __typename?: 'AdditionalInformationSection';
  lessons?: Maybe<Scalars['String']>;
  operatingHq?: Maybe<Scalars['String']>;
  progress?: Maybe<Scalars['String']>;
  sectionIsValid?: Maybe<Scalars['Boolean']>;
};

export type AdditionalInformationSectionInput = {
  lessons?: InputMaybe<Scalars['String']>;
  operatingHq?: InputMaybe<Scalars['String']>;
  progress?: InputMaybe<Scalars['String']>;
  sectionIsValid?: InputMaybe<Scalars['Boolean']>;
};

export enum ApplicabilityLevel {
  Always = 'ALWAYS',
  Mostly = 'MOSTLY',
  Never = 'NEVER',
  Rarely = 'RARELY'
}

export type ApplicableHazardCount = {
  __typename?: 'ApplicableHazardCount';
  count: Scalars['Int'];
  libraryHazard: LibraryHazard;
  total: Scalars['Int'];
};

export type ApplicableHazardCountByLocation = {
  __typename?: 'ApplicableHazardCountByLocation';
  count: Scalars['Int'];
  location: ProjectLocation;
  total: Scalars['Int'];
};

export type ApplicableHazardCountByProject = {
  __typename?: 'ApplicableHazardCountByProject';
  count: Scalars['Int'];
  project: Project;
  total: Scalars['Int'];
};

export type ApplicableHazardCountBySiteCondition = {
  __typename?: 'ApplicableHazardCountBySiteCondition';
  count: Scalars['Int'];
  librarySiteCondition: LibrarySiteCondition;
  total: Scalars['Int'];
};

export type ApplicableHazardCountByTask = {
  __typename?: 'ApplicableHazardCountByTask';
  count: Scalars['Int'];
  libraryTask: LibraryTask;
  total: Scalars['Int'];
};

export type ApplicableHazardCountByTaskType = {
  __typename?: 'ApplicableHazardCountByTaskType';
  count: Scalars['Int'];
  libraryTask: LibraryTask;
  total: Scalars['Int'];
};

export type AttachmentSection = {
  __typename?: 'AttachmentSection';
  documents?: Maybe<Array<File>>;
  photos?: Maybe<Array<File>>;
  sectionIsValid?: Maybe<Scalars['Boolean']>;
};

export type AttachmentSectionInput = {
  documents?: InputMaybe<Array<FileInput>>;
  photos?: InputMaybe<Array<FileInput>>;
  sectionIsValid?: InputMaybe<Scalars['Boolean']>;
};

export type AttachmentsInput = {
  descriptionDocumentProvided?: InputMaybe<Scalars['String']>;
  documents?: InputMaybe<Array<FileInput>>;
  documentsProvided?: InputMaybe<Array<DocumentsProvidedInput>>;
  photos?: InputMaybe<Array<FileInput>>;
};

export type AttachmentsType = {
  __typename?: 'AttachmentsType';
  descriptionDocumentProvided?: Maybe<Scalars['String']>;
  documents?: Maybe<Array<File>>;
  documentsProvided?: Maybe<Array<DocumentsProvidedType>>;
  photos?: Maybe<Array<File>>;
};

export type AttributeConfiguration = {
  __typename?: 'AttributeConfiguration';
  defaultLabel: Scalars['String'];
  defaultLabelPlural: Scalars['String'];
  filterable: Scalars['Boolean'];
  key: Scalars['String'];
  label: Scalars['String'];
  labelPlural: Scalars['String'];
  mandatory: Scalars['Boolean'];
  mappings?: Maybe<Scalars['JSON']>;
  required: Scalars['Boolean'];
  visible: Scalars['Boolean'];
};

export type AttributeConfigurationInput = {
  filterable: Scalars['Boolean'];
  key: Scalars['String'];
  label: Scalars['String'];
  labelPlural: Scalars['String'];
  mappings?: InputMaybe<Scalars['JSON']>;
  required: Scalars['Boolean'];
  visible: Scalars['Boolean'];
};

export enum AuditActionType {
  Created = 'CREATED',
  Deleted = 'DELETED',
  Updated = 'UPDATED'
}

export type AuditActor = {
  __typename?: 'AuditActor';
  id: Scalars['UUID'];
  name: Scalars['String'];
  role?: Maybe<Scalars['String']>;
};

export type AuditEvent = {
  __typename?: 'AuditEvent';
  actionType: AuditActionType;
  actor?: Maybe<AuditActor>;
  auditKey: AuditKeyType;
  diffValues?: Maybe<DiffValue>;
  objectDetails?: Maybe<Auditable>;
  objectId: Scalars['UUID'];
  objectType: AuditObjectType;
  timestamp: Scalars['DateTime'];
  transactionId: Scalars['UUID'];
};

export enum AuditKeyType {
  DailyReport = 'dailyReport',
  DailyReportStatus = 'dailyReport_status',
  Project = 'project',
  ProjectAdditionalSupervisorIds = 'project_additionalSupervisorIds',
  ProjectContractName = 'project_contractName',
  ProjectContractReference = 'project_contractReference',
  ProjectContractorId = 'project_contractorId',
  ProjectCustomerStatus = 'project_customerStatus',
  ProjectDescription = 'project_description',
  ProjectEndDate = 'project_endDate',
  ProjectEngineerName = 'project_engineerName',
  ProjectExternalKey = 'project_externalKey',
  ProjectLibraryAssetTypeId = 'project_libraryAssetTypeId',
  ProjectLibraryDivisionId = 'project_libraryDivisionId',
  ProjectLibraryProjectTypeId = 'project_libraryProjectTypeId',
  ProjectLibraryRegionId = 'project_libraryRegionId',
  ProjectManagerId = 'project_managerId',
  ProjectName = 'project_name',
  ProjectProjectZipCode = 'project_projectZipCode',
  ProjectStartDate = 'project_startDate',
  ProjectStatus = 'project_status',
  ProjectSupervisorId = 'project_supervisorId',
  ProjectWorkTypeId = 'project_workTypeId',
  ProjectWorkTypeIds = 'project_workTypeIds',
  SiteCondition = 'siteCondition',
  Task = 'task',
  TaskEndDate = 'task_endDate',
  TaskStartDate = 'task_startDate',
  TaskStatus = 'task_status'
}

export enum AuditObjectType {
  DailyReport = 'DAILY_REPORT',
  Project = 'PROJECT',
  SiteCondition = 'SITE_CONDITION',
  Task = 'TASK'
}

export type Auditable = {
  id: Scalars['UUID'];
};

export type BarnLocationInput = {
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type BarnLocationType = {
  __typename?: 'BarnLocationType';
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type BaseSupervisor = {
  __typename?: 'BaseSupervisor';
  externalKey: Scalars['String'];
  id: Scalars['UUID'];
  name: Scalars['String'];
  tenantId?: Maybe<Scalars['UUID']>;
  userId?: Maybe<Scalars['UUID']>;
};

export type BurnKitLocationInput = {
  burnKitLocationName: Scalars['String'];
  id: Scalars['UUID'];
};

export type BurnKitLocationType = {
  __typename?: 'BurnKitLocationType';
  burnKitLocationName: Scalars['String'];
  id: Scalars['UUID'];
};

export type ClearanceTypesInput = {
  clearanceTypes: Scalars['String'];
  id: Scalars['Int'];
};

export type ClearanceTypesType = {
  __typename?: 'ClearanceTypesType';
  clearanceTypes: Scalars['String'];
  id: Scalars['Int'];
};

export type Completion = {
  __typename?: 'Completion';
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  /** @deprecated Use completedBy instead */
  completedById?: Maybe<Scalars['UUID']>;
};

export type Contractor = {
  __typename?: 'Contractor';
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type ControlAnalysis = {
  __typename?: 'ControlAnalysis';
  furtherExplanation?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  implemented?: Maybe<Scalars['Boolean']>;
  name: Scalars['String'];
  notImplementedReason?: Maybe<Scalars['String']>;
};

export type ControlAnalysisInput = {
  furtherExplanation?: InputMaybe<Scalars['String']>;
  id: Scalars['UUID'];
  implemented?: InputMaybe<Scalars['Boolean']>;
  name?: InputMaybe<Scalars['String']>;
  notImplementedReason?: InputMaybe<Scalars['String']>;
};

export type ControlAssessment = {
  __typename?: 'ControlAssessment';
  /** @deprecated This field is deprecated due to redundancy with the 'controlSelections'. Please use 'controlSelections' going forward. */
  controlIds?: Maybe<Array<Scalars['String']>>;
  controlSelections?: Maybe<Array<ControlSelection>>;
  hazardId: Scalars['String'];
};

export type ControlAssessmentInput = {
  controlSelections?: InputMaybe<Array<ControlSelectionInput>>;
  hazardId: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
};

export type ControlSelection = {
  __typename?: 'ControlSelection';
  id: Scalars['String'];
  name?: Maybe<Scalars['String']>;
  recommended?: Maybe<Scalars['Boolean']>;
  selected?: Maybe<Scalars['Boolean']>;
};

export type ControlSelectionInput = {
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
  recommended?: InputMaybe<Scalars['Boolean']>;
  selected?: InputMaybe<Scalars['Boolean']>;
};

export type ControlsConceptInput = {
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
};

export type ControlsConceptType = {
  __typename?: 'ControlsConceptType';
  id: Scalars['String'];
  name?: Maybe<Scalars['String']>;
};

export type CreateActivityInput = {
  crewId?: InputMaybe<Scalars['UUID']>;
  criticalDescription?: InputMaybe<Scalars['String']>;
  endDate: Scalars['Date'];
  externalKey?: InputMaybe<Scalars['String']>;
  isCritical?: Scalars['Boolean'];
  libraryActivityTypeId?: InputMaybe<Scalars['UUID']>;
  locationId: Scalars['UUID'];
  metaAttributes?: InputMaybe<Scalars['DictScalar']>;
  name: Scalars['String'];
  startDate: Scalars['Date'];
  status?: ActivityStatus;
  tasks?: Array<CreateTaskInput>;
};

export type CreateHazardControlInput = {
  isApplicable?: Scalars['Boolean'];
  libraryControlId: Scalars['UUID'];
};

export type CreateHazardInput = {
  controls?: Array<CreateHazardControlInput>;
  isApplicable?: Scalars['Boolean'];
  libraryHazardId: Scalars['UUID'];
};

export type CreateInsightInput = {
  description?: InputMaybe<Scalars['String']>;
  name: Scalars['String'];
  url: Scalars['String'];
  visibility?: Scalars['Boolean'];
};

export type CreateProjectInput = {
  additionalSupervisors?: InputMaybe<Array<Scalars['UUID']>>;
  contractName?: InputMaybe<Scalars['String']>;
  contractReference?: InputMaybe<Scalars['String']>;
  contractorId?: InputMaybe<Scalars['UUID']>;
  description?: InputMaybe<Scalars['String']>;
  endDate: Scalars['Date'];
  engineerName?: InputMaybe<Scalars['String']>;
  externalKey?: InputMaybe<Scalars['String']>;
  libraryAssetTypeId?: InputMaybe<Scalars['UUID']>;
  libraryDivisionId?: InputMaybe<Scalars['UUID']>;
  libraryProjectTypeId?: InputMaybe<Scalars['UUID']>;
  libraryRegionId?: InputMaybe<Scalars['UUID']>;
  locations: Array<ProjectLocationInput>;
  managerId?: InputMaybe<Scalars['UUID']>;
  name: Scalars['String'];
  number?: InputMaybe<Scalars['String']>;
  projectZipCode?: InputMaybe<Scalars['String']>;
  startDate: Scalars['Date'];
  status?: ProjectStatus;
  supervisorId?: InputMaybe<Scalars['UUID']>;
  workTypeIds?: InputMaybe<Array<Scalars['UUID']>>;
};

export type CreateSiteConditionInput = {
  hazards: Array<CreateHazardInput>;
  librarySiteConditionId: Scalars['UUID'];
  locationId: Scalars['UUID'];
};

export type CreateTaskInput = {
  hazards: Array<CreateHazardInput>;
  libraryTaskId: Scalars['UUID'];
};

export type CreateTenantInput = {
  authRealmName: Scalars['String'];
  displayName: Scalars['String'];
  tenantName: Scalars['String'];
};

export type Crew = {
  __typename?: 'Crew';
  externalKey: Scalars['String'];
  id: Scalars['UUID'];
};

export type CrewInfoInput = {
  crewDetails?: InputMaybe<UserInfoInput>;
  discussionConducted: Scalars['Boolean'];
  otherCrewDetails?: InputMaybe<Scalars['String']>;
  signature?: InputMaybe<FileInput>;
};

export type CrewInfoType = {
  __typename?: 'CrewInfoType';
  crewDetails?: Maybe<UserInfoType>;
  discussionConducted: Scalars['Boolean'];
  otherCrewDetails?: Maybe<Scalars['String']>;
  signature?: Maybe<File>;
};

export type CrewInformationDataInput = {
  signature?: InputMaybe<FileInput>;
  supervisorInfo: UserInfoInput;
};

export type CrewInformationDataType = {
  __typename?: 'CrewInformationDataType';
  signature?: Maybe<File>;
  supervisorInfo: UserInfoType;
};

export type CrewInformationInput = {
  companyName?: InputMaybe<Scalars['String']>;
  department?: InputMaybe<Scalars['String']>;
  displayName?: InputMaybe<Scalars['String']>;
  email?: InputMaybe<Scalars['String']>;
  employeeNumber?: InputMaybe<Scalars['String']>;
  externalId?: InputMaybe<Scalars['String']>;
  jobTitle?: InputMaybe<Scalars['String']>;
  managerEmail?: InputMaybe<Scalars['String']>;
  managerId?: InputMaybe<Scalars['String']>;
  managerName?: InputMaybe<Scalars['String']>;
  name?: InputMaybe<Scalars['String']>;
  primary?: InputMaybe<Scalars['Boolean']>;
  signature?: InputMaybe<FileInput>;
  type?: InputMaybe<CrewType>;
};

export type CrewInformationType = {
  __typename?: 'CrewInformationType';
  companyName?: Maybe<Scalars['String']>;
  department?: Maybe<Scalars['String']>;
  displayName?: Maybe<Scalars['String']>;
  email?: Maybe<Scalars['String']>;
  employeeNumber?: Maybe<Scalars['String']>;
  externalId?: Maybe<Scalars['String']>;
  jobTitle?: Maybe<Scalars['String']>;
  managerEmail?: Maybe<Scalars['String']>;
  managerId?: Maybe<Scalars['String']>;
  managerName?: Maybe<Scalars['String']>;
  name?: Maybe<Scalars['String']>;
  primary?: Maybe<Scalars['Boolean']>;
  signature?: Maybe<File>;
  type?: Maybe<CrewType>;
};

export type CrewLeader = {
  __typename?: 'CrewLeader';
  companyName?: Maybe<Scalars['String']>;
  createdAt: Scalars['DateTime'];
  id: Scalars['UUID'];
  lanid?: Maybe<Scalars['String']>;
  name: Scalars['String'];
};

export type CrewSection = {
  __typename?: 'CrewSection';
  contractor?: Maybe<Scalars['String']>;
  documents?: Maybe<Array<File>>;
  foremanName?: Maybe<Scalars['String']>;
  nFlaggers?: Maybe<Scalars['Int']>;
  nLaborers?: Maybe<Scalars['Int']>;
  nOperators?: Maybe<Scalars['Int']>;
  nOtherCrew?: Maybe<Scalars['Int']>;
  nSafetyProf?: Maybe<Scalars['Int']>;
  nWelders?: Maybe<Scalars['Int']>;
  sectionIsValid?: Maybe<Scalars['Boolean']>;
};

export type CrewSectionInput = {
  contractor?: InputMaybe<Scalars['String']>;
  documents?: InputMaybe<Array<FileInput>>;
  foremanName?: InputMaybe<Scalars['String']>;
  nFlaggers?: InputMaybe<Scalars['Int']>;
  nLaborers?: InputMaybe<Scalars['Int']>;
  nOperators?: InputMaybe<Scalars['Int']>;
  nOtherCrew?: InputMaybe<Scalars['Int']>;
  nSafetyProf?: InputMaybe<Scalars['Int']>;
  nWelders?: InputMaybe<Scalars['Int']>;
  sectionIsValid?: InputMaybe<Scalars['Boolean']>;
};

export type CrewSignOffInput = {
  creatorSign?: InputMaybe<CrewInfoInput>;
  crewSign?: InputMaybe<Array<CrewInfoInput>>;
  multipleCrews: MultipleCrewsInput;
};

export type CrewSignOffType = {
  __typename?: 'CrewSignOffType';
  creatorSign?: Maybe<CrewInfoType>;
  crewSign?: Maybe<Array<CrewInfoType>>;
  multipleCrews: MultipleCrewsType;
};

export enum CrewType {
  Other = 'OTHER',
  Personnel = 'PERSONNEL'
}

export type CriticalActivityType = {
  __typename?: 'CriticalActivityType';
  date: Scalars['Date'];
  isCritical: Scalars['Boolean'];
};

export type CriticalRiskArea = {
  __typename?: 'CriticalRiskArea';
  name: Scalars['String'];
};

export type CriticalRiskAreaInput = {
  name: Scalars['String'];
};

export type CriticalTasksSelectionInput = {
  jobDescription: Scalars['String'];
  specialPrecautionsNotes?: InputMaybe<Scalars['String']>;
  taskSelections: Array<TaskSelectionConceptInput>;
};

export type CriticalTasksSelectionType = {
  __typename?: 'CriticalTasksSelectionType';
  jobDescription: Scalars['String'];
  specialPrecautionsNotes?: Maybe<Scalars['String']>;
  taskSelections: Array<TaskSelectionConcept>;
};

export type CustomHazardsInput = {
  lowEnergyHazards?: InputMaybe<Array<EnergyHazardsInput>>;
};

export type CustomHazardsType = {
  __typename?: 'CustomHazardsType';
  lowEnergyHazards?: Maybe<Array<EnergyHazardsType>>;
};

export type CustomMedicalFacility = {
  __typename?: 'CustomMedicalFacility';
  address: Scalars['String'];
};

export type CustomMedicalFacilityInput = {
  address: Scalars['String'];
};

export type DailyReport = Auditable & FormInterface & {
  __typename?: 'DailyReport';
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location: ProjectLocation;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  operatingHq?: Maybe<Scalars['String']>;
  sections?: Maybe<Sections>;
  sectionsJSON?: Maybe<Scalars['JSONScalar']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type DailyReportCrewRecommendation = {
  __typename?: 'DailyReportCrewRecommendation';
  constructionCompany?: Maybe<Scalars['String']>;
  foremanName?: Maybe<Scalars['String']>;
};

export type DailyReportFormsList = Auditable & FormInterfaceWithContents & {
  __typename?: 'DailyReportFormsList';
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location: ProjectLocation;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  operatingHq?: Maybe<Scalars['String']>;
  sections?: Maybe<Sections>;
  sectionsJSON?: Maybe<Scalars['JSONScalar']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type DailyReportRecommendation = {
  __typename?: 'DailyReportRecommendation';
  crew?: Maybe<DailyReportCrewRecommendation>;
  safetyAndCompliance?: Maybe<DailyReportSafetyAndComplianceRecommendation>;
};

export type DailyReportSafetyAndComplianceRecommendation = {
  __typename?: 'DailyReportSafetyAndComplianceRecommendation';
  phaCompletion?: Maybe<Scalars['String']>;
  sopNumber?: Maybe<Scalars['String']>;
  sopType?: Maybe<Scalars['String']>;
  stepsCalledIn?: Maybe<Scalars['String']>;
};

export type DailySourceInformationConceptsInput = {
  appVersion?: InputMaybe<Scalars['String']>;
  sectionIsValid?: InputMaybe<Scalars['Boolean']>;
  sourceInformation?: InputMaybe<SourceAppInformation>;
};

export type DailySourceInformationConceptsType = {
  __typename?: 'DailySourceInformationConceptsType';
  appVersion?: Maybe<Scalars['String']>;
  sectionIsValid?: Maybe<Scalars['Boolean']>;
  sourceInformation?: Maybe<SourceAppInformation>;
};

export type DateRangeInput = {
  endDate: Scalars['Date'];
  startDate: Scalars['Date'];
};

export type DatedActivitiesResponse = {
  __typename?: 'DatedActivitiesResponse';
  activities: Array<Activity>;
  date: Scalars['Date'];
};

export type DatedJsbResponse = {
  __typename?: 'DatedJSBResponse';
  date: Scalars['Date'];
  jobSafetyBriefings: Array<JobSafetyBriefing>;
};

export type DatedReportsResponse = {
  __typename?: 'DatedReportsResponse';
  dailyReports: Array<DailyReport>;
  date: Scalars['Date'];
};

export type DatedRiskLevel = {
  __typename?: 'DatedRiskLevel';
  date: Scalars['Date'];
  riskLevel: RiskLevel;
};

export type DatedSiteConditions = {
  __typename?: 'DatedSiteConditions';
  date: Scalars['Date'];
  siteConditions: Array<SiteCondition>;
};

export type DatedTaskResponse = {
  __typename?: 'DatedTaskResponse';
  date: Scalars['Date'];
  tasks: Array<Task>;
};

export type Department = {
  __typename?: 'Department';
  createdAt: Scalars['DateTime'];
  id: Scalars['UUID'];
  name: Scalars['String'];
  opco: Opco;
};

export type DepartmentObservedConceptInput = {
  id?: InputMaybe<Scalars['UUID']>;
  name: Scalars['String'];
};

export type DepartmentObservedConceptType = {
  __typename?: 'DepartmentObservedConceptType';
  id?: Maybe<Scalars['UUID']>;
  name: Scalars['String'];
};

export type DiffValue = {
  type?: Maybe<Scalars['String']>;
};

export type DiffValueLiteral = DiffValue & {
  __typename?: 'DiffValueLiteral';
  newValue?: Maybe<Scalars['String']>;
  oldValue?: Maybe<Scalars['String']>;
  type: Scalars['String'];
};

export type DiffValueScalar = DiffValue & {
  __typename?: 'DiffValueScalar';
  added?: Maybe<Array<Scalars['String']>>;
  newValues?: Maybe<Array<Scalars['String']>>;
  oldValues?: Maybe<Array<Scalars['String']>>;
  removed?: Maybe<Array<Scalars['String']>>;
  type: Scalars['String'];
};

export type DirectoryGroup = {
  __typename?: 'DirectoryGroup';
  createdAt: Scalars['String'];
  directoryId: Scalars['String'];
  id: Scalars['String'];
  idpId: Scalars['String'];
  name: Scalars['String'];
  organizationId?: Maybe<Scalars['String']>;
  /** @deprecated Deprecated due to  change in WorkOS API. */
  rawAttributes?: Maybe<Scalars['JSON']>;
  updatedAt: Scalars['String'];
};

export type DirectoryUser = {
  __typename?: 'DirectoryUser';
  createdAt: Scalars['String'];
  customAttributes: Scalars['JSON'];
  directoryId: Scalars['String'];
  emails: Array<DirectoryUserEmail>;
  firstName?: Maybe<Scalars['String']>;
  groups: Array<DirectoryGroup>;
  id: Scalars['String'];
  idpId: Scalars['String'];
  jobTitle?: Maybe<Scalars['String']>;
  lastName?: Maybe<Scalars['String']>;
  organizationId?: Maybe<Scalars['String']>;
  /** @deprecated Deprecated due to change in WorkOS API. Use custom_attributes. */
  rawAttributes?: Maybe<Scalars['JSON']>;
  role?: Maybe<Scalars['JSON']>;
  slug?: Maybe<Scalars['String']>;
  state: DirectoryUserState;
  updatedAt: Scalars['String'];
  username?: Maybe<Scalars['String']>;
};

export type DirectoryUserEmail = {
  __typename?: 'DirectoryUserEmail';
  primary?: Maybe<Scalars['Boolean']>;
  type?: Maybe<Scalars['String']>;
  value?: Maybe<Scalars['String']>;
};

export enum DirectoryUserState {
  Active = 'active',
  Inactive = 'inactive'
}

export type DocumentsProvidedInput = {
  id: Scalars['Int'];
  name: Scalars['String'];
};

export type DocumentsProvidedType = {
  __typename?: 'DocumentsProvidedType';
  id: Scalars['Int'];
  name: Scalars['String'];
};

export type EboActivityConceptInput = {
  id: Scalars['UUID'];
  name: Scalars['String'];
  tasks: Array<EboTaskSelectionConceptInput>;
};

export type EboActivityConceptType = {
  __typename?: 'EBOActivityConceptType';
  id?: Maybe<Scalars['UUID']>;
  name: Scalars['String'];
  tasks: Array<EboTaskSelectionConceptType>;
};

export type EboControlsConceptInput = {
  hazardControlConnectorId?: InputMaybe<Scalars['String']>;
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
};

export type EboControlsConceptType = {
  __typename?: 'EBOControlsConceptType';
  hazardControlConnectorId?: Maybe<Scalars['String']>;
  id: Scalars['String'];
  name?: Maybe<Scalars['String']>;
};

export type EboHazardObservationConceptInput = {
  description?: InputMaybe<Scalars['String']>;
  directControlDescription?: InputMaybe<Scalars['String']>;
  directControls?: InputMaybe<Array<EboControlsConceptInput>>;
  directControlsImplemented?: InputMaybe<Scalars['Boolean']>;
  energyLevel?: InputMaybe<Scalars['String']>;
  hazardControlConnectorId?: InputMaybe<Scalars['String']>;
  hecaScoreHazard?: InputMaybe<Scalars['String']>;
  hecaScoreHazardPercentage?: InputMaybe<Scalars['Float']>;
  id: Scalars['String'];
  indirectControls?: InputMaybe<Array<EboControlsConceptInput>>;
  limitedControlDescription?: InputMaybe<Scalars['String']>;
  limitedControls?: InputMaybe<Array<EboControlsConceptInput>>;
  name?: InputMaybe<Scalars['String']>;
  observed: Scalars['Boolean'];
  reason?: InputMaybe<Scalars['String']>;
  taskHazardConnectorId?: InputMaybe<Scalars['String']>;
};

export type EboHazardObservationConceptType = {
  __typename?: 'EBOHazardObservationConceptType';
  description?: Maybe<Scalars['String']>;
  directControlDescription?: Maybe<Scalars['String']>;
  directControls?: Maybe<Array<EboControlsConceptType>>;
  directControlsImplemented?: Maybe<Scalars['Boolean']>;
  energyLevel?: Maybe<Scalars['String']>;
  hazardControlConnectorId?: Maybe<Scalars['String']>;
  hecaScoreHazard?: Maybe<Scalars['String']>;
  hecaScoreHazardPercentage?: Maybe<Scalars['Float']>;
  id: Scalars['String'];
  indirectControls?: Maybe<Array<EboControlsConceptType>>;
  limitedControlDescription?: Maybe<Scalars['String']>;
  limitedControls?: Maybe<Array<EboControlsConceptType>>;
  name?: Maybe<Scalars['String']>;
  observed: Scalars['Boolean'];
  reason?: Maybe<Scalars['String']>;
  taskHazardConnectorId?: Maybe<Scalars['String']>;
};

export type EboHighEnergyTaskConceptInput = {
  activityId?: InputMaybe<Scalars['String']>;
  activityName?: InputMaybe<Scalars['String']>;
  hazards?: Array<EboHazardObservationConceptInput>;
  hecaScoreTask?: InputMaybe<Scalars['String']>;
  hecaScoreTaskPercentage?: InputMaybe<Scalars['Float']>;
  id: Scalars['String'];
  instanceId?: Scalars['Int'];
  name?: InputMaybe<Scalars['String']>;
  taskHazardConnectorId?: InputMaybe<Scalars['String']>;
};

export type EboHighEnergyTaskConceptType = {
  __typename?: 'EBOHighEnergyTaskConceptType';
  activityId?: Maybe<Scalars['String']>;
  activityName?: Maybe<Scalars['String']>;
  hazards: Array<EboHazardObservationConceptType>;
  hecaScoreTask?: Maybe<Scalars['String']>;
  hecaScoreTaskPercentage?: Maybe<Scalars['Float']>;
  id: Scalars['String'];
  instanceId: Scalars['Int'];
  name?: Maybe<Scalars['String']>;
  taskHazardConnectorId?: Maybe<Scalars['String']>;
};

export type EboSummaryInput = {
  viewed: Scalars['Boolean'];
};

export type EboSummaryType = {
  __typename?: 'EBOSummaryType';
  viewed: Scalars['Boolean'];
};

export type EboTaskSelectionConceptInput = {
  fromWorkOrder: Scalars['Boolean'];
  hazards?: Array<EboHazardObservationConceptInput>;
  id: Scalars['UUID'];
  instanceId?: Scalars['Int'];
  name?: InputMaybe<Scalars['String']>;
  riskLevel: RiskLevel;
  taskHazardConnectorId?: InputMaybe<Scalars['String']>;
};

export type EboTaskSelectionConceptType = {
  __typename?: 'EBOTaskSelectionConceptType';
  fromWorkOrder: Scalars['Boolean'];
  hazards: Array<EboHazardObservationConceptType>;
  id: Scalars['UUID'];
  instanceId: Scalars['Int'];
  name?: Maybe<Scalars['String']>;
  riskLevel: RiskLevel;
  taskHazardConnectorId?: Maybe<Scalars['String']>;
};

export type Ewp = {
  __typename?: 'EWP';
  equipmentInformation: Array<EquipmentInformation>;
  id: Scalars['String'];
  metadata: EwpMetadata;
  referencePoints: Array<Scalars['String']>;
};

export type EwpEquipmentInformationInput = {
  circuitBreaker: Scalars['String'];
  switch: Scalars['String'];
  transformer: Scalars['String'];
};

export type EwpInput = {
  equipmentInformation: Array<EwpEquipmentInformationInput>;
  id: Scalars['String'];
  metadata: EwpMetadataInput;
  referencePoints: Array<Scalars['String']>;
};

export type EwpMetadata = {
  __typename?: 'EWPMetadata';
  completed?: Maybe<Scalars['DateTime']>;
  issued: Scalars['DateTime'];
  issuedBy: Scalars['String'];
  procedure: Scalars['String'];
  receivedBy: Scalars['String'];
  remote: Scalars['Boolean'];
};

export type EwpMetadataInput = {
  completed?: InputMaybe<Scalars['DateTime']>;
  issued: Scalars['DateTime'];
  issuedBy: Scalars['String'];
  procedure: Scalars['String'];
  receivedBy: Scalars['String'];
  remote: Scalars['Boolean'];
};

export type EditActivityInput = {
  crewId?: InputMaybe<Scalars['UUID']>;
  criticalDescription?: InputMaybe<Scalars['String']>;
  endDate?: InputMaybe<Scalars['Date']>;
  id: Scalars['UUID'];
  isCritical?: InputMaybe<Scalars['Boolean']>;
  libraryActivityTypeId?: InputMaybe<Scalars['UUID']>;
  name?: InputMaybe<Scalars['String']>;
  startDate?: InputMaybe<Scalars['Date']>;
  status?: InputMaybe<ActivityStatus>;
};

export type EditHazardControlInput = {
  id?: InputMaybe<Scalars['UUID']>;
  isApplicable?: Scalars['Boolean'];
  libraryControlId: Scalars['UUID'];
};

export type EditHazardInput = {
  controls?: Array<EditHazardControlInput>;
  id?: InputMaybe<Scalars['UUID']>;
  isApplicable?: Scalars['Boolean'];
  libraryHazardId: Scalars['UUID'];
};

export type EditProjectInput = {
  additionalSupervisors?: InputMaybe<Array<Scalars['UUID']>>;
  contractName?: InputMaybe<Scalars['String']>;
  contractReference?: InputMaybe<Scalars['String']>;
  contractorId?: InputMaybe<Scalars['UUID']>;
  description?: InputMaybe<Scalars['String']>;
  endDate: Scalars['Date'];
  engineerName?: InputMaybe<Scalars['String']>;
  externalKey?: InputMaybe<Scalars['String']>;
  id: Scalars['UUID'];
  libraryAssetTypeId?: InputMaybe<Scalars['UUID']>;
  libraryDivisionId?: InputMaybe<Scalars['UUID']>;
  libraryProjectTypeId?: InputMaybe<Scalars['UUID']>;
  libraryRegionId?: InputMaybe<Scalars['UUID']>;
  locations: Array<EditProjectLocationInput>;
  managerId?: InputMaybe<Scalars['UUID']>;
  name: Scalars['String'];
  number?: InputMaybe<Scalars['String']>;
  projectZipCode?: InputMaybe<Scalars['String']>;
  startDate: Scalars['Date'];
  status: ProjectStatus;
  supervisorId?: InputMaybe<Scalars['UUID']>;
  workTypeIds?: InputMaybe<Array<Scalars['UUID']>>;
};

export type EditProjectLocationInput = {
  additionalSupervisors?: InputMaybe<Array<Scalars['UUID']>>;
  externalKey?: InputMaybe<Scalars['String']>;
  id?: InputMaybe<Scalars['UUID']>;
  latitude: Scalars['Decimal'];
  longitude: Scalars['Decimal'];
  name: Scalars['String'];
  supervisorId?: InputMaybe<Scalars['UUID']>;
};

export type EditSiteConditionInput = {
  hazards?: Array<EditHazardInput>;
  id: Scalars['UUID'];
};

export type EditTaskInput = {
  hazards?: Array<EditHazardInput>;
  id: Scalars['UUID'];
};

export type EditTenantInput = {
  authRealmName: Scalars['String'];
  displayName: Scalars['String'];
  tenantName: Scalars['String'];
};

export type EmergencyContact = {
  __typename?: 'EmergencyContact';
  name: Scalars['String'];
  phoneNumber: Scalars['String'];
  primary: Scalars['Boolean'];
};

export type EmergencyContactInput = {
  name: Scalars['String'];
  phoneNumber: Scalars['String'];
  primary: Scalars['Boolean'];
};

export type EnergyBasedObservation = FormInterface & {
  __typename?: 'EnergyBasedObservation';
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  contents: EnergyBasedObservationLayout;
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location?: Maybe<ProjectLocation>;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  operatingHq?: Maybe<Scalars['String']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type EnergyBasedObservationFormsList = FormInterfaceWithContents & {
  __typename?: 'EnergyBasedObservationFormsList';
  Contents: Scalars['JSON'];
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  contents: Scalars['JSON'];
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location?: Maybe<ProjectLocation>;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  operatingHq?: Maybe<Scalars['String']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type EnergyBasedObservationInput = {
  activities?: InputMaybe<Array<EboActivityConceptInput>>;
  additionalInformation?: InputMaybe<Scalars['String']>;
  details?: InputMaybe<ObservationDetailsConceptInput>;
  gpsCoordinates?: InputMaybe<Array<GpsCoordinatesInput>>;
  highEnergyTasks?: InputMaybe<Array<EboHighEnergyTaskConceptInput>>;
  historicIncidents?: InputMaybe<Array<Scalars['String']>>;
  personnel?: InputMaybe<Array<PersonnelConceptInput>>;
  photos?: InputMaybe<Array<FileInput>>;
  sourceInfo?: InputMaybe<SourceInformationConceptsInput>;
  summary?: InputMaybe<EboSummaryInput>;
};

export type EnergyBasedObservationLayout = {
  __typename?: 'EnergyBasedObservationLayout';
  activities?: Maybe<Array<EboActivityConceptType>>;
  additionalInformation?: Maybe<Scalars['String']>;
  completions?: Maybe<Array<Completion>>;
  details?: Maybe<ObservationDetailsConceptType>;
  gpsCoordinates?: Maybe<Array<GpsCoordinates>>;
  highEnergyTasks?: Maybe<Array<EboHighEnergyTaskConceptType>>;
  historicIncidents?: Maybe<Array<Scalars['String']>>;
  personnel?: Maybe<Array<PersonnelConceptType>>;
  photos?: Maybe<Array<File>>;
  sourceInfo?: Maybe<SourceInformationConceptsType>;
  summary?: Maybe<EboSummaryType>;
};

export type EnergyControlInfoInput = {
  controlInfoValues?: InputMaybe<Scalars['String']>;
  id: Scalars['Int'];
  name: Scalars['String'];
};

export type EnergyControlInfoType = {
  __typename?: 'EnergyControlInfoType';
  controlInfoValues?: Maybe<Scalars['String']>;
  id: Scalars['Int'];
  name: Scalars['String'];
};

export type EnergyControlsInput = {
  controls?: InputMaybe<Array<ControlsConceptInput>>;
};

export type EnergyControlsype = {
  __typename?: 'EnergyControlsype';
  controls?: Maybe<Array<ControlsConceptType>>;
};

export type EnergyHazardsInput = {
  controls?: InputMaybe<EnergyControlsInput>;
  controlsImplemented?: Scalars['Boolean'];
  customControls?: InputMaybe<EnergyControlsInput>;
  energyTypes?: InputMaybe<Scalars['String']>;
  id: Scalars['UUID'];
  name?: InputMaybe<Scalars['String']>;
};

export type EnergyHazardsType = {
  __typename?: 'EnergyHazardsType';
  controls?: Maybe<EnergyControlsype>;
  controlsImplemented: Scalars['Boolean'];
  customControls?: Maybe<EnergyControlsype>;
  energyTypes?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  name?: Maybe<Scalars['String']>;
};

export enum EnergyLevel {
  HighEnergy = 'HIGH_ENERGY',
  LowEnergy = 'LOW_ENERGY',
  NotDefined = 'NOT_DEFINED'
}

export type EnergySourceControl = {
  __typename?: 'EnergySourceControl';
  arcFlashCategory?: Maybe<Scalars['Int']>;
  clearancePoints?: Maybe<Scalars['String']>;
  ewp: Array<Ewp>;
  transferOfControl: Scalars['Boolean'];
  voltages: Array<Voltage>;
};

export type EnergySourceControlInput = {
  arcFlashCategory?: InputMaybe<Scalars['Int']>;
  clearancePoints?: InputMaybe<Scalars['String']>;
  ewp: Array<EwpInput>;
  transferOfControl: Scalars['Boolean'];
  voltages: Array<VoltageInput>;
};

export enum EnergyType {
  Biological = 'BIOLOGICAL',
  Chemical = 'CHEMICAL',
  Electrical = 'ELECTRICAL',
  Gravity = 'GRAVITY',
  Mechanical = 'MECHANICAL',
  Motion = 'MOTION',
  NotDefined = 'NOT_DEFINED',
  Pressure = 'PRESSURE',
  Radiation = 'RADIATION',
  Sound = 'SOUND',
  Temperature = 'TEMPERATURE'
}

export type EntityConfigurationInput = {
  attributes?: InputMaybe<Array<AttributeConfigurationInput>>;
  key: Scalars['String'];
  label: Scalars['String'];
  labelPlural: Scalars['String'];
};

export type EquipmentInformation = {
  __typename?: 'EquipmentInformation';
  circuitBreaker: Scalars['String'];
  switch: Scalars['String'];
  transformer: Scalars['String'];
};

export type File = {
  __typename?: 'File';
  category?: Maybe<FileCategory>;
  crc32c?: Maybe<Scalars['String']>;
  date?: Maybe<Scalars['Date']>;
  description?: Maybe<Scalars['String']>;
  displayName: Scalars['String'];
  exists: Scalars['Boolean'];
  id: Scalars['String'];
  md5?: Maybe<Scalars['String']>;
  mimetype?: Maybe<Scalars['String']>;
  name: Scalars['String'];
  signedUrl: Scalars['String'];
  size?: Maybe<Scalars['String']>;
  time?: Maybe<Scalars['String']>;
  url: Scalars['String'];
};

export enum FileCategory {
  Hasp = 'HASP',
  Jha = 'JHA',
  Other = 'OTHER',
  Pssr = 'PSSR'
}

export type FileInput = {
  category?: InputMaybe<FileCategory>;
  crc32c?: InputMaybe<Scalars['String']>;
  date?: InputMaybe<Scalars['Date']>;
  description?: InputMaybe<Scalars['String']>;
  displayName: Scalars['String'];
  id?: InputMaybe<Scalars['String']>;
  md5?: InputMaybe<Scalars['String']>;
  mimetype?: InputMaybe<Scalars['String']>;
  name: Scalars['String'];
  signedUrl?: InputMaybe<Scalars['String']>;
  size?: InputMaybe<Scalars['String']>;
  time?: InputMaybe<Scalars['String']>;
  url?: Scalars['String'];
};

export type FilterLocationDateRange = {
  __typename?: 'FilterLocationDateRange';
  activities: Array<Activity>;
  additionalSupervisors: Array<Supervisor>;
  address?: Maybe<Scalars['String']>;
  dailyReports: Array<DatedReportsResponse>;
  dailySnapshots: Array<CriticalActivityType>;
  datedActivities: Array<DatedActivitiesResponse>;
  datedSiteConditions: Array<DatedSiteConditions>;
  datedTasks: Array<DatedTaskResponse>;
  endDate?: Maybe<Scalars['Date']>;
  externalKey?: Maybe<Scalars['String']>;
  hazardControlSettings: Array<LocationHazardControlSettings>;
  id: Scalars['UUID'];
  jobSafetyBriefings: Array<DatedJsbResponse>;
  latitude: Scalars['Decimal'];
  longitude: Scalars['Decimal'];
  name: Scalars['String'];
  project?: Maybe<Project>;
  risk: RiskLevel;
  riskCalculation?: Maybe<RiskCalculationDetails>;
  riskLevel: RiskLevel;
  riskLevels: Array<DatedRiskLevel>;
  siteConditions: Array<SiteCondition>;
  startDate?: Maybe<Scalars['Date']>;
  supervisor?: Maybe<Supervisor>;
  tasks: Array<Task>;
};


export type FilterLocationDateRangeActivitiesArgs = {
  date?: InputMaybe<Scalars['Date']>;
  endDate?: InputMaybe<Scalars['Date']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
  startDate?: InputMaybe<Scalars['Date']>;
};


export type FilterLocationDateRangeDailyReportsArgs = {
  filterDateRange: DateRangeInput;
};


export type FilterLocationDateRangeDailySnapshotsArgs = {
  dateRange: DateRangeInput;
};


export type FilterLocationDateRangeDatedActivitiesArgs = {
  filterDateRange: DateRangeInput;
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type FilterLocationDateRangeDatedSiteConditionsArgs = {
  filterDateRange: DateRangeInput;
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type FilterLocationDateRangeDatedTasksArgs = {
  filterDateRange: DateRangeInput;
  orderBy?: InputMaybe<Array<TaskOrderBy>>;
};


export type FilterLocationDateRangeJobSafetyBriefingsArgs = {
  filterDateRange: DateRangeInput;
};


export type FilterLocationDateRangeRiskCalculationArgs = {
  date?: InputMaybe<Scalars['Date']>;
};


export type FilterLocationDateRangeRiskLevelArgs = {
  date?: InputMaybe<Scalars['Date']>;
};


export type FilterLocationDateRangeRiskLevelsArgs = {
  filterDateRange: DateRangeInput;
};


export type FilterLocationDateRangeSiteConditionsArgs = {
  date?: InputMaybe<Scalars['Date']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type FilterLocationDateRangeTasksArgs = {
  date?: InputMaybe<Scalars['Date']>;
  orderBy?: InputMaybe<Array<TaskOrderBy>>;
};

export type FirstAidaedLocation = {
  __typename?: 'FirstAIDAEDLocation';
  id: Scalars['UUID'];
  locationName: Scalars['String'];
  locationType: LocationType;
};

export type FirstAidLocationInput = {
  firstAidLocationName: Scalars['String'];
  id: Scalars['UUID'];
};

export type FirstAidLocationType = {
  __typename?: 'FirstAidLocationType';
  firstAidLocationName: Scalars['String'];
  id: Scalars['UUID'];
};

export type FormDefinition = {
  __typename?: 'FormDefinition';
  externalKey: Scalars['String'];
  id: Scalars['UUID'];
  name: Scalars['String'];
  status: FormDefinitionStatus;
};

export enum FormDefinitionStatus {
  Active = 'ACTIVE',
  Inactive = 'INACTIVE'
}

export type FormInterface = {
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location?: Maybe<ProjectLocation>;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  operatingHq?: Maybe<Scalars['String']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type FormInterfaceWithContents = {
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location?: Maybe<ProjectLocation>;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  operatingHq?: Maybe<Scalars['String']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type FormListFilterOptions = {
  __typename?: 'FormListFilterOptions';
  createdByUsers: Array<OptionItem>;
  formIds: Array<Scalars['String']>;
  formNames: Array<Scalars['String']>;
  locations: Array<OptionItem>;
  operatingHqs: Array<Scalars['String']>;
  supervisors: Array<OptionItem>;
  updatedByUsers: Array<OptionItem>;
  workPackages: Array<OptionItem>;
};

export type FormListFilterSearchInput = {
  searchColumn: Scalars['String'];
  searchValue: Scalars['String'];
};

export type FormListOrderBy = {
  direction: OrderByDirection;
  field: FormListOrderByField;
};

export enum FormListOrderByField {
  CreatedAt = 'CREATED_AT',
  Id = 'ID',
  Status = 'STATUS',
  UpdatedAt = 'UPDATED_AT'
}

export enum FormStatus {
  Complete = 'COMPLETE',
  InProgress = 'IN_PROGRESS',
  PendingPostJobBrief = 'PENDING_POST_JOB_BRIEF',
  PendingSignOff = 'PENDING_SIGN_OFF'
}

export type FormStatusInput = {
  status: FormStatus;
};

export enum FormType {
  EnergyBasedObservation = 'ENERGY_BASED_OBSERVATION',
  JobSafetyBriefing = 'JOB_SAFETY_BRIEFING',
  NatgridJobSafetyBriefing = 'NATGRID_JOB_SAFETY_BRIEFING'
}

export type FormsNotificationsInput = {
  createdAt?: InputMaybe<Scalars['DateTime']>;
  formType: FormType;
  notificationType: NotificationsType;
  receiverIds: Array<RecieverInput>;
};

export type GpsCoordinates = {
  __typename?: 'GPSCoordinates';
  latitude: Scalars['Decimal'];
  longitude: Scalars['Decimal'];
};

export type GpsCoordinatesInput = {
  latitude: Scalars['Decimal'];
  longitude: Scalars['Decimal'];
};

export type GeneralReferenceMaterialInput = {
  category?: InputMaybe<Scalars['String']>;
  id: Scalars['Int'];
  link: Scalars['String'];
  name: Scalars['String'];
};

export type GeneralReferenceMaterialType = {
  __typename?: 'GeneralReferenceMaterialType';
  category?: Maybe<Scalars['String']>;
  id: Scalars['Int'];
  link: Scalars['String'];
  name: Scalars['String'];
};

export type GroupDiscussionInformationInput = {
  groupDiscussionNotes?: InputMaybe<Scalars['String']>;
  viewed: Scalars['Boolean'];
};

export type GroupDiscussionInformationType = {
  __typename?: 'GroupDiscussionInformationType';
  groupDiscussionNotes?: Maybe<Scalars['String']>;
  viewed: Scalars['Boolean'];
};

export type GroupDiscussionInput = {
  viewed: Scalars['Boolean'];
};

export type GroupDiscussionType = {
  __typename?: 'GroupDiscussionType';
  viewed: Scalars['Boolean'];
};

export type HazardAnalysis = {
  __typename?: 'HazardAnalysis';
  controls: Array<ControlAnalysis>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  name: Scalars['String'];
  notApplicableReason?: Maybe<Scalars['String']>;
};

export type HazardAnalysisInput = {
  controls: Array<ControlAnalysisInput>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  name?: InputMaybe<Scalars['String']>;
  notApplicableReason?: InputMaybe<Scalars['String']>;
};

export type HazardsControlsInput = {
  additionalComments?: InputMaybe<Scalars['String']>;
  customHazards?: InputMaybe<CustomHazardsInput>;
  energyTypes: Array<Scalars['String']>;
  manuallyAddedHazards?: InputMaybe<HighLowEnergyHazardsInput>;
  siteConditions?: InputMaybe<Array<TaskSiteConditonEnergyHazardsInput>>;
  tasks?: InputMaybe<Array<TaskSiteConditonEnergyHazardsInput>>;
};

export type HazardsControlsType = {
  __typename?: 'HazardsControlsType';
  additionalComments?: Maybe<Scalars['String']>;
  customHazards?: Maybe<CustomHazardsType>;
  energyTypes: Array<Scalars['String']>;
  manuallyAddedHazards?: Maybe<HighLowEnergyHazardsType>;
  siteConditions?: Maybe<Array<TaskSiteConditonEnergyHazardsType>>;
  tasks?: Maybe<Array<TaskSiteConditonEnergyHazardsType>>;
};

export type HighLowEnergyHazardsInput = {
  highEnergyHazards?: InputMaybe<Array<EnergyHazardsInput>>;
  lowEnergyHazards?: InputMaybe<Array<EnergyHazardsInput>>;
};

export type HighLowEnergyHazardsType = {
  __typename?: 'HighLowEnergyHazardsType';
  highEnergyHazards?: Maybe<Array<EnergyHazardsType>>;
  lowEnergyHazards?: Maybe<Array<EnergyHazardsType>>;
};

export type Incident = {
  __typename?: 'Incident';
  archivedAt?: Maybe<Scalars['DateTime']>;
  description: Scalars['String'];
  id: Scalars['UUID'];
  incidentDate: Scalars['Date'];
  incidentId?: Maybe<Scalars['String']>;
  incidentType: Scalars['String'];
  severity?: Maybe<Scalars['String']>;
  severityCode?: Maybe<IncidentSeverityEnum>;
  taskType?: Maybe<Scalars['String']>;
  taskTypeId?: Maybe<Scalars['UUID']>;
};

export enum IncidentSeverityEnum {
  Deaths = 'DEATHS',
  FirstAidOnly = 'FIRST_AID_ONLY',
  LostTime = 'LOST_TIME',
  NearDeaths = 'NEAR_DEATHS',
  NotApplicable = 'NOT_APPLICABLE',
  OtherNonOccupational = 'OTHER_NON_OCCUPATIONAL',
  ReportPurposesOnly = 'REPORT_PURPOSES_ONLY',
  RestrictionOrJobTransfer = 'RESTRICTION_OR_JOB_TRANSFER'
}

export type IngestColumn = {
  __typename?: 'IngestColumn';
  attribute: Scalars['String'];
  ignoreOnIngest: Scalars['Boolean'];
  name: Scalars['String'];
  requiredOnIngest: Scalars['Boolean'];
};

export type IngestOption = {
  __typename?: 'IngestOption';
  columns: Array<IngestColumn>;
  description: Scalars['String'];
  id: IngestType;
  name: Scalars['String'];
};

export type IngestOptionItems = {
  __typename?: 'IngestOptionItems';
  items: Array<Scalars['DictScalar']>;
};

export type IngestOptions = {
  __typename?: 'IngestOptions';
  options: Array<IngestOption>;
};

export type IngestSubmitType = {
  __typename?: 'IngestSubmitType';
  added: Array<Scalars['DictScalar']>;
  deleted: Array<Scalars['DictScalar']>;
  items: Array<Scalars['DictScalar']>;
  key: IngestType;
  updated: Array<Scalars['DictScalar']>;
};

export enum IngestType {
  CompatibleUnits = 'compatible_units',
  ElementTaskLink = 'element_task_link',
  Elements = 'elements',
  HydroOneJobTypeTaskMap = 'hydro_one_job_type_task_map',
  HydroOneWo = 'hydro_one_wo',
  IncidentToLibraryTaskLink = 'incident_to_library_task_link',
  LibraryActivityTypes = 'library_activity_types',
  LibraryActivityTypesForTenant = 'library_activity_types_for_tenant',
  LibraryDivisions = 'library_divisions',
  LibraryRegions = 'library_regions',
  LibraryTasks = 'library_tasks',
  WorkpackageToCompatibleUnitMapping = 'workpackage_to_compatible_unit_mapping',
  WorktypeLink = 'worktype_link'
}

export type Insight = {
  __typename?: 'Insight';
  createdAt: Scalars['DateTime'];
  description?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  name: Scalars['String'];
  url: Scalars['String'];
  visibility: Scalars['Boolean'];
};

export enum JsbFiltersOnEnum {
  ProjectLocation = 'PROJECT_LOCATION',
  UserDetails = 'USER_DETAILS'
}

export type JsbMetadata = {
  __typename?: 'JSBMetadata';
  briefingDateTime: Scalars['DateTime'];
};

export type JsbMetadataInput = {
  briefingDateTime: Scalars['DateTime'];
};

export type JsbSupervisor = {
  __typename?: 'JSBSupervisor';
  email: Scalars['String'];
  id: Scalars['String'];
  name: Scalars['String'];
};

export type JobHazardAnalysisSection = {
  __typename?: 'JobHazardAnalysisSection';
  sectionIsValid?: Maybe<Scalars['Boolean']>;
  siteConditions: Array<SiteConditionAnalysis>;
  tasks: Array<TaskAnalysis>;
};

export type JobHazardAnalysisSectionInput = {
  sectionIsValid?: InputMaybe<Scalars['Boolean']>;
  siteConditions: Array<SiteConditionAnalysisInput>;
  tasks: Array<TaskAnalysisInput>;
};

export type JobSafetyBriefing = FormInterface & {
  __typename?: 'JobSafetyBriefing';
  archivedAt?: Maybe<Scalars['Date']>;
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  contents: JobSafetyBriefingLayout;
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location?: Maybe<ProjectLocation>;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  name: Scalars['String'];
  operatingHq?: Maybe<Scalars['String']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type JobSafetyBriefingFormsList = FormInterfaceWithContents & {
  __typename?: 'JobSafetyBriefingFormsList';
  Contents: Scalars['JSON'];
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  contents: Scalars['JSON'];
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location?: Maybe<ProjectLocation>;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  name: Scalars['String'];
  operatingHq?: Maybe<Scalars['String']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type JobSafetyBriefingLayout = {
  __typename?: 'JobSafetyBriefingLayout';
  activities?: Maybe<Array<ActivityConceptType>>;
  additionalPpe?: Maybe<Array<Scalars['String']>>;
  aedInformation?: Maybe<AedInformation>;
  completions?: Maybe<Array<Completion>>;
  controlAssessmentSelections?: Maybe<Array<ControlAssessment>>;
  crewSignOff?: Maybe<Array<CrewInformationType>>;
  criticalRiskAreaSelections?: Maybe<Array<CriticalRiskArea>>;
  customNearestMedicalFacility?: Maybe<CustomMedicalFacility>;
  distributionBulletinSelections?: Maybe<Array<Scalars['String']>>;
  documents?: Maybe<Array<File>>;
  emergencyContacts?: Maybe<Array<EmergencyContact>>;
  energySourceControl?: Maybe<EnergySourceControl>;
  gpsCoordinates?: Maybe<Array<GpsCoordinates>>;
  groupDiscussion?: Maybe<GroupDiscussionType>;
  hazardsAndControlsNotes?: Maybe<Scalars['String']>;
  jsbId: Scalars['UUID'];
  jsbMetadata?: Maybe<JsbMetadata>;
  minimumApproachDistance?: Maybe<Scalars['String']>;
  nearestMedicalFacility?: Maybe<MedicalFacility>;
  otherWorkProcedures?: Maybe<Scalars['String']>;
  photos?: Maybe<Array<File>>;
  recommendedTaskSelections?: Maybe<Array<RecommendedTaskSelection>>;
  siteConditionSelections?: Maybe<Array<SiteConditionSelection>>;
  sourceInfo?: Maybe<SourceInformationConceptsType>;
  taskSelections?: Maybe<Array<TaskSelectionConcept>>;
  workLocation?: Maybe<WorkLocation>;
  workPackageMetadata?: Maybe<WorkPackageMetadata>;
  workProcedureSelections?: Maybe<Array<WorkProcedureSelection>>;
};

export type LibraryActivityGroup = {
  __typename?: 'LibraryActivityGroup';
  aliases: Array<Maybe<Scalars['String']>>;
  id: Scalars['UUID'];
  name: Scalars['String'];
  tasks: Array<LibraryTask>;
  workTypes?: Maybe<Array<WorkTypeWithActivityAliasType>>;
};


export type LibraryActivityGroupTasksArgs = {
  orderBy?: InputMaybe<Array<LibraryTaskOrderBy>>;
};

export type LibraryActivityType = {
  __typename?: 'LibraryActivityType';
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type LibraryAsset = {
  __typename?: 'LibraryAsset';
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type LibraryControl = {
  __typename?: 'LibraryControl';
  archivedAt?: Maybe<Scalars['DateTime']>;
  controlType?: Maybe<TypeOfControl>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  name: Scalars['String'];
  ppe?: Maybe<Scalars['Boolean']>;
};

export type LibraryDivision = {
  __typename?: 'LibraryDivision';
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export enum LibraryFilterType {
  SiteCondition = 'SITE_CONDITION',
  Task = 'TASK'
}

export type LibraryHazard = {
  __typename?: 'LibraryHazard';
  archivedAt?: Maybe<Scalars['DateTime']>;
  controls: Array<LibraryControl>;
  energyLevel?: Maybe<EnergyLevel>;
  energyType?: Maybe<EnergyType>;
  id: Scalars['UUID'];
  imageUrl: Scalars['String'];
  imageUrlPng: Scalars['String'];
  isApplicable: Scalars['Boolean'];
  name: Scalars['String'];
  taskApplicabilityLevels: Array<TaskApplicabilityLevel>;
};


export type LibraryHazardControlsArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};

export type LibraryProjectType = {
  __typename?: 'LibraryProjectType';
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type LibraryRegion = {
  __typename?: 'LibraryRegion';
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type LibrarySiteCondition = {
  __typename?: 'LibrarySiteCondition';
  archivedAt?: Maybe<Scalars['DateTime']>;
  hazards: Array<LibraryHazard>;
  id: Scalars['UUID'];
  name: Scalars['String'];
};


export type LibrarySiteConditionHazardsArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};

export type LibraryTask = {
  __typename?: 'LibraryTask';
  activitiesGroups?: Maybe<Array<LibraryActivityGroup>>;
  category?: Maybe<Scalars['String']>;
  hazards: Array<LibraryHazard>;
  hespScore: Scalars['Int'];
  id: Scalars['UUID'];
  isCritical: Scalars['Boolean'];
  name: Scalars['String'];
  riskLevel: RiskLevel;
  standardOperatingProcedures?: Maybe<Array<StandardOperatingProcedure>>;
  workTypes?: Maybe<Array<WorkType>>;
};


export type LibraryTaskHazardsArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type LibraryTaskWorkTypesArgs = {
  tenantId?: InputMaybe<Scalars['UUID']>;
};

export type LibraryTaskOrderBy = {
  direction: OrderByDirection;
  field: LibraryTaskOrderByField;
};

export enum LibraryTaskOrderByField {
  Category = 'CATEGORY',
  Id = 'ID',
  Name = 'NAME'
}

export type LinkedLibraryControl = {
  __typename?: 'LinkedLibraryControl';
  archivedAt?: Maybe<Scalars['DateTime']>;
  controlType?: Maybe<TypeOfControl>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  name: Scalars['String'];
  ppe?: Maybe<Scalars['Boolean']>;
};

export type LinkedLibraryHazard = {
  __typename?: 'LinkedLibraryHazard';
  archivedAt?: Maybe<Scalars['DateTime']>;
  controls: Array<LinkedLibraryControl>;
  energyLevel?: Maybe<EnergyLevel>;
  energyType?: Maybe<EnergyType>;
  id: Scalars['UUID'];
  imageUrl: Scalars['String'];
  imageUrlPng: Scalars['String'];
  isApplicable: Scalars['Boolean'];
  name: Scalars['String'];
  taskApplicabilityLevels: Array<TaskApplicabilityLevel>;
};


export type LinkedLibraryHazardControlsArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};

export type LinkedLibrarySiteCondition = {
  __typename?: 'LinkedLibrarySiteCondition';
  archivedAt?: Maybe<Scalars['DateTime']>;
  hazards: Array<LinkedLibraryHazard>;
  id: Scalars['UUID'];
  name: Scalars['String'];
  workTypes?: Maybe<Array<WorkType>>;
};


export type LinkedLibrarySiteConditionHazardsArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type LinkedLibrarySiteConditionWorkTypesArgs = {
  tenantId?: InputMaybe<Scalars['UUID']>;
};

export type LinkedLibraryTask = {
  __typename?: 'LinkedLibraryTask';
  activitiesGroups?: Maybe<Array<LibraryActivityGroup>>;
  archivedAt?: Maybe<Scalars['DateTime']>;
  category?: Maybe<Scalars['String']>;
  hazards: Array<LinkedLibraryHazard>;
  hespScore: Scalars['Int'];
  id: Scalars['UUID'];
  isCritical: Scalars['Boolean'];
  name: Scalars['String'];
  riskLevel: RiskLevel;
  standardOperatingProcedures?: Maybe<Array<StandardOperatingProcedure>>;
  workTypes?: Maybe<Array<WorkType>>;
};


export type LinkedLibraryTaskHazardsArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type LinkedLibraryTaskWorkTypesArgs = {
  tenantId?: InputMaybe<Scalars['UUID']>;
};

export type LocationFilterBy = {
  field: LocationFilterByField;
  values: Array<Scalars['String']>;
};

export enum LocationFilterByField {
  Contractor = 'CONTRACTOR',
  Divisions = 'DIVISIONS',
  Project = 'PROJECT',
  ProjectStatus = 'PROJECT_STATUS',
  Regions = 'REGIONS',
  Risk = 'RISK',
  Supervisor = 'SUPERVISOR',
  Types = 'TYPES',
  WorkTypes = 'WORK_TYPES'
}

export type LocationHazardControlSettings = {
  __typename?: 'LocationHazardControlSettings';
  createdAt: Scalars['DateTime'];
  disabled: Scalars['Boolean'];
  id: Scalars['UUID'];
  libraryControlId?: Maybe<Scalars['UUID']>;
  libraryHazardId: Scalars['UUID'];
  locationId: Scalars['UUID'];
  userId: Scalars['UUID'];
};

export type LocationHazardControlSettingsInput = {
  libraryControlId?: InputMaybe<Scalars['UUID']>;
  libraryHazardId: Scalars['UUID'];
  locationId: Scalars['UUID'];
};

export type LocationInformationInput = {
  address?: InputMaybe<Scalars['String']>;
  city?: InputMaybe<Scalars['String']>;
  landmark?: InputMaybe<Scalars['String']>;
  minimumApproachDistance: Scalars['String'];
  operatingHq?: InputMaybe<Scalars['String']>;
  state?: InputMaybe<Scalars['String']>;
  vehicleNumber?: InputMaybe<Array<Scalars['String']>>;
};

export type LocationInformationType = {
  __typename?: 'LocationInformationType';
  address?: Maybe<Scalars['String']>;
  city?: Maybe<Scalars['String']>;
  landmark?: Maybe<Scalars['String']>;
  minimumApproachDistance: Scalars['String'];
  operatingHq?: Maybe<Scalars['String']>;
  state?: Maybe<Scalars['String']>;
  vehicleNumber?: Maybe<Array<Scalars['String']>>;
};

export type LocationInformationV2Input = {
  address?: InputMaybe<Scalars['String']>;
  circuit?: InputMaybe<Scalars['String']>;
  city?: InputMaybe<Scalars['String']>;
  createdAt: Scalars['DateTime'];
  gpsCoordinates?: InputMaybe<GpsCoordinatesInput>;
  landmark?: InputMaybe<Scalars['String']>;
  state?: InputMaybe<Scalars['String']>;
  voltageInformation?: InputMaybe<VoltageInformationV2Input>;
};

export type LocationInformationV2Type = {
  __typename?: 'LocationInformationV2Type';
  address?: Maybe<Scalars['String']>;
  circuit?: Maybe<Scalars['String']>;
  city?: Maybe<Scalars['String']>;
  createdAt: Scalars['DateTime'];
  gpsCoordinates?: Maybe<GpsCoordinates>;
  landmark?: Maybe<Scalars['String']>;
  state?: Maybe<Scalars['String']>;
  voltageInformation?: Maybe<VoltageInformationV2Type>;
};

export type LocationOrderBy = {
  direction: OrderByDirection;
  field: LocationOrderByField;
};

export enum LocationOrderByField {
  LocationName = 'LOCATION_NAME'
}

export type LocationReturnType = {
  __typename?: 'LocationReturnType';
  id: Scalars['UUID'];
};

export type LocationRiskLevelByDate = {
  __typename?: 'LocationRiskLevelByDate';
  location?: Maybe<ProjectLocation>;
  locationName: Scalars['String'];
  projectName: Scalars['String'];
  riskLevelByDate: Array<RiskLevelByDate>;
};

export type LocationRiskLevelCount = {
  __typename?: 'LocationRiskLevelCount';
  count: Scalars['Int'];
  date: Scalars['Date'];
  riskLevel: RiskLevel;
};

export enum LocationType {
  AedLocation = 'AED_LOCATION',
  BurnKitLocation = 'BURN_KIT_LOCATION',
  FirstAidLocation = 'FIRST_AID_LOCATION'
}

export type Manager = {
  __typename?: 'Manager';
  firstName?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  lastName?: Maybe<Scalars['String']>;
  name: Scalars['String'];
};

export type MapExtentInput = {
  xMax: Scalars['Float'];
  xMin: Scalars['Float'];
  yMax: Scalars['Float'];
  yMin: Scalars['Float'];
};

export type Me = {
  __typename?: 'Me';
  email?: Maybe<Scalars['String']>;
  firstName?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  lastName?: Maybe<Scalars['String']>;
  name: Scalars['String'];
  opco?: Maybe<Opco>;
  permissions?: Maybe<Array<Permission>>;
  role?: Maybe<Scalars['String']>;
  tenant: MyTenant;
  tenantName: Scalars['String'];
  userPreferences: Array<UserPreference>;
};

export type MedicalFacility = {
  __typename?: 'MedicalFacility';
  address?: Maybe<Scalars['String']>;
  city?: Maybe<Scalars['String']>;
  description: Scalars['String'];
  distanceFromJob?: Maybe<Scalars['Float']>;
  phoneNumber?: Maybe<Scalars['String']>;
  state?: Maybe<Scalars['String']>;
  zip?: Maybe<Scalars['Int']>;
};

export type MedicalFacilityInput = {
  address?: InputMaybe<Scalars['String']>;
  city?: InputMaybe<Scalars['String']>;
  description: Scalars['String'];
  distanceFromJob?: InputMaybe<Scalars['Float']>;
  phoneNumber?: InputMaybe<Scalars['String']>;
  state?: InputMaybe<Scalars['String']>;
  zip?: InputMaybe<Scalars['Int']>;
};

export type MedicalInformationInput = {
  aedInformation?: InputMaybe<AedInformationDataInput>;
  burnKitLocation?: InputMaybe<BurnKitLocationInput>;
  customAedLocation?: InputMaybe<CustomMedicalFacilityInput>;
  customBurnKitLocation?: InputMaybe<CustomMedicalFacilityInput>;
  customFirstAidKitLocation?: InputMaybe<CustomMedicalFacilityInput>;
  customMedicalNearestHospital?: InputMaybe<CustomMedicalFacilityInput>;
  firstAidKitLocation?: InputMaybe<FirstAidLocationInput>;
  nearestHospital?: InputMaybe<MedicalFacilityInput>;
  vehicleNumber?: InputMaybe<Array<Scalars['String']>>;
};

export type MedicalInformationType = {
  __typename?: 'MedicalInformationType';
  aedInformation?: Maybe<AedInformationDataType>;
  burnKitLocation?: Maybe<BurnKitLocationType>;
  customAedLocation?: Maybe<CustomMedicalFacility>;
  customBurnKitLocation?: Maybe<CustomMedicalFacility>;
  customFirstAidKitLocation?: Maybe<CustomMedicalFacility>;
  customMedicalNearestHospital?: Maybe<CustomMedicalFacility>;
  firstAidKitLocation?: Maybe<FirstAidLocationType>;
  nearestHospital?: Maybe<MedicalFacility>;
  vehicleNumber?: Maybe<Array<Scalars['String']>>;
};

export type MininimumApproachDistanceInput = {
  phaseToGround?: InputMaybe<Scalars['String']>;
  phaseToPhase?: InputMaybe<Scalars['String']>;
};

export type MininimumApproachDistanceType = {
  __typename?: 'MininimumApproachDistanceType';
  phaseToGround?: Maybe<Scalars['String']>;
  phaseToPhase?: Maybe<Scalars['String']>;
};

export type MultipleCrewsInput = {
  crewDiscussion?: InputMaybe<Scalars['Boolean']>;
  multipleCrewInvolved: Scalars['Boolean'];
  personIncharge?: InputMaybe<Array<UserInfoInput>>;
};

export type MultipleCrewsType = {
  __typename?: 'MultipleCrewsType';
  crewDiscussion?: Maybe<Scalars['Boolean']>;
  multipleCrewInvolved: Scalars['Boolean'];
  personIncharge?: Maybe<Array<UserInfoType>>;
};

export type Mutation = {
  __typename?: 'Mutation';
  addLocationHazardControlSettings?: Maybe<Scalars['Void']>;
  addSupervisorToActivity: Scalars['Boolean'];
  addTasksToActivity: Activity;
  archiveAllProjects: Scalars['Int'];
  archiveInsight: Scalars['Boolean'];
  completeEnergyBasedObservation: EnergyBasedObservation;
  /** Validate and save the job safety briefing and mark it complete */
  completeJobSafetyBriefing: JobSafetyBriefing;
  configureTenant: WorkPackageConfiguration;
  createActivity: Activity;
  createInsight: Insight;
  createLocationFromLatLon: LocationReturnType;
  createProject: Project;
  createSiteCondition: SiteCondition;
  createTenant?: Maybe<MyTenant>;
  deleteActivity: Scalars['Boolean'];
  deleteDailyReport: Scalars['Boolean'];
  deleteEnergyBasedObservation: Scalars['Boolean'];
  /** Mark the job safety briefing as deleted */
  deleteJobSafetyBriefing: Scalars['Boolean'];
  /** Mark the Natgrid job safety briefing as deleted */
  deleteNatgridJobSafetyBriefing: Scalars['Boolean'];
  deleteProject: Scalars['Boolean'];
  deleteSiteCondition: Scalars['Boolean'];
  deleteTask: Scalars['Boolean'];
  editActivity?: Maybe<Activity>;
  editProject: Project;
  editSiteCondition: SiteCondition;
  editTask: Task;
  editTenant: MyTenant;
  fileUploadPolicies: Array<SignedPostPolicy>;
  ingestCsv: IngestSubmitType;
  recalculate?: Maybe<Scalars['Void']>;
  removeLocationHazardControlSettings?: Maybe<Scalars['Void']>;
  removeSupervisorFromActivity: Scalars['Boolean'];
  removeTasksFromActivity?: Maybe<Activity>;
  reopenEnergyBasedObservation: EnergyBasedObservation;
  /** Mark the job safety briefing as reopened */
  reopenJobSafetyBriefing: JobSafetyBriefing;
  /** Mark the natgrid job safety briefing as reopened */
  reopenNatgridJobSafetyBriefing: NatGridJobSafetyBriefing;
  reorderInsights: Array<Insight>;
  saveDailyReport: DailyReport;
  saveEnergyBasedObservation: EnergyBasedObservation;
  /** Save partial submissions of the job safety briefing */
  saveJobSafetyBriefing: JobSafetyBriefing;
  /** Save submissions of the Natgrid job safety briefing */
  saveNatgridJobSafetyBriefing: NatGridJobSafetyBriefing;
  saveUserPreferences: UserPreference;
  updateDailyReportStatus: DailyReport;
  updateInsight: Insight;
};


export type MutationAddLocationHazardControlSettingsArgs = {
  locationHazardControlSettingInputs: Array<LocationHazardControlSettingsInput>;
};


export type MutationAddSupervisorToActivityArgs = {
  activityId: Scalars['UUID'];
  supervisorId: Scalars['UUID'];
};


export type MutationAddTasksToActivityArgs = {
  id: Scalars['UUID'];
  newTasks: AddActivityTasksInput;
};


export type MutationArchiveInsightArgs = {
  id: Scalars['UUID'];
};


export type MutationCompleteEnergyBasedObservationArgs = {
  energyBasedObservationInput: EnergyBasedObservationInput;
  id: Scalars['UUID'];
};


export type MutationCompleteJobSafetyBriefingArgs = {
  jobSafetyBriefingInput: SaveJobSafetyBriefingInput;
};


export type MutationConfigureTenantArgs = {
  entityConfiguration: EntityConfigurationInput;
};


export type MutationCreateActivityArgs = {
  activityData: CreateActivityInput;
};


export type MutationCreateInsightArgs = {
  createInput: CreateInsightInput;
};


export type MutationCreateLocationFromLatLonArgs = {
  date?: InputMaybe<Scalars['DateTime']>;
  gpsCoordinates: GpsCoordinatesInput;
  name?: InputMaybe<Scalars['String']>;
};


export type MutationCreateProjectArgs = {
  project: CreateProjectInput;
};


export type MutationCreateSiteConditionArgs = {
  data: CreateSiteConditionInput;
};


export type MutationCreateTenantArgs = {
  tenantCreate: CreateTenantInput;
};


export type MutationDeleteActivityArgs = {
  id: Scalars['UUID'];
};


export type MutationDeleteDailyReportArgs = {
  id: Scalars['UUID'];
};


export type MutationDeleteEnergyBasedObservationArgs = {
  id: Scalars['UUID'];
};


export type MutationDeleteJobSafetyBriefingArgs = {
  id: Scalars['UUID'];
};


export type MutationDeleteNatgridJobSafetyBriefingArgs = {
  id: Scalars['UUID'];
};


export type MutationDeleteProjectArgs = {
  id: Scalars['UUID'];
};


export type MutationDeleteSiteConditionArgs = {
  id: Scalars['UUID'];
};


export type MutationDeleteTaskArgs = {
  id: Scalars['UUID'];
};


export type MutationEditActivityArgs = {
  activityData: EditActivityInput;
};


export type MutationEditProjectArgs = {
  project: EditProjectInput;
};


export type MutationEditSiteConditionArgs = {
  data: EditSiteConditionInput;
};


export type MutationEditTaskArgs = {
  taskData: EditTaskInput;
};


export type MutationEditTenantArgs = {
  tenantEdit: EditTenantInput;
};


export type MutationFileUploadPoliciesArgs = {
  count?: Scalars['Int'];
};


export type MutationIngestCsvArgs = {
  body: Scalars['String'];
  delimiter?: Scalars['String'];
  key: IngestType;
};


export type MutationRecalculateArgs = {
  recalculateInput: RecalculateInput;
};


export type MutationRemoveLocationHazardControlSettingsArgs = {
  locationHazardControlSettingIds?: Array<Scalars['UUID']>;
};


export type MutationRemoveSupervisorFromActivityArgs = {
  activityId: Scalars['UUID'];
  supervisorId: Scalars['UUID'];
};


export type MutationRemoveTasksFromActivityArgs = {
  id: Scalars['UUID'];
  taskIdsToBeRemoved: RemoveActivityTasksInput;
};


export type MutationReopenEnergyBasedObservationArgs = {
  id: Scalars['UUID'];
};


export type MutationReopenJobSafetyBriefingArgs = {
  id: Scalars['UUID'];
};


export type MutationReopenNatgridJobSafetyBriefingArgs = {
  id: Scalars['UUID'];
};


export type MutationReorderInsightsArgs = {
  limit?: InputMaybe<Scalars['Int']>;
  orderedIds: Array<Scalars['UUID']>;
};


export type MutationSaveDailyReportArgs = {
  dailyReportInput: SaveDailyReportInput;
};


export type MutationSaveEnergyBasedObservationArgs = {
  energyBasedObservationInput: EnergyBasedObservationInput;
  id?: InputMaybe<Scalars['UUID']>;
};


export type MutationSaveJobSafetyBriefingArgs = {
  jobSafetyBriefingInput: SaveJobSafetyBriefingInput;
};


export type MutationSaveNatgridJobSafetyBriefingArgs = {
  formStatus?: InputMaybe<FormStatusInput>;
  natgridJobSafetyBriefing: NatGridJobSafetyBriefingInput;
  notificationInput?: InputMaybe<FormsNotificationsInput>;
};


export type MutationSaveUserPreferencesArgs = {
  data: Scalars['String'];
  entityType: UserPreferenceEntityType;
  userId: Scalars['UUID'];
};


export type MutationUpdateDailyReportStatusArgs = {
  id: Scalars['UUID'];
  status: FormStatus;
};


export type MutationUpdateInsightArgs = {
  id: Scalars['UUID'];
  updateInput: UpdateInsightInput;
};

export type MyTenant = {
  __typename?: 'MyTenant';
  authRealm?: Maybe<Scalars['String']>;
  configurations: TenantConfigurations;
  displayName: Scalars['String'];
  name: Scalars['String'];
  workos: Array<WorkOs>;
};

export type NatGridEnergySourceControlInput = {
  clearanceNumber?: InputMaybe<Scalars['String']>;
  clearanceTypes: ClearanceTypesInput;
  controls: Array<EnergyControlInfoInput>;
  controlsDescription?: InputMaybe<Scalars['String']>;
  deEnergized?: Scalars['Boolean'];
  energized?: Scalars['Boolean'];
  pointsOfProtection?: Array<PointsOfProtectionInput>;
};

export type NatGridEnergySourceControlType = {
  __typename?: 'NatGridEnergySourceControlType';
  clearanceNumber?: Maybe<Scalars['String']>;
  clearanceTypes: ClearanceTypesType;
  controls: Array<EnergyControlInfoType>;
  controlsDescription?: Maybe<Scalars['String']>;
  deEnergized: Scalars['Boolean'];
  energized: Scalars['Boolean'];
  pointsOfProtection: Array<PointsOfProtectionType>;
};

export type NatGridJobSafetyBriefing = FormInterface & {
  __typename?: 'NatGridJobSafetyBriefing';
  archivedAt?: Maybe<Scalars['Date']>;
  barnLocation?: Maybe<BarnLocationType>;
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  contents: NatGridJobSafetyBriefingLayout;
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location?: Maybe<ProjectLocation>;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  name: Scalars['String'];
  operatingHq?: Maybe<Scalars['String']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type NatGridJobSafetyBriefingFormsList = FormInterfaceWithContents & {
  __typename?: 'NatGridJobSafetyBriefingFormsList';
  Contents: Scalars['JSON'];
  completedAt?: Maybe<Scalars['DateTime']>;
  completedBy?: Maybe<User>;
  contents: Scalars['JSON'];
  createdAt: Scalars['DateTime'];
  createdBy?: Maybe<User>;
  date: Scalars['Date'];
  formId?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  location?: Maybe<ProjectLocation>;
  locationName?: Maybe<Scalars['String']>;
  multipleLocation?: Maybe<Scalars['Boolean']>;
  name: Scalars['String'];
  operatingHq?: Maybe<Scalars['String']>;
  source?: Maybe<SourceInformation>;
  status: FormStatus;
  supervisor?: Maybe<Array<JsbSupervisor>>;
  updatedAt?: Maybe<Scalars['DateTime']>;
  updatedBy?: Maybe<User>;
  workPackage?: Maybe<Project>;
};

export type NatGridJobSafetyBriefingInput = {
  activities?: InputMaybe<Array<ActivityConceptInput>>;
  attachmentSection?: InputMaybe<AttachmentsInput>;
  barnLocation?: InputMaybe<BarnLocationInput>;
  crewSignOff?: InputMaybe<CrewSignOffInput>;
  criticalTasksSelections?: InputMaybe<CriticalTasksSelectionInput>;
  energySourceControl?: InputMaybe<NatGridEnergySourceControlInput>;
  generalReferenceMaterials?: InputMaybe<Array<GeneralReferenceMaterialInput>>;
  gpsCoordinates?: InputMaybe<Array<GpsCoordinatesInput>>;
  groupDiscussion?: InputMaybe<GroupDiscussionInformationInput>;
  hazardsControl?: InputMaybe<HazardsControlsInput>;
  jsbId?: InputMaybe<Scalars['UUID']>;
  jsbMetadata?: InputMaybe<JsbMetadataInput>;
  medicalInformation?: InputMaybe<MedicalInformationInput>;
  postJobBrief?: InputMaybe<PostJobBriefInput>;
  siteConditions?: InputMaybe<NatGridSiteConditionInput>;
  standardOperatingProcedure?: InputMaybe<Array<TaskStandardOperatingProcedureInput>>;
  supervisorSignOff?: InputMaybe<SupervisorSignOffInput>;
  taskHistoricIncidents?: InputMaybe<Array<NatGridTaskHistoricIncidentInput>>;
  voltageInfo?: InputMaybe<VoltageInformationInput>;
  workLocation?: InputMaybe<LocationInformationInput>;
  workLocationWithVoltageInfo?: InputMaybe<Array<LocationInformationV2Input>>;
  workPackageMetadata?: InputMaybe<WorkPackageMetadataInput>;
};

export type NatGridJobSafetyBriefingLayout = {
  __typename?: 'NatGridJobSafetyBriefingLayout';
  activities?: Maybe<Array<ActivityConceptType>>;
  attachmentSection?: Maybe<AttachmentsType>;
  barnLocation?: Maybe<BarnLocationType>;
  completions?: Maybe<Array<Completion>>;
  crewSignOff?: Maybe<CrewSignOffType>;
  criticalTasksSelections?: Maybe<CriticalTasksSelectionType>;
  energySourceControl?: Maybe<NatGridEnergySourceControlType>;
  generalReferenceMaterials?: Maybe<Array<GeneralReferenceMaterialType>>;
  gpsCoordinates?: Maybe<Array<GpsCoordinates>>;
  groupDiscussion?: Maybe<GroupDiscussionInformationType>;
  hazardsControl?: Maybe<HazardsControlsType>;
  jsbId?: Maybe<Scalars['UUID']>;
  jsbMetadata?: Maybe<JsbMetadata>;
  medicalInformation?: Maybe<MedicalInformationType>;
  postJobBrief?: Maybe<PostJobBriefType>;
  siteConditions?: Maybe<NatGridSiteConditionType>;
  standardOperatingProcedure?: Maybe<Array<TaskStandardOperatingProcedureType>>;
  supervisorSignOff?: Maybe<SupervisorSignOffType>;
  taskHistoricIncidents?: Maybe<Array<NatGridTaskHistoricIncidentType>>;
  voltageInfo?: Maybe<VoltageInformationType>;
  workLocation?: Maybe<LocationInformationType>;
  workLocationWithVoltageInfo?: Maybe<Array<LocationInformationV2Type>>;
  workPackageMetadata?: Maybe<WorkPackageMetadata>;
};

export type NatGridSiteConditionInput = {
  additionalComments?: InputMaybe<Scalars['String']>;
  digSafe?: InputMaybe<Scalars['String']>;
  siteConditionSelections?: InputMaybe<Array<SiteConditionSelectionInput>>;
};

export type NatGridSiteConditionType = {
  __typename?: 'NatGridSiteConditionType';
  additionalComments?: Maybe<Scalars['String']>;
  digSafe?: Maybe<Scalars['String']>;
  siteConditionSelections?: Maybe<Array<SiteConditionSelection>>;
};

export type NatGridTaskHistoricIncidentInput = {
  historicIncidents?: InputMaybe<Array<Scalars['String']>>;
  id: Scalars['UUID'];
  name?: InputMaybe<Scalars['String']>;
};

export type NatGridTaskHistoricIncidentType = {
  __typename?: 'NatGridTaskHistoricIncidentType';
  historicIncidents?: Maybe<Array<Scalars['String']>>;
  id: Scalars['UUID'];
  name?: Maybe<Scalars['String']>;
};

export type NotImplementedControlPercent = {
  __typename?: 'NotImplementedControlPercent';
  implemented: Scalars['Int'];
  libraryControl: LibraryControl;
  percent: Scalars['Float'];
  total: Scalars['Int'];
};

export type NotImplementedControlPercentByHazard = {
  __typename?: 'NotImplementedControlPercentByHazard';
  implemented: Scalars['Int'];
  libraryHazard: LibraryHazard;
  percent: Scalars['Float'];
  total: Scalars['Int'];
};

export type NotImplementedControlPercentByLocation = {
  __typename?: 'NotImplementedControlPercentByLocation';
  implemented: Scalars['Int'];
  location: ProjectLocation;
  percent: Scalars['Float'];
  total: Scalars['Int'];
};

export type NotImplementedControlPercentByProject = {
  __typename?: 'NotImplementedControlPercentByProject';
  implemented: Scalars['Int'];
  percent: Scalars['Float'];
  project: Project;
  total: Scalars['Int'];
};

export type NotImplementedControlPercentByTask = {
  __typename?: 'NotImplementedControlPercentByTask';
  implemented: Scalars['Int'];
  libraryTask: LibraryTask;
  percent: Scalars['Float'];
  total: Scalars['Int'];
};

export type NotImplementedControlPercentByTaskType = {
  __typename?: 'NotImplementedControlPercentByTaskType';
  implemented: Scalars['Int'];
  libraryTask: LibraryTask;
  percent: Scalars['Float'];
  total: Scalars['Int'];
};

export enum NotificationsType {
  Email = 'EMAIL',
  Push = 'PUSH',
  Sms = 'SMS'
}

export type ObservationDetailsConceptInput = {
  departmentObserved: DepartmentObservedConceptInput;
  observationDate: Scalars['Date'];
  observationTime: Scalars['Time'];
  opcoObserved?: InputMaybe<OpCoObservedConceptInput>;
  subopcoObserved?: InputMaybe<OpCoObservedConceptInput>;
  workLocation?: InputMaybe<Scalars['String']>;
  workOrderNumber?: InputMaybe<Scalars['String']>;
  workType?: InputMaybe<Array<WorkTypeConceptInput>>;
};

export type ObservationDetailsConceptType = {
  __typename?: 'ObservationDetailsConceptType';
  departmentObserved: DepartmentObservedConceptType;
  observationDate: Scalars['Date'];
  observationTime: Scalars['Time'];
  opcoObserved?: Maybe<OpCoObservedConceptType>;
  subopcoObserved?: Maybe<OpCoObservedConceptType>;
  workLocation?: Maybe<Scalars['String']>;
  workOrderNumber?: Maybe<Scalars['String']>;
  workType?: Maybe<Array<WorkTypeConceptType>>;
};

export type OpCoObservedConceptInput = {
  fullName?: InputMaybe<Scalars['String']>;
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type OpCoObservedConceptType = {
  __typename?: 'OpCoObservedConceptType';
  fullName?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type Opco = {
  __typename?: 'Opco';
  createdAt: Scalars['DateTime'];
  departments: Array<Department>;
  fullName?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  name: Scalars['String'];
  parentOpco?: Maybe<Opco>;
};

export type OperatingProcedureInput = {
  id: Scalars['UUID'];
  link?: InputMaybe<Scalars['String']>;
  name?: InputMaybe<Scalars['String']>;
};

export type OperatingProcedureType = {
  __typename?: 'OperatingProcedureType';
  id: Scalars['UUID'];
  link?: Maybe<Scalars['String']>;
  name?: Maybe<Scalars['String']>;
};

export type OptionItem = {
  __typename?: 'OptionItem';
  id: Scalars['String'];
  name: Scalars['String'];
};

export type OrderBy = {
  direction: OrderByDirection;
  field: OrderByField;
};

export enum OrderByDirection {
  Asc = 'ASC',
  Desc = 'DESC'
}

export enum OrderByField {
  Id = 'ID',
  Name = 'NAME'
}

export enum Permission {
  AddActivities = 'ADD_ACTIVITIES',
  AddControls = 'ADD_CONTROLS',
  AddHazards = 'ADD_HAZARDS',
  AddOpcoAndDepartment = 'ADD_OPCO_AND_DEPARTMENT',
  AddPreferences = 'ADD_PREFERENCES',
  AddProjects = 'ADD_PROJECTS',
  AddReports = 'ADD_REPORTS',
  AddSiteConditions = 'ADD_SITE_CONDITIONS',
  AddTenants = 'ADD_TENANTS',
  AllowEditsAfterEditPeriod = 'ALLOW_EDITS_AFTER_EDIT_PERIOD',
  AssignControls = 'ASSIGN_CONTROLS',
  AssignUsersToProjects = 'ASSIGN_USERS_TO_PROJECTS',
  ConfigureApplication = 'CONFIGURE_APPLICATION',
  ConfigureCustomTemplates = 'CONFIGURE_CUSTOM_TEMPLATES',
  CreateCwf = 'CREATE_CWF',
  DeleteOwnReports = 'DELETE_OWN_REPORTS',
  DeleteProjects = 'DELETE_PROJECTS',
  DeleteReports = 'DELETE_REPORTS',
  EditActivities = 'EDIT_ACTIVITIES',
  EditControls = 'EDIT_CONTROLS',
  EditDeleteAllCwf = 'EDIT_DELETE_ALL_CWF',
  EditDeleteOwnCwf = 'EDIT_DELETE_OWN_CWF',
  EditHazards = 'EDIT_HAZARDS',
  EditOwnReports = 'EDIT_OWN_REPORTS',
  EditProjects = 'EDIT_PROJECTS',
  EditReports = 'EDIT_REPORTS',
  EditSiteConditions = 'EDIT_SITE_CONDITIONS',
  EditSupervisorSignOff = 'EDIT_SUPERVISOR_SIGN_OFF',
  EditTasks = 'EDIT_TASKS',
  EditTenants = 'EDIT_TENANTS',
  GetFeatureFlagDetails = 'GET_FEATURE_FLAG_DETAILS',
  GetReportsToken = 'GET_REPORTS_TOKEN',
  ReopenAllCwf = 'REOPEN_ALL_CWF',
  ReopenOwnCwf = 'REOPEN_OWN_CWF',
  ReopenOwnReport = 'REOPEN_OWN_REPORT',
  ReopenProject = 'REOPEN_PROJECT',
  ReopenReports = 'REOPEN_REPORTS',
  ViewActivities = 'VIEW_ACTIVITIES',
  ViewAllCwf = 'VIEW_ALL_CWF',
  ViewCompanies = 'VIEW_COMPANIES',
  ViewControls = 'VIEW_CONTROLS',
  ViewCrew = 'VIEW_CREW',
  ViewCrewLeaders = 'VIEW_CREW_LEADERS',
  ViewHazards = 'VIEW_HAZARDS',
  ViewInsightReports = 'VIEW_INSIGHT_REPORTS',
  ViewInspections = 'VIEW_INSPECTIONS',
  ViewManagers = 'VIEW_MANAGERS',
  ViewMedicalFacilities = 'VIEW_MEDICAL_FACILITIES',
  ViewNotifications = 'VIEW_NOTIFICATIONS',
  ViewProject = 'VIEW_PROJECT',
  ViewProjectAudits = 'VIEW_PROJECT_AUDITS',
  ViewSiteConditions = 'VIEW_SITE_CONDITIONS',
  ViewSupervisorSignOff = 'VIEW_SUPERVISOR_SIGN_OFF',
  ViewTasks = 'VIEW_TASKS'
}

export type PersonnelConceptInput = {
  id?: InputMaybe<Scalars['UUID']>;
  name: Scalars['String'];
  role?: InputMaybe<Scalars['String']>;
};

export type PersonnelConceptType = {
  __typename?: 'PersonnelConceptType';
  id?: Maybe<Scalars['UUID']>;
  name: Scalars['String'];
  role?: Maybe<Scalars['String']>;
};

export type PointsOfProtectionInput = {
  details: Scalars['String'];
  id: Scalars['Int'];
  name: Scalars['String'];
};

export type PointsOfProtectionType = {
  __typename?: 'PointsOfProtectionType';
  details: Scalars['String'];
  id: Scalars['Int'];
  name: Scalars['String'];
};

export type PortfolioLearnings = {
  __typename?: 'PortfolioLearnings';
  applicableHazards: Array<ApplicableHazardCount>;
  applicableHazardsByProject: Array<ApplicableHazardCountByProject>;
  applicableHazardsBySiteCondition: Array<ApplicableHazardCountBySiteCondition>;
  applicableHazardsByTask: Array<ApplicableHazardCountByTask>;
  applicableHazardsByTaskType: Array<ApplicableHazardCountByTaskType>;
  notImplementedControls: Array<NotImplementedControlPercent>;
  notImplementedControlsByHazard: Array<NotImplementedControlPercentByHazard>;
  notImplementedControlsByProject: Array<NotImplementedControlPercentByProject>;
  notImplementedControlsByTask: Array<NotImplementedControlPercentByTask>;
  notImplementedControlsByTaskType: Array<NotImplementedControlPercentByTaskType>;
  projectRiskLevelOverTime: Array<ProjectRiskLevelCount>;
  reasonsControlsNotImplemented: Array<ReasonControlNotImplemented>;
};


export type PortfolioLearningsApplicableHazardsByProjectArgs = {
  libraryHazardId: Scalars['UUID'];
};


export type PortfolioLearningsApplicableHazardsBySiteConditionArgs = {
  libraryHazardId: Scalars['UUID'];
};


export type PortfolioLearningsApplicableHazardsByTaskArgs = {
  libraryHazardId: Scalars['UUID'];
};


export type PortfolioLearningsApplicableHazardsByTaskTypeArgs = {
  libraryHazardId: Scalars['UUID'];
};


export type PortfolioLearningsNotImplementedControlsByHazardArgs = {
  libraryControlId: Scalars['UUID'];
};


export type PortfolioLearningsNotImplementedControlsByProjectArgs = {
  libraryControlId: Scalars['UUID'];
};


export type PortfolioLearningsNotImplementedControlsByTaskArgs = {
  libraryControlId: Scalars['UUID'];
};


export type PortfolioLearningsNotImplementedControlsByTaskTypeArgs = {
  libraryControlId: Scalars['UUID'];
};

export type PortfolioLearningsInput = {
  contractorIds?: InputMaybe<Array<Scalars['UUID']>>;
  divisionIds?: InputMaybe<Array<Scalars['UUID']>>;
  endDate: Scalars['Date'];
  projectIds?: InputMaybe<Array<Scalars['UUID']>>;
  projectStatuses?: InputMaybe<Array<ProjectStatus>>;
  regionIds?: InputMaybe<Array<Scalars['UUID']>>;
  startDate: Scalars['Date'];
};

export type PortfolioPlanning = {
  __typename?: 'PortfolioPlanning';
  projectRiskLevelByDate: Array<ProjectRiskLevelByDate>;
  projectRiskLevelOverTime: Array<ProjectRiskLevelCount>;
  taskRiskLevelByDate: Array<TaskRiskLevelByDate>;
};


export type PortfolioPlanningTaskRiskLevelByDateArgs = {
  orderBy?: InputMaybe<Array<TaskOrderBy>>;
};

export type PortfolioPlanningInput = {
  contractorIds?: InputMaybe<Array<Scalars['UUID']>>;
  divisionIds?: InputMaybe<Array<Scalars['UUID']>>;
  endDate: Scalars['Date'];
  projectIds?: InputMaybe<Array<Scalars['UUID']>>;
  projectStatuses?: InputMaybe<Array<ProjectStatus>>;
  regionIds?: InputMaybe<Array<Scalars['UUID']>>;
  startDate: Scalars['Date'];
};

export type PostJobBriefDiscussionInput = {
  changesInProcedureWork: Scalars['Boolean'];
  changesInProcedureWorkDescription?: InputMaybe<Scalars['String']>;
  crewMemebersAdequateTrainingProvided: Scalars['Boolean'];
  crewMemebersAdequateTrainingProvidedDescription?: InputMaybe<Scalars['String']>;
  jobBriefAdequateCommunication: Scalars['Boolean'];
  jobBriefAdequateCommunicationDescription?: InputMaybe<Scalars['String']>;
  jobWentAsPlanned: Scalars['Boolean'];
  jobWentAsPlannedDescription?: InputMaybe<Scalars['String']>;
  nearMissOccuredDescription?: InputMaybe<Scalars['String']>;
  nearMissOccuredDuringActivities: Scalars['Boolean'];
  otherLessonLearnt: Scalars['Boolean'];
  otherLessonLearntDescription?: InputMaybe<Scalars['String']>;
  safetyConcernsIdentifiedDuringWork: Scalars['Boolean'];
  safetyConcernsIdentifiedDuringWorkDescription?: InputMaybe<Scalars['String']>;
};

export type PostJobBriefDiscussionType = {
  __typename?: 'PostJobBriefDiscussionType';
  changesInProcedureWork: Scalars['Boolean'];
  changesInProcedureWorkDescription?: Maybe<Scalars['String']>;
  crewMemebersAdequateTrainingProvided: Scalars['Boolean'];
  crewMemebersAdequateTrainingProvidedDescription?: Maybe<Scalars['String']>;
  jobBriefAdequateCommunication: Scalars['Boolean'];
  jobBriefAdequateCommunicationDescription?: Maybe<Scalars['String']>;
  jobWentAsPlanned: Scalars['Boolean'];
  jobWentAsPlannedDescription?: Maybe<Scalars['String']>;
  nearMissOccuredDescription?: Maybe<Scalars['String']>;
  nearMissOccuredDuringActivities: Scalars['Boolean'];
  otherLessonLearnt: Scalars['Boolean'];
  otherLessonLearntDescription?: Maybe<Scalars['String']>;
  safetyConcernsIdentifiedDuringWork: Scalars['Boolean'];
  safetyConcernsIdentifiedDuringWorkDescription?: Maybe<Scalars['String']>;
};

export type PostJobBriefInput = {
  discussionItems: PostJobBriefDiscussionInput;
  postJobDiscussionNotes?: InputMaybe<Scalars['String']>;
  supervisorApprovalSignOff?: InputMaybe<UserInfoInput>;
};

export type PostJobBriefType = {
  __typename?: 'PostJobBriefType';
  discussionItems: PostJobBriefDiscussionType;
  postJobDiscussionNotes?: Maybe<Scalars['String']>;
  supervisorApprovalSignOff?: Maybe<UserInfoType>;
};

export type Project = Auditable & {
  __typename?: 'Project';
  additionalSupervisors: Array<Supervisor>;
  audits: Array<AuditEvent>;
  contractName?: Maybe<Scalars['String']>;
  contractReference?: Maybe<Scalars['String']>;
  contractor?: Maybe<Contractor>;
  description?: Maybe<Scalars['String']>;
  endDate: Scalars['Date'];
  engineerName?: Maybe<Scalars['String']>;
  externalKey?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  libraryAssetType?: Maybe<LibraryAsset>;
  libraryDivision?: Maybe<LibraryDivision>;
  libraryProjectType?: Maybe<LibraryProjectType>;
  libraryRegion?: Maybe<LibraryRegion>;
  locations: Array<ProjectLocation>;
  manager?: Maybe<Manager>;
  maximumTaskDate?: Maybe<Scalars['Date']>;
  minimumTaskDate?: Maybe<Scalars['Date']>;
  name: Scalars['String'];
  number: Scalars['String'];
  projectZipCode?: Maybe<Scalars['String']>;
  riskLevel: RiskLevel;
  startDate: Scalars['Date'];
  status: ProjectStatus;
  supervisor?: Maybe<Supervisor>;
  workTypes: Array<WorkType>;
};


export type ProjectLocationsArgs = {
  id?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
  search?: InputMaybe<Scalars['String']>;
};


export type ProjectRiskLevelArgs = {
  date?: InputMaybe<Scalars['Date']>;
};

export type ProjectLearnings = {
  __typename?: 'ProjectLearnings';
  applicableHazards: Array<ApplicableHazardCount>;
  applicableHazardsByLocation: Array<ApplicableHazardCountByLocation>;
  applicableHazardsBySiteCondition: Array<ApplicableHazardCountBySiteCondition>;
  applicableHazardsByTask: Array<ApplicableHazardCountByTask>;
  applicableHazardsByTaskType: Array<ApplicableHazardCountByTaskType>;
  locationRiskLevelOverTime: Array<LocationRiskLevelCount>;
  notImplementedControls: Array<NotImplementedControlPercent>;
  notImplementedControlsByHazard: Array<NotImplementedControlPercentByHazard>;
  notImplementedControlsByLocation: Array<NotImplementedControlPercentByLocation>;
  notImplementedControlsByTask: Array<NotImplementedControlPercentByTask>;
  notImplementedControlsByTaskType: Array<NotImplementedControlPercentByTaskType>;
  reasonsControlsNotImplemented: Array<ReasonControlNotImplemented>;
};


export type ProjectLearningsApplicableHazardsByLocationArgs = {
  libraryHazardId: Scalars['UUID'];
};


export type ProjectLearningsApplicableHazardsBySiteConditionArgs = {
  libraryHazardId: Scalars['UUID'];
};


export type ProjectLearningsApplicableHazardsByTaskArgs = {
  libraryHazardId: Scalars['UUID'];
};


export type ProjectLearningsApplicableHazardsByTaskTypeArgs = {
  libraryHazardId: Scalars['UUID'];
};


export type ProjectLearningsNotImplementedControlsByHazardArgs = {
  libraryControlId: Scalars['UUID'];
};


export type ProjectLearningsNotImplementedControlsByLocationArgs = {
  libraryControlId: Scalars['UUID'];
};


export type ProjectLearningsNotImplementedControlsByTaskArgs = {
  libraryControlId: Scalars['UUID'];
};


export type ProjectLearningsNotImplementedControlsByTaskTypeArgs = {
  libraryControlId: Scalars['UUID'];
};

export type ProjectLearningsInput = {
  endDate: Scalars['Date'];
  locationIds?: InputMaybe<Array<Scalars['UUID']>>;
  projectId: Scalars['UUID'];
  startDate: Scalars['Date'];
};

export type ProjectLocation = {
  __typename?: 'ProjectLocation';
  activities: Array<Activity>;
  additionalSupervisors: Array<Supervisor>;
  address?: Maybe<Scalars['String']>;
  dailyReports: Array<DailyReport>;
  dailySnapshots: Array<CriticalActivityType>;
  endDate?: Maybe<Scalars['Date']>;
  externalKey?: Maybe<Scalars['String']>;
  hazardControlSettings: Array<LocationHazardControlSettings>;
  id: Scalars['UUID'];
  jobSafetyBriefings: Array<JobSafetyBriefing>;
  latitude: Scalars['Decimal'];
  longitude: Scalars['Decimal'];
  name: Scalars['String'];
  project?: Maybe<Project>;
  risk: RiskLevel;
  riskCalculation?: Maybe<RiskCalculationDetails>;
  riskLevel: RiskLevel;
  siteConditions: Array<SiteCondition>;
  startDate?: Maybe<Scalars['Date']>;
  supervisor?: Maybe<Supervisor>;
  tasks: Array<Task>;
};


export type ProjectLocationActivitiesArgs = {
  date?: InputMaybe<Scalars['Date']>;
  endDate?: InputMaybe<Scalars['Date']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
  startDate?: InputMaybe<Scalars['Date']>;
};


export type ProjectLocationDailyReportsArgs = {
  date?: InputMaybe<Scalars['Date']>;
};


export type ProjectLocationDailySnapshotsArgs = {
  dateRange: DateRangeInput;
};


export type ProjectLocationJobSafetyBriefingsArgs = {
  date?: InputMaybe<Scalars['Date']>;
};


export type ProjectLocationRiskCalculationArgs = {
  date?: InputMaybe<Scalars['Date']>;
};


export type ProjectLocationRiskLevelArgs = {
  date?: InputMaybe<Scalars['Date']>;
};


export type ProjectLocationSiteConditionsArgs = {
  date?: InputMaybe<Scalars['Date']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type ProjectLocationTasksArgs = {
  date?: InputMaybe<Scalars['Date']>;
  orderBy?: InputMaybe<Array<TaskOrderBy>>;
};

export type ProjectLocationInput = {
  additionalSupervisors?: InputMaybe<Array<Scalars['UUID']>>;
  externalKey?: InputMaybe<Scalars['String']>;
  latitude: Scalars['Decimal'];
  longitude: Scalars['Decimal'];
  name: Scalars['String'];
  supervisorId?: InputMaybe<Scalars['UUID']>;
};

export type ProjectLocationOrderBy = {
  direction: OrderByDirection;
  field: ProjectLocationOrderByField;
};

export enum ProjectLocationOrderByField {
  Id = 'ID',
  Name = 'NAME',
  RiskLevel = 'RISK_LEVEL'
}

export type ProjectLocationResponse = {
  __typename?: 'ProjectLocationResponse';
  filterLocationsDateRange: Array<FilterLocationDateRange>;
  locationsCount: Scalars['Int'];
};

export type ProjectOrderBy = {
  direction: OrderByDirection;
  field: ProjectOrderByField;
};

export enum ProjectOrderByField {
  Id = 'ID',
  Name = 'NAME',
  RiskLevel = 'RISK_LEVEL'
}

export type ProjectPlanning = {
  __typename?: 'ProjectPlanning';
  locationRiskLevelByDate: Array<LocationRiskLevelByDate>;
  locationRiskLevelOverTime: Array<LocationRiskLevelCount>;
  taskRiskLevelByDate: Array<TaskRiskLevelByDate>;
};


export type ProjectPlanningTaskRiskLevelByDateArgs = {
  orderBy?: InputMaybe<Array<TaskOrderBy>>;
};

export type ProjectPlanningInput = {
  endDate: Scalars['Date'];
  locationIds?: InputMaybe<Array<Scalars['UUID']>>;
  projectId: Scalars['UUID'];
  startDate: Scalars['Date'];
};

export type ProjectRiskLevelByDate = {
  __typename?: 'ProjectRiskLevelByDate';
  project?: Maybe<Project>;
  projectName: Scalars['String'];
  riskLevelByDate: Array<RiskLevelByDate>;
};

export type ProjectRiskLevelCount = {
  __typename?: 'ProjectRiskLevelCount';
  count: Scalars['Int'];
  date: Scalars['Date'];
  riskLevel: RiskLevel;
};

export enum ProjectStatus {
  Active = 'ACTIVE',
  Completed = 'COMPLETED',
  Pending = 'PENDING'
}

export type Query = {
  __typename?: 'Query';
  activities: Array<Activity>;
  activityGroupsLibrary: Array<LibraryActivityGroup>;
  activityTypesLibrary: Array<LibraryActivityType>;
  assetTypesLibrary: Array<LibraryAsset>;
  contractors: Array<Contractor>;
  controlsLibrary: Array<LibraryControl>;
  crewLeaders: Array<CrewLeader>;
  dailyReport?: Maybe<DailyReport>;
  dailyReportResponse: DailyReportFormsList;
  dailyReports: Array<DailyReport>;
  divisionsLibrary: Array<LibraryDivision>;
  energyBasedObservation: EnergyBasedObservation;
  energyBasedObservationResponse: EnergyBasedObservationFormsList;
  filterLocationDateRange: Array<ProjectLocationResponse>;
  firstAidAedLocation: Array<FirstAidaedLocation>;
  formDefinitions: Array<FormDefinition>;
  formsList: Array<FormInterface>;
  formsListCount: Scalars['Int'];
  formsListFilterOptions: FormListFilterOptions;
  formsListWithContents: Array<FormInterfaceWithContents>;
  hazardsLibrary: Array<LibraryHazard>;
  historicalIncidents: Array<Incident>;
  ingestOptionItems: IngestOptionItems;
  ingestOptions: IngestOptions;
  insights: Array<Insight>;
  jobSafetyBriefing: JobSafetyBriefing;
  jobSafetyBriefingResponse: JobSafetyBriefingFormsList;
  jsbSupervisors: Array<JsbSupervisor>;
  lastAddedAdhocJobSafetyBriefing?: Maybe<JobSafetyBriefing>;
  lastAddedJobSafetyBriefing?: Maybe<JobSafetyBriefing>;
  lastNatgridJobSafetyBriefing: NatGridJobSafetyBriefing;
  locationHazardControlSettings: Array<LocationHazardControlSettings>;
  locationSiteConditions: Array<SiteCondition>;
  managers: Array<Manager>;
  me: Me;
  natgridJobSafetyBriefing: NatGridJobSafetyBriefing;
  natgridJobSafetyBriefingResponse: NatGridJobSafetyBriefingFormsList;
  nearestMedicalFacilities: Array<MedicalFacility>;
  portfolioLearnings: PortfolioLearnings;
  portfolioPlanning: PortfolioPlanning;
  project: Project;
  projectLearnings: ProjectLearnings;
  projectLocations: Array<ProjectLocation>;
  projectPlanning: ProjectPlanning;
  projectTypesLibrary: Array<LibraryProjectType>;
  projects: Array<Project>;
  recentlyUsedCrewLeaders: Array<RecentUsedCrewLeaderReturnType>;
  recommendations: Recommendation;
  regionsLibrary: Array<LibraryRegion>;
  restApiWrapper: RestApiWrapper;
  siteConditions: Array<SiteCondition>;
  siteConditionsLibrary: Array<LibrarySiteCondition>;
  supervisors: Array<Supervisor>;
  system: System;
  tasks: Array<Task>;
  tasksLibrary: Array<LibraryTask>;
  tenantAndWorkTypeLinkedLibrarySiteConditions: Array<LinkedLibrarySiteCondition>;
  tenantAndWorkTypeLinkedLibraryTasks: Array<LinkedLibraryTask>;
  tenantLinkedControlsLibrary: Array<LinkedLibraryControl>;
  tenantLinkedHazardsLibrary: Array<LinkedLibraryHazard>;
  tenantWorkTypes: Array<WorkType>;
  uiConfig: UiConfigs;
  workosDirectoryUsers: WorkOsDirectoryUsersResponseType;
};


export type QueryActivitiesArgs = {
  date?: InputMaybe<Scalars['Date']>;
  filterTenantSettings?: InputMaybe<Scalars['Boolean']>;
  id?: InputMaybe<Scalars['UUID']>;
  locationId?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryActivityGroupsLibraryArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryActivityTypesLibraryArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryAssetTypesLibraryArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryContractorsArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryControlsLibraryArgs = {
  allowArchived?: Scalars['Boolean'];
  id?: InputMaybe<Scalars['UUID']>;
  libraryHazardId?: InputMaybe<Scalars['UUID']>;
  librarySiteConditionId?: InputMaybe<Scalars['UUID']>;
  libraryTaskId?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
  type: LibraryFilterType;
};


export type QueryCrewLeadersArgs = {
  limit?: InputMaybe<Scalars['Int']>;
  offset?: InputMaybe<Scalars['Int']>;
};


export type QueryDailyReportArgs = {
  id: Scalars['UUID'];
  status?: InputMaybe<FormStatus>;
};


export type QueryDailyReportResponseArgs = {
  id: Scalars['UUID'];
  status?: InputMaybe<FormStatus>;
};


export type QueryDailyReportsArgs = {
  date: Scalars['Date'];
  projectLocationId: Scalars['UUID'];
};


export type QueryDivisionsLibraryArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryEnergyBasedObservationArgs = {
  id: Scalars['UUID'];
};


export type QueryEnergyBasedObservationResponseArgs = {
  id: Scalars['UUID'];
};


export type QueryFilterLocationDateRangeArgs = {
  contractorIds?: InputMaybe<Array<Scalars['UUID']>>;
  filterBy?: InputMaybe<Array<LocationFilterBy>>;
  filterTenantSettings?: InputMaybe<Scalars['Boolean']>;
  id?: InputMaybe<Scalars['UUID']>;
  libraryDivisionIds?: InputMaybe<Array<Scalars['UUID']>>;
  libraryProjectTypeIds?: InputMaybe<Array<Scalars['UUID']>>;
  libraryRegionIds?: InputMaybe<Array<Scalars['UUID']>>;
  limit?: InputMaybe<Scalars['Int']>;
  mapExtent?: InputMaybe<MapExtentInput>;
  offset?: InputMaybe<Scalars['Int']>;
  orderBy?: InputMaybe<Array<ProjectLocationOrderBy>>;
  projectIds?: InputMaybe<Array<Scalars['UUID']>>;
  projectStatus?: InputMaybe<Array<ProjectStatus>>;
  search?: InputMaybe<Scalars['String']>;
  supervisorIds?: InputMaybe<Array<Scalars['UUID']>>;
  workTypeIds?: InputMaybe<Array<Scalars['UUID']>>;
};


export type QueryFirstAidAedLocationArgs = {
  locationType?: InputMaybe<LocationType>;
  orderBy?: InputMaybe<Array<LocationOrderBy>>;
};


export type QueryFormsListArgs = {
  adHoc?: Scalars['Boolean'];
  createdByIds?: InputMaybe<Array<Scalars['UUID']>>;
  endCompletedAt?: InputMaybe<Scalars['Date']>;
  endCreatedAt?: InputMaybe<Scalars['Date']>;
  endDate?: InputMaybe<Scalars['Date']>;
  endReportDate?: InputMaybe<Scalars['Date']>;
  endUpdatedAt?: InputMaybe<Scalars['Date']>;
  formId?: InputMaybe<Array<Scalars['String']>>;
  formName?: InputMaybe<Array<Scalars['String']>>;
  formStatus?: InputMaybe<Array<FormStatus>>;
  limit?: InputMaybe<Scalars['Int']>;
  locationIds?: InputMaybe<Array<Scalars['UUID']>>;
  managerIds?: InputMaybe<Array<Scalars['String']>>;
  offset?: InputMaybe<Scalars['Int']>;
  operatingRegionNames?: InputMaybe<Array<Scalars['String']>>;
  orderBy?: InputMaybe<Array<FormListOrderBy>>;
  projectIds?: InputMaybe<Array<Scalars['UUID']>>;
  search?: InputMaybe<Scalars['String']>;
  startCompletedAt?: InputMaybe<Scalars['Date']>;
  startCreatedAt?: InputMaybe<Scalars['Date']>;
  startDate?: InputMaybe<Scalars['Date']>;
  startReportDate?: InputMaybe<Scalars['Date']>;
  startUpdatedAt?: InputMaybe<Scalars['Date']>;
  updatedByIds?: InputMaybe<Array<Scalars['UUID']>>;
};


export type QueryFormsListCountArgs = {
  adHoc?: Scalars['Boolean'];
  createdByIds?: InputMaybe<Array<Scalars['UUID']>>;
  endCompletedAt?: InputMaybe<Scalars['Date']>;
  endCreatedAt?: InputMaybe<Scalars['Date']>;
  endDate?: InputMaybe<Scalars['Date']>;
  endReportDate?: InputMaybe<Scalars['Date']>;
  endUpdatedAt?: InputMaybe<Scalars['Date']>;
  formId?: InputMaybe<Array<Scalars['String']>>;
  formName?: InputMaybe<Array<Scalars['String']>>;
  formStatus?: InputMaybe<Array<FormStatus>>;
  locationIds?: InputMaybe<Array<Scalars['UUID']>>;
  managerIds?: InputMaybe<Array<Scalars['String']>>;
  operatingRegionNames?: InputMaybe<Array<Scalars['String']>>;
  projectIds?: InputMaybe<Array<Scalars['UUID']>>;
  search?: InputMaybe<Scalars['String']>;
  startCompletedAt?: InputMaybe<Scalars['Date']>;
  startCreatedAt?: InputMaybe<Scalars['Date']>;
  startDate?: InputMaybe<Scalars['Date']>;
  startReportDate?: InputMaybe<Scalars['Date']>;
  startUpdatedAt?: InputMaybe<Scalars['Date']>;
  updatedByIds?: InputMaybe<Array<Scalars['UUID']>>;
};


export type QueryFormsListFilterOptionsArgs = {
  filterSearch?: InputMaybe<FormListFilterSearchInput>;
  limit?: InputMaybe<Scalars['Int']>;
  offset?: InputMaybe<Scalars['Int']>;
};


export type QueryFormsListWithContentsArgs = {
  adHoc?: Scalars['Boolean'];
  createdByIds?: InputMaybe<Array<Scalars['UUID']>>;
  endCompletedAt?: InputMaybe<Scalars['Date']>;
  endCreatedAt?: InputMaybe<Scalars['Date']>;
  endDate?: InputMaybe<Scalars['Date']>;
  endReportDate?: InputMaybe<Scalars['Date']>;
  endUpdatedAt?: InputMaybe<Scalars['Date']>;
  formId?: InputMaybe<Array<Scalars['String']>>;
  formName?: InputMaybe<Array<Scalars['String']>>;
  formStatus?: InputMaybe<Array<FormStatus>>;
  limit?: InputMaybe<Scalars['Int']>;
  locationIds?: InputMaybe<Array<Scalars['UUID']>>;
  managerIds?: InputMaybe<Array<Scalars['String']>>;
  offset?: InputMaybe<Scalars['Int']>;
  operatingRegionNames?: InputMaybe<Array<Scalars['String']>>;
  orderBy?: InputMaybe<Array<FormListOrderBy>>;
  projectIds?: InputMaybe<Array<Scalars['UUID']>>;
  search?: InputMaybe<Scalars['String']>;
  startCompletedAt?: InputMaybe<Scalars['Date']>;
  startCreatedAt?: InputMaybe<Scalars['Date']>;
  startDate?: InputMaybe<Scalars['Date']>;
  startReportDate?: InputMaybe<Scalars['Date']>;
  startUpdatedAt?: InputMaybe<Scalars['Date']>;
  updatedByIds?: InputMaybe<Array<Scalars['UUID']>>;
};


export type QueryHazardsLibraryArgs = {
  allowArchived?: Scalars['Boolean'];
  id?: InputMaybe<Scalars['UUID']>;
  librarySiteConditionId?: InputMaybe<Scalars['UUID']>;
  libraryTaskId?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
  type: LibraryFilterType;
};


export type QueryHistoricalIncidentsArgs = {
  allowArchived?: Scalars['Boolean'];
  libraryTaskId: Scalars['UUID'];
};


export type QueryIngestOptionItemsArgs = {
  key: IngestType;
};


export type QueryInsightsArgs = {
  after?: InputMaybe<Scalars['UUID']>;
  limit?: InputMaybe<Scalars['Int']>;
};


export type QueryJobSafetyBriefingArgs = {
  id: Scalars['UUID'];
};


export type QueryJobSafetyBriefingResponseArgs = {
  id: Scalars['UUID'];
};


export type QueryJsbSupervisorsArgs = {
  limit?: InputMaybe<Scalars['Int']>;
  offset?: InputMaybe<Scalars['Int']>;
};


export type QueryLastAddedJobSafetyBriefingArgs = {
  filterOn?: JsbFiltersOnEnum;
  projectLocationId?: InputMaybe<Scalars['UUID']>;
};


export type QueryLastNatgridJobSafetyBriefingArgs = {
  allowArchived?: InputMaybe<Scalars['Boolean']>;
};


export type QueryLocationHazardControlSettingsArgs = {
  locationId: Scalars['UUID'];
};


export type QueryLocationSiteConditionsArgs = {
  filterTenantSettings?: InputMaybe<Scalars['Boolean']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
  siteInput: SiteLocationInput;
};


export type QueryManagersArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryNatgridJobSafetyBriefingArgs = {
  id: Scalars['UUID'];
};


export type QueryNatgridJobSafetyBriefingResponseArgs = {
  id: Scalars['UUID'];
};


export type QueryNearestMedicalFacilitiesArgs = {
  latitude: Scalars['Decimal'];
  longitude: Scalars['Decimal'];
};


export type QueryPortfolioLearningsArgs = {
  portfolioLearningsInput: PortfolioLearningsInput;
};


export type QueryPortfolioPlanningArgs = {
  portfolioPlanningInput: PortfolioPlanningInput;
};


export type QueryProjectArgs = {
  filterTenantSettings?: InputMaybe<Scalars['Boolean']>;
  projectId: Scalars['UUID'];
};


export type QueryProjectLearningsArgs = {
  projectLearningsInput: ProjectLearningsInput;
};


export type QueryProjectLocationsArgs = {
  contractorIds?: InputMaybe<Array<Scalars['UUID']>>;
  filterBy?: InputMaybe<Array<LocationFilterBy>>;
  filterTenantSettings?: InputMaybe<Scalars['Boolean']>;
  id?: InputMaybe<Scalars['UUID']>;
  libraryDivisionIds?: InputMaybe<Array<Scalars['UUID']>>;
  libraryProjectTypeIds?: InputMaybe<Array<Scalars['UUID']>>;
  libraryRegionIds?: InputMaybe<Array<Scalars['UUID']>>;
  limit?: InputMaybe<Scalars['Int']>;
  offset?: InputMaybe<Scalars['Int']>;
  orderBy?: InputMaybe<Array<ProjectLocationOrderBy>>;
  projectIds?: InputMaybe<Array<Scalars['UUID']>>;
  projectStatus?: InputMaybe<Array<ProjectStatus>>;
  search?: InputMaybe<Scalars['String']>;
  supervisorIds?: InputMaybe<Array<Scalars['UUID']>>;
  workTypeIds?: InputMaybe<Array<Scalars['UUID']>>;
};


export type QueryProjectPlanningArgs = {
  projectPlanningInput: ProjectPlanningInput;
};


export type QueryProjectTypesLibraryArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryProjectsArgs = {
  id?: InputMaybe<Scalars['UUID']>;
  limit?: InputMaybe<Scalars['Int']>;
  offset?: InputMaybe<Scalars['Int']>;
  orderBy?: InputMaybe<Array<ProjectOrderBy>>;
  search?: InputMaybe<Scalars['String']>;
  status?: InputMaybe<ProjectStatus>;
};


export type QueryRecentlyUsedCrewLeadersArgs = {
  allowArchived?: InputMaybe<Scalars['Boolean']>;
  limit?: InputMaybe<Scalars['Int']>;
};


export type QueryRegionsLibraryArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryRestApiWrapperArgs = {
  endpoint: Scalars['String'];
  method: Scalars['String'];
  payload?: InputMaybe<Scalars['String']>;
};


export type QuerySiteConditionsArgs = {
  date?: InputMaybe<Scalars['Date']>;
  filterTenantSettings?: InputMaybe<Scalars['Boolean']>;
  id?: InputMaybe<Scalars['UUID']>;
  locationId?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QuerySiteConditionsLibraryArgs = {
  allowArchived?: Scalars['Boolean'];
  id?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QuerySupervisorsArgs = {
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type QueryTasksArgs = {
  date?: InputMaybe<Scalars['Date']>;
  filterTenantSettings?: InputMaybe<Scalars['Boolean']>;
  id?: InputMaybe<Scalars['UUID']>;
  locationId?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<TaskOrderBy>>;
  search?: InputMaybe<Scalars['String']>;
};


export type QueryTasksLibraryArgs = {
  allowArchived?: Scalars['Boolean'];
  ids?: InputMaybe<Array<Scalars['UUID']>>;
  orderBy?: InputMaybe<Array<LibraryTaskOrderBy>>;
};


export type QueryTenantAndWorkTypeLinkedLibrarySiteConditionsArgs = {
  id?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
  tenantWorkTypeIds: Array<Scalars['UUID']>;
};


export type QueryTenantAndWorkTypeLinkedLibraryTasksArgs = {
  ids?: InputMaybe<Array<Scalars['UUID']>>;
  orderBy?: InputMaybe<Array<LibraryTaskOrderBy>>;
  tenantWorkTypeIds: Array<Scalars['UUID']>;
};


export type QueryTenantLinkedControlsLibraryArgs = {
  allowArchived?: Scalars['Boolean'];
  id?: InputMaybe<Scalars['UUID']>;
  libraryHazardId?: InputMaybe<Scalars['UUID']>;
  librarySiteConditionId?: InputMaybe<Scalars['UUID']>;
  libraryTaskId?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
  type?: InputMaybe<LibraryFilterType>;
};


export type QueryTenantLinkedHazardsLibraryArgs = {
  allowArchived?: Scalars['Boolean'];
  id?: InputMaybe<Scalars['UUID']>;
  librarySiteConditionId?: InputMaybe<Scalars['UUID']>;
  libraryTaskId?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
  type?: InputMaybe<LibraryFilterType>;
};


export type QueryUiConfigArgs = {
  formType: FormType;
};


export type QueryWorkosDirectoryUsersArgs = {
  after?: InputMaybe<Scalars['String']>;
  before?: InputMaybe<Scalars['String']>;
  directoryIds: Array<Scalars['String']>;
  group?: InputMaybe<Scalars['String']>;
  limit?: InputMaybe<Scalars['String']>;
  order?: InputMaybe<Scalars['String']>;
  updateCache?: InputMaybe<Scalars['Boolean']>;
};

export type ReasonControlNotImplemented = {
  __typename?: 'ReasonControlNotImplemented';
  count: Scalars['Int'];
  reason: Scalars['String'];
};

export type RecalculateInput = {
  id: Scalars['UUID'];
  trigger: Triggers;
};

export type RecentUsedCrewLeaderReturnType = {
  __typename?: 'RecentUsedCrewLeaderReturnType';
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type RecieverInput = {
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type Recommendation = {
  __typename?: 'Recommendation';
  dailyReport?: Maybe<DailyReportRecommendation>;
};


export type RecommendationDailyReportArgs = {
  projectLocationId: Scalars['UUID'];
};

export type RecommendedTaskSelection = {
  __typename?: 'RecommendedTaskSelection';
  fromWorkOrder: Scalars['Boolean'];
  id: Scalars['UUID'];
  name?: Maybe<Scalars['String']>;
  recommended?: Maybe<Scalars['Boolean']>;
  riskLevel: RiskLevel;
  selected?: Maybe<Scalars['Boolean']>;
};

export type RecommendedTaskSelectionInput = {
  fromWorkOrder: Scalars['Boolean'];
  id: Scalars['UUID'];
  name?: InputMaybe<Scalars['String']>;
  recommended?: InputMaybe<Scalars['Boolean']>;
  riskLevel: RiskLevel;
  selected?: InputMaybe<Scalars['Boolean']>;
};

export type RemoveActivityTasksInput = {
  taskIdsToBeRemoved?: Array<Scalars['UUID']>;
};

export type RestApiWrapper = {
  __typename?: 'RestApiWrapper';
  endpoint: Scalars['String'];
  method: Scalars['String'];
  payload?: Maybe<Scalars['String']>;
  response?: Maybe<Scalars['JSON']>;
};

export type RiskCalculationDetails = {
  __typename?: 'RiskCalculationDetails';
  isContractorAtRisk: Scalars['Boolean'];
  isCrewAtRisk: Scalars['Boolean'];
  isSupervisorAtRisk: Scalars['Boolean'];
  totalTaskRiskLevel: RiskLevel;
};

export enum RiskLevel {
  High = 'HIGH',
  Low = 'LOW',
  Medium = 'MEDIUM',
  Recalculating = 'RECALCULATING',
  Unknown = 'UNKNOWN'
}

export type RiskLevelByDate = {
  __typename?: 'RiskLevelByDate';
  date: Scalars['Date'];
  riskLevel: RiskLevel;
};

export type SaveDailyReportInput = {
  additionalInformation?: InputMaybe<AdditionalInformationSectionInput>;
  attachments?: InputMaybe<AttachmentSectionInput>;
  crew?: InputMaybe<CrewSectionInput>;
  dailySourceInfo?: InputMaybe<DailySourceInformationConceptsInput>;
  date: Scalars['Date'];
  id?: InputMaybe<Scalars['UUID']>;
  jobHazardAnalysis?: InputMaybe<JobHazardAnalysisSectionInput>;
  projectLocationId: Scalars['UUID'];
  safetyAndCompliance?: InputMaybe<Scalars['DictScalar']>;
  taskSelection?: InputMaybe<TaskSelectionSectionInput>;
  workSchedule?: InputMaybe<WorkScheduleInput>;
};

export type SaveJobSafetyBriefingInput = {
  activities?: InputMaybe<Array<ActivityConceptInput>>;
  additionalPpe?: InputMaybe<Array<Scalars['String']>>;
  aedInformation?: InputMaybe<AedInformationInput>;
  controlAssessmentSelections?: InputMaybe<Array<ControlAssessmentInput>>;
  crewSignOff?: InputMaybe<Array<CrewInformationInput>>;
  criticalRiskAreaSelections?: InputMaybe<Array<CriticalRiskAreaInput>>;
  customNearestMedicalFacility?: InputMaybe<CustomMedicalFacilityInput>;
  distributionBulletinSelections?: InputMaybe<Array<Scalars['String']>>;
  documents?: InputMaybe<Array<FileInput>>;
  emergencyContacts?: InputMaybe<Array<EmergencyContactInput>>;
  energySourceControl?: InputMaybe<EnergySourceControlInput>;
  gpsCoordinates?: InputMaybe<Array<GpsCoordinatesInput>>;
  groupDiscussion?: InputMaybe<GroupDiscussionInput>;
  hazardsAndControlsNotes?: InputMaybe<Scalars['String']>;
  jsbId?: InputMaybe<Scalars['UUID']>;
  jsbMetadata?: InputMaybe<JsbMetadataInput>;
  minimumApproachDistance?: InputMaybe<Scalars['String']>;
  nearestMedicalFacility?: InputMaybe<MedicalFacilityInput>;
  otherWorkProcedures?: InputMaybe<Scalars['String']>;
  photos?: InputMaybe<Array<FileInput>>;
  recommendedTaskSelections?: InputMaybe<Array<RecommendedTaskSelectionInput>>;
  siteConditionSelections?: InputMaybe<Array<SiteConditionSelectionInput>>;
  sourceInfo?: InputMaybe<SourceInformationConceptsInput>;
  taskSelections?: InputMaybe<Array<TaskSelectionConceptInput>>;
  workLocation?: InputMaybe<WorkLocationInput>;
  workPackageMetadata?: InputMaybe<WorkPackageMetadataInput>;
  workProcedureSelections?: InputMaybe<Array<WorkProcedureSelectionInput>>;
};

export type Sections = {
  __typename?: 'Sections';
  additionalInformation?: Maybe<AdditionalInformationSection>;
  attachments?: Maybe<AttachmentSection>;
  completions?: Maybe<Array<Completion>>;
  crew?: Maybe<CrewSection>;
  dailySourceInfo?: Maybe<DailySourceInformationConceptsType>;
  jobHazardAnalysis?: Maybe<JobHazardAnalysisSection>;
  safetyAndCompliance?: Maybe<Scalars['DictScalar']>;
  taskSelection?: Maybe<TaskSelectionSection>;
  workSchedule?: Maybe<WorkSchedule>;
};

export type SignedPostPolicy = {
  __typename?: 'SignedPostPolicy';
  fields: Scalars['String'];
  id: Scalars['String'];
  signedUrl: Scalars['String'];
  url: Scalars['String'];
};

export type SiteCondition = Auditable & {
  __typename?: 'SiteCondition';
  createdBy?: Maybe<User>;
  hazards: Array<SiteConditionHazard>;
  id: Scalars['UUID'];
  isManuallyAdded: Scalars['Boolean'];
  librarySiteCondition: LinkedLibrarySiteCondition;
  location: ProjectLocation;
  name: Scalars['String'];
  /** @deprecated site_condition.risk_level is not used anymore, will be removed soon */
  riskLevel: RiskLevel;
};


export type SiteConditionHazardsArgs = {
  isApplicable?: InputMaybe<Scalars['Boolean']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};

export type SiteConditionAnalysis = {
  __typename?: 'SiteConditionAnalysis';
  hazards: Array<HazardAnalysis>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  name: Scalars['String'];
};

export type SiteConditionAnalysisInput = {
  hazards: Array<HazardAnalysisInput>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  name?: InputMaybe<Scalars['String']>;
};

export type SiteConditionHazard = {
  __typename?: 'SiteConditionHazard';
  controls: Array<SiteConditionHazardControl>;
  createdBy?: Maybe<User>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  libraryHazard: LibraryHazard;
  name: Scalars['String'];
};


export type SiteConditionHazardControlsArgs = {
  isApplicable?: InputMaybe<Scalars['Boolean']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};

export type SiteConditionHazardControl = {
  __typename?: 'SiteConditionHazardControl';
  createdBy?: Maybe<User>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  libraryControl: LibraryControl;
  name: Scalars['String'];
};

export type SiteConditionSelection = {
  __typename?: 'SiteConditionSelection';
  id: Scalars['UUID'];
  name?: Maybe<Scalars['String']>;
  recommended: Scalars['Boolean'];
  selected: Scalars['Boolean'];
};

export type SiteConditionSelectionInput = {
  id: Scalars['UUID'];
  name?: InputMaybe<Scalars['String']>;
  recommended: Scalars['Boolean'];
  selected: Scalars['Boolean'];
};

export type SiteLocationInput = {
  date: Scalars['Date'];
  latitude: Scalars['Decimal'];
  longitude: Scalars['Decimal'];
};

export enum SourceAppInformation {
  Android = 'ANDROID',
  Ios = 'IOS',
  WebPortal = 'WEB_PORTAL'
}

export enum SourceInformation {
  Android = 'ANDROID',
  Ios = 'IOS',
  WebPortal = 'WEB_PORTAL'
}

export type SourceInformationConceptsInput = {
  appVersion?: InputMaybe<Scalars['String']>;
  sourceInformation?: InputMaybe<SourceAppInformation>;
};

export type SourceInformationConceptsType = {
  __typename?: 'SourceInformationConceptsType';
  appVersion?: Maybe<Scalars['String']>;
  sourceInformation?: Maybe<SourceAppInformation>;
};

export type StandardOperatingProcedure = {
  __typename?: 'StandardOperatingProcedure';
  id: Scalars['UUID'];
  link: Scalars['String'];
  name: Scalars['String'];
};

export type Supervisor = {
  __typename?: 'Supervisor';
  firstName?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  lastName?: Maybe<Scalars['String']>;
  name: Scalars['String'];
};

export type SupervisorSignOffInput = {
  dateTime: Scalars['DateTime'];
  supervisor: CrewInformationDataInput;
};

export type SupervisorSignOffType = {
  __typename?: 'SupervisorSignOffType';
  dateTime: Scalars['DateTime'];
  supervisor: CrewInformationDataType;
};

export type System = {
  __typename?: 'System';
  version: Scalars['String'];
};

export type Task = Auditable & {
  __typename?: 'Task';
  activity?: Maybe<Activity>;
  /** @deprecated Will soon be replaced by end_date on Activity */
  endDate?: Maybe<Scalars['Date']>;
  hazards: Array<TaskHazard>;
  id: Scalars['UUID'];
  incidents: Array<Incident>;
  libraryTask: LibraryTask;
  location: ProjectLocation;
  name: Scalars['String'];
  riskLevel: RiskLevel;
  riskLevels: Array<DatedRiskLevel>;
  /** @deprecated Will soon be replaced by start_date on Activity */
  startDate?: Maybe<Scalars['Date']>;
  /** @deprecated Will soon be replaced by status on Activity */
  status: TaskStatus;
};


export type TaskHazardsArgs = {
  isApplicable?: InputMaybe<Scalars['Boolean']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};


export type TaskRiskLevelArgs = {
  date?: InputMaybe<Scalars['Date']>;
};


export type TaskRiskLevelsArgs = {
  filterDateRange: DateRangeInput;
};

export type TaskAnalysis = {
  __typename?: 'TaskAnalysis';
  hazards: Array<HazardAnalysis>;
  id: Scalars['UUID'];
  name: Scalars['String'];
  notApplicableReason?: Maybe<Scalars['String']>;
  notes?: Maybe<Scalars['String']>;
  performed: Scalars['Boolean'];
  sectionIsValid?: Maybe<Scalars['Boolean']>;
};

export type TaskAnalysisInput = {
  hazards: Array<HazardAnalysisInput>;
  id: Scalars['UUID'];
  name?: InputMaybe<Scalars['String']>;
  notApplicableReason?: InputMaybe<Scalars['String']>;
  notes?: InputMaybe<Scalars['String']>;
  performed: Scalars['Boolean'];
  sectionIsValid?: InputMaybe<Scalars['Boolean']>;
};

export type TaskApplicabilityLevel = {
  __typename?: 'TaskApplicabilityLevel';
  applicabilityLevel: ApplicabilityLevel;
  taskId: Scalars['UUID'];
};

export type TaskHazard = {
  __typename?: 'TaskHazard';
  controls: Array<TaskHazardControl>;
  createdBy?: Maybe<User>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  libraryHazard: LibraryHazard;
  name: Scalars['String'];
};


export type TaskHazardControlsArgs = {
  isApplicable?: InputMaybe<Scalars['Boolean']>;
  orderBy?: InputMaybe<Array<OrderBy>>;
};

export type TaskHazardControl = {
  __typename?: 'TaskHazardControl';
  createdBy?: Maybe<User>;
  id: Scalars['UUID'];
  isApplicable: Scalars['Boolean'];
  libraryControl: LibraryControl;
  name: Scalars['String'];
};

export type TaskOrderBy = {
  direction: OrderByDirection;
  field: TaskOrderByField;
};

export enum TaskOrderByField {
  Category = 'CATEGORY',
  EndDate = 'END_DATE',
  Id = 'ID',
  Name = 'NAME',
  ProjectLocationName = 'PROJECT_LOCATION_NAME',
  ProjectName = 'PROJECT_NAME',
  StartDate = 'START_DATE',
  Status = 'STATUS'
}

export type TaskRiskLevelByDate = {
  __typename?: 'TaskRiskLevelByDate';
  locationName: Scalars['String'];
  projectName: Scalars['String'];
  riskLevelByDate: Array<RiskLevelByDate>;
  task?: Maybe<Task>;
  taskName: Scalars['String'];
};

export type TaskSelection = {
  __typename?: 'TaskSelection';
  id: Scalars['UUID'];
  name: Scalars['String'];
  riskLevel: RiskLevel;
};

export type TaskSelectionConcept = {
  __typename?: 'TaskSelectionConcept';
  fromWorkOrder: Scalars['Boolean'];
  id: Scalars['UUID'];
  name?: Maybe<Scalars['String']>;
  riskLevel: RiskLevel;
};

export type TaskSelectionConceptInput = {
  fromWorkOrder: Scalars['Boolean'];
  id: Scalars['UUID'];
  name?: InputMaybe<Scalars['String']>;
  riskLevel: RiskLevel;
};

export type TaskSelectionInput = {
  id: Scalars['UUID'];
  name: Scalars['String'];
  riskLevel: RiskLevel;
};

export type TaskSelectionSection = {
  __typename?: 'TaskSelectionSection';
  sectionIsValid?: Maybe<Scalars['Boolean']>;
  selectedTasks: Array<TaskSelection>;
};

export type TaskSelectionSectionInput = {
  sectionIsValid?: InputMaybe<Scalars['Boolean']>;
  selectedTasks: Array<TaskSelectionInput>;
};

export type TaskSiteConditonEnergyHazardsInput = {
  highEnergyHazards?: InputMaybe<Array<EnergyHazardsInput>>;
  id: Scalars['UUID'];
  lowEnergyHazards?: InputMaybe<Array<EnergyHazardsInput>>;
  name?: InputMaybe<Scalars['String']>;
};

export type TaskSiteConditonEnergyHazardsType = {
  __typename?: 'TaskSiteConditonEnergyHazardsType';
  highEnergyHazards?: Maybe<Array<EnergyHazardsType>>;
  id: Scalars['UUID'];
  lowEnergyHazards?: Maybe<Array<EnergyHazardsType>>;
  name?: Maybe<Scalars['String']>;
};

export type TaskStandardOperatingProcedureInput = {
  id: Scalars['UUID'];
  name?: InputMaybe<Scalars['String']>;
  sops?: InputMaybe<Array<OperatingProcedureInput>>;
};

export type TaskStandardOperatingProcedureType = {
  __typename?: 'TaskStandardOperatingProcedureType';
  id: Scalars['UUID'];
  name?: Maybe<Scalars['String']>;
  sops?: Maybe<Array<OperatingProcedureType>>;
};

export enum TaskStatus {
  Complete = 'COMPLETE',
  InProgress = 'IN_PROGRESS',
  NotCompleted = 'NOT_COMPLETED',
  NotStarted = 'NOT_STARTED'
}

export type TenantConfigurations = {
  __typename?: 'TenantConfigurations';
  entities: Array<WorkPackageConfiguration>;
};

export enum Triggers {
  ActivityChanged = 'ACTIVITY_CHANGED',
  ActivityDeleted = 'ACTIVITY_DELETED',
  ContractorChangedForProject = 'CONTRACTOR_CHANGED_FOR_PROJECT',
  ContractorDataChanged = 'CONTRACTOR_DATA_CHANGED',
  ContractorDataChangedForTenant = 'CONTRACTOR_DATA_CHANGED_FOR_TENANT',
  CrewDataChangedForTenant = 'CREW_DATA_CHANGED_FOR_TENANT',
  IncidentChanged = 'INCIDENT_CHANGED',
  LibraryTaskDataChanged = 'LIBRARY_TASK_DATA_CHANGED',
  ProjectChanged = 'PROJECT_CHANGED',
  ProjectLocationSiteConditionsChanged = 'PROJECT_LOCATION_SITE_CONDITIONS_CHANGED',
  SupervisorsChangedForProject = 'SUPERVISORS_CHANGED_FOR_PROJECT',
  SupervisorChangedForProjectLocation = 'SUPERVISOR_CHANGED_FOR_PROJECT_LOCATION',
  SupervisorDataChanged = 'SUPERVISOR_DATA_CHANGED',
  SupervisorDataChangedForTenant = 'SUPERVISOR_DATA_CHANGED_FOR_TENANT',
  TaskChanged = 'TASK_CHANGED',
  TaskDeleted = 'TASK_DELETED',
  UpdateTaskRisk = 'UPDATE_TASK_RISK'
}

export enum TypeOfControl {
  Direct = 'DIRECT',
  Indirect = 'INDIRECT'
}

export type UiConfigs = {
  __typename?: 'UIConfigs';
  Contents: Scalars['JSON'];
  contents: Scalars['JSON'];
  formType?: Maybe<FormType>;
  id: Scalars['UUID'];
};

export type UpdateInsightInput = {
  description?: InputMaybe<Scalars['String']>;
  name?: InputMaybe<Scalars['String']>;
  url?: InputMaybe<Scalars['String']>;
  visibility?: InputMaybe<Scalars['Boolean']>;
};

export type User = {
  __typename?: 'User';
  firstName?: Maybe<Scalars['String']>;
  id: Scalars['UUID'];
  lastName?: Maybe<Scalars['String']>;
  name: Scalars['String'];
};

export type UserInfoInput = {
  email: Scalars['String'];
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type UserInfoType = {
  __typename?: 'UserInfoType';
  email: Scalars['String'];
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type UserPreference = {
  __typename?: 'UserPreference';
  contents: Scalars['JSON'];
  createdAt: Scalars['DateTime'];
  entityType: UserPreferenceEntityType;
  id: Scalars['UUID'];
  updatedAt: Scalars['DateTime'];
  userId: Scalars['UUID'];
};

export enum UserPreferenceEntityType {
  CwfTemplateFilters = 'CWFTemplateFilters',
  CwfTemplateFormFilters = 'CWFTemplateFormFilters',
  FormFilters = 'FormFilters',
  MapFilters = 'MapFilters'
}

export type Voltage = {
  __typename?: 'Voltage';
  type: VoltageType;
  unit: Scalars['String'];
  value?: Maybe<Scalars['Float']>;
  valueStr?: Maybe<Scalars['String']>;
};

export type VoltageInformationFromConfigInput = {
  id: Scalars['UUID'];
  other: Scalars['Boolean'];
  value: Scalars['String'];
};

export type VoltageInformationFromConfigType = {
  __typename?: 'VoltageInformationFromConfigType';
  id: Scalars['UUID'];
  other: Scalars['Boolean'];
  value: Scalars['String'];
};

export type VoltageInformationInput = {
  circuit: Scalars['String'];
  voltages: Scalars['String'];
};

export type VoltageInformationType = {
  __typename?: 'VoltageInformationType';
  circuit: Scalars['String'];
  voltages: Scalars['String'];
};

export type VoltageInformationV2Input = {
  minimumApproachDistance?: InputMaybe<MininimumApproachDistanceInput>;
  voltage?: InputMaybe<VoltageInformationFromConfigInput>;
};

export type VoltageInformationV2Type = {
  __typename?: 'VoltageInformationV2Type';
  minimumApproachDistance?: Maybe<MininimumApproachDistanceType>;
  voltage?: Maybe<VoltageInformationFromConfigType>;
};

export type VoltageInput = {
  type: VoltageType;
  unit: Scalars['String'];
  value?: InputMaybe<Scalars['Float']>;
  valueStr?: InputMaybe<Scalars['String']>;
};

export enum VoltageType {
  Primary = 'PRIMARY',
  Secondary = 'SECONDARY',
  Transmission = 'TRANSMISSION'
}

export type WorkLocation = {
  __typename?: 'WorkLocation';
  address: Scalars['String'];
  city: Scalars['String'];
  description: Scalars['String'];
  operatingHq?: Maybe<Scalars['String']>;
  state: Scalars['String'];
};

export type WorkLocationInput = {
  address: Scalars['String'];
  city: Scalars['String'];
  description: Scalars['String'];
  operatingHq?: InputMaybe<Scalars['String']>;
  state: Scalars['String'];
};

export type WorkOs = {
  __typename?: 'WorkOS';
  workosDirectoryId: Scalars['String'];
  workosOrgId: Scalars['String'];
};

export type WorkOsDirectoryUsersResponseType = {
  __typename?: 'WorkOSDirectoryUsersResponseType';
  data: Array<DirectoryUser>;
};

export type WorkPackageConfiguration = {
  __typename?: 'WorkPackageConfiguration';
  attributes?: Maybe<Array<AttributeConfiguration>>;
  defaultLabel: Scalars['String'];
  defaultLabelPlural: Scalars['String'];
  key: Scalars['String'];
  label: Scalars['String'];
  labelPlural: Scalars['String'];
};

export type WorkPackageMetadata = {
  __typename?: 'WorkPackageMetadata';
  workPackageLocationId: Scalars['UUID'];
};

export type WorkPackageMetadataInput = {
  workPackageLocationId: Scalars['UUID'];
};

export type WorkProcedureSelection = {
  __typename?: 'WorkProcedureSelection';
  id: Scalars['String'];
  name?: Maybe<Scalars['String']>;
  values: Array<Scalars['String']>;
};

export type WorkProcedureSelectionInput = {
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
  values: Array<Scalars['String']>;
};

export type WorkSchedule = {
  __typename?: 'WorkSchedule';
  endDatetime?: Maybe<Scalars['DateTime']>;
  sectionIsValid?: Maybe<Scalars['Boolean']>;
  startDatetime?: Maybe<Scalars['DateTime']>;
};

export type WorkScheduleInput = {
  endDatetime?: InputMaybe<Scalars['DateTime']>;
  sectionIsValid?: InputMaybe<Scalars['Boolean']>;
  startDatetime?: InputMaybe<Scalars['DateTime']>;
};

export type WorkType = {
  __typename?: 'WorkType';
  code?: Maybe<Scalars['String']>;
  coreWorkTypeIds?: Maybe<Array<Scalars['UUID']>>;
  id: Scalars['UUID'];
  name: Scalars['String'];
  tenantId?: Maybe<Scalars['UUID']>;
};

export type WorkTypeConceptInput = {
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type WorkTypeConceptType = {
  __typename?: 'WorkTypeConceptType';
  id: Scalars['UUID'];
  name: Scalars['String'];
};

export type WorkTypeWithActivityAliasType = {
  __typename?: 'WorkTypeWithActivityAliasType';
  alias?: Maybe<Scalars['String']>;
  code?: Maybe<Scalars['String']>;
  coreWorkTypeIds?: Maybe<Array<Scalars['UUID']>>;
  id: Scalars['UUID'];
  name: Scalars['String'];
  tenantId?: Maybe<Scalars['UUID']>;
};

export type ActivitiesQueryVariables = Exact<{
  projectLocationId?: InputMaybe<Scalars['UUID']>;
}>;


export type ActivitiesQuery = { __typename?: 'Query', projectLocations: Array<{ __typename?: 'ProjectLocation', activities: Array<{ __typename?: 'Activity', id: any, name: string, status: ActivityStatus, startDate?: any | null, endDate?: any | null, tasks: Array<{ __typename?: 'Task', id: any, name: string, riskLevel: RiskLevel, status: TaskStatus, libraryTask: { __typename?: 'LibraryTask', id: any } }> }> }> };

export type CreateActivityMutationVariables = Exact<{
  activityData: CreateActivityInput;
}>;


export type CreateActivityMutation = { __typename?: 'Mutation', createActivity: { __typename?: 'Activity', id: any, location: { __typename?: 'ProjectLocation', id: any } } };

export type RemoveTasksFromActivityMutationVariables = Exact<{
  id: Scalars['UUID'];
  taskIds: RemoveActivityTasksInput;
}>;


export type RemoveTasksFromActivityMutation = { __typename?: 'Mutation', removeTasksFromActivity?: { __typename?: 'Activity', id: any, name: string, tasks: Array<{ __typename?: 'Task', id: any, name: string }> } | null };

export type AddTasksToActivityMutationVariables = Exact<{
  id: Scalars['UUID'];
  newTasks: AddActivityTasksInput;
}>;


export type AddTasksToActivityMutation = { __typename?: 'Mutation', addTasksToActivity: { __typename?: 'Activity', id: any, name: string, tasks: Array<{ __typename?: 'Task', id: any, name: string }> } };

export type DeleteActivityMutationVariables = Exact<{
  id: Scalars['UUID'];
}>;


export type DeleteActivityMutation = { __typename?: 'Mutation', deleteActivity: boolean };

export type CrewLeadersQueryVariables = Exact<{ [key: string]: never; }>;


export type CrewLeadersQuery = { __typename?: 'Query', crewLeaders: Array<{ __typename?: 'CrewLeader', id: any, name: string }> };

export type EboContentsFragment = { __typename?: 'EnergyBasedObservationLayout', additionalInformation?: string | null, historicIncidents?: Array<string> | null, activities?: Array<{ __typename?: 'EBOActivityConceptType', id?: any | null, name: string, tasks: Array<{ __typename?: 'EBOTaskSelectionConceptType', fromWorkOrder: boolean, riskLevel: RiskLevel, id: any, name?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> }> | null, details?: { __typename?: 'ObservationDetailsConceptType', observationDate: any, observationTime: any, workLocation?: string | null, workOrderNumber?: string | null, departmentObserved: { __typename?: 'DepartmentObservedConceptType', id?: any | null, name: string }, opcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, subopcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, workType?: Array<{ __typename?: 'WorkTypeConceptType', id: any, name: string }> | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, highEnergyTasks?: Array<{ __typename?: 'EBOHighEnergyTaskConceptType', id: string, name?: string | null, activityName?: string | null, activityId?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> | null, personnel?: Array<{ __typename?: 'PersonnelConceptType', id?: any | null, name: string, role?: string | null }> | null, summary?: { __typename?: 'EBOSummaryType', viewed: boolean } | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null };

export type EboQueryVariables = Exact<{
  id: Scalars['UUID'];
}>;


export type EboQuery = { __typename?: 'Query', energyBasedObservation: { __typename?: 'EnergyBasedObservation', completedAt?: any | null, createdAt: any, id: any, status: FormStatus, updatedAt?: any | null, createdBy?: { __typename?: 'User', id: any, firstName?: string | null, lastName?: string | null, name: string } | null, completedBy?: { __typename?: 'User', id: any } | null, contents: { __typename?: 'EnergyBasedObservationLayout', additionalInformation?: string | null, historicIncidents?: Array<string> | null, activities?: Array<{ __typename?: 'EBOActivityConceptType', id?: any | null, name: string, tasks: Array<{ __typename?: 'EBOTaskSelectionConceptType', fromWorkOrder: boolean, riskLevel: RiskLevel, id: any, name?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> }> | null, details?: { __typename?: 'ObservationDetailsConceptType', observationDate: any, observationTime: any, workLocation?: string | null, workOrderNumber?: string | null, departmentObserved: { __typename?: 'DepartmentObservedConceptType', id?: any | null, name: string }, opcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, subopcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, workType?: Array<{ __typename?: 'WorkTypeConceptType', id: any, name: string }> | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, highEnergyTasks?: Array<{ __typename?: 'EBOHighEnergyTaskConceptType', id: string, name?: string | null, activityName?: string | null, activityId?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> | null, personnel?: Array<{ __typename?: 'PersonnelConceptType', id?: any | null, name: string, role?: string | null }> | null, summary?: { __typename?: 'EBOSummaryType', viewed: boolean } | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null } }, me: { __typename?: 'Me', role?: string | null } };

export type SaveEboMutationVariables = Exact<{
  energyBasedObservationInput: EnergyBasedObservationInput;
  id?: InputMaybe<Scalars['UUID']>;
}>;


export type SaveEboMutation = { __typename?: 'Mutation', saveEnergyBasedObservation: { __typename?: 'EnergyBasedObservation', id: any, status: FormStatus, createdBy?: { __typename?: 'User', id: any, firstName?: string | null, lastName?: string | null, name: string } | null, contents: { __typename?: 'EnergyBasedObservationLayout', additionalInformation?: string | null, historicIncidents?: Array<string> | null, activities?: Array<{ __typename?: 'EBOActivityConceptType', id?: any | null, name: string, tasks: Array<{ __typename?: 'EBOTaskSelectionConceptType', fromWorkOrder: boolean, riskLevel: RiskLevel, id: any, name?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> }> | null, details?: { __typename?: 'ObservationDetailsConceptType', observationDate: any, observationTime: any, workLocation?: string | null, workOrderNumber?: string | null, departmentObserved: { __typename?: 'DepartmentObservedConceptType', id?: any | null, name: string }, opcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, subopcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, workType?: Array<{ __typename?: 'WorkTypeConceptType', id: any, name: string }> | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, highEnergyTasks?: Array<{ __typename?: 'EBOHighEnergyTaskConceptType', id: string, name?: string | null, activityName?: string | null, activityId?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> | null, personnel?: Array<{ __typename?: 'PersonnelConceptType', id?: any | null, name: string, role?: string | null }> | null, summary?: { __typename?: 'EBOSummaryType', viewed: boolean } | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null } } };

export type CompleteEboMutationVariables = Exact<{
  id: Scalars['UUID'];
  energyBasedObservationInput: EnergyBasedObservationInput;
}>;


export type CompleteEboMutation = { __typename?: 'Mutation', completeEnergyBasedObservation: { __typename?: 'EnergyBasedObservation', id: any, status: FormStatus, createdBy?: { __typename?: 'User', id: any, firstName?: string | null, lastName?: string | null, name: string } | null, contents: { __typename?: 'EnergyBasedObservationLayout', additionalInformation?: string | null, historicIncidents?: Array<string> | null, activities?: Array<{ __typename?: 'EBOActivityConceptType', id?: any | null, name: string, tasks: Array<{ __typename?: 'EBOTaskSelectionConceptType', fromWorkOrder: boolean, riskLevel: RiskLevel, id: any, name?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> }> | null, details?: { __typename?: 'ObservationDetailsConceptType', observationDate: any, observationTime: any, workLocation?: string | null, workOrderNumber?: string | null, departmentObserved: { __typename?: 'DepartmentObservedConceptType', id?: any | null, name: string }, opcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, subopcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, workType?: Array<{ __typename?: 'WorkTypeConceptType', id: any, name: string }> | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, highEnergyTasks?: Array<{ __typename?: 'EBOHighEnergyTaskConceptType', id: string, name?: string | null, activityName?: string | null, activityId?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> | null, personnel?: Array<{ __typename?: 'PersonnelConceptType', id?: any | null, name: string, role?: string | null }> | null, summary?: { __typename?: 'EBOSummaryType', viewed: boolean } | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null } } };

export type ReopenEboMutationVariables = Exact<{
  id: Scalars['UUID'];
}>;


export type ReopenEboMutation = { __typename?: 'Mutation', reopenEnergyBasedObservation: { __typename?: 'EnergyBasedObservation', id: any, status: FormStatus, createdBy?: { __typename?: 'User', id: any, firstName?: string | null, lastName?: string | null, name: string } | null, contents: { __typename?: 'EnergyBasedObservationLayout', additionalInformation?: string | null, historicIncidents?: Array<string> | null, activities?: Array<{ __typename?: 'EBOActivityConceptType', id?: any | null, name: string, tasks: Array<{ __typename?: 'EBOTaskSelectionConceptType', fromWorkOrder: boolean, riskLevel: RiskLevel, id: any, name?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> }> | null, details?: { __typename?: 'ObservationDetailsConceptType', observationDate: any, observationTime: any, workLocation?: string | null, workOrderNumber?: string | null, departmentObserved: { __typename?: 'DepartmentObservedConceptType', id?: any | null, name: string }, opcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, subopcoObserved?: { __typename?: 'OpCoObservedConceptType', id: any, name: string, fullName?: string | null } | null, workType?: Array<{ __typename?: 'WorkTypeConceptType', id: any, name: string }> | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, highEnergyTasks?: Array<{ __typename?: 'EBOHighEnergyTaskConceptType', id: string, name?: string | null, activityName?: string | null, activityId?: string | null, instanceId: number, taskHazardConnectorId?: string | null, hazards: Array<{ __typename?: 'EBOHazardObservationConceptType', id: string, hazardControlConnectorId?: string | null, taskHazardConnectorId?: string | null, name?: string | null, description?: string | null, energyLevel?: string | null, directControlsImplemented?: boolean | null, observed: boolean, reason?: string | null, directControlDescription?: string | null, limitedControlDescription?: string | null, indirectControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, directControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null, limitedControls?: Array<{ __typename?: 'EBOControlsConceptType', id: string, hazardControlConnectorId?: string | null, name?: string | null }> | null }> }> | null, personnel?: Array<{ __typename?: 'PersonnelConceptType', id?: any | null, name: string, role?: string | null }> | null, summary?: { __typename?: 'EBOSummaryType', viewed: boolean } | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null } } };

export type DeleteEboMutationVariables = Exact<{
  id: Scalars['UUID'];
}>;


export type DeleteEboMutation = { __typename?: 'Mutation', deleteEnergyBasedObservation: boolean };

export type HistoricalIncidentsQueryVariables = Exact<{
  libraryTaskId: Scalars['UUID'];
}>;


export type HistoricalIncidentsQuery = { __typename?: 'Query', historicalIncidents: Array<{ __typename?: 'Incident', id: any, severity?: string | null, incidentDate: any, taskTypeId?: any | null, taskType?: string | null, severityCode?: IncidentSeverityEnum | null, incidentType: string, incidentId?: string | null, description: string }> };

export type FileUploadPoliciesMutationVariables = Exact<{
  count: Scalars['Int'];
}>;


export type FileUploadPoliciesMutation = { __typename?: 'Mutation', fileUploadPolicies: Array<{ __typename?: 'SignedPostPolicy', id: string, url: string, signedUrl: string, fields: string }> };

export type HazardsLibraryQueryVariables = Exact<{
  type: LibraryFilterType;
  libraryTaskId?: InputMaybe<Scalars['UUID']>;
  librarySiteConditionId?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy> | OrderBy>;
}>;


export type HazardsLibraryQuery = { __typename?: 'Query', hazardsLibrary: Array<{ __typename?: 'LibraryHazard', id: any, name: string, isApplicable: boolean, energyType?: EnergyType | null, energyLevel?: EnergyLevel | null, imageUrl: string, controls: Array<{ __typename?: 'LibraryControl', id: any, name: string, isApplicable: boolean, controlType?: TypeOfControl | null }>, taskApplicabilityLevels: Array<{ __typename?: 'TaskApplicabilityLevel', applicabilityLevel: ApplicabilityLevel, taskId: any }> }> };

export type JsbContentsFragment = { __typename?: 'JobSafetyBriefingLayout', jsbId: any, otherWorkProcedures?: string | null, hazardsAndControlsNotes?: string | null, controlAssessmentSelections?: Array<{ __typename?: 'ControlAssessment', hazardId: string, controlIds?: Array<string> | null, controlSelections?: Array<{ __typename?: 'ControlSelection', id: string, selected?: boolean | null, recommended?: boolean | null }> | null }> | null, emergencyContacts?: Array<{ __typename?: 'EmergencyContact', name: string, phoneNumber: string, primary: boolean }> | null, jsbMetadata?: { __typename?: 'JSBMetadata', briefingDateTime: any } | null, nearestMedicalFacility?: { __typename?: 'MedicalFacility', description: string, address?: string | null, city?: string | null, distanceFromJob?: number | null, phoneNumber?: string | null, state?: string | null, zip?: number | null } | null, customNearestMedicalFacility?: { __typename?: 'CustomMedicalFacility', address: string } | null, aedInformation?: { __typename?: 'AEDInformation', location: string } | null, activities?: Array<{ __typename?: 'ActivityConceptType', name: string, tasks: Array<{ __typename?: 'TaskSelectionConcept', id: any }> }> | null, taskSelections?: Array<{ __typename?: 'TaskSelectionConcept', id: any, fromWorkOrder: boolean }> | null, recommendedTaskSelections?: Array<{ __typename?: 'RecommendedTaskSelection', id: any, fromWorkOrder: boolean, recommended?: boolean | null, selected?: boolean | null }> | null, workLocation?: { __typename?: 'WorkLocation', address: string, city: string, description: string, state: string, operatingHq?: string | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, workProcedureSelections?: Array<{ __typename?: 'WorkProcedureSelection', id: string, values: Array<string> }> | null, energySourceControl?: { __typename?: 'EnergySourceControl', arcFlashCategory?: number | null, clearancePoints?: string | null, transferOfControl: boolean, ewp: Array<{ __typename?: 'EWP', id: string, referencePoints: Array<string>, metadata: { __typename?: 'EWPMetadata', completed?: any | null, issued: any, issuedBy: string, procedure: string, receivedBy: string, remote: boolean }, equipmentInformation: Array<{ __typename?: 'EquipmentInformation', circuitBreaker: string, switch: string, transformer: string }> }>, voltages: Array<{ __typename?: 'Voltage', type: VoltageType, unit: string, valueStr?: string | null }> } | null, siteConditionSelections?: Array<{ __typename?: 'SiteConditionSelection', id: any, recommended: boolean, selected: boolean }> | null, criticalRiskAreaSelections?: Array<{ __typename?: 'CriticalRiskArea', name: string }> | null, crewSignOff?: Array<{ __typename?: 'CrewInformationType', name?: string | null, type?: CrewType | null, externalId?: string | null, employeeNumber?: string | null, jobTitle?: string | null, signature?: { __typename?: 'File', id: string, name: string, displayName: string, size?: string | null, url: string, signedUrl: string } | null }> | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null, documents?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, groupDiscussion?: { __typename?: 'GroupDiscussionType', viewed: boolean } | null };

export type JsbDataFragment = { __typename?: 'JobSafetyBriefing', id: any, updatedAt?: any | null, createdAt: any, workPackage?: { __typename?: 'Project', id: any, locations: Array<{ __typename?: 'ProjectLocation', name: string }> } | null, contents: { __typename?: 'JobSafetyBriefingLayout', jsbId: any, otherWorkProcedures?: string | null, hazardsAndControlsNotes?: string | null, controlAssessmentSelections?: Array<{ __typename?: 'ControlAssessment', hazardId: string, controlIds?: Array<string> | null, controlSelections?: Array<{ __typename?: 'ControlSelection', id: string, selected?: boolean | null, recommended?: boolean | null }> | null }> | null, emergencyContacts?: Array<{ __typename?: 'EmergencyContact', name: string, phoneNumber: string, primary: boolean }> | null, jsbMetadata?: { __typename?: 'JSBMetadata', briefingDateTime: any } | null, nearestMedicalFacility?: { __typename?: 'MedicalFacility', description: string, address?: string | null, city?: string | null, distanceFromJob?: number | null, phoneNumber?: string | null, state?: string | null, zip?: number | null } | null, customNearestMedicalFacility?: { __typename?: 'CustomMedicalFacility', address: string } | null, aedInformation?: { __typename?: 'AEDInformation', location: string } | null, activities?: Array<{ __typename?: 'ActivityConceptType', name: string, tasks: Array<{ __typename?: 'TaskSelectionConcept', id: any }> }> | null, taskSelections?: Array<{ __typename?: 'TaskSelectionConcept', id: any, fromWorkOrder: boolean }> | null, recommendedTaskSelections?: Array<{ __typename?: 'RecommendedTaskSelection', id: any, fromWorkOrder: boolean, recommended?: boolean | null, selected?: boolean | null }> | null, workLocation?: { __typename?: 'WorkLocation', address: string, city: string, description: string, state: string, operatingHq?: string | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, workProcedureSelections?: Array<{ __typename?: 'WorkProcedureSelection', id: string, values: Array<string> }> | null, energySourceControl?: { __typename?: 'EnergySourceControl', arcFlashCategory?: number | null, clearancePoints?: string | null, transferOfControl: boolean, ewp: Array<{ __typename?: 'EWP', id: string, referencePoints: Array<string>, metadata: { __typename?: 'EWPMetadata', completed?: any | null, issued: any, issuedBy: string, procedure: string, receivedBy: string, remote: boolean }, equipmentInformation: Array<{ __typename?: 'EquipmentInformation', circuitBreaker: string, switch: string, transformer: string }> }>, voltages: Array<{ __typename?: 'Voltage', type: VoltageType, unit: string, valueStr?: string | null }> } | null, siteConditionSelections?: Array<{ __typename?: 'SiteConditionSelection', id: any, recommended: boolean, selected: boolean }> | null, criticalRiskAreaSelections?: Array<{ __typename?: 'CriticalRiskArea', name: string }> | null, crewSignOff?: Array<{ __typename?: 'CrewInformationType', name?: string | null, type?: CrewType | null, externalId?: string | null, employeeNumber?: string | null, jobTitle?: string | null, signature?: { __typename?: 'File', id: string, name: string, displayName: string, size?: string | null, url: string, signedUrl: string } | null }> | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null, documents?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, groupDiscussion?: { __typename?: 'GroupDiscussionType', viewed: boolean } | null }, createdBy?: { __typename?: 'User', id: any, name: string } | null, completedBy?: { __typename?: 'User', id: any } | null };

export type JsbQueryVariables = Exact<{
  id: Scalars['UUID'];
}>;


export type JsbQuery = { __typename?: 'Query', jobSafetyBriefing: { __typename?: 'JobSafetyBriefing', id: any, updatedAt?: any | null, createdAt: any, workPackage?: { __typename?: 'Project', id: any, locations: Array<{ __typename?: 'ProjectLocation', name: string }> } | null, contents: { __typename?: 'JobSafetyBriefingLayout', jsbId: any, otherWorkProcedures?: string | null, hazardsAndControlsNotes?: string | null, controlAssessmentSelections?: Array<{ __typename?: 'ControlAssessment', hazardId: string, controlIds?: Array<string> | null, controlSelections?: Array<{ __typename?: 'ControlSelection', id: string, selected?: boolean | null, recommended?: boolean | null }> | null }> | null, emergencyContacts?: Array<{ __typename?: 'EmergencyContact', name: string, phoneNumber: string, primary: boolean }> | null, jsbMetadata?: { __typename?: 'JSBMetadata', briefingDateTime: any } | null, nearestMedicalFacility?: { __typename?: 'MedicalFacility', description: string, address?: string | null, city?: string | null, distanceFromJob?: number | null, phoneNumber?: string | null, state?: string | null, zip?: number | null } | null, customNearestMedicalFacility?: { __typename?: 'CustomMedicalFacility', address: string } | null, aedInformation?: { __typename?: 'AEDInformation', location: string } | null, activities?: Array<{ __typename?: 'ActivityConceptType', name: string, tasks: Array<{ __typename?: 'TaskSelectionConcept', id: any }> }> | null, taskSelections?: Array<{ __typename?: 'TaskSelectionConcept', id: any, fromWorkOrder: boolean }> | null, recommendedTaskSelections?: Array<{ __typename?: 'RecommendedTaskSelection', id: any, fromWorkOrder: boolean, recommended?: boolean | null, selected?: boolean | null }> | null, workLocation?: { __typename?: 'WorkLocation', address: string, city: string, description: string, state: string, operatingHq?: string | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, workProcedureSelections?: Array<{ __typename?: 'WorkProcedureSelection', id: string, values: Array<string> }> | null, energySourceControl?: { __typename?: 'EnergySourceControl', arcFlashCategory?: number | null, clearancePoints?: string | null, transferOfControl: boolean, ewp: Array<{ __typename?: 'EWP', id: string, referencePoints: Array<string>, metadata: { __typename?: 'EWPMetadata', completed?: any | null, issued: any, issuedBy: string, procedure: string, receivedBy: string, remote: boolean }, equipmentInformation: Array<{ __typename?: 'EquipmentInformation', circuitBreaker: string, switch: string, transformer: string }> }>, voltages: Array<{ __typename?: 'Voltage', type: VoltageType, unit: string, valueStr?: string | null }> } | null, siteConditionSelections?: Array<{ __typename?: 'SiteConditionSelection', id: any, recommended: boolean, selected: boolean }> | null, criticalRiskAreaSelections?: Array<{ __typename?: 'CriticalRiskArea', name: string }> | null, crewSignOff?: Array<{ __typename?: 'CrewInformationType', name?: string | null, type?: CrewType | null, externalId?: string | null, employeeNumber?: string | null, jobTitle?: string | null, signature?: { __typename?: 'File', id: string, name: string, displayName: string, size?: string | null, url: string, signedUrl: string } | null }> | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null, documents?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, groupDiscussion?: { __typename?: 'GroupDiscussionType', viewed: boolean } | null }, createdBy?: { __typename?: 'User', id: any, name: string } | null, completedBy?: { __typename?: 'User', id: any } | null }, me: { __typename?: 'Me', role?: string | null } };

export type SaveJsbMutationVariables = Exact<{
  input: SaveJobSafetyBriefingInput;
}>;


export type SaveJsbMutation = { __typename?: 'Mutation', saveJobSafetyBriefing: { __typename?: 'JobSafetyBriefing', id: any, updatedAt?: any | null, createdAt: any, workPackage?: { __typename?: 'Project', id: any, locations: Array<{ __typename?: 'ProjectLocation', name: string }> } | null, contents: { __typename?: 'JobSafetyBriefingLayout', jsbId: any, otherWorkProcedures?: string | null, hazardsAndControlsNotes?: string | null, controlAssessmentSelections?: Array<{ __typename?: 'ControlAssessment', hazardId: string, controlIds?: Array<string> | null, controlSelections?: Array<{ __typename?: 'ControlSelection', id: string, selected?: boolean | null, recommended?: boolean | null }> | null }> | null, emergencyContacts?: Array<{ __typename?: 'EmergencyContact', name: string, phoneNumber: string, primary: boolean }> | null, jsbMetadata?: { __typename?: 'JSBMetadata', briefingDateTime: any } | null, nearestMedicalFacility?: { __typename?: 'MedicalFacility', description: string, address?: string | null, city?: string | null, distanceFromJob?: number | null, phoneNumber?: string | null, state?: string | null, zip?: number | null } | null, customNearestMedicalFacility?: { __typename?: 'CustomMedicalFacility', address: string } | null, aedInformation?: { __typename?: 'AEDInformation', location: string } | null, activities?: Array<{ __typename?: 'ActivityConceptType', name: string, tasks: Array<{ __typename?: 'TaskSelectionConcept', id: any }> }> | null, taskSelections?: Array<{ __typename?: 'TaskSelectionConcept', id: any, fromWorkOrder: boolean }> | null, recommendedTaskSelections?: Array<{ __typename?: 'RecommendedTaskSelection', id: any, fromWorkOrder: boolean, recommended?: boolean | null, selected?: boolean | null }> | null, workLocation?: { __typename?: 'WorkLocation', address: string, city: string, description: string, state: string, operatingHq?: string | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, workProcedureSelections?: Array<{ __typename?: 'WorkProcedureSelection', id: string, values: Array<string> }> | null, energySourceControl?: { __typename?: 'EnergySourceControl', arcFlashCategory?: number | null, clearancePoints?: string | null, transferOfControl: boolean, ewp: Array<{ __typename?: 'EWP', id: string, referencePoints: Array<string>, metadata: { __typename?: 'EWPMetadata', completed?: any | null, issued: any, issuedBy: string, procedure: string, receivedBy: string, remote: boolean }, equipmentInformation: Array<{ __typename?: 'EquipmentInformation', circuitBreaker: string, switch: string, transformer: string }> }>, voltages: Array<{ __typename?: 'Voltage', type: VoltageType, unit: string, valueStr?: string | null }> } | null, siteConditionSelections?: Array<{ __typename?: 'SiteConditionSelection', id: any, recommended: boolean, selected: boolean }> | null, criticalRiskAreaSelections?: Array<{ __typename?: 'CriticalRiskArea', name: string }> | null, crewSignOff?: Array<{ __typename?: 'CrewInformationType', name?: string | null, type?: CrewType | null, externalId?: string | null, employeeNumber?: string | null, jobTitle?: string | null, signature?: { __typename?: 'File', id: string, name: string, displayName: string, size?: string | null, url: string, signedUrl: string } | null }> | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null, documents?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, groupDiscussion?: { __typename?: 'GroupDiscussionType', viewed: boolean } | null }, createdBy?: { __typename?: 'User', id: any, name: string } | null, completedBy?: { __typename?: 'User', id: any } | null } };

export type CompleteJsbMutationVariables = Exact<{
  input: SaveJobSafetyBriefingInput;
}>;


export type CompleteJsbMutation = { __typename?: 'Mutation', completeJobSafetyBriefing: { __typename?: 'JobSafetyBriefing', id: any, updatedAt?: any | null, createdAt: any, workPackage?: { __typename?: 'Project', id: any, locations: Array<{ __typename?: 'ProjectLocation', name: string }> } | null, contents: { __typename?: 'JobSafetyBriefingLayout', jsbId: any, otherWorkProcedures?: string | null, hazardsAndControlsNotes?: string | null, controlAssessmentSelections?: Array<{ __typename?: 'ControlAssessment', hazardId: string, controlIds?: Array<string> | null, controlSelections?: Array<{ __typename?: 'ControlSelection', id: string, selected?: boolean | null, recommended?: boolean | null }> | null }> | null, emergencyContacts?: Array<{ __typename?: 'EmergencyContact', name: string, phoneNumber: string, primary: boolean }> | null, jsbMetadata?: { __typename?: 'JSBMetadata', briefingDateTime: any } | null, nearestMedicalFacility?: { __typename?: 'MedicalFacility', description: string, address?: string | null, city?: string | null, distanceFromJob?: number | null, phoneNumber?: string | null, state?: string | null, zip?: number | null } | null, customNearestMedicalFacility?: { __typename?: 'CustomMedicalFacility', address: string } | null, aedInformation?: { __typename?: 'AEDInformation', location: string } | null, activities?: Array<{ __typename?: 'ActivityConceptType', name: string, tasks: Array<{ __typename?: 'TaskSelectionConcept', id: any }> }> | null, taskSelections?: Array<{ __typename?: 'TaskSelectionConcept', id: any, fromWorkOrder: boolean }> | null, recommendedTaskSelections?: Array<{ __typename?: 'RecommendedTaskSelection', id: any, fromWorkOrder: boolean, recommended?: boolean | null, selected?: boolean | null }> | null, workLocation?: { __typename?: 'WorkLocation', address: string, city: string, description: string, state: string, operatingHq?: string | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, workProcedureSelections?: Array<{ __typename?: 'WorkProcedureSelection', id: string, values: Array<string> }> | null, energySourceControl?: { __typename?: 'EnergySourceControl', arcFlashCategory?: number | null, clearancePoints?: string | null, transferOfControl: boolean, ewp: Array<{ __typename?: 'EWP', id: string, referencePoints: Array<string>, metadata: { __typename?: 'EWPMetadata', completed?: any | null, issued: any, issuedBy: string, procedure: string, receivedBy: string, remote: boolean }, equipmentInformation: Array<{ __typename?: 'EquipmentInformation', circuitBreaker: string, switch: string, transformer: string }> }>, voltages: Array<{ __typename?: 'Voltage', type: VoltageType, unit: string, valueStr?: string | null }> } | null, siteConditionSelections?: Array<{ __typename?: 'SiteConditionSelection', id: any, recommended: boolean, selected: boolean }> | null, criticalRiskAreaSelections?: Array<{ __typename?: 'CriticalRiskArea', name: string }> | null, crewSignOff?: Array<{ __typename?: 'CrewInformationType', name?: string | null, type?: CrewType | null, externalId?: string | null, employeeNumber?: string | null, jobTitle?: string | null, signature?: { __typename?: 'File', id: string, name: string, displayName: string, size?: string | null, url: string, signedUrl: string } | null }> | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null, documents?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, groupDiscussion?: { __typename?: 'GroupDiscussionType', viewed: boolean } | null }, createdBy?: { __typename?: 'User', id: any, name: string } | null, completedBy?: { __typename?: 'User', id: any } | null } };

export type DeleteJsbMutationVariables = Exact<{
  id: Scalars['UUID'];
}>;


export type DeleteJsbMutation = { __typename?: 'Mutation', deleteJobSafetyBriefing: boolean };

export type ReopenJsbMutationVariables = Exact<{
  id: Scalars['UUID'];
}>;


export type ReopenJsbMutation = { __typename?: 'Mutation', reopenJobSafetyBriefing: { __typename?: 'JobSafetyBriefing', id: any, updatedAt?: any | null, createdAt: any, workPackage?: { __typename?: 'Project', id: any, locations: Array<{ __typename?: 'ProjectLocation', name: string }> } | null, contents: { __typename?: 'JobSafetyBriefingLayout', jsbId: any, otherWorkProcedures?: string | null, hazardsAndControlsNotes?: string | null, controlAssessmentSelections?: Array<{ __typename?: 'ControlAssessment', hazardId: string, controlIds?: Array<string> | null, controlSelections?: Array<{ __typename?: 'ControlSelection', id: string, selected?: boolean | null, recommended?: boolean | null }> | null }> | null, emergencyContacts?: Array<{ __typename?: 'EmergencyContact', name: string, phoneNumber: string, primary: boolean }> | null, jsbMetadata?: { __typename?: 'JSBMetadata', briefingDateTime: any } | null, nearestMedicalFacility?: { __typename?: 'MedicalFacility', description: string, address?: string | null, city?: string | null, distanceFromJob?: number | null, phoneNumber?: string | null, state?: string | null, zip?: number | null } | null, customNearestMedicalFacility?: { __typename?: 'CustomMedicalFacility', address: string } | null, aedInformation?: { __typename?: 'AEDInformation', location: string } | null, activities?: Array<{ __typename?: 'ActivityConceptType', name: string, tasks: Array<{ __typename?: 'TaskSelectionConcept', id: any }> }> | null, taskSelections?: Array<{ __typename?: 'TaskSelectionConcept', id: any, fromWorkOrder: boolean }> | null, recommendedTaskSelections?: Array<{ __typename?: 'RecommendedTaskSelection', id: any, fromWorkOrder: boolean, recommended?: boolean | null, selected?: boolean | null }> | null, workLocation?: { __typename?: 'WorkLocation', address: string, city: string, description: string, state: string, operatingHq?: string | null } | null, gpsCoordinates?: Array<{ __typename?: 'GPSCoordinates', latitude: any, longitude: any }> | null, workProcedureSelections?: Array<{ __typename?: 'WorkProcedureSelection', id: string, values: Array<string> }> | null, energySourceControl?: { __typename?: 'EnergySourceControl', arcFlashCategory?: number | null, clearancePoints?: string | null, transferOfControl: boolean, ewp: Array<{ __typename?: 'EWP', id: string, referencePoints: Array<string>, metadata: { __typename?: 'EWPMetadata', completed?: any | null, issued: any, issuedBy: string, procedure: string, receivedBy: string, remote: boolean }, equipmentInformation: Array<{ __typename?: 'EquipmentInformation', circuitBreaker: string, switch: string, transformer: string }> }>, voltages: Array<{ __typename?: 'Voltage', type: VoltageType, unit: string, valueStr?: string | null }> } | null, siteConditionSelections?: Array<{ __typename?: 'SiteConditionSelection', id: any, recommended: boolean, selected: boolean }> | null, criticalRiskAreaSelections?: Array<{ __typename?: 'CriticalRiskArea', name: string }> | null, crewSignOff?: Array<{ __typename?: 'CrewInformationType', name?: string | null, type?: CrewType | null, externalId?: string | null, employeeNumber?: string | null, jobTitle?: string | null, signature?: { __typename?: 'File', id: string, name: string, displayName: string, size?: string | null, url: string, signedUrl: string } | null }> | null, photos?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, sourceInfo?: { __typename?: 'SourceInformationConceptsType', sourceInformation?: SourceAppInformation | null, appVersion?: string | null } | null, documents?: Array<{ __typename?: 'File', id: string, category?: FileCategory | null, crc32c?: string | null, date?: any | null, displayName: string, exists: boolean, md5?: string | null, mimetype?: string | null, name: string, signedUrl: string, size?: string | null, time?: string | null, url: string }> | null, groupDiscussion?: { __typename?: 'GroupDiscussionType', viewed: boolean } | null }, createdBy?: { __typename?: 'User', id: any, name: string } | null, completedBy?: { __typename?: 'User', id: any } | null } };

export type LastAddedAdhocJobSafetyBriefingQueryVariables = Exact<{ [key: string]: never; }>;


export type LastAddedAdhocJobSafetyBriefingQuery = { __typename?: 'Query', lastAddedAdhocJobSafetyBriefing?: { __typename?: 'JobSafetyBriefing', contents: { __typename?: 'JobSafetyBriefingLayout', workLocation?: { __typename?: 'WorkLocation', address: string, operatingHq?: string | null } | null, nearestMedicalFacility?: { __typename?: 'MedicalFacility', address?: string | null, description: string, city?: string | null, distanceFromJob?: number | null, phoneNumber?: string | null, state?: string | null, zip?: number | null } | null, aedInformation?: { __typename?: 'AEDInformation', location: string } | null, emergencyContacts?: Array<{ __typename?: 'EmergencyContact', name: string, phoneNumber: string, primary: boolean }> | null } } | null };

export type LastAddedJobSafetyBriefingQueryVariables = Exact<{
  projectLocationId?: InputMaybe<Scalars['UUID']>;
  filterOn: JsbFiltersOnEnum;
}>;


export type LastAddedJobSafetyBriefingQuery = { __typename?: 'Query', lastAddedJobSafetyBriefing?: { __typename?: 'JobSafetyBriefing', contents: { __typename?: 'JobSafetyBriefingLayout', workLocation?: { __typename?: 'WorkLocation', address: string, description: string } | null, nearestMedicalFacility?: { __typename?: 'MedicalFacility', address?: string | null, description: string, city?: string | null, distanceFromJob?: number | null, phoneNumber?: string | null, state?: string | null, zip?: number | null } | null, aedInformation?: { __typename?: 'AEDInformation', location: string } | null, emergencyContacts?: Array<{ __typename?: 'EmergencyContact', name: string, phoneNumber: string, primary: boolean }> | null } } | null };

export type LocationSiteConditionsQueryVariables = Exact<{
  siteInput: SiteLocationInput;
}>;


export type LocationSiteConditionsQuery = { __typename?: 'Query', locationSiteConditions: Array<{ __typename?: 'SiteCondition', id: any, name: string, librarySiteCondition: { __typename?: 'LinkedLibrarySiteCondition', id: any } }> };

export type NearestMedicalFacilitiesQueryVariables = Exact<{
  latitude: Scalars['Decimal'];
  longitude: Scalars['Decimal'];
}>;


export type NearestMedicalFacilitiesQuery = { __typename?: 'Query', nearestMedicalFacilities: Array<{ __typename?: 'MedicalFacility', description: string, address?: string | null, city?: string | null, distanceFromJob?: number | null, phoneNumber?: string | null, state?: string | null, zip?: number | null }> };

export type ProjectLocationsQueryVariables = Exact<{
  id?: InputMaybe<Scalars['UUID']>;
  date?: InputMaybe<Scalars['Date']>;
}>;


export type ProjectLocationsQuery = { __typename?: 'Query', projectLocations: Array<{ __typename?: 'ProjectLocation', id: any, name: string, address?: string | null, latitude: any, longitude: any, riskLevel: RiskLevel, project?: { __typename?: 'Project', id: any, name: string, description?: string | null } | null, activities: Array<{ __typename?: 'Activity', id: any, name: string, status: ActivityStatus, startDate?: any | null, endDate?: any | null, tasks: Array<{ __typename?: 'Task', id: any, name: string, riskLevel: RiskLevel, status: TaskStatus, libraryTask: { __typename?: 'LibraryTask', id: any } }> }>, jobSafetyBriefings: Array<{ __typename?: 'JobSafetyBriefing', id: any, name: string, status: FormStatus, completedAt?: any | null, completedBy?: { __typename?: 'User', id: any, name: string } | null }>, tasks: Array<{ __typename?: 'Task', id: any, name: string, riskLevel: RiskLevel, status: TaskStatus, libraryTask: { __typename?: 'LibraryTask', id: any } }>, siteConditions: Array<{ __typename?: 'SiteCondition', id: any, name: string, librarySiteCondition: { __typename?: 'LinkedLibrarySiteCondition', id: any } }> }> };

export type RegionsLibraryQueryVariables = Exact<{ [key: string]: never; }>;


export type RegionsLibraryQuery = { __typename?: 'Query', regionsLibrary: Array<{ __typename?: 'LibraryRegion', id: any, name: string }> };

export type SiteConditionsLibraryQueryVariables = Exact<{ [key: string]: never; }>;


export type SiteConditionsLibraryQuery = { __typename?: 'Query', siteConditionsLibrary: Array<{ __typename?: 'LibrarySiteCondition', id: any, name: string, archivedAt?: any | null, hazards: Array<{ __typename?: 'LibraryHazard', id: any, name: string, isApplicable: boolean, energyLevel?: EnergyLevel | null, taskApplicabilityLevels: Array<{ __typename?: 'TaskApplicabilityLevel', applicabilityLevel: ApplicabilityLevel, taskId: any }>, controls: Array<{ __typename?: 'LibraryControl', id: any, name: string, isApplicable: boolean, ppe?: boolean | null }> }> }> };

export type SiteConditionsQueryVariables = Exact<{
  locationId?: InputMaybe<Scalars['UUID']>;
  date?: InputMaybe<Scalars['Date']>;
}>;


export type SiteConditionsQuery = { __typename?: 'Query', siteConditions: Array<{ __typename?: 'SiteCondition', id: any, name: string, librarySiteCondition: { __typename?: 'LinkedLibrarySiteCondition', id: any } }> };

export type CreateSiteConditionMutationVariables = Exact<{
  siteConditionData: CreateSiteConditionInput;
}>;


export type CreateSiteConditionMutation = { __typename?: 'Mutation', createSiteCondition: { __typename?: 'SiteCondition', id: any, location: { __typename?: 'ProjectLocation', id: any } } };

export type TasksQueryVariables = Exact<{
  tasksId?: InputMaybe<Scalars['UUID']>;
  locationId?: InputMaybe<Scalars['UUID']>;
  date?: InputMaybe<Scalars['Date']>;
}>;


export type TasksQuery = { __typename?: 'Query', tasks: Array<{ __typename?: 'Task', id: any, name: string }> };

export type TasksLibraryQueryVariables = Exact<{
  tasksLibraryId?: InputMaybe<Array<Scalars['UUID']> | Scalars['UUID']>;
  orderBy?: InputMaybe<Array<LibraryTaskOrderBy> | LibraryTaskOrderBy>;
  hazardsOrderBy?: InputMaybe<Array<OrderBy> | OrderBy>;
  controlsOrderBy?: InputMaybe<Array<OrderBy> | OrderBy>;
}>;


export type TasksLibraryQuery = { __typename?: 'Query', tasksLibrary: Array<{ __typename?: 'LibraryTask', id: any, name: string, riskLevel: RiskLevel, hespScore: number, category?: string | null, workTypes?: Array<{ __typename?: 'WorkType', id: any, name: string }> | null, hazards: Array<{ __typename?: 'LibraryHazard', id: any, name: string, isApplicable: boolean, energyType?: EnergyType | null, energyLevel?: EnergyLevel | null, archivedAt?: any | null, controls: Array<{ __typename?: 'LibraryControl', id: any, name: string, isApplicable: boolean, ppe?: boolean | null }>, taskApplicabilityLevels: Array<{ __typename?: 'TaskApplicabilityLevel', applicabilityLevel: ApplicabilityLevel, taskId: any }> }>, activitiesGroups?: Array<{ __typename?: 'LibraryActivityGroup', id: any, name: string, tasks: Array<{ __typename?: 'LibraryTask', id: any }> }> | null }> };

export type TenantLinkedHazardsLibraryQueryVariables = Exact<{
  type?: InputMaybe<LibraryFilterType>;
  libraryTaskId?: InputMaybe<Scalars['UUID']>;
  librarySiteConditionId?: InputMaybe<Scalars['UUID']>;
  orderBy?: InputMaybe<Array<OrderBy> | OrderBy>;
}>;


export type TenantLinkedHazardsLibraryQuery = { __typename?: 'Query', tenantLinkedHazardsLibrary: Array<{ __typename?: 'LinkedLibraryHazard', id: any, name: string, isApplicable: boolean, energyLevel?: EnergyLevel | null, energyType?: EnergyType | null, imageUrl: string, taskApplicabilityLevels: Array<{ __typename?: 'TaskApplicabilityLevel', applicabilityLevel: ApplicabilityLevel, taskId: any }>, controls: Array<{ __typename?: 'LinkedLibraryControl', id: any, name: string, isApplicable: boolean, controlType?: TypeOfControl | null, ppe?: boolean | null, archivedAt?: any | null }> }> };

export type WorkosDirectoryUsersQueryVariables = Exact<{
  directoryIds: Array<Scalars['String']> | Scalars['String'];
}>;


export type WorkosDirectoryUsersQuery = { __typename?: 'Query', workosDirectoryUsers: { __typename?: 'WorkOSDirectoryUsersResponseType', data: Array<{ __typename?: 'DirectoryUser', id: string, idpId: string, directoryId: string, organizationId?: string | null, firstName?: string | null, lastName?: string | null, jobTitle?: string | null, username?: string | null, state: DirectoryUserState, customAttributes: any, rawAttributes?: any | null, role?: any | null, slug?: string | null, createdAt: string, updatedAt: string }> } };

export const EboContentsFragmentDoc = gql`
    fragment EboContents on EnergyBasedObservationLayout {
  activities {
    id
    name
    tasks {
      fromWorkOrder
      riskLevel
      id
      name
      instanceId
      taskHazardConnectorId
      hazards {
        id
        hazardControlConnectorId
        taskHazardConnectorId
        name
        description
        energyLevel
        directControlsImplemented
        indirectControls {
          id
          hazardControlConnectorId
          name
        }
        observed
        reason
        directControls {
          id
          hazardControlConnectorId
          name
        }
        limitedControls {
          id
          hazardControlConnectorId
          name
        }
        directControlDescription
        limitedControlDescription
      }
    }
  }
  additionalInformation
  historicIncidents
  details {
    departmentObserved {
      id
      name
    }
    opcoObserved {
      id
      name
      fullName
    }
    subopcoObserved {
      id
      name
      fullName
    }
    observationDate
    observationTime
    workLocation
    workOrderNumber
    workType {
      id
      name
    }
  }
  gpsCoordinates {
    latitude
    longitude
  }
  highEnergyTasks {
    id
    name
    activityName
    activityId
    instanceId
    taskHazardConnectorId
    hazards {
      id
      hazardControlConnectorId
      taskHazardConnectorId
      name
      description
      energyLevel
      directControlsImplemented
      indirectControls {
        id
        hazardControlConnectorId
        name
      }
      observed
      reason
      directControls {
        id
        hazardControlConnectorId
        name
      }
      limitedControls {
        id
        hazardControlConnectorId
        name
      }
      directControlDescription
      limitedControlDescription
    }
  }
  personnel {
    id
    name
    role
  }
  summary {
    viewed
  }
  photos {
    id
    category
    crc32c
    date
    displayName
    exists
    md5
    mimetype
    name
    signedUrl
    size
    time
    url
  }
  sourceInfo {
    sourceInformation
    appVersion
  }
}
    `;
export const JsbContentsFragmentDoc = gql`
    fragment JsbContents on JobSafetyBriefingLayout {
  controlAssessmentSelections {
    hazardId
    controlIds
    controlSelections {
      id
      selected
      recommended
    }
  }
  emergencyContacts {
    name
    phoneNumber
    primary
  }
  jsbId
  jsbMetadata {
    briefingDateTime
  }
  nearestMedicalFacility {
    description
    address
    city
    distanceFromJob
    phoneNumber
    state
    zip
  }
  customNearestMedicalFacility {
    address
  }
  aedInformation {
    location
  }
  activities {
    name
    tasks {
      id
    }
  }
  taskSelections {
    id
    fromWorkOrder
  }
  recommendedTaskSelections {
    id
    fromWorkOrder
    recommended
    selected
  }
  workLocation {
    address
    city
    description
    state
    operatingHq
  }
  gpsCoordinates {
    latitude
    longitude
  }
  workProcedureSelections {
    id
    values
  }
  otherWorkProcedures
  energySourceControl {
    arcFlashCategory
    clearancePoints
    ewp {
      id
      metadata {
        completed
        issued
        issuedBy
        procedure
        receivedBy
        remote
      }
      equipmentInformation {
        circuitBreaker
        switch
        transformer
      }
      referencePoints
    }
    transferOfControl
    voltages {
      type
      unit
      valueStr
    }
  }
  siteConditionSelections {
    id
    recommended
    selected
  }
  criticalRiskAreaSelections {
    name
  }
  crewSignOff {
    name
    type
    externalId
    signature {
      id
      name
      displayName
      size
      url
      signedUrl
    }
    employeeNumber
    jobTitle
  }
  hazardsAndControlsNotes
  photos {
    id
    category
    crc32c
    date
    displayName
    exists
    md5
    mimetype
    name
    signedUrl
    size
    time
    url
  }
  sourceInfo {
    sourceInformation
    appVersion
  }
  documents {
    id
    category
    crc32c
    date
    displayName
    exists
    md5
    mimetype
    name
    signedUrl
    size
    time
    url
  }
  groupDiscussion {
    viewed
  }
}
    `;
export const JsbDataFragmentDoc = gql`
    fragment JsbData on JobSafetyBriefing {
  id
  updatedAt
  workPackage {
    id
    locations {
      name
    }
  }
  contents {
    ...JsbContents
  }
  createdBy {
    id
    name
  }
  completedBy {
    id
  }
  createdAt
}
    ${JsbContentsFragmentDoc}`;
export const ActivitiesDocument = gql`
    query Activities($projectLocationId: UUID) {
  projectLocations(id: $projectLocationId) {
    activities {
      id
      name
      status
      tasks {
        id
        name
        riskLevel
        status
        libraryTask {
          id
        }
      }
      startDate
      endDate
    }
  }
}
    `;
export const CreateActivityDocument = gql`
    mutation CreateActivity($activityData: CreateActivityInput!) {
  createActivity(activityData: $activityData) {
    id
    location {
      id
    }
  }
}
    `;
export const RemoveTasksFromActivityDocument = gql`
    mutation RemoveTasksFromActivity($id: UUID!, $taskIds: RemoveActivityTasksInput!) {
  removeTasksFromActivity(id: $id, taskIdsToBeRemoved: $taskIds) {
    id
    name
    tasks {
      id
      name
    }
  }
}
    `;
export const AddTasksToActivityDocument = gql`
    mutation AddTasksToActivity($id: UUID!, $newTasks: AddActivityTasksInput!) {
  addTasksToActivity(id: $id, newTasks: $newTasks) {
    id
    name
    tasks {
      id
      name
    }
  }
}
    `;
export const DeleteActivityDocument = gql`
    mutation DeleteActivity($id: UUID!) {
  deleteActivity(id: $id)
}
    `;
export const CrewLeadersDocument = gql`
    query CrewLeaders {
  crewLeaders {
    id
    name
  }
}
    `;
export const EboDocument = gql`
    query Ebo($id: UUID!) {
  energyBasedObservation(id: $id) {
    completedAt
    createdAt
    id
    createdBy {
      id
      firstName
      lastName
      name
    }
    completedBy {
      id
    }
    status
    contents {
      ...EboContents
    }
    updatedAt
  }
  me {
    role
  }
}
    ${EboContentsFragmentDoc}`;
export const SaveEboDocument = gql`
    mutation SaveEbo($energyBasedObservationInput: EnergyBasedObservationInput!, $id: UUID) {
  saveEnergyBasedObservation(
    energyBasedObservationInput: $energyBasedObservationInput
    id: $id
  ) {
    id
    createdBy {
      id
      firstName
      lastName
      name
    }
    status
    contents {
      ...EboContents
    }
  }
}
    ${EboContentsFragmentDoc}`;
export const CompleteEboDocument = gql`
    mutation CompleteEbo($id: UUID!, $energyBasedObservationInput: EnergyBasedObservationInput!) {
  completeEnergyBasedObservation(
    id: $id
    energyBasedObservationInput: $energyBasedObservationInput
  ) {
    id
    createdBy {
      id
      firstName
      lastName
      name
    }
    status
    contents {
      ...EboContents
    }
  }
}
    ${EboContentsFragmentDoc}`;
export const ReopenEboDocument = gql`
    mutation ReopenEbo($id: UUID!) {
  reopenEnergyBasedObservation(id: $id) {
    id
    createdBy {
      id
      firstName
      lastName
      name
    }
    status
    contents {
      ...EboContents
    }
  }
}
    ${EboContentsFragmentDoc}`;
export const DeleteEboDocument = gql`
    mutation DeleteEbo($id: UUID!) {
  deleteEnergyBasedObservation(id: $id)
}
    `;
export const HistoricalIncidentsDocument = gql`
    query HistoricalIncidents($libraryTaskId: UUID!) {
  historicalIncidents(libraryTaskId: $libraryTaskId) {
    id
    severity
    incidentDate
    taskTypeId
    taskType
    severityCode
    incidentType
    incidentId
    description
  }
}
    `;
export const FileUploadPoliciesDocument = gql`
    mutation FileUploadPolicies($count: Int!) {
  fileUploadPolicies(count: $count) {
    id
    url
    signedUrl
    fields
  }
}
    `;
export const HazardsLibraryDocument = gql`
    query HazardsLibrary($type: LibraryFilterType!, $libraryTaskId: UUID, $librarySiteConditionId: UUID, $orderBy: [OrderBy!]) {
  hazardsLibrary(
    type: $type
    libraryTaskId: $libraryTaskId
    librarySiteConditionId: $librarySiteConditionId
    orderBy: $orderBy
  ) {
    id
    name
    isApplicable
    controls {
      id
      name
      isApplicable
      controlType
    }
    energyType
    energyLevel
    imageUrl
    taskApplicabilityLevels {
      applicabilityLevel
      taskId
    }
  }
}
    `;
export const JsbDocument = gql`
    query Jsb($id: UUID!) {
  jobSafetyBriefing(id: $id) {
    ...JsbData
  }
  me {
    role
  }
}
    ${JsbDataFragmentDoc}`;
export const SaveJsbDocument = gql`
    mutation SaveJsb($input: SaveJobSafetyBriefingInput!) {
  saveJobSafetyBriefing(jobSafetyBriefingInput: $input) {
    ...JsbData
  }
}
    ${JsbDataFragmentDoc}`;
export const CompleteJsbDocument = gql`
    mutation CompleteJsb($input: SaveJobSafetyBriefingInput!) {
  completeJobSafetyBriefing(jobSafetyBriefingInput: $input) {
    ...JsbData
  }
}
    ${JsbDataFragmentDoc}`;
export const DeleteJsbDocument = gql`
    mutation DeleteJsb($id: UUID!) {
  deleteJobSafetyBriefing(id: $id)
}
    `;
export const ReopenJsbDocument = gql`
    mutation ReopenJsb($id: UUID!) {
  reopenJobSafetyBriefing(id: $id) {
    ...JsbData
  }
}
    ${JsbDataFragmentDoc}`;
export const LastAddedAdhocJobSafetyBriefingDocument = gql`
    query LastAddedAdhocJobSafetyBriefing {
  lastAddedAdhocJobSafetyBriefing {
    contents {
      workLocation {
        address
        operatingHq
      }
      nearestMedicalFacility {
        address
        description
        city
        distanceFromJob
        phoneNumber
        state
        zip
      }
      aedInformation {
        location
      }
      emergencyContacts {
        name
        phoneNumber
        primary
      }
    }
  }
}
    `;
export const LastAddedJobSafetyBriefingDocument = gql`
    query LastAddedJobSafetyBriefing($projectLocationId: UUID, $filterOn: JSBFiltersOnEnum!) {
  lastAddedJobSafetyBriefing(
    filterOn: $filterOn
    projectLocationId: $projectLocationId
  ) {
    contents {
      workLocation {
        address
        description
      }
      nearestMedicalFacility {
        address
        description
        city
        distanceFromJob
        phoneNumber
        state
        zip
      }
      aedInformation {
        location
      }
      emergencyContacts {
        name
        phoneNumber
        primary
      }
    }
  }
}
    `;
export const LocationSiteConditionsDocument = gql`
    query LocationSiteConditions($siteInput: SiteLocationInput!) {
  locationSiteConditions(siteInput: $siteInput) {
    id
    name
    librarySiteCondition {
      id
    }
  }
}
    `;
export const NearestMedicalFacilitiesDocument = gql`
    query NearestMedicalFacilities($latitude: Decimal!, $longitude: Decimal!) {
  nearestMedicalFacilities(latitude: $latitude, longitude: $longitude) {
    description
    address
    city
    distanceFromJob
    phoneNumber
    state
    zip
  }
}
    `;
export const ProjectLocationsDocument = gql`
    query ProjectLocations($id: UUID, $date: Date) {
  projectLocations(id: $id) {
    id
    name
    project {
      id
      name
      description
    }
    activities(date: $date) {
      id
      name
      status
      tasks {
        id
        name
        riskLevel
        status
        libraryTask {
          id
        }
      }
      startDate
      endDate
    }
    address
    jobSafetyBriefings {
      id
      name
      status
      completedAt
      completedBy {
        id
        name
      }
    }
    latitude
    longitude
    riskLevel
    tasks(date: $date) {
      id
      name
      riskLevel
      status
      libraryTask {
        id
      }
    }
    siteConditions(date: $date) {
      id
      name
      librarySiteCondition {
        id
      }
    }
  }
}
    `;
export const RegionsLibraryDocument = gql`
    query RegionsLibrary {
  regionsLibrary {
    id
    name
  }
}
    `;
export const SiteConditionsLibraryDocument = gql`
    query SiteConditionsLibrary {
  siteConditionsLibrary(allowArchived: true) {
    id
    name
    archivedAt
    hazards {
      id
      name
      isApplicable
      energyLevel
      taskApplicabilityLevels {
        applicabilityLevel
        taskId
      }
      controls {
        id
        name
        isApplicable
        ppe
      }
    }
  }
}
    `;
export const SiteConditionsDocument = gql`
    query SiteConditions($locationId: UUID, $date: Date) {
  siteConditions(locationId: $locationId, date: $date) {
    id
    name
    librarySiteCondition {
      id
    }
  }
}
    `;
export const CreateSiteConditionDocument = gql`
    mutation CreateSiteCondition($siteConditionData: CreateSiteConditionInput!) {
  createSiteCondition(data: $siteConditionData) {
    id
    location {
      id
    }
  }
}
    `;
export const TasksDocument = gql`
    query Tasks($tasksId: UUID, $locationId: UUID, $date: Date) {
  tasks(id: $tasksId, locationId: $locationId, date: $date) {
    id
    name
  }
}
    `;
export const TasksLibraryDocument = gql`
    query TasksLibrary($tasksLibraryId: [UUID!], $orderBy: [LibraryTaskOrderBy!], $hazardsOrderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
  tasksLibrary(ids: $tasksLibraryId, orderBy: $orderBy) {
    id
    name
    riskLevel
    hespScore
    category
    workTypes {
      id
      name
    }
    hazards(orderBy: $hazardsOrderBy) {
      id
      name
      isApplicable
      controls(orderBy: $controlsOrderBy) {
        id
        name
        isApplicable
        ppe
      }
      energyType
      energyLevel
      taskApplicabilityLevels {
        applicabilityLevel
        taskId
      }
      archivedAt
    }
    activitiesGroups {
      id
      name
      tasks {
        id
      }
    }
  }
}
    `;
export const TenantLinkedHazardsLibraryDocument = gql`
    query TenantLinkedHazardsLibrary($type: LibraryFilterType, $libraryTaskId: UUID, $librarySiteConditionId: UUID, $orderBy: [OrderBy!]) {
  tenantLinkedHazardsLibrary(
    type: $type
    libraryTaskId: $libraryTaskId
    librarySiteConditionId: $librarySiteConditionId
    orderBy: $orderBy
  ) {
    id
    name
    isApplicable
    energyLevel
    energyType
    imageUrl
    taskApplicabilityLevels {
      applicabilityLevel
      taskId
    }
    controls {
      id
      name
      isApplicable
      controlType
      ppe
      archivedAt
    }
  }
}
    `;
export const WorkosDirectoryUsersDocument = gql`
    query WorkosDirectoryUsers($directoryIds: [String!]!) {
  workosDirectoryUsers(directoryIds: $directoryIds) {
    data {
      id
      idpId
      directoryId
      organizationId
      firstName
      lastName
      jobTitle
      username
      state
      customAttributes
      rawAttributes
      role
      slug
      createdAt
      updatedAt
    }
  }
}
    `;

export type SdkFunctionWrapper = <T>(action: (requestHeaders?:Record<string, string>) => Promise<T>, operationName: string, operationType?: string) => Promise<T>;


const defaultWrapper: SdkFunctionWrapper = (action, _operationName, _operationType) => action();

export function getSdk(client: GraphQLClient, withWrapper: SdkFunctionWrapper = defaultWrapper) {
  return {
    Activities(variables?: ActivitiesQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<ActivitiesQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<ActivitiesQuery>(ActivitiesDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'Activities', 'query');
    },
    CreateActivity(variables: CreateActivityMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<CreateActivityMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<CreateActivityMutation>(CreateActivityDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'CreateActivity', 'mutation');
    },
    RemoveTasksFromActivity(variables: RemoveTasksFromActivityMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<RemoveTasksFromActivityMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<RemoveTasksFromActivityMutation>(RemoveTasksFromActivityDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'RemoveTasksFromActivity', 'mutation');
    },
    AddTasksToActivity(variables: AddTasksToActivityMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<AddTasksToActivityMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<AddTasksToActivityMutation>(AddTasksToActivityDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'AddTasksToActivity', 'mutation');
    },
    DeleteActivity(variables: DeleteActivityMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<DeleteActivityMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<DeleteActivityMutation>(DeleteActivityDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'DeleteActivity', 'mutation');
    },
    CrewLeaders(variables?: CrewLeadersQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<CrewLeadersQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<CrewLeadersQuery>(CrewLeadersDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'CrewLeaders', 'query');
    },
    Ebo(variables: EboQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<EboQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<EboQuery>(EboDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'Ebo', 'query');
    },
    SaveEbo(variables: SaveEboMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<SaveEboMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<SaveEboMutation>(SaveEboDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'SaveEbo', 'mutation');
    },
    CompleteEbo(variables: CompleteEboMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<CompleteEboMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<CompleteEboMutation>(CompleteEboDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'CompleteEbo', 'mutation');
    },
    ReopenEbo(variables: ReopenEboMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<ReopenEboMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<ReopenEboMutation>(ReopenEboDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'ReopenEbo', 'mutation');
    },
    DeleteEbo(variables: DeleteEboMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<DeleteEboMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<DeleteEboMutation>(DeleteEboDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'DeleteEbo', 'mutation');
    },
    HistoricalIncidents(variables: HistoricalIncidentsQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<HistoricalIncidentsQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<HistoricalIncidentsQuery>(HistoricalIncidentsDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'HistoricalIncidents', 'query');
    },
    FileUploadPolicies(variables: FileUploadPoliciesMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<FileUploadPoliciesMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<FileUploadPoliciesMutation>(FileUploadPoliciesDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'FileUploadPolicies', 'mutation');
    },
    HazardsLibrary(variables: HazardsLibraryQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<HazardsLibraryQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<HazardsLibraryQuery>(HazardsLibraryDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'HazardsLibrary', 'query');
    },
    Jsb(variables: JsbQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<JsbQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<JsbQuery>(JsbDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'Jsb', 'query');
    },
    SaveJsb(variables: SaveJsbMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<SaveJsbMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<SaveJsbMutation>(SaveJsbDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'SaveJsb', 'mutation');
    },
    CompleteJsb(variables: CompleteJsbMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<CompleteJsbMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<CompleteJsbMutation>(CompleteJsbDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'CompleteJsb', 'mutation');
    },
    DeleteJsb(variables: DeleteJsbMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<DeleteJsbMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<DeleteJsbMutation>(DeleteJsbDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'DeleteJsb', 'mutation');
    },
    ReopenJsb(variables: ReopenJsbMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<ReopenJsbMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<ReopenJsbMutation>(ReopenJsbDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'ReopenJsb', 'mutation');
    },
    LastAddedAdhocJobSafetyBriefing(variables?: LastAddedAdhocJobSafetyBriefingQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<LastAddedAdhocJobSafetyBriefingQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<LastAddedAdhocJobSafetyBriefingQuery>(LastAddedAdhocJobSafetyBriefingDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'LastAddedAdhocJobSafetyBriefing', 'query');
    },
    LastAddedJobSafetyBriefing(variables: LastAddedJobSafetyBriefingQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<LastAddedJobSafetyBriefingQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<LastAddedJobSafetyBriefingQuery>(LastAddedJobSafetyBriefingDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'LastAddedJobSafetyBriefing', 'query');
    },
    LocationSiteConditions(variables: LocationSiteConditionsQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<LocationSiteConditionsQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<LocationSiteConditionsQuery>(LocationSiteConditionsDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'LocationSiteConditions', 'query');
    },
    NearestMedicalFacilities(variables: NearestMedicalFacilitiesQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<NearestMedicalFacilitiesQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<NearestMedicalFacilitiesQuery>(NearestMedicalFacilitiesDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'NearestMedicalFacilities', 'query');
    },
    ProjectLocations(variables?: ProjectLocationsQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<ProjectLocationsQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<ProjectLocationsQuery>(ProjectLocationsDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'ProjectLocations', 'query');
    },
    RegionsLibrary(variables?: RegionsLibraryQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<RegionsLibraryQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<RegionsLibraryQuery>(RegionsLibraryDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'RegionsLibrary', 'query');
    },
    SiteConditionsLibrary(variables?: SiteConditionsLibraryQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<SiteConditionsLibraryQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<SiteConditionsLibraryQuery>(SiteConditionsLibraryDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'SiteConditionsLibrary', 'query');
    },
    SiteConditions(variables?: SiteConditionsQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<SiteConditionsQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<SiteConditionsQuery>(SiteConditionsDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'SiteConditions', 'query');
    },
    CreateSiteCondition(variables: CreateSiteConditionMutationVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<CreateSiteConditionMutation> {
      return withWrapper((wrappedRequestHeaders) => client.request<CreateSiteConditionMutation>(CreateSiteConditionDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'CreateSiteCondition', 'mutation');
    },
    Tasks(variables?: TasksQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<TasksQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<TasksQuery>(TasksDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'Tasks', 'query');
    },
    TasksLibrary(variables?: TasksLibraryQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<TasksLibraryQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<TasksLibraryQuery>(TasksLibraryDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'TasksLibrary', 'query');
    },
    TenantLinkedHazardsLibrary(variables?: TenantLinkedHazardsLibraryQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<TenantLinkedHazardsLibraryQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<TenantLinkedHazardsLibraryQuery>(TenantLinkedHazardsLibraryDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'TenantLinkedHazardsLibrary', 'query');
    },
    WorkosDirectoryUsers(variables: WorkosDirectoryUsersQueryVariables, requestHeaders?: Dom.RequestInit["headers"]): Promise<WorkosDirectoryUsersQuery> {
      return withWrapper((wrappedRequestHeaders) => client.request<WorkosDirectoryUsersQuery>(WorkosDirectoryUsersDocument, variables, {...requestHeaders, ...wrappedRequestHeaders}), 'WorkosDirectoryUsers', 'query');
    }
  };
}
export type Sdk = ReturnType<typeof getSdk>;