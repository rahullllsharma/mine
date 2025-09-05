import type { FieldProps } from "../Field";
import type { MultiSelectProps } from "../../inputSelect/multiSelect/MultiSelect";
import Field from "../Field";
import MultiSelect from "../../inputSelect/multiSelect/MultiSelect";
import Paragraph from "../../paragraph/Paragraph";

type FieldMultiSelectProps = FieldProps &
  MultiSelectProps & {
    readOnly?: boolean;
  };

export default function FieldMultiSelect({
  options,
  value,
  defaultOption,
  isInvalid,
  placeholder,
  buttonRef,
  onSelect,
  icon,
  readOnly,
  ...fieldProps
}: FieldMultiSelectProps): JSX.Element {
  const readonlyDefaultOption =
    defaultOption?.map(option => option.name).join(", ") ?? "";
  return (
    <Field {...fieldProps}>
      {readOnly ? (
        <Paragraph text={readonlyDefaultOption} />
      ) : (
        <MultiSelect
          options={options}
          isInvalid={isInvalid}
          placeholder={placeholder}
          buttonRef={buttonRef}
          defaultOption={defaultOption}
          value={value}
          onSelect={onSelect}
          icon={icon}
          closeMenuOnSelect={false}
        />
      )}
    </Field>
  );
}
