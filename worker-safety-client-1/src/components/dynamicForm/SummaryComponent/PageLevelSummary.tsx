import type {
  ActivePageObjType,
  FormComponentData,
  FormElement,
  FormType,
  LocationUserValueType,
} from "@/components/templatesComponents/customisedForm.types";
import { useState } from "react";
import { BodyText } from "@urbint/silica";
import { cloneDeep, isArray } from "lodash-es";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import SummaryAccordion from "./SummaryAccordion";
import { renderElementInSummary } from "./RenderElementsInSummary";

export const CWFComponentList = [
  CWFItemType.ActivitiesAndTasks,
  CWFItemType.SiteConditions,
  CWFItemType.HazardsAndControls,
  CWFItemType.PersonnelComponent,
  CWFItemType.Attachment,
  CWFItemType.Location,
  CWFItemType.NearestHospital,
];

export const isUserValueEmpty = (
  userValue: null | undefined | [] | string | LocationUserValueType,
  componentData?: FormComponentData,
  type?: string
) => {
  const {
    site_conditions,
    hazards_controls,
    location_data,
    activities_tasks,
    nearest_hospital,
  } = componentData ?? {};

  switch (type) {
    case CWFItemType.HazardsAndControls:
      return (
        !hazards_controls?.manually_added_hazards?.length &&
        !hazards_controls?.site_conditions?.length &&
        !hazards_controls?.tasks?.length
      );
    case CWFItemType.SiteConditions:
      return (
        !site_conditions?.length ||
        site_conditions.every(condition => !condition.selected)
      );
    case CWFItemType.Location:
      return !location_data?.name;
    case CWFItemType.ActivitiesAndTasks:
      return !activities_tasks?.length;
    case CWFItemType.NearestHospital:
      return !nearest_hospital?.name;
    case CWFItemType.RichTextEditor:
      return false;
    case CWFItemType.Summary:
      return false;
    case CWFItemType.YesOrNo:
      return false;
    default:
      return (
        userValue === null ||
        userValue === undefined ||
        !userValue ||
        (isArray(userValue) && userValue.length === 0) ||
        (typeof userValue === "string" && userValue === "") ||
        (typeof userValue === "object" &&
          userValue !== null &&
          "name" in userValue &&
          userValue.name === "")
      );
  }
};

export const hasAnyValidContent = (
  contents: FormElement[],
  formObject: FormType
): boolean => {
  return contents.some(item => {
    if (item.type === CWFItemType.Section && item.contents?.length) {
      return hasAnyValidContent(item.contents, formObject);
    }
    return !isUserValueEmpty(
      item.properties.user_value,
      formObject.component_data,
      item.type
    );
  });
};

export const renderContentOrEmptyMessage = (
  element: FormElement,
  activePageDetails: ActivePageObjType,
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

  return element.contents.map((contentItem, _index) => {
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
          <div className="p-4 mb-4 overflow-hidden transition-all duration-200 bg-brand-gray-10 rounded-md gap-4 flex flex-col">
            <div className="flex flex-row gap-1">
              <BodyText className="text-[20px] font-semibold">
                {contentItem.properties.title}
              </BodyText>
              {contentItem.type === CWFItemType.Attachment && (
                <BodyText className="text-[20px] font-semibold">
                  ({contentItem.properties.user_value.length})
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
                ({contentItem.properties.user_value.length})
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

    const renderedContent = renderElementInSummary(
      contentItemCopy,
      activePageDetails,
      element
    );

    if (renderedContent === undefined) {
      return null;
    }

    return (
      <div
        className="p-4 bg-brand-gray-10 rounded-md mb-4"
        key={contentItemCopy.id}
      >
        <div className="flex flex-col">{renderedContent}</div>
      </div>
    );
  });
};

const PageLevelSummary = ({
  element,
  activePageDetails,
  pageMap,
  setActivePageDetails,
  allFormPagesSaved,
  formObject,
}: {
  element: FormElement;
  activePageDetails: ActivePageObjType;
  pageMap: Record<string, string>;
  setActivePageDetails: (details: ActivePageObjType) => void;
  allFormPagesSaved: boolean;
  formObject: FormType;
}) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="flex flex-col w-full gap-2">
      <SummaryAccordion
        isOpen={isOpen}
        setIsOpen={setIsOpen}
        element={element}
        pageMap={pageMap}
        setActivePageDetails={setActivePageDetails}
        activePageDetails={activePageDetails}
        allFormPagesSaved={allFormPagesSaved}
        formObject={formObject}
      />

      {isOpen && (
        <div>
          {renderContentOrEmptyMessage(element, activePageDetails, formObject)}
        </div>
      )}
    </div>
  );
};

export default PageLevelSummary;
