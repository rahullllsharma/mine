import type {
  FormType,
  FormElement,
} from "@/components/templatesComponents/customisedForm.types";
import { useRouter } from "next/router";
import useRestQuery from "@/hooks/useRestQuery";
import axiosRest from "@/api/customFlowApi";
import CSFLoader from "@/components/templatesComponents/LoaderComponent/CSFLoader";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import PageHeader from "./components/PageHeader";
import RenderSharePageWithAccordion from "./RenderSharePageWithAccordion";

const TemplateSharePage = () => {
  const {
    query: { id },
  } = useRouter();

  const { data, isLoading } = useRestQuery<FormType>({
    key: [`data-${id}`],
    endpoint: `/forms/${id}`,
    axiosConfig: {},
    axiosInstance: axiosRest,
    queryOptions: {
      enabled: !!id,
      staleTime: 0,
      cacheTime: 0,
    },
  });

  if (isLoading) {
    return <CSFLoader />;
  }

  if (!data?.contents) {
    return <></>;
  }

  const getElementsToRender = (
    contents: Array<FormElement>,
    isParentIncludedInSummary = false
  ): Array<FormElement> => {
    if (!contents || !Array.isArray(contents)) return [];

    let summaryElements: Array<FormElement> = [];

    // First, collect just the main elements (not going into their children yet)
    contents.forEach(element => {
      // Check if this element should be included in summary
      const isElementMarkedForSummary =
        element.properties?.include_in_summary === true;

      // Special handling for historical incidents - only for summary components
      const hasHistoricalIncident =
        element.type === "summary" &&
        element.properties?.historical_incident?.label;

      const shouldIncludeElement =
        isElementMarkedForSummary ||
        hasHistoricalIncident ||
        // Include elements from subpages that are marked for summary
        (isParentIncludedInSummary &&
          element.type !== CWFItemType.Page &&
          element.type !== CWFItemType.SubPage);

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
            // Only add if parent is marked for summary, if child itself is marked, or if child is a summary component with historical incident data
            if (
              isElementMarkedForSummary ||
              child.properties?.include_in_summary === true ||
              (child.type === "summary" &&
                child.properties?.historical_incident?.label)
            ) {
              summaryElements.push(child);
            }
          });

          // After adding direct children, process any nested subpages
          const nestedSubpages = element.contents.filter(
            child => child.type === CWFItemType.SubPage
          );

          if (nestedSubpages.length > 0) {
            const nestedElements = getElementsToRender(
              nestedSubpages,
              isElementMarkedForSummary
            );
            summaryElements = [...summaryElements, ...nestedElements];
          }
        }
        // For non-page elements with contents (like sections), process them recursively
        else if (element.contents && Array.isArray(element.contents)) {
          const childElements = getElementsToRender(
            element.contents,
            isElementMarkedForSummary || isParentIncludedInSummary
          );

          summaryElements = [...summaryElements, ...childElements];
        }
      }
      // Handle elements not marked for summary but might have children that are
      else if (element.contents && Array.isArray(element.contents)) {
        const childElements = getElementsToRender(
          element.contents,
          isParentIncludedInSummary
        );

        if (childElements.length > 0) {
          summaryElements = [...summaryElements, ...childElements];
        }
      }
    });

    summaryElements = summaryElements.filter(
      item => item.type === CWFItemType.Page
    );

    return summaryElements;
  };

  const getElements = getElementsToRender(data?.contents, false);

  return (
    <div className="flex bg-brand-gray-10 flex-col gap-4 overflow-auto">
      <PageHeader
        title={data?.properties.title}
        status={data?.properties.status}
      />
      <div className="flex flex-col bg-white p-4 gap-4 pb-[120px] max-w-[800px] w-full self-center">
        {getElements.map(element => {
          return (
            <div key={element.id}>
              <RenderSharePageWithAccordion
                element={element}
                formObject={data}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TemplateSharePage;
