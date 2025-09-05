import type {
  ActivePageObjType,
  ModeTypePageSection,
} from "../../customisedForm.types";
import { useContext, useState } from "react";
import { CWFItemType } from "../../customisedForm.types";
import style from "../createTemplateStyle.module.scss";

import CustomisedFromStateContext from "../../../../context/CustomisedDataContext/CustomisedFormStateContext";
import AddPageListItem from "./AddPageListItem";
import PageListItem from "./PageListItem";

type PageDetails = {
  id: string;
  parentId: string;
  deleteParentPage: boolean;
  subPages: string[];
};

const PageListComponent = ({
  mode,
  newPageTitle,
  setNewPageTitle,
  activePageDetails,
  setActivePageDetails,
  subPageTitle,
  setSubPageTitle,
  setParentPage,
  deletePageDetails,
  onDeletePageDetailsUpdate,
  deletePageReset,
  OnDeletePageReset,
}: {
  mode: ModeTypePageSection;
  newPageTitle: string;
  setNewPageTitle: (item: string) => void;
  activePageDetails: ActivePageObjType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  subPageTitle: string;
  setSubPageTitle: (item: string) => void;
  setParentPage: (item: string) => void;
  deletePageDetails: PageDetails[];
  onDeletePageDetailsUpdate: (data: any) => void;
  deletePageReset: boolean;
  OnDeletePageReset: (flag: boolean) => void;
}) => {
  const { state } = useContext(CustomisedFromStateContext)!;

  // const toastCtx = useContext(ToastContext);
  // const [pageContents, setPageContents] = useState(state.form.contents);

  // useEffect(() => {
  //   setPageContents(state.form.contents);
  // }, [state]);

  const [pageDeleteDetails, setPageDeleteDetails] = useState<PageDetails[]>([]);
  // const [onSubPageOrderChange, setOnSubPageOrderChange] =
  //   useState<boolean>(false);

  const handlePageDelete = (pageDetails: PageDetails) => {
    const existingDetailsIndex = pageDeleteDetails.findIndex(
      details => details.id === pageDetails.id
    );
    if (existingDetailsIndex !== -1) {
      setPageDeleteDetails(prevDetails => {
        const updatedDetails = [...prevDetails];
        updatedDetails[existingDetailsIndex] = pageDetails;
        return updatedDetails;
      });
    } else {
      setPageDeleteDetails(prevDetails => [...prevDetails, pageDetails]);
    }
  };
  const onSelectOrDeSelectPage = (currentPageDetails: PageDetails) => {
    const updatedDeletePageDetails = [...deletePageDetails]; // Create a copy of deletePageDetails
    const existingDetailsIndex = updatedDeletePageDetails.findIndex(
      details => currentPageDetails.id === details.id
    );

    // Check if this is a parent page with subpages
    if (currentPageDetails.subPages && currentPageDetails.subPages.length > 0) {
      // Get all subpages for this parent page
      const allSubPagesForParent =
        state.form.contents
          .find(page => page.id === currentPageDetails.id)
          ?.contents?.filter(content => content.type === CWFItemType.SubPage)
          .map(subPage => subPage.id) || [];

      // Check if all subpages are selected
      const allSubPagesSelected = allSubPagesForParent.every(subPageId =>
        currentPageDetails.subPages.includes(subPageId)
      );

      const updatedPageDetails = {
        ...currentPageDetails,
        deleteParentPage: allSubPagesSelected,
        parentId: allSubPagesSelected ? currentPageDetails.id : "",
      };

      if (existingDetailsIndex > -1) {
        updatedDeletePageDetails[existingDetailsIndex] = updatedPageDetails;
      } else {
        updatedDeletePageDetails.push(updatedPageDetails);
      }
    } else {
      // Handle regular page selection (no subpages)
      if (existingDetailsIndex > -1) {
        updatedDeletePageDetails[existingDetailsIndex] = currentPageDetails;
      } else {
        updatedDeletePageDetails.push(currentPageDetails);
      }
    }

    onDeletePageDetailsUpdate(updatedDeletePageDetails); // Call the callback function
  };
  // const onDragOfParentPage = (result: any) => {
  //   if (!result.destination) {
  //     toastCtx?.pushToast(
  //       "error",
  //       "The item could not be dropped in the designated area. Please try again."
  //     );

  //     return;
  //   }

  //   let items: any = Array.from(pageContents);
  //   const [reorderedItem] = items.splice(result.source.index, 1);
  //   items.splice(result.destination.index, 0, reorderedItem);
  //   items = items.map((item: any, index: number) => ({
  //     ...item,
  //     order: index + 1,
  //   }));
  //   setPageContents(items);
  //   onPageEdit(items);
  // };

  // const findParentPageIndex = (pages: any, parentId: string): number => {
  //   return pages.findIndex((page: any) => page.id === parentId);
  // };

  // const reorderSubPages = (
  //   subPages: any[],
  //   sourceIndex: number,
  //   destinationIndex: number
  // ): any[] => {
  //   const [reorderedItem] = subPages.splice(sourceIndex, 1);
  //   subPages.splice(destinationIndex, 0, reorderedItem);
  //   return subPages.map((item, index) => ({
  //     ...item,
  //     order: index + 1,
  //   }));
  // };

  // const OnDragOfSubPage = (result: any, parentPageId: string) => {
  //   console.log(result, parentPageId);

  //     const parentPages: any = [...pageContents];
  //     const activeParentPageIndex = findParentPageIndex(
  //       parentPages,
  //       parentPageId
  //     );
  //     if (activeParentPageIndex !== -1) {
  //       const activeParentPage = parentPages[activeParentPageIndex];
  //       const { contents: subPages } = activeParentPage;
  //       activeParentPage.contents = reorderSubPages(
  //         subPages,
  //         result.source.index,
  //         result.destination.index
  //       );
  //       parentPages[activeParentPageIndex] = activeParentPage;
  //       setPageContents(parentPages);
  //       setOnSubPageOrderChange(true);
  //       onPageEdit(parentPages);
  //     }
  // };
  // useEffect(() => {
  //   setOnSubPageOrderChange(false);
  // }, [pageContents]);

  return (
    <div className={style.pageListingComponentParent}>
      {state.form.contents.map(element => (
        <PageListItem
          mode={mode}
          key={element.id}
          pageDetails={element}
          activePageDetails={activePageDetails}
          setActivePageDetails={setActivePageDetails}
          pageAdditionMode={mode}
          subPageTitle={subPageTitle}
          setSubPageTitle={setSubPageTitle}
          setParentPage={setParentPage}
          handlePageDelete={handlePageDelete}
          onSelectOrDeSelectPage={onSelectOrDeSelectPage}
          deletePageReset={deletePageReset}
          OnDeletePageReset={OnDeletePageReset}
          deletePageDetails={deletePageDetails}
        />
      ))}
      {mode === "addPage" ? (
        <AddPageListItem
          newPageTitle={newPageTitle}
          setNewPageTitle={setNewPageTitle}
        />
      ) : null}
    </div>
  );
};

export default PageListComponent;
