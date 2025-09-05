import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { action } from "@storybook/addon-actions";
import { useForm } from "react-hook-form";
import { WrapperForm } from "@/utils/dev/storybook";

import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import JobBrief from "./JobBrief";

export default {
  title: "Components/Report/SafetyAndCompliance/JobBrief",
  component: JobBrief,
} as ComponentMeta<typeof JobBrief>;

const Template: ComponentStory<typeof JobBrief> = () => <JobBrief />;

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    jobBrief: {
      comprehensiveJobBriefConduct: "",
      comprehensiveJobBriefConductNotes: "",
      jobBriefConductAfterWork: "",
      jobBriefConductAfterWorkNotes: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    jobBrief: {
      comprehensiveJobBriefConduct: "1",
      comprehensiveJobBriefConductNotes: "Conducts notes",
      jobBriefConductAfterWork: "-1",
      jobBriefConductAfterWorkNotes: "After work notes",
    },
  },
};

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
