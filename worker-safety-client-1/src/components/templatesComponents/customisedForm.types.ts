import type { FieldProps } from "@/components/shared/field/Field";
import type { InputProps as AllInputProps } from "@/components/shared/input/Input";
import type { FileInputsCWF } from "@/types/natgrid/jobsafetyBriefing";
import type { LibrarySiteCondition } from "@/types/siteCondition/LibrarySiteCondition";
import type { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import type { IconName } from "@urbint/silica";
import type { PropsWithChildren, ReactNode } from "react";
import type { CheckboxOption } from "../checkboxGroup/CheckboxGroup";
import type { RiskLevel } from "../riskBadge/RiskLevel";
import type { HexColor } from "../shared/inputSelect/InputSelect";
import type { ModalProps } from "../shared/modal/Modal";
import type { SelectPrimaryOption } from "../shared/select/selectPrimary/SelectPrimary";

export type DownloadResult = "success" | "error" | "aborted";

export enum CWFItemType {
  Page = "page",
  SubPage = "sub_page",
  Section = "section",
  Choice = "choice",
  Dropdown = "dropdown",
  Contractor = "contractor",
  Region = "region",
  InputPhoneNumber = "input_phone_number",
  YesOrNo = "yes_or_no",
  InputText = "input_text",
  Slide = "slide",
  InputDateTime = "input_date_time",
  ReportDate = "report_date",
  InputNumber = "input_number",
  InputLocation = "input_location",
  InputEmail = "input_email",
  RichTextEditor = "rich_text_editor",
  HazardsAndControls = "hazards_and_controls",
  ActivitiesAndTasks = "activities_and_tasks",
  Attachment = "attachment",
  Summary = "summary",
  SiteConditions = "site_conditions",
  DocumentAttachments = "document_attachments",
  PhotoAttachments = "photo_attachments",
  Location = "location",
  NearestHospital = "nearest_hospital",
  PersonnelComponent = "personnel_component",
  Checkbox = "checkbox",
}

export type PageType = {
  id: string;
  type: string;
  order: number;
  parentId?: string;
  properties: {
    title: string;
    description: string;
    page_update_status: Status;
    include_in_summary: boolean;
  };
  contents: any[];
};

export type UploadItem = {
  id: string;
  displayName: string;
  name: string;
  size: string;
  date: string;
  time: string;
  lastModified?: string | null;
  category?: string | null;
  url: string;
  signedUrl: string;
  description?: string;
};

export type CWFDocumentItemProps = {
  document: UploadItem;
  readOnly?: boolean;
  onEdit: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onDownload: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onDelete: (event: React.MouseEvent<HTMLButtonElement>) => void;
};

export type PageIteratorType = PageType & {
  parentId?: string;
};

export type FormElementsType = {
  id: string;
  type: string;
  order: number;
  properties: any;
  contents: any[];
};

export type ModeTypePageSection =
  | "default"
  | "addPage"
  | "addSubPage"
  | "deletePage"
  | "editPage"
  | "dragPage";

export type Status =
  | "default"
  | "current"
  | "saved"
  | "saved_current"
  | "error";

export type AddPageListItemProps = {
  newPageTitle: string;
  setNewPageTitle: (item: string) => void;
  status?: Status;
};

export type TemplateSettings = {
  availability: {
    adhoc: {
      selected: boolean;
    };
    work_package: {
      selected: boolean;
    };
  };
  edit_expiry_days: number;
  report_date?: {
    required: boolean;
    field_id: string;
    field_path?: string;
  };
  work_types?: WorkTypes[];
  copy_and_rebrief?: {
    is_copy_enabled?: boolean;
    is_rebrief_enabled?: boolean;
  };
  maximum_widgets?: number;
  widgets_added?: number;
};

export type WorkTypes = {
  id: string;
  name: string;
};

export type SupervisorTypes = {
  id: string;
  name: string;
  email: string;
};

export type TemplateMetaData = {
  work_package?: {
    name?: string;
    id?: string;
  };
  work_types?: WorkTypes[];
  location?: {
    name?: string;
    id?: string;
  };
  startDate?: string;
  endDate?: string;
  is_activities_and_tasks_included?: boolean;
  is_hazards_and_controls_included?: boolean;
  is_report_date_included?: boolean;
  is_contractor_included?: boolean;
  is_summary_included?: boolean;
  is_site_conditions_included?: boolean;
  is_energy_wheel_enabled?: boolean;
  is_location_included?: boolean;
  is_nearest_hospital_included?: boolean;
  is_region_included?: boolean;
  region?: {
    name?: string;
    id?: string;
  };
  supervisor?: SupervisorTypes[];
  copy_and_rebrief?: {
    is_copy_enabled?: boolean;
    is_rebrief_enabled?: boolean;
    copy_linked_form_id?: string;
    rebrief_linked_form_id?: string;
  };
};

export type FormType = {
  id: string;
  type: string;
  order?: number;
  metadata?: TemplateMetaData;
  created_at?: string | null;
  created_by?: {
    id: string;
  } | null;
  updated_by?: string | null;
  updated_at?: string | null;
  archived_by?: string | null;
  archived_at?: string | null;
  published_by?: string | null;
  edit_expiry_days?: number | null;
  edit_expiry_time?: string | null;
  is_archived?: boolean;
  version?: number;
  published_at?: string;
  is_latest_version?: boolean | null;
  properties: {
    id?: string;
    title: string;
    status: string;
    description: string;
    report_start_date?: string;
    template_unique_id?: string;
  };
  contents: PageType[];
  template_id?: string;
  settings: TemplateSettings;
  isDisabled: boolean;
  component_data?: {
    activities_tasks?: SelectedActivity[];
    hazards_controls?: HazardControl;
    site_conditions?: SiteCondition[];
    location_data?: LocationUserValueType;
    nearest_hospital?: NearestHospitalUserValueType;
  };
  pre_population_rule_paths?: PrePopulationRulePaths;
  work_package_data?: WorkPackageData;
};

export type HazardControl = {
  tasks?: Hazards[];
  manually_added_hazards?: Hazards[];
  site_conditions?: Hazards[];
};

export type ActivePageType = {
  id: string;
  parentId: string;
  type: string;
  returnToSummaryPage?: boolean;
  summaryPageId?: string;
};

export type WorkPackageData = {
  workPackageName?: string | null;
  locationName?: string | null;
  region?: {
    id: string;
    name: string;
  } | null;
  startDate?: string;
  endDate?: string;
};

export type ActivePageObjType = ActivePageType | null;

export type WidgetType = {
  id: string;
  parentDetails: ActivePageType;
} | null;

export type PageVarietyType = "page" | "sub_page";

export type PageContentType =
  | PageType
  | AllQuestionTypes
  | SectionQuestionHolder;
export type SubPageContentType = AllQuestionTypes | SectionQuestionHolder;

export type AddPagePayloadType = {
  id: string;
  type: PageVarietyType;
  order: number;
  properties: {
    title: string;
    description: string;
    page_update_status: Status;
    include_in_summary: boolean;
  };
  contents: PageContentType[];
};

export type AddSubpagePayloadType = {
  parentPage: string;
  subpageDetails: {
    id: string;
    type: PageVarietyType;
    order: number;
    properties: {
      title: string;
      description: string;
      page_update_status: Status;
      include_in_summary: boolean;
    };
    contents: AllQuestionTypes[];
  };
};

export type AddSectionPayloadType = {
  parentData: ActivePageObjType;
  sectionData: SectionData;
};

export type SectionData = {
  id: string;
  type: CWFItemType.Section;
  order: number;
  properties: {
    title: string;
    is_repeatable?: boolean;
    child_instance?: boolean;
    include_in_summary?: boolean;
  };
  contents: SubPageContentType[];
};

export type AddFieldPayloadType = {
  parentData: ActivePageObjType;
  fieldData: AllQuestionTypes;
};

export type AddSectionFieldPayloadType = {
  parentData: ActivePageObjType;
  fieldData: AllQuestionTypes;
  section: {
    id: string;
    type: any;
    order: any;
    properties: any;
    contents: any;
  };
};

export type EditSectionFieldPayloadType = {
  parentData: ActivePageObjType;
  sectionId: string;
  updatedProperties: {
    [key: string]: EditSectionFieldPayloadType;
  };
};

export type DeleteFieldPayloadType = {
  parentData: ActivePageObjType;
  fieldData: { order: number };
  section: SectionQuestionHolder | null;
};

export type AddFieldCommentPayloadType = {
  parentData: ActivePageObjType;
  fieldData: { comment: string; order: number };
  section: SectionQuestionHolder | null;
};

export type AddFieldAttachmentsPayloadType = {
  parentData: ActivePageObjType;
  fieldData: { attachments: File[]; order: number };
  section: SectionQuestionHolder | null;
};

export type DeletePagePayloadType = {
  parentPage: string;
  id: string;
  title: string;
  type: string;
};

export type FieldValueChangePayloadType = {
  parentData: ActivePageObjType;
  fieldData: { user_value: userValueForQuestionsType; order: number };
  section: SectionQuestionHolder | null;
};

export type DeleteSectionPayloadType = {
  parentId: string;
  subPageId: string;
  pageContents: PageContentType[];
};

export type BulkDeletePagePayloadType = {
  deletePageDetails: DeletePageDetails;
};

export type FormComponentVarietyType =
  | "ACTIVITIES_AND_TASKS"
  | "SITE_CONDITIONS"
  | "HAZARDS_AND_CONTROLS"
  | "PHOTO_ATTACHMENTS"
  | "DOCUMENT_ATTACHMENTS"
  | "SUMMARY"
  | "LOCATION"
  | "NEAREST_HOSPITAL";

export type FormAttachmentsPropertiesType = {
  title: string;
  attachment_type: AttachmentTypes;
  attachments_max_count: number;
  description: string;
  user_value: SubmissionPhotoType[];
};

export type ActivitiesAndTasksPropertiesType = {
  title: string;
  description: string;
  user_value: [];
};
export type HazardsAndControlsPropertiesType = {
  title: string;
  description: string;
  user_value: [];
  sub_title: string;
};

export type EnergyAndHazardsProps = {
  readOnly?: boolean;
  preSelectedHazards?: HazardControl;
  isSummaryView?: boolean;
  subTitle: string;
};

export type AttachmentTypes = "photo" | "document";

//TODO find a way to accomodate payloadTypes for all the components
export type FormComponentPayloadType = {
  id: string;
  order: number;
  type: FormComponentVarietyType;
  is_mandatory: boolean;
  properties: FormAttachmentsPropertiesType;
  contents: [];
};

export type ReferenceContentType = {
  properties: {
    title: string;
    is_mandatory: boolean;
    hint_text?: string;
    api_details: ApiDetails;
    user_value: string[] | null;
  };
};

export type ActivitiesAndTasksFormType = {
  id: string;
  order: number;
  type: FormComponentVarietyType;
  is_mandatory: boolean;
  properties: ActivitiesAndTasksPropertiesType;
  contents: [];
};
export type HazardsAndControlsFormType = {
  id: string;
  order: number;
  type: FormComponentVarietyType;
  is_mandatory: boolean;
  properties: HazardsAndControlsPropertiesType;
  contents: [];
};

export type FormComponentActionPayloadType = {
  parentData: ActivePageObjType;
  fieldData: FormComponentPayloadType;
};

export type DocumentAttachmentsType = {
  type: "DOCUMENT_ATTACHMENTS";
  imageBlob: Blob;
  description: string;
};

export type CommonAction =
  | { type: typeof CF_REDUCER_CONSTANTS.ADD_PAGE; payload: AddPagePayloadType }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ADD_SUBPAGE;
      payload: AddSubpagePayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ADD_SECTION;
      payload: AddSectionPayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ADD_FIELD;
      payload: AddFieldPayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ADD_SECTION_FIELD;
      payload: AddSectionFieldPayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.EDIT_SECTION_FIELD;
      payload: any;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.SWITCH_CONTENT_ORDERS;
      payload: {
        parent: ActivePageType;
        updatedContents: FormElementsType[];
      };
    }
  | { type: typeof CF_REDUCER_CONSTANTS.EDIT_FIELD; payload: any } // need to check this broadly
  | {
      type: typeof CF_REDUCER_CONSTANTS.DELETE_FIELD;
      payload: DeleteFieldPayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ADD_FIELD_COMMENT;
      payload: AddFieldCommentPayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ADD_FIELD_ATTACHMENTS;
      payload: AddFieldAttachmentsPayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.DELETE_PAGE;
      payload: DeletePagePayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.DELETE_SUBPAGE;
      payload: DeletePagePayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.FIELD_VALUE_CHANGE;
      payload: FieldValueChangePayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.CHANGE_BUILDER_MODE;
      payload: FormBuilderModeProps;
    }
  | { type: typeof CF_REDUCER_CONSTANTS.FORM_NAME_CHANGE; payload: string }
  | {
      type: typeof CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE;
      payload: FormType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.DELETE_SECTION;
      payload: DeleteSectionPayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.BULK_DELETE_PAGE;
      payload: DeletePageDetails[];
    }
  | { type: typeof CF_REDUCER_CONSTANTS.PAGE_DRAG; payload: PageType[] }
  | { type: typeof CF_REDUCER_CONSTANTS.PAGE_TITLE_EDIT; payload: PageType[] }
  | {
      type: typeof CF_REDUCER_CONSTANTS.PAGE_SUMMARY_VISIBILITY_TOGGLE;
      payload: PageType[];
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.SUBPAGE_SUMMARY_VISIBILITY_TOGGLE;
      payload: PageType[];
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ADD_COMPONENTS;
      payload: FormComponentActionPayloadType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ATTACHMENTS_VALUE_CHANGE;
      payload: any;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ACTIVITIES_VALUE_CHANGE;
      payload: SelectedActivity[];
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.ENERGY_HAZARDS_VALUE_CHANGE;
      payload: Hazards[];
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.PAGE_STATUS_CHANGE;
      payload: PageType[];
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.BUTTON_DISABLE_STATUS_CHANGE;
      payload: boolean;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.CHANGE_WORK_PACKAGE_DATA;
      payload: WorkPackageData;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.SET_FORM_STATE;
      payload: boolean;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.SET_TASKS_HAZARD_DATA;
      payload: Task[];
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.SITE_CONDITIONS_VALUE_CHANGE;
      payload: SiteCondition[];
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.LOCATION_VALUE_CHANGE;
      payload: LocationUserValueType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE;
      payload: NearestHospitalUserValueType;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.SET_SITE_CONDITIONS_HAZARD_DATA;
      payload: Hazards[];
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.PERSONNEL_COMPONENT_ADD_DATA;
      payload: PersonnelComponentAddPayload;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.PERSONNEL_COMPONENT_REMOVE_DATA;
      payload: {
        componentId: string;
        rowId: string;
      };
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.RESET_PAGE;
      payload: string;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.SET_FORM_VALIDITY;
      payload: boolean;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.UPDATE_METADATA;
      payload: TemplateMetaData;
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.UPDATE_HISTORICAL_INCIDENT;
      payload: {
        componentId?: string;
        incident: HistoricalIncident | null;
      };
    }
  | {
      type: typeof CF_REDUCER_CONSTANTS.UPDATE_WIDGET_SETTINGS;
      payload: {
        maximum_widgets?: number;
        widgets_added?: number;
      };
    };

export type FormBuilderModeProps = "BUILD" | "PREVIEW";

export type UserFormMode = "EDIT" | "BUILD" | "PREVIEW" | "PREVIEW_PROPS";

export type FieldTypes =
  | "choice"
  | "dropdown"
  | "yes_or_no"
  | "input_text"
  | "input_phone_number"
  | "slide"
  | "input_date_time"
  | "input_number"
  | "input_location"
  | "input_email"
  | "report_date"
  | "contractor"
  | "region"
  | "checkbox";

export type userValueForQuestionsType =
  | string
  | string[]
  | boolean
  | number
  | UserLocationLatAndLongValue
  | LocationUserValueType
  | null;

type BaseQuestionPropertiesType = {
  title: string;
  is_mandatory: boolean;
  comments_allowed: boolean;
  attachments_allowed: boolean;
  include_in_widget: boolean;
  user_comments: string | null;
  user_attachments: File[] | null;
};

type ResponseOptionProperties = {
  response_option: ResponseOption | null;
  include_other_option?: boolean;
  include_NA_option?: boolean;
};

// Base for questions with hint text and validation
type HintAndValidation = {
  hint_text?: string;
  validation?: string[];
};

type BaseQuestionType<T> = {
  type: FieldTypes; // This will be overridden in each specific question type
  id: string;
  order: number;
  properties: T;
};

// Choice Question

export type ChoiceType = "single_choice" | "multiple_choice";
export type ResponseOption =
  | "manual_entry"
  | "fetch"
  | "fetch_from_imported_data"
  | "image";
export type ChoiceOption = {
  value: string;
  label: string;
  image_url?: string;
};
export type ChoiceFormState = BaseQuestionPropertiesType &
  ResponseOptionProperties & {
    choice_type: ChoiceType;
    options: ChoiceOption[];
    user_value: string[] | null;
    pre_population_rule_name?: PrePopulationOptionType;
  };

export type ChoiceQuestionType = BaseQuestionType<ChoiceFormState> & {
  type: "choice";
};

//Dropdown
export type DropDownOptionType = {
  value: string;
  label: string;
};

export type DropdownPropertiesType = BaseQuestionPropertiesType &
  ResponseOptionProperties & {
    hint_text: string;
    options: DropDownOptionType[];
    multiple_choice: boolean;
    user_value: string[] | null;
    pre_population_rule_name?: PrePopulationOptionType;
    returnLabelAndValue?: boolean;
    // Fields for imported data source configuration
    data_source_id?: string;
    data_source_name?: string;
    data_source_column?: string;
    api_details?: FetchFromSourceApiDetails;
  };

export type DropDownQuestionType = BaseQuestionType<DropdownPropertiesType> & {
  type: "dropdown";
};

//yes or no question type

type toggleStyle = "text" | "simple" | "thums";
type toggleOptions = {
  label: string;
  value: boolean;
};

type YesOrNoPropertiesType = Omit<BaseQuestionPropertiesType, "user_value"> & {
  hint_text: string;
  toggle_style: toggleStyle;
  toggle_options: toggleOptions[];
  user_value: boolean | null;
  pre_population_rule_name?: PrePopulationOptionType;
};

export type YesOrNoQuestionType = BaseQuestionType<YesOrNoPropertiesType> & {
  type: "yes_or_no";
};

//input_text

export type InputResponseOption =
  | "alphanumeric"
  | "allow_special_characters"
  | "regex";

export type TextInputFormat = "short_text" | "long_text";

export type InputTextPropertiesType = Omit<
  BaseQuestionPropertiesType,
  | "response_option"
  | "include_other_option"
  | "include_NA_option"
  | "defaultValue"
  | "user_value"
> &
  HintAndValidation & {
    response_option: InputResponseOption | null;
    user_value: string | null;
    input_type: TextInputFormat;
    sub_label: string;
    placeholder: string;
    validation: string[];
    pre_population_rule_name?: PrePopulationOptionType;
  };

export type InputTextQuestionType =
  BaseQuestionType<InputTextPropertiesType> & {
    type: "input_text";
  };

//input_phone_number

type InputPhoneNumberResponseOption = "auto_populate" | "manual_input";

export type InputPhoneNumberPropertiesType = Omit<
  BaseQuestionPropertiesType,
  | "include_other_option"
  | "include_NA_option"
  | "response_option"
  | "user_value"
> & {
  response_option: InputPhoneNumberResponseOption | null;
  defaultValue?: string;
  user_value: string | null;
  pre_population_rule_name?: PrePopulationOptionType;
};

export type InputPhoneNumberQuestionType =
  BaseQuestionType<InputPhoneNumberPropertiesType> & {
    type: "input_phone_number";
  };

//input_date_time

type DateResponseType =
  | "manual_input"
  | "auto_populate_current_date"
  | "calendar";

type TimeResponseType = "auto_populate_current_time" | "manual_input";

type Option = "date_time" | "date_only" | "time_only";

type DateType = "single_date" | "date_range";

type Validation = "allow_future_date" | "allow_past_date";

type ValidationTime = "allow_future_time" | "allow_past_time";

export type InputDateAndTimePropertiesType = Omit<
  BaseQuestionPropertiesType,
  | "response_option"
  | "include_other_option"
  | "include_NA_option"
  | "defaultValue"
  | "user_value"
> &
  HintAndValidation & {
    selected_type: Option;
    date_response_type: DateResponseType;
    date_options: DateType;
    date_type: DateType;
    date_validation?: Validation;
    time_validation?: ValidationTime;
    time_response_type: TimeResponseType;
    user_value: string | null;
    pre_population_rule_name?: PrePopulationOptionType;
  };

export type InputDateAndTimeQuestionType =
  BaseQuestionType<InputDateAndTimePropertiesType> & {
    type: "input_date_time" | "report_date";
  };

//input_number

type InputNumberResponseOption = "allowNegativeNumbers" | "allowDecimals";

export type InputNumberPropertiesType = Omit<
  BaseQuestionPropertiesType,
  | "response_option"
  | "include_other_option"
  | "include_NA_option"
  | "defaultValue"
  | "user_value"
> &
  HintAndValidation & {
    response_option: InputNumberResponseOption | null;
    hint_text: string;
    description: string;
    unit_name: string;
    display_units: boolean;
    user_value: number | null;
    pre_population_rule_name?: PrePopulationOptionType;
  };

export type InputNumberQuestionType =
  BaseQuestionType<InputNumberPropertiesType> & {
    type: "input_number";
  };
//input_location

type InputLocationResponseOptionType =
  | "google_api_search"
  | "manual_address_input"
  | "lat_lon"
  | "auto_populate_current_location";

export type UserLocationLatAndLongValue = {
  latitude?: string;
  longitude?: string;
};

export type UserLocationValue = {
  name?: string;
  gps_coordinates?: {
    latitude?: string;
    longitude?: string;
  };
};

export type InputLocationPropertiesType = Omit<
  BaseQuestionPropertiesType,
  | "response_option"
  | "include_other_option"
  | "include_NA_option"
  | "defaultValue"
  | "user_value"
  | "user_comments"
> & {
  response_option: InputLocationResponseOptionType | null;
  validation: string[];
  user_value: string | UserLocationLatAndLongValue | null;
  user_comments: string[] | null;
  pre_population_rule_name?: PrePopulationOptionType;
  is_show_map_preview?: boolean;
};

export type InputLocationQuestionType =
  BaseQuestionType<InputLocationPropertiesType> & {
    type: "input_location";
  };

//input_email

type EmailResponseOption = "manual_input" | "auto_populate_user_email";

export type InputEmailQuestionPropertiesType = Omit<
  BaseQuestionPropertiesType,
  | "response_option"
  | "include_other_option"
  | "include_NA_option"
  | "defaultValue"
  | "user_value"
> & {
  response_option: EmailResponseOption | null;
  validation: string[];
  user_value: string | null;
  pre_population_rule_name?: PrePopulationOptionType;
};

export type InputEmailQuestionType =
  BaseQuestionType<InputEmailQuestionPropertiesType> & {
    type: "input_email";
  };

export type AllQuestionTypes =
  | ChoiceQuestionType
  | DropDownQuestionType
  | YesOrNoQuestionType
  | InputTextQuestionType
  | InputPhoneNumberQuestionType
  | InputDateAndTimeQuestionType
  | InputNumberQuestionType
  | InputLocationQuestionType
  | InputEmailQuestionType
  | CheckboxQuestionType;

// Section type
export type SectionQuestionHolder = {
  type: CWFItemType.Section;
  properties: {
    title: string;
  };
  contents: AllQuestionTypes[];
  id: string;
  order: 1;
};

export type DeletePageDetails = {
  id: string;
  parentId: string;
  deleteParentPage: boolean;
  subPages: string[];
};

export type MultiOption = {
  id: string;
  name: string;
};
export interface TemplatesList {
  id: string;
  created_at?: string;
  created_by?: {
    id: string;
    user_name: string;
    first_name: string;
    last_name: string;
    role: string;
    tenant_name: string;
  };
  updated_at?: string | null;
  updated_by?: {
    id: string;
    user_name: string;
    first_name: string;
    last_name: string;
    role: string;
    tenant_name: string;
  };
  archived_by?: string | null;
  archived_at?: string | null;
  completed_at?: string | null;
  is_archived?: boolean;
  published_at?: string | null;
  published_by?: {
    id: string;
    user_name: string;
    first_name: string;
    last_name: string;
    role: string;
    tenant_name: string;
  };
  version?: number;
  title?: string;
  status?: string;
  properties?: {
    title?: string | null;
    description?: string | null;
    status?: string | null;
  };
  templateNames?: string;
  template_unique_id: string;
  location_data?: {
    name?: string;
    description?: string;
    gps_coordinates?: {
      latitude?: string;
      longitude?: string;
    };
  };
}

export interface PhotoItemErrorOverlayProps {
  onReload: () => void;
  showSpinner: boolean;
}

export interface TemplatesFormListFilter {
  names: MultiOption;
  created_by_users: MultiOption;
  updated_by_users: MultiOption;
  work_package: MultiOption;
  location: MultiOption;
  region: MultiOption;
  supervisor: MultiOption;
}
export interface TemplatesListMetadata {
  count: number;
  results_per_page: number;
  scroll: string | null;
}

type FilterField =
  | "FORM"
  | "LOCATIONS"
  | "STATUS"
  | "WORKPACKAGE"
  | "CREATEDBY"
  | "CREATEDON"
  | "UPDATEDBY"
  | "UPDATEDON"
  | "COMPLETEDON"
  | "REPORTEDON"
  | "REGION";

export type FormFilter = {
  field: FilterField;
  values: MultiOption[];
};

export type TemplatesListRequest = {
  limit?: number;
  offset?: number;
  orderBy?: {
    field: string;
    desc: boolean;
  };
  template_status?: string[];
  template_names?: string | string[];
  published_by?: string | string[];
  updated_by?: string | string[];
  published_at_start_date?: string | null;
  published_at_end_date?: string | null;
  updated_at_start_date?: string | null;
  updated_at_end_date?: string | null;
  search?: string | null;
  template_unique_id?: string;
  title?: string;
};

export type TemplateFormsListRequest = {
  limit?: number;
  offset?: number;
  orderBy?: {
    field: string;
    desc: boolean;
  };
  form_names?: string | string[];
  status?: string | string[];

  created_by: string | string[];
  created_at_start_date?: string | null;
  created_at_end_date?: string | null;

  completed_at_start_date?: string | null;
  completed_at_end_date?: string | null;

  updated_by?: string | string[];
  updated_at_start_date?: string | null;
  updated_at_end_date?: string | null;

  search?: string | null;

  work_package_id?: string[];
  location_id?: string[];
  region_id?: string | string[];
  reported_at_start_date?: string | null;
  reported_at_end_date?: string | null;
  supervisor_id?: string | string[];
};

export type FormBuilderActionModeType =
  | "SAVE"
  | "PUBLISH"
  | "UPDATE"
  | "DRAFT_PUBLISH";
export type FormBuilderAlertType = "PUBLISH" | "CLOSE";
export type LinkComponentObj = {
  linkName: string;
  linkHref: string;
};

export type FormComponentsPopUpType = {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (content: any) => void;
  isActivitiesAndTasksIncluded?: boolean;
};

export type FormComponentsFooterType = {
  addButtonHandler: () => void;
  cancelButtonHandler: () => void;
  isDisabled: boolean;
};

export type PhotosDeleteAlertPopupType = {
  confirmDelete: () => void;
  setShowDeleteModal: (content: boolean) => void;
};

export type PhotoItemProps = {
  url?: string;
  name: string;
  onDelete: (event: React.MouseEvent<HTMLButtonElement>) => void;
  readOnly?: boolean;
  description?: string;
  onDescriptionChange: (value: string) => void;
};

export type PhotoUploadItem = {
  id: string;
  displayName: string;
  name: string;
  size: string;
  date: string;
  time: string;
  lastModified?: string | null;
  url: string;
  signedUrl: string;
  description?: string;
};

export type PhotoUploadConfigs = {
  title: string;
  buttonLabel: string;
  buttonIcon: IconName;
  allowedFormats: string;
  allowMultiple?: boolean;
};

export type SubmissionPhotoType = {
  id: string;
  md5: string | null;
  url: string;
  date: string;
  name: string;
  size: string;
  time: string;
  last_modified?: string | null;
  crc32c: string | null;
  category: string | null;
  mimetype: string | null;
  signed_url: string;
  display_name: string;
  description: string;
};

export interface FormValuesPhotoUploaderInterface {
  photos: PhotoUploadItem[];
}

export type ItemType = {
  title: string;
  description: string;
  user_value: [];
  attachment_type?: AttachmentTypes;
  type?: string;
};

export type EditComponentType = {
  id: string;
  order: number;
  type: FormComponentVarietyType;
  is_mandatory?: boolean;
  properties: ItemType;
  contents: [];
};
export type EditTitlePopUpProps = {
  isEditModalOpen: boolean;
  setIsEditModalOpen: (isEditModalOpen: boolean) => void;
  titleName: string;
  setTitleName: (titleName: string) => void;
  onSaveTitle: (componentType: string) => void;
  onUpdateAdditionalField: (componentType: string) => void;
  isSmartAddressChecked: boolean;
  setIsSmartAddressChecked: (isSmartAddressChecked: boolean) => void;
  item: EditComponentType;
  subTitle: string;
  isEnergyWheelEnabled: boolean;
  setSubTitle: (subTitle: string) => void;
  setIsEnergyWheelEnabled: (isEnergyWheelEnabled: boolean) => void;
  isHistoricalIncidentEnabled?: boolean;
  setIsHistoricalIncidentEnabled?: (isEnabled: boolean) => void;
  historicalIncidentLabel?: string;
  setHistoricalIncidentLabel?: (label: string) => void;
};

export type CustomDeleteConfirmationsModal = Pick<
  ModalProps,
  "isOpen" | "closeModal"
> & {
  onDeleteConfirm: () => void;
  isLoading?: boolean;
  attachmentItem?: FormComponentPayloadType;
};

export const documentCategories: SelectPrimaryOption[] = [
  { id: "1", name: "JHA" },
  { id: "2", name: "PSSR" },
  { id: "3", name: "HASP" },
  { id: "4", name: "Other" },
];

export type UploadModalProps = {
  file: UploadItem;
  allowCategories?: boolean;
  onSave: (editedFile: EditedFile) => void;
  onCancel: () => void;
};

export type EditedFile = {
  id: string;
  displayName: string;
  name: string;
  category?: string;
};

export type UploadConfigs = {
  title: string;
  buttonLabel: string;
  buttonIcon: IconName;
  allowedFormats: string;
  allowMultiple?: boolean;
};

export type UploadProps = PropsWithChildren<{
  configs: UploadConfigs;
  readOnly?: boolean;
  totalDocuments?: number;
  isUploadingDocument?: boolean;
  onUpload: (file: File[]) => void;
  attachmentItem: FormComponentPayloadType;
}>;

export type FieldArrayType = "attachments.photos";

export type UploadPhotosProps = Omit<UploadProps, "onUpload"> & {
  fieldArrayName: FieldArrayType;
  attachmentItem: FormComponentPayloadType;
  onAddOfAttachments: (value: PhotoUploadItem[]) => void;
  onDescriptionChangeOfAttachments: (
    photoItem: PhotoUploadItem,
    descriptionText: string
  ) => void;
  onDeleteAttachment: (photoId: string) => void;
};

export type TaskCardProps = {
  className?: string;
  title: string;
  risk: RiskLevel;
  expandable?: boolean;
  isExpanded?: boolean;
  toggleElementExpand?: () => void;
  showRiskInformation?: boolean;
  showRiskText?: boolean;
  withLeftBorder?: boolean;
  onClickEdit?: () => void;
  children?: ReactNode;
  isReadOnly?: boolean;
};
export type HazardsAndControlsComponentProps = {
  configs: any;
  mode?: string;
};

export type ActivityAndTaskComponentProps = {
  configs: any;
  handleChangeInActivity?: (value: any) => void;
  localActivities?: any;
  mode?: string;
};

// Define types for our data structure
interface LibraryTask {
  __typename: string;
  id: string;
  riskLevel: keyof typeof RiskLevel;
  name: string;
}

export interface Task {
  __typename?: string;
  id: string;
  status?: string;
  startDate?: string;
  endDate?: string;
  riskLevel?: string;
  name: string;
  libraryTask?: LibraryTask;
  hazards?: Hazards[];
  selected?: boolean;
}

export interface Activity {
  __typename?: string;
  id: string;
  isCritical: boolean;
  criticalDescription: string | null;
  name: string;
  status: string;
  startDate: string;
  endDate: string;
  taskCount: number;
  tasks: Task[];
}

export interface ActivitiesData {
  activities: Activity[];
}

export interface SelectedTask {
  id: string;
  name: string;
  fromWorkOrder: boolean;
  riskLevel: string;
  recommended: boolean;
  selected: boolean;
  libraryTask?: LibraryTask;
}

export interface SelectedActivity {
  id: string;
  isCritical: boolean;
  criticalDescription: string | null;
  name: string;
  status: string;
  startDate: string;
  endDate: string;
  taskCount: number;
  tasks: SelectedTask[];
}
export interface SelectionPayload {
  activities: SelectedActivity[];
}
export interface ActivitiesAndTasksCardProps {
  handleChangeInActivity?: (payload: SelectionPayload) => void;
  readOnly?: boolean;
  inSummary?: boolean;
}
export interface Locations {
  id: string;
  name?: string;
}
export interface ProjectDetails {
  project: {
    name?: string;
    locations: Locations[];
    libraryRegion: {
      id: string;
      name: string;
    };
    endDate?: string;
    startDate?: string;
  };
}

export interface ApiDetails {
  name: string;
  description: string;
  endpoint: string;
  method: string;
  headers: Record<string, string>;
  request: Record<string, unknown>;
  response: Record<string, unknown>;
  query: string;
  response_path: string;
  value_key: string;
  label_key: string;
}

// Narrow type specifically for "Fetch from source" REST lookup
export interface FetchFromSourceApiDetails {
  name: string; // "Fetch from source API"
  description: string;
  endpoint: string; // e.g. `/uploads/data-sources/{datasourceId}/columns/{columnName}`
  method: "GET"; // fixed
  headers: Record<string, string>; // typically { "Content-Type": "application/json" }
  request: Record<string, never>; // GET without body
  response: Record<string, unknown>;
  value_key: string; // usually the column name
  label_key: string; // usually the column name
}

export const REGIONS_API_DETAILS = {
  name: "Regions API",
  description: "API to fetch list of regions",
  endpoint: "/graphql",
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  request: {
    query: `query RegionsLibrary {
      regionsLibrary {
        id
        name
      }
    }`,
  },
  response: {},
  query: "RegionsLibrary",
  response_path: "regionsLibrary",
  value_key: "id",
  label_key: "name",
};

export type PrePopulationOptionType =
  | "None"
  | "user_last_completed_form"
  | null;

export type NonNullPrePopulationOptionType = Exclude<
  PrePopulationOptionType,
  null
>;

export type PrePopulationRulePaths =
  | {
      [key in NonNullPrePopulationOptionType]?: string[];
    }
  | null;

export type InputBaseProps = Pick<
  AllInputProps,
  | "id"
  | "required"
  | "placeholder"
  | "pattern"
  | "onBlur"
  | "min"
  | "max"
  | "disabled"
  | "readOnly"
>;

export type InputOwnProps = {
  name: string;
  defaultValue?: string;
  value?: string;
  type: "date" | "time" | "datetime-local";
  onChange?: (e?: string) => void;
  placeholder?: string;
  icon?: IconName;
  mode?: "future" | "past" | "all";
  dateResponseType?: "auto_populate_current_date" | "calendar" | "manual_input";
  timeResponseType?: "auto_populate_current_time" | "manual_input";
};

export type FieldDateTimePickerProps = FieldProps &
  InputBaseProps &
  InputOwnProps;

export const iconByInputType: Record<
  FieldDateTimePickerProps["type"],
  IconName
> = Object.freeze({
  date: "calendar",
  time: "clock",
  "datetime-local": "calendar",
});

export interface DateTimeFormState {
  title: string;
  hint_text?: string;
  is_mandatory: boolean;
  selected_type: Option;
  date_response_type: DateResponseType;
  date_options: DateType;
  date_type: DateType;
  date_validation?: Validation;
  time_validation?: ValidationTime;
  time_response_type: TimeResponseType;
  user_value: boolean | null;
  user_comments: string | null;
  user_attachments: File[] | null;
  include_in_widget?: boolean;
}
export interface RegionFormState {
  title: string;
  hint_text?: string;
  is_mandatory: boolean;
  user_value: string[] | null;
  pre_population_rule_name: null;
  options: Array<{ value: string; label: string }>;
  multiple_choice: boolean;
  description: string | null;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  include_in_widget: boolean;
  user_comments: string | null;
  user_attachments: File[] | null;
  api_details: ApiDetails;
}

export type HazardsModalProps = {
  addHazardsModalOpen: boolean;
  hazardsData: Hazards[];
  preSelectedHazards?: Hazards[];
  energyType?: EnergyType;
  setAddHazardsModalOpen: (addHazardsModalOpen: boolean) => void;
  onSaveHazards?: (selectedHazards: Hazards[]) => void;
  manuallyAddedHazards?: (selectedHazards: Hazards[]) => void;
  subTitle: string;
  activeTab: string;
  setActiveTab: (tab: string) => void;
};
export type Controls = {
  id: string;
  name: string;
  isApplicable: boolean;
  selected?: boolean;
  isUserAdded?: boolean;
};
export type Hazards = {
  id: string;
  name: string;
  imageUrl?: string;
  energyLevel?: string;
  energyType?: string;
  isApplicable?: boolean;
  controls?: Controls[];
  selectedControlIds?: string[];
  taskApplicabilityLevels?: TaskApplicabilityLevel[];
  isUserAdded?: boolean;
  noControlsImplemented?: boolean;
  selected?: boolean;
};

export type TaskApplicabilityLevel = {
  applicabilityLevel: string;
  taskId: string;
};

export type TasksLibraryType = {
  hazards: Hazards[];
};

export const ENERGY_TYPE_COLORS: Record<string, HexColor> = {
  BIOLOGICAL: "#6EC2D8",
  CHEMICAL: "#B7D771",
  TEMPERATURE: "#F38787",
  GRAVITY: "#3FD1AD",
  MOTION: "#ECDE65",
  MECHANICAL: "#E477A4",
  ELECTRICAL: "#EAB94C",
  PRESSURE: "#7FA6D9",
  SOUND: "#86D360",
  RADIATION: "#E89746",
};

export enum EnergyLevel {
  HighEnergy = "HIGH_ENERGY",
  LowEnergy = "LOW_ENERGY",
  NotDefined = "NOT_DEFINED",
}

export enum ApplicabilityLevel {
  Always = "ALWAYS",
  Mostly = "MOSTLY",
  Rarely = "RARELY",
  Never = "NEVER",
}

export interface EnergyWheelProps {
  callback: (energyType: EnergyType) => void;
  status: {
    [key in EnergyType]?: boolean;
  };
  readOnly?: boolean;
}

export type EnergyType =
  | "BIOLOGICAL"
  | "CHEMICAL"
  | "TEMPERATURE"
  | "GRAVITY"
  | "MOTION"
  | "MECHANICAL"
  | "ELECTRICAL"
  | "PRESSURE"
  | "SOUND"
  | "RADIATION";

export const ENERGY_TYPES = {
  CHEMICAL: "CHEMICAL",
  TEMPERATURE: "TEMPERATURE",
  GRAVITY: "GRAVITY",
  MOTION: "MOTION",
  MECHANICAL: "MECHANICAL",
  ELECTRICAL: "ELECTRICAL",
  PRESSURE: "PRESSURE",
  SOUND: "SOUND",
  RADIATION: "RADIATION",
  BIOLOGICAL: "BIOLOGICAL",
};

export const ENERGY_TYPE_COLOR = {
  [ENERGY_TYPES.BIOLOGICAL]: "#6EC2D8",
  [ENERGY_TYPES.CHEMICAL]: "#B7D771",
  [ENERGY_TYPES.TEMPERATURE]: "#F38787",
  [ENERGY_TYPES.GRAVITY]: "#3FD1AD",
  [ENERGY_TYPES.MOTION]: "#ECDE65",
  [ENERGY_TYPES.MECHANICAL]: "#E477A4",
  [ENERGY_TYPES.ELECTRICAL]: "#EAB94C",
  [ENERGY_TYPES.PRESSURE]: "#7FA6D9",
  [ENERGY_TYPES.SOUND]: "#86D360",
  [ENERGY_TYPES.RADIATION]: "#E89746",
};

export type FormRendererContextType = {
  formObject: FormType;
  activePageDetails: ActivePageObjType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  mode: UserFormMode;
  getFormContents: (
    data: PageType[],
    activePageDetails: ActivePageObjType
  ) => PageType[];
  hazardsData: Hazards[];
  tasksHazardData: Hazards[];
  hasRecommendedHazards: boolean;
  getTaskHazardsMapping: () => Record<string, Hazards[]>;
  selectedHazards: Hazards[];
  setSelectedHazards: React.Dispatch<React.SetStateAction<Hazards[]>>;
  isHazardsAndControlsPage: boolean;
  setIsHazardsAndControlsPage: React.Dispatch<React.SetStateAction<boolean>>;
  manuallyAddedHazardIds: string[];
  setManuallyAddedHazardIds: React.Dispatch<React.SetStateAction<string[]>>;
  isLoading: boolean;
  showMissingControlsError: boolean;
  setShowMissingControlsError: React.Dispatch<React.SetStateAction<boolean>>;
  manuallyAddHazardsHandler: (hazards: Hazards[]) => void;
  librarySiteConditionsData?: SiteConditonsLibrary;
  librarySiteConditionsLoading: boolean;
};

export type FormRendererProviderProps = {
  children: ReactNode;
  formObject: FormType;
  activePageDetails: ActivePageObjType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  mode: UserFormMode;
  hazardsData: Hazards[];
  tasksHazardData: Hazards[];
  isLoading: boolean;
  librarySiteConditionsData?: SiteConditonsLibrary;
  librarySiteConditionsLoading: boolean;
};

export enum FormStatus {
  InProgress = "in_progress",
  Completed = "completed",
}

export type HistoricalIncident = {
  archivedAt?: string;
  description: string;
  id: string;
  incidentDate?: string;
  incidentId?: string;
  incidentType?: string;
  severity?: string;
  severityCode?: string;
  taskType?: string;
  taskTypeId?: string;
};

export type SummaryPropertiesType = {
  title: string;
  description: string;
  user_value: [];
  historical_incident?: {
    label: string;
    incident?: HistoricalIncident;
  };
};

export type CWFSummaryType = {
  id: string;
  order: number;
  type: FormComponentVarietyType;
  is_mandatory: boolean;
  properties: SummaryPropertiesType;
  contents: [];
};

export type SiteConditionsPropertiesType = {
  title: string;
  description: string;
  user_value: [];
};

export type LocationUserValueType = {
  name: string;
  gps_coordinates: UserLocationLatAndLongValue | null;
  description: string;
  manual_location: boolean;
};

export type NearestHospitalUserValueType = {
  name: string;
  gps_coordinates?: UserLocationLatAndLongValue;
  description?: string;
  phone_number: string;
  other?: boolean;
  distance?: string;
  state?: string;
  city?: string;
  zip_code?: string;
};

export type LocationPropertiesType = {
  title: string;
  description: string;
  user_value: [];
  smart_address: boolean;
  is_mandatory: boolean;
};

export type NearestHospitalPropertiesType = {
  title: string;
  description: string;
  user_value: [];
  is_mandatory?: boolean;
};

export type CWFSiteConditionsType = {
  id: string;
  order: number;
  type: FormComponentVarietyType;
  is_mandatory: boolean;
  properties: SiteConditionsPropertiesType;
  contents: [];
};

export type CWFLocationType = {
  id: string;
  order: number;
  type: FormComponentVarietyType;
  is_mandatory: boolean;
  properties: LocationPropertiesType;
  contents: [];
};

export type CWFNearestHospitalType = {
  id: string;
  order: number;
  type: FormComponentVarietyType;
  is_mandatory: boolean;
  properties: NearestHospitalPropertiesType;
  contents: [];
};

export type FormElement =
  | PageType
  | FormElementsType
  | FormComponentPayloadType
  | PersonnelComponentType;

export interface ControlModalProps {
  controlModalOpen: boolean;
  preSelectedControls: Controls[];
  hazardsControlList: Controls[];
  selectedHazardId: string;
  onAddControl: (controls: Controls[], hazardId: string) => void;
  onClose: () => void;
}

export type EditPeriodProps = {
  settings: TemplateSettings;
};

export type SiteConditonsLibrary = {
  id: string;
  name: string;
  hazards: Hazards[];
  siteConditionsLibrary: LibrarySiteCondition[];
  tenantAndWorkTypeLinkedLibrarySiteConditions: LibrarySiteCondition[];
};

export interface SiteCondition {
  id: string;
  name: string;
  selected: boolean;
  librarySiteCondition: LibrarySiteCondition;
  hazards?: SiteConditionHazard[];
  checked?: boolean;
  isManuallyAdded?: boolean;
}

interface SiteConditionHazard {
  libraryHazard: LibraryHazard;
  id: string;
  isApplicable?: boolean;
  controls?: Controls[];
}

interface LibraryHazard {
  id: string;
  isApplicable?: boolean;
  controls?: Controls[];
}

export interface SiteConditionsData {
  siteConditions?: SiteCondition[];
  locationSiteConditions?: SiteCondition[];
}

export type FormComponentData = {
  activities_tasks?: SelectedActivity[];
  hazards_controls?: HazardControl;
  site_conditions?: SiteCondition[];
  location_data?: LocationUserValueType;
  nearest_hospital?: NearestHospitalUserValueType;
};

export type ApiFormDataType = {
  contents: PageType[];
  properties: {
    status: string;
    id?: string | undefined;
    title: string;
    description: string;
    template_unique_id?: string | undefined;
    report_start_date?: Date | string;
  };
  component_data?: FormComponentData;
  metadata?: TemplateMetaData;
  template_id: string;
  pre_population_rule_paths?: PrePopulationRulePaths;
};

export type RestMutationResponse<T> = {
  mutate: (data: T) => void;
  responseData: T | null;
};

export type ProjectDetailsType = {
  project: {
    endDate?: string;
    id: string;
    libraryRegion?: {
      id: string;
      name: string;
    };
    locations?: Locations[];
    name?: string;
    startDate: string;
  };
  endDate?: string;
  id?: string;
  libraryRegion?: {
    id: string;
    name: string;
  };
  locations?: Locations[];
  name?: string;
  startDate?: string;
};

export type SettingsCheckBoxType = {
  id: string;
  name: string;
  isChecked?: boolean;
};

export type WorkTypesProps = {
  settings: TemplateSettings;
};

export type TemplateSettingsFormProps = {
  selectedTab: number;
  settings: TemplateSettings;
};
export enum TemplateSettingsNavigationTab {
  TEMPLATE_AVAILABILITY = "TEMPLATE AVAILABILITY",
  EDIT_PERIOD = "EDIT PERIOD",
  WORK_TYPES = "WORK TYPES",
  LINKED_FORMS = "LINKED FORMS",
}

export type CWFSiteConditionsProps = {
  item: CWFSiteConditionsType;
  activePageDetails: ActivePageObjType;
  section: any;
  mode: UserFormMode;
  inSummary?: boolean;
};

export type StaticSiteConditionCardProps = {
  item: CWFSiteConditionsType;
};

export type PersonnelAttributeUserValue = "single_name" | "multiple_names";

export type PersonnelAttribute = {
  attribute_id: string;
  attribute_name: string;
  is_required_for_form_completion: boolean;
  applies_to_user_value: PersonnelAttributeUserValue;
};

export type PersonnelCrewDetails = {
  name: string;
  signature: {
    id: string;
    md5: string | null;
    url: string;
    date: string;
    name: string;
    size: string;
    time: string;
    crc32c: string | null;
    category: string | null;
    mimetype: string | null;
    signedUrl: string;
    display_name: string;
  };
  type: string;
  email: string;
  primary: string | null;
  job_title: string;
  department: string;
  manager_id: string;
  external_id: string;
  company_name: string;
  display_name: string | null;
  manager_name: string;
  manager_email: string;
  employee_number: string;
};

export type PersonnelUserValue = {
  crew_details: PersonnelCrewDetails;
  selected_attribute_ids: string[];
};

export type PersonnelComponentProperties = {
  title: string;
  include_in_summary: boolean;
  attributes: PersonnelAttribute[];
  user_value: PersonnelUserValue[];
};

export type PersonnelComponentType = {
  type: CWFItemType.PersonnelComponent;
  properties: PersonnelComponentProperties;
  contents: FormElement[];
  id: string;
  order: number;
};

export type AttributeForm = {
  label: string;
  isRequired: boolean;
  appliesTo: string;
};

export type AddAttributeProps = {
  onAdd?: (attributes: AttributeForm[]) => void;
};

export type AddAttributeComponentProps = AddAttributeProps & {
  disabled?: boolean;
};

export interface PersonnelSettingsProps {
  item: PersonnelComponentType;
  onClose: () => void;
  onSave: (component: PersonnelComponentType) => void;
}

export type LocationSearchUsingAPIPops = {
  onChange: (raw: string) => void;
  onClear?: () => void;
  mode: UserFormMode;
  value: string;
  properties: any;
  setLatitude?: (lat: string) => void;
  setLongitude?: (long: string) => void;
  userLocationLatitude?: number;
  userLocationLongitude?: number;
};

export type LocationAutocompleteProps = {
  onPlaceSelected: (raw: string) => void;
  onClear?: () => void;
  mode: UserFormMode;
  value: string;
  properties: any;
  setLatitude?: (lat: string) => void;
  setLongitude?: (long: string) => void;
  userLocationLatitude?: number;
  userLocationLongitude?: number;
};

export type TemplateData = {
  id: string;
  templateName: string;
  workTypes?: WorkTypes[];
};

export type PersonelRow = {
  job_title?: string | null;
  employee_number?: string | null;
  display_name?: string | null;
  id: string;
  name: string;
  signature?: FileInputsCWF | null;
  attrIds?: string[];
  jobTitle?: string | null;
  employeeNumber?: string | null;
  type?: string | null;
  displayName?: string | null;
  email?: string | null;
  departmentName?: string | null;
  managerId?: string | null;
  managerEmail?: string | null;
  managerName?: string | null;
  external_id?: string | null;
};

export type PersonnelNameSelectorProps = {
  isOpen: boolean;
  closeModal: () => void;
  onSelectName: (rows: PersonelRow[]) => void;
  disabledIds: string[];
};
export interface CustomAttributes {
  externalId: string;
  manager_id: string;
  displayName: string;
  division_name: string | null;
  employee_type: string | null;
  manager_email: string | null;
  employeeNumber: string;
  department_name: string;
  employment_start_date: string | null;
  emails: {
    primary: boolean;
    type: string;
    value: string;
  }[];
}

export type WorkosUser = {
  id: string;
  name: string;
  idpId?: string | null | undefined;
  username?: string;
  firstName?: string;
  lastName?: string;
  jobTitle?: string | null;
  employeeNumber?: string | null;
  customAttributes?: CustomAttributes;
};

export type Mode = "idle" | "input" | "saved";

export type ChoiceProperties = {
  title: string;
  options: ChoiceOption[];
  user_value: string[] | null;
  choice_type: "single_choice" | "multiple_choice";
};

export type ChoiceAndDropdownDataProps = {
  content: {
    id: string;
    order: number;
    type: FormComponentVarietyType;
    is_mandatory: boolean;
    properties: {
      title: string;
      description: string;
      user_value: SubmissionPhotoType[];
      user_other_value?: string;
    };
    contents: [];
  };
};

export type FormHeaderProps = {
  formObject: FormType;
  mode: UserFormMode;
  linkObj: LinkComponentObj;
  workPackageData?: WorkPackageData;
  setMode?: (mode: UserFormMode) => void;
};

export interface PersonnelComponentAddPayload {
  componentId: string;
  rowId: string;
  name: string;
  signature: FileInputsCWF | null;
  attrIds: string[];
  employeeNumber?: string;
  jobTitle?: string;
  type?: string;
  displayName?: string;
  email?: string;
  departmentName?: string;
  managerId?: string;
  managerEmail?: string;
  managerName?: string;
}

export type Row = PersonelRow & { attrIds?: string[] };

export interface Props {
  person: PersonelRow;
  item: PersonnelComponentType;
  mode?: UserFormMode;
  onRequestDelete: () => void;
  onSignatureUpdate: (sig: FileInputsCWF) => void;
  onToggleAttr: (attrId: string) => void;
  singleAttrMap: Record<string, string>;
}

export type Attribute = {
  attribute_id: string;
  attribute_name: string;
  is_required_for_form_completion: boolean;
  applies_to_user_value: "single_name" | "multiple_names";
};

export type CrewRow = {
  selected_attribute_ids?: string[];
};

export type PersonnelRowType = PersonelRow & { attrIds?: string[] };

export type AttributeMeta =
  PersonnelComponentType["properties"]["attributes"][number];
export type RegionMetadata = {
  region?: {
    name: string;
    id: string;
  };
};

export type InputPropertiesType =
  | InputTextPropertiesType
  | InputDateAndTimePropertiesType
  | InputPhoneNumberPropertiesType
  | InputEmailQuestionPropertiesType
  | InputNumberPropertiesType
  | InputLocationPropertiesType;

export type DateTimeValueType =
  | {
      value: string;
    }
  | {
      from: string;
      to: string;
    };

export type OptionValue = {
  value: string;
  label: string;
};

export type DropDownValue = string[] | OptionValue[] | null;

export type CheckboxQuestionPropertiesType = Omit<
  BaseQuestionPropertiesType,
  "user_value"
> & {
  pre_population_rule_name?: PrePopulationOptionType | null;
  is_mandatory: boolean;
  comments_allowed: boolean;
  attachments_allowed: boolean;
  user_value?: string[] | null;
  choice_type: ChoiceType;
  options: OptionValueCheckbox[];
};

export type OptionValueCheckbox = {
  value: string;
  label: string;
  url?: string;
  url_display_text?: string;
};

export type CheckboxQuestionType =
  BaseQuestionType<CheckboxQuestionPropertiesType> & {
    type: "checkbox";
  };

// Props for CheckboxForm component (used in dynamicForm/checkbox.tsx)
export type CheckboxFormProps = {
  initialState?: CheckboxQuestionPropertiesType;
  onAdd: (state: CheckboxQuestionPropertiesType) => void;
  onClose: () => void;
  disabled?: boolean;
};

export interface CheckboxPreviewProps {
  content: {
    type: string;
    properties: CheckboxQuestionPropertiesType;
    id?: string;
  };
  mode: UserFormMode;
  inSummary?: boolean;
  onChange: (value: string[]) => void;
}
export type CWFAddActivityModalProps = {
  isOpen: boolean;
  closeModal: () => void;
  handleChangeInActivity?: (payload: SelectionPayload) => void;
  activityToEdit?: SelectedActivity;
  refetch?: () => void;
};

export type ActivityFilter = {
  groupName: string;
  values: Array<CheckboxOption & { isCritical?: boolean }>;
};

export interface UnifiedTask {
  id: string;
  name: string;
  riskLevel: string;
  selected: boolean;
  isApiTask: boolean;
  originalTask: any;
}

export interface UnifiedActivity {
  id: string;
  name: string;
  isCritical: boolean;
  criticalDescription: string | null;
  status: string;
  startDate: string;
  endDate: string;
  taskCount: number;
  tasks: UnifiedTask[];
}
export type PersonnelPage = PageType & {
  properties: PersonnelComponentProperties;
};
export type CWFActivityInputs = {
  locationId: string;
  name: string;
  startDate: string;
  endDate: string;
  status: { id: string; name: string };
  libraryActivityTypeId?: string;
  tasks: Array<{ libraryTaskId: string }>;
  isCritical: boolean;
  criticalDescription: string | null;
};

export enum UserFormModeTypes {
  PREVIEW = "PREVIEW",
  PREVIEW_PROPS = "PREVIEW_PROPS",
  BUILD = "BUILD",
  EDIT = "EDIT",
}

export type SummaryHistoricalIncidentSettingProps = {
  isHistoricalIncidentEnabled: boolean;
  setIsHistoricalIncidentEnabled?: (enabled: boolean) => void;
  historicalIncidentLabel: string;
  setHistoricalIncidentLabel?: (label: string) => void;
};
export interface originalLocationValues {
  location: string;
  latitude: string;
  longitude: string;
  locationDescription: string;
}
export interface pendingAction {
  type: string;
  value?: string;
}

export type FieldRendererProps = {
  content: {
    type: string;
    properties: any;
    id?: string;
  };
  order: number;
  activePageDetails: ActivePageObjType;
  section?: any;
  mode: UserFormMode;
  inSummary?: boolean;
};

export type FieldType = "input_text" | "input_phone_number" | string;

export type LocationInputContent = {
  type: FieldType;
  properties: any;
  id?: string;
};

export type LocationInputType = {
  content: LocationInputContent;
  mode: UserFormMode;
  onChange: (value: any) => void;
  inSummary?: boolean;
};

export type LinkedFormProps = {
  settings: TemplateSettings;
};

export type HistoricalIncidentProps = {
  label: string;
  componentId: string;
  readOnly?: boolean;
};
export type FetchFromSrcDropdownProps = {
  content: {
    type: string;
    properties: any;
  };
  mode: UserFormMode;
  inSummary?: boolean;
  onChange: (value: DropDownValue) => void;
};
