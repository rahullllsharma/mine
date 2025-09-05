import CheckboxGroup from "@/components/checkboxGroup/CheckboxGroup";
import MultiSelect from "@/components/shared/inputSelect/multiSelect/MultiSelect";

type MultiOptionType = "checkbox" | "multiSelect";

export type MultiOption = {
  id: string;
  name: string;
};

type MultiOptionWrapperProps = {
  options: MultiOption[];
  value?: MultiOption[];
  type?: MultiOptionType;
  onSelect: (option: MultiOption[]) => void;
};

export default function MultiOptionWrapper({
  options,
  value,
  type,
  onSelect,
}: MultiOptionWrapperProps): JSX.Element {
  const isMultiSelect = type === "multiSelect" || (!type && options.length > 4);

  return (
    <>
      {isMultiSelect ? (
        <MultiSelect
          options={options}
          value={value}
          onSelect={multiOptions => onSelect(multiOptions as MultiOption[])}
        />
      ) : (
        <CheckboxGroup options={options} value={value} onChange={onSelect} />
      )}
    </>
  );
}
