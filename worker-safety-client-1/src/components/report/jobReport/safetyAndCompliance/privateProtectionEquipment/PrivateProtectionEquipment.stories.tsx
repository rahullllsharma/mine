import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { useForm } from "react-hook-form";
import { action } from "@storybook/addon-actions";
import { WrapperForm } from "@/utils/dev/storybook";

import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import PrivateProtectionEquipment from "./PrivateProtectionEquipment";

export default {
  title: "Components/Report/SafetyAndCompliance/PrivateProtectionEquipment",
  component: PrivateProtectionEquipment,
} as ComponentMeta<typeof PrivateProtectionEquipment>;

const emptyStateValues: DailyReportInputs = {
  safetyAndCompliance: {
    privateProtectionEquipment: {
      wearingPPE: "",
      wearingPPENotes: "",
    },
  },
};

const prefilledValues: DailyReportInputs = {
  safetyAndCompliance: {
    privateProtectionEquipment: {
      wearingPPE: "0",
      wearingPPENotes:
        "No security/protection measures applied to any crew member nor visitors",
    },
  },
};

const Template: ComponentStory<typeof PrivateProtectionEquipment> = () => (
  <PrivateProtectionEquipment />
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
