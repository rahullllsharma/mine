import type {
  AttributeForm,
  PersonnelSettingsProps,
  PersonnelAttributeUserValue,
  PersonnelComponentType,
} from "@/components/templatesComponents/customisedForm.types";
import { useState, useEffect } from "react";
import { v4 as uuid } from "uuid";
import { InputRaw } from "@/components/forms/Basic/Input";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import Modal from "@/components/shared/modal/Modal";
import AddAttribute from "./AddAttribute";

const PersonnelSettings = ({
  item,
  onClose,
  onSave,
}: PersonnelSettingsProps) => {
  const [componentLabel, setComponentLabel] = useState(
    item.properties.title || "Sign Off"
  );
  const [attributes, setAttributes] = useState<AttributeForm[]>([]);

  useEffect(() => {
    if (item.properties.attributes && item.properties.attributes.length > 0) {
      const existingAttributes = item.properties.attributes.map(attr => ({
        label: attr.attribute_name,
        isRequired: attr.is_required_for_form_completion,
        appliesTo: attr.applies_to_user_value,
      }));
      setAttributes(existingAttributes);
    }
  }, [item.properties.attributes]);

  const handleAttributeSubmit = (newAttributes: AttributeForm[]) => {
    setAttributes(newAttributes);
  };

  const createObjectForPersonnelComponent = (): PersonnelComponentType => {
    return {
      type: CWFItemType.PersonnelComponent,
      properties: {
        title: componentLabel,
        include_in_summary: item.properties.include_in_summary,
        attributes: attributes.map(attr => ({
          attribute_id: uuid(),
          attribute_name: attr.label,
          is_required_for_form_completion: attr.isRequired,
          applies_to_user_value: attr.appliesTo as PersonnelAttributeUserValue,
        })),
        user_value: [],
      },
      contents: item.contents,
      id: item.id,
      order: item.order,
    };
  };

  const handleSave = () => {
    if (
      componentLabel.trim() &&
      (attributes.length === 0 || attributes.every(attr => attr.label.trim()))
    ) {
      const updatedComponent = createObjectForPersonnelComponent();
      onSave(updatedComponent);
      onClose();
    }
  };

  const isFormValid =
    componentLabel.trim() &&
    (attributes.length === 0 || attributes.every(attr => attr.label.trim()));

  const canAddAttribute =
    attributes.length === 0 || attributes.every(form => form.label.trim());

  return (
    <Modal
      isOpen={true}
      closeModal={onClose}
      title="Personnel Settings"
      size="lg"
    >
      <div>
        <div className="mb-6">
          <InputRaw
            label="Component Label"
            placeholder="Enter component label"
            value={componentLabel}
            onChange={value => setComponentLabel(value)}
          />
        </div>

        <div>
          <h6 className="text-lg font-semibold mb-2">Attributes</h6>
          <p className="text-sm text-neutral-shade-75 mb-4">
            Attributes can be used to indicate specific characteristics or roles
            to names on the form. For each, define if it applies to a single
            name or multiple names, and if it&apos;s required for form
            completion.
          </p>

          <AddAttribute
            onAdd={handleAttributeSubmit}
            disabled={!canAddAttribute}
            initialAttributes={attributes}
          />
        </div>
      </div>

      <div className="flex justify-end gap-2 mt-8 pt-4 border-t">
        <ButtonRegular label="Cancel" onClick={onClose} />
        <ButtonPrimary
          label="Save"
          onClick={handleSave}
          disabled={!isFormValid}
        />
      </div>
    </Modal>
  );
};

export default PersonnelSettings;
