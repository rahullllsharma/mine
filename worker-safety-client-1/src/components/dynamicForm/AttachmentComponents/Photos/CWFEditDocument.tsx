import type { SelectPrimaryOption } from "@/components/shared/select/selectPrimary/SelectPrimary";
import type { ChangeEvent } from "react";
import type { EditedFile} from "@/components/templatesComponents/customisedForm.types";
import { useState } from "react";
import { documentCategories, type UploadModalProps } from "@/components/templatesComponents/customisedForm.types";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Field from "@/components/shared/field/Field";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import FieldSelect from "@/components/shared/field/fieldSelect/FieldSelect";
import Paragraph from "@/components/shared/paragraph/Paragraph";

export default function CWFEditDocument({
  file,
  allowCategories = false,
  onSave,
  onCancel,
}: UploadModalProps): JSX.Element {
  const [editedName, setEditedName] = useState(file.name);
  const [documentCategory, setDocumentCategory] = useState<
    string | undefined | null
  >(file.category);

  const saveDocumentHandler = () => {
    let editedFile: EditedFile = {
      id: file.id,
      displayName: editedName,
      name: editedName,
    };

    if (documentCategory) {
      editedFile = { ...editedFile, category: documentCategory };
    }

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
          onSelect={(option: SelectPrimaryOption) =>
            setDocumentCategory(option.name)
          }
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
        <ButtonPrimary label="Add" onClick={saveDocumentHandler} />
      </div>
    </>
  );
}
