import type { CustomDeleteConfirmationsModal } from "@/components/templatesComponents/customisedForm.types";
import { useContext } from "react";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import Modal from "@/components/shared/modal/Modal";

export default function CustomDeleteConfirmationsModal({
  closeModal,
  onDeleteConfirm,
  isLoading,
  attachmentItem,
  ...props
}: CustomDeleteConfirmationsModal): JSX.Element {
  const toastCtx = useContext(ToastContext);
  const dialogMsg = attachmentItem?.properties?.attachment_type;
  return (
    <Modal
      {...props}
      title={dialogMsg === "photo" ? "Delete Photos" : "Delete Documents"}
      closeModal={closeModal}
    >
      <p>
        Are you sure you want to permanently delete this{" "}
        {dialogMsg === "photo" ? "photo" : "document"}? This action cannot be
        undone.
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
            toastCtx?.pushToast(
              "success",
              `${
                dialogMsg === "photo" ? "Photo" : "Document"
              } deleted Please click on Save and Continue / save and complete to push changes`
            );
            onDeleteConfirm();
          }}
          label={isLoading ? "Deleting..." : "Delete"}
        />
      </footer>
    </Modal>
  );
}
