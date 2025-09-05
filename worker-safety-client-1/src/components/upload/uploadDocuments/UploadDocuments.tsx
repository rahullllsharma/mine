import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { UploadItem, UploadProps } from "../Upload";
import type { EditedFile } from "./edit/EditDocument";
import { useMutation } from "@apollo/client";
import { Icon } from "@urbint/silica";
import { useContext, useState } from "react";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import { convertDateToString, convertToDate } from "@/utils/date/helper";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import Paragraph from "@/components/shared/paragraph/Paragraph";
import Modal from "@/components/shared/modal/Modal";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import FileUploadPolicies from "@/graphql/queries/fileUploadPolicies.gql";
import Upload from "../Upload";
import { buildUploadFormData, download, upload } from "../utils";
import EditDocument from "./edit/EditDocument";

type FieldArrayType = "crew.documents" | "attachments.documents";

export type UploadDocumentsProps = Omit<UploadProps, "onUpload"> & {
  fieldArrayName: FieldArrayType;
  modalTitle?: string;
  allowCategories?: boolean;
};

type DocumentItemProps = {
  document: UploadItem;
  readOnly?: boolean;
  onEdit: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onDownload: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onDelete: (event: React.MouseEvent<HTMLButtonElement>) => void;
};

const DocumentItem = ({
  document: { size, displayName, category, date, time },
  readOnly,
  onEdit,
  onDownload,
  onDelete,
}: DocumentItemProps): JSX.Element => {
  const getDocumentOptions = (): MenuItemProps[][] => {
    const documentOptions: MenuItemProps[][] = [];

    const groupOptions: MenuItemProps[] = [
      {
        label: "Download",
        icon: "download",
        onClick: onDownload,
      },
    ];

    const deleteOptions: MenuItemProps[] = [];

    if (!readOnly) {
      groupOptions.unshift({ label: "Edit", icon: "edit", onClick: onEdit });

      deleteOptions.push({
        label: "Delete",
        icon: "trash_empty",
        onClick: onDelete,
      });
    }

    documentOptions.push(groupOptions);
    if (deleteOptions.length > 0) {
      documentOptions.push(deleteOptions);
    }

    return documentOptions;
  };

  const documentDetails = [size, category, date, time]
    .filter(Boolean)
    .join(" • ");

  return (
    <div
      className="h-14 w-full border border-neutral-shade-38 rounded flex items-center px-2"
      data-testid="document-item"
    >
      <Icon name="file_blank_outline" className="text-2xl" />
      <div className="ml-2 truncate">
        <p className="text-sm font-semibold text-neutral-shade-100">
          {displayName}
        </p>
        <p className="text-xs text-neutral-shade-58">{documentDetails}</p>
      </div>
      <div className="ml-auto">
        <Dropdown className="z-30" menuItems={getDocumentOptions()}>
          <button className="text-xl">
            <Icon name="more_horizontal" />
          </button>
        </Dropdown>
      </div>
    </div>
  );
};

export default function UploadDocuments({
  configs,
  fieldArrayName,
  modalTitle,
  readOnly,
  allowCategories = false,
}: UploadDocumentsProps): JSX.Element {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [editedDocument, setEditedDocument] = useState<UploadItem | null>(null);
  const {
    fields: documents,
    prepend,
    update,
    remove,
  } = useFieldArray<Pick<DailyReportInputs, "attachments" | "crew">>({
    name: fieldArrayName,
  });

  const { getValues } =
    useFormContext<Pick<DailyReportInputs, "attachments" | "crew">>();

  const toastCtx = useContext(ToastContext);

  const areDocumentsUploaded = documents.length > 0;

  const uploadFileHandler = async (files: File[]) => {
    // Generate signed urls for as much files as needed
    const { fileUploadPolicies } = await getSignedUrls(files.length);

    // Waits for all uploads to finish the uploading process
    Promise.all(
      files.map(async (file, index) => {
        // Builds metadata for uploaded file
        const date = convertToDate();
        const time = date.toLocaleString("en-US", {
          hour: "numeric",
          hour12: true,
          minute: "numeric",
        });

        const uploadedFilename = fileUploadPolicies[index]?.id;

        // Executes the upload to Cloud Storage
        await upload(
          fileUploadPolicies[index].url,
          buildUploadFormData(fileUploadPolicies[index], file)
        );

        // Create an UploadItem to be handled afterwards
        return {
          id: uploadedFilename,
          name: file.name,
          displayName: file.name,
          size: `${file.size / 1000} KB`,
          date: convertDateToString(date),
          time,
          category: null,
          url: `${fileUploadPolicies[index]?.url}/${uploadedFilename}`,
          signedUrl: fileUploadPolicies[index]?.signedUrl,
        };
      })
    )
      .then((items: UploadItem[]) => {
        // If everything succeeded, add the new uploaded files to the UI
        const { allowMultiple } = configs;
        // because allowMultiple can be undefined (and treated as true in the Upload component, we need to check also for that)
        if (typeof allowMultiple === "undefined" || allowMultiple) {
          prepend(items);
        } else {
          setEditedDocument(items[0]);
          setIsUploadModalOpen(true);
        }
      })
      .catch((error: Error) => {
        console.log("Failed to upload file(s)", error);
      });
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

  // Mutation to generate signed urls for file uploads
  const [generateFileUploadPolicies, { loading: isLoading }] =
    useMutation(FileUploadPolicies);

  const editDocumentHandler = (
    event: React.MouseEvent<HTMLButtonElement>,
    document: UploadItem
  ) => {
    event.preventDefault();

    setEditedDocument(document);
    setIsUploadModalOpen(true);
  };

  const downloadDocumentHandler = async (
    event: React.MouseEvent<HTMLButtonElement>,
    file: UploadItem
  ) => {
    event.preventDefault();

    const result = await download(file.signedUrl, file.name);

    if (result === "error") {
      toastCtx?.pushToast("error", "There was an error downloading the file");
    }
  };

  const saveDocumentHandler = (file: EditedFile): void => {
    const documentIndex = documents.findIndex(doc => doc.id === file.id);
    const document = { ...editedDocument, ...file };
    //If the document doesn't exist, then it's because it's a recently uploaded file and must be prepended
    if (documentIndex === -1) {
      prepend(document);
    } else {
      update(documentIndex, document);
    }
    closeUploadModal();
  };

  const closeUploadModal = () => {
    setIsUploadModalOpen(false);
  };

  const getModalTitle = (): string =>
    modalTitle || editedDocument?.displayName || "";

  return (
    <>
      <Upload
        configs={configs}
        readOnly={readOnly}
        totalDocuments={documents.length}
        isUploadingDocument={isLoading}
        onUpload={uploadFileHandler}
      >
        <div className="flex flex-col gap-2">
          {areDocumentsUploaded ? (
            documents.map((document, index: number) => (
              <Controller
                key={index}
                name={`${fieldArrayName}.${index}`}
                defaultValue={getValues(`${fieldArrayName}.${index}`)}
                render={() => (
                  <DocumentItem
                    document={document}
                    readOnly={readOnly}
                    onEdit={(event: React.MouseEvent<HTMLButtonElement>) =>
                      editDocumentHandler(event, document)
                    }
                    onDownload={(event: React.MouseEvent<HTMLButtonElement>) =>
                      downloadDocumentHandler(event, document)
                    }
                    onDelete={(event: React.MouseEvent<HTMLButtonElement>) => {
                      event.preventDefault();
                      remove(index);
                    }}
                  />
                )}
              />
            ))
          ) : (
            <Paragraph text="No documents uploaded" />
          )}
        </div>
      </Upload>
      <Modal
        title={getModalTitle()}
        isOpen={isUploadModalOpen}
        closeModal={closeUploadModal}
      >
        {editedDocument && (
          <EditDocument
            file={editedDocument}
            allowCategories={allowCategories}
            onSave={saveDocumentHandler}
            onCancel={closeUploadModal}
          />
        )}
      </Modal>
    </>
  );
}
