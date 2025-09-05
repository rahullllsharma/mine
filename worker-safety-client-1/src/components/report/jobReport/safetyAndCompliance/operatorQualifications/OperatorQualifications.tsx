import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { SafetyAndComplianceProps } from "@/container/report/safetyAndCompliance/SafetyAndCompliance";
import { Controller, useFormContext } from "react-hook-form";

import ReportSectionHeader from "@/components/layout/report/reportSectionHeader/ReportSectionHeader";
import ReportSectionBlock from "@/components/layout/report/reportSectionBlock/ReportSectionBlock";
import ReportSectionWrapper from "@/components/layout/report/reportSectionWrapper/ReportSectionWrapper";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { yesOrNoRadioGroupOptions } from "@/radioGroupConstants";
import { FieldRules } from "@/components/shared/field/FieldRules";
import { getDefaultOption } from "../utils";

const rules = FieldRules.REQUIRED;

export type OperatorQualificationsInputs = {
  qualificationsVerified: string;
  qualificationsVerifiedNotes: string;
};

const operatorQualificationsFormInputPrefix =
  "safetyAndCompliance.operatorQualifications";

export default function OperatorQualifications({
  isCompleted,
}: SafetyAndComplianceProps): JSX.Element {
  const {
    getValues,
    formState: { errors },
  } = useFormContext<Pick<DailyReportInputs, "safetyAndCompliance">>();

  return (
    <ReportSectionWrapper>
      <ReportSectionHeader title="Operator Qualifications" />

      <ReportSectionBlock isInner>
        <Controller
          name={`${operatorQualificationsFormInputPrefix}.qualificationsVerified`}
          rules={rules}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Were the Operator Qualifications verified?"
              required
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(
                  `${operatorQualificationsFormInputPrefix}.qualificationsVerified`
                )
              )}
              error={
                errors?.safetyAndCompliance?.operatorQualifications
                  ?.qualificationsVerified?.message
              }
              hasError={
                !!errors?.safetyAndCompliance?.operatorQualifications
                  ?.qualificationsVerified?.message
              }
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${operatorQualificationsFormInputPrefix}.qualificationsVerifiedNotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${operatorQualificationsFormInputPrefix}.qualificationsVerifiedNotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
    </ReportSectionWrapper>
  );
}
