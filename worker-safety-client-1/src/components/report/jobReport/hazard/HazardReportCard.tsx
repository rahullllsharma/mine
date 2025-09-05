import type { PropsWithClassName } from "@/types/Generic";
import type { Hazard } from "@/types/project/Hazard";
import type { HazardAnalysisInput } from "@/types/report/DailyReportInputs";
import { useState } from "react";
import { Controller } from "react-hook-form";
import Switch from "@/components/switch/Switch";
import { jobHazardAnalysisFormInputPrefix } from "../JobReportCard";
import ControlReportCard from "./control/ControlReportCard";

export type HazardReportCardProps = PropsWithClassName<{
  selectedHazard?: HazardAnalysisInput;
  formGroupKey: string;
  hazard: Hazard;
  isCompleted?: boolean;
}>;

export default function HazardReportCard({
  selectedHazard,
  formGroupKey,
  hazard,
  isCompleted,
  className = "",
}: HazardReportCardProps): JSX.Element {
  // TODO: Migrate to getValue and HRF (using defaultValues)
  const [isApplicable, setIsApplicable] = useState(
    selectedHazard?.isApplicable ?? true
  );

  const fieldControl = `${jobHazardAnalysisFormInputPrefix}.${formGroupKey}.hazards.${hazard.id}`;

  const switchControlId = `${fieldControl}.isApplicable`;

  const hazardList = hazard.controls.map(control => (
    <ControlReportCard
      formGroupKey={`${formGroupKey}.hazards.${hazard.id}`}
      key={control.id}
      className="mb-4 last:mb-0"
      control={control}
      selectedControl={selectedHazard?.controls.find(
        selectedControl => selectedControl.id === control.id
      )}
      isCompleted={isCompleted}
    />
  ));

  return (
    <div
      className={`bg-brand-gray-10 p-4 ${className}`}
      data-testid={`hazard-report-card-${hazard.id}`}
      data-print-section-unbreakable
    >
      <div className="flex items-center justify-between font-semibold mb-4">
        <span className="text-base">{hazard.name}</span>
        <div className="flex items-center">
          <span className="text-sm mr-2 text-neutral-shade-75">
            Applicable?
          </span>
          <Controller
            name={switchControlId}
            defaultValue={isApplicable}
            render={({ field: { onChange } }) => (
              <Switch
                stateOverride={isApplicable}
                onToggle={(value: boolean) => {
                  setIsApplicable(value);
                  onChange(value);
                }}
                isDisabled={isCompleted}
              />
            )}
          />
        </div>
      </div>
      {isApplicable && hazardList}
    </div>
  );
}
