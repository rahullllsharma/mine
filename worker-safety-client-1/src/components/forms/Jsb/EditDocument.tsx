import type { SelectPrimaryOption } from "@/components/shared/select/selectPrimary/SelectPrimary";
import type { ChangeEvent } from "react";
import type { FileProperties } from "./AttachmentsSection";
import { useState } from "react";
import { FileCategory } from "@/api/generated/types";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Field from "@/components/shared/field/Field";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import FieldSelect from "@/components/shared/field/fieldSelect/FieldSelect";
import Paragraph from "@/components/shared/paragraph/Paragraph";

type SelectFieldOption = SelectPrimaryOption & {
  name: FileCategory;
};

// This is used only in this context
// Might be pushed to the backend in the future and fetched as needed
const documentCategories: SelectFieldOption[] = [
  { id: "1", name: FileCategory.Jha },
  { id: "2", name: FileCategory.Pssr },
  { id: "3", name: FileCategory.Hasp },
  { id: "4", name: FileCategory.Other },
];

export type UploadModalProps = {
  file: FileProperties;
  allowCategories?: boolean;
  onSave: (editedFile: EditedFile) => void;
  onCancel: () => void;
};

export type EditedFile = {
  id: string;
  displayName: string;
  name: string;
  category?: FileCategory;
};

export default function EditDocument({
  file,
  allowCategories = false,
  onSave,
  onCancel,
}: Readonly<UploadModalProps>): JSX.Element {
  const [editedName, setEditedName] = useState(file.name);
  const [documentCategory, setDocumentCategory] = useState<
    FileCategory | undefined
  >(file?.category);

  const saveDocumentHandler = () => {
    const editedFile: EditedFile = {
      id: file.id,
      displayName: editedName,
      name: file.name,
      category: documentCategory,
    };

    onSave(editedFile);
  };

  return (
    <>
      <FieldInput
        label="Name"
        placeholder="Add a name"
        defaultValue={editedName}
        onChange={(e: ChangeEvent<HTMLInputElement>) =>
          setEditedName(e.target.value)
        }
      />
      {allowCategories && (
        <FieldSelect
          label="Document type"
          className="mt-4"
          defaultOption={documentCategories.find(
            option => option.name === file.category
          )}
          options={documentCategories}
          onSelect={option => {
            const documentCategoryIndex = documentCategories.findIndex(
              doc => option.id === doc.id
            );

            setDocumentCategory(
              documentCategoryIndex > -1
                ? documentCategories[documentCategoryIndex]["name"]
                : undefined
            );
          }}
        />
      )}
      <Field label="File name" className="mt-4">
        <Paragraph text={file.name} />
      </Field>

      <Field label="Date / time uploaded" className="mt-4">
        <Paragraph text={`${file.date} ${file.time}`} />
      </Field>

      <div className="flex justify-end mt-10">
        <ButtonRegular className="mr-3" label="Cancel" onClick={onCancel} />
        <ButtonPrimary label="Save document" onClick={saveDocumentHandler} />
      </div>
    </>
  );
}
