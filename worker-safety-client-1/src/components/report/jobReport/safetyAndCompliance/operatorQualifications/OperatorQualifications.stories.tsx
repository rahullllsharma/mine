import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { useForm } from "react-hook-form";
import { action } from "@storybook/addon-actions";
import { WrapperForm } from "@/utils/dev/storybook";

import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import OperatorQualifications from "./OperatorQualifications";

export default {
  title: "Components/Report/SafetyAndCompliance/OperatorQualifications",
  component: OperatorQualifications,
} as ComponentMeta<typeof OperatorQualifications>;

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    operatorQualifications: {
      qualificationsVerified: "",
      qualificationsVerifiedNotes: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    operatorQualifications: {
      qualificationsVerified: "1",
      qualificationsVerifiedNotes: "All ok",
    },
  },
};

const Template: ComponentStory<typeof OperatorQualifications> = () => (
  <OperatorQualifications />
);

const WithSubmitButton = (defaultValues: DailyReportInputs): JSX.Element => {
  const methods = useForm<DailyReportInputs>({
    defaultValues,
  });
  return (
    <WrapperForm methods={methods}>
      <ButtonPrimary
        className="mb-4"
        onClick={methods.handleSubmit(action("onSubmit"))}
        label="Submit"
      />
      <Template />
    </WrapperForm>
  );
};

export const WithoutSubmit = (): JSX.Element => (
  <WrapperForm>
    <Template />
  </WrapperForm>
);

export const WithSubmitEmpty = (): JSX.Element => {
  return <WithSubmitButton {...emptyStateValues} />;
};

export const WithSubmitFilled = (): JSX.Element => {
  return <WithSubmitButton {...prefilledValues} />;
};
