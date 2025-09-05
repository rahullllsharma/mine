import type { UploadConfigs } from "./Upload";
import { fireEvent, screen, waitFor } from "@testing-library/react";
import { formRender } from "@/utils/dev/jest";
import Upload from "./Upload";

const configs: UploadConfigs = {
  title: "Documents",
  buttonLabel: "Add documents",
  buttonIcon: "file_blank_outline",
  allowedFormats: ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx",
};

const mockOnUpload = jest.fn();

describe(Upload.name, () => {
  describe("when the page renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = formRender(
        <Upload configs={configs} onUpload={mockOnUpload} />
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it('should call "onUpload" callback when the upload button is clicked', async () => {
      formRender(<Upload configs={configs} onUpload={mockOnUpload} />);
      const file = new File(["(⌐□_□)"], "crew.png", {
        type: "image/png",
      });
      const fileInputElement = screen.getByTitle("file-uploader");
      await waitFor(() =>
        fireEvent.change(fileInputElement, {
          target: { files: [file] },
        })
      );
      expect(mockOnUpload).toHaveBeenCalledWith([file]);
    });
  });
});
