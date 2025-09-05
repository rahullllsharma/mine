import type { FormFilter } from "@/container/insights/filters/formFilters/FormFilters";
import type { LocationFilter } from "@/container/mapView/filters/mapFilters/MapFilters";
import type { TemplateFormsFilter } from "@/components/templatesComponents/filter/TemplateFormFilters";

type UserPermission =
  | "VIEW_PROJECT"
  | "VIEW_TASKS"
  | "VIEW_SITE_CONDITIONS"
  | "VIEW_HAZARDS"
  | "VIEW_CONTROLS"
  | "VIEW_INSPECTIONS"
  | "VIEW_INSIGHT_REPORTS"
  | "ASSIGN_USERS_TO_PROJECTS"
  | "ASSIGN_CONTROLS"
  | "ADD_TASKS"
  | "ADD_HAZARDS"
  | "ADD_CONTROLS"
  | "ADD_SITE_CONDITIONS"
  | "ADD_FORMS"
  | "ADD_REPORTS"
  | "EDIT_HAZARDS"
  | "EDIT_CONTROLS"
  | "EDIT_TASKS"
  | "EDIT_SITE_CONDITIONS"
  | "EDIT_PROJECTS"
  | "EDIT_OWN_REPORTS"
  | "EDIT_REPORTS"
  | "REOPEN_REPORTS"
  | "ADD_PROJECTS"
  | "REOPEN_PROJECT"
  | "CONFIGURE_APPLICATION"
  | "DELETE_OWN_REPORTS"
  | "DELETE_REPORTS"
  | "DELETE_PROJECTS"
  | "VIEW_PROJECT_AUDITS"
  | "ADD_ACTIVITIES"
  | "REOPEN_OWN_REPORT"
  | "CONFIGURE_CUSTOM_TEMPLATES";

export type UserPreferenceLocationMapFilters = {
  id: string;
  entityType: "MapFilters";
  contents: LocationFilter[];
};

export type UserPreferenceFormFilters = {
  id: string;
  entityType: "FormFilters";
  contents: FormFilter[];
};

export type UserPreferenceCWFTemplateFormFilters = {
  id: string;
  entityType: "CWFTemplateFormFilters";
  contents: TemplateFormsFilter[];
};

type UserPerference =
  | UserPreferenceLocationMapFilters
  | UserPreferenceFormFilters
  | UserPreferenceCWFTemplateFormFilters;

type UserRole = "administrator" | "manager" | "supervisor" | "viewer";
type OpCo = { id: string; name: string };
type AuthUser = {
  name: string;
  permissions: UserPermission[];
  role: UserRole;
  initials: string;
  id: string;
  email: string;
  opco: OpCo | null;
  userPreferences: UserPerference[];
};

export type { AuthUser, UserPermission, UserRole };
