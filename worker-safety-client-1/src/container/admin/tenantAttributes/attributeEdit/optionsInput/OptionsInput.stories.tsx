import type { FormInputsOptions } from "@/container/admin/tenantAttributes/types";
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { useForm } from "react-hook-form";
import { WrapperForm, WrapperModal } from "@/utils/dev/storybook";
import { OptionsInput } from "./OptionsInput";

type OptionsInputArgs = {
  mandatory: boolean;
  options: FormInputsOptions[];
};

export default {
  title: "Components/TenantAttributes/OptionsInput",
  component: OptionsInput,
} as ComponentMeta<typeof OptionsInput>;

const Template: ComponentStory<typeof OptionsInput> = args => {
  const { mandatory, options } = args as OptionsInputArgs;

  const methods = useForm({
    mode: "onChange",
    defaultValues: {
      mandatory: mandatory,
      options,
    },
  });

  return (
    <WrapperModal title={`Edit Singular value`}>
      <WrapperForm methods={methods}>
        <OptionsInput />
      </WrapperForm>
    </WrapperModal>
  );
};

export const Playground = Template.bind({});
Playground.args = {
  mandatory: false,
  options: [
    {
      key: "visible",
      value: true,
    },
    {
      key: "required",
      value: true,
    },
    {
      key: "filterable",
      value: true,
    },
  ],
};

export const Mandatory = Template.bind({});
Mandatory.args = {
  mandatory: true,
  options: [
    {
      key: "visible",
      value: true,
    },
    {
      key: "required",
      value: true,
    },
    {
      key: "filterable",
      value: true,
    },
  ],
};
