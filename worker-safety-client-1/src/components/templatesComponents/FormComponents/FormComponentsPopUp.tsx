import type { FormComponentsPopUpType } from "../customisedForm.types";
import { useContext, useState } from "react";
import { debounce } from "lodash-es";
import Modal from "@/components/shared/modal/Modal";
import {
  COMPONENTS_LIST,
  COMPONENTS_TYPES,
  ALERT_MESSAGES_FOR_COMPONENTS,
} from "@/utils/customisedFormUtils/customisedForm.constants";
import RadioGroup from "@/components/shared/radioGroup/RadioGroup";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import FormsComponentsPopUpFooter from "./FormComponentsPopUpFooter";
import { AddComponentsHandler } from "./utils/AddComponentsHandler";

const FormComponentsPopUp = ({
  isOpen,
  onClose,
  onAdd,
}: FormComponentsPopUpType) => {
  const [selectedComponent, setSelectedComponent] = useState<string | null>(
    null
  );
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const toastCtx = useContext(ToastContext);
  const cancelButtonHandler = () => {
    setSelectedComponent(null);
    onClose();
  };

  const addButtonHandler = debounce(() => {
    AddComponentsHandler(selectedComponent as string, onAdd, dispatch, state);
    onClose();
    additionAlert(selectedComponent as string);
    setSelectedComponent(null);
  }, 250);

  const additionAlert = (typeOfAttachment: string) => {
    const message =
      ALERT_MESSAGES_FOR_COMPONENTS[typeOfAttachment] ||
      "Component added successfully! Please click on Save/Update to save the changes";
    toastCtx?.pushToast("success", message);
  };

  const isComponentIncluded = (componentType: string) => {
    const metadata = state.form?.metadata;
    switch (componentType) {
      case COMPONENTS_TYPES.ACTIVITIES_AND_TASKS:
        return metadata?.is_activities_and_tasks_included ?? false;
      case COMPONENTS_TYPES.HAZARDS_AND_CONTROLS:
        return metadata?.is_hazards_and_controls_included ?? false;
      case COMPONENTS_TYPES.SUMMARY:
        return metadata?.is_summary_included ?? false;
      case COMPONENTS_TYPES.SITE_CONDITIONS:
        return metadata?.is_site_conditions_included ?? false;
      case COMPONENTS_TYPES.LOCATION:
        return metadata?.is_location_included ?? false;
      case COMPONENTS_TYPES.NEAREST_HOSPITAL:
        return metadata?.is_nearest_hospital_included ?? false;
      case COMPONENTS_TYPES.PHOTO_ATTACHMENTS:
      case COMPONENTS_TYPES.DOCUMENT_ATTACHMENTS:
      default:
        return false;
    }
  };

  const validOptions = COMPONENTS_LIST.map(option => ({
    id: option.id,
    value: option.description,
    description: option.label,
    disabled: isComponentIncluded(option.description),
  }));

  return (
    <Modal title="Add Component" isOpen={isOpen} closeModal={onClose} size="lg">
      <RadioGroup
        direction="col"
        options={validOptions}
        onSelect={event => {
          setSelectedComponent(event);
        }}
      />
      <FormsComponentsPopUpFooter
        cancelButtonHandler={cancelButtonHandler}
        addButtonHandler={addButtonHandler}
        isDisabled={!selectedComponent}
      />
    </Modal>
  );
};
export default FormComponentsPopUp;
