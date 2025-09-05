import axiosRest from "@/api/restApi";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { CircularLoader } from "@/components/uploadLoader/uploadLoader";
import useRestMutation from "@/hooks/useRestMutation";
import { BodyText, SectionHeading } from "@urbint/silica";
import type { AxiosError } from "axios";
import { useContext, useEffect, useState } from "react";
import DataExportPreviewTable from "./DataExportPreviewTable";

export default function DataExport({
  setDataSources,
  isRefreshData,
  navigateToDataImport,
}: {
  setDataSources: (dataSources: string[]) => void;
  isRefreshData: boolean;
  navigateToDataImport: () => void;
}) {
  const [fetchFromSrcData, setFetchFromSrcData] = useState<any[]>([]);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const toastCtx = useContext(ToastContext);

  const { mutate: fetchFileImportedData, isLoading: isFetching } =
    useRestMutation({
      endpoint: `uploads/data-sources/`,
      method: "get",
      axiosInstance: axiosRest,
      dtoFn: data => data,
      mutationOptions: {
        onSuccess: (responseData: any) => {
          setFetchFromSrcData(responseData.data);
          setDataSources(responseData.data.map((item: any) => item.name));
        },
        onError: (error: AxiosError) => {
          console.log(error);
        },
      },
    });

  const { mutate: downloadFile } = useRestMutation<any>({
    endpoint: (data: any) => `/uploads/data-sources/${data.id}/download`,
    method: "get",
    axiosInstance: axiosRest,
    axiosConfig: {
      responseType: "blob",
    },
    mutationOptions: {
      onSuccess: async (response: any, variables: any) => {
        setDownloadingId(null);

        const blob = new Blob([response.data], {
          type:
            response.headers?.["content-type"] || "application/octet-stream",
        });

        // Use the original uploaded filename
        const filename =
          variables.originalFilename || `data-source-${Date.now()}.csv`;

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      },
      onError: (error: AxiosError) => {
        setDownloadingId(null);

        console.log("error", error);
        toastCtx?.pushToast("error", "File download failed");
      },
    },
  });

  useEffect(() => {
    fetchFileImportedData({});
  }, [isRefreshData]);

  const handleDownload = async (previewData: any) => {
    setDownloadingId(previewData.id);
    downloadFile({
      id: previewData.id,
      originalFilename: previewData.file_name,
    });
  };

  const NoDataSrcAvailable: React.FC = () => {
    return (
      <div className="flex flex-col items-center justify-center bg-gray-50 gap-4 pt-8 pb-8 pl-8 pr-2 mt-9 rounded-md">
        <BodyText className="text-neutral-shade-75 font-semibold">
          No Data Sources Available
        </BodyText>
        <p className="text-neutral-shade-75 text-sm">
          Start by
          <span
            className="text-[#007899] hover:text-gray-800 cursor-pointer"
            onClick={navigateToDataImport}
          >
            {" "}
            importing a file
          </span>{" "}
          to populate field options in your templates and skip manual entry.
        </p>
      </div>
    );
  };

  return (
    <>
      <SectionHeading className="text-xl font-semibold">
        All Data Sources
      </SectionHeading>
      <BodyText className="text-neutral-shade-75 mb-3">
        To update a data source, download it, make your edits, and re-upload
        with the same filename to overwrite.
      </BodyText>
      {isFetching ? (
        <div className="flex items-center justify-center min-h-[410px]">
          <CircularLoader className="text-gray-500" />
        </div>
      ) : fetchFromSrcData.length > 0 ? (
        <div className="min-h-[410px] max-h-[410px] overflow-y-auto mt-3  no-scrollbar">
          <DataExportPreviewTable
            data={fetchFromSrcData}
            onDownload={handleDownload}
            downloadingId={downloadingId}
          />
        </div>
      ) : (
        <NoDataSrcAvailable />
      )}
    </>
  );
}
