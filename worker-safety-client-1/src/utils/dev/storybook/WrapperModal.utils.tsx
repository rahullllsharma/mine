import type { ModalSize } from "@/components/shared/modal/Modal";
import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";
import { useState } from "react";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import Modal from "@/components/shared/modal/Modal";

function WrapperModal({
  title,
  size = "md",
  className,
  children,
}: PropsWithClassName<{ title: string; size?: ModalSize }>): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);

  function closeModal() {
    setIsOpen(false);
  }

  function openModal() {
    setIsOpen(true);
  }

  return (
    <>
      <ButtonPrimary label="Open" onClick={openModal} />
      <Modal
        title={title}
        isOpen={isOpen}
        closeModal={closeModal}
        size={size}
        className={cx(className)}
      >
        {children}
      </Modal>
    </>
  );
}

export { WrapperModal };
