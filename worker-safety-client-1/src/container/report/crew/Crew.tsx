import type { FieldSearchSelectProps } from "@/components/shared/field/fieldSearchSelect/FieldSearchSelect";
import type { UploadConfigs } from "@/components/upload/Upload";
import UploadDocuments from "@/components/upload/uploadDocuments/UploadDocuments";
import CrewInformation from "./information/CrewInformation";

export type CrewProps = {
  companies?: FieldSearchSelectProps["options"];
  isCompleted?: boolean;
};

export default function Crew({
  companies = [],
  isCompleted,
}: CrewProps): JSX.Element {
  const uploadConfigs: UploadConfigs = {
    title: "Crew Documents",
    buttonLabel: isCompleted ? "Download crew info" : "Upload crew info",
    buttonIcon: isCompleted ? "download" : "group",
    allowedFormats:
      ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.apng,.avif,.gif,.jpg,.jpeg,.png,.svg,.webp",
    allowMultiple: false,
  };

  return (
    <>
      <CrewInformation companies={companies} isCompleted={isCompleted} />
      <UploadDocuments
        configs={uploadConfigs}
        fieldArrayName="crew.documents"
        readOnly={isCompleted}
      />
    </>
  );
}
