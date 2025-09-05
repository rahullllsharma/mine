import type {
  FormElement,
  FormType,
} from "@/components/templatesComponents/customisedForm.types";
import { useState } from "react";
import { BodyText } from "@urbint/silica";
import { cloneDeep } from "lodash-es";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import {
  CWFComponentList,
  hasAnyValidContent,
  isUserValueEmpty,
} from "@/components/dynamicForm/SummaryComponent/PageLevelSummary";
import RenderAccordion from "../RenderAccordion";
import renderContent from "./components/CommonContent";

const renderContentOrEmptyMessage = (
  element: FormElement,
  formObject: FormType
) => {
  if (!element.contents || element.contents.length === 0) {
    return (
      <div
        className="p-4 overflow-hidden transition-all duration-200 bg-brand-gray-10 rounded-md"
        key={`${element.id}-empty`}
      >
        <div className="text-neutral-shade-58">No information provided</div>
      </div>
    );
  }

  const hasValidContent = hasAnyValidContent(element.contents, formObject);

  if (
    !hasValidContent &&
    element.contents.every(item => !CWFComponentList.includes(item.type))
  ) {
    return (
      <div
        className="p-4 overflow-hidden transition-all duration-200 bg-brand-gray-10 rounded-md"
        key={`${element.id}-empty`}
      >
        <div className="text-neutral-shade-58">No information provided</div>
      </div>
    );
  }

  return element.contents.map(contentItem => {
    const contentItemCopy = cloneDeep(contentItem);
    const isUserValueEmptyForItem = isUserValueEmpty(
      contentItem.properties.user_value,
      formObject.component_data,
      contentItem.type
    );
    if (
      contentItem.type === CWFItemType.Section &&
      !contentItem.properties.is_repeatable
    ) {
      const emptyContentTitles: string[] = [];

      for (let i = contentItem.contents.length - 1; i >= 0; i--) {
        const item = contentItem.contents[i];
        if (
          isUserValueEmpty(
            item.properties.user_value,
            formObject.component_data,
            item.type
          )
        ) {
          if (CWFComponentList.includes(item.type) && item.properties.title) {
            const title =
              item.type === CWFItemType.Attachment &&
              item.properties.user_value &&
              Array.isArray(item.properties.user_value)
                ? `${item.properties.title} (${item.properties.user_value.length})`
                : item.properties.title;
            emptyContentTitles.push(title);
          }
          contentItemCopy.contents.splice(i, 1);
        }
      }

      if (contentItemCopy.contents.length === 0) {
        return (
          <div
            className="p-4 mb-4 overflow-hidden transition-all duration-200 bg-brand-gray-10 rounded-md gap-4 flex flex-col"
            key={`${contentItem.id}-empty`}
          >
            <div className="flex flex-row gap-1">
              <BodyText className="text-[20px] font-semibold">
                {contentItem.properties.title}
              </BodyText>
              {contentItem.type === CWFItemType.Attachment && (
                <BodyText className="text-[20px] font-semibold">
                  ({contentItem.properties.user_value?.length || 0})
                </BodyText>
              )}
            </div>
            {emptyContentTitles.length > 0 && (
              <div className="flex flex-col gap-1">
                {emptyContentTitles.map((title, index) => (
                  <BodyText key={index} className="text-[20px] font-semibold">
                    {title}
                  </BodyText>
                ))}
              </div>
            )}
            <BodyText className="text-neutral-shade-58">
              No information provided
            </BodyText>
          </div>
        );
      }
    } else if (
      CWFComponentList.includes(contentItem.type) &&
      isUserValueEmptyForItem
    ) {
      return (
        <div
          className="p-4 mb-4 overflow-hidden transition-all duration-200 bg-brand-gray-10 rounded-md gap-4 flex flex-col"
          key={`${contentItem.id}-empty`}
        >
          <div className="flex flex-row gap-1">
            <BodyText className="text-[20px] font-semibold">
              {contentItem.properties.title}
            </BodyText>
            {contentItem.type === CWFItemType.Attachment && (
              <BodyText className="text-[20px] font-semibold">
                ({contentItem.properties.user_value?.length || 0})
              </BodyText>
            )}
          </div>
          <BodyText className="text-neutral-shade-58">
            No information provided
          </BodyText>
        </div>
      );
    } else if (isUserValueEmptyForItem) {
      return null;
    }

    const renderedContent = renderContent(
      contentItemCopy,
      formObject.component_data,
      formObject.metadata,
      element
    );

    if (renderedContent === undefined) {
      return null;
    }

    return (
      <div
        className="bg-brand-gray-10 mb-2 rounded-lg"
        key={contentItemCopy.id}
      >
        {renderedContent}
      </div>
    );
  });
};

const RenderSharePageWithAccordion = ({
  element,
  formObject,
}: {
  element: FormElement;
  formObject: FormType;
}) => {
  const [isAccordionOpen, setIsAccordionOpen] = useState(true);

  return (
    <div className="flex flex-col w-full gap-2">
      <RenderAccordion
        isOpen={isAccordionOpen}
        setIsOpen={setIsAccordionOpen}
        element={element}
      />

      {isAccordionOpen && (
        <>{renderContentOrEmptyMessage(element, formObject)}</>
      )}
    </div>
  );
};

export default RenderSharePageWithAccordion;
