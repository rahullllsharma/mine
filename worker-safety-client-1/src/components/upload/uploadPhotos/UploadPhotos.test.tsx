import type { UploadConfigs, UploadItem } from "../Upload";
import { fireEvent, screen } from "@testing-library/react";
import { nanoid } from "nanoid";
import { MockedProvider } from "@apollo/client/testing";
import { formRender } from "@/utils/dev/jest";
import UploadPhotos from "./UploadPhotos";

const photos: UploadItem[] = [
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

describe(UploadPhotos.name, () => {
  describe("when the page renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = formRender(
        <MockedProvider>
          <UploadPhotos configs={configs} fieldArrayName="attachments.photos" />
        </MockedProvider>
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it("should have a paragraph stating that no photos are uploaded", () => {
      formRender(
        <MockedProvider>
          <UploadPhotos configs={configs} fieldArrayName="attachments.photos" />
        </MockedProvider>
      );
      screen.getByText(/no photos uploaded/i);
    });

    it.todo("should add a new photo when the add button is clicked");
  });

  describe("when the page renders with photos", () => {
    it("should display the list of available photos", () => {
      formRender(
        <MockedProvider>
          <UploadPhotos configs={configs} fieldArrayName="attachments.photos" />
        </MockedProvider>,
        { attachments: { photos } }
      );
      const documentElement = screen.getAllByTestId("photo-item");
      expect(documentElement).toHaveLength(3);
    });

    describe("when the user clicks the delete button on the top right corner of the photo", () => {
      beforeEach(() => {
        const photo = [
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
        ];
        formRender(
          <MockedProvider>
            <UploadPhotos
              configs={configs}
              fieldArrayName="attachments.photos"
            />
          </MockedProvider>,
          { attachments: { photos: photo } }
        );
      });

      it("should remove the photo after confirming deletion in the modal", () => {
        // Find the delete button
        const deleteButton = screen.getByLabelText("Delete photo");

        // Click the delete button
        fireEvent.click(deleteButton);
        expect(
          screen.getByText(content => content.includes("delete this photo"))
        ).toBeInTheDocument();

        // Get the confirm button in the modal and click it
        const confirmButton = screen.getByRole("button", { name: "Delete" });
        fireEvent.click(confirmButton);

        // Check if the photo has been removed
        expect(screen.queryByTestId("photo-item")).toBeNull();
      });
    });
  });
});
