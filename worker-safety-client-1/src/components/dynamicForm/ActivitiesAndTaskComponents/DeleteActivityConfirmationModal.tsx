import type { ModalProps } from "@/components/shared/modal/Modal";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";

export type DeleteActivityConfirmationModalProps = Pick<
  ModalProps,
  "isOpen" | "closeModal"
> & {
  onConfirm: () => void;
  isLoading?: boolean;
};

export default function DeleteActivityConfirmationModal({
  isOpen,
  closeModal,
  onConfirm,
  isLoading = false,
}: DeleteActivityConfirmationModalProps): JSX.Element {
  return (
    <Modal
      title="Delete Tasks"
      isOpen={isOpen}
      closeModal={closeModal}
      size="md"
    >
      <div className="mb-10">
        <p className="text-neutral-shade-75">
          Are you sure you want to delete these Tasks?
        </p>
      </div>
      <div className="flex justify-end gap-3">
        <ButtonRegular
          label="Cancel"
          onClick={closeModal}
          disabled={isLoading}
        />
        <ButtonDanger label="Confirm" onClick={onConfirm} loading={isLoading} />
      </div>
    </Modal>
  );
}
