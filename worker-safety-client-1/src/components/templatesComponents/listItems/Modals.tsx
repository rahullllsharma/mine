import React from "react";
import PublishTemplateModal from "../listPopUpComponents/publishTemplateModal";
import VersionHistoryModal from "../listPopUpComponents/versionHistoryModal";

interface ModalsProps {
  showVersionHistory: boolean;
  showPublishModal: boolean;
  togglePublishTemplateModal: () => void;
  toggleVersionHistoryModal: (templateUUID?: string) => void;
  selectedTemplateUUID: string;
  publishTemplate: () => void;
  selectedTemplateTitle: string;
}

const Modals: React.FC<ModalsProps> = ({
  showVersionHistory,
  showPublishModal,
  togglePublishTemplateModal,
  toggleVersionHistoryModal,
  selectedTemplateUUID,
  publishTemplate,
  selectedTemplateTitle,
}) => (
  <>
    <VersionHistoryModal
      isOpen={showVersionHistory}
      onClose={toggleVersionHistoryModal}
      publishedTemplateUUID={selectedTemplateUUID}
      selectedTemplateTitle={selectedTemplateTitle}
    />
    <PublishTemplateModal
      isOpen={showPublishModal}
      onClose={togglePublishTemplateModal}
      publishTemplate={publishTemplate}
    />
  </>
);

export default Modals;
