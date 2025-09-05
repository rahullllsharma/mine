import type { FormInputsOptions } from "@/container/admin/tenantAttributes/types";
import { Controller, useFormContext } from "react-hook-form";
import { useState } from "react";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { FieldRules } from "@/components/shared/field/FieldRules";
import { messages } from "@/locales/messages";
import { MappingInput } from "./mappingInput/MappingInput";
import { OptionsInput } from "./optionsInput/OptionsInput";

type AttributeSubmittedValues = {
  label: string;
  labelPlural: string;
  mappings?: Record<string, string[]>;
  options?: FormInputsOptions[];
};

type AttributeEditProps = {
  isEntityAttribute?: boolean;
  isSubmitting?: boolean;
  onSubmit: (data: AttributeSubmittedValues) => void;
  onCancel: () => void;
};

function AttributeEdit({
  isEntityAttribute,
  isSubmitting,
  onSubmit,
  onCancel,
}: AttributeEditProps): JSX.Element {
  const {
    formState: { errors },
    getValues,
    handleSubmit,
    setValue,
  } = useFormContext();
  const [mappingsBeingEdited, setMappingsBeingEdited] = useState(new Map());

  const { label, labelPlural, mappings } = getValues();
  const mappingsArray = Object.entries(
    (mappings as Record<string, string[]>) ?? {}
  );

  const rules = {
    ...FieldRules.REQUIRED,
    minLength: {
      value: 3,
      message: messages.minCharLength.replace("{value}", "3"),
    },
    maxLength: {
      value: 50,
      message: messages.maxCharLength.replace("{value}", "50"),
    },
  };

  const pluralLabel = mappingsArray.length === 1 ? "" : "s";
  const countValueLabel = `${mappingsArray.length} value${pluralLabel}`;

  return (
    <>
      <div className="flex flex-wrap gap-4">
        <Controller
          name="label"
          rules={rules}
          defaultValue={label}
          render={({ field }) => (
            <FieldInput
              {...field}
              htmlFor="label"
              id="label"
              label="Attribute name (singular)"
              error={errors.label?.message}
              containerClassName="w-full sm:flex-1"
            />
          )}
        />
        <Controller
          name="labelPlural"
          rules={rules}
          defaultValue={labelPlural}
          render={({ field }) => (
            <FieldInput
              {...field}
              htmlFor="labelPlural"
              id="labelPlural"
              label="Attribute name (plural)"
              error={errors.labelPlural?.message}
              containerClassName="w-full sm:flex-1"
            />
          )}
        />
      </div>
      {mappingsArray.length > 0 && (
        <section className="mt-6">
          <h6 className="flex justify-between font-medium mb-1 text-sm">
            <span>Attributes Values</span>
            <span>{countValueLabel}</span>
          </h6>
          <ul className="bg-brand-gray-10 p-3">
            {mappingsArray.map(([key, value], index) => (
              <li key={index} className="p-2 mb-2 last:mb-0 bg-white">
                <MappingInput
                  defaultLabel={key}
                  label={value[0]}
                  isDefault={index === 0}
                  badgeNumber={index + 1}
                  onSubmit={(newLabel: string) => {
                    setValue("mappings", { ...mappings, [key]: [newLabel] });
                  }}
                  onEditOpen={() => {
                    setMappingsBeingEdited(
                      previousMap => new Map(previousMap.set(key, true))
                      
                    );
                  }}
                  onEditClose={() => {
                    setMappingsBeingEdited(
                      previousMap => new Map(previousMap.set(key, false))
                    );
                  }}
                />
              </li>
            ))}
          </ul>
        </section>
      )}
      {isEntityAttribute && <OptionsInput />}
      <footer className="flex justify-end mt-6 gap-4">
        <ButtonTertiary label="Cancel" onClick={onCancel} />
        <ButtonPrimary
          label="Save"
          type="submit"
          disabled={[...mappingsBeingEdited.values()].some(key => key)}
          onClick={handleSubmit((data: AttributeSubmittedValues) => {
            onSubmit(data);
          })}
          loading={isSubmitting}
        />
      </footer>
    </>
  );
}

export { AttributeEdit };
export type { AttributeSubmittedValues };
