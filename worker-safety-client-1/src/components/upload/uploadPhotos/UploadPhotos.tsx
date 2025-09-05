import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { UploadItem, UploadProps } from "../Upload";
import type { FileUploadPolicy } from "../utils";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import { useMutation } from "@apollo/client";
import { useState } from "react";
import { CaptionText } from "@urbint/silica";
import FileUploadPolicies from "@/graphql/queries/fileUploadPolicies.gql";
import { convertDateToString, convertToDate } from "@/utils/date/helper";
import Paragraph from "@/components/shared/paragraph/Paragraph";
import { messages } from "@/locales/messages";
import { buildUploadFormData, upload } from "../utils";
import Upload from "../Upload";
import { CircularLoader } from "../../uploadLoader/uploadLoader";
import CustomDeleteConfirmationsModal from "@/components/dynamicForm/AttachmentComponents/Photos/CustomDeleteConfirmationsModel";
import Button from "../../shared/button/Button";
import { ErrorPhotoItem } from "../errorPhotoItem/ErrorPhotoItem";
import { PhotoItem } from "../photoItem/PhotoItem";

export type FieldArrayType = "attachments.photos";

export type UploadPhotosProps = Omit<UploadProps, "onUpload"> & {
  fieldArrayName: FieldArrayType;
};

const TIMEOUT_DURATION = 300000; // 300 seconds in milliseconds

export default function UploadPhotos({
  configs,
  fieldArrayName,
  readOnly,
}: UploadPhotosProps): JSX.Element {
  const {
    fields: photos,
    prepend,
    remove,
    update,
  } = useFieldArray<Pick<DailyReportInputs, "attachments">>({
    name: fieldArrayName,
  });

  const { getValues } =
    useFormContext<Pick<DailyReportInputs, "attachments">>();

  const [uploadingFiles, setUploadingFiles] = useState<
    { file: File; index: number }[]
  >([]);
  const [errorFiles, setErrorFiles] = useState<{ file: File; index: number }[]>(
    []
  );
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [photoIndexToDelete, setPhotoIndexToDelete] = useState<number | null>(
    null
  );
  const [abortControllers, setAbortControllers] = useState<{
    [key: number]: AbortController;
  }>({});

  const arePhotosUploaded = photos.length > 0;

  // Mutation to generate signed urls for file uploads
  const [generateFileUploadPolicies, { loading: isLoading }] =
    useMutation(FileUploadPolicies);

  const timeoutPromise = (ms: number) =>
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error(messages.requestTimedOut)), ms);
    });

  const handleUpload = async (
    file: File,
    index: number,
    fileUploadPolicy: FileUploadPolicy,
    abortController: AbortController
  ): Promise<UploadItem | null> => {
    try {
      const uploadWithTimeout = Promise.race([
        upload(
          fileUploadPolicy.url,
          buildUploadFormData(fileUploadPolicy, file),
          abortController
        ),
        timeoutPromise(TIMEOUT_DURATION),
      ]);

      const response = await uploadWithTimeout;

      if (response === "aborted") {
        console.error(`Upload of ${file.name} was aborted`);
        return null;
      }

      if (response === "error") {
        throw new Error(`Upload failed for ${file.name}`);
      }

      const date = convertToDate();
      const time = date.toLocaleString("en-US", {
        hour: "numeric",
        hour12: true,
        minute: "numeric",
      });
      const uploadedFilename = fileUploadPolicy.id;

      const newDocument: UploadItem = {
        id: uploadedFilename,
        name: file.name,
        displayName: file.name,
        size: `${file.size / 1000} KB`,
        date: convertDateToString(date),
        time,
        category: null,
        url: `${fileUploadPolicy.url}/${uploadedFilename}`,
        signedUrl: fileUploadPolicy.signedUrl,
        description: "",
      };

      return newDocument;
    } catch (error) {
      console.error(`Failed to upload file ${file.name}`, error);
      setErrorFiles(prev => [
        ...prev,
        { file, index, isTimeout: error === messages.requestTimedOut },
      ]);
      return null;
    } finally {
      setAbortControllers(prev => {
        const { [index]: _, ...rest } = prev;
        return rest;
      });
      setUploadingFiles(prev => prev.filter(item => item.index !== index));
    }
  };

  const uploadFileHandler = async (files: File[]) => {
    setUploadingFiles(files.map((file, index) => ({ file, index })));
    setErrorFiles([]);

    try {
      const { fileUploadPolicies } = await Promise.race([
        getSignedUrls(files.length),
        timeoutPromise(TIMEOUT_DURATION),
      ]);

      const uploadPromises = files.map(async (file, index) => {
        const abortController = new AbortController();
        setAbortControllers(prev => ({ ...prev, [index]: abortController }));

        return handleUpload(
          file,
          index,
          fileUploadPolicies[index],
          abortController
        );
      });

      const uploadedDocuments = await Promise.all(uploadPromises);
      const successfulUploads = uploadedDocuments.filter(
        (doc): doc is UploadItem => doc !== null
      );

      if (successfulUploads.length) {
        prepend(successfulUploads);
      }
    } catch (error) {
      console.error("Failed to get signed URLs or timed out", error);
      setErrorFiles(
        files.map((file, index) => ({
          file,
          index,
          isTimeout: error === messages.requestTimedOut,
          isGlobalError: true,
        }))
      );
      setUploadingFiles([]);
    }
  };

  const handleRetry = async (file: File, index: number) => {
    setUploadingFiles(prev => [...prev, { file, index }]);
    setErrorFiles(prev => prev.filter(item => item.index !== index));

    try {
      // Wrap both the URL fetching and upload process in Promise.race
      const result = await Promise.race([
        (async () => {
          const { fileUploadPolicies } = await getSignedUrls(1);
          const abortController = new AbortController();
          setAbortControllers(prev => ({ ...prev, [index]: abortController }));

          const newDocument = await handleUpload(
            file,
            index,
            fileUploadPolicies[0],
            abortController
          );
          return newDocument;
        })(),
        timeoutPromise(TIMEOUT_DURATION),
      ]);

      if (result !== null) {
        prepend([result as UploadItem]);
      }
    } catch (error) {
      console.error("Failed to retry upload", error);
      setErrorFiles(prev => [
        ...prev,
        {
          file,
          index,
          isTimeout: error === messages.requestTimedOut,
          isGlobalError: true,
        },
      ]);
      setUploadingFiles(prev => prev.filter(item => item.index !== index));
    } finally {
      // Clean up the abort controller
      setAbortControllers(prev => {
        const newControllers = { ...prev };
        delete newControllers[index];
        return newControllers;
      });
    }
  };

  // Actual request to mutation to retrieve signed urls for further upload
  const getSignedUrls = async (nFiles: number) => {
    const { data } = await generateFileUploadPolicies({
      variables: {
        count: nFiles,
      },
    });
    return data;
  };

  // Handle delete button click to show modal
  const handleDeleteClick = (index: number) => {
    setPhotoIndexToDelete(index);
    setShowDeleteModal(true);
  };

  // Confirm deletion from modal
  const confirmDelete = () => {
    if (photoIndexToDelete !== null) {
      remove(photoIndexToDelete);
      setPhotoIndexToDelete(null);
    }
    setShowDeleteModal(false);
  };

  const handleCancel = (index: number) => {
    if (abortControllers[index]) {
      abortControllers[index].abort();
      setAbortControllers(prev => {
        const { [index]: _, ...rest } = prev;
        return rest;
      });
    }
    setUploadingFiles(prev => prev.filter(item => item.index !== index));
    setErrorFiles(prev => prev.filter(item => item.index !== index));
  };

  const UploadingPhotoItem = ({
    file,
    onCancel,
  }: {
    file: File;
    onCancel: () => void;
  }): JSX.Element => (
    <div className="mb-4 flex gap-4 p-4 bg-brand-gray-10 w-full">
      <div className="inset-0 flex items-center justify-center rounded w-[120px] h-[120px] bg-brand-urbint-60">
        <CircularLoader />
      </div>
      <div className="flex-1 flex flex-col justify-center px-2 max-w-lg text-neutral-shade-75">
        <CaptionText className="md:text-sm font-semibold">
          Uploading
        </CaptionText>
        <CaptionText>{file.name}</CaptionText>
      </div>
      <div className="flex items-center">
        <Button
          onClick={onCancel}
          className="md:text-sm text-neutral-shade-75 w-auto"
          label="Cancel"
        />
      </div>
    </div>
  );

  return (
    <>
      <Upload
        configs={configs}
        readOnly={readOnly}
        totalDocuments={photos.length}
        isUploadingDocument={isLoading}
        onUpload={uploadFileHandler}
      >
        <div className="rounded w-full flex flex-col gap-6 items-start">
          {uploadingFiles.map(({ file, index }) => (
            <UploadingPhotoItem
              key={`uploading-${index}`}
              file={file}
              onCancel={() => handleCancel(index)}
            />
          ))}

          {errorFiles.map(({ file, index }) => (
            <ErrorPhotoItem
              key={`error-${index}`}
              file={file}
              onRetry={() => handleRetry(file, index)}
              onCancel={() => handleCancel(index)}
            />
          ))}

          {arePhotosUploaded ? (
            <>
              {photos.map((photo, index: number) => (
                <Controller
                  key={photo.id}
                  name={`${fieldArrayName}.${index}`}
                  defaultValue={getValues(`${fieldArrayName}.${index}`)}
                  render={() => (
                    <PhotoItem
                      readOnly={readOnly}
                      url={photo.signedUrl}
                      name={photo.displayName}
                      onDelete={(
                        event: React.MouseEvent<HTMLButtonElement>
                      ) => {
                        event.preventDefault();
                        handleDeleteClick(index);
                      }}
                      description={photo.description}
                      onDescriptionChange={(value: string) => {
                        update(index, { ...photo, description: value });
                      }}
                    />
                  )}
                />
              ))}
            </>
          ) : (
            <Paragraph text="No Photos uploaded" />
          )}
        </div>
      </Upload>
      {/* Modal for delete confirmation */}
      {showDeleteModal && (
        <CustomDeleteConfirmationsModal
          isOpen={showDeleteModal}
          closeModal={() => setShowDeleteModal(false)}
          onDeleteConfirm={confirmDelete}
          isLoading={false}
        />
      )}
    </>
  );
}
