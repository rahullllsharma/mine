import { useRef, useEffect, useState } from "react";
import { Icon } from "@urbint/silica";
import {
  CWFItemType,
  type ActivePageObjType,
  type PageType,
} from "@/components/templatesComponents/customisedForm.types";
import { StepItem } from "@/components/forms/Basic/StepItem";

type EditablePageListItemType = {
  activePageDetails: ActivePageObjType;
  pageDetails: PageType;
  setParentPage: (item: string) => void;
  setActivePageDetails: (item: ActivePageObjType) => void;
  type: string;
  subPageDetails?: PageType;
  onEditChange: (activePageDetails: ActivePageObjType, value: string) => void;
};

const InputBox = ({
  details,
  onEditChange,
  activePageDetails,
}: {
  details: PageType | null;
  onEditChange: (activePageDetails: ActivePageObjType, value: string) => void;
  activePageDetails: ActivePageObjType;
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [inputState, setInputState] = useState(details?.properties.title);
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  return details ? (
    <div className="relative p-3 flex w-full items-center text-base font-normal text-neutral-shade-100 rounded-md border border-solid lg:flex  border-neutral-shade-26 rounded-md focus-within:ring-1 focus-within:ring-brand-gray-60 bg-neutral-light-100">
      <Icon
        name="circle"
        className="text-neutral-shade-58 border-2 border-transparent box-border"
      />

      <input
        type="text"
        ref={inputRef}
        placeholder="Page Title"
        value={inputState}
        onChange={e => {
          setInputState(e.target.value);
          onEditChange(activePageDetails, e.target.value);
        }}
        className="flex-auto rounded-md appearance-none focus:outline-none disabled:bg-neutral-light-77 read-only:cursor-default disabled:cursor-not-allowed disabled:opacity-38 min-w-0 pl-2"
      />
    </div>
  ) : null;
};

const EditablePageListItem = ({
  activePageDetails,
  pageDetails,
  setParentPage,
  setActivePageDetails,
  type,
  subPageDetails,
  onEditChange,
}: EditablePageListItemType) => {
  return (
    <div className="relative">
      {type === CWFItemType.Page ? (
        <>
          {activePageDetails?.id === pageDetails.id ? (
            <InputBox
              details={pageDetails}
              onEditChange={onEditChange}
              activePageDetails={activePageDetails}
            />
          ) : (
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
          )}
        </>
      ) : (
        <>
          {activePageDetails?.id === subPageDetails?.id ? (
            <InputBox
              details={subPageDetails || null}
              onEditChange={onEditChange}
              activePageDetails={activePageDetails}
            />
          ) : (
            <StepItem
              status={
                activePageDetails?.id === subPageDetails?.id
                  ? "current"
                  : "default"
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
        </>
      )}
    </div>
  );
};

export default EditablePageListItem;
