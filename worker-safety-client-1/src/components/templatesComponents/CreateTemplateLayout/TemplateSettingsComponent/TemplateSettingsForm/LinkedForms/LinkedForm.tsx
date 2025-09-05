import type { LinkedFormProps } from "@/components/templatesComponents/customisedForm.types";
import type { CheckboxOption } from "@/components/checkboxGroup/CheckboxGroup";
import { useState } from "react";
import { Controller, useFormContext } from "react-hook-form";
import { Subheading } from "@urbint/silica";
import CheckboxGroup from "@/components/checkboxGroup/CheckboxGroup";

export default function LinkedForms({
  settings,
}: LinkedFormProps): JSX.Element {
  const { setValue } = useFormContext();
  const [currentCopyAndRebrief, setCurrentCopyAndRebrief] = useState(settings.copy_and_rebrief);

  // Build template options based on current state
  const linkedTypeOptions = [
    {
      id: "rebrief",
      name: "Allow rebriefing this form (available during Edit Period)",
      isChecked: currentCopyAndRebrief?.is_rebrief_enabled,
    },
    {
      id: "copy",
      name: "Allow copying this form",
      isChecked: currentCopyAndRebrief?.is_copy_enabled,
    },
  ];

  return (
    <div className="p-4">
      <Subheading>Linked Forms</Subheading>
      <div className="pt-4">
        <Controller
          name="copy_and_rebrief"
          defaultValue={linkedTypeOptions}
          render={({ field }) => (
            <div>
              <CheckboxGroup
                options={linkedTypeOptions}
                value={linkedTypeOptions.filter(option => option.isChecked)}
                onChange={async(newValue: CheckboxOption[]) => {
                  const updatedConnectivity = {
                    is_copy_enabled: !!newValue.find(option => option.id === "copy"),
                    is_rebrief_enabled: !!newValue.find(option => option.id === "rebrief"),
                  };
                    // Update local state
                    setCurrentCopyAndRebrief(updatedConnectivity);
                    // Update form state with validation and dirty state
                    setValue("copy_and_rebrief", updatedConnectivity, {
                      shouldDirty: true,
                    });
                    // trigger validation for immediate feedback
                    await field.onChange(updatedConnectivity);
                }}
              />
            </div>
          )}
        />
      </div>
    </div>
  );
}
