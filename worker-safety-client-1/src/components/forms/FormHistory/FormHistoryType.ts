export interface FormHistoryProps {
  data: AuditData[];
  isAuditDataLoading: boolean;
  location?: string;
}

export interface AuditData {
  id: string;
  created_at: string;
  object_id: string;
  object_type: string;
  event_type: string;
  location: string;
  created_by: string;
  role: string;
  source_app?: string | null;
  pages?: Page[] | null;
  fields?: Field[] | null;
  sections?: Section[] | null;
}

export interface Page {
  name: string;
  sections?: Section[] | null;
  fields?: Field[] | null;
}

export interface Section {
  name: string;
  sections?: Section[] | null;
  section_type: string;
  operation_type: string;
  fields?: Field[] | null;
}

export interface Field {
  name: string;
  old_value?: string;
  new_value?: string;
}
