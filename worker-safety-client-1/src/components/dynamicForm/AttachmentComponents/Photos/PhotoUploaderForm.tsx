import type {
  ActivePageObjType,
  FormComponentPayloadType,
  PhotoUploadItem,
  SubmissionPhotoType,
} from "@/components/templatesComponents/customisedForm.types";
import { FormProvider, useForm } from "react-hook-form";
import { useContext } from "react";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import {
  ALLOWED_DOCUMENTS_FORMATS,
  ALLOWED_IMAGE_FORMATS,
  CF_REDUCER_CONSTANTS,
} from "@/utils/customisedFormUtils/customisedForm.constants";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { convertToSubmissionPhotoType } from "./utils";
import CWFAttachmentUploader from "./CWFPhotoUploader";

const PhotoForm = ({
  mode,
  section,
  activePageDetails,
  item,
  inSummary,
}: {
  mode: string;
  section: any;
  activePageDetails: ActivePageObjType;
  item: FormComponentPayloadType;
  inSummary?: boolean;
}) => {
  const attachmentType = item.properties.attachment_type;
  const methods = useForm({
    defaultValues: { photos: [] },
  });
  const { dispatch } = useContext(CustomisedFromStateContext)!;

  const OnAddOfAttachments = (value: PhotoUploadItem[]) => {
    if (value.length > 0) {
      const submissionAttachmentsArray = convertToSubmissionPhotoType(value);
      dispatch({
        type: CF_REDUCER_CONSTANTS.BUTTON_DISABLE_STATUS_CHANGE,
        payload: false,
      });
      dispatch({
        type: CF_REDUCER_CONSTANTS.ATTACHMENTS_VALUE_CHANGE,
        payload: {
          parentData: activePageDetails,
          fieldData: {
            ...item,
            properties: {
              ...item.properties,
              user_value: [
                ...submissionAttachmentsArray,
                ...(item.properties.user_value || []),
              ],
            },
          },
          section: section,
        },
      });
    }
  };

  const OnDescriptionChangeOfAttachments = (
    photoItem: PhotoUploadItem,
    descriptionText: string
  ) => {
    if (photoItem) {
      const photoItemSubmissionType = convertToSubmissionPhotoType([
        photoItem,
      ])[0];

      const newUserValueArray = item.properties.user_value.map(
        (attachmentEntity: SubmissionPhotoType) => {
          if (attachmentEntity.id === photoItemSubmissionType.id) {
            attachmentEntity.description = descriptionText;
          }
          return attachmentEntity;
        }
      );

      dispatch({
        type: CF_REDUCER_CONSTANTS.ATTACHMENTS_VALUE_CHANGE,
        payload: {
          parentData: activePageDetails,
          fieldData: {
            ...item,
            properties: {
              ...item.properties,
              user_value: [...newUserValueArray],
            },
          },
          section: section,
        },
      });
    }
  };

  const OnDeleteAttachment = (photoId: string) => {
    item.properties.user_value = item.properties.user_value.filter(
      (photo: SubmissionPhotoType) => photo.id !== photoId
    );
  };

  const isPhoto = attachmentType === "photo";
  return (
    <FormProvider {...methods}>
      <CWFAttachmentUploader
        configs={{
          title: item.properties.title || (isPhoto ? "Photos" : "Documents"),
          buttonLabel: `Add ${
            item.properties.title || (isPhoto ? "Photos" : "Documents")
          }`,
          buttonIcon: "image_alt",
          allowedFormats: isPhoto
            ? ALLOWED_IMAGE_FORMATS.map(format => `.${format}`).join(",")
            : ALLOWED_DOCUMENTS_FORMATS.map(format => `.${format}`).join(","),
          allowMultiple: true,
        }}
        readOnly={mode === UserFormModeTypes.PREVIEW}
        fieldArrayName="attachments.photos"
        attachmentItem={item}
        onAddOfAttachments={OnAddOfAttachments}
        onDescriptionChangeOfAttachments={OnDescriptionChangeOfAttachments}
        onDeleteAttachment={OnDeleteAttachment}
        inSummary={inSummary}
        isDisabled={mode === UserFormModeTypes.BUILD || mode === UserFormModeTypes.PREVIEW_PROPS}
      />
    </FormProvider>
  );
};

export default PhotoForm;
