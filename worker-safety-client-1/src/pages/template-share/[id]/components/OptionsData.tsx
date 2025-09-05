import type {
  ChoiceProperties,
  DropdownPropertiesType,
  ChoiceAndDropdownDataProps,
} from "@/components/templatesComponents/customisedForm.types";
import { BodyText, ComponentLabel } from "@urbint/silica";

const isChoiceProperties = (
  properties: unknown
): properties is ChoiceProperties =>
  typeof (properties as ChoiceProperties).choice_type === "string" &&
  Array.isArray((properties as ChoiceProperties).options);

const isDropdownProperties = (
  properties: unknown
): properties is DropdownPropertiesType =>
  typeof (properties as DropdownPropertiesType).multiple_choice === "boolean" &&
  Array.isArray((properties as DropdownPropertiesType).options);

const OptionsData = ({ content }: ChoiceAndDropdownDataProps) => {
  const properties = content.properties;

  let title = "";
  let options: { value: string; label: string }[] = [];
  let selectedOptions: string[] = [];

  if (isChoiceProperties(properties)) {
    title = properties.title;
    options = properties.options;
    selectedOptions = [...(properties.user_value ?? [])];
  } else if (isDropdownProperties(properties)) {
    title = properties.title;
    options = properties.options;
    selectedOptions = [...(properties.user_value ?? [])];
  } else {
    return <div>Invalid properties</div>;
  }

  const renderOtherText = (optionValue: string, label: string) => {
    if (
      optionValue.toLowerCase() === "other" ||
      label.toLowerCase() === "other"
    ) {
      if (
        properties.user_other_value &&
        properties.user_other_value.trim() !== ""
      ) {
        return `${label}: ${properties.user_other_value}`;
      }
    }
    return label;
  };

  const renderAnswer = () => {
    if (selectedOptions.length > 0) {
      if (
        (isChoiceProperties(properties) &&
          properties.choice_type === "single_choice") ||
        (isDropdownProperties(properties) && !properties.multiple_choice)
      ) {
        const selectedValue = selectedOptions[0];
        const label =
          options.find(o => o.value === selectedValue)?.label || selectedValue;
        return (
          <BodyText className="text-base">
            {renderOtherText(selectedValue, label)}
          </BodyText>
        );
      }

      return (
        <ul className="list-disc list-inside pl-2">
          {selectedOptions.map((option, index) => {
            const label =
              options.find(opt => opt.value === option)?.label || option;
            return (
              <li key={index} className="text-base">
                {renderOtherText(option, label)}
              </li>
            );
          })}
        </ul>
      );
    }
  };

  return (
    <div className="flex flex-col gap-2 bg-brand-gray-10 p-4 rounded-lg">
      <ComponentLabel className="text-md font-semibold">{title}</ComponentLabel>
      {renderAnswer()}
    </div>
  );
};

export default OptionsData;
