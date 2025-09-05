import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { useForm } from "react-hook-form";
import { DevTool } from "@hookform/devtools";

import { WrapperForm } from "@/utils/dev/storybook";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import AdditionalInformation from "./AdditionalInformation";

export default {
  title: "Container/Report/AdditionalInformation",
  component: AdditionalInformation,
} as ComponentMeta<typeof AdditionalInformation>;

const Template: ComponentStory<typeof AdditionalInformation> = args => (
  <div className="overflow-auto p-2" style={{ height: "90vh" }}>
    <AdditionalInformation {...args} />
  </div>
);

export const WithoutSubmit = (): JSX.Element => (
  <WrapperForm>
    <Template />
  </WrapperForm>
);

export const WithSubmit = (): JSX.Element => {
  const methods = useForm();
  return (
    <WrapperForm methods={methods}>
      <ButtonPrimary
        className="mb-4"
        onClick={methods.handleSubmit(action("onSubmit"))}
        label="Submit"
      />
      <Template />
      <DevTool control={methods.control} />
    </WrapperForm>
  );
};

export const Readonly = (): JSX.Element => {
  const methods = useForm({
    defaultValues: {
      additionalInformation: {
        progress:
          "This text area is for overall progress updates about this specific location and any tasks or site conditions that may have been completed during that time. ",
        lessons:
          "This text area is for some lessons learned while on the job completing various items.",
      },
    },
  });

  return (
    <WrapperForm methods={methods}>
      <Template isCompleted />
    </WrapperForm>
  );
};
