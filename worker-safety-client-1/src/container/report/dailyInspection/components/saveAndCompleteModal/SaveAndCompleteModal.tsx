import type { ModalProps } from "@/components/shared/modal/Modal";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";

import Modal from "@/components/shared/modal/Modal";

export type SaveAndCompleteModalProps = Pick<
  ModalProps,
  "isOpen" | "closeModal"
> & {
  onPrimaryBtnClick: () => void;
  isLoading?: boolean;
};

export default function SaveAndCompleteModal({
  closeModal,
  onPrimaryBtnClick,
  isLoading,
  ...props
}: SaveAndCompleteModalProps): JSX.Element {
  return (
    <Modal
      {...props}
      title="Are you sure you want to complete this report?"
      closeModal={closeModal}
    >
      <p>
        You will not be able to make changes once you&#39;ve completed the
        report.
      </p>
      <footer className="mt-14 flex flex-col sm:flex-row w-full sm:w-auto self-end gap-5">
        <ButtonSecondary
          disabled={isLoading}
          onClick={closeModal}
          label="Save and finish later"
        />
        <ButtonPrimary
          disabled={isLoading}
          onClick={onPrimaryBtnClick}
          label={isLoading ? "Saving..." : "Complete report"}
        />
      </footer>
    </Modal>
  );
}
