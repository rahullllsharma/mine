import { screen, fireEvent, waitFor, render } from "@testing-library/react";
import { act } from "react-dom/test-utils";

import { mockTenantStore } from "@/utils/dev/jest";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CWFItemType } from "../../../customisedForm.types";
import PageListComponent from "../PageList";

type PageDetails = {
  id: string;
  parentId: string;
  deleteParentPage: boolean;
  subPages: string[];
};

// Mock the context
const mockContextValue = {
  state: {
    form: {
      id: "test-form-id",
      type: "form",
      properties: {
        title: "Test Form",
        status: "published",
        description: "Test form description",
      },
      contents: [
        {
          id: "parent-page-1",
          type: CWFItemType.Page,
          order: 1,
          properties: {
            title: "Parent Page 1",
            description: "Test parent page",
            page_update_status: "published" as any,
            include_in_summary: false,
          },
          contents: [
            {
              id: "subpage-1",
              type: CWFItemType.SubPage,
              order: 1,
              properties: {
                title: "Subpage 1",
                description: "Test subpage 1",
                page_update_status: "published" as any,
                include_in_summary: false,
              },
            },
            {
              id: "subpage-2",
              type: CWFItemType.SubPage,
              order: 2,
              properties: {
                title: "Subpage 2",
                description: "Test subpage 2",
                page_update_status: "published" as any,
                include_in_summary: false,
              },
            },
          ],
        },
        {
          id: "parent-page-2",
          type: CWFItemType.Page,
          order: 2,
          properties: {
            title: "Parent Page 2",
            description: "Test parent page 2",
            page_update_status: "published" as any,
            include_in_summary: false,
          },
          contents: [
            {
              id: "subpage-3",
              type: CWFItemType.SubPage,
              order: 1,
              properties: {
                title: "Subpage 3",
                description: "Test subpage 3",
                page_update_status: "published" as any,
                include_in_summary: false,
              },
            },
          ],
        },
        {
          id: "simple-page",
          type: CWFItemType.Page,
          order: 3,
          properties: {
            title: "Simple Page",
            description: "Test simple page",
            page_update_status: "published" as any,
            include_in_summary: false,
          },
          contents: [],
        },
      ],
      settings: {
        availability: {
          adhoc: { selected: true },
          work_package: { selected: false },
        },
        edit_expiry_days: 30,
      },
      isDisabled: false,
    },
    formBuilderMode: "edit" as any,
    isFormDirty: false,
    isFormIsValid: true,
  },
  dispatch: jest.fn(),
};

// Mock child components
jest.mock("../PageListItem", () => {
  return function MockPageListItem(props: any) {
    return (
      <div data-testid={`page-list-item-${props.pageDetails.id}`}>
        <button
          data-testid={`parent-checkbox-${props.pageDetails.id}`}
          onClick={() => {
            props.onSelectOrDeSelectPage({
              id: props.pageDetails.id,
              parentId: props.pageDetails.id,
              deleteParentPage: true,
              subPages: props.pageDetails.contents
                .filter((content: any) => content.type === CWFItemType.SubPage)
                .map((subPage: any) => subPage.id),
            });
          }}
        >
          Select Parent
        </button>
        {props.pageDetails.contents
          .filter((content: any) => content.type === CWFItemType.SubPage)
          .map((subPage: any) => (
            <button
              key={subPage.id}
              data-testid={`subpage-checkbox-${subPage.id}`}
              onClick={() => {
                props.onSelectOrDeSelectPage({
                  id: props.pageDetails.id,
                  parentId: props.pageDetails.id,
                  deleteParentPage: false,
                  subPages: [subPage.id],
                });
              }}
            >
              Select Subpage {subPage.id}
            </button>
          ))}
      </div>
    );
  };
});

jest.mock("../AddPageListItem", () => {
  return function MockAddPageListItem() {
    return <div data-testid="add-page-list-item">Add Page</div>;
  };
});

const defaultProps = {
  mode: "deletePage" as const,
  newPageTitle: "",
  setNewPageTitle: jest.fn(),
  activePageDetails: {
    id: "parent-page-1",
    parentId: "root",
    type: CWFItemType.Page,
  },
  setActivePageDetails: jest.fn(),
  subPageTitle: "",
  setSubPageTitle: jest.fn(),
  setParentPage: jest.fn(),
  deletePageDetails: [],
  onDeletePageDetailsUpdate: jest.fn(),
  deletePageReset: false,
  OnDeletePageReset: jest.fn(),
};

const renderWithContext = (props = {}) => {
  return render(
    <CustomisedFromStateContext.Provider value={mockContextValue}>
      <PageListComponent {...defaultProps} {...props} />
    </CustomisedFromStateContext.Provider>
  );
};

describe(PageListComponent.name, () => {
  mockTenantStore();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("onSelectOrDeSelectPage function", () => {
    it("should mark parent page for deletion when all subpages are selected", async () => {
      const mockOnDeletePageDetailsUpdate = jest.fn();

      renderWithContext({
        onDeletePageDetailsUpdate: mockOnDeletePageDetailsUpdate,
        deletePageDetails: [],
      });

      const parentCheckbox = screen.getByTestId(
        "parent-checkbox-parent-page-1"
      );

      await act(async () => {
        fireEvent.click(parentCheckbox);
      });

      await waitFor(() => {
        expect(mockOnDeletePageDetailsUpdate).toHaveBeenCalledWith([
          {
            id: "parent-page-1",
            parentId: "parent-page-1",
            deleteParentPage: true,
            subPages: ["subpage-1", "subpage-2"],
          },
        ]);
      });
    });

    it("should not mark parent page for deletion when some subpages are unselected", async () => {
      const mockOnDeletePageDetailsUpdate = jest.fn();

      renderWithContext({
        onDeletePageDetailsUpdate: mockOnDeletePageDetailsUpdate,
        deletePageDetails: [],
      });

      const subpageCheckbox = screen.getByTestId("subpage-checkbox-subpage-1");

      await act(async () => {
        fireEvent.click(subpageCheckbox);
      });

      await waitFor(() => {
        expect(mockOnDeletePageDetailsUpdate).toHaveBeenCalledWith([
          {
            id: "parent-page-1",
            parentId: "",
            deleteParentPage: false,
            subPages: ["subpage-1"],
          },
        ]);
      });
    });

    it("should handle parent page with single subpage correctly", async () => {
      const mockOnDeletePageDetailsUpdate = jest.fn();

      renderWithContext({
        onDeletePageDetailsUpdate: mockOnDeletePageDetailsUpdate,
        deletePageDetails: [],
      });

      const parentCheckbox = screen.getByTestId(
        "parent-checkbox-parent-page-2"
      );

      await act(async () => {
        fireEvent.click(parentCheckbox);
      });

      await waitFor(() => {
        expect(mockOnDeletePageDetailsUpdate).toHaveBeenCalledWith([
          {
            id: "parent-page-2",
            parentId: "parent-page-2",
            deleteParentPage: true,
            subPages: ["subpage-3"],
          },
        ]);
      });
    });

    it("should handle simple page without subpages correctly", async () => {
      const mockOnDeletePageDetailsUpdate = jest.fn();

      renderWithContext({
        onDeletePageDetailsUpdate: mockOnDeletePageDetailsUpdate,
        deletePageDetails: [],
      });

      const parentCheckbox = screen.getByTestId("parent-checkbox-simple-page");

      await act(async () => {
        fireEvent.click(parentCheckbox);
      });

      await waitFor(() => {
        expect(mockOnDeletePageDetailsUpdate).toHaveBeenCalledWith([
          {
            id: "simple-page",
            parentId: "simple-page",
            deleteParentPage: true,
            subPages: [],
          },
        ]);
      });
    });

    it("should update existing page details instead of creating duplicates", async () => {
      const existingPageDetails: PageDetails[] = [
        {
          id: "parent-page-1",
          parentId: "parent-page-1",
          deleteParentPage: true,
          subPages: ["subpage-1"],
        },
      ];

      const mockOnDeletePageDetailsUpdate = jest.fn();

      renderWithContext({
        onDeletePageDetailsUpdate: mockOnDeletePageDetailsUpdate,
        deletePageDetails: existingPageDetails,
      });

      const parentCheckbox = screen.getByTestId(
        "parent-checkbox-parent-page-1"
      );

      await act(async () => {
        fireEvent.click(parentCheckbox);
      });

      await waitFor(() => {
        expect(mockOnDeletePageDetailsUpdate).toHaveBeenCalledWith([
          {
            id: "parent-page-1",
            parentId: "parent-page-1",
            deleteParentPage: true,
            subPages: ["subpage-1", "subpage-2"],
          },
        ]);
      });
    });

    it("should set parentId to empty string when not all subpages are selected", async () => {
      const mockOnDeletePageDetailsUpdate = jest.fn();

      renderWithContext({
        onDeletePageDetailsUpdate: mockOnDeletePageDetailsUpdate,
        deletePageDetails: [],
      });

      const subpageCheckbox = screen.getByTestId("subpage-checkbox-subpage-1");

      await act(async () => {
        fireEvent.click(subpageCheckbox);
      });

      await waitFor(() => {
        const callArgs = mockOnDeletePageDetailsUpdate.mock.calls[0][0];
        expect(callArgs[0].parentId).toBe("");
        expect(callArgs[0].deleteParentPage).toBe(false);
      });
    });
  });

  describe("Component rendering", () => {
    it("should render all pages from form contents", () => {
      renderWithContext();

      expect(
        screen.getByTestId("page-list-item-parent-page-1")
      ).toBeInTheDocument();
      expect(
        screen.getByTestId("page-list-item-parent-page-2")
      ).toBeInTheDocument();
      expect(
        screen.getByTestId("page-list-item-simple-page")
      ).toBeInTheDocument();
    });

    it("should render AddPageListItem when mode is addPage", () => {
      renderWithContext({ mode: "addPage" });

      expect(screen.getByTestId("add-page-list-item")).toBeInTheDocument();
    });

    it("should not render AddPageListItem when mode is not addPage", () => {
      renderWithContext({ mode: "deletePage" });

      expect(
        screen.queryByTestId("add-page-list-item")
      ).not.toBeInTheDocument();
    });
  });
});
