import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { SafetyAndComplianceProps } from "@/container/report/safetyAndCompliance/SafetyAndCompliance";
import { Controller, useFormContext } from "react-hook-form";

import ReportSectionHeader from "@/components/layout/report/reportSectionHeader/ReportSectionHeader";
import ReportSectionBlock from "@/components/layout/report/reportSectionBlock/ReportSectionBlock";
import ReportSectionWrapper from "@/components/layout/report/reportSectionWrapper/ReportSectionWrapper";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { notApplicableRadioGroupOptions } from "@/radioGroupConstants";
import { FieldRules } from "@/components/shared/field/FieldRules";
import { getDefaultOption } from "../utils";

const rules = FieldRules.REQUIRED;

export type DigSafeMarkOutsInputs = {
  markOutsVerified: string;
  markOutsVerifiedNotes: string;
  facilitiesLocatedAndExposed: string;
  facilitiesLocatedAndExposedNotes: string;
  digSafeMarkOutsLocation: string;
};

const digSafeMarkOutsFormInputPrefix = "safetyAndCompliance.digSafeMarkOuts";

export default function DigSafeMarkOuts({
  isCompleted,
}: SafetyAndComplianceProps): JSX.Element {
  const {
    getValues,
    formState: { errors },
  } = useFormContext<Pick<DailyReportInputs, "safetyAndCompliance">>();

  return (
    <ReportSectionWrapper>
      <ReportSectionHeader title="Digsafe / Mark Outs" />

      <ReportSectionBlock isInner>
        <Controller
          name={`${digSafeMarkOutsFormInputPrefix}.markOutsVerified`}
          rules={rules}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Were all Mark Outs verified?"
              required
              options={notApplicableRadioGroupOptions}
              defaultOption={getDefaultOption(
                notApplicableRadioGroupOptions,
                getValues(`${digSafeMarkOutsFormInputPrefix}.markOutsVerified`)
              )}
              error={
                errors?.safetyAndCompliance?.digSafeMarkOuts?.markOutsVerified
                  ?.message
              }
              hasError={
                !!errors?.safetyAndCompliance?.digSafeMarkOuts?.markOutsVerified
              }
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${digSafeMarkOutsFormInputPrefix}.markOutsVerifiedNotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${digSafeMarkOutsFormInputPrefix}.markOutsVerifiedNotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>

      <ReportSectionBlock isInner>
        <Controller
          name={`${digSafeMarkOutsFormInputPrefix}.facilitiesLocatedAndExposed`}
          rules={rules}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Were all Facilities located and exposed prior to excavation?"
              required
              options={notApplicableRadioGroupOptions}
              defaultOption={getDefaultOption(
                notApplicableRadioGroupOptions,
                getValues(
                  `${digSafeMarkOutsFormInputPrefix}.facilitiesLocatedAndExposed`
                )
              )}
              error={
                errors?.safetyAndCompliance?.digSafeMarkOuts
                  ?.facilitiesLocatedAndExposed?.message
              }
              hasError={
                !!errors?.safetyAndCompliance?.digSafeMarkOuts
                  ?.facilitiesLocatedAndExposed
              }
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${digSafeMarkOutsFormInputPrefix}.facilitiesLocatedAndExposedNotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${digSafeMarkOutsFormInputPrefix}.facilitiesLocatedAndExposedNotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>

      <ReportSectionBlock>
        <Controller
          name={`${digSafeMarkOutsFormInputPrefix}.digSafeMarkOutsLocation`}
          rules={rules}
          render={({ field }) => (
            <FieldInput
              {...field}
              label="Digsafe location?"
              required
              error={
                errors?.safetyAndCompliance?.digSafeMarkOuts
                  ?.digSafeMarkOutsLocation?.message
              }
              value={getValues(
                `${digSafeMarkOutsFormInputPrefix}.digSafeMarkOutsLocation`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
    </ReportSectionWrapper>
  );
}
