import type {
  ActivePageObjType,
  CWFSummaryType,
  FormElement,
  PageType,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import { DateTime } from "luxon";
import { BodyText, SectionHeading } from "@urbint/silica";
import {
  CWFItemType,
  UserFormModeTypes,
} from "@/components/templatesComponents/customisedForm.types";
import { useFormRendererContext } from "@/components/templatesComponents/FormPreview/Components/FormRendererContext";
import HistoricalIncident from "../HistoricalIncident/HistoricalIncident";
import { SummaryTextedBlankField } from "./utils";
import PageLevelSummary from "./PageLevelSummary";

const CWFSummary = ({
  item,
  activePageDetails,
  showTextedBlankFieldForSummary,
  mode,
}: {
  item: CWFSummaryType;
  activePageDetails: ActivePageObjType;
  showTextedBlankFieldForSummary?: boolean;
  mode: UserFormMode;
}): JSX.Element => {
  const { formObject, setActivePageDetails } = useFormRendererContext();
  const state = { form: formObject };

  if (!state?.form?.contents) {
    return <></>;
  }
  const pageMap: Record<string, string> = {};

  // Function to check if all pages before the summary page are complete
  const areAllPreviousPagesComplete = (): boolean => {
    if (!state.form.contents || !Array.isArray(state.form.contents))
      return false;
    if (!activePageDetails) return false;

    // Assuming the pages are ordered and the summary page is somewhere in the list
    // Find summary page index
    const summaryPageIndex = state.form.contents.findIndex(
      page => page.id === activePageDetails.id
    );

    if (summaryPageIndex <= 0) return true; // No previous pages or invalid summary page

    // Check if all previous pages have "saved" status
    for (let i = 0; i < summaryPageIndex; i++) {
      const page = state.form.contents[i] as PageType;
      if (page.properties?.page_update_status !== "saved") {
        return false;
      }

      // Also check subpages if they exist
      if (page.contents && Array.isArray(page.contents)) {
        const subpages = page.contents.filter(
          content => content.type === CWFItemType.SubPage
        );

        for (const subpage of subpages) {
          if (subpage.properties?.page_update_status !== "saved") {
            return false;
          }
        }
      }
    }

    return true;
  };

  const isAtLeastOnePageCompleted = (): boolean => {
    if (!state.form.contents || !Array.isArray(state.form.contents))
      return false;

    const isPageOrSubpagesSaved = (page: PageType): boolean => {
      if (page.properties?.page_update_status === "saved") {
        return true;
      }

      if (page.contents && Array.isArray(page.contents)) {
        const subpages = page.contents.filter(
          content => content.type === CWFItemType.SubPage
        );

        for (const subpage of subpages) {
          if (subpage.properties?.page_update_status === "saved") {
            return true;
          }
        }
      }

      return false;
    };

    for (const page of state.form.contents) {
      if (isPageOrSubpagesSaved(page as PageType)) {
        return true;
      }
    }

    return false;
  };

  // Function to check if all pages in the form are saved
  const isFormFullySaved = (): boolean => {
    if (!state.form.contents || !Array.isArray(state.form.contents))
      return false;

    // Helper function to check if a page and all its subpages are saved
    const isPageAndSubpagesSaved = (page: PageType): boolean => {
      if (page.properties?.page_update_status !== "saved") {
        return false;
      }

      // Check subpages if they exist
      if (page.contents && Array.isArray(page.contents)) {
        const subpages = page.contents.filter(
          content => content.type === CWFItemType.SubPage
        );

        for (const subpage of subpages) {
          if (subpage.properties?.page_update_status !== "saved") {
            return false;
          }
        }
      }

      return true;
    };

    // Check all pages
    for (const page of state.form.contents) {
      if (!isPageAndSubpagesSaved(page as PageType)) {
        return false;
      }
    }

    return true;
  };

  const allFormPagesSaved = isFormFullySaved();
  const atLeastOnePageCompleted = isAtLeastOnePageCompleted();

  const getSummaryElements = (
    contents: Array<FormElement>,
    parentPageId?: string,
    isParentIncludedInSummary = false
  ): Array<FormElement> => {
    if (!contents || !Array.isArray(contents)) return [];

    let summaryElements: Array<FormElement> = [];

    // First, collect just the main elements (not going into their children yet)
    contents.forEach(element => {
      // If current element is a page, it becomes the parent page for its children
      const currentParentPageId =
        element.type === CWFItemType.Page ||
        element.type === CWFItemType.SubPage
          ? element.id
          : parentPageId;

      // Track the parent page for this element
      if (currentParentPageId) {
        pageMap[element.id] = currentParentPageId;
      }

      // Check if this element should be included in summary
      const isElementMarkedForSummary =
        element.properties?.include_in_summary === true;

      const shouldIncludeElement =
        element.properties?.page_update_status === "saved" &&
        (isElementMarkedForSummary ||
          // Include elements from subpages that are marked for summary
          (isParentIncludedInSummary &&
            element.type !== CWFItemType.Page &&
            element.type !== CWFItemType.SubPage));

      if (shouldIncludeElement) {
        // First add the parent element
        summaryElements.push(element);

        // For pages and subpages with content, process their contents immediately after
        if (
          (element.type === CWFItemType.Page ||
            element.type === CWFItemType.SubPage) &&
          element.contents &&
          Array.isArray(element.contents) &&
          element.contents.length > 0
        ) {
          // Process non-page child elements first (fields, sections, etc.)
          const directChildElements = element.contents.filter(
            child =>
              child.type !== CWFItemType.Page &&
              child.type !== CWFItemType.SubPage
          );

          // Mark these children for proper parent attribution
          directChildElements.forEach(child => {
            pageMap[child.id] = element.id;

            if (child.properties?.include_in_summary === true) {
              summaryElements.push(child);
            }
          });

          // After adding direct children, process any nested subpages
          const nestedSubpages = element.contents.filter(
            child => child.type === CWFItemType.SubPage
          );

          if (nestedSubpages.length > 0) {
            const nestedElements = getSummaryElements(
              nestedSubpages,
              currentParentPageId,
              isElementMarkedForSummary
            );
            summaryElements = [...summaryElements, ...nestedElements];
          }
        }
        // For non-page elements with contents (like sections), process them recursively
        else if (element.contents && Array.isArray(element.contents)) {
          const childElements = getSummaryElements(
            element.contents,
            currentParentPageId,
            isElementMarkedForSummary || isParentIncludedInSummary
          );

          summaryElements = [...summaryElements, ...childElements];
        }
      }
      // Handle elements not marked for summary but might have children that are
      else if (element.contents && Array.isArray(element.contents)) {
        const childElements = getSummaryElements(
          element.contents,
          currentParentPageId,
          isParentIncludedInSummary
        );

        if (childElements.length > 0) {
          summaryElements = [...summaryElements, ...childElements];
        }
      }
    });

    // Only include elements of type Page in the summaryElements
    summaryElements = summaryElements.filter(
      el => el.type === CWFItemType.Page
    );

    return summaryElements;
  };

  // Get all elements that should be included in the summary
  const summaryElements = getSummaryElements(
    state.form.contents,
    undefined,
    false
  );
  const allPreviousPagesComplete = areAllPreviousPagesComplete();

  const handleLastUpdatedDate = () => {
    return formObject.updated_at
      ? DateTime.fromISO(formObject.updated_at, { zone: "utc" })
          .toLocal()
          .toLocaleString({
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
          })
      : "";
  };

  return (
    <div className="flex justify-between flex-col gap-4">
      <SectionHeading className="text-xl text-neutral-shade-100 font-semibold">
        {item.properties.title ?? "Summary"}
      </SectionHeading>
      {mode !== UserFormModeTypes.BUILD && atLeastOnePageCompleted && (
        <BodyText>Last Updated: {handleLastUpdatedDate()}</BodyText>
      )}
      {mode !== UserFormModeTypes.BUILD && allPreviousPagesComplete ? (
        showTextedBlankFieldForSummary ? (
          <SummaryTextedBlankField />
        ) : (
          <>
            {summaryElements.length > 0 ? (
              summaryElements.map(element => (
                <div key={element.id}>
                  <PageLevelSummary
                    element={element}
                    activePageDetails={activePageDetails}
                    pageMap={pageMap}
                    setActivePageDetails={setActivePageDetails}
                    allFormPagesSaved={allFormPagesSaved}
                    formObject={formObject}
                  />
                </div>
              ))
            ) : (
              <div className="text-neutral-shade-58">
                No items to display in summary.
              </div>
            )}
            {item.properties?.historical_incident?.label && (
              <HistoricalIncident
                label={item.properties?.historical_incident?.label}
                componentId={item.id}
                readOnly={
                  mode === UserFormModeTypes.PREVIEW ||
                  mode === UserFormModeTypes.PREVIEW_PROPS
                }
              />
            )}
          </>
        )
      ) : (
        <div className="flex flex-col items-center sm:flex-row gap-2 sm:gap-4 p-2 sm:p-4 bg-gray-100 h-24 sm:h-32 w-full mt-5">
          <BodyText className="text-neutrals-secondary">
            Complete required information in previous sections to display this
            content.
          </BodyText>
        </div>
      )}
    </div>
  );
};

export default CWFSummary;
