import type { FieldProps } from "../Field";
import type { SelectPrimaryProps } from "../../select/selectPrimary/SelectPrimary";
import Field from "../Field";
import SelectPrimary from "../../select/selectPrimary/SelectPrimary";
import Paragraph from "../../paragraph/Paragraph";

export type FieldSelectProps = FieldProps &
  SelectPrimaryProps & {
    readOnly?: boolean;
  };

export default function FieldSelect({
  options,
  defaultOption,
  isInvalid,
  placeholder,
  buttonRef,
  size,
  onSelect,
  readOnly,
  ...fieldProps
}: FieldSelectProps): JSX.Element {
  return (
    <Field {...fieldProps}>
      {readOnly ? (
        <Paragraph text={defaultOption?.name} />
      ) : (
        <SelectPrimary
          options={options}
          isInvalid={isInvalid}
          placeholder={placeholder}
          buttonRef={buttonRef}
          defaultOption={defaultOption}
          size={size}
          onSelect={onSelect}
        />
      )}
    </Field>
  );
}
