import type { FormEvent } from "react";
import { useEffect, useState, useMemo } from "react";
import Checkbox from "../shared/checkbox/Checkbox";

export type CheckboxOption = {
  id: string;
  name: string;
  isChecked?: boolean;
};

type CheckboxGroupProps = {
  options: CheckboxOption[];
  value?: CheckboxOption[];
  onChange?: (option: CheckboxOption[]) => void;
  onItemChange?: (item: CheckboxOption) => void;
  disabled?: boolean;
  hasError?: boolean;
  preventDuplicateIds?: boolean;
};

const getSelectedOptions = (
  options: CheckboxOption[],
  value: CheckboxOption[] = []
): CheckboxOption[] =>
  options.map(({ id, name }) => ({
    id,
    name,
    isChecked: !!value.find(item => item.id === id),
  }));

export default function CheckboxGroup({
  options,
  value,
  onChange,
  onItemChange,
  disabled = false,
  hasError = false,
  preventDuplicateIds = false,
}: CheckboxGroupProps): JSX.Element {
  const [selectedOptions, setSelectedOptions] = useState<CheckboxOption[]>(
    getSelectedOptions(options)
  );

  // Generate a unique prefix for this checkbox group only if preventDuplicateIds is true
  const groupPrefix = useMemo(
    () => (preventDuplicateIds ? Math.random().toString(36).slice(2, 8) : null),
    [preventDuplicateIds]
  );

  useEffect(() => {
    if (value) {
      setSelectedOptions(getSelectedOptions(options, value));
    }
  }, [options, value]);

  const handleItemSelect = (event: FormEvent<HTMLInputElement>) => {
    const {
      currentTarget: { checked, id },
    } = event;

    // Extract the original id only if using unique IDs
    const originalId = preventDuplicateIds
      ? id.split("__").slice(1).join("__")
      : id;

    if (onItemChange) {
      onItemChange(
        options
          .filter(option => option.id === originalId)
          .map(option => ({ ...option, isChecked: checked }))[0]
      );
    }

    const selectedItem = selectedOptions.find(
      option => option.id === originalId
    );

    if (selectedItem) {
      const newOptions = selectedOptions.map(option => {
        return option.id === originalId
          ? { ...selectedItem, isChecked: checked }
          : option;
      });
      setSelectedOptions(newOptions);

      if (onChange) {
        onChange(
          newOptions
            .filter(option => option.isChecked)
            .map(option => ({ id: option.id, name: option.name }))
        );
      }
    }
  };

  return (
    <div className="flex flex-col gap-3">
      {selectedOptions.map(option => {
        const uniqueId = preventDuplicateIds
          ? `${groupPrefix}__${option.id}`
          : option.id;
        return (
          <div key={uniqueId} className="flex items-center gap-2">
            <Checkbox
              id={uniqueId}
              onChange={handleItemSelect}
              checked={option.isChecked}
              disabled={disabled}
              hasError={hasError}
            />
            <label
              htmlFor={uniqueId}
              className="text-tiny text-neutral-shade-100"
            >
              {option.name}
            </label>
          </div>
        );
      })}
    </div>
  );
}
