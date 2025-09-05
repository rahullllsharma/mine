import type {
  HazardAggregator,
  TaskHazardAggregator,
} from "@/types/project/HazardAggregator";
import type { PropsWithClassName } from "@/types/Generic";
import type {
  SiteConditionAnalysisInputs,
  TaskAnalysisInputs,
} from "@/types/report/DailyReportInputs";
import { useState } from "react";
import { Controller, useFormContext } from "react-hook-form";
import { has } from "lodash-es";
import Switch from "@/components/switch/Switch";

import FieldSelect from "@/components/shared/field/fieldSelect/FieldSelect";
import { getTaskNotPerformedOptions } from "@/container/report/jobHazardAnalysis/constants";
import { FieldRules } from "@/components/shared/field/FieldRules";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import HazardReportCard from "./hazard/HazardReportCard";

export type JobReportCardProps = PropsWithClassName<{
  job: HazardAggregator | TaskHazardAggregator;
  selectedJob?: TaskAnalysisInputs | SiteConditionAnalysisInputs;
  switchLabel: string;
  formGroupKey: "siteConditions" | "tasks";
  isCompleted?: boolean;
}>;

export const jobHazardAnalysisFormInputPrefix = "jobHazardAnalysis";

export default function JobReportCard({
  selectedJob,
  formGroupKey,
  job,
  switchLabel,
  isCompleted,
  children,
}: JobReportCardProps): JSX.Element {
  const { task } = useTenantStore(state => state.getAllEntities());
  const {
    formState: { errors },
  } = useFormContext();

  const [isApplicable, setIsApplicable] = useState<boolean>(
    (selectedJob as SiteConditionAnalysisInputs)?.isApplicable ??
      (selectedJob as TaskAnalysisInputs)?.performed ??
      true
  );

  const fieldControl = `${jobHazardAnalysisFormInputPrefix}.${formGroupKey}.${job.id}`;

  const switchControlId = `${fieldControl}.${
    formGroupKey === "tasks" ? "performed" : "isApplicable"
  }`;
  const selectControlId = `${fieldControl}.notApplicableReason`;
  const selectControlDefaultOption =
    formGroupKey === "tasks" && selectedJob?.notApplicableReason
      ? {
          id: selectedJob.notApplicableReason,
          name: selectedJob.notApplicableReason,
        }
      : undefined;

  const isSelectControlInvalid = has(errors, selectControlId);

  const jobHazardList = job.hazards.map(hazard => (
    <HazardReportCard
      formGroupKey={`${formGroupKey}.${job.id}`}
      key={hazard.id}
      hazard={hazard}
      selectedHazard={selectedJob?.hazards.find(
        selectedHazard => selectedHazard.id === hazard.id
      )}
      isCompleted={isCompleted}
      className="mb-4 last:mb-0"
    />
  ));

  const { name: activityName } = (job as TaskHazardAggregator)?.activity || {};

  return (
    <div className="shadow-10 p-4" data-testid={`job-report-card-${job.id}`}>
      <section className="flex items-center justify-between font-semibold mb-4">
        <h4 className="text-lg text-neutral-shade-100">
          {job.name}
          {activityName && (
            <p className="font-medium text-tiny">{activityName}</p>
          )}
        </h4>
        <div className="flex items-center">
          <span className="text-sm mr-2 text-neutral-shade-75">
            {switchLabel}
          </span>
          <Controller
            name={switchControlId}
            defaultValue={isApplicable}
            render={({ field: { onChange } }) => (
              <Switch
                title={switchLabel}
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
      </section>
      {children}
      {isApplicable && jobHazardList}
      {!isApplicable && formGroupKey === "tasks" && (
        <Controller
          name={selectControlId}
          rules={FieldRules.REQUIRED}
          defaultValue={selectControlDefaultOption}
          render={({ field: { onChange, ref } }) => (
            <FieldSelect
              className="mt-1"
              label={`Why was this ${task.label.toLowerCase()} not performed?`}
              required
              options={getTaskNotPerformedOptions()}
              defaultOption={selectControlDefaultOption}
              isInvalid={isSelectControlInvalid}
              buttonRef={ref}
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
      )}
    </div>
  );
}
