import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { SafetyAndComplianceProps } from "@/container/report/safetyAndCompliance/SafetyAndCompliance";
import { Controller, useFormContext } from "react-hook-form";

import ReportSectionHeader from "@/components/layout/report/reportSectionHeader/ReportSectionHeader";
import ReportSectionBlock from "@/components/layout/report/reportSectionBlock/ReportSectionBlock";
import ReportSectionWrapper from "@/components/layout/report/reportSectionWrapper/ReportSectionWrapper";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { yesOrNoRadioGroupOptions } from "@/radioGroupConstants";
import { getDefaultOption } from "../utils";

export type SpottersSafetyObserverInputs = {
  safetyObserverAssigned: string;
  safetyObserverAssignedNotes: string;
  spotterIdentifiedMachineryBackingUp: string;
};

const spottersSafetyObserverFormInputPrefix =
  "safetyAndCompliance.spottersSafetyObserver";

export default function SpottersSafetyObserver({
  isCompleted,
}: SafetyAndComplianceProps): JSX.Element {
  const { getValues } =
    useFormContext<Pick<DailyReportInputs, "safetyAndCompliance">>();

  return (
    <ReportSectionWrapper>
      <ReportSectionHeader title="Spotters/Safety Observer" />

      <ReportSectionBlock isInner>
        <Controller
          name={`${spottersSafetyObserverFormInputPrefix}.safetyObserverAssigned`}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Has a Safety Observer been assigned?"
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(
                  `${spottersSafetyObserverFormInputPrefix}.safetyObserverAssigned`
                )
              )}
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${spottersSafetyObserverFormInputPrefix}.safetyObserverAssignedNotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${spottersSafetyObserverFormInputPrefix}.safetyObserverAssignedNotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>

      <ReportSectionBlock>
        <Controller
          name={`${spottersSafetyObserverFormInputPrefix}.spotterIdentifiedMachineryBackingUp`}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Spotter Identified when machinery and/or equipment is backing up?"
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(
                  `${spottersSafetyObserverFormInputPrefix}.spotterIdentifiedMachineryBackingUp`
                )
              )}
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
    </ReportSectionWrapper>
  );
}
