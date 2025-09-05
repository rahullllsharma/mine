import Table from "@/components/table/Table";
import { CircularLoader } from "@/components/uploadLoader/uploadLoader";
import { formatRelativeOrAbsoluteDate } from "@/utils/date/helper";
import { Icon } from "@urbint/silica";
import { useMemo } from "react";
import type { Column } from "react-table";

export default function DataExportPreviewTable({
  data,
  onDownload,
  downloadingId,
}: {
  data: any;
  onDownload: (previewData: any) => void;
  downloadingId: string | null;
}) {
  const columns: Column<any>[] = useMemo(
    () => [
      {
        Header: "Data Source Name",
        width: 150,
        accessor: previewData => previewData.name,
      },
      {
        Header: "Uploaded File",
        width: 150,
        accessor: previewData => previewData.file_name,
      },
      {
        Header: "Last Updated By",
        width: 150,
        accessor: previewData => {
          const username = previewData.created_by_username || "";
          const formattedDate = previewData.updated_at
            ? formatRelativeOrAbsoluteDate(previewData.updated_at)
            : "";

          return formattedDate ? (
            <span>
              {username}{" "}
              <span className="text-gray-500">({formattedDate})</span>
            </span>
          ) : (
            username
          );
        },
      },
      {
        Header: "Download",
        width: 50,
        accessor: previewData => (
          <div className="flex items-center justify-center pl-2 pr-4">
            {downloadingId === previewData.id ? (
              <CircularLoader />
            ) : (
              <Icon
                name="download"
                onClick={() => onDownload(previewData)}
                className="text-lg text-neutral-shade-75 mr-2 border-2 pl-2 pr-2 cursor-pointer"
              />
            )}
          </div>
        ),
      },
    ],
    [downloadingId, onDownload]
  );

  return <Table columns={columns} data={data} isLoading={false} />;
}
