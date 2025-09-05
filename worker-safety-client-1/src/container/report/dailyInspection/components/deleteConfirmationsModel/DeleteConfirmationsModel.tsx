import type { ModalProps } from "@/components/shared/modal/Modal";
import { useContext } from "react";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import Modal from "@/components/shared/modal/Modal";

export type DeleteConfirmationsModalProps = Pick<
  ModalProps,
  "isOpen" | "closeModal"
> & {
  onDeleteConfirm: () => void;
  isLoading?: boolean;
};

export default function DeleteConfirmationsModal({
  closeModal,
  onDeleteConfirm,
  isLoading,
  ...props
}: DeleteConfirmationsModalProps): JSX.Element {
  const toastCtx = useContext(ToastContext);
  return (
    <Modal {...props} title="Delete photos" closeModal={closeModal}>
      <p>
        Are you sure you want to permanently delete this photo? This action
        cannot be undone.
      </p>
      <footer className="mt-14 flex flex-col sm:flex-row w-full sm:w-auto self-end gap-5">
        <ButtonSecondary
          disabled={isLoading}
          onClick={closeModal}
          label="Cancel"
        />
        <ButtonDanger
          disabled={isLoading}
          onClick={() => {
            // 2) Show the toast first (or after calling onDeleteConfirm)
            toastCtx?.pushToast("success", "Photo deleted Please click on Save and Continue / save and complete to push the changes");
            // 3) Then invoke onDeleteConfirm
            onDeleteConfirm();
          }}
          label={isLoading ? "Deleting..." : "Delete"}
        />
      </footer>
    </Modal>
  );
}