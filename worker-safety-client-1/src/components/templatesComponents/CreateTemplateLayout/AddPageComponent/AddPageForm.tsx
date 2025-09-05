import { useContext } from "react";
import { v4 as uuidv4 } from "uuid";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import {
  CWFItemType,
  type ActivePageObjType,
  type ModeTypePageSection,
} from "../../customisedForm.types";
import style from "../createTemplateStyle.module.scss";
import CustomisedFromStateContext from "../../../../context/CustomisedDataContext/CustomisedFormStateContext";

type AddPageFormProps = {
  label: string;
  setMode: (a: ModeTypePageSection) => void;
  newPageTitle: string;
  setNewPageTitle: (item: string) => void;
  mode: string;
  setActivePageDetails: (item: ActivePageObjType) => void;
  parentPage: string;
  setParentPage: (item: string) => void;
};

const AddPageForm = ({
  label,
  setMode,
  newPageTitle,
  setNewPageTitle,
  mode,
  setActivePageDetails,
  parentPage,
  setParentPage,
}: AddPageFormProps) => {
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;

  const addData = (currentMode: string) => {
    if (currentMode === "addPage") {
      const currentID = uuidv4();
      if (newPageTitle.trim() !== "") {
        dispatch({
          type: CF_REDUCER_CONSTANTS.ADD_PAGE,
          payload: {
            id: currentID,
            type: CWFItemType.Page,
            order: state.form.contents.length + 1,
            properties: {
              title: newPageTitle,
              description: "",
              page_update_status: "default",
              include_in_summary: false,
            },
            contents: [],
          },
        });
        setNewPageTitle("");
        setMode("default");
        setActivePageDetails({
          id: currentID,
          parentId: "root",
          type: CWFItemType.Page,
        });
        setParentPage(currentID);
      }
    } else {
      const currentID = uuidv4();
      const currentOrder =
        state.form.contents.map(page => {
          if (page.id === parentPage) {
            return page;
          }
        })[0]?.contents.length || 0;

      if (newPageTitle.trim() !== "") {
        dispatch({
          type: CF_REDUCER_CONSTANTS.ADD_SUBPAGE,
          payload: {
            parentPage: parentPage,
            subpageDetails: {
              id: currentID,
              type: CWFItemType.SubPage,
              order: currentOrder + 1,
              properties: {
                title: newPageTitle,
                description: "",
                page_update_status: "default",
                include_in_summary: false,
              },
              contents: [],
            },
          },
        });
      }

      setNewPageTitle("");
      setMode("default");
      setActivePageDetails({
        id: currentID,
        parentId: parentPage,
        type: CWFItemType.SubPage,
      });
    }
  };
  const isAddDisabled = newPageTitle.trim().length === 0;
  return (
    <div className={style.addPageFormComponent}>
      <div className={style.addPageFormComponent__headerPanel}>
        <h3 className="text-section-heading font-section-heading text-neutrals-primary text-lg font-semibold p-4 md:p-0">
          {label}
        </h3>
        <div className={style.addPageFormComponent__ctaPanel}>
          <ButtonIcon
            iconName="check_big"
            disabled={isAddDisabled}
            onClick={() => {
              addData(mode);
            }}
          />

          <ButtonIcon
            iconName="close_big"
            disabled={false}
            onClick={() => {
              setNewPageTitle("");
              setMode("default");
            }}
          />
        </div>
      </div>

      <p className="ml-0 text-base font-normal text-neutral-shade-100">
        {mode === "addPage" ? "Input Page Title" : "Input Sub page Title"}
      </p>
    </div>
  );
};

export default AddPageForm;
