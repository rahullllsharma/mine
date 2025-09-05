import type { TemplateSettings } from "../../../../customisedForm.types";
import type { CheckboxOption } from "../../../../../checkboxGroup/CheckboxGroup";
import { Controller, useFormContext } from "react-hook-form";
import { CaptionText, Subheading } from "@urbint/silica";
import CheckboxGroup from "../../../../../checkboxGroup/CheckboxGroup";
import { useEffect, useState } from "react";

type TemplateAvailabilityProps = {
  settings: TemplateSettings;
};

export default function TemplateAvailability({
  settings,
}: TemplateAvailabilityProps): JSX.Element {
  const { setValue } = useFormContext();
  const [currentAvailability, setCurrentAvailability] = useState(settings.availability);

  // Update local state when settings change
  useEffect(() => {
    setCurrentAvailability(settings.availability);
  }, [settings.availability]);

  // Build template options based on current state
  const templateTypeOptions = [
    {
      id: "adhoc",
      name: "Ad-hoc template",
      isChecked: currentAvailability.adhoc.selected,
    },
    {
      id: "work_package",
      name: "Work package template",
      isChecked: currentAvailability.work_package.selected,
    },
  ];

  return (
    <div>
      <Subheading>Template Availability *</Subheading>
      <CaptionText className="text-neutral-shade-58 leading-[3rem]">
        Select the template&apos;s availability as Ad-Hoc, Work Package, or
        Both.
      </CaptionText>
      <CaptionText className="text-neutral-shade-58 leading-[3rem]">
        <span className="text-neutral-shade-75">Ad-Hoc templates</span> appear
        only through the “Add” option on the Forms List Page.
      </CaptionText>
      <CaptionText className="text-neutral-shade-58 leading-[3rem]">
        <span className="text-neutral-shade-75">Work Package templates</span>{" "}
        are available exclusively in a Work Package via the “Add” option in the
        Daily Summary View.
      </CaptionText>
      <Controller
        name="availability"
        defaultValue={templateTypeOptions}
        rules={{
          validate: value =>
            Object.values(value).some((option: any) => option.selected) ||
            "At least one Template Availability option must be selected",
        }}
        render={({ field, fieldState: { error } }) => (
          <div>
            <CheckboxGroup
              options={templateTypeOptions}
              value={templateTypeOptions.filter(option => option.isChecked)}
              onChange={async(newValue: CheckboxOption[]) => {
                const updatedAvailability = {
                  adhoc: {
                    selected: !!newValue.find(option => option.id === "adhoc"),
                  },
                  work_package: {
                    selected: !!newValue.find(
                      option => option.id === "work_package"
                    ),
                  },
                };

                  // Update local state
                  setCurrentAvailability(updatedAvailability);

                  // Update form state with validation and dirty state
                  setValue("availability", updatedAvailability, {
                    shouldDirty: true,
                  });
        
                  // trigger validation for immediate feedback
                  await field.onChange(updatedAvailability);
              }}
            />
            {error && (
              <span className="text-red-500 text-sm mt-1">{error.message}</span>
            )}
          </div>
        )}
      />
    </div>
  );
}
