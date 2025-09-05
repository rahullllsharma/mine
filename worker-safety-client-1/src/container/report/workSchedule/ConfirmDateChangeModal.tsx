import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";

type ConfirmDateChangeModalProps = {
  onCancel: () => void;
  onConfirm: () => void;
  isOpen?: boolean;
  isForLocationCheck?: boolean;
};

function ConfirmDateChangeModal({
  onCancel,
  onConfirm,
  isOpen = true,
  isForLocationCheck,
}: ConfirmDateChangeModalProps) {
  return (
    <Modal
      isOpen={isOpen}
      title={isForLocationCheck ? "Change Location?" : "Change Date?"}
      closeModal={onCancel}
    >
      <div className="mb-3 border-b">
        <p className="mb-5 text-base/6">
          Proceeding may update some information on this form. <br />
          Are you sure you want to continue?
        </p>
      </div>
      <div className="flex justify-end gap-3">
        <ButtonRegular label="Cancel" onClick={onCancel} />
        <ButtonDanger label={`Confirm Change`} onClick={onConfirm} />
      </div>
    </Modal>
  );
}

export { ConfirmDateChangeModal };
