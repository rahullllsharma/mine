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
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { getDefaultOption } from "../utils";

const rules = FieldRules.REQUIRED;

export type WorkMethodsInputs = {
  contractorAccess: string;
  contractorAccessNotes: string;
};

const workMethodsFormInputPrefix = "safetyAndCompliance.workMethods";

export default function WorkMethods({
  isCompleted,
}: SafetyAndComplianceProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const {
    getValues,
    formState: { errors },
  } = useFormContext<Pick<DailyReportInputs, "safetyAndCompliance">>();

  return (
    <ReportSectionWrapper>
      <ReportSectionHeader title="Work Methods" />

      <ReportSectionBlock isInner>
        <Controller
          name={`${workMethodsFormInputPrefix}.contractorAccess`}
          rules={rules}
          render={({ field: { onChange } }) => (
            <FieldRadioGroup
              label={`Could the ${workPackage.attributes.primeContractor.label} access & navigate the NG procedures?`}
              required
              options={yesOrNoRadioGroupOptions}
              defaultOption={getDefaultOption(
                yesOrNoRadioGroupOptions,
                getValues(`${workMethodsFormInputPrefix}.contractorAccess`)
              )}
              error={
                errors?.safetyAndCompliance?.workMethods?.contractorAccess
                  ?.message
              }
              hasError={
                !!errors?.safetyAndCompliance?.workMethods?.contractorAccess
              }
              onSelect={onChange}
              readOnly={isCompleted}
            />
          )}
        />
        <Controller
          name={`${workMethodsFormInputPrefix}.contractorAccessNotes`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Notes"
              initialValue={getValues(
                `${workMethodsFormInputPrefix}.contractorAccessNotes`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </ReportSectionBlock>
    </ReportSectionWrapper>
  );
}
