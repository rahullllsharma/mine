import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import SaveAndCompleteModal from "./SaveAndCompleteModal";

export default {
  title: "Container/Report/Modal/SaveAndCompleteModal",
  component: SaveAndCompleteModal,
} as ComponentMeta<typeof SaveAndCompleteModal>;

const Template: ComponentStory<typeof SaveAndCompleteModal> = args => {
  return <SaveAndCompleteModal {...args} />;
};

export const Playground = Template.bind({});
Playground.args = {
  isOpen: true,
  isLoading: false,
  closeModal: action("closed modal"),
  onPrimaryBtnClick: action("primary action trigger"),
};
