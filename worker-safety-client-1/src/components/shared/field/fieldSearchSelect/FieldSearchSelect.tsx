import type { FieldProps } from "../Field";
import type { SearchSelectProps } from "../../inputSelect/searchSelect/SearchSelect";
import Field from "../Field";
import SearchSelect from "../../inputSelect/searchSelect/SearchSelect";
import Paragraph from "../../paragraph/Paragraph";

export type FieldSearchSelectProps = FieldProps &
  SearchSelectProps & {
    readOnly?: boolean;
  };

export default function FieldSearchSelect({
  options,
  defaultOption,
  isInvalid,
  placeholder,
  buttonRef,
  size,
  onSelect,
  onBlur,
  readOnly,
  icon,
  isClearable,
  value,
  ...fieldProps
}: FieldSearchSelectProps): JSX.Element {
  return (
    <Field {...fieldProps}>
      {readOnly ? (
        <Paragraph text={defaultOption?.name} />
      ) : (
        <SearchSelect
          options={options}
          isInvalid={isInvalid}
          placeholder={placeholder}
          buttonRef={buttonRef}
          defaultOption={defaultOption}
          size={size}
          onSelect={onSelect}
          onBlur={onBlur}
          icon={icon}
          isClearable={isClearable}
          value={value}
        />
      )}
    </Field>
  );
}
