import type {
  FormInputs,
  ValidKeys,
} from "@/container/admin/tenantAttributes/types";
import { useFormContext } from "react-hook-form";
import {
  isMandatoryField,
  shouldUpdateNonVisibleFields,
} from "@/container/admin/tenantAttributes/attributeEdit/optionsInput/utils";
import { InputElement } from "@/container/admin/tenantAttributes/attributeEdit/inputElement/InputElement";

function OptionsInput() {
  const { getValues, setValue, watch } = useFormContext<FormInputs>();
  const { mandatory } = getValues();
  /**
   * Using watch instead of using of useFieldArray,
   * because watch will trigger on value change that occurs in onCheckboxChange
   */
  const watchOptions = watch("options");

  const onCheckboxChange = (key: ValidKeys, value: boolean) => {
    if (shouldUpdateNonVisibleFields(key)) {
      const { options } = getValues();
      const updatedOptions = options.map(entry => {
        if (entry.key === key) {
          return entry;
        }

        return {
          ...entry,
          /**
           * We only want to update the value if the visible value is set to false
           * in case it's true, we want to keep the value in the fields array
           */
          ...(value ? {} : { value }),
          isDisabled: !value,
        };
      });

      setValue("options", updatedOptions);
    }
  };

  return (
    <section className="mt-6">
      <h6 className="font-medium text-sm">Attribute&#39;s attributes</h6>
      <p className="text-sm mt-1 text-neutral-shade-75">
        Visible attributes will be displayed in the application; required
        attributes require a value.
      </p>
      <ul className="flex gap-6 my-3">
        {watchOptions.map(({ key, value, isDisabled }, index) => {
          const isMandatory = isMandatoryField(mandatory, key);

          return (
            <li key={key}>
              {/*
               * This component was added to better track inner state, because of the visibility rules.
               * When changing the 'visible' checkbox to false, the rest of the options should default to false.
               * When the input was uncontrolled, this change was not happening, the previous value was kept.
               * So if visible was set to false and required was true, required would get disabled,
               * but the true value would visually persist.
               * With this approach, the required value now changes to true.
               */}
              <InputElement
                index={index}
                label={key}
                value={value}
                isDisabled={isDisabled}
                isMandatory={isMandatory}
                onInputChange={onCheckboxChange}
              />
            </li>
          );
        })}
      </ul>
      {mandatory && (
        <p className="text-sm mt-1 text-neutral-shade-75">
          This attribute is mandatory.
        </p>
      )}
    </section>
  );
}

export { OptionsInput };
