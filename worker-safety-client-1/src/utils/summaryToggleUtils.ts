/**
 * Utility functions for managing "Include in Summary" toggle functionality
 * across form components in the template builder.
 */

import type {
  FormElementsType,
  PageType,
} from "@/components/templatesComponents/customisedForm.types";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";

/**
 * Interface for summary toggle state analysis
 */
interface SummaryToggleAnalysis {
  totalComponents: number;
  includedComponents: number;
  hasAnyIncluded: boolean;
  allIncluded: boolean;
}

/**
 * Configuration for components that should be excluded from summary toggle operations
 */
const EXCLUDED_COMPONENT_TYPES = new Set([
  CWFItemType.Page,
  CWFItemType.SubPage,
  CWFItemType.Summary,
]);

/**
 * Recursively analyzes all components in the form to determine summary inclusion state
 *
 * @param items - Array of form elements to analyze
 * @returns Analysis object containing component counts and inclusion states
 */
export const analyzeSummaryToggleState = (
  items: FormElementsType[]
): SummaryToggleAnalysis => {
  let totalComponents = 0;
  let includedComponents = 0;

  const processComponentsRecursively = (
    components: FormElementsType[]
  ): void => {
    for (const component of components) {
      // Skip excluded component types
      if (EXCLUDED_COMPONENT_TYPES.has(component.type as CWFItemType)) {
        // Still process nested contents for excluded types
        if (component.contents?.length > 0) {
          processComponentsRecursively(component.contents);
        }
        continue;
      }

      totalComponents++;

      if (component.properties?.include_in_summary === true) {
        includedComponents++;
      }

      // Recursively process nested contents
      if (component.contents?.length > 0) {
        processComponentsRecursively(component.contents);
      }
    }
  };

  processComponentsRecursively(items);

  return {
    totalComponents,
    includedComponents,
    hasAnyIncluded: includedComponents > 0,
    allIncluded: totalComponents > 0 && includedComponents === totalComponents,
  };
};

/**
 * Determines the master toggle state based on current form content
 *
 * @param formContents - Array of pages in the form
 * @returns True if any components are included in summary, false otherwise
 */
export const getMasterToggleState = (formContents: PageType[]): boolean => {
  if (!formContents?.length) return false;

  const analysis = analyzeSummaryToggleState(formContents);
  return analysis.hasAnyIncluded;
};

/**
 * Recursively updates all eligible components with the specified summary inclusion state
 *
 * @param components - Array of components to update
 * @param includeInSummary - New state to apply
 * @param updateCallback - Function called for each component that needs updating
 */
export const updateComponentsSummaryState = (
  components: FormElementsType[],
  includeInSummary: boolean,
  updateCallback: (
    component: FormElementsType,
    parentSection?: FormElementsType
  ) => void
): void => {
  const processComponent = (
    component: FormElementsType,
    parentSection?: FormElementsType
  ): void => {
    // Skip excluded component types
    if (EXCLUDED_COMPONENT_TYPES.has(component.type as CWFItemType)) {
      // Still process nested contents for excluded types
      if (component.contents?.length > 0) {
        for (const nestedComponent of component.contents) {
          processComponent(nestedComponent, component);
        }
      }
      return;
    }

    // Update the component
    updateCallback(component, parentSection);

    // Process nested components if this is a section
    if (
      component.type === CWFItemType.Section &&
      component.contents?.length > 0
    ) {
      for (const nestedComponent of component.contents) {
        processComponent(nestedComponent, component);
      }
    }
  };

  for (const component of components) {
    processComponent(component);
  }
};

/**
 * Checks if any components in the provided array are included in summary
 * Used for page-level summary toggle state determination
 *
 * @param components - Array of components to check
 * @returns True if any component has include_in_summary set to true
 */
export const hasAnyComponentsIncludedInSummary = (
  components: FormElementsType[]
): boolean => {
  if (!components?.length) return false;
  return analyzeSummaryToggleState(components).hasAnyIncluded;
};
