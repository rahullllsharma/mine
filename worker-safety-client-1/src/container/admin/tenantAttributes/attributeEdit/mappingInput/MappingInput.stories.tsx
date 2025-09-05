import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { noop } from "lodash-es";
import Modal from "@/components/shared/modal/Modal";
import { MappingInput } from "./MappingInput";

export default {
  title: "Components/TenantAttributes/MappingInput",
  component: MappingInput,
  argTypes: {
    onSubmit: { action: "onFormSubmit" },
  },
} as ComponentMeta<typeof MappingInput>;

const Template: ComponentStory<typeof MappingInput> = args => {
  return (
    <Modal isOpen closeModal={noop} title="Mapping Input Modal">
      <MappingInput {...args} />
    </Modal>
  );
};

export const Playground = Template.bind({});
Playground.args = {
  defaultLabel: "Default",
  label: "Label",
  badgeNumber: 1,
  isDefault: true,
};
