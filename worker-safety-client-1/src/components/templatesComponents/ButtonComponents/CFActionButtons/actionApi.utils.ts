import type { FormType, PageType } from "../../customisedForm.types";
import { CWFItemType } from "../../customisedForm.types";

export function hasContentForSummary(formData: FormType | undefined): boolean {
  if (!formData) {
    return false;
  }
  // Check if pages have include_in_summary = true
  const hasPageWithSummary = formData.contents.some(
    page => page.properties && page.properties.include_in_summary === true
  );

  if (hasPageWithSummary) {
    return true;
  }

  // Check all nested contents recursively
  function checkNestedContents(contents: PageType[]) {
    if (!contents || !Array.isArray(contents)) {
      return false;
    }

    for (const item of contents) {
      // Check if the current item has include_in_summary = true
      if (item.properties && item.properties.include_in_summary === true) {
        return true;
      }

      // Check sub-pages
      if (
        item.type === CWFItemType.SubPage &&
        item.properties &&
        item.properties.include_in_summary === true
      ) {
        return true;
      }

      // Check sections, components, etc.
      if (
        item.type === CWFItemType.Section ||
        item.type === CWFItemType.HazardsAndControls ||
        item.type === CWFItemType.ActivitiesAndTasks
      ) {
        if (item.properties && item.properties.include_in_summary === true) {
          return true;
        }
      }

      // Recursively check contents of this item
      if (Array.isArray(item.contents) && checkNestedContents(item.contents)) {
        return true;
      }
    }

    return false;
  }

  // Check all nested elements
  return checkNestedContents(formData.contents);
}

export function checkTemplateWithOnlySummary(
  formData: FormType | undefined
): boolean {
  if (!formData) {
    return false;
  }

  if (formData.contents.length !== 1) {
    return false;
  }

  const page = formData.contents[0];

  if (!page.contents || page.contents.length !== 1) {
    return false;
  }

  const content = page.contents[0];

  if (content.type === CWFItemType.Summary) {
    return true;
  }

  if (content.type === CWFItemType.Section) {
    if (!content.contents || content.contents.length !== 1) {
      return false;
    }

    return content.contents[0].type === CWFItemType.Summary;
  }

  return false;
}
