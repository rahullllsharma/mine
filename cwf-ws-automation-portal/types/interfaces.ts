export interface Environment {
  url: string;
  username: string;
  password: string;
}

export interface EnvConfig {
  environment: {
    integ: Environment;
    staging: Environment;
    production: Environment;
  };
}

export interface ApiEnvironmentUrls {
  integ: string;
  staging: string;
  production: string;
}

export interface ApiCategories {
  cwfTemplates: ApiEnvironmentUrls;
  cwfTemplatesSaveAndComplete: ApiEnvironmentUrls;
}

export interface ApiUrlConfig {
  url: ApiCategories;
}

// export interface FormMetadata {
//   work_package: {
//     name: string;
//     id: string;
//   };
//   location: {
//     name: string;
//     id: string;
//   };
// }

export interface TemplateMetadata {
  is_energy_wheel_enabled?: boolean;
  is_report_date_included?: boolean;
  is_activities_and_tasks_included?: boolean;
  is_hazards_and_controls_included?: boolean;
  is_summary_included?: boolean;
  is_site_conditions_included?: boolean;
  is_location_included?: boolean;
  is_nearest_hospital_included?: boolean;
}

export interface User {
  id: string;
  user_name: string;
  first_name: string;
  last_name: string;
  role: string;
  tenant_name: string;
}

export interface FormProperties {
  title: string;
  description: string | null;
  status: string;
  report_start_date: string | null;
}

export interface DateTimeProperties {
  title: string;
  hint_text: string | null;
  description: string | null;
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: string | null;
  user_comments: string | null;
  user_attachments: any[] | null;
  selected_type: string;
  date_response_type: string;
  date_options: string;
  date_validation: string;
  date_type: string;
  time_response_type: string;
  time_validation: string;
}
export interface ReportingDateTimeProperties {
  title: string;
  hint_text: string | null;
  description: string | null;
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: {
    value: string; // ISO 8601 date-time string
  } | null;
  user_comments: string | null;
  user_attachments: any[] | null;
  selected_type: string;
  date_response_type: string;
  date_options: string;
  date_validation: string | null;
  date_type: string;
  time_response_type: string;
  time_validation: string | null;
}

export interface TextProperties {
  title: string;
  hint_text: string;
  description: string | null;
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: string | null;
  user_comments: string | null;
  user_attachments: any[] | null;
  pre_population_rule_name: string | null;
  response_option: string;
  validation: any[];
  input_type: string;
  sub_label: string;
  placeholder: string;
  visible_lines: number;
}

export interface PhoneNumberProperties {
  title: string;
  hint_text: string | null;
  description: string | null;
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: string | null;
  user_comments: string | null;
  user_attachments: any[] | null;
  response_option: string; // "manual_input" in this case
  validation: any[] | null; // Array of validation rules or null
}

export interface NumberProperties {
  title: string;
  hint_text: string | null;
  description: string | null;
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: string | null;
  user_comments: string | null;
  user_attachments: any[] | null;
  response_option: string; // "manual_input" in this case
  display_units: boolean; // Whether to display units
  unit_name: string | null; // Unit of measurement (e.g., "kg", "m")
  validation: any[] | null; // Array of validation rules or null
}

export interface AttachmentProperties {
  title: string;
  attachment_type: "photo" | "document";
  attachment_max_count: number;
  user_value: any[];
  include_in_summary: boolean;
}

export interface ActivitiesAndTasksProperties {
  title: string;
  hint_text: string | null;
  description: string | null;
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: any[];
  user_comments: string | null;
  user_attachments: any[] | null;
  add_button_enabled: boolean;
  api_details: any | null; // Need clarification on this
  include_in_summary: boolean;
}

export interface ChoiceOption {
  value: string;
  label: string;
  image_url: string | null;
}

export interface ChoiceProperties {
  title: string;
  hint_text: string | null;
  description: string | null;
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: string[] | null;
  user_comments: string | null;
  user_attachments: any[] | null;
  pre_population_rule_name: string | null;
  choice_type: string;
  response_option: string;
  options: ChoiceOption[];
  include_other_option: boolean;
  include_NA_option: boolean;
  include_in_summary: boolean;
}

export interface HazardsAndControlsProperties {
  title: string;
  hint_text: string | null;
  description: string | null;
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: any[];
  user_comments: string | null;
  user_attachments: any[] | null;
  add_button_enabled: boolean;
  api_details: any | null;
  include_in_summary: boolean;
  sub_title: string | null;

}
export interface EmailProperties {
  title: string;
  hint_text: string | null;
  description: string | null;
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: string[] | null;
  user_comments: string | null;
  user_attachments: any[] | null;
  pre_population_rule_name: string | null;
  response_option: string;
  include_in_summary: boolean;
  validation: any[];
}
export interface ContentBase {
  type: string;
  properties: Record<string, any>;
  contents: Content[];
  id: string;
  order: number;
}

export interface FormContent {
  type: "form";
  properties: FormProperties;
  contents: PageContent[];
  metadata: TemplateMetadata;
  component_data: null;
  template_id: string;
  id: string;
  created_at: string;
  created_by: User;
  updated_at: string;
  updated_by: User;
  archived_by: null;
  archived_at: null;
  is_archived: boolean;
  published_at: null;
  published_by: null;
  version: number;
  order: number;
}

export interface PageContent extends ContentBase {
  type: "page";
  properties: {
    title: string;
    description: string;
    page_update_status: string;
  };
}

export interface SectionContent extends ContentBase {
  type: "section";
  properties: {
    title: string;
  };
}

export interface InputDateTimeContent extends ContentBase {
  type: "input_date_time";
  properties: DateTimeProperties;
}

export interface InputPhoneNumberContent extends ContentBase {
  type: "input_phone_number";
  properties: PhoneNumberProperties;
}

export interface InputEmailContent extends ContentBase {
  type: "input_email";
  properties: EmailProperties;
}

export interface InputNumberContent extends ContentBase {
  type: "input_number";
  properties: NumberProperties;
}

export interface ReportDateTimeContent extends ContentBase {
  type: "report_date";
  properties: ReportingDateTimeProperties;
}

export interface InputTextContent extends ContentBase {
  type: "input_text";
  properties: TextProperties;
}

export interface ChoiceContent extends ContentBase {
  type: "choice";
  properties: ChoiceProperties;
}

export interface AttachmentContent extends ContentBase {
  type: "attachment";
  properties: AttachmentProperties;
  is_mandatory: boolean;
}

export interface ActivitiesAndTasksContent extends ContentBase {
  type: "activities_and_tasks";
  properties: ActivitiesAndTasksProperties;
}

export interface HazardsAndControlsContent extends ContentBase {
  type: "hazards_and_controls";
  properties: HazardsAndControlsProperties;
}

export type Content =
  | PageContent
  | SectionContent
  | InputDateTimeContent
  | InputTextContent
  | ChoiceContent
  | InputPhoneNumberContent
  | InputNumberContent
  | ReportDateTimeContent
  | AttachmentContent
  | ActivitiesAndTasksContent
  | InputEmailContent
  | HazardsAndControlsContent;

export interface ContentCounters {
  [contentType: string]: number;
}
