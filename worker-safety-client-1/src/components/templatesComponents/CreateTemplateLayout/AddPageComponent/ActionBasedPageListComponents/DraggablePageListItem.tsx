import { Icon } from "@urbint/silica";
import {
  CWFItemType,
  type ActivePageObjType,
  type PageType,
} from "@/components/templatesComponents/customisedForm.types";
import { StepItem } from "@/components/forms/Basic/StepItem";

type DraggablePageListItemType = {
  activePageDetails: ActivePageObjType;
  pageDetails: PageType;
  setParentPage: (item: string) => void;
  setActivePageDetails: (item: ActivePageObjType) => void;
  type: string;
  subPageDetails?: PageType;
};

const DraggablePageListItem = ({
  activePageDetails,
  pageDetails,
  setParentPage,
  setActivePageDetails,
  type,
  subPageDetails,
}: DraggablePageListItemType) => {
  return (
    <div className="relative">
      <div
        className="absolute"
        style={{
          top: "9px",
          left: "13px",
          fontSize: "22px",
          background: "whitesmoke",
        }}
      >
        <Icon name="grid_vertical_round" />
      </div>
      {type === CWFItemType.Page ? (
        <StepItem
          status={
            activePageDetails?.id === pageDetails.id ? "current" : "default"
          }
          label={pageDetails.properties.title}
          onClick={() => {
            setParentPage(pageDetails.id);
            setActivePageDetails({
              id: pageDetails.id,
              parentId: "root",
              type: CWFItemType.Page,
            });
          }}
        />
      ) : (
        <StepItem
          status={
            activePageDetails?.id === subPageDetails?.id ? "current" : "default"
          }
          label={subPageDetails?.properties.title || ""}
          onClick={() => {
            setActivePageDetails({
              id: subPageDetails?.id || "",
              parentId: pageDetails?.id,
              type: CWFItemType.SubPage,
            });
          }}
        />
      )}
    </div>
  );
};

export default DraggablePageListItem;
