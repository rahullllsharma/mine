import type { PropsWithClassName } from "@/types/Generic";
import type { Control } from "@/types/project/Control";
import type { ControlAnalysisInput } from "@/types/report/DailyReportInputs";
import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import { get } from "lodash-es";
import cx from "classnames";
import { useFormContext, Controller } from "react-hook-form";
import FieldSelect from "@/components/shared/field/fieldSelect/FieldSelect";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { jobHazardAnalysisFormInputPrefix } from "@/components/report/jobReport/JobReportCard";
import { FieldRules } from "@/components/shared/field/FieldRules";
import { getControlNotPerformedOptions } from "@/container/report/jobHazardAnalysis/constants";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export type ControlReportCardProps = PropsWithClassName<{
  selectedControl?: ControlAnalysisInput;
  formGroupKey: string;
  control: Control;
  isCompleted?: boolean;
}>;

const options: RadioGroupOption[] = [
  { id: 1, value: true, description: "Implemented" },
  { id: 2, value: false, description: "Not Implemented" },
];

const getDefaultOption = (value?: boolean | null) => {
  // this is "tied" to the index in the options array. maybe we could use an object instead?
  return typeof value === "boolean" ? options[value ? 0 : 1] : null;
};

export default function ControlReportCard({
  selectedControl,
  formGroupKey,
  control,
  isCompleted,
  className,
}: ControlReportCardProps): JSX.Element {
  const { control: controlEntity } = useTenantStore(state =>
    state.getAllEntities()
  );
  const fieldControl = `${jobHazardAnalysisFormInputPrefix}.${formGroupKey}.controls.${control.id}`;
  const radioControlId = `${fieldControl}.implemented`;
  const selectControlId = `${fieldControl}.notImplementedReason`;
  const furtherExplanationControl = `${fieldControl}.furtherExplanation`;

  const {
    formState: { errors },
    getValues,
    watch,
  } = useFormContext();

  // By default, dont choose anything, we force the user to make a decision.
  const implementedDefaultOption = getDefaultOption(
    selectedControl?.implemented
  );

  const watchControlImplemented = watch(
    radioControlId,
    getValues(radioControlId) ?? implementedDefaultOption?.value
  );

  const reasonDefaultOption = selectedControl?.notImplementedReason
    ? {
        id: selectedControl?.notImplementedReason,
        name: selectedControl?.notImplementedReason,
      }
    : undefined;

  const furtherExplanationDefaultValue = selectedControl?.furtherExplanation;

  const radioControlError = get(errors, radioControlId);
  const selectControlError = get(errors, selectControlId);
  const furtherExplanationControlError = get(errors, furtherExplanationControl);

  return (
    <div
      className={cx(
        "border border-dashed border-brand-gray-40 rounded-lg pt-4 pb-3 px-4",
        className
      )}
      data-testid={`control-report-card-${control.id}`}
    >
      <Controller
        name={radioControlId}
        defaultValue={implementedDefaultOption?.value}
        rules={FieldRules.BOOLEAN_REQUIRED}
        render={({ field: { onChange, value } }) => (
          <FieldRadioGroup
            label={control.name}
            required
            options={options}
            error={radioControlError?.message}
            hasError={!!radioControlError}
            defaultOption={getDefaultOption(value)}
            onSelect={onChange}
            readOnly={isCompleted}
          />
        )}
      />
      {watchControlImplemented === false && (
        <>
          <Controller
            name={selectControlId}
            // TODO: if we need an id, then this should be updated to only use the .id from CONTROL_NOT_PERFORMED_OPTIONS
            rules={FieldRules.REQUIRED}
            defaultValue={reasonDefaultOption}
            render={({ field: { onChange, ref } }) => (
              <FieldSelect
                className="mt-4"
                label={`Why is this ${controlEntity.label.toLowerCase()} not implemented?`}
                required
                options={getControlNotPerformedOptions()}
                defaultOption={reasonDefaultOption}
                isInvalid={!!selectControlError}
                buttonRef={ref}
                onSelect={onChange}
                readOnly={isCompleted}
              />
            )}
          />

          <Controller
            name={furtherExplanationControl}
            rules={FieldRules.REQUIRED}
            defaultValue={furtherExplanationDefaultValue}
            render={({ field }) => (
              <FieldTextArea
                {...field}
                required
                initialValue={field.value}
                label="Further Explanation"
                className="mt-4"
                readOnly={isCompleted}
                error={furtherExplanationControlError?.message}
                hasError={!!furtherExplanationControlError}
              />
            )}
          />
        </>
      )}
    </div>
  );
}
