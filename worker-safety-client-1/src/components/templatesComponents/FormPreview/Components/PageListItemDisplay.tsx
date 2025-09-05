import type {
  UserFormMode,
  ActivePageObjType,
  PageType,
} from "../../customisedForm.types";
import { useContext, useMemo, useState } from "react";
import { StepItem } from "@/components/forms/Basic/StepItem";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import useCWFFormState from "@/hooks/useCWFFormState";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import style from "../../CreateTemplateLayout/createTemplateStyle.module.scss";
import { CWFItemType } from "../../customisedForm.types";

type PageListItemDisplayProps = {
  pageElement: PageType;
  activePageDetails: ActivePageObjType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  mode?: UserFormMode;
};
const PageListItemDisplay = ({
  pageElement,
  activePageDetails,
  setActivePageDetails,
  mode,
}: PageListItemDisplayProps) => {
  const [subPageIdArr, setSubPageIdArr] = useState<string[]>([pageElement.id]);
  const customFormState = useContext(CustomisedFromStateContext)!;
  const isFormDirty = customFormState?.state.isFormDirty || false;
  const { setCWFFormStateDirty } = useCWFFormState();
  const { dispatch } = useContext(CustomisedFromStateContext)!;

  const extractSubPages = useMemo(() => {
    const allSubPagesList = pageElement.contents.filter(
      element => element.type === CWFItemType.SubPage
    );
    const allIds = allSubPagesList.map(element => element.id);
    setSubPageIdArr(prev => [...prev, ...allIds]);
    return allSubPagesList;
  }, [pageElement]);

  const getCurrentPage = (pageDetails: PageType) => {
    const isActive = activePageDetails?.id === pageDetails.id;
    const status = pageDetails.properties.page_update_status;

    if (!isActive) return status;

    if (status === "saved") return "saved_current";
    if (status === "error") return "error";
    return "current";
  };

  const handlePageNavigation = (
    page: PageType,
    currentPageDetails: ActivePageObjType
  ) => {
    const curPageData = customFormState.state.form.contents.find(
      (item: PageType) => item.id === currentPageDetails?.id
    );
    const navigateToPage = () => {
      setActivePageDetails({
        id: page.id,
        parentId: "root",
        type: CWFItemType.Page,
      });
    };

    if (isFormDirty && mode !== "PREVIEW") {
      const confirmLeave = window.confirm("Discard unsaved changes?");
      if (confirmLeave) {
        setCWFFormStateDirty(false);
        dispatch({
          type: CF_REDUCER_CONSTANTS.RESET_PAGE,
          payload: activePageDetails?.id || "",
        });
        if (
          curPageData?.contents.some(
            content => content.type === CWFItemType.Location
          )
        ) {
          const stored_location_data = localStorage.getItem("location_data");
          if (stored_location_data) {
            dispatch({
              type: CF_REDUCER_CONSTANTS.LOCATION_VALUE_CHANGE,
              payload: JSON.parse(stored_location_data),
            });
          }
        }
        navigateToPage();
      }
    } else {
      navigateToPage();
    }
  };

  return (
    <div
      className={
        pageElement.properties.page_update_status === "saved"
          ? style.successPageTraversal
          : ""
      }
    >
      <StepItem
        key={pageElement.id}
        status={getCurrentPage(pageElement)}
        // status={getStepItemStatus(pageElement)}
        label={pageElement.properties.title}
        onClick={() => handlePageNavigation(pageElement, activePageDetails)}
      />

      {subPageIdArr.includes(activePageDetails ? activePageDetails.id : "") && (
        <div className={style.pageListingComponentParent__subPagesSection}>
          {extractSubPages.map((subPageDetails, index) => (
            <div
              key={index}
              className={
                subPageDetails.properties.page_update_status === "saved"
                  ? style.successPageTraversal
                  : ""
              }
            >
              <StepItem
                key={index}
                status={getCurrentPage(subPageDetails)}
                label={subPageDetails.properties.title}
                onClick={() => {
                  setActivePageDetails({
                    id: subPageDetails.id,
                    parentId: pageElement.id,
                    type: CWFItemType.SubPage,
                  });
                }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PageListItemDisplay;
