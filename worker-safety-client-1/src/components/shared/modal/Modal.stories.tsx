import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { PropsWithClassName } from "@/types/Generic";

import type { ModalProps } from "./Modal";
import { useState } from "react";
import ButtonPrimary from "../button/primary/ButtonPrimary";
import Modal from "./Modal";

export default {
  title: "Silica/Modal",
  component: Modal,
  argTypes: {
    isOpen: { control: false },
    children: { control: false },
  },
} as ComponentMeta<typeof Modal>;

function Wrapper({
  children,
  ...tailProps
}: PropsWithClassName<ModalProps>): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);

  function closeModal() {
    setIsOpen(false);
  }

  function openModal() {
    setIsOpen(true);
  }

  return (
    <>
      <div>
        <ButtonPrimary type="button" onClick={openModal} label="Open Dialog" />
      </div>
      <Modal {...tailProps} isOpen={isOpen} closeModal={closeModal}>
        {children}
      </Modal>
    </>
  );
}

const TemplateModal: ComponentStory<typeof Modal> = args => (
  <Wrapper {...args}></Wrapper>
);

export const WithSmallContent = TemplateModal.bind({});
WithSmallContent.args = {
  title: "Are you sure you want to do this?",
  size: "md",
  children: (
    <div>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      <br />
      Sed tempor laoreet neque, id facilisis tortor efficitur ut.
    </div>
  ),
};

export const WithLargeContent = TemplateModal.bind({});
WithLargeContent.args = {
  title: "Are you sure you want to do this?",
  size: "md",
  children: (
    <div>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer non
      lectus vitae lacus consequat laoreet nec non neque. In at lectus non
      sapien pellentesque lobortis quis ac lectus. Ut tempor aliquam rutrum.
      Nullam consequat eros sed fringilla placerat.
      <br />
      Sed tempor laoreet neque, id facilisis tortor efficitur ut.
    </div>
  ),
};

export const WithSubTitle = TemplateModal.bind({});
WithSubTitle.args = {
  title: "Are you sure you want to do this?",
  subtitle: "Subtitle",
  size: "md",
  children: (
    <div>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      <br />
      Sed tempor laoreet neque, id facilisis tortor efficitur ut.
    </div>
  ),
};
