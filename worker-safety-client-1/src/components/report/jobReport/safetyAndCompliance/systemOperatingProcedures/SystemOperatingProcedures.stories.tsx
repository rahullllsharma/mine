import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { action } from "@storybook/addon-actions";
import { useForm } from "react-hook-form";
import { WrapperForm } from "@/utils/dev/storybook";

import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import SystemOperatingProcedures from "./SystemOperatingProcedures";

export default {
  title: "Components/Report/SafetyAndCompliance/SystemOperatingProcedures",
  component: SystemOperatingProcedures,
  decorators: [
    Story => (
      <div className="overflow-auto h-screen">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof SystemOperatingProcedures>;

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    systemOperatingProcedures: {
      onSiteAndCurrent: "",
      onSiteAndCurrentNotes: "",
      gasControlsNotified: "",
      gasControlsNotifiedNotes: "",
      sopId: "",
      sopType: "",
      sopStepsCalledIn: "",
      sopComments: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    systemOperatingProcedures: {
      onSiteAndCurrent: "0",
      onSiteAndCurrentNotes: "",
      gasControlsNotified: "1",
      gasControlsNotifiedNotes: "",
      sopId: "#11AA22",
      sopType: "-",
      sopStepsCalledIn: "Steps called in",
      sopComments: "No additional comments",
    },
  },
};

const Template: ComponentStory<typeof SystemOperatingProcedures> = () => (
  <SystemOperatingProcedures />
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
