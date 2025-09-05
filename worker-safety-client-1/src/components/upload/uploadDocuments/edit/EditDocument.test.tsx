import { fireEvent, render, screen } from "@testing-library/react";
import { nanoid } from "nanoid";
import EditDocument from "./EditDocument";

const mockOnSave = jest.fn();
const mockOnCancel = jest.fn();

const file = {
  id: nanoid(),
  name: "CrewMember.xls",
  displayName: "Crew Details",
  size: "564 KB",
  date: "11/22/2021",
  time: "10:50PM",
  url: "path/to/file",
  signedUrl: "path/to/fileToDownload",
};

const fileWithCategory = { ...file, category: "JHA" };

describe(EditDocument.name, () => {
  describe("when it renders", () => {
    beforeEach(() => {
      render(
        <EditDocument file={file} onSave={mockOnSave} onCancel={mockOnCancel} />
      );
    });

    it("should match the snapshot", () => {
      const { asFragment } = render(
        <EditDocument file={file} onSave={mockOnSave} onCancel={mockOnCancel} />
      );
      expect(asFragment()).toMatchSnapshot();
    });

    describe("when the user clicks the save button", () => {
      beforeEach(() => {
        jest.clearAllMocks();
      });

      it('should call the "onSave" callback with the same file name ', () => {
        fireEvent.click(screen.getByRole("button", { name: /save document/i }));
        expect(mockOnSave).toHaveBeenCalledWith({
          id: file.id,
          displayName: file.name,
          name: file.name,
        });
      });

      it("should create a document with the updated document name", () => {
        const inputElement = screen.getByRole("textbox");
        fireEvent.change(inputElement, { target: { value: "Test document" } });
        fireEvent.click(screen.getByRole("button", { name: /save document/i }));
        expect(mockOnSave).toHaveBeenCalledWith({
          id: file.id,
          displayName: "Test document",
          name: "Test document",
        });
      });
    });

    describe("when the user clicks the cancel button", () => {
      it('should call the "mockOnCancel" function', () => {
        fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
        expect(mockOnSave).toHaveBeenCalled();
      });
    });
  });

  describe("when it renders with file type", () => {
    beforeEach(() => {
      render(
        <EditDocument
          file={fileWithCategory}
          onSave={mockOnSave}
          onCancel={mockOnCancel}
        />
      );
    });

    it("should match the snapshot", () => {
      const { asFragment } = render(
        <EditDocument
          file={fileWithCategory}
          onSave={mockOnSave}
          onCancel={mockOnCancel}
        />
      );
      expect(asFragment()).toMatchSnapshot();
    });

    describe("when the user clicks the save button", () => {
      beforeEach(() => {
        jest.clearAllMocks();
      });

      it('should call the "onSave" callback with the same file type', () => {
        fireEvent.click(screen.getByRole("button", { name: /save document/i }));
        expect(mockOnSave).toHaveBeenCalledWith({
          id: fileWithCategory.id,
          displayName: fileWithCategory.name,
          name: fileWithCategory.name,
          category: fileWithCategory.category,
        });
      });
    });
  });
});
