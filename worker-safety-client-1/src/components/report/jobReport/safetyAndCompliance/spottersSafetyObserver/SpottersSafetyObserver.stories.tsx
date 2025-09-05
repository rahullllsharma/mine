import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { useForm } from "react-hook-form";
import { action } from "@storybook/addon-actions";
import { WrapperForm } from "@/utils/dev/storybook";

import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import SpottersSafetyObserver from "./SpottersSafetyObserver";

export default {
  title: "Components/Report/SafetyAndCompliance/SpottersSafetyObserver",
  component: SpottersSafetyObserver,
} as ComponentMeta<typeof SpottersSafetyObserver>;

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    spottersSafetyObserver: {
      safetyObserverAssigned: "",
      safetyObserverAssignedNotes: "",
      spotterIdentifiedMachineryBackingUp: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    spottersSafetyObserver: {
      safetyObserverAssigned: "0",
      safetyObserverAssignedNotes: "Not yet",
      spotterIdentifiedMachineryBackingUp: "1",
    },
  },
};

const Template: ComponentStory<typeof SpottersSafetyObserver> = () => (
  <SpottersSafetyObserver />
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
