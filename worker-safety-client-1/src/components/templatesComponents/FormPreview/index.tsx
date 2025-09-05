import type {
  ProjectDetailsType} from "../customisedForm.types";
import { useContext, useEffect, useState } from "react";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import {
  CWFItemType,
  type ActivePageObjType,
  type FormType,
  type LinkComponentObj,
  type PageType,
  type UserFormMode,
  type WorkPackageData,
} from "../customisedForm.types";
import MainFormContainer from "./Components/MainFormContainer";
import TemplateFormHeader from "./Components/TemplateFormHeader";

type FormPreviewProps = {
  formObject: FormType;
  mode: UserFormMode;
  linkObj: LinkComponentObj;
  workPackageData?: WorkPackageData;
  setMode?: (mode: UserFormMode) => void;
  projectDetails?: ProjectDetailsType;
  creatingForm?: boolean;
};

const getFirstElement = (pageList: PageType[]) => {
  if (pageList.length) {
    return {
      id: pageList[0].id,
      parentId: "root",
      type: CWFItemType.Page,
      include_in_summary: pageList[0].properties.include_in_summary,
    };
  } else {
    return null;
  }
};

const FormPreview = ({
  formObject,
  mode,
  linkObj,
  workPackageData,
  setMode,
  projectDetails,
  creatingForm
}: FormPreviewProps) => {
  const [activePageDetails, setActivePageDetails] = useState<ActivePageObjType>(getFirstElement(formObject.contents));

  const { state, dispatch } = useContext(CustomisedFromStateContext)!;

  useEffect(() => {
    if (formObject) {
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: { ...formObject },
      });
    }

    if (workPackageData) {
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_WORK_PACKAGE_DATA,
        payload: { ...workPackageData },
      });
    }
  }, []);

  return (
    <>
      <TemplateFormHeader
        workPackageData={workPackageData}
        setMode={setMode}
        mode={mode}
        linkObj={linkObj}
        formObject={formObject}
      />
      <div className="flex justify-center h-full responsive-padding-y">
        {state.form ? (
          <MainFormContainer
            formObject={state.form}
            activePageDetails={activePageDetails}
            setActivePageDetails={setActivePageDetails}
            mode={mode}
            projectDetails={projectDetails}
            creatingForm={creatingForm}
          />
        ) : null}
      </div>
    </>
  );
};

export default FormPreview;
