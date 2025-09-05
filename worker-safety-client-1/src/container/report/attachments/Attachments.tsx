import type { UploadConfigs } from "@/components/upload/Upload";
import UploadDocuments from "@/components/upload/uploadDocuments/UploadDocuments";
import UploadPhotos from "@/components/upload/uploadPhotos/UploadPhotos";

export type AttachmentsProps = {
  isCompleted?: boolean;
};

export default function Attachments({
  isCompleted,
}: AttachmentsProps): JSX.Element {
  const documentUploadConfig: UploadConfigs = {
    title: "Documents",
    buttonLabel: isCompleted ? "Download documents" : "Add documents",
    buttonIcon: isCompleted ? "download" : "file_blank_outline",
    allowedFormats: ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx",
  };

  const photoUploadConfig: UploadConfigs = {
    title: "Photos",
    buttonLabel: isCompleted ? "Download photos" : "Add photos",
    buttonIcon: isCompleted ? "download" : "image_alt",
    allowedFormats: ".apng,.avif,.gif,.jpg,.jpeg,.png,.svg,.webp",
  };

  return (
    <>
      <section>
        <UploadPhotos
          configs={photoUploadConfig}
          fieldArrayName="attachments.photos"
          readOnly={isCompleted}
        />
      </section>
      <section className="mt-6">
        <UploadDocuments
          configs={documentUploadConfig}
          fieldArrayName="attachments.documents"
          readOnly={isCompleted}
          allowCategories
        />
      </section>
    </>
  );
}
