import type {
  PageContentType,
  AllQuestionTypes,
  SectionQuestionHolder,
  userValueForQuestionsType,
  SubPageContentType,
  PageType,
  ActivePageType,
} from "@/components/templatesComponents/customisedForm.types";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";

type FieldValueChangeData = {
  user_value: userValueForQuestionsType;
  order: number;
};
type FieldCommentData = { comment: string; order: number };
type FieldAttachmentsData = { attachments: File[]; order: number };

type FieldData = FieldValueChangeData | FieldCommentData | FieldAttachmentsData;

export const updateContentProperties = (
  content: AllQuestionTypes | PageContentType | SubPageContentType,
  fieldData: FieldData,
  actionType: string
) => {
  if (content.order === fieldData.order) {
    if (actionType === CF_REDUCER_CONSTANTS.FIELD_VALUE_CHANGE) {
      const typedFieldData = fieldData as FieldValueChangeData;
      return {
        ...content,
        properties: {
          ...content.properties,
          user_value: typedFieldData.user_value,
        },
      };
    } else if (actionType === CF_REDUCER_CONSTANTS.ADD_FIELD_COMMENT) {
      const typedFieldData = fieldData as FieldCommentData;
      return {
        ...content,
        properties: {
          ...content.properties,
          user_comments: typedFieldData.comment,
        },
      };
    } else if (actionType === CF_REDUCER_CONSTANTS.ADD_FIELD_ATTACHMENTS) {
      const typedFieldData = fieldData as FieldAttachmentsData;
      return {
        ...content,
        properties: {
          ...content.properties,
          user_attachments: typedFieldData.attachments,
        },
      };
    }
  }
  return content;
};

export const updateSectionContents = (
  pageContent: PageContentType,
  section: SectionQuestionHolder | null,
  fieldData: FieldData,
  actionType: string
) => {
  if (
    pageContent.type === CWFItemType.Section &&
    pageContent.id === section?.id
  ) {
    return {
      ...pageContent,
      contents: pageContent.contents.map(content =>
        updateContentProperties(content, fieldData, actionType)
      ),
    };
  }
  return pageContent;
};

export const updatePageContents = (
  page: PageType,
  parentData: ActivePageType,
  section: SectionQuestionHolder | null,
  fieldData: FieldData,
  actionType: string
) => {
  if (page.id === parentData.id) {
    return {
      ...page,
      contents: section
        ? page.contents.map(pageContent =>
            updateSectionContents(pageContent, section, fieldData, actionType)
          )
        : page.contents.map(content =>
            updateContentProperties(content, fieldData, actionType)
          ),
    };
  }
  return page;
};

export const updateSubPageContents = (
  pageContent: PageContentType,
  parentData: ActivePageType,
  section: SectionQuestionHolder | null,
  fieldData: FieldData,
  actionType: string
): PageContentType => {
  if (
    pageContent.type === CWFItemType.SubPage &&
    pageContent.id === parentData.id
  ) {
    return {
      ...pageContent,
      contents: section
        ? pageContent.contents.map(subPageContent =>
            updateSectionContents(
              subPageContent,
              section,
              fieldData,
              actionType
            )
          )
        : pageContent.contents.map(content =>
            updateContentProperties(content, fieldData, actionType)
          ),
    };
  }
  return pageContent;
};

export const updatePages = (
  page: PageType,
  parentData: ActivePageType,
  section: SectionQuestionHolder | null,
  fieldData: FieldData,
  actionType: string
): PageType => {
  if (page.id === parentData.parentId) {
    return {
      ...page,
      contents: page.contents.map(pageContent =>
        updateSubPageContents(
          pageContent,
          parentData,
          section,
          fieldData,
          actionType
        )
      ),
    };
  }
  return page;
};

export const calculatePrePopulationPath = (
  formContents: PageType[],
  parentIds: string[] = []
): Record<string, string[]> | null => {
  const result: Record<string, string[]> = {};

  formContents.forEach(
    (
      formContentElement: PageType | AllQuestionTypes | SectionQuestionHolder
    ) => {
      const currentIds = [...parentIds, formContentElement.id];

      if (
        "pre_population_rule_name" in formContentElement.properties &&
        formContentElement.properties.pre_population_rule_name &&
        formContentElement.properties.pre_population_rule_name != "None"
      ) {
        const ruleName = formContentElement.properties.pre_population_rule_name;
        const path = currentIds.join("/");

        if (!result[ruleName]) {
          result[ruleName] = [];
        }

        result[ruleName].push(path);
      }

      if ("contents" in formContentElement && formContentElement.contents) {
        const nestedResult = calculatePrePopulationPath(
          formContentElement.contents as PageType[],
          currentIds
        );

        for (const [key, paths] of Object.entries(nestedResult || {})) {
          if (!result[key]) {
            result[key] = [];
          }
          result[key] = result[key].concat(paths);
        }
      }
    }
  );

  return Object.keys(result).length === 0 ? null : result;
};
