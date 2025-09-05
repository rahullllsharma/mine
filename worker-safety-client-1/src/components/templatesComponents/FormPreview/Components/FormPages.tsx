import type {
  ActivePageObjType,
  PageType,
  UserFormMode,
} from "../../customisedForm.types";
import { useContext } from "react";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import useLeavePageConfirm from "@/hooks/useLeavePageConfirm";
import style from "../../CreateTemplateLayout/createTemplateStyle.module.scss";
import PageListItemDisplay from "./PageListItemDisplay";

const FormPages = ({
  formPages,
  activePageDetails,
  setActivePageDetails,
  mode,
}: {
  formPages: PageType[];
  activePageDetails: ActivePageObjType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  mode?: UserFormMode;
}) => {
  const customFormState = useContext(CustomisedFromStateContext)!;

  const isFormDirty = customFormState?.state.isFormDirty || false;

  useLeavePageConfirm("Discard unsaved changes?", isFormDirty);

  return (
    <div className={style.addPageComponentParent}>
      <div className={style.addPageComponentParent__pageList}>
        <div className={style.pageListingComponentParentPreview}>
          {formPages.map(element => (
            <PageListItemDisplay
              key={element.id}
              pageElement={element}
              activePageDetails={activePageDetails}
              setActivePageDetails={setActivePageDetails}
              mode={mode}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default FormPages;
