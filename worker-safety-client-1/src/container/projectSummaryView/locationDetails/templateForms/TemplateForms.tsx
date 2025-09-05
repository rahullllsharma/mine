import type { TemplatesForm } from "@/types/Templates/TemplateLists";
import type { Location } from "@/types/project/Location";
import cx from "classnames";
import { ActionLabel, Icon } from "@urbint/silica";
import { DateTime } from "luxon";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import { getFormattedDate, getFormattedShortTime } from "@/utils/date/helper";
import StatusBadge from "@/components/statusBadge/StatusBadge";
import { useAuthStore } from "@/store/auth/useAuthStore.store";

const convertDateToLocalZone = (date: string): string => {
  if (!date) return "";
  return DateTime.fromISO(`${date}Z` as string)
    .toLocal()
    .toString();
};

const getHeaderCardText = (templateForm: TemplatesForm): string => {
  const isInProgress = templateForm?.status === "in_progress";

  let infoText = `${getFormattedDate(
    templateForm.created_at as string,
    "long"
  )} at ${getFormattedShortTime(
    convertDateToLocalZone(templateForm.created_at ?? "")
  )} by ${templateForm.created_by?.user_name}`;

  let subHeaderText = `Created on ${infoText}`;

  if (!isInProgress) {
    infoText = `${getFormattedDate(
      templateForm.updated_at as string,
      "long"
    )} at ${getFormattedShortTime(
      convertDateToLocalZone(templateForm.updated_at ?? "")
    )} by ${templateForm.updated_by?.user_name}`;

    subHeaderText = `Completed ${infoText}`;
  }

  return subHeaderText;
};

type TemplateFormsSectionProps = {
  templateForm: TemplatesForm;
  viewReportFn: () => void;
  location: Location;
};

function TemplateFormsSection({
  templateForm,
  viewReportFn,
}: TemplateFormsSectionProps): JSX.Element {
  const isInProgress = templateForm?.status === "in_progress";

  const taskHeader = (
    <TemplateFormHeader
      templateForm={templateForm}
      isInProgress={isInProgress}
      viewReportFn={viewReportFn}
    />
  );

  return (
    <TaskCard
      className={cx({
        ["border-brand-gray-60"]: isInProgress,
        ["border-brand-urbint-40"]: !isInProgress,
      })}
      isOpen
      taskHeader={taskHeader}
    />
  );
}

export default function TemplateForms({
  element,
  viewReportFn,
  location,
}: {
  element: TemplatesForm;
  viewReportFn: () => void;
  location: Location;
}): JSX.Element {
  return (
    <TemplateFormsSection
      key={element.id}
      templateForm={element}
      viewReportFn={viewReportFn}
      location={location}
    />
  );
}

type TemplateFormsHeaderProps = {
  templateForm: TemplatesForm;
  isInProgress: boolean;
  viewReportFn: () => void;
};

type TemplateFormsIconProps = {
  userPermissions: string[];
  isOwn: boolean;
  isCompleted: boolean;
};

const getIconNameBasedOnPermissions = ({
  userPermissions,
  isOwn,
  isCompleted,
}: TemplateFormsIconProps) => {
  const canEdit =
    userPermissions.includes("EDIT_DELETE_ALL_CWF") ||
    (!isCompleted &&
      isOwn &&
      userPermissions.includes("EDIT_DELETE_OWN_CWF")) ||
    (isCompleted && userPermissions.includes("ALLOW_EDITS_AFTER_EDIT_PERIOD"));

  if (userPermissions.includes("CREATE_CWF") && canEdit) {
    return "edit";
  }

  return "show";
};

const TemplateFormIcon = ({
  userPermissions,
  isOwn,
  isCompleted,
}: TemplateFormsIconProps) => {
  const iconName = getIconNameBasedOnPermissions({
    userPermissions,
    isOwn,
    isCompleted,
  });
  return <Icon name={iconName} className="text-xl" />;
};

function TemplateFormHeader({
  templateForm,
  isInProgress,
  viewReportFn,
}: TemplateFormsHeaderProps): JSX.Element {
  const iconName = isInProgress ? "pie_chart_25" : "circle_check";
  const iconClassName = isInProgress
    ? "text-brand-gray-60"
    : "text-brand-urbint-40";
  const { title, status } = templateForm;
  const {
    me: { id: userId, permissions: userPermissions },
  } = useAuthStore();
  const isOwn = templateForm?.created_by?.id === userId;
  const isCompleted = templateForm?.status === "completed";

  return (
    <>
      <div
        className="flex flex-row flex-1 justify-between items-center p-3 cursor-pointer"
        onClick={viewReportFn}
      >
        <div className="w-full">
          <div className="flex flex-auto m-0 items-center gap-3 w-full md:flex-initial md:gap-4 md:w-auto md:ml-1 md:mr-4 justify-between">
            <div className="text-left text-base text-neutral-shade-100 font-bold flex flex-auto m-0 items-center gap-3 w-full md:flex-initial md:gap-4 md:w-auto md:ml-1 md:mr-4">
              <Icon name={iconName} className={cx("text-xl", iconClassName)} />
              <div className="flex flex-col gap-2">
                <div className="flex flex-row gap-2">
                  <ActionLabel className="font-semibold">{title}</ActionLabel>
                  {status && <StatusBadge status={status.toUpperCase()} />}
                </div>
                <span className="text-tiny font-medium text-neutral-shade-58">
                  {getHeaderCardText(templateForm)}
                </span>
              </div>
            </div>
            <div>
              <TemplateFormIcon
                userPermissions={userPermissions}
                isOwn={isOwn}
                isCompleted={isCompleted}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
