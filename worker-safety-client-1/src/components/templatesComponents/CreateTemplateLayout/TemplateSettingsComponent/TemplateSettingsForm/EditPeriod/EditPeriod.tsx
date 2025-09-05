import type { EditPeriodProps } from "../../../../customisedForm.types";
import { Controller, useFormContext } from "react-hook-form";
import { CaptionText, Subheading } from "@urbint/silica";
import { useEffect, useState } from "react";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";

export default function EditPeriod({ settings }: EditPeriodProps): JSX.Element {
  const { setValue } = useFormContext();
  const [currentPeriod, setCurrentPeriod] = useState(settings.edit_expiry_days);

  useEffect(() => {
    setCurrentPeriod(settings.edit_expiry_days);
  }, [settings.edit_expiry_days]);

  return (
    <div>
      <Subheading>Edit Period *</Subheading>
      <CaptionText className="text-neutral-shade-58 leading-[3rem]">
        Setting in days to define how long after the Completed On date users are
        allowed to edit forms that are in Complete status
      </CaptionText>
      <CaptionText className="text-neutral-shade-58 leading-[3rem]">
        Edit Period (days)
      </CaptionText>
      <Controller
        name="edit_expiry_days"
        defaultValue={currentPeriod}
        rules={{
          required: "This is a required field",
          validate: value =>
            value >= 0 || "Edit period must be a non-negative number",
        }}
        render={({ field, fieldState: { error } }) => (
          <div>
            <FieldInput
              value={currentPeriod}
              type="number"
              required
              error={error?.message}
              min={0}
              onChange={e => {
                const value = parseInt(
                  (e.target as HTMLInputElement).value,
                  10
                );
                setCurrentPeriod(value);

                setValue("edit_expiry_days", value, { shouldDirty: true });

                field.onChange(value);
              }}
            />
          </div>
        )}
      />
    </div>
  );
}
