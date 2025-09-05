import type {
  FormElementsType,
  PageType,
} from "@/components/templatesComponents/customisedForm.types";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import {
  updateComponentsSummaryState,
  getMasterToggleState,
  hasAnyComponentsIncludedInSummary,
} from "./summaryToggleUtils";

describe("summaryToggleUtils", () => {
  describe("updateComponentsSummaryState", () => {
    it("should update components inside sections correctly", () => {
      const updatedComponents: FormElementsType[] = [];
      const updateCallback = (component: FormElementsType) => {
        updatedComponents.push(component);
      };

      const components: FormElementsType[] = [
        {
          id: "section1",
          type: CWFItemType.Section,
          order: 1,
          properties: {
            title: "Test Section",
            include_in_summary: false,
          },
          contents: [
            {
              id: "field1",
              type: "input_text",
              order: 1,
              properties: {
                title: "Field 1",
                include_in_summary: false,
              },
            },
            {
              id: "field2",
              type: "choice",
              order: 2,
              properties: {
                title: "Field 2",
                include_in_summary: false,
              },
            },
          ],
        },
      ];

      updateComponentsSummaryState(components, true, updateCallback);

      // Should update the section and both nested components
      expect(updatedComponents).toHaveLength(3);
      expect(updatedComponents[0].id).toBe("section1");
      expect(updatedComponents[1].id).toBe("field1");
      expect(updatedComponents[2].id).toBe("field2");
    });

    it("should handle nested sections correctly", () => {
      const updatedComponents: FormElementsType[] = [];
      const updateCallback = (component: FormElementsType) => {
        updatedComponents.push(component);
      };

      const components: FormElementsType[] = [
        {
          id: "section1",
          type: CWFItemType.Section,
          order: 1,
          properties: {
            title: "Outer Section",
            include_in_summary: false,
          },
          contents: [
            {
              id: "field1",
              type: "input_text",
              order: 1,
              properties: {
                title: "Field 1",
                include_in_summary: false,
              },
            },
            {
              id: "section2",
              type: CWFItemType.Section,
              order: 2,
              properties: {
                title: "Inner Section",
                include_in_summary: false,
              },
              contents: [
                {
                  id: "field2",
                  type: "choice",
                  order: 1,
                  properties: {
                    title: "Field 2",
                    include_in_summary: false,
                  },
                },
              ],
            },
          ],
        },
      ];

      updateComponentsSummaryState(components, true, updateCallback);

      // Should update: outer section, field1, inner section, field2
      expect(updatedComponents).toHaveLength(4);
      expect(updatedComponents[0].id).toBe("section1");
      expect(updatedComponents[1].id).toBe("field1");
      expect(updatedComponents[2].id).toBe("section2");
      expect(updatedComponents[3].id).toBe("field2");
    });
  });

  describe("getMasterToggleState", () => {
    it("should return true when any component is included in summary", () => {
      const formContents: PageType[] = [
        {
          id: "page1",
          type: CWFItemType.Page,
          order: 1,
          properties: {
            title: "Page 1",
            description: "Test page",
            page_update_status: "default" as const,
            include_in_summary: false,
          },
          contents: [
            {
              id: "field1",
              type: "input_text",
              order: 1,
              properties: {
                title: "Field 1",
                include_in_summary: true, // This should make getMasterToggleState return true
              },
            },
          ],
        },
      ];

      expect(getMasterToggleState(formContents)).toBe(true);
    });

    it("should return false when no components are included in summary", () => {
      const formContents: PageType[] = [
        {
          id: "page1",
          type: CWFItemType.Page,
          order: 1,
          properties: {
            title: "Page 1",
            description: "Test page",
            page_update_status: "default" as const,
            include_in_summary: false,
          },
          contents: [
            {
              id: "field1",
              type: "input_text",
              order: 1,
              properties: {
                title: "Field 1",
                include_in_summary: false,
              },
            },
          ],
        },
      ];

      expect(getMasterToggleState(formContents)).toBe(false);
    });
  });

  describe("hasAnyComponentsIncludedInSummary", () => {
    it("should detect components inside sections", () => {
      const components: FormElementsType[] = [
        {
          id: "section1",
          type: CWFItemType.Section,
          order: 1,
          properties: {
            title: "Test Section",
            include_in_summary: false,
          },
          contents: [
            {
              id: "field1",
              type: "input_text",
              order: 1,
              properties: {
                title: "Field 1",
                include_in_summary: true, // This should be detected
              },
            },
          ],
        },
      ];

      expect(hasAnyComponentsIncludedInSummary(components)).toBe(true);
    });
  });
});
