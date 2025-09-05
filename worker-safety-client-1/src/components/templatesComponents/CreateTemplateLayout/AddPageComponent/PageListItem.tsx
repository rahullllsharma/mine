import type {
  ActivePageObjType,
  PageType,
  ModeTypePageSection,
} from "../../customisedForm.types";
import { useEffect, useMemo, useState } from "react";

import { CWFItemType } from "../../customisedForm.types";
import style from "../createTemplateStyle.module.scss";
import AddPageListItem from "./AddPageListItem";
import WithDeletePage from "./withDeletePage";

type PageDetails = {
  id: string;
  parentId: string;
  deleteParentPage: boolean;
  subPages: string[];
};

type PageListItemProps = {
  pageDetails: PageType;
  activePageDetails: ActivePageObjType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  pageAdditionMode: string;
  subPageTitle: string;
  setSubPageTitle: (item: string) => void;
  setParentPage: (item: string) => void;
  mode: ModeTypePageSection;
  handlePageDelete: (details: PageDetails) => void;
  onSelectOrDeSelectPage: (details: PageDetails) => void;
  deletePageReset: boolean;
  OnDeletePageReset: (flag: boolean) => void;
  deletePageDetails: PageDetails[];
};

const PageListItem = ({
  pageDetails,
  pageAdditionMode,
  subPageTitle,
  setSubPageTitle,
  activePageDetails,
  setActivePageDetails,
  setParentPage,
  mode,
  onSelectOrDeSelectPage,
  deletePageReset,
  OnDeletePageReset,
  deletePageDetails,
}: PageListItemProps) => {
  const [subPageIdArr, setSubPageIdArr] = useState<string[]>([pageDetails.id]);

  useEffect(() => {
    //clearing page selected state after user action
    if (deletePageReset) {
      setParentPageToDelete("");
      setSubPagesToDelete([]);
      //retaining Page Delete flag
      OnDeletePageReset(false);
    }
  }, [deletePageReset]);

  const extractSubPages = useMemo(() => {
    const allSubPagesList = pageDetails.contents.filter(
      element => element.type === CWFItemType.SubPage
    );
    const allIds = allSubPagesList.map(element => element.id);
    setSubPageIdArr(prev => [...prev, ...allIds]);
    return allSubPagesList;
  }, [pageDetails, subPageTitle]);

  const [parentPageToDelete, setParentPageToDelete] = useState<string>("");
  const [subPagesToDelete, setSubPagesToDelete] = useState<string[]>([]);

  useEffect(() => {
    const currentPageDetails = deletePageDetails.find(
      details => details.id === pageDetails.id
    );

    if (currentPageDetails) {
      setParentPageToDelete(currentPageDetails.parentId || "");
      setSubPagesToDelete(currentPageDetails.subPages || []);
    } else {
      setParentPageToDelete("");
      setSubPagesToDelete([]);
    }
  }, [deletePageDetails, pageDetails.id]);

  const onChangeOfCheckboxValue = ({
    id,
    parentId,
    deleteParentPage: deleteFlag,
    subPages,
  }: PageDetails) => {
    onSelectOrDeSelectPage({
      id: id,
      parentId: parentId,
      deleteParentPage: deleteFlag,
      subPages,
    });
  };

  const addParentPageToDelete = (pageId: string) => {
    setParentPageToDelete(pageId);
    const subPagesWithId: string[] = pageDetails.contents
      .filter(
        (item: { type: string; id: string }) =>
          item.type === CWFItemType.SubPage
      )
      .map((item: { id: string }) => item.id);
    setSubPagesToDelete(subPagesWithId);
    onChangeOfCheckboxValue({
      id: pageDetails.id,
      parentId: pageId,
      deleteParentPage: true,
      subPages: subPagesWithId,
    });
  };

  const removeParentPageToDelete = () => {
    setParentPageToDelete("");
    setSubPagesToDelete([]);
    onChangeOfCheckboxValue({
      id: pageDetails.id,
      parentId: "",
      deleteParentPage: false,
      subPages: [],
    });
  };

  const addSubPageToDelete = (pageId: string) => {
    setSubPagesToDelete(prevState => [...prevState, pageId]);
    onChangeOfCheckboxValue({
      id: pageDetails.id,
      parentId: parentPageToDelete,
      deleteParentPage: !!parentPageToDelete,
      subPages: [...subPagesToDelete, pageId],
    });
  };

  const removeSubPageToDelete = (pageId: string) => {
    setSubPagesToDelete(prevState =>
      prevState.filter(subPage => subPage !== pageId)
    );
    onChangeOfCheckboxValue({
      id: pageDetails.id,
      parentId: parentPageToDelete,
      deleteParentPage: !!parentPageToDelete,
      subPages: subPagesToDelete.filter(subPage => subPage !== pageId),
    });
  };

  return (
    <div>
      <WithDeletePage
        status={
          activePageDetails?.id === pageDetails.id
            ? "current"
            : pageDetails.properties.page_update_status
        }
        label={pageDetails.properties.title}
        mode={mode}
        selected={parentPageToDelete === pageDetails.id}
        onSelectOfPage={() => {
          setParentPage(pageDetails.id);
          setActivePageDetails({
            id: pageDetails.id,
            parentId: "root",
            type: CWFItemType.Page,
          });
        }}
        onSelectOfCheckbox={() => {
          if (parentPageToDelete) {
            removeParentPageToDelete();
          } else {
            addParentPageToDelete(pageDetails.id);
          }
        }}
      />

      {subPageIdArr.includes(activePageDetails ? activePageDetails.id : "") && (
        <div className={style.pageListingComponentParent__subPagesSection}>
          {extractSubPages.map(subPageDetails => (
            <WithDeletePage
              key={subPageDetails.id}
              status={
                activePageDetails?.id === subPageDetails.id
                  ? "current"
                  : subPageDetails.properties.page_update_status
              }
              selected={
                subPagesToDelete.length
                  ? subPagesToDelete.includes(subPageDetails.id)
                  : false
              }
              mode={mode}
              label={subPageDetails.properties.title}
              onSelectOfPage={function (): void {
                setActivePageDetails({
                  id: subPageDetails.id,
                  parentId: pageDetails.id,
                  type: CWFItemType.SubPage,
                });
              }}
              onSelectOfCheckbox={() => {
                if (subPagesToDelete.includes(subPageDetails.id)) {
                  removeSubPageToDelete(subPageDetails.id);
                } else {
                  addSubPageToDelete(subPageDetails.id);
                }
              }}
            />
          ))}
          {pageAdditionMode === "addSubPage" ? (
            <AddPageListItem
              newPageTitle={subPageTitle}
              setNewPageTitle={setSubPageTitle}
            />
          ) : null}
        </div>
      )}
    </div>
  );
};

export default PageListItem;
