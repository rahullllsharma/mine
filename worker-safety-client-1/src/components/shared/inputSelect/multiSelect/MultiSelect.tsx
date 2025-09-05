import type { InputSelectOption, InputSelectProps } from "../InputSelect";
import InputSelect from "../InputSelect";

export type MultiSelectProps = Omit<
  InputSelectProps<InputSelectOption[]>,
  "isMulti" | "size"
>;

export default function MultiSelect({
  onSelect,
  ...props
}: MultiSelectProps): JSX.Element {
  const handleItemSelect = (
    item: InputSelectOption | readonly InputSelectOption[]
  ): void => onSelect(item as InputSelectOption[]);

  return <InputSelect {...props} isMulti onSelect={handleItemSelect} />;
}
