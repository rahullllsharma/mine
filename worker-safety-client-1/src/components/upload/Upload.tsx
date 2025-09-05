import type { IconName } from "@urbint/silica";
import type { PropsWithChildren } from "react";
import { useContext, useRef } from "react";
import ButtonSecondary from "../shared/button/secondary/ButtonSecondary";
import ToastContext from "../shared/toast/context/ToastContext";

const maxFiles: Readonly<number> = 25;
const maxFileSize: Readonly<number> = 9999;

export type UploadConfigs = {
  title: string;
  buttonLabel: string;
  buttonIcon: IconName;
  allowedFormats: string;
  allowMultiple?: boolean;
};

export type UploadProps = PropsWithChildren<{
  configs: UploadConfigs;
  readOnly?: boolean;
  totalDocuments?: number;
  isUploadingDocument?: boolean;
  onUpload: (file: File[]) => void;
}>;

//Update this type when synching with BE models
export type UploadItem = {
  id: string;
  displayName: string;
  name: string;
  size: string;
  date: string;
  time: string;
  category?: string | null;
  url: string;
  signedUrl: string;
  description?: string;
};

export default function Upload({
  configs,
  readOnly,
  totalDocuments,
  isUploadingDocument,
  onUpload,
  children,
}: UploadProps): JSX.Element {
  const {
    title,
    buttonLabel,
    buttonIcon,
    allowedFormats,
    allowMultiple = true,
  } = configs;
  const uploadRef = useRef<HTMLInputElement>(null);
  const toastCtx = useContext(ToastContext);
  const formatsText = allowedFormats
    .replace(/\./g, "")
    .replace(/\,/g, ", ")
    .toUpperCase();

  const uploadDocumentHandler = () => {
    uploadRef.current?.click();
  };

  const downloadDocumentsHandler = () => {
    //TODO Download all documents
    console.log("downloadDocumentsHandler");
  };

  const getSizeExceededErrorMessage = (selectedFilesCount: number): string => {
    return selectedFilesCount === 1
      ? "Max size exceeded (10MB)"
      : "Some files exceed the max size (10MB)";
  };

  const fileSelectedHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { files } = event.target;
    if (files) {
      const filteredFiles = Array.from(files).filter(
        file => file.size / 1000 < maxFileSize
      );

      if (filteredFiles.length < files.length) {
        toastCtx?.pushToast("error", getSizeExceededErrorMessage(files.length));
      }

      // TODO WSAPP-1136: This should be handled when the BE raises an error
      if (filteredFiles.length > maxFiles) {
        toastCtx?.pushToast(
          "error",
          `Upload files limit exceeded, you have ${filteredFiles.length}, limit is ${maxFiles}`
        );
        return;
      }

      if (filteredFiles.length > 0) {
        onUpload(filteredFiles);
      }

      if (uploadRef.current) {
        uploadRef.current.value = "";
      }
    }
  };

  const isDisabled = totalDocuments === 0 && readOnly;

  return (
    <>
      <div className="flex justify-between">
        <h6 className="text-xl text-neutral-shade-100 font-semibold">
          {title}
        </h6>
        {/* While bulk download is not supported, button should be hidden */}
        {!readOnly && (
          <ButtonSecondary
            className="hidden sm:block"
            iconStart={buttonIcon}
            label={buttonLabel}
            disabled={isDisabled}
            loading={isUploadingDocument}
            onClick={
              readOnly ? downloadDocumentsHandler : uploadDocumentHandler
            }
          />
        )}
        <input
          title="file-uploader"
          type="file"
          className="hidden"
          ref={uploadRef}
          multiple={allowMultiple}
          accept={allowedFormats}
          onChange={fileSelectedHandler}
        />
      </div>
      {!readOnly && (
        <div className="text-xs font-normal text-neutral-shade-75 mt-0.5">
          <p>{formatsText}</p>
          <p>Max file size: 10MB</p>
        </div>
      )}
      <div className="mt-6">{children}</div>
      {!readOnly && (
        <ButtonSecondary
          className="block sm:hidden mt-4 w-full"
          iconStart={buttonIcon}
          label={buttonLabel}
          disabled={isDisabled}
          onClick={readOnly ? downloadDocumentsHandler : uploadDocumentHandler}
        />
      )}
    </>
  );
}
