import type { UploadConfigs, UploadItem } from "../Upload";
import { MockedProvider } from "@apollo/client/testing";
import { fireEvent, screen } from "@testing-library/react";
import { nanoid } from "nanoid";
import { formRender } from "@/utils/dev/jest";
import UploadDocuments from "./UploadDocuments";

const documents: UploadItem[] = [
  {
    id: nanoid(),
    name: "Crew Member Info",
    displayName: "Crew Member Info",
    size: "564 KB",
    date: "2022-01-20",
    time: "10:50AM",
    url: "",
    signedUrl: "",
  },
  {
    id: nanoid(),
    name: "Crew Member Info 2",
    displayName: "Crew Member Info 2",
    size: "121 kb",
    date: "2022-01-21",
    time: "4:25PM",
    url: "",
    signedUrl: "",
  },
  {
    id: nanoid(),
    name: "Crew Member Info 3",
    displayName: "Crew Member Info 3",
    size: "854 kb",
    date: "2022-01-20",
    time: "8:00PM",
    url: "",
    signedUrl: "",
  },
];

const configs: UploadConfigs = {
  title: "Documents",
  buttonLabel: "Add documents",
  buttonIcon: "file_blank_outline",
  allowedFormats: ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx",
};

describe(UploadDocuments.name, () => {
  describe("when the page renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = formRender(
        <MockedProvider>
          <UploadDocuments
            configs={configs}
            fieldArrayName="attachments.documents"
          />
        </MockedProvider>
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it("should have a paragraph stating that no documents are uploaded", () => {
      formRender(
        <MockedProvider>
          <UploadDocuments
            configs={configs}
            fieldArrayName="attachments.documents"
          />
        </MockedProvider>
      );
      screen.getByText(/no documents uploaded/i);
    });

    it.todo("should add a new document when the add button is clicked");
  });

  describe("when the page renders with documents", () => {
    it("should display the list of available documents", () => {
      formRender(
        <MockedProvider>
          <UploadDocuments
            configs={configs}
            fieldArrayName="attachments.documents"
          />
        </MockedProvider>,
        { attachments: { documents } }
      );
      const documentElement = screen.getAllByTestId("document-item");
      expect(documentElement).toHaveLength(3);
    });

    describe('when the user clicks the "more" options icon on a specific document', () => {
      beforeEach(() => {
        const document = [
          {
            id: nanoid(),
            name: "Crew Member Info",
            displayName: "Crew Member Info",
            size: "564 KB",
            date: "2022-01-20",
            time: "10:50AM",
          },
        ];
        formRender(
          <MockedProvider>
            <UploadDocuments
              configs={configs}
              fieldArrayName="attachments.documents"
            />
          </MockedProvider>,
          { attachments: { documents: document } }
        );
      });

      it("should display a dropdown menu", () => {
        const optionsElement = screen.getByRole("button", { name: "" });
        fireEvent.click(optionsElement);
        screen.getByRole("menu");
      });

      it('should remove the document when the "delete" option is clicked', () => {
        const optionsElement = screen.getByRole("button", { name: "" });
        fireEvent.click(optionsElement);
        const deleteElement = screen.getByRole("button", { name: /delete/i });
        fireEvent.click(deleteElement);
        expect(screen.queryByTestId("document-item")).toBeNull();
      });

      it.todo("should download the file");
    });
  });
});
