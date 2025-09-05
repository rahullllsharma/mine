import Modal from "@/components/shared/modal/Modal";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";

type DeletePageConfirmationModalType = {
  deletePageModalOpen: boolean;
  setDeletePageModalOpen: (item: boolean) => void;
  onConfirmOfDeletePage: () => void;
};

const DeletePageConfirmationModal = ({
  deletePageModalOpen,
  setDeletePageModalOpen,
  onConfirmOfDeletePage,
}: DeletePageConfirmationModalType) => {
  return (
    <Modal
      title="Delete Pages"
      isOpen={deletePageModalOpen}
      closeModal={() => setDeletePageModalOpen(false)}
      size={"md"}
    >
      <div>
        <div>Do you want to delete the selected pages?</div>
        <div className="flex self-end w-full pt-4 flex-row-reverse m-t-4 border-t-2 border-solid mt-4">
          <ButtonDanger
            label={"Delete"}
            onClick={() => onConfirmOfDeletePage()}
          />
          <ButtonRegular
            className="mr-2"
            label="Cancel"
            onClick={() => setDeletePageModalOpen(false)}
          />
        </div>
      </div>
    </Modal>
  );
};

export default DeletePageConfirmationModal;
