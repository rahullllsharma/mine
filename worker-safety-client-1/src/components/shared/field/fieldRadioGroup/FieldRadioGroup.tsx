import type { RadioGroupProps } from "../../radioGroup/RadioGroup";
import type { FieldProps } from "../Field";
import Paragraph from "../../paragraph/Paragraph";
import RadioGroup from "../../radioGroup/RadioGroup";
import Field from "../Field";

export type FieldRadioGroupProps = FieldProps &
  RadioGroupProps & {
    readOnly?: boolean;
  };

export default function FieldRadioGroup({
  options,
  defaultOption,
  onSelect,
  hasError,
  readOnly,
  ...fieldProps
}: FieldRadioGroupProps): JSX.Element {
  return (
    <Field {...fieldProps}>
      {readOnly ? (
        <Paragraph
          text={defaultOption?.description || defaultOption?.value.toString()}
        />
      ) : (
        <RadioGroup
          options={options}
          defaultOption={defaultOption}
          hasError={hasError}
          onSelect={onSelect}
        />
      )}
    </Field>
  );
}
