import type {
  AttributeForm,
  AddAttributeComponentProps,
} from "@/components/templatesComponents/customisedForm.types";
import { useState, useEffect } from "react";
import { BodyText } from "@urbint/silica";
import { InputRaw } from "@/components/forms/Basic/Input";
import { Checkbox } from "@/components/forms/Basic/Checkbox";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import { APPLIES_OPTIONS } from "@/utils/customisedFormUtils/customisedForm.constants";

const AddAttribute = ({
  onAdd,
  disabled,
  initialAttributes,
}: AddAttributeComponentProps & { initialAttributes?: AttributeForm[] }) => {
  const [attributeForms, setAttributeForms] = useState<AttributeForm[]>([]);

  useEffect(() => {
    if (initialAttributes && initialAttributes.length > 0) {
      setAttributeForms(initialAttributes);
      if (onAdd) {
        onAdd(initialAttributes);
      }
    }
  }, [initialAttributes, onAdd]);

  const handleInputChange = (
    index: number,
    field: string,
    value: string | boolean
  ) => {
    const updated = attributeForms.map((form, i) =>
      i === index ? { ...form, [field]: value } : form
    );

    setAttributeForms(updated);
    if (onAdd) {
      onAdd(updated);
    }
  };

  const addNewAttribute = () => {
    if (
      attributeForms.length === 0 ||
      attributeForms.every(form => form.label.trim())
    ) {
      const newForms = [
        ...attributeForms,
        {
          label: "",
          isRequired: false,
          appliesTo: "multiple_names",
        },
      ];
      setAttributeForms(newForms);
      if (onAdd) {
        onAdd(newForms);
      }
    }
  };

  const removeAttribute = (indexToRemove: number) => {
    const updated = attributeForms.filter(
      (_, index) => index !== indexToRemove
    );
    setAttributeForms(updated);
    if (onAdd) {
      onAdd(updated);
    }
  };

  return (
    <div className="mt-4">
      <div className="flex flex-col">
        {attributeForms.map((form, index) => (
          <div key={index}>
            <div className="flex flex-col gap-4">
              <div>
                <div className="mb-1">
                  <BodyText className="text-sm font-medium text-neutral-shade-100">
                    Attribute Label {index + 1}
                  </BodyText>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-grow">
                    <InputRaw
                      placeholder="Enter attribute label"
                      value={form.label}
                      onChange={value => {
                        handleInputChange(index, "label", value);
                      }}
                    />
                  </div>
                  <ButtonTertiary
                    label="Remove"
                    iconStart="minus_circle_outline"
                    size="sm"
                    onClick={() => removeAttribute(index)}
                  />
                </div>
              </div>

              <div>
                <Checkbox
                  checked={form.isRequired}
                  onClick={() =>
                    handleInputChange(index, "isRequired", !form.isRequired)
                  }
                >
                  <span className="text-brand-gray-80 text-sm">
                    Required for form completion
                  </span>
                </Checkbox>
              </div>

              <div>
                <FieldRadioGroup
                  label="Applies to"
                  options={APPLIES_OPTIONS}
                  defaultOption={APPLIES_OPTIONS.find(
                    opt => opt.value === form.appliesTo
                  )}
                  onSelect={value =>
                    handleInputChange(index, "appliesTo", value)
                  }
                />
              </div>
            </div>
            {index < attributeForms.length - 1 && (
              <div className="my-6">
                <hr className="border-neutral-shade-26" />
              </div>
            )}
          </div>
        ))}

        <div className="my-6">
          <hr className="border-neutral-shade-26" />
        </div>

        <div>
          <ButtonTertiary
            label="Add Attribute"
            iconStart="plus_circle_outline"
            size="sm"
            onClick={addNewAttribute}
            disabled={
              !attributeForms.every(form => form.label.trim()) || disabled
            }
          />
        </div>
      </div>
    </div>
  );
};

export default AddAttribute;
