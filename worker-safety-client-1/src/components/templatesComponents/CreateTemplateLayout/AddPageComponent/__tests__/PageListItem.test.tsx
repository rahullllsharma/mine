import { screen, fireEvent, waitFor } from "@testing-library/react";
import { act } from "react-dom/test-utils";

import { formRender, mockTenantStore } from "@/utils/dev/jest";
import { CWFItemType } from "../../../customisedForm.types";
import PageListItem from "../PageListItem";

// Mock the CSS module
jest.mock("../createTemplateStyle.module.scss", () => ({
  pageListingComponentParent__subPagesSection: "mock-subpages-section",
}));

// Mock child components
jest.mock("../WithDeletePage", () => {
  return function MockWithDeletePage(props: any) {
    return (
      <div data-testid={`with-delete-page-${props.label}`}>
        <span>{props.label}</span>
        <button
          data-testid={`checkbox-${props.label}`}
          onClick={props.onSelectOfCheckbox}
          className={props.selected ? "selected" : "not-selected"}
        >
          {props.selected ? "Selected" : "Not Selected"}
        </button>
        <button
          data-testid={`page-select-${props.label}`}
          onClick={props.onSelectOfPage}
        >
          Select Page
        </button>
      </div>
    );
  };
});

jest.mock("../AddPageListItem", () => {
  return function MockAddPageListItem(props: any) {
    return (
      <div data-testid="add-subpage-item">
        <input
          data-testid="subpage-title-input"
          value={props.newPageTitle}
          onChange={e => props.setNewPageTitle(e.target.value)}
        />
      </div>
    );
  };
});

const mockPageDetails = {
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
};

const defaultProps = {
  pageDetails: mockPageDetails,
  activePageDetails: {
    id: "parent-page-1",
    parentId: "root",
    type: CWFItemType.Page,
  },
  setActivePageDetails: jest.fn(),
  pageAdditionMode: "deletePage",
  subPageTitle: "",
  setSubPageTitle: jest.fn(),
  setParentPage: jest.fn(),
  mode: "deletePage" as const,
  handlePageDelete: jest.fn(),
  onSelectOrDeSelectPage: jest.fn(),
  deletePageReset: false,
  OnDeletePageReset: jest.fn(),
  deletePageDetails: [],
};

const renderComponent = (props = {}) => {
  return formRender(<PageListItem {...defaultProps} {...props} />);
};

describe(PageListItem.name, () => {
  mockTenantStore();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Component rendering", () => {
    it("should render parent page with correct title", () => {
      renderComponent();

      expect(screen.getByText("Parent Page 1")).toBeInTheDocument();
    });

    it("should render subpages with correct titles when parent is active", () => {
      renderComponent({
        activePageDetails: {
          id: "parent-page-1",
          parentId: "root",
          type: CWFItemType.Page,
        },
      });

      expect(screen.getByText("Subpage 1")).toBeInTheDocument();
      expect(screen.getByText("Subpage 2")).toBeInTheDocument();
    });

    it("should not render subpages when parent page is not active", () => {
      renderComponent({
        activePageDetails: {
          id: "other-page",
          parentId: "root",
          type: CWFItemType.Page,
        },
      });

      expect(
        screen.queryByTestId("with-delete-page-Subpage 1")
      ).not.toBeInTheDocument();
      expect(
        screen.queryByTestId("with-delete-page-Subpage 2")
      ).not.toBeInTheDocument();
    });

    it("should render AddPageListItem when pageAdditionMode is addSubPage", () => {
      renderComponent({
        pageAdditionMode: "addSubPage",
        activePageDetails: {
          id: "parent-page-1",
          parentId: "root",
          type: CWFItemType.Page,
        },
      });

      expect(screen.getByTestId("add-subpage-item")).toBeInTheDocument();
    });

    it("should not render AddPageListItem when pageAdditionMode is not addSubPage", () => {
      renderComponent({
        pageAdditionMode: "deletePage",
        activePageDetails: {
          id: "parent-page-1",
          parentId: "root",
          type: CWFItemType.Page,
        },
      });

      expect(screen.queryByTestId("add-subpage-item")).not.toBeInTheDocument();
    });
  });

  describe("Parent page checkbox interactions", () => {
    it("should call onSelectOrDeSelectPage when parent checkbox is clicked", async () => {
      const mockOnSelectOrDeSelectPage = jest.fn();

      renderComponent({
        onSelectOrDeSelectPage: mockOnSelectOrDeSelectPage,
      });

      const parentCheckbox = screen.getByTestId("checkbox-Parent Page 1");

      await act(async () => {
        fireEvent.click(parentCheckbox);
      });

      expect(mockOnSelectOrDeSelectPage).toHaveBeenCalledWith({
        id: "parent-page-1",
        parentId: "parent-page-1",
        deleteParentPage: true,
        subPages: ["subpage-1", "subpage-2"],
      });
    });

    it("should remove parent page selection when parent checkbox is clicked again", async () => {
      const mockOnSelectOrDeSelectPage = jest.fn();

      renderComponent({
        onSelectOrDeSelectPage: mockOnSelectOrDeSelectPage,
        deletePageDetails: [
          {
            id: "parent-page-1",
            parentId: "parent-page-1",
            deleteParentPage: true,
            subPages: ["subpage-1", "subpage-2"],
          },
        ],
      });

      const parentCheckbox = screen.getByTestId("checkbox-Parent Page 1");

      await act(async () => {
        fireEvent.click(parentCheckbox);
      });

      expect(mockOnSelectOrDeSelectPage).toHaveBeenCalledWith({
        id: "parent-page-1",
        parentId: "",
        deleteParentPage: false,
        subPages: [],
      });
    });
  });

  describe("Page selection interactions", () => {
    it("should call setActivePageDetails and setParentPage when parent page is selected", async () => {
      const mockSetActivePageDetails = jest.fn();
      const mockSetParentPage = jest.fn();

      renderComponent({
        setActivePageDetails: mockSetActivePageDetails,
        setParentPage: mockSetParentPage,
      });

      const pageSelectButton = screen.getByTestId("page-select-Parent Page 1");

      await act(async () => {
        fireEvent.click(pageSelectButton);
      });

      expect(mockSetParentPage).toHaveBeenCalledWith("parent-page-1");
      expect(mockSetActivePageDetails).toHaveBeenCalledWith({
        id: "parent-page-1",
        parentId: "root",
        type: CWFItemType.Page,
      });
    });

    it("should call setActivePageDetails when subpage is selected", async () => {
      const mockSetActivePageDetails = jest.fn();

      renderComponent({
        setActivePageDetails: mockSetActivePageDetails,
        activePageDetails: {
          id: "parent-page-1",
          parentId: "root",
          type: CWFItemType.Page,
        },
      });

      const subpageSelectButton = screen.getByTestId("page-select-Subpage 1");

      await act(async () => {
        fireEvent.click(subpageSelectButton);
      });

      expect(mockSetActivePageDetails).toHaveBeenCalledWith({
        id: "subpage-1",
        parentId: "parent-page-1",
        type: CWFItemType.SubPage,
      });
    });
  });

  describe("Delete page reset functionality", () => {
    it("should call OnDeletePageReset when deletePageReset is true", async () => {
      const mockOnDeletePageReset = jest.fn();

      renderComponent({
        deletePageReset: true,
        OnDeletePageReset: mockOnDeletePageReset,
      });

      await waitFor(() => {
        expect(mockOnDeletePageReset).toHaveBeenCalledWith(false);
      });
    });
  });
});
