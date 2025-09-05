import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { SafetyAndComplianceProps } from "@/container/report/safetyAndCompliance/SafetyAndCompliance";
import { Controller, useFormContext } from "react-hook-form";

import ReportSectionHeader from "@/components/layout/report/reportSectionHeader/ReportSectionHeader";
import ReportSectionBlock from "@/components/layout/report/reportSectionBlock/ReportSectionBlock";
import ReportSectionWrapper from "@/components/layout/report/reportSectionWrapper/ReportSectionWrapper";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import {
  notApplicableRadioGroupOptions,
  yesOrNoRadioGroupOptions,
} from "@/radioGroupConstants";
import { FieldRules } from "@/components/shared/field/FieldRules";
import { getDefaultOption } from "../utils";

const rules = FieldRules.REQUIRED;

export type JobBriefInputs = {
  comprehensiveJobBriefConduct: string;
  comprehensiveJobBriefConductNotes: string;
  jobBriefConductAfterWork: string;
  jobBriefConductAfterWorkNotes: string;
};

const jobBriefFormInputPrefix = "safetyAndCompliance.jobBrief";

export default function JobBrief({
  isCompleted,
}: SafetyAndComplianceProps): JSX.Element {
  const {
    getValues,
    formState: { errors },
  } = useFormContext<Pick<DailyReportInputs, "safetyAndCompliance">>();

  return (
    <ReportSectionWrapper>
      <ReportSectionHeader title="Job Brief" />

      <ReportSectionBlock isInner>
        <Controller
          name={`${jobBriefFormInputPrefix}.comprehensiveJobBriefConduct`}
          rules={rules}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Was a comprehensive job brief conducted?"
              required
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(
                  `${jobBriefFormInputPrefix}.comprehensiveJobBriefConduct`
                )
              )}
              onSelect={onChange}
              hasError={
                !!errors?.safetyAndCompliance?.jobBrief
                  ?.comprehensiveJobBriefConduct
              }
              error={
                errors?.safetyAndCompliance?.jobBrief
                  ?.comprehensiveJobBriefConduct?.message
              }
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${jobBriefFormInputPrefix}.comprehensiveJobBriefConductNotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${jobBriefFormInputPrefix}.comprehensiveJobBriefConductNotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>

      <ReportSectionBlock isInner>
        <Controller
          name={`${jobBriefFormInputPrefix}.jobBriefConductAfterWork`}
          rules={rules}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Was a Job Brief conducted after changes to work performed?"
              required
              options={notApplicableRadioGroupOptions}
              defaultOption={getDefaultOption(
                notApplicableRadioGroupOptions,
                getValues(`${jobBriefFormInputPrefix}.jobBriefConductAfterWork`)
              )}
              onSelect={onChange}
              hasError={
                !!errors?.safetyAndCompliance?.jobBrief
                  ?.jobBriefConductAfterWork
              }
              error={
                errors?.safetyAndCompliance?.jobBrief?.jobBriefConductAfterWork
                  ?.message
              }
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${jobBriefFormInputPrefix}.jobBriefConductAfterWorkNotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${jobBriefFormInputPrefix}.jobBriefConductAfterWorkNotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
    </ReportSectionWrapper>
  );
}
