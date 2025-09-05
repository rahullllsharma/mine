import type { SupervisorTypes } from "@/components/templatesComponents/customisedForm.types";
import { DateTime } from "luxon";
import NextLink from "next/link";
import { BodyText, CaptionText, Icon } from "@urbint/silica";
import Link from "@/components/shared/link/Link";
import Table from "@/components/table/Table";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import StatusBadge from "../../../statusBadge/StatusBadge";

const getColumns = () => [
  {
    id: "formName",
    Header: "Form Name",
    width: 120,
    accessor: (listData: any) => {
      return (
        <NextLink href={`/template-forms/view?formId=${listData?.id}`} passHref>
          <Link label={listData?.title ? listData?.title : ""} allowWrapping />
        </NextLink>
      );
    },
  },
  {
    id: "status",
    Header: "Status",
    width: 50,
    accessor: (listData: any) => {
      return <StatusBadge status={listData?.status?.toUpperCase()} />;
    },
  },
  {
    id: "created_by",
    Header: "Created By",
    width: 80,
    accessor: (listData: any) => {
      return (
        <div className="truncate">{listData?.created_by?.user_name || ""}</div>
      );
    },
  },
  {
    id: "created_at",
    Header: "Created On",
    width: 80,
    accessor: (listData: any) =>
      listData?.created_at
        ? DateTime.fromISO(listData?.created_at).toFormat("LLL dd, yyyy")
        : "",
  },
  {
    id: "completed_at",
    Header: "Completed On",
    width: 90,
    accessor: (listData: any) =>
      listData?.completed_at
        ? DateTime.fromISO(listData?.completed_at).toFormat("LLL dd, yyyy")
        : "",
  },
  {
    id: "WorkPackageName",
    Header: "Project",
    width: 80,
    accessor: (listData: any) => {
      if (listData?.metadata?.work_package?.name == "undefined") return "";
      else return listData?.metadata?.work_package?.name;
    },
  },
  {
    id: "WorkPackage",
    Header: "Location",
    width: 120,
    accessor: (listData: any) => {
      const location_data = listData?.location_data;
      return (
        <div className="w-full">
          <div className="flex items-start gap-1 min-w-0 w-full">
            {location_data?.gps_coordinates?.latitude &&
            location_data?.gps_coordinates?.longitude ? (
              <Icon
                name="location"
                className="text-xl leading-5 text-neutral-shade-75 flex-shrink-0"
              />
            ) : (
              <div className="w-5 h-5"></div>
            )}
            <div className="min-w-0 flex-1 overflow-hidden">
              <Tooltip title={location_data?.name || ""}>
                <BodyText className="truncate sm:w-20 lg:w-20 xl:w-28 text-sm">
                  {location_data?.name}
                </BodyText>
              </Tooltip>
              <Tooltip title={location_data?.description || ""}>
                <CaptionText className="truncate sm:w-20 lg:w-20 xl:w-28 text-black ">
                  {location_data?.description || ""}
                </CaptionText>
              </Tooltip>
            </div>
          </div>
        </div>
      );
    },
  },
  {
    id: "region",
    Header: "region",
    width: 80,
    accessor: (listData: any) => {
      if (listData?.metadata?.region?.name == "undefined") return "";
      else return listData?.metadata?.region?.name;
    },
  },
  {
    id: "updated_by",
    Header: "Updated by",
    width: 80,
    accessor: (listData: any) => {
      return (
        <div className="truncate">{listData?.updated_by?.user_name || ""}</div>
      );
    },
  },
  {
    id: "updated_at",
    Header: "Updated On",
    width: 80,
    accessor: (listData: any) =>
      listData?.updated_at
        ? DateTime.fromISO(listData?.updated_at).toFormat("LLL dd, yyyy")
        : "",
  },
  {
    id: "report_date",
    Header: "Report Date",
    width: 90,
    accessor: (listData: any) =>
      listData?.report_start_date
        ? DateTime.fromISO(listData?.report_start_date).toFormat("LLL dd, yyyy")
        : "",
  },
  {
    id: "supervisor",
    Header: "Supervisor",
    width: 80,
    accessor: (listData: any) => {
      return (
        listData?.metadata?.supervisor
          ?.filter(
            (supervisor: SupervisorTypes) =>
              supervisor.name && supervisor.name.trim()
          )
          ?.map((supervisor: SupervisorTypes) => supervisor.name)
          .join(", ") || ""
      );
    },
  },
];

const TemplateFormTable = ({
  templateFormsData,
  isLoading = false,
}: {
  templateFormsData: any;
  isLoading?: boolean;
}): JSX.Element => {
  const columns = getColumns();

  return (
    <Table columns={columns} data={templateFormsData} isLoading={isLoading} />
  );
};

export default TemplateFormTable;
