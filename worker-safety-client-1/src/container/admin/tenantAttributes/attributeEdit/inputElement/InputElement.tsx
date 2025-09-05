import type { FormEvent } from "react";
import type { ValidKeys } from "@/container/admin/tenantAttributes/types";
import { Controller } from "react-hook-form";
import cx from "classnames";
import { useState, useEffect } from "react";
import Checkbox from "@/components/shared/checkbox/Checkbox";

type InputElementProps = {
  index: number;
  label: ValidKeys;
  value: boolean;
  isDisabled: boolean;
  isMandatory: boolean;
  onInputChange: (key: ValidKeys, value: boolean) => void;
};

function InputElement({
  index,
  label,
  value,
  isDisabled,
  isMandatory,
  onInputChange,
}: InputElementProps) {
  const [isChecked, setIsChecked] = useState(value);

  useEffect(() => {
    setIsChecked(value);
  }, [value]);

  return (
    <Controller
      name={`options.${index}.value`}
      defaultValue={value}
      render={({ field }) => (
        <label
          className={cx("flex items-center gap-3", {
            "hover:cursor-pointer": !isMandatory,
            "hover:cursor-not-allowed": isMandatory,
          })}
        >
          <Checkbox
            {...field}
            id={`options.${index}.value`}
            label={label}
            disabled={isMandatory || isDisabled}
            checked={isChecked}
            onChange={(event: FormEvent<HTMLInputElement>) => {
              /**
               * Maintain RHF normal behaviour
               */
              field.onChange(event);
              onInputChange(label, event.currentTarget.checked);
            }}
            onClick={() => setIsChecked(previousChecked => !previousChecked)}
          />
          <span
            className={cx("capitalize", {
              "text-neutral-shade-100": !(isMandatory || isDisabled),
              "text-neutral-shade-75": isMandatory || isDisabled,
            })}
          >
            {label}
          </span>
        </label>
      )}
    />
  );
}

export { InputElement };
