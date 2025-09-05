import type {
  FormComponentData,
  SectionData,
  TemplateMetaData,
} from "@/components/templatesComponents/customisedForm.types";
import React from "react";
import { BodyText } from "@urbint/silica";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import {
  CWFComponentList,
  isUserValueEmpty,
} from "@/components/dynamicForm/SummaryComponent/PageLevelSummary";
import renderContent from "./CommonContent";

const Section = ({
  sectionContent,
  componentData,
  metaData,
  parentElement,
}: {
  sectionContent: SectionData;
  componentData: FormComponentData | undefined;
  metaData: TemplateMetaData | undefined;
  parentElement?: any;
}): JSX.Element | null => {
  if (
    !sectionContent?.contents ||
    !Array.isArray(sectionContent.contents) ||
    sectionContent.contents.length === 0
  ) {
    return null;
  }

  const hasAnyUserValue = sectionContent.contents.some((element: any) => {
    if (element?.type === CWFItemType.RichTextEditor) {
      return true;
    } else if (CWFComponentList.includes(element.type)) {
      return !isUserValueEmpty(
        element?.properties?.user_value,
        componentData,
        element.type
      );
    } else {
      const userValue = element?.properties?.user_value;
      if (Array.isArray(userValue)) {
        return userValue.length > 0;
      }
      return userValue !== null && userValue !== undefined && userValue !== "";
    }
  });

  if (!hasAnyUserValue) {
    return null;
  }

  const filterChildInstances = (parent: any, element: any) => {
    return (
      parent?.contents?.filter(
        (parentElementContent: any) =>
          parentElementContent.type === CWFItemType.Section &&
          parentElementContent.properties.child_instance &&
          parentElementContent.order === element.order
      ) || []
    );
  };

  const getRepeatableSectionTitle = (element: any, parent: any) => {
    let title = element.properties.title ?? "Section";

    if (element.properties.is_repeatable && parent) {
      const childInstances = filterChildInstances(parent, element);

      if (childInstances.length > 0) {
        title += ` (${childInstances.length})`;
      }
    }

    if (element.properties.child_instance && parent) {
      const siblingInstances = filterChildInstances(parent, element);

      const instanceIndex = siblingInstances.findIndex(
        (inst: any) => inst.id === element.id
      );
      if (instanceIndex !== -1) {
        title += ` (${instanceIndex + 1}/${siblingInstances.length})`;
      }
    }

    return title;
  };

  return (
    <>
      {sectionContent?.properties?.is_repeatable ? null : (
        <div className="flex flex-col py-4">
          <BodyText className="px-4 text-[20px] font-semibold">
            {getRepeatableSectionTitle(sectionContent, parentElement)}
          </BodyText>
          <div>
            {sectionContent?.contents?.map((element: any) => (
              <div key={element.id} className="flex flex-col -mb-4">
                {renderContent(
                  element,
                  componentData,
                  metaData,
                  sectionContent
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export default Section;
