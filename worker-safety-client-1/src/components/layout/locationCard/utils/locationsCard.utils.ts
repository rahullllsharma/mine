import type { LocationCardDynamicProps } from "@/hooks/useTenantFeatures";
import type { ReactNode } from "react";
import type { Activity } from "@/types/activity/Activity";
import { createElement } from "react";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import { messages } from "@/locales/messages";
import { getFeatureLabels } from "@/utils/featureLabels";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

type OptionalPropsArgs = {
  workPackageType?: string;
  division?: string;
  region?: string;
  primaryAssignedPersonLocation?: string;
  activities?: Activity[];
  displayLocationCardDynamicProps: LocationCardDynamicProps;
};

type OptionalProps = {
  slots: string[];
  identifier: string | ReactNode;
};

type PrimaryAssignedPersonValues = {
  primaryAssignedPersonLocation?: string;
  isPrimaryAssignedPersonLocationVisible: boolean;
  primaryAssignedPersonActivity?: string[];
  isPrimaryAssignedPersonActivityVisible: boolean;
};

type TypeValues = {
  activityType: string[];
  isActivityTypeVisible: boolean;
  workPackageType: string;
  isWorkPackageTypeVisible: boolean;
};

type TenantSpecificProps = PrimaryAssignedPersonValues &
  TypeValues & {
    tenantValues: LocationCardDynamicProps;
  };

type TenantSpecificFields = {
  identifier: string | ReactNode;
  lastSlot: string;
};

type RelevantActivity = Partial<Activity>;

type ActivityValues = {
  activityTypes: string[];
  activitySupervisors: string[];
};

const getTooltipElement = (activityTypeNormalized: string) =>
  createElement(
    Tooltip,
    {
      title: activityTypeNormalized,
      position: "top",
      className: "capitalize",
    },
    messages.multiple
  );

const generateIdentifierInfo = (
  value: string,
  {
    activityType,
    isActivityTypeVisible,
    workPackageType,
    isWorkPackageTypeVisible,
  }: TypeValues
) => {
  const { VALUES } = getFeatureLabels();

  const isVisible =
    value === VALUES.ACTIVITY
      ? isActivityTypeVisible
      : isWorkPackageTypeVisible;

  if (!isVisible) {
    return "";
  }

  // default VALUES.WORK_PACKAGE
  let assignedValue: string | ReactNode = workPackageType;
  if (value === VALUES.ACTIVITY) {
    const activityTypeNormalized = activityType.join(" ");

    assignedValue =
      activityType.length > 1
        ? getTooltipElement(activityTypeNormalized)
        : activityTypeNormalized;
  }

  return assignedValue ?? "";
};

const generateLastSlotInfo = (
  value: string,
  {
    isPrimaryAssignedPersonActivityVisible,
    primaryAssignedPersonActivity,
    isPrimaryAssignedPersonLocationVisible,
    primaryAssignedPersonLocation,
  }: PrimaryAssignedPersonValues
) => {
  const { VALUES } = getFeatureLabels();

  const isVisible =
    value === VALUES.ACTIVITY
      ? isPrimaryAssignedPersonActivityVisible
      : isPrimaryAssignedPersonLocationVisible;

  if (!isVisible) {
    return "";
  }

  // default VALUES.LOCATION
  let assignedValue = primaryAssignedPersonLocation;
  if (value === VALUES.ACTIVITY) {
    assignedValue = (primaryAssignedPersonActivity ?? []).join(", ");
  }

  return assignedValue ?? "";
};

const getTenantSpecificFields = ({
  tenantValues,
  primaryAssignedPersonLocation,
  isPrimaryAssignedPersonLocationVisible,
  primaryAssignedPersonActivity,
  isPrimaryAssignedPersonActivityVisible,
  activityType,
  isActivityTypeVisible,
  workPackageType,
  isWorkPackageTypeVisible,
}: TenantSpecificProps): TenantSpecificFields => {
  const response: TenantSpecificFields = {
    identifier: "",
    lastSlot: "",
  };

  response.identifier = generateIdentifierInfo(tenantValues.identifier, {
    activityType,
    isActivityTypeVisible,
    workPackageType,
    isWorkPackageTypeVisible,
  });
  response.lastSlot = generateLastSlotInfo(tenantValues.slot3, {
    isPrimaryAssignedPersonActivityVisible,
    primaryAssignedPersonActivity,
    isPrimaryAssignedPersonLocationVisible,
    primaryAssignedPersonLocation,
  });

  return response;
};

const getCardOptionalProps = ({
  workPackageType,
  division,
  region,
  primaryAssignedPersonLocation,
  activities,
  displayLocationCardDynamicProps,
}: OptionalPropsArgs): OptionalProps => {
  const { getAllEntities } = useTenantStore.getState();
  const { workPackage, location, activity } = getAllEntities();
  const { activityTypes, activitySupervisors } =
    getActivitiesValues(activities);

  const slots: string[] = [];

  if (workPackage.attributes.division.visible && division) {
    slots.push(division);
  }

  if (workPackage.attributes.region.visible && region) {
    slots.push(region);
  }

  const { identifier, lastSlot } = getTenantSpecificFields({
    tenantValues: displayLocationCardDynamicProps,
    primaryAssignedPersonLocation,
    isPrimaryAssignedPersonLocationVisible:
      location.attributes.primaryAssignedPerson.visible,
    primaryAssignedPersonActivity: activitySupervisors,
    isPrimaryAssignedPersonActivityVisible:
      workPackage.attributes.primaryAssignedPerson.visible,
    activityType: activityTypes ?? "",
    isActivityTypeVisible: activity.attributes.libraryActivityType.visible,
    workPackageType: workPackageType ?? "",
    isWorkPackageTypeVisible: workPackage.attributes.workPackageType.visible,
  });

  if (lastSlot) {
    slots.push(lastSlot);
  }

  return {
    slots,
    identifier,
  };
};

const getActivitiesValues = (activities: RelevantActivity[] = []) =>
  activities.reduce<ActivityValues>(
    (acc, entry) => {
      if (entry.libraryActivityType?.name) {
        acc.activityTypes.push(entry.libraryActivityType?.name);
      }

      if (entry.supervisors && entry.supervisors?.length > 0) {
        acc.activitySupervisors.push(
          ...entry.supervisors.map(supervisorEntry => supervisorEntry.name)
        );
      }

      return acc;
    },
    {
      activityTypes: [],
      activitySupervisors: [],
    }
  );

export { getCardOptionalProps, getActivitiesValues, getTooltipElement };
export type { RelevantActivity, OptionalPropsArgs };
