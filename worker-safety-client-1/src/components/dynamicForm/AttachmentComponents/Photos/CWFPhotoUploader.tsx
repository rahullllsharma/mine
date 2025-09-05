import type {
  UploadItem,
  UploadPhotosProps,
} from "@/components/templatesComponents/customisedForm.types";
import type { EditedFile } from "@/components/upload/uploadDocuments/edit/EditDocument";
import type { FileUploadPolicy } from "@/components/upload/utils";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { useMutation } from "@apollo/client";
import { useContext, useEffect, useState } from "react";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { ErrorPhotoItem } from "@/components/upload/errorPhotoItem/ErrorPhotoItem";
import { PhotoItem } from "@/components/upload/photoItem/PhotoItem";
import { buildUploadFormData, upload } from "@/components/upload/utils";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import FileUploadPolicies from "@/graphql/queries/fileUploadPolicies.gql";
import useCWFFormState from "@/hooks/useCWFFormState";
import { messages } from "@/locales/messages";
import {
  CF_REDUCER_CONSTANTS,
  FORMATS_IGNORED,
} from "@/utils/customisedFormUtils/customisedForm.constants";
import { convertDateToString, convertToDate } from "@/utils/date/helper";
import CustomDeleteConfirmationsModal from "./CustomDeleteConfirmationsModel";
import CWFDocumentItem from "./CWFDocumentItem";
import CWFEditDocument from "./CWFEditDocument";
import CWFUpload from "./CWFUpload";
import CWFUploadingPhotoItem from "./CWFUploadingPhotoItem";
import {
  BlankField,
  convertToPhotoUploadItem,
  downloadDocumentHandler,
  isImage,
  timeoutPromise,
} from "./utils";

const TIMEOUT_DURATION = 300000;

export default function CWFAttachmentUploader({
  configs,
  fieldArrayName,
  readOnly,
  attachmentItem,
  onAddOfAttachments,
  onDescriptionChangeOfAttachments,
  onDeleteAttachment,
  inSummary,
  isDisabled,
}: UploadPhotosProps & { inSummary?: boolean , isDisabled?: boolean }): JSX.Element {
  const {
    fields: photos,
    prepend,
    remove,
    update,
  } = useFieldArray<Pick<DailyReportInputs, "attachments">>({
    name: fieldArrayName,
  });
  const toastCtx = useContext(ToastContext);
  const [editedDocument, setEditedDocument] = useState<UploadItem | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const { dispatch } = useContext(CustomisedFromStateContext)!;
  useEffect(() => {
    if (attachmentItem.properties.user_value != null) {
      prepend(convertToPhotoUploadItem(attachmentItem.properties.user_value));
    }
  }, []);

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

  const { setCWFFormStateDirty } = useCWFFormState();

  const arePhotosUploaded = photos.length > 0;

  const [generateFileUploadPolicies, { loading: isLoading }] =
    useMutation(FileUploadPolicies);

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
        toastCtx?.pushToast("error", `Upload of ${file.name} was aborted`);
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
        lastModified: date.toISOString().replace("Z", ""),
        category: null,
        url: `${fileUploadPolicy.url}/${uploadedFilename}`,
        signedUrl: fileUploadPolicy.signedUrl,
        description: "",
      };

      return newDocument;
    } catch (error) {
      toastCtx?.pushToast("error", `Failed to upload file ${file.name}`);
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
    //setting Form dirty ,after user started uploading files
    setCWFFormStateDirty(true);

    const unsupportedFiles = files.filter(file =>
      FORMATS_IGNORED.includes(file.name.split(".").pop()?.toLowerCase() || "")
    );
    if (unsupportedFiles.length) {
      dispatch({
        type: CF_REDUCER_CONSTANTS.BUTTON_DISABLE_STATUS_CHANGE,
        payload: false,
      });
      toastCtx?.pushToast("error", "Format not supported.");
      return;
    }
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
        if (!readOnly) {
          onAddOfAttachments(successfulUploads);
        }
      }
    } catch (error) {
      dispatch({
        type: CF_REDUCER_CONSTANTS.BUTTON_DISABLE_STATUS_CHANGE,
        payload: false,
      });
      toastCtx?.pushToast("error", "Failed to get signed URLs or timed out");
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
      toastCtx?.pushToast("error", "Failed to retry upload");
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
      setAbortControllers(prev => {
        const newControllers = { ...prev };
        delete newControllers[index];
        return newControllers;
      });
    }
  };

  const getSignedUrls = async (nFiles: number) => {
    const { data } = await generateFileUploadPolicies({
      variables: {
        count: nFiles,
      },
    });
    return data;
  };

  const handleDeleteClick = (index: number) => {
    setPhotoIndexToDelete(index);
    setShowDeleteModal(true);
  };

  const confirmDelete = () => {
    if (photoIndexToDelete !== null) {
      const photoToDelete = photos[photoIndexToDelete];
      remove(photoIndexToDelete);
      if (photoToDelete) {
        onDeleteAttachment(photoToDelete.id);
      }
      setPhotoIndexToDelete(null);
    }
    setShowDeleteModal(false);
  };

  const saveDocumentHandler = (editedFile: EditedFile): void => {
    const documentIndex = photos.findIndex(doc => doc.id === editedFile.id);

    if (!editedDocument) return;

    const originalFileName = editedDocument.displayName;
    const fileParts = originalFileName.split(".");
    const extension = fileParts.length > 0 ? fileParts.pop() : "";

    const newFileParts = editedFile.displayName.split(".");
    const newBaseName = newFileParts.slice(0, -1).join(".") || newFileParts[0];

    const updatedDocument = {
      ...editedDocument,
      ...editedFile,
      displayName: `${newBaseName}.${extension}`,
      name: `${newBaseName}.${extension}`,
    } as UploadItem;

    if (documentIndex === -1) {
      prepend(updatedDocument);
    } else {
      update(documentIndex, updatedDocument);
      attachmentItem.properties.user_value[
        documentIndex
      ].display_name = `${newBaseName}.${extension}`;
      attachmentItem.properties.user_value[
        documentIndex
      ].name = `${newBaseName}.${extension}`;
    }
    closeUploadModal();
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

  const renderBlankField = photos.length === 0 && uploadingFiles.length === 0;

  const editDocumentHandler = (
    event: React.MouseEvent<HTMLButtonElement>,
    document: UploadItem
  ) => {
    event.preventDefault();

    setEditedDocument(document);
    setIsUploadModalOpen(true);
  };

  const closeUploadModal = () => {
    setIsUploadModalOpen(false);
  };

  return (
    <>
      <CWFUpload
        configs={configs}
        readOnly={readOnly}
        totalDocuments={photos.length}
        isUploadingDocument={isLoading}
        onUpload={uploadFileHandler}
        attachmentItem={attachmentItem}
        inSummary={inSummary}
        isDisabled={isDisabled}
      >
        <div className="rounded w-full flex flex-col gap-6 items-start">
          {uploadingFiles.map(({ file, index }) => (
            <CWFUploadingPhotoItem
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

          {renderBlankField && <BlankField />}

          {arePhotosUploaded ? (
            <>
              {photos.map((photo, index) => (
                <Controller
                  key={photo.id}
                  name={`${fieldArrayName}.${index}`}
                  defaultValue={getValues(`${fieldArrayName}.${index}`)}
                  render={() =>
                    isImage(photo.name) ? (
                      <PhotoItem
                        readOnly={readOnly}
                        url={photo.signedUrl}
                        name={photo.displayName}
                        onDelete={event => {
                          event.preventDefault();
                          handleDeleteClick(index);
                        }}
                        description={photo.description}
                        onDescriptionChange={(value: string) => {
                          update(index, { ...photo, description: value });
                          onDescriptionChangeOfAttachments(photo, value);
                        }}
                      />
                    ) : (
                      <CWFDocumentItem
                        document={photo}
                        readOnly={readOnly}
                        onEdit={event => {
                          event.preventDefault();
                          editDocumentHandler(event, photo);
                        }}
                        onDownload={event => {
                          event.preventDefault();
                          downloadDocumentHandler(event, photo);
                        }}
                        onDelete={event => {
                          event.preventDefault();
                          handleDeleteClick(index);
                        }}
                      />
                    )
                  }
                />
              ))}
            </>
          ) : null}
        </div>
      </CWFUpload>

      {showDeleteModal && (
        <CustomDeleteConfirmationsModal
          isOpen={showDeleteModal}
          closeModal={() => setShowDeleteModal(false)}
          onDeleteConfirm={confirmDelete}
          isLoading={false}
          attachmentItem={attachmentItem}
        />
      )}
      {isUploadModalOpen && editedDocument && (
        <Modal
          title="Edit"
          isOpen={isUploadModalOpen}
          closeModal={closeUploadModal}
        >
          <CWFEditDocument
            file={editedDocument}
            allowCategories={false}
            onSave={saveDocumentHandler}
            onCancel={closeUploadModal}
          />
        </Modal>
      )}
    </>
  );
}
