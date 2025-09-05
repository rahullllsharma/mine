import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { useForm } from "react-hook-form";

import { action } from "@storybook/addon-actions";

import { WrapperForm } from "@/utils/dev/storybook";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import Plans from "./Plans";

export default {
  title: "Components/Report/SafetyAndCompliance/Plans",
  component: Plans,
} as ComponentMeta<typeof Plans>;

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    plans: { comprehensivePHAConducted: "", membersReviewedAndSignedOff: "" },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    plans: { comprehensivePHAConducted: "0", membersReviewedAndSignedOff: "1" },
  },
};

const Template: ComponentStory<typeof Plans> = () => <Plans />;

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
