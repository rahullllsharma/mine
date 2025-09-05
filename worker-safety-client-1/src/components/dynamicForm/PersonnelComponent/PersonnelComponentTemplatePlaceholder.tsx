import type {
  PersonnelComponentProperties,
  PersonnelAttribute,
} from "@/components/templatesComponents/customisedForm.types";
import { SectionHeading } from "@urbint/silica";
import { useEffect, useState } from "react";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import FieldSelect from "@/components/shared/field/fieldSelect/FieldSelect";
import CheckboxGroup from "@/components/checkboxGroup/CheckboxGroup";
import { DEFAULT_ATTRIBUTE_CHOICE } from "@/utils/customisedFormUtils/customisedForm.constants";

const getUniqueAttributes = (
  attributes: PersonnelAttribute[]
): PersonnelAttribute[] => {
  if (!attributes || attributes.length === 0) {
    return [];
  }

  const uniqueAttributes = new Map<string, PersonnelAttribute>();

  attributes.forEach(attr => {
    if (!uniqueAttributes.has(attr.attribute_name)) {
      uniqueAttributes.set(attr.attribute_name, {
        applies_to_user_value: attr.applies_to_user_value,
        attribute_id: attr.attribute_id,
        attribute_name: attr.attribute_name,
        is_required_for_form_completion: attr.is_required_for_form_completion,
      });
    }
  });

  return Array.from(uniqueAttributes.values());
};

const PersonnelComponentTemplatePlaceholder = ({
  isDisabled,
  properties,
}: {
  isDisabled: boolean;
  properties: PersonnelComponentProperties;
}) => {
  const [checkboxOptions, setCheckboxOptions] = useState<
    Array<{ id: string; name: string; isChecked?: boolean }>
  >([DEFAULT_ATTRIBUTE_CHOICE]);

  useEffect(() => {
    const attributes = getUniqueAttributes(properties.attributes);

    if (attributes.length > 0) {
      const newOptions = attributes.map(attr => ({
        id: attr.attribute_id,
        name: attr.attribute_name,
        isChecked: false,
      }));

      setCheckboxOptions(newOptions);
    } else {
      setCheckboxOptions([DEFAULT_ATTRIBUTE_CHOICE]);
    }
  }, [properties.attributes]);

  const handleCheckboxChange = (
    selectedOptions: Array<{ id: string; name: string }>
  ) => {
    setCheckboxOptions(prevOptions =>
      prevOptions.map(option => ({
        ...option,
        isChecked: selectedOptions.some(selected => selected.id === option.id),
      }))
    );
  };

  const options = [{ id: "placeholder", name: "Placeholder Option XYZ" }];

  return (
    <div>
      <SectionHeading className="text-xl text-neutral-shade-100 font-semibold mb-2">
        {properties.title || "Personnel"}
      </SectionHeading>

      <div className="flex flex-col gap-2 p-4 bg-gray-100">
        <label className="block md:text-sm text-neutral-shade-75 font-semibold leading-normal">
          Name
        </label>
        <div
          className={`flex flex-col gap-2 ${
            isDisabled ? "pointer-events-none opacity-50" : ""
          }`}
        >
          <FieldSelect options={options} onSelect={() => null} placeholder="" />
          <CheckboxGroup
            options={checkboxOptions}
            value={checkboxOptions.filter(opt => opt.isChecked)}
            disabled={isDisabled}
            onChange={handleCheckboxChange}
          />

          <ButtonSecondary
            disabled={isDisabled}
            iconStart="plus_circle_outline"
            label="Sign for Name"
            className="w-fit"
          />
        </div>
      </div>
    </div>
  );
};

export default PersonnelComponentTemplatePlaceholder;
