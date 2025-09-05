export enum AuditActionType {
  CREATED = "CREATED",
  UPDATED = "UPDATED",
  DELETED = "DELETED",
}

export const auditActionTypeLabel = {
  [AuditActionType.CREATED]: "Added a",
  [AuditActionType.UPDATED]: "Updated the",
  [AuditActionType.DELETED]: "Deleted a",
};
