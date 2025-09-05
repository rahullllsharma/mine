/* istanbul ignore file */
import type { HTMLAttributes } from "react";
import type { Form } from "../../types/formsList/formsList";
import { formatCamelCaseString, getFormattedDate } from "@/utils/date/helper";
import { getSupervisorNames } from "@/container/table/FormsTable";
import { useTenantStore } from "../../store/tenant/useTenantStore.store";
import StatusBadge from "../statusBadge/StatusBadge";
import CardRow from "./cardRow/CardRow";

type CardItemProps = Pick<HTMLAttributes<HTMLButtonElement>, "onClick"> & {
  formsData: Form;
  isLoading?: boolean;
};

function CardItemContent({ formsData }: { formsData: Form }): JSX.Element {
  const { formList } = useTenantStore(state => state.getAllEntities());
  const rawFormName = formsData?.__typename
    ? formatCamelCaseString(formsData?.__typename)
    : "";

  const formName =
    rawFormName === "Nat Grid Job Safety Briefing"
      ? "Distribution Job Safety Briefing"
      : rawFormName;

  return (
    <>
      <header className="text-neutral-shade-100 text-lg font-semibold">
        {formName}
      </header>
      <div className="mt-4">
        {formList.attributes.status?.visible && (
          <div className="flex text-sm items-center py-1.5">
            <span className="flex-1 text-neutral-shade-100 text-sm font-semibold">
              {formList.attributes.status.label}
            </span>
            <StatusBadge status={formsData.status} label={formsData.status} />
          </div>
        )}
        {formList.attributes.workPackage?.visible && (
          <CardRow label={formList.attributes.workPackage.label}>
            {formsData.workPackage?.name}
          </CardRow>
        )}
        {formList.attributes.location?.visible && (
          <>
            {(() => {
              const location = formsData.location
                ? formsData.location.name
                : formsData?.locationName;
              return (
                <CardRow label={formList.attributes.location.label}>
                  {location}
                </CardRow>
              );
            })()}
          </>
        )}
        {formList.attributes.createdBy?.visible && (
          <CardRow label={formList.attributes.createdBy.label}>
            {formsData.createdBy?.name}
          </CardRow>
        )}
        {formList.attributes.createdOn?.visible && (
          <CardRow label={formList.attributes.createdOn.label}>
            {formsData?.createdAt
              ? getFormattedDate(formsData?.createdAt, "short")
              : ""}
          </CardRow>
        )}
        {formList.attributes.updatedBy?.visible && (
          <CardRow label={formList.attributes.updatedBy.label}>
            {formsData.updatedBy?.name}
          </CardRow>
        )}
        {formList.attributes.updatedOn?.visible && (
          <CardRow label={formList.attributes.updatedOn.label}>
            {formsData?.updatedAt
              ? getFormattedDate(formsData?.updatedAt, "short")
              : ""}
          </CardRow>
        )}
        {formList.attributes.completedOn?.visible && (
          <CardRow label={formList.attributes.completedOn.label}>
            {formsData?.completedAt
              ? getFormattedDate(formsData?.completedAt, "short")
              : ""}
          </CardRow>
        )}
        {formList.attributes.date?.visible && (
          <CardRow label={formList.attributes.date.label}>
            {formsData?.date ? getFormattedDate(formsData?.date, "short") : ""}
          </CardRow>
        )}
        {formList.attributes.operatingHQ?.visible && (
          <CardRow label={formList.attributes.operatingHQ.label}>
            {formsData?.operatingHq}
          </CardRow>
        )}
        {formList.attributes.supervisor?.visible && (
          <CardRow label={formList.attributes.supervisor.label}>
            {getSupervisorNames(formsData)}
          </CardRow>
        )}
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

export default function FormCardItem({
  formsData,
  isLoading,
  onClick,
}: CardItemProps): JSX.Element {
  return (
    <div className="flex rounded bg-white shadow-5">
      {isLoading ? (
        <CardItemPlaceholder />
      ) : (
        <button className="flex-1 p-6 text-left" onClick={onClick}>
          <CardItemContent formsData={formsData} />
        </button>
      )}
    </div>
  );
}
