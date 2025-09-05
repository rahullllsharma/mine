import type { MultiOption } from "@/components/templatesComponents/customisedForm.types";

export type PublishedFilterField =
  | "TEMPLATENAME"
  | "PUBLISHEDBY"
  | "PUBLISHEDON";

export type PublishedFilter = {
  field: FilterField;
  values: MultiOption[] | { from: Date | null; to: Date | null };
};

export type DraftFilterField = "TEMPLATENAME" | "UPDATEDBY" | "UPDATEDAT";

export type DraftFilter = {
  field: DraftFilterField;
  values: MultiOption[] | { from: Date | null; to: Date | null };
};
export type FilterField = PublishedFilterField | DraftFilterField;

export type TemplatesForm = {
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
  is_archived?: boolean;
  published_at?: string | null;
  published_by?: {
    id: string;
    user_name: string;
    first_name: string;
    last_name: string;
    role: string;
    tenant_name: string;
  } | null;
  version?: number;
  title: string;
  status?: string;
};

export type TemplatesFormsList = {
  group_by_key: string;
  forms: TemplatesForm[];
};
