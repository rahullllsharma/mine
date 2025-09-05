import { BodyText, SectionHeading } from "@urbint/silica";
import type { AxiosError } from "axios";
import { useContext, useMemo, useState } from "react";

import axiosRest from "@/api/restApi";
import { InputRaw } from "@/components/forms/Basic/Input";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import ErrorBanner from "@/components/templatesComponents/ErrorBanner/ErrorBanner";
import WarningBanner from "@/components/templatesComponents/WarningBanner/WarningBanner";
import FileUploader from "@/components/upload/FileUploader";
import useRestMutation from "@/hooks/useRestMutation";
import { parseExcelMetadata } from "@/utils/excel/excelUtils";
import DataImportPreviewTable from "./DataImportPreviewTable";

type ExcelColumnData = {
  column: string;
  exampleData: string;
};

type Props = {
  onCancel: () => void;
  dataSources: string[];
  onFileImportSuccess: (isSuccess: boolean) => void;
};

export default function DataImport({
  onCancel,
  dataSources,
  onFileImportSuccess,
}: Props) {
  const [data, setData] = useState<ExcelColumnData[]>([]);
  const [showOverwriteModal, setShowOverwriteModal] = useState(false);
  const [errorBannerDetails, setErrorBannerDetails] = useState<{
    isError: boolean;
    message: string;
  }>({ isError: false, message: "" });
  const [fileName, setFileName] = useState<string>("");
  const [fileMetadata, setFileMetadata] = useState<{
    rowCount: number;
    columnCount: number;
  }>({ rowCount: 0, columnCount: 0 });
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [validationWarning, setValidationWarning] = useState<string>("");
  const toastCtx = useContext(ToastContext);
  const [loading, setLoading] = useState(false);

  const isDuplicate = useMemo(
    () => dataSources.includes(fileName.split(".")[0]),
    [dataSources, fileName]
  );

  const { mutate: importFile } = useRestMutation({
    endpoint: `uploads/data-sources/`,
    method: "post",

    axiosInstance: axiosRest,
    dtoFn: (dataForm: { file: File; data_source_name: string }) => {
      const formData = new FormData();
      formData.append("file", dataForm.file);
      formData.append("data_source_name", dataForm.data_source_name);
      return formData;
    },
    mutationOptions: {
      onSuccess: () => {
        handleFileImportSuccess();
        setLoading(false);
        handleCancel();
        onFileImportSuccess(true);
      },
      onError: (error: AxiosError) => {
        handleFileImportError(error);
        setLoading(false);
        handleCancel();
      },
    },
  });

  const handleCancel = () => {
    setData([]);
    setFileName("");
    setUploadedFile(null);
    setErrorBannerDetails({ isError: false, message: "" });
    setValidationWarning("");
    onCancel();
  };

  const onClickImportFile = () => {
    if (isDuplicate) {
      setShowOverwriteModal(true);
    } else {
      setLoading(true);
      invokeImportFile();
    }
  };
  const onClickOverwriteFile = () => {
    setLoading(true);
    invokeImportFile();
  };

  const invokeImportFile = () => {
    setShowOverwriteModal(false);

    if (uploadedFile) {
      importFile({
        file: uploadedFile,
        data_source_name: fileName,
      });
    }
  };

  const handleFileImportSuccess = () => {
    toastCtx?.pushToast("success", "File imported successfully");
  };
  const handleFileImportError = (error: AxiosError) => {
    console.log("error", error);
    toastCtx?.pushToast("error", "File import failed");
  };

  const OverwriteModalComponent = () => (
    <Modal
      title="Overwrite Data Source?"
      size="lg"
      isOpen={showOverwriteModal}
      closeModal={() => setShowOverwriteModal(false)}
    >
      <div className="mb-3 border-b pb-4">
        <div className="mb-2 text-[15px]">
          <BodyText className="text-neutral-shade-75 text-sm">
            A data source named
            <span className="font-semibold ml-1">
              {fileName.split(".")[0]}{" "}
            </span>
            already exists. Continuing will overwrite it with your new file.
            This action cannot be undone.
          </BodyText>
          <BodyText className="text-neutral-shade-75 mt-5 text-sm">
            To import this as a new source, please cancel and give it a unique
            name.
          </BodyText>
        </div>
      </div>

      <div className="flex justify-end gap-3">
        <ButtonRegular
          label="Cancel"
          className="border"
          onClick={() => setShowOverwriteModal(false)}
        />
        <ButtonPrimary
          label={`Confirm Overwrite`}
          onClick={onClickOverwriteFile}
          disabled={false}
          loading={loading}
        />
      </div>
    </Modal>
  );
  return (
    <>
      <div className="flex flex-col h-full">
        <div className="flex-1 overflow-y-auto min-h-0">
          <SectionHeading className="text-xl font-semibold">
            Upload File
          </SectionHeading>
          <BodyText className="text-neutral-shade-75 mb-3">
            Upload a data source (.csv, .xlsx, .xls) to populate field options
            in your templates and skip manual entry.
          </BodyText>
          {errorBannerDetails.isError && (
            <ErrorBanner
              className="mb-3"
              message={errorBannerDetails.message}
              onClose={() =>
                setErrorBannerDetails({ isError: false, message: "" })
              }
            />
          )}
          {validationWarning && (
            <WarningBanner
              className="mb-3"
              message={validationWarning}
              onClose={() => setValidationWarning("")}
            />
          )}
          {/* File Uploader */}
          <FileUploader
            config={{
              allowedFormats: [".csv", ".xlsx", ".xls"],
              buttonLabel: "Browse File",
              buttonIcon: "search_small",
              maxFileSize: 10,
              maxFiles: 1,
            }}
            onError={(isError, message) => {
              setErrorBannerDetails({ isError, message });
            }}
            onUpload={async files => {
              setErrorBannerDetails({ isError: false, message: "" });
              setValidationWarning("");
              setData([]); // Reset data first
              setFileName(files[0].name.split(".")[0]);
              setUploadedFile(files[0]);

              const { allData, columns } = await parseExcelMetadata(files[0]);
              setFileMetadata({
                rowCount: allData.length,
                columnCount: columns.length,
              });

              // Validation 1: Check if any column names are NO_COLUMN
              const blankColumns = columns.filter(
                col =>
                  !col ||
                  col.toString().trim() === "" ||
                  col.toString().trim().includes("NO_COLUMN")
              );
              if (blankColumns.length === columns.length) {
                setErrorBannerDetails({
                  isError: true,
                  message:
                    "Excel file must have at least one column header to proceed with import.",
                });
                return;
              }

              // Validation 2: Check if there are some blank columns (but not all)

              if (
                blankColumns.length > 0 &&
                blankColumns.length < columns.length
              ) {
                setValidationWarning(
                  "Excel file has data, but some column names are missing. You can still import this file."
                );
              }

              for (const obj in allData[0]) {
                const column = obj;
                const exampleData = allData[0][obj];
                const excelValues = {
                  column,
                  exampleData: exampleData.toString(),
                };
                setData(prev => [...prev, excelValues]);
              }
            }}
          />
          {/* Data Source Input and Preview Table */}
          {data.length > 0 && (
            <>
              <div className="mt-3 p-2">
                <InputRaw
                  label="Data Source Name *"
                  sublabel="Filename is used by default. Change it to a name that's easier to remember."
                  value={fileName}
                  onChange={e => {
                    console.log("InputRaw onChange called with:", e);
                    setFileName(e);
                  }}
                />
                <SectionHeading className="text-base font-semibold mt-3">
                  File Preview
                </SectionHeading>
                <BodyText className="text-neutral-shade-75 mb-3">
                  Showing 1 example row with all {fileMetadata.columnCount}{" "}
                  columns. Once confirmed, {fileMetadata.rowCount} total rows
                  will be imported.
                </BodyText>
              </div>

              <div className="min-h-[250px] max-h-[250px] overflow-y-auto mt-3 no-scrollbar">
                <DataImportPreviewTable data={data} />
              </div>
            </>
          )}
        </div>

        {/* Actions section */}
        {data.length > 0 && (
          <div className="flex justify-end w-full py-4 mt-4 bg-white flex-shrink-0">
            <div className="flex gap-3">
              <ButtonSecondary label="Cancel" onClick={handleCancel} />
              <ButtonPrimary
                label="Import File"
                disabled={!fileName.trim()}
                loading={loading}
                onClick={onClickImportFile}
              />
            </div>
          </div>
        )}
      </div>

      {/* Overwrite Modal */}
      {showOverwriteModal && <OverwriteModalComponent />}
    </>
  );
}
