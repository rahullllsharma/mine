import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";
import { useEffect, useState } from "react";
import { RadioGroup as HeadlessUiRadioGroup } from "@headlessui/react";

export type RadioGroupProps = PropsWithClassName<{
  direction?: "row" | "col";
  hideLabels?: boolean;
  isDisabled?: boolean;
  hasError?: boolean;
  options: RadioGroupOption[];
  defaultOption?: RadioGroupOption | null;
  onSelect: (option: string) => void;
}>;

export interface RadioGroupOption<T = string | boolean> {
  id: number;
  value: T;
  description?: string;
  disabled?: boolean;
}

const getContainerStyle = (isDisabled: boolean, hasError: boolean): string => {
  let containerStyle =
    "flex items-center justify-center border rounded-xl w-5 h-5 ";

  if (isDisabled) {
    containerStyle += "border-neutral-shade-26 cursor-not-allowed";
  } else if (hasError) {
    containerStyle += "border-system-error-40";
  } else {
    containerStyle +=
      "border-neutral-shade-38 cursor-pointer hover:border-neutral-shade-58 hover:shadow-10";
  }

  return containerStyle;
};

export default function RadioGroup({
  direction = "row",
  hideLabels,
  isDisabled = false,
  hasError = false,
  options,
  defaultOption,
  className,
  onSelect,
}: RadioGroupProps): JSX.Element {
  const [selected, setSelected] = useState(
    () => options.find(option => option.id === defaultOption?.id)?.value
  );

  useEffect(() => {
    const id = defaultOption?.id;
    const selectedValue = id
      ? options.find(option => option.id === id)?.value
      : undefined;

    setSelected(selectedValue);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [defaultOption?.id]);

  const handleOptionChecked = (option: string) => {
    setSelected(option);
    onSelect(option);
  };

  return (
    <HeadlessUiRadioGroup
      value={selected}
      onChange={handleOptionChecked}
      disabled={isDisabled}
      className={cx(`flex flex-wrap flex-${direction} gap-6`, className)}
    >
      {options.map((option: RadioGroupOption, index: number) => (
        <HeadlessUiRadioGroup.Option
          key={index}
          value={option.value}
          className="flex items-center"
          disabled={!!option.disabled}
        >
          {({ checked }) => {
            const isOptionDisabled = !!option.disabled || isDisabled;
            return (
              <>
                <div className={getContainerStyle(isOptionDisabled, hasError)}>
                  {checked && (
                    <div
                      className={`w-2.5 h-2.5 rounded-xl ${
                        isOptionDisabled
                          ? "bg-neutral-shade-58"
                          : "bg-brand-urbint-40 shadow-5"
                      }`}
                    ></div>
                  )}
                </div>

                {!hideLabels && (
                  <HeadlessUiRadioGroup.Label className="text-neutral-shade-100 text-base ml-2">
                    {option.description || option.value}
                  </HeadlessUiRadioGroup.Label>
                )}
              </>
            );
          }}
        </HeadlessUiRadioGroup.Option>
      ))}
    </HeadlessUiRadioGroup>
  );
}
