/* eslint-disable no-negated-condition */
import type { HTMLAttributes } from "react";

import type { SupervisorTypes } from "@/components/templatesComponents/customisedForm.types";
import { useRouter } from "next/router";

import { DateTime } from "luxon";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import CardRow from "../../listCardItem/cardRow/CardRow";
import StatusBadge from "../../../statusBadge/StatusBadge";

type CardItemProps = Pick<HTMLAttributes<HTMLButtonElement>, "onClick"> & {
  templateFormsData: any;
  isLoading?: boolean;
  onView: (id: string) => void;
};

function CardItemContent({ templateFormsData }: CardItemProps): JSX.Element {
  const { templateForm } = useTenantStore(state => state.getAllEntities());
  return (
    <>
      <header className="text-neutral-shade-100 text-lg font-semibold flex items-center">
        {templateFormsData?.title}
      </header>
      <div className="mt-1">
        <CardRow label={templateForm.attributes.status.label || "Status"}>
          {" "}
          <StatusBadge
            status={templateFormsData?.status?.toUpperCase() || ""}
          />
        </CardRow>
      </div>
      <div className="mt-1">
        <CardRow
          label={templateForm.attributes.createdBy.label || "Created By"}
        >
          {templateFormsData?.created_by?.user_name || ""}
        </CardRow>
      </div>
      <div className="mt-1">
        <CardRow
          label={templateForm.attributes.createdOn.label || "Created On"}
        >
          {templateFormsData?.metadata?.created_at === "undefined"
            ? ""
            : DateTime.fromISO(templateFormsData?.created_at).toFormat(
                "LLL dd, yyyy"
              ) || ""}
        </CardRow>
      </div>
      <div className="mt-1">
        <CardRow
          label={templateForm.attributes.completedOn.label || "Completed On"}
        >
          {templateFormsData?.completed_at !== null
            ? DateTime.fromISO(templateFormsData?.completed_at).toFormat(
                "LLL dd, yyyy"
              )
            : ""}
        </CardRow>
      </div>
      <div className="mt-1">
        <CardRow label={templateForm.attributes.Project.label || "Project"}>
          {templateFormsData?.metadata?.work_package?.name === "undefined"
            ? ""
            : templateFormsData?.metadata?.work_package?.name}
        </CardRow>
      </div>
      <div className="mt-1">
        <CardRow label={templateForm.attributes.location.label || "Location"}>
          {templateFormsData?.metadata?.location?.name === "undefined"
            ? ""
            : templateFormsData?.metadata?.location?.name}
        </CardRow>
      </div>
      <div className="mt-1">
        <CardRow label={templateForm.attributes.region.label || "Region"}>
          {templateFormsData?.metadata?.region?.name === "undefined"
            ? ""
            : templateFormsData?.metadata?.region?.name}
        </CardRow>
      </div>
      <div className="mt-1">
        <CardRow
          label={templateForm.attributes.updatedBy.label || "Updated By"}
        >
          {templateFormsData?.updated_by?.user_name || ""}
        </CardRow>
      </div>

      <div className="mt-1">
        <CardRow
          label={templateForm.attributes.updatedOn.label || "Updated On"}
        >
          {DateTime.fromISO(templateFormsData?.updated_at).toFormat(
            "LLL dd, yyyy"
          ) || ""}
        </CardRow>
      </div>
      <div className="mt-1">
        <CardRow
          label={templateForm.attributes.reportDate.label || "Report Date"}
        >
          {templateFormsData?.report_start_date
            ? DateTime.fromISO(templateFormsData.report_start_date).toFormat(
                "LLL dd, yyyy"
              )
            : ""}
        </CardRow>
      </div>
      <div className="mt-1">
        <CardRow
          label={templateForm.attributes?.supervisor?.label || "Supervisor"}
        >
          {templateFormsData?.metadata?.supervisor
            ?.map((supervisor: SupervisorTypes) => supervisor.name)
            .join(", ") || ""}
        </CardRow>
      </div>
    </>
  );
}
function CardItemPlaceholder(): JSX.Element {
  const itemRowPlaceholder = (
    <div className="flex border-solid border-t my-1 py-1 text-sm ">
      <span className="flex-1">
        <div className="h-3 rounded animate-pulse w-1/3 bg-gray-300"></div>
      </span>
      <span className="h-3 rounded animate-pulse w-2/5 bg-gray-200"></span>
    </div>
  );
  return (
    <div className="flex-1 p-6">
      <header className="h-5 rounded animate-pulse w-1/2 bg-gray-300" />
      <div className="mt-4">
        {itemRowPlaceholder}
        {itemRowPlaceholder}
        {itemRowPlaceholder}
        {itemRowPlaceholder}
      </div>
    </div>
  );
}

function TemplateFormCardView({
  templateFormsData,
  isLoading,
  onView,
}: CardItemProps): JSX.Element {
  const router = useRouter();
  const formNavigator = () => {
    const pathname = `/template-forms/view`;
    const query = `formId=${templateFormsData?.id}`;
    router.push({
      pathname,
      query,
    });
  };
  return (
    <div className="flex rounded bg-white shadow-5">
      {isLoading ? (
        <CardItemPlaceholder />
      ) : (
        <button
          className="flex-1 p-6 text-left"
          onClick={() => formNavigator()}
        >
          <div className="flex-1 p-6 text-left">
            <CardItemContent
              templateFormsData={templateFormsData}
              onView={onView}
            />
          </div>
        </button>
      )}
    </div>
  );
}

export default TemplateFormCardView;
