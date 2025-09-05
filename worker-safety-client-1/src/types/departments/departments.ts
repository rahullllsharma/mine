export interface Department {
  attributes: Attributes;
  relationships: Relationships;
  type: string;
  id: string;
  links: DepartmentLinks;
}

export interface Attributes {
  name: string;
  created_at: Date;
}

export interface DepartmentLinks {
  self: string;
}

export interface Relationships {
  opco: Opco;
}

export interface Opco {
  data: Data;
  links: OpcoLinks;
}

export interface Data {
  id: string;
  type: string;
}

export interface OpcoLinks {
  related: string;
}
