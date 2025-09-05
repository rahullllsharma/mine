import type { FormBuilderAlertType } from "../../customisedForm.types";
import { useContext } from "react";
import { BodyText } from "@urbint/silica";
import Modal from "@/components/shared/modal/Modal";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import {
  checkTemplateWithOnlySummary,
  hasContentForSummary,
} from "./actionApi.utils";

interface ActionAlertProps {
  isOpen: boolean;
  setIsOpen: (value: boolean) => void;
  mode: FormBuilderAlertType | null;
  closeAction?: () => void;
  successAction?: () => void;
}
type AlertConfig = {
  title: string;
  message: string;
  cancelLabel: string;
  confirmLabel: string;
};

const ActionAlertPopUp = ({
  isOpen,
  setIsOpen,
  mode,
  closeAction,
  successAction,
}: ActionAlertProps) => {
  const { state } = useContext(CustomisedFromStateContext) || {
    state: { form: undefined },
  };

  if (!isOpen || !mode) {
    return null;
  }

  const doesSummaryHasContent = hasContentForSummary(state.form);
  const templateWithOnlySummary = checkTemplateWithOnlySummary(state.form);
  const emptyTemplate = state.form?.contents.length === 0;

  const handleClose = () => {
    if (closeAction) {
      closeAction();
    } else {
      setIsOpen(false);
    }
  };

  const handleSuccess = () => {
    if (successAction) {
      successAction();
    } else {
      setIsOpen(false);
    }
  };

  const getAlertConfig = (
    alertMode: FormBuilderAlertType
  ): AlertConfig | null => {
    switch (alertMode) {
      case "CLOSE":
        return {
          title: "Close",
          message: "Do you want to save the changes before closing the screen?",
          cancelLabel: "No",
          confirmLabel: "Yes",
        };
      case "PUBLISH":
        if (templateWithOnlySummary || emptyTemplate) {
          return {
            title: "Publish template",
            message:
              "You are creating a template with no pages in it. Are you sure you want to continue?",
            cancelLabel: "Cancel",
            confirmLabel: "Publish",
          };
        } else if (doesSummaryHasContent) {
          return {
            title: "Publish template",
            message: `Would you like to Proceed? Clicking "Publish" will set this template as the new version to be set up in the future`,
            cancelLabel: "Cancel",
            confirmLabel: "Publish",
          };
        } else {
          return {
            title: "Warning",
            message:
              "No data elements are marked ON for displaying in summary. Please go to the respective pages and turn ON the setting for displaying in summary. Alternatively you can still publish the template without a Summary page. Do you wish to continue?",
            cancelLabel: "No",
            confirmLabel: "Yes",
          };
        }
      default:
        return null;
    }
  };

  const alertConfig = getAlertConfig(mode);

  if (!alertConfig) {
    return null;
  }

  const { title, message, cancelLabel, confirmLabel } = alertConfig;

  return (
    <Modal
      title={title}
      isOpen={isOpen}
      closeModal={() => setIsOpen(false)}
      size="md"
      aria-labelledby="alert-modal-title"
    >
      <div>
        <BodyText>{message}</BodyText>

        <div className="flex w-full pt-4 border-t-2 border-solid mt-4 flex-wrap justify-end gap-x-2 gap-y-2">
          <ButtonSecondary
            label={cancelLabel}
            onClick={handleClose}
            aria-label={cancelLabel}
          />
          <ButtonPrimary
            label={confirmLabel}
            onClick={handleSuccess}
            aria-label={confirmLabel}
          />
        </div>
      </div>
    </Modal>
  );
};

export default ActionAlertPopUp;
