import ToastContext from "@/components/shared/toast/context/ToastContext";
import { useContext, useEffect, useState } from "react";
import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";
import {
  ActivePageObjType,
  PageType,
  ModeTypePageSection,
} from "../../customisedForm.types";
import style from "../createTemplateStyle.module.scss";
import MockPageListItem from "./MockPageListItem";

type PageDetails = {
  id: string;
  parentId: string;
  deleteParentPage: boolean;
  subPages: string[];
};

const MockPageListComponent = ({
  mode,
  activePageDetails,
  setActivePageDetails,
  setParentPage,
  onPageEdit,
  mockPageContents,
  setMockPageContents,
}: {
  mode: ModeTypePageSection;
  activePageDetails: ActivePageObjType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  setParentPage: (item: string) => void;
  onPageEdit: (data: any) => void;
  mockPageContents: PageType[];
  setMockPageContents: (items: any) => void;
}) => {
  const toastCtx = useContext(ToastContext);
  const [pageDeleteDetails, setPageDeleteDetails] = useState<PageDetails[]>([]);
  const [onSubPageOrderChange, setOnSubPageOrderChange] =
    useState<boolean>(false);

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

  const onDragEnd = (result: any) => {
    if (!result.destination) {
      toastCtx?.pushToast(
        "error",
        "The item could not be dropped in the designated area. Please try again."
      );

      return;
    }
    const { type } = result;
    if (type === "PAGE") {
      onDragOfParentPage(result);
    } else if (type === "SUB_PAGE") {
      const parentPageId = result.source.droppableId;
      OnDragOfSubPage(result, parentPageId);
    }
  };

  const onDragOfParentPage = (result: any) => {
    if (!result.destination) {
      toastCtx?.pushToast(
        "error",
        "The item could not be dropped in the designated area. Please try again."
      );

      return;
    }

    let items: any = Array.from(mockPageContents);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    items = items.map((item: any, index: number) => ({
      ...item,
      order: index + 1,
    }));
    setMockPageContents(items);
    onPageEdit(items);
  };

  const findParentPageIndex = (pages: any, parentId: string): number => {
    return pages.findIndex((page: any) => page.id === parentId);
  };

  const reorderSubPages = (
    subPages: any[],
    sourceIndex: number,
    destinationIndex: number
  ): any[] => {
    const [reorderedItem] = subPages.splice(sourceIndex, 1);
    subPages.splice(destinationIndex, 0, reorderedItem);
    return subPages.map((item, index) => ({
      ...item,
      order: index + 1,
    }));
  };

  const OnDragOfSubPage = (result: any, parentPageId: string) => {
    const parentPages: any = [...mockPageContents];
    const activeParentPageIndex = findParentPageIndex(
      parentPages,
      parentPageId
    );

    if (activeParentPageIndex !== -1) {
      const activeParentPage = parentPages[activeParentPageIndex];
      const { contents: subPages } = activeParentPage;

      activeParentPage.contents = reorderSubPages(
        subPages,
        result.source.index,
        result.destination.index
      );

      parentPages[activeParentPageIndex] = activeParentPage;

      setMockPageContents(parentPages);
      setOnSubPageOrderChange(true);
      onPageEdit(parentPages);
    }
  };
  useEffect(() => {
    setOnSubPageOrderChange(false);
  }, [mockPageContents]);

  const onEditChange = (
    currentActivePageDetails: ActivePageObjType,
    value: string
  ) => {
    const newState = [...mockPageContents];
    if (currentActivePageDetails?.parentId === "root") {
      const pageToUpdate = newState.find(
        page => page.id === currentActivePageDetails.id
      );
      if (pageToUpdate) {
        pageToUpdate.properties.title = value;
      }
    } else {
      const parentPage = newState.find(
        page => page.id === currentActivePageDetails?.parentId
      );
      if (parentPage && parentPage.contents) {
        const subpageToUpdate = parentPage.contents.find(
          subpage => subpage.id === currentActivePageDetails?.id
        );
        if (subpageToUpdate) {
          subpageToUpdate.properties.title = value;
        }
      }
    }
    setMockPageContents(newState);
  };

  return (
    <div className={style.pageListingComponentParent}>
      {mode === "dragPage" ? (
        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="droppable" isDropDisabled={false} type="PAGE">
            {(provided, snapshot) => (
              <div
                {...provided.droppableProps}
                ref={provided.innerRef}
                style={{
                  minHeight: "300px",
                  background: snapshot.isDraggingOver ? "lightblue " : "white",
                }}
                className={style.pageListingComponentParent}
              >
                {mockPageContents.map((element, index) => (
                  <Draggable
                    key={element.id}
                    draggableId={element.id}
                    index={index}
                  >
                    {(draggableProvided: any) => (
                      <div
                        ref={draggableProvided.innerRef}
                        {...draggableProvided.draggableProps}
                        {...draggableProvided.dragHandleProps}
                        style={{
                          backgroundColor: "white",
                          ...draggableProvided.draggableProps.style,
                          marginBottom: "5px",
                        }}
                      >
                        <MockPageListItem
                          mode={mode}
                          key={element.id}
                          pageDetails={element}
                          activePageDetails={activePageDetails}
                          setActivePageDetails={setActivePageDetails}
                          setParentPage={setParentPage}
                          handlePageDelete={handlePageDelete}
                          onSubPageOrderChange={onSubPageOrderChange}
                          onEditChange={onEditChange}
                        />
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      ) : (
        <>
          {mockPageContents.map(element => (
            <MockPageListItem
              mode={mode}
              key={element.id}
              pageDetails={element}
              activePageDetails={activePageDetails}
              setActivePageDetails={setActivePageDetails}
              setParentPage={setParentPage}
              handlePageDelete={handlePageDelete}
              onSubPageOrderChange={onSubPageOrderChange}
              onEditChange={onEditChange}
            />
          ))}
        </>
      )}
    </div>
  );
};

export default MockPageListComponent;
