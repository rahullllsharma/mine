import type { AuditActionType } from "./AuditActionType";
import type { AuditObjectType } from "./AuditObjectType";
import type { UserRole } from "../auth/AuthUser";

export type AuditEvent = {
  transactionId: string;
  timestamp: string;
  actor: AuditActor;
  actionType: AuditActionType;
  objectType: AuditObjectType;
  objectDetails: AuditDiffDetails;
  auditKey: string;
  diffValues?: AuditDiffValues;
};

type AuditDiffDetails = {
  id: string;
  name: string;
  location?: {
    id: string;
    name: string;
  };
};

type AuditDiffValues = {
  type?: "String" | "List";
  oldValue?: string;
  newValue?: string;
  oldValues?: string[];
  newValues?: string[];
  added?: string[];
  removed?: string[];
};

type AuditActor = {
  id: string;
  name: string;
  role?: UserRole;
};
