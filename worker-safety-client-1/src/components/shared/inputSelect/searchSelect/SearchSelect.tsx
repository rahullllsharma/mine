import type { InputSelectOption, InputSelectProps } from "../InputSelect";
import InputSelect from "../InputSelect";

export type SearchSelectProps = Omit<
  InputSelectProps<InputSelectOption>,
  "isSearchable"
>;

export default function SearchSelect({
  onSelect,
  ...props
}: SearchSelectProps): JSX.Element {
  const handleItemSelect = (
    item: InputSelectOption | readonly InputSelectOption[]
  ): void => onSelect(item as InputSelectOption);

  return <InputSelect {...props} isSearchable onSelect={handleItemSelect} />;
}
