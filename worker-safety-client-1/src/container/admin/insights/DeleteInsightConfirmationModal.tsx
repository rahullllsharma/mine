import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import Modal from "@/components/shared/modal/Modal";

interface DeleteInsightConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (id: string) => void;
  id: string | null;
  isDeleting?: boolean;
}

const DeleteInsightConfirmationModal = ({
  isOpen,
  onClose,
  onSubmit,
  id,
  isDeleting = false,
}: DeleteInsightConfirmationModalProps): JSX.Element => {
  const closeModal = () => {
    onClose();
  };

  return (
    <Modal isOpen={isOpen} closeModal={closeModal} title="Delete Insight">
      <div className="flex flex-col gap-4">
        <p>
          You are deleting the Insight, this will remove the report/dashboard
          from the Insights menu.
        </p>
        <footer className="flex justify-end gap-4 border-t border-gray-300 pt-4 pb-0 px-6 w-[calc(100%+48px)] -left-6 relative">
          <ButtonTertiary label="Cancel" onClick={closeModal} />
          {id ? (
            <ButtonDanger
              label="Delete Report"
              onClick={() => {
                onSubmit(id);
              }}
              loading={isDeleting}
            />
          ) : null}
        </footer>
      </div>
    </Modal>
  );
};

export default DeleteInsightConfirmationModal;
