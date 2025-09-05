import type {
  ActivePageObjType,
  FormElement,
  FormType,
} from "@/components/templatesComponents/customisedForm.types";
import { Icon } from "@urbint/silica";
import {
  FormStatus,
  UserFormModeTypes,
} from "@/components/templatesComponents/customisedForm.types";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { handleFormMode } from "@/components/forms/Utils";
import SummaryElementWrapper from "./SummaryElementWrapper";

const SummaryAccordion = ({
  isOpen,
  setIsOpen,
  element,
  pageMap,
  setActivePageDetails,
  activePageDetails,
  allFormPagesSaved,
  formObject,
}: {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  element: FormElement;
  pageMap?: Record<string, string>;
  setActivePageDetails?: (details: ActivePageObjType) => void;
  activePageDetails?: ActivePageObjType;
  allFormPagesSaved?: boolean;
  formObject: FormType;
}) => {
  const {
    me: { id: userId, permissions: userPermissions },
  } = useAuthStore();
  const isOwn = formObject?.created_by?.id === userId;
  const isCompleted = formObject?.properties?.status === "completed";

  const handleEditFormPermission = () => {
    const modes = handleFormMode(userPermissions, isOwn, isCompleted);
    return (
      modes.includes(UserFormModeTypes.EDIT) ||
      modes.includes(UserFormModeTypes.BUILD)
    );
  };
  return (
    <div className="w-full flex-1 flex flex-row">
      <button
        className={`flex w-full items-center gap-2 text-left p-2`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <Icon
          name="chevron_big_right"
          className={`text-[20px] transform transition-transform duration-200 ${
            isOpen ? "rotate-90" : ""
          }`}
        />
        <div className={`flex items-center text-[20px] font-semibold`}>
          {element.properties.title}
        </div>
      </button>
      {handleEditFormPermission() && (
        <div className="flex flex-col items-center justify-center">
          <SummaryElementWrapper
            elementId={element.id}
            pageMap={pageMap}
            setActivePageDetails={setActivePageDetails}
            activePageDetails={activePageDetails}
            isFormFullySaved={
              allFormPagesSaved &&
              formObject.properties.status === FormStatus.Completed
            }
          />
        </div>
      )}
    </div>
  );
};

export default SummaryAccordion;
