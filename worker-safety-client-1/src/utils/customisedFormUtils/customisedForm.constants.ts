import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";

export const CF_REDUCER_CONSTANTS = {
  ADD_PAGE: "ADD_PAGE" as const,
  ADD_SUBPAGE: "ADD_SUBPAGE" as const,
  ADD_SECTION: "ADD_SECTION" as const,
  ADD_FIELD: "ADD_FIELD" as const,
  EDIT_FIELD: "EDIT_FIELD" as const,
  SWITCH_SECTION_ORDERS: "SWITCH_SECTION_ORDERS" as const,
  ADD_SECTION_FIELD: "ADD_SECTION_FIELD" as const,
  EDIT_SECTION_FIELD: "EDIT_SECTION_FILED" as const,
  DELETE_FIELD: "DELETE_FIELD" as const,
  DELETE_PAGE: "DELETE_PAGE" as const,
  DELETE_SUBPAGE: "DELETE_SUBPAGE" as const,
  CHANGE_BUILDER_MODE: "CHANGE_BUILDER_MODE" as const,
  ADD_FIELD_COMMENT: "ADD_FIELD_COMMENT" as const,
  ADD_FIELD_ATTACHMENTS: "ADD_FIELD_ATTACHMENTS" as const,
  FIELD_VALUE_CHANGE: "FIELD_VALUE_CHANGE" as const,
  FORM_NAME_CHANGE: "FORM_NAME_CHANGE" as const,
  CHANGE_INITIAL_STATE: "CHANGE_INITIAL_STATE" as const,
  SET_API_DATA: "SET_API_DATA" as const,
  DELETE_SECTION: "DELETE_SECTION" as const,
  BULK_DELETE_PAGE: "BULK_DELETE_PAGE" as const,
  PAGE_DRAG: "PAGE_DRAG" as const,
  PAGE_TITLE_EDIT: "PAGE_TITLE_EDIT" as const,
  PAGE_STATUS_CHANGE: "PAGE_STATUS_CHANGE" as const,
  SWITCH_CONTENT_ORDERS: "SWITCH_CONTENT_ORDERS" as const,
  ADD_COMPONENTS: "ADD_COMPONENTS" as const,
  ATTACHMENTS_VALUE_CHANGE: "ATTACHMENTS_VALUE_CHANGE" as const,
  DOCUMENTS_VALUE_CHANGE: "DOCUMENTS_VALUE_CHANGE" as const,
  BUTTON_DISABLE_STATUS_CHANGE: "BUTTON_DISABLE_STATUS_CHANGE" as const,
  ACTIVITIES_VALUE_CHANGE: "ACTIVITIES_VALUE_CHANGE" as const,
  ENERGY_HAZARDS_VALUE_CHANGE: "ENERGY_HAZARDS_VALUE_CHANGE" as const,
  CHANGE_WORK_PACKAGE_DATA: "CHANGE_WORK_PACKAGE_DATA" as const,
  PAGE_SUMMARY_VISIBILITY_TOGGLE: "PAGE_SUMMARY_VISIBILITY_TOGGLE" as const,
  SUBPAGE_SUMMARY_VISIBILITY_TOGGLE:
    "SUBPAGE_SUMMARY_VISIBILITY_TOGGLE" as const,
  SET_FORM_STATE: "SET_FORM_STATE" as const,
  SET_TASKS_HAZARD_DATA: "SET_TASKS_HAZARD_DATA" as const,
  SITE_CONDITIONS_VALUE_CHANGE: "SITE_CONDITIONS_VALUE_CHANGE" as const,
  LOCATION_VALUE_CHANGE: "LOCATION_VALUE_CHANGE" as const,
  NEAREST_HOSPITAL_VALUE_CHANGE: "NEAREST_HOSPITAL_VALUE_CHANGE" as const,
  SET_SITE_CONDITIONS_HAZARD_DATA: "SET_SITE_CONDITIONS_HAZARD_DATA" as const,
  PERSONNEL_COMPONENT_ADD_DATA: "PERSONNEL_COMPONENT_ADD_DATA" as const,
  PERSONNEL_COMPONENT_REMOVE_DATA: "PERSONNEL_COMPONENT_REMOVE_DATA" as const,
  RESET_PAGE: "RESET_PAGE" as const,
  SET_FORM_VALIDITY: "SET_FORM_VALIDITY" as const,
  UPDATE_METADATA: "UPDATE_METADATA" as const,
  UPDATE_HISTORICAL_INCIDENT: "UPDATE_HISTORICAL_INCIDENT" as const,
  UPDATE_WIDGET_SETTINGS: "UPDATE_WIDGET_SETTINGS" as const,
};

export const COMPONENTS_TYPES = {
  ACTIVITIES_AND_TASKS: "ACTIVITIES_AND_TASKS" as const,
  SITE_CONDITIONS: "SITE_CONDITIONS" as const,
  HAZARDS_AND_CONTROLS: "HAZARDS_AND_CONTROLS" as const,
  PHOTO_ATTACHMENTS: "PHOTO_ATTACHMENTS" as const,
  DOCUMENT_ATTACHMENTS: "DOCUMENT_ATTACHMENTS" as const,
  SUMMARY: "SUMMARY" as const,
  LOCATION: "LOCATION" as const,
  NEAREST_HOSPITAL: "NEAREST_HOSPITAL" as const,
  PERSONNEL_COMPONENT: "PERSONNEL_COMPONENT" as const,
};

export const COMPONENTS_LIST = [
  {
    id: 1,
    label: "Activities and Tasks",
    description: "ACTIVITIES_AND_TASKS",
  },
  {
    id: 2,
    label: "Site Conditions",
    description: "SITE_CONDITIONS",
  },
  {
    id: 3,
    label: "Hazards and Controls",
    description: "HAZARDS_AND_CONTROLS",
  },
  {
    id: 4,
    label: "Photo Attachments",
    description: "PHOTO_ATTACHMENTS",
  },
  {
    id: 5,
    label: "Document Attachments",
    description: "DOCUMENT_ATTACHMENTS",
  },
  {
    id: 6,
    label: "Summary",
    description: "SUMMARY",
  },
  {
    id: 7,
    label: "Location",
    description: "LOCATION",
  },
  {
    id: 8,
    label: "Nearest Hospital",
    description: "NEAREST_HOSPITAL",
  },
  {
    id: 9,
    label: "Personnel",
    description: "PERSONNEL_COMPONENT",
  },
];

export const ALLOWED_IMAGE_FORMATS = [
  "jpg",
  "jpeg",
  "png",
  "gif",
  "svg",
  "apng",
];
export const ALLOWED_DOCUMENTS_FORMATS = [
  "pdf",
  "doc",
  "docx",
  "xls",
  "xlsx",
  "ppt",
  "pptx",
];
export const maxFiles: Readonly<number> = 10;
export const photoMaxFileSize: Readonly<number> = 15000;
export const documentMaxFileSize: Readonly<number> = 20000;
export const photoMaxSize = "15MB";
export const documentMaxSize = "20MB";
export const FORMATS_IGNORED = ["heic", "svg", "avif"];

export const prePopulationOptions: RadioGroupOption[] = [
  { id: 1, value: "None", description: "None" },
  {
    id: 2,
    value: "user_last_completed_form",
    description: "From user's last completed form",
  },
];

export const ALERT_MESSAGES_FOR_COMPONENTS: Record<string, string> = {
  PHOTO_ATTACHMENTS: "Photo Attachments Component added successfully",
  DOCUMENT_ATTACHMENTS: "Document Attachments Component added successfully",
  ACTIVITIES_AND_TASKS: "Activities and Tasks Component added successfully",
  HAZARDS_AND_CONTROLS: "Hazards and Controls Component added successfully",
  SUMMARY: "Summary Component added successfully",
  SITE_CONDITIONS: "Site conditions Component added successfully",
  PERSONNEL_COMPONENT: "Personnel Component added successfully",
};

export const HIDDEN_COMPONENTS_FOR_REPEATABLE: string[] = [
  "attachment",
  "hazards_and_controls",
  "activities_and_tasks",
  "SITE_CONDITIONS",
  "summary",
  "contractor",
  "report_date",
];

export const ALLOWED_KEYS_FOR_NUMBER_TYPE = [
  "Backspace",
  "Tab",
  "ArrowLeft",
  "ArrowRight",
  "Delete",
  "Home",
  "End",
  "-",
  ".",
];

export const APPLIES_OPTIONS: RadioGroupOption[] = [
  { id: 1, value: "multiple_names", description: "Multiple Names" },
  { id: 2, value: "single_name", description: "Single Name" },
];

export const DEFAULT_ATTRIBUTE_CHOICE = {
  id: "placeholder",
  name: "Attribute Name",
  isChecked: false,
};
