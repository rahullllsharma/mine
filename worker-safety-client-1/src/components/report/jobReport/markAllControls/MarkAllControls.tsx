import type { HazardAnalysisInput } from "@/types/report/DailyReportInputs";
import type {
  HazardAggregator,
  TaskHazardAggregator,
} from "@/types/project/HazardAggregator";
import { useFormContext } from "react-hook-form";
import { useState } from "react";
import { useUpdateEffect } from "usehooks-ts";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import Checkbox from "@/components/shared/checkbox/Checkbox";

function hasAllControlsImplemented(hazards: HazardAnalysisInput[] = []) {
  if (hazards.length === 0) {
    return false;
  }

  const controlsImplemented = hazards
    .map(hazard => hazard.controls.map(control => control.implemented))
    .flat();

  return controlsImplemented.every(Boolean);
}

type MarkAllControlsProps = {
  element: TaskHazardAggregator | HazardAggregator;
  hazards?: HazardAnalysisInput[];
  formGroupKey: "siteConditions" | "tasks";
};

const MarkAllControls = ({
  element,
  hazards,
  formGroupKey,
}: MarkAllControlsProps) => {
  const { control: controlEntity } = useTenantStore(state =>
    state.getAllEntities()
  );
  const methods = useFormContext();
  const [isMarkAllChecked, setIsMarkAllChecked] = useState<boolean>(() =>
    hasAllControlsImplemented(hazards)
  );

  const fieldValues = element.hazards
    .map(hazard =>
      hazard.controls.map(
        control =>
          `jobHazardAnalysis.${formGroupKey}.${element.id}.hazards.${hazard.id}.controls.${control.id}.implemented`
      )
    )
    .flat();

  const watchedFieldValues = methods.watch(fieldValues);

  useUpdateEffect(() => {
    setIsMarkAllChecked(watchedFieldValues.every(Boolean));
  }, [watchedFieldValues]);

  const setAllControlsState = (checked: boolean) => {
    for (const value of fieldValues) {
      methods.setValue(value, checked || undefined, {
        shouldDirty: true,
        shouldValidate: true,
      });
    }

    setIsMarkAllChecked(checked);
  };

  return (
    <label
      className="flex items-center mb-4 gap-4"
      htmlFor={`markAll.${element.id}`}
    >
      <Checkbox
        id={`markAll.${element.id}`}
        checked={isMarkAllChecked}
        onChange={event => {
          const {
            currentTarget: { checked },
          } = event;
          setAllControlsState(checked);
        }}
      />
      <span className="font-semibold text-neutral-shade-75 hover:cursor-pointer">
        {`Mark all ${controlEntity.labelPlural.toLowerCase()} as implemented`}
      </span>
    </label>
  );
};

export { MarkAllControls };
