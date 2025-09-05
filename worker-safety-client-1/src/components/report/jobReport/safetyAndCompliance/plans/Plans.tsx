import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { SafetyAndComplianceProps } from "@/container/report/safetyAndCompliance/SafetyAndCompliance";
import { Controller, useFormContext } from "react-hook-form";
import ReportSectionHeader from "@/components/layout/report/reportSectionHeader/ReportSectionHeader";
import ReportSectionBlock from "@/components/layout/report/reportSectionBlock/ReportSectionBlock";
import ReportSectionWrapper from "@/components/layout/report/reportSectionWrapper/ReportSectionWrapper";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { yesOrNoRadioGroupOptions } from "@/radioGroupConstants";
import { getDefaultOption } from "../utils";

export type PlansInputs = {
  comprehensivePHAConducted: string;
  membersReviewedAndSignedOff: string;
};

const plansFormInputPrefix = "safetyAndCompliance.plans";

export default function Plans({
  isCompleted,
}: SafetyAndComplianceProps): JSX.Element {
  const { getValues } =
    useFormContext<Pick<DailyReportInputs, "safetyAndCompliance">>();

  return (
    <ReportSectionWrapper>
      <ReportSectionHeader title="Plans" />

      <ReportSectionBlock>
        <Controller
          name={`${plansFormInputPrefix}.comprehensivePHAConducted`}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Was a comprehensive PHA conducted?"
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(`${plansFormInputPrefix}.comprehensivePHAConducted`)
              )}
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>

      <ReportSectionBlock>
        <Controller
          name={`${plansFormInputPrefix}.membersReviewedAndSignedOff`}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label="Have all crew members reviewed and signed off on the HASP?"
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(`${plansFormInputPrefix}.membersReviewedAndSignedOff`)
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
