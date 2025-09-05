import type { UploadProps } from "@/components/templatesComponents/customisedForm.types";
import { CaptionText, SectionHeading } from "@urbint/silica";
import { useContext, useRef } from "react";
import cx from "classnames";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import {
  CF_REDUCER_CONSTANTS,
  documentMaxFileSize,
  documentMaxSize,
  maxFiles,
  photoMaxFileSize,
  photoMaxSize,
} from "@/utils/customisedFormUtils/customisedForm.constants";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import {
  documentFormatsText,
  getMaxFilesErrorMessage,
  photosFormatsText,
} from "./utils";

export default function CWFUpload({
  configs,
  readOnly,
  isUploadingDocument,
  onUpload,
  children,
  attachmentItem,
  inSummary,
  isDisabled,
}: UploadProps & { inSummary?: boolean; isDisabled?: boolean }): JSX.Element {
  const {
    title,
    buttonLabel,
    buttonIcon,
    allowedFormats,
    allowMultiple = true,
  } = configs;
  const uploadRef = useRef<HTMLInputElement>(null);
  const toastCtx = useContext(ToastContext);
  const { dispatch } = useContext(CustomisedFromStateContext)!;

  const uploadDocumentHandler = () => {
    if (!isDisabled) {
      uploadRef.current?.click();
    }
  };

  const maxFileSize =
    attachmentItem?.properties?.attachment_type === "photo"
      ? photoMaxFileSize
      : documentMaxFileSize;

  const getSizeExceededErrorMessage = (selectedFilesCount: number): string => {
    const maxSizeDisplay =
      attachmentItem?.properties?.attachment_type === "photo" ? "15MB" : "20MB";

    return selectedFilesCount === 1
      ? `Max size exceeded (${maxSizeDisplay})`
      : `Some files exceed the max size (${maxSizeDisplay})`;
  };

  const fileSelectedHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { files } = event.target;
    if (files) {
      const filteredFiles = Array.from(files).filter(
        file => file.size / 1000 < maxFileSize
      );
      const hasValidFiles = filteredFiles.length > 0;
      const hasInvalidFiles = files.length > filteredFiles.length;
      if (hasInvalidFiles) {
        toastCtx?.pushToast("error", getSizeExceededErrorMessage(files.length));
      }

      if (filteredFiles.length > maxFiles) {
        const isPhoto = attachmentItem?.properties?.attachment_type === "photo";
        toastCtx?.pushToast("error", getMaxFilesErrorMessage(isPhoto));
      }
      dispatch({
        type: CF_REDUCER_CONSTANTS.BUTTON_DISABLE_STATUS_CHANGE,
        payload: hasValidFiles && filteredFiles.length <= maxFiles,
      });

      if (hasValidFiles && filteredFiles.length <= maxFiles) {
        onUpload(filteredFiles);
      }

      if (uploadRef.current) {
        uploadRef.current.value = "";
      }
    }
  };

  const maxSize =
    attachmentItem?.properties?.attachment_type === "photo"
      ? photoMaxSize
      : documentMaxSize;

  const maxSizeSection = (
    <div className="text-xs text-neutral-600 mt-0.5">
      <CaptionText>
        {attachmentItem?.properties?.attachment_type === "photo"
          ? photosFormatsText
          : documentFormatsText}
      </CaptionText>
      <CaptionText className="text-xs">Max file size: {maxSize}</CaptionText>
    </div>
  );

  return (
    <>
      {/* Title section always rendered outside */}
      <div className="flex justify-between">
        <SectionHeading
          className={`${
            inSummary ? "text-[20px]" : "text-xl"
          } text-neutral-shade-100 font-semibold`}
        >
          {title}
        </SectionHeading>
        {!readOnly && (
          <>
            <ButtonSecondary
              className="sm:block"
              iconStart={buttonIcon}
              label={buttonLabel}
              loading={isUploadingDocument}
              onClick={uploadDocumentHandler}
              disabled={isDisabled}
            />
            <input
              title="file-uploader"
              type="file"
              className="hidden"
              ref={uploadRef}
              multiple={allowMultiple}
              accept={allowedFormats}
              onChange={fileSelectedHandler}
              disabled={isDisabled}
            />
          </>
        )}
      </div>

      {/* Content section with conditional background */}
      <div
        className={cx("mt-4", {
          "bg-gray-100 p-4 rounded-md mt-2": inSummary,
        })}
      >
        {maxSizeSection}
        {children}
      </div>
    </>
  );
}
