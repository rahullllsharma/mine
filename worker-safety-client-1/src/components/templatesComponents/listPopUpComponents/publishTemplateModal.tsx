import ButtonPrimary from "../../shared/button/primary/ButtonPrimary";
import ButtonTertiary from "../../shared/button/tertiary/ButtonTertiary";
import Modal from "../../shared/modal/Modal";

type PublishTemplateModalProps = {
  isOpen: boolean;
  onClose: () => void;
  publishTemplate: () => void;
};

const PublishTemplateModal = ({
  isOpen,
  onClose,
  publishTemplate,
}: PublishTemplateModalProps) => {
  return (
    <Modal
      className="max-w-[50rem] bg-[#f7f8f8]"
      title="Publish Template"
      isOpen={isOpen}
      closeModal={onClose}
    >
      <div>
        {`Would you like to Proceed? Clicking 'Publish' will set this template as
        the new version to be used in the future.`}
      </div>

      <div className="flex justify-end gap-4 pt-12 pb-0">
        <ButtonTertiary label="Cancel" onClick={onClose} />
        <ButtonPrimary label="Publish" onClick={publishTemplate} />
      </div>
    </Modal>
  );
};

export default PublishTemplateModal;
