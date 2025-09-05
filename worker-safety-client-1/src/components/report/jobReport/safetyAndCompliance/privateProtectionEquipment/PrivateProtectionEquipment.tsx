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

export type PrivateProtectionEquipmentInputs = {
  wearingPPE: string;
  wearingPPENotes: string;
};

const privateProtectionEquipmentFormInputPrefix =
  "safetyAndCompliance.privateProtectionEquipment";

export default function PrivateProtectionEquipment({
  isCompleted,
}: SafetyAndComplianceProps): JSX.Element {
  const {
    getValues,
    formState: { errors },
  } = useFormContext<Pick<DailyReportInputs, "safetyAndCompliance">>();

  return (
    <ReportSectionWrapper>
      <ReportSectionHeader title="PPE" />

      <ReportSectionBlock isInner>
        <Controller
          name={`${privateProtectionEquipmentFormInputPrefix}.wearingPPE`}
          rules={rules}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Were all crew members and visitors wearing the appropriate PPE?"
              required
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(
                  `${privateProtectionEquipmentFormInputPrefix}.wearingPPE`
                )
              )}
              error={
                errors?.safetyAndCompliance?.privateProtectionEquipment
                  ?.wearingPPE?.message
              }
              hasError={
                !!errors?.safetyAndCompliance?.privateProtectionEquipment
                  ?.wearingPPE
              }
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${privateProtectionEquipmentFormInputPrefix}.wearingPPENotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${privateProtectionEquipmentFormInputPrefix}.wearingPPENotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
    </ReportSectionWrapper>
  );
}
