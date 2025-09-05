import type { EntityAttributeMap } from "@/store/tenant/types";
import type { Form } from "@/types/formsList/formsList";
import NextLink from "next/link";
import { Icon } from "@urbint/silica";
import Link from "@/components/shared/link/Link";
import Table from "@/components/table/Table";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import StatusBadge from "@/components/statusBadge/StatusBadge";
import { formatCamelCaseString, getFormattedDate } from "@/utils/date/helper";

const getColumns = ({
  formName,
  status,
  location,
  formId,
  createdBy,
  createdOn,
  workPackage,
  updatedOn,
  updatedBy,
  completedOn,
  date,
  operatingHQ,
  supervisor,
}: EntityAttributeMap) => [
  {
    id: "formName",
    Header: formName.label,
    width: 120,
    // eslint-disable-next-line react/display-name
    accessor: (formsData: Form) => {
      let pathname;
      let query = {};

      switch (formsData?.__typename) {
        case "DailyReport":
          pathname = `/projects/${[formsData?.workPackage?.id]}/locations/${[
            formsData?.location?.id,
          ]}/reports/${[formsData.id]}`;
          query = { pathOrigin: "forms" };
          break;
        case "JobSafetyBriefing":
          pathname = `/jsb`;
          query = {
            locationId: [formsData?.location?.id],
            jsbId: [formsData?.id],
            pathOrigin: "forms",
          };
          break;
        case "EnergyBasedObservation":
          pathname = `/ebo`;
          query = {
            eboId: [formsData?.id],
          };
          break;
        case "Distribution Job Safety Briefing":
          pathname = formsData?.id
            ? `/jsb-share/natgrid/${formsData.id}`
            : `/forms`;
          break;
        default:
          pathname = ""; // Default value if no match is found
          break;
      }

      return (
        <NextLink href={{ pathname, query }} passHref>
          <Link
            label={
              formsData?.__typename
                ? formatCamelCaseString(formsData?.__typename)
                : ""
            }
            allowWrapping
          />
        </NextLink>
      );
    },
  },
  ...(formId?.visible
    ? [
        {
          id: "formId",
          Header: formId.label ?? "Form ID",
          width: 120,
          accessor: (formsData: Form) => formsData?.formId,
        },
      ]
    : []),

  ...(location.visible
    ? [
        {
          id: "location",
          Header: location?.label,
          width: 150,
          accessor: (formsData: Form) => {
            const adHocLocation = formsData.locationName || "";
            const adHocLocationSubstring = adHocLocation?.substring(0, 40);
            const adHocLocationSuffix =
              (adHocLocation?.length ?? 0) > 40 ? "..." : "";
            const adHocLocationLabel = `${adHocLocationSubstring}${adHocLocationSuffix}`;

            const label = formsData.location
              ? formsData.location.name
              : adHocLocationLabel;
            const multiLocationCount = formsData?.multipleLocation;

            return (
              <div className="flex items-center gap-1">
                {formsData?.__typename == "Distribution Job Safety Briefing" &&
                formsData?.locationName ? (
                  multiLocationCount ? (
                    <Icon name="multi_location" />
                  ) : (
                    <Icon name="location" />
                  )
                ) : (
                  ""
                )}
                <span>{label}</span>
              </div>
            );
          },
        },
      ]
    : []),
  ...(status.visible
    ? [
        {
          id: "status",
          Header: status?.label,
          width: 120,
          accessor: (formsData: Form) => (
            <StatusBadge status={formsData?.status} />
          ),
        },
      ]
    : []),
  ...(workPackage.visible
    ? [
        {
          id: "workPackage",
          Header: workPackage?.label,
          width: 150,
          accessor: (formsData: Form) => formsData?.workPackage?.name,
        },
      ]
    : []),

  ...(createdBy.visible
    ? [
        {
          id: "createdBy",
          Header: createdBy?.label,
          width: 120,
          accessor: (formsData: Form) => formsData?.createdBy?.name,
        },
      ]
    : []),
  ...(createdOn.visible
    ? [
        {
          id: "createdOn",
          Header: createdOn.label,
          width: 100,
          accessor: (formsData: Form) =>
            formsData?.createdAt
              ? getFormattedDate(formsData?.createdAt, "long")
              : "",
        },
      ]
    : []),
  ...(updatedBy.visible
    ? [
        {
          id: "updatedBy",
          Header: updatedBy.label,
          width: 100,
          accessor: (formsData: Form) => formsData?.updatedBy?.name,
        },
      ]
    : []),
  ...(updatedOn.visible
    ? [
        {
          id: "updatedOn",
          Header: updatedOn.label,
          width: 100,
          accessor: (formsData: Form) =>
            formsData?.updatedAt
              ? getFormattedDate(formsData?.updatedAt, "long")
              : "",
        },
      ]
    : []),
  ...(completedOn.visible
    ? [
        {
          id: "completedOn",
          Header: completedOn.label,
          width: 100,
          accessor: (formsData: Form) =>
            formsData?.completedAt
              ? getFormattedDate(formsData?.completedAt, "long")
              : "",
        },
      ]
    : []),
  ...(date.visible
    ? [
        {
          id: "reportDate",
          Header: date.label,
          width: 100,
          accessor: (formsData: Form) =>
            formsData?.date ? getFormattedDate(formsData?.date, "long") : "",
        },
      ]
    : []),
  ...(operatingHQ.visible
    ? [
        {
          id: "operatingHq",
          Header: operatingHQ.label,
          width: 100,
          accessor: (formsData: Form) => formsData?.operatingHq,
        },
      ]
    : []),
  ...(supervisor.visible
    ? [
        {
          id: "supervisor",
          Header: supervisor.label,
          width: 100,
          accessor: (formsData: Form) => getSupervisorNames(formsData) || "",
        },
      ]
    : []),
];

export const getSupervisorNames = (formsData: Form) => {
  return formsData?.supervisor
    ?.map(supervisors => supervisors.name?.trim())
    .filter(name => name)
    .join(", ");
};

export default function FormsTable({
  formsData,
  isLoading = false,
}: {
  formsData: Form[];
  isLoading?: boolean;
}): JSX.Element {
  const { formList } = useTenantStore(state => state.getAllEntities());

  return (
    <Table
      columns={getColumns(formList.attributes)}
      data={formsData}
      isLoading={isLoading}
    />
  );
}
