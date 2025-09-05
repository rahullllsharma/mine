import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { PropsWithClassName } from "@/types/Generic";
import React from "react";
import { FormProvider, useForm } from "react-hook-form";

import { action } from "@storybook/addon-actions";
import { DevTool } from "@hookform/devtools";
import { WrapperForm } from "@/utils/dev/storybook";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ControlReportCard from "./ControlReportCard";

export default {
  title: "Components/Report/JobReport/Hazard/Control",
  component: ControlReportCard,
  decorators: [
    Story => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
} as ComponentMeta<typeof ControlReportCard>;

function Wrapper({ children }: PropsWithClassName): JSX.Element {
  const methods = useForm();
  return <FormProvider {...methods}>{children}</FormProvider>;
}

const Template: ComponentStory<typeof ControlReportCard> = args => (
  <ControlReportCard {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  className: "max-w-sm",
  control: { id: "1", name: "Gloves", isApplicable: true },
};

export const WithSubmitButton: ComponentStory<typeof ControlReportCard> =
  args => {
    const methods = useForm();
    return (
      <WrapperForm methods={methods}>
        <ButtonPrimary
          className="mb-4"
          onClick={methods.handleSubmit(action("onSubmit"))}
          label="Submit"
        />
        <Template {...args} />
        <DevTool control={methods.control} />
      </WrapperForm>
    );
  };
WithSubmitButton.args = {
  className: "max-w-sm",
  control: { id: "1", name: "Gloves", isApplicable: true },
};
