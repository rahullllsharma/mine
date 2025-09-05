import { useMemo, useState } from "react";
import { Draggable, Droppable } from "react-beautiful-dnd";
import {
  type ActivePageObjType,
  type PageType,
  type ModeTypePageSection,
  CWFItemType,
} from "../../customisedForm.types";
import style from "../createTemplateStyle.module.scss";
import DraggablePageListItem from "./ActionBasedPageListComponents/DraggablePageListItem";
import EditablePageListItem from "./ActionBasedPageListComponents/EditablePageListItem";

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
  setParentPage: (item: string) => void;
  mode: ModeTypePageSection;
  handlePageDelete: (details: PageDetails) => void;
  onSubPageOrderChange: boolean;
  onEditChange: (activePageDetails: ActivePageObjType, value: string) => void;
};

const MockPageListItem = ({
  pageDetails,
  activePageDetails,
  setActivePageDetails,
  setParentPage,
  mode,
  onSubPageOrderChange,
  onEditChange,
}: PageListItemProps) => {
  const [subPageIdArr, setSubPageIdArr] = useState<string[]>([pageDetails.id]);
  const extractSubPages = useMemo(() => {
    const allSubPagesList = pageDetails.contents.filter(
      element => element.type === CWFItemType.SubPage
    );
    const allIds = allSubPagesList.map(element => element.id);
    setSubPageIdArr(prev => [...prev, ...allIds]);
    return allSubPagesList;
  }, [pageDetails, onSubPageOrderChange]);

  return (
    <>
      {mode === "dragPage" ? (
        <div>
          <DraggablePageListItem
            activePageDetails={activePageDetails}
            pageDetails={pageDetails}
            setParentPage={setParentPage}
            setActivePageDetails={setActivePageDetails}
            type={"page"}
          />

          {subPageIdArr.includes(
            activePageDetails ? activePageDetails.id : ""
          ) && (
            <div className={style.pageListingComponentParent__subPagesSection}>
              <Droppable
                droppableId={pageDetails.id}
                isDropDisabled={false}
                type="SUB_PAGE"
              >
                {(provided, snapshot: any) => (
                  <div
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    style={{
                      background: snapshot.isDraggingOver
                        ? "lightblue "
                        : "white",
                      height: snapshot.isDraggingOver ? "200px" : "auto",
                    }}
                  >
                    {extractSubPages.map(
                      (subPageDetails: any, index: number) => (
                        <Draggable
                          key={subPageDetails.id}
                          draggableId={subPageDetails.id}
                          index={index}
                        >
                          {(draggableProvided: any) => (
                            <div
                              ref={draggableProvided.innerRef}
                              {...draggableProvided.draggableProps}
                              {...draggableProvided.dragHandleProps}
                              style={{
                                ...draggableProvided.draggableProps.style,
                                marginBottom: "5px",
                                background: "white",
                              }}
                            >
                              <DraggablePageListItem
                                activePageDetails={activePageDetails}
                                pageDetails={pageDetails}
                                setParentPage={setParentPage}
                                setActivePageDetails={setActivePageDetails}
                                type={"subPage"}
                                subPageDetails={subPageDetails}
                              />
                            </div>
                          )}
                        </Draggable>
                      )
                    )}
                  </div>
                )}
              </Droppable>
            </div>
          )}
        </div>
      ) : (
        <div>
          <EditablePageListItem
            activePageDetails={activePageDetails}
            pageDetails={pageDetails}
            setParentPage={setParentPage}
            setActivePageDetails={setActivePageDetails}
            type={"page"}
            onEditChange={onEditChange}
          />
          {subPageIdArr.includes(
            activePageDetails ? activePageDetails.id : ""
          ) && (
            <div className={style.pageListingComponentParent__subPagesSection}>
              {extractSubPages.map((subPageDetails: any) => (
                <EditablePageListItem
                  key={subPageDetails.id}
                  activePageDetails={activePageDetails}
                  pageDetails={pageDetails}
                  setParentPage={setParentPage}
                  setActivePageDetails={setActivePageDetails}
                  type={"subPage"}
                  subPageDetails={subPageDetails}
                  onEditChange={onEditChange}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default MockPageListItem;
