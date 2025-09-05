import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { useForm } from "react-hook-form";

import { WrapperForm } from "@/utils/dev/storybook";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import Attachments from "./Attachments";

export default {
  title: "Container/Report/Attachments",
  component: Attachments,
  decorators: [
    Story => (
      <div className="overflow-auto p-2 pb-10" style={{ height: "90vh" }}>
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof Attachments>;

const Template: ComponentStory<typeof Attachments> = args => (
  <Attachments {...args} />
);

const defaultValues: DailyReportInputs = {
  attachments: {
    documents: [],
    photos: [],
  },
};

export const WithoutSubmit = (): JSX.Element => (
  <WrapperForm>
    <Template />
  </WrapperForm>
);

export const WithSubmit = (): JSX.Element => {
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

export const Readonly = (): JSX.Element => (
  <WrapperForm>
    <Template isCompleted />
  </WrapperForm>
);
