import Modal from "@/components/shared/modal/Modal";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";

type EditPageConfirmationModalType = {
  editPageModalOpen: boolean;
  setEditPageModalOpen: (item: boolean) => void;
  onEditPageConfirm: (item: string) => void;
};

const EditPageConfirmationModal = ({
  editPageModalOpen,
  setEditPageModalOpen,
  onEditPageConfirm,
}: EditPageConfirmationModalType) => {
  return (
    <Modal
      title="Edit Page"
      isOpen={editPageModalOpen}
      closeModal={() => setEditPageModalOpen(false)}
      size={"md"}
    >
      <div>
        <div>Are you sure you want to proceed with making the edits?</div>
        <div className="flex self-end w-full pt-4 flex-row-reverse m-t-4 border-t-2 border-solid mt-4">
          <ButtonDanger
            label={"Yes"}
            onClick={() => onEditPageConfirm("save")}
          />
          <ButtonRegular
            className="mr-2"
            label="No"
            onClick={() => setEditPageModalOpen(false)}
          />
        </div>
      </div>
    </Modal>
  );
};

export default EditPageConfirmationModal;
