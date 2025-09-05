import type {
  ActivePageObjType,
  PageType,
  WidgetType,
  ModeTypePageSection,
} from "../customisedForm.types";
import React, { useContext, useEffect, useState } from "react";
import orderBy from "lodash/orderBy";
import { CWFItemType } from "../customisedForm.types";
import CustomisedFromStateContext from "../../../context/CustomisedDataContext/CustomisedFormStateContext";
import style from "./createTemplateStyle.module.scss";

import AddPageComponent from "./AddPageComponent";
import PreviewComponent from "./PreviewComponent";

const getContentsArr = (
  data: PageType[],
  activePageDetails: ActivePageObjType
) => {
  const dowWork = () => {
    if (activePageDetails?.type) {
      if (activePageDetails.type === CWFItemType.SubPage) {
        return (
          data
            .filter(
              (element: PageType) => element.id === activePageDetails.parentId
            )?.[0]
            ?.contents.filter(
              (item: PageType) => item.id === activePageDetails.id
            )?.[0]?.contents || []
        );
      } else {
        return (
          data.filter(
            (element: PageType) => element.id === activePageDetails.id
          )?.[0]?.contents || []
        );
      }
    }
  };
  const contents = dowWork();
  return orderBy(contents || [], o => o.order, "asc");
};

const CreateTemplateLayout = () => {
  const [newPageTitle, setNewPageTitle] = useState<string>("");
  const [activePageDetails, setActivePageDetails] =
    useState<ActivePageObjType>(null);
  const [activeWidgetDetails, setActiveWidgetDetails] =
    useState<WidgetType>(null);
  const [subPageTitle, setSubPageTitle] = useState<string>("");
  const [parentPage, setParentPage] = useState<string>("");
  const [mode, setMode] = useState<ModeTypePageSection>("default");
  const { state } = useContext(CustomisedFromStateContext)!;

  const activeContents = getContentsArr(state.form.contents, activePageDetails);

  useEffect(() => {
    if (!activePageDetails && state.form.contents.length) {
      setActivePageDetails({
        id: state.form.contents[0].id,
        parentId: "root",
        type: CWFItemType.Page,
      });
    }
  }, [activePageDetails, state]);

  return (
    <div className={`${style.createTemplateLayoutParent}`}>
      <div className={style.createTemplateLayoutParent__leftSide}>
        <AddPageComponent
          newPageTitle={newPageTitle}
          setNewPageTitle={setNewPageTitle}
          activePageDetails={activePageDetails}
          setActivePageDetails={setActivePageDetails}
          subPageTitle={subPageTitle}
          setSubPageTitle={setSubPageTitle}
          parentPage={parentPage}
          setParentPage={setParentPage}
          mode={mode}
          setMode={setMode}
        />
      </div>
      <div className={style.createTemplateLayoutParent__rightSide}>
        <PreviewComponent
          activePageDetails={activePageDetails}
          setActivePageDetails={setActivePageDetails}
          activeWidgetDetails={activeWidgetDetails}
          setActiveWidgetDetails={setActiveWidgetDetails}
          activeContents={activeContents}
          setMode={setMode}
        />
      </div>
    </div>
  );
};

export default React.memo(CreateTemplateLayout);
