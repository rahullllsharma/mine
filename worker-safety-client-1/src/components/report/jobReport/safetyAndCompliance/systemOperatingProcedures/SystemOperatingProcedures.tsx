import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { SafetyAndComplianceProps } from "@/container/report/safetyAndCompliance/SafetyAndCompliance";
import { Controller, useFormContext } from "react-hook-form";

import ReportSectionHeader from "@/components/layout/report/reportSectionHeader/ReportSectionHeader";
import ReportSectionBlock from "@/components/layout/report/reportSectionBlock/ReportSectionBlock";
import ReportSectionWrapper from "@/components/layout/report/reportSectionWrapper/ReportSectionWrapper";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { yesOrNoRadioGroupOptions } from "@/radioGroupConstants";
import { FieldRules } from "@/components/shared/field/FieldRules";
import { getDefaultOption } from "../utils";

const rules = FieldRules.REQUIRED;

export type SystemOperatingProceduresInputs = {
  onSiteAndCurrent: string;
  onSiteAndCurrentNotes: string;
  gasControlsNotified: string;
  gasControlsNotifiedNotes: string;
  sopId: string;
  sopType: string;
  sopStepsCalledIn: string;
  sopComments: string;
};

const systemOperatingProceduresFormInputPrefix =
  "safetyAndCompliance.systemOperatingProcedures";

export default function SystemOperatingProcedures({
  isCompleted,
}: SafetyAndComplianceProps): JSX.Element {
  const {
    getValues,
    formState: { errors },
  } = useFormContext<Pick<DailyReportInputs, "safetyAndCompliance">>();

  return (
    <ReportSectionWrapper>
      <ReportSectionHeader title="System Operating Procedures" />

      <ReportSectionBlock isInner>
        <Controller
          name={`${systemOperatingProceduresFormInputPrefix}.onSiteAndCurrent`}
          rules={rules}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Was the SOPs onsite and current?"
              required
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(
                  `${systemOperatingProceduresFormInputPrefix}.onSiteAndCurrent`
                )
              )}
              error={
                errors?.safetyAndCompliance?.systemOperatingProcedures
                  ?.onSiteAndCurrent?.message
              }
              hasError={
                !!errors?.safetyAndCompliance?.systemOperatingProcedures
                  ?.onSiteAndCurrent
              }
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${systemOperatingProceduresFormInputPrefix}.onSiteAndCurrentNotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${systemOperatingProceduresFormInputPrefix}.onSiteAndCurrentNotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>

      <ReportSectionBlock isInner>
        <Controller
          name={`${systemOperatingProceduresFormInputPrefix}.gasControlsNotified`}
          rules={rules}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Has Gas Controls been notified & has approval been given prior to the steps being performed?"
              required
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(
                  `${systemOperatingProceduresFormInputPrefix}.gasControlsNotified`
                )
              )}
              error={
                errors?.safetyAndCompliance?.systemOperatingProcedures
                  ?.gasControlsNotified?.message
              }
              hasError={
                !!errors?.safetyAndCompliance?.systemOperatingProcedures
                  ?.gasControlsNotified
              }
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${systemOperatingProceduresFormInputPrefix}.gasControlsNotifiedNotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${systemOperatingProceduresFormInputPrefix}.gasControlsNotifiedNotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
      <ReportSectionBlock>
        <Controller
          name={`${systemOperatingProceduresFormInputPrefix}.sopId`}
          rules={rules}
          render={({ field }) => (
            <FieldInput
              {...field}
              label="SOP#"
              required
              error={
                errors?.safetyAndCompliance?.systemOperatingProcedures?.sopId
                  ?.message
              }
              value={getValues(
                `${systemOperatingProceduresFormInputPrefix}.sopId`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
      <ReportSectionBlock>
        <Controller
          name={`${systemOperatingProceduresFormInputPrefix}.sopType`}
          rules={rules}
          render={({ field }) => (
            <FieldInput
              {...field}
              label="SOP Type"
              required
              error={
                errors?.safetyAndCompliance?.systemOperatingProcedures?.sopType
                  ?.message
              }
              value={getValues(
                `${systemOperatingProceduresFormInputPrefix}.sopType`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
      <ReportSectionBlock>
        <Controller
          name={`${systemOperatingProceduresFormInputPrefix}.sopStepsCalledIn`}
          rules={rules}
          render={({ field }) => (
            <FieldInput
              {...field}
              label="Steps called in"
              required
              error={
                errors?.safetyAndCompliance?.systemOperatingProcedures
                  ?.sopStepsCalledIn?.message
              }
              value={getValues(
                `${systemOperatingProceduresFormInputPrefix}.sopStepsCalledIn`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
      <ReportSectionBlock>
        <Controller
          name={`${systemOperatingProceduresFormInputPrefix}.sopComments`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="SOP Comments"
              initialValue={getValues(
                `${systemOperatingProceduresFormInputPrefix}.sopComments`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
    </ReportSectionWrapper>
  );
}
