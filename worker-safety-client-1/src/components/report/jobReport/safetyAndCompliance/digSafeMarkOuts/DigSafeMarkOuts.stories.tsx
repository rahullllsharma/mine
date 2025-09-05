import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { useForm } from "react-hook-form";
import { action } from "@storybook/addon-actions";
import { WrapperForm } from "@/utils/dev/storybook";

import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import DigSafeMarkOuts from "./DigSafeMarkOuts";

export default {
  title: "Components/Report/SafetyAndCompliance/DigSafeMarkOuts",
  component: DigSafeMarkOuts,
} as ComponentMeta<typeof DigSafeMarkOuts>;

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    digSafeMarkOuts: {
      markOutsVerified: "",
      markOutsVerifiedNotes: "",
      facilitiesLocatedAndExposed: "",
      facilitiesLocatedAndExposedNotes: "",
      digSafeMarkOutsLocation: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    digSafeMarkOuts: {
      markOutsVerified: "-1",
      markOutsVerifiedNotes: "N/A",
      facilitiesLocatedAndExposed: "1",
      facilitiesLocatedAndExposedNotes: "Yes",
      digSafeMarkOutsLocation: "No additional notes",
    },
  },
};

const Template: ComponentStory<typeof DigSafeMarkOuts> = () => (
  <DigSafeMarkOuts />
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
