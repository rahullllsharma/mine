import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { useForm } from "react-hook-form";
import { noop } from "lodash-es";
import Modal from "@/components/shared/modal/Modal";
import { WrapperForm } from "@/utils/dev/storybook";
import { AttributeEdit } from "./AttributeEdit";

export default {
  title: "Components/TenantAttributes/AttributeEdit",
  component: AttributeEdit,
  argTypes: {
    onSubmit: { action: "onFormSubmit" },
    onCancel: { action: "onCancelButtonClick" },
  },
} as ComponentMeta<typeof AttributeEdit>;

const Template: ComponentStory<typeof AttributeEdit> = args => {
  const methods = useForm({
    mode: "onBlur",
    defaultValues: {
      label: "Singular",
      labelPlural: "Plural",
    },
  });

  return (
    <Modal isOpen={true} closeModal={noop} title={`Edit Singular value`}>
      <WrapperForm methods={methods}>
        <AttributeEdit {...args} />
      </WrapperForm>
    </Modal>
  );
};

export const Playground = Template.bind({});
Playground.args = {};
