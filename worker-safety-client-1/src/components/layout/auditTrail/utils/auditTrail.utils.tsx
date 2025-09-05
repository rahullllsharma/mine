import type { AuditEvent } from "@/types/auditTrail/AuditEvent";
import { Icon } from "@urbint/silica";
import {
  AuditActionType,
  auditActionTypeLabel,
} from "@/types/auditTrail/AuditActionType";
import { getAuditTrailLabels } from "@/locales/messages";
import { AuditObjectType } from "@/types/auditTrail/AuditObjectType";

const highlightedTextClasses = "text-brand-urbint-60 font-semibold";
const noValueLabel = (
  <span className="font-normal text-neutral-shade-58">None</span>
);

// as we're not getting the workPackage status specific key from the BE, we are adding the prefix ourselves for now
// the intent is to have these specific labels ("pending", "active"...) fully customizable by the clients (for the work packages use case)
export const getProjectStatusKey = (
  objectType: AuditObjectType,
  auditKey: string,
  value: string
) => {
  if (objectType === AuditObjectType.PROJECT && auditKey === "project_status") {
    return `${auditKey}_${value}`;
  }
  return "";
};

const getDiffValuesLabel = (projectStatusKey: string, diffValue: string) => {
  const labels = getAuditTrailLabels();
  return (
    labels[projectStatusKey] || labels[diffValue] || diffValue || noValueLabel
  );
};

const buildContentForCreateOrDeleteCard = (
  objectType: AuditObjectType,
  actionType: AuditActionType,
  name: string
): JSX.Element => {
  const labels = getAuditTrailLabels();
  return (
    <>
      <span>{`${auditActionTypeLabel[actionType]} ${
        labels[objectType.toLowerCase()]
      }: `}</span>
      <span className={highlightedTextClasses}>{name}</span>
    </>
  );
};

const buildContentForUpdateCard = (
  objectType: AuditObjectType,
  actionType: AuditActionType,
  auditKey: string,
  name: string,
  oldValue: string,
  newValue: string
): JSX.Element => {
  const labels = getAuditTrailLabels();
  const oldProjectStatusKey = getProjectStatusKey(
    objectType,
    auditKey,
    oldValue
  );

  const newProjectStatusKey = getProjectStatusKey(
    objectType,
    auditKey,
    newValue
  );
  return (
    <>
      <span>{`${auditActionTypeLabel[actionType]} `}</span>
      <span className={highlightedTextClasses}>{`${labels[auditKey]}`}</span>
      <span>{` in the `}</span>
      <span className={highlightedTextClasses}>{`${
        labels[objectType.toLowerCase()]
      }`}</span>
      {/* when we're dealing with project audit events, we won't need to mention which project the Audit events are referring to */}
      {objectType !== AuditObjectType.PROJECT && (
        <span className={highlightedTextClasses}>{`: ${name}`}</span>
      )}
      <span>{` from `}</span>
      <span className={highlightedTextClasses}>
        {getDiffValuesLabel(oldProjectStatusKey, oldValue)}
      </span>
      <span>
        <Icon
          name="long_right"
          className="mx-1 text-base text-neutral-shade-75"
        />
      </span>
      <span className={highlightedTextClasses}>
        {getDiffValuesLabel(newProjectStatusKey, newValue)}
      </span>
    </>
  );
};

const buildContentForMultiSelectUpdate = (
  auditKey: string,
  objectType: AuditObjectType,
  addedItems: string[] = [],
  removedItems: string[] = []
): JSX.Element => {
  const labels = getAuditTrailLabels();
  if (addedItems?.length && removedItems?.length) {
    return (
      <>
        <span>{`Added `}</span>
        <span className={highlightedTextClasses}>{labels[auditKey]}</span>
        <span>{` in the `}</span>
        <span className={highlightedTextClasses}>
          {labels[objectType.toLowerCase()]}
        </span>
        <span>: </span>
        <span className={highlightedTextClasses}>{addedItems.join(", ")}</span>
        <span>{` and deleted: `}</span>
        <span className={highlightedTextClasses}>
          {removedItems.join(", ")}
        </span>
      </>
    );
  }

  const [action, updatedItems = []] = addedItems?.length
    ? ["Added", addedItems]
    : ["Deleted", removedItems];

  return (
    <>
      <span>{`${action} `} </span>
      <span className={highlightedTextClasses}>{labels[auditKey]}</span>
      <span>{` in the `}</span>
      <span className={highlightedTextClasses}>
        {labels[objectType.toLowerCase()]}
      </span>
      <span>: </span>
      <span className={highlightedTextClasses}>{updatedItems.join(", ")}</span>
    </>
  );
};

export const getAuditCardContent = ({
  objectType,
  actionType,
  objectDetails,
  diffValues,
  auditKey,
}: AuditEvent): JSX.Element => {
  if (
    actionType === AuditActionType.CREATED ||
    actionType === AuditActionType.DELETED
  ) {
    return buildContentForCreateOrDeleteCard(
      objectType,
      actionType,
      objectDetails.name
    );
  }
  if (diffValues?.type === "List") {
    return buildContentForMultiSelectUpdate(
      auditKey,
      objectType,
      diffValues.added as string[],
      diffValues.removed as string[]
    );
  }

  return buildContentForUpdateCard(
    objectType,
    actionType,
    auditKey,
    objectDetails.name,
    diffValues?.oldValue as string,
    diffValues?.newValue as string
  );
};

// DAILY INSPECTION REPORT - AUDIT CARDS CONTENT

const buildDIRCardContentForCreateOrDelete = (
  objectType: AuditObjectType,
  actionType: AuditActionType
): JSX.Element => {
  const labels = getAuditTrailLabels();
  return (
    <>
      <span>{auditActionTypeLabel[actionType]} </span>
      <span className={highlightedTextClasses}>
        {labels[objectType.toLowerCase()]}
      </span>
    </>
  );
};

const buildDIRCardContentForUpdate = (
  auditKey: string,
  newValue: string,
  oldValue: string,
  objectType: AuditObjectType
): JSX.Element => {
  const labels = getAuditTrailLabels();
  if (auditKey === "dailyReport_status" && newValue === "complete") {
    return (
      <>
        <span>Completed a </span>
        <span className={highlightedTextClasses}>
          {labels[objectType.toLowerCase()]}
        </span>
      </>
    );
  } else if (
    auditKey === "dailyReport_status" &&
    oldValue === "complete" &&
    newValue === "in_progress"
  ) {
    return (
      <>
        <span>Re-opened a </span>
        <span className={highlightedTextClasses}>
          {labels[objectType.toLowerCase()]}
        </span>
      </>
    );
  }
  // for now, the only update event we will be dealing with, is when the report is completed (handled above)
  // the remaining scenarios will be addressed in the next iteration (WSAPP-554)
  return <></>;
};

export const getDIRCardContent = ({
  actionType,
  objectType,
  auditKey,
  diffValues,
}: AuditEvent): JSX.Element => {
  if (
    actionType === AuditActionType.CREATED ||
    actionType === AuditActionType.DELETED
  ) {
    return buildDIRCardContentForCreateOrDelete(objectType, actionType);
  }
  return buildDIRCardContentForUpdate(
    auditKey,
    diffValues?.newValue as string,
    diffValues?.oldValue as string,
    objectType
  );
};
